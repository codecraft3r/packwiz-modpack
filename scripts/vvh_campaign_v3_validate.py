#!/usr/bin/env python3
"""Read-only semantic validator for the VvH Concord campaign (v3).

The v3 generator is the source of the eight chapter files.  This validator
deliberately reads the emitted SNBT instead of importing the generator, so it
also catches stale, hand-edited, or partially generated campaigns.  ``--output``
is the only write operation; without it the working tree is untouched.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from collections import defaultdict
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
    "ch01_island_charter.snbt",
    "ch02_callings.snbt",
    "ch03_lantern_order.snbt",
    "ch04_house_night.snbt",
    "ch05_free_companies.snbt",
    "ch06_common_ground.snbt",
    "ch07_odd_hours.snbt",
    "ch08_market_services.snbt",
)
HEX_ID = re.compile(r"^[0-9A-F]{16}$")
WORD = re.compile(r"[A-Za-z0-9]+(?:['’][A-Za-z]+)?")
COBBLEMON = re.compile(r"cobblemon", re.I)
UNESCAPED_AMP = re.compile(r"(?<!\\)&\s")
ITEM_CURRENCY = {
    "numismatics:bevel": 1,
    "numismatics:sprocket": 2,
    "numismatics:cog": 8,
}
COIN_IDS = set(ITEM_CURRENCY)
# These denominations exist in the broader Numismatics economy, but are
# intentionally outside this campaign's bounded Bevel/Sprocket/Cog ledger.
UNSUPPORTED_COIN_IDS = {
    "numismatics:spur",
    "numismatics:crown",
    "numismatics:sun",
}
COOLDOWN = 604800


def rel(path: Path, root: Path) -> str:
    try:
        return path.resolve().relative_to(root.resolve()).as_posix()
    except ValueError:
        return str(path.resolve())


def parse_semantic(path: Path) -> Any:
    text = path.read_text(encoding="utf-8-sig")
    return Parser(text, str(path)).parse()


def flatten_strings(value: Any) -> Iterable[str]:
    if isinstance(value, str):
        yield value
    elif isinstance(value, dict):
        for child in value.values():
            yield from flatten_strings(child)
    elif isinstance(value, list):
        for child in value:
            yield from flatten_strings(child)


def item_id(value: Any) -> str | None:
    if isinstance(value, str):
        return value
    if isinstance(value, dict) and isinstance(value.get("id"), str):
        return value["id"]
    return None


def item_count(value: Any) -> int:
    if not isinstance(value, dict):
        return 1
    raw = value.get("count", 1)
    # Counts are stack quantities, never booleans, floats, or numeric strings.
    return raw if isinstance(raw, int) and not isinstance(raw, bool) else 0


def task_items(quest: dict[str, Any]) -> set[str]:
    return {
        iid
        for task in quest.get("tasks", [])
        if isinstance(task, dict)
        for iid in [item_id(task.get("item"))]
        if iid
    }


def reward_items(quest: dict[str, Any]) -> set[str]:
    return {
        iid
        for reward in quest.get("rewards", [])
        if isinstance(reward, dict)
        for iid in [item_id(reward.get("item"))]
        if iid
    }


def currency_total(objects: Iterable[dict[str, Any]]) -> int:
    total = 0
    for obj in objects:
        if not isinstance(obj, dict):
            continue
        iid = item_id(obj.get("item"))
        if iid in ITEM_CURRENCY:
            total += item_count(obj.get("item")) * ITEM_CURRENCY[iid]
    return total


class Checks:
    def __init__(self) -> None:
        self.items: list[dict[str, Any]] = []

    def add(self, name: str, failures: Iterable[str] = (), *, details: dict[str, Any] | None = None) -> None:
        issues = list(failures)
        self.items.append({
            "name": name,
            "status": "pass" if not issues else "fail",
            "failures": issues,
            "details": details or {},
        })

    @property
    def failed(self) -> list[dict[str, Any]]:
        return [item for item in self.items if item["status"] == "fail"]


def run(root: Path, output: Path | None = None) -> tuple[dict[str, Any], int]:
    root = root.resolve()
    base = root / "config/ftbquests/quests"
    chapters_dir = base / "chapters"
    groups_path = base / "chapter_groups.snbt"
    data_path = base / "data.snbt"
    lang_path = base / "lang/en_us.snbt"
    chapter_paths = [chapters_dir / name for name in EXPECTED_CHAPTERS]
    parse_targets = [*chapter_paths, groups_path, data_path, lang_path]
    checks = Checks()

    actual = sorted(path.name for path in chapters_dir.glob("*.snbt")) if chapters_dir.exists() else []
    checks.add(
        "exact_eight_chapter_files",
        [
            f"missing chapter files: {sorted(set(EXPECTED_CHAPTERS) - set(actual))}"
            for _ in [0]
            if set(EXPECTED_CHAPTERS) - set(actual)
        ] + [
            f"unexpected chapter files: {sorted(set(actual) - set(EXPECTED_CHAPTERS))}"
            for _ in [0]
            if set(actual) - set(EXPECTED_CHAPTERS)
        ],
        details={"expected": list(EXPECTED_CHAPTERS), "actual": actual},
    )

    parsed: dict[Path, Any] = {}
    parse_failures: list[str] = []
    for path in parse_targets:
        if not path.exists():
            parse_failures.append(f"{rel(path, root)}: missing")
            continue
        result = validate_file(path)
        parse_failures.extend(d.format(use_color=False) for d in result.diagnostics)
        if result.ok:
            try:
                parsed[path] = parse_semantic(path)
            except (SNBTError, OSError, UnicodeError) as exc:
                parse_failures.append(f"{rel(path, root)}: semantic parser: {exc}")
    checks.add("snbt_parse", parse_failures, details={"files_checked": [rel(path, root) for path in parse_targets]})

    chapters: dict[str, dict[str, Any]] = {
        path.name: value
        for path, value in parsed.items()
        if path in chapter_paths and isinstance(value, dict)
    }
    quests: dict[str, dict[str, Any]] = {}
    quest_chapter: dict[str, str] = {}
    locations: defaultdict[str, list[str]] = defaultdict(list)
    id_failures: list[str] = []

    def register(value: Any, location: str) -> None:
        if not isinstance(value, str):
            id_failures.append(f"{location}: missing id")
            return
        locations[value].append(location)
        if not HEX_ID.fullmatch(value):
            id_failures.append(f"{location}: malformed id {value!r}")

    for filename, chapter in chapters.items():
        register(chapter.get("id"), f"{filename}:chapter")
        for index, quest in enumerate(chapter.get("quests", [])):
            if not isinstance(quest, dict):
                id_failures.append(f"{filename}: quest[{index}] is not a compound")
                continue
            qid = quest.get("id")
            register(qid, f"{filename}:quest[{index}]")
            if isinstance(qid, str):
                quests[qid] = quest
                quest_chapter[qid] = filename
            for kind in ("tasks", "rewards"):
                for obj_index, obj in enumerate(quest.get(kind, [])):
                    register(obj.get("id") if isinstance(obj, dict) else None, f"{filename}:{kind}[{obj_index}]")
    groups_doc = parsed.get(groups_path)
    if isinstance(groups_doc, dict):
        for index, group in enumerate(groups_doc.get("chapter_groups", [])):
            if isinstance(group, dict):
                register(group.get("id"), f"chapter_groups.snbt:chapter_groups[{index}]")
    duplicates = [f"{key}: {values}" for key, values in locations.items() if len(values) > 1]
    checks.add("global_unique_ids", [*id_failures, *duplicates], details={"objects": sum(map(len, locations.values())), "unique_ids": len(locations)})

    dependencies: dict[str, list[str]] = {}
    graph_failures: list[str] = []
    for qid, quest in quests.items():
        raw = quest.get("dependencies", [])
        if not isinstance(raw, list):
            graph_failures.append(f"{qid}: dependencies must be a list")
            raw = []
        dependencies[qid] = [str(dep) for dep in raw]
        graph_failures.extend(f"{qid}: unresolved dependency {dep}" for dep in dependencies[qid] if dep not in quests)
    state: dict[str, int] = {}
    stack: list[str] = []

    def visit(qid: str) -> None:
        if state.get(qid) == 2:
            return
        if state.get(qid) == 1:
            start = stack.index(qid) if qid in stack else 0
            graph_failures.append("dependency cycle: " + " -> ".join([*stack[start:], qid]))
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
    checks.add("dependencies_resolve_and_acyclic", graph_failures)

    roots = [qid for qid, deps in dependencies.items() if not deps]
    reverse: defaultdict[str, set[str]] = defaultdict(set)
    for qid, deps in dependencies.items():
        for dep in deps:
            reverse[dep].add(qid)
    reachable: set[str] = set()
    pending = list(roots)
    while pending:
        qid = pending.pop()
        if qid in reachable:
            continue
        reachable.add(qid)
        pending.extend(reverse[qid])
    reach_failures = [f"{qid} ({quest_chapter.get(qid, '?')}) is unreachable from a root quest" for qid in quests if qid not in reachable]
    if len(roots) != 1:
        reach_failures.append(f"expected exactly one campaign root quest, found {len(roots)}: {roots}")
    checks.add("quest_reachability", reach_failures, details={"roots": roots, "reachable": len(reachable), "quests": len(quests)})

    title_failures: list[str] = []
    for filename, chapter in chapters.items():
        for field, value in (("chapter.title", chapter.get("title")),):
            for text in flatten_strings(value):
                # Chapter labels carry a numeric prefix (``04 ·``), which is
                # navigation metadata rather than a player-facing title word.
                title_text = re.sub(r"^\s*\d+\s*[·.-]\s*", "", text)
                if len(WORD.findall(title_text)) > 4:
                    title_failures.append(f"{filename}:{field}: more than four words: {text!r}")
        for qid, quest in ((str(q.get("id")), q) for q in chapter.get("quests", []) if isinstance(q, dict)):
            for text in flatten_strings(quest.get("title")):
                if len(WORD.findall(text)) > 4:
                    title_failures.append(f"{qid}.title: more than four words: {text!r}")
    checks.add("short_titles_max_four_words", title_failures)

    checkmark_failures: list[str] = []
    cue = re.compile(r"\b(read|acknowledge|confirm|sign|choose|consider|claim|consent|welcome|charter|calling|invitation|board|coin|record|lantern|seal|hand|door|margin)\w*\b", re.I)
    checkmark_count = 0
    for qid, quest in quests.items():
        tasks = [task for task in quest.get("tasks", []) if isinstance(task, dict)]
        marks = [task for task in tasks if task.get("type") == "checkmark"]
        if not marks:
            continue
        checkmark_count += len(marks)
        hard = [task for task in tasks if task.get("type") in {"item", "advancement", "statistic", "entity"}]
        text = " ".join(flatten_strings({"title": quest.get("title"), "subtitle": quest.get("subtitle"), "description": quest.get("description"), "tasks": marks}))
        if not hard and not quest.get("optional") and not cue.search(text):
            checkmark_failures.append(f"{qid} {quest.get('title')!r}: mandatory checkmark-only quest lacks an orientation/attestation cue")
    checks.add("checkmark_restrictions", checkmark_failures, details={"checkmark_tasks": checkmark_count})

    amp_failures: list[str] = []
    cobblemon_failures: list[str] = []
    for path in parse_targets:
        if not path.exists():
            continue
        text = path.read_text(encoding="utf-8-sig")
        for line_number, line in enumerate(text.splitlines(), 1):
            if UNESCAPED_AMP.search(line):
                amp_failures.append(f"{rel(path, root)}:{line_number}: unescaped '& '")
            if COBBLEMON.search(line):
                cobblemon_failures.append(f"{rel(path, root)}:{line_number}: removed Cobblemon reference")
    checks.add("no_unescaped_ampersand_space", amp_failures)
    checks.add("no_removed_cobblemon_references", cobblemon_failures)

    component_failures: list[str] = []
    component_count = 0

    def inspect_components(value: Any, location: str) -> None:
        nonlocal component_count
        if isinstance(value, dict):
            container = value.get("irons_spellbooks:spell_container")
            if container is not None:
                component_count += 1
                required = {"maxSpells", "mustEquip", "spellWheel", "data"}
                if not isinstance(container, dict):
                    component_failures.append(f"{location}: spell_container must be a compound")
                else:
                    missing = sorted(required - set(container))
                    if missing:
                        component_failures.append(f"{location}: spell_container missing {missing}")
                    slots = container.get("data")
                    if not isinstance(slots, list):
                        component_failures.append(f"{location}: spell_container.data must be a list")
                    else:
                        for index, slot in enumerate(slots):
                            required_slot = {"id", "index", "level", "locked"}
                            if not isinstance(slot, dict):
                                component_failures.append(f"{location}.data[{index}]: spell slot must be a compound")
                            else:
                                missing_slot = sorted(required_slot - set(slot))
                                if missing_slot:
                                    component_failures.append(f"{location}.data[{index}]: missing {missing_slot}")
            for key, child in value.items():
                inspect_components(child, f"{location}.{key}")
        elif isinstance(value, list):
            for index, child in enumerate(value):
                inspect_components(child, f"{location}[{index}]")

    for path, document in parsed.items():
        inspect_components(document, rel(path, root))
    checks.add("spell_container_mandatory_fields", component_failures, details={"components_checked": component_count})

    currency_failures: list[str] = []
    personal = team = 0
    chapter_ledgers: dict[str, dict[str, int]] = {}
    currency_references = 0
    for filename, chapter in chapters.items():
        chapter_personal = chapter_team = 0
        for qid, quest in ((str(q.get("id")), q) for q in chapter.get("quests", []) if isinstance(q, dict)):
            if quest.get("can_repeat") is True:
                continue
            for kind in ("tasks", "rewards"):
                for obj in quest.get(kind, []):
                    if not isinstance(obj, dict):
                        continue
                    iid = item_id(obj.get("item"))
                    if iid in UNSUPPORTED_COIN_IDS:
                        currency_failures.append(f"{qid}:{kind}:{obj.get('id')}: unsupported campaign currency denomination {iid}")
                    if iid not in COIN_IDS:
                        continue
                    currency_references += 1
                    count = item_count(obj.get("item"))
                    if count <= 0:
                        currency_failures.append(f"{qid}:{kind}:{obj.get('id')}: currency count must be positive")
                    if kind == "rewards":
                        if not isinstance(obj.get("team_reward"), bool):
                            currency_failures.append(f"{qid}:{kind}:{obj.get('id')}: team_reward must be explicit for currency rewards")
                        value = count * ITEM_CURRENCY[iid]
                        if obj.get("team_reward") is True:
                            chapter_team += value
                        else:
                            chapter_personal += value
        personal += chapter_personal
        team += chapter_team
        chapter_ledgers[filename] = {"personal_bevel_equivalents": chapter_personal, "team_bevel_equivalents": chapter_team}
    checks.add(
        "currency_denomination_scaling_and_ledgers",
        currency_failures,
        details={
            "bevel_equivalents": dict(ITEM_CURRENCY),
            "currency_references": currency_references,
            "one_time_personal_bevel_equivalents": personal,
            "one_time_team_bevel_equivalents": team,
            "one_time_all_claimable_bevel_equivalents": personal + team,
            "by_chapter": chapter_ledgers,
        },
    )

    repeatable_failures: list[str] = []
    repeatables = {qid: quest for qid, quest in quests.items() if quest.get("can_repeat") is True}
    sinks: dict[str, dict[str, Any]] = {}
    faucets: dict[str, dict[str, Any]] = {}
    for qid, quest in repeatables.items():
        if quest_chapter.get(qid) != EXPECTED_CHAPTERS[-1]:
            repeatable_failures.append(f"{qid}: repeatable quest must be in Chapter 08")
        if quest.get("optional") is not True:
            repeatable_failures.append(f"{qid}: repeatable quest must be optional")
        if quest.get("repeat_cooldown") != COOLDOWN:
            repeatable_failures.append(f"{qid}: repeat_cooldown must be {COOLDOWN}")
        rewards = [reward for reward in quest.get("rewards", []) if isinstance(reward, dict)]
        if not rewards or any(reward.get("team_reward") is not True for reward in rewards):
            repeatable_failures.append(f"{qid}: every repeatable reward must explicitly be team-scoped")
        coin_outputs = [reward for reward in rewards if item_id(reward.get("item")) in COIN_IDS]
        if coin_outputs:
            faucets[qid] = {"quest": quest, "outputs": coin_outputs}
        else:
            sinks[qid] = {"quest": quest, "outputs": rewards}
            inputs = [task for task in quest.get("tasks", []) if isinstance(task, dict) and task.get("type") == "item" and task.get("consume_items") is True and item_id(task.get("item")) in COIN_IDS]
            if len(inputs) != 1:
                repeatable_failures.append(f"{qid}: sink must consume exactly one currency item task")
            elif item_count(inputs[0].get("item")) <= 0:
                repeatable_failures.append(f"{qid}: sink currency price must be positive")
    if len(faucets) != 1:
        repeatable_failures.append(f"expected exactly one repeatable faucet, found {len(faucets)}")
    else:
        faucet_id, faucet = next(iter(faucets.items()))
        outputs = faucet["outputs"]
        all_rewards = [reward for reward in faucet["quest"].get("rewards", []) if isinstance(reward, dict)]
        if len(all_rewards) != 1 or len(outputs) != 1 or item_id(outputs[0].get("item")) != "numismatics:bevel" or item_count(outputs[0].get("item")) != 1:
            repeatable_failures.append(f"{faucet_id}: faucet must output exactly one team Bevel")
        if any(item_id(task.get("item")) in COIN_IDS for task in faucet["quest"].get("tasks", []) if isinstance(task, dict)):
            repeatable_failures.append(f"{faucet_id}: faucet must not consume campaign currency")
    if len(sinks) != 5:
        repeatable_failures.append(f"expected exactly five repeatable currency sinks, found {len(sinks)}")
    repeatable_faucet = sum(currency_total(entry["outputs"]) for entry in faucets.values())
    repeatable_sink_cost = sum(currency_total([task for task in entry["quest"].get("tasks", []) if isinstance(task, dict) and task.get("consume_items") is True]) for entry in sinks.values())
    checks.add("repeatable_faucet_and_team_sinks", repeatable_failures, details={"repeatables": sorted(repeatables), "faucets": sorted(faucets), "sinks": sorted(sinks), "faucet_bevel_equivalents_per_week": repeatable_faucet, "sink_cost_bevel_equivalents_per_week": repeatable_sink_cost})

    collision_failures: list[str] = []

    def descendants(qid: str) -> set[str]:
        found: set[str] = set()
        pending = list(reverse[qid])
        while pending:
            child = pending.pop()
            if child in found:
                continue
            found.add(child)
            pending.extend(reverse[child])
        return found

    # Reward stock must not satisfy a later progression condition. The sole
    # exception is campaign currency deliberately consumed by a repeatable sink;
    # without that flow, the currency would have no player-controlled purpose.
    for qid, quest in quests.items():
        rewarded = reward_items(quest)
        for child in sorted(descendants(qid)):
            child_quest = quests[child]
            overlap = rewarded & task_items(child_quest)
            allowed_sink_currency = {
                item_id(entry.get("item"))
                for entry in child_quest.get("tasks", [])
                if isinstance(entry, dict)
                and child_quest.get("can_repeat") is True
                and entry.get("type") == "item"
                and entry.get("consume_items") is True
                and item_id(entry.get("item")) in COIN_IDS
            }
            forbidden = sorted(iid for iid in overlap if iid not in allowed_sink_currency)
            if forbidden:
                collision_failures.append(f"{qid} rewards {forbidden}, descendant {child} uses as a task")
    checks.add("no_reward_item_used_by_descendant_task", collision_failures)

    failed = checks.failed
    report: dict[str, Any] = {
        "schema_version": 1,
        "campaign": "VvH Concord campaign v3",
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "root": str(root),
        "status": "pass" if not failed else "fail",
        "summary": {"checks": len(checks.items), "passed": len(checks.items) - len(failed), "failed": len(failed), "chapters_parsed": len(chapters), "quests_parsed": len(quests)},
        "checks": checks.items,
        "limitations": ["Static SNBT validation does not prove acceptance by the shipped FTB Quests loader or runtime team/cooldown behavior."],
    }
    if output is not None:
        destination = output if output.is_absolute() else root / output
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    return report, 0 if not failed else 1


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=ROOT_DEFAULT, help="repository root")
    parser.add_argument("--output", type=Path, default=None, help="optional JSON report path")
    args = parser.parse_args()
    report, code = run(args.root, args.output)
    print(f"[{report['status'].upper()}] {report['summary']['passed']}/{report['summary']['checks']} checks passed; {report['summary']['failed']} failed")
    for check in report["checks"]:
        if check["status"] == "fail":
            print(f"  [FAIL] {check['name']}")
            for failure in check["failures"]:
                print(f"    - {failure}")
    if args.output is not None:
        destination = args.output if args.output.is_absolute() else args.root.resolve() / args.output
        print(f"Report: {destination}")
    return code


if __name__ == "__main__":
    raise SystemExit(main())
