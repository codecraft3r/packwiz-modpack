#!/usr/bin/env python3
"""Synchronize the VvH campaign manifest from the live SNBT and localization.

This intentionally does not regenerate quest chapters or prose. The authored
SNBT/localization are the source of truth; the manifest is validation input.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parent))
from vvh_validate import parse_snbt  # noqa: E402


COLOR = re.compile(r"&.")


def item_id(value: Any) -> str | None:
    if isinstance(value, str):
        return value
    if isinstance(value, dict):
        raw = value.get("id")
        return raw if isinstance(raw, str) else None
    return None


def normalize_task(task: dict[str, Any], lang: dict[str, Any]) -> dict[str, Any]:
    count = task.get("count", 1)
    return {
        "advancement": task.get("advancement"),
        "consume": bool(task.get("consume", task.get("consume_items", False))),
        "count": count if isinstance(count, int) else 1,
        "criterion": task.get("criterion", ""),
        "id": task["id"],
        "item": item_id(task.get("item")),
        "optional": bool(task.get("optional", False)),
        "stat": task.get("stat"),
        "title": lang.get(f"task.{task['id']}.title", ""),
        "type": task.get("type", "checkmark"),
        "value": task.get("value", 1),
    }


def synchronize(root: Path) -> dict[str, Any]:
    manifest_path = root / "docs/vvh/campaign_manifest.json"
    existing = json.loads(manifest_path.read_text(encoding="utf-8"))
    existing_chapters = {chapter["id"]: chapter for chapter in existing["chapters"]}
    lang = parse_snbt(root / "config/ftbquests/quests/lang/en_us.snbt")
    chapters: list[dict[str, Any]] = []

    for path in sorted((root / "config/ftbquests/quests/chapters").glob("vvh_*.snbt")):
        source = parse_snbt(path)
        chapter_id = source["id"]
        old = existing_chapters.get(chapter_id, {})
        quests: list[dict[str, Any]] = []
        for quest in source.get("quests", []):
            quest_id = quest["id"]
            raw_title = lang.get(f"quest.{quest_id}.title", quest_id)
            quests.append(
                {
                    "dependencies": quest.get("dependencies", []),
                    "description": lang.get(f"quest.{quest_id}.quest_desc", []),
                    "hide_dependency_lines": bool(quest.get("hide_dependency_lines", False)),
                    "icon": item_id(quest.get("icon")),
                    "id": quest_id,
                    "min_required_dependencies": quest.get("min_required_dependencies", 0),
                    "optional": bool(quest.get("optional", False)),
                    "repeat_cooldown": quest.get("repeat_cooldown", 0),
                    "repeatable": bool(quest.get("can_repeat", False)),
                    "rewards": quest.get("rewards", []),
                    "shape": quest.get("shape", source.get("default_quest_shape", "circle")),
                    "size": quest.get("size", 1.0),
                    "subtitle": lang.get(f"quest.{quest_id}.quest_subtitle", ""),
                    "tasks": [normalize_task(task, lang) for task in quest.get("tasks", [])],
                    "title": COLOR.sub("", raw_title),
                    "x": quest.get("x", 0),
                    "y": quest.get("y", 0),
                    "can_repeat": bool(quest.get("can_repeat", False)),
                }
            )
        chapters.append(
            {
                "filename": source.get("filename", path.stem),
                "icon": item_id(source.get("icon")),
                "id": chapter_id,
                "images": source.get("images", []),
                "order": source.get("order_index", old.get("order", 0)),
                "quests": quests,
                "title": lang.get(f"chapter.{chapter_id}.title", old.get("title", chapter_id)),
            }
        )

    existing["chapters"] = chapters
    return existing


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("root", type=Path, nargs="?", default=Path("."))
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    root = args.root.resolve()
    path = root / "docs/vvh/campaign_manifest.json"
    rendered = json.dumps(synchronize(root), indent=2, ensure_ascii=False) + "\n"
    current = path.read_text(encoding="utf-8")
    if args.check:
        if current != rendered:
            print("campaign manifest is stale")
            return 1
        print("campaign manifest is synchronized")
        return 0
    path.write_text(rendered, encoding="utf-8")
    print(f"synchronized {path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
