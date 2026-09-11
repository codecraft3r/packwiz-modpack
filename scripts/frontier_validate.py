#!/usr/bin/env python3
"""Validate the new campaign and its boundary with the archived VvH book."""
from __future__ import annotations
import argparse
import collections
import hashlib
import json
import math
import re
import struct
import tomllib
from pathlib import Path
from typing import Any
from frontier_campaign import chapter_names, ident, load
from vvh_validate import Parser

COINS = {'numismatics:spur': 1, 'numismatics:bevel': 8, 'numismatics:sprocket': 16,
         'numismatics:cog': 64, 'numismatics:crown': 512, 'numismatics:sun': 4096}
ENCHANTMENT_CAPS = {'minecraft:mending': 1, 'minecraft:fortune': 3,
                    'minecraft:unbreaking': 3, 'minecraft:protection': 4}
DISABLED_EQUIPMENT = {'mekanism:mekasuit_helmet', 'mekanism:mekasuit_bodyarmor',
                      'mekanism:mekasuit_pants', 'mekanism:mekasuit_boots',
                      'mekanism:antiprotonic_nucleosynthesizer', 'mekanism:quantum_entangloporter'}

PROGRESSION_MODES = {
    'welcome': 'flexible',
    'fresh': 'flexible',
    'milestone': 'flexible',
    'boss_milestone': 'flexible',
    'crew_confirmed': 'linear',
    'contract': 'linear',
    'shop': 'linear',
}
ART_PACK_REL = Path('global_packs/required_resources/vvh_backgrounds')
ART_IMAGE_FIELDS = ('image', 'x', 'y', 'width', 'height', 'alpha', 'order', 'rotation')
ART_RECORD_FIELDS = set(ART_IMAGE_FIELDS) | {'sha256', 'pixel_width', 'pixel_height'}

# This is loaded from the reviewed graph-runtime evidence below.  The fallback
# is deliberately empty: a shape is valid only when the shipped-runtime proof
# says so, rather than because it happens to be accepted by a local renderer.

def finite_number(value: Any) -> bool:
    return type(value) in (int, float) and math.isfinite(value)

def faction_of(quest: dict[str, Any]) -> str | None:
    """Return an explicit or source-key faction marker for cross-lock checks."""
    for field in ('faction', 'requires_faction', 'branch'):
        value = quest.get(field)
        if isinstance(value, str):
            value = value.lower()
            if 'hunter' in value:
                return 'hunter'
            if 'vampire' in value or 'night' in value:
                return 'vampire'
    key = str(quest.get('key', '')).lower()
    if key.startswith('hunter_') or key.endswith('_hunter'):
        return 'hunter'
    if key.startswith('vampire_') or key.endswith('_vampire'):
        return 'vampire'
    return None

def positive_int(value: Any) -> bool:
    return type(value) is int and value > 0

def currency(records: list[dict[str, Any]]) -> int:
    return sum(COINS.get(r.get('item', {}).get('id'), 0) * r.get('count', r.get('item', {}).get('count', 1)) for r in records)


def _art_asset_path(root: Path, image: Any) -> Path | None:
    """Resolve a resource location into the checked-in required-resource pack."""
    if not isinstance(image, str) or image.count(':') != 1:
        return None
    namespace, relative = image.split(':', 1)
    if not re.fullmatch(r'[a-z0-9_.-]+', namespace) or not relative or '\\' in relative:
        return None
    parts = Path(relative).parts
    if any(part in ('', '.', '..') for part in parts):
        return None
    pack_root = (root / ART_PACK_REL).resolve()
    candidate = (pack_root / 'assets' / namespace / Path(*parts)).resolve()
    try:
        candidate.relative_to(pack_root)
    except ValueError:
        return None
    return candidate


def _png_dimensions(path: Path) -> tuple[int, int] | None:
    """Read PNG IHDR dimensions without Pillow or another image dependency."""
    try:
        with path.open('rb') as handle:
            if handle.read(8) != b'\x89PNG\r\n\x1a\n':
                return None
            length_bytes = handle.read(4)
            chunk_type = handle.read(4)
            if len(length_bytes) != 4 or chunk_type != b'IHDR':
                return None
            length = struct.unpack('>I', length_bytes)[0]
            if length < 8 or length > 1024:
                return None
            ihdr = handle.read(length)
            if len(ihdr) < 8:
                return None
            width, height = struct.unpack('>II', ihdr[:8])
            return width, height
    except OSError:
        return None


def _file_sha256(path: Path) -> str | None:
    try:
        digest = hashlib.sha256()
        with path.open('rb') as handle:
            for chunk in iter(lambda: handle.read(1024 * 1024), b''):
                digest.update(chunk)
        return digest.hexdigest()
    except OSError:
        return None

def audit(root: Path) -> dict[str, Any]:
    manifest = load(root)
    if manifest is None:
        return {'active': False, 'errors': []}
    errors: list[str] = []
    def require(condition: bool, message: str) -> None:
        if not condition:
            errors.append(message)
    def read(relative: str):
        return json.loads((root / relative).read_text())
    try:
        art_source = json.loads((root / 'docs/frontier/art-source.json').read_text()) \
            if (root / 'docs/frontier/art-source.json').is_file() else None
        live = read('docs/frontier/evidence/live-registry.json')
        proof = read('docs/frontier/evidence/pack-provenance.json')
        advancements = read('docs/frontier/evidence/advancement-criteria.json')
        stacks = read('docs/frontier/evidence/reward-stack-limits.json')['items']
        survival = read('docs/frontier/evidence/survival-paths.json')
        graph_runtime = read('docs/frontier/evidence/graph-runtime.json')
        base = root / 'config/ftbquests/quests'
        chapters = [Parser(p.read_text(), str(p)).parse() for p in sorted((base / 'chapters').glob('*.snbt'))]
        tables = [Parser(p.read_text(), str(p)).parse() for p in sorted((base / 'reward_tables').glob('*.snbt'))]
        groups = Parser((base / 'chapter_groups.snbt').read_text(), 'chapter_groups').parse()['chapter_groups']
    except (OSError, ValueError, KeyError) as exc:
        return {'active': True, 'errors': [f'Frontier input could not be loaded: {exc}']}
    runtime_metadata = root / graph_runtime.get('metadata', '')
    require(runtime_metadata.is_file(), 'graph-runtime: missing pinned FTB Quests metadata')
    if runtime_metadata.is_file():
        require(hashlib.sha256(runtime_metadata.read_bytes()).hexdigest() == graph_runtime.get('metadata_sha256'),
                'graph-runtime: stale pinned-artifact proof')
        try:
            runtime_toml = tomllib.loads(runtime_metadata.read_text())
            require(runtime_toml.get('filename') == graph_runtime.get('artifact'),
                    'graph-runtime: artifact pin changed')
        except (OSError, ValueError, tomllib.TOMLDecodeError):
            require(False, 'graph-runtime: invalid pinned metadata')
    runtime_shapes = set(graph_runtime.get('shapes', []))
    require(bool(runtime_shapes), 'graph-runtime: no verified shipped quest shapes')
    require(bool(re.fullmatch(r'[0-9a-fA-F]{64}', str(graph_runtime.get('artifact_sha256', '')))),
            'graph-runtime: invalid artifact hash evidence')
    all_ids: dict[str, str] = {}
    quest_map: dict[str, dict[str, Any]] = {}
    def register(value: str, owner: str):
        require(bool(re.fullmatch(r'[0-9A-F]{16}', str(value))), f'{owner}: invalid ID {value}')
        require(value not in all_ids, f'Global ID collision: {value} in {owner}')
        all_ids[value] = owner
    for group in groups:
        register(group['id'], 'chapter group')
    for chapter in chapters:
        register(chapter['id'], chapter['filename'])
        require(chapter['group'] in all_ids, f'Unknown group on {chapter["filename"]}')
        for link in chapter.get('quest_links', []):
            link_id = link.get('id') if isinstance(link, dict) else None
            require(isinstance(link_id, str), f'{chapter["filename"]}: QuestLink has no ID')
            if isinstance(link_id, str):
                register(link_id, f'{chapter["filename"]} QuestLink')
        for q in chapter['quests']:
            register(q['id'], q.get('title', 'quest'));quest_map[q['id']] = q
            for family in ['tasks', 'rewards']:
                for entry in q.get(family, []):register(entry['id'], family)
    # QuestLink targets can only be resolved after all chapter quests have been
    # indexed.  Keep this separate from registration so forward references work.
    for chapter in chapters:
        for link in chapter.get('quest_links', []):
            target = link.get('linked_quest') if isinstance(link, dict) else None
            require(target in quest_map,
                    f'{chapter["filename"]}: QuestLink target does not resolve: {target}')
    for table in tables:
        register(table['id'], 'reward table')
        for r in table.get('rewards', []):
            if 'id' in r:register(r['id'], 'table reward')
    visiting: set[str] = set(); visited: set[str] = set()
    def visit(qid: str):
        if qid in visiting:
            errors.append(f'Dependency cycle at {qid}');return
        if qid in visited:return
        visiting.add(qid)
        for dep in quest_map[qid].get('dependencies', []):
            require(dep in quest_map, f'Missing dependency {dep}')
            if dep in quest_map:visit(dep)
        visiting.remove(qid);visited.add(qid)
    for qid in quest_map:visit(qid)
    for ns, record in proof.items():
        path = root / record['metadata']
        require(path.is_file(), f'{ns}: missing pinned metadata')
        if not path.is_file():continue
        metadata = tomllib.loads(path.read_text())
        require(hashlib.sha256(path.read_bytes()).hexdigest() == record['metadata_sha256'], f'{ns}: stale pinned-artifact proof')
        require(metadata['filename'] == record['filename'] and metadata['download']['hash'] == record['download_hash'], f'{ns}: artifact pin changed')
        require(bool(record.get('live_jar_sha256')), f'{ns}: no live artifact hash')
    references: set[tuple[str, str]] = set()
    for relative, digest in survival['pack_overrides'].items():
        path = root / relative
        require(path.is_file() and hashlib.sha256(path.read_bytes()).hexdigest() == digest,
                f'{relative}: survival recipe evidence is stale')
    direct_items = {t['item']['id'] for q in manifest['quests'] for t in q['tasks'] + q['rewards'] if 'item' in t}
    direct_items.update(t['to_observe'] for q in manifest['quests'] for t in q['tasks'] if t['type'] == 'observation')
    for iid in sorted(direct_items):
        ns = iid.split(':')[0]
        if ns == 'minecraft' or iid in COINS:
            continue  # Vanilla survival items and the deliberately server-issued currency.
        receipt = survival['items'].get(iid)
        require(receipt is not None, f'{iid}: missing survival obtainability evidence')
        if receipt and receipt['kind'] != 'pack_override':
            require(ns in proof and receipt.get('parent_artifact_sha256') == proof[ns]['live_jar_sha256'],
                    f'{iid}: survival evidence does not match the pinned artifact')
    source_quests = {q['key']: q for q in manifest['quests']}
    require(len(source_quests) == len(manifest['quests']), 'Duplicate source quest keys')
    source_chapters = {c['key']: c for c in manifest.get('chapters', [])}
    require(len(source_chapters) == len(manifest.get('chapters', [])), 'Duplicate source chapter keys')
    require('welcome' in source_quests, 'Source graph has no welcome root')
    source_deps: dict[str, list[str]] = {}
    dependents: dict[str, list[str]] = collections.defaultdict(list)
    for q in manifest['quests']:
        key = q.get('key')
        deps = q.get('deps')
        require(isinstance(deps, list), f'{key}: source prerequisites must be a list')
        if not isinstance(deps, list):
            deps = []
        source_deps[key] = deps
        if all(isinstance(dep, str) for dep in deps):
            require(len(deps) == len(set(deps)), f'{key}: duplicate source prerequisites')
            require(key not in deps, f'{key}: quest cannot depend on itself')
        if key != 'welcome':
            require(bool(deps), f'{key}: every new quest except welcome needs a prerequisite')
        else:
            require(not deps, 'welcome: root quest cannot have prerequisites')
        for dep in deps:
            known_dependency = isinstance(dep, str) and dep in source_quests
            require(known_dependency, f'{key}: unknown source prerequisite {dep}')
            if known_dependency:
                dependents[dep].append(key)

    # Validate direction and reachability in the authored source graph.  The
    # emitted graph is checked separately above, including archived chapters.
    source_visiting: set[str] = set()
    source_visited: set[str] = set()
    def visit_source(key: str) -> None:
        if key in source_visiting:
            errors.append(f'Source dependency cycle at {key}')
            return
        if key in source_visited or key not in source_quests:
            return
        source_visiting.add(key)
        for dep in source_deps.get(key, []):
            if isinstance(dep, str) and dep in source_quests:
                visit_source(dep)
        source_visiting.remove(key)
        source_visited.add(key)
    for key in source_quests:
        visit_source(key)
    reachable: set[str] = set()
    if 'welcome' in source_quests:
        todo = ['welcome']
        while todo:
            key = todo.pop()
            if key in reachable:
                continue
            reachable.add(key)
            todo.extend(dependents.get(key, []))
    for key in source_quests:
        require(key in reachable, f'{key}: source graph is disconnected from welcome')

    def source_ancestors(key: str) -> set[str]:
        found: set[str] = set()
        todo = list(source_deps.get(key, []))
        while todo:
            dep = todo.pop()
            if not isinstance(dep, str) or dep in found or dep not in source_quests:
                continue
            found.add(dep)
            todo.extend(source_deps.get(dep, []))
        return found

    # Faction branches may depend on shared route work, but one faction must
    # never unlock itself through the opposing faction's private milestone.
    for q in manifest['quests']:
        q_faction = faction_of(q)
        for dep in source_ancestors(q.get('key')):
            dep_faction = faction_of(source_quests.get(dep, {}))
            require(not (q_faction and dep_faction and q_faction != dep_faction),
                    f'{q.get("key")}: faction cross-lock on {dep}')

    for iid, record in stacks.items():
        require(positive_int(record['max_stack_size']), f'{iid}: invalid stack receipt')
        ns = iid.split(':')[0]
        evidence = record['evidence']
        hashes = {j['sha256'].lower() for j in evidence.get('jars', [])}
        hashes.update(str(evidence.get(k, '')).lower() for k in ['sha256', 'parent_artifact_sha256'])
        if ns != 'minecraft':
            require(ns in proof and proof[ns]['live_jar_sha256'].lower() in hashes,
                    f'{iid}: stack receipt does not match the pinned artifact')

    external_by_chapter: dict[str, set[str]] = collections.defaultdict(set)
    external_ancestors_by_chapter: dict[str, set[str]] = collections.defaultdict(set)
    for q in manifest['quests']:
        key = q['key']
        chapter_key = q.get('chapter')
        require(chapter_key in source_chapters, f'{key}: unknown source chapter {chapter_key}')
        for field in ('x', 'y', 'size'):
            require(finite_number(q.get(field)), f'{key}: {field} must be finite')
        require(finite_number(q.get('size')) and 0 < q.get('size') <= 4,
                f'{key}: quest size must be positive and sensible')
        shape = q.get('shape')
        require(isinstance(shape, str) and shape in runtime_shapes,
                f'{key}: unsupported shipped quest shape {shape!r}')
        ancestors = source_ancestors(key)
        for dep in ancestors:
            if source_quests.get(dep, {}).get('chapter') != chapter_key:
                external_ancestors_by_chapter[chapter_key].add(dep)
        for dep in source_deps.get(key, []):
            dep_chapter = source_quests.get(dep, {}).get('chapter') if isinstance(dep, str) else None
            if dep_chapter != chapter_key:
                external_by_chapter[chapter_key].add(dep)
    for chapter_key, chapter in source_chapters.items():
        links = chapter.get('links', [])
        require(isinstance(links, list), f'{chapter_key}: source QuestLinks must be a list')
        if not isinstance(links, list):
            links = []
        seen_links: set[str] = set()
        for link in links:
            target = link.get('quest') if isinstance(link, dict) else None
            require(isinstance(target, str) and target in source_quests,
                    f'{chapter_key}: QuestLink target does not resolve: {target}')
            require(target not in seen_links, f'{chapter_key}: duplicate source QuestLink for {target}')
            if isinstance(target, str):
                seen_links.add(target)
            for field in ('x', 'y'):
                value = link.get(field) if isinstance(link, dict) else None
                require(finite_number(value), f'{chapter_key}: QuestLink {field} must be finite')
            require(target in external_ancestors_by_chapter.get(chapter_key, set()),
                    f'{chapter_key}: QuestLink is not an external prerequisite: {target}')
        for target in sorted(external_by_chapter.get(chapter_key, set())):
            require(sum(1 for link in links if isinstance(link, dict) and link.get('quest') == target) == 1,
                    f'{chapter_key}: external prerequisite {target} needs exactly one local QuestLink')

    for ch in manifest['chapters']:references.add(('item', ch['icon']))
    new_names = chapter_names(root)
    actual_new = [c for c in chapters if c['filename'] in new_names]
    actual_new_by_key = {c['filename'][len('frontier_'):]: c for c in actual_new}
    require(len(actual_new) == len(manifest['chapters']), 'Missing Frontier chapters')
    require(sum(len(c['quests']) for c in actual_new) == len(manifest['quests']), 'Frontier quest count differs from source')

    # Frontier backgrounds are authored in a reviewable JSON contract and
    # projected into native FTB ``images`` compounds by compose().  Keep the
    # provenance (digest and source pixel dimensions) out of SNBT while
    # checking it here against the exact emitted native fields and asset pack.
    # Frontier is now an art-backed campaign.  Keep this fail-closed even if a
    # caller deletes both the source contract and emitted image compounds:
    # every active Frontier build must ship the reviewed art closure.
    if art_source is None:
        require(False, 'art-source: manifest is required for the active Frontier campaign')
        art_source = {}
    else:
        require(art_source.get('schema') == 'frontier-art-v1', 'art-source: schema must be frontier-art-v1')
        art_chapters = art_source.get('chapters')
        require(isinstance(art_chapters, dict), 'art-source: chapters must be a mapping')
        if not isinstance(art_chapters, dict):
            art_chapters = {}
        require(len(art_chapters) == 9, f'art-source: expected exactly 9 backgrounds, found {len(art_chapters)}')
        expected_chapter_keys = {chapter.get('key') for chapter in manifest.get('chapters', [])}
        require(len(expected_chapter_keys) == 9 and None not in expected_chapter_keys,
                'Frontier source must define exactly 9 chapter keys for backgrounds')
        require(set(art_chapters) == expected_chapter_keys,
                'art-source: chapter keys differ from Frontier source chapters')
        resourcepack_root = root / ART_PACK_REL
        mcmeta = resourcepack_root / 'pack.mcmeta'
        require(mcmeta.is_file(), 'art-source: resourcepack pack.mcmeta is missing')
        if mcmeta.is_file():
            try:
                mcmeta_data = json.loads(mcmeta.read_text())
                require(mcmeta_data.get('pack', {}).get('pack_format') == 34,
                        'art-source: resourcepack pack.mcmeta must use format 34')
            except (OSError, ValueError, AttributeError):
                require(False, 'art-source: resourcepack pack.mcmeta is invalid JSON')
        for chapter_key in sorted(expected_chapter_keys - {None}):
            record = art_chapters.get(chapter_key)
            owner = f'art-source:{chapter_key}'
            require(isinstance(record, dict), f'{owner}: background record must be an object')
            if not isinstance(record, dict):
                continue
            require(set(record) == ART_RECORD_FIELDS,
                    f'{owner}: fields must be exactly {sorted(ART_RECORD_FIELDS)}')
            for field in ('x', 'y', 'width', 'height', 'rotation'):
                require(finite_number(record.get(field)), f'{owner}: {field} must be finite')
            require(finite_number(record.get('width')) and record.get('width') > 0,
                    f'{owner}: width must be positive')
            require(finite_number(record.get('height')) and record.get('height') > 0,
                    f'{owner}: height must be positive')
            require(type(record.get('alpha')) is int and 1 <= record.get('alpha') <= 255,
                    f'{owner}: alpha must be an integer from 1 through 255')
            require(type(record.get('order')) is int and record.get('order') < 0,
                    f'{owner}: order must be a negative native background order')
            require(finite_number(record.get('rotation')) and record.get('rotation') == 0,
                    f'{owner}: rotation must be native 0')
            require(type(record.get('pixel_width')) is int and record.get('pixel_width') > 0,
                    f'{owner}: pixel_width must be positive')
            require(type(record.get('pixel_height')) is int and record.get('pixel_height') > 0,
                    f'{owner}: pixel_height must be positive')
            if (finite_number(record.get('width')) and finite_number(record.get('height')) and
                    type(record.get('pixel_width')) is int and record.get('pixel_width') > 0 and
                    type(record.get('pixel_height')) is int and record.get('pixel_height') > 0 and
                    record.get('height') > 0):
                require(math.isclose(
                    record['width'] / record['height'],
                    record['pixel_width'] / record['pixel_height'],
                    rel_tol=1e-6,
                    abs_tol=1e-6,
                ), f'{owner}: native image aspect ratio differs from PNG pixel ratio')
            require(isinstance(record.get('sha256'), str) and
                    bool(re.fullmatch(r'[0-9a-fA-F]{64}', str(record.get('sha256')))),
                    f'{owner}: sha256 must be a 64-character hex digest')
            require(record.get('image') == f'poiesis:textures/questpics/frontier/{chapter_key}.png',
                    f'{owner}: image path must use the Frontier chapter resource convention')
            asset = _art_asset_path(root, record.get('image'))
            require(asset is not None and asset.suffix.lower() == '.png',
                    f'{owner}: image must be a safe PNG resource location')
            if asset is None:
                continue
            require(asset.is_file(), f'{owner}: missing asset {record.get("image")}')
            if asset.is_file():
                digest = _file_sha256(asset)
                require(digest is not None and digest.lower() == str(record.get('sha256', '')).lower(),
                        f'{owner}: asset SHA256 differs from art-source')
                dimensions = _png_dimensions(asset)
                require(dimensions == (record.get('pixel_width'), record.get('pixel_height')),
                        f'{owner}: PNG dimensions differ from art-source')
            emitted = actual_new_by_key.get(chapter_key, {}).get('images')
            require(isinstance(emitted, list) and len(emitted) == 1,
                    f'{owner}: emitted chapter must contain exactly one background')
            if isinstance(emitted, list) and len(emitted) == 1:
                image = emitted[0]
                require(isinstance(image, dict) and set(image) == set(ART_IMAGE_FIELDS),
                        f'{owner}: emitted image has unexpected fields')
                if isinstance(image, dict):
                    for field in ART_IMAGE_FIELDS:
                        require(image.get(field) == record.get(field),
                                f'{owner}: emitted {field} differs from art-source')
    for chapter_key, emitted_chapter in actual_new_by_key.items():
        require(emitted_chapter.get('default_hide_dependency_lines') is False,
                f'{chapter_key}: Frontier dependency lines must remain visible')
        links = emitted_chapter.get('quest_links', [])
        require(isinstance(links, list), f'{chapter_key}: emitted QuestLinks must be a list')
        if not isinstance(links, list):
            links = []
        expected_targets = external_by_chapter.get(chapter_key, set())
        source_links = {link['quest']: link for link in source_chapters.get(chapter_key, {}).get('links', [])
                        if isinstance(link, dict) and isinstance(link.get('quest'), str)}
        emitted_targets: list[str] = []
        for link in links:
            target = link.get('linked_quest') if isinstance(link, dict) else None
            emitted_targets.append(target)
            required_link_fields = {'id', 'linked_quest', 'x', 'y', 'shape', 'size'}
            require(isinstance(link, dict) and set(link) == required_link_fields,
                    f'{chapter_key}: malformed emitted QuestLink')
            require(target in quest_map, f'{chapter_key}: QuestLink target does not resolve: {target}')
            require(finite_number(link.get('x')) and finite_number(link.get('y')),
                    f'{chapter_key}: emitted QuestLink coordinates must be finite')
            require(link.get('shape') == 'diamond' and link.get('size') == 0.8,
                    f'{chapter_key}: emitted QuestLink geometry is not verified diamond/0.8')
            if isinstance(target, str) and target.startswith('6E26'):
                target_key = next((key for key in source_quests
                                   if ident('quest:' + key) == target), None)
                if target_key in source_links:
                    source_link = source_links[target_key]
                    require(link.get('id') == ident(f'link:{chapter_key}:{target_key}'),
                            f'{chapter_key}: QuestLink ID differs from source target')
                    require(link.get('x') == float(source_link.get('x')) and
                            link.get('y') == float(source_link.get('y')),
                            f'{chapter_key}: QuestLink coordinates differ from source')
        for dep in sorted(expected_targets):
            target_id = ident('quest:' + dep)
            require(emitted_targets.count(target_id) == 1,
                    f'{chapter_key}: external prerequisite {dep} needs exactly one native QuestLink')
        require(set(emitted_targets) == {ident('quest:' + dep) for dep in source_links},
                f'{chapter_key}: emitted QuestLinks differ from source prerequisites')
    for q in manifest['quests']:
        emitted = quest_map.get(ident('quest:' + q['key']))
        require(emitted is not None, f'Missing quest {q["key"]}')
        references.add(('item', q['icon']))
        require(currency(q['rewards']) == q['coins'], f'{q["key"]}: displayed currency differs from rewards')
        require(bool(q['tasks']) and bool(q['rewards']), f'{q["key"]}: empty task or reward set')
        require(q['kind'] in ['welcome', 'fresh', 'milestone', 'boss_milestone', 'crew_confirmed', 'contract', 'shop'],
                f'{q["key"]}: unsupported quest kind')
        require(len(q['title'].split()) <= 4, f'{q["key"]}: graph title exceeds four words')
        for dep in q['deps']:
            require(dep in source_quests, f'{q["key"]}: unknown source prerequisite {dep}')
        if emitted:
            require(emitted.get('optional') is True, f'{q["key"]}: new adventure must be optional')
            require(emitted.get('progression_mode') == PROGRESSION_MODES.get(q['kind']),
                    f'{q["key"]}: progression mode does not match quest kind')
            expected_dependencies = {ident('quest:' + dep) for dep in q['deps']}
            actual_dependencies = set(emitted.get('dependencies', []))
            require(actual_dependencies == expected_dependencies,
                    f'{q["key"]}: emitted dependencies differ from source')
            for field in ('x', 'y', 'size', 'shape'):
                require(emitted.get(field) == q.get(field),
                        f'{q["key"]}: emitted {field} differs from source')
            require(emitted.get('hide_dependency_lines') is not True,
                    f'{q["key"]}: Frontier dependency lines must remain visible')
        for t in q['tasks']:
            require(t['type'] in ['advancement', 'item', 'kill', 'observation', 'checkmark'], f'{q["key"]}: unsupported task')
            if 'item' in t:references.add(('item', t['item']['id']))
            if t['type'] == 'item':
                require(positive_int(t.get('count')) and type(t.get('consume_items')) is bool,
                        f'{q["key"]}: item count/consumption must be explicit')
            if t['type'] == 'kill':
                require(positive_int(t.get('value')), f'{q["key"]}: invalid kill target')
            if t.get('consume_items'):require(t.get('task_screen_only') is True, f'{q["key"]}: automatic consumption')
            if t['type'] == 'observation':references.add(('block', t['to_observe']))
            if t['type'] == 'kill':references.add(('entity', t['entity']))
            if t['type'] == 'advancement':
                references.add(('advancement', t['advancement']))
                require(t['advancement'] in advancements or t['advancement'] == 'minecraft:end/enter_end_gateway', f'Missing advancement criteria: {t["advancement"]}')
                require(t.get('criterion') == '', f'{q["key"]}: whole advancement must be explicit')
        for r in q['rewards']:
            iid = r['item']['id']
            references.add(('item', iid))
            # One item fits any valid registered item. Bulk entries fail closed
            # unless the maximum is backed by the pinned registry/constructor.
            limit = stacks.get(iid, {}).get('max_stack_size', 1)
            require(r['type'] == 'item' and positive_int(r['count']) and r['count'] <= limit,
                    f'{q["key"]}: reward exceeds verified stack limit for {iid} ({limit})')
            components = r['item'].get('components', {})
            require(not components or (iid == 'minecraft:enchanted_book' and set(components) == {'minecraft:stored_enchantments'}),
                    f'{q["key"]}: unreviewed reward components')
            if 'minecraft:stored_enchantments' in components:
                enchantments = components['minecraft:stored_enchantments']
                levels = enchantments.get('levels', {})
                require(set(enchantments) == {'levels'} and len(levels) == 1 and all(
                    positive_int(level) and level <= ENCHANTMENT_CAPS.get(enchantment, 0)
                    for enchantment, level in levels.items()), f'{q["key"]}: invalid enchanted-book component')
            require(r['team_reward'] == q['shared'], f'{q["key"]}: mixed personal/shared rewards')
            require(r.get('autoclaim') == 'disabled', f'{q["key"]}: automatic reward claim')
        if all(t['type'] == 'checkmark' for t in q['tasks']):require(q['coins'] == 0 and not q['repeat'], f'{q["key"]}: honor check issues currency or repeats')
        if q['kind'] in ['contract', 'shop']:require(q['shared'] and q['repeat'] >= 60, f'{q["key"]}: repeat scope/cooldown missing')
        else:
            require(not q['repeat'], f'{q["key"]}: one-time reward made repeatable')
        if q['kind'] == 'contract':
            require(q['repeat'] >= 21600, f'{q["key"]}: faucet cooldown too short')
            require(bool(q['deps']) and all(not source_quests.get(d, {}).get('repeat', 1) for d in q['deps']),
                    f'{q["key"]}: faucet needs a one-time progression gate')
            require(all(t['type'] == 'kill' or (t['type'] == 'item' and t.get('consume_items') is True)
                        for t in q['tasks']), f'{q["key"]}: contract lacks fresh work or consumed inputs')
        if q['kind'] == 'shop':
            price = currency(q['tasks'])
            require(price > 0 and q['coins'] == 0 and all(
                t['type'] == 'item' and t['item']['id'] in COINS and t.get('consume_items') is True
                and t.get('task_screen_only') is True for t in q['tasks']), f'{q["key"]}: purchase must consume a positive manual coin payment')
            prices = re.findall(r'Price: (\d+) Spurs\.', '\n'.join(q['description']))
            require(prices == [str(price)], f'{q["key"]}: advertised price differs from consumed coins')
        text = '\n'.join([q['title']] + q['description'])
        require(not re.search(r'(?<!\\)&\s', text), f'{q["key"]}: invalid formatting code')
    for kind, value in sorted(references):
        require(value not in DISABLED_EQUIPMENT, f'{value}: disabled equipment must not be required or awarded')
        require(value.split(':')[0] == 'minecraft' or value.split(':')[0] in proof, f'{value}: no artifact proof')
        result = live.get(kind + ' ' + value)
        require(result is not None, f'Missing live registry check: {kind} {value}')
        if result:
            require(result['code'] == 0 and not re.search(r'unknown|invalid|incorrect|failed to parse', result['response'], re.I), f'Failed live registry check: {kind} {value}')
    personal = sum(q['coins'] for q in manifest['quests'] if not q['repeat'] and not q['shared'])
    shared = sum(q['coins'] for q in manifest['quests'] if not q['repeat'] and q['shared'])
    faucets = [q for q in manifest['quests'] if q['kind'] == 'contract']
    board = sum(currency(q['tasks']) for q in manifest['quests'] if q['kind'] == 'shop')
    per_window = sum(q['coins'] for q in faucets)
    require(personal <= 4704 and shared == 0, 'One-time currency exceeds the reviewed budget')
    require(per_window <= 480, 'Repeatable currency exceeds the reviewed six-hour budget')
    require(per_window < board, 'One repeat window can finance the entire new board')
    sold = {r['item']['id'] for q in manifest['quests'] if q['kind'] == 'shop' for r in q['rewards']}
    bought = {t['item']['id'] for q in faucets for t in q['tasks'] if 'item' in t}
    require(not sold & bought, 'Direct store-to-contract currency arbitrage')
    # The old objects are generated from their reviewed source, not the stale live snapshot.
    import vvh_campaign_v3 as source
    expected_files = source.outputs(root)
    for path, content in expected_files.items():
        if path.parent == base / 'chapters' and path.stem in new_names:
            require(path.exists(), f'Frontier emitted file is missing: {path.name}')
            if path.exists():
                require(Parser(path.read_text(), str(path)).parse() == Parser(content, str(path)).parse(),
                        f'Frontier emitted file differs from source: {path.name}')
        if path == root / 'docs/frontier/render-manifest.json':
            manifest_path = path
            require(manifest_path.exists(), 'Frontier render manifest is missing')
            if manifest_path.exists():
                try:
                    require(json.loads(manifest_path.read_text()) == json.loads(content),
                            'Frontier render manifest differs from source')
                except (OSError, ValueError):
                    require(False, 'Frontier render manifest is invalid JSON')
    old_chapters, _ = source.build_campaign()
    expected_quests = {ident('quest:' + key) for key in source_quests}
    for ch in old_chapters:
        rendered_old = Parser(source.render_chapter(ch), ch.filename).parse()
        for q in rendered_old['quests']:
            expected_quests.add(q['id'])
            require(quest_map.get(q['id']) == q, f'Archived quest changed: {q["id"]}')
    require(set(quest_map) == expected_quests, 'Loaded book contains unreviewed or missing quests')
    return {'active': True, 'errors': errors, 'new_quests': len(manifest['quests']),
            'archived_quests': sum(len(c.quests) for c in old_chapters), 'total_quests': len(quest_map),
            'unique_registry_ids': len(all_ids), 'resource_checks': len(references),
            'verified_bulk_reward_items': len(stacks),
            'modded_survival_paths': len(survival['items']),
            'economy_spurs': {'minimum_required_route': 0, 'personal_completionist': personal, 'team_one_time': shared,
                'repeatable_per_team_per_six_hours': per_window, 'weekly_per_team_upper_bound': per_window * 28,
                'weekly_five_solo_teams_upper_bound': per_window * 28 * 5, 'one_of_each_new_purchase': board},
            'runtime': 'Registry syntax and exact pinned artifact hashes verified; client GUI, reward claims and two-account purchase behavior pending.'}

def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', type=Path, default=Path(__file__).resolve().parents[1]);parser.add_argument('--output', type=Path)
    args = parser.parse_args();report = audit(args.root.resolve());text = json.dumps(report, indent=2)+'\n'
    if args.output:args.output.parent.mkdir(parents=True, exist_ok=True);args.output.write_text(text)
    print(text);return int(bool(report['errors']))
if __name__ == '__main__':raise SystemExit(main())
