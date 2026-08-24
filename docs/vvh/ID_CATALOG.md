# VvH Current-Pack ID Catalog

This catalog contains only IDs referenced by the live six-chapter campaign. Every non-vanilla namespace must be backed by a `.pw.toml` that is present in the current `index.toml`, and every evidence JAR must match that metadata's exact filename.

An unrelated downloaded JAR is not proof that a mod is installed. Run `python -B -X utf8 scripts/vvh_sync_catalog.py --check .` before release.

## Pack membership

| Namespace | Indexed metadata | Pinned JAR | Side | Download hash |
| --- | --- | --- | --- | --- |
| `create` | `mods/create.pw.toml` | `create-1.21.1-6.0.10.jar` | `both` | `sha512:11cc8fc049d2f67f6548c7abfada6b82a3adb5c7ca410a742de04bbca76e03862c518721b88d806f6e6d768a4d68531fdb903a85859b25d1484d550cc7bafd4b` |
| `explorerscompass` | `mods/explorers-compass.pw.toml` | `ExplorersCompass-1.21.1-3.4.0-neoforge.jar` | `both` | `sha512:a1b2e385aaacb547763441fc23e9a33a0b1d67bd32094cd605ded3fbdd1c7a0e5fc4520fdfa090c29d2d3384b685e3ead91b32d20030e45632c94145ee3ec668` |
| `exposure` | `mods/exposure.pw.toml` | `exposure-neoforge-1.21.1-1.9.18.jar` | `both` | `sha512:2c0310cfbc9abfcf9e589fdf1079829253e47eb3ac84684a643951ebc432536a4e6f6567a67fc8ba4f4d55036e513804ff0996adee6a8a11cf59c76399de5ef6` |
| `irons_spellbooks` | `mods/irons-spells-n-spellbooks.pw.toml` | `irons_spellbooks-1.21.1-3.16.3.jar` | `both` | `sha512:fd782f98c6c59b193c4832f33775291d2a7e639e1e23dd47510bfb494d99d182bec1253566b9394f96c733a0d0108be34bd729614b82dc29e55e096fdeb96f5b` |
| `numismatics` | `mods/numismatics.pw.toml` | `CreateNumismatics-1.0.20+neoforge-mc1.21.1.jar` | `both` | `sha512:2b4ccd516865997735e1a3ec323615bd32d9388e15cc04097ac455f2b453423fccd21969782ecfd031b3de6ed85506ba5349da24c32f5e3eaaf558c5163cf203` |
| `vampirism` | `mods/vampirism.pw.toml` | `Vampirism-1.21-1.10.12.jar` | `both` | `sha512:b19aec3fb8abb2c83047b64d2497fa440e9295044919b546cfaedd417e604e2176e48c289745ed0a03ec57d032e7051e16de993ef3107d42f5b077187662c070` |

## Campaign items and icons

| Namespace | ID | Display name | Exact evidence JAR | JAR entry evidence |
| --- | --- | --- | --- | --- |
| `create` | `create:andesite_alloy` | Andesite Alloy | `create-1.21.1-6.0.10.jar` | `assets/create/lang/en_us.json::item.create.andesite_alloy` |
| `create` | `create:andesite_casing` | Andesite Casing | `create-1.21.1-6.0.10.jar` | `assets/create/lang/en_us.json::block.create.andesite_casing` |
| `create` | `create:basin` | Basin | `create-1.21.1-6.0.10.jar` | `assets/create/lang/en_us.json::block.create.basin` |
| `create` | `create:chute` | Chute | `create-1.21.1-6.0.10.jar` | `assets/create/lang/en_us.json::block.create.chute` |
| `create` | `create:cogwheel` | Cogwheel | `create-1.21.1-6.0.10.jar` | `assets/create/lang/en_us.json::block.create.cogwheel` |
| `create` | `create:depot` | Depot | `create-1.21.1-6.0.10.jar` | `assets/create/lang/en_us.json::block.create.depot` |
| `create` | `create:encased_fan` | Encased Fan | `create-1.21.1-6.0.10.jar` | `assets/create/lang/en_us.json::block.create.encased_fan` |
| `create` | `create:gearbox` | Gearbox | `create-1.21.1-6.0.10.jar` | `assets/create/lang/en_us.json::block.create.gearbox` |
| `create` | `create:large_cogwheel` | Large Cogwheel | `create-1.21.1-6.0.10.jar` | `assets/create/lang/en_us.json::block.create.large_cogwheel` |
| `create` | `create:mechanical_drill` | Mechanical Drill | `create-1.21.1-6.0.10.jar` | `assets/create/lang/en_us.json::block.create.mechanical_drill` |
| `create` | `create:mechanical_press` | Mechanical Press | `create-1.21.1-6.0.10.jar` | `assets/create/lang/en_us.json::block.create.mechanical_press` |
| `create` | `create:precision_mechanism` | Precision Mechanism | `create-1.21.1-6.0.10.jar` | `assets/create/lang/en_us.json::item.create.precision_mechanism` |
| `create` | `create:shaft` | Shaft | `create-1.21.1-6.0.10.jar` | `assets/create/lang/en_us.json::block.create.shaft` |
| `create` | `create:smart_chute` | Smart Chute | `create-1.21.1-6.0.10.jar` | `assets/create/lang/en_us.json::block.create.smart_chute` |
| `create` | `create:water_wheel` | Water Wheel | `create-1.21.1-6.0.10.jar` | `assets/create/lang/en_us.json::block.create.water_wheel` |
| `create` | `create:windmill_bearing` | Windmill Bearing | `create-1.21.1-6.0.10.jar` | `assets/create/lang/en_us.json::block.create.windmill_bearing` |
| `explorerscompass` | `explorerscompass:explorerscompass` | Explorer's Compass | `ExplorersCompass-1.21.1-3.4.0-neoforge.jar` | `assets/explorerscompass/models/item/explorerscompass.json; data/explorerscompass/recipe/explorers_compass.json` |
| `exposure` | `exposure:album` | Photo Album | `exposure-neoforge-1.21.1-1.9.18.jar` | `assets/exposure/lang/en_us.json::item.exposure.album` |
| `exposure` | `exposure:black_and_white_film` | Black and White Film | `exposure-neoforge-1.21.1-1.9.18.jar` | `assets/exposure/lang/en_us.json::item.exposure.black_and_white_film` |
| `exposure` | `exposure:camera` | Camera | `exposure-neoforge-1.21.1-1.9.18.jar` | `assets/exposure/lang/en_us.json::item.exposure.camera` |
| `exposure` | `exposure:camera_stand` | Camera Stand | `exposure-neoforge-1.21.1-1.9.18.jar` | `assets/exposure/lang/en_us.json::item.exposure.camera_stand` |
| `exposure` | `exposure:color_film` | Color Film | `exposure-neoforge-1.21.1-1.9.18.jar` | `assets/exposure/lang/en_us.json::item.exposure.color_film` |
| `exposure` | `exposure:high_sensitivity_color_film` | High-Sensitivity Color Film | `exposure-neoforge-1.21.1-1.9.18.jar` | `assets/exposure/lang/en_us.json::item.exposure.high_sensitivity_color_film; data/exposure/recipe/high_sensitivity_color_film.json` |
| `exposure` | `exposure:photograph` | Photograph | `exposure-neoforge-1.21.1-1.9.18.jar` | `assets/exposure/lang/en_us.json::item.exposure.photograph` |
| `exposure` | `exposure:photograph_frame` | Photograph Frame | `exposure-neoforge-1.21.1-1.9.18.jar` | `assets/exposure/lang/en_us.json::item.exposure.photograph_frame` |
| `irons_spellbooks` | `irons_spellbooks:affinity_ring` | Ring of %s Affinity | `irons_spellbooks-1.21.1-3.16.3.jar` | `assets/irons_spellbooks/lang/en_us.json::item.irons_spellbooks.affinity_ring` |
| `irons_spellbooks` | `irons_spellbooks:arcane_essence` | Arcane Essence | `irons_spellbooks-1.21.1-3.16.3.jar` | `assets/irons_spellbooks/lang/en_us.json::item.irons_spellbooks.arcane_essence` |
| `irons_spellbooks` | `irons_spellbooks:blank_rune` | Blank Runestone | `irons_spellbooks-1.21.1-3.16.3.jar` | `assets/irons_spellbooks/lang/en_us.json::item.irons_spellbooks.blank_rune` |
| `irons_spellbooks` | `irons_spellbooks:blood_rune` | Blood Rune | `irons_spellbooks-1.21.1-3.16.3.jar` | `assets/irons_spellbooks/lang/en_us.json::item.irons_spellbooks.blood_rune` |
| `irons_spellbooks` | `irons_spellbooks:common_ink` | Common Ink | `irons_spellbooks-1.21.1-3.16.3.jar` | `assets/irons_spellbooks/lang/en_us.json::item.irons_spellbooks.common_ink` |
| `irons_spellbooks` | `irons_spellbooks:copper_spell_book` | Flimsy Journal | `irons_spellbooks-1.21.1-3.16.3.jar` | `assets/irons_spellbooks/lang/en_us.json::item.irons_spellbooks.copper_spell_book; data/irons_spellbooks/recipe/copper_spell_book.json` |
| `irons_spellbooks` | `irons_spellbooks:cultist_boots` | Cultist Boots | `irons_spellbooks-1.21.1-3.16.3.jar` | `assets/irons_spellbooks/lang/en_us.json::item.irons_spellbooks.cultist_boots; data/irons_spellbooks/recipe/cultist_boots_crafting.json` |
| `irons_spellbooks` | `irons_spellbooks:cultist_chestplate` | Cultist Armor | `irons_spellbooks-1.21.1-3.16.3.jar` | `assets/irons_spellbooks/lang/en_us.json::item.irons_spellbooks.cultist_chestplate; data/irons_spellbooks/recipe/cultist_chestplate_crafting.json` |
| `irons_spellbooks` | `irons_spellbooks:cultist_helmet` | Cultist Hood | `irons_spellbooks-1.21.1-3.16.3.jar` | `assets/irons_spellbooks/lang/en_us.json::item.irons_spellbooks.cultist_helmet; data/irons_spellbooks/recipe/cultist_helmet_crafting.json` |
| `irons_spellbooks` | `irons_spellbooks:cultist_leggings` | Cultist Leggings | `irons_spellbooks-1.21.1-3.16.3.jar` | `assets/irons_spellbooks/lang/en_us.json::item.irons_spellbooks.cultist_leggings; data/irons_spellbooks/recipe/cultist_leggings_crafting.json` |
| `irons_spellbooks` | `irons_spellbooks:holy_rune` | Holy Rune | `irons_spellbooks-1.21.1-3.16.3.jar` | `assets/irons_spellbooks/lang/en_us.json::item.irons_spellbooks.holy_rune` |
| `irons_spellbooks` | `irons_spellbooks:inscription_table` | Inscription Table | `irons_spellbooks-1.21.1-3.16.3.jar` | `assets/irons_spellbooks/lang/en_us.json::block.irons_spellbooks.inscription_table; data/irons_spellbooks/recipe/inscription_table.json` |
| `irons_spellbooks` | `irons_spellbooks:priest_boots` | Priest Boots | `irons_spellbooks-1.21.1-3.16.3.jar` | `assets/irons_spellbooks/lang/en_us.json::item.irons_spellbooks.priest_boots` |
| `irons_spellbooks` | `irons_spellbooks:priest_chestplate` | Priest Robes | `irons_spellbooks-1.21.1-3.16.3.jar` | `assets/irons_spellbooks/lang/en_us.json::item.irons_spellbooks.priest_chestplate` |
| `irons_spellbooks` | `irons_spellbooks:priest_helmet` | Priest Mask | `irons_spellbooks-1.21.1-3.16.3.jar` | `assets/irons_spellbooks/lang/en_us.json::item.irons_spellbooks.priest_helmet` |
| `irons_spellbooks` | `irons_spellbooks:priest_leggings` | Priest Leggings | `irons_spellbooks-1.21.1-3.16.3.jar` | `assets/irons_spellbooks/lang/en_us.json::item.irons_spellbooks.priest_leggings` |
| `irons_spellbooks` | `irons_spellbooks:scroll` | Scroll | `irons_spellbooks-1.21.1-3.16.3.jar` | `assets/irons_spellbooks/lang/en_us.json::item.irons_spellbooks.scroll` |
| `irons_spellbooks` | `irons_spellbooks:spell_book` | Spell Book | `irons_spellbooks-1.21.1-3.16.3.jar` | `assets/irons_spellbooks/lang/en_us.json::item.irons_spellbooks.spell_book` |
| `irons_spellbooks` | `irons_spellbooks:uncommon_ink` | Uncommon Ink | `irons_spellbooks-1.21.1-3.16.3.jar` | `assets/irons_spellbooks/lang/en_us.json::item.irons_spellbooks.uncommon_ink` |
| `numismatics` | `numismatics:bevel` | Bevel | `CreateNumismatics-1.0.20+neoforge-mc1.21.1.jar` | `assets/numismatics/lang/en_us.json::item.numismatics.bevel` |
| `vampirism` | `vampirism:alchemical_cauldron` | Alchemical Cauldron | `Vampirism-1.21-1.10.12.jar` | `assets/vampirism/lang/en_us.json::block.vampirism.alchemical_cauldron` |
| `vampirism` | `vampirism:altar_infusion` | Altar of Infusion | `Vampirism-1.21-1.10.12.jar` | `assets/vampirism/lang/en_us.json::block.vampirism.altar_infusion` |
| `vampirism` | `vampirism:altar_inspiration` | Altar of Inspiration | `Vampirism-1.21-1.10.12.jar` | `assets/vampirism/lang/en_us.json::block.vampirism.altar_inspiration; data/vampirism/recipe/vampire/altar_inspiration.json` |
| `vampirism` | `vampirism:blood_bottle` | Blood Bottle | `Vampirism-1.21-1.10.12.jar` | `assets/vampirism/lang/en_us.json::item.vampirism.blood_bottle` |
| `vampirism` | `vampirism:blood_container` | Blood Container | `Vampirism-1.21-1.10.12.jar` | `assets/vampirism/lang/en_us.json::block.vampirism.blood_container` |
| `vampirism` | `vampirism:blood_infused_enhanced_iron_ingot` | Enhanced Blood-Infused Iron Ingot | `Vampirism-1.21-1.10.12.jar` | `assets/vampirism/lang/en_us.json::item.vampirism.blood_infused_enhanced_iron_ingot; data/vampirism/recipe/vampire/blood_infused_enhanced_iron_ingot.json` |
| `vampirism` | `vampirism:blood_infused_iron_ingot` | Blood-Infused Iron Ingot | `Vampirism-1.21-1.10.12.jar` | `assets/vampirism/lang/en_us.json::item.vampirism.blood_infused_iron_ingot; data/vampirism/recipe/vampire/blood_infused_iron_ingot.json` |
| `vampirism` | `vampirism:blood_pedestal` | Blood Pedestal | `Vampirism-1.21-1.10.12.jar` | `assets/vampirism/lang/en_us.json::block.vampirism.blood_pedestal` |
| `vampirism` | `vampirism:coffin_red` | Red Coffin | `Vampirism-1.21-1.10.12.jar` | `assets/vampirism/lang/en_us.json::block.vampirism.coffin_red; data/vampirism/recipe/vampire/coffin_red.json` |
| `vampirism` | `vampirism:crossbow_arrow_spitfire` | Spitfire | `Vampirism-1.21-1.10.12.jar` | `assets/vampirism/lang/en_us.json::item.vampirism.crossbow_arrow_spitfire` |
| `vampirism` | `vampirism:crossbow_arrow_teleport` | Teleport Quarrel | `Vampirism-1.21-1.10.12.jar` | `assets/vampirism/lang/en_us.json::item.vampirism.crossbow_arrow_teleport` |
| `vampirism` | `vampirism:crossbow_arrow_vampire_killer` | Vampire Killer Quarrel | `Vampirism-1.21-1.10.12.jar` | `assets/vampirism/lang/en_us.json::item.vampirism.crossbow_arrow_vampire_killer` |
| `vampirism` | `vampirism:enhanced_crossbow` | Enhanced Crossbow | `Vampirism-1.21-1.10.12.jar` | `assets/vampirism/lang/en_us.json::item.vampirism.enhanced_crossbow` |
| `vampirism` | `vampirism:garlic_diffuser` | Garlic Diffuser | `Vampirism-1.21-1.10.12.jar` | `assets/vampirism/lang/en_us.json::block.vampirism.garlic_diffuser` |
| `vampirism` | `vampirism:heart_seeker_enhanced` | Enhanced Heartseeker | `Vampirism-1.21-1.10.12.jar` | `data/vampirism/recipe/vampire/heart_seeker_enhanced.json::result.id; de/teamlapen/vampirism/core/ModItems.class::heart_seeker_enhanced` |
| `vampirism` | `vampirism:holy_salt` | Blessed Salt | `Vampirism-1.21-1.10.12.jar` | `assets/vampirism/lang/en_us.json::item.vampirism.holy_salt` |
| `vampirism` | `vampirism:holy_water_bottle` | Holy Water | `Vampirism-1.21-1.10.12.jar` | `assets/vampirism/lang/en_us.json::item.vampirism.holy_water_bottle` |
| `vampirism` | `vampirism:holy_water_splash_bottle_enhanced` | Enhanced Splash Bottle of Holy Water | `Vampirism-1.21-1.10.12.jar` | `de/teamlapen/vampirism/core/ModItems.class::holy_water_splash_bottle_enhanced; assets/vampirism/models/item/holy_water_splash_bottle_enhanced.json` |
| `vampirism` | `vampirism:hunter_axe` | Hunter Axe | `Vampirism-1.21-1.10.12.jar` | `assets/vampirism/lang/en_us.json::item.vampirism.hunter_axe` |
| `vampirism` | `vampirism:hunter_axe_enhanced` | Enhanced Hunter Axe | `Vampirism-1.21-1.10.12.jar` | `data/vampirism/recipe/hunter_axe_enhanced.json::result.id; de/teamlapen/vampirism/core/ModItems.class::hunter_axe_enhanced` |
| `vampirism` | `vampirism:hunter_coat_chest` | Hunter Coat | `Vampirism-1.21-1.10.12.jar` | `assets/vampirism/lang/en_us.json::item.vampirism.hunter_coat_chest` |
| `vampirism` | `vampirism:hunter_coat_feet` | Hunter Coat Boots | `Vampirism-1.21-1.10.12.jar` | `assets/vampirism/lang/en_us.json::item.vampirism.hunter_coat_feet` |
| `vampirism` | `vampirism:hunter_coat_head` | Hunter Coat Helmet | `Vampirism-1.21-1.10.12.jar` | `assets/vampirism/lang/en_us.json::item.vampirism.hunter_coat_head` |
| `vampirism` | `vampirism:hunter_coat_legs` | Hunter Coat Leggings | `Vampirism-1.21-1.10.12.jar` | `assets/vampirism/lang/en_us.json::item.vampirism.hunter_coat_legs` |
| `vampirism` | `vampirism:hunter_table` | Hunter Research Table | `Vampirism-1.21-1.10.12.jar` | `assets/vampirism/lang/en_us.json::block.vampirism.hunter_table` |
| `vampirism` | `vampirism:injection_garlic` | Garlic Injection | `Vampirism-1.21-1.10.12.jar` | `assets/vampirism/lang/en_us.json::item.vampirism.injection_garlic; de/teamlapen/vampirism/core/ModItems.class::injection_garlic` |
| `vampirism` | `vampirism:pitchfork` | Pitchfork | `Vampirism-1.21-1.10.12.jar` | `assets/vampirism/lang/en_us.json::item.vampirism.pitchfork` |
| `vampirism` | `vampirism:pure_blood_4` | Pure Blood (purity 4) | `Vampirism-1.21-1.10.12.jar` | `data/vampirism/recipe/blood_infused_enhanced_iron_ingot_from_pure_blood_4.json::fluid.item; de/teamlapen/vampirism/core/ModItems.class::pure_blood_4` |
| `vampirism` | `vampirism:pure_salt` | Pure Salt | `Vampirism-1.21-1.10.12.jar` | `assets/vampirism/lang/en_us.json::item.vampirism.pure_salt` |
| `vampirism` | `vampirism:purified_garlic` | Purified Garlic | `Vampirism-1.21-1.10.12.jar` | `assets/vampirism/lang/en_us.json::item.vampirism.purified_garlic` |
| `vampirism` | `vampirism:stake` | Stake | `Vampirism-1.21-1.10.12.jar` | `assets/vampirism/lang/en_us.json::item.vampirism.stake` |
| `vampirism` | `vampirism:vampire_cloak_white_black` | Vampire Cloak | `Vampirism-1.21-1.10.12.jar` | `assets/vampirism/lang/en_us.json::item.vampirism.vampire_cloak_white_black` |
| `vampirism` | `vampirism:vampire_fang` | Vampire Fang | `Vampirism-1.21-1.10.12.jar` | `assets/vampirism/lang/en_us.json::item.vampirism.vampire_fang` |
| `vampirism` | `vampirism:weapon_table` | Hunter Weapon Table | `Vampirism-1.21-1.10.12.jar` | `assets/vampirism/lang/en_us.json::block.vampirism.weapon_table` |

## Campaign advancements

| ID | Exact evidence JAR | JAR entry evidence |
| --- | --- | --- |
| `exposure:adventure/exposure` | `exposure-neoforge-1.21.1-1.9.18.jar` | `data/exposure/advancement/adventure/exposure.json` |
| `exposure:adventure/moment_in_time` | `exposure-neoforge-1.21.1-1.9.18.jar` | `data/exposure/advancement/adventure/moment_in_time.json` |
| `vampirism:hunter/become_hunter` | `Vampirism-1.21-1.10.12.jar` | `data/vampirism/advancement/hunter/become_hunter.json` |
| `vampirism:vampire/become_vampire` | `Vampirism-1.21-1.10.12.jar` | `data/vampirism/advancement/vampire/become_vampire.json` |

## Campaign spell IDs

| ID | School | Exact evidence JAR | JAR entry evidence |
| --- | --- | --- | --- |
| `irons_spellbooks:blood_slash` | blood | `irons_spellbooks-1.21.1-3.16.3.jar` | `assets/irons_spellbooks/lang/en_us.json::spell.irons_spellbooks.blood_slash; io/redspace/ironsspellbooks/spells/blood/BloodSlashSpell.class` |
| `irons_spellbooks:blood_step` | blood | `irons_spellbooks-1.21.1-3.16.3.jar` | `assets/irons_spellbooks/lang/en_us.json::spell.irons_spellbooks.blood_step; io/redspace/ironsspellbooks/spells/blood/BloodStepSpell.class` |
| `irons_spellbooks:heal` | holy | `irons_spellbooks-1.21.1-3.16.3.jar` | `assets/irons_spellbooks/lang/en_us.json::spell.irons_spellbooks.heal; io/redspace/ironsspellbooks/spells/holy/HealSpell.class` |
| `irons_spellbooks:recall` | ender | `irons_spellbooks-1.21.1-3.16.3.jar` | `assets/irons_spellbooks/lang/en_us.json::spell.irons_spellbooks.recall; io/redspace/ironsspellbooks/spells/ender/RecallSpell.class` |

## FTB Quests schema observations

- Installed evidence JAR: `ftb-quests-neoforge-2101.1.33.jar`
- Observed task/reward types: `advancement`, `checkmark`, `choice`, `item`

Vanilla `minecraft:*` IDs are outside this campaign-scoped catalog. Runtime/client checks remain separate from static Packwiz membership and JAR-entry proof.
