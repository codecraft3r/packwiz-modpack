# Critical Economy Choice Tables

These six native tables are additive utility choices. They are intentionally
not wired into `en_us.snbt` by this fragment; the integration owner should merge
the titles into the active language source during the normal localization pass.

## Table contract

- IDs `7A11C0DEF0000005` through `7A11C0DEF000000A` are reserved and stable.
- Every table uses `loot_size: 1`: one claim selects one complete supply entry.
- No table contains Bevels, armor tiers, spellbooks, spells, upgrade orbs, boss
  gear, Vampirism/Hunter levels, or currency-generating inputs.
- Items are already present in the live campaign's resolved item set. The final
  JAR-index validator must still be run against the materialized pack.
- Tables are not substitutes for faction access or class identity. They provide
  modest supplies that save setup time for a particular kind of session.

## Distinct purposes

- Blood: bottles, fang, rune, vellum, and glass for controlled blood preparation.
- Holy: garlic, rune, shield, lanterns, and bread for wards, safety, and support.
- Neutral: map-making, correspondence, route finding, and safe courier work.
- Specialty: Create assembly, glue, press, arcane preparation, and scaffolding.
- Event: fireworks, bell, lighting, art, and a display stand for hosted events.
- Civic: stonework, scaffolding, lighting, storage, and a simple public doorway.

The existing table #1 now uses honest “starter supply kit” names. Its custom
names remain flavorful, but the item lore makes clear that the contents are
consumable supplies rather than durable class tokens or role unlocks.

## Economy review

The tables have no currency input/output and are choice rewards only. They save
time without changing vertical progression. The integrated economy has seven
paid civic requisitions at 1/2/1/1/1/2/2 Bevels (some nodes may appear beside
early campaign content), for a complete ten-Bevel weekly board. Keep those paid
sinks separate from these free thematic choices. The fallback remains the sole
repeatable Bevel issuer.

## Required checks

Parse all ten reward-table SNBT files, assert stable IDs and unique reward IDs,
check localization-fragment coverage, run `py_compile scripts/vvh_validate.py`,
then run the full validator only after chapter/manifest integration is complete.
No client or two-account playtest is implied by this document.
