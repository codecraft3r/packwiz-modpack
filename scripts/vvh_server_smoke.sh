#!/usr/bin/env bash
set -euo pipefail

usage() {
  echo "usage: $0 <runtime-dir> <work-dir> <evidence-dir> <neoforge-version>" >&2
  exit 2
}

[[ $# -eq 4 ]] || usage
RUNTIME_DIR="$(realpath "$1")"
WORK_DIR="$(realpath -m "$2")"
EVIDENCE_DIR="$(realpath -m "$3")"
NEOFORGE_VERSION="$4"
SERVER_DIR="$WORK_DIR/server"
INSTALLER="$WORK_DIR/neoforge-${NEOFORGE_VERSION}-installer.jar"
LOG="$EVIDENCE_DIR/server-console.log"
SUMMARY_JSON="$EVIDENCE_DIR/runtime-smoke-summary.json"
SUMMARY_MD="$EVIDENCE_DIR/runtime-smoke-summary.md"

if command -v python >/dev/null 2>&1; then
  PYTHON_BIN=python
elif command -v python3 >/dev/null 2>&1; then
  PYTHON_BIN=python3
else
  echo "Python 3 is required to summarize smoke-test evidence" >&2
  exit 1
fi

mkdir -p "$WORK_DIR" "$EVIDENCE_DIR"
rm -rf "$SERVER_DIR"
mkdir -p "$SERVER_DIR"

installer_url="https://maven.neoforged.net/releases/net/neoforged/neoforge/${NEOFORGE_VERSION}/neoforge-${NEOFORGE_VERSION}-installer.jar"
printf '%s\n' "$installer_url" > "$EVIDENCE_DIR/neoforge-installer-url.txt"
curl -fL --retry 4 --retry-all-errors "$installer_url" -o "$INSTALLER" \
  >"$EVIDENCE_DIR/neoforge-installer-download.log" 2>&1
sha256sum "$INSTALLER" > "$EVIDENCE_DIR/neoforge-installer.sha256"
(
  cd "$SERVER_DIR"
  java -jar "$INSTALLER" --installServer
) >"$EVIDENCE_DIR/neoforge-install.log" 2>&1

cp -a "$RUNTIME_DIR"/. "$SERVER_DIR"/
printf 'eula=true\n' > "$SERVER_DIR/eula.txt"
cat > "$SERVER_DIR/server.properties" <<'EOF'
allow-flight=true
difficulty=normal
enable-command-block=true
enable-jmx-monitoring=false
enable-query=false
enable-rcon=false
enforce-secure-profile=false
force-gamemode=false
gamemode=survival
generate-structures=true
hardcore=false
level-name=vvh-ci-world
max-players=4
max-tick-time=-1
motd=VvH CI disposable smoke test
network-compression-threshold=256
online-mode=false
player-idle-timeout=0
prevent-proxy-connections=false
simulation-distance=4
spawn-animals=true
spawn-monsters=true
spawn-npcs=true
spawn-protection=0
sync-chunk-writes=false
view-distance=4
white-list=false
EOF
cat > "$SERVER_DIR/user_jvm_args.txt" <<'EOF'
-Xms1G
-Xmx5G
-Dterminal.jline=false
-Dterminal.ansi=false
-Dlog4j2.formatMsgNoLookups=true
EOF

[[ -x "$SERVER_DIR/run.sh" ]] || chmod +x "$SERVER_DIR/run.sh" 2>/dev/null || true
[[ -f "$SERVER_DIR/run.sh" ]] || { echo "NeoForge installer did not create run.sh" >&2; exit 1; }

cleanup() {
  set +e
  [[ -n "${SERVER_PID:-}" ]] && kill "$SERVER_PID" 2>/dev/null
  [[ -n "${KEEPER_PID:-}" ]] && kill "$KEEPER_PID" 2>/dev/null
  [[ -n "${FIFO:-}" ]] && rm -f "$FIFO"
}
trap cleanup EXIT

windows_shell=0
case "$(uname -s)" in
  MINGW*|MSYS*|CYGWIN*) windows_shell=1 ;;
esac

if [[ "$windows_shell" -eq 1 ]]; then
  # A native JVM does not reliably consume an MSYS FIFO as console stdin.
  # Feed the commands through an anonymous pipe after the log reaches Done.
  (
    while ! grep -Eq 'Done \([0-9.]+s\)!|Done \([0-9.]+s\)! For help' "$LOG" 2>/dev/null; do
      sleep 5
    done
    printf 'ftbquests reload\n'
    sleep 20
    printf 'list\n'
    sleep 5
    printf 'stop\n'
  ) | (
    cd "$SERVER_DIR"
    java @user_jvm_args.txt "@libraries/net/neoforged/neoforge/${NEOFORGE_VERSION}/win_args.txt" nogui
  ) > "$LOG" 2>&1 &
  SERVER_PID=$!
else
  FIFO="$WORK_DIR/server-console.in"
  rm -f "$FIFO"
  mkfifo "$FIFO"
  # Keep the FIFO open while the JVM starts and while commands are written.
  tail -f /dev/null > "$FIFO" &
  KEEPER_PID=$!
  (
    cd "$SERVER_DIR"
    bash ./run.sh nogui
  ) < "$FIFO" > "$LOG" 2>&1 &
  SERVER_PID=$!
  exec 3> "$FIFO"
fi

started=0
start_deadline=$((SECONDS + 2100))
while (( SECONDS < start_deadline )); do
  if grep -Eq 'Done \([0-9.]+s\)!|Done \([0-9.]+s\)! For help' "$LOG" 2>/dev/null; then
    started=1
    break
  fi
  if ! kill -0 "$SERVER_PID" 2>/dev/null; then
    break
  fi
  sleep 5
done

if [[ "$started" -ne 1 ]]; then
  echo "Server failed to reach Done state" >&2
  tail -n 300 "$LOG" >&2 || true
  exit 1
fi

if [[ "$windows_shell" -eq 0 ]]; then
  printf 'ftbquests reload\n' >&3
  sleep 20
  printf 'list\n' >&3
  sleep 5
  printf 'stop\n' >&3
fi

exit_deadline=$((SECONDS + 240))
while kill -0 "$SERVER_PID" 2>/dev/null && (( SECONDS < exit_deadline )); do
  sleep 2
done
if kill -0 "$SERVER_PID" 2>/dev/null; then
  echo "Server did not stop cleanly after command" >&2
  kill "$SERVER_PID" 2>/dev/null || true
  wait "$SERVER_PID" || true
  exit 1
fi
wait "$SERVER_PID"
server_status=$?

cp "$SERVER_DIR/logs/latest.log" "$EVIDENCE_DIR/latest.log" 2>/dev/null || true
find "$SERVER_DIR/crash-reports" -type f -maxdepth 1 -print > "$EVIDENCE_DIR/crash-reports.txt" 2>/dev/null || true

# Targeted quest/config failures. General mod warnings are retained in logs but do not
# fail this campaign-specific check unless they implicate FTB Quests, VvH files/IDs,
# or data parsing/registry resolution.
"$PYTHON_BIN" - "$LOG" "$EVIDENCE_DIR/targeted-errors.txt" <<'PY'
from __future__ import annotations
import re
import sys
from pathlib import Path

log = Path(sys.argv[1]).read_text(encoding="utf-8", errors="replace").splitlines()
out = Path(sys.argv[2])
patterns = [
    re.compile(r"(?i)(ftb.?quests|vvh_|7A11C0DE).*(error|exception|failed|unknown|invalid|couldn.?t|cannot)"),
    re.compile(r"(?i)(error|exception|failed|unknown|invalid|couldn.?t|cannot).*(ftb.?quests|vvh_|7A11C0DE)"),
    re.compile(r"(?i)(failed to parse|failed to load|unknown registry|unknown item|unknown reward|unknown task).*(quest|snbt|7A11C0DE|vvh_)"),
]
matches = []
for i, line in enumerate(log, 1):
    if any(p.search(line) for p in patterns):
        matches.append(f"{i}: {line}")
out.write_text("\n".join(matches) + ("\n" if matches else ""), encoding="utf-8")
print(len(matches))
PY
error_count="$(wc -l < "$EVIDENCE_DIR/targeted-errors.txt" | tr -d ' ')"

reload_evidence="$(grep -Ei 'ftbquests|quest.*reload|reload.*quest' "$LOG" | tail -n 80 || true)"
printf '%s\n' "$reload_evidence" > "$EVIDENCE_DIR/ftbquests-reload-lines.txt"

done_line="$(grep -E 'Done \([0-9.]+s\)!' "$LOG" | tail -n 1 || true)"
"$PYTHON_BIN" - "$SUMMARY_JSON" "$server_status" "$error_count" "$done_line" <<'PY'
import json, sys
from pathlib import Path
path = Path(sys.argv[1])
server_status = int(sys.argv[2])
error_count = int(sys.argv[3])
done_line = sys.argv[4]
summary = {
    "status": "pass" if server_status == 0 and error_count == 0 and done_line else "fail",
    "server_exit_code": server_status,
    "reached_done": bool(done_line),
    "done_line": done_line,
    "ftbquests_reload_command_sent": True,
    "targeted_quest_error_count": error_count,
    "scope": "headless NeoForge dedicated-server startup and FTB Quests reload only",
    "not_verified": [
        "client quest-book rendering",
        "player task completion and reward claiming",
        "two-account team reward semantics",
        "FTB Teams faction switching and FTB Chunks claim transfer",
        "PvP/skirmish controls and backup restore",
    ],
}
path.write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8")
print(json.dumps(summary, indent=2))
PY

cat > "$SUMMARY_MD" <<EOF
# Disposable Server Smoke Test

- Result: **$( [[ "$server_status" -eq 0 && "$error_count" -eq 0 ]] && echo PASS || echo FAIL )**
- NeoForge: \`${NEOFORGE_VERSION}\`
- Dedicated server reached the vanilla/NeoForge \`Done\` state: **yes**
- \`ftbquests reload\` was sent after startup.
- Clean commanded shutdown exit code: \`${server_status}\`
- Targeted VvH/FTB Quests parse, registry, task, reward, or reload errors: \`${error_count}\`
- Full console: \`docs/vvh/evidence/server/server-console.log\`
- Latest log: \`docs/vvh/evidence/server/latest.log\`

This verifies headless dedicated-server startup and a post-start quest reload. Client rendering, actual task completion, reward claiming, two-account team semantics, allegiance changes, claim transfer, skirmish controls, and backup restore **requires runtime verification**.
EOF

if [[ "$server_status" -ne 0 || "$error_count" -ne 0 ]]; then
  echo "Campaign-specific server smoke test failed" >&2
  exit 1
fi
