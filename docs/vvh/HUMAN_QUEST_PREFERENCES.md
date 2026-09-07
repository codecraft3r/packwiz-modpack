# VvH Human Quest Preferences

Status: current. Maintained artifact: update when later human edits provide new evidence.

These preferences were mined from manual correction sequences on `dev`
(post-generation repair passes, palette iterations, ID/count fixes, and the
f3ecc4b Market-crate addition) plus the explicit Ch4/Ch5 review appendices
(2026-09). Newest deliberate human corrections outrank older generated
states; repeated corrections are requirements, one-offs are heuristics.

## Hard requirements (enforced by validators where marked [V])

- Authoritative source is `scripts/vvh_campaign_v3.py`; generated SNBT must
  never be hand-edited without porting the change into the generator. [V: drift check]
- Quest-ID stability beats generator prettiness: legacy IDs (e.g. Market
  crates 17-20 with task IDs 0x21-0x24 and reward IDs 0x31-0x48) are
  preserved across redesigns. [V: protected-crate check]
- Minimum semantic diff: a palette rebalance must not rewrite tuned rewards,
  titles, dependencies, or coordinates, and vice versa.
- Chapter 5 dependency lines are invisible (`default_hide_dependency_lines`
  on the Market chapter only). [V: chapter-default check + renderer]
- Market layout is two-wing: building palettes left, progression kits
  right, explanations center. [V: department report]
- Purchase cooldowns are short (building 180s, progression 300s); the
  Rumour Ledger faucet stays weekly and team-scoped. [V: cooldown checks]
- Purchases are personal-scope; bulk kits must not multiply per team
  member. Descriptions state scope, price, consumption, and cooldown. [V]
- No purchase rewards its own input currency; no easy diamond redemption;
  no Handcrafted-specific kit. [V: prohibited-premium + handcrafted checks]
- Building kits provide raw flexible stock (general masonry uses raw Stone,
  never Cobblestone-as-masonry), never premade structures, and one
  coherent log/masonry identity per palette. [V: masonry checks]
- Multi-stack rewards ship as multiple unique 64-count entries, never one
  giant count. [V: stack-safety check]
- Candidate modded material names must be verified from pinned JARs before
  use (Umbra palette and Abyssal alloy names were rejected unverified). [V:
  verified-ID sets]
- Faction/specialty branches never hard-gate shared server progression;
  Neutral opt-out stays viable. [V: neutral + reachability checks]
- Titles stay within four words; no unescaped ampersand-space. [V]
- Checkmark-only quests issue no currency (except the protected Neutral
  opt-out). [V]
- Chapter core spines keep currency parity across factions (Tier I-III
  currency [1, 2, 4] bevel-equivalent). [V: parity check]

## Soft heuristics (review, not enforced)

- Prefer centered vertical World-Building spines with obvious hubs; side
  clusters compact with negative space and short local dependencies.
- Prefer mechanically concrete quests (workstations, lanes, services) over
  generic collect-filler; use mod-specific stations over vanilla surrogates.
- Construction support should feel generous but never trivialize gathering:
  past construction rewards went massive quantities -> themed palettes ->
  structured stacks -> reductions -> streamlining. Preserve that lesson.
- Reward time-savers, cooperation, theme, and next-activity support; avoid
  diamonds, generic precious metals, armor tiers, boss gear, high-tier
  spells, and faction advancement as reflex rewards.
- Commission quests should establish functional identity (signals, rig,
  hearth, archive), not inspect material piles; commissions pay controlled
  currency sized for a matching Market kit without creating loops.
- Static renders are diagnostic only and must be labeled as such; real
  client acceptance is required for icons, tasks, codecs, cooldowns, team
  behavior, and overflow handling.

## Explicit reversals on record

- Diamonds removed from building bundles and Concord Bond.
- Generic iron/arrow/flint rewards replaced by mod-specific equivalents.
- Handcrafted-specific kit proposed, then explicitly rejected.
- Stack-of-Diamonds redemption considered, rejected without a written model.
- Weekly team-scoped Market model replaced by short-cooldown personal model.
- Cobblestone-as-masonry replaced by raw Stone in general kits.
- Unavailable Cobblemon content removed; unverified IDs are not guessed.

## Enforcement map

- `scripts/vvh_campaign_v3.py --check`: source/sink drift.
- `scripts/vvh_campaign_v3_validate.py`: all [V] rules above plus the
  machine-readable `market_report` (quest, department, price, cooldown,
  scope, slots, full-stack equivalents, namespaces).
- `scripts/vvh_render_layouts.py`: effective hidden-line rendering.
