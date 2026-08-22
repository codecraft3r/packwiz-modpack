# FTB Quests Patterns and Audit Notes

Use this file after reading the main skill. Treat every code block as a shape to adapt to the installed FTB Quests version; copy exact field spelling and list syntax from a working chapter in the target pack.

## Portable task shapes

~~~snbt
// Item task: verify the target pack's item/count nesting.
{
  id: "<unique-task-id>"
  type: "item"
  item: { id: "<namespace:item>" }
  count: 1
  consume_items: false
}
~~~

~~~snbt
// Advancement task: many current builds require criterion, with an empty
// value meaning the whole advancement. Confirm this in the shipped build.
{
  id: "<unique-task-id>"
  type: "advancement"
  advancement: "<namespace:path>"
  criterion: ""
}
~~~

~~~snbt
// Stat task: use a statistic that exists in the installed mod and describe
// its real trigger in the quest copy.
{
  id: "<unique-task-id>"
  type: "stat"
  stat: "<namespace:statistic>"
  value: 1
}
~~~

~~~snbt
// Human-reviewed social/build task.
{ id: "<unique-task-id>" type: "checkmark" }
~~~

## Palette quest pattern (building incentives)

FTB Quests cannot reliably verify complex placed multiblocks in-world. To incentivize building without requiring untrackable placement tasks, use the **Palette Quest pattern**: require gathering/crafting a curated, accessible starter palette of thematic blocks. When completed, award abundant matching blocks (2x-3x quantity plus tools like a stonecutter) and valuable crafting materials (diamonds, iron, obsidian). This establishes a clear visual theme and directly supplies the materials and incentives to build:

~~~snbt
{
  id: "<unique-quest-id>"
  title: "Outpost Construction"
  subtitle: "Gather a fortified stonework and timber palette"
  tasks: [
    {
      id: "<task-stone>"
      type: "item"
      item: { id: "minecraft:stone_bricks" }
      count: 64
      consume_items: false
    }
    {
      id: "<task-logs>"
      type: "item"
      item: { id: "minecraft:oak_logs" }
      count: 32
      consume_items: false
    }
    {
      id: "<task-bars>"
      type: "item"
      item: { id: "minecraft:iron_bars" }
      count: 16
      consume_items: false
    }
    {
      id: "<task-lanterns>"
      type: "item"
      item: { id: "minecraft:lantern" }
      count: 8
      consume_items: false
    }
  ]
  rewards: [
    // 2x-3x building supply multiplier + stonecutter
    {
      id: "<reward-stone-bricks>"
      type: "item"
      item: { id: "minecraft:stone_bricks" }
      count: 128
    }
    {
      id: "<reward-logs>"
      type: "item"
      item: { id: "minecraft:oak_logs" }
      count: 64
    }
    {
      id: "<reward-bars>"
      type: "item"
      item: { id: "minecraft:iron_bars" }
      count: 32
    }
    {
      id: "<reward-stonecutter>"
      type: "item"
      item: { id: "minecraft:stonecutter" }
      count: 1
    }
    // High-value crafting materials
    {
      id: "<reward-iron>"
      type: "item"
      item: { id: "minecraft:iron_ingot" }
      count: 64
    }
    {
      id: "<reward-diamonds>"
      type: "item"
      item: { id: "minecraft:diamond" }
      count: 16
    }
    {
      id: "<reward-currency>"
      type: "item"
      item: { id: "<namespace:currency>" }
      count: <scaled-amount>
    }
  ]
}
~~~

## Claim-safe reconnaissance and prank pattern

Never create quests requiring territory invasion, griefing, or untrackable sparring across claim boundaries. Use tangible, survival-friendly mechanics supported by installed mods (such as photography via Exposure camera and film, harmless throwable items, or non-destructive prank devices):

~~~snbt
{
  id: "<unique-quest-id>"
  title: "Shadow Reconnaissance"
  subtitle: "Capture photographic intel of rival movements"
  tasks: [
    {
      id: "<task-camera>"
      type: "item"
      item: { id: "exposure:camera" }
      consume_items: false
    }
    {
      id: "<task-film>"
      type: "item"
      item: { id: "exposure:black_and_white_film" }
      count: 1
      consume_items: false
    }
  ]
  rewards: [
    {
      id: "<reward-extra-film>"
      type: "item"
      item: { id: "exposure:black_and_white_film" }
      count: 2
    }
    {
      id: "<reward-currency>"
      type: "item"
      item: { id: "<namespace:currency>" }
      count: <scaled-amount>
    }
  ]
}
~~~

## Branch and exchange patterns

For an "any N of M" route, create M comparable quests, attach them directly to the same common opener, and make the capstone depend on all M with the target schema's minimum set to N. Compute a shortest path to the capstone. If every alternative depends on one of its siblings, the real requirement may be N+1 even though the capstone says N.

Use the installed schema's quest-level optional flag for side stories. Graph optionality and UI optionality are separate: a quest can gate nothing and still look mandatory to a player.

A repeatable exchange normally has this semantic shape:

~~~snbt
can_repeat: true
repeat_cooldown: <ticks>
task: {
  type: "item"
  consume_items: true
  item: { count: <price> id: "<namespace:currency>" }
}
rewards: [
  {
    type: "item"
    item: { count: <safe-count> id: "<namespace:utility-item>" }
    team_reward: true
  }
]
~~~

Do not copy the placeholder currency or reward IDs. Price in the pack's real denomination, state the price in the quest title/description, and choose team_reward per reward rather than inheriting an accidental default. If progress is team-scoped, test the exact behavior when one player pays and another claims.

For a reviewed building quest, prefer a checkmark plus concise build standard. If an item task merely previews expected materials, keep it non-consuming. Consume materials only for an explicit hand-in, donation, or stockpile; otherwise the player may pay once by placing the blocks and again when the quest removes a second bundle.

## Economy accounting matrix

Record these independently; do not collapse them into one “total rewards” number:

| Ledger | Question |
| --- | --- |
| Minimum personal | What does one player receive on the shortest intended route? |
| Completionist personal | What can one player claim from every one-time personal branch? |
| Normal team | What does one shared progress team receive on one intended route? |
| Completionist team | What can one progress container receive from every one-time team branch? |
| Repeatable | What can one team and the fragmented-team worst case mint per cooldown window? |
| Sink board | What does every repeatable purchase cost in one cooldown window? |

Verify choice-reward semantics from the installed FTB Quests build. Count one selected entry when that is the actual claim behavior; do not multiply by a reward table's `loot_size` or presentation metadata without evidence. Require every repeatable currency source and sink to have an exact scope, amount, cooldown, and dependency. A fallback faucet should not self-fund the complete sink board.

Scale currency rewards dynamically with quest tree depth and milestone significance (e.g., Bevel -> Sprocket -> Cog -> Crown). Substantive late-game milestones must not award trivial early-game pocket change.

## Layout audit pattern

Treat coordinates as part of implementation, not decoration:

1. Put the shared or mandatory spine on one consistent axis.
2. Arrange comparable alternatives as a symmetric fan or evenly spaced row.
3. Put optional progression and story branches on stable sides of the spine.
4. Re-render after dependency or coordinate edits and count crossings.
5. Inspect titles, icon/background contrast, and text wrapping at real client scale.

Keep node titles to a pack-tested short ceiling, normally two to four words. Put lane names, suitability, and explanatory labels in subtitles; retain prices, cooldowns, or consent warnings in titles only when players need them before opening the node.

A generated graph board proves source geometry only. Label it as source-level evidence until the chapter is opened in the shipped client.

## Audit checklist

- [ ] Every ID is unique within the chapter and does not collide with existing chapters.
- [ ] Every task/reward type and required field is accepted by the installed FTB Quests version.
- [ ] Every item, block, entity, advancement, statistic, recipe, currency, and command namespace resolves in the target pack.
- [ ] Every task and reward item is confirmed obtainable in survival (no backend, internal, or creative-only items).
- [ ] Advancement criteria and stat semantics match the actual trigger.
- [ ] Dependencies form an acyclic graph; the opener, branch minimum, and capstone are reachable.
- [ ] The computed shortest path matches every advertised any-N-of-M requirement; no hidden sibling prerequisite raises N.
- [ ] Side-story quests use explicit optional UI semantics when supported.
- [ ] Building quests use the Palette Quest pattern (gathering accessible palette items + 2x-3x building rewards + crafting materials) rather than untrackable multiblock placement.
- [ ] Workstations and progression altars verify core component and tank acquisition in inventory, not world assembly.
- [ ] Conflict, prank, and reconnaissance quests respect FTB Chunks / FTB Teams claim safety (e.g. photography, harmless throwables).
- [ ] Repeatable quests have a visible price, a cooldown/stock limiter, and a worst-case weekly budget.
- [ ] No purchase can refund its own input, create a cheaper input, or dominate all other routes.
- [ ] Personal/team, minimum/completionist, repeatable, fragmented-team, and full-sink totals are accounted separately.
- [ ] Currency rewards scale progressively with quest depth rather than paying flat starter change across all tiers.
- [ ] Specialized crafting materials (runes, obsidian, ingots) satisfy full-set crafting thresholds (e.g. 4 runes for full armor, 16 obsidian for portal).
- [ ] Early rewards provide immediate survival utility (gear, tools, bed, food) rather than dormant high-tier fragments.
- [ ] Consumable rewards (inks, potions) are provided in meaningful batches rather than token scraps.
- [ ] Team/individual progress and team_reward behavior are deliberate and playtested.
- [ ] Every translation key exists, and copy names the action and its purpose.
- [ ] Player-facing text contains no design guarantees, admin commentary, placeholder status, or balance claims.
- [ ] Mandatory onboarding forms a closed dependency loop; every required clause feeds the terminal acknowledgement and downstream gate.
- [ ] Substantive progression uses hard native criteria where possible; checkmark-only quests are optional/explanatory or modestly rewarded and do not default to currency.
- [ ] Item tasks state inspect, consume, place, or public-contribution semantics, and no prerequisite reward trivially auto-completes the next task.
- [ ] Every material reward reaches a useful current-stage recipe/service threshold; adjacent rewards are distinct and late milestones avoid starter filler.
- [ ] Faction/class anti-conditions use verified visibility support or an accessible redesign; no ordinary visible quest is currently impossible for its audience.
- [ ] Persistent-world campaigns avoid unrequested wipe/finale framing and leave infrastructure, roles, or future pressures in play.
- [ ] Every icon/image reference resolves with exact case and / separators.
- [ ] Edited layouts have no accidental overlap/crossing, and source renders are not mislabeled as client screenshots.
- [ ] Resource-pack metadata and Packwiz SHA-256 values match the hosted asset.
- [ ] The authoritative source and derived files synchronize idempotently; a stale generator cannot silently overwrite live authoring.
- [ ] No custom KubeJS quest logic was added unless explicitly authorized.
- [ ] A disposable-world smoke test completed the minimum path and one exchange.

## Player-balance worksheet

Before committing, write down:

| Field | Value |
| --- | --- |
| Current server band | <tools / armor / machines / bosses / collection> |
| Expected active players | <regular / peak> |
| Typical session | <minutes> |
| Route count and minimum | <M routes / N required> |
| Repeat window | <cooldown or stock> |
| Max currency issued per player/week | <amount> |
| Currency scaling across tiers | <denominations and volume progression> |
| One-time personal/team ceilings | <minimum route / completionist> |
| Fragmented-team repeatable ceiling | <teams × amount per cooldown> |
| Full sink-board price | <amount per cooldown> |
| Strongest purchased item | <item + why it is not a tier skip> |
| Smallest material bundle | <recipe/service enabled at the current stage> |
| Specialized material sets | <full-set gear craft verified: e.g. 4 runes, 16 obsidian> |
| Checkmark-only quests | <why each is optional/explanatory or modestly rewarded> |
| Building verification | <Palette Quest item requirements and stock multipliers> |
| World lifetime | <persistent, seasonal, or event-based framing> |
| Catch-up benefit | <convenience, infrastructure, information> |
| Manual test remaining | <none or exact step> |

