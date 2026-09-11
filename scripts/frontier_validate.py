#!/usr/bin/env python3
"""Validate the new campaign and its boundary with the archived VvH book."""
from __future__ import annotations
import argparse
import collections
import hashlib
import json
import re
import tomllib
from pathlib import Path
from typing import Any
from frontier_campaign import chapter_names, ident, load
from vvh_validate import Parser

COINS = {'numismatics:spur': 1, 'numismatics:bevel': 8, 'numismatics:sprocket': 16,
         'numismatics:cog': 64, 'numismatics:crown': 512, 'numismatics:sun': 4096}

def currency(records: list[dict[str, Any]]) -> int:
    return sum(COINS.get(r.get('item', {}).get('id'), 0) * r.get('count', r.get('item', {}).get('count', 1)) for r in records)

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
        live = read('docs/frontier/evidence/live-registry.json')
        proof = read('docs/frontier/evidence/pack-provenance.json')
        advancements = read('docs/frontier/evidence/advancement-criteria.json')
        base = root / 'config/ftbquests/quests'
        chapters = [Parser(p.read_text(), str(p)).parse() for p in sorted((base / 'chapters').glob('*.snbt'))]
        tables = [Parser(p.read_text(), str(p)).parse() for p in sorted((base / 'reward_tables').glob('*.snbt'))]
        groups = Parser((base / 'chapter_groups.snbt').read_text(), 'chapter_groups').parse()['chapter_groups']
    except (OSError, ValueError, KeyError) as exc:
        return {'active': True, 'errors': [f'Frontier input could not be loaded: {exc}']}
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
        for q in chapter['quests']:
            register(q['id'], q.get('title', 'quest'));quest_map[q['id']] = q
            for family in ['tasks', 'rewards']:
                for entry in q.get(family, []):register(entry['id'], family)
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
    for ch in manifest['chapters']:references.add(('item', ch['icon']))
    new_names = chapter_names(root)
    actual_new = [c for c in chapters if c['filename'] in new_names]
    require(len(actual_new) == len(manifest['chapters']), 'Missing Frontier chapters')
    require(sum(len(c['quests']) for c in actual_new) == len(manifest['quests']), 'Frontier quest count differs from source')
    for q in manifest['quests']:
        emitted = quest_map.get(ident('quest:' + q['key']))
        require(emitted is not None, f'Missing quest {q["key"]}')
        references.add(('item', q['icon']))
        require(currency(q['rewards']) == q['coins'], f'{q["key"]}: displayed currency differs from rewards')
        require(bool(q['tasks']) and bool(q['rewards']), f'{q["key"]}: empty task or reward set')
        if emitted:
            require(emitted.get('optional') is True, f'{q["key"]}: new adventure must be optional')
        for t in q['tasks']:
            require(t['type'] in ['advancement', 'item', 'kill', 'observation', 'checkmark'], f'{q["key"]}: unsupported task')
            if 'item' in t:references.add(('item', t['item']['id']))
            if t.get('consume_items'):require(t.get('task_screen_only') is True, f'{q["key"]}: automatic consumption')
            if t['type'] == 'observation':references.add(('block', t['to_observe']))
            if t['type'] == 'kill':references.add(('entity', t['entity']))
            if t['type'] == 'advancement':
                references.add(('advancement', t['advancement']))
                require(t['advancement'] in advancements or t['advancement'] == 'minecraft:end/enter_end_gateway', f'Missing advancement criteria: {t["advancement"]}')
                require(t.get('criterion') == '', f'{q["key"]}: whole advancement must be explicit')
        for r in q['rewards']:
            references.add(('item', r['item']['id']))
            require(r['type'] == 'item' and 0 < r['count'] <= 64, f'{q["key"]}: invalid reward quantity/type')
            require(r['team_reward'] == q['shared'], f'{q["key"]}: mixed personal/shared rewards')
            require(r.get('autoclaim') == 'disabled', f'{q["key"]}: automatic reward claim')
        if all(t['type'] == 'checkmark' for t in q['tasks']):require(q['coins'] == 0 and not q['repeat'], f'{q["key"]}: honor check issues currency or repeats')
        if q['kind'] in ['contract', 'shop']:require(q['shared'] and q['repeat'] >= 60, f'{q["key"]}: repeat scope/cooldown missing')
        else:require(not q['deps'], f'{q["key"]}: adventure unexpectedly gated')
        if q['kind'] == 'contract':require(q['repeat'] >= 21600, f'{q["key"]}: faucet cooldown too short')
        text = '\n'.join([q['title']] + q['description'])
        require(not re.search(r'(?<!\\)&\s', text), f'{q["key"]}: invalid formatting code')
    for kind, value in sorted(references):
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
    require(per_window < board, 'One repeat window can finance the entire new board')
    sold = {r['item']['id'] for q in manifest['quests'] if q['kind'] == 'shop' for r in q['rewards']}
    bought = {t['item']['id'] for q in faucets for t in q['tasks'] if 'item' in t}
    require(not sold & bought, 'Direct store-to-contract currency arbitrage')
    # The old objects are generated from their reviewed source, not the stale live snapshot.
    import vvh_campaign_v3 as source
    expected_files = source.outputs(root)
    for path, content in expected_files.items():
        if path.parent == base / 'chapters' and path.stem in new_names:
            if not path.exists():
                continue
            require(Parser(path.read_text(), str(path)).parse() == Parser(content, str(path)).parse(), f'Frontier emitted file differs from source: {path.name}')
    old_chapters, _ = source.build_campaign()
    for ch in old_chapters:
        rendered_old = Parser(source.render_chapter(ch), ch.filename).parse()
        for q in rendered_old['quests']:require(quest_map.get(q['id']) == q, f'Archived quest changed: {q["id"]}')
    return {'active': True, 'errors': errors, 'new_quests': len(manifest['quests']),
            'archived_quests': sum(len(c.quests) for c in old_chapters), 'total_quests': len(quest_map),
            'unique_registry_ids': len(all_ids), 'resource_checks': len(references),
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
