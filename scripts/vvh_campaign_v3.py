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
import copy
import hashlib
import json
import os
import re
import tempfile
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Iterable

from vvh_campaign_overrides import ACTIVE_REVIEWED_QUEST_OVERRIDES, REVIEWED_SOURCE_COMMITS

Q_PREFIX = 0x7A11C0DF00000000
T_PREFIX = 0x7A11C1DF00000000
R_PREFIX = 0x7A11C2DF00000000
C_PREFIX = 0x7A11C3DF00000000
G_PREFIX = 0x7A11C4DF00000000
L_PREFIX = 0x7A11C5DF00000000
WEEK = 604800
HASH_LEDGER_REL = Path("docs/vvh/generated_output_hashes.json")
HASH_LEDGER_VERSION = 1

RETIRED_CHAPTER_FILES = {
    "ch05_free_companies.snbt",
    "ch06_common_ground.snbt",
    "ch07_odd_hours.snbt",
    "ch08_market_services.snbt",
    "ch09_common_ground.snbt",
    "ch10_market_services.snbt",
}

REVIEWED_OVERRIDE_FIELDS = {
    "description",
    "icon",
    "min_required_dependencies",
    "rewards",
    "subtitle",
    "tasks",
    "title",
    "x",
}
HEX_ID = re.compile(r"^[0-9A-F]{16}$")


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
        hide_dependency_lines: bool | None = None,
    ) -> str:
        quest: dict[str, Any] = {
            "dependencies": list(dependencies),
            "description": [description],
            "icon": {"id": icon},
            "id": qid(self.number, index),
        }
        # ``None`` means inherit the chapter default.  An explicit boolean is
        # retained in the quest so a future chapter default change cannot
        # erase a deliberate exception (including an explicit ``false``).
        if hide_dependency_lines is not None:
            quest["hide_dependency_lines"] = hide_dependency_lines
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
        # One panorama frames the whole chapter; keep the native 16:9 aspect.
        images=[{
            "alpha": 130, "height": 13.5, "width": 24,
            "image": "poiesis:textures/questpics/vvh/island_remembers.png",
            "order": -40, "rotation": 0.0, "x": 0, "y": -1,
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
        # One panorama frames the whole chapter; keep the native 16:9 aspect.
        images=[{
            "alpha": 105, "height": 13.5, "width": 24,
            "image": "poiesis:textures/questpics/vvh/rivalry_without_ruin.png",
            "order": -40, "rotation": 0.0, "x": 0, "y": -1,
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
        # One panorama frames the whole chapter; keep the native 16:9 aspect.
        images=[{
            "alpha": 140, "height": 19.125, "width": 34,
            "image": "poiesis:textures/questpics/vvh/lantern_order_holy_panorama.png",
            "order": -40, "rotation": 0.0, "x": 0, "y": -2.5,
        }],
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
    # trimmed bulk rewards to a starter kit and retained the ordinary Sprocket
    # currency reward. IDs preserved.
    building_supplies_rewards = [
        item_reward(3, 6, "numismatics:sprocket", title="1 Sprocket"),
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
        description="Gather an essential construction stock of stone bricks, logs, iron bars, and lanterns. Completing this foundation rewards a manageable starter building kit with two stacks of stone, a stack each of oak and spruce logs, iron, copper, a stonecutter, a wrench, and one Sprocket to spend at the Market.",
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
        item_reward(3, 75, "numismatics:sprocket", title="1 Sprocket"),
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
        description="Establish the physical study for the Lantern Order's arcane curriculum. Gathering deepslate, dark oak, and amethyst shards unlocks the holy magic branches and awards a compact starter cache of deepslate, dark oak, sand, scaffolding, lapis, an enchanting table, a lectern, and one Sprocket to spend on the Celestial Spire Crate at the Market.",
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
            # Rabbit Stew is unstackable. Preserve the original entitlement
            # ID and total quantity, delivering each remaining bowl separately.
            item_reward(3, 94, "minecraft:rabbit_stew"),
            *[item_reward(3, 0x5000 + index, "minecraft:rabbit_stew") for index in range(1, 16)],
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
    # Chapter 4 is deliberately pinned to the live horseshoe.  Keep existing
    # quest IDs, coordinates, dependencies, optional flags, and First Thirst
    # semantics stable; redesigned task/reward identities use the reserved
    # 0x4000/0x5000 local ranges so old claims cannot be silently reclaimed.
    ch = Chapter(
        4,
        "ch04_house_night",
        "04 · House of Night",
        group,
        "vampirism:vampire_fang",
        2,
        # One panorama frames the whole chapter; keep the native 16:9 aspect.
        images=[{
            "alpha": 150, "height": 19.125, "width": 34,
            "image": "poiesis:textures/questpics/vvh/house_of_night_blood_panorama.png",
            "order": -40, "rotation": 0.0, "x": 0, "y": -2.5,
        }],
    )
    # New identities are deliberately disjoint from the historical task and
    # reward IDs.  Existing Sprocket IDs are retained where the entitlement
    # remains currency, including commission rewards whose scope is now shared.
    def nt(index: int, item: str, count: int = 1, title: str | None = None):
        return item_task(4, 0x4000 + index, item, count, title)

    def nc(index: int, title: str):
        return check_task(4, 0x4000 + index, f"Player-confirmed: {title}")

    def nr(index: int, item: str, count: int = 1, *, team: bool = False, title: str | None = None):
        return item_reward(4, 0x5000 + index, item, count, team=team, title=title)

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
        subtitle="Tier II · Altar ascent",
        description="Prepare your ascent from Vampire level 4 to level 5. Bring an Altar of Infusion, eight Altar Pillars, four Altar Tips, eight Stone Bricks, five Human Hearts, and a Vampire Book. Build four two-pillar columns three blocks north, south, east, and west of the altar, with their bases at altar height. Fill each pillar with a Stone Brick and cap each column with a tip. This supplies the eight structure points for the night-time ritual; no pure blood is needed. These inventory checks record your supplies, so assemble and activate the altar yourself.",
        icon="vampirism:altar_infusion",
        x=0,
        y=-7,
        shape="gear",
        size=1.3,
        tasks=[
            nt(1, "vampirism:altar_infusion", title="Bring an Altar of Infusion"),
            nt(2, "vampirism:altar_pillar", 8, "Bring eight Altar Pillars"),
            nt(3, "vampirism:altar_tip", 4, "Bring four Altar Tips"),
            nt(4, "minecraft:stone_bricks", 8, "Bring eight Stone Bricks"),
            nt(54, "vampirism:human_heart", 5, "Bring five Human Hearts"),
            nt(55, "vampirism:vampire_book", title="Bring a Vampire Book"),
        ],
        rewards=[
            item_reward(4, 0x5B, "numismatics:sprocket", 2),
        ],
        dependencies=[core1],
    )
    core3 = ch.add(
        3,
        title="House Charter",
        subtitle="Tier III · Shared refuge",
        description="Found the House: keep a real coffin at the daytime refuge, prepare a backpack and clipboard for its quartermaster, and sign a House plan naming the Dark Spire, Blood Foundry, Guest Hall, and Blood Vault services with their public-access boundaries. The plan is player-confirmed; the quest does not inspect private claims or book text.",
        icon="vampirism:coffin_red",
        x=0,
        y=-4,
        shape="gear",
        size=1.3,
        tasks=[
            nt(5, "vampirism:coffin_red", title="Bring a House Coffin"),
            nt(6, "sophisticatedbackpacks:backpack", title="Bring a Quartermaster Backpack"),
            nt(7, "create:clipboard", title="Bring a House Clipboard"),
            nt(8, "minecraft:written_book", title="Carry the signed House Plan"),
            nc(9, "I signed the House plan and marked its public boundaries"),
        ],
        rewards=[
            item_reward(4, 0x5E, "numismatics:sprocket", 2),
            nr(2, "minecraft:compass", title="House Route Compass"),
        ],
        dependencies=[core2],
    )

    b_spire = ch.add(
        14,
        title="Dark Spire Commission",
        subtitle="Commission · Observation and signalling",
        description="Establish the Dark Spire service: keep a spyglass for observation, a bell for local signalling, and a written signal register. State what the tower broadcasts and where its public boundary begins; the Market palette recommendation is Celestial Spire or another suitable tower palette. Television and Viewfinder belong to Nocturnal Broadcast later.",
        icon="minecraft:spyglass",
        x=-6.5,
        y=-1.0,
        shape="square",
        size=1.1,
        optional=True,
        tasks=[
            nt(10, "minecraft:spyglass", title="Bring a Spire Spyglass"),
            nt(11, "minecraft:bell", title="Bring a Signal Bell"),
            nt(12, "minecraft:paper", 8, "Bring eight Signal Register Pages"),
            nc(13, "I named the tower service and its public boundary"),
        ],
        rewards=[item_reward(4, 0x61, "numismatics:sprocket", 2, team=True)],
        dependencies=[core3],
    )
    b_foundry = ch.add(
        15,
        title="Blood Foundry Commission",
        subtitle="Commission · Blood handling",
        description="Establish the Foundry service with a Blood Grinder and a small raw-blood input. Four Raw Beef provide 800 mB of impure blood when the grinder's lower fluid receiver accepts the batch; confirm that output at the service boundary. The recommended Market palette is Heavy Bastion or Create Builder. Sieve Extraction later teaches conversion of impure blood, while this commission establishes the input apparatus.",
        icon="vampirism:blood_grinder",
        x=-2.5,
        y=0.5,
        shape="square",
        size=1.1,
        optional=True,
        tasks=[
            nt(14, "vampirism:blood_grinder", title="Bring a Blood Grinder"),
            nt(15, "minecraft:beef", 4, "Bring four Raw Beef"),
            nc(18, "I ran the beef batch into a lower fluid receiver and marked the Foundry boundary"),
        ],
        rewards=[item_reward(4, 0x63, "numismatics:sprocket", 2, team=True)],
        dependencies=[core3],
    )
    b_manor = ch.add(
        16,
        title="Guest Hall Commission",
        subtitle="Commission · Reception service",
        description="Establish the Guest Hall as a public reception service: prepare a lectern and visitor register, keep a barrel of welcome stock, and name the public entrance without granting access to private claimed areas. The Market palette recommendation is Frontier Watch or Village Timber.",
        icon="minecraft:lectern",
        x=2.5,
        y=0.5,
        shape="square",
        size=1.1,
        optional=True,
        tasks=[
            nt(19, "minecraft:lectern", title="Bring a Visitor Register Lectern"),
            nt(20, "minecraft:writable_book", title="Bring a Visitor Register"),
            nt(21, "minecraft:barrel", title="Bring a Welcome Barrel"),
            nt(22, "minecraft:campfire", title="Bring a Reception Hearth"),
            nc(23, "I marked the public entrance and visitor service boundary"),
        ],
        rewards=[item_reward(4, 0x65, "numismatics:sprocket", 2, team=True)],
        dependencies=[core3],
    )
    b_vault = ch.add(
        17,
        title="Blood Vault Commission",
        subtitle="Commission · Archive and reserve records",
        description="Establish the Blood Vault as an archive and reserve-management station: keep a lectern, written ledger, and labelled chest for reserve records. The recommended Market palette is Sanctified Brewery or Iron's Spells Arcanum. The commission documents the service; it does not require a completed blood-storage system or an advanced spell workshop.",
        icon="minecraft:lectern",
        x=6.5,
        y=-1.0,
        shape="square",
        size=1.1,
        optional=True,
        tasks=[
            nt(24, "minecraft:lectern", title="Bring an Archive Lectern"),
            nt(25, "minecraft:written_book", title="Bring the Reserve Ledger"),
            nt(26, "minecraft:chest", title="Bring a Reserve Chest"),
            nc(27, "I defined the archive and reserve-management service"),
        ],
        rewards=[item_reward(4, 0x67, "numismatics:sprocket", 2, team=True)],
        dependencies=[core3],
    )

    mastery = ch.add(
        9,
        title="Dawn Watch",
        subtitle="Specialty · Dawn warning",
        description="Build a dawn-warning relay for the public route: bring a Daylight Detector, repeaters, and a clearly labelled warning lamp. The wiring test is player-confirmed because an ordinary task cannot inspect live signal connectivity.",
        icon="minecraft:daylight_detector",
        x=-10.5,
        y=0,
        shape="hexagon",
        size=1.3,
        optional=True,
        tasks=[
            nt(28, "minecraft:daylight_detector", title="Bring a Daylight Detector"),
            nt(29, "minecraft:repeater", 2, "Bring two Signal Repeaters"),
            nt(30, "minecraft:redstone_lamp", title="Bring a Warning Lamp"),
            nc(31, "I tested the dawn warning circuit at first light"),
        ],
        rewards=[
            item_reward(4, 0x69, "numismatics:sprocket", 2),
            nr(4, "minecraft:redstone", 16),
            nr(5, "minecraft:repeater", 2),
        ],
        dependencies=[b_spire],
    )
    courier = ch.add(
        8,
        title="Nocturnal Broadcast",
        subtitle="Specialty · Vista broadcast",
        description="Bring a Television and Viewfinder to establish visual broadcast capabilities across the island. The House supplies two Sprockets and eight Hollow Cassettes for recording feeds.",
        icon="vista:television",
        x=-7.5,
        y=2,
        shape="diamond",
        optional=True,
        tasks=[
            item_task(4, 19, "vista:television", title="Bring a Television"),
            item_task(4, 20, "vista:viewfinder", title="Bring a Viewfinder"),
        ],
        rewards=[
            item_reward(4, 0x35, "numismatics:sprocket", 2),
            item_reward(4, 0x36, "vista:hollow_cassette"),
            nr(0x100, "vista:hollow_cassette"),
            nr(0x101, "vista:hollow_cassette"),
            nr(0x102, "vista:hollow_cassette"),
            nr(0x103, "vista:hollow_cassette"),
            nr(0x104, "vista:hollow_cassette"),
            nr(0x105, "vista:hollow_cassette"),
            nr(0x106, "vista:hollow_cassette"),
        ],
        dependencies=[b_spire],
    )
    metallurgy = ch.add(
        7,
        title="Sieve Extraction",
        subtitle="Specialty · Blood processing",
        description="Turn impure blood into a useful House supply. Place one Blood Container above the Blood Sieve to feed it and a second below to receive blood. Four parts of impure blood yield three parts of blood; run 1,200 mB through the Sieve for 900 mB, enough to fill one Blood Bottle. Its item task only proves that a Blood Bottle exists, so the player-confirmed note records the Sieve as its origin. Run a batch and check the receiving container before confirming the test yourself; the inventory tasks only check that you have the apparatus. Collecting blood from animals is a separate job.",
        icon="vampirism:blood_sieve",
        x=-4.5,
        y=3.5,
        shape="gear",
        optional=True,
        tasks=[
            nt(32, "vampirism:blood_sieve", title="Bring a Blood Sieve"),
            nt(33, "vampirism:blood_container", title="Bring an Input Blood Container"),
            nt(34, "vampirism:blood_container", title="Bring an Output Blood Container"),
            nt(56, "vampirism:blood_bottle", title="Bring a Processed Blood Bottle"),
            nc(35, "I bottled processed blood from the Sieve output; the item task cannot prove its origin"),
        ],
        rewards=[
            item_reward(4, 0x31, "numismatics:sprocket"),
            nr(6, "minecraft:bucket", 2),
            nr(7, "minecraft:glass_bottle", 16),
        ],
        dependencies=[b_foundry],
    )
    transit = ch.add(
        13,
        title="Sunproof Transit",
        subtitle="Specialty · Daytime survival",
        description="Plan a shaded daytime route to a refuge you can reach. Hold your Umbrella in your main hand to block vampire sun damage, and remember that switching to another item leaves you exposed. Travel the route and confirm the journey yourself. Shelter and ordinary precautions still matter along the way.",
        icon="vampirism:umbrella",
        x=-1.5,
        y=4.5,
        shape="diamond",
        optional=True,
        tasks=[
            nt(36, "vampirism:umbrella", title="Carry a Sunproof Umbrella"),
            nc(37, "I completed the shaded route between refuges"),
        ],
        rewards=[
            item_reward(4, 0x2D, "numismatics:sprocket"),
            nr(8, "minecraft:black_wool", 3),
            nr(9, "vampirism:vampire_orchid", 2),
            nr(26, "minecraft:stick", 2),
        ],
        dependencies=[b_foundry],
    )
    stores = ch.add(
        12,
        title="Remedy Counter",
        subtitle="Specialty · Visitor remedies",
        description="Keep a Remedy Counter for ordinary visitors. In an Alchemist Cauldron, combine 1,000 mB of strong Healing potion with an Amethyst Shard for Greater Healing, or 1,000 mB of long Invisibility potion with a Shriving Stone for Invisibility Elixir. Bottle the remedies in 250 mB portions. Bring one of each and confirm that the counter is stocked and labelled. These are visitor remedies; keep the House's blood supply and daytime protection services available separately.",
        icon="irons_spellbooks:alchemist_cauldron",
        x=1.5,
        y=4.5,
        shape="diamond",
        optional=True,
        tasks=[
            nt(38, "irons_spellbooks:alchemist_cauldron", title="Bring an Alchemist Cauldron"),
            nt(39, "irons_spellbooks:greater_healing_potion", title="Bring a Greater Healing Remedy"),
            nt(40, "irons_spellbooks:invisibility_elixir", title="Bring an Invisibility Remedy"),
            nc(41, "I labelled the visitor remedies and their faction limits"),
        ],
        rewards=[
            item_reward(4, 0x29, "numismatics:sprocket"),
            nr(10, "minecraft:glass_bottle", 16),
            nr(11, "minecraft:amethyst_shard", 8),
            nr(12, "irons_spellbooks:shriving_stone", 4),
        ],
        dependencies=[b_manor],
    )
    palette = ch.add(
        6,
        title="Open House",
        subtitle="Specialty · Public wayfinding",
        description="Publish a signed visitor guide, mark the public entrance, and show where private claimed areas begin. Test access to one designated public area only; this attestation does not grant unrestricted access to the claim.",
        icon="minecraft:written_book",
        x=4.5,
        y=3.5,
        shape="diamond",
        optional=True,
        tasks=[
            nt(42, "minecraft:written_book", title="Bring a Signed Visitor Guide"),
            nt(43, "minecraft:oak_sign", title="Bring an Entrance Sign"),
            nc(44, "I tested the public entrance and private boundary"),
        ],
        rewards=[
            item_reward(4, 0x1A, "numismatics:sprocket"),
            nr(13, "minecraft:paper", 8),
        ],
        dependencies=[b_manor],
    )
    reserve = ch.add(
        5,
        title="Crimson Reserve",
        subtitle="Specialty · Blood supply",
        description="Maintain an emergency reserve: carry eight Blood Bottles and two Blood Containers, then confirm that the reserve is filled and reachable. A Blood Container holds 12,600 mB, but the item tasks cannot read fluid level; the reward adds separate containers, feed, leads, and limited fencing without claiming automated storage.",
        icon="vampirism:blood_container",
        x=7.5,
        y=2,
        shape="diamond",
        optional=True,
        tasks=[
            nt(45, "vampirism:blood_bottle", 8, "Carry eight Blood Bottles"),
            nt(46, "vampirism:blood_container", 2, "Carry two Blood Containers"),
            nc(47, "I checked that the reserve is filled and reachable"),
        ],
        rewards=[
            item_reward(4, 0x25, "numismatics:sprocket"),
            nr(14, "vampirism:blood_container"),
            nr(15, "vampirism:blood_container"),
            nr(16, "minecraft:wheat", 32),
            nr(17, "minecraft:carrot", 16),
            nr(18, "minecraft:potato", 16),
            nr(19, "minecraft:lead", 4),
            nr(20, "minecraft:oak_fence", 8),
            nr(21, "minecraft:oak_fence_gate", 2),
        ],
        dependencies=[b_vault],
    )
    script = ch.add(
        4,
        title="Scarlet Script",
        subtitle="Specialty · Blood-mage workshop",
        description="Complete a blood-mage workshop with an Arcane Anvil, Scroll Forge, and the Cultist equipment set. The reward offers a Blood Staff with paper and controlled Rare and Epic Ink for the next script; it does not return the armour or hand out unrelated fixed scrolls.",
        icon="irons_spellbooks:blood_staff",
        x=10.5,
        y=0,
        shape="diamond",
        optional=True,
        tasks=[
            nt(48, "irons_spellbooks:arcane_anvil", title="Bring an Arcane Anvil"),
            nt(49, "irons_spellbooks:scroll_forge", title="Bring a Scroll Forge"),
            nt(50, "irons_spellbooks:cultist_helmet", title="Bring the Cultist Hood"),
            nt(51, "irons_spellbooks:cultist_chestplate", title="Bring the Cultist Chestplate"),
            nt(52, "irons_spellbooks:cultist_leggings", title="Bring the Cultist Leggings"),
            nt(53, "irons_spellbooks:cultist_boots", title="Bring the Cultist Boots"),
        ],
        rewards=[
            item_reward(4, 0x70, "numismatics:sprocket", 2),
            nr(22, "irons_spellbooks:blood_staff"),
            nr(23, "minecraft:paper", 16),
            nr(24, "irons_spellbooks:rare_ink", 2),
            nr(25, "irons_spellbooks:epic_ink"),
        ],
        dependencies=[b_vault],
    )

    return ch


MINUTE = 60
BUILDING_MARKET_COOLDOWN = 3 * MINUTE
PROGRESSION_MARKET_COOLDOWN = 5 * MINUTE


def build_market(group: str) -> Chapter:
    """Build the 19-node Market catalogue.

    The four hand-authored crates keep their live quest/task IDs. Existing
    reward IDs remain attached to the same item identity; new task and reward
    locals use the reserved 0x4000/0x5000 Chapter 5 ranges. Every paid stock
    entry is a shared FTB Team entitlement and is excluded from claim-all so
    a payment never silently duplicates across teammates or floods inventory.
    """
    ch = Chapter(
        5,
        "ch05_market_services",
        "05 · Market Services",
        group,
        "numismatics:sprocket",
        0,
        default_hide_dependency_lines=True,
        # One panorama frames the whole chapter; keep the native 16:9 aspect.
        images=[{
            "alpha": 130, "height": 22.5, "width": 40,
            "image": "poiesis:textures/questpics/vvh/free_company_mediator_panorama.png",
            "order": -40, "rotation": 0.0, "x": 0, "y": 2.25,
        }],
    )

    def shared_reward(local: int, item: str, count: int = 1, *, legacy: int | None = None) -> dict[str, Any]:
        reward = item_reward(5, legacy if legacy is not None else 0x5000 + local, item, count, team=True)
        reward["auto"] = "disabled"
        reward["exclude_from_claim_all"] = True
        return reward

    def new_reward(local: int, item: str, count: int = 1) -> dict[str, Any]:
        return shared_reward(local, item, count)

    def new_task(local: int, item: str, count: int, title: str) -> dict[str, Any]:
        if not 0x0000 <= local <= 0x0FFF:
            raise ValueError(f"Chapter 5 task local outside 0x4000-0x4FFF: {local:#x}")
        return item_task(5, 0x4000 + local, item, count, title, consume=True)

    opener = ch.add(
        1,
        title="Read the Board",
        subtitle="Catalogue guide · Shared team stock",
        description="The board has two departments: building palettes on the left, progression and utility kits on the right. A purchase consumes the exact posted price, creates one shared set of team reward entitlements, and never returns currency. Claim each reward manually so a large order does not flood an occupied inventory. Building orders restock after 180 seconds; progression and utility orders restock after 300 seconds. The Rumour Ledger remains the only weekly currency source.",
        icon="numismatics:banking_guide",
        x=0,
        y=-7,
        shape="hexagon",
        size=1.5,
        tasks=[check_task(5, 1, "I understand prices, cooldowns, and shared team claims")],
        dependencies=[qid(2, 7)],
    )

    def purchase(index: int, *, title: str, subtitle: str, description: str, icon: str, x: float, y: float, price_item: str, price_count: int, task_local: int | None, legacy_task: int | None, rewards: list[dict[str, Any]], cooldown: int, shape: str) -> str:
        coin = {"numismatics:bevel": "Bevel", "numismatics:sprocket": "Sprocket", "numismatics:cog": "Cog"}[price_item]
        label = f"Submit {price_count} {coin}{'' if price_count == 1 else 's'}"
        task = item_task(5, legacy_task, price_item, price_count, label, consume=True) if legacy_task is not None else new_task(task_local or 0, price_item, price_count, label)
        return ch.add(index, title=title, subtitle=subtitle, description=description, icon=icon, x=x, y=y,
                      shape=shape, size=1.45 if index == 7 else 1.0, optional=True, can_repeat=True,
                      cooldown=cooldown, tasks=[task], rewards=rewards, dependencies=[opener])

    # Ten left-hand building palettes. The four crate indices 0x11-0x14 and
    # their task locals 0x21-0x24 are preserved exactly.
    purchase(3, title="Works Kit", subtitle="1 Sprocket · 180 s",
        description="Submit and consume 1 Sprocket for one shared team order: 8 stacks of raw Stone, 4 stacks of Oak Logs, 2 stacks of Sand, 16 Glass, and 8 Lanterns. Claim each entry manually. Building stock for repairs, shelters, and civic rooms; no machines, Diamonds, or combat gear. Restocks after 180 seconds.",
        icon="minecraft:stone", x=-10, y=-2.5, price_item="numismatics:sprocket", price_count=1,
        task_local=None, legacy_task=3, cooldown=BUILDING_MARKET_COOLDOWN, shape="square",
        rewards=[*[shared_reward(0, "minecraft:stone", 64, legacy=0x49 + i) for i in range(8)],
                 *[shared_reward(1 + i, "minecraft:oak_log", 64) for i in range(4)],
                 shared_reward(5, "minecraft:sand", 64), shared_reward(6, "minecraft:sand", 64),
                 shared_reward(0, "minecraft:glass", 16, legacy=0x55), shared_reward(0, "minecraft:lantern", 8, legacy=0x56)])
    purchase(0x0F, title="Village Timber Kit", subtitle="1 Sprocket · 180 s",
        description="Submit and consume 1 Sprocket for one shared team village palette: 4 stacks of raw Stone, 4 stacks of Spruce Logs, 2 stacks of Terracotta, 2 stacks of Sand, Glass, Lanterns, and 2 Campfires for homes, inns, and workshops. Claim each stack manually. Restocks after 180 seconds; this is a house-and-inn palette, not a fortress or machine kit.",
        icon="minecraft:spruce_log", x=-5, y=-2.5, price_item="numismatics:sprocket", price_count=1,
        task_local=None, legacy_task=0x0C, cooldown=BUILDING_MARKET_COOLDOWN, shape="square",
        rewards=[*[new_reward(0xE0 + i, "minecraft:stone", 64) for i in range(4)],
                 *[new_reward(0xE4 + i, "minecraft:spruce_log", 64) for i in range(4)],
                 shared_reward(0, "minecraft:terracotta", 64, legacy=0x60), shared_reward(0, "minecraft:terracotta", 64, legacy=0x61),
                 *[new_reward(0xE8 + i, "minecraft:sand", 64) for i in range(2)],
                 shared_reward(0, "minecraft:glass", 32, legacy=0x62), shared_reward(0, "minecraft:lantern", 8, legacy=0x63), shared_reward(0, "minecraft:campfire", 2, legacy=0x64)])
    purchase(0x16, title="Fortress Kit", subtitle="2 Sprockets · 180 s",
        description="Submit and consume 2 Sprockets for one shared team fortress palette: 6 stacks of raw Stone, 4 stacks of Deepslate, 2 stacks of Dark Oak Logs, 32 Iron Bars, 16 Chains, and 16 Lanterns. Claim entries manually. Restocks after 180 seconds; it supplies structure and lighting, never armour, weapons, or machinery.",
        icon="minecraft:deepslate", x=-10, y=1, price_item="numismatics:sprocket", price_count=2,
        task_local=0x10, legacy_task=None, cooldown=BUILDING_MARKET_COOLDOWN, shape="square",
        rewards=[*[shared_reward(0x10 + i, "minecraft:stone", 64) for i in range(6)], *[shared_reward(0x16 + i, "minecraft:deepslate", 64) for i in range(4)],
                 *[shared_reward(0x1A + i, "minecraft:dark_oak_log", 64) for i in range(2)], shared_reward(0x1C, "minecraft:iron_bars", 32), shared_reward(0x1D, "minecraft:chain", 16), shared_reward(0x1E, "minecraft:lantern", 16)])
    purchase(0x11, title="Celestial Spire Crate", subtitle="2 Sprockets · 180 s",
        description="Submit and consume 2 Sprockets for one shared team dark observatory palette: Deepslate Tiles, Dark Oak Planks, Tinted Glass, Nether Brick Pillars, Wisewood Shelving, Amethyst Clusters, Bookshelves, and Sea Lanterns. Claim each entry manually. Restocks after 180 seconds. Arcane architecture only; no Enchanting Table or spell workstation.",
        icon="minecraft:deepslate_tiles", x=-5, y=1, price_item="numismatics:sprocket", price_count=2,
        task_local=None, legacy_task=0x21, cooldown=BUILDING_MARKET_COOLDOWN, shape="square",
        rewards=[shared_reward(0, "minecraft:deepslate_tiles", 64, legacy=0x31), shared_reward(0, "minecraft:deepslate_tiles", 64, legacy=0x77), shared_reward(0x40, "minecraft:deepslate_tiles", 64), shared_reward(0x41, "minecraft:deepslate_tiles", 64), shared_reward(0x42, "minecraft:dark_oak_planks", 64, legacy=0x32), shared_reward(0x43, "minecraft:dark_oak_planks", 64), shared_reward(0x44, "minecraft:dark_oak_planks", 64), shared_reward(0x45, "minecraft:dark_oak_planks", 64), shared_reward(0x46, "minecraft:tinted_glass", 64, legacy=0x33), shared_reward(0x47, "minecraft:tinted_glass", 64), shared_reward(0xB1, "minecraft:deepslate_tiles", 64), shared_reward(0xB2, "minecraft:dark_oak_planks", 64), shared_reward(0, "minecraft:amethyst_cluster", 16, legacy=0x34), shared_reward(0, "minecraft:bookshelf", 16, legacy=0x35), shared_reward(0, "minecraft:sea_lantern", 8, legacy=0x36), new_reward(0xDA, "irons_spellbooks:nether_brick_pillar", 16), new_reward(0xDB, "irons_spellbooks:wisewood_bookshelf", 16), new_reward(0xDC, "irons_spellbooks:wisewood_chiseled_bookshelf", 16)])
    purchase(0x12, title="Sanctified Brewery Crate", subtitle="2 Sprockets · 180 s",
        description="Submit and consume 2 Sprockets for one shared team light apothecary palette: Polished Tuff, Whitewood Planks, Frosted Glass, Jars, Faucets, and Lanterns. Claim each entry manually. Restocks after 180 seconds. Decorative service stock only; no progression ingredients or repeated workstations.",
        icon="abyssal_decor:white_wood_planks", x=-10, y=4.5, price_item="numismatics:sprocket", price_count=2,
        task_local=None, legacy_task=0x22, cooldown=BUILDING_MARKET_COOLDOWN, shape="square",
        rewards=[shared_reward(0, "minecraft:polished_tuff", 64, legacy=0x37), shared_reward(0, "minecraft:polished_tuff", 64, legacy=0x78), shared_reward(0x48, "minecraft:polished_tuff", 64), shared_reward(0x49, "minecraft:polished_tuff", 64), shared_reward(0x4A, "abyssal_decor:white_wood_planks", 64, legacy=0x38), shared_reward(0x4B, "abyssal_decor:white_wood_planks", 64), shared_reward(0x4C, "abyssal_decor:white_wood_planks", 64), shared_reward(0x4D, "abyssal_decor:frosted_glass", 64, legacy=0x39), shared_reward(0x4E, "abyssal_decor:frosted_glass", 64), shared_reward(0xB3, "minecraft:polished_tuff", 64), shared_reward(0xB4, "abyssal_decor:white_wood_planks", 64), shared_reward(0xB5, "abyssal_decor:frosted_glass", 64), shared_reward(0, "supplementaries:jar", 16, legacy=0x3A), shared_reward(0, "supplementaries:faucet", 4, legacy=0x3B), shared_reward(0, "minecraft:lantern", 16, legacy=0x3C)])
    purchase(0x13, title="Frontier Watch Crate", subtitle="2 Sprockets · 180 s",
        description="Submit and consume 2 Sprockets for one shared team frontier palette: 3 stacks of raw Stone, Spruce Planks, Scaffolding, Timber Frames, Rope, Way Signs, Torches, and 2 Spyglasses for outposts and watchtowers. Claim each entry manually. Restocks after 180 seconds; route accents remain modest.",
        icon="supplementaries:timber_frame", x=-5, y=4.5, price_item="numismatics:sprocket", price_count=2,
        task_local=None, legacy_task=0x23, cooldown=BUILDING_MARKET_COOLDOWN, shape="square",
        rewards=[shared_reward(0, "minecraft:spruce_planks", 64, legacy=0x3D), shared_reward(0, "minecraft:spruce_planks", 64, legacy=0x79), shared_reward(0x50, "minecraft:spruce_planks", 64), shared_reward(0x51, "minecraft:spruce_planks", 64), shared_reward(0x52, "minecraft:spruce_planks", 64), shared_reward(0xB6, "minecraft:spruce_planks", 64), shared_reward(0, "supplementaries:timber_frame", 64, legacy=0x3E), shared_reward(0x53, "supplementaries:timber_frame", 64), shared_reward(0x54, "supplementaries:timber_frame", 64), shared_reward(0x55, "minecraft:scaffolding", 64), shared_reward(0x56, "minecraft:scaffolding", 64), shared_reward(0, "supplementaries:rope", 32, legacy=0x3F), shared_reward(0, "supplementaries:way_sign_oak", 16, legacy=0x40), shared_reward(0, "minecraft:torch", 32, legacy=0x41), shared_reward(0, "minecraft:spyglass", 1, legacy=0x42), shared_reward(0x50D4, "minecraft:spyglass", 1), *[new_reward(0x100 + i, "minecraft:stone", 64) for i in range(3)]] )
    purchase(0x14, title="Heavy Bastion Crate", subtitle="2 Sprockets · 180 s",
        description="Submit and consume 2 Sprockets for one shared team industrial fortress palette: Create Deco Iron Catwalks, Sheet Metal, Supports, Mesh Fences, Chains, and Iron Bars. Claim each entry manually. Restocks after 180 seconds; structural stock only, never armour, weapons, or advanced machinery.",
        icon="createdeco:industrial_iron_catwalk", x=-10, y=8, price_item="numismatics:sprocket", price_count=2,
        task_local=None, legacy_task=0x24, cooldown=BUILDING_MARKET_COOLDOWN, shape="square",
        rewards=[shared_reward(0, "createdeco:industrial_iron_catwalk", 64, legacy=0x43), shared_reward(0x57, "createdeco:industrial_iron_catwalk", 64), shared_reward(0x58, "createdeco:industrial_iron_catwalk", 64), shared_reward(0xB7, "createdeco:industrial_iron_catwalk", 64), shared_reward(0xBE, "createdeco:industrial_iron_catwalk", 64), shared_reward(0, "createdeco:industrial_iron_sheet_metal", 64, legacy=0x44), shared_reward(0x59, "createdeco:industrial_iron_sheet_metal", 64), shared_reward(0x5A, "createdeco:industrial_iron_sheet_metal", 64), shared_reward(0xB8, "createdeco:industrial_iron_sheet_metal", 64), shared_reward(0xBF, "createdeco:industrial_iron_sheet_metal", 64), shared_reward(0, "createdeco:industrial_iron_support", 32, legacy=0x45), shared_reward(0x5B, "createdeco:industrial_iron_support", 32), shared_reward(0x5C, "createdeco:industrial_iron_mesh_fence", 32, legacy=0x46), shared_reward(0x5D, "createdeco:industrial_iron_mesh_fence", 32), shared_reward(0, "minecraft:chain", 32, legacy=0x47), shared_reward(0, "minecraft:iron_bars", 32, legacy=0x48)])
    purchase(0x17, title="Create Builder's Palette", subtitle="2 Sprockets · 180 s",
        description="Submit and consume 2 Sprockets for one shared team Create architecture order: Stone, Andesite Casing, Copper Casing, Glass, Scaffolding, and façade stock for workshops and windows. Claim each stack manually. Restocks after 180 seconds; Precision Mechanisms, machines, and automation equipment stay out.",
        icon="create:andesite_casing", x=-5, y=8, price_item="numismatics:sprocket", price_count=2,
        task_local=0x11, legacy_task=None, cooldown=BUILDING_MARKET_COOLDOWN, shape="square",
        rewards=[shared_reward(0x20, "minecraft:stone", 64), shared_reward(0x21, "minecraft:stone", 64), shared_reward(0x26, "minecraft:stone", 64), shared_reward(0x27, "minecraft:stone", 64), shared_reward(0x28, "create:andesite_casing", 64), shared_reward(0x29, "create:andesite_casing", 64), shared_reward(0x2A, "create:copper_casing", 64), shared_reward(0x2B, "create:copper_casing", 64), shared_reward(0x2C, "minecraft:glass", 64), shared_reward(0x2D, "minecraft:glass", 64), shared_reward(0x2E, "minecraft:scaffolding", 64), shared_reward(0x2F, "minecraft:scaffolding", 64)])
    purchase(0x15, title="Create Deco Palette", subtitle="2 Sprockets · 180 s",
        description="Submit and consume 2 Sprockets for one shared team Create Deco masonry palette in the Pearl family: Pearl Bricks, Stairs, Walls, Slabs, Industrial Iron Windows, and Industrial Iron Bars. Claim each entry manually. Restocks after 180 seconds; this is decorative masonry, not machinery or progression parts.",
        icon="createdeco:pearl_bricks", x=-10, y=11.5, price_item="numismatics:sprocket", price_count=2,
        task_local=None, legacy_task=0x0D, cooldown=BUILDING_MARKET_COOLDOWN, shape="square",
        rewards=[shared_reward(0, "createdeco:pearl_bricks", 64, legacy=0x70), shared_reward(0x70, "createdeco:pearl_bricks", 64), shared_reward(0x71, "createdeco:pearl_bricks", 64), shared_reward(0x72, "createdeco:pearl_brick_stairs", 64), shared_reward(0x73, "createdeco:pearl_brick_stairs", 64), shared_reward(0x74, "createdeco:pearl_brick_wall", 64), shared_reward(0x75, "createdeco:pearl_brick_wall", 64), shared_reward(0x76, "createdeco:pearl_brick_slab", 64), shared_reward(0x77, "createdeco:pearl_brick_slab", 64), shared_reward(0xB9, "createdeco:pearl_bricks", 64), shared_reward(0xBA, "createdeco:pearl_brick_stairs", 64), shared_reward(0xBB, "createdeco:pearl_brick_wall", 64), shared_reward(0xBC, "createdeco:pearl_brick_slab", 64), shared_reward(0, "createdeco:industrial_iron_window", 16, legacy=0x74), shared_reward(0, "createdeco:industrial_iron_bars", 16, legacy=0x75)])
    purchase(0x18, title="Abyssal Deepworks Palette", subtitle="2 Sprockets · 180 s",
        description="Submit and consume 2 Sprockets for one shared team Abyssal Decor construction order: Blackwood Planks, Black Pearl Bricks, Deepbronze Tiles, Blaze Glass, and Deepbronze Bars. Claim each stack manually. Restocks after 180 seconds; rare ingots and progression alloys are excluded.",
        icon="abyssal_decor:black_pearl_bricks", x=-5, y=11.5, price_item="numismatics:sprocket", price_count=2,
        task_local=0x12, legacy_task=None, cooldown=BUILDING_MARKET_COOLDOWN, shape="square",
        rewards=[shared_reward(0x30, "abyssal_decor:blackwood_planks", 64), shared_reward(0x31, "abyssal_decor:blackwood_planks", 64), shared_reward(0x36, "abyssal_decor:blackwood_planks", 64), shared_reward(0x37, "abyssal_decor:black_pearl_bricks", 64), shared_reward(0x38, "abyssal_decor:black_pearl_bricks", 64), shared_reward(0x39, "abyssal_decor:black_pearl_brick_wall", 64), shared_reward(0x3A, "abyssal_decor:deepbronze_tiles", 64), shared_reward(0x3B, "abyssal_decor:deepbronze_tiles", 64), shared_reward(0x3C, "abyssal_decor:blaze_glass", 64), shared_reward(0x3D, "abyssal_decor:blaze_glass", 64), shared_reward(0x3E, "abyssal_decor:deepbronze_bars", 32), shared_reward(0x3F, "abyssal_decor:blackwood_stairs", 64), shared_reward(0xBD, "abyssal_decor:blackwood_planks", 64)])

    # Five right-hand progression/utility purchases.
    purchase(2, title="Field Kit", subtitle="1 Bevel · 300 s",
        description="Submit and consume 1 Bevel for one shared team field refill: 16 Cooked Beef, 32 Torches, 4 Leads, and one Shield. Claim each entry manually. Restocks after 300 seconds; expedition convenience, not building stock or permanent combat power.",
        icon="numismatics:bevel", x=6, y=-2.5, price_item="numismatics:bevel", price_count=1, task_local=None, legacy_task=2, cooldown=PROGRESSION_MARKET_COOLDOWN, shape="diamond",
        rewards=[shared_reward(0, "minecraft:cooked_beef", 16, legacy=1), shared_reward(0, "minecraft:torch", 32, legacy=2), shared_reward(0, "minecraft:lead", 4, legacy=3), shared_reward(0, "minecraft:shield", legacy=0x76)])
    purchase(5, title="Create Starter Kit", subtitle="2 Sprockets · 300 s",
        description="Submit and consume 2 Sprockets for one shared team early-Create starter: Andesite Alloy, Shafts, Cogwheels, Large Cogwheels, Belt Connectors, a Wrench, and Copper. Claim entries manually. Restocks after 300 seconds; Precision Mechanisms and a functioning factory stay out.",
        icon="create:shaft", x=10, y=-2.5, price_item="numismatics:sprocket", price_count=2, task_local=None, legacy_task=5, cooldown=PROGRESSION_MARKET_COOLDOWN, shape="diamond",
        rewards=[shared_reward(0, "create:andesite_alloy", 16, legacy=0x0C), shared_reward(0, "create:shaft", 8, legacy=0x0D), shared_reward(0, "create:cogwheel", 8, legacy=0x0E), shared_reward(0, "create:large_cogwheel", 4, legacy=0x0F), shared_reward(0, "create:belt_connector", 4, legacy=0x65), shared_reward(0, "create:wrench", legacy=0x66), shared_reward(0, "minecraft:copper_ingot", 16, legacy=0x67)])
    purchase(4, title="Iron's Spells Starter Kit", subtitle="1 Sprocket · 300 s",
        description="Submit and consume 1 Sprocket for one shared team first-steps magic kit: Arcane Essence, Blank Runes, Common Ink, and Uncommon Ink. Claim each entry manually. Restocks after 300 seconds; no advanced armour, spellbook, random scrolls, or high-tier loadout.",
        icon="irons_spellbooks:arcane_essence", x=6, y=1, price_item="numismatics:sprocket", price_count=1, task_local=None, legacy_task=4, cooldown=PROGRESSION_MARKET_COOLDOWN, shape="diamond",
        rewards=[shared_reward(0, "irons_spellbooks:arcane_essence", 8, legacy=8), shared_reward(0, "irons_spellbooks:blank_rune", 2, legacy=9), shared_reward(0, "irons_spellbooks:common_ink", 8, legacy=0x0A), shared_reward(0, "irons_spellbooks:uncommon_ink", 4, legacy=0x0B)])
    purchase(9, title="Recovery Crate", subtitle="1 Sprocket · 300 s",
        description="Submit and consume 1 Sprocket for one shared team recovery cache: cooked food, Torches, 16 Honey Bottles, and 4 Golden Apples. Claim entries manually after a failed expedition. Restocks after 300 seconds; no permanent combat upgrades, beds, shields, or mounts.",
        icon="minecraft:golden_apple", x=10, y=1, price_item="numismatics:sprocket", price_count=1, task_local=None, legacy_task=9, cooldown=PROGRESSION_MARKET_COOLDOWN, shape="diamond",
        rewards=[shared_reward(0x90, "minecraft:cooked_beef", 16), shared_reward(0x91, "minecraft:torch", 32), shared_reward(0, "minecraft:honey_bottle", 16, legacy=0x16), shared_reward(0, "minecraft:golden_apple", 4, legacy=0x17)])
    purchase(10, title="Transit Crate", subtitle="2 Sprockets · 300 s",
        description="Submit and consume 2 Sprockets for one shared team route kit: 2 Saddles, 16 Leads, 32 Firework Rockets, 4 Oak Boats, and 4 Compasses. Claim each entry manually; claim every saddle and boat separately. Restocks after 300 seconds; ordinary transport only—no Elytra, permanent flight, or advanced teleportation.",
        icon="minecraft:saddle", x=6, y=4.5, price_item="numismatics:sprocket", price_count=2, task_local=None, legacy_task=10, cooldown=PROGRESSION_MARKET_COOLDOWN, shape="diamond",
        rewards=[shared_reward(0, "minecraft:saddle", 1, legacy=0x18), shared_reward(0xA0, "minecraft:saddle", 1), shared_reward(0, "minecraft:lead", 16, legacy=0x19), shared_reward(0, "minecraft:firework_rocket", 32, legacy=0x1A), *[shared_reward(0xA1 + i, "minecraft:oak_boat", 1) for i in range(4)], shared_reward(0, "minecraft:compass", 4, legacy=0x1C)])

    # Central Concord Bond keeps its quest ID but uses a new reserved task
    # local.  Two Sprockets price a deliberately finished roads-and-bridges
    # order: it is larger than one basic palette while remaining below four
    # Works purchases and does not replace specialist kits.
    purchase(7, title="Concord Bond", subtitle="2 Sprockets · 300 s",
        description="Submit and consume 2 Sprockets for one shared team civic roads-and-bridges order: 8 stacks of raw Stone, 4 stacks of Stone Slabs, 2 stacks of Stone Brick Slabs, 4 stacks of Oak Logs, 4 stacks of Scaffolding, 2 stacks of Oak Fences, 16 Chains, and 16 Lanterns. Claim entries manually for one named public road, bridge, or shared-stock project. Restocks after 300 seconds; no Diamonds, alloy, or combat gear.",
        icon="minecraft:stone_slab", x=0, y=-2.5, price_item="numismatics:sprocket", price_count=2, task_local=0x13, legacy_task=None, cooldown=PROGRESSION_MARKET_COOLDOWN, shape="hexagon",
        rewards=[shared_reward(0, "minecraft:stone", 64, legacy=0x10), shared_reward(0, "minecraft:stone", 64, legacy=0x11), shared_reward(0, "minecraft:stone", 64, legacy=0x12), shared_reward(0, "minecraft:stone", 64, legacy=0x69),
                 *[new_reward(0xF0 + i, "minecraft:stone", 64) for i in range(4)],
                 shared_reward(0, "minecraft:oak_log", 64, legacy=0x13), shared_reward(0, "minecraft:oak_log", 64, legacy=0x1D),
                 *[new_reward(0xF4 + i, "minecraft:oak_log", 64) for i in range(2)],
                 shared_reward(0, "minecraft:scaffolding", 64, legacy=0x6A), shared_reward(0, "minecraft:scaffolding", 64, legacy=0x6B),
                 *[new_reward(0xF6 + i, "minecraft:scaffolding", 64) for i in range(2)],
                 *[new_reward(0xF8 + i, "minecraft:stone_slab", 64) for i in range(4)],
                 *[new_reward(0xFC + i, "minecraft:stone_brick_slab", 64) for i in range(2)],
                 *[new_reward(0xFE + i, "minecraft:oak_fence", 64) for i in range(2)],
                 shared_reward(0, "minecraft:chain", 16, legacy=0x6D), shared_reward(0, "minecraft:lantern", 16, legacy=0x6E)])

    ch.add(6, title="Rumour Ledger", subtitle="Fallback · 1 team Bevel · 604800 s",
        description="Submit and consume one Written Book naming a findable place, a real problem, and the person who will review the result. This is the board's sole currency faucet: one shared team Bevel entitlement every 604800 seconds. Claim it manually; purchases restock in minutes but never produce currency.",
        icon="minecraft:written_book", x=0, y=2, shape="diamond", optional=True, can_repeat=True, cooldown=WEEK,
        tasks=[item_task(5, 7, "minecraft:written_book", title="Submit one written field ledger", consume=True), check_task(5, 11, "I named the place, problem, and reviewer")],
        rewards=[shared_reward(0, "numismatics:bevel", legacy=0x1E)], dependencies=[opener])
    ch.add(8, title="Know the Coins", subtitle="Spur · Bevel · Sprocket · Cog",
        description="Numismatics values are Spur 1, Bevel 8, Sprocket 16, and Cog 64. Purchases consume their displayed price and create one shared team reward set with manual claims: 180-second building restocks and 300-second progression or civic restocks. Only the Rumour Ledger is weekly.",
        icon="numismatics:cog", x=0, y=5.5, shape="diamond", size=1.15, optional=True,
        tasks=[check_task(5, 8, "I understand the coin denominations")], dependencies=[opener])
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
    apply_reviewed_overrides(chapters)
    return chapters, groups


def apply_reviewed_overrides(chapters: list[Chapter]) -> None:
    """Apply reviewed edits while guarding their stable-ID/schema boundary."""
    for commit in REVIEWED_SOURCE_COMMITS:
        if not isinstance(commit, str) or not re.fullmatch(r"[0-9a-f]{7,40}", commit):
            raise ValueError(f"invalid reviewed source commit marker {commit!r}")
    quests_by_id = {quest["id"]: quest for chapter in chapters for quest in chapter.quests}
    original_global_ids = {
        str(value.get("id"))
        for chapter in chapters
        for quest in chapter.quests
        for value in (
            [{"id": chapter.id}, quest, *quest.get("tasks", []), *quest.get("rewards", [])]
        )
        if isinstance(value, dict) and value.get("id") is not None
    }
    for quest_id, fields in ACTIVE_REVIEWED_QUEST_OVERRIDES.items():
        if quest_id not in quests_by_id:
            raise ValueError(f"reviewed override targets unknown quest {quest_id}")
        if not isinstance(fields, dict) or set(fields) - REVIEWED_OVERRIDE_FIELDS:
            unknown = sorted(set(fields) - REVIEWED_OVERRIDE_FIELDS) if isinstance(fields, dict) else ["<non-object>"]
            raise ValueError(f"reviewed override for {quest_id} has unsupported fields {unknown}")
        quest = quests_by_id[quest_id]
        for family in ("tasks", "rewards"):
            if family not in fields:
                continue
            replacement = fields[family]
            original = quest.get(family, [])
            if not isinstance(replacement, list) or not all(isinstance(item, dict) for item in replacement):
                raise ValueError(f"reviewed override for {quest_id}.{family} must be a list of compounds")
            original_ids = [item.get("id") for item in original if isinstance(item, dict)]
            replacement_ids = [item.get("id") for item in replacement]
            family_prefix = T_PREFIX if family == "tasks" else R_PREFIX
            quest_number = int(quest_id, 16)
            chapter_number = (quest_number - Q_PREFIX) // 0x100000
            expected_family_start = family_prefix + chapter_number * 0x100000
            valid_ids = all(
                isinstance(item_id, str)
                and HEX_ID.fullmatch(item_id)
                and expected_family_start <= int(item_id, 16) < expected_family_start + 0x100000
                for item_id in replacement_ids
            )
            if (
                len(set(replacement_ids)) != len(replacement_ids)
                or not valid_ids
                or bool(
                    (set(replacement_ids) - set(original_ids))
                    & (original_global_ids - set(original_ids))
                )
            ):
                raise ValueError(
                    f"reviewed override for {quest_id}.{family} contains invalid or duplicate stable IDs: "
                    f"{replacement_ids!r}; expected {family_prefix:016X} chapter range"
                )
        if "description" in fields and (
            not isinstance(fields["description"], list)
            or not all(isinstance(value, str) for value in fields["description"])
        ):
            raise ValueError(f"reviewed override for {quest_id}.description must be a list of strings")
        for field_name in ("title", "subtitle"):
            if field_name in fields and not isinstance(fields[field_name], str):
                raise ValueError(f"reviewed override for {quest_id}.{field_name} must be a string")
        if "icon" in fields and (
            not isinstance(fields["icon"], dict) or not isinstance(fields["icon"].get("id"), str)
        ):
            raise ValueError(f"reviewed override for {quest_id}.icon must contain a string id")
        if "x" in fields and (
            isinstance(fields["x"], bool) or not isinstance(fields["x"], (int, float))
        ):
            raise ValueError(f"reviewed override for {quest_id}.x must be numeric")
        if "min_required_dependencies" in fields:
            minimum = fields["min_required_dependencies"]
            dependencies = quest.get("dependencies", [])
            if (
                isinstance(minimum, bool)
                or not isinstance(minimum, int)
                or minimum < 0
                or not isinstance(dependencies, list)
                or minimum > len(dependencies)
            ):
                raise ValueError(
                    f"reviewed override for {quest_id}.min_required_dependencies={minimum!r} "
                    f"is invalid for {len(dependencies) if isinstance(dependencies, list) else 0} dependencies"
                )
        # These edits were accepted on ``dev`` before the generator caught up.
        # Keep them as an explicit, reviewable source overlay so generation cannot
        # silently discard a committed human correction.  The overlay is keyed by
        # stable quest ID and only replaces fields that were deliberately reviewed.
        quest.update(copy.deepcopy(fields))
    final_ids: list[Any] = []
    for chapter in chapters:
        final_ids.append(chapter.id)
        for quest in chapter.quests:
            final_ids.extend(
                value.get("id")
                for value in ([quest, *quest.get("tasks", []), *quest.get("rewards", [])])
                if isinstance(value, dict) and value.get("id") is not None
            )
    if len(final_ids) != len(set(final_ids)):
        raise ValueError("reviewed quest overlay introduced duplicate chapter, quest, task, or reward IDs")


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


def json_safe(value: Any) -> Any:
    """Keep IDs larger than JavaScript's safe integer range exact in JSON."""
    if isinstance(value, bool):
        return value
    if isinstance(value, int) and abs(value) > 9_007_199_254_740_991:
        return str(value)
    if isinstance(value, dict):
        return {key: json_safe(child) for key, child in value.items()}
    if isinstance(value, list):
        return [json_safe(child) for child in value]
    return value


def normalized_manifest(chapters: list[Chapter], groups: list[dict[str, str]]) -> dict[str, Any]:
    normalized: list[dict[str, Any]] = []
    for chapter in chapters:
        qs: list[dict[str, Any]] = []
        for quest in chapter.quests:
            qs.append({
                "dependencies": quest.get("dependencies", []),
                "description": quest.get("description", []),
                # The manifest exposes the value the renderer should use,
                # while preserving an explicit quest override in the emitted
                # SNBT.  This is intentionally chapter-scoped: Market lines
                # inherit ``true`` and every other chapter inherits ``false``.
                "hide_dependency_lines": quest.get(
                    "hide_dependency_lines", chapter.default_hide_dependency_lines
                ),
                "icon": quest["icon"]["id"],
                "id": quest["id"],
                "min_required_dependencies": quest.get("min_required_dependencies", 0),
                "optional": quest.get("optional", False),
                "repeat_cooldown": quest.get("repeat_cooldown", 0),
                "repeatable": quest.get("can_repeat", False),
                "rewards": json_safe(quest.get("rewards", [])),
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
        "reviewed_source_commits": list(REVIEWED_SOURCE_COMMITS),
        "chapter_count": len(chapters),
        "quest_count": sum(len(ch.quests) for ch in chapters),
        "groups": groups,
        "chapters": normalized,
    }


def output_matches(path: Path, expected: str) -> bool:
    """Compare generated output by value where formatting is non-semantic.

    SNBT and the manifest are hand-editable data formats.  Reordering compound
    keys should not create a false source-drift failure, while malformed data
    must still fail closed and be rewritten by a normal generation run.
    """
    if not path.exists():
        return False
    current = path.read_text(encoding="utf-8-sig")
    if path.suffix == ".snbt":
        try:
            from vvh_validate import Parser

            # Preserve SNBT numeric suffixes while comparing.  FTB's loader
            # distinguishes an int from a long and a float from a double even
            # when Python would consider their values equal (for example
            # ``1`` versus ``1L`` or ``1.0`` versus ``1.0d``).
            return (
                Parser(current, str(path), preserve_numeric_types=True).parse()
                == Parser(expected, str(path), preserve_numeric_types=True).parse()
            )
        except (OSError, ValueError, TypeError):
            return False
    if path.suffix == ".json":
        try:
            return json.loads(current) == json.loads(expected)
        except (json.JSONDecodeError, TypeError):
            return False
    return current == expected


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _parse_source_data(text: str, path: Path) -> Any:
    if path.suffix == ".snbt":
        from vvh_validate import Parser

        return Parser(text, str(path), preserve_numeric_types=True).parse()
    if path.suffix == ".json":
        return json.loads(text)
    return None


def semantic_quest_diffs(root: Path, expected: dict[Path, str]) -> list[str]:
    """Return compact quest-level drift details for ``--check``.

    Formatting changes remain useful path drift, but quest details identify
    the save-relevant changes a reviewer must reconcile: IDs, tasks, rewards,
    dependencies, and coordinates.  This deliberately does not normalize
    away SNBT numeric types.
    """
    lines: list[str] = []
    fields = {
        "tasks": "tasks",
        "rewards": "rewards",
        "dependencies": "dependencies",
        "x": "coordinates",
        "y": "coordinates",
    }
    for path, rendered in expected.items():
        if path.suffix != ".snbt" or "chapters" not in path.parts:
            continue
        if not path.exists():
            lines.append(f"{path.name}: missing generated chapter")
            continue
        try:
            current = _parse_source_data(path.read_text(encoding="utf-8-sig"), path)
            target = _parse_source_data(rendered, path)
        except (OSError, ValueError, TypeError):
            # ``output_matches`` reports malformed data as ordinary drift;
            # avoid hiding it behind a secondary semantic-parser exception.
            continue
        current_q = {q.get("id"): q for q in current.get("quests", []) if isinstance(q, dict)}
        target_q = {q.get("id"): q for q in target.get("quests", []) if isinstance(q, dict)}
        for quest_id in sorted(set(current_q) - set(target_q)):
            lines.append(f"{path.name}: removed quest {quest_id}")
        for quest_id in sorted(set(target_q) - set(current_q)):
            lines.append(f"{path.name}: added quest {quest_id}")
        for quest_id in sorted(set(current_q) & set(target_q)):
            before = current_q[quest_id]
            after = target_q[quest_id]
            changed = {label for key, label in fields.items() if before.get(key) != after.get(key)}
            if changed:
                lines.append(f"{path.name}: quest {quest_id} changed {', '.join(sorted(changed))}")
    return lines


def _ledger_path(root: Path) -> Path:
    return root / HASH_LEDGER_REL


def _ledger_for(
    root: Path,
    expected: dict[Path, str],
    *,
    baseline_receipt: dict[str, Any] | None = None,
) -> dict[str, Any]:
    missing = [path.relative_to(root).as_posix() for path in sorted(expected) if not path.exists()]
    if missing:
        raise RuntimeError("cannot record generated-output hashes; outputs are missing: " + ", ".join(missing))
    ledger: dict[str, Any] = {
        "version": HASH_LEDGER_VERSION,
        "algorithm": "sha256",
        "authoritative_source": "scripts/vvh_campaign_v3.py",
        "managed_outputs": {
            path.relative_to(root).as_posix(): _sha256(path) for path in sorted(expected)
        },
    }
    if baseline_receipt is not None:
        ledger["bootstrap_receipt"] = baseline_receipt
    else:
        # A normal generation refreshes managed-output hashes, but must not
        # erase the provenance proving how the initial ledger was established.
        # Preserve the immutable-baseline receipt across every later write.
        previous = _read_ledger(root)
        if previous is not None and isinstance(previous.get("bootstrap_receipt"), dict):
            ledger["bootstrap_receipt"] = previous["bootstrap_receipt"]
    return ledger


def _baseline_counterpart(root: Path, baseline_root: Path, path: Path) -> Path | None:
    relative = path.relative_to(root)
    candidates = [baseline_root / relative]
    parts = relative.parts
    if parts[:3] == ("config", "ftbquests", "quests"):
        candidates.append(baseline_root / "quests" / Path(*parts[3:]))
        if baseline_root.name.lower() == "quests":
            candidates.append(baseline_root / Path(*parts[3:]))
    if parts[:2] == ("docs", "vvh"):
        candidates.append(baseline_root / "vvh" / Path(*parts[2:]))
        if baseline_root.name.lower() == "vvh":
            candidates.append(baseline_root / Path(*parts[2:]))
    return next((candidate for candidate in candidates if candidate.exists()), None)


def _verify_baseline_fixture(
    root: Path,
    expected: dict[Path, str],
    baseline_root: Path,
) -> tuple[list[str], dict[str, str]]:
    """Verify live files against the immutable pre-edit snapshot.

    A bootstrap with a baseline fixture intentionally does not require the
    redesigned source output to equal the old live files.  It proves that the
    files about to be guarded are the reconciled live baseline, then records
    their current hashes so a subsequent staged generation can proceed.
    """
    errors: list[str] = []
    fixture_hashes: dict[str, str] = {}
    for path in sorted(expected):
        counterpart = _baseline_counterpart(root, baseline_root, path)
        rel = path.relative_to(root).as_posix()
        if counterpart is None:
            errors.append(f"baseline fixture is missing {rel}")
            continue
        if not path.exists():
            errors.append(f"live output is missing while bootstrapping {rel}")
            continue
        baseline_text = counterpart.read_text(encoding="utf-8-sig")
        fixture_hash = _sha256(counterpart)
        fixture_hashes[rel] = fixture_hash
        # Bootstrap is the one point where we can prove that no unrecorded
        # edit slipped in before the first ledger existed.  Require bytes to
        # match the immutable fixture, then retain the semantic check for a
        # clearer failure if a fixture was malformed.
        if _sha256(path) != fixture_hash:
            errors.append(f"live output bytes differ from immutable baseline {rel}")
        elif not output_matches(path, baseline_text):
            errors.append(f"live output does not semantically match reconciled baseline {rel}")
    return errors, fixture_hashes


def _read_ledger(root: Path) -> dict[str, Any] | None:
    path = _ledger_path(root)
    if not path.exists():
        return None
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise RuntimeError(f"cannot read generated-output hash ledger {path}: {exc}") from exc
    if data.get("version") != HASH_LEDGER_VERSION or data.get("algorithm") != "sha256":
        raise RuntimeError(f"unsupported generated-output hash ledger format in {path}")
    entries = data.get("managed_outputs")
    if not isinstance(entries, dict) or not all(isinstance(k, str) and isinstance(v, str) for k, v in entries.items()):
        raise RuntimeError(f"invalid managed_outputs in generated-output hash ledger {path}")
    return data


def _ledger_drift(root: Path, expected: dict[Path, str], ledger: dict[str, Any]) -> list[str]:
    entries = ledger["managed_outputs"]
    expected_rel = {path.relative_to(root).as_posix() for path in expected}
    errors: list[str] = []
    for path in sorted(expected):
        rel = path.relative_to(root).as_posix()
        recorded = entries.get(rel)
        if recorded is None:
            if path.exists():
                errors.append(f"untracked managed output {rel}; bootstrap/reconcile before writing")
            continue
        if not path.exists():
            errors.append(f"managed output disappeared since last build: {rel}")
        elif _sha256(path) != recorded:
            errors.append(f"external edit detected in {rel} (ledger hash {recorded}, current {_sha256(path)})")
    for rel in sorted(set(entries) - expected_rel):
        path = root / Path(rel)
        if path.exists():
            errors.append(f"ledger tracks output no longer emitted by source: {rel}")
    return errors


def _write_ledger_atomic(root: Path, ledger: dict[str, Any]) -> None:
    path = _ledger_path(root)
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, temp_name = tempfile.mkstemp(prefix=".vvh-generated-output-", suffix=".tmp", dir=path.parent)
    try:
        with os.fdopen(fd, "w", encoding="utf-8", newline="\n") as handle:
            json.dump(ledger, handle, indent=2, ensure_ascii=False, sort_keys=True)
            handle.write("\n")
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temp_name, path)
    finally:
        if os.path.exists(temp_name):
            os.unlink(temp_name)


def _stage_outputs(root: Path, expected: dict[Path, str]) -> Path:
    # Keep asset paths and staged relative paths on the same absolute basis;
    # callers of this helper (including tests) may pass ``Path('.')``.
    root = root.resolve()
    expected = {
        (path if path.is_absolute() else root / path).resolve(): content
        for path, content in expected.items()
    }
    stage = Path(tempfile.mkdtemp(prefix="vvh-campaign-stage-", dir=root))
    try:
        for path, content in expected.items():
            staged = stage / path.relative_to(root)
            staged.parent.mkdir(parents=True, exist_ok=True)
            staged.write_text(content, encoding="utf-8", newline="\n")
            _parse_source_data(content, path)
        # Validate the staged files as a complete FTB Quests emission.  This
        # catches duplicate IDs, dangling dependencies, invalid reward/task
        # compounds, and stack/count errors before any tracked file moves.
        from vvh_campaign_v3_validate import load_catalog_item_ids, validate_emitted_files

        _, catalog_errors, catalog_details = load_catalog_item_ids(root)
        stack_limits = catalog_details.get("stack_limits", {})
        from frontier_campaign import load as load_frontier
        frontier = load_frontier(root)
        if frontier:
            import shutil
            (stage / "docs/frontier/evidence").mkdir(parents=True, exist_ok=True)
            shutil.copy2(root / "docs/frontier/quest-source.json", stage / "docs/frontier/quest-source.json")
            # The Frontier chapter art contract is source data, while the
            # generated images and pack metadata are distribution inputs.  A
            # staged validation must see the same small asset closure that the
            # client will receive; copying the entire resource pack would make
            # the safety check needlessly expensive and obscure ownership.
            from frontier_campaign import load_art_source
            art_source = load_art_source(root)
            if art_source:
                art_source_path = root / "docs/frontier/art-source.json"
                shutil.copy2(art_source_path, stage / "docs/frontier/art-source.json")
                art_pack = root / "global_packs/required_resources/vvh_backgrounds"
                staged_pack = stage / "global_packs/required_resources/vvh_backgrounds"
                if (art_pack / "pack.mcmeta").is_file():
                    staged_pack.mkdir(parents=True, exist_ok=True)
                    shutil.copy2(art_pack / "pack.mcmeta", staged_pack / "pack.mcmeta")
                from frontier_validate import _art_asset_path
                for record in art_source.get("chapters", {}).values():
                    if not isinstance(record, dict):
                        continue
                    asset = _art_asset_path(root, record.get("image"))
                    if asset is None or not asset.is_file():
                        continue
                    target = stage / asset.relative_to(root)
                    target.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copy2(asset, target)
            for evidence in (root / "docs/frontier/evidence").glob("*.json"):
                shutil.copy2(evidence, stage / "docs/frontier/evidence" / evidence.name)
            overrides = json.loads((root / "docs/frontier/evidence/survival-paths.json").read_text())["pack_overrides"]
            for relative in overrides:
                target = stage / relative
                target.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(root / relative, target)
            for proof in json.loads((root / "docs/frontier/evidence/pack-provenance.json").read_text()).values():
                target = stage / proof["metadata"]
                target.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(root / proof["metadata"], target)
            graph_runtime = json.loads((root / "docs/frontier/evidence/graph-runtime.json").read_text())
            target = stage / graph_runtime["metadata"]
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(root / graph_runtime["metadata"], target)
        _, errors, warnings = validate_emitted_files(stage, stack_limits)
        if frontier:
            from frontier_validate import audit
            errors.extend(audit(stage)["errors"])
        if catalog_errors:
            errors.extend(f"catalog: {error}" for error in catalog_errors)
        if errors:
            raise RuntimeError(
                "staged semantic validation failed:\n- " + "\n- ".join(errors)
            )
        if warnings:
            print("staged semantic validation warnings:\n- " + "\n- ".join(warnings))
        return stage
    except Exception:
        import shutil

        shutil.rmtree(stage, ignore_errors=True)
        raise


def _replace_staged(root: Path, stage: Path, expected: dict[Path, str], ledger: dict[str, Any]) -> list[str]:
    # Re-check immediately before the first replacement so an edit made after
    # preflight cannot be silently lost.  No file is touched on failure.
    drift = _ledger_drift(root, expected, ledger)
    if drift:
        raise RuntimeError("\n".join(["refusing to overwrite unexpected live edits:", *[f"- {line}" for line in drift]]))
    changed: list[str] = []
    for path, content in expected.items():
        if output_matches(path, content):
            continue
        staged = stage / path.relative_to(root)
        path.parent.mkdir(parents=True, exist_ok=True)
        os.replace(staged, path)
        changed.append(path.relative_to(root).as_posix())
    return changed


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
    from frontier_campaign import compose
    return compose(root, result, snbt)


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate the authoritative five-chapter VvH campaign")
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--check", action="store_true", help="Report drift without writing")
    parser.add_argument(
        "--bootstrap-ledger",
        action="store_true",
        help="Record hashes only after existing live outputs match this source (or --baseline-root); never rewrites outputs",
    )
    parser.add_argument(
        "--baseline-root",
        type=Path,
        help="Immutable pre-edit snapshot used with --bootstrap-ledger to verify reconciled live outputs",
    )
    parser.add_argument("--prune-retired", action="store_true", help="Delete only explicitly named retired chapter files")
    args = parser.parse_args()
    if args.check and args.bootstrap_ledger:
        parser.error("--check and --bootstrap-ledger cannot be combined")
    root = args.root.resolve()
    expected = outputs(root)
    chapters_dir = root / "config/ftbquests/quests/chapters"
    expected_chapter_paths = {path for path in expected if path.parent == chapters_dir}
    stale: list[str] = []
    for path, content in expected.items():
        if not output_matches(path, content):
            stale.append(str(path.relative_to(root)))

    unexpected = sorted(path for path in chapters_dir.glob("*.snbt") if path not in expected_chapter_paths)
    for path in unexpected:
        rel = str(path.relative_to(root))
        stale.append(rel + " (unexpected chapter preserved)")

    if args.check:
        if stale:
            print("campaign source drift:\n- " + "\n- ".join(stale))
            details = semantic_quest_diffs(root, expected)
            if details:
                print("semantic quest differences:\n- " + "\n- ".join(details))
        if not _ledger_path(root).exists():
            print(f"warning: generated-output hash ledger is missing ({HASH_LEDGER_REL}); run --bootstrap-ledger after reconciling live outputs")
            return 2
        else:
            try:
                ledger = _read_ledger(root)
                if ledger:
                    drift = _ledger_drift(root, expected, ledger)
                    if drift:
                        print("hash-ledger drift:\n- " + "\n- ".join(drift))
                        return 2
            except RuntimeError as exc:
                print(f"hash-ledger error: {exc}")
                return 2
        if stale:
            return 1
        chapter_count = len(expected_chapter_paths)
        quest_count = sum(len(chapter.quests) for chapter in build_campaign()[0])
        from frontier_campaign import load as load_frontier
        if frontier := load_frontier(root):
            quest_count += len(frontier['quests'])
        print(f"campaign source is synchronized: {chapter_count} chapters, {quest_count} quests")
        return 0

    if args.bootstrap_ledger:
        baseline_receipt: dict[str, Any] | None = None
        if args.baseline_root:
            baseline_root = args.baseline_root.resolve()
            if not baseline_root.exists():
                print(f"refusing initial hash-ledger bootstrap: baseline root does not exist: {baseline_root}")
                return 2
            baseline_errors, fixture_hashes = _verify_baseline_fixture(root, expected, baseline_root)
            if baseline_errors:
                print("refusing initial hash-ledger bootstrap because live outputs do not match the immutable baseline:")
                print("- " + "\n- ".join(baseline_errors))
                return 2
            baseline_receipt = {
                "mode": "immutable-pre-edit-snapshot",
                "fixture_hashes_sha256": fixture_hashes,
            }
        elif stale:
            print("refusing initial hash-ledger bootstrap because live outputs are not synchronized:")
            print("- " + "\n- ".join(stale))
            details = semantic_quest_diffs(root, expected)
            if details:
                print("semantic quest differences:\n- " + "\n- ".join(details))
            return 2
        ledger = _ledger_for(root, expected, baseline_receipt=baseline_receipt)
        _write_ledger_atomic(root, ledger)
        source = "immutable baseline fixture" if baseline_receipt else "synchronized live outputs"
        print(f"bootstrapped {HASH_LEDGER_REL} from {source}; no generated output was rewritten")
        return 0

    try:
        ledger = _read_ledger(root)
        if ledger is None:
            print(f"refusing generation: {HASH_LEDGER_REL} is missing; reconcile live outputs, then run --bootstrap-ledger", file=__import__("sys").stderr)
            return 2
        ledger_drift = _ledger_drift(root, expected, ledger)
        if ledger_drift:
            print("refusing to overwrite unexpected live edits:\n- " + "\n- ".join(ledger_drift), file=__import__("sys").stderr)
            return 2
        stage = _stage_outputs(root, expected)
        try:
            changed = _replace_staged(root, stage, expected, ledger)
        finally:
            import shutil

            shutil.rmtree(stage, ignore_errors=True)
        _write_ledger_atomic(root, _ledger_for(root, expected))
    except (OSError, RuntimeError, ValueError, TypeError) as exc:
        print(f"generation aborted before completion: {exc}", file=__import__("sys").stderr)
        return 2

    if args.prune_retired:
        # Retired chapter deletion remains an explicit, separate action after
        # a successful staged generation; it never happens during check or
        # initial bootstrap.
        for path in unexpected:
            if path.name in RETIRED_CHAPTER_FILES:
                path.unlink()
                print(f"removed explicitly retired chapter {path.relative_to(root)}")
    action = "updated" if changed else "verified"
    print(f"{action} {len(expected)} authoritative files; unknown chapter files were not deleted")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
