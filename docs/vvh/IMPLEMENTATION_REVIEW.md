# Campaign fixes — implementation review

Implementation for `dev`: five chapters, 59 quests, including the preserved
15-quest House of Night and the rebuilt 19-node Market. Client/server gameplay
and existing-world save migration remain separate acceptance gates.

## Changed behavior

- House of Night now teaches the verified altar, refuge/service charter,
  grinder, Sieve, broadcasting, daytime travel, reserve, and alchemy workflows.
  All Chapter 4 quest IDs, positions, parents, and optional flags are retained.
  First Thirst is unchanged from the actual live baseline.
- The Market has ten building palettes, five utility purchases, and four
  central information/civic nodes. Each payment creates one shared entitlement
  set. Purchases consume the stated currency, disable automatic/bulk claiming,
  and use 180/300-second cooldowns; the one-Bevel team faucet remains weekly.
- Chapters 1–3 retain their reviewed semantics except the requested ordinary
  Sprocket wording correction and the split of unstackable Rabbit Stew rewards.
- All five chapters now use one deliberately centered panorama at its native
  16:9 aspect ratio, spanning the chapter rather than scattered thumbnails.
  Artwork uses 41–59% opacity, and the renderer includes its complete bounds.
  Quest coordinates, dependencies, and First Thirst semantics are unchanged.
- Generation validates temporary output and refuses unexpected live edits.
  The hash ledger retains the immutable baseline receipt; the pre-generation
  semantic comparison is saved under `evidence/current/`.
- The offline save migration covers 80 personal-to-shared reward transitions
  and five split fanouts, including Broadcast's eight individual cassettes.
  New files include campaign-specific preferences, mechanics evidence,
  deterministic economy reporting, and source-faithful/orthogonal renders.

## Verification

- 35 campaign regression tests pass. The SNBT parser suite passes with one
  skipped test; all 12 current SNBT files pass grammar validation.
- The campaign audit passes with zero errors. Its five visible warnings cover
  exact First Thirst preservation, two Blood Bottle continuity overlaps, and
  the reviewed faction currency differences.
- Exact pinned artifact evidence covers all 13 used mod namespaces. The
  bytecode stack receipt covers 220 campaign items. This is source evidence,
  not a running-server registry dump.
- Generation is synchronized and repeatable; Packwiz list succeeds and its
  second refresh leaves index/pack hashes unchanged. Catalogue reproduction
  also succeeds without the ignored JAR cache.
- Final render metrics match the saved SNBT. Every chapter has zero node
  overlaps, visible edge crossings, and clipped review labels. Background art
  resolves; seven item icons have explicit labelled fallbacks. The natural
  above-node label estimates remain visible in metadata; collision-aware
  review placement is a separate presentation step.

Review `evidence/current/layouts/contact_sheet.png`, the Chapter 4/5 detail
boards, `evidence/current/campaign-validation.json`, and `SAVE_MIGRATION.md`.
The client/server acceptance and backup migration gates in `UNRESOLVED.md`
remain open. No source-level result is presented as gameplay proof.
