# VvH Human Quest Preferences

Status: current review baseline. The generator, reviewed override record, and
live Packwiz files are authoritative; this document records the preferences
the validator should preserve.

## September 11 scoped supersession

The owner explicitly requested a fresh, balanced adventure/machine/shared-project book that accounts for already-advanced players. The five-chapter architecture and its detailed layout/cooldown preferences now govern the **preserved archive**. The new nine-chapter Frontier surface is additive at the source level and becomes the primary player-facing book. Stable old quest IDs remain protected. See `docs/frontier/README.md`; the standard generator composes both layers.

## Enforced archive preferences

- Keep `scripts/vvh_campaign_v3.py` as the authoring source and port accepted
  live edits into its explicit `vvh_campaign_overrides.py` record.
- Preserve stable quest, task, reward, and table IDs when changing wording,
  rewards, or layout.
- Keep the five-chapter architecture: Charter, Callings, Lantern Order, House
  of Night, and Market Services.
- Keep Neutral a protected opt-out. It has one checkmark, no item prerequisite,
  no faction branch, and the current practical personal kit.
- Keep Chapter 05 dependency lines hidden at chapter level; all other chapters
  retain visible dependency lines unless a quest explicitly hides them.
- Keep Market purchases on the shared paid-entitlement path: one explicit
  payment and one shared reward entitlement set per FTB Team, with explicit
  consumed prices, 180-second building cooldowns, and 300-second
  progression/civic cooldowns. Keep Rumour Ledger team-scoped and weekly.
- Keep general masonry kits on raw Stone rather than Cobblestone, avoid premium
  currency loops, and keep each reward entry within one stack.
- Use native item and advancement tasks for mechanical progression. Use
  checkmarks for rules, choices, and human-reviewed social outcomes.
- Keep titles short, descriptions explicit about scope and price, and item tasks
  explicit about `consume_items` semantics.
- Verify new non-vanilla IDs against the indexed Packwiz artifact, not an
  unrelated downloaded JAR or display-name guess.

## Current structural baseline

Each faction has a three-quest required core, four optional building hubs, and
eight optional leaves. There is no any-three-of-eight breadth gate or team
capstone in the current files. The validator derives route and economy facts
from the emitted graph instead of carrying those historical assertions.

Hunter and Vampire share core payout values `[1, 2, 4]` Bevel-equivalent. Their
optional branch payouts currently total 47 and 41 personal Bevel-equivalents;
the validator reports that difference as a warning for review rather than
calling the ledgers equal.

## Review heuristics

Prefer centered vertical spines, compact side branches, concrete workstations,
useful time-savers, coherent material palettes, and restrained utility rewards.
Static renders are diagnostic only. Client captures are required for icons,
text wrapping, codecs, cooldowns, reward delivery, and team behaviour.

## Superseded decisions

The full-iron Neutral kit, 32-beef requirement, any-three-of-eight gate,
weekly purchase board, faction capstones, and exact economic parity belong to
older designs. They must not be reintroduced by a validator, preview, or
documentation update without a new reviewed source change.

## Corrected brief additions (2026-09-07)

The structured evidence ledger is
`docs/vvh/HUMAN_QUEST_PREFERENCES.json`. It records concrete before/after
changes, supporting commits or explicit instructions, confidence, scope, and
how each preference is enforced. Commit authorship and a commit subject are
provenance only; they are not evidence of a human preference by themselves.

The current brief approves generous common-material building palettes when
they are paid Market purchases. That approval is scoped to finite paid sinks;
it does not restore large free construction grants throughout the campaign.

Paid Market purchases have a shared-entitlement exception to the usual
personal-reward default: one explicit currency payment by an FTB Team buys
one shared set of reward entitlements. The installed FTB Quests claim key and
claim order must be verified in a two-account test. `team_reward: false` alone
does not make quest progression personal or prevent team multiplication. The
seven-day Rumour Ledger is a separate team-scoped recurring faucet; its slow
issuance is not changed by the 180-second building or 300-second progression
purchase delays.

The four preserved Market crate identities are `7A11C0DF00500011` through
`7A11C0DF00500014`, with the corresponding existing task IDs ending in
`00500021` through `00500024`. The `7A1105AA...` appendix IDs are rejected.
Existing reward IDs remain stable where reward identity remains unchanged.

Finite common-material help in a purchased palette is not automatically an
infinite exploit. Review it against price, cooldown, team claim scope,
recycling, NPC exchange, denomination conversion, and descendant milestone
shortcuts. A reward that merely helps a later task is a finite continuity
overlap; a repeatable reward that reproduces its input or defeats a decisive
workstation remains a release blocker.

The pinned Create Numismatics candidate artifact used for current registry
investigation is
`CreateNumismatics-1.0.20+neoforge-mc1.21.1.jar`, SHA-256
`1375BA1B50E53FD09435029B5B2D5B94779BA397CCA7E01180D07B0F624E5B9B`.
This is artifact evidence only; it does not prove that a live client loaded
the item registry or that an item is obtainable in survival.
