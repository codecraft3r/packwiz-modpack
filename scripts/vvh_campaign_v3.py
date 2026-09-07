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
L_PREFIX = 0x7A11C5DF00000000
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


def lid(chapter: int, index: int) -> str:
    return hid(L_PREFIX, chapter, index)


def lid_int(chapter: int, index: int) -> int:
    return int(lid(chapter, index), 16)


def esc(value: str) -> str:
    return '"' + value.replace("\\", "\\\\").replace('"', '\\"').replace("\n", "\\n") + '"'


def snbt(value: Any, indent: int = 0) -> str:
    pad = "\t" * indent
    if isinstance(value, bool):
        return "true" if value else "false"
    if isinstance(value, int):
        return f"{value}L" if value > 2147483647 or value < -2147483648 else str(value)
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


def choice_reward(chapter_index: int, local_id: int, table_id: int, title: str | None = None) -> dict[str, Any]:
    reward: dict[str, Any] = {
        "id": rid(chapter_index, local_id),
        "table_id": table_id,
        "type": "choice",
    }
    if title:
        reward["title"] = title
    return reward


@dataclass
class RewardTable:
    id: int
    filename: str
    title: str
    rewards: list[dict[str, Any]]


def build_reward_tables() -> list[RewardTable]:
    return [
        RewardTable(
            id=lid_int(3, 1),
            filename="holy_focus_choice",
            title="Holy Focus Choice",
            rewards=[
                {"id": lid(3, 2), "item": {"count": 1, "id": "irons_spellbooks:artificer_cane"}},
                {"id": lid(3, 3), "item": {"count": 1, "id": "irons_spellbooks:graybeard_staff"}},
            ],
        )
    ]


def render_reward_table(table: RewardTable) -> str:
    data = {
        "id": f"{table.id:016X}",
        "order_index": 0,
        "rewards": table.rewards,
        "title": table.title,
    }
    return snbt(data) + "\n"

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
    # Chapter-level FTB default for hiding dependency lines. Only the Market
    # sets this; every other chapter keeps visible progression lines.
    default_hide_dependency_lines: bool = False

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
        item_reward(3, 20, "numismatics:sprocket", 2),
        item_reward(3, 21, "irons_spellbooks:rare_ink", 8),
        item_reward(3, 22, "irons_spellbooks:epic_ink", 4),
        item_reward(3, 97, "irons_spellbooks:holy_rune", 4),
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
    # Reconciled 2026-09-07 with live origin/dev: human streamlining (f3ecc4b)
    # trimmed bulk rewards to a starter kit and titled the sprocket as the
    # Order Construction Grant redeemable at the Market. IDs preserved.
    building_supplies_rewards = [
        item_reward(3, 6, "numismatics:sprocket", title="Order Construction Grant"),
        item_reward(3, 100, "minecraft:stone", 64),
        item_reward(3, 101, "minecraft:stone", 64),
        item_reward(3, 130, "minecraft:oak_log", 64),
        item_reward(3, 150, "minecraft:spruce_log", 64),
        item_reward(3, 10, "minecraft:iron_ingot", 16),
        item_reward(3, 70, "minecraft:copper_ingot", 16),
        item_reward(3, 72, "minecraft:stonecutter"),
        item_reward(3, 73, "supplementaries:wrench"),
    ]
    core2 = ch.add(
        2,
        title="Building Supplies",
        subtitle="Tier II · Construction stock",
        description="Gather an essential construction stock of stone bricks, logs, iron bars, and lanterns. Completing this foundation rewards a manageable starter building kit with two stacks of stone, a stack each of oak and spruce logs, iron, copper, a stonecutter, a wrench, and a sprocket construction grant to redeem at the Market.",
        icon="minecraft:stone",
        x=0,
        y=-7,
        shape="gear",
        size=1.3,
        tasks=[
            item_task(3, 4, "minecraft:stone_bricks", 32, "Inspect thirty-two Stone Bricks"),
            item_task(3, 5, "minecraft:oak_log", 16, "Inspect sixteen Oak Logs"),
            item_task(3, 6, "minecraft:iron_bars", 8, "Inspect eight Iron Bars"),
            item_task(3, 70, "minecraft:lantern", 4, "Inspect four Lanterns"),
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

    # Reconciled 2026-09-07 with live origin/dev: human streamlining (f3ecc4b)
    # trimmed the cache to a compact starter tied to the Celestial Spire Crate.
    # IDs preserved.
    wizard_tower_rewards = [
        item_reward(3, 75, "numismatics:sprocket", title="Order Construction Grant"),
        item_reward(3, 200, "minecraft:cobbled_deepslate", 64),
        item_reward(3, 201, "minecraft:cobbled_deepslate", 64),
        item_reward(3, 230, "minecraft:dark_oak_log", 64),
        item_reward(3, 250, "minecraft:sand", 64),
        item_reward(3, 270, "minecraft:scaffolding", 64),
        item_reward(3, 77, "minecraft:lapis_lazuli", 16),
        item_reward(3, 272, "minecraft:amethyst_shard", 16),
        item_reward(3, 273, "minecraft:enchanting_table"),
        item_reward(3, 274, "minecraft:lectern"),
    ]
    b_wizard = ch.add(
        14,
        title="Arcane Spire",
        subtitle="Facility Hub · Arcane Study",
        description="Establish the physical study for the Lantern Order's arcane curriculum. Gathering deepslate, dark oak, and amethyst shards unlocks the holy magic branches and awards a compact starter cache of deepslate, dark oak, sand, scaffolding, lapis, an enchanting table, a lectern, and a sprocket construction grant for the Celestial Spire Crate at the Market.",
        icon="irons_spellbooks:inscription_table",
        x=-6.5,
        y=-1.0,
        shape="square",
        optional=True,
        tasks=[
            item_task(3, 75, "minecraft:cobbled_deepslate", 16, "Inspect sixteen Cobbled Deepslate"),
            item_task(3, 76, "minecraft:dark_oak_log", 16, "Inspect sixteen Dark Oak Logs"),
            item_task(3, 78, "minecraft:amethyst_shard", 8, "Inspect eight Amethyst Shards"),
        ],
        rewards=wizard_tower_rewards,
        dependencies=[core3],
    )

    brewery_rewards = [
        item_reward(3, 79, "numismatics:sprocket"),
        *[item_reward(3, 300 + i, "minecraft:tuff", 64) for i in range(18)],
        *[item_reward(3, 330 + i, "abyssal_decor:white_wood_log", 64) for i in range(5)],
        *[item_reward(3, 350 + i, "abyssal_decor:frosted_glass", 64) for i in range(6)],
        item_reward(3, 370, "minecraft:scaffolding", 64),
        item_reward(3, 371, "minecraft:scaffolding", 64),
        item_reward(3, 375, "supplementaries:jar", 16),
        item_reward(3, 376, "supplementaries:faucet", 4),
        item_reward(3, 80, "minecraft:redstone", 64),
        item_reward(3, 81, "minecraft:glowstone_dust", 64),
        item_reward(3, 82, "minecraft:golden_carrot", 16),
        item_reward(3, 372, "minecraft:brewing_stand"),
        item_reward(3, 373, "minecraft:cauldron", 2),
        item_reward(3, 374, "minecraft:lantern", 64),
    ]
    b_brewery = ch.add(
        15,
        title="Apothecary Lab",
        subtitle="Construction · Holy brewery",
        description="Erect a specialized alchemical laboratory to distill holy tinctures, extracts, and draughts. Gather tuff stone, white wood timber, and laboratory glass bottles. The Order supplies bulk volcanic tuff, white wood logs, frosted glass, scaffolding, apothecary jars, liquid faucets, brewing stands, cauldrons, redstone, glowstone, and golden carrots.",
        icon="minecraft:brewing_stand",
        x=-2.5,
        y=0.5,
        shape="square",
        optional=True,
        tasks=[
            item_task(3, 79, "minecraft:tuff", 32, "Inspect thirty-two Tuff"),
            item_task(3, 80, "abyssal_decor:white_wood_log", 32, "Inspect thirty-two White Wood Logs"),
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
        description="Prepare an Inscription Table, an Apprentice's Spell Book, and an Alchemist Cauldron, then demonstrate one Holy spell. The Order equips the initiate with four Holy Runes, Rare and Epic inks, and holy scrolls for healing, divine smite, and recall.",
        icon="irons_spellbooks:holy_rune",
        x=-10.5,
        y=0,
        shape="diamond",
        optional=True,
        tasks=[
            item_task(3, 12, "irons_spellbooks:inscription_table", title="Inspect an Inscription Table"),
            item_task(3, 13, "irons_spellbooks:gold_spell_book", title="Carry an Apprentice's Spell Book"),
            item_task(3, 97, "irons_spellbooks:alchemist_cauldron", title="Craft an Alchemist Cauldron"),
            check_task(3, 24, "I demonstrated one Holy spell"),
        ],
        rewards=hunter_spell_rewards(),
        dependencies=[b_wizard],
    )
    defense = ch.add(
        5,
        title="Pure Defense",
        subtitle="Specialty · Holy vestments",
        description="Forge the holy armaments of the Lantern Order: construct an Arcane Anvil and a Scroll Forge, then don a full set of Priest's vestments. The Order rewards your devotion with a Villager Bible, your choice of an Artificer's Cane or Graybeard Staff, a stack of paper, four pots of Epic Ink, and a sprocket.",
        icon="irons_spellbooks:priest_chestplate",
        x=-7.5,
        y=2,
        shape="diamond",
        optional=True,
        tasks=[
            item_task(3, 34, "irons_spellbooks:arcane_anvil", title="Craft an Arcane Anvil"),
            item_task(3, 35, "irons_spellbooks:scroll_forge", title="Craft a Scroll Forge"),
            item_task(3, 36, "irons_spellbooks:priest_helmet", title="Equip a Priest Hood"),
            item_task(3, 98, "irons_spellbooks:priest_chestplate", title="Equip Priest Robes"),
            item_task(3, 99, "irons_spellbooks:priest_leggings", title="Equip Priest Leggings"),
            item_task(3, 100, "irons_spellbooks:priest_boots", title="Equip Priest Boots"),
        ],
        rewards=[
            item_reward(3, 37, "numismatics:sprocket", 2),
            item_reward(3, 38, "irons_spellbooks:villager_spell_book", title="Villager Bible"),
            choice_reward(3, 39, lid_int(3, 1), title="Choice: Artificer's Cane or Graybeard Staff"),
            item_reward(3, 98, "minecraft:paper", 64),
            item_reward(3, 99, "irons_spellbooks:epic_ink", 4),
        ],
        dependencies=[b_wizard],
    )
    consecrated = ch.add(
        6,
        title="Consecrated Work",
        subtitle="Specialty · Workstations",
        description="Establish a sanctified workshop: assemble an Alchemical Cauldron and an Altar of Cleansing, then prepare sixteen heads of Garlic and Pure Salt Water. The Order rewards your purification efforts with two sprockets, four bottles of Ultimate Holy Water, a Garlic Diffuser, and sixteen bottles of Alchemical Fire.",
        icon="vampirism:alchemical_cauldron",
        x=-4.5,
        y=3.5,
        shape="diamond",
        optional=True,
        tasks=[
            item_task(3, 15, "vampirism:alchemical_cauldron", title="Craft an Alchemical Cauldron"),
            item_task(3, 16, "vampirism:altar_cleansing", title="Construct an Altar of Cleansing"),
            item_task(3, 17, "vampirism:garlic", 16, "Gather sixteen Garlic"),
            item_task(3, 18, "vampirism:pure_salt_water", 4, "Brew four bottles of Pure Salt Water"),
        ],
        rewards=[
            item_reward(3, 26, "numismatics:sprocket", 2),
            item_reward(3, 27, "vampirism:holy_water_bottle_ultimate", 4),
            item_reward(3, 28, "vampirism:garlic_diffuser_normal"),
            item_reward(3, 30, "vampirism:item_alchemical_fire", 16),
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
            item_reward(3, 40, "numismatics:sprocket", 2),
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
            item_reward(3, 51, "numismatics:sprocket", 2),
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
            item_reward(3, 44, "numismatics:sprocket", 2),
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
        description="Set up archery targets, training mannequins, and test specialized quarrels. The Order equips the post with two sprockets, substantial reserves of spitfire and teleport quarrels, normal quarrels, bombs, and harming bamboo spikes.",
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
            item_reward(3, 48, "numismatics:sprocket", 2),
            item_reward(3, 49, "vampirism:crossbow_arrow_spitfire", 32),
            item_reward(3, 50, "vampirism:crossbow_arrow_teleport", 32),
            item_reward(3, 54, "vampirism:crossbow_arrow_normal", 64),
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
            item_reward(3, 29, "numismatics:sprocket", 2),
            item_reward(3, 16, "createbigcannons:ram_rod"),
            item_reward(3, 17, "createbigcannons:worm"),
            item_reward(3, 18, "create:wrench"),
            item_reward(3, 19, "createbigcannons:powder_charge", 64),
            item_reward(3, 91, "createbigcannons:mortar_stone", 64),
        ],
        dependencies=[b_armory],
    )

    return ch


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
    # Reworked 2026-09-07 per Ch4 appendix: teach the Altar of Infusion
    # upgrade (pillars + tips + structure) instead of verifying the base
    # altar; generic bottle/iron/lead/redstone bundle removed.
    core2 = ch.add(
        2,
        title="Red Measure",
        subtitle="Tier II · Altar ascent",
        description="Raise a meaningfully upgraded Altar of Infusion: four Altar Pillars crowned with four Altar Tips over a true stone foundation. The reward funds ritual upkeep with currency, a blood transport bucket, and candles rather than unrelated bulk.",
        icon="vampirism:altar_infusion",
        x=0,
        y=-7,
        shape="gear",
        size=1.3,
        tasks=[
            item_task(4, 91, "vampirism:altar_pillar", 4, "Raise four Altar Pillars"),
            item_task(4, 92, "vampirism:altar_tip", 4, "Crown the pillars with four Altar Tips"),
            item_task(4, 93, "minecraft:stone_bricks", 16, "Lay sixteen Stone Bricks of foundation"),
        ],
        rewards=[
            item_reward(4, 91, "numismatics:sprocket"),
            item_reward(4, 92, "vampirism:blood_bucket"),
            item_reward(4, 93, "minecraft:candle", 16),
        ],
        dependencies=[core1],
    )
    # Redesigned 2026-09-07 per Ch4 appendix: Tier III Household muster that
    # unlocks the four commissions. Heartseeker, blood-iron, and generic
    # metal rewards removed; no altar/storage/automation duplication.
    core3 = ch.add(
        3,
        title="Inherited Edge",
        subtitle="Tier III · Household muster",
        description="Muster the Household: raise a House Notice Board, draft the Household Roll, and convene the four commissions that raise the Spire, Foundry, Hall, and Vault. The reward rings in the new House with a muster bell, currency, and paper without issuing weapons, blood iron, or bulk metals.",
        icon="supplementaries:notice_board",
        x=0,
        y=-4,
        shape="gear",
        size=1.3,
        tasks=[
            item_task(4, 94, "supplementaries:notice_board", title="Raise a House Notice Board"),
            item_task(4, 95, "minecraft:writable_book", title="Draft the Household Roll"),
            check_task(4, 96, "I convened the four commissions"),
        ],
        rewards=[
            item_reward(4, 94, "numismatics:sprocket", 2),
            item_reward(4, 95, "minecraft:bell"),
            item_reward(4, 96, "minecraft:paper", 16),
        ],
        dependencies=[core2],
    )

    # Reworked 2026-09-07 per Ch4 appendix: functional Spire commission
    # (signals/observation/broadcast). Material piles removed; the sprocket
    # spends at the Market Celestial Spire Crate without funding loops.
    b_spire = ch.add(
        14,
        title="Dark Spire",
        subtitle="Commission · Signals and watch",
        description="Commission the Dark Spire as the island's nocturnal signal post: raise lightning rods, post a lookout spyglass, and stock broadcast cassettes for the Nocturnal Broadcast crew. The commission pays one sprocket, sized for the Market Celestial Spire Crate, plus wiring for the signal lamps.",
        icon="minecraft:lightning_rod",
        x=-6.5,
        y=-1.0,
        shape="square",
        optional=True,
        tasks=[
            item_task(4, 97, "minecraft:lightning_rod", 8, "Raise eight Lightning Rods"),
            item_task(4, 98, "minecraft:spyglass", title="Post a lookout Spyglass"),
            item_task(4, 99, "vista:hollow_cassette", 4, "Stock four blank Broadcast Cassettes"),
        ],
        rewards=[
            item_reward(4, 97, "numismatics:sprocket"),
            item_reward(4, 98, "minecraft:redstone", 16),
        ],
        dependencies=[core3],
    )
    # Reworked 2026-09-07 per Ch4 appendix: functional Foundry commission
    # (rendering rig/extraction logistics). Material piles removed; the
    # sprocket spends at the Market Heavy Bastion Crate without loops.
    b_foundry = ch.add(
        15,
        title="Blood Foundry",
        subtitle="Commission · Rendering rig",
        description="Commission the Blood Foundry as the House rendering rig: set seething cauldrons, rig hoist chains, and bank furnace fuel for extraction work. The commission pays one sprocket, sized for the Market Heavy Bastion Crate, plus fuel for the first firing. Sieve automation itself belongs to Sieve Extraction.",
        icon="minecraft:cauldron",
        x=-2.5,
        y=0.5,
        shape="square",
        optional=True,
        tasks=[
            item_task(4, 100, "minecraft:cauldron", 2, "Set two Rendering Cauldrons"),
            item_task(4, 101, "minecraft:chain", 16, "Rig sixteen Hoist Chains"),
            item_task(4, 102, "minecraft:furnace", 4, "Bank four Smelting Furnaces"),
        ],
        rewards=[
            item_reward(4, 99, "numismatics:sprocket"),
            item_reward(4, 100, "minecraft:coal", 16),
        ],
        dependencies=[core3],
    )
    # Reworked 2026-09-07 per Ch4 appendix: functional Hall commission
    # (hospitality: stores, hearth, beds). Material piles removed; the
    # sprocket spends at the Market Frontier Watch Crate without loops.
    b_manor = ch.add(
        16,
        title="Guest Hall",
        subtitle="Commission · Hearth and beds",
        description="Commission the Guest Hall as the island's open hearth: fill provision barrels, keep a welcome campfire, and air two guest beds for travellers caught out after dark. The commission pays one sprocket, sized for the Market Frontier Watch Crate, plus a first welcome stock of bread.",
        icon="minecraft:campfire",
        x=2.5,
        y=0.5,
        shape="square",
        optional=True,
        tasks=[
            item_task(4, 103, "minecraft:barrel", 4, "Fill four Provision Barrels"),
            item_task(4, 104, "minecraft:campfire", 2, "Keep two Welcome Campfires"),
            item_task(4, 105, "minecraft:white_bed", 2, "Air two Guest Beds"),
        ],
        rewards=[
            item_reward(4, 101, "numismatics:sprocket"),
            item_reward(4, 102, "minecraft:bread", 16),
        ],
        dependencies=[core3],
    )
    # Reworked 2026-09-07 per Ch4 appendix: functional Vault commission
    # (records/archive/secure reserves). Material piles removed; the sprocket
    # spends at the Market Sanctified Brewery Crate without loops.
    b_vault = ch.add(
        17,
        title="Blood Vault",
        subtitle="Commission · Archive and reserves",
        description="Commission the Blood Vault as the House archive: shelve records bookshelves, stand a catalogue lectern, and glaze tinted panes for the sealed reserve. The commission pays one sprocket, sized for the Market Sanctified Brewery Crate, plus paper for the first ledgers. Bulk automation belongs to Sieve Extraction.",
        icon="minecraft:lectern",
        x=6.5,
        y=-1.0,
        shape="square",
        optional=True,
        tasks=[
            item_task(4, 106, "minecraft:bookshelf", 2, "Shelve two Archive Bookshelves"),
            item_task(4, 107, "minecraft:lectern", title="Stand a Catalogue Lectern"),
            item_task(4, 108, "minecraft:tinted_glass", 8, "Glaze eight Tinted Archive Panes"),
        ],
        rewards=[
            item_reward(4, 103, "numismatics:sprocket"),
            item_reward(4, 104, "minecraft:paper", 16),
        ],
        dependencies=[core3],
    )

    # Reworked 2026-09-07 per Ch4 appendix: late Dark Spire civic lighting
    # duty, not a weapon tax. Enhanced Heartseeker, enhanced alloy, orb, and
    # diamonds removed; one-time Cog-scale lighting milestone retained.
    mastery = ch.add(
        9,
        title="Night's Due",
        subtitle="Specialty · Signal lighting",
        description="Pay the Night's Due: hang the Spire's signal lighting across the public route, soul-lanterns where the dark pools deepest, then walk the lit perimeter to prove it. This civic lighting duty pays once at Cog scale with lamps and glowstone; it grants no weapons, alloy, or diamonds.",
        icon="minecraft:soul_lantern",
        x=-10.5,
        y=0,
        shape="hexagon",
        size=1.3,
        optional=True,
        tasks=[
            item_task(4, 109, "minecraft:lantern", 16, "Hang sixteen Signal Lanterns"),
            item_task(4, 110, "minecraft:soul_lantern", 8, "Set eight Soul-Lanterns"),
            check_task(4, 111, "I walked the lit perimeter"),
        ],
        rewards=[
            item_reward(4, 105, "numismatics:cog"),
            item_reward(4, 106, "minecraft:glowstone", 16),
            item_reward(4, 107, "minecraft:redstone_lamp", 4),
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
        # Adjusted 2026-09-07 per Ch4 appendix: currency reward raised to two
        # sprockets; cassettes doubled to support actual broadcast use.
        rewards=[
            item_reward(4, 53, "numismatics:sprocket", 2),
            item_reward(4, 54, "vista:hollow_cassette", 8),
        ],
        dependencies=[b_spire],
    )
    # Reworked 2026-09-07 per Ch4 appendix: dedicated blood-processing lane
    # quest (sieve + livestock + feed). Generic metal rewards replaced with
    # lane support; no enhanced alloy granted.
    metallurgy = ch.add(
        7,
        title="Sieve Extraction",
        subtitle="Specialty · Blood processing",
        description="Run a functioning blood-processing lane: commission a Blood Sieve, lead livestock to the pens, and stock feed for the herd. The reward outfits the lane with hoppers, collection bottles, and feed without handing out enhanced alloy or foundry metals.",
        icon="vampirism:blood_sieve",
        x=-4.5,
        y=3.5,
        shape="gear",
        optional=True,
        tasks=[
            item_task(4, 49, "vampirism:blood_sieve", title="Commission a Blood Sieve"),
            item_task(4, 50, "minecraft:lead", 4, "Lead four Head of Livestock"),
            item_task(4, 51, "minecraft:wheat", 16, "Stock sixteen Wheat"),
        ],
        rewards=[
            item_reward(4, 49, "numismatics:sprocket"),
            item_reward(4, 50, "minecraft:hopper", 2),
            item_reward(4, 51, "minecraft:glass_bottle", 16),
            item_reward(4, 52, "minecraft:wheat", 16),
        ],
        dependencies=[b_foundry],
    )
    # Reworked 2026-09-07 per Ch4 appendix: focused daytime-survival loop
    # around the verified Sunscreen Beacon plus umbrella. Saddle/clock
    # tasks and lead/rocket/map rewards removed to avoid duplicating the
    # Market Transit Crate and Broadcast quest.
    transit = ch.add(
        13,
        title="Sunproof Transit",
        subtitle="Specialty · Daytime survival",
        description="Walk at noon and live: raise a Sunscreen Beacon over the foundry route, carry a sunshade umbrella, and prove the crossing on foot. The reward sustains the courier with blood top-ups and trail food; mounts, rockets, maps, and flight stay with the Market Transit Crate and ordinary progression.",
        icon="vampirism:umbrella",
        x=-1.5,
        y=4.5,
        shape="diamond",
        optional=True,
        tasks=[
            item_task(4, 43, "vampirism:sunscreen_beacon", title="Raise a Sunscreen Beacon"),
            item_task(4, 44, "vampirism:umbrella", title="Carry a Sunshade Umbrella"),
            check_task(4, 45, "I crossed the route at noon"),
        ],
        rewards=[
            item_reward(4, 45, "numismatics:sprocket"),
            item_reward(4, 46, "minecraft:glass_bottle", 16),
            item_reward(4, 47, "minecraft:cooked_beef", 16),
        ],
        dependencies=[b_foundry],
    )
    # Reworked 2026-09-07 per Ch4 appendix: distinctive hearth-table service
    # for visitors; generic brewing-stand package removed. No duplication of
    # the Market Recovery Crate or Crimson Reserve; no bulk materials.
    stores = ch.add(
        12,
        title="Wayfarer Table",
        subtitle="Specialty · Hearth service",
        description="Keep the wayfarer's table: a lit hearth campfire, a served welcome cake, and dressed table pots for travellers of any diet. The reward restocks baking and lighting without duplicating the Market Recovery Crate, the Crimson Reserve, or bulk construction stock.",
        icon="minecraft:cake",
        x=1.5,
        y=4.5,
        shape="diamond",
        optional=True,
        tasks=[
            item_task(4, 40, "minecraft:campfire", title="Keep a Hearth Campfire"),
            item_task(4, 41, "minecraft:cake", title="Serve a Welcome Cake"),
            item_task(4, 42, "minecraft:flower_pot", 2, "Dress two Table Pots"),
        ],
        rewards=[
            item_reward(4, 41, "numismatics:sprocket"),
            item_reward(4, 42, "minecraft:wheat", 16),
            item_reward(4, 43, "minecraft:sugar", 8),
            item_reward(4, 44, "minecraft:torch", 16),
        ],
        dependencies=[b_manor],
    )
    # Reworked 2026-09-07 per Ch4 appendix: non-building social function
    # (guest registry). Manor-palette concept, bulk blocks, iron, diamond,
    # and stonecutter removed entirely.
    palette = ch.add(
        6,
        title="Guest Registry",
        subtitle="Specialty · Welcome records",
        description="Open the Guest Hall's doors on paper: stand a registry lectern, open the guest book, and personally welcome a first guest of the mixed settlement. A social and administrative function, not another block collection; it grants record stock, never building bulk, iron, or diamonds.",
        icon="minecraft:lectern",
        x=4.5,
        y=3.5,
        shape="diamond",
        optional=True,
        tasks=[
            item_task(4, 15, "minecraft:lectern", title="Stand a Registry Lectern"),
            item_task(4, 16, "minecraft:writable_book", title="Open the Guest Book"),
            check_task(4, 17, "I welcomed a first guest"),
        ],
        rewards=[
            item_reward(4, 26, "numismatics:sprocket"),
            item_reward(4, 27, "minecraft:paper", 16),
            item_reward(4, 28, "minecraft:feather", 16),
        ],
        dependencies=[b_manor],
    )
    # Reworked 2026-09-07 per Ch4 appendix: deeper emergency reserve with
    # real breeding support. Storage theme kept; automation stays with the
    # Sieve lane and no farm-bypassing herds are granted.
    reserve = ch.add(
        5,
        title="Crimson Reserve",
        subtitle="Specialty · Blood supply",
        description="Hold the emergency reserve visibly: eight blood bottles across two blood containers, plus the breeding stock to refill them. The reward seeds a real herd with feed, leads, and modest fencing; it does not automate processing (see Sieve Extraction) or replace building a farm.",
        icon="vampirism:blood_container",
        x=7.5,
        y=2,
        shape="diamond",
        optional=True,
        tasks=[
            item_task(4, 34, "vampirism:blood_bottle", 8, "Carry eight Blood Bottles"),
            item_task(4, 35, "vampirism:blood_container", 2, "Hold two Blood Containers"),
        ],
        rewards=[
            item_reward(4, 37, "numismatics:sprocket"),
            item_reward(4, 38, "minecraft:glass_bottle", 32),
            item_reward(4, 39, "minecraft:lead", 4),
            item_reward(4, 40, "minecraft:oak_fence", 16),
            item_reward(4, 108, "minecraft:wheat", 16),
            item_reward(4, 109, "minecraft:carrot", 8),
            item_reward(4, 110, "minecraft:potato", 8),
        ],
        dependencies=[b_vault],
    )
    # Reworked 2026-09-07 per Ch4 appendix: blood-mage workshop and loadout
    # mirroring the structure of Ch3 Pure Defense (workstation + equipment +
    # controlled supplies), with vampire items throughout. Random high-tier
    # scrolls, duplicate scrolls, free endgame armour, and task-invalidating
    # rewards removed.
    script = ch.add(
        4,
        title="Scarlet Script",
        subtitle="Specialty · Blood-mage workshop",
        description="Complete the blood-mage workshop: raise an Arcane Anvil, bind an Iron Spell Book, wield a Blood Staff, and fill blood vials for the work ahead. The reward outfits the mage with an upgrade orb, vellum, paper, controlled epic ink, and currency; it grants no high-tier scrolls and nothing that replaces the assembled loadout.",
        icon="irons_spellbooks:blood_staff",
        x=10.5,
        y=0,
        shape="diamond",
        optional=True,
        tasks=[
            item_task(4, 12, "irons_spellbooks:arcane_anvil", title="Raise an Arcane Anvil"),
            item_task(4, 13, "irons_spellbooks:iron_spell_book", title="Bind an Iron Spell Book"),
            item_task(4, 14, "irons_spellbooks:blood_staff", title="Wield a Blood Staff"),
            item_task(4, 24, "irons_spellbooks:blood_vial", 4, "Fill four Blood Vials"),
        ],
        rewards=[
            item_reward(4, 112, "numismatics:sprocket", 2),
            item_reward(4, 113, "irons_spellbooks:blood_upgrade_orb"),
            item_reward(4, 114, "irons_spellbooks:bloody_vellum", 16),
            item_reward(4, 115, "minecraft:paper", 32),
            item_reward(4, 116, "irons_spellbooks:epic_ink", 2),
        ],
        dependencies=[b_vault],
    )

    return ch


MINUTE = 60
BUILDING_MARKET_COOLDOWN = 3 * MINUTE
PROGRESSION_MARKET_COOLDOWN = 5 * MINUTE


def build_market(group: str) -> Chapter:
    # Redesigned 2026-09-07 per Ch5 appendix: two-wing storefront with
    # building palettes left, progression kits right, explanations center.
    # Dependency lines stay hidden chapter-wide; purchase cooldowns are
    # short (3/5 min) while the currency faucet remains weekly. All
    # purchases are personal-scope unless stated; no purchase returns its
    # own currency and no diamond redemption exists.
    ch = Chapter(
        5,
        "ch05_market_services",
        "05 · Market Services",
        group,
        "numismatics:sprocket",
        0,
        default_hide_dependency_lines=True,
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
        subtitle="Market guide · Personal scope",
        description="The board is two departments: building palettes on the left, progression and utility kits on the right. Every purchase consumes the exact posted price for one personal kit, restocks after three minutes (building) or five minutes (progression), and never pays currency back. The Rumour Ledger remains the sole slow weekly team faucet.",
        icon="numismatics:banking_guide",
        x=0,
        y=-5,
        shape="hexagon",
        size=1.4,
        tasks=[check_task(5, 1, "I understand prices, cooldowns, and personal scope")],
        dependencies=[qid(2, 7)],
    )

    def sink(index: int, *, title: str, subtitle: str, description: str, icon: str, x: float, y: float, price_item: str, price_count: int, task_idx: int, rewards: list[dict[str, Any]], cooldown: int = PROGRESSION_MARKET_COOLDOWN, shape: str = "diamond") -> str:
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
            shape="hexagon" if index == 7 else shape,
            size=1.3 if index == 7 else 1.0,
            optional=True,
            can_repeat=True,
            cooldown=cooldown,
            tasks=[item_task(5, task_idx, price_item, price_count, label, consume=True)],
            rewards=rewards,
            dependencies=[opener],
        )

    # Left wing: raw and themed building palettes (square family).
    sink(
        3,
        title="Works Kit",
        subtitle="1 Sprocket · 3 min",
        description="Consume one Sprocket for a personal raw building stock of bulk Stone, Oak, Sand, Glass, and Lanterns: about twelve full-stack equivalents for repairs, shelters, and civic rooms. Restocks after three minutes. Flexible raw stock, not premade bricks, machines, or combat gear.",
        icon="minecraft:stone",
        x=-7,
        y=-1,
        price_item="numismatics:sprocket",
        price_count=1,
        task_idx=3,
        cooldown=BUILDING_MARKET_COOLDOWN,
        shape="square",
        rewards=[
            item_reward(5, 73, "minecraft:stone", 64),
            item_reward(5, 74, "minecraft:stone", 64),
            item_reward(5, 75, "minecraft:stone", 64),
            item_reward(5, 76, "minecraft:stone", 64),
            item_reward(5, 77, "minecraft:stone", 64),
            item_reward(5, 78, "minecraft:stone", 64),
            item_reward(5, 79, "minecraft:stone", 64),
            item_reward(5, 80, "minecraft:stone", 64),
            item_reward(5, 81, "minecraft:stone", 64),
            item_reward(5, 82, "minecraft:oak_log", 64),
            item_reward(5, 83, "minecraft:oak_log", 64),
            item_reward(5, 84, "minecraft:sand", 64),
            item_reward(5, 85, "minecraft:glass", 16),
            item_reward(5, 86, "minecraft:lantern", 8),
        ],
    )
    sink(
        15,
        title="Village Hearth Kit",
        subtitle="1 Sprocket · 3 min",
        description="Consume one Sprocket for a personal village palette of Bricks, Oak, Terracotta, Glass, Lanterns, and a Hearth Campfire for homes, inns, and workshops. Restocks after three minutes. Homes and civic rooms, not fortifications or machinery.",
        icon="minecraft:bricks",
        x=-3.5,
        y=-1,
        price_item="numismatics:sprocket",
        price_count=1,
        task_idx=12,
        cooldown=BUILDING_MARKET_COOLDOWN,
        shape="square",
        rewards=[
            item_reward(5, 87, "minecraft:brick", 64),
            item_reward(5, 88, "minecraft:brick", 64),
            item_reward(5, 89, "minecraft:brick", 64),
            item_reward(5, 90, "minecraft:brick", 64),
            item_reward(5, 91, "minecraft:brick", 64),
            item_reward(5, 92, "minecraft:brick", 64),
            item_reward(5, 93, "minecraft:oak_log", 64),
            item_reward(5, 94, "minecraft:oak_log", 64),
            item_reward(5, 95, "minecraft:oak_log", 64),
            item_reward(5, 96, "minecraft:terracotta", 64),
            item_reward(5, 97, "minecraft:terracotta", 64),
            item_reward(5, 98, "minecraft:glass", 32),
            item_reward(5, 99, "minecraft:lantern", 8),
            item_reward(5, 100, "minecraft:campfire", 2),
        ],
    )
    # Right wing: progression starters and utility (diamond family).
    sink(
        2,
        title="Field Kit",
        subtitle="1 Bevel · 5 min",
        description="Consume one Bevel for a personal survival refill of food, torches, leads, and a shield for late arrivals and failed expeditions. Restocks after five minutes. Convenience, not building stock or progression.",
        icon="numismatics:bevel",
        x=7,
        y=-1,
        price_item="numismatics:bevel",
        price_count=1,
        task_idx=2,
        cooldown=PROGRESSION_MARKET_COOLDOWN,
        shape="diamond",
        rewards=[
            item_reward(5, 1, "minecraft:cooked_beef", 16),
            item_reward(5, 2, "minecraft:torch", 32),
            item_reward(5, 3, "minecraft:lead", 4),
            item_reward(5, 118, "minecraft:shield"),
        ],
    )
    sink(
        5,
        title="Create Starter Kit",
        subtitle="2 Sprockets · 5 min",
        description="Consume two Sprockets for a personal early-Create starter of alloy, shafts, cogwheels, belts, a wrench, and copper for first machines. Restocks after five minutes. A beginning, not precision mechanisms, brass-age parts, or an automated factory.",
        icon="create:shaft",
        x=3.5,
        y=-1,
        price_item="numismatics:sprocket",
        price_count=2,
        task_idx=5,
        cooldown=PROGRESSION_MARKET_COOLDOWN,
        shape="diamond",
        rewards=[
            item_reward(5, 12, "create:andesite_alloy", 16),
            item_reward(5, 13, "create:shaft", 8),
            item_reward(5, 14, "create:cogwheel", 8),
            item_reward(5, 15, "create:large_cogwheel", 4),
            item_reward(5, 101, "create:belt_connector", 4),
            item_reward(5, 102, "create:wrench"),
            item_reward(5, 103, "minecraft:copper_ingot", 16),
        ],
    )
    sink(
        4,
        title="Iron's Spells Starter Kit",
        subtitle="1 Sprocket · 5 min",
        description="Consume one Sprocket for a personal first-steps magic kit of essence, blank runes, common and uncommon inks, and a Copper Spell Book. Restocks after five minutes. Learn the school, not a finished mage loadout or high-tier scrolls.",
        icon="irons_spellbooks:copper_spell_book",
        x=7,
        y=2.5,
        price_item="numismatics:sprocket",
        price_count=1,
        task_idx=4,
        cooldown=PROGRESSION_MARKET_COOLDOWN,
        shape="diamond",
        rewards=[
            item_reward(5, 8, "irons_spellbooks:arcane_essence", 8),
            item_reward(5, 9, "irons_spellbooks:blank_rune", 2),
            item_reward(5, 10, "irons_spellbooks:common_ink", 8),
            item_reward(5, 11, "irons_spellbooks:uncommon_ink", 4),
            item_reward(5, 104, "irons_spellbooks:copper_spell_book"),
        ],
    )
    sink(
        9,
        title="Recovery Crate",
        subtitle="1 Sprocket · 5 min",
        description="Consume one Sprocket for a personal recovery cache after a failed expedition: beds, shields, honey, and golden apples. Restocks after five minutes. Readiness restored, no permanent combat power, no mounts.",
        icon="minecraft:golden_apple",
        x=3.5,
        y=2.5,
        price_item="numismatics:sprocket",
        price_count=1,
        task_idx=9,
        cooldown=PROGRESSION_MARKET_COOLDOWN,
        shape="diamond",
        rewards=[
            item_reward(5, 20, "minecraft:white_bed", 2),
            item_reward(5, 21, "minecraft:shield", 2),
            item_reward(5, 22, "minecraft:honey_bottle", 16),
            item_reward(5, 23, "minecraft:golden_apple", 4),
        ],
    )
    sink(
        10,
        title="Transit Crate",
        subtitle="2 Sprockets · 5 min",
        description="Consume two Sprockets for a personal route kit of saddles, leads, rockets, boats, and compasses to move people and stock. Restocks after five minutes. No elytra, no teleport tier, no permanent flight.",
        icon="minecraft:saddle",
        x=3.5,
        y=6,
        price_item="numismatics:sprocket",
        price_count=2,
        task_idx=10,
        cooldown=PROGRESSION_MARKET_COOLDOWN,
        shape="diamond",
        rewards=[
            item_reward(5, 24, "minecraft:saddle", 4),
            item_reward(5, 25, "minecraft:lead", 16),
            item_reward(5, 26, "minecraft:firework_rocket", 64),
            item_reward(5, 27, "minecraft:oak_boat", 4),
            item_reward(5, 28, "minecraft:compass", 4),
        ],
    )
    # Re-scoped 2026-09-07 per Ch5 appendix: the Cog purchase becomes a
    # civic-works package with distinctive scale but no diamonds,
    # progression alloy, or strict domination of lower kits.
    sink(
        7,
        title="Civic Works Bond",
        subtitle="1 Cog · 5 min",
        description="Consume one Cog for a personal civic-works package behind one shared project: bulk Stone and Oak, scaffolding, Glass, Chains, and Lanterns at a scale no single lower kit matches. Restocks after five minutes. Shared building stock, not diamonds, alloy, or combat gear.",
        icon="numismatics:cog",
        x=0,
        y=-1,
        price_item="numismatics:cog",
        price_count=1,
        task_idx=6,
        cooldown=PROGRESSION_MARKET_COOLDOWN,
        rewards=[
            item_reward(5, 16, "minecraft:stone", 64),
            item_reward(5, 17, "minecraft:stone", 64),
            item_reward(5, 18, "minecraft:stone", 64),
            item_reward(5, 105, "minecraft:stone", 64),
            item_reward(5, 19, "minecraft:oak_log", 64),
            item_reward(5, 29, "minecraft:oak_log", 64),
            item_reward(5, 106, "minecraft:scaffolding", 64),
            item_reward(5, 107, "minecraft:scaffolding", 64),
            item_reward(5, 108, "minecraft:glass", 32),
            item_reward(5, 109, "minecraft:chain", 16),
            item_reward(5, 110, "minecraft:lantern", 16),
        ],
    )
    # Center column: the faucet stays weekly and team-scoped by design; the
    # coin guide is informational and non-repeatable.
    ch.add(
        6,
        title="Rumour Ledger",
        subtitle="Fallback · 1 team Bevel weekly",
        description="File one written maintenance report naming a findable place, a real problem, and the person who will review the result. The book is consumed as the archive copy; this is the board's sole slow currency faucet, deliberately weekly and team-scoped while purchases restock in minutes.",
        icon="minecraft:written_book",
        x=0,
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
        description="Numismatics base values are Spur 1, Bevel 8, Sprocket 16, and Cog 64. Routine work pays Bevels, specialties pay Sprockets, and major team milestones pay Cogs; Crowns and Suns remain outside this campaign. Purchases are personal-scope with three-minute building and five-minute progression restocks; only the Rumour Ledger faucet is weekly and team-scoped.",
        icon="numismatics:cog",
        x=0,
        y=6,
        shape="diamond",
        optional=True,
        tasks=[check_task(5, 8, "I understand the coin denominations")],
        dependencies=[opener],
    )

    # Left wing, lower rows: the four preserved human-authored construction
    # crates (IDs 17-20 kept). Contents are the refined manual palettes,
    # unchanged; the redesign moves them into the building wing with short
    # personal restocks and explicit scope/contents descriptions.
    def crate(
        index: int,
        *,
        title: str,
        subtitle: str,
        description: str,
        icon: str,
        x: float,
        y: float,
        task_idx: int,
        rewards: list[dict[str, Any]],
    ) -> str:
        return ch.add(
            index,
            title=title,
            subtitle=subtitle,
            description=description,
            icon=icon,
            x=x,
            y=y,
            shape="square",
            optional=True,
            can_repeat=True,
            cooldown=BUILDING_MARKET_COOLDOWN,
            tasks=[item_task(5, task_idx, "numismatics:sprocket", 1, "Submit 1 Sprocket", consume=True)],
            rewards=rewards,
            dependencies=[opener],
        )

    # NOTE: live quest IDs use hex-style numbering 7A11C0DF00500011-14, i.e.
    # decimal indices 17-20. Decimal 11-14 (…0000B-E) stay free.
    crate(
        17,
        title="Celestial Spire Crate",
        subtitle="1 Sprocket · 3 min",
        description="Consume one Sprocket for a personal dark-arcane palette of deepslate tiles, dark oak planks, tinted glass, amethyst clusters, bookshelves, and sea lanterns for observatories and ritual studies. Restocks after three minutes. An Order Construction Grant spends here. Decorative stock, not progression alloy or workstations.",
        icon="minecraft:deepslate_tiles",
        x=-7,
        y=2.5,
        task_idx=0x21,
        # Stack-safety split 2026-09-07 per Ch5 appendix S11: the legacy
        # 128-count tile reward becomes two 64-count entries. Original ID
        # 0x31 kept for the first stack; 119 allocated for the second.
        rewards=[
            item_reward(5, 0x31, "minecraft:deepslate_tiles", 64),
            item_reward(5, 119, "minecraft:deepslate_tiles", 64),
            item_reward(5, 0x32, "minecraft:dark_oak_planks", 64),
            item_reward(5, 0x33, "minecraft:tinted_glass", 64),
            item_reward(5, 0x34, "minecraft:amethyst_cluster", 16),
            item_reward(5, 0x35, "minecraft:bookshelf", 16),
            item_reward(5, 0x36, "minecraft:sea_lantern", 8),
        ],
    )
    crate(
        18,
        title="Sanctified Brewery Crate",
        subtitle="1 Sprocket · 3 min",
        description="Consume one Sprocket for a personal light-masonry palette of polished tuff, white wood planks, frosted glass, apothecary jars, faucets, and lanterns for breweries, workshops, and scholastic halls. Restocks after three minutes. An Order Construction Grant spends here. Decorative stock, not progression alloy or workstations.",
        icon="abyssal_decor:white_wood_planks",
        x=-3.5,
        y=2.5,
        task_idx=0x22,
        # Stack-safety split 2026-09-07 per Ch5 appendix S11: legacy 128
        # tuff reward divided across IDs 0x37 (kept) and 120 (allocated).
        rewards=[
            item_reward(5, 0x37, "minecraft:polished_tuff", 64),
            item_reward(5, 120, "minecraft:polished_tuff", 64),
            item_reward(5, 0x38, "abyssal_decor:white_wood_planks", 64),
            item_reward(5, 0x39, "abyssal_decor:frosted_glass", 64),
            item_reward(5, 0x3A, "supplementaries:jar", 16),
            item_reward(5, 0x3B, "supplementaries:faucet", 4),
            item_reward(5, 0x3C, "minecraft:lantern", 16),
        ],
    )
    crate(
        19,
        title="Frontier Watch Crate",
        subtitle="1 Sprocket · 3 min",
        description="Consume one Sprocket for a personal frontier palette of spruce planks, timber frames, ropes, way signs, torches, and spyglasses for outposts and watchtowers. Restocks after three minutes. An Order Construction Grant spends here. Decorative stock, not progression alloy or workstations.",
        icon="supplementaries:timber_frame",
        x=-7,
        y=6,
        task_idx=0x23,
        # Stack-safety split 2026-09-07 per Ch5 appendix S11: legacy 128
        # planks divided across IDs 0x3D (kept) and 121 (allocated).
        rewards=[
            item_reward(5, 0x3D, "minecraft:spruce_planks", 64),
            item_reward(5, 121, "minecraft:spruce_planks", 64),
            item_reward(5, 0x3E, "supplementaries:timber_frame", 64),
            item_reward(5, 0x3F, "supplementaries:rope", 32),
            item_reward(5, 0x40, "supplementaries:way_sign_oak", 16),
            item_reward(5, 0x41, "minecraft:torch", 32),
            item_reward(5, 0x42, "minecraft:spyglass", 2),
        ],
    )
    crate(
        20,
        title="Heavy Bastion Crate",
        subtitle="1 Sprocket · 3 min",
        description="Consume one Sprocket for a personal fortress palette of Create Deco iron catwalks, sheet metal, supports, mesh fences, chains, and iron bars for bastions and armories. Restocks after three minutes. An Order Construction Grant spends here. Decorative stock, not progression alloy or workstations.",
        icon="createdeco:industrial_iron_catwalk",
        x=-3.5,
        y=6,
        task_idx=0x24,
        rewards=[
            item_reward(5, 0x43, "createdeco:industrial_iron_catwalk", 64),
            item_reward(5, 0x44, "createdeco:industrial_iron_sheet_metal", 64),
            item_reward(5, 0x45, "createdeco:industrial_iron_support", 32),
            item_reward(5, 0x46, "createdeco:industrial_iron_mesh_fence", 32),
            item_reward(5, 0x47, "minecraft:chain", 32),
            item_reward(5, 0x48, "minecraft:iron_bars", 32),
        ],
    )
    # New 2026-09-07 per Ch5 appendix: Create Deco palette from IDs
    # verified in the pinned Create Deco JAR (pearl/scarlet brick families
    # and iron windows). No unverified Umbra palette is used.
    sink(
        21,
        title="Create Deco Palette",
        subtitle="2 Sprockets · 3 min",
        description="Consume two Sprockets for a personal Create Deco palette of Pearl and Scarlet bricks with stairs plus iron windows and bars for industrial facades. Restocks after three minutes. Decorative stock, not machines, precision parts, or combat gear.",
        icon="createdeco:pearl_bricks",
        x=-5.25,
        y=9.5,
        price_item="numismatics:sprocket",
        price_count=2,
        task_idx=13,
        cooldown=BUILDING_MARKET_COOLDOWN,
        shape="square",
        rewards=[
            item_reward(5, 112, "createdeco:pearl_bricks", 64),
            item_reward(5, 113, "createdeco:scarlet_bricks", 64),
            item_reward(5, 114, "createdeco:pearl_brick_stairs", 32),
            item_reward(5, 115, "createdeco:scarlet_brick_stairs", 32),
            item_reward(5, 116, "createdeco:industrial_iron_window", 16),
            item_reward(5, 117, "createdeco:industrial_iron_bars", 16),
        ],
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
        "default_hide_dependency_lines": chapter.default_hide_dependency_lines,
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
            "default_hide_dependency_lines": chapter.default_hide_dependency_lines,
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
    tables = build_reward_tables()
    base = root / "config/ftbquests/quests"
    result: dict[Path, str] = {
        base / "chapter_groups.snbt": render_groups(groups),
        base / "data.snbt": render_data(),
        base / "lang/en_us.snbt": "{\n}\n",
        root / "docs/vvh/campaign_manifest.json": json.dumps(normalized_manifest(chapters, groups), indent=2, ensure_ascii=False) + "\n",
    }
    for chapter in chapters:
        result[base / "chapters" / f"{chapter.filename}.snbt"] = render_chapter(chapter)
    for table in tables:
        result[base / "reward_tables" / f"{table.filename}.snbt"] = render_reward_table(table)
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
