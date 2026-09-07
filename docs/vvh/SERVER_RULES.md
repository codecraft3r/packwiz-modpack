# VvH Server Rules

Status: current and mandatory for every VvH quest edit.

This document records the persistent server contract that quest content must preserve. It is a design input, not player-facing copy.

## World model

- VvH runs as a persistent SMP. It is not a disposable season or wipe-world campaign.
- The regular population is a small trusted group with uneven attendance and occasional larger sessions.
- The slowest regular player is the pacing reference. The fastest grinder is an adversarial economy test, not the target audience.
- Places, routes, archives, workshops, refuges, markets, and public services should remain useful after their originating quest is complete.

## Progression identities

- The two progression factions are the **Lantern Order / Hunters** and the **House of Night / Vampires**.
- **Neutral / Civic / Commons / Free Companies is a protected opt-out**, not a third progression faction.
- Neutral players may trade, build infrastructure, mediate, host services, and use the market board.
- Neutral players receive no dedicated progression chapter and no faction-equivalent quest tree.
- Neutral players are outside faction rivalry unless they voluntarily join a clearly opt-in activity.
- Hunter and Vampire progression must have comparable effort, economic weight, branch depth, and capstone value without becoming item-for-item copies.

## Claims, consent, and rivalry

- Claims are inviolable.
- Theft, griefing, destructive sabotage, forced invasions, and irreversible interference are never quest objectives.
- PvP is opt-in. A request to stop ends the activity.
- Pranks, scouting, races, photography, propaganda, markets, build showcases, scavenger hunts, and challenges are allowed only when they are claim-safe, reversible, and do not target Neutral players.
- Combat may occur as an optional social activity. Faction-specific mod progression may still involve combat mechanics.
- Public projects must identify their public entrance or access boundary so a protected build does not become an accidental locked door.

## Progress ownership

- FTB Teams owns quest and team progress.
- Vampirism owns actual Hunter or Vampire state.
- Do not create custom synchronization code between FTB Teams and Vampirism.
- Do not force joint Vampire/Hunter progression.
- Do not fake faction locking with player-facing text.
- If reliable native live-state visibility cannot be proven, structure branches so impossible quests do not block unrelated players.
- Do not add custom KubeJS quest logic unless native FTB Quests support is genuinely insufficient and this rule is explicitly amended.

## Economy contract

- Personal rewards are the default. Team rewards are reserved for shared projects or an explicit paid shared-entitlement exception.
- Currency scales with quest depth and effort.
- Repeatables must have explicit inputs, explicit consumed prices, deliberate cooldowns, and declared reward scope.
- No repeatable may reproduce its own input, finance the full market board, or become the optimal route through the pack.
- A finite reward may help a later descendant task when it is an earned continuity aid. Review that overlap against the task's decisive workstation or milestone; reject repeatable self-funding, duplication, and tier-skipping shortcuts.
- Reward quantities must cross a useful gameplay threshold rather than arriving as decorative scraps.
- Market palettes are an explicit paid exception to the personal default: one submitted price by an FTB Team grants one shared reward entitlement set. The installed FTB Quests claim key and payer/teammate claim order require a two-account runtime check; `team_reward: false` alone is not a scope guarantee.
- Building purchases use a 180-second delay and progression/utility purchases use 300 seconds. The Rumour Ledger remains a separate seven-day team-scoped faucet; purchase delays do not accelerate recurring currency issuance.
- Common structural materials are allowed in finite paid palettes. Check price, cooldown, stock, recycling, NPC exchange, denomination conversion, fragmentation, inventory overflow, and descendant shortcuts before release.

The pinned Create Numismatics candidate artifact for current registry work is
`CreateNumismatics-1.0.20+neoforge-mc1.21.1.jar` with SHA-256
`1375BA1B50E53FD09435029B5B2D5B94779BA397CCA7E01180D07B0F624E5B9B`.
This verifies the inspected file bytes only; it does not establish live
registry loading or survival obtainability.

## Required authoring chain

Before changing VvH quests, read in order:

1. `skills/ftb-quest-authoring/SKILL.md`
2. `skills/ftb-quest-authoring/references/player-facing-campaign-design.md`
3. `skills/ftb-quest-authoring/references/ftb-quests-patterns.md`
4. `skills/snbt-validation/SKILL.md`
5. this file
6. `docs/vvh/SOURCE_AUTHORITY.md`
7. the current live campaign and validation evidence

Any proposal that conflicts with these rules requires an explicit documented decision before implementation.
