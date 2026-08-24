# VvH Current-Pack Mod Presence Audit

## Finding

The player report was correct. Commit `7500a28` shipped 18 live SNBT references to `cobblemon:*` or `cobblemonraiddens:*`, but the current `dev` Packwiz manifest contains zero Cobblemon or Raid Dens `.pw.toml` files and `packwiz list` reports neither mod.

Affected live nodes were Chapter 05 quests `7A11C0DE50000001`–`7A11C0DE50000004` and Chapter 06 quest `7A11C0DE60000004`.

## Root cause

The earlier ID catalog proved that those IDs existed inside downloaded JARs from unrelated “All the Mons” and “Living Atlas” inventories. It did not prove that those JARs were indexed by this pack. The validator therefore accepted valid IDs from absent mods.

## Campaign repair

| Existing ID | Current node | Current-pack mechanics |
| --- | --- | --- |
| `7A11C0DE50000001` | Surveyor's Kit | Craft and carry the indexed Explorer's Compass. |
| `7A11C0DE50000002` | First Exposure | Carry an Exposure camera and film, then trigger its native first-photo advancement. |
| `7A11C0DE50000003` | Moment in Time | Trigger Exposure's native printed-photograph advancement. |
| `7A11C0DE50000004` | Island Album | Carry a photo album and attest to four public field records. |
| `7A11C0DE60000004` | Archivist's Crate | Spend three Bevels for a team-sized film and display-frame restock. |

Quest IDs, graph positions, dependency structure, Bevel issuance, team scope, cooldowns, and the 19-Bevel sink-board total remain stable. The replacement lane uses current indexed mods and preserves the original exploration-to-public-infrastructure role without pretending removed content exists.

## New release gate

`scripts/vvh_sync_catalog.py` now derives the campaign-scoped catalog from live `ch*.snbt` references. Every non-vanilla namespace must map to a `.pw.toml` present in `index.toml`; the evidence JAR filename, side, download hash, and index hash must match the current metadata. The campaign validator independently repeats those checks.

The synchronized catalog now contains only six campaign-used mod namespaces: `create`, `explorerscompass`, `exposure`, `irons_spellbooks`, `numismatics`, and `vampirism`. Unrelated downloaded JAR inventories are excluded.

## Evidence boundary

Static Packwiz membership and exact JAR-entry checks prove that the referenced content belongs to the pack. They do not prove client rendering, already-earned advancement synchronization, reward delivery, or two-account team behavior; those checks remain listed in `UNRESOLVED.md`.
