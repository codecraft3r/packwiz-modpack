# VvH Season One Balance Audit

## Authoritative economy model

This document describes the live chapter SNBT and native reward tables. It is
the economy reference for future quest authors; do not infer payouts from old
plans, screenshots, or generated prose. The current model is Bevel-first:
substantive progression pays guaranteed Bevels, while thematic materials and
construction supplies are additional utility.

| Measure | Live target | Meaning |
|---|---:|---|
| Normal selected route, personal | **18** Bevels | One intended route through the campaign; allowed band is 18–24. |
| One-time completionist, personal | **50** Bevels | All one-time personal branches; allowed band is 45–50. |
| Normal selected route, team treasury | **6** Bevels | The selected faction route plus its shared capstones. |
| All one-time branches, team treasury | **14** Bevels | Every available faction/capstone branch in one progress container. |
| Post-campaign fallback | **1/team/week** | `ARCHIVE A NEW RUMOUR`, trust checkmark, 604800-second cooldown. |
| Full paid requisition board | **10 Bevels/week** | Seven team-scoped sinks priced 1/2/1/1/1/2/2. |
| Bevels in choice tables #2–#4 | **0** | Currency is guaranteed directly, never a competing random choice. |

The 14-Bevel team figure is an all-branches treasury ceiling, not the normal
route payout. It includes the extra Chapter 1 invitation capstone in addition
to the three faction charters and Chapters 5–7 shared capstones. A normal team
should be planned around six team Bevels; do not accidentally remove or add the
extra two without an explicit economy review.

## Scope and reward rules

- Direct `numismatics:bevel` item rewards are the guaranteed currency source.
- Routine progression rewards use `team_reward: false`; shared charters,
  capstones, and the weekly fallback use `team_reward: true`.
- Chapter 5 specialties pay two personal Bevels because each represents a
  larger multi-part contribution.
- Shared capstones pay two team Bevels each.
- The season seal pays three personal Bevels plus its fair-themed utility.
- Introductory labels, low-effort checks, and lane explanations may remain
  utility-only, but substantive objectives must not be paper-only.
- Bevels are never granted as an entry in choice tables
  `7A11C0DEF0000002`, `7A11C0DEF0000003`, or `7A11C0DEF0000004`.
- Do not grant armor tiers, boss gear, Vampirism/Hunter levels, high-tier
  spell power, or finished vehicles as quest rewards.

Choice semantics are important: a native choice reward grants one selected
entry. `loot_size` is table metadata and must not be multiplied into Bevel
exposure. The utility tables may offer player choice among building, travel,
and spell-preparation supplies, but currency remains a separate guaranteed
reward on substantive quests.

## Route accounting

The following accounting uses direct item rewards only. Personal rewards are
counted once per claimant; `team_reward: true` rewards are counted once per FTB
team. The repeatable fallback is excluded from one-time totals.

### Normal route

A player follows one faction/progression route and the shared campaign spine.
The live intended-path calculation is:

- 18 personal Bevels.
- 6 team Bevels for the selected route and shared capstones.
- Additional thematic materials, construction supplies, and capped utility
  choices as listed in the live reward tables.

This is the expected route for a regular player. The validator accepts 18–24
personal Bevels so a small future route clarification does not invalidate the
release, but any increase must be reviewed against the 50-Bevel completionist
ceiling.

### Completionist route

Completing every one-time personal branch issues 50 personal Bevels. Completing
every team-scoped faction/capstone branch issues 14 team Bevels to that progress
container. These are finite issuance ceilings, not weekly income.

Because the personal ceiling is already at the top of the approved range, a
future personal Bevel must replace or remove an optional personal payout, or be
converted to a utility/team reward. New content should preferentially consume
Bevels through a visible shared sink rather than minting more currency.

## Repeatable income and sinks

`ARCHIVE A NEW RUMOUR` (`7A11C0DE19000007`) is the only repeatable Bevel issuer.
It is a trust-based checkmark, remains gated behind the season seal, pays exactly
one team-scoped Bevel, and has a seven-day cooldown. It does not consume Bevels.

The seven Chapter 9 requisitions are team-scoped, consume Bevels, and each has a
seven-day cooldown:

| Requisition | Price | Output purpose |
|---|---:|---|
| Lighting | 1 | Lanterns and torches for public routes. |
| Transit | 2 | Rails and powered rails. |
| Festival | 1 | Fireworks and lanterns for events. |
| Repair | 1 | Super Glue and scaffolding. |
| Hospitality | 1 | Books and lanterns for civic spaces. |
| Public works | 2 | Stone bricks, scaffolding, and Andesite Alloy for a shared build. |
| Neutral arcane research | 2 | Low-tier Arcane Essence, blank runes, and amethyst. |

The complete board costs ten Bevels per team per week and produces no Bevels,
so it cannot self-fund. One shared team can earn at most one fallback Bevel in a
week. Eight fragmented teams can earn at most eight server-wide, but each team
still needs ten to complete its own board; fragmentation is therefore an
administrative/inflation risk, not a positive conversion loop.

## Safety checks for future additions

Before adding a reward, recalculate the live SNBT and confirm:

1. Normal intended personal issuance remains 18–24.
2. One-time completionist personal issuance remains 45–50.
3. Normal selected-route team issuance remains six.
4. All-branches one-time team treasury remains 14 unless an explicit decision
   changes the policy.
5. The only repeatable Bevel issuer remains `19000007`, at one/team/week.
6. Choice tables #2–#4 contain zero Bevel entries.
7. The ten-Bevel weekly board cannot be funded by the one-Bevel fallback.
8. New rewards save time or enable shared play without creating a runaway lead.

The static validator records these values in the generated evidence report.
Runtime checks still need a disposable client/server claim test for personal,
team, fallback, and paid-board behavior.
