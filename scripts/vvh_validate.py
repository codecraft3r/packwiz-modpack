#!/usr/bin/env python3
"""Static validator and design-audit helper for VvH Season One.

This does not pretend to replace the exact FTB Quests loader. It parses the shipped
SNBT dialect, validates the campaign graph/economy/assets against the discovered
pack, and writes machine-readable evidence for the disposable-server stage.
"""
from __future__ import annotations

import argparse
import itertools
import json
import math
import re
import sys
from collections import Counter, defaultdict
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable

VVH_PREFIX = "7A11C0DE"
HEX_ID = re.compile(r"^[0-9A-F]{16}$")
IMAGE_CODE = re.compile(r"\{image:([^\s}]+)")
COLOR_CODE = re.compile(r"&[0-9a-fk-or]", re.I)


class SNBTError(ValueError):
    pass


@dataclass(frozen=True)
class Token:
    kind: str
    value: str
    offset: int


class Tokenizer:
    def __init__(self, text: str, source: str) -> None:
        self.text = text
        self.source = source
        self.i = 0
        self.n = len(text)

    def _skip(self) -> None:
        while self.i < self.n:
            if self.text[self.i].isspace() or self.text[self.i] == ',':
                self.i += 1
                continue
            if self.text.startswith("//", self.i):
                j = self.text.find("\n", self.i + 2)
                self.i = self.n if j < 0 else j + 1
                continue
            if self.text.startswith("/*", self.i):
                j = self.text.find("*/", self.i + 2)
                if j < 0:
                    raise SNBTError(f"{self.source}: unterminated block comment at {self.i}")
                self.i = j + 2
                continue
            break

    def next(self) -> Token:
        self._skip()
        if self.i >= self.n:
            return Token("EOF", "", self.i)
        start = self.i
        c = self.text[self.i]
        if c in "{}[]:":
            self.i += 1
            return Token(c, c, start)
        if c in '"\'':
            quote = c
            self.i += 1
            escaped = False
            while self.i < self.n:
                ch = self.text[self.i]
                if escaped:
                    escaped = False
                    self.i += 1
                    continue
                if ch == "\\":
                    escaped = True
                    self.i += 1
                    continue
                if ch == quote:
                    self.i += 1
                    raw = self.text[start:self.i]
                    if quote == '"':
                        try:
                            return Token("STRING", json.loads(raw), start)
                        except json.JSONDecodeError as exc:
                            raise SNBTError(f"{self.source}: bad quoted string at {start}: {exc}") from exc
                    # Single-quoted strings are uncommon here; decode minimal escapes.
                    body = raw[1:-1].replace("\\'", "'").replace("\\\\", "\\")
                    return Token("STRING", body, start)
                self.i += 1
            raise SNBTError(f"{self.source}: unterminated string at {start}")
        while self.i < self.n:
            ch = self.text[self.i]
            if ch.isspace() or ch in "{}[]:,":
                break
            if self.text.startswith("//", self.i) or self.text.startswith("/*", self.i):
                break
            self.i += 1
        if self.i == start:
            raise SNBTError(f"{self.source}: unexpected character {c!r} at {start}")
        return Token("BARE", self.text[start:self.i], start)


class Parser:
    def __init__(self, text: str, source: str) -> None:
        self.tok = Tokenizer(text, source)
        self.source = source
        self.look = self.tok.next()

    def consume(self, kind: str) -> Token:
        if self.look.kind != kind:
            raise SNBTError(f"{self.source}: expected {kind}, got {self.look.kind} {self.look.value!r} at {self.look.offset}")
        cur = self.look
        self.look = self.tok.next()
        return cur

    def parse(self) -> Any:
        value = self.value()
        if self.look.kind != "EOF":
            raise SNBTError(f"{self.source}: trailing token {self.look.value!r} at {self.look.offset}")
        return value

    def value(self) -> Any:
        if self.look.kind == "{":
            return self.compound()
        if self.look.kind == "[":
            return self.list_value()
        if self.look.kind == "STRING":
            return self.consume("STRING").value
        if self.look.kind == "BARE":
            raw = self.consume("BARE").value
            low = raw.lower()
            if low == "true":
                return True
            if low == "false":
                return False
            if low in {"null", "none"}:
                return None
            m = re.fullmatch(r"([+-]?(?:\d+(?:\.\d*)?|\.\d+)(?:[eE][+-]?\d+)?)([bBsSlLfFdD]?)", raw)
            if m:
                num, suffix = m.groups()
                try:
                    if "." in num or "e" in num.lower() or suffix.lower() in {"f", "d"}:
                        return float(num)
                    return int(num)
                except ValueError:
                    pass
            return raw
        raise SNBTError(f"{self.source}: expected value at {self.look.offset}, got {self.look.kind}")

    def compound(self) -> dict[str, Any]:
        self.consume("{")
        out: dict[str, Any] = {}
        while self.look.kind != "}":
            if self.look.kind not in {"STRING", "BARE"}:
                raise SNBTError(f"{self.source}: expected compound key at {self.look.offset}")
            key = self.look.value
            self.look = self.tok.next()
            self.consume(":")
            if key in out:
                raise SNBTError(f"{self.source}: duplicate key {key!r}")
            out[key] = self.value()
            if self.look.kind == "EOF":
                raise SNBTError(f"{self.source}: unterminated compound")
        self.consume("}")
        return out

    def list_value(self) -> list[Any]:
        self.consume("[")
        out: list[Any] = []
        while self.look.kind != "]":
            if self.look.kind == "EOF":
                raise SNBTError(f"{self.source}: unterminated list")
            out.append(self.value())
        self.consume("]")
        return out


def parse_snbt(path: Path) -> Any:
    return Parser(path.read_text(encoding="utf-8"), str(path)).parse()


def iter_dicts(value: Any) -> Iterable[dict[str, Any]]:
    if isinstance(value, dict):
        yield value
        for v in value.values():
            yield from iter_dicts(v)
    elif isinstance(value, list):
        for v in value:
            yield from iter_dicts(v)


def strip_codes(text: str) -> str:
    return COLOR_CODE.sub("", text)


class Audit:
    def __init__(self) -> None:
        self.errors: list[str] = []
        self.warnings: list[str] = []
        self.notes: list[str] = []
        self.metrics: dict[str, Any] = {}

    def error(self, msg: str) -> None:
        self.errors.append(msg)

    def warn(self, msg: str) -> None:
        self.warnings.append(msg)

    def note(self, msg: str) -> None:
        self.notes.append(msg)

    def check(self, condition: bool, msg: str) -> None:
        if not condition:
            self.error(msg)


def load_jar_entries(index_root: Path) -> set[str]:
    entries: set[str] = set()
    if not index_root.exists():
        return entries
    for path in index_root.glob("*.entries.txt"):
        entries.update(line.strip() for line in path.read_text(encoding="utf-8", errors="replace").splitlines() if line.strip())
    return entries


def resolve_item(item_id: str, entries: set[str], source_root: Path) -> bool:
    if ":" not in item_id:
        return False
    ns, path = item_id.split(":", 1)
    if ns == "minecraft":
        return item_id in {
            "minecraft:amethyst_shard", "minecraft:beetroot_soup", "minecraft:bell",
            "minecraft:book", "minecraft:bookshelf", "minecraft:bread", "minecraft:bricks",
            "minecraft:bundle", "minecraft:cake", "minecraft:carved_pumpkin", "minecraft:chest",
            "minecraft:chiseled_stone_bricks", "minecraft:clock", "minecraft:compass",
            "minecraft:cooked_beef", "minecraft:crossbow", "minecraft:dark_oak_door",
            "minecraft:emerald", "minecraft:fermented_spider_eye", "minecraft:filled_map",
            "minecraft:firework_rocket", "minecraft:hay_block", "minecraft:iron_sword",
            "minecraft:item_frame", "minecraft:lantern", "minecraft:lead", "minecraft:minecart",
            "minecraft:oak_sign", "minecraft:painting", "minecraft:paper", "minecraft:powered_rail",
            "minecraft:rail", "minecraft:red_banner", "minecraft:red_candle", "minecraft:scaffolding",
            "minecraft:stone_bricks",
            "minecraft:shield", "minecraft:slime_ball", "minecraft:soul_lantern", "minecraft:spyglass",
            "minecraft:target", "minecraft:torch", "minecraft:writable_book",
            "minecraft:armor_stand", "minecraft:crafting_table", "minecraft:iron_door",
            "minecraft:lectern", "minecraft:recovery_compass", "minecraft:white_bed",
            "minecraft:amethyst_cluster", "minecraft:diamond_pickaxe", "minecraft:firework_star",
        }
    model = f"assets/{ns}/models/item/{path}.json"
    if model in entries:
        return True
    # Nature's Compass was not selected into the compact JAR index, but its exact
    # item ID is already used by the authoritative pack's working reward table.
    if item_id == "naturescompass:naturescompass":
        existing = source_root / "config/ftbquests/quests/reward_tables/1A0B1A4E5A9E3000.snbt"
        return existing.exists() and item_id in existing.read_text(encoding="utf-8")
    return False


def resolve_image(ref: str, entries: set[str], source_root: Path, asset_roots: list[Path]) -> bool:
    if ":" not in ref:
        return False
    ns, path = ref.split(":", 1)
    if ns == "minecraft":
        return ref in {
            "minecraft:textures/block/amethyst_cluster.png",
            "minecraft:textures/item/book.png", "minecraft:textures/item/bread.png",
            "minecraft:textures/item/compass_16.png", "minecraft:textures/item/filled_map.png",
            "minecraft:textures/item/firework_rocket.png", "minecraft:textures/item/iron_sword.png",
            "minecraft:textures/item/lantern.png", "minecraft:textures/item/spyglass.png",
            "minecraft:textures/item/writable_book.png",
        }
    if f"assets/{ns}/{path}" in entries:
        return True
    # Resource-pack fallback paths, when present in unpacked source or supplied
    # as an external materialized resource-pack root.
    candidates = [
        source_root / "global_packs/required_resources",
        *asset_roots,
    ]
    return any((root / "assets" / ns / path).exists() for root in candidates)


def minimum_completion_set(target: str, quests: dict[str, dict[str, Any]]) -> frozenset[str]:
    """Return a deterministic minimum-cost completion set.

    The graph is a DAG and every quest has one dependency requirement. We keep one
    best set per dependency and enumerate only the direct N-of-M choices. This
    preserves shared ancestors through set union without the exponential product of
    every equivalent route variant.
    """
    memo: dict[str, frozenset[str]] = {}
    active: set[str] = set()

    def rec(qid: str) -> frozenset[str]:
        if qid in memo:
            return memo[qid]
        if qid in active:
            raise ValueError(f"cycle at {qid}")
        active.add(qid)
        q = quests[qid]
        deps = q.get("dependencies", [])
        need = q.get("min_required_dependencies", 0) or len(deps)
        if not deps or need == 0:
            result = frozenset({qid})
        else:
            dep_sets = {dep: rec(dep) for dep in deps}
            choices = itertools.combinations(deps, need)
            result = min(
                (frozenset({qid}).union(*(dep_sets[d] for d in choice)) for choice in choices),
                key=lambda x: (len(x), sorted(x)),
            )
        active.remove(qid)
        memo[qid] = result
        return result

    return rec(target)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("root", type=Path)
    ap.add_argument("--jar-index", type=Path, required=True)
    ap.add_argument(
        "--asset-root",
        type=Path,
        action="append",
        default=[],
        help="Unpacked resource-pack root(s), each containing assets/",
    )
    ap.add_argument("--report", type=Path)
    args = ap.parse_args()
    root = args.root.resolve()
    source_root = root
    asset_roots = [path.resolve() for path in args.asset_root]
    report_path = args.report or (root / "docs/vvh/evidence/static-validation.json")
    report_path.parent.mkdir(parents=True, exist_ok=True)
    audit = Audit()

    quest_root = root / "config/ftbquests/quests"
    parsed: dict[Path, Any] = {}
    for path in sorted(quest_root.rglob("*.snbt")):
        try:
            parsed[path] = parse_snbt(path)
        except Exception as exc:  # noqa: BLE001
            audit.error(f"SNBT parse failed: {path.relative_to(root)}: {exc}")
    audit.metrics["snbt_files_parsed"] = len(parsed)

    stale_cobblemon = []
    for path in sorted(quest_root.rglob("*.snbt")):
        text = path.read_text(encoding="utf-8", errors="replace")
        if re.search(r"cobblemon:", text, re.I):
            stale_cobblemon.append(str(path.relative_to(root)))
    audit.metrics["removed_cobblemon_namespace_refs"] = len(stale_cobblemon)
    for rel in stale_cobblemon:
        audit.error(f"Removed Cobblemon namespace remains in quest data: {rel}")

    manifest_path = root / "docs/vvh/campaign_manifest.json"
    try:
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    except Exception as exc:  # noqa: BLE001
        audit.error(f"Manifest load failed: {exc}")
        manifest = {"chapters": [], "reward_tables": []}

    # Collect global IDs from all parsed quest data.
    id_locations: dict[str, list[str]] = defaultdict(list)
    for path, doc in parsed.items():
        for obj in iter_dicts(doc):
            value = obj.get("id")
            if isinstance(value, str) and HEX_ID.fullmatch(value):
                id_locations[value].append(str(path.relative_to(root)))
    for ident, locs in sorted(id_locations.items()):
        if len(locs) > 1:
            audit.error(f"Duplicate FTB object ID {ident}: {locs}")
    audit.metrics["global_ftb_ids"] = len(id_locations)

    vvh_quests: dict[str, dict[str, Any]] = {}
    chapters_by_id: dict[str, dict[str, Any]] = {}
    for ch in manifest.get("chapters", []):
        chapters_by_id[ch["id"]] = ch
        audit.check(bool(HEX_ID.fullmatch(ch["id"])), f"Invalid chapter ID {ch.get('id')}")
        for q in ch.get("quests", []):
            qid = q["id"]
            audit.check(bool(HEX_ID.fullmatch(qid)), f"Invalid quest ID {qid}")
            if qid in vvh_quests:
                audit.error(f"Duplicate quest ID in manifest: {qid}")
            vvh_quests[qid] = q
            if not q.get("tasks"):
                audit.error(f"Quest {qid} {q.get('title')} has no tasks")
            if not q.get("title") or not q.get("subtitle") or not q.get("description"):
                audit.error(f"Quest {qid} lacks complete player-facing copy")
            deps = q.get("dependencies", [])
            need = q.get("min_required_dependencies", 0)
            if need and not (1 <= need <= len(deps)):
                audit.error(f"Quest {qid} invalid min_required_dependencies={need} for {len(deps)} deps")
            for dep in deps:
                if dep not in vvh_quests and not any(dep in qq.get("id", "") for cc in manifest.get("chapters", []) for qq in cc.get("quests", [])):
                    # second pass below handles forward refs cleanly
                    pass

    for qid, q in vvh_quests.items():
        for dep in q.get("dependencies", []):
            if dep not in vvh_quests and dep not in id_locations:
                audit.error(f"Quest {qid} depends on missing object {dep}")

    # DAG and reachability.
    visiting: set[str] = set()
    visited: set[str] = set()
    def visit(qid: str) -> None:
        if qid in visited:
            return
        if qid in visiting:
            audit.error(f"Dependency cycle includes {qid}")
            return
        visiting.add(qid)
        for dep in vvh_quests[qid].get("dependencies", []):
            if dep in vvh_quests:
                visit(dep)
        visiting.remove(qid)
        visited.add(qid)
    for qid in vvh_quests:
        visit(qid)
    audit.metrics["vvh_quests"] = len(vvh_quests)
    audit.metrics["vvh_chapters"] = len(manifest.get("chapters", []))

    roots = {qid for qid, q in vvh_quests.items() if not q.get("dependencies")}
    reverse: dict[str, set[str]] = defaultdict(set)
    for qid, q in vvh_quests.items():
        for dep in q.get("dependencies", []):
            if dep in vvh_quests:
                reverse[dep].add(qid)
    reachable = set(roots)
    stack = list(roots)
    while stack:
        cur = stack.pop()
        for child in reverse[cur]:
            if child not in reachable:
                reachable.add(child)
                stack.append(child)
    for missing in sorted(set(vvh_quests) - reachable):
        audit.error(f"Unreachable quest {missing} {vvh_quests[missing].get('title')}")
    audit.metrics["root_quests"] = sorted(roots)

    # Translation coverage.
    lang_path = quest_root / "lang/en_us.snbt"
    lang = parsed.get(lang_path, {})
    if not isinstance(lang, dict):
        audit.error("Language file did not parse as a compound")
        lang = {}
    required_keys: set[str] = {f"chapter_group.{manifest.get('group_id')}.title"}
    for table in manifest.get("reward_tables", []):
        required_keys.add(f"reward_table.{table['id']}.title")
        for r in table.get("rewards", []):
            required_keys.add(f"reward.{r['id']}.title")
    for ch in manifest.get("chapters", []):
        required_keys.add(f"chapter.{ch['id']}.title")
        for q in ch.get("quests", []):
            required_keys.update({
                f"quest.{q['id']}.title",
                f"quest.{q['id']}.quest_subtitle",
                f"quest.{q['id']}.quest_desc",
            })
            for t in q.get("tasks", []):
                required_keys.add(f"task.{t['id']}.title")
            for r in q.get("rewards", []):
                required_keys.add(f"reward.{r['id']}.title")
    missing_keys = sorted(required_keys - set(lang))
    for key in missing_keys:
        audit.error(f"Missing localization key {key}")
    audit.metrics["localization_keys_required"] = len(required_keys)

    # Text density and duplicated adjacent lines.
    long_lines: list[tuple[str, int, str]] = []
    for qid, q in vvh_quests.items():
        desc = q.get("description", [])
        for line in desc:
            plain = strip_codes(line)
            if len(plain) > 220:
                long_lines.append((qid, len(plain), plain[:100]))
        for a, b in zip(desc, desc[1:]):
            if a and a == b:
                audit.error(f"Quest {qid} contains duplicated adjacent description line {a!r}")
    for qid, length, sample in long_lines:
        audit.warn(f"Long description line ({length} chars) in {qid}: {sample}…")
    audit.metrics["long_description_lines"] = len(long_lines)

    # Exact item, advancement and image resolution.
    entries = load_jar_entries(args.jar_index.resolve())
    item_ids: set[str] = set()
    advancement_ids: set[str] = set()
    image_refs: set[str] = set()
    for ch in manifest.get("chapters", []):
        item_ids.add(ch["icon"])
        for image in ch.get("images", []):
            image_refs.add(image["image"])
        for q in ch.get("quests", []):
            item_ids.add(q["icon"])
            for line in q.get("description", []):
                image_refs.update(IMAGE_CODE.findall(line))
            for t in q.get("tasks", []):
                if t.get("item"):
                    item_ids.add(t["item"])
                if t.get("advancement"):
                    advancement_ids.add(t["advancement"])
            for r in q.get("rewards", []):
                if r.get("item"):
                    item_ids.add(r["item"])
                if r.get("item_data"):
                    item_ids.add(r["item_data"]["id"])
    for table in manifest.get("reward_tables", []):
        for r in table.get("rewards", []):
            if r.get("item"):
                item_ids.add(r["item"])
            if r.get("item_data"):
                item_ids.add(r["item_data"]["id"])
    for item in sorted(item_ids):
        if not resolve_item(item, entries, source_root):
            audit.error(f"Unresolved item/icon ID: {item}")
    for adv in sorted(advancement_ids):
        ns, path = adv.split(":", 1)
        if f"data/{ns}/advancement/{path}.json" not in entries and f"data/{ns}/advancements/{path}.json" not in entries:
            audit.error(f"Unresolved advancement ID: {adv}")
    for ref in sorted(image_refs):
        if not resolve_image(ref, entries, source_root, asset_roots):
            audit.error(f"Unresolved image reference: {ref}")
    audit.metrics["item_ids_checked"] = len(item_ids)
    audit.metrics["advancements_checked"] = len(advancement_ids)
    audit.metrics["image_refs_checked"] = len(image_refs)

    # The revised foundations must expose a small, verified Iron's Spells weave.
    # Keep this check deliberately narrow: it proves the authored Blood, Holy, and
    # mediator surfaces exist without pretending that a faction is a hard class.
    chapter_titles = {ch.get("title", ""): ch for ch in manifest.get("chapters", [])}
    iron_requirements = {
        "VvH 02 · House of Night": {
            "items": {"irons_spellbooks:blood_rune", "irons_spellbooks:bloody_vellum"},
            "images": {
                "irons_spellbooks:textures/item/blood_rune.png",
                "irons_spellbooks:textures/item/blood_staff.png",
                "irons_spellbooks:textures/item/blood_vial.png",
            },
        },
        "VvH 03 · Lantern Order": {
            "items": {"irons_spellbooks:holy_rune"},
            "images": {
                "irons_spellbooks:textures/item/holy_rune.png",
                "irons_spellbooks:textures/item/priest_chestplate.png",
                "irons_spellbooks:textures/item/upgrade_orb_holy.png",
            },
        },
        "VvH 04 · Free Companies": {
            "items": {"irons_spellbooks:arcane_essence", "irons_spellbooks:arcane_rune"},
            "images": {
                "irons_spellbooks:textures/item/arcane_rune.png",
                "irons_spellbooks:textures/item/affinity_ring_blood.png",
                "irons_spellbooks:textures/item/affinity_ring_holy.png",
            },
        },
    }
    iron_usage: dict[str, dict[str, list[str]]] = {}
    for title, requirement in iron_requirements.items():
        chapter = chapter_titles.get(title)
        if chapter is None:
            audit.error(f"Iron's Spells weave chapter is missing: {title}")
            continue
        chapter_items: set[str] = {chapter.get("icon", "")}
        chapter_images: set[str] = {img.get("image", "") for img in chapter.get("images", [])}
        for q in chapter.get("quests", []):
            chapter_items.add(q.get("icon", ""))
            for t in q.get("tasks", []):
                if t.get("item"):
                    chapter_items.add(t["item"])
            for r in q.get("rewards", []):
                if r.get("item"):
                    chapter_items.add(r["item"])
                if r.get("item_data"):
                    chapter_items.add(r["item_data"].get("id", ""))
        missing_items = sorted(requirement["items"] - chapter_items)
        missing_images = sorted(requirement["images"] - chapter_images)
        for item in missing_items:
            audit.error(f"Iron's Spells item is not surfaced in {title}: {item}")
        for image in missing_images:
            audit.error(f"Iron's Spells image is not surfaced in {title}: {image}")
        iron_usage[title] = {"items": sorted(requirement["items"] & chapter_items), "images": sorted(requirement["images"] & chapter_images)}
    audit.metrics["iron_spell_weave"] = iron_usage

    # Paper remains useful as lore text, but it must not be a primary campaign
    # payout. This catches regressions in both direct rewards and choice tables.
    paper_rewards: list[str] = []
    for chapter in manifest.get("chapters", []):
        for quest in chapter.get("quests", []):
            for reward in quest.get("rewards", []):
                item = reward.get("item") or (reward.get("item_data") or {}).get("id")
                if item == "minecraft:paper":
                    paper_rewards.append(f"{chapter.get('title')}: {quest.get('title')}: {reward.get('id')}")
    for table in manifest.get("reward_tables", []):
        for reward in table.get("rewards", []):
            item = reward.get("item") or (reward.get("item_data") or {}).get("id")
            if item == "minecraft:paper":
                paper_rewards.append(f"choice {table.get('title')}: {reward.get('id')}")
    audit.metrics["primary_paper_rewards"] = paper_rewards
    for reward in paper_rewards:
        audit.error(f"Primary campaign reward is still paper: {reward}")

    # Validate the legacy Living Atlas objects modified by the dev-modlist migration too.
    migrated_names = {
        "a_blank_page.snbt", "first_resonance.snbt", "the_weathered_ledger.snbt",
        "atlas_exchange.snbt", "1A0B1A4E5A9E2000.snbt", "1A0B1A4E5A9E3000.snbt",
    }
    migrated_items: set[str] = set()
    migrated_advancements: set[str] = set()
    for path, doc in parsed.items():
        if path.name not in migrated_names:
            continue
        for obj in iter_dicts(doc):
            item = obj.get("item")
            if isinstance(item, dict) and isinstance(item.get("id"), str):
                migrated_items.add(item["id"])
            icon = obj.get("icon")
            if isinstance(icon, dict) and isinstance(icon.get("id"), str):
                migrated_items.add(icon["id"])
            adv = obj.get("advancement")
            if isinstance(adv, str):
                migrated_advancements.add(adv)
    for item in sorted(migrated_items):
        if not resolve_item(item, entries, source_root):
            audit.error(f"Migrated Living Atlas unresolved item/icon ID: {item}")
    for adv in sorted(migrated_advancements):
        ns, path = adv.split(":", 1)
        if adv == "minecraft:story/mine_diamond":
            continue
        if f"data/{ns}/advancement/{path}.json" not in entries and f"data/{ns}/advancements/{path}.json" not in entries:
            audit.error(f"Migrated Living Atlas unresolved advancement ID: {adv}")
    audit.metrics["migrated_legacy_item_ids_checked"] = len(migrated_items)
    audit.metrics["migrated_legacy_advancement_ids_checked"] = len(migrated_advancements)

    # Reward scope and repeatable economy.
    table_ids = {t["id"] for t in manifest.get("reward_tables", [])}
    repeatable_weekly_prices = 0
    repeatable_rewards: list[dict[str, Any]] = []
    bevel_personal_per_player = 0
    bevel_team_total_per_progress_container = 0
    bevel_team_quests: list[str] = []
    for qid, q in vvh_quests.items():
        for r in q.get("rewards", []):
            if not isinstance(r.get("team_reward"), bool):
                audit.error(f"Reward {r.get('id')} in {qid} lacks explicit team_reward")
            if r.get("type") == "choice" and r.get("table_id") not in table_ids:
                audit.error(f"Reward {r.get('id')} references missing choice table {r.get('table_id')}")
            if r.get("item") == "numismatics:bevel":
                if q.get("repeatable"):
                    audit.error(f"Repeatable quest {qid} issues Bevel currency")
                elif r.get("team_reward"):
                    bevel_team_quests.append(qid)
                    bevel_team_total_per_progress_container += int(r.get("count", 1))
                else:
                    bevel_personal_per_player += int(r.get("count", 1))
        if q.get("repeatable"):
            if q.get("repeat_cooldown") != 604800:
                audit.error(f"Repeatable {qid} cooldown is {q.get('repeat_cooldown')}, expected 604800 seconds")
            pay = [t for t in q.get("tasks", []) if t.get("type") == "item" and t.get("item") == "numismatics:bevel" and t.get("consume")]
            rewards = q.get("rewards", [])
            if rewards:
                if len(pay) != 1:
                    audit.error(f"Economic repeatable {qid} must have exactly one consuming Bevel task")
                    price = 0
                else:
                    price = int(pay[0].get("count", 1))
                    repeatable_weekly_prices += price
                for r in rewards:
                    if not r.get("team_reward"):
                        audit.error(f"Repeatable cache reward {r.get('id')} must be team_reward=true")
                    if r.get("item") == "numismatics:bevel":
                        audit.error(f"Repeatable cache {qid} self-funds with Bevels")
                repeatable_rewards.append({"quest": qid, "price": price, "rewards": [(r.get("item"), r.get("count")) for r in rewards]})
            else:
                if pay:
                    audit.error(f"Rewardless social repeatable {qid} unexpectedly consumes Bevels")
                if not all(t.get("type") == "checkmark" for t in q.get("tasks", [])):
                    audit.error(f"Rewardless social repeatable {qid} must use trust-based checkmarks only")
                audit.metrics.setdefault("social_repeatables", []).append(qid)
    audit.metrics["repeatable_weekly_full_board_price"] = repeatable_weekly_prices
    audit.metrics["repeatable_caches"] = repeatable_rewards
    audit.metrics["bevel_personal_per_player"] = bevel_personal_per_player
    audit.metrics["bevel_team_quest_count"] = len(bevel_team_quests)
    audit.metrics["bevel_team_total_per_progress_container"] = bevel_team_total_per_progress_container
    audit.metrics["max_bevel_issuance_6_players_2_faction_teams"] = (
        bevel_personal_per_player * 6 + bevel_team_total_per_progress_container * 2
    )
    audit.metrics["max_bevel_issuance_6_neutral_parties"] = (
        bevel_personal_per_player * 6 + bevel_team_total_per_progress_container * 6
    )
    if bevel_personal_per_player or bevel_team_total_per_progress_container:
        audit.error(
            "VvH must issue zero Bevels; found "
            f"{bevel_personal_per_player} personal and "
            f"{bevel_team_total_per_progress_container} team-scoped currency"
        )

    # Layout collision and line-crossing heuristics, chapter by chapter.
    layout_issues: list[str] = []
    crossing_counts: dict[str, int] = {}
    for ch in manifest.get("chapters", []):
        qs = ch.get("quests", [])
        by_id = {q["id"]: q for q in qs}
        for a, b in itertools.combinations(qs, 2):
            dist = math.hypot(float(a["x"]) - float(b["x"]), float(a["y"]) - float(b["y"]))
            min_dist = 0.58 * (float(a.get("size", 1.0)) + float(b.get("size", 1.0)))
            if dist < min_dist:
                layout_issues.append(f"{ch['title']}: node overlap risk {a['title']} ↔ {b['title']} (distance {dist:.2f})")
        segments: list[tuple[str, str, tuple[float,float], tuple[float,float]]] = []
        for q in qs:
            if q.get("hide_dependency_lines"):
                continue
            for dep in q.get("dependencies", []):
                if dep in by_id:
                    p1=(float(by_id[dep]["x"]),float(by_id[dep]["y"]))
                    p2=(float(q["x"]),float(q["y"]))
                    segments.append((dep,q["id"],p1,p2))
        def orient(a,b,c):
            return (b[0]-a[0])*(c[1]-a[1])-(b[1]-a[1])*(c[0]-a[0])
        crossings=0
        for s1,s2 in itertools.combinations(segments,2):
            if {s1[0],s1[1]} & {s2[0],s2[1]}:
                continue
            a,b=s1[2],s1[3]; c,d=s2[2],s2[3]
            o1,o2,o3,o4=orient(a,b,c),orient(a,b,d),orient(c,d,a),orient(c,d,b)
            if o1*o2 < 0 and o3*o4 < 0:
                crossings += 1
        crossing_counts[ch["title"]] = crossings
        if crossings > 4:
            audit.warn(f"{ch['title']} has {crossings} dependency-line crossings in static layout")
    for issue in layout_issues:
        audit.error(issue)
    audit.metrics["dependency_crossings"] = crossing_counts

    # Dead-content heuristic: optional leaves with no reward and no repeatability.
    leaf_review: list[dict[str, str]] = []
    for qid, q in vvh_quests.items():
        if q.get("optional") and not q.get("rewards") and not reverse.get(qid) and not q.get("repeatable"):
            leaf_review.append({"id": qid, "title": q["title"]})
    audit.metrics["optional_rewardless_leaf_review"] = leaf_review
    if len(leaf_review) > 12:
        audit.warn(f"{len(leaf_review)} optional rewardless leaf quests need a deliberate dead-content review")

    # Minimum-path simulation to the season seal and After the Bells opener.
    target = next((qid for qid, q in vvh_quests.items() if q.get("title") == "SEAL SEASON ONE"), None)
    if target:
        try:
            best = minimum_completion_set(target, vvh_quests)
            audit.metrics["minimum_quest_count_to_season_seal"] = len(best)
            audit.metrics["one_minimum_path_ids"] = sorted(best)
            audit.metrics["minimum_path_checkmark_tasks"] = sum(
                sum(1 for t in vvh_quests[qid].get("tasks", []) if t.get("type") == "checkmark")
                for qid in best
            )
            charter_required = {
                qid for qid, q in vvh_quests.items()
                if q.get("title") in {"OPEN THE ISLAND CHARTER", "SIGN THE CHARTER"}
            }
            intended = set(best) | charter_required
            audit.metrics["minimum_intended_path_quest_count_including_charter"] = len(intended)
            audit.metrics["minimum_intended_path_checkmark_tasks_including_charter"] = sum(
                sum(1 for t in vvh_quests[qid].get("tasks", []) if t.get("type") == "checkmark")
                for qid in intended
            )
        except Exception as exc:  # noqa: BLE001
            audit.error(f"Minimum-path simulation failed: {exc}")
    else:
        audit.error("Could not identify SEAL SEASON ONE target")

    # KubeJS boundary.
    new_scripts = [p for p in (root / "kubejs").rglob("*vvh*") if p.is_file()] if (root / "kubejs").exists() else []
    if new_scripts:
        audit.error(f"Unexpected custom VvH KubeJS scripts: {[str(p.relative_to(root)) for p in new_scripts]}")
    audit.metrics["new_vvh_kubejs_files"] = len(new_scripts)

    report = {
        "status": "pass" if not audit.errors else "fail",
        "errors": audit.errors,
        "warnings": audit.warnings,
        "notes": audit.notes,
        "metrics": audit.metrics,
        "runtime_verification": [
            "requires runtime verification — exact FTB Quests loader acceptance and log cleanliness",
            "requires runtime verification — normal-scale client chapter rendering, text wrapping, contrast, and image crop",
            "requires runtime verification — two-account personal versus team reward claiming",
            "requires runtime verification — FTB Teams join/leave/switch progress and FTB Chunks claim handling",
            "requires runtime verification — optional skirmish PvP controls and backup restore procedure",
        ],
    }
    report_path.write_text(json.dumps(report, indent=2, sort_keys=True), encoding="utf-8")
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0 if not audit.errors else 1


if __name__ == "__main__":
    raise SystemExit(main())
