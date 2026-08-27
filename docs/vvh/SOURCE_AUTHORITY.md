# VvH Source Authority

Status: current.

The repository previously contained several incompatible campaign generations. This file makes ownership explicit so an old generator or handoff cannot silently restore retired architecture.

## Current authority order

When sources disagree, use this order:

1. The installed Packwiz index, current configs, datapacks, and installed-artifact evidence.
2. The current repository-scoped quest-authoring and SNBT-validation skills.
3. `docs/vvh/SERVER_RULES.md`.
4. `scripts/vvh_campaign_v3.py`, the deterministic authoring source for the five live chapter files.
5. The generated live SNBT under `config/ftbquests/quests/`.
6. `docs/vvh/campaign_manifest.json` and current validation evidence under `docs/vvh/evidence/current/`.
7. Current design and balance documentation under `docs/vvh/`.

The installed pack wins over remembered IDs, display-name guesses, old prompts, old ZIPs, and historical prose.

## Generator ownership

`scripts/vvh_campaign_v3.py` is authoritative despite its historical filename. It generates exactly:

- `config/ftbquests/quests/chapter_groups.snbt`
- `config/ftbquests/quests/data.snbt`
- `config/ftbquests/quests/lang/en_us.snbt`
- the five live chapter SNBT files
- `docs/vvh/campaign_manifest.json`

Normal generation preserves unknown chapter files. Named retired historical chapter files are removed only with the explicit `--prune-retired` flag. `--check` is read-only and fails when generated output drifts.

Derived catalogues, review renders, validation reports, Packwiz hashes, and runtime evidence remain owned by their dedicated tools. They are not silently overwritten by the campaign generator.

## Live architecture

The only live top-level chapters are:

1. `01 · The Island Charter`
2. `02 · Choose a Calling`
3. `03 · Lantern Order`
4. `04 · House of Night`
5. `05 · Market Services`

Neutral is a protected opt-out in Chapter 02. It is not a third faction and has no progression chapter.

## Superseded material

The following may remain in Git history or the documentation tree as research history, but they are not implementation authority:

- any 8–10 chapter campaign plan;
- any dedicated Free Companies or Neutral progression tree;
- any historical 109-quest graph;
- forced Vampire/Hunter treaty progression;
- season/wipe assumptions;
- `scripts/vvh_build.py` as a live whole-campaign authoring source;
- `docs/vvh-implementation-plan.md`;
- `docs/vvh/QUESTLINE_EXPANSION_HANDOFF.md`;
- `docs/vvh/QUEST_EDIT_REQUESTS.md` where it describes retired architecture;
- historical layout and validation folders outside `docs/vvh/evidence/current/`.

Historical material may inform ideas only after the idea is re-verified against the current pack, current skills, server rules, and five-chapter architecture.

## Standard commands

```sh
python scripts/vvh_campaign_v3.py --check
python scripts/vvh_campaign_v3_validate.py --output docs/vvh/evidence/current/campaign-validation.json
python scripts/validate_snbt.py config/
python scripts/test_validate_snbt.py
packwiz refresh
packwiz list
packwiz refresh
```

The second `packwiz refresh` must be stable. Static parsing and source-level layout review are not runtime playtests.
