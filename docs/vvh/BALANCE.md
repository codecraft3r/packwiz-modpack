# VvH Concord Reward Economy

This document describes the live v3 denomination economy. Values are derived
from the exact pinned Create: Numismatics JAR, not from visual coin size.

| Coin | Base value | Bevel-equivalent | Campaign use |
|---|---:|---:|---|
| Spur | 1 | 0.125 | not issued by this campaign |
| Bevel | 8 | 1 | ordinary core work and weekly fallback |
| Sprocket | 16 | 2 | callings, specialties, and hosted events |
| Cog | 64 | 8 | optional mastery and team capstones |
| Crown | 512 | 64 | intentionally not issued |
| Sun | 4096 | 512 | intentionally not issued |

## One-time issuance

| Path | Personal | Team treasury |
|---|---:|---:|
| Normal intended route | 23–25 Bevel-equivalent | 24 Bevel-equivalent |
| Chosen-faction mastery and optional breadth | adds up to 8–12 | unchanged |
| Every one-time branch | 83 Bevel-equivalent | 40 Bevel-equivalent |

The normal personal route comprises one calling, three accessible faction core
steps, any two specialties, the Common Ground spine plus any two side
contributions, and any three events. The advanced mastery card is optional and
pays one personal Cog because its requirements are substantially later than the
server's current state.

The 83-point completionist ceiling is not reachable through passive repetition.
It requires completing all faction initiations, all core chains, every
specialty, all three advanced mastery cards, the full civic chapter, and all six
events. Cross-faction completion remains possible, but the first step of each
faction core depends on its corresponding calling rather than a generic gate.

## Reward hierarchy

- Ordinary core: one Bevel plus useful catch-up or workstation stock.
- Calling, specialty, or event: one Sprocket plus a thematic bundle.
- Especially large civic contribution: up to two Sprockets.
- Optional mastery: one personal Cog plus late-path utility.
- Team charter or shared capstone: one team Cog plus public project stock.
- No substantive quest pays paper as its primary reward.
- Spell rewards are verified, capped low-tier scrolls and materials rather than
  random high-tier drops.
- No reward directly generates a stronger currency or a self-funding loop.

## Weekly services

All repeatables are optional, team-scoped, and have a 604800-second cooldown.

| Service | Cost | Purpose |
|---|---:|---|
| Field Kit | 1 Bevel | food, light, and leads |
| Works Kit | 1 Sprocket | structural repair stock |
| Arcane Kit | 1 Sprocket | multi-school inscription stock |
| Foundry Kit | 2 Sprockets | substantial Create repair stock |
| Concord Bond | 1 Cog | a major common project bundle |

The full board costs 17 Bevel-equivalent per team per week. The sole repeatable
faucet is `Rumour Ledger`: one consumed written report plus a trust attestation
pays exactly one team Bevel per week. It cannot self-fund even the smallest
premium service, and fragmented teams gain no compounding conversion route.

## Risk boundaries

- Team recreation can still multiply native FTB Team cooldown containers; this
  cannot be server-capped without custom logic and must be a social rule.
- Foundry and Concord outputs are intentionally generous time-savers. Human
  playtesting should compare them with normal Create and diamond acquisition.
- Currency is a choice enabler, not direct combat power. The meaningful sinks
  are visible in Chapter 08 before players decide how much optional work to do.
