#!/usr/bin/env python3
"""Synchronize campaign ID evidence with the live Packwiz manifest.

The existing catalog supplies direct JAR-entry evidence, but an entry is kept
only when its source JAR is the exact filename pinned by an indexed .pw.toml.
This prevents unrelated or stale downloaded JARs from proving pack content.
"""
from __future__ import annotations

import argparse
import json
import sys
import tomllib
from pathlib import Path
from typing import Any

SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

from vvh_validate import Parser  # noqa: E402


NAMESPACE_METADATA = {
    "create": "mods/create.pw.toml",
    "explorerscompass": "mods/explorers-compass.pw.toml",
    "exposure": "mods/exposure.pw.toml",
    "irons_spellbooks": "mods/irons-spells-n-spellbooks.pw.toml",
    "numismatics": "mods/numismatics.pw.toml",
    "vampirism": "mods/vampirism.pw.toml",
}

EXTRA_ITEM_EVIDENCE = {
    "explorerscompass:explorerscompass": {
        "display_name": "Explorer's Compass",
        "source_entry": (
            "assets/explorerscompass/models/item/explorerscompass.json; "
            "data/explorerscompass/recipe/explorers_compass.json"
        ),
    },
    "exposure:album": {
        "display_name": "Photo Album",
        "source_entry": "assets/exposure/lang/en_us.json::item.exposure.album",
    },
    "exposure:black_and_white_film": {
        "display_name": "Black and White Film",
        "source_entry": "assets/exposure/lang/en_us.json::item.exposure.black_and_white_film",
    },
    "exposure:camera": {
        "display_name": "Camera",
        "source_entry": "assets/exposure/lang/en_us.json::item.exposure.camera",
    },
    "exposure:camera_stand": {
        "display_name": "Camera Stand",
        "source_entry": "assets/exposure/lang/en_us.json::item.exposure.camera_stand",
    },
    "exposure:color_film": {
        "display_name": "Color Film",
        "source_entry": "assets/exposure/models/item/color_film.json",
    },
    "exposure:high_sensitivity_color_film": {
        "display_name": "High-Sensitivity Color Film",
        "source_entry": (
            "assets/exposure/lang/en_us.json::item.exposure.high_sensitivity_color_film; "
            "data/exposure/recipe/high_sensitivity_color_film.json"
        ),
    },
    "exposure:photograph": {
        "display_name": "Photograph",
        "source_entry": "assets/exposure/lang/en_us.json::item.exposure.photograph",
    },
    "exposure:photograph_frame": {
        "display_name": "Photograph Frame",
        "source_entry": "assets/exposure/lang/en_us.json::item.exposure.photograph_frame",
    },
}

EXTRA_ADVANCEMENT_EVIDENCE = {
    "exposure:adventure/exposure": {
        "source_entry": "data/exposure/advancement/adventure/exposure.json",
    },
    "exposure:adventure/moment_in_time": {
        "source_entry": "data/exposure/advancement/adventure/moment_in_time.json",
    },
}


def item_id(value: Any) -> str | None:
    if isinstance(value, str):
        return value
    if isinstance(value, dict) and isinstance(value.get("id"), str):
        return value["id"]
    return None


def parse_live_snbt(path: Path) -> dict[str, Any]:
    text = path.read_text(encoding="utf-8").lstrip("\ufeff")
    value = Parser(text, str(path)).parse()
    if not isinstance(value, dict):
        raise ValueError(f"{path}: expected root compound")
    return value


def collect_live_references(root: Path) -> tuple[set[str], set[str], set[str]]:
    items: set[str] = set()
    advancements: set[str] = set()
    spells: set[str] = set()

    data = parse_live_snbt(root / "config/ftbquests/quests/data.snbt")
    if (iid := item_id(data.get("icon"))) is not None:
        items.add(iid)

    for path in sorted((root / "config/ftbquests/quests/chapters").glob("ch*.snbt")):
        chapter = parse_live_snbt(path)
        if (iid := item_id(chapter.get("icon"))) is not None:
            items.add(iid)
        for quest in chapter.get("quests", []):
            if (iid := item_id(quest.get("icon"))) is not None:
                items.add(iid)
            for task in quest.get("tasks", []):
                if (iid := item_id(task.get("item"))) is not None:
                    items.add(iid)
                if isinstance(task.get("advancement"), str):
                    advancements.add(task["advancement"])
            for reward in quest.get("rewards", []):
                stack = reward.get("item")
                if (iid := item_id(stack)) is not None:
                    items.add(iid)
                if not isinstance(stack, dict) or not isinstance(stack.get("components"), dict):
                    continue
                components = stack["components"]
                affinity = components.get("irons_spellbooks:affinity_data")
                if isinstance(affinity, dict) and isinstance(affinity.get("id"), str):
                    spells.add(affinity["id"])
                container = components.get("irons_spellbooks:spell_container")
                if isinstance(container, dict):
                    for slot in container.get("data", []):
                        if isinstance(slot, dict) and isinstance(slot.get("id"), str):
                            spells.add(slot["id"])
    return items, advancements, spells


def pack_membership(root: Path, namespaces: set[str]) -> dict[str, Any]:
    index = tomllib.loads((root / "index.toml").read_text(encoding="utf-8"))
    index_files = {entry["file"]: entry for entry in index.get("files", [])}
    proofs: dict[str, Any] = {}
    for namespace in sorted(namespaces):
        metadata_rel = NAMESPACE_METADATA.get(namespace)
        if metadata_rel is None:
            raise ValueError(f"no Packwiz metadata mapping for live namespace {namespace!r}")
        if metadata_rel not in index_files:
            raise ValueError(f"{namespace}: {metadata_rel} is not indexed by index.toml")
        metadata_path = root / metadata_rel
        metadata = tomllib.loads(metadata_path.read_text(encoding="utf-8"))
        download = metadata.get("download", {})
        if metadata.get("side", "both") == "client":
            raise ValueError(f"{namespace}: campaign content cannot come from client-only {metadata_rel}")
        proofs[namespace] = {
            "metadata": metadata_rel,
            "name": metadata.get("name"),
            "filename": metadata.get("filename"),
            "side": metadata.get("side", "both"),
            "download_hash_format": download.get("hash-format"),
            "download_hash": download.get("hash"),
            "index_sha256": index_files[metadata_rel].get("hash"),
        }
    return proofs


def synchronize(root: Path) -> dict[str, Any]:
    path = root / "docs/vvh/id_catalog.json"
    old = json.loads(path.read_text(encoding="utf-8"))
    items, advancements, spells = collect_live_references(root)
    non_vanilla_items = {iid for iid in items if not iid.startswith("minecraft:")}
    namespaces = {
        value.split(":", 1)[0]
        for value in (*non_vanilla_items, *advancements, *spells)
    }
    proofs = pack_membership(root, namespaces)
    old_items = {str(entry.get("id")): entry for entry in old.get("entries", [])}
    old_advancements = {
        str(entry.get("id")): entry
        for group in old.get("advancements", {}).values()
        for entry in group
    }
    old_spells = {str(entry.get("id")): entry for entry in old.get("spells", [])}

    entries: list[dict[str, Any]] = []
    for iid in sorted(non_vanilla_items):
        namespace = iid.split(":", 1)[0]
        entry = dict(old_items.get(iid, {}))
        if not entry:
            extra = EXTRA_ITEM_EVIDENCE.get(iid)
            if extra is None:
                raise ValueError(f"missing direct item evidence for {iid}")
            entry = {"namespace": namespace, "id": iid, **extra, "obtainability_note": ""}
        expected_jar = proofs[namespace]["filename"]
        entry["source_jar"] = entry.get("source_jar") or expected_jar
        if entry.get("source_jar") != expected_jar:
            raise ValueError(
                f"{iid}: evidence JAR {entry.get('source_jar')!r} is not current Packwiz JAR {expected_jar!r}"
            )
        if not entry.get("source_entry"):
            raise ValueError(f"{iid}: direct JAR entry evidence is empty")
        entries.append(entry)

    advancement_entries: list[dict[str, Any]] = []
    for aid in sorted(advancements):
        namespace = aid.split(":", 1)[0]
        entry = dict(old_advancements.get(aid, {}))
        if not entry:
            extra = EXTRA_ADVANCEMENT_EVIDENCE.get(aid)
            if extra is None:
                raise ValueError(f"missing direct advancement evidence for {aid}")
            entry = {"id": aid, **extra}
        expected_jar = proofs[namespace]["filename"]
        entry["source_jar"] = entry.get("source_jar") or expected_jar
        if entry.get("source_jar") != expected_jar:
            raise ValueError(
                f"{aid}: evidence JAR {entry.get('source_jar')!r} is not current Packwiz JAR {expected_jar!r}"
            )
        advancement_entries.append(entry)

    spell_entries: list[dict[str, Any]] = []
    for sid in sorted(spells):
        entry = dict(old_spells.get(sid, {}))
        if not entry:
            raise ValueError(f"missing direct spell evidence for {sid}")
        expected_jar = proofs[sid.split(":", 1)[0]]["filename"]
        if entry.get("source_jar") != expected_jar:
            raise ValueError(
                f"{sid}: evidence JAR {entry.get('source_jar')!r} is not current Packwiz JAR {expected_jar!r}"
            )
        spell_entries.append(entry)

    return {
        "generated_from": "Live ch*.snbt references bound to current indexed Packwiz metadata and exact JAR-entry evidence.",
        "verification_scope": "Campaign-used non-vanilla IDs only; unrelated downloaded JARs are excluded.",
        "verified_namespaces": sorted(namespaces),
        "unverified_namespaces": [],
        "pack_membership": {
            "index": "index.toml",
            "namespaces": proofs,
        },
        "entries": entries,
        "advancements": {"campaign": advancement_entries},
        "spells": spell_entries,
        "numismatics_denominations": old.get("numismatics_denominations", {}),
        "ftb_quests": old.get("ftb_quests", {}),
    }


def render_markdown(catalog: dict[str, Any]) -> str:
    lines = [
        "# VvH Current-Pack ID Catalog",
        "",
        "This catalog contains only IDs referenced by the live six-chapter campaign. "
        "Every non-vanilla namespace must be backed by a `.pw.toml` that is present in "
        "the current `index.toml`, and every evidence JAR must match that metadata's exact filename.",
        "",
        "An unrelated downloaded JAR is not proof that a mod is installed. Run "
        "`python -B -X utf8 scripts/vvh_sync_catalog.py --check .` before release.",
        "",
        "## Pack membership",
        "",
        "| Namespace | Indexed metadata | Pinned JAR | Side | Download hash |",
        "| --- | --- | --- | --- | --- |",
    ]
    proofs = catalog["pack_membership"]["namespaces"]
    for namespace, proof in proofs.items():
        digest = str(proof.get("download_hash", ""))
        lines.append(
            f"| `{namespace}` | `{proof['metadata']}` | `{proof['filename']}` | "
            f"`{proof['side']}` | `{proof.get('download_hash_format')}:{digest}` |"
        )

    lines.extend(
        [
            "",
            "## Campaign items and icons",
            "",
            "| Namespace | ID | Display name | Exact evidence JAR | JAR entry evidence |",
            "| --- | --- | --- | --- | --- |",
        ]
    )
    for entry in catalog["entries"]:
        lines.append(
            f"| `{entry['namespace']}` | `{entry['id']}` | {entry.get('display_name', '')} | "
            f"`{entry['source_jar']}` | `{entry['source_entry']}` |"
        )

    lines.extend(
        [
            "",
            "## Campaign advancements",
            "",
            "| ID | Exact evidence JAR | JAR entry evidence |",
            "| --- | --- | --- |",
        ]
    )
    for entry in catalog["advancements"]["campaign"]:
        lines.append(f"| `{entry['id']}` | `{entry['source_jar']}` | `{entry['source_entry']}` |")

    lines.extend(
        [
            "",
            "## Campaign spell IDs",
            "",
            "| ID | School | Exact evidence JAR | JAR entry evidence |",
            "| --- | --- | --- | --- |",
        ]
    )
    for entry in catalog["spells"]:
        lines.append(
            f"| `{entry['id']}` | {entry.get('school', '')} | `{entry['source_jar']}` | "
            f"`{entry['source_entry']}` |"
        )

    lines.extend(
        [
            "",
            "## FTB Quests schema observations",
            "",
            f"- Installed evidence JAR: `{catalog['ftb_quests'].get('installed_filename', '')}`",
            "- Observed task/reward types: "
            + ", ".join(f"`{value}`" for value in catalog["ftb_quests"].get("task_types_observed", [])),
            "",
            "Vanilla `minecraft:*` IDs are outside this campaign-scoped catalog. Runtime/client checks "
            "remain separate from static Packwiz membership and JAR-entry proof.",
            "",
        ]
    )
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("root", type=Path, nargs="?", default=Path("."))
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    root = args.root.resolve()
    path = root / "docs/vvh/id_catalog.json"
    markdown_path = root / "docs/vvh/ID_CATALOG.md"
    catalog = synchronize(root)
    rendered = json.dumps(catalog, indent=2, ensure_ascii=False) + "\n"
    markdown = render_markdown(catalog)
    current = path.read_text(encoding="utf-8")
    if args.check:
        stale: list[str] = []
        if current != rendered:
            stale.append(str(path))
        if markdown_path.read_text(encoding="utf-8") != markdown:
            stale.append(str(markdown_path))
        if stale:
            print("campaign ID catalog is stale: " + ", ".join(stale))
            return 1
        print("campaign ID catalog is synchronized with Packwiz")
        return 0
    path.write_text(rendered, encoding="utf-8")
    markdown_path.write_text(markdown, encoding="utf-8")
    print(f"synchronized {path} and {markdown_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
