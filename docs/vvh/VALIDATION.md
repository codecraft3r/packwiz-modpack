# VvH Six-Chapter Validation Contract

This document is the release contract for the current Chapters 01–06 campaign. Static validation is required before release, but it is not a substitute for a disposable client/server playtest.

## Required static gate

Run the campaign validator from the pack root:

```powershell
python -B -X utf8 scripts/vvh_campaign_validate.py --output docs/vvh/evidence/campaign-v2-validation.json
```

The validator is read-only unless `--output` is supplied. It exits nonzero if a required check fails and writes a structured report containing per-check status, economy totals, SHA-256 source hashes, a UTC timestamp, limitations, and pending runtime tests.

The required gate covers:

- exactly the six expected chapter files and successful structural SNBT parsing;
- globally unique chapter, quest, task, and reward IDs;
- resolved, acyclic dependencies and reachability from the Chapter 01 terminal;
- the Chapter 01 closed rules loop and symmetric, open Chapter 02 faction branches;
- current chapter groups, data schema, and disabled testing unlock mode;
- player-copy, title-length, ampersand, and player-visible meta-label rules;
- observed task and reward types;
- current-Packwiz membership for every non-vanilla namespace, including indexed metadata, server availability, exact pinned JAR filename, and download hash;
- catalog-backed non-vanilla items, icons, advancements, images, spell IDs, and component codecs;
- substantive hard criteria, including the Chapter 04 Cultist armor set;
- Chapter 05 field-archive and shared-Create attestations;
- Chapter 06 weekly payment, cooldown, team-reward, and zero-faucet rules;
- reward-to-descendant-task collision protection;
- the exact economy ledgers below; and
- the boundary prohibiting campaign KubeJS changes.

## Localization

The current chapters use inline strings. Localization completeness therefore means **zero unresolved translation-key references**. An empty `config/ftbquests/quests/lang/en_us.snbt` is complete only while no player-facing field refers to a translation key. Any future key reference must be added to that file.

## Economy assertions

| Metric | Required result |
|---|---:|
| All-claimable one-time personal Bevels | 44 |
| Intended-completionist personal Bevels with one faction selection | 42 |
| One-time team Bevels | 6 |
| Minimum Hunter route | 12 personal + 2 team |
| Minimum Vampire route | 12 personal + 2 team |
| Repeatable Bevel faucet | 0 |
| Full weekly team sink board | 19 |

The five Chapter 06 sinks cost 4/4/3/3/5 Bevels. They consume currency, use a 604800-second cooldown, grant team-scoped crate outputs, and never issue Bevels.

## Catalog, manifest, and parser evidence

Synchronize the campaign-scoped ID catalog and prove it is bound to the live Packwiz index:

```powershell
python -B -X utf8 scripts/vvh_sync_catalog.py
python -B -X utf8 scripts/vvh_sync_catalog.py --check
```

The catalog contains only IDs used by the live campaign. A namespace fails validation when its `.pw.toml` is absent from `index.toml`, client-only, renamed, or pinned to a different JAR/hash. Unrelated downloaded JARs are never accepted as installation evidence.

Synchronize the campaign manifest and verify it is current:

```powershell
python -B -X utf8 scripts/vvh_sync_manifest.py
python -B -X utf8 scripts/vvh_sync_manifest.py --check
```

The synchronizer reads the live `ch*.snbt` files, preserves inline copy and nested item counts, records all three chapter groups, and includes only reward tables referenced by the live campaign.

The focused structural command covering `chapter_groups.snbt`, `data.snbt`, `lang/en_us.snbt`, and all six chapter files passes 9/9. The broader `scripts/test_validate_snbt.py` suite passes all 34 tests with one intentional skip. The campaign validator passes 28/28 required checks.

## Runtime boundary

Static success does not prove acceptance by the shipped FTB Quests loader, client rendering, native advancement behavior, item-component serialization, reward delivery, team scope, faction switching, or weekly cooldown enforcement. Those checks remain open in `docs/vvh/UNRESOLVED.md`.

Record runtime commands, exit codes, relevant logs, and client observations in `docs/vvh/evidence/`. A missing runtime or client environment is a pending evidence boundary; a live SNBT, graph, localization, economy, ID, or KubeJS failure remains a release blocker.
