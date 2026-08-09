# VvH Balance Audit — dev retune

## Design band

The campaign assumes an unknown live-world progression state and therefore avoids vertical rewards. Quests should fund movement, building, events, maintenance, and catch-up without replacing Vampirism progression, hunter technology, late Create/Aeronautics builds, boss drops, high-tier magic, or endgame equipment.

## Strongest direct grants

- Create Goggles: quality-of-life information, not a progression machine.
- Nature's Compass: navigation convenience, not rare loot.
- 12 Arcane Essence / 8 Andesite Alloy / 8 Super Glue / 32 Scaffolding: modest friction reducers.
- Public caches: scaffolding, lanterns, torches, rails, food, fireworks, glue.

No VvH quest grants Vampirism levels, Hunter levels, vampire blood progression, high-tier crossbows, boss weapons, finished vehicles, netherite/diamond equipment, or Bevel currency.

## Currency

VvH issues **0 Bevels**. Postgame exchanges consume a maximum of **6 Bevels per FTB progress container per full weekly board**:

- lighting: 1
- transit: 2
- festival: 1
- repair: 1
- hospitality: 1

Outputs cannot produce Bevels or cheaply reproduce their own price. This makes the board a sink, not a faucet or self-funding loop.

## Faction fairness

All three foundations grant exactly the same team utility cache. Faction-specific items are objectives the players obtain through normal play, not rewards that let one faction skip its own progression.

The House and Order each require five of seven works and one current-alignment confirmation. Free Companies also require five of seven works. Neutral players therefore do not pay an economic penalty for refusing supernatural alignment.

## Route-time estimates

These are design estimates, not measured live-play timings:

- Charter + invitation: 10–25 minutes, excluding the actual Vampirism faction-conversion process.
- One foundation: roughly 2–5 team-hours depending on world state and build ambition.
- Any 3/8 personal contributions: 2–4 hours, heavily overlapping ordinary play.
- Any 4/8 public works: 4–10 server-hours, often spread across several players/sessions.
- Rivalry night: 45–120 minutes, optional.
- Long Night Fair: 60–150 minutes plus whatever public works already exist.

## Reward inventory

| Chapter/Table | Quest/Entry | Reward | Scope |
|---|---|---|---|
| VvH 00 · The Island Charter | SIGN THE CHARTER | custom paper keepsake | personal |
| VvH 00 · The Island Charter | SIGN THE CHARTER | 1× `minecraft:compass` | personal |
| VvH 00 · The Island Charter | SIGN THE CHARTER | 8× `minecraft:torch` | personal |
| VvH 01 · Three Invitations | TAKE THE CRIMSON INVITATION | custom paper keepsake | personal |
| VvH 01 · Three Invitations | TAKE THE LANTERN OATH | custom paper keepsake | personal |
| VvH 01 · Three Invitations | SIGN THE FREE COMPANY REGISTER | custom paper keepsake | personal |
| VvH 01 · Three Invitations | CHOOSE YOUR PERSONAL TRADE LENS | choice table `7A11C0DEF0000001` | personal |
| VvH 02 · House of Night | CHARTER THE HOUSE OF NIGHT | custom paper keepsake | team |
| VvH 02 · House of Night | CHARTER THE HOUSE OF NIGHT | 32× `minecraft:scaffolding` | team |
| VvH 02 · House of Night | CHARTER THE HOUSE OF NIGHT | 4× `create:super_glue` | team |
| VvH 03 · Lantern Order | CHARTER THE LANTERN ORDER | custom paper keepsake | team |
| VvH 03 · Lantern Order | CHARTER THE LANTERN ORDER | 32× `minecraft:scaffolding` | team |
| VvH 03 · Lantern Order | CHARTER THE LANTERN ORDER | 4× `create:super_glue` | team |
| VvH 04 · Free Companies | CHARTER THE FREE COMPANY | custom paper keepsake | team |
| VvH 04 · Free Companies | CHARTER THE FREE COMPANY | 32× `minecraft:scaffolding` | team |
| VvH 04 · Free Companies | CHARTER THE FREE COMPANY | 4× `create:super_glue` | team |
| VvH 05 · The Work Each Hand Knows | THREE HANDS' WORTH | choice table `7A11C0DEF0000002` | personal |
| VvH 06 · The Island Remembers | FOUR THINGS THE ISLAND KEEPS | 16× `minecraft:lantern` | team |
| VvH 06 · The Island Remembers | FOUR THINGS THE ISLAND KEEPS | 32× `minecraft:scaffolding` | team |
| VvH 06 · The Island Remembers | FOUR THINGS THE ISLAND KEEPS | custom paper keepsake | team |
| VvH 07 · Rivalry Without Ruin | ARCHIVE A RIVALRY NIGHT | 16× `minecraft:firework_rocket` | team |
| VvH 07 · Rivalry Without Ruin | ARCHIVE A RIVALRY NIGHT | 2× `minecraft:cake` | team |
| VvH 07 · Rivalry Without Ruin | ARCHIVE A RIVALRY NIGHT | custom paper keepsake | team |
| VvH 08 · The Long Night Fair | SEAL SEASON ONE | custom paper keepsake | personal |
| VvH 08 · The Long Night Fair | SEAL SEASON ONE | choice table `7A11C0DEF0000003` | personal |
| VvH 09 · After the Bells | LIGHTING REQUISITION — 1 BEVEL | 16× `minecraft:lantern` | team |
| VvH 09 · After the Bells | LIGHTING REQUISITION — 1 BEVEL | 32× `minecraft:torch` | team |
| VvH 09 · After the Bells | TRANSIT REQUISITION — 2 BEVELS | 32× `minecraft:rail` | team |
| VvH 09 · After the Bells | TRANSIT REQUISITION — 2 BEVELS | 8× `minecraft:powered_rail` | team |
| VvH 09 · After the Bells | FESTIVAL REQUISITION — 1 BEVEL | 16× `minecraft:firework_rocket` | team |
| VvH 09 · After the Bells | FESTIVAL REQUISITION — 1 BEVEL | 2× `minecraft:cake` | team |
| VvH 09 · After the Bells | REPAIR REQUISITION — 1 BEVEL | 4× `create:super_glue` | team |
| VvH 09 · After the Bells | REPAIR REQUISITION — 1 BEVEL | 32× `minecraft:scaffolding` | team |
| VvH 09 · After the Bells | HOSPITALITY REQUISITION — 1 BEVEL | 16× `minecraft:bread` | team |
| VvH 09 · After the Bells | HOSPITALITY REQUISITION — 1 BEVEL | 8× `minecraft:cooked_beef` | team |
| VvH 09 · After the Bells | LEAVE A SEASON TWO PRESSURE | custom paper keepsake | team |
| Choice: Choose a Personal Trade Lens | Builder Lens | custom paper lens | claimant |
| Choice: Choose a Personal Trade Lens | Engineer Lens | custom paper lens | claimant |
| Choice: Choose a Personal Trade Lens | Pathfinder Lens | custom paper lens | claimant |
| Choice: Choose a Personal Trade Lens | Keeper Lens | custom paper lens | claimant |
| Choice: Choose a Personal Trade Lens | Arcanist Lens | custom paper lens | claimant |
| Choice: Choose a Personal Trade Lens | Archivist Lens | custom paper lens | claimant |
| Choice: Choose a Practical Contribution Favor | Eight Andesite Alloy | 8× `create:andesite_alloy` | claimant |
| Choice: Choose a Practical Contribution Favor | Twelve Arcane Essence | 12× `irons_spellbooks:arcane_essence` | claimant |
| Choice: Choose a Practical Contribution Favor | Thirty-Two Scaffolding | 32× `minecraft:scaffolding` | claimant |
| Choice: Choose a Practical Contribution Favor | Eight Super Glue | 8× `create:super_glue` | claimant |
| Choice: Choose a Long Night Fair Favor | Create Goggles | 1× `create:goggles` | claimant |
| Choice: Choose a Long Night Fair Favor | Nature's Compass | 1× `naturescompass:naturescompass` | claimant |
| Choice: Choose a Long Night Fair Favor | Sixteen Lanterns | 16× `minecraft:lantern` | claimant |
| Choice: Choose a Long Night Fair Favor | Thirty-Two Rails | 32× `minecraft:rail` | claimant |

## Hostile edge cases

- **Faction switch just before claim:** historical advancement is insufficient; shared foundation cache requires current-state peer/host confirmation.
- **Two accounts in one FTB party:** team caches use `team_reward: true`; personal keepsakes/favors use `team_reward: false`. Exact two-client claiming still requires runtime verification.
- **Neutral joins a faction after completing Free Company:** old neutral charter remains history; no automatic reset/refund.
- **Repeatable payer/claim split:** price is consumed from the completing team task and output is a team reward. Test once with two disposable accounts before live use.
- **Progress reset abuse:** admin runbook explicitly forbids resetting completed milestones merely to reissue supplies.
