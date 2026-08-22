from pathlib import Path

ROOT = Path(".")

# 1. chapter_groups.snbt
groups_snbt = """{
\tchapter_groups: [
\t\t{ id: "7A11C0DE00000001", title: "Getting Started & Rules" }
\t\t{ id: "7A11C0DE00000002", title: "Factions & Progression" }
\t]
}
"""
(ROOT / "config/ftbquests/quests/chapter_groups.snbt").write_text(groups_snbt, encoding="utf-8")

# 2. Reward table: 7A11C0DEF0000001.snbt (Vampire Cloaks)
reward_table_snbt = """{
\tid: "7A11C0DEF0000001"
\tloot_size: 1
\torder_index: 0
\trewards: [
\t\t{ item: { count: 1, id: "vampirism:vampire_cloak_red" }, title: "Crimson Vampire Cloak" }
\t\t{ item: { count: 1, id: "vampirism:vampire_cloak_black" }, title: "Obsidian Vampire Cloak" }
\t\t{ item: { count: 1, id: "vampirism:vampire_cloak_white" }, title: "Pure White Vampire Cloak" }
\t\t{ item: { count: 1, id: "vampirism:vampire_cloak_blue" }, title: "Midnight Blue Vampire Cloak" }
\t]
\ttitle: "Vampire Cloak Selection"
}
"""
(ROOT / "config/ftbquests/quests/reward_tables/7A11C0DEF0000001.snbt").write_text(reward_table_snbt, encoding="utf-8")

# 3. Chapter 1: ch01_intro_rules.snbt
ch01_snbt = """{
\tdefault_hide_dependency_lines: false
\tdefault_quest_shape: ""
\tfilename: "ch01_intro_rules"
\tgroup: "7A11C0DE00000001"
\ticon: { id: "minecraft:compass" }
\tid: "7A11C0DE10000000"
\torder_index: 0
\tquest_links: [ ]
\tquests: [
\t\t{
\t\t\tdescription: [
\t\t\t\t"Welcome to the server! This quest book is your guide to getting established, understanding server etiquette, and participating in faction activities."
\t\t\t\t""
\t\t\t\t"Take your initial orientation tools and check out the rules around this chapter before venturing out into the world."
\t\t\t]
\t\t\ticon: { id: "minecraft:compass" }
\t\t\tid: "7A11C0DE10000001"
\t\t\trewards: [
\t\t\t\t{
\t\t\t\t\tid: "7A11C0DE10000011"
\t\t\t\t\titem: { count: 1, id: "minecraft:compass" }
\t\t\t\t\ttype: "item"
\t\t\t\t}
\t\t\t\t{
\t\t\t\t\tid: "7A11C0DE10000012"
\t\t\t\t\titem: { count: 16, id: "minecraft:torch" }
\t\t\t\t\ttype: "item"
\t\t\t\t}
\t\t\t]
\t\t\tshape: "hexagon"
\t\t\tsize: 1.5d
\t\t\tsubtitle: "Orientation, tools, and getting started."
\t\t\ttasks: [
\t\t\t\t{
\t\t\t\t\tid: "7A11C0DE10000021"
\t\t\t\t\ttitle: "I Have Read the Welcome Guide"
\t\t\t\t\ttype: "checkmark"
\t\t\t\t}
\t\t\t]
\t\t\ttitle: "Welcome & Starter Kit"
\t\t\tx: 0.0d
\t\t\ty: -2.0d
\t\t}
\t\t{
\t\t\tdependencies: ["7A11C0DE10000001"]
\t\t\tdescription: [
\t\t\t\t"You can claim chunks in your map interface via FTB Chunks to prevent unauthorized modification and griefing."
\t\t\t\t""
\t\t\t\t"Always build permanent homes and bases on designated permanent land. Respect other players' chunk claims and boundaries."
\t\t\t]
\t\t\ticon: { id: "minecraft:filled_map" }
\t\t\tid: "7A11C0DE10000002"
\t\t\tshape: "diamond"
\t\t\tsubtitle: "Claiming land and protecting your bases."
\t\t\ttasks: [
\t\t\t\t{
\t\t\t\t\tid: "7A11C0DE10000022"
\t\t\t\t\ttitle: "I Understand Land Claims"
\t\t\t\t\ttype: "checkmark"
\t\t\t\t}
\t\t\t]
\t\t\ttitle: "Land Claims & FTB Chunks"
\t\t\tx: -2.5d
\t\t\ty: 0.5d
\t\t}
\t\t{
\t\t\tdependencies: ["7A11C0DE10000001"]
\t\t\tdescription: [
\t\t\t\t"The two active factions are Vampires and Hunters. Creating separate third-party warring factions is discouraged."
\t\t\t\t""
\t\t\t\t"§l§6THE NEUTRAL RULE:§r Neutral players (civilians, traders, farmers) are to be §l§cLEFT COMPLETELY ALONE§r unless they explicitly provoke conflict."
\t\t\t\t""
\t\t\t\t"Rivalry between Vampires and Hunters should be playful, spirited, and non-destructive. No griefing, theft, or irreversible damage."
\t\t\t]
\t\t\ticon: { id: "minecraft:shield" }
\t\t\tid: "7A11C0DE10000003"
\t\t\tshape: "octagon"
\t\t\tsubtitle: "Playful rivalry, non-griefing, and neutral protection."
\t\t\ttasks: [
\t\t\t\t{
\t\t\t\t\tid: "7A11C0DE10000023"
\t\t\t\t\ttitle: "I Accept the Neutral & Conflict Rules"
\t\t\t\t\ttype: "checkmark"
\t\t\t\t}
\t\t\t]
\t\t\ttitle: "Rules of Engagement & Neutrals"
\t\t\tx: 2.5d
\t\t\ty: 0.5d
\t\t}
\t\t{
\t\t\tdependencies: [
\t\t\t\t"7A11C0DE10000002"
\t\t\t\t"7A11C0DE10000003"
\t\t\t]
\t\t\tdescription: [
\t\t\t\t"You can create or join an FTB Team with teammates using the FTB Teams menu to share quest progress and claims."
\t\t\t\t""
\t\t\t\t"The server uses Create: Numismatics currency: Spurs, Bevels, Sprockets, and Cogs. Earn coins by completing substantive quest milestones and trade with other players!"
\t\t\t]
\t\t\ticon: { id: "numismatics:bevel" }
\t\t\tid: "7A11C0DE10000004"
\t\t\trewards: [
\t\t\t\t{
\t\t\t\t\tid: "7A11C0DE10000014"
\t\t\t\t\titem: { count: 4, id: "numismatics:bevel" }
\t\t\t\t\ttype: "item"
\t\t\t\t}
\t\t\t]
\t\t\tshape: "gear"
\t\t\tsubtitle: "Teams, economy, and Numismatics coins."
\t\t\ttasks: [
\t\t\t\t{
\t\t\t\t\tid: "7A11C0DE10000024"
\t\t\t\t\ttitle: "I Understand Teams and Coins"
\t\t\t\t\ttype: "checkmark"
\t\t\t\t}
\t\t\t]
\t\t\ttitle: "FTB Teams & Economy"
\t\t\tx: 0.0d
\t\t\ty: 2.5d
\t\t}
\t]
\ttitle: "01 · Introduction & Rules"
}
"""
(ROOT / "config/ftbquests/quests/chapters/ch01_intro_rules.snbt").write_text(ch01_snbt, encoding="utf-8")

# 4. Chapter 2: ch02_factions.snbt
ch02_snbt = """{
\tdefault_hide_dependency_lines: false
\tdefault_quest_shape: ""
\tfilename: "ch02_factions"
\tgroup: "7A11C0DE00000002"
\ticon: { id: "minecraft:spyglass" }
\tid: "7A11C0DE20000000"
\torder_index: 0
\tquest_links: [ ]
\tquests: [
\t\t{
\t\t\tdescription: [
\t\t\t\t"Three distinct playstyles exist on the server:"
\t\t\t\t""
\t\t\t\t"§4§lVampires:§r Creatures of the night who harness blood mechanics, speed, stealth, and blood arcana."
\t\t\t\t"§b§lHunters:§r Dedicated sentinels who use garlic, stakes, alchemy, and buffed holy arcana."
\t\t\t\t"§a§lNeutrals:§r Peaceful civilians, crafters, and traders who stay out of the conflict."
\t\t\t\t""
\t\t\t\t"Making third-party warring factions is discouraged. Choose your path below!"
\t\t\t]
\t\t\ticon: { id: "minecraft:spyglass" }
\t\t\tid: "7A11C0DE20000001"
\t\t\tshape: "hexagon"
\t\t\tsize: 1.5d
\t\t\tsubtitle: "Vampires, Hunters, or Peaceful Neutrals."
\t\t\ttasks: [
\t\t\t\t{
\t\t\t\t\tid: "7A11C0DE20000021"
\t\t\t\t\ttitle: "I Have Considered My Path"
\t\t\t\t\ttype: "checkmark"
\t\t\t\t}
\t\t\t]
\t\t\ttitle: "Choosing Your Path"
\t\t\tx: 0.0d
\t\t\ty: -3.0d
\t\t}
\t\t{
\t\t\tdependencies: ["7A11C0DE20000001"]
\t\t\tdescription: [
\t\t\t\t"To embrace vampirism, obtain a §cVampire Fang§r from a vampire mob in the dark, infect yourself, and undergo the transformation."
\t\t\t\t""
\t\t\t\t"This unlocks the full Vampire questline, blood storage, gothic architecture, and life-siphoning blood spells."
\t\t\t]
\t\t\ticon: { id: "vampirism:vampire_fang" }
\t\t\tid: "7A11C0DE20000002"
\t\t\trewards: [
\t\t\t\t{
\t\t\t\t\tid: "7A11C0DE20000012"
\t\t\t\t\titem: { count: 8, id: "vampirism:blood_bottle" }
\t\t\t\t\ttype: "item"
\t\t\t\t}
\t\t\t\t{
\t\t\t\t\tid: "7A11C0DE20000013"
\t\t\t\t\titem: { count: 4, id: "numismatics:bevel" }
\t\t\t\t\ttype: "item"
\t\t\t\t}
\t\t\t]
\t\t\tshape: "heart"
\t\t\tsubtitle: "Embrace the blood and stalk the night."
\t\t\ttasks: [
\t\t\t\t{
\t\t\t\t\tid: "7A11C0DE20000022"
\t\t\t\t\titem: { count: 1, id: "vampirism:vampire_fang" }
\t\t\t\t\ttype: "item"
\t\t\t\t}
\t\t\t\t{
\t\t\t\t\tadvancement: "vampirism:vampire/become_vampire"
\t\t\t\t\tcriterion: ""
\t\t\t\t\tid: "7A11C0DE20000023"
\t\t\t\t\ttype: "advancement"
\t\t\t\t}
\t\t\t]
\t\t\ttitle: "Path of Blood (Vampires)"
\t\t\tx: -3.5d
\t\t\ty: 0.0d
\t\t}
\t\t{
\t\t\tdependencies: ["7A11C0DE20000001"]
\t\t\tdescription: [
\t\t\t\t"To join the Hunter Order, find a hunter camp or craft a Garlic Injector to inoculate yourself against the infection."
\t\t\t\t""
\t\t\t\t"This unlocks the Hunter questline, specialized weaponry, alchemy, and buffed holy spells."
\t\t\t]
\t\t\ticon: { id: "vampirism:injection_garlic" }
\t\t\tid: "7A11C0DE20000003"
\t\t\trewards: [
\t\t\t\t{
\t\t\t\t\tid: "7A11C0DE20000015"
\t\t\t\t\titem: { count: 1, id: "vampirism:hunter_axe_normal" }
\t\t\t\t\ttype: "item"
\t\t\t\t}
\t\t\t\t{
\t\t\t\t\tid: "7A11C0DE20000016"
\t\t\t\t\titem: { count: 4, id: "numismatics:bevel" }
\t\t\t\t\ttype: "item"
\t\t\t\t}
\t\t\t]
\t\t\tshape: "diamond"
\t\t\tsubtitle: "Take up the stake and defend the light."
\t\t\ttasks: [
\t\t\t\t{
\t\t\t\t\tid: "7A11C0DE20000025"
\t\t\t\t\titem: { count: 1, id: "vampirism:injection_garlic" }
\t\t\t\t\ttype: "item"
\t\t\t\t}
\t\t\t\t{
\t\t\t\t\tadvancement: "vampirism:hunter/become_hunter"
\t\t\t\t\tcriterion: ""
\t\t\t\t\tid: "7A11C0DE20000026"
\t\t\t\t\ttype: "advancement"
\t\t\t\t}
\t\t\t]
\t\t\ttitle: "Path of the Stake (Hunters)"
\t\t\tx: 3.5d
\t\t\ty: 0.0d
\t\t}
\t\t{
\t\t\tdependencies: ["7A11C0DE20000001"]
\t\t\tdescription: [
\t\t\t\t"If you prefer to focus on building, engineering, farming, or trading without getting involved in the Vampire vs Hunter rivalry, declare your neutrality here."
\t\t\t\t""
\t\t\t\t"Neutrals are protected under server rules from all raids and attacks as long as they do not provoke either faction."
\t\t\t]
\t\t\ticon: { id: "minecraft:iron_chestplate" }
\t\t\tid: "7A11C0DE20000004"
\t\t\trewards: [
\t\t\t\t{
\t\t\t\t\tid: "7A11C0DE20000017"
\t\t\t\t\titem: { count: 1, id: "minecraft:iron_helmet" }
\t\t\t\t\ttype: "item"
\t\t\t\t}
\t\t\t\t{
\t\t\t\t\tid: "7A11C0DE20000018"
\t\t\t\t\titem: { count: 1, id: "minecraft:iron_chestplate" }
\t\t\t\t\ttype: "item"
\t\t\t\t}
\t\t\t\t{
\t\t\t\t\tid: "7A11C0DE20000019"
\t\t\t\t\titem: { count: 1, id: "minecraft:iron_leggings" }
\t\t\t\t\ttype: "item"
\t\t\t\t}
\t\t\t\t{
\t\t\t\t\tid: "7A11C0DE2000001A"
\t\t\t\t\titem: { count: 1, id: "minecraft:iron_boots" }
\t\t\t\t\ttype: "item"
\t\t\t\t}
\t\t\t\t{
\t\t\t\t\tid: "7A11C0DE2000001B"
\t\t\t\t\titem: { count: 1, id: "minecraft:iron_sword" }
\t\t\t\t\ttype: "item"
\t\t\t\t}
\t\t\t\t{
\t\t\t\t\tid: "7A11C0DE2000001C"
\t\t\t\t\titem: { count: 1, id: "minecraft:iron_pickaxe" }
\t\t\t\t\ttype: "item"
\t\t\t\t}
\t\t\t\t{
\t\t\t\t\tid: "7A11C0DE2000001D"
\t\t\t\t\titem: { count: 1, id: "minecraft:iron_axe" }
\t\t\t\t\ttype: "item"
\t\t\t\t}
\t\t\t\t{
\t\t\t\t\tid: "7A11C0DE2000001E"
\t\t\t\t\titem: { count: 1, id: "minecraft:iron_shovel" }
\t\t\t\t\ttype: "item"
\t\t\t\t}
\t\t\t\t{
\t\t\t\t\tid: "7A11C0DE2000001F"
\t\t\t\t\titem: { count: 1, id: "minecraft:white_bed" }
\t\t\t\t\ttype: "item"
\t\t\t\t}
\t\t\t\t{
\t\t\t\t\tid: "7A11C0DE20000020"
\t\t\t\t\titem: { count: 32, id: "minecraft:cooked_beef" }
\t\t\t\t\ttype: "item"
\t\t\t\t}
\t\t\t\t{
\t\t\t\t\tid: "7A11C0DE20000027"
\t\t\t\t\titem: { count: 8, id: "numismatics:bevel" }
\t\t\t\t\ttype: "item"
\t\t\t\t}
\t\t\t]
\t\t\tshape: "square"
\t\t\tsubtitle: "Civilian life, crafting, and protected neutrality."
\t\t\ttasks: [
\t\t\t\t{
\t\t\t\t\tid: "7A11C0DE20000028"
\t\t\t\t\ttitle: "I Choose Peaceful Neutrality"
\t\t\t\t\ttype: "checkmark"
\t\t\t\t}
\t\t\t]
\t\t\ttitle: "Choosing Neutrality"
\t\t\tx: 0.0d
\t\t\ty: 1.5d
\t\t}
\t]
\ttitle: "02 · Choosing Your Path"
}
"""
(ROOT / "config/ftbquests/quests/chapters/ch02_factions.snbt").write_text(ch02_snbt, encoding="utf-8")

# 5. Chapter 3: ch03_hunters.snbt
ch03_snbt = """{
\tdefault_hide_dependency_lines: false
\tdefault_quest_shape: ""
\tfilename: "ch03_hunters"
\tgroup: "7A11C0DE00000002"
\ticon: { id: "vampirism:hunter_table" }
\tid: "7A11C0DE30000000"
\torder_index: 1
\tquest_links: [ ]
\tquests: [
\t\t{
\t\t\tdescription: [
\t\t\t\t"Craft a Hunter Table to access specialized hunter gear, stakes, and upgrades."
\t\t\t\t""
\t\t\t\t"Wooden stakes allow you to finish off downed vampires before they can regenerate."
\t\t\t]
\t\t\ticon: { id: "vampirism:hunter_table" }
\t\t\tid: "7A11C0DE30000001"
\t\t\trewards: [
\t\t\t\t{
\t\t\t\t\tid: "7A11C0DE30000011"
\t\t\t\t\titem: { count: 1, id: "vampirism:hunter_hat_normal" }
\t\t\t\t\ttype: "item"
\t\t\t\t}
\t\t\t\t{
\t\t\t\t\tid: "7A11C0DE30000012"
\t\t\t\t\titem: { count: 1, id: "vampirism:hunter_coat_normal" }
\t\t\t\t\ttype: "item"
\t\t\t\t}
\t\t\t\t{
\t\t\t\t\tid: "7A11C0DE30000013"
\t\t\t\t\titem: { count: 1, id: "vampirism:hunter_leggings_normal" }
\t\t\t\t\ttype: "item"
\t\t\t\t}
\t\t\t\t{
\t\t\t\t\tid: "7A11C0DE30000014"
\t\t\t\t\titem: { count: 1, id: "vampirism:hunter_boots_normal" }
\t\t\t\t\ttype: "item"
\t\t\t\t}
\t\t\t\t{
\t\t\t\t\tid: "7A11C0DE30000015"
\t\t\t\t\titem: { count: 32, id: "minecraft:iron_ingot" }
\t\t\t\t\ttype: "item"
\t\t\t\t}
\t\t\t\t{
\t\t\t\t\tid: "7A11C0DE30000016"
\t\t\t\t\titem: { count: 4, id: "numismatics:bevel" }
\t\t\t\t\ttype: "item"
\t\t\t\t}
\t\t\t]
\t\t\tshape: "hexagon"
\t\t\tsize: 1.5d
\t\t\tsubtitle: "Hunter Table, stakes, and equipment."
\t\t\ttasks: [
\t\t\t\t{
\t\t\t\t\tid: "7A11C0DE30000021"
\t\t\t\t\titem: { count: 1, id: "vampirism:hunter_table" }
\t\t\t\t\ttype: "item"
\t\t\t\t}
\t\t\t\t{
\t\t\t\t\tid: "7A11C0DE30000022"
\t\t\t\t\titem: { count: 4, id: "vampirism:stake" }
\t\t\t\t\ttype: "item"
\t\t\t\t}
\t\t\t]
\t\t\ttitle: "Hunter Armory & Stakes"
\t\t\tx: 0.0d
\t\t\ty: -4.0d
\t\t}
\t\t{
\t\t\tdependencies: ["7A11C0DE30000001"]
\t\t\tdescription: [
\t\t\t\t"Hunters need secure, well-fortified outposts and watchtowers."
\t\t\t\t""
\t\t\t\t"Gather a starter bundle of fortified building materials: Stone Bricks, Logs, Iron Bars, and Lanterns. Completing this grants double building materials plus valuable crafting supplies so you can build a proper outpost!"
\t\t\t]
\t\t\ticon: { id: "minecraft:stone_bricks" }
\t\t\tid: "7A11C0DE30000002"
\t\t\trewards: [
\t\t\t\t{
\t\t\t\t\tid: "7A11C0DE30000031"
\t\t\t\t\titem: { count: 128, id: "minecraft:stone_bricks" }
\t\t\t\t\ttype: "item"
\t\t\t\t}
\t\t\t\t{
\t\t\t\t\tid: "7A11C0DE30000032"
\t\t\t\t\titem: { count: 64, id: "minecraft:oak_log" }
\t\t\t\t\ttype: "item"
\t\t\t\t}
\t\t\t\t{
\t\t\t\t\tid: "7A11C0DE30000033"
\t\t\t\t\titem: { count: 32, id: "minecraft:iron_bars" }
\t\t\t\t\ttype: "item"
\t\t\t\t}
\t\t\t\t{
\t\t\t\t\tid: "7A11C0DE30000034"
\t\t\t\t\titem: { count: 16, id: "minecraft:lantern" }
\t\t\t\t\ttype: "item"
\t\t\t\t}
\t\t\t\t{
\t\t\t\t\tid: "7A11C0DE30000035"
\t\t\t\t\titem: { count: 1, id: "minecraft:stonecutter" }
\t\t\t\t\ttype: "item"
\t\t\t\t}
\t\t\t\t{
\t\t\t\t\tid: "7A11C0DE30000036"
\t\t\t\t\titem: { count: 16, id: "minecraft:diamond" }
\t\t\t\t\ttype: "item"
\t\t\t\t}
\t\t\t\t{
\t\t\t\t\tid: "7A11C0DE30000037"
\t\t\t\t\titem: { count: 64, id: "minecraft:iron_ingot" }
\t\t\t\t\ttype: "item"
\t\t\t\t}
\t\t\t\t{
\t\t\t\t\tid: "7A11C0DE30000038"
\t\t\t\t\titem: { count: 64, id: "create:andesite_alloy" }
\t\t\t\t\ttype: "item"
\t\t\t\t}
\t\t\t]
\t\t\tshape: "square"
\t\t\tsubtitle: "Gather watchpost materials for generous building rewards."
\t\t\ttasks: [
\t\t\t\t{
\t\t\t\t\tid: "7A11C0DE30000041"
\t\t\t\t\titem: { count: 64, id: "minecraft:stone_bricks" }
\t\t\t\t\ttype: "item"
\t\t\t\t}
\t\t\t\t{
\t\t\t\t\tid: "7A11C0DE30000042"
\t\t\t\t\titem: { count: 32, id: "minecraft:oak_log" }
\t\t\t\t\ttype: "item"
\t\t\t\t}
\t\t\t\t{
\t\t\t\t\tid: "7A11C0DE30000043"
\t\t\t\t\titem: { count: 16, id: "minecraft:iron_bars" }
\t\t\t\t\ttype: "item"
\t\t\t\t}
\t\t\t\t{
\t\t\t\t\tid: "7A11C0DE30000044"
\t\t\t\t\titem: { count: 8, id: "minecraft:lantern" }
\t\t\t\t\ttype: "item"
\t\t\t\t}
\t\t\t]
\t\t\ttitle: "Fortified Outpost Construction"
\t\t\tx: -2.5d
\t\t\ty: -1.5d
\t\t}
\t\t{
\t\t\tdependencies: ["7A11C0DE30000001"]
\t\t\tdescription: [
\t\t\t\t"Craft an Alchemical Cauldron and brew Holy Water. Holy Water is an essential throwing weapon and cleansing agent against vampires."
\t\t\t]
\t\t\ticon: { id: "vampirism:alchemical_cauldron" }
\t\t\tid: "7A11C0DE30000003"
\t\t\trewards: [
\t\t\t\t{
\t\t\t\t\tid: "7A11C0DE30000051"
\t\t\t\t\titem: { count: 1, id: "minecraft:brewing_stand" }
\t\t\t\t\ttype: "item"
\t\t\t\t}
\t\t\t\t{
\t\t\t\t\tid: "7A11C0DE30000052"
\t\t\t\t\titem: { count: 16, id: "minecraft:glass_bottle" }
\t\t\t\t\ttype: "item"
\t\t\t\t}
\t\t\t\t{
\t\t\t\t\tid: "7A11C0DE30000053"
\t\t\t\t\titem: { count: 16, id: "minecraft:blaze_powder" }
\t\t\t\t\ttype: "item"
\t\t\t\t}
\t\t\t\t{
\t\t\t\t\tid: "7A11C0DE30000054"
\t\t\t\t\titem: { count: 16, id: "minecraft:nether_wart" }
\t\t\t\t\ttype: "item"
\t\t\t\t}
\t\t\t\t{
\t\t\t\t\tid: "7A11C0DE30000055"
\t\t\t\t\titem: { count: 8, id: "minecraft:glistering_melon_slice" }
\t\t\t\t\ttype: "item"
\t\t\t\t}
\t\t\t\t{
\t\t\t\t\tid: "7A11C0DE30000056"
\t\t\t\t\titem: { count: 8, id: "minecraft:golden_carrot" }
\t\t\t\t\ttype: "item"
\t\t\t\t}
\t\t\t\t{
\t\t\t\t\tid: "7A11C0DE30000057"
\t\t\t\t\titem: { count: 2, id: "numismatics:sprocket" }
\t\t\t\t\ttype: "item"
\t\t\t\t}
\t\t\t]
\t\t\tshape: "diamond"
\t\t\tsubtitle: "Cauldrons, brewing, and holy water."
\t\t\ttasks: [
\t\t\t\t{
\t\t\t\t\tid: "7A11C0DE30000061"
\t\t\t\t\titem: { count: 1, id: "vampirism:alchemical_cauldron" }
\t\t\t\t\ttype: "item"
\t\t\t\t}
\t\t\t\t{
\t\t\t\t\tid: "7A11C0DE30000062"
\t\t\t\t\titem: { count: 1, id: "vampirism:holy_water_bottle_normal" }
\t\t\t\t\ttype: "item"
\t\t\t\t}
\t\t\t]
\t\t\ttitle: "Alchemical Countermeasures"
\t\t\tx: 2.5d
\t\t\ty: -1.5d
\t\t}
\t\t{
\t\t\tdependencies: ["7A11C0DE30000003"]
\t\t\tdescription: [
\t\t\t\t"Craft an Inscription Table and a Copper Spell Book to begin learning magic."
\t\t\t\t""
\t\t\t\t"§6§lHunters receive a natural buff to Holy Magic!§r Use your holy runes and inks to craft Priest armor and inscribe healing and smiting spells."
\t\t\t]
\t\t\ticon: { id: "irons_spellbooks:copper_spell_book" }
\t\t\tid: "7A11C0DE30000004"
\t\t\trewards: [
\t\t\t\t{
\t\t\t\t\tid: "7A11C0DE30000071"
\t\t\t\t\titem: { count: 4, id: "irons_spellbooks:holy_rune" }
\t\t\t\t\ttype: "item"
\t\t\t\t}
\t\t\t\t{
\t\t\t\t\tid: "7A11C0DE30000072"
\t\t\t\t\titem: { count: 16, id: "irons_spellbooks:rare_ink" }
\t\t\t\t\ttype: "item"
\t\t\t\t}
\t\t\t\t{
\t\t\t\t\tid: "7A11C0DE30000073"
\t\t\t\t\titem: { count: 4, id: "irons_spellbooks:epic_ink" }
\t\t\t\t\ttype: "item"
\t\t\t\t}
\t\t\t\t{
\t\t\t\t\tid: "7A11C0DE30000074"
\t\t\t\t\titem: {
\t\t\t\t\t\tcomponents: {
\t\t\t\t\t\t\t"irons_spellbooks:spell_container": {
\t\t\t\t\t\t\t\tdata: [
\t\t\t\t\t\t\t\t\t{
\t\t\t\t\t\t\t\t\t\tid: "irons_spellbooks:heal"
\t\t\t\t\t\t\t\t\t\tlevel: 1
\t\t\t\t\t\t\t\t\t}
\t\t\t\t\t\t\t\t]
\t\t\t\t\t\t\t}
\t\t\t\t\t\t}
\t\t\t\t\t\tcount: 1
\t\t\t\t\t\tid: "irons_spellbooks:scroll"
\t\t\t\t\t}
\t\t\t\t\ttitle: "Scroll of Heal"
\t\t\t\t\ttype: "item"
\t\t\t\t}
\t\t\t\t{
\t\t\t\t\tid: "7A11C0DE30000075"
\t\t\t\t\titem: {
\t\t\t\t\t\tcomponents: {
\t\t\t\t\t\t\t"irons_spellbooks:spell_container": {
\t\t\t\t\t\t\t\tdata: [
\t\t\t\t\t\t\t\t\t{
\t\t\t\t\t\t\t\t\t\tid: "irons_spellbooks:smite"
\t\t\t\t\t\t\t\t\t\tlevel: 1
\t\t\t\t\t\t\t\t\t}
\t\t\t\t\t\t\t\t]
\t\t\t\t\t\t\t}
\t\t\t\t\t\t}
\t\t\t\t\t\tcount: 1
\t\t\t\t\t\tid: "irons_spellbooks:scroll"
\t\t\t\t\t}
\t\t\t\t\ttitle: "Scroll of Smite"
\t\t\t\t\ttype: "item"
\t\t\t\t}
\t\t\t\t{
\t\t\t\t\tid: "7A11C0DE30000076"
\t\t\t\t\titem: {
\t\t\t\t\t\tcomponents: {
\t\t\t\t\t\t\t"irons_spellbooks:spell_container": {
\t\t\t\t\t\t\t\tdata: [
\t\t\t\t\t\t\t\t\t{
\t\t\t\t\t\t\t\t\t\tid: "irons_spellbooks:blessing_of_life"
\t\t\t\t\t\t\t\t\t\tlevel: 1
\t\t\t\t\t\t\t\t\t}
\t\t\t\t\t\t\t\t]
\t\t\t\t\t\t\t}
\t\t\t\t\t\t}
\t\t\t\t\t\tcount: 1
\t\t\t\t\t\tid: "irons_spellbooks:scroll"
\t\t\t\t\t}
\t\t\t\t\ttitle: "Scroll of Blessing of Life"
\t\t\t\t\ttype: "item"
\t\t\t\t}
\t\t\t\t{
\t\t\t\t\tid: "7A11C0DE30000077"
\t\t\t\t\titem: {
\t\t\t\t\t\tcomponents: {
\t\t\t\t\t\t\t"irons_spellbooks:spell_container": {
\t\t\t\t\t\t\t\tdata: [
\t\t\t\t\t\t\t\t\t{
\t\t\t\t\t\t\t\t\t\tid: "irons_spellbooks:recall"
\t\t\t\t\t\t\t\t\t\tlevel: 1
\t\t\t\t\t\t\t\t\t}
\t\t\t\t\t\t\t\t]
\t\t\t\t\t\t\t}
\t\t\t\t\t\t}
\t\t\t\t\t\tcount: 1
\t\t\t\t\t\tid: "irons_spellbooks:scroll"
\t\t\t\t\t}
\t\t\t\t\ttitle: "Scroll of Recall"
\t\t\t\t\ttype: "item"
\t\t\t\t}
\t\t\t\t{
\t\t\t\t\tid: "7A11C0DE30000078"
\t\t\t\t\titem: {
\t\t\t\t\t\tcomponents: {
\t\t\t\t\t\t\t"irons_spellbooks:spell_container": {
\t\t\t\t\t\t\t\tdata: [
\t\t\t\t\t\t\t\t\t{
\t\t\t\t\t\t\t\t\t\tid: "irons_spellbooks:spectral_hammer"
\t\t\t\t\t\t\t\t\t\tlevel: 1
\t\t\t\t\t\t\t\t\t}
\t\t\t\t\t\t\t\t]
\t\t\t\t\t\t\t}
\t\t\t\t\t\t}
\t\t\t\t\t\tcount: 1
\t\t\t\t\t\tid: "irons_spellbooks:scroll"
\t\t\t\t\t}
\t\t\t\t\ttitle: "Scroll of Spectral Hammer"
\t\t\t\t\ttype: "item"
\t\t\t\t}
\t\t\t]
\t\t\tshape: "gear"
\t\t\tsubtitle: "Inscribe holy magic and utility spells."
\t\t\ttasks: [
\t\t\t\t{
\t\t\t\t\tid: "7A11C0DE30000081"
\t\t\t\t\titem: { count: 1, id: "irons_spellbooks:copper_spell_book" }
\t\t\t\t\ttype: "item"
\t\t\t\t}
\t\t\t\t{
\t\t\t\t\tid: "7A11C0DE30000082"
\t\t\t\t\titem: { count: 1, id: "irons_spellbooks:inscription_table" }
\t\t\t\t\ttype: "item"
\t\t\t\t}
\t\t\t]
\t\t\ttitle: "Holy Arcana & Inscription"
\t\t\tx: 2.5d
\t\t\ty: 1.5d
\t\t}
\t\t{
\t\t\tdependencies: ["7A11C0DE30000002"]
\t\t\tdescription: [
\t\t\t\t"Equip yourself for long-range patrols and field reconnaissance."
\t\t\t\t""
\t\t\t\t"A Spyglass helps spot vampire movement from watchtowers, while a Crossbow and a Backpack keep your expedition supplied."
\t\t\t]
\t\t\ticon: { id: "minecraft:spyglass" }
\t\t\tid: "7A11C0DE30000005"
\t\t\trewards: [
\t\t\t\t{
\t\t\t\t\tid: "7A11C0DE30000091"
\t\t\t\t\titem: { count: 64, id: "minecraft:arrow" }
\t\t\t\t\ttype: "item"
\t\t\t\t}
\t\t\t\t{
\t\t\t\t\tid: "7A11C0DE30000092"
\t\t\t\t\titem: { count: 16, id: "vampirism:arrow_garlic" }
\t\t\t\t\ttype: "item"
\t\t\t\t}
\t\t\t\t{
\t\t\t\t\tid: "7A11C0DE30000093"
\t\t\t\t\titem: { count: 1, id: "sophisticatedbackpacks:iron_backpack" }
\t\t\t\t\ttype: "item"
\t\t\t\t}
\t\t\t\t{
\t\t\t\t\tid: "7A11C0DE30000094"
\t\t\t\t\titem: { count: 2, id: "numismatics:sprocket" }
\t\t\t\t\ttype: "item"
\t\t\t\t}
\t\t\t]
\t\t\tshape: "diamond"
\t\t\tsubtitle: "Crossbows, spyglasses, and expedition packs."
\t\t\ttasks: [
\t\t\t\t{
\t\t\t\t\tid: "7A11C0DE300000A1"
\t\t\t\t\titem: { count: 1, id: "minecraft:spyglass" }
\t\t\t\t\ttype: "item"
\t\t\t\t}
\t\t\t\t{
\t\t\t\t\tid: "7A11C0DE300000A2"
\t\t\t\t\titem: { count: 1, id: "minecraft:crossbow" }
\t\t\t\t\ttype: "item"
\t\t\t\t}
\t\t\t\t{
\t\t\t\t\tid: "7A11C0DE300000A3"
\t\t\t\t\titem: { count: 1, id: "sophisticatedbackpacks:backpack" }
\t\t\t\t\ttype: "item"
\t\t\t\t}
\t\t\t]
\t\t\ttitle: "Hunter Scouting & Expeditions"
\t\t\tx: -2.5d
\t\t\ty: 1.5d
\t\t}
\t\t{
\t\t\tdependencies: [
\t\t\t\t"7A11C0DE30000004"
\t\t\t\t"7A11C0DE30000005"
\t\t\t]
\t\t\tdescription: [
\t\t\t\t"Use Exposure to craft a camera and black & white film."
\t\t\t\t""
\t\t\t\t"Take reconnaissance photos of vampire strongholds or snap dramatic propaganda photos for the Order to display in your watchpost!"
\t\t\t]
\t\t\ticon: { id: "exposure:camera" }
\t\t\tid: "7A11C0DE30000006"
\t\t\trewards: [
\t\t\t\t{
\t\t\t\t\tid: "7A11C0DE300000B1"
\t\t\t\t\titem: { count: 2, id: "exposure:color_film" }
\t\t\t\t\ttype: "item"
\t\t\t\t}
\t\t\t\t{
\t\t\t\t\tid: "7A11C0DE300000B2"
\t\t\t\t\titem: { count: 2, id: "exposure:black_and_white_film" }
\t\t\t\t\ttype: "item"
\t\t\t\t}
\t\t\t\t{
\t\t\t\t\tid: "7A11C0DE300000B3"
\t\t\t\t\titem: { count: 1, id: "exposure:album" }
\t\t\t\t\ttype: "item"
\t\t\t\t}
\t\t\t\t{
\t\t\t\t\tid: "7A11C0DE300000B4"
\t\t\t\t\titem: { count: 2, id: "numismatics:sprocket" }
\t\t\t\t\ttype: "item"
\t\t\t\t}
\t\t\t]
\t\t\tshape: "gear"
\t\t\tsize: 1.3d
\t\t\tsubtitle: "Capture reconnaissance and propaganda photos."
\t\t\ttasks: [
\t\t\t\t{
\t\t\t\t\tid: "7A11C0DE300000C1"
\t\t\t\t\titem: { count: 1, id: "exposure:camera" }
\t\t\t\t\ttype: "item"
\t\t\t\t}
\t\t\t\t{
\t\t\t\t\tid: "7A11C0DE300000C2"
\t\t\t\t\titem: { count: 1, id: "exposure:black_and_white_film" }
\t\t\t\t\ttype: "item"
\t\t\t\t}
\t\t\t]
\t\t\ttitle: "Reconnaissance & Propaganda"
\t\t\tx: 0.0d
\t\t\ty: 3.5d
\t\t}
\t]
\ttitle: "03 · The Hunter Order"
}
"""
(ROOT / "config/ftbquests/quests/chapters/ch03_hunters.snbt").write_text(ch03_snbt, encoding="utf-8")

# 6. Chapter 4: ch04_vampires.snbt
ch04_snbt = """{
\tdefault_hide_dependency_lines: false
\tdefault_quest_shape: ""
\tfilename: "ch04_vampires"
\tgroup: "7A11C0DE00000002"
\ticon: { id: "vampirism:coffin_red" }
\tid: "7A11C0DE40000000"
\torder_index: 2
\tquest_links: [ ]
\tquests: [
\t\t{
\t\t\tdescription: [
\t\t\t\t"Craft a Coffin to safely sleep through the lethal daylight and gather blood bottles to stay fed."
\t\t\t\t""
\t\t\t\t"Completing this awards a Vampire Knowledge Book, a Vampire Cloak, and materials to forge blood weapons!"
\t\t\t]
\t\t\ticon: { id: "vampirism:coffin_red" }
\t\t\tid: "7A11C0DE40000001"
\t\t\trewards: [
\t\t\t\t{
\t\t\t\t\tid: "7A11C0DE40000011"
\t\t\t\t\titem: { count: 1, id: "vampirism:vampire_book" }
\t\t\t\t\ttype: "item"
\t\t\t\t}
\t\t\t\t{
\t\t\t\t\tid: "7A11C0DE40000012"
\t\t\t\t\ttable_id: "7A11C0DEF0000001"
\t\t\t\t\ttype: "choice"
\t\t\t\t}
\t\t\t\t{
\t\t\t\t\tid: "7A11C0DE40000013"
\t\t\t\t\titem: { count: 2, id: "vampirism:blood_infused_iron_ingot" }
\t\t\t\t\ttype: "item"
\t\t\t\t}
\t\t\t\t{
\t\t\t\t\tid: "7A11C0DE40000014"
\t\t\t\t\titem: { count: 2, id: "minecraft:iron_block" }
\t\t\t\t\ttype: "item"
\t\t\t\t}
\t\t\t\t{
\t\t\t\t\tid: "7A11C0DE40000015"
\t\t\t\t\titem: { count: 1, id: "numismatics:sprocket" }
\t\t\t\t\ttype: "item"
\t\t\t\t}
\t\t\t]
\t\t\tshape: "hexagon"
\t\t\tsize: 1.5d
\t\t\tsubtitle: "Coffins, blood, and the vampire tome."
\t\t\ttasks: [
\t\t\t\t{
\t\t\t\t\tid: "7A11C0DE40000021"
\t\t\t\t\titem: { count: 1, id: "vampirism:coffin_red" }
\t\t\t\t\ttype: "item"
\t\t\t\t}
\t\t\t\t{
\t\t\t\t\tid: "7A11C0DE40000022"
\t\t\t\t\titem: { count: 4, id: "vampirism:blood_bottle" }
\t\t\t\t\ttype: "item"
\t\t\t\t}
\t\t\t]
\t\t\ttitle: "Coffins & Night Survival"
\t\t\tx: 0.0d
\t\t\ty: -4.0d
\t\t}
\t\t{
\t\t\tdependencies: ["7A11C0DE40000001"]
\t\t\tdescription: [
\t\t\t\t"Vampires thrive in gothic manors, crypts, and shadowed castles."
\t\t\t\t""
\t\t\t\t"Gather a starter bundle of gothic building materials: Deepslate Bricks, Dark Oak Wood, Fences, and Lanterns. Completing this rewards tripled building stock, obsidian for a full portal, and diamonds!"
\t\t\t]
\t\t\ticon: { id: "minecraft:deepslate_bricks" }
\t\t\tid: "7A11C0DE40000002"
\t\t\trewards: [
\t\t\t\t{
\t\t\t\t\tid: "7A11C0DE40000031"
\t\t\t\t\titem: { count: 192, id: "minecraft:deepslate_bricks" }
\t\t\t\t\ttype: "item"
\t\t\t\t}
\t\t\t\t{
\t\t\t\t\tid: "7A11C0DE40000032"
\t\t\t\t\titem: { count: 96, id: "minecraft:dark_oak_planks" }
\t\t\t\t\ttype: "item"
\t\t\t\t}
\t\t\t\t{
\t\t\t\t\tid: "7A11C0DE40000033"
\t\t\t\t\titem: { count: 48, id: "minecraft:dark_oak_fence" }
\t\t\t\t\ttype: "item"
\t\t\t\t}
\t\t\t\t{
\t\t\t\t\tid: "7A11C0DE40000034"
\t\t\t\t\titem: { count: 16, id: "minecraft:lantern" }
\t\t\t\t\ttype: "item"
\t\t\t\t}
\t\t\t\t{
\t\t\t\t\tid: "7A11C0DE40000035"
\t\t\t\t\titem: { count: 32, id: "minecraft:torch" }
\t\t\t\t\ttype: "item"
\t\t\t\t}
\t\t\t\t{
\t\t\t\t\tid: "7A11C0DE40000036"
\t\t\t\t\titem: { count: 1, id: "minecraft:stonecutter" }
\t\t\t\t\ttype: "item"
\t\t\t\t}
\t\t\t\t{
\t\t\t\t\tid: "7A11C0DE40000037"
\t\t\t\t\titem: { count: 16, id: "minecraft:diamond" }
\t\t\t\t\ttype: "item"
\t\t\t\t}
\t\t\t\t{
\t\t\t\t\tid: "7A11C0DE40000038"
\t\t\t\t\titem: { count: 64, id: "minecraft:iron_ingot" }
\t\t\t\t\ttype: "item"
\t\t\t\t}
\t\t\t\t{
\t\t\t\t\tid: "7A11C0DE40000039"
\t\t\t\t\titem: { count: 16, id: "minecraft:obsidian" }
\t\t\t\t\ttype: "item"
\t\t\t\t}
\t\t\t]
\t\t\tshape: "square"
\t\t\tsubtitle: "Gather gothic materials for abundant building rewards."
\t\t\ttasks: [
\t\t\t\t{
\t\t\t\t\tid: "7A11C0DE40000041"
\t\t\t\t\titem: { count: 64, id: "minecraft:deepslate_bricks" }
\t\t\t\t\ttype: "item"
\t\t\t\t}
\t\t\t\t{
\t\t\t\t\tid: "7A11C0DE40000042"
\t\t\t\t\titem: { count: 32, id: "minecraft:dark_oak_log" }
\t\t\t\t\ttype: "item"
\t\t\t\t}
\t\t\t\t{
\t\t\t\t\tid: "7A11C0DE40000043"
\t\t\t\t\titem: { count: 16, id: "minecraft:dark_oak_fence" }
\t\t\t\t\ttype: "item"
\t\t\t\t}
\t\t\t\t{
\t\t\t\t\tid: "7A11C0DE40000044"
\t\t\t\t\titem: { count: 8, id: "minecraft:lantern" }
\t\t\t\t\ttype: "item"
\t\t\t\t}
\t\t\t]
\t\t\ttitle: "Gothic Manor & Castle Construction"
\t\t\tx: -2.5d
\t\t\ty: -1.5d
\t\t}
\t\t{
\t\t\tdependencies: ["7A11C0DE40000001"]
\t\t\tdescription: [
\t\t\t\t"Acquire an Altar of Inspiration to advance your vampire level, and a Blood Container to store liquid blood."
\t\t\t\t""
\t\t\t\t"Completing this provides leads, walls, fences, and gates to build a livestock pen for a sustainable blood supply!"
\t\t\t]
\t\t\ticon: { id: "vampirism:altar_inspiration" }
\t\t\tid: "7A11C0DE40000003"
\t\t\trewards: [
\t\t\t\t{
\t\t\t\t\tid: "7A11C0DE40000051"
\t\t\t\t\titem: { count: 4, id: "minecraft:lead" }
\t\t\t\t\ttype: "item"
\t\t\t\t}
\t\t\t\t{
\t\t\t\t\tid: "7A11C0DE40000052"
\t\t\t\t\titem: { count: 32, id: "minecraft:deepslate_tile_wall" }
\t\t\t\t\ttype: "item"
\t\t\t\t}
\t\t\t\t{
\t\t\t\t\tid: "7A11C0DE40000053"
\t\t\t\t\titem: { count: 32, id: "minecraft:oak_fence" }
\t\t\t\t\ttype: "item"
\t\t\t\t}
\t\t\t\t{
\t\t\t\t\tid: "7A11C0DE40000054"
\t\t\t\t\titem: { count: 4, id: "minecraft:oak_fence_gate" }
\t\t\t\t\ttype: "item"
\t\t\t\t}
\t\t\t\t{
\t\t\t\t\tid: "7A11C0DE40000055"
\t\t\t\t\titem: { count: 32, id: "minecraft:iron_ingot" }
\t\t\t\t\ttype: "item"
\t\t\t\t}
\t\t\t\t{
\t\t\t\t\tid: "7A11C0DE40000056"
\t\t\t\t\titem: { count: 2, id: "numismatics:sprocket" }
\t\t\t\t\ttype: "item"
\t\t\t\t}
\t\t\t]
\t\t\tshape: "diamond"
\t\t\tsubtitle: "Ritual altars, blood storage, and livestock pens."
\t\t\ttasks: [
\t\t\t\t{
\t\t\t\t\tid: "7A11C0DE40000061"
\t\t\t\t\titem: { count: 1, id: "vampirism:altar_inspiration" }
\t\t\t\t\ttype: "item"
\t\t\t\t}
\t\t\t\t{
\t\t\t\t\tid: "7A11C0DE40000062"
\t\t\t\t\titem: { count: 1, id: "vampirism:blood_container" }
\t\t\t\t\ttype: "item"
\t\t\t\t}
\t\t\t]
\t\t\ttitle: "Altar Components & Blood Pen"
\t\t\tx: 2.5d
\t\t\ty: -1.5d
\t\t}
\t\t{
\t\t\tdependencies: ["7A11C0DE40000003"]
\t\t\tdescription: [
\t\t\t\t"Craft an Inscription Table and a Copper Spell Book to begin learning magic."
\t\t\t\t""
\t\t\t\t"§4§lBlood Magic empowers Vampires with offensive life-siphoning and combat agility!§r Use your blood runes and inks to craft Cultist armor and inscribe blood spells."
\t\t\t]
\t\t\ticon: { id: "irons_spellbooks:copper_spell_book" }
\t\t\tid: "7A11C0DE40000004"
\t\t\trewards: [
\t\t\t\t{
\t\t\t\t\tid: "7A11C0DE40000071"
\t\t\t\t\titem: { count: 4, id: "irons_spellbooks:blood_rune" }
\t\t\t\t\ttype: "item"
\t\t\t\t}
\t\t\t\t{
\t\t\t\t\tid: "7A11C0DE40000072"
\t\t\t\t\titem: { count: 16, id: "irons_spellbooks:rare_ink" }
\t\t\t\t\ttype: "item"
\t\t\t\t}
\t\t\t\t{
\t\t\t\t\tid: "7A11C0DE40000073"
\t\t\t\t\titem: { count: 4, id: "irons_spellbooks:epic_ink" }
\t\t\t\t\ttype: "item"
\t\t\t\t}
\t\t\t\t{
\t\t\t\t\tid: "7A11C0DE40000074"
\t\t\t\t\titem: {
\t\t\t\t\t\tcomponents: {
\t\t\t\t\t\t\t"irons_spellbooks:spell_container": {
\t\t\t\t\t\t\t\tdata: [
\t\t\t\t\t\t\t\t\t{
\t\t\t\t\t\t\t\t\t\tid: "irons_spellbooks:blood_slash"
\t\t\t\t\t\t\t\t\t\tlevel: 1
\t\t\t\t\t\t\t\t\t}
\t\t\t\t\t\t\t\t]
\t\t\t\t\t\t\t}
\t\t\t\t\t\t}
\t\t\t\t\t\tcount: 1
\t\t\t\t\t\tid: "irons_spellbooks:scroll"
\t\t\t\t\t}
\t\t\t\t\ttitle: "Scroll of Blood Slash"
\t\t\t\t\ttype: "item"
\t\t\t\t}
\t\t\t\t{
\t\t\t\t\tid: "7A11C0DE40000075"
\t\t\t\t\titem: {
\t\t\t\t\t\tcomponents: {
\t\t\t\t\t\t\t"irons_spellbooks:spell_container": {
\t\t\t\t\t\t\t\tdata: [
\t\t\t\t\t\t\t\t\t{
\t\t\t\t\t\t\t\t\t\tid: "irons_spellbooks:blood_needles"
\t\t\t\t\t\t\t\t\t\tlevel: 1
\t\t\t\t\t\t\t\t\t}
\t\t\t\t\t\t\t\t]
\t\t\t\t\t\t\t}
\t\t\t\t\t\t}
\t\t\t\t\t\tcount: 1
\t\t\t\t\t\tid: "irons_spellbooks:scroll"
\t\t\t\t\t}
\t\t\t\t\ttitle: "Scroll of Blood Needles"
\t\t\t\t\ttype: "item"
\t\t\t\t}
\t\t\t\t{
\t\t\t\t\tid: "7A11C0DE40000076"
\t\t\t\t\titem: {
\t\t\t\t\t\tcomponents: {
\t\t\t\t\t\t\t"irons_spellbooks:spell_container": {
\t\t\t\t\t\t\t\tdata: [
\t\t\t\t\t\t\t\t\t{
\t\t\t\t\t\t\t\t\t\tid: "irons_spellbooks:acupuncture"
\t\t\t\t\t\t\t\t\t\tlevel: 1
\t\t\t\t\t\t\t\t\t}
\t\t\t\t\t\t\t\t]
\t\t\t\t\t\t\t}
\t\t\t\t\t\t}
\t\t\t\t\t\tcount: 1
\t\t\t\t\t\tid: "irons_spellbooks:scroll"
\t\t\t\t\t}
\t\t\t\t\ttitle: "Scroll of Acupuncture"
\t\t\t\t\ttype: "item"
\t\t\t\t}
\t\t\t\t{
\t\t\t\t\tid: "7A11C0DE40000077"
\t\t\t\t\titem: {
\t\t\t\t\t\tcomponents: {
\t\t\t\t\t\t\t"irons_spellbooks:spell_container": {
\t\t\t\t\t\t\t\tdata: [
\t\t\t\t\t\t\t\t\t{
\t\t\t\t\t\t\t\t\t\tid: "irons_spellbooks:ray_of_siphoning"
\t\t\t\t\t\t\t\t\t\tlevel: 1
\t\t\t\t\t\t\t\t\t}
\t\t\t\t\t\t\t\t]
\t\t\t\t\t\t\t}
\t\t\t\t\t\t}
\t\t\t\t\t\tcount: 1
\t\t\t\t\t\tid: "irons_spellbooks:scroll"
\t\t\t\t\t}
\t\t\t\t\ttitle: "Scroll of Ray of Siphoning"
\t\t\t\t\ttype: "item"
\t\t\t\t}
\t\t\t\t{
\t\t\t\t\tid: "7A11C0DE40000078"
\t\t\t\t\titem: {
\t\t\t\t\t\tcomponents: {
\t\t\t\t\t\t\t"irons_spellbooks:spell_container": {
\t\t\t\t\t\t\t\tdata: [
\t\t\t\t\t\t\t\t\t{
\t\t\t\t\t\t\t\t\t\tid: "irons_spellbooks:recall"
\t\t\t\t\t\t\t\t\t\tlevel: 1
\t\t\t\t\t\t\t\t\t}
\t\t\t\t\t\t\t\t]
\t\t\t\t\t\t\t}
\t\t\t\t\t\t}
\t\t\t\t\t\tcount: 1
\t\t\t\t\t\tid: "irons_spellbooks:scroll"
\t\t\t\t\t}
\t\t\t\t\ttitle: "Scroll of Recall"
\t\t\t\t\ttype: "item"
\t\t\t\t}
\t\t\t]
\t\t\tshape: "gear"
\t\t\tsubtitle: "Inscribe blood magic and life-siphoning arts."
\t\t\ttasks: [
\t\t\t\t{
\t\t\t\t\tid: "7A11C0DE40000081"
\t\t\t\t\titem: { count: 1, id: "irons_spellbooks:copper_spell_book" }
\t\t\t\t\ttype: "item"
\t\t\t\t}
\t\t\t\t{
\t\t\t\t\tid: "7A11C0DE40000082"
\t\t\t\t\titem: { count: 1, id: "irons_spellbooks:inscription_table" }
\t\t\t\t\ttype: "item"
\t\t\t\t}
\t\t\t]
\t\t\ttitle: "Blood Arcana & Inscription"
\t\t\tx: 2.5d
\t\t\ty: 1.5d
\t\t}
\t\t{
\t\t\tdependencies: ["7A11C0DE40000002"]
\t\t\tdescription: [
\t\t\t\t"Forge blood-infused equipment and carry a backpack to transport blood bottles during nighttime expeditions."
\t\t\t]
\t\t\ticon: { id: "vampirism:blood_infused_iron_ingot" }
\t\t\tid: "7A11C0DE40000005"
\t\t\trewards: [
\t\t\t\t{
\t\t\t\t\tid: "7A11C0DE40000091"
\t\t\t\t\titem: { count: 8, id: "vampirism:blood_bottle" }
\t\t\t\t\ttype: "item"
\t\t\t\t}
\t\t\t\t{
\t\t\t\t\tid: "7A11C0DE40000092"
\t\t\t\t\titem: { count: 1, id: "sophisticatedbackpacks:iron_backpack" }
\t\t\t\t\ttype: "item"
\t\t\t\t}
\t\t\t\t{
\t\t\t\t\tid: "7A11C0DE40000093"
\t\t\t\t\titem: { count: 2, id: "numismatics:sprocket" }
\t\t\t\t\ttype: "item"
\t\t\t\t}
\t\t\t]
\t\t\tshape: "diamond"
\t\t\tsubtitle: "Blood iron forging and night packs."
\t\t\ttasks: [
\t\t\t\t{
\t\t\t\t\tid: "7A11C0DE400000A1"
\t\t\t\t\titem: { count: 1, id: "vampirism:blood_infused_iron_ingot" }
\t\t\t\t\ttype: "item"
\t\t\t\t}
\t\t\t\t{
\t\t\t\t\tid: "7A11C0DE400000A2"
\t\t\t\t\titem: { count: 1, id: "sophisticatedbackpacks:backpack" }
\t\t\t\t\ttype: "item"
\t\t\t\t}
\t\t\t]
\t\t\ttitle: "Night Prowler Equipment"
\t\t\tx: -2.5d
\t\t\ty: 1.5d
\t\t}
\t\t{
\t\t\tdependencies: [
\t\t\t\t"7A11C0DE40000004"
\t\t\t\t"7A11C0DE40000005"
\t\t\t]
\t\t\tdescription: [
\t\t\t\t"Craft an Exposure camera and color film."
\t\t\t\t""
\t\t\t\t"Capture dramatic color portraits of your coven, or stealthy night reconnaissance photos of hunter positions to keep in your album!"
\t\t\t]
\t\t\ticon: { id: "exposure:camera" }
\t\t\tid: "7A11C0DE40000006"
\t\t\trewards: [
\t\t\t\t{
\t\t\t\t\tid: "7A11C0DE400000B1"
\t\t\t\t\titem: { count: 2, id: "exposure:color_film" }
\t\t\t\t\ttype: "item"
\t\t\t\t}
\t\t\t\t{
\t\t\t\t\tid: "7A11C0DE400000B2"
\t\t\t\t\titem: { count: 2, id: "exposure:black_and_white_film" }
\t\t\t\t\ttype: "item"
\t\t\t\t}
\t\t\t\t{
\t\t\t\t\tid: "7A11C0DE400000B3"
\t\t\t\t\titem: { count: 1, id: "exposure:album" }
\t\t\t\t\ttype: "item"
\t\t\t\t}
\t\t\t\t{
\t\t\t\t\tid: "7A11C0DE400000B4"
\t\t\t\t\titem: { count: 2, id: "numismatics:sprocket" }
\t\t\t\t\ttype: "item"
\t\t\t\t}
\t\t\t]
\t\t\tshape: "gear"
\t\t\tsize: 1.3d
\t\t\tsubtitle: "Stealth surveillance and coven portraits."
\t\t\ttasks: [
\t\t\t\t{
\t\t\t\t\tid: "7A11C0DE400000C1"
\t\t\t\t\titem: { count: 1, id: "exposure:camera" }
\t\t\t\t\ttype: "item"
\t\t\t\t}
\t\t\t\t{
\t\t\t\t\tid: "7A11C0DE400000C2"
\t\t\t\t\titem: { count: 1, id: "exposure:color_film" }
\t\t\t\t\ttype: "item"
\t\t\t\t}
\t\t\t]
\t\t\ttitle: "Espionage & Surveillance"
\t\t\tx: 0.0d
\t\t\ty: 3.5d
\t\t}
\t]
\ttitle: "04 · The Vampire Coven"
}
"""
(ROOT / "config/ftbquests/quests/chapters/ch04_vampires.snbt").write_text(ch04_snbt, encoding="utf-8")

# 7. Localization: config/ftbquests/quests/lang/en_us.snbt
(ROOT / "config/ftbquests/quests/lang/en_us.snbt").write_text("{\n}\n", encoding="utf-8")

print("All 4 chapters and reward tables successfully created!")
