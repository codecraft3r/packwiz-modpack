# VvH Current-Pack ID Catalog

This catalog contains only IDs referenced by the live eight-chapter campaign. Every non-vanilla namespace must be backed by a `.pw.toml` that is present in the current `index.toml`, and every evidence JAR must match that metadata's exact filename.

An unrelated downloaded JAR is not proof that a mod is installed. Run `python -B -X utf8 scripts/vvh_sync_catalog.py --check .` before release.

## Pack membership

| Namespace | Indexed metadata | Pinned JAR | Side | Download hash |
| --- | --- | --- | --- | --- |
| `abyssal_decor` | `mods/abyssal-decor.pw.toml` | `abyssal_decor_1.21.1_0.11.0_Neoforge.jar` | `both` | `sha512:58c1f233fb56f3360c772ee77525f23da3877738fe20ebff81f8841de47dd81dda420495e2b03407b5ae9078a2457d4d51b654fe65ccfe61cd97993f6f1e562c` |
| `create` | `mods/create.pw.toml` | `create-1.21.1-6.0.10.jar` | `both` | `sha512:11cc8fc049d2f67f6548c7abfada6b82a3adb5c7ca410a742de04bbca76e03862c518721b88d806f6e6d768a4d68531fdb903a85859b25d1484d550cc7bafd4b` |
| `createbigcannons` | `mods/create-big-cannons.pw.toml` | `createbigcannons-5.11.7+mc.1.21.1.jar` | `both` | `sha512:24f414dfbb973a0f4d9c9b2aa059edc7bed4d23b4f39eb1f7d23a1d6b437e3b5d64cca6e4b85ff7eb2815743fa711d54ad652bffe96d1eb1234544716006440d` |
| `explorerscompass` | `mods/explorers-compass.pw.toml` | `ExplorersCompass-1.21.1-3.4.0-neoforge.jar` | `both` | `sha512:a1b2e385aaacb547763441fc23e9a33a0b1d67bd32094cd605ded3fbdd1c7a0e5fc4520fdfa090c29d2d3384b685e3ead91b32d20030e45632c94145ee3ec668` |
| `exposure` | `mods/exposure.pw.toml` | `exposure-neoforge-1.21.1-1.9.18.jar` | `both` | `sha512:2c0310cfbc9abfcf9e589fdf1079829253e47eb3ac84684a643951ebc432536a4e6f6567a67fc8ba4f4d55036e513804ff0996adee6a8a11cf59c76399de5ef6` |
| `irons_spellbooks` | `mods/irons-spells-n-spellbooks.pw.toml` | `irons_spellbooks-1.21.1-3.16.3.jar` | `both` | `sha512:fd782f98c6c59b193c4832f33775291d2a7e639e1e23dd47510bfb494d99d182bec1253566b9394f96c733a0d0108be34bd729614b82dc29e55e096fdeb96f5b` |
| `mannequins` | `mods/mannequins.pw.toml` | `mannequins-3.0.0-rc.1.jar` | `both` | `sha512:1b844a327605f26a4b87b8b5608c09620354b5d1a8c39573477e374f78f1ee4a27b11be605cf5a2f8d3339a715f2b373afcbba3f725bcf189b8e384f506f16e6` |
| `numismatics` | `mods/numismatics.pw.toml` | `CreateNumismatics-1.0.20+neoforge-mc1.21.1.jar` | `both` | `sha512:2b4ccd516865997735e1a3ec323615bd32d9388e15cc04097ac455f2b453423fccd21969782ecfd031b3de6ed85506ba5349da24c32f5e3eaaf558c5163cf203` |
| `sophisticatedbackpacks` | `mods/sophisticated-backpacks.pw.toml` | `sophisticatedbackpacks-1.21.1-3.25.78.2107.jar` | `both` | `sha512:c2c9bc314068eb4a216dc8cd0826e7763ffa49f948595c9454a42ac80b1d0bd8e83a40752c6ee374ca5cdaafbf34be0577105b77947d7c2e60e1e7695630f7b7` |
| `supplementaries` | `mods/supplementaries.pw.toml` | `supplementaries-1.21.1-3.9.1-neoforge.jar` | `both` | `sha512:b72fad1d77d6d9dd536ce008f23a9014f4d47231ebf5c4e7d5c23156243f5135eacaf34b2d022a028412ffe5e803081b48abdf3ed61951c6930ad463633c9abb` |
| `vampirism` | `mods/vampirism.pw.toml` | `Vampirism-1.21-1.10.12.jar` | `both` | `sha512:b19aec3fb8abb2c83047b64d2497fa440e9295044919b546cfaedd417e604e2176e48c289745ed0a03ec57d032e7051e16de993ef3107d42f5b077187662c070` |
| `vista` | `mods/vista_tv.pw.toml` | `vista-1.21.1-5.4.4-neoforge.jar` | `both` | `sha512:a26106fb220f71a09e5b7817f757952f0b5ff277d2a29cfce07255d307a680bdde8158ccc0ffa9311356e70a125b26ed85216a9418aa195fd47dc48a4b15dd60` |

## Campaign items and icons

| Namespace | ID | Display name | Exact evidence JAR | JAR entry evidence |
| --- | --- | --- | --- | --- |
| `abyssal_decor` | `abyssal_decor:frosted_glass` | Frosted Glass | `abyssal_decor_1.21.1_0.11.0_Neoforge.jar` | `assets/abyssal_decor/models/item/frosted_glass.json` |
| `abyssal_decor` | `abyssal_decor:white_wood_log` | Whitewood Log | `abyssal_decor_1.21.1_0.11.0_Neoforge.jar` | `assets/abyssal_decor/models/item/white_wood_log.json` |
| `create` | `create:andesite_alloy` | Andesite Alloy | `create-1.21.1-6.0.10.jar` | `assets/create/lang/en_us.json::item.create.andesite_alloy` |
| `create` | `create:belt_connector` | Mechanical Belt | `create-1.21.1-6.0.10.jar` | `assets/create/models/item/belt_connector.json; data/create/recipe/crafting/kinetics/belt_connector.json` |
| `create` | `create:brass_ingot` | Brass Ingot | `create-1.21.1-6.0.10.jar` | `assets/create/models/item/brass_ingot.json; data/create/recipe/mixing/brass_ingot.json; data/create/recipe/pressing/brass_ingot.json` |
| `create` | `create:brown_toolbox` | Brown Toolbox | `create-1.21.1-6.0.10.jar` | `assets/create/models/item/brown_toolbox.json; data/create/recipe/crafting/curiosities/brown_toolbox.json` |
| `create` | `create:clipboard` | Clipboard | `create-1.21.1-6.0.10.jar` | `assets/create/models/item/clipboard.json; data/create/recipe/crafting/appliances/clipboard.json` |
| `create` | `create:precision_mechanism` | Precision Mechanism | `create-1.21.1-6.0.10.jar` | `assets/create/lang/en_us.json::item.create.precision_mechanism` |
| `create` | `create:wrench` | Wrench | `create-1.21.1-6.0.10.jar` | `assets/create/models/item/wrench.json; data/create/recipe/crafting/kinetics/wrench.json` |
| `createbigcannons` | `createbigcannons:cannon_carriage` | Cannon Carriage | `createbigcannons-5.11.7+mc.1.21.1.jar` | `assets/createbigcannons/models/item/cannon_carriage.json; data/createbigcannons/recipe/cannon_carriage.json` |
| `createbigcannons` | `createbigcannons:mortar_stone` | Mortar Stone | `createbigcannons-5.11.7+mc.1.21.1.jar` | `assets/createbigcannons/models/item/mortar_stone.json; data/createbigcannons/recipe/mortar_stone.json` |
| `createbigcannons` | `createbigcannons:powder_charge` | Powder Charge | `createbigcannons-5.11.7+mc.1.21.1.jar` | `assets/createbigcannons/models/item/powder_charge.json; data/createbigcannons/recipe/powder_charge.json` |
| `createbigcannons` | `createbigcannons:ram_rod` | Ram Rod | `createbigcannons-5.11.7+mc.1.21.1.jar` | `assets/createbigcannons/models/item/ram_rod.json; data/createbigcannons/recipe/ram_rod.json` |
| `createbigcannons` | `createbigcannons:worm` | Worm | `createbigcannons-5.11.7+mc.1.21.1.jar` | `assets/createbigcannons/models/item/worm.json; data/createbigcannons/recipe/worm.json` |
| `createbigcannons` | `createbigcannons:wrought_iron_cannon_chamber` | Wrought Iron Cannon Chamber | `createbigcannons-5.11.7+mc.1.21.1.jar` | `assets/createbigcannons/models/item/wrought_iron_cannon_chamber.json; data/createbigcannons/recipe/wrought_iron_cannon_chamber.json` |
| `createbigcannons` | `createbigcannons:wrought_iron_cannon_end` | Wrought Iron Cannon End | `createbigcannons-5.11.7+mc.1.21.1.jar` | `assets/createbigcannons/models/item/wrought_iron_cannon_end.json; data/createbigcannons/recipe/wrought_iron_cannon_end.json` |
| `explorerscompass` | `explorerscompass:explorerscompass` | Explorer's Compass | `ExplorersCompass-1.21.1-3.4.0-neoforge.jar` | `assets/explorerscompass/models/item/explorerscompass.json; data/explorerscompass/recipe/explorers_compass.json` |
| `exposure` | `exposure:black_and_white_film` | Black and White Film | `exposure-neoforge-1.21.1-1.9.18.jar` | `assets/exposure/lang/en_us.json::item.exposure.black_and_white_film` |
| `exposure` | `exposure:camera` | Camera | `exposure-neoforge-1.21.1-1.9.18.jar` | `assets/exposure/lang/en_us.json::item.exposure.camera` |
| `exposure` | `exposure:color_film` | Color Film | `exposure-neoforge-1.21.1-1.9.18.jar` | `assets/exposure/lang/en_us.json::item.exposure.color_film` |
| `irons_spellbooks` | `irons_spellbooks:alchemist_cauldron` | Alchemist Cauldron | `irons_spellbooks-1.21.1-3.16.3.jar` | `assets/irons_spellbooks/models/item/alchemist_cauldron.json; data/irons_spellbooks/recipe/alchemist_cauldron.json` |
| `irons_spellbooks` | `irons_spellbooks:arcane_anvil` | Arcane Anvil | `irons_spellbooks-1.21.1-3.16.3.jar` | `assets/irons_spellbooks/models/item/arcane_anvil.json; data/irons_spellbooks/recipe/arcane_anvil.json` |
| `irons_spellbooks` | `irons_spellbooks:arcane_essence` | Arcane Essence | `irons_spellbooks-1.21.1-3.16.3.jar` | `assets/irons_spellbooks/lang/en_us.json::item.irons_spellbooks.arcane_essence` |
| `irons_spellbooks` | `irons_spellbooks:blank_rune` | Blank Runestone | `irons_spellbooks-1.21.1-3.16.3.jar` | `assets/irons_spellbooks/lang/en_us.json::item.irons_spellbooks.blank_rune` |
| `irons_spellbooks` | `irons_spellbooks:blood_rune` | Blood Rune | `irons_spellbooks-1.21.1-3.16.3.jar` | `assets/irons_spellbooks/lang/en_us.json::item.irons_spellbooks.blood_rune` |
| `irons_spellbooks` | `irons_spellbooks:blood_upgrade_orb` | Blood Upgrade Orb | `irons_spellbooks-1.21.1-3.16.3.jar` | `assets/irons_spellbooks/models/item/blood_upgrade_orb.json; data/irons_spellbooks/recipe/blood_upgrade_orb.json` |
| `irons_spellbooks` | `irons_spellbooks:common_ink` | Common Ink | `irons_spellbooks-1.21.1-3.16.3.jar` | `assets/irons_spellbooks/lang/en_us.json::item.irons_spellbooks.common_ink` |
| `irons_spellbooks` | `irons_spellbooks:copper_spell_book` | Flimsy Journal | `irons_spellbooks-1.21.1-3.16.3.jar` | `assets/irons_spellbooks/lang/en_us.json::item.irons_spellbooks.copper_spell_book; data/irons_spellbooks/recipe/copper_spell_book.json` |
| `irons_spellbooks` | `irons_spellbooks:epic_ink` | Epic Ink | `irons_spellbooks-1.21.1-3.16.3.jar` | `assets/irons_spellbooks/models/item/epic_ink.json` |
| `irons_spellbooks` | `irons_spellbooks:gold_spell_book` | Apprentice's Spell Book | `irons_spellbooks-1.21.1-3.16.3.jar` | `assets/irons_spellbooks/models/item/gold_spell_book.json; data/irons_spellbooks/recipe/gold_spell_book.json` |
| `irons_spellbooks` | `irons_spellbooks:holy_rune` | Holy Rune | `irons_spellbooks-1.21.1-3.16.3.jar` | `assets/irons_spellbooks/lang/en_us.json::item.irons_spellbooks.holy_rune` |
| `irons_spellbooks` | `irons_spellbooks:inscription_table` | Inscription Table | `irons_spellbooks-1.21.1-3.16.3.jar` | `assets/irons_spellbooks/lang/en_us.json::block.irons_spellbooks.inscription_table; data/irons_spellbooks/recipe/inscription_table.json` |
| `irons_spellbooks` | `irons_spellbooks:priest_boots` | Priest Boots | `irons_spellbooks-1.21.1-3.16.3.jar` | `assets/irons_spellbooks/models/item/priest_boots.json; data/irons_spellbooks/recipe/priest_boots_crafting.json` |
| `irons_spellbooks` | `irons_spellbooks:priest_chestplate` | Priest Robes | `irons_spellbooks-1.21.1-3.16.3.jar` | `assets/irons_spellbooks/models/item/priest_chestplate.json; data/irons_spellbooks/recipe/priest_chestplate_crafting.json` |
| `irons_spellbooks` | `irons_spellbooks:priest_helmet` | Priest Mask | `irons_spellbooks-1.21.1-3.16.3.jar` | `assets/irons_spellbooks/models/item/priest_helmet.json; data/irons_spellbooks/recipe/priest_helmet_crafting.json` |
| `irons_spellbooks` | `irons_spellbooks:priest_leggings` | Priest Leggings | `irons_spellbooks-1.21.1-3.16.3.jar` | `assets/irons_spellbooks/models/item/priest_leggings.json; data/irons_spellbooks/recipe/priest_leggings_crafting.json` |
| `irons_spellbooks` | `irons_spellbooks:rare_ink` | Rare Ink | `irons_spellbooks-1.21.1-3.16.3.jar` | `assets/irons_spellbooks/models/item/rare_ink.json` |
| `irons_spellbooks` | `irons_spellbooks:scroll` | Scroll | `irons_spellbooks-1.21.1-3.16.3.jar` | `assets/irons_spellbooks/lang/en_us.json::item.irons_spellbooks.scroll` |
| `irons_spellbooks` | `irons_spellbooks:scroll_forge` | Scroll Forge | `irons_spellbooks-1.21.1-3.16.3.jar` | `assets/irons_spellbooks/models/item/scroll_forge.json; data/irons_spellbooks/recipe/scroll_forge.json` |
| `irons_spellbooks` | `irons_spellbooks:uncommon_ink` | Uncommon Ink | `irons_spellbooks-1.21.1-3.16.3.jar` | `assets/irons_spellbooks/lang/en_us.json::item.irons_spellbooks.uncommon_ink` |
| `irons_spellbooks` | `irons_spellbooks:villager_spell_book` | Villager Bible | `irons_spellbooks-1.21.1-3.16.3.jar` | `assets/irons_spellbooks/models/item/villager_spell_book.json` |
| `irons_spellbooks` | `irons_spellbooks:wizard_boots` | Wizard Boots | `irons_spellbooks-1.21.1-3.16.3.jar` | `assets/irons_spellbooks/models/item/wizard_boots.json; data/irons_spellbooks/recipe/wizard_boots.json` |
| `irons_spellbooks` | `irons_spellbooks:wizard_chestplate` | Wizard Robes | `irons_spellbooks-1.21.1-3.16.3.jar` | `assets/irons_spellbooks/models/item/wizard_chestplate.json; data/irons_spellbooks/recipe/wizard_chestplate.json` |
| `irons_spellbooks` | `irons_spellbooks:wizard_helmet` | Wizard Helmet | `irons_spellbooks-1.21.1-3.16.3.jar` | `assets/irons_spellbooks/models/item/wizard_helmet.json` |
| `irons_spellbooks` | `irons_spellbooks:wizard_leggings` | Wizard Leggings | `irons_spellbooks-1.21.1-3.16.3.jar` | `assets/irons_spellbooks/models/item/wizard_leggings.json; data/irons_spellbooks/recipe/wizard_leggings.json` |
| `mannequins` | `mannequins:mannequin` | Mannequin | `mannequins-3.0.0-rc.1.jar` | `assets/mannequins/models/item/mannequin.json; data/mannequins/recipe/mannequin.json` |
| `numismatics` | `numismatics:banking_guide` | Banking Guide | `CreateNumismatics-1.0.20+neoforge-mc1.21.1.jar` | `assets/numismatics/models/item/banking_guide.json; data/numismatics/recipe/crafting/banking_guide.json` |
| `numismatics` | `numismatics:bevel` | Bevel | `CreateNumismatics-1.0.20+neoforge-mc1.21.1.jar` | `assets/numismatics/lang/en_us.json::item.numismatics.bevel` |
| `numismatics` | `numismatics:cog` | Cog | `CreateNumismatics-1.0.20+neoforge-mc1.21.1.jar` | `assets/numismatics/models/item/cog.json` |
| `numismatics` | `numismatics:sprocket` | Sprocket | `CreateNumismatics-1.0.20+neoforge-mc1.21.1.jar` | `assets/numismatics/models/item/sprocket.json` |
| `sophisticatedbackpacks` | `sophisticatedbackpacks:backpack` | Backpack | `sophisticatedbackpacks-1.21.1-3.25.78.2107.jar` | `assets/sophisticatedbackpacks/models/item/backpack.json; data/sophisticatedbackpacks/recipe/backpack.json` |
| `supplementaries` | `supplementaries:bamboo_spikes_tipped` | Tipped Bamboo Spikes | `supplementaries-1.21.1-3.9.1-neoforge.jar` | `assets/supplementaries/models/item/bamboo_spikes_tipped.json; data/supplementaries/recipe/bamboo_spikes_tipped.json` |
| `supplementaries` | `supplementaries:bomb` | Bomb | `supplementaries-1.21.1-3.9.1-neoforge.jar` | `assets/supplementaries/models/item/bomb.json; data/supplementaries/recipe/bomb.json` |
| `supplementaries` | `supplementaries:faucet` | Faucet | `supplementaries-1.21.1-3.9.1-neoforge.jar` | `assets/supplementaries/models/item/faucet.json; data/supplementaries/recipe/faucet.json` |
| `supplementaries` | `supplementaries:jar` | Jar | `supplementaries-1.21.1-3.9.1-neoforge.jar` | `assets/supplementaries/models/item/jar.json; data/supplementaries/recipe/jar.json` |
| `supplementaries` | `supplementaries:rope_arrow` | Rope Arrow | `supplementaries-1.21.1-3.9.1-neoforge.jar` | `assets/supplementaries/models/item/rope_arrow.json` |
| `supplementaries` | `supplementaries:wrench` | Wrench | `supplementaries-1.21.1-3.9.1-neoforge.jar` | `assets/supplementaries/models/item/wrench.json; data/supplementaries/recipe/wrench.json` |
| `vampirism` | `vampirism:alchemical_cauldron` | Alchemical Cauldron | `Vampirism-1.21-1.10.12.jar` | `assets/vampirism/lang/en_us.json::block.vampirism.alchemical_cauldron` |
| `vampirism` | `vampirism:alchemy_table` | Alchemy Table | `Vampirism-1.21-1.10.12.jar` | `assets/vampirism/models/item/alchemy_table.json; data/vampirism/recipe/alchemy_table.json` |
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
| `vampirism` | `vampirism:hunter_axe_normal` | Hunter Axe Normal | `Vampirism-1.21-1.10.12.jar` | `assets/vampirism/models/item/hunter_axe_normal.json; data/vampirism/recipe/hunter_axe_normal.json` |
| `vampirism` | `vampirism:hunter_coat_chest_normal` | Hunter Coat Chest Normal | `Vampirism-1.21-1.10.12.jar` | `assets/vampirism/models/item/hunter_coat_chest_normal.json; data/vampirism/recipe/hunter_coat_chest_normal.json` |
| `vampirism` | `vampirism:hunter_coat_feet_normal` | Hunter Coat Feet Normal | `Vampirism-1.21-1.10.12.jar` | `assets/vampirism/models/item/hunter_coat_feet_normal.json; data/vampirism/recipe/hunter_coat_feet_normal.json` |
| `vampirism` | `vampirism:hunter_coat_head_normal` | Hunter Coat Head Normal | `Vampirism-1.21-1.10.12.jar` | `assets/vampirism/models/item/hunter_coat_head_normal.json; data/vampirism/recipe/hunter_coat_head_normal.json` |
| `vampirism` | `vampirism:hunter_coat_legs_normal` | Hunter Coat Legs Normal | `Vampirism-1.21-1.10.12.jar` | `assets/vampirism/models/item/hunter_coat_legs_normal.json; data/vampirism/recipe/hunter_coat_legs_normal.json` |
| `vampirism` | `vampirism:hunter_table` | Hunter Research Table | `Vampirism-1.21-1.10.12.jar` | `assets/vampirism/lang/en_us.json::block.vampirism.hunter_table` |
| `vampirism` | `vampirism:injection_garlic` | Garlic Injection | `Vampirism-1.21-1.10.12.jar` | `assets/vampirism/lang/en_us.json::item.vampirism.injection_garlic; de/teamlapen/vampirism/core/ModItems.class::injection_garlic` |
| `vampirism` | `vampirism:item_alchemical_fire` | Alchemical Fire | `Vampirism-1.21-1.10.12.jar` | `assets/vampirism/models/item/item_alchemical_fire.json` |
| `vampirism` | `vampirism:potion_table` | Potion table | `Vampirism-1.21-1.10.12.jar` | `assets/vampirism/models/item/potion_table.json; data/vampirism/recipe/hunter/potion_table.json` |
| `vampirism` | `vampirism:pure_salt` | Pure Salt | `Vampirism-1.21-1.10.12.jar` | `assets/vampirism/lang/en_us.json::item.vampirism.pure_salt` |
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
