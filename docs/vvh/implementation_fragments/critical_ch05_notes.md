# Critical Chapter 5 implementation notes

## Graph and choice policy

- `7A11C0DE15000001` remains gated by any one of the three faction charters (`min_required_dependencies: 1`).
- `7A11C0DE15000002` through `7A11C0DE15000009` are all `optional: true` alternatives. They are arranged as a symmetric four-left/four-right fan at `y: 0`; opener and capstone remain centered.
- `7A11C0DE1500000A` remains the capstone with all eight specialty dependencies and `min_required_dependencies: 3`.
- `7A11C0DE15000101` is the single post-capstone handoff. The former `15000102` node was removed because it duplicated the specialty review standard.
- Chapter art uses four existing verified item textures as sparse corner accents at unique positions/orders (`(-11,-3)`, `(11,-3)`, `(-11,5)`, `(11,5)`), leaving the centered four-left/four-right specialty fan clear for orientation.

## Contact points

Each specialty keeps one observable item contact plus one human-review checkmark:

| Quest | Contact item | Review action |
|---|---|---|
| Engineer | 4 `create:andesite_alloy` | repeatable machine service |
| Arcanist | 4 `irons_spellbooks:arcane_essence` | repeatable spell-preparation step |
| Night Specialist | 1 `vampirism:vampire_fang` | faction-facing procedure |
| Aeronaut | 16 `minecraft:scaffolding` | safe vehicle-site procedure |
| Diplomat | 1 `minecraft:bell` | public signal/mediation procedure |
| Quartermaster | 2 `minecraft:barrel` | labelled field kit |
| Pathfinder | 1 `minecraft:filled_map` | survivable route record |
| Archivist | 1 `minecraft:writable_book` | archive procedure |

The chapter's item tasks have no `consume` or `consume_items` field, so they are non-consuming inventory proofs. Player-facing copy deliberately says “Present,” not “Submit.” The `PASS THE KEY` writable-book proof is also non-consuming; it verifies possession while the review checkmark covers the recorded handoff.

The Aeronaut contact was lowered from `createpropulsion:wing` to 16 `minecraft:scaffolding`: the server is currently early Create, and scaffolding is already used by live Chapters 0, 1, 3, 4, and 9. This keeps the specialty accessible without guessing a new ID; the later Wing project remains optional world progression elsewhere.

## Reward and economy

- Specialty reward choices now reference reserved table `7A11C0DEF0000008` (decimal `8796023610973093896`).
- Each substantive specialty retains its existing 2 personal Bevel reward.
- The existing capstone retains 2 team Bevels.
- The handoff is team utility-only and introduces no Bevel.

## Deleted IDs

- Deleted quest ID: `7A11C0DE15000102` (`LEAVE THE METHOD READY`), merged into the single `15000101` handoff.
- Deleted task ID: `7A11C0DE15100102` from the former two-node handoff was reused for the writable-book contact task on `15000101`; it is not duplicated.
- Deleted task ID: `7A11C0DE1510AA01`, the duplicate Archivist writable-book task.
- Deleted Quartermaster item task IDs `7A11C0DE15100049` and `7A11C0DE1510004A`; the specialty now has one concrete barrel contact instead of a redundant supply bundle.

No other chapters, tables, manifests, scripts, or KubeJS were edited in this pass.
