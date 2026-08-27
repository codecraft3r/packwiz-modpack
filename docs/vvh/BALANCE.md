# VvH Balance and Economy Ledger

Status: current five-chapter campaign.

## Currency basis

All comparisons use Bevel-equivalent value:

| Coin | Value |
|---|---:|
| Spur | 0.125 |
| Bevel | 1 |
| Sprocket | 2 |
| Cog | 8 |
| Crown | 64 |
| Sun | 512 |

## Route issuance

| Ledger | Bevel-equivalent |
|---|---:|
| Neutral one-time route | 2 personal |
| Minimum Hunter route through Tier IV | 15 personal + 8 team |
| Minimum Vampire route through Tier IV | 15 personal + 8 team |
| Hunter personal completionism | 31 |
| Vampire personal completionism | 31 |
| Whole campaign one-time personal completionism | 68 |
| Whole campaign one-time team completionism | 16 |

The minimum faction route is faction entry, Core I–III, any three counted specialties, breadth gate, and capstone. Chapter 01 contains no currency issuance.

## Stage scaling

| Stage | Normal currency pattern |
|---|---|
| Faction entry | 1 Sprocket |
| Core I | 1 Bevel |
| Core II | 1 Sprocket |
| Core III | 2 Sprockets |
| Normal specialty | 1 Sprocket |
| Advanced specialty | 1 Cog |
| Team capstone | 1 team Cog |

Currency normally arrives with an immediately useful thematic bundle. Quantities are sized to support a real craft, trip, workstation, or build rather than a token sample.

## Hunter / Vampire parity

| Dimension | Lantern Order | House of Night |
|---|---:|---:|
| Total quests | 15 | 15 |
| Core quests | 3 | 3 |
| Counted specialties | 8 | 8 |
| Deep optional branches | 2 | 2 |
| Breadth requirement | 3 of 8 | 3 of 8 |
| Core currency | 7 | 7 |
| Specialty currency | 22 | 22 |
| Personal completionism | 31 | 31 |
| Team capstone | 8 | 8 |
| Tier IV structure | team refuge | team refuge |

Parity is structural and economic, not cosmetic. Hunters receive holy support, field logistics, medicine, and defensive preparation. Vampires receive blood infrastructure, nocturnal logistics, ritual utility, hospitality, and extraction systems.

## Weekly service-board sinks

| Service | Price | Bevel-equivalent |
|---|---:|---:|
| Field Kit | 1 Bevel | 1 |
| Works Kit | 1 Sprocket | 2 |
| Arcane Kit | 1 Sprocket | 2 |
| Foundry Kit | 2 Sprockets | 4 |
| Recovery Crate | 1 Sprocket | 2 |
| Transit Crate | 2 Sprockets | 4 |
| Concord Bond | 1 Cog | 8 |
| **Complete weekly board** |  | **23** |

Every purchase consumes exactly the displayed coin input. Every service is team-scoped and has a seven-day cooldown.

## Repeatable issuance

`Rumour Ledger` consumes one written book and pays one team Bevel every seven days.

- Weekly faucet per FTB Team: **1 Bevel-equivalent**.
- Complete weekly board: **23 Bevel-equivalent**.
- A team relying only on fallback income needs 23 weekly windows to buy one complete board cycle.
- Fragmented-team worst case is `1 × number of separately maintained FTB Teams` per week. This is monitored socially and in future economy reviews.

The faucet does not reproduce its input, does not return currency used to buy itself, and cannot self-fund the board.

## Collision controls

The semantic validator rejects:

- duplicate quest, task, and reward IDs;
- missing or cyclic dependencies;
- reward items that satisfy descendant item tasks;
- repeatables that reproduce their own input;
- non-consumed displayed purchase prices;
- asymmetric faction ledgers;
- fallback issuance that reaches premium-service scale;
- hidden Core III bypasses at faction breadth gates.
