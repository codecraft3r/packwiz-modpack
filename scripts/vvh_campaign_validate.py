#!/usr/bin/env python3
"""Read-only static validator for the six-chapter VvH campaign.

The working tree is not modified unless ``--output`` is supplied.  This script
uses the repository's structural SNBT validator, then parses the same files for
campaign-specific graph, copy, ID, criteria, repeatable, and economy checks.
It is deliberately narrower than ``vvh_validate.py``: the older validator is
for the retired ten-chapter campaign and has incompatible IDs/economy rules.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import subprocess
import sys
import tomllib
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable

SCRIPT_DIR = Path(__file__).resolve().parent
ROOT_DEFAULT = SCRIPT_DIR.parent
sys.dont_write_bytecode = True
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

from validate_snbt import validate_file  # noqa: E402
from vvh_validate import Parser, SNBTError  # noqa: E402


EXPECTED_CHAPTERS = (
    "ch01_intro_rules.snbt",
    "ch02_factions.snbt",
    "ch03_hunters.snbt",
    "ch04_vampires.snbt",
    "ch05_shared_horizons.snbt",
    "ch06_requisitions.snbt",
)
EXPECTED_QUEST_COUNTS = {
    EXPECTED_CHAPTERS[0]: 4,
    EXPECTED_CHAPTERS[1]: 4,
    EXPECTED_CHAPTERS[2]: 7,
    EXPECTED_CHAPTERS[3]: 7,
    EXPECTED_CHAPTERS[4]: 9,
    EXPECTED_CHAPTERS[5]: 6,
}
CH01_WELCOME = "7A11C0DE10000001"
CH01_CLAIMS = "7A11C0DE10000002"
CH01_RIVALRY = "7A11C0DE10000003"
CH01_TERMINAL = "7A11C0DE10000004"
CH02_OVERVIEW = "7A11C0DE20000001"
CH02_VAMPIRE = "7A11C0DE20000002"
CH02_HUNTER = "7A11C0DE20000003"
CH02_NEUTRAL = "7A11C0DE20000004"
BEVEL = "numismatics:bevel"
HEX_ID = re.compile(r"^[0-9A-F]{16}$")
WORD = re.compile(r"[A-Za-z0-9]+(?:['’][A-Za-z]+)?")
TRANSLATE_TAG = re.compile(r"\{translate:([A-Za-z0-9_.-]+)")
BARE_TRANSLATION = re.compile(r"^[a-z][a-z0-9_]*(?:\.[a-z0-9_]+){2,}$")
IMAGE_TAG = re.compile(r"\{image:([^}\s]+)")
FORBIDDEN_COPY = (
    (re.compile(r"\bbalanced\b", re.I), "balanced"),
    (re.compile(r"\bintentionally\b", re.I), "intentionally"),
    (re.compile(r"\bvalidator\b", re.I), "validator"),
    (re.compile(r"\bdesign goal\b", re.I), "design goal"),
    (re.compile(r"\badmin note\b", re.I), "admin note"),
    (re.compile(r"\bseason finale\b", re.I), "season finale"),
    (re.compile(r"\bwipe\b", re.I), "wipe"),
)
PLAYER_META_COPY = (
    (re.compile(r"\bterminal gate\b", re.I), "Terminal gate"),
    (re.compile(r"\bnative gate\b", re.I), "Native gate"),
    (re.compile(r"\bcore\s+t[1-4]\b", re.I), "Core T1/T2/T3/T4"),
)
HARD_TASK_TYPES = {"advancement", "item"}
CHECKMARK_ALLOWLIST = {
    CH01_WELCOME,
    CH01_CLAIMS,
    CH01_RIVALRY,
    CH01_TERMINAL,
    CH02_OVERVIEW,
    CH02_NEUTRAL,
    "7A11C0DE50000009",  # witnessed public-build capstone
    "7A11C0DE60000001",  # explanatory sink-board opener
}
CH04_CULTIST_SET = {
    "irons_spellbooks:cultist_helmet",
    "irons_spellbooks:cultist_chestplate",
    "irons_spellbooks:cultist_leggings",
    "irons_spellbooks:cultist_boots",
}


def rel(path: Path, root: Path) -> str:
    try:
        return path.resolve().relative_to(root.resolve()).as_posix()
    except ValueError:
        return str(path.resolve())


def flatten_strings(value: Any) -> Iterable[str]:
    if isinstance(value, str):
        yield value
    elif isinstance(value, list):
        for item in value:
            yield from flatten_strings(item)


def player_texts(chapter: dict[str, Any]) -> Iterable[tuple[str, str]]:
    chapter_id = str(chapter.get("id", "<chapter>"))
    for field in ("title", "subtitle", "description"):
        for text in flatten_strings(chapter.get(field)):
            yield f"{chapter_id}.{field}", text
    for quest in chapter.get("quests", []):
        qid = str(quest.get("id", "<quest>"))
        for field in ("title", "subtitle", "description"):
            for text in flatten_strings(quest.get(field)):
                yield f"{qid}.{field}", text
        for kind in ("tasks", "rewards"):
            for obj in quest.get(kind, []):
                for field in ("title", "subtitle", "description"):
                    for text in flatten_strings(obj.get(field)):
                        yield f"{qid}.{kind}.{obj.get('id', '<missing>')}.{field}", text


def item_id(obj: Any) -> str | None:
    if isinstance(obj, str):
        return obj
    if isinstance(obj, dict):
        value = obj.get("id")
        return value if isinstance(value, str) else None
    return None


def item_count(obj: Any) -> int:
    if isinstance(obj, dict):
        try:
            return int(obj.get("count", 1))
        except (TypeError, ValueError):
            return 0
    return 1


def direct_bevels(quest: dict[str, Any], *, team: bool | None = None) -> int:
    total = 0
    for reward in quest.get("rewards", []):
        if reward.get("type") != "item" or item_id(reward.get("item")) != BEVEL:
            continue
        is_team = reward.get("team_reward") is True
        if team is not None and is_team != team:
            continue
        total += item_count(reward.get("item"))
    return total


def task_items(quest: dict[str, Any]) -> set[str]:
    return {
        iid
        for task in quest.get("tasks", [])
        if task.get("type") == "item"
        for iid in [item_id(task.get("item"))]
        if iid
    }


def reward_items(quest: dict[str, Any]) -> set[str]:
    return {
        iid
        for reward in quest.get("rewards", [])
        if reward.get("type") == "item"
        for iid in [item_id(reward.get("item"))]
        if iid
    }


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def parse_semantic(path: Path) -> Any:
    """Parse FTB SNBT while preserving the structural validator's BOM tolerance."""
    text = path.read_text(encoding="utf-8")
    return Parser(text.lstrip("\ufeff"), str(path)).parse()


class Checks:
    def __init__(self) -> None:
        self.items: list[dict[str, Any]] = []

    def add(
        self,
        name: str,
        failures: Iterable[str] = (),
        *,
        details: dict[str, Any] | None = None,
        required: bool = True,
    ) -> None:
        issues = list(failures)
        self.items.append(
            {
                "name": name,
                "required": required,
                "status": "pass" if not issues else "fail",
                "failures": issues,
                "details": details or {},
            }
        )

    @property
    def failed_required(self) -> list[dict[str, Any]]:
        return [c for c in self.items if c["required"] and c["status"] == "fail"]


def run(root: Path, output: Path | None) -> tuple[dict[str, Any], int]:
    root = root.resolve()
    chapters_dir = root / "config/ftbquests/quests/chapters"
    groups_path = root / "config/ftbquests/quests/chapter_groups.snbt"
    data_path = root / "config/ftbquests/quests/data.snbt"
    lang_path = root / "config/ftbquests/quests/lang/en_us.snbt"
    catalog_path = root / "docs/vvh/id_catalog.json"
    chapter_paths = [chapters_dir / name for name in EXPECTED_CHAPTERS]
    checks = Checks()

    actual_files = sorted(p.name for p in chapters_dir.glob("*.snbt")) if chapters_dir.exists() else []
    expected_set = set(EXPECTED_CHAPTERS)
    exact_failures: list[str] = []
    missing = sorted(expected_set - set(actual_files))
    extra = sorted(set(actual_files) - expected_set)
    if missing:
        exact_failures.append(f"missing chapter files: {missing}")
    if extra:
        exact_failures.append(f"unexpected chapter files: {extra}")
    checks.add(
        "exact_six_chapter_files",
        exact_failures,
        details={"expected": list(EXPECTED_CHAPTERS), "actual": actual_files},
    )

    parse_targets = [*chapter_paths, groups_path, data_path, lang_path]
    grammar_failures: list[str] = []
    parsed: dict[Path, Any] = {}
    for path in parse_targets:
        if not path.exists():
            grammar_failures.append(f"{rel(path, root)}: missing")
            continue
        result = validate_file(path)
        grammar_failures.extend(d.format(use_color=False) for d in result.diagnostics)
        if result.ok:
            try:
                parsed[path] = parse_semantic(path)
            except (SNBTError, OSError, UnicodeError) as exc:
                grammar_failures.append(f"{rel(path, root)}: semantic parser: {exc}")
    checks.add(
        "snbt_parse",
        grammar_failures,
        details={"files_checked": [rel(p, root) for p in parse_targets]},
    )

    chapters: dict[str, dict[str, Any]] = {
        path.name: value
        for path, value in parsed.items()
        if path in chapter_paths and isinstance(value, dict)
    }
    catalog: dict[str, Any] = {}
    catalog_failures: list[str] = []
    try:
        catalog = json.loads(catalog_path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        catalog_failures.append(f"{rel(catalog_path, root)}: {exc}")
    checks.add("id_catalog_json", catalog_failures)

    shape_failures: list[str] = []
    for name, expected in EXPECTED_QUEST_COUNTS.items():
        chapter = chapters.get(name)
        if chapter is None:
            shape_failures.append(f"{name}: unavailable after parse")
            continue
        actual = len(chapter.get("quests", []))
        if actual != expected:
            shape_failures.append(f"{name}: expected {expected} quests, found {actual}")
    checks.add(
        "campaign_shape",
        shape_failures,
        details={"expected_quest_counts": EXPECTED_QUEST_COUNTS},
    )

    quests: dict[str, dict[str, Any]] = {}
    quest_chapter: dict[str, str] = {}
    id_locations: list[tuple[str, str]] = []
    missing_id_failures: list[str] = []
    for filename, chapter in chapters.items():
        cid = chapter.get("id")
        if not isinstance(cid, str):
            missing_id_failures.append(f"{filename}: chapter id missing")
        else:
            id_locations.append((cid, f"{filename}:chapter"))
            if not HEX_ID.fullmatch(cid):
                missing_id_failures.append(f"{filename}: malformed chapter id {cid!r}")
        for qindex, quest in enumerate(chapter.get("quests", [])):
            qid = quest.get("id")
            if not isinstance(qid, str):
                missing_id_failures.append(f"{filename}: quest[{qindex}] id missing")
                continue
            id_locations.append((qid, f"{filename}:quest:{qid}"))
            quests[qid] = quest
            quest_chapter[qid] = filename
            if not HEX_ID.fullmatch(qid):
                missing_id_failures.append(f"{filename}: malformed quest id {qid!r}")
            for kind in ("tasks", "rewards"):
                for index, obj in enumerate(quest.get(kind, [])):
                    oid = obj.get("id")
                    if not isinstance(oid, str):
                        missing_id_failures.append(f"{qid}: {kind}[{index}] id missing")
                    else:
                        id_locations.append((oid, f"{filename}:{kind}:{qid}:{oid}"))
                        if not HEX_ID.fullmatch(oid):
                            missing_id_failures.append(f"{qid}: malformed {kind[:-1]} id {oid!r}")
    by_id: dict[str, list[str]] = defaultdict(list)
    for object_id, location in id_locations:
        by_id[object_id].append(location)
    duplicate_failures = [f"{object_id}: {locations}" for object_id, locations in by_id.items() if len(locations) > 1]
    checks.add(
        "global_unique_ids",
        [*missing_id_failures, *duplicate_failures],
        details={
            "chapter_quest_task_reward_ids": len(id_locations),
            "unique_ids": len(by_id),
        },
    )

    dependency_failures: list[str] = []
    dependencies: dict[str, list[str]] = {}
    for qid, quest in quests.items():
        deps = quest.get("dependencies", [])
        if not isinstance(deps, list):
            dependency_failures.append(f"{qid}: dependencies must be a list")
            deps = []
        dependencies[qid] = [str(dep) for dep in deps]
        for dep in dependencies[qid]:
            if dep not in quests:
                dependency_failures.append(f"{qid}: unresolved dependency {dep}")
    state: dict[str, int] = {}
    stack: list[str] = []

    def visit(qid: str) -> None:
        status = state.get(qid, 0)
        if status == 2:
            return
        if status == 1:
            start = stack.index(qid) if qid in stack else 0
            dependency_failures.append("dependency cycle: " + " -> ".join([*stack[start:], qid]))
            return
        state[qid] = 1
        stack.append(qid)
        for dep in dependencies.get(qid, []):
            if dep in quests:
                visit(dep)
        stack.pop()
        state[qid] = 2

    for qid in quests:
        visit(qid)
    checks.add("dependencies_resolve_and_acyclic", dependency_failures)

    ancestor_memo: dict[str, set[str]] = {}

    def ancestors(qid: str, active: set[str] | None = None) -> set[str]:
        if qid in ancestor_memo:
            return ancestor_memo[qid]
        active = set() if active is None else set(active)
        if qid in active:
            return set()
        active.add(qid)
        out: set[str] = set()
        for dep in dependencies.get(qid, []):
            out.add(dep)
            if dep in quests:
                out.update(ancestors(dep, active))
        ancestor_memo[qid] = out
        return out

    reach_failures: list[str] = []
    for qid, filename in quest_chapter.items():
        if filename == EXPECTED_CHAPTERS[0]:
            continue
        if CH01_TERMINAL not in ancestors(qid):
            reach_failures.append(f"{filename}:{qid} is not downstream of {CH01_TERMINAL}")
    checks.add("all_chapters_reachable_from_ch01_terminal", reach_failures)

    ch01_failures: list[str] = []
    if set(dependencies.get(CH01_TERMINAL, [])) != {CH01_CLAIMS, CH01_RIVALRY}:
        ch01_failures.append(
            f"{CH01_TERMINAL} must depend directly on both mandatory clauses; found {dependencies.get(CH01_TERMINAL, [])}"
        )
    if dependencies.get(CH01_CLAIMS, []) != [CH01_WELCOME]:
        ch01_failures.append(f"{CH01_CLAIMS} must depend only on {CH01_WELCOME}")
    if dependencies.get(CH01_RIVALRY, []) != [CH01_WELCOME]:
        ch01_failures.append(f"{CH01_RIVALRY} must depend only on {CH01_WELCOME}")
    checks.add("ch01_closed_rules_loop", ch01_failures)

    ch02_failures: list[str] = []
    branch_ids = (CH02_VAMPIRE, CH02_HUNTER, CH02_NEUTRAL)
    for qid in branch_ids:
        quest = quests.get(qid, {})
        if dependencies.get(qid, []) != [CH02_OVERVIEW]:
            ch02_failures.append(f"{qid} must depend only on the centered overview")
        if quest.get("optional") is not True:
            ch02_failures.append(f"{qid} must remain optional/open")
    vampire = quests.get(CH02_VAMPIRE, {})
    hunter = quests.get(CH02_HUNTER, {})
    neutral = quests.get(CH02_NEUTRAL, {})
    if float(vampire.get("x", 999)) != -float(hunter.get("x", 998)) or float(vampire.get("y", 999)) != float(hunter.get("y", 998)):
        ch02_failures.append("Vampire and Hunter branches are not symmetric across x=0 on the same row")
    if float(neutral.get("x", 999)) != 0.0:
        ch02_failures.append("Neutral branch must sit on the center axis")
    expected_gate_types = Counter({"item": 1, "advancement": 1})
    for qid in (CH02_VAMPIRE, CH02_HUNTER):
        actual_types = Counter(str(task.get("type")) for task in quests.get(qid, {}).get("tasks", []))
        if actual_types != expected_gate_types:
            ch02_failures.append(f"{qid}: expected one item and one advancement task, found {dict(actual_types)}")
        if direct_bevels(quests.get(qid, {}), team=False) != 2:
            ch02_failures.append(f"{qid}: expected exactly two personal Bevels")
    choice_set = set(branch_ids)
    for qid, deps in dependencies.items():
        if quest_chapter.get(qid) not in {EXPECTED_CHAPTERS[0], EXPECTED_CHAPTERS[1]} and choice_set.intersection(deps):
            ch02_failures.append(f"{qid}: later campaign content is locked behind a faction/neutral choice")
    checks.add("ch02_symmetric_open_branches", ch02_failures)

    group_failures: list[str] = []
    expected_groups = {
        "7A11C0DE00000001": "Introduction and Rules",
        "7A11C0DE00000002": "Factions and Progression",
        "7A11C0DE00000003": "Shared Horizons",
    }
    group_doc = parsed.get(groups_path, {}) if isinstance(parsed.get(groups_path), dict) else {}
    actual_groups = {
        str(group.get("id")): group.get("title")
        for group in group_doc.get("chapter_groups", [])
        if isinstance(group, dict)
    }
    if actual_groups != expected_groups:
        group_failures.append(f"chapter groups differ: expected {expected_groups}, found {actual_groups}")
    expected_membership = {
        EXPECTED_CHAPTERS[0]: "7A11C0DE00000001",
        EXPECTED_CHAPTERS[1]: "7A11C0DE00000002",
        EXPECTED_CHAPTERS[2]: "7A11C0DE00000002",
        EXPECTED_CHAPTERS[3]: "7A11C0DE00000002",
        EXPECTED_CHAPTERS[4]: "7A11C0DE00000003",
        EXPECTED_CHAPTERS[5]: "7A11C0DE00000003",
    }
    for filename, group_id in expected_membership.items():
        if chapters.get(filename, {}).get("group") != group_id:
            group_failures.append(f"{filename}: expected group {group_id}, found {chapters.get(filename, {}).get('group')}")
    checks.add("chapter_groups", group_failures)

    data_failures: list[str] = []
    data_doc = parsed.get(data_path, {}) if isinstance(parsed.get(data_path), dict) else {}
    if data_doc.get("version") != 13:
        data_failures.append(f"data.snbt version must remain 13; found {data_doc.get('version')}")
    if data_doc.get("progression_mode") != "flexible":
        data_failures.append(f"testing/unlock progression is forbidden; expected flexible, found {data_doc.get('progression_mode')}")
    if data_path.exists() and "testing" in data_path.read_text(encoding="utf-8").lower():
        data_failures.append("data.snbt contains testing unlock text")
    checks.add("data_schema_and_no_testing_unlock", data_failures, details={"settings": data_doc})

    title_failures: list[str] = []
    copy_failures: list[str] = []
    meta_failures: list[str] = []
    all_player_text: list[tuple[str, str]] = []
    for chapter in chapters.values():
        all_player_text.extend(player_texts(chapter))
    for location, text in all_player_text:
        if location.endswith(".title"):
            words = WORD.findall(text)
            if len(words) > 4:
                title_failures.append(f"{location}: {len(words)} words: {text!r}")
        for pattern, label in FORBIDDEN_COPY:
            if pattern.search(text):
                copy_failures.append(f"{location}: forbidden player-copy phrase {label!r}: {text!r}")
        for pattern, label in PLAYER_META_COPY:
            if pattern.search(text):
                meta_failures.append(f"{location}: player-visible implementation label {label!r}: {text!r}")
    checks.add("title_word_count_max_four", title_failures)
    checks.add("forbidden_player_copy", copy_failures)
    checks.add("player_visible_meta_labels", meta_failures)

    amp_failures: list[str] = []
    for path in parse_targets:
        if not path.exists():
            continue
        for line_no, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
            if re.search(r"(?<!\\)&\s", line):
                amp_failures.append(f"{rel(path, root)}:{line_no}: unescaped '& ' formatting token")
    checks.add("no_unescaped_ampersand_space", amp_failures)

    allowed_types = set(catalog.get("ftb_quests", {}).get("task_types_observed", []))
    type_failures: list[str] = []
    for qid, quest in quests.items():
        for kind in ("tasks", "rewards"):
            for obj in quest.get(kind, []):
                obj_type = obj.get("type")
                if obj_type not in allowed_types:
                    type_failures.append(f"{qid}:{kind}:{obj.get('id')}: unsupported/unobserved type {obj_type!r}")
    checks.add("observed_task_reward_types", type_failures, details={"allowed": sorted(allowed_types)})

    catalog_items = {str(entry.get("id")): entry for entry in catalog.get("entries", [])}
    catalog_advancements: dict[str, dict[str, Any]] = {}
    for group in catalog.get("advancements", {}).values():
        for entry in group:
            catalog_advancements[str(entry.get("id"))] = entry
    catalog_spells = {str(entry.get("id")): entry for entry in catalog.get("spells", [])}
    item_refs: list[tuple[str, str]] = []
    advancement_refs: list[tuple[str, str]] = []
    icon_refs: list[tuple[str, str]] = []
    data_icon = item_id(data_doc.get("icon"))
    if data_icon:
        icon_refs.append(("data.snbt", data_icon))
    for filename, chapter in chapters.items():
        iid = item_id(chapter.get("icon"))
        if iid:
            icon_refs.append((f"{filename}:chapter", iid))
        for quest in chapter.get("quests", []):
            qid = str(quest.get("id"))
            iid = item_id(quest.get("icon"))
            if iid:
                icon_refs.append((qid, iid))
            for task in quest.get("tasks", []):
                iid = item_id(task.get("item"))
                if iid:
                    item_refs.append((f"{qid}:task:{task.get('id')}", iid))
                advancement = task.get("advancement")
                if isinstance(advancement, str):
                    advancement_refs.append((f"{qid}:task:{task.get('id')}", advancement))
            for reward in quest.get("rewards", []):
                iid = item_id(reward.get("item"))
                if iid:
                    item_refs.append((f"{qid}:reward:{reward.get('id')}", iid))

    pack_proofs = catalog.get("pack_membership", {}).get("namespaces", {})
    used_pack_namespaces = sorted(
        {
            value.split(":", 1)[0]
            for _location, value in [*item_refs, *icon_refs, *advancement_refs]
            if not value.startswith("minecraft:")
        }
    )
    membership_failures: list[str] = []
    index_files: dict[str, dict[str, Any]] = {}
    try:
        index_doc = tomllib.loads((root / "index.toml").read_text(encoding="utf-8"))
        index_files = {
            str(entry.get("file")): entry
            for entry in index_doc.get("files", [])
            if isinstance(entry, dict)
        }
    except (OSError, UnicodeError, tomllib.TOMLDecodeError) as exc:
        membership_failures.append(f"index.toml could not be parsed: {exc}")
    for namespace in used_pack_namespaces:
        proof = pack_proofs.get(namespace)
        if not isinstance(proof, dict):
            membership_failures.append(f"{namespace}: no current-Packwiz namespace proof")
            continue
        metadata_rel = proof.get("metadata")
        if not isinstance(metadata_rel, str) or metadata_rel not in index_files:
            membership_failures.append(f"{namespace}: metadata {metadata_rel!r} is not indexed by index.toml")
            continue
        metadata_path = root / metadata_rel
        try:
            metadata = tomllib.loads(metadata_path.read_text(encoding="utf-8"))
        except (OSError, UnicodeError, tomllib.TOMLDecodeError) as exc:
            membership_failures.append(f"{namespace}: could not parse {metadata_rel}: {exc}")
            continue
        download = metadata.get("download", {})
        actual = {
            "filename": metadata.get("filename"),
            "side": metadata.get("side", "both"),
            "download_hash_format": download.get("hash-format"),
            "download_hash": download.get("hash"),
            "index_sha256": index_files[metadata_rel].get("hash"),
        }
        for field, value in actual.items():
            if proof.get(field) != value:
                membership_failures.append(
                    f"{namespace}: catalog {field}={proof.get(field)!r} does not match {metadata_rel} value {value!r}"
                )
        if actual["side"] == "client":
            membership_failures.append(f"{namespace}: {metadata_rel} is client-only and unavailable to quest logic")
    checks.add(
        "packwiz_namespace_membership",
        membership_failures,
        details={"used_non_vanilla_namespaces": used_pack_namespaces},
    )

    item_failures: list[str] = []
    for location, iid in [*item_refs, *icon_refs]:
        if iid.startswith("minecraft:"):
            continue
        entry = catalog_items.get(iid)
        if entry is None:
            item_failures.append(f"{location}: non-vanilla item/icon missing from catalog: {iid}")
        elif not entry.get("source_jar") or not entry.get("source_entry"):
            item_failures.append(f"{location}: catalog entry lacks direct JAR evidence path: {iid}")
        elif entry.get("source_jar") != pack_proofs.get(iid.split(":", 1)[0], {}).get("filename"):
            item_failures.append(
                f"{location}: evidence JAR {entry.get('source_jar')!r} is not the current Packwiz JAR for {iid}"
            )
    checks.add(
        "item_and_icon_catalog_coverage",
        item_failures,
        details={"item_references": len(item_refs), "icon_references": len(icon_refs)},
    )

    advancement_failures: list[str] = []
    for location, advancement in advancement_refs:
        entry = catalog_advancements.get(advancement)
        if entry is None:
            advancement_failures.append(f"{location}: advancement missing from catalog: {advancement}")
            continue
        namespace = advancement.split(":", 1)[0]
        if not entry.get("source_entry") or entry.get("source_jar") != pack_proofs.get(namespace, {}).get("filename"):
            advancement_failures.append(
                f"{location}: advancement evidence is not bound to the current Packwiz JAR: {advancement}"
            )
    checks.add(
        "advancement_catalog_coverage",
        advancement_failures,
        details={"advancement_references": len(advancement_refs)},
    )

    image_refs = [
        (location, image)
        for location, text in all_player_text
        for image in IMAGE_TAG.findall(text)
    ]
    image_failures = [
        f"{location}: image reference is neither vanilla nor a cataloged item namespace ID: {image}"
        for location, image in image_refs
        if not image.startswith("minecraft:") and image not in catalog_items
    ]
    checks.add(
        "images_and_icons_resolve",
        [*image_failures, *[f for f in item_failures if ": non-vanilla item/icon" in f]],
        details={"image_references": len(image_refs), "icon_references": len(icon_refs)},
    )

    localization_keys = set(parsed.get(lang_path, {}).keys()) if isinstance(parsed.get(lang_path), dict) else set()
    translation_refs: set[str] = set()
    for _location, text in all_player_text:
        translation_refs.update(TRANSLATE_TAG.findall(text))
        if BARE_TRANSLATION.fullmatch(text):
            translation_refs.add(text)
    unresolved_translations = sorted(translation_refs - localization_keys)
    checks.add(
        "zero_unresolved_localization_keys",
        [f"unresolved translation key: {key}" for key in unresolved_translations],
        details={
            "translation_keys_referenced": sorted(translation_refs),
            "localization_keys_defined": len(localization_keys),
            "inline_strings": not translation_refs,
        },
    )

    component_failures: list[str] = []
    for qid, quest in quests.items():
        for reward in quest.get("rewards", []):
            stack = reward.get("item")
            if not isinstance(stack, dict):
                continue
            components = stack.get("components")
            if not isinstance(components, dict):
                continue
            spell_container = components.get("irons_spellbooks:spell_container")
            if spell_container is not None:
                required_root = {"maxSpells", "spellWheel", "mustEquip", "data"}
                missing_root = required_root - set(spell_container) if isinstance(spell_container, dict) else required_root
                if missing_root:
                    component_failures.append(f"{qid}:{reward.get('id')}: spell container missing {sorted(missing_root)}")
                    continue
                for slot in spell_container.get("data", []):
                    missing_slot = {"id", "index", "level", "locked"} - set(slot) if isinstance(slot, dict) else {"id", "index", "level", "locked"}
                    if missing_slot:
                        component_failures.append(f"{qid}:{reward.get('id')}: spell slot missing {sorted(missing_slot)}")
                        continue
                    spell_entry = catalog_spells.get(str(slot.get("id")))
                    if spell_entry is None:
                        component_failures.append(f"{qid}:{reward.get('id')}: uncataloged spell {slot.get('id')}")
                    elif spell_entry.get("source_jar") != pack_proofs.get("irons_spellbooks", {}).get("filename"):
                        component_failures.append(
                            f"{qid}:{reward.get('id')}: spell evidence is not bound to the current Iron's Spells JAR"
                        )
            affinity_data = components.get("irons_spellbooks:affinity_data")
            if isinstance(affinity_data, dict) and isinstance(affinity_data.get("id"), str):
                spell_entry = catalog_spells.get(affinity_data["id"])
                if spell_entry is None:
                    component_failures.append(
                        f"{qid}:{reward.get('id')}: uncataloged affinity spell {affinity_data['id']}"
                    )
                elif spell_entry.get("source_jar") != pack_proofs.get("irons_spellbooks", {}).get("filename"):
                    component_failures.append(
                        f"{qid}:{reward.get('id')}: affinity evidence is not bound to the current Iron's Spells JAR"
                    )
    checks.add("item_component_codec_and_spell_ids", component_failures)

    criteria_failures: list[str] = []
    for qid, quest in quests.items():
        task_types = {str(task.get("type")) for task in quest.get("tasks", [])}
        if qid not in CHECKMARK_ALLOWLIST and not (task_types & HARD_TASK_TYPES):
            criteria_failures.append(f"{qid} {quest.get('title')!r}: substantive quest lacks a hard native criterion")
    blood_arcana = quests.get("7A11C0DE40000005", {})
    missing_cultist = sorted(CH04_CULTIST_SET - task_items(blood_arcana))
    if missing_cultist:
        criteria_failures.append(
            "7A11C0DE40000005 'Bloodbound Arcana': missing hard Cultist armor tasks " + str(missing_cultist)
        )
    checks.add("substantive_hard_criteria", criteria_failures)

    shared_failures: list[str] = []
    archive = quests.get("7A11C0DE50000004", {})
    if "exposure:album" not in task_items(archive):
        shared_failures.append(
            "7A11C0DE50000004 'Island Album': missing hard Photo Album evidence"
        )
    if not any(task.get("type") == "checkmark" for task in archive.get("tasks", [])):
        shared_failures.append(
            "7A11C0DE50000004 'Island Album': missing explicit public field-record attestation"
        )
    for qid in ("7A11C0DE50000005", "7A11C0DE50000006", "7A11C0DE50000007", "7A11C0DE50000008"):
        if not any(task.get("type") == "checkmark" for task in quests.get(qid, {}).get("tasks", [])):
            shared_failures.append(
                f"{qid} {quests.get(qid, {}).get('title')!r}: inventory alone does not prove the machine was connected/used at the shared co-op site"
            )
    checks.add("shared_activity_runtime_attestations", shared_failures)

    repeatable_failures: list[str] = []
    repeatables = {qid: quest for qid, quest in quests.items() if quest.get("can_repeat") is True}
    sink_total = 0
    repeatable_faucet = 0
    for qid, quest in repeatables.items():
        if quest_chapter.get(qid) != EXPECTED_CHAPTERS[5]:
            repeatable_failures.append(f"{qid}: repeatable quest exists outside Chapter 06")
        if quest.get("repeat_cooldown") != 604800:
            repeatable_failures.append(f"{qid}: cooldown must be 604800, found {quest.get('repeat_cooldown')}")
        bevel_inputs = [
            task
            for task in quest.get("tasks", [])
            if task.get("type") == "item"
            and item_id(task.get("item")) == BEVEL
            and task.get("consume_items") is True
        ]
        if len(bevel_inputs) != 1:
            repeatable_failures.append(f"{qid}: expected exactly one consumed Bevel input, found {len(bevel_inputs)}")
        else:
            price = item_count(bevel_inputs[0].get("item"))
            if price <= 0:
                repeatable_failures.append(f"{qid}: Bevel price must be positive")
            sink_total += price
        rewards = quest.get("rewards", [])
        if not rewards or any(reward.get("team_reward") is not True for reward in rewards):
            repeatable_failures.append(f"{qid}: every repeatable reward must be explicitly team-scoped")
        bevel_output = direct_bevels(quest)
        repeatable_faucet += bevel_output
        if bevel_output:
            repeatable_failures.append(f"{qid}: repeatable sink outputs {bevel_output} Bevel(s)")
    if len(repeatables) != 5:
        repeatable_failures.append(f"expected five Chapter 06 repeatable sinks, found {len(repeatables)}")
    if sink_total != 19:
        repeatable_failures.append(f"full sink-board price must be 19 Bevels, found {sink_total}")
    if repeatable_faucet != 0:
        repeatable_failures.append(f"repeatable Bevel faucet must be zero, found {repeatable_faucet}")
    checks.add(
        "chapter06_repeatable_sinks",
        repeatable_failures,
        details={
            "repeatable_quests": sorted(repeatables),
            "repeatable_bevel_faucet": repeatable_faucet,
            "sink_board_bevel_price": sink_total,
        },
    )

    reverse: dict[str, set[str]] = defaultdict(set)
    for qid, deps in dependencies.items():
        for dep in deps:
            reverse[dep].add(qid)

    def descendants(qid: str) -> set[str]:
        found: set[str] = set()
        pending = list(reverse.get(qid, set()))
        while pending:
            current = pending.pop()
            if current in found:
                continue
            found.add(current)
            pending.extend(reverse.get(current, set()))
        return found

    collision_failures: list[str] = []
    for qid, quest in quests.items():
        rewarded = reward_items(quest)
        for descendant in sorted(descendants(qid)):
            collision = rewarded & task_items(quests[descendant])
            if collision:
                collision_failures.append(
                    f"{qid} rewards {sorted(collision)}, later required by descendant {descendant}"
                )
    checks.add("reward_task_descendant_collision", collision_failures)

    one_time = {qid: quest for qid, quest in quests.items() if not quest.get("can_repeat")}
    one_time_personal = sum(direct_bevels(quest, team=False) for quest in one_time.values())
    one_time_team = sum(direct_bevels(quest, team=True) for quest in one_time.values())
    hunter_route = [CH02_HUNTER, *[f"7A11C0DE3000000{i}" for i in range(1, 5)]]
    vampire_route = [CH02_VAMPIRE, *[f"7A11C0DE4000000{i}" for i in range(1, 5)]]

    def route_totals(route: list[str]) -> dict[str, int]:
        return {
            "personal_bevels": sum(direct_bevels(quests.get(qid, {}), team=False) for qid in route),
            "team_bevels": sum(direct_bevels(quests.get(qid, {}), team=True) for qid in route),
        }

    hunter_totals = route_totals(hunter_route)
    vampire_totals = route_totals(vampire_route)
    selection_values = [
        direct_bevels(quests.get(CH02_VAMPIRE, {}), team=False),
        direct_bevels(quests.get(CH02_HUNTER, {}), team=False),
    ]
    intended_completionist_personal = one_time_personal - min(selection_values or [0])
    economy = {
        "one_time_all_claimable_personal_bevels": one_time_personal,
        "one_time_team_bevels": one_time_team,
        "minimum_hunter_faction_route": hunter_totals,
        "minimum_vampire_faction_route": vampire_totals,
        "intended_completionist_personal_bevels_one_selection": intended_completionist_personal,
        "maximum_completionist_personal_bevels_both_selections": one_time_personal,
        "completionist_team_bevels": one_time_team,
        "repeatable_bevel_faucet": repeatable_faucet,
        "sink_board_bevel_price_per_team_per_week": sink_total,
    }
    economy_failures: list[str] = []
    if one_time_personal != 44:
        economy_failures.append(f"all-claimable one-time personal ledger must be 44, found {one_time_personal}")
    if one_time_team != 6:
        economy_failures.append(f"one-time team ledger must be 6, found {one_time_team}")
    for label, totals in (("Hunter", hunter_totals), ("Vampire", vampire_totals)):
        if totals != {"personal_bevels": 12, "team_bevels": 2}:
            economy_failures.append(f"minimum {label} faction route must be 12 personal / 2 team, found {totals}")
    if intended_completionist_personal != 42:
        economy_failures.append(
            f"intended completionist ledger with one faction selection must be 42 personal, found {intended_completionist_personal}"
        )
    if repeatable_faucet != 0:
        economy_failures.append(f"repeatable faucet must be zero, found {repeatable_faucet}")
    if sink_total != 19:
        economy_failures.append(f"sink board must cost 19, found {sink_total}")
    checks.add("economy_ledgers", economy_failures, details=economy)

    kube_failures: list[str] = []
    kube_root = root / "kubejs"
    kube_scripts = sorted(p for p in kube_root.rglob("*") if p.is_file()) if kube_root.exists() else []
    campaign_markers: list[str] = []
    campaign_pattern = re.compile(r"7A11C0DE[1-6]|ch0[1-6]_|vvh|ftbquests", re.I)
    for path in kube_scripts:
        try:
            text = path.read_text(encoding="utf-8", errors="replace")
        except OSError as exc:
            kube_failures.append(f"cannot inspect {rel(path, root)}: {exc}")
            continue
        if campaign_pattern.search(text):
            campaign_markers.append(rel(path, root))
    try:
        proc = subprocess.run(
            ["git", "status", "--porcelain=v1", "--", "kubejs"],
            cwd=root,
            text=True,
            capture_output=True,
            check=False,
        )
        dirty_kubejs = [line for line in proc.stdout.splitlines() if line.strip()]
        if proc.returncode != 0:
            kube_failures.append(f"git status for kubejs failed: {proc.stderr.strip()}")
    except OSError as exc:
        dirty_kubejs = []
        kube_failures.append(f"could not run git status for kubejs boundary: {exc}")
    if dirty_kubejs:
        kube_failures.append(f"campaign worktree has KubeJS changes: {dirty_kubejs}")
    if campaign_markers:
        kube_failures.append(f"KubeJS files contain campaign/FTB Quests markers: {campaign_markers}")
    checks.add(
        "no_campaign_kubejs",
        kube_failures,
        details={
            "kubejs_files_scanned": [rel(p, root) for p in kube_scripts],
            "preexisting_givespell_allowed": "kubejs/server_scripts/givespell.js",
            "dirty_kubejs": dirty_kubejs,
        },
    )

    hash_paths = [
        *chapter_paths,
        groups_path,
        data_path,
        lang_path,
        root / "CHANGELOG.md",
        catalog_path,
        root / "docs/vvh/ID_CATALOG.md",
        root / "docs/vvh/CAMPAIGN_DESIGN.md",
        root / "docs/vvh/MOD_PRESENCE_AUDIT.md",
        root / "docs/vvh/VALIDATION.md",
        root / "docs/vvh/UNRESOLVED.md",
        root / "docs/vvh/campaign_manifest.json",
        root / "index.toml",
        root / "scripts/vvh_sync_catalog.py",
        root / "scripts/vvh_sync_manifest.py",
        Path(__file__).resolve(),
        *[
            root / proof["metadata"]
            for proof in pack_proofs.values()
            if isinstance(proof, dict) and isinstance(proof.get("metadata"), str)
        ],
    ]
    file_hashes = {
        rel(path, root): sha256(path)
        for path in hash_paths
        if path.exists() and path.is_file()
    }
    required_failures = checks.failed_required
    report: dict[str, Any] = {
        "schema_version": 1,
        "campaign": "VvH campaign v2",
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "root": str(root),
        "status": "pass" if not required_failures else "fail",
        "summary": {
            "checks": len(checks.items),
            "passed": sum(1 for check in checks.items if check["status"] == "pass"),
            "failed": sum(1 for check in checks.items if check["status"] == "fail"),
            "failed_required": len(required_failures),
            "chapters_parsed": len(chapters),
            "quests_parsed": len(quests),
        },
        "checks": checks.items,
        "economy": economy,
        "file_hashes_sha256": file_hashes,
        "limitations": [
            "Static SNBT parsing does not prove acceptance by the shipped FTB Quests loader.",
            "minecraft:* item/icon IDs are accepted by namespace and are not exhaustively checked against the vanilla registry here.",
            "Packwiz-bound JAR entries prove exact IDs/resources, not survival balance, faction eligibility, or runtime trigger behavior.",
            "Client rendering, text wrapping, red-error badges, reward delivery, and data-component tooltips require an actual client.",
            "Personal/team claims, weekly cooldown scope, faction switching, and FTB Teams synchronization require a two-account disposable-world test.",
        ],
        "runtime_tests_pending": [
            "dedicated server load and FTB Quests reload with log review",
            "client open of all six chapters and visual/text inspection",
            "Vampirism become_vampire and become_hunter triggers, including already-completed state",
            "Explorer's Compass possession and Exposure advancement behavior, including already-completed state",
            "Create shared-site attestations and Chapter 05 capstone completion",
            "one payer plus teammate claim for all five Chapter 06 sinks, followed by cooldown rejection",
            "personal versus team Bevel claims with two accounts and fragmented teams",
        ],
    }
    if output is not None:
        destination = output if output.is_absolute() else root / output
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_text(json.dumps(report, indent=2, sort_keys=False) + "\n", encoding="utf-8")
    return report, 0 if not required_failures else 1


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=ROOT_DEFAULT, help="repository root (default: inferred)")
    parser.add_argument("--output", type=Path, default=None, help="explicit JSON report path; omitted means read-only")
    args = parser.parse_args()
    report, exit_code = run(args.root, args.output)
    print(
        f"[{report['status'].upper()}] {report['summary']['passed']}/{report['summary']['checks']} checks passed; "
        f"{report['summary']['failed_required']} required check(s) failed"
    )
    for check in report["checks"]:
        if check["status"] == "fail":
            print(f"  [FAIL] {check['name']}")
            for failure in check["failures"]:
                print(f"    - {failure}")
    if args.output is not None:
        destination = args.output if args.output.is_absolute() else args.root.resolve() / args.output
        print(f"Report: {destination}")
    return exit_code


if __name__ == "__main__":
    raise SystemExit(main())
