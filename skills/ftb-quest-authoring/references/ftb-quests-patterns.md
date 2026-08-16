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

## Layout audit pattern

Treat coordinates as part of implementation, not decoration:

1. Put the shared or mandatory spine on one consistent axis.
2. Arrange comparable alternatives as a symmetric fan or evenly spaced row.
3. Put optional progression and story branches on stable sides of the spine.
4. Re-render after dependency or coordinate edits and count crossings.
5. Inspect titles, icon/background contrast, and text wrapping at real client scale.

A generated graph board proves source geometry only. Label it as source-level evidence until the chapter is opened in the shipped client.

## Audit checklist

- [ ] Every ID is unique within the chapter and does not collide with existing chapters.
- [ ] Every task/reward type and required field is accepted by the installed FTB Quests version.
- [ ] Every item, block, entity, advancement, statistic, recipe, currency, and command namespace resolves in the target pack.
- [ ] Advancement criteria and stat semantics match the actual trigger.
- [ ] Dependencies form an acyclic graph; the opener, branch minimum, and capstone are reachable.
- [ ] The computed shortest path matches every advertised any-N-of-M requirement; no hidden sibling prerequisite raises N.
- [ ] Side-story quests use explicit optional UI semantics when supported.
- [ ] Repeatable quests have a visible price, a cooldown/stock limiter, and a worst-case weekly budget.
- [ ] No purchase can refund its own input, create a cheaper input, or dominate all other routes.
- [ ] Personal/team, minimum/completionist, repeatable, fragmented-team, and full-sink totals are accounted separately.
- [ ] Team/individual progress and team_reward behavior are deliberate and playtested.
- [ ] Every translation key exists, and copy names the action and its purpose.
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
| One-time personal/team ceilings | <minimum route / completionist> |
| Fragmented-team repeatable ceiling | <teams × amount per cooldown> |
| Full sink-board price | <amount per cooldown> |
| Strongest purchased item | <item + why it is not a tier skip> |
| Catch-up benefit | <convenience, infrastructure, information> |
| Manual test remaining | <none or exact step> |
