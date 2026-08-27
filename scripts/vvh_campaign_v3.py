#!/usr/bin/env python3
"""Authoritative source for the VvH Concord campaign.

This deliberately replaces the retired campaign generator.  It writes only
the live FTB Quests chapter files, chapter groups, data file, and empty
localization shell; the manifest, ID catalog, layout boards, and validation
reports remain derived by their dedicated scripts.
"""
from __future__ import annotations

import argparse
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


Q_PREFIX = 0x7A11C0DF00000000
T_PREFIX = 0x7A11C1DF00000000
R_PREFIX = 0x7A11C2DF00000000
C_PREFIX = 0x7A11C3DF00000000
G_PREFIX = 0x7A11C4DF00000000


def hid(prefix: int, chapter: int, index: int) -> str:
    return f"{prefix + chapter * 0x100000 + index:016X}"


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
            body = ", ".join(f"{k if re.fullmatch(r'[A-Za-z0-9_]+', k) else esc(k)}: {snbt(v, indent)}" for k, v in value.items())
            return "{ " + body + " }"
        rows = ["{"]
        for key, val in value.items():
            rendered_key = key if re.fullmatch(r"[A-Za-z0-9_]+", key) else esc(key)
            rendered = snbt(val, indent + 1)
            rows.append(f"{pad}\t{rendered_key}: {rendered}")
        rows.append(f"{pad}}}")
        return "\n".join(rows)
    raise TypeError(type(value))


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
        *,
        title: str,
        subtitle: str,
        description: str,
        icon: str,
        x: float,
        y: float,
        tasks: list[dict[str, Any]],
        rewards: list[dict[str, Any]] | None = None,
        dependencies: list[str] | None = None,
        optional: bool = False,
        shape: str = "",
        size: float = 1.0,
        min_deps: int = 0,
        can_repeat: bool = False,
        cooldown: int = 0,
    ) -> str:
        index = len(self.quests) + 1
        qid = hid(Q_PREFIX, self.number, index)
        quest: dict[str, Any] = {
            "dependencies": dependencies or [],
            "description": [description],
            "icon": {"id": icon},
            "id": qid,
        }
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
        return qid


def task(ch: int, idx: int, item: str, count: int = 1, *, consume: bool = False, title: str = "Inspect supplies") -> dict[str, Any]:
    # Inventory tasks prove possession, not observation or travel. Keep their
    # player-facing verbs honest even when source call sites use older wording.
    if title.startswith("Inspect "):
        title = "Have " + title.removeprefix("Inspect ")
    elif title.startswith("Carry "):
        title = "Have " + title.removeprefix("Carry ")
    return {
        "consume_items": consume,
        "id": hid(T_PREFIX, ch, idx),
        "item": {"count": count, "id": item},
        "title": title,
        "type": "item",
    }


def check(ch: int, idx: int, title: str) -> dict[str, Any]:
    clearer = {
        "Read the welcome": "I have read the welcome",
        "Acknowledge claim boundaries": "I understand claim boundaries",
        "Acknowledge rivalry limits": "I agree to stop on request",
        "Acknowledge team progress": "I know who shares progress",
        "Sign after reading every branch": "I accept all three promises",
        "Consider all three callings": "I reviewed all three callings",
        "Confirm your first calling": "I choose this calling",
        "Confirm two specialty records": "I completed two specialties",
        "Read the event board": "I understand the event choices",
        "Read prices and team scope": "I understand prices and team scope",
        "Read the denomination guide": "I understand the coin denominations",
    }
    title = clearer.get(title, title)
    return {"id": hid(T_PREFIX, ch, idx), "title": title, "type": "checkmark"}


def advancement(ch: int, idx: int, aid: str) -> dict[str, Any]:
    return {"advancement": aid, "criterion": "", "id": hid(T_PREFIX, ch, idx), "type": "advancement"}


def reward(ch: int, idx: int, item: str, count: int = 1, *, team: bool = False, title: str | None = None) -> dict[str, Any]:
    result: dict[str, Any] = {
        "id": hid(R_PREFIX, ch, idx),
        "item": {"count": count, "id": item},
        "team_reward": team,
        "type": "item",
    }
    if title:
        result["title"] = title
    return result


def scroll(ch: int, idx: int, spell: str, title: str) -> dict[str, Any]:
    return {
        "id": hid(R_PREFIX, ch, idx),
        "item": {
            "components": {
                "irons_spellbooks:spell_container": {
                    "data": [{"id": spell, "index": 0, "level": 1, "locked": False}],
                    "maxSpells": 1,
                    "mustEquip": False,
                    "spellWheel": False,
                }
            },
            "count": 1,
            "id": "irons_spellbooks:scroll",
        },
        "team_reward": False,
        "title": title,
        "type": "item",
    }


def image(path: str, x: float, y: float, width: float, height: float, *, alpha: int = 24, order: int = -40, rotation: float = 0.0) -> dict[str, Any]:
    return {"alpha": alpha, "height": height, "image": path, "order": order, "rotation": rotation, "width": width, "x": x, "y": y}


def build_campaign() -> tuple[list[Chapter], list[dict[str, str]]]:
    g_charter = hid(G_PREFIX, 1, 0)
    g_callings = hid(G_PREFIX, 2, 0)
    g_services = hid(G_PREFIX, 3, 0)
    groups = [
        {"id": g_charter, "title": "The Charter"},
        {"id": g_callings, "title": "Callings and Craft"},
        {"id": g_services, "title": "Markets and Services"},
    ]
    chapters: list[Chapter] = []

    # 01 — closed-loop onboarding (Preserved 100% intact as ideal).
    c = Chapter(1, "ch01_island_charter", "01 · The Island Charter", g_charter, "minecraft:compass", 0,
        [image("poiesis:textures/questpics/vvh/rivalry_without_ruin.png", 0, 3, 9, 5, alpha=20)])
    welcome = c.add(title="Island Charter", subtitle="Orientation · A persistent world", description="Mara Venn repaired paths for people she never met and crossed out her own name when the work held. The island remembers useful places, then leaves their story to the players who keep them alive.", icon="minecraft:compass", x=0, y=-4, tasks=[check(1, 1, "Read the welcome")], rewards=[reward(1, 1, "minecraft:compass"), reward(1, 2, "minecraft:torch", 16)], shape="hexagon", size=1.5)
    claims = c.add(title="Claim Clearly", subtitle="Required · Land and public access", description="A visible boundary lets neighbors build close without guessing where welcome ends. Public works need a named entrance and an owner so protection never becomes an accidental locked door.", icon="minecraft:filled_map", x=-4, y=-1, tasks=[check(1, 2, "Acknowledge claim boundaries")], dependencies=[welcome], shape="diamond")
    rivalry = c.add(title="Rivalry With Consent", subtitle="Required · Conflict and pranks", description="A feud is only worth continuing when yesterday's work still exists tomorrow. Consent, claim safety, and an immediate stop keep competition memorable instead of exhausting.", icon="minecraft:shield", x=0, y=-1, tasks=[check(1, 3, "Acknowledge rivalry limits")], dependencies=[welcome], shape="octagon")
    teams = c.add(title="Choose Teammates", subtitle="Required · Shared progress", description="An FTB Team joins quest progress to claimed ground and shared rewards. Choose it deliberately; a team is a promise about who may finish, claim, and maintain work together.", icon="minecraft:chest", x=4, y=-1, tasks=[check(1, 4, "Acknowledge team progress")], dependencies=[welcome], shape="gear")
    charter = c.add(title="Sign the Charter", subtitle="Required · Protect · consent · share", description="The charter is deliberately small: protect lasting work, ask before rivalry, and know who shares your progress. Once those promises are settled, every calling remains visible and the island can grow in directions nobody planned.", icon="minecraft:writable_book", x=0, y=2.5, tasks=[check(1, 5, "Sign after reading every branch")], dependencies=[claims, rivalry, teams], rewards=[reward(1, 3, "minecraft:bread", 16)], shape="hexagon", size=1.5)
    chapters.append(c)

    # 02 — symmetrical identity choice with a native any-one gate and onboarding utility.
    c = Chapter(2, "ch02_callings", "02 · Choose a Calling", g_callings, "minecraft:spyglass", 0,
        [image("poiesis:textures/questpics/vvh/season_one_crest.png", 0, 2, 6, 6, alpha=18), image("poiesis:textures/questpics/vvh/free_company_writ.png", 0, 8, 3, 3, alpha=24, order=-39)])
    roads = c.add(title="Three Callings", subtitle="Identity · Night, lantern, or civic", description="Transformation changes a body; a calling changes what someone chooses to maintain. The House, the Order, and the Free Companies each offer a useful place in the world without forbidding curiosity about the others.", icon="minecraft:spyglass", x=0, y=-5, tasks=[check(2, 1, "Consider all three callings")], dependencies=[charter], shape="hexagon", size=1.5)
    night = c.add(title="Join the House", subtitle="Vampire · Nightbound route", description="Nightbound players trade daylight ease for hunger, speed, and a new obligation to prepare safe rooms after sunset. The House values restraint because appetite without hospitality leaves no neighbors worth knowing.", icon="vampirism:vampire_fang", x=-5, y=-2, tasks=[task(2, 2, "vampirism:vampire_fang", title="Carry a vampire fang"), advancement(2, 3, "vampirism:vampire/become_vampire")], dependencies=[roads], rewards=[reward(2, 1, "numismatics:sprocket"), reward(2, 2, "vampirism:vampire_cloak_white_black")], optional=True, shape="circle")
    civic = c.add(title="Join the Commons", subtitle="Free Company · Shared services", description="A civic calling keeps workshops, roads, trade, and shelter outside faction demands. Its authority comes from services anyone can use and the quiet power to refuse a feud.", icon="create:wrench", x=0, y=-2, tasks=[task(2, 4, "create:wrench", title="Carry a Create wrench"), task(2, 5, "numismatics:banking_guide", title="Carry a banking guide"), task(2, 6, "minecraft:shield", title="Carry a shield")], dependencies=[roads], rewards=[reward(2, 3, "numismatics:sprocket"), reward(2, 5, "minecraft:cooked_beef", 32), reward(2, 6, "minecraft:iron_pickaxe"), reward(2, 7, "minecraft:iron_axe"), reward(2, 10, "minecraft:iron_helmet"), reward(2, 11, "minecraft:iron_chestplate"), reward(2, 12, "minecraft:iron_leggings"), reward(2, 13, "minecraft:iron_boots")], optional=True, shape="gear")
    hunter = c.add(title="Join the Order", subtitle="Hunter · Lantern route", description="Hunters accept specialized tools and the responsibility to make danger legible before striking it. The Order's best patrols leave behind wards, remedies, and a route home—not trophies.", icon="vampirism:injection_garlic", x=5, y=-2, tasks=[task(2, 7, "vampirism:injection_garlic", title="Carry a garlic injection"), advancement(2, 8, "vampirism:hunter/become_hunter")], dependencies=[roads], rewards=[reward(2, 8, "numismatics:sprocket"), reward(2, 9, "minecraft:crossbow")], optional=True, shape="circle")
    wayfinder = c.add(title="Wayfinder Guide", subtitle="Optional · Navigation basics", description="The island rewards travelers who mark their turns before nightfall. A compass in hand turns uncharted wilderness into legible paths everyone can share.", icon="explorerscompass:explorerscompass", x=-2.5, y=0.5, tasks=[task(2, 10, "explorerscompass:explorerscompass", title="Carry an Explorer's Compass")], dependencies=[roads], rewards=[reward(2, 14, "minecraft:torch", 16), reward(2, 15, "minecraft:bread", 16)], optional=True, shape="diamond")
    first_coin = c.add(title="First Currency", subtitle="Optional · The island ledger", description="Trade here runs on Numismatics coins: Spurs for pocket change, Bevels for daily labor, and Sprockets for skilled craftsmanship. Keep a guide close to understand posted prices.", icon="numismatics:banking_guide", x=2.5, y=0.5, tasks=[task(2, 11, "numismatics:banking_guide", title="Carry a banking guide")], dependencies=[roads], rewards=[reward(2, 16, "numismatics:bevel")], optional=True, shape="diamond")
    calling_gate = c.add(title="Keep Doors Open", subtitle="Complete any one calling", description="A first calling gives the world a place to start, not a wall around the others. Workshops, archives, and public events remain open so players can understand one another's craft.", icon="minecraft:oak_door", x=0, y=3.5, tasks=[check(2, 9, "Confirm your first calling")], dependencies=[night, civic, hunter], min_deps=1, shape="hexagon", size=1.5)
    chapters.append(c)

    # 03 — Hunter parity spine and specialized branches.
    c = Chapter(3, "ch03_lantern_order", "03 · The Lantern Order", g_callings, "vampirism:hunter_table", 1,
        [image("poiesis:textures/questpics/vvh/lantern_order_holy_panorama.png", -6, 3, 5, 7, alpha=24), image("poiesis:textures/questpics/vvh/holy_public_ward.png", 6, 9, 5, 7, alpha=22, order=-39), image("poiesis:textures/questpics/vvh/holy_school_crest.png", 0, 12, 2.5, 2.5, alpha=30, order=-38)])
    h1 = c.add(title="Salt and Steel", subtitle="Core I · A working field bench", description="Tamsin Rook keeps a bent stake above the research table, not as a victory but as proof that poor preparation follows people home. A complete field bench gives the next patrol time to think before the door opens.", icon="vampirism:hunter_table", x=0, y=-6, tasks=[task(3, 1, "vampirism:hunter_table", title="Inspect a Hunter Table"), task(3, 2, "vampirism:stake", 4, title="Inspect four stakes"), task(3, 3, "vampirism:hunter_axe_normal", title="Inspect a normal Hunter Axe")], dependencies=[hunter], rewards=[reward(3, 1, "numismatics:bevel"), reward(3, 2, "vampirism:hunter_coat_head_normal"), reward(3, 3, "vampirism:hunter_coat_chest_normal"), reward(3, 4, "vampirism:hunter_coat_legs_normal"), reward(3, 5, "vampirism:hunter_coat_feet_normal")], shape="hexagon", size=1.4)
    h2 = c.add(title="Consecrated Work", subtitle="Core II · Remedies and wards", description="A refuge becomes trustworthy when its remedies are stocked before anyone needs them. Holy preparation here means stewardship: clean water, clear labels, and enough reserve for the stranger who arrives after the patrol.", icon="vampirism:alchemical_cauldron", x=0, y=-3, tasks=[task(3, 4, "vampirism:alchemical_cauldron", title="Inspect an Alchemical Cauldron"), task(3, 5, "vampirism:holy_water_bottle_normal", 4, title="Inspect four normal Holy Waters"), task(3, 6, "vampirism:pure_salt", 8, title="Inspect eight Pure Salt")], dependencies=[h1], rewards=[reward(3, 6, "numismatics:bevel"), reward(3, 7, "minecraft:blaze_powder", 16), reward(3, 8, "minecraft:nether_wart", 16), reward(3, 9, "minecraft:iron_ingot", 32), reward(3, 10, "minecraft:gunpowder", 16)], shape="gear")
    h3 = c.add(title="Long Watch", subtitle="Core III · Ranged fieldcraft", description="The Order measures a patrol by how safely it can hand the next watch to someone else. Reliable quarrels and a maintained weapon table turn one veteran's skill into equipment the whole refuge can understand.", icon="vampirism:weapon_table", x=0, y=0, tasks=[task(3, 7, "vampirism:weapon_table", title="Inspect a Hunter Weapon Table"), task(3, 8, "vampirism:basic_crossbow", title="Inspect a basic hunter crossbow"), task(3, 9, "vampirism:crossbow_arrow_vampire_killer", 16, title="Inspect sixteen killer quarrels")], dependencies=[h2], rewards=[reward(3, 11, "numismatics:bevel"), reward(3, 12, "minecraft:arrow", 64), reward(3, 13, "minecraft:feather", 32), reward(3, 14, "minecraft:flint", 32), reward(3, 15, "minecraft:iron_ingot", 32)], shape="gear")
    h4 = c.add(title="Bright Oath", subtitle="Optional mastery · Enhanced fieldcraft", description="Tamsin's last rule is simple: power belongs where it can be accounted for. The enhanced axe hangs beside a ledger of every time it left the refuge and whether it returned clean.", icon="vampirism:hunter_axe_enhanced", x=6, y=0, tasks=[task(3, 10, "vampirism:hunter_axe_enhanced", title="Inspect an enhanced Hunter Axe"), task(3, 11, "vampirism:holy_water_splash_bottle_enhanced", title="Inspect enhanced splash Holy Water")], dependencies=[h3], rewards=[reward(3, 16, "numismatics:cog"), reward(3, 17, "irons_spellbooks:affinity_ring_holy"), reward(3, 18, "minecraft:obsidian", 16), reward(3, 19, "minecraft:diamond", 8)], optional=True, shape="hexagon", size=1.4)
    holy = c.add(title="Mercy Manual", subtitle="Specialty · Holy support magic", description="Sister Aveline's manual begins with triage, not triumph. A spellwright who can heal, recall, and strike with restraint makes every expedition less dependent on whichever veteran happened to log in first.", icon="irons_spellbooks:holy_rune", x=-6, y=-1.5, tasks=[task(3, 12, "irons_spellbooks:inscription_table", title="Inspect an Inscription Table"), task(3, 13, "irons_spellbooks:copper_spell_book", title="Inspect a Flimsy Journal"), task(3, 14, "irons_spellbooks:holy_rune", 4, title="Inspect four Holy Runes"), check(3, 24, "I demonstrated one Holy spell")], dependencies=[h2], rewards=[reward(3, 20, "numismatics:sprocket"), reward(3, 21, "irons_spellbooks:uncommon_ink", 16), reward(3, 22, "irons_spellbooks:rare_ink", 8), scroll(3, 23, "irons_spellbooks:heal", "Scroll of Heal"), scroll(3, 24, "irons_spellbooks:divine_smite", "Scroll of Divine Smite"), scroll(3, 25, "irons_spellbooks:recall", "Scroll of Recall")], optional=True, shape="diamond")
    outpost = c.add(title="Stone Lantern", subtitle="Specialty · Outpost palette", description="A watchpost should be recognizable in bad weather and easy to repair with ordinary stock. This palette establishes the language; the expanded supply can become a tower, refuge, wall, or roadside ward chosen by its builders.", icon="minecraft:stone_bricks", x=-3, y=3, tasks=[task(3, 15, "minecraft:stone_bricks", 64, title="Inspect sixty-four Stone Bricks"), task(3, 16, "minecraft:oak_log", 32, title="Inspect thirty-two Oak Logs"), task(3, 17, "minecraft:iron_bars", 16, title="Inspect sixteen Iron Bars"), task(3, 18, "minecraft:lantern", 8, title="Inspect eight Lanterns")], dependencies=[h2], rewards=[reward(3, 26, "numismatics:sprocket"), reward(3, 27, "minecraft:stone_bricks", 192), reward(3, 28, "minecraft:oak_log", 96), reward(3, 29, "minecraft:iron_bars", 48), reward(3, 30, "minecraft:lantern", 24), reward(3, 31, "minecraft:iron_ingot", 32), reward(3, 32, "minecraft:diamond", 4), reward(3, 33, "minecraft:stonecutter")], optional=True, shape="square")
    alchemy = c.add(title="Pure Defense", subtitle="Specialty · Garlic and salt wards", description="A line of salt across a doorway can give a besieged patrol the five seconds needed to reload. Stocking purified salt and defensive waters ensures the refuge holds even when outnumbered.", icon="vampirism:pure_salt", x=-6, y=3, tasks=[task(3, 34, "vampirism:pure_salt", 8, title="Inspect eight Pure Salt"), task(3, 35, "vampirism:holy_salt", 32, title="Inspect thirty-two Holy Salt"), task(3, 36, "vampirism:injection_garlic", title="Inspect a Garlic Injection")], dependencies=[h2], rewards=[reward(3, 37, "numismatics:sprocket"), reward(3, 38, "vampirism:holy_water_bottle_normal", 16), reward(3, 39, "vampirism:pure_salt", 16)], optional=True, shape="diamond")
    bolts = c.add(title="Hunter Armament", subtitle="Specialty · Specialized ammunition", description="Different threats demand different answers: incendiary spitfire quarrels illuminate shadows, while teleport quarrels reposition a trapped scout to safe ground.", icon="vampirism:crossbow_arrow_spitfire", x=3, y=3, tasks=[task(3, 40, "vampirism:crossbow_arrow_spitfire", 16, title="Inspect sixteen spitfire quarrels"), task(3, 41, "vampirism:crossbow_arrow_teleport", 16, title="Inspect sixteen teleport quarrels")], dependencies=[h3], rewards=[reward(3, 42, "numismatics:sprocket"), reward(3, 43, "minecraft:iron_ingot", 32), reward(3, 44, "minecraft:arrow", 64)], optional=True, shape="gear")
    scout = c.add(title="Field Ledger", subtitle="Specialty · Claim-safe reconnaissance", description="A photograph can warn a neighbor without crossing their boundary or turning rumor into accusation. The ledger gives the Order evidence it can discuss, archive, and eventually admit was wrong.", icon="exposure:camera", x=6, y=3, tasks=[task(3, 19, "explorerscompass:explorerscompass", title="Inspect an Explorer's Compass"), task(3, 20, "exposure:camera", title="Inspect a Camera"), advancement(3, 21, "exposure:adventure/moment_in_time")], dependencies=[h3], rewards=[reward(3, 45, "numismatics:sprocket"), reward(3, 46, "exposure:album"), reward(3, 47, "exposure:color_film", 4), reward(3, 48, "exposure:black_and_white_film", 4), reward(3, 49, "exposure:photograph_frame", 8)], optional=True, shape="gear")
    hgate = c.add(title="Two Lanterns", subtitle="Breadth · Core plus any two specialties", description="No refuge should depend on a single expert. Two practiced specialties are enough to make the Order resilient while leaving room for later players to adopt the third.", icon="minecraft:lantern", x=0, y=6.5, tasks=[check(3, 22, "Confirm two specialty records")], dependencies=[h3, holy, outpost, alchemy, bolts, scout], min_deps=3, shape="diamond")
    hcharter = c.add(title="Lantern Charter", subtitle="Team capstone · Mark a public refuge", description="Tamsin keeps one lodestone unengraved for the refuge that will outlive its founders. Its eventual name should belong to the stranger who finds shelter there when no officer is online.", icon="minecraft:lodestone", x=0, y=9.5, tasks=[task(3, 23, "minecraft:lodestone", title="Inspect the refuge lodestone")], dependencies=[hgate], rewards=[reward(3, 50, "numismatics:cog", team=True), reward(3, 51, "minecraft:stone_bricks", 128, team=True), reward(3, 52, "minecraft:lantern", 32, team=True), reward(3, 53, "minecraft:barrel", 8, team=True)], shape="hexagon", size=1.6)
    chapters.append(c)

    # 04 — Vampire parity spine and specialized branches.
    c = Chapter(4, "ch04_house_night", "04 · The House of Night", g_callings, "vampirism:vampire_fang", 2,
        [image("poiesis:textures/questpics/vvh/house_of_night_blood_panorama.png", -6, 3, 5, 7, alpha=24), image("poiesis:textures/questpics/vvh/blood_ritual_workstation.png", 6, 9, 5, 7, alpha=22, order=-39), image("poiesis:textures/questpics/vvh/blood_school_crest.png", 0, 12, 2.5, 2.5, alpha=30, order=-38)])
    v1 = c.add(title="First Thirst", subtitle="Core I · Stored blood and shelter", description="Ilyas Venn labels every bottle with a donor, a date, or the word unknown. Hunger becomes governable when supply is visible, and a prepared room lets restraint survive the hour when it matters.", icon="vampirism:altar_inspiration", x=0, y=-6, tasks=[task(4, 1, "vampirism:altar_inspiration", title="Inspect an Altar of Inspiration"), task(4, 2, "vampirism:blood_container", title="Inspect a Blood Container"), task(4, 3, "vampirism:blood_bottle", 4, title="Inspect four Blood Bottles")], dependencies=[night], rewards=[reward(4, 1, "numismatics:bevel"), reward(4, 2, "vampirism:armor_of_swiftness_head_normal"), reward(4, 3, "vampirism:armor_of_swiftness_chest_normal"), reward(4, 4, "vampirism:armor_of_swiftness_legs_normal"), reward(4, 5, "vampirism:armor_of_swiftness_feet_normal")], shape="hexagon", size=1.4)
    v2 = c.add(title="Red Measure", subtitle="Core II · Ritual infrastructure", description="An altar is not a shortcut around consequence. Pedestals, storage, and measured ingredients turn inheritance into a repeatable craft that another player can inspect instead of a secret only one veteran understands.", icon="vampirism:altar_infusion", x=0, y=-3, tasks=[task(4, 4, "vampirism:altar_infusion", title="Inspect an Altar of Infusion"), task(4, 5, "vampirism:blood_pedestal", 4, title="Inspect four Blood Pedestals"), task(4, 6, "vampirism:blood_infused_iron_ingot", 2, title="Inspect two Blood-Infused Iron")], dependencies=[v1], rewards=[reward(4, 6, "numismatics:bevel"), reward(4, 7, "minecraft:glass_bottle", 32), reward(4, 8, "minecraft:iron_ingot", 32), reward(4, 9, "minecraft:lead", 8), reward(4, 10, "minecraft:redstone", 32)], shape="gear")
    v3 = c.add(title="Inherited Edge", subtitle="Core III · Controlled armament", description="A weapon with a lineage is still a tool that someone must maintain. The House treats its edge as shared responsibility: enough stock for repair, no mystery about where its strength came from.", icon="vampirism:heart_seeker_normal", x=0, y=0, tasks=[task(4, 7, "vampirism:blood_sieve", title="Inspect a Blood Sieve"), task(4, 8, "vampirism:heart_seeker_normal", title="Inspect a normal Heartseeker"), task(4, 9, "vampirism:blood_infused_iron_ingot", 4, title="Inspect four Blood-Infused Iron")], dependencies=[v2], rewards=[reward(4, 11, "numismatics:bevel"), reward(4, 12, "minecraft:iron_block", 2), reward(4, 13, "minecraft:redstone", 32), reward(4, 14, "minecraft:gold_ingot", 16), reward(4, 15, "minecraft:coal", 32)], shape="gear")
    v4 = c.add(title="Night's Due", subtitle="Optional mastery · Enhanced bloodwork", description="Ilyas calls the enhanced blade a debt made visible. Its scabbard bears the names of three people who may demand it be put away, including one who is not nightbound.", icon="vampirism:heart_seeker_enhanced", x=6, y=0, tasks=[task(4, 10, "vampirism:heart_seeker_enhanced", title="Inspect an enhanced Heartseeker"), task(4, 11, "vampirism:blood_infused_enhanced_iron_ingot", 2, title="Inspect two Enhanced Blood-Infused Iron")], dependencies=[v3], rewards=[reward(4, 16, "numismatics:cog"), reward(4, 17, "irons_spellbooks:affinity_ring_blood"), reward(4, 18, "minecraft:obsidian", 16), reward(4, 19, "minecraft:diamond", 8)], optional=True, shape="hexagon", size=1.4)
    blood = c.add(title="Scarlet Script", subtitle="Specialty · Blood utility magic", description="The House writes blood magic as memory before it writes it as violence. Movement, recovery, and measured siphoning let a spellwright protect a night route without reducing every problem to damage.", icon="irons_spellbooks:blood_rune", x=-6, y=-1.5, tasks=[task(4, 12, "irons_spellbooks:inscription_table", title="Inspect an Inscription Table"), task(4, 13, "irons_spellbooks:copper_spell_book", title="Inspect a Flimsy Journal"), task(4, 14, "irons_spellbooks:blood_rune", 4, title="Inspect four Blood Runes"), check(4, 24, "I demonstrated one Blood spell")], dependencies=[v2], rewards=[reward(4, 20, "numismatics:sprocket"), reward(4, 21, "irons_spellbooks:uncommon_ink", 16), reward(4, 22, "irons_spellbooks:rare_ink", 8), scroll(4, 23, "irons_spellbooks:blood_slash", "Scroll of Blood Slash"), scroll(4, 24, "irons_spellbooks:blood_step", "Scroll of Blood Step"), scroll(4, 25, "irons_spellbooks:ray_of_siphoning", "Scroll of Siphoning")], optional=True, shape="diamond")
    manor = c.add(title="House of Doors", subtitle="Specialty · Manor palette", description="A manor earns its name from the number of people who can find a safe door, not the height of its walls. This palette can become a crypt, guest hall, garden court, or night clinic chosen by its builders.", icon="vampirism:dark_stone_bricks", x=-3, y=3, tasks=[task(4, 15, "vampirism:dark_stone_bricks", 64, title="Inspect sixty-four Dark Stone Bricks"), task(4, 16, "minecraft:dark_oak_log", 32, title="Inspect thirty-two Dark Oak Logs"), task(4, 17, "minecraft:dark_oak_fence", 16, title="Inspect sixteen Dark Oak Fences"), task(4, 18, "minecraft:lantern", 8, title="Inspect eight Lanterns")], dependencies=[v2], rewards=[reward(4, 26, "numismatics:sprocket"), reward(4, 27, "vampirism:dark_stone_bricks", 192), reward(4, 28, "minecraft:dark_oak_log", 96), reward(4, 29, "minecraft:dark_oak_fence", 48), reward(4, 30, "minecraft:lantern", 24), reward(4, 31, "minecraft:iron_ingot", 32), reward(4, 32, "minecraft:diamond", 4), reward(4, 33, "minecraft:stonecutter")], optional=True, shape="square")
    reserve = c.add(title="Crimson Reserve", subtitle="Specialty · Blood collection", description="A well-managed crypt maintains a secure blood reserve so that emerging fledglings never experience the delirium of sudden thirst. Containers and clean glassware keep the cellar orderly.", icon="vampirism:blood_container", x=-6, y=3, tasks=[task(4, 34, "vampirism:blood_bottle", 4, title="Inspect four Blood Bottles"), task(4, 35, "vampirism:blood_container", title="Inspect a Blood Container")], dependencies=[v2], rewards=[reward(4, 36, "numismatics:sprocket"), reward(4, 37, "minecraft:glass_bottle", 32), reward(4, 38, "minecraft:lead", 8)], optional=True, shape="diamond")
    sieve = c.add(title="Sieve Extraction", subtitle="Specialty · Blood metallurgy", description="Blood-infused iron requires careful purification. Passing molten alloy through a specialized sieve separates impurities and tempers the metal for durable arms and armor.", icon="vampirism:blood_sieve", x=3, y=3, tasks=[task(4, 39, "vampirism:blood_sieve", title="Inspect a Blood Sieve"), task(4, 40, "vampirism:blood_infused_iron_ingot", 4, title="Inspect four Blood-Infused Iron")], dependencies=[v3], rewards=[reward(4, 41, "numismatics:sprocket"), reward(4, 42, "minecraft:redstone", 32), reward(4, 43, "minecraft:gold_ingot", 16), reward(4, 44, "minecraft:iron_ingot", 16)], optional=True, shape="gear")
    courier = c.add(title="Moon Courier", subtitle="Specialty · Safe night routes", description="Nessa Vale once delivered a sealed letter three days late because she refused to cross a sleeping farm uninvited. The route took longer; the trust it preserved became a road everyone still used.", icon="vampirism:umbrella", x=6, y=3, tasks=[task(4, 19, "vampirism:umbrella", title="Inspect an Umbrella"), task(4, 20, "explorerscompass:explorerscompass", title="Inspect an Explorer's Compass"), task(4, 21, "exposure:camera", title="Inspect a Camera")], dependencies=[v3], rewards=[reward(4, 45, "numismatics:sprocket"), reward(4, 46, "exposure:album"), reward(4, 47, "exposure:high_sensitivity_color_film", 4), reward(4, 48, "exposure:black_and_white_film", 4), reward(4, 49, "minecraft:firework_rocket", 32)], optional=True, shape="gear")
    vgate = c.add(title="Two Seals", subtitle="Breadth · Core plus any two specialties", description="A house becomes fragile when one person holds every useful secret. Two practiced specialties are enough to share responsibility while leaving a third role open for a later arrival.", icon="vampirism:vampire_cloak_white_black", x=0, y=6.5, tasks=[check(4, 22, "Confirm two specialty records")], dependencies=[v3, blood, manor, reserve, sieve, courier], min_deps=3, shape="diamond")
    vcharter = c.add(title="Night Charter", subtitle="Team capstone · Mark a night refuge", description="Ilyas keeps one lodestone wrapped in a guest's old scarf. It waits for a refuge whose door can be found, whose service can be named, and whose keeper can be questioned when something fails.", icon="minecraft:lodestone", x=0, y=9.5, tasks=[task(4, 23, "minecraft:lodestone", title="Inspect the refuge lodestone")], dependencies=[vgate], rewards=[reward(4, 50, "numismatics:cog", team=True), reward(4, 51, "vampirism:dark_stone_bricks", 128, team=True), reward(4, 52, "minecraft:lantern", 32, team=True), reward(4, 53, "minecraft:barrel", 8, team=True)], shape="hexagon", size=1.6)
    chapters.append(c)

    # 05 — denomination-aware sinks plus a slow hard-task fallback faucet.
    c = Chapter(5, "ch05_market_services", "05 · Market Services", g_services, "numismatics:sprocket", 0,
        [image("poiesis:textures/questpics/vvh/free_company_writ.png", 0, 4, 5, 5, alpha=18)])
    board = c.add(title="Read the Board", subtitle="Weekly services · Team-scoped", description="The board turns quest earnings into choices players can feel in the world. Small purses solve immediate friction; larger denominations fund whole-team projects without pretending every coin is identical pocket change.", icon="numismatics:banking_guide", x=0, y=-5, tasks=[check(5, 1, "Read prices and team scope")], dependencies=[calling_gate], shape="hexagon", size=1.4)
    field = c.add(title="Field Kit", subtitle="One Bevel · Once per team each week", description="A small purse replaces the supplies most likely to strand a late arrival. It is deliberately ordinary: food, light, and a way to bring something awkward home.", icon="numismatics:bevel", x=-6, y=-1.5, tasks=[task(5, 2, "numismatics:bevel", consume=True, title="Submit one Bevel")], dependencies=[board], rewards=[reward(5, 1, "minecraft:cooked_beef", 32, team=True), reward(5, 2, "minecraft:torch", 64, team=True), reward(5, 3, "minecraft:lead", 8, team=True)], optional=True, shape="gear", can_repeat=True, cooldown=604800)
    works = c.add(title="Works Kit", subtitle="One Sprocket · Once per team each week", description="The works purse is sized for a visible repair rather than a decorative handful. It supports roads, public rooms, and the unglamorous patch that keeps an old build useful.", icon="numismatics:sprocket", x=-2, y=-0.5, tasks=[task(5, 3, "numismatics:sprocket", consume=True, title="Submit one Sprocket")], dependencies=[board], rewards=[reward(5, 4, "minecraft:stone_bricks", 128, team=True), reward(5, 5, "minecraft:oak_log", 64, team=True), reward(5, 6, "minecraft:iron_ingot", 32, team=True), reward(5, 7, "minecraft:lantern", 16, team=True)], optional=True, shape="gear", can_repeat=True, cooldown=604800)
    arcane = c.add(title="Arcane Kit", subtitle="One Sprocket · Once per team each week", description="The arcane purse restocks a teaching table rather than gambling on a random spell. Its materials support several schools and leave the final inscription to the player who understands the need.", icon="irons_spellbooks:uncommon_ink", x=2, y=-0.5, tasks=[task(5, 4, "numismatics:sprocket", consume=True, title="Submit one Sprocket")], dependencies=[board], rewards=[reward(5, 8, "irons_spellbooks:arcane_essence", 16, team=True), reward(5, 9, "irons_spellbooks:blank_rune", 4, team=True), reward(5, 10, "irons_spellbooks:common_ink", 16, team=True), reward(5, 11, "irons_spellbooks:uncommon_ink", 8, team=True)], optional=True, shape="gear", can_repeat=True, cooldown=604800)
    foundry = c.add(title="Foundry Kit", subtitle="Two Sprockets · Once per team each week", description="A foundry restock should keep a public line moving through more than one repair. Alloy, brass, and mechanisms buy back time while leaving ore generation and advanced machines valuable.", icon="create:precision_mechanism", x=6, y=-1.5, tasks=[task(5, 5, "numismatics:sprocket", 2, consume=True, title="Submit two Sprockets")], dependencies=[board], rewards=[reward(5, 12, "create:andesite_alloy", 64, team=True), reward(5, 13, "create:brass_ingot", 32, team=True), reward(5, 14, "create:precision_mechanism", 8, team=True), reward(5, 15, "create:belt_connector", 16, team=True)], optional=True, shape="gear", can_repeat=True, cooldown=604800)
    bond = c.add(title="Concord Bond", subtitle="One Cog · Once per team each week", description="The bond is stamped with a bridge on one face and an empty foundation on the other. Redeeming it puts substantial structural and fabrication stock behind the common project your team chooses.", icon="numismatics:cog", x=0, y=3, tasks=[task(5, 6, "numismatics:cog", consume=True, title="Submit one Cog")], dependencies=[board], rewards=[reward(5, 16, "minecraft:stone_bricks", 256, team=True), reward(5, 17, "minecraft:oak_log", 128, team=True), reward(5, 18, "minecraft:iron_ingot", 64, team=True), reward(5, 19, "minecraft:diamond", 16, team=True), reward(5, 20, "create:andesite_alloy", 64, team=True)], optional=True, shape="hexagon", size=1.4, can_repeat=True, cooldown=604800)
    rumour = c.add(title="Rumour Ledger", subtitle="Weekly report · 1 team Bevel", description="After callings are chosen, the archive pays for one specific maintenance report: a findable place, a real problem, and the name of whoever will check the result. The written book is consumed as the filed copy.", icon="minecraft:written_book", x=-3, y=6.5, tasks=[task(5, 7, "minecraft:written_book", consume=True, title="Submit one written field ledger"), check(5, 9, "I named the place, problem, and reviewer")], dependencies=[board], rewards=[reward(5, 21, "numismatics:bevel", team=True)], optional=True, shape="diamond", can_repeat=True, cooldown=604800)
    denominations = c.add(title="Know the Coins", subtitle="Coin guide · Spur · Bevel · Sprocket · Cog", description="The bank counts base value: a Spur is 1, a Bevel 8, a Sprocket 16, and a Cog 64. Routine work pays Bevels, specialties pay Sprockets, and major team milestones pay Cogs. Crowns and Suns can wait for an economy large enough to deserve them.", icon="numismatics:cog", x=3, y=6.5, tasks=[check(5, 8, "Read the denomination guide")], dependencies=[board], optional=True, shape="diamond")
    chapters.append(c)

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


def render_data(groups: list[dict[str, str]]) -> str:
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
        "version": 13,
    }) + "\n"


def outputs(root: Path) -> dict[Path, str]:
    chapters, groups = build_campaign()
    base = root / "config/ftbquests/quests"
    result = {base / "chapter_groups.snbt": render_groups(groups), base / "data.snbt": render_data(groups), base / "lang/en_us.snbt": "{\n}\n"}
    for chapter in chapters:
        result[base / "chapters" / f"{chapter.filename}.snbt"] = render_chapter(chapter)
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate the authoritative VvH Concord campaign")
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    root = args.root.resolve()
    expected = outputs(root)
    chapters_dir = root / "config/ftbquests/quests/chapters"
    expected_paths = set(expected)
    stale: list[str] = []
    for path, content in expected.items():
        if not path.exists() or path.read_text(encoding="utf-8-sig") != content:
            stale.append(str(path.relative_to(root)))
            if not args.check:
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text(content, encoding="utf-8")
    for path in chapters_dir.glob("*.snbt"):
        if path not in expected_paths:
            stale.append(str(path.relative_to(root)))
            if not args.check:
                path.unlink()
    if args.check:
        if stale:
            print("campaign source is stale: " + ", ".join(sorted(stale)))
            return 1
        print("campaign source is synchronized")
        return 0
    print(f"wrote {len(expected)} files; removed retired chapter files")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
