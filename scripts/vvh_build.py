#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Iterable

GROUP_ID = "7A11C0DE00000001"
PREFIX = "7A11C0DE"
ROLE_TABLE = "7A11C0DEF0000001"
TRADE_TABLE = "7A11C0DEF0000002"
FAIR_TABLE = "7A11C0DEF0000003"
VERSION = "2.0.0-dev.1"
SOURCE_SHA = "3e4842383dd1e029f054aedfe19940f0b53adbcd"


def oid(ch: int, kind: int, n: int) -> str:
    value = f"{PREFIX}{ch:02X}{kind:X}{n:05X}"
    assert len(value) == 16 and re.fullmatch(r"[0-9A-F]{16}", value)
    return value


def qid(ch: int, n: int) -> str:
    return oid(ch, 0, n)


def tid(ch: int, n: int) -> str:
    return oid(ch, 1, n)


def rid(ch: int, n: int) -> str:
    return oid(ch, 2, n)


def jstr(value: str) -> str:
    return json.dumps(value, ensure_ascii=False)


def custom_paper(name: str, color: str, lore: str, data: dict[str, Any]) -> dict[str, Any]:
    custom_data = {"vvh_campaign": "season_one", **data}
    return {
        "id": "minecraft:paper",
        "count": 1,
        "components": {
            "minecraft:custom_data": custom_data,
            "minecraft:custom_name": json.dumps({"color": color, "italic": False, "text": name}, separators=(",", ":")),
            "minecraft:enchantment_glint_override": True,
            "minecraft:lore": [json.dumps({"color": "gray", "italic": False, "text": lore}, separators=(",", ":"))],
        },
    }


@dataclass
class Task:
    id: str
    title: str
    type: str = "checkmark"
    item: str | None = None
    count: int = 1
    consume: bool = False
    advancement: str | None = None
    criterion: str = ""
    stat: str | None = None
    value: int = 1
    optional: bool = False


@dataclass
class Reward:
    id: str
    title: str
    type: str = "item"
    item: str | None = None
    count: int = 1
    team_reward: bool = False
    item_data: dict[str, Any] | None = None
    table_id: str | None = None
    exclude_from_claim_all: bool = False


@dataclass
class Quest:
    id: str
    title: str
    subtitle: str
    desc: list[str]
    icon: str
    x: float
    y: float
    tasks: list[Task]
    rewards: list[Reward] = field(default_factory=list)
    dependencies: list[str] = field(default_factory=list)
    min_required_dependencies: int = 0
    min_width: int = 280
    shape: str = "circle"
    size: float = 1.2
    optional: bool = False
    can_repeat: bool = False
    repeat_cooldown: int = 0
    hide_until_deps_complete: bool = False
    hide_dependency_lines: bool = False


@dataclass
class Chapter:
    code: int
    filename: str
    title: str
    icon: str
    order: int
    quests: list[Quest]
    images: list[dict[str, Any]] = field(default_factory=list)

    @property
    def id(self) -> str:
        return qid(self.code, 0)


class Campaign:
    def __init__(self) -> None:
        self.chapters: list[Chapter] = []
        self.reward_tables: list[dict[str, Any]] = []

    def all_quests(self) -> Iterable[Quest]:
        for chapter in self.chapters:
            yield from chapter.quests


def ck(ch: int, n: int, title: str) -> Task:
    return Task(tid(ch, n), title)


def item_task(ch: int, n: int, title: str, item: str, count: int = 1, *, consume: bool = False) -> Task:
    return Task(tid(ch, n), title, type="item", item=item, count=count, consume=consume)


def adv_task(ch: int, n: int, title: str, advancement: str) -> Task:
    return Task(tid(ch, n), title, type="advancement", advancement=advancement, criterion="")


def stat_task(ch: int, n: int, title: str, stat: str, value: int) -> Task:
    return Task(tid(ch, n), title, type="stat", stat=stat, value=value)


def plain_reward(ch: int, n: int, title: str, item: str, count: int, *, team: bool) -> Reward:
    return Reward(rid(ch, n), title, item=item, count=count, team_reward=team)


def paper_reward(ch: int, n: int, title: str, name: str, color: str, lore: str, data: dict[str, Any], *, team: bool) -> Reward:
    return Reward(rid(ch, n), title, item_data=custom_paper(name, color, lore, data), team_reward=team)


def choice_reward(ch: int, n: int, title: str, table_id: str, *, team: bool = False) -> Reward:
    return Reward(rid(ch, n), title, type="choice", table_id=table_id, team_reward=team, exclude_from_claim_all=True)


def lines(image: str, heading: str, *body: str) -> list[str]:
    return [f"{{image:{image} width:48 height:48 align:center}}", heading, "", *body]


def chapter_images(*paths: str) -> list[dict[str, Any]]:
    coords = [(-5.2, -1.2, -9.0), (5.2, 1.5, 8.0), (-4.5, 4.5, 5.0), (4.5, 5.0, -6.0)]
    out = []
    for idx, path in enumerate(paths):
        x, y, rot = coords[idx % len(coords)]
        out.append({
            "alpha": 80 if idx == 0 else 62,
            "height": 1.55,
            "image": path,
            "order": -30,
            "rotation": rot,
            "width": 1.55,
            "x": x,
            "y": y,
        })
    return out


def build_campaign() -> Campaign:
    c = Campaign()

    # 00 — Charter / rules. Keep this small; the rest of the book should be play, not policy.
    ch = 0x10
    qs: list[Quest] = []
    root = qid(ch, 1)
    qs.append(Quest(root, "&6&lOPEN THE ISLAND CHARTER", "Two minutes now; fewer arguments at 1:30 a.m.", lines(
        "minecraft:textures/item/writable_book.png", "&6&lTHE ISLAND NEEDS A MEMORY",
        "&fThe server usually dies when progression finishes before the world becomes worth remembering.",
        "&fSeason One reverses that with useful places, ridiculous rivalries, faction identity, public works, and records of what actually happened.",
        "",
        "&eRead the three reference clauses around this page, then sign the short charter below.&f They separate real hard protections from rules that only work because friends agree to honor them.",
        "",
        "&8Top gear is an ending. Municipal drama is renewable."
    ), "minecraft:writable_book", 0, -5, [ck(ch, 1, "Open the Charter")], shape="hexagon", size=1.75))
    qs.append(Quest(qid(ch, 3), "&aLAND, CLAIMS, AND RESET ZONES", "Permanent work needs a boundary that actually means something.", lines(
        "minecraft:textures/item/filled_map.png", "&a&lBUILD WHERE THE WORLD REMEMBERS",
        "&fHomes, faction halls, markets, roads, memorials, public machines, and lore sites belong only on land the host has explicitly confirmed permanent.",
        "&fAny announced reset zone is an expedition site, not a place for irreplaceable work. Claims are hard boundaries only where the live FTB Chunks configuration really enforces them.",
        "",
        "&cNo prank, theft, faction stunt, or contract overrides another team's protected claim or explicit consent.",
        "",
        "&8If the reset eats your cathedral, the cathedral was camping."
    ), "minecraft:filled_map", -4.6, -1.3, [ck(ch, 3, "I Know the Permanent-Land and Claim Rule")], dependencies=[root], optional=True, shape="diamond"))
    qs.append(Quest(qid(ch, 5), "&dRIVALRY, NEUTRALS, AND OPTIONAL COMBAT", "Make stories, not support tickets.", lines(
        "minecraft:textures/item/firework_rocket.png", "&d&lTHE FUNNY WAR CLAUSE",
        "&fVampires and Hunters may compete through banners, mascots, markets, races, scavenger hunts, public challenges, expeditions, propaganda, cooking, architecture, and reversible wilderness mischief.",
        "&fNeutrals may trade, mediate, scout, judge, rescue, courier, host, or sell services to either side without becoming a consolation faction.",
        "",
        "&cNo claim intrusion, theft, spawn camping, targeted harassment, irreversible sabotage, or destruction wearing a comedy moustache.",
        "&fCombat is a scheduled opt-in event only, with a host, backup, stop condition, protected noncombatants, and rebuild plan. Winning never grants progression power.",
        "",
        "&8A prank with a cleanup crew is a bit. A crater is an incident."
    ), "minecraft:firework_rocket", 0, -0.2, [ck(ch, 5, "I Accept the Rivalry and Optional-Combat Boundary")], dependencies=[root], optional=True, shape="octagon"))
    qs.append(Quest(qid(ch, 6), "&6VAMPIRISM, FTB TEAMS, AND SWITCHING", "Two faction systems exist. Do not pretend they are the same database.", lines(
        "vampirism:textures/item/vampire_fang.png", "&6&lONE BODY, ONE PARTY, TWO KINDS OF ALLEGIANCE",
        "&fVampirism now provides real Vampire and Hunter factions. FTB Teams provides shared quest progress and FTB Chunks ownership. Season One uses both, but it does not automatically synchronize them.",
        "",
        "&eA Vampirism advancement records that an event happened; it is not a live faction-state detector forever.",
        "&fBefore a faction team claims shared foundation supplies, one teammate or the host confirms that the team is presently aligned with that faction.",
        "&fAsk the host before joining, leaving, or switching an FTB party. Claims, storage, contracts, and quest history must be checked rather than guessed.",
        "",
        "&8The bureaucracy has developed fangs."
    ), "vampirism:vampire_fang", 4.6, -1.3, [ck(ch, 6, "I Understand Vampirism Faction vs FTB Team State")], dependencies=[root], optional=True, shape="gear"))
    final_charter = qid(ch, 8)
    qs.append(Quest(final_charter, "&6&lSIGN THE CHARTER", "Four boundaries, one signature, useful travel supplies.", lines(
        "minecraft:textures/item/writable_book.png", "&6&lTHE FOUR-LINE VERSION",
        "&f1. Build irreplaceable work only on confirmed permanent land.",
        "&f2. Claims and consent outrank rivalry, contracts, and bits.",
        "&f3. Combat is optional, scheduled, supervised, and reversible.",
        "&f4. Vampirism faction state and FTB team state are separate; switches need a quick host review.",
        "",
        "&eClick to sign.&f The reference clauses stay visible whenever somebody begins a sentence with 'technically'.",
        "",
        "&6Starter nudge:&f one Compass and eight Torches. Enough to leave spawn with a plan; not enough to delete the opening game."
    ), "minecraft:writable_book", 0, 3.8, [ck(ch, 8, "Sign the Island Charter")], rewards=[
        paper_reward(ch, 1, "Field Charter", "Field Charter — Season One", "gold", "Signed before choosing a banner; prestige, not power.", {"document": "island_charter"}, team=False),
        plain_reward(ch, 2, "Personal Compass", "minecraft:compass", 1, team=False),
        plain_reward(ch, 3, "Eight Travel Torches", "minecraft:torch", 8, team=False),
    ], dependencies=[root], shape="hexagon", size=2.0, hide_until_deps_complete=True))
    c.chapters.append(Chapter(ch, "vvh_00_island_charter", "VvH 00 · The Island Charter", "minecraft:writable_book", 0, qs, chapter_images(
        "poiesis:textures/questpics/vvh/season_one_crest.png", "vampirism:textures/item/vampire_fang.png", "minecraft:textures/item/lantern.png"
    )))

    # 01 — Allegiance. Real Vampirism factions are now the mechanical spine; Neutral remains a full civic path.
    ch = 0x11
    qs = []
    aroot = qid(ch, 1)
    qs.append(Quest(aroot, "&6&lREAD THE THREE INVITATIONS", "Choose what kind of problem you want to become useful at.", lines(
        "minecraft:textures/item/compass_16.png", "&6&lTHREE LEGITIMATE WAYS TO BELONG",
        "&4Vampires&f gain a real supernatural progression and are asked to turn that identity into hospitality, ritual spaces, night infrastructure, and civic obligations.",
        "&bHunters&f gain their own real progression and are asked to turn vigilance into safe roads, public knowledge, workshops, and reliable refuge.",
        "&aNeutrals&f remain human/non-aligned and become the connective tissue: trade, contracts, mapping, MCA civic life, rescue, logistics, and arbitration.",
        "",
        "&eNothing here is permanent.&f Switching is allowed, but it creates social and claim bookkeeping. Pick the role you actually want to play this week, not the reward you think is numerically best.",
        "",
        "&8The Atlas has stopped pretending the word 'faction' is metaphorical."
    ), "minecraft:compass", 0, -5, [ck(ch, 1, "Read All Three Invitations")], shape="hexagon", size=1.75))
    qs.append(Quest(qid(ch, 2), "&4&lTAKE THE CRIMSON INVITATION", "Become a Vampire, then register the choice socially.", lines(
        "vampirism:textures/item/vampire_fang.png", "&4&lTHE HOUSE OF NIGHT",
        "&fComplete Vampirism's &eBecome a Vampire&f advancement, then click the second task after your current faction choice and intended FTB team are clear to at least one other player or the host.",
        "",
        "&7The advancement is historical evidence, not a permanent live-state lock. If you later cure/switch, the old page remains part of your story rather than becoming a loophole for fresh foundation caches.",
        "",
        "&8Please file all immortality paperwork before sunrise."
    ), "vampirism:vampire_fang", -5.0, -0.8, [adv_task(ch, 21, "Become a Vampire", "vampirism:vampire/become_vampire"), ck(ch, 22, "Our Current Allegiance and FTB Team Are Clear")], dependencies=[aroot], rewards=[
        paper_reward(ch, 23, "Crimson Invitation", "Crimson Invitation", "dark_red", "A record of joining the House of Night; not proof of current faction state.", {"allegiance": "vampire"}, team=False)
    ], shape="heart", size=1.45))
    qs.append(Quest(qid(ch, 3), "&b&lTAKE THE LANTERN OATH", "Become a Hunter, then register the choice socially.", lines(
        "vampirism:textures/item/garlic.png", "&b&lTHE LANTERN ORDER",
        "&fComplete Vampirism's &eBecome a Hunter&f advancement, then click the second task after your current faction choice and intended FTB team are clear to at least one other player or the host.",
        "",
        "&7The advancement records that you joined at least once. Later betrayal/switching does not erase history, so shared caches still use peer/host confirmation of current allegiance.",
        "",
        "&8The official uniform is 'prepared'. The cape remains under committee review."
    ), "vampirism:garlic", 0, 0.6, [adv_task(ch, 31, "Become a Hunter", "vampirism:hunter/become_hunter"), ck(ch, 32, "Our Current Allegiance and FTB Team Are Clear")], dependencies=[aroot], rewards=[
        paper_reward(ch, 33, "Lantern Oath", "Lantern Oath", "aqua", "A record of joining the Lantern Order; not proof of current faction state.", {"allegiance": "hunter"}, team=False)
    ], shape="diamond", size=1.45))
    qs.append(Quest(qid(ch, 4), "&a&lSIGN THE FREE COMPANY REGISTER", "Stay neutral on purpose, not by forgetting to choose.", lines(
        "minecraft:textures/item/filled_map.png", "&a&lTHE FREE COMPANIES",
        "&fRemain outside Vampire and Hunter alignment for now. Name one service you want to be known for: courier work, maps, market brokerage, MCA diplomacy, rescue, hospitality, construction, intelligence, or event hosting.",
        "",
        "&eClick after another player knows what service you offer.&f Neutrality is a playable civic role with its own foundation chapter, not a beige skip button.",
        "",
        "&8Somebody has to invoice the supernatural."
    ), "minecraft:filled_map", 5.0, -0.8, [ck(ch, 41, "I Registered a Neutral Service With Another Player")], dependencies=[aroot], rewards=[
        paper_reward(ch, 43, "Free Company Writ", "Free Company Writ", "green", "A licence to be useful without wearing either faction's problems.", {"allegiance": "neutral"}, team=False)
    ], shape="square", size=1.45))
    qs.append(Quest(qid(ch, 5), "&eCHOOSE YOUR PERSONAL TRADE LENS", "Faction answers who you stand with; this answers how you help.", lines(
        "minecraft:textures/item/spyglass.png", "&e&lONE ROLE, ZERO CLASS LOCKS",
        "&fClaim one cosmetic Trade Lens: Builder, Engineer, Pathfinder, Keeper, Arcanist, or Archivist. It grants no stats and does not restrict later quests.",
        "",
        "&7The purpose is social legibility. When a project stalls, people should have a rough idea who enjoys fixing which kind of problem.",
        "",
        "&8Multiclassing is permitted because this is literally paper."
    ), "minecraft:spyglass", 0, 4.4, [ck(ch, 51, "I Know What Kind of Work I Want First")], rewards=[choice_reward(ch, 52, "Choose a Personal Trade Lens", ROLE_TABLE)], dependencies=[aroot], optional=True, shape="octagon", size=1.35))
    c.chapters.append(Chapter(ch, "vvh_01_three_invitations", "VvH 01 · Three Invitations", "minecraft:compass", 1, qs, chapter_images(
        "vampirism:textures/item/vampire_fang.png", "vampirism:textures/item/garlic.png", "minecraft:textures/item/filled_map.png"
    )))

    # Helper for the parallel foundations.
    def foundation_chapter(ch: int, filename: str, title: str, chapter_icon: str, root_title: str, root_subtitle: str, root_icon: str,
                           root_tasks: list[Task], faction_color: str, projects: list[tuple[int, str, str, str, list[Task], list[str]]],
                           final_title: str, final_name: str, final_lore: str, final_data: dict[str, Any], images: tuple[str, ...]) -> Chapter:
        qs2: list[Quest] = []
        r0 = qid(ch, 1)
        qs2.append(Quest(r0, root_title, root_subtitle, lines(
            images[0], f"{faction_color}&lFOUNDATION WORK, NOT A TECH TREE",
            "&fComplete any &e5 of 7&f foundation works. Every option leaves a useful place, supply, route, or institution behind; none exists merely to make an inventory number go up.",
            "",
            "&eShared-cache rule:&f before claiming the foundation cache, one teammate or the host confirms the FTB team presently represents this faction/company.",
            "&fHistorical allegiance achievements do not entitle a switched team to duplicate supplies.",
            "",
            "&7Use the five-part creative rubric when a project says REVIEW: function, access, safety, story, maintenance. Two-player peer review or one host review passes it.",
        ), root_icon, 0, -5, root_tasks, shape="hexagon", size=1.7))
        pids = []
        xs = [-6.0, -4.0, -2.0, 0.0, 2.0, 4.0, 6.0]
        ys = [-1.4, 0.2, -0.7, 0.8, -0.7, 0.2, -1.4]
        shapes = ["square", "diamond", "gear", "heart", "gear", "diamond", "square"]
        for idx, (n, qt, sub, icon, tasks, body) in enumerate(projects):
            pid = qid(ch, n); pids.append(pid)
            qs2.append(Quest(pid, qt, sub, lines(images[min(idx + 1, len(images)-1)], f"{faction_color}&lFOUNDATION WORK {idx + 1}", *body), icon, xs[idx], ys[idx], tasks, dependencies=[r0], shape=shapes[idx], size=1.25))
        final = qid(ch, 10)
        qs2.append(Quest(final, final_title, "Five useful works become a home people can actually rely on.", lines(
            images[0], f"{faction_color}&lA PLACE WITH OBLIGATIONS",
            "&fFinish any five foundation works, then click the review task after the team confirms the current allegiance/company identity, names the headquarters, and records one maintenance owner or rotation.",
            "",
            "&eReward philosophy:&f each foundation gets the same horizontal construction cache: scaffolding and Super Glue. Faction flavor lives in what you built, not in getting a numerically better loot table.",
            "",
            "&7The keepsake is historical. Switching later does not make it a coupon."
        ), chapter_icon, 0, 4.6, [ck(ch, 101, "Current Identity Confirmed; Headquarters Named; Maintenance Owner Recorded")], rewards=[
            paper_reward(ch, 102, "Foundation Charter", final_name, "dark_red" if faction_color == "&4" else ("aqua" if faction_color == "&b" else "green"), final_lore, final_data, team=True),
            plain_reward(ch, 103, "Thirty-Two Scaffolding", "minecraft:scaffolding", 32, team=True),
            plain_reward(ch, 104, "Four Super Glue", "create:super_glue", 4, team=True),
        ], dependencies=pids, min_required_dependencies=5, shape="hexagon", size=2.0, hide_until_deps_complete=True))
        return Chapter(ch, filename, title, chapter_icon, ch - 0x10, qs2, chapter_images(*images))

    # 02 — Vampire foundation. Real mod mechanics, but violence is not the only path.
    ch = 0x12
    vampire_projects = [
        (2, "&4BUILD THE COMMON COFFIN ROOM", "REVIEW · bedrooms that make the faction's actual needs visible.", "vampirism:coffin_red", [item_task(ch, 21, "Carry a Red Coffin", "vampirism:coffin_red"), ck(ch, 22, "REVIEW: The House Has a Shared Sleeping/Recovery Space")], [
            "&fPlace at least one functional coffin in an accessible shared room, plus ordinary storage or seating for visitors. The point is a headquarters people return to, not a lone coffin abandoned in a cave.",
            "&7REVIEW checks function, access, safety, story, and maintenance."
        ]),
        (3, "&4RAISE AN ALTAR CHAMBER", "Make the first faction ritual object part of a place, not a lawn ornament.", "vampirism:altar_inspiration", [item_task(ch, 31, "Carry an Altar of Inspiration", "vampirism:altar_inspiration"), ck(ch, 32, "REVIEW: The Altar Has a Safe, Named Chamber")], [
            "&fObtain an Altar of Inspiration and install it in a deliberate chamber with a safe approach and a sign/book explaining the room.",
            "&fLeave enough space that teammates are not clipping through furniture during progression.",
            "&8Ancient evil remains subject to fire code."
        ]),
        (4, "&4STOCK A BLOOD PANTRY", "A faction resource should have a home before it becomes chest soup.", "vampirism:blood_bottle", [item_task(ch, 41, "Carry 4 Blood Bottles", "vampirism:blood_bottle", 4), ck(ch, 42, "REVIEW: A Labelled Shared Blood Pantry Exists")], [
            "&fCarry four Blood Bottles and establish a labelled shared pantry or processing corner. Do not consume the bottles for the quest; the task checks possession only.",
            "&fLeave a written restock rule so a late player knows whether supplies are communal, reserved, or trade stock."
        ]),
        (5, "&4OPEN THE NIGHT KITCHEN", "Hospitality is faction infrastructure too.", "vampiresdelight:blood_pie", [item_task(ch, 51, "Carry a Blood Pie", "vampiresdelight:blood_pie"), ck(ch, 52, "REVIEW: The Night Kitchen Can Host a Visitor")], [
            "&fUse Vampire's Delight or ordinary food infrastructure to make a small kitchen/serving area. Carry one Blood Pie as proof you touched the pack's vampire-food loop.",
            "&fThe room passes when a guest can arrive, understand what is communal, and leave without raiding a progression chest."
        ]),
        (6, "&4MARK A SAFE NIGHT ROUTE", "The House should improve travel, not merely occupy a basement.", "minecraft:lantern", [ck(ch, 61, "REVIEW: A Signed Night Route Connects Two Useful Places")], [
            "&fCreate or adopt a signed route between the House and one public destination: spawn, market, port, workshop, road, archive, or neutral office. Make hazards visible without flooding the whole island with random torches.",
            "&7A route is infrastructure when somebody else can follow it alone."
        ]),
        (7, "&4HOST A BLOODLESS VISIT", "Show that faction identity can create a scene without creating a corpse.", "vampiresdelight:spirit_lantern", [ck(ch, 71, "Two Players Visited the House for a Tour, Meal, Trade, or Ceremony")], [
            "&fInvite at least one player who is not required to be a Vampire. Give them a tour, meal, trade, ceremony, archive reading, or ridiculous local custom.",
            "&fNo PvP or feeding is required. The social event itself is the objective."
        ]),
        (8, "&4INSTALL ONE USEFUL MACHINE", "Immortality still benefits from logistics.", "create:mechanical_press", [item_task(ch, 81, "Carry a Mechanical Press", "create:mechanical_press"), ck(ch, 82, "REVIEW: The Machine Serves a Shared Function")], [
            "&fBuild or adopt one Create machine that solves a real shared problem: processing, doors, storage movement, kitchen support, transport loading, or spectacle with an actual use.",
            "&fCarry a Mechanical Press as a modest objective proof; the reviewed machine itself may use any appropriate Create components."
        ]),
    ]
    c.chapters.append(foundation_chapter(ch, "vvh_02_house_of_night", "VvH 02 · House of Night", "vampirism:vampire_fang", "&4&lFOUND THE HOUSE OF NIGHT", "Real vampire progression, followed by civic consequences.", "vampirism:vampire_fang",
        [adv_task(ch, 11, "At Least One Teammate Has Become a Vampire", "vampirism:vampire/become_vampire"), ck(ch, 12, "Current Vampire Alignment Confirmed for This FTB Team")], "&4", vampire_projects,
        "&4&lCHARTER THE HOUSE OF NIGHT", "Charter of the House of Night", "Five works turned supernatural progression into a place with obligations.", {"foundation": "vampire"},
        ("vampirism:textures/item/vampire_fang.png", "vampirism:textures/item/vampire_fang.png", "minecraft:textures/item/lantern.png", "minecraft:textures/item/writable_book.png")))

    # 03 — Hunter foundation.
    ch = 0x13
    hunter_projects = [
        (2, "&bBUILD THE PUBLIC WATCHHOUSE", "REVIEW · visible service before private arsenal.", "minecraft:lantern", [ck(ch, 21, "REVIEW: The Watchhouse Has Public Information and a Safe Guest Area")], [
            "&fBuild a small watchhouse, gatehouse, or civic room with public information: local hazards, routes, contacts, or shelter instructions. Private equipment can remain private; the public-facing service must be obvious.",
            "&8A watchhouse with no information is just a suspicious shed."
        ]),
        (3, "&bESTABLISH THE HUNTER TABLE", "Put the actual faction workstation somewhere teammates can use it.", "vampirism:hunter_table", [item_task(ch, 31, "Carry a Hunter Table", "vampirism:hunter_table"), ck(ch, 32, "REVIEW: The Hunter Table Is Installed in a Shared Workshop")], [
            "&fObtain a Hunter Table and install it in a shared workshop with storage and enough room for somebody else to understand the station without excavating your bedroom.",
            "&7This is progression infrastructure, not a requirement to sprint the hunter tech tree."
        ]),
        (4, "&bKEEP THE GARLIC RESERVE", "Preparedness is funnier when it has labels.", "vampirism:garlic", [item_task(ch, 41, "Carry 8 Garlic", "vampirism:garlic", 8), ck(ch, 42, "REVIEW: A Labelled Shared Garlic/Field-Supply Reserve Exists")], [
            "&fCarry eight Garlic and establish a labelled field-supply reserve. It can also contain food, maps, lanterns, spare tools, or first-response supplies.",
            "&fDo not consume the Garlic for the quest. The point is a maintained shared reserve."
        ]),
        (5, "&bASSEMBLE A STAKE DRILL KIT", "Tools become culture when people know the safety rules.", "vampirism:stake", [item_task(ch, 51, "Carry 4 Stakes", "vampirism:stake", 4), ck(ch, 52, "REVIEW: A Safe Training/Equipment Area Exists")], [
            "&fCarry four Stakes and make a tiny training or equipment area. It may be ceremonial or practical, but it needs a clear rule against using faction equipment as an excuse to harass unwilling players.",
            "&7The quest does not require the hidden stake-kill advancement. Violence remains optional."
        ]),
        (6, "&bOPEN THE ALCHEMICAL BENCH", "Make countermeasure tech legible to the team.", "vampirism:alchemical_cauldron", [item_task(ch, 61, "Carry an Alchemical Cauldron", "vampirism:alchemical_cauldron"), ck(ch, 62, "REVIEW: The Cauldron Has a Safe Shared Work Area")], [
            "&fObtain an Alchemical Cauldron and install it with labelled ingredient/storage space. The station should be usable without blocking a hallway or setting the meeting room on fire.",
            "&8Chemistry is just potion-making wearing safety goggles."
        ]),
        (7, "&bLIGHT A REFUGE ROUTE", "A Hunter faction earns trust by making retreat possible.", "minecraft:lantern", [ck(ch, 71, "REVIEW: A Signed, Lit Refuge Route Connects Two Useful Places")], [
            "&fCreate or adopt a readable route between the Order and one public destination. Mark turns, major hazards, and a safe fallback point rather than carpeting the island with torch spam.",
            "&fA player unfamiliar with the route should be able to use it without voice chat."
        ]),
        (8, "&bRUN ONE CIVILIAN SAFETY DRILL", "Preparation without a victim.", "minecraft:shield", [ck(ch, 81, "At Least Two Players Completed a Safety/Rescue Drill")], [
            "&fRun a short drill with another player: night escort, lost-player retrieval, route evacuation, Hordes shelter test, equipment demo, or emergency supply run.",
            "&fNo combat is necessary. The output is one improvement to the route, instructions, or supplies discovered by the drill."
        ]),
    ]
    c.chapters.append(foundation_chapter(ch, "vvh_03_lantern_order", "VvH 03 · Lantern Order", "vampirism:garlic", "&b&lFOUND THE LANTERN ORDER", "Real hunter progression, followed by public responsibility.", "vampirism:garlic",
        [adv_task(ch, 11, "At Least One Teammate Has Become a Hunter", "vampirism:hunter/become_hunter"), ck(ch, 12, "Current Hunter Alignment Confirmed for This FTB Team")], "&b", hunter_projects,
        "&b&lCHARTER THE LANTERN ORDER", "Charter of the Lantern Order", "Five works turned vigilance into public service instead of an arms race.", {"foundation": "hunter"},
        ("vampirism:textures/item/garlic.png", "vampirism:textures/item/garlic.png", "minecraft:textures/item/lantern.png", "minecraft:textures/item/writable_book.png")))

    # 04 — Neutral foundation. Same five-of-seven workload, no supernatural tax.
    ch = 0x14
    neutral_projects = [
        (2, "&aOPEN A CONTRACT BOARD", "REVIEW · one visible place where people can ask for help.", "minecraft:writable_book", [ck(ch, 21, "REVIEW: A Public Contract Board Has At Least 3 Clear Job Types")], [
            "&fBuild a board, desk, book, or mailbox where players can request services. Include at least three examples such as courier, mapping, construction, mediation, rescue, market procurement, escort, or event staffing.",
            "&fPrices may be items, favors, Bevels, or negotiated nonsense. Terms must be understandable before acceptance."
        ]),
        (3, "&aMARK A COURIER ROUTE", "REVIEW · turn a trip into shared knowledge.", "minecraft:filled_map", [item_task(ch, 31, "Carry a Filled Map", "minecraft:filled_map"), ck(ch, 32, "REVIEW: A Named Courier Route Connects Two Useful Places")], [
            "&fCarry a Filled Map and publish one named route between useful locations. Include at least one navigation aid: signs, map markers, road, landmark, or written directions.",
            "&7Fast travel is optional; shared knowledge is the actual infrastructure."
        ]),
        (4, "&aESTABLISH A MARKET STALL", "REVIEW · trade should create meetings, not spreadsheets.", "minecraft:emerald", [ck(ch, 41, "REVIEW: A Stall or Counter Lists Goods/Services and Contact Terms")], [
            "&fCreate a market stall, exchange counter, or service desk with a visible offer. At least one trade should be useful to both factions or to a late joiner.",
            "&fDo not design a closed-loop arbitrage machine around quest rewards."
        ]),
        (5, "&aMAKE A GUESTHOUSE OR WAYSTATION", "REVIEW · neutrality should be somewhere people can meet.", "minecraft:white_bed", [ck(ch, 51, "REVIEW: A Neutral Guest/Meeting Space Can Host 2 Players")], [
            "&fBuild a small guesthouse, embassy room, tavern corner, or waystation with seating/sleeping, food access, and a clearly neutral meeting area.",
            "&fThe space should be useful when Vampire and Hunter players need to talk without standing in somebody's storage room."
        ]),
        (6, "&aSTART THE CIVIC LEDGER", "REVIEW · record agreements before memory becomes fan fiction.", "minecraft:book", [ck(ch, 61, "REVIEW: A Shared Ledger Records At Least 3 Contracts, Places, or Decisions")], [
            "&fUse books, signs, lecterns, or an archive chest to record at least three useful facts: contracts, route notes, faction agreements, public project owners, trade terms, or unresolved disputes.",
            "&7The ledger is allowed to be funny. It is not allowed to be useless."
        ]),
        (7, "&aMAKE ONE MCA CIVIC CONNECTION", "MCA is for people and places, not just furniture with dialogue boxes.", "minecraft:bell", [ck(ch, 71, "REVIEW: We Used MCA/Civic Play to Create One Named Relationship or Place")], [
            "&fUse Minecraft Comes Alive / Capitals, when available in the current world, to create one named civic connection: village liaison, household, public role, settlement story, ceremony, or negotiated relationship.",
            "&fIf world conditions make MCA unavailable, the host may approve an equivalent player-run civic role instead."
        ]),
        (8, "&aRUN A MEDIATION OR RESCUE", "Solve one problem nobody owns by default.", "minecraft:recovery_compass", [ck(ch, 81, "Another Player Confirms the Mediation, Rescue, or Logistics Help")], [
            "&fHelp resolve one real cross-player problem: lost gear retrieval, route confusion, disputed trade, transport failure, event scheduling, missing supplies, or a faction misunderstanding.",
            "&fThe other player confirms completion. Manufactured arguments do not count; please do not optimize bureaucracy."
        ]),
    ]
    c.chapters.append(foundation_chapter(ch, "vvh_04_free_companies", "VvH 04 · Free Companies", "minecraft:filled_map", "&a&lFOUND A FREE COMPANY", "Neutrality becomes valuable when it has services, routes, and a place to meet.", "minecraft:filled_map",
        [ck(ch, 11, "Current Neutral/Independent Status Confirmed With Another Player")], "&a", neutral_projects,
        "&a&lCHARTER THE FREE COMPANY", "Free Company Charter", "Five works made neutrality a service network rather than an absence of faction content.", {"foundation": "neutral"},
        ("poiesis:textures/questpics/vvh/free_company_writ.png", "minecraft:textures/item/writable_book.png", "minecraft:textures/item/filled_map.png", "minecraft:textures/item/lantern.png")))

    vampire_final = qid(0x12, 10)
    hunter_final = qid(0x13, 10)
    neutral_final = qid(0x14, 10)

    # 05 — Personal contributions. Deliberately broader than faction progression.
    ch = 0x15
    qs = []
    croot = qid(ch, 1)
    qs.append(Quest(croot, "&6&lTHE WORK EACH HAND KNOWS", "Complete any three routes. Let somebody else be good at the other five.", lines(
        "minecraft:textures/item/writable_book.png", "&6&lSPECIALIZATION WITHOUT HOMEWORK",
        "&fAfter any one foundation is established, complete any &e3 of 8&f contribution routes. They overlap ordinary play and are designed so a Neutral, Vampire, or Hunter can finish the chapter without changing faction.",
        "",
        "&7A route passes when it leaves behind something reusable: a machine, service, guide, relationship, supply system, route, or documented technique. Pure inventory flexing is not a contribution.",
        "",
        "&8The Atlas has discovered comparative advantage and is being unbearable about it."
    ), "minecraft:crafting_table", 0, -5, [ck(ch, 1, "Read the Eight Contribution Routes")], dependencies=[vampire_final, hunter_final, neutral_final], min_required_dependencies=1, shape="hexagon", size=1.7))
    route_specs = [
        (2, "&6ENGINEER — MAKE MOTION USEFUL", "create:mechanical_press", [item_task(ch, 21, "Carry 8 Andesite Alloy", "create:andesite_alloy", 8), ck(ch, 22, "REVIEW: A Create System Solves a Shared Problem")], ["&fCarry eight Andesite Alloy, then build or improve a Create system used by at least one other player.", "&fGood outputs include processing, loading, doors, elevators, workshop tooling, kitchen support, or moving spectacle that actually moves something useful."]),
        (3, "&dARCANIST — MAKE MAGIC TEACHABLE", "irons_spellbooks:arcane_essence", [item_task(ch, 31, "Carry 8 Arcane Essence", "irons_spellbooks:arcane_essence", 8), ck(ch, 32, "REVIEW: A Spell/Ingredient/Upgrade Tip Is Published")], ["&fCarry eight Arcane Essence and publish one practical Iron's Spells guide, labelled station, sample kit, or demonstration another player can reproduce.", "&fThe quest rewards teaching the system, not owning the rarest spell."]),
        (4, "&4FACTION SPECIALIST — TRANSLATE THE SUPERNATURAL", "vampirism:vampire_fang", [ck(ch, 41, "REVIEW: I Taught or Documented One Vampirism Mechanic for Someone Else")], ["&fDocument or demonstrate one useful Vampirism mechanic, progression dependency, faction-specific workstation, safe countermeasure, or Vampire's Delight recipe.", "&fA Neutral may complete this by interviewing/observing a faction player and publishing the result. No faction conversion is required."]),
        (5, "&bAERONAUT — BUILD TOWARD A VEHICLE", "createpropulsion:wing", [item_task(ch, 51, "Carry a Propulsion Wing", "createpropulsion:wing"), ck(ch, 52, "REVIEW: A Vehicle/Airframe Test or Dock Improvement Was Documented")], ["&fCarry one Create Propulsion Wing and contribute to an airframe, vehicle, dock, hangar, test stand, or transport prototype.", "&fThe machine does not have to be a finished airship. A documented test that prevents the next person from repeating your crash counts."]),
        (6, "&aDIPLOMAT — MAKE A RELATIONSHIP LEGIBLE", "minecraft:bell", [ck(ch, 61, "Another Player Confirms a Trade, MCA, Faction, or Civic Agreement")], ["&fCreate or clarify one real agreement: trade terms, MCA/civic relationship, faction access rule, public-project ownership, event schedule, or dispute resolution.", "&fWrite the result somewhere participants can find later. Diplomacy without a record is just vibes with a meeting time."]),
        (7, "&eQUARTERMASTER — FEED A GROUP", "minecraft:bread", [ck(ch, 71, "REVIEW: A Shared Meal or Supply Station Served At Least 2 Players")], ["&fUse Farmer's Delight, Vampire's Delight, or ordinary food to run a shared meal, pantry, travel ration station, or event table for at least two players.", "&fVampire-specific and human-friendly options can coexist; the point is hospitality without forcing anybody's diet or faction."]),
        (8, "&aPATHFINDER — TURN DISTANCE INTO A ROUTE", "naturescompass:naturescompass", [item_task(ch, 81, "Carry a Filled Map", "minecraft:filled_map"), ck(ch, 82, "REVIEW: A New Route/Map Is Usable Without Voice Chat")], ["&fCarry a Filled Map and publish a route to a biome, structure, settlement, public work, faction hall, or expedition point.", "&fInclude signs, landmarks, map notes, Via Romana roadwork, or written directions so another person can follow it alone."]),
        (9, "&fARCHIVIST — PRESERVE ONE FAILURE", "minecraft:writable_book", [ck(ch, 91, "REVIEW: A Failure, Fix, or Weird Event Was Archived With a Useful Lesson")], ["&fWrite down one failed machine, bad expedition, faction misunderstanding, Hordes incident, server bug workaround, or ridiculous accident and the lesson it produced.", "&fThe archive should save the next player time or make the story worth retelling. Ideally both."]),
    ]
    pids=[]; xs=[-6,-4.2,-2.2,0,2.2,4.2,6,0]; ys=[-1.2,0.6,-0.5,1.0,-0.5,0.6,-1.2,3.0]
    for i,(n,title,icon,tasks,body) in enumerate(route_specs):
        pid=qid(ch,n); pids.append(pid)
        qs.append(Quest(pid,title,"Personal contribution · useful output required.",lines("minecraft:textures/item/writable_book.png","&6&lLEAVE SOMETHING BEHIND",*body,"","&7Progress is personal within your current FTB quest team; reviewed output may be faction or server-wide."),icon,xs[i],ys[i],tasks,dependencies=[croot],shape=["gear","hexagon","heart","diamond","square","circle","diamond","square"][i]))
    contribution_final=qid(ch,10)
    qs.append(Quest(contribution_final,"&6&lTHREE HANDS' WORTH", "Choose one practical favor after contributing in three different ways.", lines(
        "minecraft:textures/item/writable_book.png", "&6&lBREADTH WITHOUT COMPLETIONISM",
        "&fComplete any three contribution routes. You do not get a bonus for clearing all eight, because that would quietly turn choice into homework.",
        "",
        "&eClaim one practical favor:&f a small horizontal utility bundle. The strongest option shortens setup friction; none hands out faction rank, boss loot, rare gear, or a finished vehicle.",
        "",
        "&8Someone else is allowed to know things you don't. Horrifying."
    ), "minecraft:crafting_table", 0, 5.4, [ck(ch, 101, "Record Which Three Routes I Contributed")], rewards=[choice_reward(ch, 102, "Choose a Practical Contribution Favor", TRADE_TABLE)], dependencies=pids, min_required_dependencies=3, shape="hexagon", size=2.0, hide_until_deps_complete=True))
    c.chapters.append(Chapter(ch,"vvh_05_work_each_hand_knows","VvH 05 · The Work Each Hand Knows","minecraft:crafting_table",5,qs,chapter_images("minecraft:textures/item/writable_book.png","vampirism:textures/item/vampire_fang.png","minecraft:textures/item/filled_map.png","minecraft:textures/item/writable_book.png")))

    # 06 — Public infrastructure.
    ch=0x16; qs=[]; iroot=qid(ch,1)
    qs.append(Quest(iroot,"&6&lTHE ISLAND REMEMBERS", "Complete any four public works. Build history into the commute.", lines(
        "minecraft:textures/item/lantern.png", "&6&lPUBLIC WORKS ARE THE REAL ENDGAME",
        "&fComplete any &e4 of 8&f projects. Each must be public or clearly shared, named, and maintainable. Projects may be new builds or substantial upgrades to something players already care about.",
        "",
        "&7REVIEW uses function, access, safety, story, maintenance. A beautiful object nobody can use is art; good. It is simply not this particular quest.",
        "",
        "&8The road to endgame is now literally a road."
    ),"minecraft:lantern",0,-5,[ck(ch,1,"Read the Public-Works Rubric")],dependencies=[contribution_final],shape="hexagon",size=1.7))
    infra=[
        (2,"&eROAD OR WAYFINDING SPINE","minecraft:rail",[ck(ch,21,"REVIEW: A Named Route Links 3 Useful Places")],["&fCreate or upgrade a road, rail, path, sign system, or Via Romana route linking at least three useful locations.","&fIt needs readable navigation and a maintenance owner or faction/company responsibility."]),
        (3,"&6MARKET AND CONTRACT HALL","minecraft:emerald",[ck(ch,31,"REVIEW: A Public Market/Contract Space Has At Least 3 Active Uses")],["&fBuild or improve a public market with at least three useful offers, contract categories, or service desks.","&fInclude neutral access and clear rules for faction goods rather than creating a private chest mall with a dramatic roof."]),
        (4,"&6SHARED WORKSHOP","create:mechanical_press",[ck(ch,41,"REVIEW: A Public Workshop Exposes At Least 2 Useful Capabilities")],["&fCreate a workshop where players can access at least two useful capabilities such as Create processing, repair/build tools, enchanting support, storage, or safe experiment space.","&fLabel what is public versus personal before somebody 'borrows' the important gear forever."]),
        (5,"&fARCHIVE AND MEMORIAL","minecraft:lectern",[ck(ch,51,"REVIEW: The Archive Preserves At Least 5 Real Server Facts/Stories")],["&fBuild or expand an archive, museum, memorial, map room, newspaper office, or gallery preserving at least five real facts, events, failures, places, or people from this world.","&fFuture players should be able to infer that things happened here before they logged in."]),
        (6,"&aCOMMUNITY KITCHEN","minecraft:bread",[ck(ch,61,"REVIEW: A Shared Kitchen/Pantry Supports Multiple Diets and Players")],["&fBuild a public kitchen or pantry that supports ordinary food plus faction-specific needs where practical. Farmer's Delight and Vampire's Delight both count.","&fPublish what is communal, what should be restocked, and who gets yelled at when the last ration disappears."]),
        (7,"&bAIRSHIP / VEHICLE PORT","createpropulsion:wing",[ck(ch,71,"REVIEW: A Dock, Hangar, Test Field, or Vehicle Station Is Publicly Usable")],["&fBuild or improve a dock, hangar, test field, landing marker, vehicle depot, or loading platform for Create Aeronautics/Propulsion play.","&fIt can precede a fully working craft. Infrastructure that makes future vehicles easier is already valuable."]),
        (8,"&cHORDE REFUGE","minecraft:iron_door",[ck(ch,81,"REVIEW: A Refuge/Alarm Plan Was Tested With Another Player")],["&fBuild a refuge, fallback room, alarm point, lit retreat route, or emergency-supply station useful during The Hordes or other world threats.","&fTest the plan with another player and fix at least one issue found during the drill."]),
        (9,"&dMEETING HALL / PUBLIC STAGE","minecraft:bell",[ck(ch,91,"REVIEW: The Space Hosted a Real Meeting, Ceremony, Performance, or Briefing")],["&fCreate a meeting hall, public stage, council table, courtroom, chapel, tavern room, or outdoor forum and actually use it for one event.","&fA room becomes history when somebody can say what happened there."]),
    ]
    pids=[]; xs=[-6,-4.2,-2.2,0,2.2,4.2,6,0]; ys=[-1.3,0.5,-0.5,1.0,-0.5,0.5,-1.3,3]
    for i,(n,tit,icon,tasks,body) in enumerate(infra):
        pid=qid(ch,n); pids.append(pid); qs.append(Quest(pid,tit,"Server-wide creative milestone · peer/host review.",lines("minecraft:textures/item/lantern.png","&6&lPUBLIC WORK",*body,"","&eScope:&f the physical project is server-wide even though FTB Quests records completion in the reviewing team's progress container."),icon,xs[i],ys[i],tasks,dependencies=[iroot],shape=["diamond","square","gear","hexagon","heart","diamond","square","octagon"][i]))
    infra_final=qid(ch,11)
    qs.append(Quest(infra_final,"&6&lFOUR THINGS THE ISLAND KEEPS", "Public work should still matter after everybody's inventory improves.", lines(
        "minecraft:textures/item/lantern.png","&6&lTHE PLACE IS STARTING TO HAVE A PAST",
        "&fFinish any four public works. Take one screenshot/map/book record of the finished set and place a copy in the archive or a public chest.",
        "",
        "&eTeam cache:&f lighting and scaffolding for maintenance. The reward funds upkeep rather than bypassing the next technology tier.",
        "",
        "&8Congratulations: you have invented municipal services in a game about punching trees."
    ),"minecraft:lantern",0,5.5,[ck(ch,111,"Archive One Record of the Four Public Works")],rewards=[plain_reward(ch,112,"Sixteen Maintenance Lanterns","minecraft:lantern",16,team=True),plain_reward(ch,113,"Thirty-Two Maintenance Scaffolding","minecraft:scaffolding",32,team=True),paper_reward(ch,114,"Civic Works Docket","Civic Works Docket","gold","Four public works survived long enough to become part of the island's story.",{"document":"public_works"},team=True)],dependencies=pids,min_required_dependencies=4,shape="hexagon",size=2.0,hide_until_deps_complete=True))
    c.chapters.append(Chapter(ch,"vvh_06_island_remembers","VvH 06 · The Island Remembers","minecraft:lantern",6,qs,chapter_images("minecraft:textures/item/lantern.png","minecraft:textures/item/filled_map.png","minecraft:textures/item/writable_book.png","minecraft:textures/item/lantern.png")))

    # 07 — Rivalry. Noncombat first, skirmish is gated behind actually having a funny rivalry.
    ch=0x17; qs=[]; rroot=qid(ch,1)
    qs.append(Quest(rroot,"&d&lRIVALRY WITHOUT RUIN", "Complete two noncombat formats before the skirmish even appears as a serious idea.", lines(
        "minecraft:textures/item/firework_rocket.png","&d&lTHE OBJECTIVE IS A STORY SOMEBODY RETELLS",
        "&fEvery challenge here is optional. Run any format that both sides understand, with a visible end condition and cleanup owner. Rewards are cosmetic/status or event supplies, never combat power.",
        "",
        "&cThe skirmish branch requires at least two noncombat rivalry activities first.&f If the factions cannot survive a mascot contest, they have not earned swords.",
        "",
        "&8Cold war, but the missiles are baked goods."
    ),"minecraft:firework_rocket",0,-5,[ck(ch,1,"Read the Safe-Rivalry Rules")],dependencies=[contribution_final],shape="hexagon",size=1.7))
    rivalry=[
        (2,"&dPROPAGANDA EXCHANGE","minecraft:painting",[ck(ch,21,"Both Sides Displayed a Reversible Poster/Banner/Exhibit")],["&fEach participating side makes one reversible public propaganda piece, banner display, museum label, or dramatic accusation about the other.","&fNo placing inside protected claims without permission. Cleanup deadline required."]),
        (3,"&eBLOOD VS GARLIC COOK-OFF","vampiresdelight:blood_pie",[ck(ch,31,"At Least 3 Players Judged or Attended the Cook-Off")],["&fRun a themed food contest using Vampire's Delight, Farmer's Delight, garlic, blood-themed cuisine, or absurd neutral entries.","&fJudge presentation, story, taste-by-roleplay, logistics, or whatever criteria are agreed before the event. Nobody has to consume food their faction mechanics dislike."]),
        (4,"&aSCAVENGER HUNT","minecraft:compass",[ck(ch,41,"A Hunt Was Completed and Every Clue Was Removed/Archived")],["&fPlace a short clue chain in public or explicitly permitted wilderness space. Finish with a harmless trophy, message, location reveal, or public project tour.","&fArchive the best clue afterward; remove anything that became litter."]),
        (5,"&bCOURIER / VEHICLE RACE","createpropulsion:wing",[ck(ch,51,"A Race Ran With a Published Route and Safety Rule")],["&fRun a foot, road, rail, boat, glider, or vehicle courier race. Publish the route, allowed transport, start/end, and one safety rule before launching.","&fReward a funny category as well as speed: best crash recovery, best courier uniform, most unnecessary engineering, etc."]),
        (6,"&6MARKET CHALLENGE","minecraft:emerald",[ck(ch,61,"A Timed Trade/Service Challenge Ended With a Public Result")],["&fGive both sides the same time window and goal: procure a themed bundle, provide a service, attract customers, or solve a public shortage.","&fNo fake transactions, item duplication, or quest-reward resale loops. The interesting part is organization and negotiation."]),
        (7,"&fMASCOT / ARCHITECTURE SHOWDOWN","minecraft:armor_stand",[ck(ch,71,"Both Sides Presented a Mascot, Mini-Build, or Ceremonial Object")],["&fEach side presents a reversible mascot, mini-build, float, outfit, ceremonial object, or one-chunk display. Neutrals judge or enter an independent category.","&fThe server keeps the funniest result only if its owner wants it kept."]),
    ]
    pids=[]; xs=[-5,-3,-1,1,3,5]; ys=[-1,0.8,-0.2,0.8,-0.2,-1]
    for i,(n,tit,icon,tasks,body) in enumerate(rivalry):
        pid=qid(ch,n); pids.append(pid); qs.append(Quest(pid,tit,"Optional social contest · reversible by design.",lines("minecraft:textures/item/firework_rocket.png","&d&lSAFE RIVALRY FORMAT",*body,"","&7Participation earns the story. Winning earns bragging rights, not better gear."),icon,xs[i],ys[i],tasks,dependencies=[rroot],optional=True,shape=["square","heart","diamond","gear","square","octagon"][i]))
    skirmish=qid(ch,8)
    qs.append(Quest(skirmish,"&cSANCTIONED SKIRMISH — ONLY IF EVERY BOX IS TRUE", "A release valve, not the campaign's central mechanic.", lines(
        "minecraft:textures/item/iron_sword.png","&c&lHOSTED, OPT-IN, BACKED UP",
        "&fOnly schedule this after at least two noncombat rivalry activities and when both factions actively want it.",
        "&fBefore start: roster, loadout ceiling, arena, spectator protection, inventory-loss rule, backup, stop command, restore plan, and rebuild owner.",
        "",
        "&eCompletion means the event ended safely and the world was restored/rebuilt as agreed.&f No reward depends on kills or winning.",
        "",
        "&cIf live PvP controls and backup restoration have not been tested, this quest is 'requires runtime verification' and must remain unused."
    ),"minecraft:shield",0,3.1,[ck(ch,81,"Host Confirms Consent, Backup, Controls, Stop Condition, and Safe End")],dependencies=pids,min_required_dependencies=2,optional=True,shape="diamond",size=1.4,hide_dependency_lines=True))
    rivalry_final=qid(ch,9)
    qs.append(Quest(rivalry_final,"&d&lARCHIVE A RIVALRY NIGHT", "Two silly contests are enough to make the factions feel real.", lines(
        "minecraft:textures/item/writable_book.png","&d&lKEEP THE JOKE, DELETE THE LITTER",
        "&fAfter any two rivalry formats, archive the result: winner if relevant, funniest incident, cleanup status, and one thing to change next time.",
        "",
        "&eReward:&f a team festival bundle. It helps stage the next event but contains no weapons or faction progression.",
        "",
        "&8History is what remains after the temporary banners come down."
    ),"minecraft:writable_book",0,5.4,[ck(ch,91,"Archive the Rivalry Result and Confirm Cleanup")],rewards=[plain_reward(ch,92,"Sixteen Firework Rockets","minecraft:firework_rocket",16,team=True),plain_reward(ch,93,"Two Cakes","minecraft:cake",2,team=True),paper_reward(ch,94,"Rivalry Night Broadside","Rivalry Night Broadside","light_purple","Proof that two factions can manufacture drama without manufacturing a crater.",{"document":"rivalry_night"},team=True)],dependencies=pids,min_required_dependencies=2,optional=True,shape="hexagon",size=1.8,hide_dependency_lines=True))
    c.chapters.append(Chapter(ch,"vvh_07_rivalry_without_ruin","VvH 07 · Rivalry Without Ruin","minecraft:firework_rocket",7,qs,chapter_images("minecraft:textures/item/firework_rocket.png","vampirism:textures/item/garlic.png","vampirism:textures/item/vampire_fang.png","minecraft:textures/item/filled_map.png")))

    # 08 — Capstone fair. Requires infrastructure but not rivalry attendance.
    ch=0x18; qs=[]; froot=qid(ch,1)
    qs.append(Quest(froot,"&6&lCALL THE LONG NIGHT FAIR", "Any four contributions; no perfect attendance required.", lines(
        "minecraft:textures/item/lantern.png","&6&lTHE SEASON ENDS WITH A PLACE FULL OF PEOPLE",
        "&fSchedule one public fair, tour night, festival, summit, or exhibition using infrastructure the server has actually built. Complete any &e4 of 6&f contribution categories.",
        "",
        "&7The event should expose unfinished hooks as well as achievements. A good finale creates reasons to log in next week instead of pretending the world is complete.",
        "",
        "&8Bring lanterns. Bring food. Bring the one machine everyone was told not to turn on indoors."
    ),"minecraft:lantern",0,-5,[ck(ch,1,"Date, Location, and Public Invitation Are Posted")],dependencies=[infra_final],shape="hexagon",size=1.7))
    fair=[
        (2,"&4HOUSE OF NIGHT HOSPITALITY","vampiresdelight:blood_wine_bottle",[ck(ch,21,"Vampire-Themed Hospitality, Ritual, Tour, or Exhibit Was Hosted")],["&fProvide a House contribution: Vampire's Delight table, faction tour, archive reading, ritual demonstration, night-route walk, or aesthetic exhibit.","&fGuests are not required to become Vampires, fight, or participate in feeding mechanics."]),
        (3,"&bLANTERN ORDER SERVICE","vampirism:garlic",[ck(ch,31,"Hunter-Themed Safety, Craft, Route, or Public-Service Exhibit Was Hosted")],["&fProvide an Order contribution: safety demo, public route briefing, workstation tour, rescue drill, garlic-themed table, or countermeasure museum.","&fThe point is public service and faction character, not target practice on unwilling guests."]),
        (4,"&aFREE COMPANY MARKET","minecraft:emerald",[ck(ch,41,"Neutral Market, Contract Desk, Mediation Table, or Courier Service Operated")],["&fRun a neutral contribution: trades, contracts, map desk, courier service, guesthouse, arbitration, MCA civic exhibit, or event logistics.","&fAt least one interaction should cross faction lines."]),
        (5,"&6ENGINEERING / AERONAUTICS EXHIBITION","createpropulsion:wing",[ck(ch,51,"A Machine, Vehicle, Dock, Workshop, or Controlled Test Was Demonstrated")],["&fDemonstrate a Create system, vehicle, airframe, dock, rail feature, workshop, or safely controlled engineering failure.","&fDesign the spectator area before discovering why propellers need spectator areas."]),
        (6,"&ePUBLIC FEAST / PERFORMANCE","minecraft:bread",[ck(ch,61,"A Shared Meal, Performance, Game, or Ceremony Served the Event")],["&fProvide food, music/performance, mini-game, ceremony, awards, speeches, guided tour, or another contribution that gives players something to do together rather than merely inspect chests.","&fUse Farmer's Delight/Vampire's Delight if useful; ordinary Minecraft food is also valid."]),
        (7,"&fARCHIVE THE SEASON","minecraft:writable_book",[ck(ch,71,"At Least 5 Season Facts, Images, Maps, Quotes, or Results Were Archived")],["&fBefore the event ends, archive at least five concrete pieces of history: faction changes, projects, rivalry results, failures, screenshots/maps, quotes, contracts, deaths worth remembering, or unfinished hooks.","&fFuture players should be able to reconstruct Season One without asking for a three-hour Discord oral history."]),
    ]
    pids=[]; xs=[-5,-3,-1,1,3,5]; ys=[-1.1,0.8,-0.2,0.8,-0.2,-1.1]
    for i,(n,tit,icon,tasks,body) in enumerate(fair):
        pid=qid(ch,n); pids.append(pid); qs.append(Quest(pid,tit,"Capstone contribution · one real event output.",lines("minecraft:textures/item/lantern.png","&6&lLONG NIGHT CONTRIBUTION",*body),icon,xs[i],ys[i],tasks,dependencies=[froot],shape=["heart","diamond","square","gear","circle","octagon"][i]))
    fair_final=qid(ch,9)
    qs.append(Quest(fair_final,"&6&lSEAL SEASON ONE", "The reward is useful. The world you built is the actual progression.", lines(
        "minecraft:textures/item/firework_rocket.png","&6&lAFTER THE BELLS",
        "&fComplete any four Fair contributions, then record one unresolved pressure or ambition that players genuinely want to continue.",
        "&fExamples: faction politics, a vehicle project, settlement story, Hordes defense, public work, expedition, magic problem, or infrastructure failure.",
        "",
        "&eClaim a commemorative Seal and one horizontal favor.&f No boss loot, faction levels, rare weapons, netherite, or finished late-game machine is hidden here.",
        "",
        "&8A season is complete when it produces a sequel hook, not when the todo list reaches zero."
    ),"minecraft:firework_rocket",0,5.2,[ck(ch,91,"Archive the Fair and One Genuine Future Hook")],rewards=[paper_reward(ch,92,"Season One Seal","Season One Seal — Long Night Fair","gold","The island became worth remembering before the gear made it easy.",{"document":"season_one_seal"},team=False),choice_reward(ch,93,"Choose a Long Night Fair Favor",FAIR_TABLE)],dependencies=pids,min_required_dependencies=4,shape="hexagon",size=2.1,hide_until_deps_complete=True))
    c.chapters.append(Chapter(ch,"vvh_08_long_night_fair","VvH 08 · The Long Night Fair","minecraft:lantern",8,qs,chapter_images("minecraft:textures/item/lantern.png","minecraft:textures/item/firework_rocket.png","vampirism:textures/item/vampire_fang.png","vampirism:textures/item/garlic.png")))

    # 09 — Limited postgame civic sinks. No faction arms subsidies.
    ch=0x19; qs=[]; proot=qid(ch,1)
    qs.append(Quest(proot,"&6&lAFTER THE BELLS", "Weekly convenience without a treadmill.", lines(
        "numismatics:textures/item/coin/bevel.png","&6&lCIVIC REQUISITIONS",
        "&fThe season is over. These optional seven-day exchanges turn existing Bevels into small public-use caches for maintenance and events.",
        "",
        "&fPrices are visible, inputs are consumed, and no output creates Bevels, faction levels, weapons, blood, hunter tech, or another item that cheaply reproduces its own price.",
        "",
        "&eAgree on payer and destination before submitting.&f A team reward exists once per FTB progress container; it is not one cache per teammate.",
        "",
        "&8Postgame inflation remains undefeated by vibes."
    ),"numismatics:bevel",0,-5,[ck(ch,1,"Read the Civic Requisition Terms")],dependencies=[fair_final],shape="hexagon",size=1.7))

    def exchange(n: int, title: str, subtitle: str, icon: str, x: float, y: float, price: int, body: list[str], rewards: list[tuple[str,int,str]]) -> Quest:
        return Quest(qid(ch,n),title,subtitle,lines("numismatics:textures/item/coin/bevel.png","&6&lWEEKLY TEAM CACHE",*body,"",f"&ePrice:&f {price} Bevel{'s' if price != 1 else ''}. &7Renews seven days after this FTB team claims it."),icon,x,y,[item_task(ch,n*10+1,f"Submit {price} Bevel{'s' if price != 1 else ''}","numismatics:bevel",price,consume=True)],rewards=[plain_reward(ch,n*10+2+i,rt,item,count,team=True) for i,(item,count,rt) in enumerate(rewards)],dependencies=[proot],optional=True,can_repeat=True,repeat_cooldown=604800,shape="gear")
    qs.append(exchange(2,"&eLIGHTING REQUISITION — 1 BEVEL","Roads, halls, refuge routes, and events.","minecraft:lantern",-5,-1,1,["&fReceive sixteen Lanterns and thirty-two Torches for a named public route, refuge, hall, or event."],[("minecraft:lantern",16,"Sixteen Public Lanterns"),("minecraft:torch",32,"Thirty-Two Public Torches")]))
    qs.append(exchange(3,"&6TRANSIT REQUISITION — 2 BEVELS","A modest rail cache; still requires engineering.","minecraft:rail",-2.5,0.3,2,["&fReceive thirty-two Rails and eight Powered Rails. Stations, redstone, route design, and locomotion remain your problem."],[("minecraft:rail",32,"Thirty-Two Rails"),("minecraft:powered_rail",8,"Eight Powered Rails")]))
    qs.append(exchange(4,"&dFESTIVAL REQUISITION — 1 BEVEL","Consumable celebration with a cleanup owner.","minecraft:firework_rocket",0,0.8,1,["&fReceive sixteen Firework Rockets and two Cakes for a scheduled public event. Please do not turn fireworks into a server benchmark."],[("minecraft:firework_rocket",16,"Sixteen Festival Rockets"),("minecraft:cake",2,"Two Event Cakes")]))
    qs.append(exchange(5,"&aREPAIR REQUISITION — 1 BEVEL","For temporary access and moving parts.","create:super_glue",2.5,0.3,1,["&fReceive four Super Glue and thirty-two Scaffolding. Record which public work received the cache."],[("create:super_glue",4,"Four Super Glue"),("minecraft:scaffolding",32,"Thirty-Two Scaffolding")]))
    qs.append(exchange(6,"&cHOSPITALITY REQUISITION — 1 BEVEL","Meetings, late arrivals, fairs, and rescue runs.","minecraft:bread",5,-1,1,["&fReceive sixteen Bread and eight Cooked Beef. Faction-specific cuisine remains player-crafted rather than quest-subsidized."],[("minecraft:bread",16,"Sixteen Bread"),("minecraft:cooked_beef",8,"Eight Cooked Beef")]))
    qs.append(Quest(qid(ch,7),"&fARCHIVE A NEW RUMOUR","One paragraph, one real place, one actionable question.",lines("minecraft:textures/item/writable_book.png","&f&lTURN AN UNFINISHED THING INTO A HOOK","&fWrite a short rumour tied to a real location, player ambition, faction dispute, settlement, threat, unfinished machine, public work, or mystery.","&fEnd with a question somebody could act on next session.","","&7This renews weekly and intentionally grants no item. The archive should create play, not currency."),"minecraft:writable_book",-2.5,4.5,[ck(ch,71,"I Added One Actionable Rumour")],dependencies=[proot],optional=True,can_repeat=True,repeat_cooldown=604800,shape="square"))
    qs.append(Quest(qid(ch,9),"&eLEAVE A SEASON TWO PRESSURE","Do not pre-author a sequel nobody wants yet.",lines("minecraft:textures/item/filled_map.png","&e&lNAME THE NEXT PRESSURE","&fChoose one unresolved pressure worth a future season and record stakeholders plus evidence that people actually care about it.","&fGood candidates include Vampirism politics, a settlement story, an airship project, Hordes defense, border expansion, infrastructure failure, expedition, magical incident, or a rivalry that acquired consequences.","","&eTeam keepsake:&f one Unresolved Pressure Docket."),"minecraft:filled_map",2.5,4.5,[ck(ch,91,"We Recorded One Evidence-Based Season Two Hook")],rewards=[paper_reward(ch,92,"Unresolved Pressure Docket","Unresolved Pressure Docket","yellow","A future season begins only when the world supplies evidence.",{"document":"season_two_hook"},team=True)],dependencies=[proot],optional=True,shape="heart"))
    c.chapters.append(Chapter(ch,"vvh_09_after_the_bells","VvH 09 · After the Bells","numismatics:bevel",9,qs,chapter_images("numismatics:textures/item/coin/bevel.png","minecraft:textures/item/lantern.png","minecraft:textures/item/firework_rocket.png")))

    # Choice tables. Fixed, horizontal, no faction-specific combat progression.
    role_rewards=[
        ("builder","Builder Lens","yellow","Improve the experience of places."),
        ("engineer","Engineer Lens","gold","Make motion, power, or logistics useful."),
        ("pathfinder","Pathfinder Lens","aqua","Turn distance into routes other people can follow."),
        ("keeper","Keeper Lens","green","Maintain food, hospitality, supplies, and continuity."),
        ("arcanist","Arcanist Lens","light_purple","Make magic and supernatural systems understandable."),
        ("archivist","Archivist Lens","white","Preserve guides, contracts, failures, and server memory."),
    ]
    c.reward_tables.append({"id":ROLE_TABLE,"title":"Choose a Personal Trade Lens","order_index":10,"rewards":[{"id":f"7A11C0DEF001{i:04X}","title":name,"item_data":custom_paper(name,color,lore,{"role":key})} for i,(key,name,color,lore) in enumerate(role_rewards,1)]})
    c.reward_tables.append({"id":TRADE_TABLE,"title":"Choose a Practical Contribution Favor","order_index":11,"rewards":[
        {"id":"7A11C0DEF0020001","title":"Eight Andesite Alloy","item":"create:andesite_alloy","count":8},
        {"id":"7A11C0DEF0020002","title":"Twelve Arcane Essence","item":"irons_spellbooks:arcane_essence","count":12},
        {"id":"7A11C0DEF0020003","title":"Thirty-Two Scaffolding","item":"minecraft:scaffolding","count":32},
        {"id":"7A11C0DEF0020004","title":"Eight Super Glue","item":"create:super_glue","count":8},
    ]})
    c.reward_tables.append({"id":FAIR_TABLE,"title":"Choose a Long Night Fair Favor","order_index":12,"rewards":[
        {"id":"7A11C0DEF0030001","title":"Create Goggles","item":"create:goggles","count":1},
        {"id":"7A11C0DEF0030002","title":"Nature's Compass","item":"naturescompass:naturescompass","count":1},
        {"id":"7A11C0DEF0030003","title":"Sixteen Lanterns","item":"minecraft:lantern","count":16},
        {"id":"7A11C0DEF0030004","title":"Thirty-Two Rails","item":"minecraft:rail","count":32},
    ]})
    return c

def snbt_value(value: Any, indent: int = 0) -> str:
    pad = "\t" * indent
    if isinstance(value, bool):
        return "true" if value else "false"
    if isinstance(value, str):
        return jstr(value)
    if isinstance(value, int):
        return str(value)
    if isinstance(value, float):
        num = f"{value:.2f}".rstrip("0").rstrip(".")
        if "." not in num:
            num += ".0"
        return num + "d"
    if isinstance(value, list):
        if not value:
            return "[ ]"
        parts = [snbt_value(v, indent + 1) for v in value]
        return "[\n" + "\n".join(("\t" * (indent + 1)) + p for p in parts) + "\n" + pad + "]"
    if isinstance(value, dict):
        if not value:
            return "{ }"
        parts = []
        for k, v in value.items():
            key = jstr(k) if ":" in k else k
            rendered = snbt_value(v, indent + 1)
            parts.append(("\t" * (indent + 1)) + f"{key}: {rendered}")
        return "{\n" + "\n".join(parts) + "\n" + pad + "}"
    raise TypeError(value)


def render_item(item_data: dict[str, Any]) -> dict[str, Any]:
    out: dict[str, Any] = {}
    if item_data.get("components"):
        out["components"] = item_data["components"]
    out["count"] = item_data.get("count", 1)
    out["id"] = item_data["id"]
    return out


def task_obj(task: Task) -> dict[str, Any]:
    out: dict[str, Any] = {"id": task.id}
    if task.type == "item":
        if task.consume:
            out["consume_items"] = True
        if task.count != 1:
            out["count"] = task.count
        out["item"] = {"count": 1, "id": task.item}
    elif task.type == "advancement":
        out["advancement"] = task.advancement
        out["criterion"] = task.criterion
    elif task.type == "stat":
        out["stat"] = task.stat
        out["value"] = task.value
    if task.optional:
        out["optional"] = True
    out["type"] = task.type
    return out


def reward_obj(reward: Reward) -> dict[str, Any]:
    out: dict[str, Any] = {}
    if reward.exclude_from_claim_all:
        out["exclude_from_claim_all"] = True
    out["id"] = reward.id
    if reward.type == "choice":
        assert reward.table_id
        out["table_id"] = int(reward.table_id, 16)
    else:
        if reward.item_data:
            out["item"] = render_item(reward.item_data)
        else:
            out["item"] = {"count": reward.count, "id": reward.item}
    out["team_reward"] = reward.team_reward
    out["type"] = reward.type
    return out


def quest_obj(quest: Quest) -> dict[str, Any]:
    out: dict[str, Any] = {}
    if quest.can_repeat:
        out["can_repeat"] = True
    if quest.dependencies:
        out["dependencies"] = quest.dependencies
    if quest.hide_until_deps_complete:
        out["hide_until_deps_complete"] = True
    if quest.hide_dependency_lines:
        out["hide_dependency_lines"] = True
    out["icon"] = {"id": quest.icon}
    out["id"] = quest.id
    if quest.min_required_dependencies:
        out["min_required_dependencies"] = quest.min_required_dependencies
    out["min_width"] = quest.min_width
    if quest.optional:
        out["optional"] = True
    if quest.repeat_cooldown:
        out["repeat_cooldown"] = quest.repeat_cooldown
    if quest.rewards:
        out["rewards"] = [reward_obj(r) for r in quest.rewards]
    out["shape"] = quest.shape
    out["size"] = quest.size
    out["tasks"] = [task_obj(t) for t in quest.tasks]
    out["x"] = quest.x
    out["y"] = quest.y
    return out


def render_chapter(chapter: Chapter) -> str:
    obj: dict[str, Any] = {
        "autofocus_id": chapter.quests[0].id,
        "default_hide_dependency_lines": False,
        "default_quest_shape": "circle",
        "filename": chapter.filename,
        "group": GROUP_ID,
        "icon": {"id": chapter.icon},
        "id": chapter.id,
    }
    if chapter.images:
        obj["images"] = chapter.images
    obj["order_index"] = chapter.order
    obj["progression_mode"] = "flexible"
    obj["quest_links"] = []
    obj["quests"] = [quest_obj(q) for q in chapter.quests]
    return snbt_value(obj) + "\n"


def render_reward_table(table: dict[str, Any]) -> str:
    rewards = []
    for reward in table["rewards"]:
        out = {"id": reward["id"]}
        if reward.get("item_data"):
            out["item"] = render_item(reward["item_data"])
        else:
            out["item"] = {"count": reward.get("count", 1), "id": reward["item"]}
        rewards.append(out)
    obj = {
        "id": table["id"],
        "loot_size": 1,
        "order_index": table["order_index"],
        "use_title": True,
        "rewards": rewards,
    }
    return snbt_value(obj) + "\n"


def render_lang(campaign: Campaign) -> str:
    out: list[str] = []
    out.append(f"\tfile.vvh_campaign_version: {jstr(VERSION)}")
    out.append(f"\tchapter_group.{GROUP_ID}.title: {jstr('Vampires vs Hunters — Season One')}")
    for table in campaign.reward_tables:
        out.append(f"\treward_table.{table['id']}.title: {jstr(table['title'])}")
        for reward in table["rewards"]:
            out.append(f"\treward.{reward['id']}.title: {jstr(reward['title'])}")
    for chapter in campaign.chapters:
        out.append("")
        out.append(f"\tchapter.{chapter.id}.title: {jstr(chapter.title)}")
        for quest in chapter.quests:
            out.append(f"\tquest.{quest.id}.quest_desc: [")
            for line in quest.desc:
                out.append(f"\t\t{jstr(line)}")
            out.append("\t]")
            out.append(f"\tquest.{quest.id}.quest_subtitle: {jstr(quest.subtitle)}")
            out.append(f"\tquest.{quest.id}.title: {jstr(quest.title)}")
            for task in quest.tasks:
                out.append(f"\ttask.{task.id}.title: {jstr(task.title)}")
            for reward in quest.rewards:
                out.append(f"\treward.{reward.id}.title: {jstr(reward.title)}")
    return "\n".join(out) + "\n"


def update_lang(path: Path, block: str) -> None:
    start = "\t// BEGIN VvH SEASON ONE"
    end = "\t// END VvH SEASON ONE"
    text = path.read_text(encoding="utf-8")
    pattern = re.compile(r"\n?\t// BEGIN VvH SEASON ONE.*?\t// END VvH SEASON ONE\n?", re.S)
    text = pattern.sub("\n", text)
    idx = text.rfind("}")
    if idx < 0:
        raise RuntimeError(f"No closing brace in {path}")
    insertion = f"\n{start}\n{block}{end}\n"
    text = text[:idx].rstrip() + insertion + text[idx:]
    path.write_text(text, encoding="utf-8")


def update_chapter_groups(path: Path) -> None:
    text = path.read_text(encoding="utf-8")
    if GROUP_ID in text:
        return
    title = "Vampires vs Hunters — Season One"
    path.write_text("{\n\tchapter_groups: [\n\t\t{ id: \"%s\", title: %s }\n\t]\n}\n" % (GROUP_ID, jstr(title)), encoding="utf-8")


def _replace_once(text: str, old: str, new: str, label: str) -> str:
    if old not in text:
        raise RuntimeError(f"Legacy Atlas migration expected {label}, but the pinned dev source no longer matches")
    return text.replace(old, new, 1)


def _replace_lang_desc(text: str, quest_id: str, desc: list[str]) -> str:
    pattern = re.compile(rf"\tquest\.{re.escape(quest_id)}\.quest_desc: \[\n.*?\n\t\]\n", re.S)
    rendered = f"\tquest.{quest_id}.quest_desc: [\n" + "\n".join(f"\t\t{jstr(line)}" for line in desc) + "\n\t]\n"
    text2, n = pattern.subn(rendered, text, count=1)
    if n != 1:
        raise RuntimeError(f"Could not replace legacy quest description {quest_id}")
    return text2


def _replace_lang_scalar(text: str, key: str, value: str) -> str:
    pattern = re.compile(rf"^(\t{re.escape(key)}:\s*).*$", re.M)
    text2, n = pattern.subn(rf"\1{jstr(value)}", text, count=1)
    if n != 1:
        raise RuntimeError(f"Could not replace legacy translation {key}")
    return text2


def migrate_legacy_atlas(root: Path) -> None:
    """Repair Living Atlas content invalidated by the dev branch's Cobblemon removal.

    Existing object IDs and chapter topology are deliberately preserved so any existing
    FTB Quests progress remains attached to the same quest/task/reward objects. Only
    the removed mod references and player-facing semantics are migrated.
    """
    chapters = root / "config/ftbquests/quests/chapters"
    tables = root / "config/ftbquests/quests/reward_tables"
    lang_probe = root / "config/ftbquests/quests/lang/en_us.snbt"
    probe_paths = list(chapters.glob("*.snbt")) + list(tables.glob("*.snbt")) + ([lang_probe] if lang_probe.exists() else [])
    if not any("cobblemon:" in path.read_text(encoding="utf-8").lower() for path in probe_paths):
        return

    p = chapters / "a_blank_page.snbt"
    text = p.read_text(encoding="utf-8")
    text = text.replace('image: "cobblemon:textures/item/poke_balls/poke_ball.png"', 'image: "vampirism:textures/item/garlic.png"')
    text = text.replace('icon: { id: "cobblemon:poke_ball" }', 'icon: { id: "vampirism:garlic" }', 1)
    text = _replace_once(text, '''\t\t\t\t{\n\t\t\t\t\tid: "1A0B1A4E5A9E0011"\n\t\t\t\t\tstat: "cobblemon:captured"\n\t\t\t\t\ttype: "stat"\n\t\t\t\t\tvalue: 2\n\t\t\t\t}''', '''\t\t\t\t{\n\t\t\t\t\tcount: 2\n\t\t\t\t\tid: "1A0B1A4E5A9E0011"\n\t\t\t\t\titem: { count: 1, id: "vampirism:garlic" }\n\t\t\t\t\ttype: "item"\n\t\t\t\t}''', "Session 00 removed capture stat")
    text = _replace_once(text, '''\t\t\t\t{\n\t\t\t\t\tid: "1A0B1A4E5A9E0012"\n\t\t\t\t\tstat: "cobblemon:battles_total"\n\t\t\t\t\ttype: "stat"\n\t\t\t\t\tvalue: 1\n\t\t\t\t}''', '''\t\t\t\t{\n\t\t\t\t\tcount: 4\n\t\t\t\t\tid: "1A0B1A4E5A9E0012"\n\t\t\t\t\titem: { count: 1, id: "create:andesite_alloy" }\n\t\t\t\t\ttype: "item"\n\t\t\t\t}''', "Session 00 removed battle stat")
    p.write_text(text, encoding="utf-8")

    p = chapters / "first_resonance.snbt"
    text = p.read_text(encoding="utf-8")
    text = text.replace('icon: { id: "cobblemon:poke_ball" }', 'icon: { id: "vampirism:vampire_fang" }', 1)
    text = _replace_once(text, '''\t\t\t\t{\n\t\t\t\t\tid: "1A0B1A4E5A9E0121"\n\t\t\t\t\tstat: "cobblemon:captured"\n\t\t\t\t\ttype: "stat"\n\t\t\t\t\tvalue: 5\n\t\t\t\t}''', '''\t\t\t\t{\n\t\t\t\t\tid: "1A0B1A4E5A9E0121"\n\t\t\t\t\titem: { count: 1, id: "vampirism:vampire_fang" }\n\t\t\t\t\ttype: "item"\n\t\t\t\t}''', "First Resonance removed capture task")
    text = _replace_once(text, '''\t\t\t\t{\n\t\t\t\t\tid: "1A0B1A4E5A9E0122"\n\t\t\t\t\tstat: "cobblemon:battles_total"\n\t\t\t\t\ttype: "stat"\n\t\t\t\t\tvalue: 3\n\t\t\t\t}''', '''\t\t\t\t{\n\t\t\t\t\tadvancement: "vampirism:main/vampire_forest"\n\t\t\t\t\tcriterion: ""\n\t\t\t\t\tid: "1A0B1A4E5A9E0122"\n\t\t\t\t\ttype: "advancement"\n\t\t\t\t}''', "First Resonance removed battle task")
    text = _replace_once(text, '''\t\t\t\t{\n\t\t\t\t\tid: "1A0B1A4E5A9E0161"\n\t\t\t\t\tstat: "cobblemon:battles_total"\n\t\t\t\t\ttype: "stat"\n\t\t\t\t\tvalue: 5\n\t\t\t\t}''', '''\t\t\t\t{\n\t\t\t\t\tcount: 8\n\t\t\t\t\tid: "1A0B1A4E5A9E0161"\n\t\t\t\t\titem: { count: 1, id: "minecraft:lantern" }\n\t\t\t\t\ttype: "item"\n\t\t\t\t}''', "First Resonance removed group battle task")
    p.write_text(text, encoding="utf-8")

    p = chapters / "the_weathered_ledger.snbt"
    text = p.read_text(encoding="utf-8")
    text = text.replace('icon: { id: "cobblemon:poke_ball" }', 'icon: { id: "vampirism:vampire_fang" }', 1)
    text = _replace_once(text, '''\t\t\t\t{\n\t\t\t\t\tid: "1A0B1A4E5A9E0361"\n\t\t\t\t\tstat: "cobblemon:captured"\n\t\t\t\t\ttype: "stat"\n\t\t\t\t\tvalue: 8\n\t\t\t\t}''', '''\t\t\t\t{\n\t\t\t\t\tadvancement: "vampirism:main/vampire_forest"\n\t\t\t\t\tcriterion: ""\n\t\t\t\t\tid: "1A0B1A4E5A9E0361"\n\t\t\t\t\ttype: "advancement"\n\t\t\t\t}''', "Weathered Ledger removed capture task")
    text = _replace_once(text, '''\t\t\t\t{\n\t\t\t\t\tid: "1A0B1A4E5A9E0362"\n\t\t\t\t\tstat: "cobblemon:battles_total"\n\t\t\t\t\ttype: "stat"\n\t\t\t\t\tvalue: 8\n\t\t\t\t}''', '''\t\t\t\t{\n\t\t\t\t\tcount: 8\n\t\t\t\t\tid: "1A0B1A4E5A9E0362"\n\t\t\t\t\titem: { count: 1, id: "vampiresdelight:hardtack" }\n\t\t\t\t\ttype: "item"\n\t\t\t\t}''', "Weathered Ledger removed battle task")
    p.write_text(text, encoding="utf-8")

    p = chapters / "atlas_exchange.snbt"
    text = p.read_text(encoding="utf-8")
    text = text.replace('icon: { id: "cobblemon:great_ball" }', 'icon: { id: "vampiresdelight:hardtack" }')
    text = text.replace('item: { count: 1, id: "cobblemon:great_ball" }', 'item: { count: 1, id: "vampiresdelight:hardtack" }')
    text = re.sub(r'count: 4(?=\s+id: \"1A0B1A4E5A9E0671\")', 'count: 16', text, count=1)
    p.write_text(text, encoding="utf-8")

    for table_name in ("1A0B1A4E5A9E2000.snbt", "1A0B1A4E5A9E3000.snbt"):
        p = tables / table_name
        text = p.read_text(encoding="utf-8")
        text = text.replace('item: { count: 12, id: "cobblemon:poke_ball" }', 'item: { count: 16, id: "vampiresdelight:hardtack" }')
        p.write_text(text, encoding="utf-8")

    lang = root / "config/ftbquests/quests/lang/en_us.snbt"
    text = lang.read_text(encoding="utf-8")
    text = _replace_lang_desc(text, "1A0B1A4E5A9E0002", [
        "{image:minecraft:textures/item/writable_book.png width:48 height:48 align:center}",
        "&e&lWELCOME, TINY CARTOGRAPHER — DEV EDITION", "",
        "&fThe pack changed underneath this old Atlas page, so the removed Cobblemon chores have been migrated without changing quest IDs or wiping progress.", "",
        "&b1. &fCarry two Vampirism Garlic.",
        "&b2. &fCarry four Create Andesite Alloy.",
        "&b3. &fReturn near world spawn with another real player and both click your own rally checkmark.", "",
        "&7Existing completion stays attached to the same task IDs. New players get objectives that actually exist in the dev modlist.", "",
        "&8The Atlas survived a total ecosystem replacement. Relatable."
    ])
    text = _replace_lang_desc(text, "1A0B1A4E5A9E0003", [
        "{image:vampirism:textures/item/garlic.png width:48 height:48 align:center}", "&a&lFIELD SUPPLY: GARLIC", "",
        "&fCarry &e2 Vampirism Garlic&f. Nothing is consumed. This replaces the removed catch-stat task while preserving its original FTB object ID.", "",
        "&7Find, grow, trade, or borrow it. The tutorial is checking that you touched the current supernatural ecology, not that you picked a faction.", "",
        "&8Yes, the vampire campaign begins with garlic. The book enjoys tension."
    ])
    text = _replace_lang_desc(text, "1A0B1A4E5A9E0004", [
        "{image:create:textures/item/andesite_alloy.png width:48 height:48 align:center}", "&6&lFIELD SUPPLY: ANDESITE ALLOY", "",
        "&fCarry &e4 Andesite Alloy&f. Nothing is consumed. This replaces the removed battle-stat task and keeps the tutorial connected to a system that still exists on dev.", "",
        "&7Craft, trade, or receive help. The Atlas is measuring contact with the pack, not moral purity about crafting everything alone.", "",
        "&8A machine is a spell that filed better documentation."
    ])
    text = _replace_lang_desc(text, "1A0B1A4E5A9E0007", [
        "{image:minecraft:textures/item/firework_rocket.png width:48 height:48 align:center}", "&a&lNOW CAUSE PROBLEMS (COOPERATIVELY)", "",
        "&fYou finished Session 00. The current dev pack now revolves much more strongly around Vampirism, Create/Aeronautics, magic, civic play, building, and social systems.", "",
        "&bSuggested afterparty:&f compare Garlic acquisition stories, tour a first Create contraption, find out why the woods suddenly feel less friendly, or help a late arrival finish their page.", "",
        "&8The tutorial is over. The consequences have fangs."
    ])
    text = _replace_lang_scalar(text, "quest.1A0B1A4E5A9E0003.title", "&a&lCARRY 2: Field Garlic")
    text = _replace_lang_scalar(text, "quest.1A0B1A4E5A9E0003.quest_subtitle", "Two garlic. Zero consumption. One extremely relevant new mod.")
    text = _replace_lang_scalar(text, "quest.1A0B1A4E5A9E0004.title", "&6&lCARRY 4: Andesite Alloy")
    text = _replace_lang_scalar(text, "quest.1A0B1A4E5A9E0004.quest_subtitle", "A tiny Create touchpoint instead of a removed battle stat.")
    text = _replace_lang_scalar(text, "task.1A0B1A4E5A9E0011.title", "Carry Two Vampirism Garlic")
    text = _replace_lang_scalar(text, "task.1A0B1A4E5A9E0012.title", "Carry Four Andesite Alloy")

    text = _replace_lang_desc(text, "1A0B1A4E5A9E0102", [
        "{image:vampirism:textures/item/vampire_fang.png width:48 height:48 align:center}", "&4&lDUSK-LENS: THE NEW ECOLOGY", "",
        "&fCarry one &eVampire Fang&f and discover the &eVampire Forest&f advancement. Nothing is consumed.", "",
        "&7This migrated route replaces removed Cobblemon lifetime statistics while keeping the old quest/task IDs, so existing team progress remains attached.", "",
        "&8The stars were replaced by teeth. Budget cuts."
    ])
    text = _replace_lang_scalar(text, "quest.1A0B1A4E5A9E0102.title", "&4&lDUSK-LENS: FANG & FOREST")
    text = _replace_lang_scalar(text, "quest.1A0B1A4E5A9E0102.quest_subtitle", "One fang. One vampire forest. Current pack, same quest ID.")
    text = _replace_lang_scalar(text, "task.1A0B1A4E5A9E0121.title", "Carry One Vampire Fang")
    text = _replace_lang_scalar(text, "task.1A0B1A4E5A9E0122.title", "Discover a Vampire Forest")

    text = _replace_lang_desc(text, "1A0B1A4E5A9E0106", [
        "{image:minecraft:textures/item/lantern.png width:48 height:48 align:center}", "&3&lCHORUS-LENS: A GROUP WITH A DESTINATION", "",
        "&fCarry &e8 Lanterns&f, then tick the second task after joining at least one other player for a real outing: exploration, build tour, route test, rescue, faction visit, or public-work trip.", "",
        "&7This preserves the old social-route IDs without depending on the removed Cobblemon battle/raid system.", "",
        "&8A victory still sounds better with witnesses; the victory just has fewer hit points now."
    ])
    text = _replace_lang_scalar(text, "task.1A0B1A4E5A9E0161.title", "Carry Eight Lanterns")

    text = _replace_lang_desc(text, "1A0B1A4E5A9E0306", [
        "{image:vampirism:textures/item/vampire_fang.png width:48 height:48 align:center}", "&3&lCHORUS-LENS: STRANGE ROADS, REAL WITNESSES", "",
        "&fDiscover a &eVampire Forest&f, carry &e8 Hardtack&f, then tick the last box after completing the trip or field test with another player.", "",
        "&7This migrated route occupies the old Cobblemon social-route IDs. The objective is current-pack exploration plus a shared story, not faction membership or combat.", "",
        "&8Please allow the ominous biome to make at least one tactical recommendation."
    ])
    text = _replace_lang_scalar(text, "task.1A0B1A4E5A9E0361.title", "Discover a Vampire Forest")
    text = _replace_lang_scalar(text, "task.1A0B1A4E5A9E0362.title", "Carry Eight Hardtack")

    text = _replace_lang_desc(text, "1A0B1A4E5A9E0407", [
        "{image:vampiresdelight:textures/item/hardtack.png width:48 height:48 align:center}", "&d&lHARDTACK TRAVEL CACHE", "",
        "&fSpend the existing Bevel price for &e16 Vampire's Delight Hardtack&f. The old Great Ball offer referenced a mod removed from dev; this keeps the exchange slot and object IDs alive.", "",
        "&7The output is cheap travel food, not Vampire rank, blood, weapons, or a faction progression skip.", "",
        "&8The exchange has pivoted from pocket monsters to haunted municipal lighting."
    ])
    text = _replace_lang_scalar(text, "quest.1A0B1A4E5A9E0407.title", "&d&lHARDTACK TRAVEL CACHE")
    text = _replace_lang_scalar(text, "quest.1A0B1A4E5A9E0407.quest_subtitle", "Sixteen travel rations; zero deleted namespaces.")
    text = _replace_lang_scalar(text, "reward.1A0B1A4E5A9E0671.title", "&e16 Hardtack")
    text = _replace_lang_scalar(text, "reward.1A0B1A4E5A9E3013.title", "&e16 Hardtack")

    # Remaining prose references are migration copy, not object IDs. Replace them intentionally.
    substitutions = {
        "Management is a Slowpoke.": "Management is currently hiding from a vampire hunter.",
        "Poke Balls": "Hardtack",
        "Poke Ball": "Hardtack",
        "rare Pokemon": "faction levels",
        "Rare Pokemon": "Faction levels",
        "Pokemon": "fieldwork",
        "Pokémon": "fieldwork",
        "Cobblemon": "the removed creature system",
        "Raid Den": "group field",
        "cobblemon:textures/item/poke_balls/poke_ball.png": "vampirism:textures/item/garlic.png",
        "cobblemon:textures/gui/battle/battle_menu_fight.png": "vampirism:textures/item/vampire_fang.png",
        "cobblemon:textures/item/poke_balls/great_ball.png": "vampiresdelight:textures/item/hardtack.png",
    }
    for old, new in substitutions.items():
        text = text.replace(old, new)
    if re.search(r"cobblemon:|cobblemon|poke ?ball|pok[eé]mon", text, re.I):
        raise RuntimeError("Legacy Atlas localization still contains removed Cobblemon/Poke references after migration")
    lang.write_text(text, encoding="utf-8")

    # No removed namespace may remain in the actual quest/reward files after migration.
    legacy_paths = list(chapters.glob("*.snbt")) + list(tables.glob("*.snbt")) + [lang]
    stale = [str(path) for path in legacy_paths if "cobblemon:" in path.read_text(encoding="utf-8").lower()]
    if stale:
        raise RuntimeError(f"Removed Cobblemon namespace remains after migration: {stale}")

def update_changelog(path: Path, quest_count: int) -> None:
    marker = "## [Unreleased] — VvH Season One dev-modlist retune"
    text = path.read_text(encoding="utf-8") if path.exists() else "# Changelog\n"
    if marker in text:
        return
    block = f"""\n{marker}\n\n- Retuned the ten-chapter, {quest_count}-quest Vampires vs Hunters campaign to the current `dev` modlist at `{SOURCE_SHA}`. Vampire and Hunter routes now use the installed Vampirism 1.10.12 faction/progression surface, Vampire's Delight, Create/Aeronautics, MCA civic play, The Hordes, and the current transport/building stack.\n- Migrated existing Living Atlas quest/reward object IDs away from the removed Cobblemon namespace so old quest progress is preserved while new players receive valid current-pack objectives and rewards.\n- Kept Neutral/Free Company play mechanically viable, kept combat optional, preserved fixed horizontal rewards, and added no VvH KubeJS quest engine or dynamic faction reward multiplier.\n"""
    first_break = text.find("\n", text.find("#"))
    if first_break >= 0:
        text = text[: first_break + 1] + block + text[first_break + 1 :]
    else:
        text += block
    path.write_text(text, encoding="utf-8")

def manifest(campaign: Campaign) -> dict[str, Any]:
    return {
        "version": VERSION,
        "group_id": GROUP_ID,
        "reward_tables": campaign.reward_tables,
        "chapters": [
            {
                "id": chapter.id,
                "filename": chapter.filename,
                "title": chapter.title,
                "icon": chapter.icon,
                "images": chapter.images,
                "order": chapter.order,
                "quests": [
                    {
                        "id": q.id,
                        "title": re.sub(r"&.", "", q.title),
                        "subtitle": q.subtitle,
                        "description": q.desc,
                        "icon": q.icon,
                        "shape": q.shape,
                        "dependencies": q.dependencies,
                        "min_required_dependencies": q.min_required_dependencies,
                        "optional": q.optional,
                        "repeatable": q.can_repeat,
                        "repeat_cooldown": q.repeat_cooldown,
                        "hide_dependency_lines": q.hide_dependency_lines,
                        "tasks": [vars(t) for t in q.tasks],
                        "rewards": [vars(r) for r in q.rewards],
                        "x": q.x,
                        "y": q.y,
                        "size": q.size,
                    }
                    for q in chapter.quests
                ],
            }
            for chapter in campaign.chapters
        ],
    }


def write_docs(root: Path, campaign: Campaign) -> None:
    docs = root / "docs/vvh"
    evidence = docs / "evidence"
    evidence.mkdir(parents=True, exist_ok=True)
    man = manifest(campaign)
    (docs / "campaign_manifest.json").write_text(json.dumps(man, indent=2, sort_keys=True), encoding="utf-8")

    quest_count = sum(len(ch.quests) for ch in campaign.chapters)
    task_count = sum(len(q.tasks) for q in campaign.all_quests())
    quest_reward_count = sum(len(q.rewards) for q in campaign.all_quests())
    table_reward_count = sum(len(t["rewards"]) for t in campaign.reward_tables)

    (docs / "DISCOVERY.md").write_text(f"""# VvH Discovery — dev branch retune

## Authoritative pack snapshot

- Repository: `codecraft3r/packwiz-modpack`
- Source branch: `dev`
- Pinned dev revision: `{SOURCE_SHA}`
- Pack name: `Poiesis 2`
- `pack.toml` version field at this revision: `2.4.0`
- Changelog development label: `3.0.0-pre1`
- Minecraft: `1.21.1`
- NeoForge: `21.1.233`
- FTB Quests: `2101.1.27`
- FTB Teams: `2101.1.10`
- FTB Chunks: `2101.1.19`
- KubeJS: `2101.7.2-build.368`
- Dev server materialization: 135 JARs, about 424 MiB of JAR payload.

The mismatch between the `pack.toml` version field and the changelog development label is pre-existing dev-branch metadata drift. VvH records it rather than silently changing release metadata unrelated to this campaign.

## Modlist change that forced the retune

The old Season One build targeted master before the current dev overhaul. The dev branch removes Cobblemon and a large set of its addons plus AE2/Tempad/Tom's Storage-era assumptions, while adding a real Vampirism stack and new social/transport surfaces.

Key exact installed systems used by this revision:

- Vampirism `1.10.12`
- Godly Vampirism `1.10.0`
- Vampire's Delight `0.1.12b`
- Vampirism Integrations `1.10.2`
- Vampirism Iron's Spells Compatibility `0.0.6`
- Iron's Spells 'n Spellbooks `3.16.2`
- Create `6.0.10` plus Create Aeronautics/Propulsion/Avionics, Create Big Cannons, Enchantment Industry, Numismatics, and other addons
- Minecraft Comes Alive Reborn and Capitals
- The Hordes
- Farmer's Delight
- Nature's Compass / Explorer's Compass
- Mekanism, Powah, Flux Networks, Sophisticated Backpacks, Via Romana, and the existing building/decor stack

## Exact data inspected

The build harness materialized the server pack from Packwiz and indexed the actual installed JARs. Exact advancement JSON was inspected for:

- `vampirism:vampire/become_vampire`
- `vampirism:hunter/become_hunter`
- `vampirism:vampire/first_blood`
- `vampirism:hunter/stake`
- `vampirism:hunter/technology`
- `vampirism:main/vampire_forest`

Exact recipes/items were also resolved for the Vampire/Hunter foundation workstations and supplies. The campaign does not guess namespaces from a wiki.

## Existing quest debt discovered

The dev branch still carried the previous Living Atlas chapters and reward tables, but those files referenced the removed `cobblemon:` namespace in icons, images, statistics, reward items, and localization. Shipping VvH without fixing those pages would leave the quest book internally broken.

The generator therefore performs an idempotent migration of the existing Living Atlas content while preserving its quest/task/reward object IDs. Old Cobblemon objectives become current-dev Vampirism/Create/exploration/social objectives; Great/Poke Ball rewards become Vampire's Delight Hardtack travel utility. This is a content migration, not a progress reset.

## Implemented VvH surface

- {len(campaign.chapters)} VvH chapters
- {quest_count} VvH quests
- {task_count} VvH tasks
- {quest_reward_count} direct quest rewards
- {len(campaign.reward_tables)} VvH reward tables / {table_reward_count} choice-table entries
- 0 new VvH KubeJS scripts
- 3 equal foundation branches: Vampire, Hunter, Neutral
- 8 choice-based personal contribution routes
- 8 shared/public infrastructure projects
- 6 noncombat rivalry formats plus one separately gated optional skirmish
- 6 Long Night Fair contribution categories
- 5 limited weekly civic requisition sinks

## Progression assumption

No representative live world/save or current player inventory snapshot was supplied. Rewards therefore remain horizontal, modest, and useful across a broad early-to-midgame band. Creative tasks use peer/host review rather than brittle block scanning.
""", encoding="utf-8")

    (docs / "DECISIONS.md").write_text("""# VvH Decisions — dev retune

## D-001 — Vampires and Hunters are now real Vampirism factions

- Previous campaign assumption: no Vampirism faction mod was installed, so Vampire/Hunter were purely civic identities.
- New evidence: dev ships Vampirism 1.10.12 plus Godly Vampirism, Vampire's Delight, integrations, and Iron's Spells compatibility. Exact `become_vampire` and `become_hunter` advancements are present in the installed JAR.
- Corrected decision: the allegiance chapter now uses real Vampirism faction-entry advancements and the foundation chapters use actual faction workstations/resources.
- Player-facing effect: faction choice has genuine mechanics while the quest campaign still pushes those mechanics toward buildings, hospitality, routes, public service, and stories instead of a kill ladder.
- Migration: old VvH artifact should not be installed over dev; use this retuned drop-in.

## D-002 — Vampirism faction state and FTB Teams state remain separate

- Evidence: the installed systems do not provide a proven native synchronization layer between Vampirism factions and FTB Teams quest/claim parties.
- Decision: do not invent one in KubeJS. FTB Teams owns quest progress/claims; Vampirism owns supernatural faction state. Shared foundation-cache claims require a short peer/host confirmation of current alignment.
- Important nuance: `become_vampire` / `become_hunter` advancements are historical achievements. They do not erase themselves if a player later changes faction, so they cannot be treated as permanent live-state locks.

## D-003 — Keep Neutral as a full path

- Evidence: the product brief explicitly needs neutral traders, mediators, mercenaries, and diplomats.
- Decision: Free Companies have the same five-of-seven foundation workload and the same utility cache as the supernatural factions, using contracts, markets, routes, MCA civic play, rescue, and mediation.

## D-004 — No dynamic faction reward multiplier

- Original draft: reward scaling up to 2× based on active faction population.
- Decision: rejected again. Vampirism itself now supplies faction differentiation, making an extra loot multiplier even less necessary. Dynamic scaling would accelerate progression, complicate faction switching, and make neutral play economically second-class.
- Replacement: fixed reward classes—personal keepsakes/favors, one team utility cache per foundation/public milestone, and priced/cooldown-limited postgame requisitions.

## D-005 — Preserve and migrate Living Atlas object IDs

- Evidence: dev removed Cobblemon but still shipped old Atlas files containing `cobblemon:` tasks, icons, images, and rewards.
- Decision: repair those pages in-place and preserve existing quest/task/reward IDs so saved FTB quest progress remains attached.
- Player-facing effect: old pages now point to Vampirism/Create/current social objectives instead of deleted systems.

## D-006 — Creative work is human-reviewed

- Original draft: automated block-count scans for houses/vehicles.
- Decision: rejected as too brittle for modded blocks, contraptions, unusual architecture, and moving vehicles. Creative projects use concise function/access/safety/story/maintenance rubrics and checkmarks with two-player peer review or one host review.

## D-007 — Noncombat rivalry must precede any skirmish

- Decision: the optional skirmish is gated behind at least two completed noncombat rivalry formats. It can never become the first or default expression of faction identity.
- Rewards are participation/story supplies only; kills and wins grant no progression power.

## D-008 — No destructive reset automation ships in the quest package

- The original reset-zone concept remains operationally useful, but safe chunk regeneration across every dev mod was not proven by the quest build itself.
- Decision: document zones and recovery procedures; do not ship a destructive reset script merely because the pitch imagined one.
""", encoding="utf-8")

    chapter_rows = "\n".join(f"| {i:02d} | {ch.title} | {len(ch.quests)} |" for i, ch in enumerate(campaign.chapters))
    (docs / "QUEST_MAP.md").write_text(f"""# VvH Season One Quest Map

| # | Chapter | Quests |
|---:|---|---:|
{chapter_rows}

## Intended loop

`Island Charter → Three Invitations → one of three Foundations → any 3/8 Personal Contributions → any 4/8 Public Works → Long Night Fair → limited postgame requisitions`

`Rivalry Without Ruin` branches after the contribution chapter and remains optional. Its skirmish node requires two completed noncombat rivalry formats.

## Foundation equivalence

Each of House of Night, Lantern Order, and Free Companies uses the same structural budget:

1. one identity/current-state confirmation opener;
2. seven foundation works;
3. complete any five;
4. name the headquarters and maintenance owner;
5. receive the same 32 Scaffolding + 4 Super Glue team utility cache plus a different historical charter.

The routes are intentionally not palette-swapped copies. Vampires build around coffins, altar, blood pantry, Vampire's Delight hospitality, night routes, hosting, and Create utility. Hunters build around public watch, Hunter Table, garlic reserve, stake drill, alchemy, refuge routes, and safety drills. Neutrals build contracts, courier routes, markets, guest space, archives, MCA civic relationships, and mediation/rescue.

## Minimum mainline

The campaign uses flexible progression and native `min_required_dependencies` rather than forcing completionism. A minimum route includes:

- Charter signature
- one foundation opener + any five foundation works + foundation charter
- contribution opener + any three routes + contribution completion
- infrastructure opener + any four public works + civic completion
- Fair opener + any four contributions + Season One seal

Optional reference clauses, extra foundation works, extra personal routes, rivalry, skirmish, and postgame rumors are not required for the seal.
""", encoding="utf-8")

    reward_rows = []
    for ch in campaign.chapters:
        for q in ch.quests:
            for r in q.rewards:
                if r.type == "choice":
                    value = f"choice table `{r.table_id}`"
                elif r.item_data:
                    value = r.item_data.get("components", {}).get("minecraft:custom_name", "custom paper keepsake")
                    value = "custom paper keepsake"
                else:
                    value = f"{r.count}× `{r.item}`"
                reward_rows.append(f"| {ch.title} | {re.sub(r'&.', '', q.title)} | {value} | {'team' if r.team_reward else 'personal'} |")
    for table in campaign.reward_tables:
        for r in table["rewards"]:
            val = "custom paper lens" if r.get("item_data") else f"{r.get('count',1)}× `{r.get('item')}`"
            reward_rows.append(f"| Choice: {table['title']} | {r['title']} | {val} | claimant |")
    reward_rows_text = "\n".join(reward_rows)
    (docs / "BALANCE.md").write_text(f"""# VvH Balance Audit — dev retune

## Design band

The campaign assumes an unknown live-world progression state and therefore avoids vertical rewards. Quests should fund movement, building, events, maintenance, and catch-up without replacing Vampirism progression, hunter technology, late Create/Aeronautics builds, boss drops, high-tier magic, or endgame equipment.

## Strongest direct grants

- Create Goggles: quality-of-life information, not a progression machine.
- Nature's Compass: navigation convenience, not rare loot.
- 12 Arcane Essence / 8 Andesite Alloy / 8 Super Glue / 32 Scaffolding: modest friction reducers.
- Public caches: scaffolding, lanterns, torches, rails, food, fireworks, glue.

No VvH quest grants Vampirism levels, Hunter levels, vampire blood progression, high-tier crossbows, boss weapons, finished vehicles, netherite/diamond equipment, or Bevel currency.

## Currency

VvH issues **0 Bevels**. Postgame exchanges consume a maximum of **6 Bevels per FTB progress container per full weekly board**:

- lighting: 1
- transit: 2
- festival: 1
- repair: 1
- hospitality: 1

Outputs cannot produce Bevels or cheaply reproduce their own price. This makes the board a sink, not a faucet or self-funding loop.

## Faction fairness

All three foundations grant exactly the same team utility cache. Faction-specific items are objectives the players obtain through normal play, not rewards that let one faction skip its own progression.

The House and Order each require five of seven works and one current-alignment confirmation. Free Companies also require five of seven works. Neutral players therefore do not pay an economic penalty for refusing supernatural alignment.

## Route-time estimates

These are design estimates, not measured live-play timings:

- Charter + invitation: 10–25 minutes, excluding the actual Vampirism faction-conversion process.
- One foundation: roughly 2–5 team-hours depending on world state and build ambition.
- Any 3/8 personal contributions: 2–4 hours, heavily overlapping ordinary play.
- Any 4/8 public works: 4–10 server-hours, often spread across several players/sessions.
- Rivalry night: 45–120 minutes, optional.
- Long Night Fair: 60–150 minutes plus whatever public works already exist.

## Reward inventory

| Chapter/Table | Quest/Entry | Reward | Scope |
|---|---|---|---|
{reward_rows_text}

## Hostile edge cases

- **Faction switch just before claim:** historical advancement is insufficient; shared foundation cache requires current-state peer/host confirmation.
- **Two accounts in one FTB party:** team caches use `team_reward: true`; personal keepsakes/favors use `team_reward: false`. Exact two-client claiming still requires runtime verification.
- **Neutral joins a faction after completing Free Company:** old neutral charter remains history; no automatic reset/refund.
- **Repeatable payer/claim split:** price is consumed from the completing team task and output is a team reward. Test once with two disposable accounts before live use.
- **Progress reset abuse:** admin runbook explicitly forbids resetting completed milestones merely to reissue supplies.
""", encoding="utf-8")

    (docs / "ASSET_SOURCES.md").write_text("""# VvH Asset Sources

No external web artwork is shipped by this build.

Current chapter backgrounds/icons use assets already distributed by the installed pack and its mods, including vanilla Minecraft, Vampirism, Vampire's Delight, Create, Farmer's Delight, Nature's Compass, Iron's Spells, and Create Numismatics. These references are resolved against the materialized dev JAR set during validation.

The existing Poiesis Living Atlas resource pack remains the source for the older Atlas chapter key art. No copyrighted image-search asset, hotlink, or newly vendored third-party binary was added.

Two original transparent pixel-art emblems are now generated, reviewed, referenced by VvH 00/VvH 04, and shipped in the prerelease living-atlas-art-v4 asset. The five wide scene prompts remain queued because they need full painted backgrounds rather than cutouts.
""", encoding="utf-8")

    (docs / "ASSET_PROMPTS.md").write_text("""# VvH Original Asset Queue

The campaign is fully loadable without the remaining wide key art. The accepted transparent emblems below are installed in the v4 art release; the other five prompts still use installed mod/vanilla art as legal temporary fallbacks.

## ASSET-001 — Season crest
- Status: accepted, generated, reviewed, installed in living-atlas-art-v4
- Intended use: VvH chapter-group navigation identity / season announcement
- Final output path: `assets/poiesis/textures/questpics/vvh/season_one_crest.png`
- Canvas: 512x512 px
- Aspect ratio: 1:1
- Alpha: required
- Safe area: central 78%; no content touching outer 24 px
- Visual continuity: dark-fantasy guild ledger; chunky woodcut linework; crimson/bone Vampire half, steel-blue/gold Hunter half, parchment-green Neutral knot joining both; Minecraft-block-aware silhouette, not official Minecraft branding
- Subject and composition: circular heraldic seal split by a vertical lantern, left motif a stylized bat/fang and chalice silhouette, right motif garlic/lantern and watchtower silhouette, lower centre a map/contract knot representing neutrals; balanced visual weight, no weapons as dominant motif
- Generation prompt: Transparent heraldic crest for a small Minecraft-style social RPG campaign, hand-cut woodblock and illuminated-ledger aesthetic, circular seal, left crimson and bone vampire faction represented by abstract bat wings, fang and ceremonial vessel, right steel-blue and antique-gold hunter faction represented by garlic sprig, lantern and watchtower, lower parchment-green neutral contract/map knot bridging the sides, strong 2–4 px equivalent ink line, simplified shapes readable at 32 pixels, no words, no official game logo, slightly imperfect hand-printed texture
- Negative prompt: text, letters, logos, photorealism, anime, gore, realistic blood, guns, crossbows dominating the image, tiny clutter, gradients that disappear at icon scale, watermark, copyrighted logo
- Post-processing: chroma-key removal; alpha/fringe audit; nearest-neighbor resize to 512x512; test at 128/64/32 px; keep transparent margin; optimize PNG
- Acceptance checks: all three roles readable; no side looks more powerful; recognizable at 32 px; clean alpha; no text; verified in v4 ZIP
- Release asset: living-atlas-art-v4/poiesis-living-atlas-art-v4.zip
- Temporary fallback: `minecraft:textures/item/compass_16.png`

## ASSET-002 — House of Night key art
- Status: needed
- Intended use: Vampire foundation chapter background
- Final output path: `assets/poiesis/textures/questpics/vvh/house_of_night.png`
- Canvas: 1280x720 px
- Aspect ratio: 16:9
- Alpha: not required
- Safe area: central 46% low-detail for quest nodes
- Visual continuity: crimson, black-brown wood, bone, dim gold; gouache-over-woodcut; visual cues drawn from actual Vampirism altar/coffin/blood-container vocabulary without copying UI screenshots
- Subject and composition: block-built manor interior and courtyard at blue hour, side vignettes of a coffin room, altar chamber, labelled pantry, night kitchen and lantern route, players hosting a visitor rather than fighting; centre kept quiet
- Generation prompt: Wide production key art for a Minecraft-like vampire civic guild chapter, block-aware gothic manor at blue hour, warm crimson and dim gold windows, side vignettes showing functional coffin room, ritual altar chamber, labelled blood pantry, supernatural kitchen and a lantern-lit public route, several blocky adventurers hosting a guest and maintaining the building, no central combat, painterly gouache plus engraved woodcut texture, central 46 percent deliberately low detail for UI nodes, atmospheric but readable in dark UI
- Negative prompt: gore, feeding close-up, seductive vampire portrait, one overpowered hero, combat scene, text, logo, photorealism, muddy black centre, UI elements, watermark
- Post-processing: lower centre contrast; vignette edges; palette match to faction crimson/bone; 16:9 crop check; PNG optimize
- Acceptance checks: reads as vampire infrastructure/hospitality before combat; centre remains legible; no embedded text
- Temporary fallback: Vampirism fang + vanilla lantern textures

## ASSET-003 — Lantern Order key art
- Status: needed
- Intended use: Hunter foundation chapter background
- Final output path: `assets/poiesis/textures/questpics/vvh/lantern_order.png`
- Canvas: 1280x720 px
- Aspect ratio: 16:9
- Alpha: not required
- Safe area: central 46% low-detail
- Visual continuity: steel-blue, parchment, garlic green, antique gold; woodcut/gouache companion piece to ASSET-002
- Subject and composition: block-built watchhouse/workshop with lantern route, Hunter Table/alchemy silhouettes, garlic reserve and refuge map; players helping an escorted traveler, not posing as monster slayers
- Generation prompt: Wide production key art for a Minecraft-like hunter civic order, sturdy block-built watchhouse and shared workshop at dusk, steel-blue roof accents, antique-gold lantern route, garlic drying rack, alchemical workspace and public refuge signage shapes, several blocky adventurers escorting a traveler and checking supplies, vigilant but non-militaristic mood, hand-printed woodcut plus gouache texture, central area quiet for quest nodes, matched composition weight to a vampire manor companion image
- Negative prompt: firing squad, gore, trophies of dead vampires, giant weapon, modern military gear, police aesthetic, photorealism, text, watermark, cluttered centre
- Post-processing: palette harmonization with House art; reduce centre detail; readability test at chapter scale; PNG optimize
- Acceptance checks: public-service identity is obvious; no glorification of killing; equal visual prestige to Vampire art
- Temporary fallback: Vampirism garlic + vanilla lantern textures

## ASSET-004 — Free Company writ crest
- Status: accepted, generated, reviewed, installed in living-atlas-art-v4
- Intended use: Neutral foundation chapter icon/background motif
- Final output path: `assets/poiesis/textures/questpics/vvh/free_company_writ.png`
- Canvas: 512x512 px
- Aspect ratio: 1:1
- Alpha: required
- Safe area: 80% central
- Visual continuity: parchment, moss green, copper, ink-black; same woodcut linework as faction crest
- Subject and composition: folded route map, sealed contract, courier satchel, market awning and small bell arranged as a compact civic emblem; no weapons
- Generation prompt: Transparent guild emblem for a neutral Free Company in a block-world fantasy server, woodcut ledger illustration, folded map and route line behind a sealed contract, small courier satchel, market awning and civic bell, parchment and moss-green palette with copper accents, chunky simple silhouette readable at 32 pixels, no text, no money pile, no weapon motif
- Negative prompt: corporate logo, national flag, bank icon, realistic currency, sword, gun, tiny illegible writing, photorealism, watermark
- Post-processing: chroma-key removal; alpha/fringe audit; nearest-neighbor resize to 512x512; simplify route marks; palette reduction; icon-scale tests
- Acceptance checks: communicates trade/routes/mediation; equal status to faction crests; no text; verified in v4 ZIP
- Release asset: living-atlas-art-v4/poiesis-living-atlas-art-v4.zip
- Temporary fallback: `minecraft:textures/item/filled_map.png`

## ASSET-005 — Public works panorama
- Status: needed
- Intended use: The Island Remembers chapter background
- Final output path: `assets/poiesis/textures/questpics/vvh/island_remembers.png`
- Canvas: 1280x720 px
- Aspect ratio: 16:9
- Alpha: not required
- Safe area: central upper 45% subdued
- Visual continuity: warm parchment-gold nightfall, all faction colors present only as accents
- Subject and composition: one inhabited island showing connected road/rail, market, archive, kitchen, workshop, airship dock, refuge, meeting hall; visual lines converge but centre stays calm
- Generation prompt: Wide illustrated block-world island town at dusk showing accumulated public infrastructure rather than a hero, connected road and short rail line, market, archive/map room, community kitchen, shared mechanical workshop, small airship dock/test field, emergency refuge and public meeting hall, tiny crimson vampire, steel-blue hunter and green-neutral accents distributed evenly, warm lanterns, hand-painted woodcut/gouache style, central upper area low detail for quest UI nodes, sense of history and repeated use
- Negative prompt: empty pristine city, giant castle dominating scene, combat, text labels, official Minecraft logo, photorealism, cluttered centre, watermark
- Post-processing: centre contrast reduction; slight paper texture; sharpen infrastructure silhouettes; PNG optimize
- Acceptance checks: at least six public-work types visible; world feels lived-in; no one faction owns the composition
- Temporary fallback: vanilla lantern/rail/book imagery

## ASSET-006 — Rivalry without ruin woodcut
- Status: needed
- Intended use: safe-rivalry chapter background
- Final output path: `assets/poiesis/textures/questpics/vvh/rivalry_without_ruin.png`
- Canvas: 1024x576 px
- Aspect ratio: 16:9
- Alpha: not required
- Safe area: central 50% quiet
- Visual continuity: satirical illuminated-manuscript marginalia; faction colors; warm parchment
- Subject and composition: Vampire and Hunter teams at far edges presenting absurd food, mascots, banners and race contraptions; neutral referee at lower centre; scavenger clues and fireworks; no battle in focus
- Generation prompt: Wide satirical woodcut illustration for harmless faction rivalry in a block-world fantasy server, crimson vampire team at far left and steel-blue hunter team at far right presenting absurd mascots, garlic-versus-blood themed cooking dishes, propaganda banners and overengineered race contraptions, parchment-green neutral referee with clipboard at lower centre, scavenger clues and fireworks in background, theatrical friendly tension, central area deliberately low-detail for quest nodes, aged manuscript texture, no text
- Negative prompt: warfare, gore, angry mob, griefed buildings, realistic weapons, text, official logos, photorealism, cluttered centre, watermark
- Post-processing: reduce centre contrast; palette harmonize; vignette; PNG optimize
- Acceptance checks: funny before threatening; multiple safe formats readable; no text
- Temporary fallback: firework/garlic/fang/map textures

## ASSET-007 — Long Night Fair key art
- Status: needed
- Intended use: Season One capstone background and announcement
- Final output path: `assets/poiesis/textures/questpics/vvh/long_night_fair.png`
- Canvas: 1280x720 px
- Aspect ratio: 16:9
- Alpha: not required
- Safe area: central upper 45% subdued; strongest activity along lower third/edges
- Visual continuity: warm gold against blue-black night; crimson, steel-blue and green identities mixed rather than segregated; woodcut-gouache finish
- Subject and composition: lantern procession through the actual kinds of works the campaign created—market, workshop, archive, kitchen, routes, dock—plus Vampire hospitality, Hunter public-service exhibit, neutral contract desk, small airship/vehicle demonstration and fireworks; no central hero
- Generation prompt: Production key art for a block-world social RPG finale called a long-night fair, inhabited island town at deep blue night lit by hundreds of warm lanterns, mixed procession passing public market, mechanical workshop, archive, community kitchen, mapped road and small airship dock, crimson vampire hosts with supernatural food table, steel-blue hunter stewards with public safety exhibit, parchment-green neutral traders and contract desk, controlled whimsical vehicle demonstration and fireworks over water, collective celebration without a central hero, painterly woodcut-gouache hybrid, central upper area quiet for quest nodes, no text
- Negative prompt: title lettering, logo, lone warrior, combat, gore, dark unreadable image, chaotic centre, photorealism, watermark
- Post-processing: preserve UI-safe centre; blacks lifted for dark UI; 16:9 and 2:1 crop tests; PNG optimize
- Acceptance checks: communicates accumulated world history and all three identities; multiple contribution types visible; readable at chapter scale
- Temporary fallback: lantern/firework/fang/garlic textures
""", encoding="utf-8")

    (docs / "VERIFICATION.md").write_text(f"""# VvH Verification — dev branch

## Resolved before authoring

- Dev branch exists and was pinned to `{SOURCE_SHA}`.
- Packwiz metadata at the pinned source was materialized successfully before the retune.
- Exact installed JAR contents were indexed rather than inferring IDs from names.
- Vampirism faction-entry advancements exist and use Vampirism's faction trigger for level 1.
- `vampirism:main/vampire_forest` is a real location advancement.
- Exact item/recipe data exists for the Vampire altar/coffin/blood resources and Hunter table/stake/alchemical stations used by foundation quests.
- Vampire's Delight Hardtack is a cheap current-pack travel ration and is used to replace removed Cobblemon reward slots without granting faction progression.
- Existing Living Atlas files contained invalid `cobblemon:` references on dev; the generator repairs them while retaining object IDs.

## Architectural verification decisions

- Current live Vampirism faction state is not represented by a proven native FTB Quests task. The campaign therefore uses exact historical faction-entry advancements plus explicit current-state peer/host confirmation for shared faction caches.
- No KubeJS synchronization or reward-scaling layer was added.
- Creative-build scanning remains unproven/undesirable for the modded building surface; peer/host review is used.
- World-reset automation remains outside the shipped quest package until a disposable-world reset test proves every relevant boundary and mod-data interaction.

## Automated build tests

The CI gauntlet is expected to run after generation against the pinned dev revision and record Packwiz cleanliness, exact namespace resolution, SNBT parsing, graph/economy validation, layout renders, server materialization, and a disposable NeoForge + FTB Quests reload smoke test under `docs/vvh/evidence/`.

## Requires runtime verification

- two-client personal versus team reward claiming;
- current Vampirism faction → FTB Teams social confirmation workflow during a real faction switch;
- live claim ownership/transfer after leaving a faction FTB party;
- normal-scale client chapter rendering and text wrapping;
- skirmish PvP toggle, protected noncombatants, backup, and restore;
- any future destructive wilderness reset procedure.
""", encoding="utf-8")

    (docs / "ADMIN_RUNBOOK.md").write_text("""# VvH Administrator Runbook — dev retune

## Launch

1. Back up world + FTB quest/team data.
2. Verify the live pack commit matches the build's pinned dev revision or rerun the generator/validation against the newer dev head.
3. Run `packwiz refresh`; an unexpected diff means the drop-in is stale or incompletely copied.
4. Launch a disposable server and inspect FTB Quests loading before touching the live world.
5. Open all VvH and migrated Living Atlas pages on a client. Search the quest files for `cobblemon:`; there should be none.
6. Publish the permanent-building boundary. Do not advertise automated resets until separately proven on disposable chunks.

## Faction onboarding

Vampirism and FTB Teams are separate systems.

- Vampirism Vampire/Hunter state determines supernatural mechanics.
- FTB Teams determines shared quest progress and FTB Chunks ownership.
- Finish the personal Charter before joining a shared faction FTB party when practical.
- House of Night and Lantern Order foundation caches require a second player/host to confirm the FTB team is presently aligned with the claimed Vampirism faction.
- A past `become_vampire` / `become_hunter` advancement is historical evidence only; do not use it alone to approve a post-switch cache.
- Free Companies use personal/neutral FTB parties unless the server intentionally creates a shared neutral company.

## Faction switch

1. Record old Vampirism faction, FTB party, claims, shared storage obligations, contracts, and public-project ownership.
2. Complete the actual Vampirism cure/betrayal/switch process through normal mod mechanics.
3. Before leaving the old FTB party, remove personal items and identify who owns each claim/public responsibility.
4. Change FTB party only after the claim plan is understood.
5. Verify quest progress/reward visibility after the switch. Do not reset old foundation quests to mint a second cache.
6. The old charter remains historical. Complete the new branch/foundation only when the new team does the actual work.

Exact claim-transfer behavior still **requires runtime verification** with disposable accounts on the live config.

## Creative review

A project passes with two-player peer review or one host review using:

1. Function — does the stated service actually work?
2. Access — can intended users reach/use/understand it?
3. Safety — does it avoid obvious grief/entity/TPS hazards?
4. Story — is it named, contextualized, or connected to server life?
5. Maintenance — is an owner/rotation/restock expectation clear?

Do not enforce palette, block counts, or one architectural solution.

## Rivalry / skirmish

Run noncombat formats first. A skirmish is disabled in practice until the host has proven:

- explicit roster consent;
- arena/boundary;
- loadout ceiling;
- protected spectators/noncombatants;
- inventory/death rule;
- fresh verified backup;
- PvP start/stop controls;
- stop command/condition;
- restore/rebuild owner.

No kill/win reward is issued by VvH.

## Weekly requisitions

One teammate pays the Bevel cost; the cache is a team reward. Stand beside the intended public destination chest before claiming. Never refund the Bevel while leaving the cache in circulation.

## Progress repair

Take a backup. Identify the exact FTB team and object ID from `campaign_manifest.json`. Use targeted FTB Quests progress commands/editor tools only. Avoid reset-all/complete-all on the live world.
""", encoding="utf-8")

    (docs / "VALIDATION.md").write_text("""# VvH Validation

The generated package includes `scripts/vvh_validate.py`, `scripts/vvh_render_layouts.py`, `scripts/vvh_discover.py`, and `scripts/vvh_server_smoke.sh`.

Static validation must cover:

- all edited SNBT parses;
- unique global FTB object IDs;
- acyclic/reachable VvH graph and valid any-N-of-M minima;
- all localization keys;
- all item/icon/image/advancement references against the materialized dev JAR index;
- zero `cobblemon:` references after Living Atlas migration;
- no new VvH KubeJS files;
- explicit personal/team reward scope;
- repeatable Bevel prices/cooldowns and zero Bevel issuance;
- source-level layout overlap/crossing checks.

The dedicated-server stage must materialize the exact Packwiz pack, launch NeoForge 21.1.233 in a disposable world, wait for startup, execute FTB Quests reload, and fail on targeted quest/config/missing-ID errors. Client visual tests and multi-account interaction tests remain distinct manual evidence; they are never described as completed merely because the server parsed the files.
""", encoding="utf-8")

    (docs / "UNRESOLVED.md").write_text("""# VvH Unresolved / Live Checks

- [ ] **requires runtime verification** — capture every VvH chapter plus the migrated Living Atlas pages at normal client UI scale; fix wrapping, crop, contrast, icon scale, or dependency-line issues.
- [ ] **requires runtime verification** — use two disposable accounts in one FTB party to verify every personal-vs-team reward assumption.
- [ ] **requires runtime verification** — test Vampire → Neutral/Human → Hunter (and reverse where supported) alongside FTB party changes and claims; document exact claim ownership outcome.
- [ ] **requires runtime verification** — prove optional skirmish PvP start/stop plus backup restoration before enabling it.
- [ ] **requires runtime verification** — publish/test permanent and reset boundaries; no destructive reset automation ships here.
- [x] Generated, reviewed, and installed the transparent season crest and Free Company writ; both resolve from living-atlas-art-v4.
- [ ] Generate/review/install the five remaining wide scene key-art assets; current installed-mod fallbacks keep those chapters loadable.
""", encoding="utf-8")

def install(root: Path) -> None:
    campaign = build_campaign()
    migrate_legacy_atlas(root)
    chapters_dir = root / "config/ftbquests/quests/chapters"
    lang_path = root / "config/ftbquests/quests/lang/en_us.snbt"
    tables_dir = root / "config/ftbquests/quests/reward_tables"
    chapters_dir.mkdir(parents=True, exist_ok=True)
    tables_dir.mkdir(parents=True, exist_ok=True)
    for chapter in campaign.chapters:
        (chapters_dir / f"{chapter.filename}.snbt").write_text(render_chapter(chapter), encoding="utf-8")
    for table in campaign.reward_tables:
        (tables_dir / f"{table['id']}.snbt").write_text(render_reward_table(table), encoding="utf-8")
    update_chapter_groups(root / "config/ftbquests/quests/chapter_groups.snbt")
    update_lang(lang_path, render_lang(campaign))
    update_changelog(root / "CHANGELOG.md", sum(len(ch.quests) for ch in campaign.chapters))
    write_docs(root, campaign)
    print(json.dumps({
        "chapters": len(campaign.chapters),
        "quests": sum(len(ch.quests) for ch in campaign.chapters),
        "tasks": sum(len(q.tasks) for q in campaign.all_quests()),
        "quest_rewards": sum(len(q.rewards) for q in campaign.all_quests()),
        "reward_tables": len(campaign.reward_tables),
    }, indent=2))


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("root", type=Path)
    args = parser.parse_args()
    install(args.root.resolve())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
