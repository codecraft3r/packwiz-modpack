# VvH Current-Pack ID Catalog

This catalog contains only IDs referenced by the live eight-chapter campaign. Every non-vanilla namespace must be backed by a `.pw.toml` that is present in the current `index.toml`, and every evidence JAR must match that metadata's exact filename.

An unrelated downloaded JAR is not proof that a mod is installed. Run `python -B -X utf8 scripts/vvh_sync_catalog.py --check .` before release.

## Pack membership

| Namespace | Indexed metadata | Pinned JAR | Side | Download hash |
| --- | --- | --- | --- | --- |
| `create` | `mods/create.pw.toml` | `create-1.21.1-6.0.10.jar` | `both` | `sha512:11cc8fc049d2f67f6548c7abfada6b82a3adb5c7ca410a742de04bbca76e03862c518721b88d806f6e6d768a4d68531fdb903a85859b25d1484d550cc7bafd4b` |
| `explorerscompass` | `mods/explorers-compass.pw.toml` | `ExplorersCompass-1.21.1-3.4.0-neoforge.jar` | `both` | `sha512:a1b2e385aaacb547763441fc23e9a33a0b1d67bd32094cd605ded3fbdd1c7a0e5fc4520fdfa090c29d2d3384b685e3ead91b32d20030e45632c94145ee3ec668` |
| `exposure` | `mods/exposure.pw.toml` | `exposure-neoforge-1.21.1-1.9.18.jar` | `both` | `sha512:2c0310cfbc9abfcf9e589fdf1079829253e47eb3ac84684a643951ebc432536a4e6f6567a67fc8ba4f4d55036e513804ff0996adee6a8a11cf59c76399de5ef6` |
| `irons_spellbooks` | `mods/irons-spells-n-spellbooks.pw.toml` | `irons_spellbooks-1.21.1-3.16.3.jar` | `both` | `sha512:fd782f98c6c59b193c4832f33775291d2a7e639e1e23dd47510bfb494d99d182bec1253566b9394f96c733a0d0108be34bd729614b82dc29e55e096fdeb96f5b` |
| `numismatics` | `mods/numismatics.pw.toml` | `CreateNumismatics-1.0.20+neoforge-mc1.21.1.jar` | `both` | `sha512:2b4ccd516865997735e1a3ec323615bd32d9388e15cc04097ac455f2b453423fccd21969782ecfd031b3de6ed85506ba5349da24c32f5e3eaaf558c5163cf203` |
| `supplementaries` | `mods/supplementaries.pw.toml` | `supplementaries-1.21.1-3.9.1-neoforge.jar` | `both` | `sha512:b72fad1d77d6d9dd536ce008f23a9014f4d47231ebf5c4e7d5c23156243f5135eacaf34b2d022a028412ffe5e803081b48abdf3ed61951c6930ad463633c9abb` |
| `vampirism` | `mods/vampirism.pw.toml` | `Vampirism-1.21-1.10.12.jar` | `both` | `sha512:b19aec3fb8abb2c83047b64d2497fa440e9295044919b546cfaedd417e604e2176e48c289745ed0a03ec57d032e7051e16de993ef3107d42f5b077187662c070` |
| `vista` | `mods/vista_tv.pw.toml` | `vista-1.21.1-5.4.4-neoforge.jar` | `both` | `sha512:a26106fb220f71a09e5b7817f757952f0b5ff277d2a29cfce07255d307a680bdde8158ccc0ffa9311356e70a125b26ed85216a9418aa195fd47dc48a4b15dd60` |

## Campaign items and icons

| Namespace | ID | Display name | Exact evidence JAR | JAR entry evidence |
| --- | --- | --- | --- | --- |
| `create` | `create:andesite_alloy` | Andesite Alloy | `create-1.21.1-6.0.10.jar` | `assets/create/lang/en_us.json::item.create.andesite_alloy` |
| `create` | `create:belt_connector` | Mechanical Belt | `create-1.21.1-6.0.10.jar` | `assets/create/models/item/belt_connector.json; data/create/recipe/crafting/kinetics/belt_connector.json` |
| `create` | `create:brass_ingot` | Brass Ingot | `create-1.21.1-6.0.10.jar` | `assets/create/models/item/brass_ingot.json; data/create/recipe/mixing/brass_ingot.json; data/create/recipe/pressing/brass_ingot.json` |
| `create` | `create:precision_mechanism` | Precision Mechanism | `create-1.21.1-6.0.10.jar` | `assets/create/lang/en_us.json::item.create.precision_mechanism` |
| `explorerscompass` | `explorerscompass:explorerscompass` | Explorer's Compass | `ExplorersCompass-1.21.1-3.4.0-neoforge.jar` | `assets/explorerscompass/models/item/explorerscompass.json; data/explorerscompass/recipe/explorers_compass.json` |
| `exposure` | `exposure:album` | Photo Album | `exposure-neoforge-1.21.1-1.9.18.jar` | `assets/exposure/lang/en_us.json::item.exposure.album` |
| `exposure` | `exposure:black_and_white_film` | Black and White Film | `exposure-neoforge-1.21.1-1.9.18.jar` | `assets/exposure/lang/en_us.json::item.exposure.black_and_white_film` |
| `exposure` | `exposure:camera` | Camera | `exposure-neoforge-1.21.1-1.9.18.jar` | `assets/exposure/lang/en_us.json::item.exposure.camera` |
| `exposure` | `exposure:color_film` | Color Film | `exposure-neoforge-1.21.1-1.9.18.jar` | `assets/exposure/lang/en_us.json::item.exposure.color_film` |
| `exposure` | `exposure:photograph_frame` | Photograph Frame | `exposure-neoforge-1.21.1-1.9.18.jar` | `assets/exposure/lang/en_us.json::item.exposure.photograph_frame` |
| `irons_spellbooks` | `irons_spellbooks:arcane_essence` | Arcane Essence | `irons_spellbooks-1.21.1-3.16.3.jar` | `assets/irons_spellbooks/lang/en_us.json::item.irons_spellbooks.arcane_essence` |
| `irons_spellbooks` | `irons_spellbooks:blank_rune` | Blank Runestone | `irons_spellbooks-1.21.1-3.16.3.jar` | `assets/irons_spellbooks/lang/en_us.json::item.irons_spellbooks.blank_rune` |
| `irons_spellbooks` | `irons_spellbooks:blood_rune` | Blood Rune | `irons_spellbooks-1.21.1-3.16.3.jar` | `assets/irons_spellbooks/lang/en_us.json::item.irons_spellbooks.blood_rune` |
| `irons_spellbooks` | `irons_spellbooks:blood_upgrade_orb` | Blood Upgrade Orb | `irons_spellbooks-1.21.1-3.16.3.jar` | `assets/irons_spellbooks/models/item/blood_upgrade_orb.json; data/irons_spellbooks/recipe/blood_upgrade_orb.json` |
| `irons_spellbooks` | `irons_spellbooks:common_ink` | Common Ink | `irons_spellbooks-1.21.1-3.16.3.jar` | `assets/irons_spellbooks/lang/en_us.json::item.irons_spellbooks.common_ink` |
| `irons_spellbooks` | `irons_spellbooks:copper_spell_book` | Flimsy Journal | `irons_spellbooks-1.21.1-3.16.3.jar` | `assets/irons_spellbooks/lang/en_us.json::item.irons_spellbooks.copper_spell_book; data/irons_spellbooks/recipe/copper_spell_book.json` |
| `irons_spellbooks` | `irons_spellbooks:holy_rune` | Holy Rune | `irons_spellbooks-1.21.1-3.16.3.jar` | `assets/irons_spellbooks/lang/en_us.json::item.irons_spellbooks.holy_rune` |
| `irons_spellbooks` | `irons_spellbooks:holy_upgrade_orb` | Holy Upgrade Orb | `irons_spellbooks-1.21.1-3.16.3.jar` | `assets/irons_spellbooks/models/item/holy_upgrade_orb.json; data/irons_spellbooks/recipe/holy_upgrade_orb.json` |
| `irons_spellbooks` | `irons_spellbooks:inscription_table` | Inscription Table | `irons_spellbooks-1.21.1-3.16.3.jar` | `assets/irons_spellbooks/lang/en_us.json::block.irons_spellbooks.inscription_table; data/irons_spellbooks/recipe/inscription_table.json` |
| `irons_spellbooks` | `irons_spellbooks:rare_ink` | Rare Ink | `irons_spellbooks-1.21.1-3.16.3.jar` | `assets/irons_spellbooks/models/item/rare_ink.json` |
| `irons_spellbooks` | `irons_spellbooks:scroll` | Scroll | `irons_spellbooks-1.21.1-3.16.3.jar` | `assets/irons_spellbooks/lang/en_us.json::item.irons_spellbooks.scroll` |
| `irons_spellbooks` | `irons_spellbooks:uncommon_ink` | Uncommon Ink | `irons_spellbooks-1.21.1-3.16.3.jar` | `assets/irons_spellbooks/lang/en_us.json::item.irons_spellbooks.uncommon_ink` |
| `irons_spellbooks` | `irons_spellbooks:wizard_boots` | Wizard Boots | `irons_spellbooks-1.21.1-3.16.3.jar` | `assets/irons_spellbooks/models/item/wizard_boots.json; data/irons_spellbooks/recipe/wizard_boots.json` |
| `irons_spellbooks` | `irons_spellbooks:wizard_chestplate` | Wizard Robes | `irons_spellbooks-1.21.1-3.16.3.jar` | `assets/irons_spellbooks/models/item/wizard_chestplate.json; data/irons_spellbooks/recipe/wizard_chestplate.json` |
| `irons_spellbooks` | `irons_spellbooks:wizard_helmet` | Wizard Helmet | `irons_spellbooks-1.21.1-3.16.3.jar` | `assets/irons_spellbooks/models/item/wizard_helmet.json` |
| `irons_spellbooks` | `irons_spellbooks:wizard_leggings` | Wizard Leggings | `irons_spellbooks-1.21.1-3.16.3.jar` | `assets/irons_spellbooks/models/item/wizard_leggings.json; data/irons_spellbooks/recipe/wizard_leggings.json` |
| `numismatics` | `numismatics:banking_guide` | Banking Guide | `CreateNumismatics-1.0.20+neoforge-mc1.21.1.jar` | `assets/numismatics/models/item/banking_guide.json; data/numismatics/recipe/crafting/banking_guide.json` |
| `numismatics` | `numismatics:bevel` | Bevel | `CreateNumismatics-1.0.20+neoforge-mc1.21.1.jar` | `assets/numismatics/lang/en_us.json::item.numismatics.bevel` |
| `numismatics` | `numismatics:cog` | Cog | `CreateNumismatics-1.0.20+neoforge-mc1.21.1.jar` | `assets/numismatics/models/item/cog.json` |
| `numismatics` | `numismatics:sprocket` | Sprocket | `CreateNumismatics-1.0.20+neoforge-mc1.21.1.jar` | `assets/numismatics/models/item/sprocket.json` |
| `supplementaries` | `supplementaries:rope_arrow` | Rope Arrow | `supplementaries-1.21.1-3.9.1-neoforge.jar` | `assets/supplementaries/models/item/rope_arrow.json` |
| `vampirism` | `vampirism:alchemical_cauldron` | Alchemical Cauldron | `Vampirism-1.21-1.10.12.jar` | `assets/vampirism/lang/en_us.json::block.vampirism.alchemical_cauldron` |
| `vampirism` | `vampirism:altar_infusion` | Altar of Infusion | `Vampirism-1.21-1.10.12.jar` | `assets/vampirism/lang/en_us.json::block.vampirism.altar_infusion` |
| `vampirism` | `vampirism:altar_inspiration` | Altar of Inspiration | `Vampirism-1.21-1.10.12.jar` | `assets/vampirism/lang/en_us.json::block.vampirism.altar_inspiration; data/vampirism/recipe/vampire/altar_inspiration.json` |
| `vampirism` | `vampirism:basic_crossbow` | Basic Crossbow | `Vampirism-1.21-1.10.12.jar` | `assets/vampirism/models/item/basic_crossbow.json; data/vampirism/recipe/basic_crossbow.json` |
| `vampirism` | `vampirism:blood_bottle` | Blood Bottle | `Vampirism-1.21-1.10.12.jar` | `assets/vampirism/lang/en_us.json::item.vampirism.blood_bottle` |
| `vampirism` | `vampirism:blood_container` | Blood Container | `Vampirism-1.21-1.10.12.jar` | `assets/vampirism/lang/en_us.json::block.vampirism.blood_container` |
| `vampirism` | `vampirism:blood_infused_enhanced_iron_ingot` | Enhanced Blood-Infused Iron Ingot | `Vampirism-1.21-1.10.12.jar` | `assets/vampirism/lang/en_us.json::item.vampirism.blood_infused_enhanced_iron_ingot; data/vampirism/recipe/vampire/blood_infused_enhanced_iron_ingot.json` |
| `vampirism` | `vampirism:blood_infused_iron_ingot` | Blood-Infused Iron Ingot | `Vampirism-1.21-1.10.12.jar` | `assets/vampirism/lang/en_us.json::item.vampirism.blood_infused_iron_ingot; data/vampirism/recipe/vampire/blood_infused_iron_ingot.json` |
| `vampirism` | `vampirism:blood_pedestal` | Blood Pedestal | `Vampirism-1.21-1.10.12.jar` | `assets/vampirism/lang/en_us.json::block.vampirism.blood_pedestal` |
| `vampirism` | `vampirism:blood_sieve` | Blood Sieve | `Vampirism-1.21-1.10.12.jar` | `assets/vampirism/models/item/blood_sieve.json; data/vampirism/recipe/general/blood_sieve.json` |
| `vampirism` | `vampirism:crossbow_arrow_normal` | Quarrel | `Vampirism-1.21-1.10.12.jar` | `assets/vampirism/models/item/crossbow_arrow_normal.json; data/vampirism/recipe/hunter/crossbow_arrow_normal.json` |
| `vampirism` | `vampirism:crossbow_arrow_spitfire` | Spitfire | `Vampirism-1.21-1.10.12.jar` | `assets/vampirism/lang/en_us.json::item.vampirism.crossbow_arrow_spitfire` |
| `vampirism` | `vampirism:crossbow_arrow_teleport` | Teleport Quarrel | `Vampirism-1.21-1.10.12.jar` | `assets/vampirism/lang/en_us.json::item.vampirism.crossbow_arrow_teleport` |
| `vampirism` | `vampirism:crossbow_arrow_vampire_killer` | Vampire Killer Quarrel | `Vampirism-1.21-1.10.12.jar` | `assets/vampirism/lang/en_us.json::item.vampirism.crossbow_arrow_vampire_killer` |
| `vampirism` | `vampirism:dark_stone_bricks` | Dark Stone Bricks | `Vampirism-1.21-1.10.12.jar` | `assets/vampirism/models/item/dark_stone_bricks.json` |
| `vampirism` | `vampirism:heart_seeker_enhanced` | Enhanced Heartseeker | `Vampirism-1.21-1.10.12.jar` | `data/vampirism/recipe/vampire/heart_seeker_enhanced.json::result.id; de/teamlapen/vampirism/core/ModItems.class::heart_seeker_enhanced` |
| `vampirism` | `vampirism:heart_seeker_normal` | Heart Seeker Normal | `Vampirism-1.21-1.10.12.jar` | `assets/vampirism/models/item/heart_seeker_normal.json; data/vampirism/recipe/vampire/heart_seeker_normal.json` |
| `vampirism` | `vampirism:holy_water_bottle_normal` | Holy Water Bottle Normal | `Vampirism-1.21-1.10.12.jar` | `assets/vampirism/models/item/holy_water_bottle_normal.json` |
| `vampirism` | `vampirism:holy_water_splash_bottle_enhanced` | Enhanced Splash Bottle of Holy Water | `Vampirism-1.21-1.10.12.jar` | `de/teamlapen/vampirism/core/ModItems.class::holy_water_splash_bottle_enhanced; assets/vampirism/models/item/holy_water_splash_bottle_enhanced.json` |
| `vampirism` | `vampirism:hunter_axe_enhanced` | Enhanced Hunter Axe | `Vampirism-1.21-1.10.12.jar` | `data/vampirism/recipe/hunter_axe_enhanced.json::result.id; de/teamlapen/vampirism/core/ModItems.class::hunter_axe_enhanced` |
| `vampirism` | `vampirism:hunter_axe_normal` | Hunter Axe Normal | `Vampirism-1.21-1.10.12.jar` | `assets/vampirism/models/item/hunter_axe_normal.json; data/vampirism/recipe/hunter_axe_normal.json` |
| `vampirism` | `vampirism:hunter_coat_chest_normal` | Hunter Coat Chest Normal | `Vampirism-1.21-1.10.12.jar` | `assets/vampirism/models/item/hunter_coat_chest_normal.json; data/vampirism/recipe/hunter_coat_chest_normal.json` |
| `vampirism` | `vampirism:hunter_coat_feet_normal` | Hunter Coat Feet Normal | `Vampirism-1.21-1.10.12.jar` | `assets/vampirism/models/item/hunter_coat_feet_normal.json; data/vampirism/recipe/hunter_coat_feet_normal.json` |
| `vampirism` | `vampirism:hunter_coat_head_normal` | Hunter Coat Head Normal | `Vampirism-1.21-1.10.12.jar` | `assets/vampirism/models/item/hunter_coat_head_normal.json; data/vampirism/recipe/hunter_coat_head_normal.json` |
| `vampirism` | `vampirism:hunter_coat_legs_normal` | Hunter Coat Legs Normal | `Vampirism-1.21-1.10.12.jar` | `assets/vampirism/models/item/hunter_coat_legs_normal.json; data/vampirism/recipe/hunter_coat_legs_normal.json` |
| `vampirism` | `vampirism:hunter_table` | Hunter Research Table | `Vampirism-1.21-1.10.12.jar` | `assets/vampirism/lang/en_us.json::block.vampirism.hunter_table` |
| `vampirism` | `vampirism:injection_garlic` | Garlic Injection | `Vampirism-1.21-1.10.12.jar` | `assets/vampirism/lang/en_us.json::item.vampirism.injection_garlic; de/teamlapen/vampirism/core/ModItems.class::injection_garlic` |
| `vampirism` | `vampirism:pure_salt` | Pure Salt | `Vampirism-1.21-1.10.12.jar` | `assets/vampirism/lang/en_us.json::item.vampirism.pure_salt` |
| `vampirism` | `vampirism:purified_garlic` | Purified Garlic | `Vampirism-1.21-1.10.12.jar` | `assets/vampirism/models/item/purified_garlic.json; data/vampirism/recipe/purified_garlic.json` |
| `vampirism` | `vampirism:stake` | Stake | `Vampirism-1.21-1.10.12.jar` | `assets/vampirism/lang/en_us.json::item.vampirism.stake` |
| `vampirism` | `vampirism:umbrella` | Umbrella | `Vampirism-1.21-1.10.12.jar` | `assets/vampirism/models/item/umbrella.json; data/vampirism/recipe/general/umbrella.json` |
| `vampirism` | `vampirism:vampire_cloak_white_black` | Vampire Cloak | `Vampirism-1.21-1.10.12.jar` | `assets/vampirism/lang/en_us.json::item.vampirism.vampire_cloak_white_black` |
| `vampirism` | `vampirism:vampire_fang` | Vampire Fang | `Vampirism-1.21-1.10.12.jar` | `assets/vampirism/lang/en_us.json::item.vampirism.vampire_fang` |
| `vampirism` | `vampirism:weapon_table` | Hunter Weapon Table | `Vampirism-1.21-1.10.12.jar` | `assets/vampirism/lang/en_us.json::block.vampirism.weapon_table` |
| `vista` | `vista:hollow_cassette` | Hollow Cassette | `vista-1.21.1-5.4.4-neoforge.jar` | `assets/vista/models/item/hollow_cassette.json; data/vista/recipe/hollow_cassette.json` |
| `vista` | `vista:television` | Television | `vista-1.21.1-5.4.4-neoforge.jar` | `assets/vista/models/item/television.json; data/vista/recipe/television.json` |
| `vista` | `vista:viewfinder` | Viewfinder | `vista-1.21.1-5.4.4-neoforge.jar` | `assets/vista/models/item/viewfinder.json; data/vista/recipe/viewfinder.json` |

## Campaign advancements

| ID | Exact evidence JAR | JAR entry evidence |
| --- | --- | --- |
| `exposure:adventure/moment_in_time` | `exposure-neoforge-1.21.1-1.9.18.jar` | `data/exposure/advancement/adventure/moment_in_time.json` |
| `vampirism:hunter/become_hunter` | `Vampirism-1.21-1.10.12.jar` | `data/vampirism/advancement/hunter/become_hunter.json` |
| `vampirism:vampire/become_vampire` | `Vampirism-1.21-1.10.12.jar` | `data/vampirism/advancement/vampire/become_vampire.json` |

## Campaign spell IDs

| ID | School | Exact evidence JAR | JAR entry evidence |
| --- | --- | --- | --- |
| `irons_spellbooks:blood_slash` | blood | `irons_spellbooks-1.21.1-3.16.3.jar` | `assets/irons_spellbooks/lang/en_us.json::spell.irons_spellbooks.blood_slash; io/redspace/ironsspellbooks/spells/blood/BloodSlashSpell.class` |
| `irons_spellbooks:blood_step` | blood | `irons_spellbooks-1.21.1-3.16.3.jar` | `assets/irons_spellbooks/lang/en_us.json::spell.irons_spellbooks.blood_step; io/redspace/ironsspellbooks/spells/blood/BloodStepSpell.class` |
| `irons_spellbooks:divine_smite` | holy | `irons_spellbooks-1.21.1-3.16.3.jar` | `assets/irons_spellbooks/lang/en_us.json::spell.irons_spellbooks.divine_smite; io/redspace/ironsspellbooks/spells/holy/DivineSmiteSpell.class` |
| `irons_spellbooks:heal` | holy | `irons_spellbooks-1.21.1-3.16.3.jar` | `assets/irons_spellbooks/lang/en_us.json::spell.irons_spellbooks.heal; io/redspace/ironsspellbooks/spells/holy/HealSpell.class` |
| `irons_spellbooks:ray_of_siphoning` | blood | `irons_spellbooks-1.21.1-3.16.3.jar` | `assets/irons_spellbooks/lang/en_us.json::spell.irons_spellbooks.ray_of_siphoning; io/redspace/ironsspellbooks/spells/blood/RayOfSiphoningSpell.class` |
| `irons_spellbooks:recall` | ender | `irons_spellbooks-1.21.1-3.16.3.jar` | `assets/irons_spellbooks/lang/en_us.json::spell.irons_spellbooks.recall; io/redspace/ironsspellbooks/spells/ender/RecallSpell.class` |

## Numismatics denominations

Values were extracted from `dev.ithundxr.createnumismatics.content.backend.Coin` in the exact pinned JAR.

| ID | Spurs | Bevel-equivalent |
| --- | ---: | ---: |
| `numismatics:spur` | 1 | 0.125 |
| `numismatics:bevel` | 8 | 1 |
| `numismatics:sprocket` | 16 | 2 |
| `numismatics:cog` | 64 | 8 |
| `numismatics:crown` | 512 | 64 |
| `numismatics:sun` | 4096 | 512 |

## FTB Quests schema observations

- Installed evidence JAR: `ftb-quests-neoforge-2101.1.33.jar`
- Observed task/reward types: `advancement`, `checkmark`, `choice`, `item`

Vanilla `minecraft:*` IDs are outside this campaign-scoped catalog. Runtime/client checks remain separate from static Packwiz membership and JAR-entry proof.
