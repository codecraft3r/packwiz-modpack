# VvH Campaign Design

Status: current five-chapter campaign. The generated source and live SNBT are
the authority; this document explains the player-facing shape without adding
mechanics that are not present in the files.

## Player loop

Players acknowledge the Island Charter, choose House, Neutral, or Order, then
follow the selected faction spine or leave faction progression as a protected
Neutral opt-out. Faction branches teach concrete pack mechanics and reward
useful equipment, workstations, records, routes, and services. Market Services
is available after any calling and remains usable after faction progress.

| Chapter | Quests | Function |
|---|---:|---|
| 01 · The Island Charter | 5 | Three witnessed rules plus a terminal acknowledgement |
| 02 · Choose a Calling | 5 | House, Neutral, Order, and a one-of-three continuation |
| 03 · Lantern Order | 15 | Three required core quests, four hubs, eight optional leaves |
| 04 · House of Night | 15 | Three required core quests, four hubs, eight optional leaves |
| 05 · Market Services | 19 target | Four information nodes, ten building palettes, five progression/utility purchases |

The generated campaign currently has **59 quests** after the 19-quest Market
rebuild. Chapter 05 is the only chapter with a chapter-level hidden
dependency-line default.

## Chapter 01 — The Island Charter

`Island Charter` opens three clauses: `Name Public Doors`, `Consent First`, and
`Leave Work Standing`. `Sign the Charter` requires any two of those three
dependencies (`min_required_dependencies: 2`) so a witnessed guest can join
after two promises while the third is backfilled. The file records the
exception explicitly; it is not a validator-only rule.

The Charter uses checkmark acknowledgements and practical map, torch, and bread
rewards. It issues no currency. Every later chapter descends from its terminal.

## Chapter 02 — Choose a Calling

The decision surface is:

`Join the House | Choose Neutral | Join the Order`

House and Order use native Vampirism item and advancement tasks. Neutral uses a
single explicit acknowledgement and supplies a small personal starter kit:
one Sprocket, 16 cooked beef, eight emeralds, 16 paper, a spyglass, shield,
and white bed. It has no item prerequisite and no faction progression branch.

`Keep Doors Open` depends on one of the three calling quests. It is a
continuation acknowledgement, not a hidden three-of-three gate, and it opens
the shared Market chapter.

## Chapters 03 and 04 — Faction campaigns

Each faction has a three-quest required core spine. Core III opens four optional
building hubs; each hub has two optional specialty leaves. There is no
any-three-of-eight threshold and no team capstone in the current files. The
branches remain optional and do not gate shared Market access.

Lantern Order hubs are `Arcane Spire`, `Apothecary Lab`, `Survey Outpost`, and
`Garrison Armory`. Their leaves cover holy support, defence, medicine, refuge,
records, transit, armament, and artillery.

House of Night hubs are `Dark Spire`, `Blood Foundry`, `Thrall Hall`, and
`Blood Vault`. Their leaves cover shrouds, omens, extraction, transit, tithe,
registry, reserve, and script.

The validator reports the minimum personal-currency route from the live graph
instead of assuming a historical breadth gate. Current lower bounds to Core
III are derived at validation time.

## Chapter 05 — Market Services

Market Services is a catalogue with four central information nodes, ten
building palettes on the left, and five progression or utility purchases on
the right. Purchases consume explicit Numismatics inputs and grant one shared
reward entitlement set per FTB Team payment. Building services use a
180-second cooldown; progression and utility services use 300 seconds.
`Rumour Ledger` is the only weekly faucet: it pays one team
Bevel-equivalent per 604800 seconds. The short purchase delays do not change
the weekly currency schedule.

The board cost is generated from the revised source and must be refreshed with
`scripts/vvh_economy_report.py` after Chapter 4 and Chapter 5 edits. The
faucet is intentionally too small to fund the board by itself. Finite common
materials in paid palettes are allowed after reviewing recycling, NPC
exchanges, denomination conversion, team fragmentation, and milestone
shortcuts; free bulk construction rewards remain separately bounded. The
current source contains no custom KubeJS state bridge or fabricated faction
lock.

## Verification boundary

Native item and advancement tasks prove the relevant inventory or advancement
state. Checkmarks record rules, choices, and human-reviewed social outcomes.
Static validation proves syntax, graph integrity, file provenance, and the
declared economy. It does not prove client rendering, already-earned
advancement synchronization, reward delivery between teammates, or resource
pack artwork; those remain runtime gates in `UNRESOLVED.md`.

The installed FTB Quests claim behavior requires a two-account acceptance test:
one payer submits the exact displayed price, the team receives one shared set
of entitlements, teammates can coordinate collection, and an occupied
inventory does not silently duplicate or destroy stock. Static `team_reward`
flags are evidence to inspect, not proof of this transaction.
