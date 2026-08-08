#!/usr/bin/env python3
"""Package the intentional VvH repository delta as a reviewable drop-in ZIP."""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import subprocess
import sys
import zipfile
from pathlib import Path, PurePosixPath

ALLOWED_EXACT = {
    "CHANGELOG.md",
    "pack.toml",
    "index.toml",
    "config/ftbquests/quests/chapter_groups.snbt",
    "config/ftbquests/quests/lang/en_us.snbt",
    "config/ftbquests/quests/chapters/a_blank_page.snbt",
    "config/ftbquests/quests/chapters/first_resonance.snbt",
    "config/ftbquests/quests/chapters/the_weathered_ledger.snbt",
    "config/ftbquests/quests/chapters/atlas_exchange.snbt",
    "config/ftbquests/quests/reward_tables/1A0B1A4E5A9E2000.snbt",
    "config/ftbquests/quests/reward_tables/1A0B1A4E5A9E3000.snbt",
    "global_packs/required_resources/poiesis_living_atlas_art.pw.toml",
}
ALLOWED_PREFIXES = (
    "config/ftbquests/quests/chapters/vvh_",
    "config/ftbquests/quests/reward_tables/7A11C0DE",
    "docs/vvh/",
    "scripts/vvh_",
)


def run(root: Path, *args: str, check: bool = True) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["git", "-C", str(root), *args],
        check=check,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def is_allowed(rel: str) -> bool:
    return rel in ALLOWED_EXACT or any(rel.startswith(prefix) for prefix in ALLOWED_PREFIXES)


def changed_paths(root: Path, base: str) -> list[str]:
    tracked = run(root, "diff", "--name-only", "--diff-filter=ACMRTUXB", base, "--").stdout.splitlines()
    untracked = run(root, "ls-files", "--others", "--exclude-standard", "-z").stdout.split("\0")
    paths = sorted({p for p in tracked + untracked if p})
    return paths


def deleted_paths(root: Path, base: str) -> list[str]:
    return sorted(
        p for p in run(root, "diff", "--name-only", "--diff-filter=D", base, "--").stdout.splitlines() if p
    )


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("root", type=Path)
    ap.add_argument("--base", required=True)
    ap.add_argument("--zip", dest="zip_path", type=Path, required=True)
    ap.add_argument("--manifest", type=Path, required=True)
    ap.add_argument("--changed-list", type=Path, required=True)
    ap.add_argument("--patch", type=Path, required=True)
    args = ap.parse_args()

    root = args.root.resolve()
    paths = changed_paths(root, args.base)
    deleted = deleted_paths(root, args.base)
    if deleted:
        raise SystemExit(f"Refusing to package deletions: {deleted}")
    if not paths:
        raise SystemExit("No changed files found")

    disallowed = [p for p in paths if not is_allowed(p)]
    if disallowed:
        raise SystemExit("Unexpected changed files outside VvH allowlist:\n" + "\n".join(disallowed))

    missing = [p for p in paths if not (root / p).is_file()]
    if missing:
        raise SystemExit("Changed paths are not regular files:\n" + "\n".join(missing))

    required = {
        "pack.toml",
        "index.toml",
        "config/ftbquests/quests/chapter_groups.snbt",
        "config/ftbquests/quests/lang/en_us.snbt",
        "config/ftbquests/quests/chapters/a_blank_page.snbt",
        "config/ftbquests/quests/chapters/first_resonance.snbt",
        "config/ftbquests/quests/chapters/the_weathered_ledger.snbt",
        "config/ftbquests/quests/chapters/atlas_exchange.snbt",
        "config/ftbquests/quests/reward_tables/1A0B1A4E5A9E2000.snbt",
        "config/ftbquests/quests/reward_tables/1A0B1A4E5A9E3000.snbt",
        "docs/vvh/VALIDATION.md",
        "docs/vvh/VERIFICATION.md",
        "docs/vvh/UNRESOLVED.md",
        "docs/vvh/campaign_manifest.json",
        "scripts/vvh_build.py",
        "scripts/vvh_validate.py",
        "scripts/vvh_render_layouts.py",
    }
    missing_required = sorted(required.difference(paths))
    if missing_required:
        raise SystemExit("Required VvH deliverables missing from delta:\n" + "\n".join(missing_required))

    chapter_paths = [p for p in paths if p.startswith("config/ftbquests/quests/chapters/vvh_")]
    table_paths = [p for p in paths if p.startswith("config/ftbquests/quests/reward_tables/7A11C0DE")]
    if len(chapter_paths) != 10:
        raise SystemExit(f"Expected 10 VvH chapters, found {len(chapter_paths)}")
    if len(table_paths) != 3:
        raise SystemExit(f"Expected 3 VvH reward tables, found {len(table_paths)}")

    entries = []
    for rel in paths:
        path = root / rel
        entries.append({
            "path": rel,
            "size": path.stat().st_size,
            "sha256": sha256(path),
        })

    manifest = {
        "format": 1,
        "base_repository": "codecraft3r/packwiz-modpack",
        "base_sha": args.base,
        "file_count": len(entries),
        "chapters": len(chapter_paths),
        "reward_tables": len(table_paths),
        "files": entries,
    }
    args.manifest.parent.mkdir(parents=True, exist_ok=True)
    args.manifest.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    args.changed_list.write_text("\n".join(paths) + "\n", encoding="utf-8")

    # The textual patch is supplemental; untracked files are represented in the ZIP + manifest.
    patch = run(root, "diff", "--binary", args.base, "--").stdout
    args.patch.write_text(patch, encoding="utf-8")

    args.zip_path.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(args.zip_path, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9) as zf:
        for rel in paths:
            zf.write(root / rel, PurePosixPath(rel).as_posix())
        zf.writestr("VVH_DROPIN_MANIFEST.json", json.dumps(manifest, indent=2, sort_keys=True) + "\n")
        zf.writestr(
            "INSTALL.md",
            "# VvH Season One drop-in\n\n"
            f"Base revision: `{args.base}`.\n\n"
            "Extract into the root of `codecraft3r/packwiz-modpack`, review the diff, "
            "run `packwiz refresh` and `packwiz list`, then perform the client/live-server checks "
            "listed in `docs/vvh/UNRESOLVED.md`. Do not enable resets or sanctioned skirmishes "
            "until their runtime checks pass.\n",
        )

    print(json.dumps({
        "zip": str(args.zip_path),
        "file_count": len(entries),
        "chapters": len(chapter_paths),
        "reward_tables": len(table_paths),
    }, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
