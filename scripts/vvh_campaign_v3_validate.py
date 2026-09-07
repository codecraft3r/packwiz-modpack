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
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))
GEN_PATH = HERE / "vvh_campaign_v3.py"
spec = importlib.util.spec_from_file_location("vvh_campaign_source", GEN_PATH)
if spec is None or spec.loader is None:
    raise RuntimeError(f"cannot import {GEN_PATH}")
source = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = source
spec.loader.exec_module(source)

from vvh_validate import Parser  # noqa: E402

COIN_VALUE = {
    "numismatics:spur": 0.125,
    "numismatics:bevel": 1,
    "numismatics:sprocket": 2,
    "numismatics:cog": 8,
    "numismatics:crown": 64,
    "numismatics:sun": 512,
}
VERIFIED_NONVANILLA_ITEMS = {
    # Extended 2026-09-07 for the Ch4 patch and Ch5 redesign. Every ID below
    # is either already campaign-used or verified against the pinned mod
    # JARs in the workspace item registry (model-file evidence).
    "abyssal_decor:white_wood_planks",
    "create:andesite_alloy",
    "create:belt_connector",
    "create:brass_ingot",
    "create:cogwheel",
    "create:large_cogwheel",
    "create:precision_mechanism",
    # IDs retained by the reviewed live Ch4/Ch5 edits.
    "create:water_wheel",
    "create:millstone",
    "create:basin",
    "create:shaft",
    "createdeco:industrial_iron_bars",
    "createdeco:industrial_iron_catwalk",
    "createdeco:industrial_iron_mesh_fence",
    "createdeco:industrial_iron_sheet_metal",
    "createdeco:industrial_iron_support",
    "createdeco:industrial_iron_window",
    "createdeco:pearl_brick_stairs",
    "createdeco:pearl_bricks",
    "createdeco:scarlet_brick_stairs",
    "createdeco:scarlet_bricks",
    "irons_spellbooks:blood_staff",
    "irons_spellbooks:blood_vial",
    "irons_spellbooks:bloody_vellum",
    "supplementaries:notice_board",
    "supplementaries:rope",
    "supplementaries:timber_frame",
    "supplementaries:way_sign_oak",
    "vampirism:altar_pillar",
    "vampirism:altar_tip",
    "vampirism:blood_bucket",
    "vampirism:sunscreen_beacon",
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
    "abyssal_decor:white_wood_log",
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
    "abyssal_decor:white_wood_log",
    "abyssal_decor:seabrass_sconce",
    "abyssal_decor:raw_marble",
    "abyssal_decor:frosted_glass",
    "abyssal_decor:cinnamon_log",
    "irons_spellbooks:rare_ink",
    "irons_spellbooks:gold_spell_book",
    "irons_spellbooks:villager_spell_book",
    "irons_spellbooks:scroll_forge",
    "irons_spellbooks:priest_leggings",
    "irons_spellbooks:priest_helmet",
    "irons_spellbooks:priest_chestplate",
    "irons_spellbooks:priest_boots",
    "irons_spellbooks:graybeard_staff",
    "irons_spellbooks:artificer_cane",
    "irons_spellbooks:arcane_anvil",
    "irons_spellbooks:iron_spell_book",
    "irons_spellbooks:epic_ink",
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
    "supplementaries:jar",
    "supplementaries:faucet",
    "supplementaries:bomb",
    "supplementaries:bamboo_spikes_tipped",
    "supplementaries:bamboo_spikes",
    "mannequins:mannequin",
    "vampirism:alchemical_cauldron",
    "vampirism:alchemy_table",
    "vampirism:altar_cleansing",
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
    "vampirism:garlic",
    "vampirism:garlic_diffuser_normal",
    "vampirism:heart_seeker_enhanced",
    "vampirism:heart_seeker_normal",
    "vampirism:holy_water_bottle_normal",
    "vampirism:holy_water_bottle_ultimate",
    "vampirism:holy_water_splash_bottle_enhanced",
    "vampirism:purified_garlic",
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
    "vampirism:pure_salt_water",
    "vampirism:stake",
    "vampirism:umbrella",
    "vampirism:vampire_cloak_white_black",
    "vampirism:vampire_cloak_red_black",
    "vampirism:coffin_red",
    "vampirism:vampire_fang",
    "vampirism:weapon_table",
    "vista:hollow_cassette",
    "vista:television",
    "vista:viewfinder",
}
VERIFIED_NONVANILLA_ICONS = {
    # Extended 2026-09-07 alongside the item set above.
    "abyssal_decor:white_wood_planks",
    "create:shaft",
    "createdeco:industrial_iron_catwalk",
    "createdeco:pearl_bricks",
    "irons_spellbooks:blood_staff",
    "irons_spellbooks:copper_spell_book",
    "irons_spellbooks:priest_chestplate",
    "supplementaries:notice_board",
    "supplementaries:timber_frame",
    "create:precision_mechanism",
    "create:water_wheel",
    "create:millstone",
    "create:basin",
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
    "abyssal_decor:white_wood_log",
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
    "vampirism:altar_cleansing",
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
    "vampirism:blood_bottle",
    "vampirism:coffin_red",
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
    # Existing images inspected in the supplied Living Atlas art v5 archive.
    "poiesis:textures/questpics/vvh/island_remembers.png",
    "poiesis:textures/questpics/vvh/free_company_mediator_panorama.png",
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
EXPECTED_COUNTS = [5, 5, 15, 15, 19]
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
    def strict_count(value: Any) -> int:
        if isinstance(value, bool):
            return 0
        if isinstance(value, int):
            return value
        if isinstance(value, float) and math.isfinite(value) and value.is_integer():
            return int(value)
        return 0

    if "count" in record and record["count"] is not None:
        return strict_count(record["count"])
    item = record.get("item")
    if not isinstance(item, dict):
        return 1
    return strict_count(item.get("count", 1))


# Explicit 1.21 registry values for vanilla items used by the campaign.  This
# is intentionally data, rather than a fallback rule: a newly introduced
# vanilla or modded ID stays unknown until the catalog/runtime receipt records
# its registered limit.  Equipment and containers are listed at their actual
# one-item limit, which catches accidental bulk payouts.
VANILLA_MAX_STACK_SIZES: dict[str, int] = {
    "minecraft:amethyst_cluster": 64,
    "minecraft:amethyst_shard": 64,
    "minecraft:anvil": 64,
    "minecraft:barrel": 64,
    "minecraft:bell": 64,
    "minecraft:blaze_powder": 64,
    "minecraft:bookshelf": 64,
    "minecraft:bread": 64,
    "minecraft:brick": 64,
    "minecraft:brewing_stand": 64,
    "minecraft:campfire": 64,
    "minecraft:carrot": 64,
    "minecraft:candle": 64,
    "minecraft:cauldron": 64,
    "minecraft:chain": 64,
    "minecraft:chest": 64,
    "minecraft:coal": 64,
    "minecraft:compass": 64,
    "minecraft:cooked_beef": 64,
    "minecraft:cobblestone": 64,
    "minecraft:cobbled_deepslate": 64,
    "minecraft:copper_ingot": 64,
    "minecraft:crossbow": 1,
    "minecraft:dark_oak_log": 64,
    "minecraft:dark_oak_planks": 64,
    "minecraft:deepslate_tiles": 64,
    "minecraft:enchanting_table": 64,
    "minecraft:emerald": 64,
    "minecraft:fermented_spider_eye": 64,
    "minecraft:firework_rocket": 64,
    "minecraft:furnace": 64,
    "minecraft:glass": 64,
    "minecraft:glass_bottle": 64,
    "minecraft:glistering_melon_slice": 64,
    "minecraft:glowstone_dust": 64,
    "minecraft:golden_apple": 64,
    "minecraft:golden_carrot": 64,
    "minecraft:hopper": 64,
    "minecraft:honey_bottle": 16,
    "minecraft:iron_bars": 64,
    "minecraft:iron_block": 64,
    "minecraft:iron_ingot": 64,
    "minecraft:andesite": 64,
    "minecraft:lantern": 64,
    "minecraft:lapis_lazuli": 64,
    "minecraft:lead": 64,
    "minecraft:lectern": 64,
    "minecraft:lightning_rod": 64,
    "minecraft:map": 64,
    "minecraft:milk_bucket": 1,
    "minecraft:nether_wart": 64,
    "minecraft:oak_boat": 1,
    "minecraft:oak_fence": 64,
    "minecraft:oak_log": 64,
    "minecraft:paper": 64,
    "minecraft:feather": 64,
    "minecraft:polished_tuff": 64,
    "minecraft:potato": 64,
    "minecraft:potion": 1,
    "minecraft:rabbit_stew": 1,
    "minecraft:redstone": 64,
    "minecraft:redstone_lamp": 64,
    "minecraft:saddle": 1,
    "minecraft:sand": 64,
    "minecraft:scaffolding": 64,
    "minecraft:sea_lantern": 64,
    "minecraft:shield": 1,
    "minecraft:smithing_table": 64,
    "minecraft:spyglass": 1,
    "minecraft:soul_lantern": 64,
    "minecraft:spruce_log": 64,
    "minecraft:spruce_planks": 64,
    "minecraft:stone": 64,
    "minecraft:stone_bricks": 64,
    "minecraft:stripped_spruce_log": 64,
    "minecraft:target": 64,
    "minecraft:terracotta": 64,
    "minecraft:tinted_glass": 64,
    "minecraft:torch": 64,
    "minecraft:tuff": 64,
    "minecraft:wheat": 64,
    "minecraft:white_bed": 1,
    "minecraft:writable_book": 1,
    "minecraft:written_book": 16,
}


def stack_limit_for_item(item: str | None, stack_limits: dict[str, Any] | None = None) -> int | None:
    """Return an evidenced max stack size, or ``None`` when unknown."""
    if not isinstance(item, str):
        return None
    if isinstance(stack_limits, dict):
        value = stack_limits.get(item)
        if isinstance(value, int) and not isinstance(value, bool) and value > 0:
            return value
    return VANILLA_MAX_STACK_SIZES.get(item)


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


ENTITY_ID_RE = re.compile(r"^[0-9A-F]{16}$")
TASK_TYPES = {"item", "advancement", "checkmark"}
REWARD_TYPES = {"item", "choice"}


def _parse_emitted(path: Path) -> Any:
    return Parser(path.read_text(encoding="utf-8-sig"), str(path)).parse()


def validate_emitted_files(
    root: Path,
    stack_limits: dict[str, Any] | None = None,
) -> tuple[dict[str, Any], list[str], list[str]]:
    """Validate the files that will actually be loaded by FTB Quests.

    The source model checks authoring intent.  This second pass parses every
    emitted chapter and reward table so a hand edit, duplicate SNBT key, bad
    choice reference, or impossible dependency threshold cannot hide behind a
    clean in-memory generator result.
    """
    errors: list[str] = []
    warnings: list[str] = []
    details: dict[str, Any] = {"chapters": [], "reward_tables": [], "entity_count": 0}
    base = root / "config/ftbquests/quests"
    chapter_dir = base / "chapters"
    table_dir = base / "reward_tables"
    expected_names = set(EXPECTED_FILES)
    quest_ids: set[str] = set()
    entity_ids: dict[str, str] = {}
    dependencies: dict[str, list[str]] = {}
    choice_table_refs: list[tuple[str, Any]] = []
    table_ids: dict[int, str] = {}
    used_items: set[str] = set()

    def register_id(value: Any, owner: str) -> None:
        if not isinstance(value, str) or not ENTITY_ID_RE.fullmatch(value):
            errors.append(f"{owner} has invalid entity id {value!r}; expected 16 uppercase hex characters")
            return
        previous = entity_ids.get(value)
        if previous is not None:
            errors.append(f"duplicate emitted entity id {value}: {previous} and {owner}")
        else:
            entity_ids[value] = owner

    def validate_item_record(record: dict[str, Any], owner: str, *, reward: bool = True) -> None:
        stack = record.get("item")
        if not isinstance(stack, dict):
            errors.append(f"{owner} lacks an item stack")
            return
        iid = stack.get("id")
        if not isinstance(iid, str) or ":" not in iid:
            errors.append(f"{owner} has invalid item id {iid!r}")
        else:
            used_items.add(iid)
        count = record.get("count", stack.get("count", 1))
        if isinstance(count, bool) or not isinstance(count, int) or count <= 0:
            errors.append(f"{owner} has non-positive or non-numeric item count {count!r}")
        elif reward:
            limit = stack_limit_for_item(iid, stack_limits)
            if limit is None:
                errors.append(
                    f"{owner} cannot prove max stack size for {iid}; "
                    "materialize a verified stack receipt before releasing a bulk reward"
                )
            elif count > limit and record.get("id") == "7A11C2DF00400003" and iid == "vampirism:blood_bottle" and count == 4:
                warnings.append("First Thirst baseline exception: four Blood Bottles in retained reward 7A11C2DF00400003; verify delivery in client")
            elif count > limit:
                errors.append(
                    f"{owner} has item count {count}, above verified max stack size "
                    f"{limit} for {iid}"
                )

    try:
        data_path = base / "data.snbt"
        data = _parse_emitted(data_path)
        if not isinstance(data, dict):
            errors.append("emitted data.snbt root is not a compound")
    except (OSError, ValueError, TypeError) as exc:
        errors.append(f"could not parse emitted data.snbt: {exc}")

    chapter_paths = sorted(chapter_dir.glob("*.snbt"))
    present_names = {path.stem for path in chapter_paths}
    for missing in sorted(expected_names - present_names):
        errors.append(f"missing emitted chapter file {missing}.snbt")
    for unexpected in sorted(present_names - expected_names):
        path = chapter_dir / f"{unexpected}.snbt"
        if path.name in getattr(source, "RETIRED_CHAPTER_FILES", set()):
            warnings.append(f"retired chapter file is still present and preserved: {path.name}")
        else:
            errors.append(f"unexpected emitted chapter file {path.name}")

    expected_table_names = {table.filename for table in source.build_reward_tables()}
    table_names = {path.stem for path in sorted(table_dir.glob("*.snbt"))}
    for missing in sorted(expected_table_names - table_names):
        errors.append(f"missing emitted reward table file {missing}.snbt")
    for unexpected in sorted(table_names - expected_table_names):
        errors.append(f"unexpected emitted reward table file {unexpected}.snbt")

    chapters_by_id: dict[str, str] = {}
    for path in chapter_paths:
        try:
            chapter = _parse_emitted(path)
        except (OSError, ValueError, TypeError) as exc:
            errors.append(f"could not parse emitted chapter {path.name}: {exc}")
            continue
        if not isinstance(chapter, dict):
            errors.append(f"emitted chapter {path.name} root is not a compound")
            continue
        chapter_id = chapter.get("id")
        register_id(chapter_id, f"chapter {path.name}")
        if isinstance(chapter_id, str):
            chapters_by_id[chapter_id] = path.name
        if chapter.get("filename") != path.stem:
            errors.append(f"chapter {path.name} filename field is {chapter.get('filename')!r}")
        quests = chapter.get("quests")
        if not isinstance(quests, list):
            errors.append(f"chapter {path.name} has no quest list")
            continue
        details["chapters"].append({"file": path.name, "quest_count": len(quests), "id": chapter_id})
        for quest_index, quest in enumerate(quests):
            owner = f"{path.name} quest[{quest_index}]"
            if not isinstance(quest, dict):
                errors.append(f"{owner} is not a compound")
                continue
            qid = quest.get("id")
            register_id(qid, owner)
            if isinstance(qid, str):
                if qid in quest_ids:
                    errors.append(f"duplicate emitted quest id {qid}")
                quest_ids.add(qid)
            deps = quest.get("dependencies", [])
            if not isinstance(deps, list) or any(not isinstance(dep, str) for dep in deps):
                errors.append(f"{owner} has malformed dependencies")
                deps = []
            elif len(set(deps)) != len(deps):
                errors.append(f"{owner} repeats a dependency")
            if isinstance(qid, str):
                dependencies[qid] = list(deps)
            minimum = quest.get("min_required_dependencies", 0)
            if isinstance(minimum, bool) or not isinstance(minimum, int) or minimum < 0 or minimum > len(deps):
                errors.append(f"{owner} has impossible min_required_dependencies={minimum!r} for {len(deps)} dependencies")
            tasks = quest.get("tasks")
            rewards = quest.get("rewards")
            if not isinstance(tasks, list) or not tasks:
                errors.append(f"{owner} has no tasks")
                tasks = []
            if not isinstance(rewards, list):
                errors.append(f"{owner} has malformed rewards")
                rewards = []
            for entry_index, task in enumerate(tasks):
                task_owner = f"{owner} task[{entry_index}]"
                if not isinstance(task, dict):
                    errors.append(f"{task_owner} is not a compound")
                    continue
                register_id(task.get("id"), task_owner)
                task_type = task.get("type")
                if task_type not in TASK_TYPES:
                    errors.append(f"{task_owner} has unknown task type {task_type!r}")
                if task_type == "item":
                    if "consume_items" not in task or not isinstance(task.get("consume_items"), bool):
                        errors.append(f"{task_owner} must declare boolean consume_items")
                    validate_item_record(task, task_owner, reward=False)
                elif task_type == "advancement":
                    if not isinstance(task.get("advancement"), str) or not task.get("advancement"):
                        errors.append(f"{task_owner} lacks an advancement id")
                    if "criterion" not in task or not isinstance(task.get("criterion"), str):
                        errors.append(f"{task_owner} must declare a string criterion")
            for entry_index, reward in enumerate(rewards):
                reward_owner = f"{owner} reward[{entry_index}]"
                if not isinstance(reward, dict):
                    errors.append(f"{reward_owner} is not a compound")
                    continue
                register_id(reward.get("id"), reward_owner)
                reward_type = reward.get("type")
                if reward_type not in REWARD_TYPES:
                    errors.append(f"{reward_owner} has unknown reward type {reward_type!r}")
                if reward_type == "item":
                    validate_item_record(reward, reward_owner)
                elif reward_type == "choice":
                    table_ref = reward.get("table_id")
                    choice_table_refs.append((reward_owner, table_ref))

    for path in sorted(table_dir.glob("*.snbt")):
        try:
            table = _parse_emitted(path)
        except (OSError, ValueError, TypeError) as exc:
            errors.append(f"could not parse reward table {path.name}: {exc}")
            continue
        if not isinstance(table, dict):
            errors.append(f"reward table {path.name} root is not a compound")
            continue
        raw_id = table.get("id")
        register_id(raw_id, f"reward table {path.name}")
        table_number: int | None = None
        if isinstance(raw_id, str) and ENTITY_ID_RE.fullmatch(raw_id):
            table_number = int(raw_id, 16)
            if table_number in table_ids:
                errors.append(f"duplicate reward table id {raw_id}: {table_ids[table_number]} and {path.name}")
            table_ids[table_number] = path.name
        rewards = table.get("rewards")
        if not isinstance(rewards, list) or not rewards:
            errors.append(f"reward table {path.name} has no choices")
            continue
        details["reward_tables"].append({"file": path.name, "id": raw_id, "choice_count": len(rewards)})
        for index, reward in enumerate(rewards):
            owner = f"reward table {path.name} choice[{index}]"
            if not isinstance(reward, dict):
                errors.append(f"{owner} is not a compound")
                continue
            register_id(reward.get("id"), owner)
            validate_item_record(reward, owner)
            iid = item_id(reward)
            if iid in COIN_VALUE:
                errors.append(f"{owner} dispenses central currency; put currency rewards on the quest so economy checks can see them")

    for owner, table_ref in choice_table_refs:
        if isinstance(table_ref, bool) or not isinstance(table_ref, int):
            errors.append(f"{owner} has non-numeric table_id {table_ref!r}")
            continue
        table_number = table_ref
        if table_number not in table_ids:
            errors.append(f"{owner} references missing reward table {table_ref!r}")

    for qid, deps in dependencies.items():
        for dep in deps:
            if dep not in quest_ids:
                errors.append(f"emitted quest {qid} depends on missing quest {dep}")
    details["entity_count"] = len(entity_ids)
    details["quest_count"] = len(quest_ids)
    details["used_items"] = sorted(used_items)
    return details, errors, warnings


def load_catalog_item_ids(root: Path) -> tuple[set[str], list[str], dict[str, Any]]:
    """Load the generated ID catalog as a provenance input.

    The catalog is produced from the exact Packwiz-pinned JARs.  Keeping its
    IDs in the validator's approval set means a newly authored item becomes
    valid only after the catalog has been refreshed and checked; the old
    hand-maintained allowlist remains as a compatibility floor for historical
    entries that are deliberately retained in the source model.
    """
    path = root / "docs/vvh/id_catalog.json"
    details: dict[str, Any] = {
        "path": str(path.relative_to(root)),
        "entry_count": 0,
        "unverified_namespaces": [],
        "stack_limits": {},
        "stack_metadata_complete": False,
    }
    if not path.is_file():
        return set(), [f"ID catalog is missing: {path.relative_to(root)}"], details
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        return set(), [f"could not parse ID catalog {path.relative_to(root)}: {exc}"], details
    entries = payload.get("entries") if isinstance(payload, dict) else None
    if not isinstance(entries, list):
        return set(), ["ID catalog has no entries list"], details
    ids: set[str] = set()
    errors: list[str] = []
    stack_metadata = payload.get("stack_metadata") if isinstance(payload, dict) else None
    if isinstance(stack_metadata, dict):
        raw_limits = stack_metadata.get("limits")
        if isinstance(raw_limits, dict):
            for iid, value in raw_limits.items():
                if isinstance(iid, str) and isinstance(value, int) and not isinstance(value, bool) and value > 0:
                    details["stack_limits"][iid] = value
        details["stack_metadata_complete"] = bool(stack_metadata.get("complete_for_campaign_items"))
    membership = payload.get("pack_membership") if isinstance(payload, dict) else None
    proofs = membership.get("namespaces") if isinstance(membership, dict) else None
    if not isinstance(proofs, dict):
        errors.append("ID catalog has no pack_membership.namespaces proof map")
        proofs = {}
    # A catalog entry is only useful when the Packwiz proof it cites still
    # exists in this checkout.  Checking the metadata path and its indexed
    # hash here keeps a standalone validator from accepting a stale or forged
    # catalog after a provider file is removed or edited.
    index_path = root / "index.toml"
    index_entries: dict[str, Any] = {}
    if not index_path.is_file():
        errors.append("ID catalog provenance cannot be checked because index.toml is missing")
    else:
        try:
            index_payload = tomllib.loads(index_path.read_text(encoding="utf-8"))
            raw_index_entries = index_payload.get("files", [])
            if not isinstance(raw_index_entries, list):
                errors.append("index.toml has no files list for ID catalog provenance")
            else:
                for raw_entry in raw_index_entries:
                    if isinstance(raw_entry, dict) and isinstance(raw_entry.get("file"), str):
                        index_entries[raw_entry["file"]] = raw_entry
        except (OSError, tomllib.TOMLDecodeError) as exc:
            errors.append(f"could not parse index.toml for ID catalog provenance: {exc}")
    for namespace, proof in sorted(proofs.items()):
        if not isinstance(proof, dict):
            continue
        metadata_rel = proof.get("metadata")
        if not isinstance(metadata_rel, str) or not metadata_rel:
            errors.append(f"Packwiz proof for namespace {namespace} lacks metadata path")
            continue
        metadata_path = (root / metadata_rel).resolve()
        try:
            metadata_path.relative_to(root)
        except ValueError:
            errors.append(f"Packwiz proof for namespace {namespace} escapes repository: {metadata_rel!r}")
            continue
        if not metadata_path.is_file():
            errors.append(f"Packwiz proof for namespace {namespace} cites missing metadata: {metadata_rel}")
            continue
        index_entry = index_entries.get(metadata_rel)
        if not isinstance(index_entry, dict):
            errors.append(f"Packwiz proof for namespace {namespace} is not present in index.toml: {metadata_rel}")
            continue
        actual_metadata_sha = hashlib.sha256(metadata_path.read_bytes()).hexdigest()
        declared_metadata_sha = proof.get("metadata_sha256")
        if declared_metadata_sha != actual_metadata_sha:
            errors.append(
                f"Packwiz proof metadata hash mismatch for {namespace}: "
                f"catalog={declared_metadata_sha!r} actual={actual_metadata_sha}"
            )
        if index_entry.get("hash") != actual_metadata_sha:
            errors.append(
                f"Packwiz index hash mismatch for catalog proof {namespace}: "
                f"index={index_entry.get('hash')!r} actual={actual_metadata_sha}"
            )
        if proof.get("index_sha256") != index_entry.get("hash"):
            errors.append(f"Packwiz proof index hash disagrees with index.toml for namespace {namespace}")
        try:
            metadata_payload = tomllib.loads(metadata_path.read_text(encoding="utf-8"))
        except (OSError, tomllib.TOMLDecodeError) as exc:
            errors.append(f"could not parse Packwiz metadata for catalog proof {namespace}: {exc}")
            continue
        if proof.get("filename") != metadata_payload.get("filename"):
            errors.append(f"Packwiz proof filename disagrees with metadata for namespace {namespace}")
        download = metadata_payload.get("download")
        if not isinstance(download, dict):
            errors.append(f"Packwiz metadata for catalog proof {namespace} has no download table")
        else:
            for proof_key, metadata_key in (("download_hash_format", "hash-format"), ("download_hash", "hash")):
                if proof.get(proof_key) != download.get(metadata_key):
                    errors.append(f"Packwiz proof {proof_key} disagrees with metadata for namespace {namespace}")
    observed_unverified: set[str] = set()
    for index, entry in enumerate(entries):
        if not isinstance(entry, dict):
            errors.append(f"ID catalog entry[{index}] is not an object")
            continue
        iid = entry.get("id")
        if not isinstance(iid, str) or ":" not in iid:
            errors.append(f"ID catalog entry[{index}] has invalid item id {iid!r}")
            continue
        if not isinstance(entry.get("source_jar"), str) or not entry.get("source_jar"):
            errors.append(f"ID catalog entry {iid} lacks source_jar provenance")
        if not isinstance(entry.get("source_entry"), str) or not entry.get("source_entry"):
            errors.append(f"ID catalog entry {iid} lacks source_entry provenance")
        if "max_stack_size" in entry:
            value = entry.get("max_stack_size")
            if value is not None and (not isinstance(value, int) or isinstance(value, bool) or value <= 0):
                errors.append(f"ID catalog entry {iid} has invalid max_stack_size {value!r}")
            if value is not None and iid in details["stack_limits"] and details["stack_limits"].get(iid) != value:
                errors.append(f"ID catalog stack metadata disagrees with entry {iid}")
            if value is not None and iid not in details["stack_limits"]:
                details["stack_limits"][iid] = value
        namespace = iid.split(":", 1)[0]
        proof = proofs.get(namespace)
        if not isinstance(proof, dict):
            errors.append(f"ID catalog entry {iid} lacks Packwiz proof for namespace {namespace}")
        else:
            if entry.get("source_jar") != proof.get("filename"):
                errors.append(
                    f"ID catalog entry {iid} cites JAR {entry.get('source_jar')!r}, "
                    f"but Packwiz proof pins {proof.get('filename')!r}"
                )
            if not isinstance(entry.get("artifact_verified"), bool):
                errors.append(f"ID catalog entry {iid} lacks boolean artifact_verified status")
            elif entry.get("artifact_verified") is not True:
                observed_unverified.add(namespace)
            if proof.get("artifact_verified") is not entry.get("artifact_verified"):
                errors.append(f"ID catalog entry {iid} disagrees with namespace artifact proof status")
        ids.add(iid)
    details["entry_count"] = len(ids)
    details["unverified_namespaces"] = sorted(observed_unverified)
    declared_verified = payload.get("verified_namespaces", []) if isinstance(payload, dict) else []
    declared_unverified = payload.get("unverified_namespaces", []) if isinstance(payload, dict) else []
    expected_verified = sorted(namespace for namespace, proof in proofs.items() if proof.get("artifact_verified") is True)
    expected_unverified = sorted(namespace for namespace, proof in proofs.items() if proof.get("artifact_verified") is not True)
    if not isinstance(declared_verified, list) or sorted(declared_verified) != expected_verified:
        errors.append("ID catalog verified_namespaces does not match Packwiz artifact proof statuses")
    if not isinstance(declared_unverified, list) or sorted(declared_unverified) != expected_unverified:
        errors.append("ID catalog unverified_namespaces does not match Packwiz artifact proof statuses")
    return ids, errors, details


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate the current five-chapter VvH campaign")
    parser.add_argument("--root", type=Path, default=HERE.parent)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    root = args.root.resolve()
    chapters, groups = source.build_campaign()
    errors: list[str] = []
    warnings: list[str] = []
    catalog_item_ids, catalog_errors, catalog_details = load_catalog_item_ids(root)
    errors.extend(catalog_errors)
    if catalog_details.get("unverified_namespaces"):
        warnings.append(
            "catalog exact JAR proof is partial; metadata-only namespaces: "
            + ", ".join(catalog_details["unverified_namespaces"])
        )
    approved_nonvanilla_items = VERIFIED_NONVANILLA_ITEMS | catalog_item_ids
    approved_nonvanilla_icons = VERIFIED_NONVANILLA_ICONS | catalog_item_ids
    used_items: set[str] = set()
    used_icons: set[str] = set()
    used_advancements: set[str] = set()
    used_spells: set[str] = set()
    used_components: set[str] = set()
    used_images: set[str] = set()

    emitted_details, emitted_errors, emitted_warnings = validate_emitted_files(
        root, catalog_details.get("stack_limits", {})
    )
    errors.extend(emitted_errors)
    warnings.extend(emitted_warnings)
    emitted_item_ids = set(emitted_details.get("used_items", []))
    used_items.update(emitted_item_ids)
    for iid in sorted(emitted_item_ids):
        if not isinstance(iid, str) or ":" not in iid:
            errors.append(f"emitted output contains malformed item id {iid!r}")
        elif not iid.startswith("minecraft:") and iid not in approved_nonvanilla_items:
            errors.append(f"unverified exact item id in emitted output: {iid}")

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
    # The reviewed guest exception deliberately allows any two witnessed
    # clauses; an explicit lower value would silently turn the Charter into a
    # one-of-three bypass. Keep the policy in the validator rather than only
    # in prose so a mutation cannot weaken the gate.
    effective_charter_min = charter_terminal.get("min_required_dependencies", len(charter_terminal["dependencies"]))
    if effective_charter_min != 2:
        errors.append("Charter terminal must require at least two of three clauses")
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
    # The reviewed 777a1e0 kit is deliberately lightweight: food, records,
    # shelter, a shield, and one Sprocket.  Neutral is an opt-out, not a free
    # full-iron combat loadout; the old requirement was a stale policy copy.
    required_neutral = {
        "minecraft:shield", "minecraft:white_bed", "minecraft:cooked_beef",
        "minecraft:spyglass", "minecraft:emerald", "minecraft:paper", "numismatics:sprocket",
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
    if neutral_food < 16:
        errors.append(f"Neutral starter food is {neutral_food}, expected at least 16 cooked meals")
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
                if not iid.startswith("minecraft:") and iid not in approved_nonvanilla_items:
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
        if not icon.startswith("minecraft:") and icon not in approved_nonvanilla_icons:
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
        # These are useful continuity handoffs in the reviewed faction trees
        # (for example a blood bottle reward followed by a blood-bottle task).
        # Keep them visible, but only block a release when the descendant
        # consumes the same item and therefore makes the handoff impossible.
        warnings.extend(
            f"reward/task continuity overlap {c['item']}: {c['ancestor']} -> {c['descendant']}"
            for c in collisions
        )

    # Market economy (two-wing storefront model, redesigned 2026-09-07).
    # Purchase cooldowns are short (3/5 min); only the currency faucet stays
    # weekly. FTB Quests uses a shared claim key for team rewards, so every
    # paid bundle must be team-scoped and excluded from claim-all. Quest
    # progress itself is still team progress; team_reward does not change it.
    repeatables = [q for q in quest_by_id.values() if q.get("can_repeat")]
    MARKET_BUILDING_COOLDOWN = 3 * 60
    MARKET_PROGRESSION_COOLDOWN = 5 * 60
    expected_market_prices = {
        source.qid(5, 2): 1,    # Field Kit: 1 Bevel
        source.qid(5, 3): 2,    # Works Kit: 1 Sprocket
        source.qid(5, 15): 2,   # Village Timber Kit: 1 Sprocket
        source.qid(5, 5): 4,    # Create Starter Kit: 2 Sprockets
        source.qid(5, 4): 2,    # Iron's Spells Starter Kit: 1 Sprocket
        source.qid(5, 9): 2,    # Recovery Crate: 1 Sprocket
        source.qid(5, 10): 4,   # Transit Crate: 2 Sprockets
        source.qid(5, 7): 4,    # Concord Bond: 2 Sprockets, below the 1-Cog ceiling
        source.qid(5, 17): 4,   # Celestial Spire Crate: 2 Sprockets
        source.qid(5, 18): 4,   # Sanctified Brewery Crate: 2 Sprockets
        source.qid(5, 19): 4,   # Frontier Watch Crate: 2 Sprockets
        source.qid(5, 20): 4,   # Heavy Bastion Crate: 2 Sprockets
        source.qid(5, 21): 4,   # Create Deco Palette: 2 Sprockets
        source.qid(5, 22): 4,   # Fortress Kit: 2 Sprockets
        source.qid(5, 23): 4,   # Create Builder's Palette: 2 Sprockets
        source.qid(5, 24): 4,   # Abyssal Deepworks Palette: 2 Sprockets
    }
    expected_market_cooldowns = {
        source.qid(5, 3): MARKET_BUILDING_COOLDOWN,
        source.qid(5, 15): MARKET_BUILDING_COOLDOWN,
        source.qid(5, 17): MARKET_BUILDING_COOLDOWN,
        source.qid(5, 18): MARKET_BUILDING_COOLDOWN,
        source.qid(5, 19): MARKET_BUILDING_COOLDOWN,
        source.qid(5, 20): MARKET_BUILDING_COOLDOWN,
        source.qid(5, 21): MARKET_BUILDING_COOLDOWN,
        source.qid(5, 22): MARKET_BUILDING_COOLDOWN,
        source.qid(5, 23): MARKET_BUILDING_COOLDOWN,
        source.qid(5, 24): MARKET_BUILDING_COOLDOWN,
        source.qid(5, 2): MARKET_PROGRESSION_COOLDOWN,
        source.qid(5, 5): MARKET_PROGRESSION_COOLDOWN,
        source.qid(5, 4): MARKET_PROGRESSION_COOLDOWN,
        source.qid(5, 9): MARKET_PROGRESSION_COOLDOWN,
        source.qid(5, 10): MARKET_PROGRESSION_COOLDOWN,
        source.qid(5, 7): MARKET_PROGRESSION_COOLDOWN,
    }
    MARKET_DEPARTMENTS = {
        source.qid(5, 3): "building",
        source.qid(5, 15): "building",
        source.qid(5, 17): "building",
        source.qid(5, 18): "building",
        source.qid(5, 19): "building",
        source.qid(5, 20): "building",
        source.qid(5, 21): "building",
        source.qid(5, 22): "building",
        source.qid(5, 23): "building",
        source.qid(5, 24): "building",
        source.qid(5, 2): "progression",
        source.qid(5, 5): "progression",
        source.qid(5, 4): "progression",
        source.qid(5, 9): "progression",
        source.qid(5, 10): "progression",
        source.qid(5, 7): "civic",
        source.qid(5, 6): "faucet",
    }
    # General masonry kits include flexible raw Stone. Specialist decorative
    # palettes can use finished masonry selected for their architecture.
    MARKET_GENERAL_MASONRY_KITS = {source.qid(5, 3), source.qid(5, 7), source.qid(5, 15), source.qid(5, 22)}
    MARKET_PROHIBITED_PREMIUMS = {
        "minecraft:diamond",
        "minecraft:netherite_ingot",
        "minecraft:netherite_scrap",
        "minecraft:elytra",
        "minecraft:nether_star",
        "minecraft:dragon_egg",
        "create:precision_mechanism",
        "numismatics:bevel",
        "numismatics:sprocket",
        "numismatics:cog",
        "numismatics:crown",
        "numismatics:sun",
        "numismatics:spur",
    }
    # Do not freeze the number of catalogue entries in the validator.  New
    # palettes are normal campaign evolution; every repeatable still has to
    # live in the Market, while the Rumour Ledger remains the sole faucet.
    market_quest_ids = {q["id"] for q in quest_by_id.values() if chapter_by_quest[q["id"]] == "ch05_market_services"}
    for repeatable in repeatables:
        if repeatable["id"] not in market_quest_ids:
            errors.append(f"repeatable quest {repeatable['id']} is outside Chapter 5 Market Services")
    # Correct live crate/task IDs; reward IDs survive when item identity does.
    protected_crates = {
        "7A11C0DF00500011": "7A11C1DF00500021",
        "7A11C0DF00500012": "7A11C1DF00500022",
        "7A11C0DF00500013": "7A11C1DF00500023",
        "7A11C0DF00500014": "7A11C1DF00500024",
    }
    for crate_id, task_id in protected_crates.items():
        quest = quest_by_id.get(crate_id)
        if quest is None:
            errors.append(f"protected Market crate ID {crate_id} is missing")
        elif task_id not in {task["id"] for task in quest.get("tasks", [])}:
            errors.append(f"protected Market crate {crate_id} lost its payment task {task_id}")
    fixture_path = root / "docs/vvh/evidence/save-migration-baseline.json"
    try:
        baseline = json.loads(fixture_path.read_text(encoding="utf-8"))
        for group in baseline["scope_transitions"]:
            if group["quest_id"] not in protected_crates:
                continue
            rewards = quest_by_id.get(group["quest_id"], {}).get("rewards", [])
            current = {reward["id"]: item_id(reward) for reward in rewards}
            for reward_id in group["reward_ids"]:
                if current.get(reward_id) != group["item"]:
                    errors.append(f"protected unchanged crate reward {reward_id} must retain item {group['item']}")
    except (OSError, ValueError, KeyError, TypeError) as exc:
        errors.append(f"cannot validate reviewed crate reward identities: {exc}")
    ch5_quests = [q for q in quest_by_id.values() if chapter_by_quest[q["id"]] == "ch05_market_services"]
    for quest in ch5_quests:
        blob = (quest["title"] + " " + " ".join(quest.get("description", []))).lower()
        if "handcrafted" in blob:
            errors.append(f"rejected Handcrafted kit concept reappeared in {quest['id']}")
        department = MARKET_DEPARTMENTS.get(quest["id"])
        if department is None:
            title_lower = quest.get("title", "").lower()
            if any(word in title_lower for word in ("kit", "palette", "crate", "works")) or float(quest.get("x", 0)) < 0:
                department = "building"
            elif abs(float(quest.get("x", 0))) <= 1.5:
                department = "central"
            else:
                department = "progression"
        if department == "building" and float(quest.get("x", 0)) >= 0:
            errors.append(f"building Market quest {quest['id']} must stay in the left department")
        if department == "progression" and float(quest.get("x", 0)) <= 0:
            errors.append(f"progression Market quest {quest['id']} must stay in the right department")
        if department in {"faucet", "civic"} and abs(float(quest.get("x", 0))) > 1.5:
            errors.append(f"central Market node {quest['id']} drifted out of the information column")
    # Chapter-level hidden dependency lines: Market only.
    for ch in chapters:
        expected_default = ch.filename == "ch05_market_services"
        if bool(ch.default_hide_dependency_lines) != expected_default:
            errors.append(f"{ch.filename} default_hide_dependency_lines should be {expected_default}")
    sinks: list[dict[str, Any]] = []
    faucets: list[dict[str, Any]] = []
    market_report: list[dict[str, Any]] = []
    for quest in repeatables:
        consumed = [t for t in quest["tasks"] if t.get("type") == "item" and t.get("consume_items")]
        if not consumed:
            errors.append(f"repeatable {quest['id']} has no consumed input")
            continue
        input_ids = {item_id(t) for t in consumed}
        output_ids = {item_id(r) for r in quest["rewards"]}
        if input_ids & output_ids:
            errors.append(f"repeatable {quest['id']} reproduces its own input {sorted(input_ids & output_ids)}")
        if any(item_id(t) in COIN_VALUE for t in consumed):
            if not quest.get("rewards"):
                errors.append(f"market sink {quest['id']} has no shared reward bundle")
            if len(consumed) != 1 or item_id(consumed[0]) not in COIN_VALUE:
                errors.append(f"market sink {quest['id']} does not consume one unambiguous currency price")
            price = sum(COIN_VALUE[item_id(t)] * item_count(t) for t in consumed if item_id(t) in COIN_VALUE)
            sinks.append({"id": quest["id"], "title": quest["title"], "price_bevel_equivalent": price})
            expected_price = expected_market_prices.get(quest["id"])
            if expected_price is not None and expected_price != price:
                errors.append(f"market sink {quest['id']} costs {price}, expected {expected_price}")
            department = MARKET_DEPARTMENTS.get(quest["id"])
            if department is None:
                title_lower = quest.get("title", "").lower()
                if any(word in title_lower for word in ("kit", "palette", "crate", "works")) or float(quest.get("x", 0)) < 0:
                    department = "building"
                else:
                    department = "progression"
            expected_cooldown = expected_market_cooldowns.get(
                quest["id"],
                MARKET_BUILDING_COOLDOWN if department == "building" else MARKET_PROGRESSION_COOLDOWN,
            )
            if quest.get("repeat_cooldown") != expected_cooldown:
                errors.append(f"market sink {quest['id']} cooldown {quest.get('repeat_cooldown')} differs from expected {expected_cooldown}")
            if bool(quest.get("task_screen_only", False)) or any(bool(task.get("task_screen_only", False)) for task in quest["tasks"]):
                errors.append(f"market sink {quest['id']} uses task_screen_only; ordinary purchases must submit in the quest book")
            if any(not bool(r.get("team_reward", False)) for r in quest["rewards"]):
                errors.append(f"market sink {quest['id']} has an individual reward key; one payment must grant one shared team entitlement")
            if any(not bool(r.get("exclude_from_claim_all", False)) for r in quest["rewards"]):
                errors.append(f"market sink {quest['id']} rewards must be manually claimed and excluded from claim-all")
            if any(item_id(reward) in COIN_VALUE for reward in quest["rewards"]):
                errors.append(f"market sink {quest['id']} returns currency")
            if any(item_id(reward) in MARKET_PROHIBITED_PREMIUMS for reward in quest["rewards"]):
                errors.append(f"market sink {quest['id']} contains a prohibited premium item")
            copy = (quest.get("subtitle", "") + " " + " ".join(quest.get("description", [])))
            if "weekly" in copy.lower():
                errors.append(f"market sink {quest['id']} still claims weekly behaviour after the short-cooldown redesign")
            copy_lower = " ".join(quest.get("description", [])).lower()
            if "personal" in copy_lower:
                errors.append(f"market sink {quest['id']} still claims a personal entitlement")
            if "team" not in copy_lower or "shared" not in copy_lower:
                errors.append(f"market sink {quest['id']} does not state its shared FTB Team claim scope")
            if "claim" not in copy_lower or "manual" not in copy_lower:
                errors.append(f"market sink {quest['id']} does not state manual reward claiming")
            if "order construction grant" in copy_lower:
                errors.append(f"market sink {quest['id']} mentions the obsolete Order Construction Grant")
            coin_name = {"numismatics:bevel": "bevel", "numismatics:sprocket": "sprocket", "numismatics:cog": "cog"}.get(item_id(consumed[0]), "")
            expected_count = item_count(consumed[0])
            if coin_name and f"{expected_count} {coin_name}" not in copy_lower:
                errors.append(f"market sink {quest['id']} does not display exact consumed price {expected_count} {coin_name}")
            reward_items = [item_id(r) for r in quest["rewards"]]
            if quest["id"] in MARKET_GENERAL_MASONRY_KITS:
                if "minecraft:stone" not in reward_items:
                    errors.append(f"masonry kit {quest['id']} lacks flexible raw Stone")
                if "minecraft:cobblestone" in reward_items:
                    errors.append(f"masonry kit {quest['id']} uses Cobblestone instead of raw Stone")
            namespaces = sorted({iid.split(":")[0] for iid in reward_items if iid and ":" in iid})
            unknown_stack_items = sorted(
                iid for iid in reward_items
                if iid and stack_limit_for_item(iid, catalog_details.get("stack_limits", {})) is None
            )
            stack_equivalents = sum(
                item_count(reward) / stack_limit_for_item(item_id(reward), catalog_details.get("stack_limits", {}))
                for reward in quest["rewards"]
                if item_id(reward) and stack_limit_for_item(item_id(reward), catalog_details.get("stack_limits", {}))
            )
            market_report.append({
                "id": quest["id"],
                "title": quest["title"],
                "department": department,
                "price_bevel_equivalent": price,
                "cooldown_seconds": quest.get("repeat_cooldown"),
                "scope": "shared_team_entitlement",
                "reward_slots": len(quest["rewards"]),
                "full_stack_equivalents": round(stack_equivalents, 2),
                "unknown_stack_items": unknown_stack_items,
                "namespaces": namespaces,
            })
        if currency_value(quest["rewards"], team=True):
            faucets.append({"id": quest["id"], "title": quest["title"], "value_bevel_equivalent": currency_value(quest["rewards"], team=True)})
    sink_total = sum(s["price_bevel_equivalent"] for s in sinks)
    faucet_total = sum(f["value_bevel_equivalent"] for f in faucets)
    # The total is deliberately derived from the live board.  A hard-coded
    # total would become stale as palettes are added or repriced.
    if faucets != [{"id": source.qid(5, 6), "title": "Rumour Ledger", "value_bevel_equivalent": 1.0}]:
        errors.append(f"unexpected repeatable faucets: {faucets}")
    rumour = quest_by_id.get(source.qid(5, 6))
    if rumour is not None:
        if rumour.get("repeat_cooldown") != source.WEEK:
            errors.append("Rumour Ledger faucet cooldown is not the protected weekly schedule")
        if "team" not in " ".join(rumour.get("description", [])).lower():
            errors.append("Rumour Ledger does not state its team scope")
    premium_prices = [s["price_bevel_equivalent"] for s in sinks if s["price_bevel_equivalent"] >= 4]
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
    for key in ("quest_count", "counted_specialties", "branch_count"):
        if hunter[key] != vampire[key]:
            errors.append(f"faction parity mismatch in {key}: Hunter={hunter[key]} Vampire={vampire[key]}")
    if hunter["core_currency"] != vampire["core_currency"]:
        warnings.append(f"reviewed faction core currency differs: Hunter={hunter['core_currency']} Vampire={vampire['core_currency']}")
    if hunter["personal_completionism"] != vampire["personal_completionism"]:
        warnings.append(
            "faction personal completionism differs: "
            f"Hunter={hunter['personal_completionism']} Vampire={vampire['personal_completionism']}"
        )

    # Derive the cheapest personal-currency route from the live dependency
    # graph.  A missing min_required_dependencies value means all dependencies
    # (the FTB Quests default); a positive value selects the cheapest required
    # predecessors.  This replaces the retired hard-coded "any 3 of 8" and
    # "15 Bevel" claims in older reports.
    route_memo: dict[str, float] = {}
    route_stack: set[str] = set()

    def minimum_route_value(qid: str) -> float:
        if qid in route_memo:
            return route_memo[qid]
        if qid in route_stack:
            return float("inf")
        route_stack.add(qid)
        quest = quest_by_id[qid]
        predecessor_costs = [minimum_route_value(dep) for dep in deps.get(qid, []) if dep in quest_by_id]
        required = int(quest.get("min_required_dependencies", 0) or 0)
        if predecessor_costs and required <= 0:
            required = len(predecessor_costs)
        if required > len(predecessor_costs):
            total = float("inf")
        else:
            total = currency_value(quest.get("rewards", []), team=False)
            total += sum(sorted(predecessor_costs)[:required])
        route_stack.remove(qid)
        route_memo[qid] = total
        return total

    faction_route_lower_bounds = {
        "hunter_core_iii": minimum_route_value(source.qid(3, 3)),
        "vampire_core_iii": minimum_route_value(source.qid(4, 3)),
    }

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
            hidden = bool(quest.get("hide_dependency_lines", False)) or bool(ch.default_hide_dependency_lines)
            if hidden:
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
        if not source.output_matches(path, content):
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
        "catalog": catalog_details,
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
            "hunter_gate": {
                "kind": "dependency_thresholds",
                "thresholds": [
                    {
                        "id": quest["id"],
                        "title": quest["title"],
                        "dependencies": deps[quest["id"]],
                        "min_required_dependencies": quest.get("min_required_dependencies", 0),
                    }
                    for quest in chapters[2].quests
                    if quest.get("min_required_dependencies", 0) > 0
                ],
            },
            "vampire_gate": {
                "kind": "dependency_thresholds",
                "thresholds": [
                    {
                        "id": quest["id"],
                        "title": quest["title"],
                        "dependencies": deps[quest["id"]],
                        "min_required_dependencies": quest.get("min_required_dependencies", 0),
                    }
                    for quest in chapters[3].quests
                    if quest.get("min_required_dependencies", 0) > 0
                ],
            },
            "reward_descendant_task_collisions": collisions,
            "emitted_files": emitted_details,
        },
        "neutral": {
            "item_prerequisites": sum(t.get("type") == "item" for t in neutral["tasks"]),
            "starter_reward_count": len(neutral["rewards"]),
            "progression_children": neutral_children,
        },
        "parity": {"hunter": hunter, "vampire": vampire, "equal": hunter == vampire},
        "economy": {
            "coin_values_bevel_equivalent": COIN_VALUE,
            "minimum_faction_route_personal": min(faction_route_lower_bounds.values()),
            "minimum_faction_route_personal_by_core": faction_route_lower_bounds,
            "neutral_route_personal": currency_value(neutral["rewards"], team=False),
            "one_time_personal_raw_completionism": one_time_personal,
            "one_time_team_completionism": one_time_team,
            "purchase_cooldowns": {"building_seconds": MARKET_BUILDING_COOLDOWN, "progression_seconds": MARKET_PROGRESSION_COOLDOWN, "faucet_seconds": source.WEEK},
            "sinks": sinks,
            "sink_total": sink_total,
            "faucets": faucets,
            "faucet_total": faucet_total,
            "market_report": market_report,
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
        "sink_total": sink_total,
        "faucet_total": faucet_total,
        "report": str(output),
    }, indent=2))
    if errors:
        print("\n".join(f"ERROR: {error}" for error in errors))
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
