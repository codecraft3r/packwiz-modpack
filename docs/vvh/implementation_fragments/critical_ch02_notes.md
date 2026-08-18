# Critical Chapter 2 implementation notes

This pass keeps House of Night as an optional faction foundation after the Crimson Invitation. The founder is not reachable until `7A11C0DE11000002` is complete. The two empty lane-label nodes (`1200000C`, `1200000D`) are removed; each real foundation work now branches directly from the founder.

## Graph truth

```text
Crimson Invitation 11000002
          |
          v
House founder 12000001 (central)
      |         \
      |          \-- progression side lane, x = 5
      |              12000003 altar
      |              12000005 cauldron
      |              12000008 Create logistics
      |              12000009 Blood school
      |
      +-- world-building spine, x = 0
          12000002 coffin room
          12000004 blood pantry / hospitality stock
          12000006 night route
          12000007 refuge lanterns
          |
          v
      1200000A House charter (all 8 dependencies, min 5)
```

All eight alternatives are `optional: true`. The charter is still a meaningful any-five capstone: its dependency set contains all eight works and `min_required_dependencies: 5`, forcing at least one work from each lane only because there are four works in each lane. Post-charter consequence nodes `12010101`–`12010103` remain optional.

## Mechanical truth

- The four progression works are altar preparation, alchemical preparation, Create logistics, and Blood-school inscription.
- Their item proofs are non-consuming (`consume: false`) and remain paired with a checkmark only for the actual shared demo, storage standard, or teaching moment.
- `vampirism:alchemical_cauldron`, `vampirism:altar_inspiration`, `create:mechanical_press`, `irons_spellbooks:blood_rune`, and `irons_spellbooks:bloody_vellum` are already present in the current chapter/manifest content.
- The kitchen/blood-wine objective is reframed as alchemical preparation. The pantry remains the one optional hospitality-stock work; no new cooking lane is added.
- New optional House depth rewards use reserved table `7A11C0DEF0000005` (`8796023610973093893`), team-scoped, with no new currency issuance.

## Human canon and consequence

Mirelle Voss is the House steward who failed to shelter people during the Greybridge truce. Nessa Quill carried the surviving guest list. Mirelle does not know whether the failure came from cowardice, a false instruction, or a door she believed was already safe; she refuses to turn uncertainty into an excuse. The founder asks the team to decide whether the new refuge rule should prioritize anonymous shelter or a named guest ledger. The House Rule and Unclaimed Cup arcs make that decision visible: a guest can leave safely without owing allegiance, while Nessa's surviving list remains evidence rather than a complete history.

No new backdated founder, spell, statistic, or faction lock is introduced. Lore is separated from objective and build review in the localization fragment.

## Visual QA

The seven repeated 1.55-unit decorations were replaced with three custom accents: a low-alpha House panorama at `(-5, 5)`, a Blood panorama at `(10, 5)`, and a crest at `(10, 14)`. Their negative orders are `-40`, `-39`, and `-38`; each `(x, y, order)` tuple is unique. Their bounds sit outside the node columns (`x = 0` and `x = 5`), so they do not cover nodes in the source geometry. Render the chapter and confirm this against the image layer before release.

## Validation record

- Parsed with `scripts/vvh_validate.py` parser: 13 total quests after removing the two lane labels and adding the three optional consequence quests; IDs remain unique.
- Founder dependency resolves to `7A11C0DE11000002`.
- Charter resolves all eight work IDs and requires five.
- No `1200000C` or `1200000D` references remain in the chapter.
- All eight works are marked optional.
- New reserved IDs are `12010101`–`12010103`, tasks `12110101`–`12110105`, rewards `12210101`–`12210103`.
- `git diff --check` passes.
