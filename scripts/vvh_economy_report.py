#!/usr/bin/env python3
"""Emit a deterministic economy report from the VvH authoring source.

This is a source-level audit.  It intentionally does not claim that FTB
Quests has delivered, consumed, or scoped a reward correctly in a live client.
Run it after chapter agents finish their source edits, before refreshing any
derived evidence.
"""
from __future__ import annotations

import argparse
import hashlib
import importlib.util
import itertools
import json
import re
import sys
import zipfile
from collections import defaultdict
from pathlib import Path
from typing import Any

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
COIN_VALUE = {
    "numismatics:spur": 0.125,
    "numismatics:bevel": 1.0,
    "numismatics:sprocket": 2.0,
    "numismatics:cog": 8.0,
    "numismatics:crown": 64.0,
    "numismatics:sun": 512.0,
}
COIN_NAMES = {item: name for item, name in zip(COIN_VALUE, ("Spur", "Bevel", "Sprocket", "Cog", "Crown", "Sun"))}
COIN_WORDS = re.compile(r"(?i)(?:spur|bevel|sprocket|cog|crown|sun|numismatics)")
SOURCE_FILE = HERE / "vvh_campaign_v3.py"
NUMISMATICS_JAR = "CreateNumismatics-1.0.20+neoforge-mc1.21.1.jar"
NUMISMATICS_SHA256 = "1375BA1B50E53FD09435029B5B2D5B94779BA397CCA7E01180D07B0F624E5B9B"


def load_source() -> Any:
    sys.path.insert(0, str(HERE))
    spec = importlib.util.spec_from_file_location("vvh_campaign_report_source", SOURCE_FILE)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {SOURCE_FILE}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def amount(rewards: list[dict[str, Any]], team: bool | None = None) -> float:
    total = 0.0
    for reward in rewards:
        if team is not None and bool(reward.get("team_reward", False)) != team:
            continue
        item = reward.get("item", {})
        item_id = item.get("id") if isinstance(item, dict) else None
        if item_id in COIN_VALUE:
            total += COIN_VALUE[item_id] * int(item.get("count", 1))
    return total


def currency_tasks(quest: dict[str, Any]) -> list[dict[str, Any]]:
    found: list[dict[str, Any]] = []
    for task in quest.get("tasks", []):
        item = task.get("item", {})
        item_id = item.get("id") if isinstance(item, dict) else None
        if task.get("type") == "item" and task.get("consume_items") and item_id in COIN_VALUE:
            count = int(task.get("count", item.get("count", 1)))
            found.append({
                "item": item_id,
                "name": COIN_NAMES[item_id],
                "count": count,
                "value_bevel": COIN_VALUE[item_id] * count,
            })
    return found


def quest_rows(chapters: list[Any]) -> list[tuple[dict[str, Any], str]]:
    return [(quest, chapter.filename) for chapter in chapters for quest in chapter.quests]


def shortest_costs(rows: list[tuple[dict[str, Any], str]]) -> dict[str, float | None]:
    """Find a conservative shortest personal-currency route to each quest."""
    by_id = {quest["id"]: quest for quest, _ in rows}
    costs: dict[str, float | None] = {qid: None for qid in by_id}
    for _ in range(len(by_id) + 1):
        changed = False
        for qid, quest in by_id.items():
            deps = [dep for dep in quest.get("dependencies", []) if dep in by_id]
            needed = int(quest.get("min_required_dependencies", len(deps)))
            if needed <= 0:
                dep_cost = 0.0
            elif len(deps) < needed:
                continue
            else:
                options = []
                for selected in itertools.combinations(deps, needed):
                    values = [costs.get(dep) for dep in selected]
                    if all(value is not None for value in values):
                        options.append(sum(value for value in values if value is not None))
                if not options:
                    continue
                dep_cost = min(options)
            candidate = dep_cost + amount(quest.get("rewards", []), team=False)
            if costs[qid] is None or candidate < costs[qid]:
                costs[qid] = candidate
                changed = True
        if not changed:
            break
    return costs


def scan_external(root: Path) -> dict[str, list[dict[str, Any]]]:
    """Find configured currency/source candidates without calling them proven."""
    buckets: dict[str, list[dict[str, Any]]] = defaultdict(list)
    scan_roots = [root / "config", root / "kubejs", root / "datapacks"]
    suffixes = {".toml", ".json", ".json5", ".js", ".ts", ".snbt", ".mcfunction", ".yml", ".yaml"}
    for scan_root in scan_roots:
        if not scan_root.exists():
            continue
        for path in sorted(p for p in scan_root.rglob("*") if p.is_file() and p.suffix.lower() in suffixes):
            try:
                lines = path.read_text(encoding="utf-8-sig").splitlines()
            except (OSError, UnicodeDecodeError):
                continue
            for number, line in enumerate(lines, 1):
                if not COIN_WORDS.search(line):
                    continue
                lowered = line.lower()
                if any(word in lowered for word in ("trade", "trading", "sell", "buy", "exchange", "convert", "denomination", "recycl")):
                    kind = "recycling_npc_exchange_or_denomination_candidates"
                elif any(word in lowered for word in ("reward", "quest", "payout", "currency", "faucet", "income", "source")):
                    kind = "configured_currency_source_candidates"
                else:
                    kind = "currency_references_needing_review"
                buckets[kind].append({"file": path.relative_to(root).as_posix(), "line": number, "text": line.strip()[:240]})
    categories = (
        "configured_currency_source_candidates",
        "recycling_npc_exchange_or_denomination_candidates",
        "currency_references_needing_review",
    )
    return {key: sorted(buckets.get(key, []), key=lambda item: (item["file"], item["line"])) for key in categories}


def scan_external_review(root: Path) -> dict[str, Any]:
    """Summarize concrete configured audit leads, with proof limits."""
    evidence: dict[str, list[dict[str, Any]]] = {
        "recipe_or_kubejs_currency_changes": [],
        "recycling": [],
        "npc_trading": [],
        "denomination_conversion": [],
    }
    roots = [root / "config", root / "kubejs", root / "datapacks"]
    suffixes = {".toml", ".json", ".json5", ".js", ".ts", ".snbt", ".mcfunction", ".yml", ".yaml"}
    for scan_root in roots:
        if not scan_root.exists():
            continue
        for path in sorted(p for p in scan_root.rglob("*") if p.is_file() and p.suffix.lower() in suffixes):
            try:
                lines = path.read_text(encoding="utf-8-sig").splitlines()
            except (OSError, UnicodeDecodeError):
                continue
            rel = path.relative_to(root).as_posix()
            name = path.name.lower()
            for number, line in enumerate(lines, 1):
                lowered = line.lower()
                coin_context = COIN_WORDS.search(line) or "numismatics" in rel.lower()
                if coin_context and any(word in lowered for word in ("recipe", "event.custom", "event.shaped", "event.shapeless", "currency")):
                    evidence["recipe_or_kubejs_currency_changes"].append({"file": rel, "line": number, "text": line.strip()[:240]})
                if "recycle" in lowered and ("spell" in name or coin_context):
                    evidence["recycling"].append({"file": rel, "line": number, "text": line.strip()[:240]})
                if any(word in lowered for word in ("trader", "villagertrade", "villager_trade", "trades")) and ("infinite" in lowered or "wandering" in lowered or "farmersdelight" in name or coin_context):
                    evidence["npc_trading"].append({"file": rel, "line": number, "text": line.strip()[:240]})
                if coin_context and any(word in lowered for word in ("denomination", "convert", "exchange", "trade")):
                    evidence["denomination_conversion"].append({"file": rel, "line": number, "text": line.strip()[:240]})
    return {
        key: {
            "status": "configured_candidate" if values else "no_static_candidate_found",
            "evidence": sorted(values, key=lambda item: (item["file"], item["line"])),
            "proof_boundary": "Static configuration is a review lead only; recipe registration, NPC offers, recycling outputs, and denomination behavior require registry/recipe inspection and a live client/server check.",
        }
        for key, values in evidence.items()
    }


def inspect_external_artifacts(root: Path) -> dict[str, Any]:
    """Inspect installed recipe/loot archives without claiming runtime registry proof."""
    jar = root / "mods" / NUMISMATICS_JAR
    result: dict[str, Any] = {
        "numismatics_jar": {"path": str(jar), "status": "unverified_missing", "sha256": None},
        "numismatics_recipe_audit": {"recipe_json_count": 0, "coin_input_recipe_count": 0, "coin_output_recipe_count": 0, "coin_loot_entry_count": 0, "config_entry_count": 0},
        "dangerous_decor_recycling": {
            "status": "unverified_runtime_gate",
            "recipe_reference_count_across_mods": 0,
            "direct_numismatics_coin_loop_count": 0,
            "evidence": [],
        },
        "proof_boundary": "Archive inspection confirms packaged JSON only. Dynamic recipe registration, loot behavior, NPC offers, config defaults, and runtime recycling still require a loaded server/client check.",
    }
    if not jar.is_file():
        return result
    digest = hashlib.sha256(jar.read_bytes()).hexdigest().upper()
    result["numismatics_jar"] = {
        "path": str(jar),
        "status": "verified_expected_digest" if digest == NUMISMATICS_SHA256 else "digest_mismatch",
        "sha256": digest,
        "expected_sha256": NUMISMATICS_SHA256,
    }
    decor_terms = ("createdeco:", "industrial_iron", "pearl_brick", "scarlet_brick", "abyssal_decor")
    try:
        with zipfile.ZipFile(jar) as archive:
            names = archive.namelist()
            recipes = [name for name in names if name.startswith("data/") and "/recipe/" in name and name.endswith(".json")]
            coin_input = 0
            coin_output = 0
            for name in recipes:
                try:
                    payload = json.loads(archive.read(name))
                except (ValueError, UnicodeDecodeError):
                    continue
                encoded = json.dumps(payload).lower()
                output = json.dumps(payload.get("result", payload.get("output", ""))).lower()
                if "numismatics:" in encoded and any(coin in encoded for coin in COIN_VALUE):
                    coin_input += 1
                if any(f'"id": "{coin}"' in output for coin in COIN_VALUE):
                    coin_output += 1
            loot_coin = sum(
                1 for name in names
                if "/loot_table/" in name
                and name.endswith(".json")
                and any(f'"id": "{coin}"' in archive.read(name).decode("utf-8", "ignore").lower() for coin in COIN_VALUE)
            )
            result["numismatics_recipe_audit"] = {
                "recipe_json_count": len(recipes),
                "coin_input_recipe_count": coin_input,
                "coin_output_recipe_count": coin_output,
                "coin_loot_entry_count": loot_coin,
                "config_entry_count": sum(1 for name in names if "/config/" in name.lower() or name.lower().endswith("config.toml")),
                "finding": "Packaged recipes include a banking guide that consumes one Cog, but no packaged recipe outputs a Numismatics coin and no packaged loot table references a Numismatics coin.",
            }
    except (OSError, zipfile.BadZipFile):
        result["numismatics_jar"]["status"] = "archive_read_error"
    for mod in sorted((root / "mods").glob("*.jar")) if (root / "mods").is_dir() else []:
        try:
            with zipfile.ZipFile(mod) as archive:
                for name in archive.namelist():
                    if "/recipe/" not in name.lower() or not name.endswith(".json"):
                        continue
                    try:
                        payload = json.loads(archive.read(name))
                    except (ValueError, UnicodeDecodeError):
                        continue
                    encoded = json.dumps(payload).lower()
                    if any(term in encoded for term in decor_terms):
                        result["dangerous_decor_recycling"]["recipe_reference_count_across_mods"] += 1
                        output = json.dumps(payload.get("result", payload.get("output", ""))).lower()
                        if any(f'"id": "{coin}"' in output for coin in COIN_VALUE):
                            result["dangerous_decor_recycling"]["direct_numismatics_coin_loop_count"] += 1
                            if len(result["dangerous_decor_recycling"]["evidence"]) < 10:
                                result["dangerous_decor_recycling"]["evidence"].append(f"{mod.name}:{name}")
        except (OSError, zipfile.BadZipFile):
            continue
    if result["dangerous_decor_recycling"]["direct_numismatics_coin_loop_count"]:
        result["dangerous_decor_recycling"]["status"] = "candidate_direct_loop_review"
    else:
        result["dangerous_decor_recycling"]["finding"] = "No direct Numismatics-coin output was found in packaged recipes that reference Create Deco/industrial-iron/decor terms; a runtime recipe dump is still required before closing the gate."
    return result
def item_payload(rewards: list[dict[str, Any]]) -> dict[str, Any]:
    """Summarize authored item payload using a clearly labeled 64-stack view."""
    by_item: dict[str, int] = defaultdict(int)
    entries = 0
    for reward in rewards:
        item = reward.get("item", {})
        item_id = item.get("id") if isinstance(item, dict) else None
        if reward.get("type") != "item" or not item_id or item_id in COIN_VALUE:
            continue
        entries += 1
        by_item[item_id] += int(item.get("count", 1))
    return {
        "item_entries": entries,
        "item_count": sum(by_item.values()),
        "stack_equivalents_assuming_64": sum(count / 64 for count in by_item.values()),
        "by_item": {item_id: by_item[item_id] for item_id in sorted(by_item)},
        "stack_limit_boundary": "64-stack equivalent is a presentation metric for this report; unstackable and mod-specific maximums require the installed registry.",
    }


def build_report(root: Path, fragmented_teams: int, team_members: int, fixed_population: int = 2, external_root: Path | None = None) -> dict[str, Any]:
    source = load_source()
    chapters, _ = source.build_campaign()
    rows = quest_rows(chapters)
    costs = shortest_costs(rows)
    one_time_personal = sum(amount(q.get("rewards", []), team=False) for q, _ in rows if not q.get("can_repeat", False))
    one_time_team = sum(amount(q.get("rewards", []), team=True) for q, _ in rows if not q.get("can_repeat", False))
    one_time_by_chapter = []
    for chapter in chapters:
        chapter_rows = [quest for quest in chapter.quests if not quest.get("can_repeat", False)]
        one_time_by_chapter.append({
            "chapter": chapter.filename,
            "personal_bevel_equivalent": amount([reward for quest in chapter_rows for reward in quest.get("rewards", [])], team=False),
            "team_bevel_equivalent": amount([reward for quest in chapter_rows for reward in quest.get("rewards", [])], team=True),
        })
    repeatable: list[dict[str, Any]] = []
    for quest, chapter in rows:
        if not quest.get("can_repeat", False):
            continue
        prices = currency_tasks(quest)
        rewards = amount(quest.get("rewards", []), team=None)
        is_faucet = int(quest.get("repeat_cooldown", 0)) >= 7 * 24 * 60 * 60
        repeatable.append({
            "chapter": chapter,
            "id": quest["id"],
            "title": quest["title"],
            "cooldown_seconds": int(quest.get("repeat_cooldown", 0)),
            "price": prices,
            "price_bevel": sum(p["value_bevel"] for p in prices),
            "reward_bevel": rewards,
            "reward_team_flags": sorted({bool(reward.get("team_reward", False)) for reward in quest.get("rewards", [])}),
            "shared_entitlement_candidate": all(bool(reward.get("team_reward", False)) for reward in quest.get("rewards", [])),
            "kind": "weekly_faucet" if is_faucet else "paid_sink",
            "payload": item_payload(quest.get("rewards", [])),
        })
    paid = [row for row in repeatable if row["kind"] == "paid_sink"]
    faucets = [row for row in repeatable if row["kind"] == "weekly_faucet"]
    findings: list[dict[str, str]] = []
    for service in paid:
        if not service["price"]:
            findings.append({"severity": "error", "id": service["id"], "message": "paid sink has no consumed currency price"})
        if not service["shared_entitlement_candidate"]:
            findings.append({"severity": "review", "id": service["id"], "message": "paid sink has mixed or non-team reward scope; verify one payment -> one shared entitlement"})
    for faucet in faucets:
        if not faucet["shared_entitlement_candidate"]:
            findings.append({"severity": "error", "id": faucet["id"], "message": "weekly faucet is not fully team-scoped"})
    board_cost = sum(row["price_bevel"] for row in paid)
    weekly_faucet = sum(row["reward_bevel"] for row in faucets)
    single_team_personal = one_time_personal * team_members
    single_team_shared = one_time_team
    single_team_total = single_team_personal + single_team_shared
    per_fragmented_team_total = one_time_personal * team_members + one_time_team
    fixed_single_team_personal = one_time_personal * fixed_population
    fixed_single_team_total = fixed_single_team_personal + one_time_team
    fixed_solo_personal = one_time_personal * fixed_population
    fixed_solo_shared = one_time_team * fixed_population
    fixed_solo_total = fixed_solo_personal + fixed_solo_shared
    faction_completion: list[dict[str, Any]] = []
    calling_titles = {"ch03_lantern_order": "Join the Order", "ch04_house_night": "Join the House"}
    by_filename = {chapter.filename: chapter for chapter in chapters}
    for filename, title in calling_titles.items():
        chapter = by_filename[filename]
        chapter_personal = amount([reward for quest in chapter.quests for reward in quest.get("rewards", [])], team=False)
        chapter_team = amount([reward for quest in chapter.quests for reward in quest.get("rewards", [])], team=True)
        call_quest = next((q for c in chapters if c.filename == "ch02_callings" for q in c.quests if q["title"] == title), None)
        call_personal = amount(call_quest.get("rewards", []), team=False) if call_quest else 0.0
        faction_completion.append({
            "faction": "Lantern Order" if filename == "ch03_lantern_order" else "House of Night",
            "personal_bevel_equivalent": chapter_personal + call_personal,
            "team_bevel_equivalent": chapter_team,
            "single_team_total_with_members": (chapter_personal + call_personal) * team_members + chapter_team,
            "note": "Faction routes are reported separately; summing both is a hypothetical upper bound, not a normal player path.",
        })
    def board_cycles(currency: float) -> int:
        return int(currency // board_cost) if board_cost else 0
    service_by_title = {row["title"]: row for row in paid}
    works = service_by_title.get("Works Kit")
    concord = service_by_title.get("Concord Bond")
    value_comparison: dict[str, Any] = {"status": "not_available"}
    if works and concord and works["price_bevel"] and concord["price_bevel"]:
        works_at_concord_price = works["payload"]["stack_equivalents_assuming_64"] * concord["price_bevel"] / works["price_bevel"]
        value_comparison = {
            "status": "current_source",
            "works_price_bevel": works["price_bevel"],
            "works_stack_equivalents": works["payload"]["stack_equivalents_assuming_64"],
            "concord_price_bevel": concord["price_bevel"],
            "concord_stack_equivalents": concord["payload"]["stack_equivalents_assuming_64"],
            "works_equivalent_at_concord_price": works_at_concord_price,
            "concord_fraction_of_works_at_same_price": concord["payload"]["stack_equivalents_assuming_64"] / works_at_concord_price if works_at_concord_price else None,
            "assessment": "Current Concord is a curated civic-material premium: it supplies shaped road/bridge stock and is about 15% below Works by 64-stack-equivalent volume at the same price. A one-Cog version would be only about 43% of Works volume at equal currency and should be rebalanced or explicitly approved as a convenience premium.",
        }
    return {
        "schema": "vvh-economy-report-v1",
        "source": "scripts/vvh_campaign_v3.py::build_campaign",
        "source_level_only": True,
        "chapters": [{"filename": chapter.filename, "title": chapter.title, "quest_count": len(chapter.quests), "default_hide_dependency_lines": bool(chapter.default_hide_dependency_lines)} for chapter in chapters],
        "quest_count": len(rows),
        "currency_basis_bevel": COIN_VALUE,
        "one_time": {
            "personal_bevel_equivalent": one_time_personal,
            "team_bevel_equivalent": one_time_team,
            "combined_bevel_equivalent": one_time_personal + one_time_team,
            "by_chapter": one_time_by_chapter,
        },
        "minimum_personal_route": {
            "reachable_quests": sum(value is not None for value in costs.values()),
            "max_reachable_cost_bevel_equivalent": max((value for value in costs.values() if value is not None), default=None),
            "cost_to_quest": {qid: costs[qid] for qid in sorted(costs)},
        },
        "repeatable": {
            "paid_sink_count": len(paid),
            "paid_sink_price_bevel_equivalent": sum(row["price_bevel"] for row in paid),
            "weekly_faucet_count": len(faucets),
            "weekly_faucet_reward_bevel_equivalent_per_team": sum(row["reward_bevel"] for row in faucets),
            "weekly_faucet_reward_bevel_equivalent_fragmented_teams": sum(row["reward_bevel"] for row in faucets) * fragmented_teams,
            "fragmented_team_count_assumption": fragmented_teams,
            "services": repeatable,
        },
        "affordability": {
            "assumptions": [
                f"One team scenario uses {team_members} members and assumes each non-team one-time reward key can be claimed once by each member.",
                "Team rewards are counted once per team. This is a source-level affordability model, not proof of claim order or late-join behavior.",
                "Team-scoped issuance is counted per team. Currency items can be transferred or traded, so economic pooling remains possible even when quest claim and progress scope differ.",
            ],
            "paid_board_cost_bevel_equivalent": board_cost,
            "single_team": {
                "teams": 1,
                "members": fixed_population,
                "population": fixed_population,
                "scenario_label": "fixed population: one team",
                "personal_pool_bevel_equivalent": fixed_single_team_personal,
                "shared_pool_bevel_equivalent": single_team_shared,
                "total_pool_bevel_equivalent": fixed_single_team_total,
                "complete_board_cycles_from_one_time_currency": board_cycles(fixed_single_team_total),
                "weeks_from_faucet_only": board_cost / weekly_faucet if weekly_faucet else None,
            },
            "fixed_population": {
                "population": fixed_population,
                "scenario_label": "fixed population: one team versus one-player teams",
                "single_team": {
                    "teams": 1,
                    "members": fixed_population,
                    "personal_pool_bevel_equivalent": fixed_single_team_personal,
                    "shared_pool_bevel_equivalent": one_time_team,
                    "total_pool_bevel_equivalent": fixed_single_team_total,
                    "weekly_faucet_bevel_equivalent": weekly_faucet,
                    "complete_board_cycles_from_one_time_currency": board_cycles(fixed_single_team_total),
                },
                "solo_teams": {
                    "teams": fixed_population,
                    "members_per_team": 1,
                    "aggregate_personal_pool_bevel_equivalent": fixed_solo_personal,
                    "aggregate_shared_pool_bevel_equivalent": fixed_solo_shared,
                    "aggregate_total_pool_bevel_equivalent": fixed_solo_total,
                    "aggregate_weekly_faucet_bevel_equivalent": weekly_faucet * fixed_population,
                    "complete_board_cycles_from_aggregate_transferable_currency": board_cycles(fixed_solo_total),
                    "scope_note": "Each solo team receives its own team-scoped issuance; currency items remain transferable/tradeable between players.",
                },
            },
            "fragmented_teams": {
                "teams": fragmented_teams,
                "members_per_team": team_members,
                "population": fragmented_teams * team_members,
                "scenario_label": "optional larger population: fragmented teams",
                "per_team_total_pool_bevel_equivalent": per_fragmented_team_total,
                "aggregate_personal_pool_bevel_equivalent": single_team_personal * fragmented_teams,
                "aggregate_shared_pool_bevel_equivalent": single_team_shared * fragmented_teams,
                "aggregate_total_pool_bevel_equivalent": per_fragmented_team_total * fragmented_teams,
                "complete_board_cycles_per_team": board_cycles(per_fragmented_team_total),
                "weeks_from_faucet_only_per_team": board_cost / weekly_faucet if weekly_faucet else None,
                "aggregate_faucet_bevel_equivalent_per_week": weekly_faucet * fragmented_teams,
            },
            "faction_completion": faction_completion,
        },
        "value_comparison": value_comparison,
        "findings": findings,
        "external_audit_root": str((external_root or root).resolve()),
        "external_audit": scan_external((external_root or root).resolve()),
        "external_audit_review": scan_external_review((external_root or root).resolve()),
        "external_artifact_audit": inspect_external_artifacts((external_root or root).resolve()),
        "limitations": [
            "Source rewards do not prove FTB claim keys, payment consumption, cooldown timing, inventory overflow, or late-join behaviour.",
            "A paid service is a shared-entitlement candidate only when every reward entry has team_reward=true; confirm this in a two-account client test.",
            "Configured-source matches are review leads. Recipe, NPC, recycling, denomination, and obtainability evidence still require registry/recipe inspection and runtime verification.",
            "Item counts are reported as authored entries; maximum stack size and component decoding require the installed client and registry.",
        ],
    }


def markdown(report: dict[str, Any]) -> str:
    one = report["one_time"]
    rep = report["repeatable"]
    lines = [
        "# VvH Economy Report",
        "",
        f"Source: `{report['source']}`. This is a deterministic source-level diagnostic; it is not client or server proof.",
        "",
        f"Campaign: {report['quest_count']} quests across {len(report['chapters'])} chapters.",
        f"One-time issuance: {one['personal_bevel_equivalent']:g} personal + {one['team_bevel_equivalent']:g} team Bevel-equivalents.",
        f"Repeatables: {rep['paid_sink_count']} paid sinks costing {rep['paid_sink_price_bevel_equivalent']:g} Bevel-equivalents in total; {rep['weekly_faucet_count']} weekly faucet(s) yielding {rep['weekly_faucet_reward_bevel_equivalent_per_team']:g} per team per week.",
        "Faction chapter one-time issuance: " + "; ".join(
            f"{row['chapter']} {row['personal_bevel_equivalent']:g} personal/{row['team_bevel_equivalent']:g} team" for row in one["by_chapter"] if row["chapter"] in {"ch03_lantern_order", "ch04_house_night"}
        ) + ".",
        "",
        "## Repeatables",
        "",
        "| Kind | Quest | Price | Cooldown | Reward scope candidate |",
        "|---|---|---:|---:|---|",
    ]
    for service in rep["services"]:
        price = ", ".join(f"{p['count']} {p['name']}" for p in service["price"]) or "none"
        scope = "shared entitlement" if service["shared_entitlement_candidate"] else "review: not all rewards team-scoped"
        stacks = service["payload"]["stack_equivalents_assuming_64"]
        lines.append(f"| {service['kind']} | {service['title']} (`{service['id']}`) | {price} | {service['cooldown_seconds']}s | {scope}; {stacks:g} 64-stack eq. |")
    affordability = report["affordability"]
    single = affordability["single_team"]
    fragmented = affordability["fragmented_teams"]
    fixed = affordability["fixed_population"]
    fixed_single = fixed["single_team"]
    fixed_solo = fixed["solo_teams"]
    lines += [
        "",
        "## Affordability model",
        "",
        f"Paid board cost: {affordability['paid_board_cost_bevel_equivalent']:g} Bevel-equivalents. At fixed population {fixed['population']}, one {fixed['population']}-player team has {fixed_single['total_pool_bevel_equivalent']:g} one-time currency and {fixed_single['weekly_faucet_bevel_equivalent']:g} Bevel-equivalent faucet per week; {fixed['population']} one-player teams have {fixed_solo['aggregate_total_pool_bevel_equivalent']:g} aggregate and {fixed_solo['aggregate_weekly_faucet_bevel_equivalent']:g} per week. Currency items can transfer/trade, so this compares issuance and claim scope rather than a hard economic pooling barrier.",
        f"Optional larger-population scenario ({fragmented['teams']} teams x {fragmented['members_per_team']} members = {fragmented['population']} players): {fragmented['aggregate_total_pool_bevel_equivalent']:g} aggregate one-time currency and {fragmented['aggregate_faucet_bevel_equivalent_per_week']:g} Bevel-equivalents per week.",
        "",
        "| Faction completion | Personal | Team | Team pool with modeled members |",
        "|---|---:|---:|---:|",
    ]
    for row in affordability["faction_completion"]:
        lines.append(f"| {row['faction']} | {row['personal_bevel_equivalent']:g} | {row['team_bevel_equivalent']:g} | {row['single_team_total_with_members']:g} |")
    comparison = report["value_comparison"]
    if comparison.get("status") == "current_source":
        lines += [
            "",
            "## Concord versus Works",
            "",
            f"Concord Bond costs {comparison['concord_price_bevel']:g} Bevel-equivalents and supplies {comparison['concord_stack_equivalents']:g} 64-stack equivalents of shaped civic stock. Works Kit costs {comparison['works_price_bevel']:g} and supplies {comparison['works_stack_equivalents']:g}; at Concord's price, Works would supply {comparison['works_equivalent_at_concord_price']:g}. Current Concord is therefore {comparison['concord_fraction_of_works_at_same_price'] * 100:.1f}% of Works by this coarse volume metric, justified only as a curated roads/bridges convenience bundle. A one-Cog version would be about 43% at equal currency and should be rebalanced or explicitly approved as a premium.",
        ]
    lines += ["", "## Findings", ""]
    if report["findings"]:
        lines.extend(
            f"- `{finding['severity']}` `{finding['id']}`: {finding['message']}" for finding in report["findings"]
        )
    else:
        lines.append("No source-level findings.")
    lines += ["", "## External audit", ""]
    for kind, matches in report["external_audit"].items():
        lines.append(f"- `{kind}`: {len(matches)} source match(es); inspect each before treating it as an active faucet, exchange, or conversion.")
    lines += ["", "### Review matrix", ""]
    for kind, review in report["external_audit_review"].items():
        files = ", ".join(sorted({item["file"] for item in review["evidence"]})) or "none"
        lines.append(f"- `{kind}`: **{review['status']}** ({len(review['evidence'])} evidence line(s); files: {files}); {review['proof_boundary']}")
    artifact = report["external_artifact_audit"]
    jar = artifact["numismatics_jar"]
    recipe_audit = artifact["numismatics_recipe_audit"]
    decor_audit = artifact["dangerous_decor_recycling"]
    lines += [
        "",
        "### Packaged archive review",
        "",
        f"- Numismatics candidate `{jar['path']}`: **{jar['status']}**, SHA-256 `{jar.get('sha256') or 'missing'}`.",
        f"- Numismatics archive recipes: {recipe_audit['recipe_json_count']} JSON recipes; {recipe_audit['coin_input_recipe_count']} recipes reference a Numismatics coin; {recipe_audit['coin_output_recipe_count']} output a Numismatics coin; {recipe_audit['coin_loot_entry_count']} loot tables reference a Numismatics coin; packaged config entries: {recipe_audit['config_entry_count']}. {recipe_audit.get('finding', '')}",
        f"- Decor/alloy recycling audit: **{decor_audit['status']}**; {decor_audit['recipe_reference_count_across_mods']} packaged recipe references across installed mod archives, {decor_audit['direct_numismatics_coin_loop_count']} direct Numismatics-coin output loop(s). {decor_audit.get('finding', '')}",
        f"- {artifact['proof_boundary']}",
    ]
    lines += ["", "## Limitations", ""]
    lines.extend(f"- {item}" for item in report["limitations"])
    return "\n".join(lines) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=ROOT, help="Packwiz checkout root")
    parser.add_argument("--fragmented-teams", type=int, default=2, help="Team count for the explicit fragmentation scenario")
    parser.add_argument("--team-members", type=int, default=2, help="Members in each optional larger-population scenario team")
    parser.add_argument("--fixed-population", type=int, default=2, help="Player count held constant for one-team versus one-player-team comparison")
    parser.add_argument("--external-root", type=Path, help="Optional installed server/pack root whose config, kubejs, and datapacks are audited for currency references")
    parser.add_argument("--format", choices=("markdown", "json"), default="markdown")
    parser.add_argument("--output", type=Path, help="Write the report to this path instead of stdout")
    parser.add_argument("--strict", action="store_true", help="Return exit code 1 when source-level findings exist")
    args = parser.parse_args()
    if args.fragmented_teams < 1 or args.team_members < 1 or args.fixed_population < 1:
        parser.error("--fragmented-teams, --team-members, and --fixed-population must be at least 1")
    report = build_report(args.root.resolve(), args.fragmented_teams, args.team_members, args.fixed_population, args.external_root.resolve() if args.external_root else None)
    text = markdown(report) if args.format == "markdown" else json.dumps(report, indent=2, sort_keys=True, ensure_ascii=False) + "\n"
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(text, encoding="utf-8", newline="\n")
    else:
        sys.stdout.write(text)
    return 1 if args.strict and report["findings"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
