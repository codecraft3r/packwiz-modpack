# VvH Discovery — dev branch retune

## Authoritative pack snapshot

- Repository: `codecraft3r/packwiz-modpack`
- Source branch: `dev`
- Pinned dev revision: `3e4842383dd1e029f054aedfe19940f0b53adbcd`
- Pack name: `Poiesis 2`
- `pack.toml` version field at this revision: `2.4.0`
- Changelog development label: `3.0.0-pre1`
- Minecraft: `1.21.1`
- NeoForge: `21.1.233`
- FTB Quests: `2101.1.27`
- FTB Teams: `2101.1.10`
- FTB Chunks: `2101.1.19`
- KubeJS: `2101.7.2-build.368`
- Dev server materialization: 135 JARs, about 424 MiB of JAR payload.

The mismatch between the `pack.toml` version field and the changelog development label is pre-existing dev-branch metadata drift. VvH records it rather than silently changing release metadata unrelated to this campaign.

## Modlist change that forced the retune

The old Season One build targeted master before the current dev overhaul. The dev branch removes Cobblemon and a large set of its addons plus AE2/Tempad/Tom's Storage-era assumptions, while adding a real Vampirism stack and new social/transport surfaces.

Key exact installed systems used by this revision:

- Vampirism `1.10.12`
- Godly Vampirism `1.10.0`
- Vampire's Delight `0.1.12b`
- Vampirism Integrations `1.10.2`
- Vampirism Iron's Spells Compatibility `0.0.6`
- Iron's Spells 'n Spellbooks `3.16.2`
- Create `6.0.10` plus Create Aeronautics/Propulsion/Avionics, Create Big Cannons, Enchantment Industry, Numismatics, and other addons
- Minecraft Comes Alive Reborn and Capitals
- The Hordes
- Farmer's Delight
- Nature's Compass / Explorer's Compass
- Mekanism, Powah, Flux Networks, Sophisticated Backpacks, Via Romana, and the existing building/decor stack

## Exact data inspected

The build harness materialized the server pack from Packwiz and indexed the actual installed JARs. Exact advancement JSON was inspected for:

- `vampirism:vampire/become_vampire`
- `vampirism:hunter/become_hunter`
- `vampirism:vampire/first_blood`
- `vampirism:hunter/stake`
- `vampirism:hunter/technology`
- `vampirism:main/vampire_forest`

Exact recipes/items were also resolved for the Vampire/Hunter foundation workstations and supplies. The campaign does not guess namespaces from a wiki.

## Existing quest debt discovered

The dev branch still carried the previous Living Atlas chapters and reward tables, but those files referenced the removed `cobblemon:` namespace in icons, images, statistics, reward items, and localization. Shipping VvH without fixing those pages would leave the quest book internally broken.

The generator therefore performs an idempotent migration of the existing Living Atlas content while preserving its quest/task/reward object IDs. Old Cobblemon objectives become current-dev Vampirism/Create/exploration/social objectives; Great/Poke Ball rewards become Vampire's Delight Hardtack travel utility. This is a content migration, not a progress reset.

## Implemented VvH surface

- 10 VvH chapters
- 82 VvH quests
- 100 VvH tasks
- 36 direct quest rewards
- 3 VvH reward tables / 14 choice-table entries
- 0 new VvH KubeJS scripts
- 3 equal foundation branches: Vampire, Hunter, Neutral
- 8 choice-based personal contribution routes
- 8 shared/public infrastructure projects
- 6 noncombat rivalry formats plus one separately gated optional skirmish
- 6 Long Night Fair contribution categories
- 5 limited weekly civic requisition sinks

## Progression assumption

No representative live world/save or current player inventory snapshot was supplied. Rewards therefore remain horizontal, modest, and useful across a broad early-to-midgame band. Creative tasks use peer/host review rather than brittle block scanning.
