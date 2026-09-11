#!/usr/bin/env python3
"""Compose the progression-aware campaign over the preserved VvH source.

No world/player files are inputs. The source manifest is deliberately kept
outside the distributed pack. Existing VvH quest/task/reward IDs stay intact.
"""
from __future__ import annotations
import copy
import hashlib
import json
from pathlib import Path
from typing import Any

SOURCE_REL = Path('docs/frontier/quest-source.json')
ART_SOURCE_REL = Path('docs/frontier/art-source.json')

def ident(key: str) -> str:
    return '6E26' + hashlib.sha256(('frontier-v1:' + key).encode()).hexdigest()[:12].upper()

def load(root: Path) -> dict[str, Any] | None:
    path = root / SOURCE_REL
    return json.loads(path.read_text()) if path.exists() else None


def load_art_source(root: Path) -> dict[str, Any] | None:
    """Load the reviewed chapter-background contract when it is available.

    The art manifest is intentionally a separate source contract from the
    quest graph.  This lets the asset owner update generated PNGs and their
    provenance without asking the quest generator to infer image placement.
    Validation owns the strict schema checks; composition only projects the
    native FTB image fields into the emitted chapter.
    """
    path = root / ART_SOURCE_REL
    return json.loads(path.read_text()) if path.exists() else None


def chapter_image(root: Path, chapter_key: str) -> dict[str, Any] | None:
    """Return one native FTB image entry for ``chapter_key`` if authored."""
    art_source = load_art_source(root)
    if not art_source:
        return None
    records = art_source.get('chapters')
    if not isinstance(records, dict):
        return None
    record = records.get(chapter_key)
    if not isinstance(record, dict):
        return None
    # sha256 and pixel dimensions are provenance fields, not FTB image
    # properties.  Keep the emitted shape deliberately small and stable.
    return {key: copy.deepcopy(record[key]) for key in (
        'image', 'x', 'y', 'width', 'height', 'alpha', 'order', 'rotation'
    ) if key in record}

def chapter_names(root: Path) -> set[str]:
    manifest = load(root)
    return {'frontier_' + c['key'] for c in manifest['chapters']} if manifest else set()

def compose(root: Path, legacy: dict[Path, str], serialize) -> dict[Path, str]:
    """Preserve legacy quest objects; alter only chapter placement and labels."""
    manifest = load(root)
    if manifest is None:
        return legacy
    from vvh_validate import Parser
    base = root / 'config/ftbquests/quests'
    result = dict(legacy)
    for path, content in legacy.items():
        if path.parent != base / 'chapters':
            continue
        chapter = Parser(content, str(path)).parse()
        chapter['group'] = ident('group:archive')
        chapter['title'] = 'Legacy · ' + chapter['title']
        chapter['order_index'] = 100 + chapter.get('order_index', 0)
        local_ids = {q['id'] for q in chapter['quests']}
        chapter['quest_links'] = [
            {'id': ident(f'archive-link:{chapter["filename"]}:{dep}'),
             'linked_quest': dep, 'x': float(q['x']), 'y': float(q['y']) - 4.0,
             'shape': 'diamond', 'size': 0.8}
            for q in chapter['quests'] for dep in q.get('dependencies', [])
            if dep not in local_ids]
        result[path] = serialize(chapter) + '\n'
    groups = [('play', 'Pick an Adventure'), ('make', 'Make Something Matter'),
              ('trade', 'Contracts and Supplies'), ('archive', 'Previous Questbook')]
    result[base / 'chapter_groups.snbt'] = serialize({'chapter_groups': [
        {'id': ident('group:' + key), 'title': title} for key, title in groups]}) + '\n'
    rendered = []
    for ci, chapter in enumerate(manifest['chapters']):
        ch = {'id': ident('chapter:' + chapter['key']), 'filename': 'frontier_' + chapter['key'],
              'title': chapter['title'], 'subtitle': chapter['subtitle'],
              'group': ident('group:' + chapter['group']), 'icon': {'id': chapter['icon']},
              'order_index': ci, 'default_hide_dependency_lines': False,
              'default_quest_shape': 'circle', 'quests': []}
        ch['quest_links'] = [
            {'id': ident(f'link:{chapter["key"]}:{link["quest"]}'),
             'linked_quest': ident('quest:' + link['quest']),
             'x': float(link['x']), 'y': float(link['y']),
             'shape': 'diamond', 'size': 0.8}
            for link in chapter.get('links', [])]
        background = chapter_image(root, chapter['key'])
        if background is not None:
            ch['images'] = [background]
        for source in (q for q in manifest['quests'] if q['chapter'] == chapter['key']):
            q = copy.deepcopy(source)
            tasks = []
            for ti, task in enumerate(q['tasks']):
                task['id'] = ident(f'task:{q["key"]}:{ti}')
                if '_title' in task:
                    task['title'] = task.pop('_title')
                tasks.append(task)
            rewards = []
            for ri, reward in enumerate(q['rewards']):
                reward['id'] = ident(f'reward:{q["key"]}:{ri}')
                rewards.append(reward)
            out = {'id': ident('quest:' + q['key']), 'title': q['title'],
                   'description': q['description'], 'icon': {'id': q['icon']},
                   'x': float(q['x']), 'y': float(q['y']), 'size': q['size'],
                   'shape': q['shape'],
                   'optional': True, 'tasks': tasks, 'rewards': rewards,
                   'progression_mode': 'linear' if q['kind'] in ['shop', 'contract', 'crew_confirmed'] else 'flexible'}
            if q['deps']:
                out['dependencies'] = [ident('quest:' + key) for key in q['deps']]
            if q['repeat']:
                out.update(can_repeat=True, repeat_cooldown=q['repeat'])
            ch['quests'].append(out)
        result[base / 'chapters' / (ch['filename'] + '.snbt')] = serialize(ch) + '\n'
        rendered.append(ch)
    result[root / 'docs/frontier/render-manifest.json'] = json.dumps({'chapters': rendered}, indent=2, ensure_ascii=False) + '\n'
    return result
