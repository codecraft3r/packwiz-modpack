# VvH Validation Report

Status: current source-level validation. Runtime client checks remain explicitly separate.

## Static campaign result

`docs/vvh/evidence/current/campaign-validation.json` reports:

- status: pass;
- 5 chapters;
- 52 quests;
- 52 reachable quests;
- zero cycles;
- zero duplicate IDs;
- zero missing dependencies;
- zero node overlaps;
- zero visible dependency crossings;
- zero reward-to-descendant-task collisions;
- exact non-vanilla item, icon, advancement, spell, component, and art-reference allowlists;
- explicit carry/submit semantics on every item task;
- true any-three-of-eight breadth gates after Core III for both factions;
- exact Hunter/Vampire economic parity;
- 23 Bevel-equivalent weekly service-board sink cost;
- 1 Bevel-equivalent weekly fallback faucet;
- generated Packwiz file hashes match `index.toml`;
- the `pack.toml` index digest matches the exact `index.toml` bytes;
- zero warnings and zero errors.

## Commands completed in the implementation workspace

```sh
python -m py_compile scripts/vvh_campaign_v3.py scripts/vvh_campaign_v3_validate.py
python -X utf8 scripts/vvh_campaign_v3.py --check --root .
python -X utf8 scripts/vvh_campaign_v3_validate.py \
  --output docs/vvh/evidence/current/campaign-validation.json
sha256sum index.toml pack.toml
```

The generator check is idempotent and the structured semantic report is deterministic. The validator also recomputes every generated Packwiz entry and the top-level index digest, so manual index refresh drift is caught before CI.

## Repository CI gauntlet

The validation workflow runs the repository's full parser and Packwiz checks in a networked GitHub runner:

```sh
python scripts/validate_snbt.py config/
python scripts/test_validate_snbt.py
python scripts/vvh_campaign_v3.py --check
python scripts/vvh_campaign_v3_validate.py --output /tmp/vvh-campaign-validation.json
packwiz refresh
packwiz list
packwiz refresh

git diff --exit-code
```

The second refresh must produce no diff.

## Runtime status

A disposable Minecraft client/server was not available in the authoring container. The following are therefore **pending human/client checks**, not silently claimed as passed:

- open every chapter at real GUI scale and inspect red `!` indicators;
- claim the opener and complete every task family used;
- test Vampire and Hunter advancement detection, including already-earned advancements;
- test late join, team change, faction switch, and Neutral paths;
- complete one minimum faction path and one optional branch;
- buy at least one market service as payer and teammate;
- verify Iron's Spells scroll component codecs at runtime;
- verify all `poiesis:` art in the required resource pack;
- inspect logs for missing IDs, parser errors, codec errors, reward errors, and missing assets.

Source-level layout boards, where generated, are geometry evidence only. They are not Minecraft screenshots or a runtime playtest.
