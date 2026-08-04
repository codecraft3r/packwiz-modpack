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

For an "any N of M" route, create M comparable quests, attach them to a common opener, and use the target schema's minimum dependency field so N completions unlock the capstone. Verify the graph in the UI and in the loader; do not rely on a hand-counted diagram.

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

## Audit checklist

- [ ] Every ID is unique within the chapter and does not collide with existing chapters.
- [ ] Every task/reward type and required field is accepted by the installed FTB Quests version.
- [ ] Every item, block, entity, advancement, statistic, recipe, currency, and command namespace resolves in the target pack.
- [ ] Advancement criteria and stat semantics match the actual trigger.
- [ ] Dependencies form an acyclic graph; the opener, branch minimum, and capstone are reachable.
- [ ] Repeatable quests have a visible price, a cooldown/stock limiter, and a worst-case weekly budget.
- [ ] No purchase can refund its own input, create a cheaper input, or dominate all other routes.
- [ ] Team/individual progress and team_reward behavior are deliberate and playtested.
- [ ] Every translation key exists, and copy names the action and its purpose.
- [ ] Every icon/image reference resolves with exact case and / separators.
- [ ] Resource-pack metadata and Packwiz SHA-256 values match the hosted asset.
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
| Strongest purchased item | <item + why it is not a tier skip> |
| Catch-up benefit | <convenience, infrastructure, information> |
| Manual test remaining | <none or exact step> |
