# Portable FTB Quests Patterns

Use these as patterns, then verify exact fields against the installed FTB Quests build.

## Branches

- Put shared infrastructure on a clear vertical spine.
- Place optional faction/progression quests on side lanes.
- Use explicit minimum-dependency counts for any-of-many progression.
- Keep dependency edges short and avoid crossings; review at fit-to-content and readable zoom.

## Tasks

- Use item/block/entity tasks for observable inventory or world state.
- Use advancement tasks only with real advancement IDs and the schema-required criterion field.
- Use stat tasks whose text matches the actual trigger.
- Use checkmarks for human-reviewed builds, social events, and trust-based standards.

## Rewards

- Prefer bounded player-choice rewards over random power spikes.
- Set `team_reward` deliberately on every reward.
- For repeatables, consume exactly the displayed price, add a cooldown or cap, and test the worst-case weekly issuance.
- Never reward an input that can be converted back into more of the same input or into a stronger exchange.

## Audit checklist

- Parse every quest/reward/localization SNBT file.
- Check globally unique FTB object IDs and dependency acyclicity.
- Verify every translation key and namespaced item/image reference.
- Resolve image paths against the actual resource-pack ZIP or extracted source.
- Run Packwiz refresh and ensure `pack.toml` and `index.toml` are clean.
- Capture server logs and real client screenshots; label source-level mockups as non-runtime evidence.
