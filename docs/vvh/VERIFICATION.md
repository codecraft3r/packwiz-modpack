# VvH Verification Matrix

Status: current five-chapter campaign. The latest local static report is a
pass with 0 errors and 5 review warnings: the exact First Thirst stack
preservation exception, two Blood Bottle continuity overlaps, and the
intentional faction core/completionism currency differences. All 13 referenced
mod namespaces have exact pinned artifact evidence. Stack evidence covers 220
campaign items and is a bytecode receipt, not a running-server registry probe.

| Layer | Check | Status |
|---|---|---|
| Source ownership | `vvh_campaign_v3.py --check` | pass |
| Python syntax | `py_compile` for generator, overlay, validator, catalog | pass |
| SNBT grammar | 12 files; 34 parser tests | pass; one parser test skipped |
| Campaign regressions | 35 preservation, migration, catalogue, economy, rendering checks | pass |
| Source graph | roots, reachability, cycles, Charter closure | pass |
| Emitted graph | parsed chapters, dependency thresholds, entity IDs | pass |
| Reward tables | choice references, duplicate IDs, item counts, currency visibility | pass |
| Neutral opt-out | no item prerequisite, current starter kit, no faction branch | pass |
| Faction structure | core spine, four hubs, eight leaves per faction | pass |
| Market economy | 16 sinks, 53 Bevel-equivalent total, one weekly team Bevel | pass |
| Identifier provenance | indexed Packwiz metadata and hash-bound catalog | pass locally |
| Preview bundle | five chapters, 59 quests, 19-node Market | pass as source diagnostics |
| Preview parser | duplicate-key rejection and large integer preservation | pass |
| Packwiz idempotency | refresh, list, refresh | pass; index and pack hashes unchanged on second refresh |
| Existing-save migration | 80 personal-to-shared transitions; five split fanouts | fixture tests pass; apply only to backed-up offline saves |
| Client/resource pack | icons, chapter art, GUI scale, text wrapping | pending runtime |
| Team transaction behaviour | payer, teammate, partial claims, overflow | pending runtime |
| Advancement behaviour | already-earned and late-join states | pending runtime |

The canonical machine-readable result is written to the requested output path
by `scripts/vvh_campaign_v3_validate.py`. It records warnings as well as the
pass/fail status; a pass does not erase unresolved runtime layers.
