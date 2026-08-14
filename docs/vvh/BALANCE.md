# VvH Season One Balance Audit

## Design band

The campaign assumes an unknown live-world progression state and therefore avoids vertical rewards. Quests should fund movement, building, events, maintenance, and catch-up without replacing Vampirism progression, hunter technology, late Create/Aeronautics builds, boss drops, high-tier magic, or endgame equipment.

## Strongest direct grants

- Create Goggles: quality-of-life information, not a progression machine.
- Nature's Compass: navigation convenience, not rare loot.
- 12 Arcane Essence / 8 Andesite Alloy / 8 Super Glue / 32 Scaffolding: modest friction reducers.
- 2 Blood Runes or 2 Holy Runes per completed supernatural foundation; 8 Arcane Essence for the neutral mediator foundation.
- Public caches: scaffolding, lanterns, torches, rails, food, fireworks, glue.

No VvH quest grants Vampirism levels, Hunter levels, vampire blood progression, high-tier crossbows, boss weapons, finished vehicles, netherite/diamond equipment, or Bevel currency.

## Currency

Chapters 0–4 do not issue currency through direct item rewards, but the shared foundation choice table (`7A11C0DEF0000002`) includes **2 Bevels as one selectable entry**. Because a choice reward grants exactly one selected entry, three completed foundations can expose at most **6 Bevels per progress container**. This is a bounded grant, not a repeatable faucet. Postgame exchanges consume a maximum of **6 Bevels per FTB progress container per full weekly board**:

- lighting: 1
- transit: 2
- festival: 1
- repair: 1
- hospitality: 1

Outputs cannot produce Bevels or cheaply reproduce their own price. This makes the board a sink, not a faucet or self-funding loop.

## Quantified Chapters 0–4 audit

The following assumes one player completes every personal quest and one FTB team completes Chapters 0–4, including all three faction foundations. `team_reward: true` is counted once per team; `team_reward: false` is counted once per claimant. A `ChoiceReward` grants exactly one selected reward; reward-table `loot_size` does not increase that choice count. The per-claimant line is an upper bound: Vampirism’s live faction rules may make some invitation branches mutually exclusive for one player, in which case the actual personal total is lower.

| Scope | Maximum direct issuance across Chapters 0–4 | Risk finding |
|---|---|---|
| Per claimant | 2 compasses, 8 scaffolding, 8 fireworks, 4 torches, 10 blood bottles, 12 garlic, 10 arcane essence, 7 holy runes, 1 blood rune, 1 arcane rune, 4 emeralds, 4 iron ingots, and one personal lens choice | Convenience/catch-up only; no armor, levels, boss gear, or tier skip. |
| One shared team | 128 scaffolding after the Free Company refund fix, 64 lanterns, 8 glass bottles, 12 hardtack, 4 andesite alloy, 6 super glue, 2 blood runes, 2 holy runes, 8 arcane essence, 2 emeralds, 2 writable books, 2 leads, and 8 bread | Construction and spell-prep supplies are useful but finite; no currency or self-replenishing input. |
| Foundation choice-table ceiling | Up to 3 selected entries across three foundations: at most 18 andesite alloy, 24 arcane essence, 72 scaffolding, 18 super glue, 9 blood runes, 9 holy runes, 72 lanterns, or 6 Bevels if the same entry is selected each time | Bevel is the dominant economic option, but capped to three one-time team claims. |
| 3–4 regular players, one team | Personal line scales to 3–4 claimants; team line remains one payout per foundation | Team reward avoids multiplying shared infrastructure by attendance. |
| 8-player peak, one team | Personal line scales to 8 claimants; team line remains one payout per foundation | No peak-population runaway unless players split into multiple FTB teams. |
| Worst team fragmentation | Team line multiplies by the number of teams that independently complete a foundation; eight solo teams could each claim the one-time team cache | Administrative multiplication risk, not an item-conversion loop; keep foundation progress team-scoped. |

### Conversion and refund checks

- Chapters 0–4 contain no repeatable reward task, no Bevel-generating exchange, and no reward that creates its own price input.
- The Free Company capstone consumes 32 scaffolding and 16 lanterns. Its scaffolding payout is now 16, so it reimburses half the scaffolding cost rather than returning the exact input. The lantern input remains a real net cost.
- The practical choice table contains no armor, equipment tier, Vampirism level, boss loot, or currency-positive conversion. The only currency entry is the bounded 2-Bevel option per foundation claim.
- Faction-specific rune grants are small and parallel: Blood and Holy foundations each grant 2 team runes, while Free Companies grant 8 Arcane Essence; none grants a spellbook, spell power, or progression level.

## Faction fairness

All three foundations grant exactly the same team utility cache. Faction-specific items are objectives the players obtain through normal play, not rewards that let one faction skip its own progression.

The House, Order, and Free Companies each require five of eight works plus a lane-aware review. School materials are modest objectives/rewards, not faction levels or high-tier spell grants. Neutral players can document limited Blood/Holy utility without becoming a substitute Vampire or Hunter progression route.

## Route-time estimates

These are design estimates, not measured live-play timings:

- Charter + invitation: 10–25 minutes, excluding the actual Vampirism faction-conversion process.
- One foundation: roughly 2–5 team-hours depending on world state and build ambition.
- Any 3/8 personal contributions: 2–4 hours, heavily overlapping ordinary play.
- Any 3/8 public works: 3–8 server-hours, often spread across several players/sessions.
- Rivalry night: 45–120 minutes, optional.
- Long Night Fair: 60–150 minutes plus whatever public works already exist.

## Reward inventory

| Chapter/Table | Quest/Entry | Reward | Scope |
|---|---|---|---|
| VvH 00 · The Island Charter | SIGN THE CHARTER | 1× `minecraft:compass` | personal |
| VvH 00 · The Island Charter | SIGN THE CHARTER | 8× `minecraft:torch` | personal |
| VvH 00 · The Island Charter | SIGN THE CHARTER | 2× `irons_spellbooks:arcane_essence` | personal |
| VvH 01 · Three Invitations | TAKE THE CRIMSON INVITATION | 2× `vampirism:blood_bottle` | personal |
| VvH 01 · Three Invitations | TAKE THE CRIMSON INVITATION | 1× `irons_spellbooks:blood_rune` | personal |
| VvH 01 · Three Invitations | TAKE THE LANTERN OATH | 4× `vampirism:garlic` | personal |
| VvH 01 · Three Invitations | TAKE THE LANTERN OATH | 1× `irons_spellbooks:holy_rune` | personal |
| VvH 01 · Three Invitations | SIGN THE FREE COMPANY REGISTER | 4× `minecraft:emerald` | personal |
| VvH 01 · Three Invitations | SIGN THE FREE COMPANY REGISTER | 1× `irons_spellbooks:arcane_rune` | personal |
| VvH 01 · Three Invitations | CHOOSE YOUR PERSONAL TRADE LENS | choice table `7A11C0DEF0000001` | personal |
| VvH 02 · House of Night | CHARTER THE HOUSE OF NIGHT | 32× `minecraft:scaffolding` | team |
| VvH 02 · House of Night | CHARTER THE HOUSE OF NIGHT | 4× `create:super_glue` | team |
| VvH 02 · House of Night | CHARTER THE HOUSE OF NIGHT | 2× `irons_spellbooks:blood_rune` | team |
| VvH 02 · House of Night | CHARTER THE HOUSE OF NIGHT | choice table `7A11C0DEF0000002` | team |
| VvH 03 · Lantern Order | CHARTER THE LANTERN ORDER | 32× `minecraft:scaffolding` | team |
| VvH 03 · Lantern Order | CHARTER THE LANTERN ORDER | 4× `create:super_glue` | team |
| VvH 03 · Lantern Order | CHARTER THE LANTERN ORDER | 2× `irons_spellbooks:holy_rune` | team |
| VvH 03 · Lantern Order | CHARTER THE LANTERN ORDER | choice table `7A11C0DEF0000002` | team |
| VvH 04 · Free Companies | CHARTER THE FREE COMPANY | 16× `minecraft:scaffolding` | team |
| VvH 04 · Free Companies | CHARTER THE FREE COMPANY | 4× `create:super_glue` | team |
| VvH 04 · Free Companies | CHARTER THE FREE COMPANY | 8× `irons_spellbooks:arcane_essence` | team |
| VvH 04 · Free Companies | CHARTER THE FREE COMPANY | choice table `7A11C0DEF0000002` | team |
| VvH 05 · The Work Each Hand Knows | THREE HANDS' WORTH | choice table `7A11C0DEF0000002` | personal |
| VvH 06 · The Island Remembers | THREE THINGS THE ISLAND KEEPS | 16× `minecraft:lantern` | team |
| VvH 06 · The Island Remembers | THREE THINGS THE ISLAND KEEPS | 32× `minecraft:scaffolding` | team |
| VvH 06 · The Island Remembers | THREE THINGS THE ISLAND KEEPS | choice table `7A11C0DEF0000002` | team |
| VvH 07 · Rivalry Without Ruin | ARCHIVE A RIVALRY NIGHT | 16× `minecraft:firework_rocket` | team |
| VvH 07 · Rivalry Without Ruin | ARCHIVE A RIVALRY NIGHT | 8× `minecraft:lantern` | team |
| VvH 07 · Rivalry Without Ruin | ARCHIVE A RIVALRY NIGHT | choice table `7A11C0DEF0000002` | team |
| VvH 08 · The Long Night Fair | SEAL SEASON ONE | 16× `minecraft:lantern` | team |
| VvH 08 · The Long Night Fair | SEAL SEASON ONE | choice table `7A11C0DEF0000003` | personal |
| VvH 09 · After the Bells | LIGHTING REQUISITION — 1 BEVEL | 16× `minecraft:lantern` | team |
| VvH 09 · After the Bells | LIGHTING REQUISITION — 1 BEVEL | 32× `minecraft:torch` | team |
| VvH 09 · After the Bells | TRANSIT REQUISITION — 2 BEVELS | 32× `minecraft:rail` | team |
| VvH 09 · After the Bells | TRANSIT REQUISITION — 2 BEVELS | 8× `minecraft:powered_rail` | team |
| VvH 09 · After the Bells | FESTIVAL REQUISITION — 1 BEVEL | 16× `minecraft:firework_rocket` | team |
| VvH 09 · After the Bells | FESTIVAL REQUISITION — 1 BEVEL | 8× `minecraft:lantern` | team |
| VvH 09 · After the Bells | REPAIR REQUISITION — 1 BEVEL | 4× `create:super_glue` | team |
| VvH 09 · After the Bells | REPAIR REQUISITION — 1 BEVEL | 32× `minecraft:scaffolding` | team |
| VvH 09 · After the Bells | HOSPITALITY REQUISITION — 1 BEVEL | 8× `minecraft:book` | team |
| VvH 09 · After the Bells | HOSPITALITY REQUISITION — 1 BEVEL | 8× `minecraft:lantern` | team |
| VvH 09 · After the Bells | LEAVE A SEASON TWO PRESSURE | choice table `7A11C0DEF0000002` | team |
| Choice: Choose a Personal Trade Lens | Builder Lens | named utility lens | claimant |
| Choice: Choose a Personal Trade Lens | Engineer Lens | named utility lens | claimant |
| Choice: Choose a Personal Trade Lens | Pathfinder Lens | named utility lens | claimant |
| Choice: Choose a Personal Trade Lens | Keeper Lens | named utility lens | claimant |
| Choice: Choose a Personal Trade Lens | Arcanist Lens | named utility lens | claimant |
| Choice: Choose a Personal Trade Lens | Archivist Lens | named utility lens | claimant |
| Choice: Choose a Practical Contribution Favor | Eight Andesite Alloy | 8× `create:andesite_alloy` | claimant |
| Choice: Choose a Practical Contribution Favor | Twelve Arcane Essence | 12× `irons_spellbooks:arcane_essence` | claimant |
| Choice: Choose a Practical Contribution Favor | Thirty-Two Scaffolding | 32× `minecraft:scaffolding` | claimant |
| Choice: Choose a Practical Contribution Favor | Eight Super Glue | 8× `create:super_glue` | claimant |
| Choice: Choose a Practical Contribution Favor | Two Blood Runes | 2× `irons_spellbooks:blood_rune` | claimant |
| Choice: Choose a Practical Contribution Favor | Two Holy Runes | 2× `irons_spellbooks:holy_rune` | claimant |
| Choice: Choose a Long Night Fair Favor | Create Goggles | 1× `create:goggles` | claimant |
| Choice: Choose a Long Night Fair Favor | Nature's Compass | 1× `naturescompass:naturescompass` | claimant |
| Choice: Choose a Long Night Fair Favor | Sixteen Lanterns | 16× `minecraft:lantern` | claimant |
| Choice: Choose a Long Night Fair Favor | Thirty-Two Rails | 32× `minecraft:rail` | claimant |
| Choice: Choose One Utility Favor | Alloy / Essence / Scaffolding / Glue / Blood Rune / Holy Rune / Lantern | one selected utility option; no currency entry | routine milestone claimant/team |

## Hostile edge cases

- **Faction switch just before claim:** historical advancement is insufficient; shared foundation cache requires current-state peer/host confirmation.
- **Two accounts in one FTB party:** team caches use `team_reward: true` once per team; personal keepsakes/favors use `team_reward: false` once per player.
- **Neutral joins a faction after completing Free Company:** old neutral charter remains history; no automatic reset/refund.
- **Repeatable payer/claim split:** price is consumed from the completing team task and output is a team reward. Test once with two disposable accounts before live use.
- **Progress reset abuse:** admin runbook explicitly forbids resetting completed milestones merely to reissue supplies.

## Quantified Chapters 5–9 economy review

This section audits the final combined Chapter 5–9 files using the verified FTB Quests source semantics: a `ChoiceReward` presents exactly one selected reward, and reward-table `loot_size` does not increase the number of choices. `team_reward: true` is tracked with the shared team identity and is claimable once per team; `team_reward: false` is once per player.

### One-time issuance

| Scope | Claims | Maximum selectable rewards before normal play limits | Bevel exposure |
|---|---:|---|---:|
| Ch. 5 personal lane, per player | 5 utility-only claims × 1 selection | up to 240 scaffolding, 60 alloy, 60 glue, 120 lanterns, or 15 of either rune | **0** |
| Ch. 5 capstone, per team | 1 practical-table claim × 1 selection | up to 48 scaffolding, 16 essence, 12 alloy/glue, or 3 of either rune | up to 2 per team |
| Ch. 6 public works, per team | 7 utility-only claims × 1 selection | up to 336 scaffolding, 84 glue, 112 essence, 21 blood/holy runes, or 168 lanterns | **0** |
| Ch. 7 rivalry events, per team | 7 utility-only claims × 1 selection | up to 336 scaffolding, 84 glue, 112 essence, 21 blood/holy runes, or 168 lanterns | **0** |
| Ch. 8 fair contributions, per team | 6 utility-only claims × 1 selection | up to 288 scaffolding, 72 alloy, 72 glue, 144 lanterns, or 18 of either rune | **0** |
| Ch. 8 season seal, per claimant | 1 fair-table claim × 1 selection | one fair-table choice; the quest's 16 lantern team grant remains separate | up to 3 per claimant |

Routine Chapter 5–8 milestones now issue **0 Bevels**. The remaining intentional seed-money sources in this scope are the three shared capstones using practical table #2 (2 Bevels each, 6 per team) and the existing personal Chapter 8 season seal (3 per claimant). With one four-player team, the maximum is **18 Bevels**—three full weekly boards. At eight peak players, the personal seal raises the ceiling to **30**; that is a finite peak-population exception, not a repeatable faucet. Team fragmentation remains the main multiplication risk for shared capstones.

The dominant choice is Bevel because it is the only selectable entry that can be converted into the Chapter 9 civic board. It is finite one-time issuance, not a self-replenishing loop; treat it as an intentional catch-up grant rather than an accidental currency reward.

### Weekly exchanges

Each Chapter 9 requisition has a seven-day cooldown and consumes Bevels. Completing the full board once per progress container costs **6 Bevels/week** and yields one team package of:

| Output | Weekly amount per team |
|---|---:|
| Lanterns | 32 |
| Torches | 32 |
| Rails | 32 |
| Powered rails | 8 |
| Firework rockets | 16 |
| Super Glue | 4 |
| Scaffolding | 32 |
| Books | 8 |

For one four-player team, the equivalent shared supply is 8 lanterns, 8 torches, 8 rails, 2 powered rails, 4 fireworks, 1 glue, 8 scaffolding, and 2 books per player per week. For one eight-player team, halve those per-player equivalents. With `T` independent FTB teams completing the board, server-wide issuance is exactly `T × 6` Bevels spent and `T` times the table above. There is no Bevel in any requisition output, so the board cannot fund its own input.

### Abuse and conversion checks

- The previously added reward on `7A11C0DE19000007` (“Archive a New Rumour”) was removed: it was a weekly, no-input checkmark and would have been a free personal choice-table faucet.
- Chapters 5–8 are one-time quests. Their Bevel selections can fund Chapter 9, but cannot be repeated by cooldown or by ordinary item conversion.
- Requisition outputs do not include Bevel, armor, Vampirism/Hunter levels, boss gear, or spell progression tiers. Goggles, compasses, rails, and supplies are convenience/civic utility rather than tier skips.
- `team_reward: true` is used on public works, rivalry, fair contributions, capstones, and all paid requisitions; Chapter 5 specialty payouts are personal. The verified once-per-team/once-per-player semantics are reflected in the ceilings above.
