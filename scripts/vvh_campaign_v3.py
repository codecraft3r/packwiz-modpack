#!/usr/bin/env python3
"""Authoritative source for the live five-chapter VvH quest campaign.

The filename is retained for repository compatibility.  The source model below
represents only the current architecture: Charter, Calling choice, Lantern
Order, House of Night, and Market Services.  It never restores the retired
Free Companies/Common Ground/Odd Hours progression chapters.

Normal writes replace only the exact files this source owns.  Unknown chapter
files are reported but preserved.  ``--prune-retired`` removes only the named
historical chapter files listed in RETIRED_CHAPTER_FILES.
"""
from __future__ import annotations

import argparse
import json
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Iterable

Q_PREFIX = 0x7A11C0DF00000000
T_PREFIX = 0x7A11C1DF00000000
R_PREFIX = 0x7A11C2DF00000000
C_PREFIX = 0x7A11C3DF00000000
G_PREFIX = 0x7A11C4DF00000000
WEEK = 604800

RETIRED_CHAPTER_FILES = {
    "ch05_free_companies.snbt",
    "ch06_common_ground.snbt",
    "ch07_odd_hours.snbt",
    "ch08_market_services.snbt",
    "ch09_common_ground.snbt",
    "ch10_market_services.snbt",
}


def hid(prefix: int, chapter: int, index: int) -> str:
    return f"{prefix + chapter * 0x100000 + index:016X}"


def qid(chapter: int, index: int) -> str:
    return hid(Q_PREFIX, chapter, index)


def tid(chapter: int, index: int) -> str:
    return hid(T_PREFIX, chapter, index)


def rid(chapter: int, index: int) -> str:
    return hid(R_PREFIX, chapter, index)


def esc(value: str) -> str:
    return '"' + value.replace("\\", "\\\\").replace('"', '\\"').replace("\n", "\\n") + '"'


def snbt(value: Any, indent: int = 0) -> str:
    pad = "\t" * indent
    if isinstance(value, bool):
        return "true" if value else "false"
    if isinstance(value, int):
        return str(value)
    if isinstance(value, float):
        return f"{value:.1f}d"
    if isinstance(value, str):
        return esc(value)
    if isinstance(value, list):
        if not value:
            return "[ ]"
        simple = all(isinstance(v, (str, int, float, bool)) for v in value)
        if simple and len(value) <= 4:
            return "[" + ", ".join(snbt(v, indent) for v in value) + "]"
        rows = ["["]
        rows.extend(f"{pad}\t{snbt(v, indent + 1)}" for v in value)
        rows.append(f"{pad}]")
        return "\n".join(rows)
    if isinstance(value, dict):
        if not value:
            return "{ }"
        simple = all(not isinstance(v, (dict, list)) for v in value.values()) and len(value) <= 4
        if simple:
            body = ", ".join(
                f"{k if re.fullmatch(r'[A-Za-z0-9_]+', k) else esc(k)}: {snbt(v, indent)}"
                for k, v in value.items()
            )
            return "{ " + body + " }"
        rows = ["{"]
        for key, val in value.items():
            rendered_key = key if re.fullmatch(r"[A-Za-z0-9_]+", key) else esc(key)
            rows.append(f"{pad}\t{rendered_key}: {snbt(val, indent + 1)}")
        rows.append(f"{pad}}}")
        return "\n".join(rows)
    raise TypeError(f"unsupported SNBT value: {type(value)!r}")


def item_task(ch: int, idx: int, item: str, count: int = 1, title: str | None = None, *, consume: bool = False) -> dict[str, Any]:
    task: dict[str, Any] = {
        "consume_items": consume,
        "id": tid(ch, idx),
        "item": {"count": 1, "id": item},
    }
    if count != 1:
        task["count"] = count
    if title:
        task["title"] = title
    task["type"] = "item"
    return task


def advancement_task(ch: int, idx: int, advancement: str) -> dict[str, Any]:
    return {"advancement": advancement, "criterion": "", "id": tid(ch, idx), "type": "advancement"}


def check_task(ch: int, idx: int, title: str) -> dict[str, Any]:
    return {"id": tid(ch, idx), "title": title, "type": "checkmark"}


def item_reward(ch: int, idx: int, item: str, count: int = 1, *, team: bool = False, title: str | None = None, components: dict[str, Any] | None = None) -> dict[str, Any]:
    item_obj: dict[str, Any] = {"count": count, "id": item}
    if components:
        item_obj["components"] = components
    reward: dict[str, Any] = {
        "id": rid(ch, idx),
        "item": item_obj,
        "team_reward": team,
    }
    if title:
        reward["title"] = title
    reward["type"] = "item"
    return reward


def scroll_reward(ch: int, idx: int, spell: str, title: str, *, level: int = 1, team: bool = False) -> dict[str, Any]:
    return {
        "id": rid(ch, idx),
        "item": {
            "components": {
                "irons_spellbooks:spell_container": {
                    "data": [{"id": spell, "index": 0, "level": level, "locked": False}],
                    "maxSpells": 1,
                    "mustEquip": False,
                    "spellWheel": False,
                }
            },
            "count": 1,
            "id": "irons_spellbooks:scroll",
        },
        "team_reward": team,
        "title": title,
        "type": "item",
    }


@dataclass
class Chapter:
    number: int
    filename: str
    title: str
    group: str
    icon: str
    order: int
    images: list[dict[str, Any]] = field(default_factory=list)
    quests: list[dict[str, Any]] = field(default_factory=list)

    @property
    def id(self) -> str:
        return hid(C_PREFIX, self.number, 0)

    def add(
        self,
        index: int,
        *,
        title: str,
        subtitle: str,
        description: str,
        icon: str,
        x: float,
        y: float,
        tasks: list[dict[str, Any]],
        rewards: list[dict[str, Any]] | None = None,
        dependencies: Iterable[str] = (),
        optional: bool = False,
        shape: str = "",
        size: float = 1.0,
        min_deps: int = 0,
        can_repeat: bool = False,
        cooldown: int = 0,
        hide_dependency_lines: bool = False,
    ) -> str:
        quest: dict[str, Any] = {
            "dependencies": list(dependencies),
            "description": [description],
            "icon": {"id": icon},
            "id": qid(self.number, index),
        }
        if hide_dependency_lines:
            quest["hide_dependency_lines"] = True
        if optional:
            quest["optional"] = True
        if min_deps:
            quest["min_required_dependencies"] = min_deps
        if can_repeat:
            quest["can_repeat"] = True
            quest["repeat_cooldown"] = cooldown
        quest.update(
            {
                "rewards": rewards or [],
                "shape": shape,
                "size": size,
                "subtitle": subtitle,
                "tasks": tasks,
                "title": title,
                "x": x,
                "y": y,
            }
        )
        self.quests.append(quest)
        return quest["id"]


def build_charter(group: str) -> Chapter:
    ch = Chapter(
        1,
        "ch01_island_charter",
        "01 · The Island Charter",
        group,
        "minecraft:compass",
        0,
        images=[{
            "alpha": 18,
            "height": 5,
            "image": "poiesis:textures/questpics/vvh/rivalry_without_ruin.png",
            "order": -40,
            "rotation": 0.0,
            "width": 12,
            "x": 0,
            "y": 3,
        }],
    )
    opener = ch.add(
        1,
        title="Island Charter",
        subtitle="Orientation · A persistent world",
        description="This island is meant to accumulate useful places, not disposable victories. Read every promise below; the quest book opens only after the rules that protect lasting work are acknowledged.",
        icon="minecraft:compass",
        x=0,
        y=-5,
        shape="hexagon",
        size=1.5,
        tasks=[check_task(1, 1, "I have read the welcome")],
        rewards=[
            item_reward(1, 1, "minecraft:map"),
            item_reward(1, 2, "minecraft:torch", 16),
        ],
    )
    public = ch.add(
        6,
        title="Name Public Doors",
        subtitle="Required · Public access",
        description="A public road, workshop, or refuge needs a named entrance and a responsible keeper. Claims remain inviolable; public access exists only where the owner clearly grants it.",
        icon="minecraft:oak_door",
        x=-4,
        y=-1.5,
        shape="diamond",
        tasks=[check_task(1, 6, "I understand how public access is granted")],
        dependencies=[opener],
    )
    consent = ch.add(
        3,
        title="Consent First",
        subtitle="Required · PvP and social play",
        description="PvP, pranks, and faction drama are opt-in. A request to stop ends the interaction immediately; silence, absence, or faction membership is not consent.",
        icon="minecraft:shield",
        x=0,
        y=-1.5,
        shape="octagon",
        tasks=[check_task(1, 3, "I agree to stop on request")],
        dependencies=[opener],
    )
    rivalry = ch.add(
        7,
        title="Leave Work Standing",
        subtitle="Required · Rivalry boundaries",
        description="Rivalry may use races, photography, markets, propaganda, and reversible jokes. It never requires theft, griefing, forced entry, destructive sabotage, or targeting Neutral players.",
        icon="exposure:camera",
        x=4,
        y=-1.5,
        shape="octagon",
        tasks=[check_task(1, 7, "I will keep rivalry claim-safe and reversible")],
        dependencies=[opener],
    )
    ch.add(
        5,
        title="Sign the Charter",
        subtitle="Required · Public access · consent · rivalry",
        description="You have read the rules that keep a persistent world playable: name public access, obtain consent, and keep rivalry reversible. The calling board is now open.",
        icon="minecraft:writable_book",
        x=0,
        y=3,
        shape="hexagon",
        size=1.6,
        tasks=[check_task(1, 5, "I accept the Charter promises")],
        rewards=[item_reward(1, 3, "minecraft:bread", 16)],
        dependencies=[public, consent, rivalry],
    )
    return ch


def build_callings(group: str) -> Chapter:
    ch = Chapter(
        2,
        "ch02_callings",
        "02 · Choose a Calling",
        group,
        "minecraft:spyglass",
        0,
        images=[{
            "alpha": 22,
            "height": 4,
            "image": "poiesis:textures/questpics/vvh/free_company_writ.png",
            "order": -40,
            "rotation": 0.0,
            "width": 4,
            "x": 0,
            "y": 0,
        }],
    )
    opener = ch.add(
        1,
        title="Three Callings",
        subtitle="House · Neutral · Order",
        description="Choose the role you want to maintain now. House and Order open faction campaigns; Neutral is a protected opt-out that supplies a practical start and exits faction progression without closing ordinary services.",
        icon="minecraft:spyglass",
        x=0,
        y=-5,
        shape="hexagon",
        size=1.5,
        tasks=[check_task(2, 1, "I reviewed all three callings")],
        dependencies=[qid(1, 5)],
    )
    house = ch.add(
        2,
        title="Join the House",
        subtitle="Vampire · Nightbound route",
        description="Become a Vampire through Vampirism and keep the fang that marks the transformation. The House campaign begins with shelter and blood logistics, then opens ritual, magic, transport, and hospitality specialties.",
        icon="vampirism:vampire_fang",
        x=-5,
        y=-1,
        shape="hexagon",
        size=1.3,
        optional=True,
        tasks=[
            item_task(2, 2, "vampirism:vampire_fang", title="Carry a vampire fang"),
            advancement_task(2, 3, "vampirism:vampire/become_vampire"),
        ],
        rewards=[
            item_reward(2, 1, "numismatics:sprocket"),
            item_reward(2, 2, "vampirism:vampire_cloak_white_black"),
            item_reward(2, 20, "minecraft:glass_bottle", 8),
        ],
        dependencies=[opener],
    )
    neutral = ch.add(
        3,
        title="Choose Neutral",
        subtitle="Protected opt-out · No faction tree",
        description="Choose Neutral when you want ordinary survival, trade, infrastructure, and public services without faction obligations. This attestation is the entire civic route; it asks for no profession items and creates no hidden third faction.",
        icon="minecraft:iron_chestplate",
        x=0,
        y=-1,
        shape="gear",
        size=1.3,
        optional=True,
        tasks=[check_task(2, 4, "I choose Neutral and opt out of faction rivalry")],
        rewards=[
            item_reward(2, 3, "numismatics:sprocket"),
            item_reward(2, 5, "minecraft:cooked_beef", 32),
            item_reward(2, 6, "minecraft:iron_sword"),
            item_reward(2, 7, "minecraft:iron_pickaxe"),
            item_reward(2, 10, "minecraft:iron_axe"),
            item_reward(2, 11, "minecraft:iron_shovel"),
            item_reward(2, 12, "minecraft:iron_hoe"),
            item_reward(2, 13, "minecraft:shield"),
            item_reward(2, 14, "minecraft:white_bed"),
            item_reward(2, 15, "minecraft:iron_helmet"),
            item_reward(2, 16, "minecraft:iron_chestplate"),
            item_reward(2, 17, "minecraft:iron_leggings"),
            item_reward(2, 18, "minecraft:iron_boots"),
        ],
        dependencies=[opener],
    )
    order = ch.add(
        4,
        title="Join the Order",
        subtitle="Hunter · Lantern route",
        description="Become a Hunter through Vampirism and keep the garlic injection used to enter the profession. The Order campaign begins with field equipment, then opens medicine, wards, reconnaissance, construction, and holy support.",
        icon="vampirism:injection_garlic",
        x=5,
        y=-1,
        shape="hexagon",
        size=1.3,
        optional=True,
        tasks=[
            item_task(2, 7, "vampirism:injection_garlic", title="Carry a garlic injection"),
            advancement_task(2, 8, "vampirism:hunter/become_hunter"),
        ],
        rewards=[
            item_reward(2, 8, "numismatics:sprocket"),
            item_reward(2, 9, "minecraft:crossbow"),
            item_reward(2, 19, "supplementaries:rope_arrow", 8),
        ],
        dependencies=[opener],
    )
    ch.add(
        7,
        title="Keep Doors Open",
        subtitle="Complete any one calling",
        description="Your first calling determines which faction campaign, if any, you maintain. Market services remain open to House, Order, and Neutral teams, and later curiosity does not rewrite the protected opt-out.",
        icon="minecraft:oak_door",
        x=0,
        y=3,
        shape="hexagon",
        size=1.5,
        min_deps=1,
        tasks=[check_task(2, 9, "I confirm this calling")],
        dependencies=[house, neutral, order],
    )
    return ch


def hunter_spell_rewards() -> list[dict[str, Any]]:
    return [
        item_reward(3, 20, "numismatics:sprocket"),
        item_reward(3, 21, "irons_spellbooks:uncommon_ink", 16),
        item_reward(3, 22, "irons_spellbooks:rare_ink", 8),
        scroll_reward(3, 23, "irons_spellbooks:heal", "Scroll of Heal"),
        scroll_reward(3, 24, "irons_spellbooks:divine_smite", "Scroll of Divine Smite"),
        scroll_reward(3, 25, "irons_spellbooks:recall", "Scroll of Recall"),
    ]


def build_hunters(group: str) -> Chapter:
    ch = Chapter(
        3,
        "ch03_lantern_order",
        "03 · Lantern Order",
        group,
        "vampirism:hunter_table",
        1,
        images=[
            {"alpha": 22, "height": 7, "image": "poiesis:textures/questpics/vvh/lantern_order_holy_panorama.png", "order": -40, "rotation": 0.0, "width": 5, "x": -11, "y": 2},
            {"alpha": 20, "height": 7, "image": "poiesis:textures/questpics/vvh/holy_public_ward.png", "order": -39, "rotation": 0.0, "width": 5, "x": 11, "y": 5},
            {"alpha": 28, "height": 2.5, "image": "poiesis:textures/questpics/vvh/holy_school_crest.png", "order": -38, "rotation": 0.0, "width": 2.5, "x": 0, "y": 10},
        ],
    )
    core1 = ch.add(
        1,
        title="Salt and Steel",
        subtitle="Tier I · Foundation",
        description="Build the field bench that makes Hunter work repeatable: a Hunter Table, stakes, and a normal Hunter Axe. The reward supplies a complete working coat so the route starts functional rather than fashionable.",
        icon="vampirism:hunter_table",
        x=0,
        y=-10,
        shape="hexagon",
        size=1.4,
        tasks=[
            item_task(3, 1, "vampirism:hunter_table", title="Inspect a Hunter Table"),
            item_task(3, 2, "vampirism:stake", 4, "Carry four stakes"),
            item_task(3, 3, "vampirism:hunter_axe_normal", title="Inspect a normal Hunter Axe"),
        ],
        rewards=[
            item_reward(3, 1, "numismatics:bevel"),
            item_reward(3, 2, "vampirism:hunter_coat_head_normal"),
            item_reward(3, 3, "vampirism:hunter_coat_chest_normal"),
            item_reward(3, 4, "vampirism:hunter_coat_legs_normal"),
            item_reward(3, 5, "vampirism:hunter_coat_feet_normal"),
        ],
        dependencies=[qid(2, 4)],
    )
    building_supplies_rewards = [
        item_reward(3, 6, "numismatics:sprocket"),
        *[item_reward(3, 100 + i, "minecraft:stone", 64) for i in range(24)],
        *[item_reward(3, 130 + i, "minecraft:oak_log", 64) for i in range(5)],
        *[item_reward(3, 150 + i, "minecraft:spruce_log", 64) for i in range(5)],
        item_reward(3, 10, "minecraft:iron_ingot", 64),
        item_reward(3, 70, "minecraft:copper_ingot", 64),
        item_reward(3, 72, "minecraft:stonecutter"),
        item_reward(3, 73, "supplementaries:wrench"),
    ]
    core2 = ch.add(
        2,
        title="Building Supplies",
        subtitle="Tier II · Construction stock",
        description="Gather an essential construction stock of stone bricks, logs, iron bars, and lanterns. Completing this foundation rewards a massive building stockpile with twenty-four full stacks of stone, five full stacks each of oak and spruce logs, a sprocket, iron, copper, a stonecutter, and a wrench.",
        icon="minecraft:stone",
        x=0,
        y=-7,
        shape="gear",
        size=1.3,
        tasks=[
            item_task(3, 4, "minecraft:stone_bricks", 64, "Inspect sixty-four Stone Bricks"),
            item_task(3, 5, "minecraft:oak_log", 32, "Inspect thirty-two Oak Logs"),
            item_task(3, 6, "minecraft:iron_bars", 16, "Inspect sixteen Iron Bars"),
            item_task(3, 70, "minecraft:lantern", 8, "Inspect eight Lanterns"),
        ],
        rewards=building_supplies_rewards,
        dependencies=[core1],
    )
    core3 = ch.add(
        3,
        title="Long Watch",
        subtitle="Tier III · Logistics",
        description="Add a Hunter Weapon Table, basic crossbow, and a real reserve of vampire-killer quarrels. The Order can now equip a second patrol instead of depending on one veteran's inventory.",
        icon="vampirism:weapon_table",
        x=0,
        y=-4,
        shape="gear",
        size=1.3,
        tasks=[
            item_task(3, 7, "vampirism:weapon_table", title="Inspect a Hunter Weapon Table"),
            item_task(3, 8, "vampirism:basic_crossbow", title="Carry a basic Hunter crossbow"),
            item_task(3, 9, "vampirism:crossbow_arrow_vampire_killer", 16, "Carry sixteen killer quarrels"),
        ],
        rewards=[
            item_reward(3, 11, "numismatics:sprocket", 2),
            item_reward(3, 12, "vampirism:crossbow_arrow_normal", 64),
            item_reward(3, 13, "minecraft:feather", 32),
            item_reward(3, 14, "vampirism:crossbow_arrow_vampire_killer", 16),
            item_reward(3, 15, "minecraft:iron_ingot", 32),
        ],
        dependencies=[core2],
    )

    wizard_tower_rewards = [
        item_reward(3, 75, "numismatics:sprocket"),
        *[item_reward(3, 200 + i, "minecraft:cobbled_deepslate", 64) for i in range(24)],
        *[item_reward(3, 230 + i, "minecraft:dark_oak_log", 64) for i in range(5)],
        *[item_reward(3, 250 + i, "minecraft:sand", 64) for i in range(12)],
        item_reward(3, 270, "minecraft:scaffolding", 64),
        item_reward(3, 271, "minecraft:scaffolding", 64),
        item_reward(3, 76, "minecraft:candle", 64),
        item_reward(3, 77, "minecraft:lapis_lazuli", 64),
        item_reward(3, 78, "minecraft:gold_ingot", 64),
        item_reward(3, 272, "minecraft:amethyst_shard", 64),
        item_reward(3, 273, "minecraft:enchanting_table"),
        item_reward(3, 274, "minecraft:lectern"),
    ]
    b_wizard = ch.add(
        14,
        title="Arcane Spire",
        subtitle="Construction · High study",
        description="Lay the foundation for an arcane study and celestial spire overlooking the island. Gather deepslate, dark oak timber, and amethyst shards. The Order delivers a massive construction cache of deepslate, dark oak logs, sand for glasswork, scaffolding, candles, lapis, gold, amethyst, a lectern, and an enchanting table.",
        icon="irons_spellbooks:inscription_table",
        x=-6.5,
        y=-1.0,
        shape="square",
        optional=True,
        tasks=[
            item_task(3, 75, "minecraft:cobbled_deepslate", 32, "Inspect thirty-two Cobbled Deepslate"),
            item_task(3, 76, "minecraft:dark_oak_log", 32, "Inspect thirty-two Dark Oak Logs"),
            item_task(3, 78, "minecraft:amethyst_shard", 16, "Inspect sixteen Amethyst Shards"),
        ],
        rewards=wizard_tower_rewards,
        dependencies=[core3],
    )

    brewery_rewards = [
        item_reward(3, 79, "numismatics:sprocket"),
        *[item_reward(3, 300 + i, "abyssal_decor:raw_marble", 64) for i in range(18)],
        *[item_reward(3, 330 + i, "abyssal_decor:cinnamon_log", 64) for i in range(5)],
        *[item_reward(3, 350 + i, "abyssal_decor:frosted_glass", 64) for i in range(6)],
        item_reward(3, 370, "minecraft:scaffolding", 64),
        item_reward(3, 371, "minecraft:scaffolding", 64),
        item_reward(3, 375, "abyssal_decor:small_seabrass_pipes", 64),
        item_reward(3, 376, "abyssal_decor:seabrass_sconce", 64),
        item_reward(3, 80, "minecraft:redstone", 64),
        item_reward(3, 81, "minecraft:copper_ingot", 64),
        item_reward(3, 82, "minecraft:quartz", 64),
        item_reward(3, 372, "minecraft:blaze_rod", 8),
        item_reward(3, 373, "irons_spellbooks:alchemist_cauldron"),
        item_reward(3, 374, "minecraft:barrel", 12),
    ]
    b_brewery = ch.add(
        15,
        title="Apothecary Lab",
        subtitle="Construction · Holy brewery",
        description="Erect a specialized alchemical laboratory to distill holy tinctures, extracts, and draughts. Gather raw marble, aromatic cinnamon timber, and laboratory glass bottles. The Order supplies bulk marble, cinnamon logs, frosted glass, distillation pipes, seabrass sconces, redstone, copper, quartz, blaze rods, an Alchemist Cauldron, and storage barrels.",
        icon="irons_spellbooks:alchemist_cauldron",
        x=-2.5,
        y=0.5,
        shape="square",
        optional=True,
        tasks=[
            item_task(3, 79, "abyssal_decor:raw_marble", 32, "Inspect thirty-two Raw Marble"),
            item_task(3, 80, "abyssal_decor:cinnamon_log", 32, "Inspect thirty-two Cinnamon Logs"),
            item_task(3, 81, "minecraft:glass_bottle", 16, "Inspect sixteen Glass Bottles"),
        ],
        rewards=brewery_rewards,
        dependencies=[core3],
    )

    recon_centre_rewards = [
        item_reward(3, 83, "numismatics:sprocket"),
        *[item_reward(3, 400 + i, "minecraft:spruce_log", 64) for i in range(10)],
        *[item_reward(3, 430 + i, "minecraft:oak_log", 64) for i in range(5)],
        *[item_reward(3, 450 + i, "minecraft:cobblestone", 64) for i in range(12)],
        item_reward(3, 470, "minecraft:scaffolding", 64),
        item_reward(3, 471, "minecraft:scaffolding", 64),
        item_reward(3, 84, "minecraft:torch", 64),
        item_reward(3, 85, "minecraft:iron_ingot", 64),
        item_reward(3, 86, "minecraft:coal", 64),
        item_reward(3, 472, "minecraft:paper", 64),
        item_reward(3, 473, "minecraft:cartography_table"),
        item_reward(3, 474, "minecraft:campfire", 4),
    ]
    b_recon = ch.add(
        16,
        title="Survey Outpost",
        subtitle="Construction · Frontier watch",
        description="Establish an elevated reconnaissance hub and cartography outpost for surveying uncharted frontier routes. Gather stripped spruce logs, cobblestone, and coal. The Order outfits the station with bulk spruce logs, oak logs, cobblestone, scaffolding, torches, iron, coal, paper, and campfires.",
        icon="minecraft:cartography_table",
        x=2.5,
        y=0.5,
        shape="square",
        optional=True,
        tasks=[
            item_task(3, 83, "minecraft:stripped_spruce_log", 32, "Inspect thirty-two Stripped Spruce Logs"),
            item_task(3, 84, "minecraft:cobblestone", 32, "Inspect thirty-two Cobblestone"),
            item_task(3, 85, "minecraft:coal", 16, "Inspect sixteen Coal"),
        ],
        rewards=recon_centre_rewards,
        dependencies=[core3],
    )

    armory_tower_rewards = [
        item_reward(3, 87, "numismatics:sprocket"),
        *[item_reward(3, 500 + i, "minecraft:stone", 64) for i in range(18)],
        *[item_reward(3, 520 + i, "minecraft:andesite", 64) for i in range(6)],
        *[item_reward(3, 530 + i, "minecraft:oak_log", 64) for i in range(5)],
        item_reward(3, 570, "minecraft:scaffolding", 64),
        item_reward(3, 571, "minecraft:scaffolding", 64),
        item_reward(3, 88, "minecraft:lantern", 64),
        item_reward(3, 89, "minecraft:iron_ingot", 64),
        item_reward(3, 90, "minecraft:chain", 64),
        item_reward(3, 572, "minecraft:iron_block", 8),
        item_reward(3, 573, "minecraft:anvil"),
        item_reward(3, 574, "minecraft:smithing_table"),
    ]
    b_armory = ch.add(
        17,
        title="Garrison Armory",
        subtitle="Construction · Heavy bastion",
        description="Construct a heavy watchtower, armory, and perimeter bastion to secure the frontier against vampire incursions. Gather foundation cobblestone, a blast furnace for the forge, and a sentry shield. The Order furnishes the bastion with eighteen stacks of stone, six stacks of andesite, five stacks of oak logs, scaffolding, lanterns, iron ingots, chains, iron blocks, an anvil, and a smithing table.",
        icon="minecraft:chain",
        x=6.5,
        y=-1.0,
        shape="square",
        optional=True,
        tasks=[
            item_task(3, 87, "minecraft:cobblestone", 64, "Inspect sixty-four Cobblestone"),
            item_task(3, 88, "minecraft:blast_furnace", title="Inspect a Blast Furnace"),
            item_task(3, 89, "minecraft:shield", title="Carry a Shield"),
        ],
        rewards=armory_tower_rewards,
        dependencies=[core3],
    )

    mercy = ch.add(
        4,
        title="Mercy Manual",
        subtitle="Specialty · Holy support",
        description="Prepare an Inscription Table, a spellbook, and four Holy Runes, then demonstrate one Holy spell. The reward provides a practical triage set for healing, controlled force, and returning home.",
        icon="irons_spellbooks:holy_rune",
        x=-10.5,
        y=0,
        shape="diamond",
        optional=True,
        tasks=[
            item_task(3, 12, "irons_spellbooks:inscription_table", title="Inspect an Inscription Table"),
            item_task(3, 13, "irons_spellbooks:copper_spell_book", title="Carry a Flimsy Journal"),
            item_task(3, 14, "irons_spellbooks:holy_rune", 4, "Carry four Holy Runes"),
            check_task(3, 24, "I demonstrated one Holy spell"),
        ],
        rewards=hunter_spell_rewards(),
        dependencies=[b_wizard],
    )
    defense = ch.add(
        5,
        title="Pure Defense",
        subtitle="Specialty · Wards",
        description="Assemble a usable reserve of Pure Salt, Purified Garlic, and a garlic injection. These supplies buy time at a refuge door without asking the quest system to pretend it inspected a finished wall.",
        icon="vampirism:pure_salt",
        x=-7.5,
        y=2,
        shape="diamond",
        optional=True,
        tasks=[
            item_task(3, 34, "vampirism:pure_salt", 8, "Carry eight Pure Salt"),
            item_task(3, 35, "vampirism:purified_garlic", 16, "Carry sixteen Purified Garlic"),
            item_task(3, 36, "vampirism:injection_garlic", title="Carry a garlic injection"),
        ],
        rewards=[
            item_reward(3, 37, "numismatics:sprocket"),
            item_reward(3, 38, "vampirism:holy_water_bottle_normal", 16),
            item_reward(3, 39, "vampirism:pure_salt", 16),
        ],
        dependencies=[b_wizard],
    )
    consecrated = ch.add(
        6,
        title="Consecrated Work",
        subtitle="Specialty · Workstations",
        description="Stock an Alchemical Cauldron with normal Holy Water and Pure Salt. This turns a private kit into a maintainable remedy station and opens the Order's specialized alchemical preparation.",
        icon="vampirism:alchemical_cauldron",
        x=-4.5,
        y=3.5,
        shape="diamond",
        optional=True,
        tasks=[
            item_task(3, 15, "vampirism:alchemical_cauldron", title="Inspect an Alchemical Cauldron"),
            item_task(3, 16, "vampirism:holy_water_bottle_normal", 4, "Carry four normal Holy Waters"),
            item_task(3, 17, "vampirism:pure_salt", 8, "Carry eight Pure Salt"),
        ],
        rewards=[
            item_reward(3, 26, "numismatics:sprocket"),
            item_reward(3, 27, "vampirism:item_alchemical_fire", 16),
            item_reward(3, 28, "minecraft:iron_ingot", 32),
        ],
        dependencies=[b_brewery],
    )
    stores = ch.add(
        12,
        title="Refuge Stores",
        subtitle="Specialty · Medicine",
        description="Craft a Potion Table and glass bottles to begin field medicine. The Order supplies a Brewing Stand, an Alchemy Table, and a substantial reserve of brewing ingredients.",
        icon="vampirism:potion_table",
        x=-1.5,
        y=4.5,
        shape="diamond",
        optional=True,
        tasks=[
            item_task(3, 40, "vampirism:potion_table", title="Craft a Potion Table"),
            item_task(3, 41, "minecraft:glass_bottle", 16, "Craft sixteen Glass Bottles"),
        ],
        rewards=[
            item_reward(3, 40, "numismatics:sprocket"),
            item_reward(3, 41, "minecraft:brewing_stand"),
            item_reward(3, 42, "vampirism:alchemy_table"),
            item_reward(3, 43, "minecraft:nether_wart", 16),
            item_reward(3, 66, "minecraft:blaze_powder", 16),
            item_reward(3, 67, "minecraft:glistering_melon_slice", 16),
            item_reward(3, 68, "minecraft:golden_carrot", 16),
            item_reward(3, 69, "minecraft:fermented_spider_eye", 8),
        ],
        dependencies=[b_brewery],
    )
    ledger = ch.add(
        8,
        title="Field Ledger",
        subtitle="Specialty · Reconnaissance",
        description="Use an Explorer's Compass and Exposure camera, then trigger the Moment in Time advancement. Photographs turn rumor into evidence without entering protected claims.",
        icon="exposure:camera",
        x=1.5,
        y=4.5,
        shape="diamond",
        optional=True,
        tasks=[
            item_task(3, 19, "explorerscompass:explorerscompass", title="Carry an Explorer's Compass"),
            item_task(3, 20, "exposure:camera", title="Carry a Camera"),
            advancement_task(3, 21, "exposure:adventure/moment_in_time"),
        ],
        rewards=[
            item_reward(3, 51, "numismatics:sprocket"),
            item_reward(3, 52, "exposure:color_film", 8),
            item_reward(3, 53, "exposure:black_and_white_film", 8),
        ],
        dependencies=[b_recon],
    )
    transit = ch.add(
        13,
        title="Patrol Transit",
        subtitle="Specialty · Field logistics",
        description="Equip a patrol expedition with a backpack, clipboard, and spyglass for reconnaissance. The Order supplies a sprocket, leads, a Create toolbox, thirty-two rope arrows, hearty rabbit stew, Vampirism's strongest invisibility draught (80 minutes), and milk for emergency recovery.",
        icon="sophisticatedbackpacks:backpack",
        x=4.5,
        y=3.5,
        shape="diamond",
        optional=True,
        tasks=[
            item_task(3, 43, "sophisticatedbackpacks:backpack", title="Obtain a Backpack"),
            item_task(3, 44, "create:clipboard", title="Obtain a Clipboard"),
            item_task(3, 45, "minecraft:spyglass", title="Carry a Spyglass"),
        ],
        rewards=[
            item_reward(3, 44, "numismatics:sprocket"),
            item_reward(3, 45, "minecraft:lead", 8),
            item_reward(3, 46, "create:brown_toolbox", title="Brown Toolbox"),
            item_reward(3, 47, "supplementaries:rope_arrow", 32),
            item_reward(3, 94, "minecraft:rabbit_stew", 16),
            item_reward(3, 95, "minecraft:potion", components={"minecraft:potion_contents": {"potion": "vampirism:very_long_invisibility"}}, title="Potion of Invisibility (01:20:00)"),
            item_reward(3, 96, "minecraft:milk_bucket"),
        ],
        dependencies=[b_recon],
    )
    armament = ch.add(
        7,
        title="Hunter Armament",
        subtitle="Specialty · Ammunition",
        description="Set up archery targets, training mannequins, and test specialized quarrels. The Order equips the post with iron ingots, substantial reserves of spitfire and teleport quarrels, normal quarrels, bombs, and harming bamboo spikes.",
        icon="vampirism:crossbow_arrow_spitfire",
        x=7.5,
        y=2,
        shape="gear",
        optional=True,
        tasks=[
            item_task(3, 48, "vampirism:crossbow_arrow_spitfire", 3, "Carry three spitfire quarrels"),
            item_task(3, 49, "vampirism:crossbow_arrow_teleport", 4, "Carry four teleport quarrels"),
            item_task(3, 92, "minecraft:target", 2, "Inspect two Target Blocks"),
            item_task(3, 93, "mannequins:mannequin", 2, "Inspect two Mannequins"),
        ],
        rewards=[
            item_reward(3, 48, "numismatics:sprocket"),
            item_reward(3, 49, "vampirism:crossbow_arrow_spitfire", 32),
            item_reward(3, 50, "vampirism:crossbow_arrow_teleport", 32),
            item_reward(3, 54, "vampirism:crossbow_arrow_normal", 64),
            item_reward(3, 55, "minecraft:iron_ingot", 32),
            item_reward(3, 92, "supplementaries:bomb", 16),
            item_reward(3, 93, "supplementaries:bamboo_spikes_tipped", 16, components={"minecraft:potion_contents": {"potion": "minecraft:harming"}}),
        ],
        dependencies=[b_armory],
    )
    mastery = ch.add(
        9,
        title="Siege Artillery",
        subtitle="Specialty · Big cannons",
        description="Construct heavy siege artillery with Create Big Cannons. Assemble a Cannon Carriage, two Wrought Iron Cannon Chambers, and a Wrought Iron Cannon End. The Order supplies a Ramrod, Worm, Create Wrench, sixty-four Powder Charges, and a stockpile of Mortar Stones.",
        icon="createbigcannons:cannon_carriage",
        x=10.5,
        y=0,
        shape="hexagon",
        size=1.3,
        optional=True,
        tasks=[
            item_task(3, 10, "createbigcannons:cannon_carriage", title="Obtain a Cannon Carriage"),
            item_task(3, 11, "createbigcannons:wrought_iron_cannon_chamber", 2, "Obtain two Wrought Iron Cannon Chambers"),
            item_task(3, 91, "createbigcannons:wrought_iron_cannon_end", title="Obtain a Wrought Iron Cannon End"),
        ],
        rewards=[
            item_reward(3, 16, "createbigcannons:ram_rod"),
            item_reward(3, 17, "createbigcannons:worm"),
            item_reward(3, 18, "create:wrench"),
            item_reward(3, 19, "createbigcannons:powder_charge", 64),
            item_reward(3, 91, "createbigcannons:mortar_stone", 64),
        ],
        dependencies=[b_armory],
    )

    return ch


def vampire_spell_rewards() -> list[dict[str, Any]]:
    return [
        item_reward(4, 20, "numismatics:sprocket"),
        item_reward(4, 21, "irons_spellbooks:uncommon_ink", 16),
        item_reward(4, 22, "irons_spellbooks:rare_ink", 8),
        scroll_reward(4, 23, "irons_spellbooks:blood_slash", "Scroll of Blood Slash"),
        scroll_reward(4, 24, "irons_spellbooks:blood_step", "Scroll of Blood Step"),
        scroll_reward(4, 25, "irons_spellbooks:ray_of_siphoning", "Scroll of Siphoning"),
    ]


def build_vampires(group: str) -> Chapter:
    ch = Chapter(
        4,
        "ch04_house_night",
        "04 · House of Night",
        group,
        "vampirism:vampire_fang",
        2,
        images=[
            {"alpha": 22, "height": 7, "image": "poiesis:textures/questpics/vvh/house_of_night_blood_panorama.png", "order": -40, "rotation": 0.0, "width": 5, "x": 11, "y": 2},
            {"alpha": 20, "height": 7, "image": "poiesis:textures/questpics/vvh/blood_ritual_workstation.png", "order": -39, "rotation": 0.0, "width": 5, "x": -11, "y": 5},
            {"alpha": 28, "height": 2.5, "image": "poiesis:textures/questpics/vvh/blood_school_crest.png", "order": -38, "rotation": 0.0, "width": 2.5, "x": 0, "y": 10},
        ],
    )
    core1 = ch.add(
        1,
        title="First Thirst",
        subtitle="Tier I · Foundation",
        description="Prepare an Altar of Inspiration, Blood Container, and four Blood Bottles. Visible reserves turn hunger from an emergency into a system another House member can maintain.",
        icon="vampirism:altar_inspiration",
        x=0,
        y=-10,
        shape="hexagon",
        size=1.4,
        tasks=[
            item_task(4, 1, "vampirism:altar_inspiration", title="Inspect an Altar of Inspiration"),
            item_task(4, 2, "vampirism:blood_container", title="Inspect a Blood Container"),
            item_task(4, 3, "vampirism:blood_bottle", 4, "Carry four Blood Bottles"),
        ],
        rewards=[
            item_reward(4, 1, "numismatics:bevel"),
            item_reward(4, 2, "irons_spellbooks:wizard_helmet", components={"minecraft:dyed_color": {"rgb": 1908001}}),
            item_reward(4, 3, "irons_spellbooks:wizard_chestplate", components={"minecraft:dyed_color": {"rgb": 1908001}}),
            item_reward(4, 4, "irons_spellbooks:wizard_leggings", components={"minecraft:dyed_color": {"rgb": 1908001}}),
            item_reward(4, 5, "irons_spellbooks:wizard_boots", components={"minecraft:dyed_color": {"rgb": 1908001}}),
        ],
        dependencies=[qid(2, 2)],
    )
    core2 = ch.add(
        2,
        title="Red Measure",
        subtitle="Tier II · Workstations",
        description="Add an Altar of Infusion, four Blood Pedestals, and two Blood-Infused Iron. The ritual becomes an inspectable workstation rather than a secret held by whoever logged in first.",
        icon="vampirism:altar_infusion",
        x=0,
        y=-7,
        shape="gear",
        size=1.3,
        tasks=[
            item_task(4, 4, "vampirism:altar_infusion", title="Inspect an Altar of Infusion"),
            item_task(4, 5, "vampirism:blood_pedestal", 4, "Inspect four Blood Pedestals"),
            item_task(4, 6, "vampirism:blood_infused_iron_ingot", 2, "Carry two Blood-Infused Iron"),
        ],
        rewards=[
            item_reward(4, 6, "numismatics:sprocket"),
            item_reward(4, 7, "minecraft:glass_bottle", 32),
            item_reward(4, 8, "minecraft:iron_ingot", 32),
            item_reward(4, 9, "minecraft:lead", 8),
            item_reward(4, 10, "minecraft:redstone", 32),
        ],
        dependencies=[core1],
    )
    core3 = ch.add(
        3,
        title="Inherited Edge",
        subtitle="Tier III · Logistics",
        description="Prepare a Blood Sieve, normal Heartseeker, and four Blood-Infused Iron. The House can now repair controlled armament and support specialized bloodwork without receiving a free late-tier blade.",
        icon="vampirism:heart_seeker_normal",
        x=0,
        y=-4,
        shape="gear",
        size=1.3,
        tasks=[
            item_task(4, 7, "vampirism:blood_sieve", title="Inspect a Blood Sieve"),
            item_task(4, 8, "vampirism:heart_seeker_normal", title="Carry a normal Heartseeker"),
            item_task(4, 9, "vampirism:blood_infused_iron_ingot", 4, "Carry four Blood-Infused Iron"),
        ],
        rewards=[
            item_reward(4, 11, "numismatics:sprocket", 2),
            item_reward(4, 12, "minecraft:iron_block", 2),
            item_reward(4, 13, "minecraft:redstone", 32),
            item_reward(4, 14, "minecraft:gold_ingot", 16),
            item_reward(4, 15, "minecraft:coal", 32),
        ],
        dependencies=[core2],
    )

    b_spire = ch.add(
        14,
        title="Dark Spire Materials",
        subtitle="Construction · Nocturnal spire",
        description="Gather obsidian, lightning rods, cut copper, and tinted glass to construct a dark transmission spire and advanced workshop overlooking the island.",
        icon="minecraft:lightning_rod",
        x=-6.5,
        y=-1.0,
        shape="square",
        optional=True,
        tasks=[
            item_task(4, 75, "minecraft:obsidian", 64, "Inspect sixty-four Obsidian"),
            item_task(4, 76, "minecraft:lightning_rod", 16, "Inspect sixteen Lightning Rods"),
            item_task(4, 77, "minecraft:cut_copper", 4, "Inspect four Cut Copper"),
            item_task(4, 78, "minecraft:tinted_glass", 16, "Inspect sixteen Tinted Glass"),
        ],
        rewards=[
            item_reward(4, 75, "numismatics:sprocket"),
            item_reward(4, 76, "minecraft:obsidian", 64),
            item_reward(4, 77, "minecraft:tinted_glass", 32),
            item_reward(4, 78, "minecraft:redstone_torch", 16),
        ],
        dependencies=[core3],
    )
    b_foundry = ch.add(
        15,
        title="Blood Foundry Materials",
        subtitle="Construction · Metallurgy lab",
        description="Gather nether bricks, quartz, cauldrons, and chains to construct a blood foundry and transit waystation for nocturnal couriers.",
        icon="minecraft:nether_bricks",
        x=-2.5,
        y=0.5,
        shape="square",
        optional=True,
        tasks=[
            item_task(4, 79, "minecraft:nether_bricks", 64, "Inspect sixty-four Nether Bricks"),
            item_task(4, 80, "minecraft:quartz", 16, "Inspect sixteen Nether Quartz"),
            item_task(4, 81, "minecraft:cauldron", 2, "Inspect two Cauldrons"),
            item_task(4, 82, "minecraft:chain", 16, "Inspect sixteen Chains"),
        ],
        rewards=[
            item_reward(4, 79, "numismatics:sprocket"),
            item_reward(4, 80, "minecraft:nether_bricks", 64),
            item_reward(4, 81, "minecraft:chain", 16),
            item_reward(4, 82, "minecraft:crimson_planks", 32),
        ],
        dependencies=[core3],
    )
    b_manor = ch.add(
        16,
        title="Guest Hall Materials",
        subtitle="Construction · Manor estate",
        description="Gather polished blackstone, crimson stems, barrels, and soul lanterns to construct an imposing manor hall and hospitality vault.",
        icon="minecraft:polished_blackstone",
        x=2.5,
        y=0.5,
        shape="square",
        optional=True,
        tasks=[
            item_task(4, 83, "minecraft:polished_blackstone", 64, "Inspect sixty-four Polished Blackstone"),
            item_task(4, 84, "minecraft:crimson_stem", 32, "Inspect thirty-two Crimson Stems"),
            item_task(4, 85, "minecraft:barrel", 4, "Inspect four Barrels"),
            item_task(4, 86, "minecraft:soul_lantern", 4, "Inspect four Soul Lanterns"),
        ],
        rewards=[
            item_reward(4, 83, "numismatics:sprocket"),
            item_reward(4, 84, "minecraft:polished_blackstone", 64),
            item_reward(4, 85, "minecraft:crimson_planks", 32),
            item_reward(4, 86, "minecraft:soul_lantern", 8),
        ],
        dependencies=[core3],
    )
    b_vault = ch.add(
        17,
        title="Blood Vault Materials",
        subtitle="Construction · Sanguine arcanum",
        description="Gather crying obsidian, amethyst shards, bookshelves, and glass to construct an arcane blood vault and sanguine library.",
        icon="minecraft:crying_obsidian",
        x=6.5,
        y=-1.0,
        shape="square",
        optional=True,
        tasks=[
            item_task(4, 87, "minecraft:crying_obsidian", 64, "Inspect sixty-four Crying Obsidian"),
            item_task(4, 88, "minecraft:amethyst_shard", 16, "Inspect sixteen Amethyst Shards"),
            item_task(4, 89, "minecraft:bookshelf", 4, "Inspect four Bookshelves"),
            item_task(4, 90, "minecraft:glass", 16, "Inspect sixteen Glass"),
        ],
        rewards=[
            item_reward(4, 87, "numismatics:sprocket"),
            item_reward(4, 88, "minecraft:crying_obsidian", 64),
            item_reward(4, 89, "minecraft:glass", 32),
            item_reward(4, 90, "minecraft:redstone", 16),
        ],
        dependencies=[core3],
    )

    mastery = ch.add(
        9,
        title="Night's Due",
        subtitle="Specialty · Advanced bloodwork",
        description="Carry an enhanced Heartseeker and two Enhanced Blood-Infused Iron. This optional late mastery pays at Cog scale while leaving the weapon and its alloy earned through actual Vampirism progression.",
        icon="vampirism:heart_seeker_enhanced",
        x=-10.5,
        y=0,
        shape="hexagon",
        size=1.3,
        optional=True,
        tasks=[
            item_task(4, 10, "vampirism:heart_seeker_enhanced", title="Carry an enhanced Heartseeker"),
            item_task(4, 11, "vampirism:blood_infused_enhanced_iron_ingot", 2, "Carry two Enhanced Blood-Infused Iron"),
        ],
        rewards=[
            item_reward(4, 16, "numismatics:cog"),
            item_reward(4, 17, "irons_spellbooks:blood_upgrade_orb"),
            item_reward(4, 18, "minecraft:obsidian", 16),
            item_reward(4, 19, "minecraft:diamond", 8),
        ],
        dependencies=[b_spire],
    )
    courier = ch.add(
        8,
        title="Nocturnal Broadcast",
        subtitle="Specialty · Vista broadcast",
        description="Craft a Television and Viewfinder to establish visual broadcast capabilities across the island. The House supplies currency and a set of hollow cassettes to record feeds.",
        icon="vista:television",
        x=-7.5,
        y=2,
        shape="diamond",
        optional=True,
        tasks=[
            item_task(4, 19, "vista:television", title="Craft a Television"),
            item_task(4, 20, "vista:viewfinder", title="Craft a Viewfinder"),
        ],
        rewards=[
            item_reward(4, 53, "numismatics:sprocket"),
            item_reward(4, 54, "vista:hollow_cassette", 4),
        ],
        dependencies=[b_spire],
    )
    metallurgy = ch.add(
        7,
        title="Sieve Extraction",
        subtitle="Specialty · Blood metallurgy",
        description="Use a Blood Sieve and four Blood-Infused Iron as proof of a working material lane. The reward restocks ordinary inputs without handing out the enhanced alloy required by later mastery.",
        icon="vampirism:blood_sieve",
        x=-4.5,
        y=3.5,
        shape="gear",
        optional=True,
        tasks=[
            item_task(4, 49, "vampirism:blood_sieve", title="Inspect a Blood Sieve"),
            item_task(4, 50, "vampirism:blood_infused_iron_ingot", 4, "Carry four Blood-Infused Iron"),
        ],
        rewards=[
            item_reward(4, 49, "numismatics:sprocket"),
            item_reward(4, 50, "minecraft:redstone", 32),
            item_reward(4, 51, "minecraft:gold_ingot", 16),
            item_reward(4, 52, "minecraft:iron_ingot", 16),
        ],
        dependencies=[b_foundry],
    )
    transit = ch.add(
        13,
        title="Sunproof Transit",
        subtitle="Specialty · Night mobility",
        description="Carry an umbrella, saddle, and clock as a coherent night-route kit. The reward adds leads and rockets for transport and signals while leaving advanced movement to ordinary progression.",
        icon="vampirism:umbrella",
        x=-1.5,
        y=4.5,
        shape="diamond",
        optional=True,
        tasks=[
            item_task(4, 43, "vampirism:umbrella", title="Carry an Umbrella"),
            item_task(4, 44, "minecraft:saddle", title="Carry a Saddle"),
            item_task(4, 45, "minecraft:clock", title="Carry a Clock"),
        ],
        rewards=[
            item_reward(4, 45, "numismatics:sprocket"),
            item_reward(4, 46, "minecraft:lead", 8),
            item_reward(4, 47, "minecraft:firework_rocket", 32),
            item_reward(4, 48, "minecraft:map", 8),
        ],
        dependencies=[b_foundry],
    )
    stores = ch.add(
        12,
        title="Guest Stores",
        subtitle="Specialty · Hospitality",
        description="Prepare a brewing stand, honey, and ordinary food for visitors who do not share the House's diet. The reserve makes hospitality functional when a route ends after dark.",
        icon="minecraft:brewing_stand",
        x=1.5,
        y=4.5,
        shape="diamond",
        optional=True,
        tasks=[
            item_task(4, 40, "minecraft:brewing_stand", title="Inspect a Brewing Stand"),
            item_task(4, 41, "minecraft:honey_bottle", 8, "Carry eight Honey Bottles"),
            item_task(4, 42, "minecraft:cooked_beef", 32, "Carry thirty-two Cooked Beef"),
        ],
        rewards=[
            item_reward(4, 41, "numismatics:sprocket"),
            item_reward(4, 42, "minecraft:glass_bottle", 32),
            item_reward(4, 43, "minecraft:golden_apple", 4),
            item_reward(4, 44, "minecraft:bread", 32),
        ],
        dependencies=[b_manor],
    )
    palette = ch.add(
        6,
        title="House of Doors",
        subtitle="Specialty · Manor palette",
        description="Gather dark stone brick, dark oak, fences, and lanterns. The expanded palette is enough for a crypt, guest hall, garden court, or night clinic chosen by its builders.",
        icon="vampirism:dark_stone_bricks",
        x=4.5,
        y=3.5,
        shape="square",
        optional=True,
        tasks=[
            item_task(4, 15, "vampirism:dark_stone_bricks", 64, "Inspect sixty-four Dark Stone Bricks"),
            item_task(4, 16, "minecraft:dark_oak_log", 32, "Inspect thirty-two Dark Oak Logs"),
            item_task(4, 17, "minecraft:dark_oak_fence", 16, "Inspect sixteen Dark Oak Fences"),
            item_task(4, 18, "minecraft:lantern", 8, "Inspect eight Lanterns"),
        ],
        rewards=[
            item_reward(4, 26, "numismatics:sprocket"),
            item_reward(4, 27, "vampirism:dark_stone_bricks", 192),
            item_reward(4, 28, "minecraft:dark_oak_log", 96),
            item_reward(4, 29, "minecraft:dark_oak_fence", 48),
            item_reward(4, 30, "minecraft:lantern", 24),
            item_reward(4, 31, "minecraft:iron_ingot", 32),
            item_reward(4, 32, "minecraft:diamond", 4),
            item_reward(4, 33, "minecraft:stonecutter"),
        ],
        dependencies=[b_manor],
    )
    reserve = ch.add(
        5,
        title="Crimson Reserve",
        subtitle="Specialty · Blood supply",
        description="Maintain Blood Bottles and a Blood Container as a visible emergency reserve. The reward adds glassware and animal-handling supplies without pretending inventory proves a finished farm.",
        icon="vampirism:blood_container",
        x=7.5,
        y=2,
        shape="diamond",
        optional=True,
        tasks=[
            item_task(4, 34, "vampirism:blood_bottle", 4, "Carry four Blood Bottles"),
            item_task(4, 35, "vampirism:blood_container", title="Inspect a Blood Container"),
        ],
        rewards=[
            item_reward(4, 37, "numismatics:sprocket"),
            item_reward(4, 38, "minecraft:glass_bottle", 32),
            item_reward(4, 39, "minecraft:lead", 8),
            item_reward(4, 40, "minecraft:oak_fence", 32),
        ],
        dependencies=[b_vault],
    )
    script = ch.add(
        4,
        title="Scarlet Script",
        subtitle="Specialty · Blood utility",
        description="Prepare an Inscription Table, spellbook, and four Blood Runes, then demonstrate one Blood spell. The reward favors movement, measured siphoning, and practical combat rather than a random high-tier scroll.",
        icon="irons_spellbooks:blood_rune",
        x=10.5,
        y=0,
        shape="diamond",
        optional=True,
        tasks=[
            item_task(4, 12, "irons_spellbooks:inscription_table", title="Inspect an Inscription Table"),
            item_task(4, 13, "irons_spellbooks:copper_spell_book", title="Carry a Flimsy Journal"),
            item_task(4, 14, "irons_spellbooks:blood_rune", 4, "Carry four Blood Runes"),
            check_task(4, 24, "I demonstrated one Blood spell"),
        ],
        rewards=vampire_spell_rewards(),
        dependencies=[b_vault],
    )

    return ch


def build_market(group: str) -> Chapter:
    ch = Chapter(
        5,
        "ch05_market_services",
        "05 · Market Services",
        group,
        "numismatics:sprocket",
        0,
        images=[{
            "alpha": 18,
            "height": 6,
            "image": "poiesis:textures/questpics/vvh/free_company_writ.png",
            "order": -40,
            "rotation": 0.0,
            "width": 7,
            "x": 0,
            "y": 1,
        }],
    )
    opener = ch.add(
        1,
        title="Read the Board",
        subtitle="Weekly services · Team-scoped",
        description="The board converts finite quest currency into visible utility. Every purchase consumes the exact posted price, repeats no faster than once per team each week, and grants no currency back.",
        icon="numismatics:banking_guide",
        x=0,
        y=-5,
        shape="hexagon",
        size=1.4,
        tasks=[check_task(5, 1, "I understand prices, cooldowns, and team scope")],
        dependencies=[qid(2, 7)],
    )

    def sink(index: int, *, title: str, subtitle: str, description: str, icon: str, x: float, y: float, price_item: str, price_count: int, task_idx: int, rewards: list[dict[str, Any]]) -> str:
        coin_name = {"numismatics:bevel": "Bevel", "numismatics:sprocket": "Sprocket", "numismatics:cog": "Cog"}[price_item]
        label = f"Submit {price_count} {coin_name}{'' if price_count == 1 else 's'}"
        return ch.add(
            index,
            title=title,
            subtitle=subtitle,
            description=description,
            icon=icon,
            x=x,
            y=y,
            shape="gear" if index != 7 else "hexagon",
            size=1.0 if index != 7 else 1.3,
            optional=True,
            can_repeat=True,
            cooldown=WEEK,
            tasks=[item_task(5, task_idx, price_item, price_count, label, consume=True)],
            rewards=rewards,
            dependencies=[opener],
        )

    sink(
        2,
        title="Field Kit",
        subtitle="1 Bevel · Weekly",
        description="Replace the ordinary supplies most likely to strand a late arrival: food, light, and leads. This is convenience, not a progression skip.",
        icon="numismatics:bevel",
        x=-6,
        y=-1,
        price_item="numismatics:bevel",
        price_count=1,
        task_idx=2,
        rewards=[
            item_reward(5, 1, "minecraft:cooked_beef", 32, team=True),
            item_reward(5, 2, "minecraft:torch", 64, team=True),
            item_reward(5, 3, "minecraft:lead", 8, team=True),
        ],
    )
    sink(
        3,
        title="Works Kit",
        subtitle="1 Sprocket · Weekly",
        description="Buy enough structural stock for a visible repair, roadside shelter, or public-room extension rather than a decorative handful.",
        icon="numismatics:sprocket",
        x=-2,
        y=-1,
        price_item="numismatics:sprocket",
        price_count=1,
        task_idx=3,
        rewards=[
            item_reward(5, 4, "minecraft:stone_bricks", 128, team=True),
            item_reward(5, 5, "minecraft:oak_log", 64, team=True),
            item_reward(5, 6, "minecraft:iron_ingot", 32, team=True),
            item_reward(5, 7, "minecraft:lantern", 16, team=True),
        ],
    )
    sink(
        4,
        title="Arcane Kit",
        subtitle="1 Sprocket · Weekly",
        description="Restock a teaching table with multi-school inscription materials. The final spell remains the player's decision; the board does not gamble on random scrolls.",
        icon="irons_spellbooks:uncommon_ink",
        x=2,
        y=-1,
        price_item="numismatics:sprocket",
        price_count=1,
        task_idx=4,
        rewards=[
            item_reward(5, 8, "irons_spellbooks:arcane_essence", 16, team=True),
            item_reward(5, 9, "irons_spellbooks:blank_rune", 4, team=True),
            item_reward(5, 10, "irons_spellbooks:common_ink", 16, team=True),
            item_reward(5, 11, "irons_spellbooks:uncommon_ink", 8, team=True),
        ],
    )
    sink(
        5,
        title="Foundry Kit",
        subtitle="2 Sprockets · Weekly",
        description="Restock a public Create line with alloy, brass, mechanisms, and belts. The bundle saves maintenance time without replacing ore generation or advanced machines.",
        icon="create:precision_mechanism",
        x=6,
        y=-1,
        price_item="numismatics:sprocket",
        price_count=2,
        task_idx=5,
        rewards=[
            item_reward(5, 12, "create:andesite_alloy", 48, team=True),
            item_reward(5, 13, "create:brass_ingot", 24, team=True),
            item_reward(5, 14, "create:precision_mechanism", 4, team=True),
            item_reward(5, 15, "create:belt_connector", 8, team=True),
        ],
    )
    sink(
        9,
        title="Recovery Crate",
        subtitle="1 Sprocket · Weekly",
        description="Buy a complete recovery cache for a difficult expedition: beds, shields, honey, and golden apples. It restores readiness without issuing permanent combat power.",
        icon="minecraft:golden_apple",
        x=-6,
        y=2.5,
        price_item="numismatics:sprocket",
        price_count=1,
        task_idx=9,
        rewards=[
            item_reward(5, 20, "minecraft:white_bed", 2, team=True),
            item_reward(5, 21, "minecraft:shield", 2, team=True),
            item_reward(5, 22, "minecraft:honey_bottle", 16, team=True),
            item_reward(5, 23, "minecraft:golden_apple", 4, team=True),
        ],
    )
    sink(
        10,
        title="Transit Crate",
        subtitle="2 Sprockets · Weekly",
        description="Equip a team route with saddles, leads, rockets, boats, and compasses. The crate helps move people and stock but grants no mount, elytra, or teleport tier.",
        icon="minecraft:saddle",
        x=-2,
        y=2.5,
        price_item="numismatics:sprocket",
        price_count=2,
        task_idx=10,
        rewards=[
            item_reward(5, 24, "minecraft:saddle", 4, team=True),
            item_reward(5, 25, "minecraft:lead", 16, team=True),
            item_reward(5, 26, "minecraft:firework_rocket", 64, team=True),
            item_reward(5, 27, "minecraft:oak_boat", 4, team=True),
            item_reward(5, 28, "minecraft:compass", 4, team=True),
        ],
    )
    sink(
        7,
        title="Concord Bond",
        subtitle="1 Cog · Weekly",
        description="Redeem a major team bond for structural and fabrication stock behind one common project. The bundle is broad, finite, and does not reproduce its Cog input.",
        icon="numismatics:cog",
        x=2,
        y=2.5,
        price_item="numismatics:cog",
        price_count=1,
        task_idx=6,
        rewards=[
            item_reward(5, 16, "minecraft:stone_bricks", 256, team=True),
            item_reward(5, 17, "minecraft:oak_log", 128, team=True),
            item_reward(5, 18, "minecraft:iron_ingot", 64, team=True),
            item_reward(5, 19, "minecraft:diamond", 8, team=True),
            item_reward(5, 29, "create:andesite_alloy", 64, team=True),
        ],
    )
    ch.add(
        6,
        title="Rumour Ledger",
        subtitle="Fallback · 1 team Bevel weekly",
        description="File one written maintenance report naming a findable place, a real problem, and the person who will review the result. The book is consumed as the archive copy; this is the board's sole slow currency faucet.",
        icon="minecraft:written_book",
        x=6,
        y=2.5,
        shape="diamond",
        optional=True,
        can_repeat=True,
        cooldown=WEEK,
        tasks=[
            item_task(5, 7, "minecraft:written_book", title="Submit one written field ledger", consume=True),
            check_task(5, 11, "I named the place, problem, and reviewer"),
        ],
        rewards=[item_reward(5, 30, "numismatics:bevel", team=True)],
        dependencies=[opener],
    )
    ch.add(
        8,
        title="Know the Coins",
        subtitle="Spur · Bevel · Sprocket · Cog",
        description="Numismatics base values are Spur 1, Bevel 8, Sprocket 16, and Cog 64. Routine work pays Bevels, specialties pay Sprockets, and major team milestones pay Cogs; Crowns and Suns remain outside this campaign.",
        icon="numismatics:cog",
        x=0,
        y=6,
        shape="diamond",
        optional=True,
        tasks=[check_task(5, 8, "I understand the coin denominations")],
        dependencies=[opener],
    )
    return ch


def build_campaign() -> tuple[list[Chapter], list[dict[str, str]]]:
    charter_group = hid(G_PREFIX, 1, 0)
    faction_group = hid(G_PREFIX, 2, 0)
    market_group = hid(G_PREFIX, 3, 0)
    groups = [
        {"id": charter_group, "title": "The Charter"},
        {"id": faction_group, "title": "Callings and Factions"},
        {"id": market_group, "title": "Markets and Services"},
    ]
    chapters = [
        build_charter(charter_group),
        build_callings(faction_group),
        build_hunters(faction_group),
        build_vampires(faction_group),
        build_market(market_group),
    ]
    return chapters, groups


def render_chapter(chapter: Chapter) -> str:
    root: dict[str, Any] = {
        "default_hide_dependency_lines": False,
        "default_quest_shape": "",
        "filename": chapter.filename,
        "group": chapter.group,
        "icon": {"id": chapter.icon},
        "id": chapter.id,
    }
    if chapter.images:
        root["images"] = chapter.images
    root.update({"order_index": chapter.order, "quest_links": [], "quests": chapter.quests, "title": chapter.title})
    return snbt(root) + "\n"


def render_groups(groups: list[dict[str, str]]) -> str:
    return snbt({"chapter_groups": groups}) + "\n"


def render_data() -> str:
    return snbt({
        "default_hide_dependency_lines": False,
        "default_quest_shape": "circle",
        "default_reward_team": False,
        "disable_gui": False,
        "drop_loot_crates": False,
        "emergency_items_cooldown": 300,
        "grid_scale": 0.5,
        "icon": {"id": "minecraft:compass"},
        "lock_message": "Complete the Island Charter first.",
        "progression_mode": "default",
        "title": "VvH · The Concord",
        "version": 14,
    }) + "\n"


def normalized_manifest(chapters: list[Chapter], groups: list[dict[str, str]]) -> dict[str, Any]:
    normalized: list[dict[str, Any]] = []
    for chapter in chapters:
        qs: list[dict[str, Any]] = []
        for quest in chapter.quests:
            qs.append({
                "dependencies": quest.get("dependencies", []),
                "description": quest.get("description", []),
                "hide_dependency_lines": quest.get("hide_dependency_lines", False),
                "icon": quest["icon"]["id"],
                "id": quest["id"],
                "min_required_dependencies": quest.get("min_required_dependencies", 0),
                "optional": quest.get("optional", False),
                "repeat_cooldown": quest.get("repeat_cooldown", 0),
                "repeatable": quest.get("can_repeat", False),
                "rewards": quest.get("rewards", []),
                "shape": quest.get("shape", ""),
                "size": quest.get("size", 1.0),
                "subtitle": quest.get("subtitle", ""),
                "tasks": quest.get("tasks", []),
                "title": quest["title"],
                "x": quest["x"],
                "y": quest["y"],
            })
        normalized.append({
            "filename": chapter.filename,
            "group": chapter.group,
            "icon": chapter.icon,
            "id": chapter.id,
            "images": chapter.images,
            "order": chapter.order,
            "quests": qs,
            "title": chapter.title,
        })
    return {
        "architecture": "five-chapter-vvh-current",
        "authoritative_source": "scripts/vvh_campaign_v3.py",
        "chapter_count": len(chapters),
        "quest_count": sum(len(ch.quests) for ch in chapters),
        "groups": groups,
        "chapters": normalized,
    }


def outputs(root: Path) -> dict[Path, str]:
    chapters, groups = build_campaign()
    base = root / "config/ftbquests/quests"
    result: dict[Path, str] = {
        base / "chapter_groups.snbt": render_groups(groups),
        base / "data.snbt": render_data(),
        base / "lang/en_us.snbt": "{\n}\n",
        root / "docs/vvh/campaign_manifest.json": json.dumps(normalized_manifest(chapters, groups), indent=2, ensure_ascii=False) + "\n",
    }
    for chapter in chapters:
        result[base / "chapters" / f"{chapter.filename}.snbt"] = render_chapter(chapter)
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate the authoritative five-chapter VvH campaign")
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--check", action="store_true", help="Report drift without writing")
    parser.add_argument("--prune-retired", action="store_true", help="Delete only explicitly named retired chapter files")
    args = parser.parse_args()
    root = args.root.resolve()
    expected = outputs(root)
    chapters_dir = root / "config/ftbquests/quests/chapters"
    expected_chapter_paths = {path for path in expected if path.parent == chapters_dir}
    stale: list[str] = []
    for path, content in expected.items():
        current = path.read_text(encoding="utf-8-sig") if path.exists() else None
        if current != content:
            stale.append(str(path.relative_to(root)))
            if not args.check:
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text(content, encoding="utf-8")

    unexpected = sorted(path for path in chapters_dir.glob("*.snbt") if path not in expected_chapter_paths)
    for path in unexpected:
        rel = str(path.relative_to(root))
        stale.append(rel + " (unexpected chapter preserved)")
        if args.prune_retired and path.name in RETIRED_CHAPTER_FILES and not args.check:
            path.unlink()
            stale[-1] = rel + " (retired chapter removed)"

    if args.check:
        if stale:
            print("campaign source drift:\n- " + "\n- ".join(stale))
            return 1
        print("campaign source is synchronized: 5 chapters, 50 quests")
        return 0

    action = "updated" if stale else "verified"
    print(f"{action} {len(expected)} authoritative files; unknown chapter files were not deleted")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
