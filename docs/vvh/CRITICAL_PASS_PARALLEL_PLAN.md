# VvH Critical-Pass Parallel Implementation

This pass converts the player audit into eight coordinated changes without
allowing parallel authors to overwrite shared quest data.

## Authority and integration

- Live chapter SNBT and `en_us.snbt` are the authoring authority.
- Chapter workers own only their assigned chapter files and unique localization
  fragments under `docs/vvh/implementation_fragments/`.
- The economy worker alone owns reward tables, balance documentation, and the
  validator.
- The root integrator alone merges localization, synchronizes the campaign
  manifest, renders final layouts, refreshes Packwiz, stages, commits, and
  pushes.
- No worker may add KubeJS, guess registry IDs, commit, push, or regenerate
  shared derived files.

## Parallel ownership

| Workstream | Exclusive files | Required outcome |
| --- | --- | --- |
| Onboarding and sinks | Chapters 00, 01, 09 | One real onboarding root, invitations after the charter, three early paid Bevel sinks, truthful currency copy |
| House of Night | Chapter 02 | Crimson invitation dependency, true 5-of-8 foundation, central build lane, Blood side progression |
| Lantern Order | Chapter 03 | Lantern oath dependency, true 5-of-8 foundation, central build lane, Holy/hunter side progression |
| Free Companies | Chapter 04 | Register dependency, balanced 4+4 pool with a true 5-of-8 capstone, duplicate-task cleanup |
| Specialties | Chapter 05 | Eight explicitly optional specialties, true 3-of-8 capstone, concrete solo test alternatives |
| Island works | Chapter 06 | Six non-duplicative upgrades/consequences, true 3-of-6 capstone |
| Rivalry and finale | Chapters 07 and 08 | Playable one-session event formats, honest solo audits, true 3-of-6 finale, readable layouts |
| Economy and validation | Reward tables, validator, balance docs | Six themed utility tables, Bevel safeguards, graph-truth and copy assertions |

## Shared narrative canon

- **Nessa Quill** is a neutral courier and archivist. She carried both surviving
  accounts of the failed Greybridge truce and cannot prove which route record
  was altered.
- **Mirelle Voss** is the House steward. She failed to shelter people during
  Greybridge and now treats hospitality as an obligation rather than decor.
- **Warden Elias Rook** saved civilians at Greybridge but abandoned a vampire
  refuge. He calls it triage and is no longer certain.
- Greybridge is past history, not a required generated location in a player's
  world. Player-built locations remain locally named.
- Lore, objective, and review/build/event standard are separate. Copy must not
  explain balance policy, repeat the objective as lore, or attach a joke to
  every quest.

## Reserved choice tables

| Table | Hex ID | Decimal SNBT reference |
| --- | --- | ---: |
| Blood | `7A11C0DEF0000005` | `8796023610973093893` |
| Holy | `7A11C0DEF0000006` | `8796023610973093894` |
| Neutral | `7A11C0DEF0000007` | `8796023610973093895` |
| Specialty | `7A11C0DEF0000008` | `8796023610973093896` |
| Event | `7A11C0DEF0000009` | `8796023610973093897` |
| Civic | `7A11C0DEF000000A` | `8796023610973093898` |

No choice table may contain Bevels. Guaranteed Bevels remain direct rewards.

## Integration acceptance

1. Only `OPEN THE ISLAND CHARTER` is a campaign root.
2. House, Lantern, and Free Company foundations are exactly 5-of-8 and expose
   balanced progression/world-building choices.
3. Specialties are 3-of-8, Island Works are 3-of-6, and Fair contributions are
   3-of-6; every alternative uses explicit optional UI semantics.
4. Early paid requisitions are available after the invitation welcome point.
   The full weekly board costs ten Bevels; the only repeatable faucet remains
   one team Bevel per seven days after the season seal.
5. No quest contains duplicate same-item proof tasks, false currency copy, an
   objective that calls a required item optional, or an empty lane-label click.
6. Layout renders have no node overlap or proper dependency-line crossings;
   custom images do not share identical coordinates/order within a chapter.
7. SNBT, IDs, dependencies, translations, item/image paths, economy, manifest
   synchronization, Packwiz idempotency, and the no-new-KubeJS boundary pass.
8. Client rendering, real task completion, and personal/team claim behavior are
   reported separately and never inferred from static validation.
