# VvH Verification — dev branch

## Resolved before authoring

- Dev branch exists and was pinned to `3e4842383dd1e029f054aedfe19940f0b53adbcd`.
- Packwiz metadata at the pinned source was materialized successfully before the retune.
- Exact installed JAR contents were indexed rather than inferring IDs from names.
- Vampirism faction-entry advancements exist and use Vampirism's faction trigger for level 1.
- `vampirism:main/vampire_forest` is a real location advancement.
- Exact item/recipe data exists for the Vampire altar/coffin/blood resources and Hunter table/stake/alchemical stations used by foundation quests.
- Vampire's Delight Hardtack is a cheap current-pack travel ration and is used to replace removed Cobblemon reward slots without granting faction progression.
- Existing Living Atlas files contained invalid `cobblemon:` references on dev; the generator repairs them while retaining object IDs.

## Architectural verification decisions

- Current live Vampirism faction state is not represented by a proven native FTB Quests task. The campaign therefore uses exact historical faction-entry advancements plus explicit current-state peer/host confirmation for shared faction caches.
- No KubeJS synchronization or reward-scaling layer was added.
- Creative-build scanning remains unproven/undesirable for the modded building surface; peer/host review is used.
- World-reset automation remains outside the shipped quest package until a disposable-world reset test proves every relevant boundary and mod-data interaction.

## Automated build tests

The CI gauntlet is expected to run after generation against the pinned dev revision and record Packwiz cleanliness, exact namespace resolution, SNBT parsing, graph/economy validation, layout renders, server materialization, and a disposable NeoForge + FTB Quests reload smoke test under `docs/vvh/evidence/`.

## Requires runtime verification

- two-client personal versus team reward claiming;
- current Vampirism faction → FTB Teams social confirmation workflow during a real faction switch;
- live claim ownership/transfer after leaving a faction FTB party;
- normal-scale client chapter rendering and text wrapping;
- skirmish PvP toggle, protected noncombatants, backup, and restore;
- any future destructive wilderness reset procedure.
