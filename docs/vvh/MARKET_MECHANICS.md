# Chapter 5 · Market Mechanics

Chapter 5 is a 19-node catalogue. The left department contains ten building
palettes; the right department contains five progression or utility purchases;
the centre contains `Read the Board`, `Concord Bond`, `Rumour Ledger`, and
`Know the Coins`. Every node depends on the board opener so the existing unlock
dependency remains true, while `default_hide_dependency_lines: true` makes the
chapter read as a catalogue. Other chapters keep their visible dependency
lines.

## Payment and claims

Each purchase has one consumed item task showing its exact price. A successful
payment creates one shared reward entitlement per reward entry for the FTB
Team (`team_reward: true`). It does not create one complete kit per teammate,
and it never returns the submitted currency. Each reward entry carries
`exclude_from_claim_all: true`, so a buyer or teammate must claim the stock
manually in manageable portions. The full inventory and two-account delivery
checks remain a client/server acceptance gate.

The installed FTB Quests 2101.1.33 source measures `repeat_cooldown` in
seconds. Building palettes use 180 seconds; progression, utility, and Concord
Bond use 300 seconds. Rumour Ledger alone repeats every 604800 seconds (seven
days) and pays one shared team Bevel after consuming one written book and
receiving its review checkmark. Purchase tasks do not use `task_screen_only`.

## Catalogue

Building palettes start at one Sprocket for the inexpensive Works and Village
options. Specialist palettes cost two Sprockets. The four preserved crates keep
their live quest IDs and task IDs:

| Palette | Quest ID | Task ID | Price | Broad stock |
| --- | --- | --- | --- | --- |
| Celestial Spire Crate | `7A11C0DF00500011` | `7A11C1DF00500021` | 2 Sprockets | Deepslate Tiles, Dark Oak, Tinted Glass, Iron's Spells Nether Brick Pillars and Wisewood Shelving, Amethyst, Bookshelves, Sea Lanterns |
| Sanctified Brewery Crate | `7A11C0DF00500012` | `7A11C1DF00500022` | 2 Sprockets | Polished Tuff, Whitewood, Frosted Glass, Jars, Faucets, Lanterns |
| Frontier Watch Crate | `7A11C0DF00500013` | `7A11C1DF00500023` | 2 Sprockets | 3 Stone stacks, Spruce, Scaffolding, Timber Frames, Rope, Way Signs, Torches, Spyglasses |
| Heavy Bastion Crate | `7A11C0DF00500014` | `7A11C1DF00500024` | 2 Sprockets | Create Deco Catwalks, Sheet Metal, Supports, Mesh Fences, Chains, Iron Bars |

The remaining building palettes are Works Kit (8 Stone stacks, 4 Oak Log
stacks, 2 Sand stacks, Glass, Lanterns), Village Timber Kit (4 raw Stone
stacks, 4 Spruce Log stacks, 2 Terracotta stacks, 2 Sand stacks, Glass,
Lanterns, and 2 Campfires), Fortress Kit (Stone, Deepslate, Dark Oak, Bars,
Chains, Lanterns), Create Builder's Palette (Stone, Casing, Glass,
Scaffolding), Create Deco Palette (one Pearl-family masonry set with windows
and bars), and Abyssal Deepworks Palette (Blackwood, Black Pearl, Deepbronze, Blaze
Glass, and Deepbronze Bars). Rare ingots, Precision Mechanisms, spell
workstations, armour, and weapons are excluded from building orders.

The five right-hand purchases are Field Kit (1 Bevel), Create Starter Kit (2
Sprockets), Iron's Spells Starter Kit (1 Sprocket), Recovery Crate (1
Sprocket), and Transit Crate (2 Sprockets). They provide modest food,
lighting, early Create parts, low-tier spell supplies, recovery consumables,
or ordinary transport. None grants permanent flight, advanced teleportation,
high-tier spell gear, or a functioning factory.

Concord Bond costs two Sprockets and supplies one larger civic roads-and-bridges
order: 8 stacks of raw Stone, 4 stacks of Stone Slabs, 2 stacks of Stone Brick
Slabs, 4 stacks of Oak Logs, 4 stacks of Scaffolding, 2 stacks of Oak Fences,
Chains, and Lanterns for one named public road, bridge, or shared-stock project.
It is priced as a scale purchase, not a Diamond exchange or a progression
shortcut.

## ID and shortcut guardrails

Existing reward IDs remain attached to unchanged item identities, including
the four crate reward families. For the Village redesign, the old Terracotta,
Glass, Lantern, and Campfire entries remain at `7A11C2DF00500060`–`64`; the
former Brick (`...0057`–`...005C`) and Oak (`...005D`–`...005F`) entries were
intentionally replaced with new Stone, Spruce, and Sand entries at
`7A11C2DF005050E0`–`E9` because their item identities changed. Concord keeps
the unchanged Stone IDs `...0010`, `...0011`, `...0012`, `...0069`, Oak IDs
`...0013`, `...001D`, Scaffolding IDs `...006A`, `...006B`, Chain `...006D`,
and Lantern `...006E`; its old Glass entry `...006C` was removed with the
redesign, while added civic stock uses `7A11C2DF005050F0`–`FF`. New Chapter 5
task locals are in `0x4000`–`0x4FFF`; new reward locals are in `0x5000`–
`0x5FFF`. Every item reward is split to its real maximum stack size, and
unstackable equipment such as saddles, boats, and Spyglasses is a separate
entry. The arcane starter contains only Arcane Essence, Blank Runes, Common
Ink, and Uncommon Ink; the Recovery Crate contains consumables rather than
beds or shields.

The paid stock intentionally helps later building or setup work but does not
provide a descendant milestone's decisive workstation, armour, spell tier,
Precision Mechanism, Elytra, or advanced transport. The weekly Ledger cannot
fund a complete purchase board by itself, and no purchase reward reproduces
its input. These are source-level economy guardrails; currency affordability,
claim cooldown persistence, inventory overflow, component decoding, and
two-account team delivery still require the actual client/server acceptance
test.
# Decorative metal recycling spot check

The final review inspected recipe JSON in the pinned Abyssal Decor 0.11.0,
Create Deco 2.1.3, and Create 6.0.10 archives. Abyssal's
`bronze_block_decraft.json` converts a Deepbronze Block into four ingots; that
block is deliberately absent from the palette. The supplied tiles are made
from Riveted Deepbronze (one yields two tiles), and six ingots make sixteen
bars. No reverse recipe from the supplied tiles or bars to ingots was found
in those archives. Bars can become other decorative grates.

Create Deco can unpack `create:industrial_iron_block` into nine industrial
iron ingots. Heavy Bastion instead supplies catwalks, sheet metal, supports,
and mesh fencing. The inspected recipes turn ingots or plates into those
pieces; no reverse ingot recipe was found for the supplied pieces. These
archive checks do not cover recipes registered dynamically or by another
mod; the loaded-server recycling check remains a release gate.
