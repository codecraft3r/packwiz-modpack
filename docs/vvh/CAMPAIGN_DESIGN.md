# VvH Campaign Design

Authoring blueprint for the five-chapter FTB Quests rebuild. This document defines the intended graph, player loop, task semantics, reward exposure, and copy direction. It is not final quest copy and does not authorize changes to live quest files.

## 1. Campaign contract

### Player experience

The campaign is for a persistent SMP. It starts with a closed rules loop, presents three equally visible identities, then opens both faction-themed exploration chapters to every player. The faction chapters teach parallel Vampirism, Iron's Spells, Create, and building play without treating a faction choice as a hard content lock. Shared Horizons ends in durable public infrastructure rather than a seasonal finale.

The core loop is:

1. Learn the rules and acknowledge every required clause.
2. Choose a vampire, hunter, or protected-neutral identity without closing content.
3. Follow either mirrored four-tier faction spine and optionally explore its three specialist branches.
4. Bring Cobblemon and Create progress into a shared public project.

### Source-of-truth and ID policy

- All proposed item, advancement, statistic, and component IDs are symbolic until checked against `docs/vvh/ID_CATALOG.md` and `docs/vvh/id_catalog.json`.
- The catalog files were not present when this blueprint was drafted. ID verification is therefore pending. Authors must not implement an ID from this document until the catalog marks it verified.
- Where this document uses an `ID_CATALOG:<token>` placeholder, the author must replace it with a verified native ID and task family. Do not guess an advancement or statistic name.
- FTB Quests chapter, quest, task, and reward IDs must stay within these exclusive ranges:

| Scope | Reserved range |
| --- | --- |
| Chapter 01 | `7A11C0DE10000000`–`7A11C0DE1FFFFFFF` |
| Chapter 02 | `7A11C0DE20000000`–`7A11C0DE2FFFFFFF` |
| Chapter 03 | `7A11C0DE30000000`–`7A11C0DE3FFFFFFF` |
| Chapter 04 | `7A11C0DE40000000`–`7A11C0DE4FFFFFFF` |
| Chapter 05 | `7A11C0DE50000000`–`7A11C0DE5FFFFFFF` |
| Shared reward tables | `7A11C0DEF0000001`–`7A11C0DEF00000FF` |

Quest IDs below are reserved now. Authors should allocate task IDs from `...1001` upward and reward IDs from `...2001` upward inside the same chapter range, keeping every ID unique.

### Global dependency rules

- `ch01.q04` is the campaign's mandatory onboarding terminal. Every chapter opener descends from it.
- `ch02` is a visible identity choice, not a gate for `ch03` or `ch04`.
- `ch03.q01` and `ch04.q01` depend on `ch01.q04`, not on a faction-selection quest.
- The three specialist quests in each faction chapter are optional off-shoots. They do not gate the core capstone.
- `ch05` is open after onboarding. Its two lanes reconverge at the co-op capstone.

### Layout and visual grammar

- Core spines run straight down `x=0`.
- Equivalent faction choices are symmetric around `x=0`: vampire `x=-3.5`, hunter `x=+3.5`, neutral `x=0, y=+1.5` relative to the faction overview.
- Branches fan to `x=-3.0` and `x=+3.0`. Hunter and vampire branch placement mirrors across their paired chapters.
- Capstones use `shape: "hexagon"`, `size: 1.5`, and sit at `x=0, y=4.5`.
- Magic and workstation quests use `gear`. A side branch that is not a magic/workstation quest uses `diamond`. All other quests use the default `circle`.
- Titles stay between two and four words. Subtitles carry lane labels, never balance or implementation commentary.

### Task and reward semantics

- Item tasks are non-consuming inventory inspections unless this document explicitly says otherwise.
- Build, demonstration, rules, and social tasks use explicit checkmark attestations. Their body must say what clicking attests.
- No reward may immediately satisfy the next quest's only substantive task.
- Personal Bevel rewards must set reward distribution to the verified personal behavior (`team_reward: false` in the current schema). Progress itself remains FTB-Team scoped unless the server uses solo/private teams or custom state.
- Team Bevel rewards must use the verified team-distribution behavior and be tested with two accounts before release.
- There are no repeatable quests or repeatable Bevel sources in this campaign.
- Create: Numismatics coins are tradeable server currency. The admin-managed sink board is deliberately outside quest scope; player copy may point players toward it but may not promise stock or prices.

### Pack-specific precedence

This rebuild brief supersedes the older payouts recorded in `RULE_EXCEPTIONS.md` F4 and F5:

- Chapter 01 pays no currency.
- Protected Neutrality pays utility only and no currency.
- Vampire and Hunter selection each pay exactly two personal Bevels.

F7 still applies to the minimal starter-tool opener. F6's faction parity principle still applies, but its older 22–24 Bevel-equivalent target is replaced by the ledger in this document.

## 2. Chapter 01 — Introduction and Rules

Four quests. This is a closed loop: the welcome opens both required clauses, and the terminal acknowledgement directly depends on both clauses. No quest after onboarding can bypass the terminal.

### `ch01.q01` — Welcome Aboard

| Field | Blueprint |
| --- | --- |
| Quest ID | `7A11C0DE10000001` |
| Position / shape | `(0, -1.5)`, circle |
| Subtitle | `Orientation · First steps` |
| Dependencies | None |
| Tasks | Checkmark: player attests that they have read the welcome and know the two required rule nodes must both be opened. |
| Rewards | Minimal starter tools only: `minecraft:compass` ×1 and `minecraft:torch` ×16. No currency. |

Copy sketch: “This book points toward the server's shared rules and the projects players have chosen to build together. Read both notices below before setting out; once they are acknowledged, the rest of the campaign opens as a map rather than a mandate.”

### `ch01.q02` — Claim Your Ground

| Field | Blueprint |
| --- | --- |
| Quest ID | `7A11C0DE10000002` |
| Position / shape | `(-3.0, 0)`, circle |
| Subtitle | `Required rule · Land claims` |
| Dependencies | `ch01.q01` |
| Tasks | Checkmark: player attests they understand how to claim land, respect existing claims, and place permanent builds only where server policy permits. |
| Rewards | None. |

Copy sketch: “Claims keep homes and public works from being changed by surprise, so check the map before building and protect the ground you intend to keep. A clear boundary lets neighbors expand safely; after acknowledging it, return to the final orientation.”

### `ch01.q03` — Rivalry Without Ruin

| Field | Blueprint |
| --- | --- |
| Quest ID | `7A11C0DE10000003` |
| Position / shape | `(+3.0, 0)`, circle |
| Subtitle | `Required rule · Engagement` |
| Dependencies | `ch01.q01` |
| Tasks | Checkmark: player attests that neutral players are protected unless they explicitly provoke conflict, and that faction rivalry never permits griefing, theft, or irreversible damage. |
| Rewards | None. |

Copy sketch: “Hunters and vampires may make trouble for each other, but the conflict stops where consent, claims, and lasting work begin. Protect neutral players and leave no irreversible damage; acknowledging that boundary keeps rivalry playable for everyone.”

### `ch01.q04` — Teams and Trade

| Field | Blueprint |
| --- | --- |
| Quest ID | `7A11C0DE10000004` |
| Position / shape | `(0, 2.5)`, circle |
| Subtitle | `Terminal gate · Teams and economy` |
| Dependencies | **All:** `ch01.q02`, `ch01.q03` |
| Tasks | Checkmark: player attests they understand FTB Team progress/claims and that Numismatics coins are tradeable currency spent through player trade or the separate admin sink board. |
| Rewards | None. No currency. |

Copy sketch: “An FTB Team can share quest progress and claimed ground, while Numismatics coins let players trade for what matters to them. Choose teammates deliberately and treat coins as spendable value; this acknowledgement opens every campaign lane.”

Topology proof: the shortest path to `ch01.q04` is `q01 → q02 + q03 → q04`. Both required clauses are direct dependencies, so neither can be skipped.

## 3. Chapter 02 — Choosing Your Path

Four quests. This chapter makes identity visible without hiding content. Vampire and Hunter use verified native gates; Neutral is a modest manual attestation. No quest in Chapters 03 or 04 depends on any choice here.

### `ch02.q01` — Three Open Roads

| Field | Blueprint |
| --- | --- |
| Quest ID | `7A11C0DE20000001` |
| Position / shape | `(0, -1.5)`, circle |
| Subtitle | `Overview · Identity paths` |
| Dependencies | `ch01.q04` |
| Tasks | Checkmark: player confirms they have considered the three paths. |
| Rewards | None. |

Copy sketch: “The night feud offers two transformations, while protected neutrality leaves room for builders, traders, and wanderers. Your identity changes how you inhabit the world, not which chapters you may read; choose the road that fits now and explore the others freely.”

### `ch02.q02` — Nightbound Path

| Field | Blueprint |
| --- | --- |
| Quest ID | `7A11C0DE20000002` |
| Position / shape | `(-3.5, 0)`, circle |
| Subtitle | `Vampire path · Native gate` |
| Dependencies | `ch02.q01` |
| Tasks | Inspect `vampirism:vampire_fang` ×1; advancement `vampirism:vampire/become_vampire` with the catalog-verified whole-advancement criterion. |
| Rewards | Two personal `numismatics:bevel`; one verified normal-tier vampire cloak (prefer a choice table if current choice semantics are confirmed). |

Copy sketch: “A vampire fang begins a transformation that trades daylight safety for blood-fed power. Complete the change to make the night your natural territory; the Coven chapter remains an open field guide rather than a lock on anyone else's play.”

### `ch02.q03` — Hunter's Oath

| Field | Blueprint |
| --- | --- |
| Quest ID | `7A11C0DE20000003` |
| Position / shape | `(+3.5, 0)`, circle |
| Subtitle | `Hunter path · Native gate` |
| Dependencies | `ch02.q01` |
| Tasks | Inspect `vampirism:injection_garlic` ×1; advancement `vampirism:hunter/become_hunter` with the catalog-verified whole-advancement criterion. |
| Rewards | Two personal `numismatics:bevel`; `vampirism:hunter_axe_normal` ×1, after catalog and tier verification. |

Copy sketch: “Garlic inoculation binds a hunter to the tools and disciplines that answer the night. Complete the initiation to take up that work; the Order chapter remains available to anyone who wants to learn its craft.”

### `ch02.q04` — Protected Neutrality

| Field | Blueprint |
| --- | --- |
| Quest ID | `7A11C0DE20000004` |
| Position / shape | `(0, +1.5)`, circle |
| Subtitle | `Civic path · Protected neutral` |
| Dependencies | `ch02.q01` |
| Tasks | Checkmark: player attests they are choosing protected neutrality and will not invoke that protection while provoking faction conflict. |
| Rewards | Utility only: `minecraft:white_bed` ×1, `minecraft:cooked_beef` ×16, and `minecraft:shield` ×1. No currency and no faction power. |

Copy sketch: “Neutrality protects space for farms, workshops, trade, and travel beyond the feud. Marking it asks both factions to leave you in peace while you honor the same boundary; your next step can be any open chapter or a civic project of your own.”

Symmetry proof: the overview is centered, Vampire and Hunter sit at equal `±3.5` offsets on the same row, and Neutral occupies the center-below position at `y=+1.5`. All three depend only on the same overview.

## 4. Chapter 03 — The Hunter Order

Seven quests: a four-tier central parity spine and three optional integrated specialist branches. The specialist quests deliberately group a coherent workshop or public-build outcome rather than turning every component into a token quest.

### Core parity spine

#### `ch03.q01` — Hunter's Bench

| Field | Blueprint |
| --- | --- |
| Quest ID | `7A11C0DE30000001` |
| Position / shape | `(0, -4.5)`, circle |
| Subtitle | `Core T1 · Foundation` |
| Dependencies | `ch01.q04` only |
| Tasks | Inspect `vampirism:hunter_table` ×1 and `vampirism:stake` ×4. |
| Rewards | One personal Bevel; a recipe-verified full normal Hunter field-kit material bundle, sized to craft a coherent basic set without granting enhanced gear. |

Copy sketch: “The Hunter Table turns ordinary metal and timber into the order's first dependable tools, while stakes give a patrol a way to end a threat cleanly. Establish both before expanding the workshop; the next tier adds brewing and field control.”

#### `ch03.q02` — Sacred Brewing

| Field | Blueprint |
| --- | --- |
| Quest ID | `7A11C0DE30000002` |
| Position / shape | `(0, -1.5)`, gear |
| Subtitle | `Core T2 · Workstations` |
| Dependencies | `ch03.q01` |
| Tasks | Inspect `vampirism:alchemical_cauldron` ×1 and `vampirism:holy_water_bottle_normal` ×1. |
| Rewards | Two personal Bevels; one full brewing-service bundle of recipe-verified bottles and reagents, enough for a useful batch without awarding enhanced holy water. |

Copy sketch: “Holy water gives a hunter a ranged answer when a stake cannot reach, but it depends on a working cauldron and a proven brew. Put that service into operation so patrols can restock; the weapon workshop follows once the order can supply its own field mixtures.”

#### `ch03.q03` — Siege Arsenal

| Field | Blueprint |
| --- | --- |
| Quest ID | `7A11C0DE30000003` |
| Position / shape | `(0, +1.5)`, gear |
| Subtitle | `Core T3 · Logistics and power` |
| Dependencies | `ch03.q02` |
| Tasks | Inspect `vampirism:weapon_table` ×1 plus one catalog-verified enhanced Hunter gear component that cannot be satisfied by the T1 reward. |
| Rewards | Three personal Bevels; a full recipe-threshold weapon/ammunition bundle for continued advanced crafting, excluding the capstone axe and enhanced holy water. |

Copy sketch: “A weapon table converts the order's supplies into gear that can survive stronger night patrols. Prove the bench can produce an enhanced component, then stock it for continued use; the last core step is a paired masterwork.”

#### `ch03.q04` — Order's Masterwork

| Field | Blueprint |
| --- | --- |
| Quest ID | `7A11C0DE30000004` |
| Position / shape | `(0, +4.5)`, hexagon, size 1.5 |
| Subtitle | `Core T4 · Faction capstone` |
| Dependencies | `ch03.q03` only |
| Tasks | Inspect `vampirism:hunter_axe_enhanced` ×1 and `vampirism:holy_water_splash_bottle_enhanced` ×1. |
| Rewards | Four personal Bevels; two team Bevels; `irons_spellbooks:affinity_ring_holy` ×1; `minecraft:obsidian` ×16; a final recipe-verified Hunter resupply bundle. |

Copy sketch: “The enhanced axe and holy water represent two answers to the same pressure: a threat that reaches both the gate and the field. Complete the pair to leave the Order with a repeatable standard of readiness; the ring and portal stock open wider travel and holy specialization.”

### Specialist branches

#### `ch03.q05` — Holy Arsenal

| Field | Blueprint |
| --- | --- |
| Quest ID | `7A11C0DE30000005` |
| Position / shape | `(+3.0, -1.5)`, gear |
| Subtitle | `Specialist · Holy magic` |
| Dependencies | `ch03.q02` |
| Tasks | Inspect `irons_spellbooks:copper_spell_book`, `irons_spellbooks:inscription_table`, a recipe-threshold quantity of `irons_spellbooks:holy_rune`, the complete verified Priest armor set, and `irons_spellbooks:scroll`; checkmark attests that a holy spell was inscribed and demonstrated. |
| Rewards | Two personal Bevels; recipe-threshold holy runes/inks; five valid level-one scrolls: `heal`, `divine_smite`, `blessing_of_life`, `recall`, and `spectral_hammer`. |

Copy sketch: “A working holy arsenal needs more than a loose scroll: it needs a book, inscription bench, runes, vestments, and a spell proved in use. Assemble and demonstrate the complete practice so the workshop can support other patrols; the reward broadens its healing, travel, and smiting repertoire.”

Implementation note: every scroll reward must copy the full component structure from `SPELL_SCROLL_FORMAT.md`: `maxSpells: 1`, `spellWheel: false`, `mustEquip: false`, and a slot with namespaced `id`, `index: 0`, valid `level`, and `locked: true`. Claimed scrolls must be compared in-client with `/createScroll` output.

#### `ch03.q06` — Siege Engineering

| Field | Blueprint |
| --- | --- |
| Quest ID | `7A11C0DE30000006` |
| Position / shape | `(-3.0, +1.5)`, gear |
| Subtitle | `Specialist · Create logistics` |
| Dependencies | `ch03.q03` |
| Tasks | Inspect `create:andesite_alloy`, `create:windmill_bearing`, `create:water_wheel`, `create:mechanical_drill`, and `create:mechanical_press` in catalog-verified recipe-threshold quantities. |
| Rewards | Two personal Bevels; a full Create maintenance bundle of verified shafts, cogwheels, belts, and casings sufficient for one useful extension. |

Copy sketch: “A siege workshop needs power that keeps moving when a patrol is away, from wind and water to drilling and pressing. Bring the complete machine set together so the Order can process supplies at scale; the rewarded maintenance stock lets another line branch from the same works.”

#### `ch03.q07` — Raise the Watch

| Field | Blueprint |
| --- | --- |
| Quest ID | `7A11C0DE30000007` |
| Position / shape | `(-3.0, -3.0)`, diamond |
| Subtitle | `Specialist · World-building` |
| Dependencies | `ch03.q01` |
| Tasks | Inspect `minecraft:stone_bricks` ×64, `minecraft:oak_log` ×32, `minecraft:iron_bars` ×16, and `minecraft:lantern` ×8. Items are not consumed. |
| Rewards | Two personal Bevels; three-times building stock: 192 stone bricks, 96 oak logs, 48 iron bars, and 24 lanterns. |

Copy sketch: “A watchpost makes patrol routes visible and gives travelers a place to report trouble. Assemble a durable stone, oak, iron, and lantern palette before building; the expanded stock is enough to turn that sample into a substantial shared outpost.”

## 5. Chapter 04 — The Vampire Coven

Seven quests. Its geometry, task weight, and Bevel issuance mirror Chapter 03 while its mechanics and fiction remain vampire-specific. Branch placement mirrors the Hunter chapter: world-building right, magic left, and Create right.

### Core parity spine

#### `ch04.q01` — Night's Shelter

| Field | Blueprint |
| --- | --- |
| Quest ID | `7A11C0DE40000001` |
| Position / shape | `(0, -4.5)`, circle |
| Subtitle | `Core T1 · Foundation` |
| Dependencies | `ch01.q04` only |
| Tasks | Inspect one verified `vampirism:coffin_*` variant and `vampirism:blood_pedestal` ×1. |
| Rewards | One personal Bevel; a recipe-verified full basic blood-work material bundle sized for a coherent starter service, without enhanced blood iron. |

Copy sketch: “A coffin makes daylight survivable, while a blood pedestal turns feeding into something the coven can store and manage. Establish both before attempting larger rites; the next tier organizes blood into a working advancement station.”

#### `ch04.q02` — Bloodwork Altars

| Field | Blueprint |
| --- | --- |
| Quest ID | `7A11C0DE40000002` |
| Position / shape | `(0, -1.5)`, gear |
| Subtitle | `Core T2 · Workstations` |
| Dependencies | `ch04.q01` |
| Tasks | Inspect `vampirism:altar_inspiration` ×1 and `vampirism:blood_container` ×1. |
| Rewards | Two personal Bevels; one full recipe-threshold blood-storage and altar-service bundle, excluding infusion-tier materials. |

Copy sketch: “Loose blood keeps one vampire alive; a container and Altar of Inspiration turn it into a coven resource and a path to deeper rites. Put both stations into service so supplies can be gathered deliberately; infusion becomes the next core challenge.”

#### `ch04.q03` — Infused Arsenal

| Field | Blueprint |
| --- | --- |
| Quest ID | `7A11C0DE40000003` |
| Position / shape | `(0, +1.5)`, gear |
| Subtitle | `Core T3 · Logistics and power` |
| Dependencies | `ch04.q02` |
| Tasks | Inspect `vampirism:altar_infusion` ×1 and `vampirism:blood_infused_enhanced_iron_ingot` ×1. |
| Rewards | Three personal Bevels; a full recipe-threshold blood-iron bundle for continued advanced crafting, excluding the capstone blade and pure blood. |

Copy sketch: “The Altar of Infusion turns stored blood and metal into parts that can carry stronger coven relics. Produce enhanced blood iron to prove the rite is stable, then stock the altar for future work; the final core step pairs a masterwork weapon with pinnacle blood.”

#### `ch04.q04` — Coven's Masterwork

| Field | Blueprint |
| --- | --- |
| Quest ID | `7A11C0DE40000004` |
| Position / shape | `(0, +4.5)`, hexagon, size 1.5 |
| Subtitle | `Core T4 · Faction capstone` |
| Dependencies | `ch04.q03` only |
| Tasks | Inspect `vampirism:heart_seeker_enhanced` ×1 and `vampirism:pure_blood_4` ×1. |
| Rewards | Four personal Bevels; two team Bevels; `irons_spellbooks:affinity_ring_blood` ×1; `minecraft:obsidian` ×16; a final recipe-verified coven resupply bundle. |

Copy sketch: “The enhanced Heart Seeker and highest pure blood prove that the coven can sustain both craft and rite at full strength. Complete the pair to establish a standard future members can follow; the ring and portal stock open wider travel and blood specialization.”

### Specialist branches

#### `ch04.q05` — Bloodbound Arcana

| Field | Blueprint |
| --- | --- |
| Quest ID | `7A11C0DE40000005` |
| Position / shape | `(-3.0, -1.5)`, gear |
| Subtitle | `Specialist · Blood magic` |
| Dependencies | `ch04.q02` |
| Tasks | Inspect `irons_spellbooks:copper_spell_book`, `irons_spellbooks:inscription_table`, a recipe-threshold quantity of `irons_spellbooks:blood_rune`, the complete verified Cultist armor set, and `irons_spellbooks:scroll`; checkmark attests that a blood spell was inscribed and demonstrated. |
| Rewards | Two personal Bevels; recipe-threshold blood runes/inks; five valid level-one scrolls: `blood_slash`, `blood_needles`, `acupuncture`, `ray_of_siphoning`, and `recall`. |

Copy sketch: “Blood arcana becomes reliable only when its book, inscription bench, runes, vestments, and first spell work as one practice. Assemble and demonstrate the complete discipline so the coven can teach it safely; the reward widens its offense, siphoning, and return routes.”

Implementation note: use the exact complete spell-container component from `SPELL_SCROLL_FORMAT.md` and compare each claimed reward with `/createScroll`. Never ship a partial component or a broken “None Scroll.”

#### `ch04.q06` — Sanguine Industry

| Field | Blueprint |
| --- | --- |
| Quest ID | `7A11C0DE40000006` |
| Position / shape | `(+3.0, +1.5)`, gear |
| Subtitle | `Specialist · Create logistics` |
| Dependencies | `ch04.q03` |
| Tasks | Inspect `create:andesite_alloy`, `create:windmill_bearing`, `create:water_wheel`, `create:mechanical_drill`, and `create:mechanical_press` in the same catalog-verified quantities as `ch03.q06`. |
| Rewards | Two personal Bevels; the same-value Create maintenance bundle as the Hunter branch. |

Copy sketch: “A blood factory should keep turning through the hours when its operators shelter from daylight, using wind and water to drive drills and presses. Assemble the complete machine set so the coven can automate routine work; the maintenance stock supports the next line without favoring one faction's engineering.”

#### `ch04.q07` — Raise the Manor

| Field | Blueprint |
| --- | --- |
| Quest ID | `7A11C0DE40000007` |
| Position / shape | `(+3.0, -3.0)`, diamond |
| Subtitle | `Specialist · World-building` |
| Dependencies | `ch04.q01` |
| Tasks | Inspect `minecraft:deepslate_bricks` ×64, `minecraft:dark_oak_log` ×32, `minecraft:dark_oak_fence` ×16, and `minecraft:lantern` ×8. Items are not consumed. |
| Rewards | Two personal Bevels; three-times building stock: 192 deepslate bricks, 96 dark oak logs, 48 dark oak fences, and 24 lanterns. |

Copy sketch: “A manor gives the coven a recognizable refuge and turns scattered supplies into a place other players can visit or avoid by choice. Assemble a deepslate, dark oak, fence, and lantern palette before building; the expanded stock can raise a substantial shared hall or crypt.”

## 6. Chapter 05 — Shared Horizons

Nine quests: four sequential Cobblemon milestones, four sequential Create co-op milestones, and one shared-build capstone. Both lane openers depend only on onboarding. The capstone requires the end of both lanes so it represents cooperation across interests rather than a faction gate.

### Cobblemon lane

#### `ch05.q01` — Ballmaker's Start

| Field | Blueprint |
| --- | --- |
| Quest ID | `7A11C0DE50000001` |
| Position / shape | `(-3.5, -4.5)`, circle |
| Subtitle | `Cobblemon · Crafting` |
| Dependencies | `ch01.q04` |
| Tasks | Inspect the catalog-verified standard Poké Ball item, expected `cobblemon:poke_ball`, in a quantity proving one craft batch. |
| Rewards | One personal Bevel; a recipe-threshold apricorn/ball-component bundle for a second batch. |

Copy sketch: “A reliable supply of Poké Balls turns chance encounters into deliberate exploration. Craft the first batch so future captures do not depend on scavenged stock; the returned components prepare the next expedition.”

#### `ch05.q02` — First Companion

| Field | Blueprint |
| --- | --- |
| Quest ID | `7A11C0DE50000002` |
| Position / shape | `(-3.5, -2.5)`, circle |
| Subtitle | `Cobblemon · First capture` |
| Dependencies | `ch05.q01` |
| Tasks | Verified native first-capture advancement/statistic: `ID_CATALOG:cobblemon.first_capture`. Test already-completed state and FTB Team synchronization. |
| Rewards | One personal Bevel; non-rare healing/travel supplies sized for one outing. |

Copy sketch: “A first capture changes the world from a list of sightings into a team you can shape. Bring a new companion home and prepare it for travel; the next milestone asks that partnership to hold up in battle.”

#### `ch05.q03` — First Victory

| Field | Blueprint |
| --- | --- |
| Quest ID | `7A11C0DE50000003` |
| Position / shape | `(-3.5, -0.5)`, circle |
| Subtitle | `Cobblemon · Battle` |
| Dependencies | `ch05.q02` |
| Tasks | Verified native first battle-win advancement/statistic: `ID_CATALOG:cobblemon.first_battle_win`. Do not substitute a battle-start statistic while calling it a win. |
| Rewards | One personal Bevel; a verified modest recovery/training bundle that does not accelerate a creature through an entire progression band. |

Copy sketch: “A battle win shows that training, moves, and matchup choices can carry a team through pressure. Earn that first result and recover together; raid dens are the next place individual preparation becomes group work.”

#### `ch05.q04` — Answer the Den

| Field | Blueprint |
| --- | --- |
| Quest ID | `7A11C0DE50000004` |
| Position / shape | `(-3.5, +1.5)`, diamond |
| Subtitle | `Cobblemon · Raid participation` |
| Dependencies | `ch05.q03` |
| Tasks | Verified native raid-participation or raid-completion trigger: `ID_CATALOG:cobblemon.raid_participation`. If no reliable native detector exists, use an explicit team-attested checkmark after a witnessed den, document the fallback, and keep the payout at one Bevel. |
| Rewards | One personal Bevel; one modest raid-recovery bundle. No rare encounter or progression-skipping reward. |

Copy sketch: “A raid den asks several players to prepare around one shared threat, even when their teams and specialties differ. Take part in a witnessed den and help the group recover afterward; that experience feeds the final public project.”

### Create co-op spine

#### `ch05.q05` — Raise the Sails

| Field | Blueprint |
| --- | --- |
| Quest ID | `7A11C0DE50000005` |
| Position / shape | `(0, -4.5)`, gear |
| Subtitle | `Create co-op · Wind power` |
| Dependencies | `ch01.q04` |
| Tasks | Inspect `create:windmill_bearing` ×1 plus the recipe-verified sail/radial-chassis stock needed for a functional windmill. |
| Rewards | One personal Bevel; a recipe-threshold shaft/cogwheel transmission bundle. |

Copy sketch: “A public factory starts with power that any visitor can see and understand. Raise a functional windmill so the site has a dependable first drive; the transmission stock carries that motion toward a second power source.”

#### `ch05.q06` — Turn the Wheel

| Field | Blueprint |
| --- | --- |
| Quest ID | `7A11C0DE50000006` |
| Position / shape | `(0, -2.5)`, gear |
| Subtitle | `Create co-op · Water power` |
| Dependencies | `ch05.q05` |
| Tasks | Inspect the catalog-verified `create:water_wheel` variant ×1 and checkmark that it has been connected to the shared power network. |
| Rewards | One personal Bevel; a recipe-threshold gearbox/belt extension bundle. |

Copy sketch: “Water power keeps the factory useful when the wind line is awkward to extend or temporarily stopped. Connect a wheel to the shared network so either source can support work; the next station turns that motion into pressing force.”

#### `ch05.q07` — Press Together

| Field | Blueprint |
| --- | --- |
| Quest ID | `7A11C0DE50000007` |
| Position / shape | `(0, -0.5)`, gear |
| Subtitle | `Create co-op · Mechanical press` |
| Dependencies | `ch05.q06` |
| Tasks | Inspect `create:mechanical_press` ×1 and one catalog-verified pressed output made at the shared site. |
| Rewards | One personal Bevel; a full recipe-threshold belt/depot or basin-service bundle for the assembly extension. |

Copy sketch: “A powered press is the first station that proves the shared network does useful work rather than merely turning. Produce a pressed output at the site so other players can rely on the service; the next step links stations into an assembly.”

#### `ch05.q08` — Assembly Line

| Field | Blueprint |
| --- | --- |
| Quest ID | `7A11C0DE50000008` |
| Position / shape | `(0, +1.5)`, gear |
| Subtitle | `Create co-op · Sequenced assembly` |
| Dependencies | `ch05.q07` |
| Tasks | Inspect the catalog-verified sequenced-assembly output (prefer `create:precision_mechanism` if the catalog and recipe confirm it) and checkmark that it was produced on the shared line. |
| Rewards | One personal Bevel; a recipe-threshold maintenance and storage bundle for continued public operation. |

Copy sketch: “An assembly line makes several machines behave like one service, giving the server a place to produce complicated parts without every player rebuilding the same workshop. Complete a verified output on the shared line; the final milestone gives both factory and raid players a lasting public home.”

### Co-op capstone

#### `ch05.q09` — Shared Landmark

| Field | Blueprint |
| --- | --- |
| Quest ID | `7A11C0DE50000009` |
| Position / shape | `(0, +4.5)`, hexagon, size 1.5 |
| Subtitle | `Co-op capstone · Public build` |
| Dependencies | **All:** `ch05.q04`, `ch05.q08` |
| Tasks | Checkmark: team attests it has completed a shared build project that joins a raid staging/recovery area to the public Create factory, marks access clearly, and leaves it usable by later visitors. |
| Rewards | Two team Bevels only. No personal Bevel and no repeatable payout. |

Copy sketch: “Raid groups need a place to gather and recover, while a public factory needs an entrance, storage, and an owner players can find. Join those needs in one shared landmark and leave access clear for whoever comes next; the completed site becomes infrastructure the server can extend rather than a final ending.”

## 7. Reward economy ledger

### Issuance by chapter

| Scope | Personal Bevels | Team Bevels | Notes |
| --- | ---: | ---: | --- |
| Chapter 01 | 0 | 0 | Starter compass and torches only. |
| Chapter 02, intended player | 0 or 2 | 0 | Vampire/Hunter: 2; Neutral: 0. Paths are intended as identities, not a farm. |
| Chapter 03 core spine | 10 | 2 | T1/T2/T3/T4 = 1/2/3/4 personal; T4 adds 2 team. |
| Chapter 03 specializations | 6 | 0 | Three quests ×2 personal. |
| Chapter 04 core spine | 10 | 2 | Exact parity with Chapter 03. |
| Chapter 04 specializations | 6 | 0 | Three quests ×2 personal. |
| Chapter 05 lanes | 8 | 0 | Eight quests ×1 personal. |
| Chapter 05 capstone | 0 | 2 | Team reward only. |

### Route totals

- Faction selection plus one four-tier core spine is **12 personal Bevels** and 2 team Bevels.
- Adding one specialist quest produces the brief's lower normal target: **14 personal Bevels**.
- Completing all three specialist quests in the chosen faction chapter produces **18 personal Bevels**. This is the intended 14–18 ordinary campaign route.
- Completionist total with one intended faction-selection payout, both faction chapters, and all Chapter 05 lanes is **42 personal Bevels** and 6 team Bevels.
- If a faction switch causes both native selection quests to become claimable, the ceiling is **44 personal Bevels** and 6 team Bevels. This remains within the requested 40–45 ceiling, but switching and advancement persistence require runtime testing.
- Repeatable issuance is **zero**.

The phrase “pick one faction, complete spine” in the brief does not arithmetically reach 14–18 under the mandated payouts: `2 + 1 + 2 + 3 + 4 = 12`. This blueprint preserves every mandated per-tier payout and treats one specialist as part of the expected normal route rather than silently inflating a tier.

### Reward guardrails

- “Full-set thematic material bundle” means exact recipe-threshold inputs for a coherent current-tier set or service, not a loose sample and not finished future-tier gear. Recipe quantities must be filled from the catalog/recipe audit before implementation.
- Hunter and Vampire bundles must be compared by recipe cost, time saved, and current usefulness. Equal stack counts alone do not prove parity.
- World-building branches use the same 3× multiplier and equivalent four-part palettes.
- Magic scroll suites are fixed one-time utility. They use valid level-one spell components and never award an above-cap spell.
- Capstone affinity rings and 16 obsidian are one-time personal utility/status rewards. The portal stock is a full, immediately useful bundle.
- No quest buys inputs, consumes currency, sells outputs back, or reproduces its own reward.
- The campaign may mention the Numismatics sink board but contains no sink-board exchange. Stock, pricing, cooldowns, and administration belong to the server runbook.

## 8. Author implementation checklist

1. Merge or read the completed ID catalog and replace every `ID_CATALOG:` token.
2. Verify every symbolic item and advancement against installed pack artifacts; do not rely on names in the old live chapters.
3. Fill every recipe-threshold bundle with exact counts and document the recipe/service it enables.
4. Preserve the reserved quest IDs and allocate unique task/reward IDs inside the chapter ranges.
5. Set every personal and team reward's distribution flag explicitly.
6. Implement the chapter dependencies exactly, especially the Chapter 01 closed loop and the absence of Chapter 02 faction locks on Chapters 03/04.
7. Use the exact scroll data component from `SPELL_SCROLL_FORMAT.md`.
8. Validate SNBT, unique IDs, localization, reachability, dependency direction, and reward totals.
9. Render all five graphs and inspect node overlap, branch mirroring, short titles, and the `y=4.5` capstones.
10. In a disposable client/world, test both native faction advancements, Cobblemon capture/win/raid triggers, Create output tasks, scroll claims, and already-completed advancement behavior.
11. Test personal versus team reward claims with two accounts and with fragmented solo teams.
12. Record static, server-load, client-visual, and multi-account evidence separately. Do not treat this design blueprint as runtime proof.

## 9. Quest count summary

| Chapter | Core/required | Specialist/side | Capstone included in | Total |
| --- | ---: | ---: | --- | ---: |
| 01 — Introduction and Rules | 4 | 0 | Required terminal (`q04`) | 4 |
| 02 — Choosing Your Path | 4 | 0 | None | 4 |
| 03 — The Hunter Order | 4 | 3 | Core T4 (`q04`) | 7 |
| 04 — The Vampire Coven | 4 | 3 | Core T4 (`q04`) | 7 |
| 05 — Shared Horizons | 8 | 0 | Separate (`q09`) | 9 |
| **Campaign** | **24** | **6** | **Three capstone nodes** | **31** |

## 10. Chapter 06 — Requisitions sink board

Chapter 06 adds six quests: one explanatory opener and five optional, weekly, team-scoped paid sinks. This section supersedes the earlier blanket statement that the campaign has no repeatable quests only for these currency-consuming requisitions. It does not authorize a repeatable Bevel source: repeatable Bevel issuance remains zero.

`ch06.q01` — **Open Requisitions** depends on the Chapter 01 terminal and explains that one teammate pays for a crate delivered to the FTB Team. It has no currency or item reward and is not repeatable.

| Weekly sink | Price | Team-scoped output | Guardrail |
| --- | ---: | --- | --- |
| Builder's Crate | 4 Bevels | 64 calcite, 32 tinted glass, 16 glowstone | Building stock only; no currency output. |
| Spellwright's Crate | 4 Bevels | 8 arcane essence, 4 blank runes, 16 common ink | Ordinary inscription inputs; no spell, upgrade orb, or currency output. |
| Ranger's Crate | 3 Bevels | 12 Great Balls, 8 Super Potions, 4 Revives | Field consumables only; no rare encounter or currency output. |
| Wayfarer's Crate | 3 Bevels | 32 firework rockets, 8 leads, 32 paper | Travel and survey stock only; no currency output. |
| Workshop Crate | 5 Bevels | 32 each of iron ingots, copper ingots, redstone, and spruce logs | Ordinary Create inputs; no finished machine or currency output. |

Every paid quest consumes exactly the displayed number of `numismatics:bevel`, uses `repeat_cooldown: 604800`, and marks every output reward `team_reward: true`. Buying all five crates costs **19 Bevels per team per week** (`4 + 4 + 3 + 3 + 5`). Because no requisition rewards Bevels or an input that mints Bevels inside this campaign, the board contains no faucet and cannot self-fund its next purchase cycle.
