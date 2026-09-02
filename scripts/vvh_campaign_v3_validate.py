#!/usr/bin/env python3
"""Semantic, graph, economy, and layout validation for the live VvH campaign."""
from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import math
import re
import sys
import tomllib
from collections import defaultdict, deque
from pathlib import Path
from typing import Any, Iterable

HERE = Path(__file__).resolve().parent
GEN_PATH = HERE / "vvh_campaign_v3.py"
spec = importlib.util.spec_from_file_location("vvh_campaign_source", GEN_PATH)
if spec is None or spec.loader is None:
    raise RuntimeError(f"cannot import {GEN_PATH}")
source = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = source
spec.loader.exec_module(source)

COIN_VALUE = {
    "numismatics:spur": 0.125,
    "numismatics:bevel": 1,
    "numismatics:sprocket": 2,
    "numismatics:cog": 8,
    "numismatics:crown": 64,
    "numismatics:sun": 512,
}
VERIFIED_NONVANILLA_ITEMS = {
    "create:andesite_alloy",
    "create:belt_connector",
    "create:brass_ingot",
    "create:precision_mechanism",
    "sophisticatedbackpacks:backpack",
    "create:clipboard",
    "create:brown_toolbox",
    "createbigcannons:wrought_iron_cannon_end",
    "createbigcannons:wrought_iron_cannon_chamber",
    "createbigcannons:worm",
    "createbigcannons:ram_rod",
    "createbigcannons:powder_charge",
    "createbigcannons:mortar_stone",
    "createbigcannons:cannon_carriage",
    "create:wrench",
    "irons_spellbooks:inscription_table",
    "irons_spellbooks:alchemist_cauldron",
    "abyssal_decor:small_seabrass_pipes",
    "abyssal_decor:seabrass_sconce",
    "abyssal_decor:raw_marble",
    "abyssal_decor:frosted_glass",
    "abyssal_decor:cinnamon_log",
    "explorerscompass:explorerscompass",
    "exposure:album",
    "exposure:black_and_white_film",
    "exposure:camera",
    "exposure:color_film",
    "exposure:high_sensitivity_color_film",
    "exposure:photograph_frame",
    "irons_spellbooks:blood_upgrade_orb",
    "irons_spellbooks:holy_upgrade_orb",
    "irons_spellbooks:arcane_essence",
    "irons_spellbooks:blank_rune",
    "irons_spellbooks:blood_rune",
    "irons_spellbooks:common_ink",
    "irons_spellbooks:copper_spell_book",
    "irons_spellbooks:holy_rune",
    "irons_spellbooks:inscription_table",
    "irons_spellbooks:alchemist_cauldron",
    "abyssal_decor:small_seabrass_pipes",
    "abyssal_decor:seabrass_sconce",
    "abyssal_decor:raw_marble",
    "abyssal_decor:frosted_glass",
    "abyssal_decor:cinnamon_log",
    "irons_spellbooks:rare_ink",
    "irons_spellbooks:scroll",
    "irons_spellbooks:uncommon_ink",
    "irons_spellbooks:wizard_boots",
    "irons_spellbooks:wizard_chestplate",
    "irons_spellbooks:wizard_helmet",
    "irons_spellbooks:wizard_leggings",
    "numismatics:bevel",
    "numismatics:cog",
    "numismatics:sprocket",
    "supplementaries:rope_arrow",
    "supplementaries:wrench",
    "supplementaries:bomb",
    "supplementaries:bamboo_spikes_tipped",
    "supplementaries:bamboo_spikes",
    "mannequins:mannequin",
    "vampirism:alchemical_cauldron",
    "vampirism:alchemy_table",
    "vampirism:altar_infusion",
    "vampirism:altar_inspiration",
    "vampirism:armor_of_swiftness_chest_normal",
    "vampirism:armor_of_swiftness_feet_normal",
    "vampirism:armor_of_swiftness_head_normal",
    "vampirism:armor_of_swiftness_legs_normal",
    "vampirism:basic_crossbow",
    "vampirism:blood_bottle",
    "vampirism:blood_container",
    "vampirism:blood_infused_enhanced_iron_ingot",
    "vampirism:blood_infused_iron_ingot",
    "vampirism:blood_pedestal",
    "vampirism:blood_sieve",
    "vampirism:crossbow_arrow_normal",
    "vampirism:crossbow_arrow_spitfire",
    "vampirism:crossbow_arrow_teleport",
    "vampirism:crossbow_arrow_vampire_killer",
    "vampirism:dark_stone_bricks",
    "vampirism:heart_seeker_enhanced",
    "vampirism:heart_seeker_normal",
    "vampirism:purified_garlic",
    "vampirism:holy_water_bottle_normal",
    "vampirism:holy_water_splash_bottle_enhanced",
    "vampirism:hunter_axe_enhanced",
    "vampirism:hunter_axe_normal",
    "vampirism:hunter_coat_chest_normal",
    "vampirism:hunter_coat_feet_normal",
    "vampirism:hunter_coat_head_normal",
    "vampirism:hunter_coat_legs_normal",
    "vampirism:hunter_table",
    "vampirism:injection_garlic",
    "vampirism:item_alchemical_fire",
    "vampirism:potion_table",
    "vampirism:pure_salt",
    "vampirism:stake",
    "vampirism:umbrella",
    "vampirism:vampire_cloak_white_black",
    "vampirism:vampire_fang",
    "vampirism:weapon_table",
    "vista:hollow_cassette",
    "vista:television",
    "vista:viewfinder",
}
VERIFIED_NONVANILLA_ICONS = {
    "create:precision_mechanism",
    "sophisticatedbackpacks:backpack",
    "create:clipboard",
    "create:brown_toolbox",
    "createbigcannons:wrought_iron_cannon_end",
    "createbigcannons:wrought_iron_cannon_chamber",
    "createbigcannons:worm",
    "createbigcannons:ram_rod",
    "createbigcannons:powder_charge",
    "createbigcannons:mortar_stone",
    "createbigcannons:cannon_carriage",
    "create:wrench",
    "irons_spellbooks:inscription_table",
    "irons_spellbooks:alchemist_cauldron",
    "abyssal_decor:small_seabrass_pipes",
    "abyssal_decor:seabrass_sconce",
    "abyssal_decor:raw_marble",
    "abyssal_decor:frosted_glass",
    "abyssal_decor:cinnamon_log",
    "exposure:album",
    "exposure:camera",
    "irons_spellbooks:blood_rune",
    "irons_spellbooks:holy_rune",
    "irons_spellbooks:uncommon_ink",
    "irons_spellbooks:wizard_boots",
    "irons_spellbooks:wizard_chestplate",
    "irons_spellbooks:wizard_helmet",
    "irons_spellbooks:wizard_leggings",
    "numismatics:banking_guide",
    "numismatics:bevel",
    "numismatics:cog",
    "numismatics:sprocket",
    "vampirism:alchemical_cauldron",
    "vampirism:alchemy_table",
    "vampirism:altar_infusion",
    "vampirism:altar_inspiration",
    "vampirism:blood_container",
    "vampirism:blood_sieve",
    "vampirism:crossbow_arrow_normal",
    "vampirism:crossbow_arrow_spitfire",
    "vampirism:dark_stone_bricks",
    "vampirism:heart_seeker_enhanced",
    "vampirism:heart_seeker_normal",
    "vampirism:hunter_axe_enhanced",
    "vampirism:hunter_table",
    "vampirism:injection_garlic",
    "vampirism:item_alchemical_fire",
    "vampirism:potion_table",
    "vampirism:pure_salt",
    "vampirism:umbrella",
    "vampirism:vampire_cloak_white_black",
    "vampirism:vampire_fang",
    "vampirism:weapon_table",
    "vista:hollow_cassette",
    "vista:television",
    "vista:viewfinder",
}
VERIFIED_ADVANCEMENTS = {
    "exposure:adventure/moment_in_time",
    "vampirism:hunter/become_hunter",
    "vampirism:vampire/become_vampire",
}
VERIFIED_SPELLS = {
    "irons_spellbooks:blood_slash",
    "irons_spellbooks:blood_step",
    "irons_spellbooks:divine_smite",
    "irons_spellbooks:heal",
    "irons_spellbooks:ray_of_siphoning",
    "irons_spellbooks:recall",
}
VERIFIED_COMPONENTS = {"irons_spellbooks:spell_container", "minecraft:dyed_color", "minecraft:potion_contents"}
VERIFIED_IMAGES = {
    "poiesis:textures/questpics/vvh/blood_ritual_workstation.png",
    "poiesis:textures/questpics/vvh/blood_school_crest.png",
    "poiesis:textures/questpics/vvh/free_company_writ.png",
    "poiesis:textures/questpics/vvh/holy_public_ward.png",
    "poiesis:textures/questpics/vvh/holy_school_crest.png",
    "poiesis:textures/questpics/vvh/house_of_night_blood_panorama.png",
    "poiesis:textures/questpics/vvh/lantern_order_holy_panorama.png",
    "poiesis:textures/questpics/vvh/rivalry_without_ruin.png",
}
EXPECTED_FILES = [
    "ch01_island_charter",
    "ch02_callings",
    "ch03_lantern_order",
    "ch04_house_night",
    "ch05_market_services",
]
EXPECTED_COUNTS = [5, 5, 15, 15, 10]
HUNTER_SPECIALTIES = [source.qid(3, i) for i in (4, 5, 6, 12, 13, 7, 8, 9)]
VAMPIRE_SPECIALTIES = [source.qid(4, i) for i in (4, 5, 6, 12, 13, 7, 8, 9)]


def iter_strings(value: Any) -> Iterable[str]:
    if isinstance(value, str):
        yield value
    elif isinstance(value, dict):
        for child in value.values():
            yield from iter_strings(child)
    elif isinstance(value, list):
        for child in value:
            yield from iter_strings(child)


def item_id(record: dict[str, Any]) -> str | None:
    item = record.get("item")
    return item.get("id") if isinstance(item, dict) else None


def item_count(record: dict[str, Any]) -> int:
    if "count" in record and record["count"] is not None:
        return int(record["count"])
    item = record.get("item")
    return int(item.get("count", 1)) if isinstance(item, dict) else 1


def currency_value(rewards: Iterable[dict[str, Any]], *, team: bool | None = None) -> float:
    total = 0.0
    for reward in rewards:
        if team is not None and bool(reward.get("team_reward", False)) != team:
            continue
        iid = item_id(reward)
        if iid in COIN_VALUE:
            total += COIN_VALUE[iid] * item_count(reward)
    return total


def proper_intersection(a: tuple[float, float], b: tuple[float, float], c: tuple[float, float], d: tuple[float, float]) -> bool:
    def orient(p: tuple[float, float], q: tuple[float, float], r: tuple[float, float]) -> float:
        return (q[0] - p[0]) * (r[1] - p[1]) - (q[1] - p[1]) * (r[0] - p[0])

    o1, o2, o3, o4 = orient(a, b, c), orient(a, b, d), orient(c, d, a), orient(c, d, b)
    eps = 1e-9
    return ((o1 > eps and o2 < -eps) or (o1 < -eps and o2 > eps)) and ((o3 > eps and o4 < -eps) or (o3 < -eps and o4 > eps))


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate the current five-chapter VvH campaign")
    parser.add_argument("--root", type=Path, default=HERE.parent)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    root = args.root.resolve()
    chapters, groups = source.build_campaign()
    errors: list[str] = []
    warnings: list[str] = []
    used_items: set[str] = set()
    used_icons: set[str] = set()
    used_advancements: set[str] = set()
    used_spells: set[str] = set()
    used_components: set[str] = set()
    used_images: set[str] = set()

    if [ch.filename for ch in chapters] != EXPECTED_FILES:
        errors.append(f"chapter files differ from expected five-chapter architecture: {[ch.filename for ch in chapters]}")
    counts = [len(ch.quests) for ch in chapters]
    if counts != EXPECTED_COUNTS:
        errors.append(f"quest counts {counts} do not match {EXPECTED_COUNTS}")

    quest_by_id: dict[str, dict[str, Any]] = {}
    chapter_by_quest: dict[str, str] = {}
    all_ids: dict[str, str] = {}
    for ch in chapters:
        used_icons.add(ch.icon)
        used_images.update(image["image"] for image in ch.images)
        if ch.id in all_ids:
            errors.append(f"duplicate chapter id {ch.id}")
        all_ids[ch.id] = f"chapter {ch.filename}"
        for quest in ch.quests:
            qid = quest["id"]
            used_icons.add(quest["icon"]["id"])
            if qid in quest_by_id:
                errors.append(f"duplicate quest id {qid}")
            quest_by_id[qid] = quest
            chapter_by_quest[qid] = ch.filename
            if qid in all_ids:
                errors.append(f"duplicate global id {qid}")
            all_ids[qid] = f"quest {quest['title']}"
            for family in ("tasks", "rewards"):
                for entry in quest.get(family, []):
                    eid = entry.get("id")
                    if not eid:
                        errors.append(f"{qid} {family[:-1]} lacks id")
                    elif eid in all_ids:
                        errors.append(f"duplicate global id {eid} in {qid}")
                    else:
                        all_ids[eid] = f"{family[:-1]} in {qid}"

    deps: dict[str, list[str]] = {}
    children: dict[str, list[str]] = defaultdict(list)
    indegree: dict[str, int] = {}
    for qid, quest in quest_by_id.items():
        deps[qid] = list(quest.get("dependencies", []))
        indegree[qid] = len(deps[qid])
        for dep in deps[qid]:
            if dep not in quest_by_id:
                errors.append(f"{qid} depends on missing quest {dep}")
            else:
                children[dep].append(qid)

    queue = deque(q for q, degree in indegree.items() if degree == 0)
    topo: list[str] = []
    indegree_work = dict(indegree)
    while queue:
        q = queue.popleft()
        topo.append(q)
        for child in children[q]:
            indegree_work[child] -= 1
            if indegree_work[child] == 0:
                queue.append(child)
    if len(topo) != len(quest_by_id):
        errors.append("quest graph contains a dependency cycle")

    roots = [q for q in quest_by_id if not deps[q]]
    if roots != [source.qid(1, 1)]:
        errors.append(f"expected exactly the Charter opener as global root, found {roots}")
    reachable: set[str] = set()
    q = deque(roots)
    while q:
        node = q.popleft()
        if node in reachable:
            continue
        reachable.add(node)
        q.extend(children[node])
    missing_reach = sorted(set(quest_by_id) - reachable)
    if missing_reach:
        errors.append(f"unreachable quests: {missing_reach}")

    charter_terminal = quest_by_id[source.qid(1, 5)]
    expected_charter = {source.qid(1, i) for i in (6, 3, 7)}
    if set(charter_terminal["dependencies"]) != expected_charter:
        errors.append("Charter terminal does not directly depend on all three mandatory clauses")
    for later_ch in chapters[1:]:
        for quest in later_ch.quests:
            ancestors: set[str] = set()
            stack = list(quest.get("dependencies", []))
            while stack:
                node = stack.pop()
                if node in ancestors:
                    continue
                ancestors.add(node)
                stack.extend(deps.get(node, []))
            if source.qid(1, 5) not in ancestors:
                errors.append(f"{quest['id']} does not descend from Sign the Charter")

    neutral = quest_by_id[source.qid(2, 3)]
    if any(task.get("type") == "item" for task in neutral["tasks"]):
        errors.append("Neutral opt-out has an item prerequisite")
    required_neutral = {
        "minecraft:iron_helmet", "minecraft:iron_chestplate", "minecraft:iron_leggings", "minecraft:iron_boots",
        "minecraft:iron_sword", "minecraft:iron_pickaxe", "minecraft:iron_axe", "minecraft:iron_shovel", "minecraft:iron_hoe",
        "minecraft:shield", "minecraft:white_bed", "minecraft:cooked_beef", "numismatics:sprocket",
    }
    neutral_rewards = {item_id(r) for r in neutral["rewards"]}
    if not required_neutral <= neutral_rewards:
        errors.append(f"Neutral starter kit is missing {sorted(required_neutral - neutral_rewards)}")
    neutral_children = children[source.qid(2, 3)]
    if neutral_children != [source.qid(2, 7)]:
        errors.append(f"Neutral has an ongoing progression route: {neutral_children}")
    if [task.get("type") for task in neutral["tasks"]] != ["checkmark"]:
        errors.append("Neutral choice is not a single explicit acknowledgement")
    if any(bool(reward.get("team_reward", False)) for reward in neutral["rewards"]):
        errors.append("Neutral starter kit must be personal, not team-scoped")
    neutral_food = sum(item_count(reward) for reward in neutral["rewards"] if item_id(reward) == "minecraft:cooked_beef")
    if neutral_food < 32:
        errors.append(f"Neutral starter food is {neutral_food}, expected at least 32 cooked meals")
    if currency_value(neutral["rewards"], team=False) != 2:
        errors.append("Neutral starter currency is not exactly one Sprocket")

    for quest in chapters[0].quests:
        if any(task.get("type") != "checkmark" for task in quest["tasks"]):
            errors.append(f"Charter quest {quest['id']} uses a non-acknowledgement task")
        if currency_value(quest["rewards"]) != 0:
            errors.append(f"Charter quest {quest['id']} issues currency")
        if any(bool(reward.get("team_reward", False)) for reward in quest["rewards"]):
            errors.append(f"Charter quest {quest['id']} has a team reward")

    for chapter_num, specialty_ids in ((3, HUNTER_SPECIALTIES), (4, VAMPIRE_SPECIALTIES)):
        core1, core2, core3 = (source.qid(chapter_num, i) for i in (1, 2, 3))
        if deps[core2] != [core1] or deps[core3] != [core2]:
            errors.append(f"chapter {chapter_num} core spine is not Tier I -> II -> III")
        for b_idx in (14, 15, 16, 17):
            b_qid = source.qid(chapter_num, b_idx)
            if deps[b_qid] != [core3]:
                errors.append(f"building quest {b_qid} in chapter {chapter_num} does not directly descend from Core III")
        pairs = (((4, 5), 14), ((6, 12), 15), ((8, 13), 16), ((7, 9), 17)) if chapter_num == 3 else (((9, 8), 14), ((7, 13), 15), ((12, 6), 16), ((5, 4), 17))
        for pair, b_idx in pairs:
            for q_idx in pair:
                q_qid = source.qid(chapter_num, q_idx)
                if deps[q_qid] != [source.qid(chapter_num, b_idx)]:
                    errors.append(f"quest {q_qid} in chapter {chapter_num} does not descend from building prerequisite {b_idx}")

    # Structural and prose rules.
    checkmark_currency_allowlist = {source.qid(2, 3)}  # Explicit protected opt-out starter choice.
    for qid, quest in quest_by_id.items():
        if len(re.findall(r"[\w']+", quest["title"])) > 4:
            errors.append(f"title exceeds four words: {quest['title']}")
        for text in iter_strings({k: quest.get(k) for k in ("title", "subtitle", "description", "tasks", "rewards")}):
            if "& " in text:
                errors.append(f"unescaped ampersand-space in {qid}: {text!r}")
        task_types = {task.get("type") for task in quest.get("tasks", [])}
        if task_types == {"checkmark"} and currency_value(quest.get("rewards", [])) > 0 and qid not in checkmark_currency_allowlist:
            errors.append(f"checkmark-only quest {qid} issues currency")
        for task in quest.get("tasks", []):
            if task.get("type") == "advancement":
                advancement = task.get("advancement")
                if isinstance(advancement, str):
                    used_advancements.add(advancement)
                if advancement not in VERIFIED_ADVANCEMENTS:
                    errors.append(f"unverified advancement in {qid}: {advancement}")
            if task.get("type") == "item" and "consume_items" not in task:
                errors.append(f"item task in {qid} does not declare carry/submit semantics")
        for entry in quest.get("tasks", []) + quest.get("rewards", []):
            iid = item_id(entry)
            if iid:
                used_items.add(iid)
                if not iid.startswith("minecraft:") and iid not in VERIFIED_NONVANILLA_ITEMS:
                    errors.append(f"unverified exact item id in {qid}: {iid}")
                if item_count(entry) <= 0:
                    errors.append(f"non-positive item count in {qid}: {iid}")
            components = entry.get("item", {}).get("components", {}) if isinstance(entry.get("item"), dict) else {}
            if isinstance(components, dict):
                used_components.update(components)
                for component in components:
                    if component not in VERIFIED_COMPONENTS:
                        errors.append(f"unverified item component in {qid}: {component}")
            if iid == "irons_spellbooks:scroll":
                container = components.get("irons_spellbooks:spell_container")
                if not isinstance(container, dict):
                    errors.append(f"scroll in {qid} lacks spell_container")
                    continue
                required = {"data", "maxSpells", "mustEquip", "spellWheel"}
                if set(container) != required:
                    errors.append(f"scroll in {qid} has incomplete codec fields {set(container)}")
                data = container.get("data")
                if not isinstance(data, list) or len(data) != 1 or set(data[0]) != {"id", "index", "level", "locked"}:
                    errors.append(f"scroll in {qid} has invalid spell slot codec")
                else:
                    spell = data[0].get("id")
                    if isinstance(spell, str):
                        used_spells.add(spell)
                    if spell not in VERIFIED_SPELLS:
                        errors.append(f"unverified spell id in {qid}: {spell}")

    for icon in sorted(used_icons):
        if not icon.startswith("minecraft:") and icon not in VERIFIED_NONVANILLA_ICONS:
            errors.append(f"unverified exact icon id: {icon}")
    for image in sorted(used_images):
        if image not in VERIFIED_IMAGES:
            errors.append(f"unverified chapter image reference: {image}")

    # Ancestor reward -> descendant task collision.
    descendants: dict[str, set[str]] = {qid: set() for qid in quest_by_id}
    for qid in reversed(topo):
        for child in children[qid]:
            descendants[qid].add(child)
            descendants[qid].update(descendants[child])
    collisions: list[dict[str, str]] = []
    for ancestor, quest in quest_by_id.items():
        reward_items = {item_id(r) for r in quest.get("rewards", []) if item_id(r)}
        for descendant in descendants[ancestor]:
            task_items = {
                item_id(t) for t in quest_by_id[descendant].get("tasks", [])
                if item_id(t) and not (t.get("consume_items") and item_id(t) in COIN_VALUE)
            }
            for iid in sorted(reward_items & task_items):
                collisions.append({"ancestor": ancestor, "descendant": descendant, "item": iid})
    if collisions:
        errors.extend(f"reward/task collision {c['item']}: {c['ancestor']} -> {c['descendant']}" for c in collisions)

    # Market economy.
    repeatables = [q for q in quest_by_id.values() if q.get("can_repeat")]
    expected_market_prices = {
        source.qid(5, 2): 1,
        source.qid(5, 3): 2,
        source.qid(5, 4): 2,
        source.qid(5, 5): 4,
        source.qid(5, 9): 2,
        source.qid(5, 10): 4,
        source.qid(5, 7): 8,
    }
    expected_repeatables = set(expected_market_prices) | {source.qid(5, 6)}
    if {quest["id"] for quest in repeatables} != expected_repeatables:
        errors.append(f"repeatable set differs from the eight approved weekly services: {[q['id'] for q in repeatables]}")
    sinks: list[dict[str, Any]] = []
    faucets: list[dict[str, Any]] = []
    for quest in repeatables:
        if quest.get("repeat_cooldown") != source.WEEK:
            errors.append(f"repeatable {quest['id']} does not use weekly cooldown")
        consumed = [t for t in quest["tasks"] if t.get("type") == "item" and t.get("consume_items")]
        if not consumed:
            errors.append(f"repeatable {quest['id']} has no consumed input")
            continue
        input_ids = {item_id(t) for t in consumed}
        output_ids = {item_id(r) for r in quest["rewards"]}
        if input_ids & output_ids:
            errors.append(f"repeatable {quest['id']} reproduces its own input {sorted(input_ids & output_ids)}")
        if any(item_id(t) in COIN_VALUE for t in consumed):
            if len(consumed) != 1 or item_id(consumed[0]) not in COIN_VALUE:
                errors.append(f"market sink {quest['id']} does not consume one unambiguous currency price")
            price = sum(COIN_VALUE[item_id(t)] * item_count(t) for t in consumed if item_id(t) in COIN_VALUE)
            sinks.append({"id": quest["id"], "title": quest["title"], "price_bevel_equivalent": price})
            if expected_market_prices.get(quest["id"]) != price:
                errors.append(f"market sink {quest['id']} costs {price}, expected {expected_market_prices.get(quest['id'])}")
            if not all(bool(r.get("team_reward", False)) for r in quest["rewards"]):
                errors.append(f"market sink {quest['id']} has a non-team reward")
            if any(item_id(reward) in COIN_VALUE for reward in quest["rewards"]):
                errors.append(f"market sink {quest['id']} returns currency")
        if currency_value(quest["rewards"], team=True):
            faucets.append({"id": quest["id"], "title": quest["title"], "value_bevel_equivalent": currency_value(quest["rewards"], team=True)})
    sink_total = sum(s["price_bevel_equivalent"] for s in sinks)
    faucet_total = sum(f["value_bevel_equivalent"] for f in faucets)
    if sink_total != 23:
        errors.append(f"full weekly sink board costs {sink_total}, expected 23 Bevel-equivalent")
    if faucets != [{"id": source.qid(5, 6), "title": "Rumour Ledger", "value_bevel_equivalent": 1.0}]:
        errors.append(f"unexpected repeatable faucets: {faucets}")
    premium_prices = [s["price_bevel_equivalent"] for s in sinks if s["price_bevel_equivalent"] >= 2]
    if premium_prices and faucet_total >= min(premium_prices):
        errors.append("fallback faucet can self-fund a premium service")
    if faucet_total >= sink_total:
        errors.append("fallback faucet can self-fund the full service board")

    # Currency totals and faction parity.
    one_time_personal = 0.0
    one_time_team = 0.0
    for quest in quest_by_id.values():
        if not quest.get("can_repeat"):
            one_time_personal += currency_value(quest["rewards"], team=False)
            one_time_team += currency_value(quest["rewards"], team=True)

    def faction_summary(chapter_num: int) -> dict[str, Any]:
        ch = chapters[chapter_num - 1]
        core = [quest_by_id[source.qid(chapter_num, i)] for i in (1, 2, 3)]
        specialties = HUNTER_SPECIALTIES if chapter_num == 3 else VAMPIRE_SPECIALTIES
        all_personal = sum(currency_value(q["rewards"], team=False) for q in ch.quests)
        return {
            "quest_count": len(ch.quests),
            "core_currency": [currency_value(q["rewards"], team=False) for q in core],
            "counted_specialties": len(specialties),
            "specialty_currency": [currency_value(quest_by_id[s]["rewards"], team=False) for s in specialties],
            "personal_completionism": all_personal,
            "branch_count": len([q for q in ch.quests if q.get("optional")]),
        }

    hunter = faction_summary(3)
    vampire = faction_summary(4)
    for key in ("quest_count", "core_currency", "counted_specialties", "branch_count"):
        if hunter[key] != vampire[key]:
            errors.append(f"faction parity mismatch in {key}: Hunter={hunter[key]} Vampire={vampire[key]}")

    # Layout overlap and line-crossing checks per chapter.
    layout: dict[str, Any] = {}
    for ch in chapters:
        by = {q["id"]: q for q in ch.quests}
        overlaps: list[dict[str, str]] = []
        for i, left in enumerate(ch.quests):
            for right in ch.quests[i + 1:]:
                distance = math.hypot(float(left["x"]) - float(right["x"]), float(left["y"]) - float(right["y"]))
                threshold = 0.75 * (float(left.get("size", 1.0)) + float(right.get("size", 1.0)))
                if distance < threshold:
                    overlaps.append({"a": left["id"], "b": right["id"]})
        edges: list[tuple[str, str, tuple[float, float], tuple[float, float]]] = []
        for quest in ch.quests:
            if quest.get("hide_dependency_lines"):
                continue
            for dep in quest.get("dependencies", []):
                if dep in by:
                    edges.append((dep, quest["id"], (float(by[dep]["x"]), float(by[dep]["y"])), (float(quest["x"]), float(quest["y"]))))
        crossings: list[dict[str, str]] = []
        for i, e1 in enumerate(edges):
            for e2 in edges[i + 1:]:
                if {e1[0], e1[1]} & {e2[0], e2[1]}:
                    continue
                if proper_intersection(e1[2], e1[3], e2[2], e2[3]):
                    crossings.append({"edge_a": f"{e1[0]}->{e1[1]}", "edge_b": f"{e2[0]}->{e2[1]}"})
        layout[ch.filename] = {"node_overlaps": overlaps, "dependency_crossings": crossings}
        if overlaps:
            errors.append(f"{ch.filename} has {len(overlaps)} node overlaps")
        if crossings:
            errors.append(f"{ch.filename} has {len(crossings)} dependency-line crossings")

    # Verify generated files match source.
    expected = source.outputs(root)
    drift = []
    for path, content in expected.items():
        if not path.exists() or path.read_text(encoding="utf-8-sig") != content:
            drift.append(str(path.relative_to(root)))
    if drift:
        errors.append(f"authoritative output drift: {drift}")

    index_path = root / "index.toml"
    pack_path = root / "pack.toml"
    packwiz_details: dict[str, Any] = {"tracked_generated_files": {}}
    if not index_path.exists() or not pack_path.exists():
        errors.append("pack.toml or index.toml is missing")
    else:
        try:
            index_data = tomllib.loads(index_path.read_text(encoding="utf-8"))
            pack_data = tomllib.loads(pack_path.read_text(encoding="utf-8"))
            index_entries = {entry["file"]: entry["hash"] for entry in index_data.get("files", [])}
            generated_pack_files = sorted(
                str(path.relative_to(root)).replace("\\", "/")
                for path in expected
                if str(path.relative_to(root)).replace("\\", "/").startswith("config/")
            )
            for relative in generated_pack_files:
                actual = hashlib.sha256((root / relative).read_bytes()).hexdigest()
                declared = index_entries.get(relative)
                packwiz_details["tracked_generated_files"][relative] = {"index": declared, "actual": actual, "match": declared == actual}
                if declared != actual:
                    errors.append(f"Packwiz index hash mismatch for {relative}: index={declared} actual={actual}")
            index_digest = hashlib.sha256(index_path.read_bytes()).hexdigest()
            declared_index_digest = pack_data.get("index", {}).get("hash")
            packwiz_details.update({
                "index_sha256": index_digest,
                "pack_toml_declared_index_sha256": declared_index_digest,
                "index_hash_matches_pack_toml": declared_index_digest == index_digest,
            })
            if declared_index_digest != index_digest:
                errors.append(f"pack.toml index hash mismatch: declared={declared_index_digest} actual={index_digest}")
        except (OSError, KeyError, TypeError, tomllib.TOMLDecodeError) as exc:
            errors.append(f"could not validate Packwiz hashes: {exc}")

    identifier_details = {
        "nonvanilla_items": sorted(item for item in used_items if not item.startswith("minecraft:")),
        "nonvanilla_icons": sorted(icon for icon in used_icons if not icon.startswith("minecraft:")),
        "advancements": sorted(used_advancements),
        "spells": sorted(used_spells),
        "components": sorted(used_components),
        "images": sorted(used_images),
    }

    report = {
        "status": "pass" if not errors else "fail",
        "architecture": {
            "chapters": len(chapters),
            "quests": len(quest_by_id),
            "chapter_quest_counts": dict(zip(EXPECTED_FILES, counts)),
            "groups": groups,
        },
        "graph": {
            "global_root": roots,
            "reachable_quests": len(reachable),
            "cycles": len(topo) != len(quest_by_id),
            "charter_clause_count": len(expected_charter),
            "hunter_gate": "any 3 of 8 after Core III",
            "vampire_gate": "any 3 of 8 after Core III",
            "reward_descendant_task_collisions": collisions,
        },
        "neutral": {
            "item_prerequisites": sum(t.get("type") == "item" for t in neutral["tasks"]),
            "starter_reward_count": len(neutral["rewards"]),
            "progression_children": neutral_children,
        },
        "parity": {"hunter": hunter, "vampire": vampire, "equal": hunter == vampire},
        "economy": {
            "coin_values_bevel_equivalent": COIN_VALUE,
            "minimum_faction_route_personal": 15,
            "neutral_route_personal": 2,
            "one_time_personal_raw_completionism": one_time_personal,
            "one_time_team_completionism": one_time_team,
            "weekly_sinks": sinks,
            "weekly_sink_total": sink_total,
            "weekly_faucets": faucets,
            "weekly_faucet_total": faucet_total,
            "fragmented_team_faucet_formula": "1 Bevel-equivalent × number of separately maintained FTB Teams per week",
        },
        "identifiers": identifier_details,
        "packwiz": packwiz_details,
        "layout": layout,
        "warnings": warnings,
        "errors": errors,
    }

    output = args.output or root / "docs/vvh/evidence/current/campaign-validation.json"
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps({
        "status": report["status"],
        "chapters": len(chapters),
        "quests": len(quest_by_id),
        "errors": len(errors),
        "warnings": len(warnings),
        "weekly_sink_total": sink_total,
        "weekly_faucet_total": faucet_total,
        "report": str(output),
    }, indent=2))
    if errors:
        print("\n".join(f"ERROR: {error}" for error in errors))
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
