# VvH Validation Contract

Status: current source-level validation. Runtime and client evidence stay
separate from this report.

## Static gauntlet

Run from the Packwiz repository root with the bundled Python runtime when the
Windows `python` alias is unavailable:

```powershell
python scripts/validate_snbt.py config/
python scripts/test_validate_snbt.py
python -m unittest discover -s scripts -p 'test_vvh*.py'
python scripts/vvh_campaign_v3.py --check
python scripts/vvh_campaign_v3_validate.py --output "$env:TEMP\vvh-campaign-validation.json"
python scripts/vvh_economy_report.py --strict --format markdown --output "$env:TEMP\vvh-economy-report.md"
python scripts/vvh_sync_catalog.py --check .
packwiz refresh
packwiz list
packwiz refresh
```

The campaign validator has two passes. It checks the source model for design
rules, then parses the emitted chapters and reward tables as the FTB loader will
see them. The emitted pass rejects malformed IDs, duplicate entities, unknown
task or reward types, impossible `min_required_dependencies`, missing
advancement criteria, missing choice tables, and hidden currency in a choice
table. It also checks dependency references and repeatable cooldown shape.

The generator compares SNBT and JSON by parsed value, preserving loader-visible
numeric suffixes while ignoring compound-key order. Normal generation still
writes only files whose value has changed and preserves unknown chapter files
unless `--prune-retired` is explicitly requested.

## Current result shape

The generated source currently reports five chapters and a 19-quest Market
(59 quests total). Do not hard-code a warning total into a validator; the
current report retains findings and warnings instead of hiding them in the
pass status.

The economy report is deterministic for the same source and external-root
inputs; two consecutive JSON runs produced the same SHA-256. The economy
fixture `uv run python scripts/test_vvh_economy_report.py` covers the
fixed-population formula and currency/board accounting.

The regression suite checks preservation of Chapters 1–3 with narrowly named
wording/stack exceptions, all Chapter 4 structural identities and First Thirst,
hash-guard refusal and baseline bootstrap, migration claim fanouts, rendering,
and fixed-population economy arithmetic. Migration fixtures are checked into
the repository so these checks also run outside the author's machine.

`generated_output_hashes.json` retains the immutable pre-edit bootstrap
receipt. Generation refuses unrecognized live edits, validates staged output,
and checks the live hashes again before replacing files. `--check` prints
per-quest semantic differences without changing files. See `VERIFICATION.md`
and the machine-readable current report for final integration results.

The Packwiz catalog is campaign-scoped. Each referenced non-vanilla namespace
must resolve to indexed metadata; the catalog records metadata SHA-256 and the
declared download hash. When a local JAR is materialized, its bytes must match
that declared hash before it can provide item-entry evidence.

The economy report keeps one-time personal currency, one-time shared/team
currency, paid Market sinks, the weekly Rumour Ledger faucet, and configured
currency/recycling/NPC/denomination references in separate ledgers. It is a
deterministic source-level diagnostic, not a runtime transaction log.

For paid Market services, check one explicit payment -> one shared entitlement
set per FTB Team. `team_reward: false` is not sufficient evidence of personal
progression or anti-multiplication behavior. Static output cannot prove claim
scope, late joiners, split claims, full-inventory delivery, cooldown timing, or
component decoding.

## Evidence boundary

Static checks prove syntax, source/file agreement, graph integrity, identifier
provenance, and declared economy. They do not prove Minecraft client rendering,
advancement synchronization for an already-qualified player, FTB team claim
order, inventory overflow behaviour, cooldown timing in a live world, or
resource-pack artwork. Those remain explicit runtime gates in
`UNRESOLVED.md`.
