#!/usr/bin/env python3
"""Merge root-level SNBT localization entries from reviewed fragments.

Fragments deliberately omit the outer compound so parallel chapter authors can
own independent files. Existing keys are replaced in place; new keys are added
before the root compound's closing brace. The script preserves unrelated
localization and supports a check-only idempotency pass.
"""

from __future__ import annotations

import argparse
import re
from pathlib import Path


KEY = re.compile(r"^([A-Za-z0-9_.]+):\s*")
ROOT_KEY = re.compile(r"^\t([A-Za-z0-9_.]+):\s*")


def bracket_delta(text: str) -> int:
    """Count square brackets outside quoted strings."""
    delta = 0
    quote: str | None = None
    escaped = False
    for char in text:
        if escaped:
            escaped = False
            continue
        if char == "\\" and quote is not None:
            escaped = True
            continue
        if quote is not None:
            if char == quote:
                quote = None
            continue
        if char in {'"', "'"}:
            quote = char
        elif char == "[":
            delta += 1
        elif char == "]":
            delta -= 1
    return delta


def read_fragment(path: Path) -> dict[str, list[str]]:
    lines = path.read_text(encoding="utf-8").splitlines()
    entries: dict[str, list[str]] = {}
    i = 0
    while i < len(lines):
        line = lines[i]
        stripped = line.strip()
        if not stripped or stripped.startswith(('#', '//')) or stripped in {'{', '}'}:
            i += 1
            continue
        base_indent = len(line) - len(line.lstrip())
        match = KEY.match(line.lstrip())
        if not match:
            raise ValueError(f"{path}:{i + 1}: expected a root localization key")
        key = match.group(1)
        block = [line[base_indent:].rstrip(',')]
        balance = bracket_delta(line)
        while balance > 0:
            i += 1
            if i >= len(lines):
                raise ValueError(f"{path}: unterminated list for {key}")
            nested = lines[i]
            if base_indent and len(nested) >= base_indent and nested[:base_indent].isspace():
                nested = nested[base_indent:]
            block.append(nested.rstrip(','))
            balance += bracket_delta(lines[i])
        if balance != 0:
            raise ValueError(f"{path}:{i + 1}: unbalanced list for {key}")
        if key in entries:
            raise ValueError(f"{path}: duplicate key {key}")
        entries[key] = block
        i += 1
    return entries


def merge(root_text: str, replacements: dict[str, list[str]]) -> str:
    lines = root_text.splitlines()
    starts: list[tuple[int, str]] = []
    for index, line in enumerate(lines):
        match = ROOT_KEY.match(line)
        if match:
            starts.append((index, match.group(1)))
    if not lines or lines[-1].strip() != "}":
        raise ValueError("language file must be one root compound ending with }")

    ranges: dict[str, tuple[int, int]] = {}
    for pos, (start, key) in enumerate(starts):
        end = starts[pos + 1][0] if pos + 1 < len(starts) else len(lines) - 1
        ranges[key] = (start, end)

    def indent(block: list[str]) -> list[str]:
        return ["\t" + line for line in block]

    out: list[str] = []
    cursor = 0
    applied: set[str] = set()
    for start, key in starts:
        if start < cursor:
            continue
        end = ranges[key][1]
        out.extend(lines[cursor:start])
        if key in replacements:
            out.extend(indent(replacements[key]))
            applied.add(key)
        else:
            out.extend(lines[start:end])
        cursor = end
    out.extend(lines[cursor:-1])

    new_keys = sorted(set(replacements) - applied)
    for key in new_keys:
        out.extend(indent(replacements[key]))
    out.append("}")
    return "\n".join(out) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("root", type=Path, nargs="?", default=Path("."))
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    root = args.root.resolve()
    lang_path = root / "config/ftbquests/quests/lang/en_us.snbt"
    fragment_dir = root / "docs/vvh/implementation_fragments"
    fragments = sorted(fragment_dir.glob("critical_*_lang.snbtfrag"))
    if not fragments:
        raise SystemExit("no critical localization fragments found")

    replacements: dict[str, list[str]] = {}
    owners: dict[str, Path] = {}
    for fragment in fragments:
        for key, block in read_fragment(fragment).items():
            if key in replacements:
                raise ValueError(f"duplicate key {key} in {owners[key]} and {fragment}")
            replacements[key] = block
            owners[key] = fragment

    current = lang_path.read_text(encoding="utf-8")
    rendered = merge(current, replacements)
    if args.check:
        if rendered != current:
            print(f"localization is stale for {len(replacements)} fragment keys")
            return 1
        print(f"localization contains {len(replacements)} synchronized fragment keys")
        return 0
    lang_path.write_text(rendered, encoding="utf-8")
    print(f"merged {len(replacements)} keys from {len(fragments)} fragments into {lang_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
