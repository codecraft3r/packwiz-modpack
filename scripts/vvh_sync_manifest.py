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


def localized_or_inline(
    source: dict[str, Any],
    field: str,
    lang: dict[str, Any],
    translation_key: str,
    default: Any,
) -> Any:
    """Prefer authored inline copy, with localization as a compatibility fallback."""
    inline = source.get(field)
    if inline is not None:
        return inline
    return lang.get(translation_key, default)


def normalize_task(task: dict[str, Any], lang: dict[str, Any]) -> dict[str, Any]:
    item = task.get("item")
    nested_count = item.get("count", 1) if isinstance(item, dict) else 1
    count = task.get("count", nested_count)
    return {
        "advancement": task.get("advancement"),
        "consume": bool(task.get("consume", task.get("consume_items", False))),
        "count": count if isinstance(count, int) else 1,
        "criterion": task.get("criterion", ""),
        "id": task["id"],
        "item": item_id(task.get("item")),
        "optional": bool(task.get("optional", False)),
        "stat": task.get("stat"),
        "title": localized_or_inline(
            task,
            "title",
            lang,
            f"task.{task['id']}.title",
            "",
        ),
        "type": task.get("type", "checkmark"),
        "value": task.get("value", 1),
    }


def normalized_ftb_id(value: Any) -> str | None:
    if isinstance(value, int):
        return f"{value:016X}"
    if isinstance(value, str):
        return value.upper()
    return None


def synchronize(root: Path) -> dict[str, Any]:
    manifest_path = root / "docs/vvh/campaign_manifest.json"
    existing = json.loads(manifest_path.read_text(encoding="utf-8"))
    existing_chapters = {chapter["id"]: chapter for chapter in existing["chapters"]}
    lang = parse_snbt(root / "config/ftbquests/quests/lang/en_us.snbt")
    groups_source = parse_snbt(root / "config/ftbquests/quests/chapter_groups.snbt")
    chapter_groups = groups_source.get("chapter_groups", [])
    chapters: list[dict[str, Any]] = []
    referenced_reward_tables: set[str] = set()

    for path in sorted((root / "config/ftbquests/quests/chapters").glob("ch*.snbt")):
        source = parse_snbt(path)
        chapter_id = source["id"]
        old = existing_chapters.get(chapter_id, {})
        quests: list[dict[str, Any]] = []
        for quest in source.get("quests", []):
            quest_id = quest["id"]
            for reward in quest.get("rewards", []):
                if isinstance(reward, dict) and reward.get("type") == "choice":
                    table_id = normalized_ftb_id(reward.get("table_id"))
                    if table_id:
                        referenced_reward_tables.add(table_id)
            raw_title = localized_or_inline(
                quest,
                "title",
                lang,
                f"quest.{quest_id}.title",
                quest_id,
            )
            quests.append(
                {
                    "dependencies": quest.get("dependencies", []),
                    "description": localized_or_inline(
                        quest,
                        "description",
                        lang,
                        f"quest.{quest_id}.quest_desc",
                        [],
                    ),
                    "hide_dependency_lines": bool(quest.get("hide_dependency_lines", False)),
                    "hide_until_deps_complete": bool(quest.get("hide_until_deps_complete", False)),
                    "icon": item_id(quest.get("icon")),
                    "id": quest_id,
                    "min_required_dependencies": quest.get("min_required_dependencies", 0),
                    "optional": bool(quest.get("optional", False)),
                    "repeat_cooldown": quest.get("repeat_cooldown", 0),
                    "repeatable": bool(quest.get("can_repeat", False)),
                    "rewards": quest.get("rewards", []),
                    "shape": quest.get("shape", source.get("default_quest_shape", "circle")),
                    "size": quest.get("size", 1.0),
                    "subtitle": localized_or_inline(
                        quest,
                        "subtitle",
                        lang,
                        f"quest.{quest_id}.quest_subtitle",
                        "",
                    ),
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
                "group": source.get("group"),
                "icon": item_id(source.get("icon")),
                "id": chapter_id,
                "images": source.get("images", []),
                "order": source.get("order_index", old.get("order", 0)),
                "quests": quests,
                "title": localized_or_inline(
                    source,
                    "title",
                    lang,
                    f"chapter.{chapter_id}.title",
                    old.get("title", chapter_id),
                ),
            }
        )

    existing["chapters"] = chapters
    existing["chapter_groups"] = chapter_groups
    reward_tables: list[dict[str, Any]] = []
    reward_tables_dir = root / "config/ftbquests/quests/reward_tables"
    for path in sorted(reward_tables_dir.glob("*.snbt")):
        source = parse_snbt(path)
        if normalized_ftb_id(source.get("id")) in referenced_reward_tables:
            reward_tables.append(source)
    existing["reward_tables"] = reward_tables
    if chapter_groups:
        # Retain the singular field for legacy tooling that treats it as the
        # campaign's entry group. Per-chapter membership is recorded above.
        existing["group_id"] = chapter_groups[0]["id"]
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
