# VvH Concord Validation Contract

## Static release gate

Run from the Packwiz repository root:

```powershell
python -m py_compile scripts/vvh_campaign_v3.py scripts/vvh_campaign_v3_validate.py scripts/vvh_sync_catalog.py
python -X utf8 scripts/vvh_campaign_v3.py --check
python -X utf8 scripts/vvh_sync_manifest.py . --check
python -X utf8 scripts/vvh_sync_catalog.py . --check
python -X utf8 scripts/vvh_campaign_v3_validate.py --output docs/vvh/evidence/campaign-v3-validation.json
```

The v3 validator proves:

- exactly eight expected chapter files parse as SNBT;
- all chapter, quest, task, and reward IDs are globally unique;
- dependencies resolve, are acyclic, and every quest is reachable from one root;
- quest titles contain no more than four words;
- checkmarks remain attached to orientation, social, spell-demonstration,
  public-usability, event, or report criteria;
- no unescaped ampersand-space or removed Cobblemon reference exists;
- Iron's Spells scroll components contain the full native codec shape;
- Bevel, Sprocket, and Cog values are accounted at 1/2/8 Bevel-equivalent;
- there is exactly one weekly team-Bevel faucet and five team-scoped sinks;
- no one-time descendant quest can be fully item-funded by ancestor rewards
  without an advancement or human attestation remaining.

## Pack and asset checks

```powershell
packwiz list
packwiz refresh
python -X utf8 scripts/vvh_render_layouts.py docs/vvh/campaign_manifest.json docs/vvh/evidence/layout-concord-v3 --resource-zip tmp/poiesis-living-atlas-art-v5.zip --metadata-out docs/vvh/evidence/layout-concord-v3/metadata.json
git diff --check
```

The layout renderer must report zero unresolved references. Run `packwiz
refresh` twice and confirm the second run is idempotent before release.

## Human smoke test still required

Static proof does not establish FTB Quests client rendering or runtime team
semantics. Before a production merge, a human should verify in the shipped
client:

1. one calling and its faction opener;
2. one Blood and one Holy spell demonstration;
3. one public-build attestation with solo and shared-team progress;
4. one personal Sprocket, one personal mastery Cog, and one team Cog claim;
5. all five weekly sinks and the weekly Rumour Ledger cooldown;
6. background/logo readability at normal UI scale.

No disposable server load is required for this iteration by user direction.
Do not describe source review boards as in-client screenshots.
