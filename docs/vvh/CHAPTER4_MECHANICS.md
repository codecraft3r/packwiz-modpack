# Chapter 4 mechanics evidence

This note records the installed-version evidence used by `build_vampires` in
`scripts/vvh_campaign_v3.py`. It is a source and recipe audit, not proof that
the client has accepted a placement, multiblock, fluid route, or social
attestation.

## Pinned artifacts

The evidence below comes from the hash-verified files under `tmp/modcache`:

- `Vampirism-1.21-1.10.12.jar`
  SHA-256 `C6DCCA1AF24DECA473A24470CCAB66053D3AA3324E453B4E1697090ED6D16BE2`
- `irons_spellbooks-1.21.1-3.16.3.jar`
  SHA-256 `55A290DB9B966E0C5D2F5C051D50775F3DB6375CDB52730C4DA528BCF5D5DAA0`
- `vista-1.21.1-5.4.4-neoforge.jar`
  SHA-256 `BDBBD8A860329EDF61D0436CED832165F652C25AD1E02E6C24D1987D972667F5`

The campaign preserves all 15 Chapter 4 quest IDs, coordinates, dependency
edges, and optional flags from the live baseline. First Thirst remains
unchanged by this redesign; its live overlay is the authoritative cloak,
four Blood Bottles, and eight glass bottles grant. The older generator source
contains dyed Wizard armour, but this note does not treat that stale source
definition as the live reward. New task identities use the Chapter 4 `0x4000` local range and new reward
identities use the `0x5000` local range. Existing Sprocket reward IDs remain in
place when the entitlement is still currency, so a redesign does not make an
already claimed currency grant appear as a new reward.

## Verified item and recipe facts

Vampirism 1.10.12 contains these exact recipes and registry assets:

- `vampirism:altar_pillar` is crafted from `minecraft:stone_bricks`.
- `vampirism:altar_tip` uses `c:ingots/iron` and `c:storage_blocks/iron`.
- `vampirism:altar_infusion` is the Altar of Infusion block used by Red
  Measure. `AltarInfusionBlockEntity` computes the first ascent as target
  Vampire level 5: 5 Human Hearts, 1 Vampire Book, 0 pure-blood level, and
  0 pure-blood quantity. The verified early structure is four cardinal
  columns, each two stone Altar Pillars high and capped by an Altar Tip: 8
  pillar blocks, 4 tips, and 8 Stone Bricks used to fill the pillars. Place
  the columns at cardinal offsets of three blocks from the altar, with their
  bases at altar level and their tips at altar level plus two. The tip scan
  searches x/z offsets through ±4 and y levels +1 through +3; activation is
  night-only and the level-5
  requirement is structure target 8, checked internally as 80 score units.
  The quest asks for component supplies;
  ordinary item tasks cannot prove the multiblock arrangement or activation.
- `vampirism:coffin_red` is a real Vampire recipe using planks and red wool.
- `vampirism:blood_grinder` is a real general recipe using a hopper, diamond,
  planks, and an iron ingot. `BloodGrinderBlockEntity` pulls item stacks from
  an inventory above or from dropped items in its capture area. Its process
  looks up the Vampirism item-blood data map, then emits `vampirism:impure_blood`
  through the fluid handler below. The map assigns `minecraft:beef` 200 mB of
  blood, so four Raw Beef represent 800 mB; the block only consumes the item
  when the lower handler can accept at least 90% of that amount. Blood Foundry
  records this input apparatus and batch check separately from the storage and
  Sieve conversion lessons.
- `vampirism:blood_sieve` is a real general recipe using quartz bricks, iron,
  planks, and a cauldron.
- `vampirism:umbrella` and `vampirism:sunscreen_beacon` are present in the
  installed Vampirism artifact. `VampirePlayer.isGettingSundamage` suppresses
  sun damage when the Umbrella is in the player's main hand during the sun
  check; Sunproof Transit therefore uses the Umbrella as the equipment
  checkpoint and leaves the route test as a checkmark. This says nothing about
  other hazards or an off-hand Umbrella.
- The Sieve block entity owns a 2,000 mB tank, pulls fluid from above, and
  pushes processed fluid below. `data/vampirism/data_maps/fluid/fluid_blood_conversion.json`
  records `vampirism:impure_blood` at a `0.75` conversion rate. There is no
  item-output recipe for the Sieve. A Blood Container is a real tank-capable
  block entity with 12,600 mB capacity, so Sieve Extraction names Blood
  Containers above and below. The Sieve's filtering tank emits the registered
  pure blood fluid, and `BloodBottleFluidHandler` accepts that fluid in a
  `vampirism:blood_bottle` with 900 mB capacity. A 1,200 mB impure batch
  therefore yields 900 mB for one full bottle. The default bottle stack has
  an empty blood component; the added item task can only check the item ID,
  while the player-confirmed note records that it was filled from Sieve output
  because item matching cannot prove origin or component amount.

Iron's Spells 3.16.3 contains exact assets and recipes for:

- `irons_spellbooks:alchemist_cauldron`, with recipe families for
  `greater_healing_potion` and `invisibility_elixir`;
- `irons_spellbooks:arcane_anvil` and `irons_spellbooks:scroll_forge`;
- `irons_spellbooks:cultist_helmet`, `cultist_chestplate`,
  `cultist_leggings`, and `cultist_boots`;
- `irons_spellbooks:blood_staff`, `rare_ink`, and `epic_ink`.

Remedy Counter uses the cauldron and those recipe-backed consumables. The
Greater Healing brew consumes a 1,000 mB Strong Healing potion base plus one
Amethyst Shard and yields 250 mB; the Invisibility brew consumes a 1,000 mB
Long Invisibility potion base plus one Shriving Stone and yields 250 mB.
Scarlet Script requires the anvil,
forge, and Cultist set, then rewards a Blood Staff and bounded ink quantities;
it does not return the armour or issue fixed scrolls.

Vista 5.4.4 registers `vista:hollow_cassette` with a maximum stack size of
one. Nocturnal Broadcast therefore emits eight separate cassette rewards: the
historical reward ID `0x36` for the first cassette and new Chapter 4 reward
IDs `0x5100` through `0x5106` for the remaining seven. This preserves the old
reward identity while keeping each unstackable reward claim distinct.

## Quest mechanics boundaries

Red Measure describes component collection separately from altar assembly.
House Charter uses a real `vampirism:coffin_red`, backpack, clipboard, and
signed `minecraft:written_book`; its plan contents and daytime refuge are
player-confirmed. The four commissions establish services with practical
workstations and explicit public boundaries. They do not require Market
access, completed Sieve machinery, or advanced spell-production stations.

Dawn Watch uses the vanilla `minecraft:daylight_detector`, repeaters, and a
warning lamp. The wiring test is a checkmark because ordinary item tasks do
not inspect signal connectivity. Open House similarly uses a signed visitor
guide and a public-boundary attestation; it does not grant claim permissions.

Crimson Reserve requires eight Blood Bottles and two Blood Containers plus a
reserve check. Its separate container rewards are individual entries because
the container is unstackable. Wheat, Carrots, Potatoes, Leads, and limited
fencing/gates support a small refillable reserve without adding processing
machinery.

Commission Sprocket rewards retain their historical reward IDs but are now
team-scoped (`team_reward: true`) to express one shared two-Sprocket grant per
team. Dawn Watch also retains its historical currency reward ID while its
source denomination changes from Cog to Sprocket. Any scope or denomination transition requires
the integration owner's save-claim compatibility handling; it must not be
treated as a fresh currency entitlement. Other Chapter 4 rewards remain
personal unless explicitly marked otherwise.

## Proof boundary

Sunproof Transit replenishes the exact ordinary Umbrella recipe inputs:
three wool, two wooden rods (Sticks), and two Vampire Orchids, from
`data/vampirism/recipe/general/umbrella.json`. The Sunscreen Beacon is not
issued as a reward; the pinned artifact does not supply a normal crafting
recipe for it. The Umbrella recipe is conditional on Vampirism's `umbrella`
configuration, so the runtime gate includes verifying that option.

Static proof covers IDs, item namespaces, recipe evidence, dependencies,
coordinates, and generated SNBT shape. It does not cover in-client altar
assembly, FTB Team claim behavior, cooldowns, inventory overflow, Blood Sieve
fluid routing, remedy recipe execution, or player-confirmed public boundaries.
Those remain runtime/client acceptance checks for the integration pass.
