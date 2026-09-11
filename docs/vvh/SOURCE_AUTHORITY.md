# VvH Source Authority

Status: current for the archived VvH source.

## September 11 progression-aware rebuild

The explicit request to start the questbook afresh around balanced adventures, machines and shared projects, while recognizing existing progress, supersedes the five-chapter-only **live surface**. `docs/frontier/quest-source.json` now owns nine new chapters; `scripts/frontier_campaign.py` composes them with the unchanged VvH quest objects under Previous Questbook. The standard `vvh_campaign_v3.py` command and staged hash-ledger guard generate both sets. All old IDs remain stable.

The owner's subsequent correction requires connected, deliberately shaped quest maps. Frontier now uses explicit coordinates, meaningful suggested milestone routes and native cross-chapter Quest Links. Flexible milestones credit existing achievements even when earlier route nodes are incomplete; crew projects, contracts and paid orders use linear progression to enforce their prerequisites. These modes follow the pinned FTB Quests implementation, not assumptions about dependency lines. The archive retains its protected geometry and hidden Market lines.

The five-chapter source, catalog and economy checks below remain authoritative for **archived VvH content**. Frontier has its own integrated audit and exact-artifact evidence; see `docs/frontier/README.md`. No historical faction capstone or third-faction campaign has been restored.


The repository previously contained several incompatible campaign generations. This file makes ownership explicit so an old generator or handoff cannot silently restore retired architecture.

## Current authority order

When sources disagree, use this order:

1. The installed Packwiz index, current configs, datapacks, and installed-artifact evidence.
2. The current repository-scoped quest-authoring and SNBT-validation skills.
3. `docs/vvh/SERVER_RULES.md`.
4. `scripts/vvh_campaign_v3.py`, plus the reviewed stable-ID overlay in
   `scripts/vvh_campaign_overrides.py`, the deterministic authoring source for
   the five live chapter files and the reward table.
5. The generated live SNBT under `config/ftbquests/quests/`.
6. `docs/vvh/campaign_manifest.json` and current validation evidence under `docs/vvh/evidence/current/`.
7. `docs/vvh/HUMAN_QUEST_PREFERENCES.md` and its structured companion
   `docs/vvh/HUMAN_QUEST_PREFERENCES.json` for scoped human design rules.
8. Current design and balance documentation under `docs/vvh/`.

The installed pack wins over remembered IDs, display-name guesses, old prompts, old ZIPs, and historical prose.

## Generator ownership

`scripts/vvh_campaign_v3.py` is authoritative despite its historical filename. Its legacy layer generates the following files; the Frontier composition layer adds nine chapters and its render manifest, and archives the five chapter containers:

- `config/ftbquests/quests/chapter_groups.snbt`
- `config/ftbquests/quests/data.snbt`
- `config/ftbquests/quests/lang/en_us.snbt`
- the five live chapter SNBT files
- `config/ftbquests/quests/reward_tables/holy_focus_choice.snbt`
- `docs/vvh/campaign_manifest.json`

Normal generation preserves unknown chapter files. Named retired historical chapter files are removed only with the explicit `--prune-retired` flag. `--check` is read-only, compares SNBT/JSON by parsed value while preserving loader-visible numeric suffixes, and fails when generated output drifts.

The overlay records accepted live commits `92a9020`, `4ed3207`, and `777a1e0`
by stable quest ID. A generator run cannot silently erase those reviewed
changes, and the manifest records the same provenance list.

Derived catalogues, review renders, validation reports, Packwiz hashes, and runtime evidence remain owned by their dedicated tools. They are not silently overwritten by the campaign generator.

`scripts/vvh_economy_report.py` is a deterministic source-level audit. It
reports personal versus shared one-time currency, paid sinks, recurring
issuance, team fragmentation, and configured currency/recycling/NPC/
denomination references. Its configured-reference matches are leads for
inspection; they do not prove recipe, survival, registry, or runtime behavior.
The report also compares one fixed player population as one team versus
one-player teams; currency items remain transferable even when claim scope is
team-scoped. Its packaged archive review records the pinned Numismatics
digest, coin recipe/loot findings, and the explicit runtime gate for recycling
and registry behavior.
The current generated outputs are
`docs/vvh/evidence/current/economy-current.json` and
`docs/vvh/evidence/current/economy-current.md`; regenerate both from the same
source revision and external server root.

Paid Market purchases are a deliberate claim-scope exception to the ordinary
personal reward default: one explicit payment must produce one shared reward
entitlement set for the FTB Team. Confirm this against the installed FTB
Quests claim key and a two-account runtime test. The weekly Rumour Ledger is a
separate team-scoped faucet and remains on its seven-day cadence.

`scripts/vvh_campaign_validate.py` is retained only for historical six-chapter
checkouts and delegates to the current validator when pointed at this manifest.
The older `scripts/vvh_sync_manifest.py` likewise delegates read-only checks to
the v3 generator and refuses to rewrite a current manifest.
`scripts/vvh_package_dropin.py` packages the current five-chapter shape and does
not require the retired ten-chapter file names.

## Live architecture

The preserved VvH archive chapters are:

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
python scripts/test_vvh_campaign_source.py
packwiz refresh
packwiz list
packwiz refresh
```

The second `packwiz refresh` must be stable. Static parsing and source-level layout review are not runtime playtests.
