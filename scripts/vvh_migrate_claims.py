#!/usr/bin/env python3
"""Offline migration helper for FTB Quests TeamData SNBT.

The persisted TeamData format is documented by the pinned v2101.1.33 source:
maps use compact quest IDs and claimed_rewards uses ``uuid:id`` QuestKeys.
This tool deliberately does not know the campaign's IDs.  A reviewed JSON
mapping supplies those changes, which makes an accidental re-grant much less
likely when a quest's reward scope changes.

Dry-run is the default.  ``--apply`` is required for a filesystem mutation and
also requires ``--expected-sha256`` as a stale-save guard.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import shutil
import sys
import tempfile
from dataclasses import dataclass
from pathlib import Path
from typing import Any


class SNBTError(ValueError):
    """Raised when the input is not parseable SNBT."""


@dataclass(frozen=True)
class RawNumber:
    raw: str


@dataclass(frozen=True)
class TypedArray:
    kind: str
    values: list[Any]


class Parser:
    """Small complete-enough SNBT parser for TeamData exports.

    It accepts the FTB newline separator rule as well as commas, comments,
    quoted/unquoted keys, numeric suffixes, and vanilla typed arrays.  Values
    retain their original numeric spelling so unrelated TeamData fields do
    not acquire a different numeric type during a migration.
    """

    _number = re.compile(r"[-+]?(?:(?:\d+(?:\.\d*)?)|(?:\.\d+))(?:[eE][-+]?\d+)?[bBsSlLfFdD]?")
    _bare = re.compile(r"[A-Za-z0-9_+\-.]+")

    def __init__(self, text: str):
        self.text = text.lstrip("\ufeff")
        self.i = 0

    def error(self, message: str) -> SNBTError:
        line = self.text.count("\n", 0, self.i) + 1
        col = self.i - self.text.rfind("\n", 0, self.i)
        return SNBTError(f"line {line}, column {col}: {message}")

    def skip(self) -> None:
        while self.i < len(self.text):
            if self.text[self.i].isspace():
                self.i += 1
            elif self.text[self.i] == "#":
                end = self.text.find("\n", self.i)
                self.i = len(self.text) if end < 0 else end + 1
            else:
                break

    def peek(self) -> str:
        self.skip()
        return self.text[self.i] if self.i < len(self.text) else ""

    def parse(self) -> dict[str, Any]:
        value = self.value()
        self.skip()
        if self.i != len(self.text):
            raise self.error("trailing tokens")
        if not isinstance(value, dict):
            raise self.error("TeamData must be a compound")
        return value

    def value(self) -> Any:
        ch = self.peek()
        if ch == "{":
            return self.compound()
        if ch == "[":
            return self.array()
        if ch in "\"'":
            return self.string()
        start = self.i
        match = self._number.match(self.text, self.i)
        if match:
            self.i = match.end()
            return RawNumber(match.group(0))
        match = self._bare.match(self.text, self.i)
        if match:
            self.i = match.end()
            token = match.group(0)
            if token == "true":
                return True
            if token == "false":
                return False
            # Infinity/NaN and unquoted custom strings are not expected in
            # TeamData, but preserving them is safer than inventing a value.
            if token in {"Infinity", "-Infinity", "NaN", "NanF", "∞", "-∞", "∞F", "-∞F"}:
                return RawNumber(token)
            raise self.error(f"invalid bare value {token!r}")
        self.i = start
        raise self.error("expected a value")

    def string(self) -> str:
        quote = self.text[self.i]
        self.i += 1
        out: list[str] = []
        while self.i < len(self.text):
            ch = self.text[self.i]
            self.i += 1
            if ch == quote:
                return "".join(out)
            if ch == "\\" and self.i < len(self.text):
                esc = self.text[self.i]
                self.i += 1
                if esc == "u" and self.i + 4 <= len(self.text):
                    digits = self.text[self.i : self.i + 4]
                    if re.fullmatch(r"[0-9a-fA-F]{4}", digits):
                        out.append(chr(int(digits, 16)))
                        self.i += 4
                        continue
                out.append({"n": "\n", "r": "\r", "t": "\t"}.get(esc, esc))
            else:
                out.append(ch)
        raise self.error("unterminated string")

    def key(self) -> str:
        ch = self.peek()
        if ch in "\"'":
            return self.string()
        match = self._bare.match(self.text, self.i)
        if not match:
            raise self.error("expected a compound key")
        self.i = match.end()
        return match.group(0)

    def separator_or_end(self, closer: str) -> str:
        self.skip()
        if self.i >= len(self.text):
            raise self.error(f"missing {closer}")
        if self.text[self.i] == ",":
            self.i += 1
            return "comma"
        if self.text[self.i] == closer:
            self.i += 1
            return "end"
        # Newline-separated SNBT values are legal.  skip() already consumed
        # the newline, so accepting the next key/value is intentional.
        return "next"

    def compound(self) -> dict[str, Any]:
        assert self.peek() == "{"
        self.i += 1
        result: dict[str, Any] = {}
        self.skip()
        while self.peek() != "}":
            if not self.peek():
                raise self.error("unterminated compound")
            k = self.key()
            self.skip()
            if self.i >= len(self.text) or self.text[self.i] != ":":
                raise self.error("expected ':' after key")
            self.i += 1
            if k in result:
                raise self.error(f"duplicate compound key {k!r}")
            result[k] = self.value()
            sep = self.separator_or_end("}")
            if sep == "end":
                return result
            if sep == "comma":
                self.skip()
                if self.peek() == "}":
                    raise self.error("trailing comma")
        self.i += 1
        return result

    def array(self) -> list[Any] | TypedArray:
        assert self.peek() == "["
        self.i += 1
        self.skip()
        kind = ""
        save = self.i
        if self.text[self.i : self.i + 2] in {"B;", "I;", "L;"}:
            kind = self.text[self.i]
            self.i += 2
        else:
            self.i = save
        values: list[Any] = []
        self.skip()
        if self.peek() == "]":
            self.i += 1
            return TypedArray(kind, values) if kind else values
        while True:
            values.append(self.value())
            sep = self.separator_or_end("]")
            if sep == "end":
                return TypedArray(kind, values) if kind else values
            if sep == "comma":
                self.skip()
                if self.peek() == "]":
                    raise self.error("trailing comma")


def quote(value: str) -> str:
    return json.dumps(value, ensure_ascii=False, separators=(",", ":"))


def dump(value: Any, indent: int = 0) -> str:
    pad = "\t" * indent
    if isinstance(value, dict):
        if not value:
            return "{}"
        lines = ["{"]
        for key, item in value.items():
            lines.append(f"\t{pad}{quote(str(key))}: {dump(item, indent + 1)}")
        lines.append(f"{pad}}}")
        return "\n".join(lines)
    if isinstance(value, TypedArray):
        prefix = f"{value.kind};" if value.kind else ""
        return "[" + prefix + ", ".join(dump(v, indent) for v in value.values) + "]"
    if isinstance(value, list):
        if not value:
            return "[ ]"
        return "[" + ", ".join(dump(v, indent) for v in value) + "]"
    if isinstance(value, str):
        return quote(value)
    if isinstance(value, RawNumber):
        return value.raw
    if isinstance(value, bool):
        return "true" if value else "false"
    if value is None:
        raise TypeError("SNBT has no null value")
    return str(value)


ZERO_UUID = "0" * 32
CLAIM_KEY = re.compile(r"^(?P<uuid>[0-9a-fA-F]{32}):(?P<id>.+)$")


def _lookup(mapping: dict[str, str], key: str) -> str:
    return mapping.get(key, mapping.get(key.upper(), mapping.get(key.lower(), key)))


def _id_maps(spec: dict[str, Any]) -> tuple[dict[str, str], dict[str, str], dict[str, str]]:
    def read(name: str) -> dict[str, str]:
        raw = spec.get(name, {})
        if not isinstance(raw, dict) or not all(isinstance(k, str) and isinstance(v, str) for k, v in raw.items()):
            raise ValueError(f"mapping field {name!r} must be an object of string IDs")
        return dict(raw)
    return read("quest_ids"), read("task_ids"), read("reward_ids")


def _merge_value(existing: Any, incoming: Any, field: str) -> Any:
    """Merge collisions conservatively when two old IDs map to one ID."""
    def as_int(value: RawNumber) -> int:
        return int(re.sub(r"[bBsSlLfFdD]$", "", value.raw))

    def suffix(value: RawNumber) -> str:
        match = re.search(r"([bBsSlLfFdD])$", value.raw)
        return match.group(1) if match else ""

    def number(value: int, left: RawNumber, right: RawNumber) -> RawNumber:
        # TeamData timestamps and progress counters are persisted as longs.
        # If either colliding value is explicitly long, keep the merged value
        # explicitly long instead of silently changing its NBT type.
        left_suffix, right_suffix = suffix(left), suffix(right)
        selected = "L" if "L" in {left_suffix.upper(), right_suffix.upper()} else left_suffix or right_suffix
        return RawNumber(f"{value}{selected}")

    if field in {"task_progress", "completion_count"}:
        return number(max(as_int(existing), as_int(incoming)), existing, incoming)
    if field in {"started", "completed"}:
        return number(min(as_int(existing), as_int(incoming)), existing, incoming)
    if field == "repeatable":
        return number(max(as_int(existing), as_int(incoming)), existing, incoming)
    return existing


def transform(data: dict[str, Any], spec: dict[str, Any]) -> dict[str, Any]:
    quest_ids, task_ids, reward_ids = _id_maps(spec)
    out = data.copy()

    for field, mapping in (("task_progress", task_ids), ("started", quest_ids), ("completed", quest_ids), ("repeatable", quest_ids), ("completion_count", quest_ids)):
        source = data.get(field)
        if not isinstance(source, dict):
            continue
        target: dict[str, Any] = {}
        for key, value in source.items():
            new_key = _lookup(mapping, key)
            target[new_key] = _merge_value(target[new_key], value, field) if new_key in target else value
        out[field] = target

    player_data = data.get("player_data")
    if isinstance(player_data, dict):
        player_out = {}
        for player, pdata in player_data.items():
            pdata_out = dict(pdata) if isinstance(pdata, dict) else pdata
            if isinstance(pdata_out, dict) and isinstance(pdata_out.get("pinned_quests"), (list, TypedArray)):
                pinned = pdata_out["pinned_quests"]
                values = [ _lookup(quest_ids, v) if isinstance(v, str) else v for v in pinned.values ] if isinstance(pinned, TypedArray) else [ _lookup(quest_ids, v) if isinstance(v, str) else v for v in pinned ]
                pdata_out["pinned_quests"] = TypedArray(pinned.kind, values) if isinstance(pinned, TypedArray) else values
            player_out[player] = pdata_out
        out["player_data"] = player_out

    transitions = spec.get("scope_transitions", [])
    if not isinstance(transitions, list):
        raise ValueError("scope_transitions must be a list")
    transition_by_old: dict[str, dict[str, str]] = {}
    for item in transitions:
        if not isinstance(item, dict) or not isinstance(item.get("old_reward_id"), str):
            raise ValueError("each scope transition needs old_reward_id")
        old = item["old_reward_id"]
        new = item.get("new_reward_id", _lookup(reward_ids, old))
        if not isinstance(new, str):
            raise ValueError("scope transition new_reward_id must be a string")
        source_scope = item.get("from", "personal")
        target_scope = item.get("to", "shared")
        if source_scope not in {"personal", "shared"} or target_scope not in {"personal", "shared"}:
            raise ValueError("scope transition from/to must be personal or shared")
        if source_scope == "shared" and target_scope == "personal":
            raise ValueError(f"cannot infer a player UUID for shared -> personal reward {old}")
        if old in transition_by_old:
            raise ValueError(f"duplicate scope transition for reward {old}")
        transition_by_old[old] = {"new": new, "from": source_scope, "to": target_scope}

    copies = spec.get("reward_claim_copies", {})
    if not isinstance(copies, dict):
        raise ValueError("reward_claim_copies must be an object of old ID to non-empty ID arrays")
    copies_by_old: dict[str, list[str]] = {}
    for old, targets in copies.items():
        if not isinstance(old, str) or not isinstance(targets, list) or not targets or not all(isinstance(target, str) and target for target in targets):
            raise ValueError("reward_claim_copies values must be non-empty arrays of string IDs")
        if old in copies_by_old:
            raise ValueError(f"duplicate reward_claim_copies entry for reward {old}")
        if len(set(targets)) != len(targets):
            raise ValueError(f"duplicate target in reward_claim_copies for reward {old}")
        copies_by_old[old] = targets

    claims = data.get("claimed_rewards")
    if isinstance(claims, dict):
        target_claims: dict[str, Any] = {}
        for raw_key, value in claims.items():
            match = CLAIM_KEY.match(raw_key)
            if not match:
                raise ValueError(f"invalid claimed_rewards key {raw_key!r}; expected compact-uuid:id")
            uuid, old_id = match.group("uuid").lower(), match.group("id")
            transition = transition_by_old.get(old_id) or transition_by_old.get(old_id.upper()) or transition_by_old.get(old_id.lower())
            copy_targets = copies_by_old.get(old_id) or copies_by_old.get(old_id.upper()) or copies_by_old.get(old_id.lower())
            target_ids = copy_targets or [_lookup(reward_ids, old_id)]
            target_uuid = uuid
            if transition:
                if transition["to"] == "shared":
                    target_uuid = ZERO_UUID
                elif transition["to"] == "personal" and uuid == ZERO_UUID:
                    raise ValueError(f"cannot infer player UUID for shared claim {raw_key!r}")
            for new_id in target_ids:
                new_key = f"{target_uuid}:{new_id}"
                if new_key in target_claims:
                    # A shared transition or claim fanout must retain the
                    # earliest historical timestamp; the reward is already
                    # claimed either way. Preserve an explicit long suffix.
                    old_value = target_claims[new_key]
                    old_timestamp = int(re.sub(r"[bBsSlLfFdD]$", "", old_value.raw))
                    new_timestamp = int(re.sub(r"[bBsSlLfFdD]$", "", value.raw))
                    old_suffix = "L" if re.search(r"[lL]$", old_value.raw) else ""
                    new_suffix = "L" if re.search(r"[lL]$", value.raw) else ""
                    target_claims[new_key] = RawNumber(f"{min(old_timestamp, new_timestamp)}{('L' if old_suffix or new_suffix else '')}")
                else:
                    target_claims[new_key] = value
        out["claimed_rewards"] = target_claims
    return out


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def apply_atomic(path: Path, content: str, expected: str, backup: Path | None) -> Path:
    actual = sha256(path)
    if actual.lower() != expected.lower():
        raise RuntimeError(f"sha256 precondition failed: expected {expected}, found {actual}")
    backup_path = backup or path.with_name(path.name + ".bak")
    if backup_path.exists():
        raise RuntimeError(f"refusing to overwrite existing backup {backup_path}")
    shutil.copy2(path, backup_path)
    fd, temp_name = tempfile.mkstemp(prefix=f".{path.name}.", suffix=".tmp", dir=str(path.parent))
    try:
        with os.fdopen(fd, "w", encoding="utf-8", newline="\n") as handle:
            handle.write(content)
            handle.flush()
            os.fsync(handle.fileno())
        # The expected hash was checked before backup creation. Recheck after
        # staging the candidate so an external edit during the operation
        # cannot be overwritten by the atomic replace.
        current = sha256(path)
        if current.lower() != expected.lower():
            raise RuntimeError(f"sha256 precondition changed during migration: expected {expected}, found {current}")
        os.replace(temp_name, path)
    finally:
        if os.path.exists(temp_name):
            os.unlink(temp_name)
    return backup_path


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("input", type=Path, help="TeamData SNBT export/file")
    ap.add_argument("--mapping", type=Path, required=True, help="reviewed JSON ID/scope mapping")
    ap.add_argument("--apply", action="store_true", help="replace input (requires --expected-sha256)")
    ap.add_argument("--expected-sha256", help="required source hash for --apply")
    ap.add_argument("--backup", type=Path, help="backup path (default: INPUT.bak)")
    ap.add_argument("--output", type=Path, help="write transformed candidate here; never writes input unless --apply")
    args = ap.parse_args(argv)
    try:
        original = args.input.read_text(encoding="utf-8")
        data = Parser(original).parse()
        spec = json.loads(args.mapping.read_text(encoding="utf-8"))
        if not isinstance(spec, dict):
            raise ValueError("mapping root must be an object")
        migrated = transform(data, spec)
        candidate = dump(migrated) + "\n"
        report = {
            "input": str(args.input),
            "input_sha256": sha256(args.input),
            "dry_run": not args.apply,
            "changed": candidate != original,
            "output": str(args.output) if args.output else (str(args.input) if args.apply else None),
        }
        if args.apply:
            if not args.expected_sha256:
                raise ValueError("--apply requires --expected-sha256")
            backup = apply_atomic(args.input, candidate, args.expected_sha256, args.backup)
            report["backup"] = str(backup)
            report["output_sha256"] = sha256(args.input)
        elif args.output:
            args.output.write_text(candidate, encoding="utf-8", newline="\n")
            report["output_sha256"] = sha256(args.output)
        print(json.dumps(report, indent=2))
        return 0
    except (OSError, ValueError, SNBTError, RuntimeError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
