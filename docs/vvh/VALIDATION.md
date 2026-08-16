# VvH Validation Contract

The generated package includes `scripts/vvh_validate.py`,
`scripts/vvh_render_layouts.py`, `scripts/vvh_discover.py`, and
`scripts/vvh_server_smoke.sh`. Static checks are required before release; a
static pass is not a substitute for a disposable client/server smoke test.

## Static checks

Run the validator with the materialized development-pack JAR index and any
unpacked resource-pack roots. It must prove:

- every edited SNBT file parses;
- global FTB object IDs are unique;
- the VvH dependency graph is acyclic and reachable, with valid any-N-of-M
  minima;
- all localization keys resolve;
- item, icon, image, advancement, and namespace references resolve against the
  installed pack/JAR index;
- no new VvH KubeJS quest logic exists;
- every direct currency reward has deliberate personal/team scope;
- Blood, Holy, and neutral Iron's Spells references resolve;
- no primary paper-only reward remains on a substantive campaign objective;
- choice tables `7A11C0DEF0000002`, `7A11C0DEF0000003`, and
  `7A11C0DEF0000004` contain zero Bevel entries;
- `ARCHIVE A NEW RUMOUR` (`7A11C0DE19000007`) is the only repeatable Bevel
  issuer, is team-scoped, trust-checkmark based, and has a 604800-second
  cooldown;
- the full requisition board costs exactly ten Bevels per team per week and
  cannot be self-funded by the one-Bevel weekly fallback.

The `dev` branch is an all-visible review build. Every quest is drawn from the
start, but its native dependencies still gate completion and reward claims. Run
the validator with `--require-all-visible` before pushing `dev`; a hidden VvH
node is a validation failure. The in-game group title includes
`[DEV · ALL NODES VISIBLE]`, and locked nodes explain that dependencies still
need to be completed.

## Economy assertions

The validator is intentionally strict against the live economy contract:

| Metric | Required result |
|---|---:|
| Normal intended-route personal Bevels | 18–24 |
| One-time completionist personal Bevels | 45–50 |
| Normal selected-route team Bevels | exactly 6 |
| All-branches one-time team treasury | exactly 14 |
| Weekly fallback | exactly 1 team Bevel |
| Eight fragmented fallback teams | at most 8 Bevels/week |
| Full weekly requisition board | 10 Bevels/team |

The normal team value is intentionally distinct from the 14 all-branches
ceiling. The latter includes every faction/capstone branch, including the extra
Chapter 1 invitation capstone. The repeatable fallback is excluded from all
one-time totals.

Choice accounting must count one selected native table entry. Never multiply
currency exposure by `loot_size`.

## Runtime checks

The dedicated-server stage must materialize the exact Packwiz pack, launch the
target NeoForge version in a disposable world, wait for startup, execute an FTB
Quests reload, and fail on targeted quest/config/missing-ID errors. Smoke-test:

- one Blood objective;
- one Holy objective;
- one neutral objective;
- one world-building objective;
- one school-material choice cache;
- one personal Bevel claim;
- one shared team capstone claim;
- the season seal;
- the weekly fallback once as a solo/team claimant, then a second claim to
  confirm the cooldown prevents issuance;
- one paid requisition and the payer/team reward scope.

Client visual tests must inspect normal text wrapping, branch layout, image crop,
logo/background composition, and missing textures. Two-account tests must cover
personal versus team claims, FTB Teams join/leave/switch behavior, and progress
container resets. These checks must be reported as pending when resources or a
playable Prism instance are unavailable; static parsing alone is never called a
playtest.

## Evidence and environment failures

Record the exact command, exit code, report path, and relevant log excerpt in
`docs/vvh/evidence/`. Distinguish repository failures from environment limits:

- missing materialized JAR index is an environment limitation for namespace
  resolution, not evidence that the quest ID is invalid;
- unavailable Prism/client runtime leaves visual and claim checks pending;
- an SNBT parse, duplicate ID, graph, localization, economy, or KubeJS failure
  remains a release blocker.
