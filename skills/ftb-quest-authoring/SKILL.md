---
name: ftb-quest-authoring
description: Design, edit, balance, validate, and release FTB Quests chapters for any Minecraft modpack. Use when authoring quest SNBT, revising progression layouts, adding native tasks/rewards, integrating art, testing economy, or preparing a Packwiz release. Resolve IDs from the installed pack and avoid custom KubeJS quest logic by default.
---

# FTB Quest Authoring

Use the installed modpack as the source of truth. Preserve unrelated work and inspect the pack before inventing IDs, task types, rewards, images, or currencies.

## Workflow

1. Record the audience, current progression, preferred activities, group size, social shape, cadence, challenge, economy, and acceptance test.
2. Inspect `pack.toml`, `index.toml`, installed JARs, existing quest chapters, reward tables, translations, and resource packs. Copy the local FTB Quests schema and ID conventions.
3. Design a compact loop: opener, optional activity/faction routes, a shared milestone, and a useful capped utility sink. Separate personal progression from server-wide milestones.
4. Implement with native FTB Quests item/block/entity/stat/advancement/checkmark tasks and native rewards. Make team scope explicit. Use honor-system checkmarks for human-reviewed builds or social events.
5. Keep the world-building path readable as the primary spine; place optional progression and faction work as side branches. Give each quest one direct objective, separate lore from objective/build standard, and merge duplicates.
6. Balance rewards against the slowest regular player. Prefer choice bundles, construction/support materials, consumables, convenience, modest equipment help, and meaningful currency sinks. Avoid tier skips, rare boss gear, currency-positive loops, duplication, and dominant routes. Cap repeatables by price, cooldown, stock, or milestone.
7. Resolve every item, advancement, recipe, currency, image, and sound reference. Keep resource paths POSIX-style and do not add custom KubeJS quest logic unless explicitly requested.
8. Validate SNBT parsing, unique IDs, dependency acyclicity/reachability, localization keys, reward caps, asset paths, Packwiz metadata, and disposable-server loading. Capture actual client screenshots for layout/art acceptance; source-level render boards are review aids, not runtime evidence.
9. Run `packwiz refresh`, inspect the diff, commit only intended files, push a focused branch, and report checks, known gaps, and the next playtest step.

## Guardrails

- Never guess a namespace or display-name-based ID.
- Do not make attendance or faction state a hard class lock unless explicitly required.
- Keep cooperative objectives completable by a subset of active players and reward public utility without permanent power skips.
- Treat failed or missing asset/runtime evidence as unverified, not as a pass.

For portable SNBT patterns and audit details, read [references/ftb-quests-patterns.md](references/ftb-quests-patterns.md).
