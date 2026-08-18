# Critical Chapter 6 handoff — consequence and upgrade pass

Chapter 6 is now a compact civic consequence chapter, not a second tour of Chapters 2–5. Existing roads, markets, workshops, archives, shelters, and vehicle/event spaces count when players substantially upgrade, link, test, or maintain them; players are not asked to rebuild equivalent structures.

## Live graph

Six optional alternatives feed `7A11C0DE1600000B THREE THINGS THE ISLAND KEEPS`. The capstone depends on `16000002` through `16000007` and keeps `min_required_dependencies: 3`.

- `16000002` connected route / wayfinding spine
- `16000003` market and contract hall
- `16000004` shared workshop and depot
- `16000005` archive and memorial
- `16000006` threat refuge / readiness station
- `16000007` public venue plus vehicle/event infrastructure

Retired redundant alternatives: `16000008` Horde Refuge and `16000009` Meeting Hall / Public Stage. Their old choice reward IDs `16210006` and `16210007` are no longer referenced by Chapter 6. This is an intentional merge into `16000006` and `16000007`; do not delete IDs from historical manifests without an explicit migration decision.

## Proof model

Each alternative has one non-consuming representative item task using an item already used elsewhere in the campaign, plus its existing checkmark review. The item is a visible signal of the relevant upgrade, not a payment. The checkmark standard accepts a solo signed maintenance/test log, one corrected failure, NPC/MCA use, or self-audit; multiplayer review is preferred but never required.

New task IDs reserved and used: `16100101`–`16100106`. Future Chapter 6 maintenance/consequence content may use the reserved `16xx0101+` range only after recording it here.

## Canon spine

Greybridge failed because route ownership, refuge capacity, and contradictory records were never reconciled. Nessa Quill asks the team to link what already exists. Mirelle and Elias disagree about which upgrade matters: Mirelle trusts a route people can find under pressure; Elias trusts a record that survives its author. The player resolves the argument through a concrete upgrade and its first test.

## Validation target

Parse the chapter, prove exactly six alternatives, all six `optional: true`, capstone dependency count 6, minimum 3, zero dependency crossings/overlaps, and three unique background image tuples with the custom island image as the single large low-alpha accent.
