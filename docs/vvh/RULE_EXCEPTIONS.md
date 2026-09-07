# VvH Recorded Exceptions and Clarifications

These entries describe deliberate current behaviour. They are part of the
review record and should be changed only with a corresponding source edit.

## F1 — Charter guest pass

`Sign the Charter` accepts any two of its three witnessed clauses. The third
promise can be backfilled after a guest joins. This is encoded as
`min_required_dependencies: 2` on the terminal quest.

## F2 — Neutral starter handout

`Choose Neutral` is a checkmark choice with no item prerequisite. It pays a
small personal kit: one Sprocket, 16 cooked beef, eight emeralds, 16 paper, a
spyglass, shield, and white bed. The old full-iron and eight-Bevel proposal is
superseded by the reviewed live edit.

## F3 — Explanatory Charter rewards

The Charter opener supplies a map and torches, and the terminal supplies bread.
These are finite explanatory rewards. The Charter does not issue currency.

## F4 — Faction branch asymmetry is visible

Chapter 3 retains its manually reduced rewards. Chapter 4 now rewards its
revised service objectives and pays each commission a one-time shared grant.
The factions do not have identical personal and team issuance. Use the
generated economy report for current values; do not restore older rewards
to manufacture numeric parity.

## F5 — Market transaction scope

One player submits the displayed price into shared FTB Team quest progress.
Each payment unlocks one shared set of reward entitlements and one shared
repeat cycle. Members coordinate manual collection; they do not each receive
a copy of the purchase. Bulk entries are excluded from claim-all. The exact
installed client still needs two-account, partial-claim, cooldown, and
full-inventory verification.

Changing an existing reward from personal to shared changes its claim key.
The offline save migration described in `SAVE_MIGRATION.md` is a release gate
for existing worlds, even when the reward ID itself is preserved.

## F6 — Purchased construction stock

The current request explicitly approves generous paid building palettes and
180-second purchase delays. This reverses the earlier small-kit and weekly
purchase guidance. It does not authorize large free faction block grants or
accelerated recurring currency issuance; Rumour Ledger remains weekly.

## F7 — Exact First Thirst preservation

The explicit instruction to leave First Thirst unchanged takes precedence over
the new stack-splitting convention. Its baseline reward
`7A11C2DF00400003` remains four Blood Bottles in one entry, although the pinned
item has a maximum stack size of one. The preservation test guards the whole
quest; this exception does not apply to new or redesigned rewards. Confirm
delivery of all four bottles during client testing before an existing-world
release.

## Superseded records

The former full-iron Neutral exception, checkmark currency payout, any-three-
of-eight faction gate, weekly purchase board, and team capstones are historical
records only. They remain searchable in Git history but are not current policy.
