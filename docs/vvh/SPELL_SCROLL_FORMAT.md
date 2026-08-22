# Iron's Spells 'n Spellbooks — Scroll Item Format (verified)

**Verified against:** `irons_spellbooks-1.21.1-3.16.2` source, git tag
[`v1.21.1-3.16.2`](https://github.com/iron431/irons-spells-n-spellbooks/tree/v1.21.1-3.16.2)
(MC 1.21.1, NeoForge). Installed in this pack: same version (`mods/irons-spells-n-spellbooks.pw.toml`).

## 1. The data component

All scrolls share the base item **`irons_spellbooks:scroll`**; the spell lives in a
NeoForge 1.21.1 **data component** registered as:

- Component id: `irons_spellbooks:spell_container` (`ComponentRegistry.SPELL_CONTAINER`, `registries/ComponentRegistry.java:40`)
- Value type: `io.redspace.ironsspellbooks.capabilities.magic.SpellContainer`
- Persistent codec: `SpellContainer.CODEC` (`capabilities/magic/SpellContainer.java:71-82`)

### Codec field map (exact)

Root object (`SpellContainer.CODEC`):

| Field | Type | Required | Notes |
|---|---|---|---|
| `maxSpells` | int | **yes** | scrolls are created with `1` |
| `spellWheel` | bool | **yes** | scrolls: `false` |
| `mustEquip` | bool | **yes** | scrolls: `false` |
| `improved` | bool | no (default `false`) | |
| `data` | list of spell slots | **yes** | |

Each entry of `data` (`SPELL_SLOT_CODEC`, SpellContainer.java:64-69):

| Field | Type | Required | Notes |
|---|---|---|---|
| `id` | ResourceLocation string | **yes** | full namespaced id, e.g. `irons_spellbooks:heal` — NOT the bare path |
| `index` | int | **yes** | slot index; scrolls use `0` |
| `level` | int | **yes** | 1 .. spell's max level |
| `locked` | bool | no (default `false`) | mod-created scrolls set this to `true` |

Reference construction path — `ISpellContainer.createScrollContainer(spell, level, stack)`
(`api/spells/ISpellContainer.java:49-55`) builds exactly:
`SpellContainer(maxSpells=1, spellWheel=false, mustEquip=false)` with one locked slot at index 0.

> A missing required field makes the codec fail to parse and yields the broken
> "None Scroll" item. This is why `{ data: [...] }` alone does not work.

## 2. Verified SNBT for FTB Quests reward tables

```snbt
{
    id: "7A11C0DE30000074"
    title: "Scroll of Heal"
    type: "item"
    item: {
        id: "irons_spellbooks:scroll"
        count: 1
        components: {
            "irons_spellbooks:spell_container": {
                maxSpells: 1
                spellWheel: false
                mustEquip: false
                data: [
                    {
                        id: "irons_spellbooks:heal"
                        index: 0
                        level: 1
                        locked: true
                    }
                ]
            }
        }
    }
}
```

### Status of existing quest files

The scroll rewards currently in `config/ftbquests/quests/chapters/ch03_hunters.snbt`
and `ch04_vampires.snbt` use only `{ data: [{ id, level }] }`. That structure is
**missing the required root fields (`maxSpells`, `spellWheel`, `mustEquip`) and the
required per-slot field (`index`)**, so it produces broken scrolls. Exact fix per
reward: add

```
maxSpells: 1
spellWheel: false
mustEquip: false
```

inside `"irons_spellbooks:spell_container"` (before `data`), and add

```
index: 0
locked: true
```

to each entry in `data`.

## 3. `/givespell` command

Registered by `kubejs/server_scripts/givespell.js` (KubeJS `2101.7.2-build.368`,
NeoForge 1.21.1, via `ServerEvents.commandRegistry`). Permission level 2 (ops).

```
/givespell <spell_id> <level> [validate]
```

- `<spell_id>`: bare path (`heal`) or fully qualified (`irons_spellbooks:heal`);
  tab completion lists every registry spell.
- `<level>`: integer.
- `[validate]`: optional boolean, default `true`.
  - Unknown spell id or `level < 1` → **always fatal**, no item given.
  - `level > maxLevel` with `validate=true` → hard error naming allowed range.
  - `level > maxLevel` with `validate=false` → warning printed, scroll still given.

Examples:

```
/givespell heal 8
/givespell irons_spellbooks:blood_slash 5 validate=false   # force above-max level w/ warning
```

The command calls `ISpellContainer.createScrollContainer(...)` directly, so its
output is byte-for-byte what the mod's own `/createScroll` produces.

## 4. Validated spell ids and max levels

All 113 spells below were extracted from the v1.21.1-3.16.2 sources
(`DefaultConfig.setMaxLevel(...)` per spell class); ids verified present in
`SpellRegistry` registration order. Quest-relevant spells used in ch03/ch04
(heal, divine_smite, blessing_of_life, recall, spectral_hammer, blood_slash,
blood_needles, acupuncture, ray_of_siphoning) all exist. Note `recall` caps at
level 1.

| Spell id | Max level | Min rarity |
|---|---|---|
| `irons_spellbooks:abyssal_shroud` | 3 | legendary |
| `irons_spellbooks:acid_orb` | 8 | common |
| `irons_spellbooks:acupuncture` | 10 | rare |
| `irons_spellbooks:angel_wing` | 5 | legendary |
| `irons_spellbooks:arcane_shackle` | 8 | rare |
| `irons_spellbooks:arrow_volley` | 6 | uncommon |
| `irons_spellbooks:ascension` | 10 | rare |
| `irons_spellbooks:ball_lightning` | 10 | common |
| `irons_spellbooks:black_hole` | 6 | legendary |
| `irons_spellbooks:blaze_storm` | 10 | common |
| `irons_spellbooks:blessing_of_life` | 10 | common |
| `irons_spellbooks:blight` | 8 | rare |
| `irons_spellbooks:blizzard` | 8 | rare |
| `irons_spellbooks:blood_needles` | 10 | uncommon |
| `irons_spellbooks:blood_slash` | 5 | rare |
| `irons_spellbooks:blood_step` | 5 | uncommon |
| `irons_spellbooks:burning_dash` | 10 | common |
| `irons_spellbooks:chain_creeper` | 6 | uncommon |
| `irons_spellbooks:chain_lightning` | 10 | uncommon |
| `irons_spellbooks:charge` | 3 | rare |
| `irons_spellbooks:cleanse` | 1 | epic |
| `irons_spellbooks:cloud_of_regeneration` | 5 | common |
| `irons_spellbooks:cone_of_cold` | 10 | common |
| `irons_spellbooks:counterspell` | 1 | rare |
| `irons_spellbooks:devour` | 10 | uncommon |
| `irons_spellbooks:divine_smite` | 5 | common |
| `irons_spellbooks:dragon_breath` | 10 | common |
| `irons_spellbooks:earthquake` | 10 | uncommon |
| `irons_spellbooks:echoing_strikes` | 5 | rare |
| `irons_spellbooks:eldritch_blast` | 5 | legendary |
| `irons_spellbooks:electrocute` | 10 | common |
| `irons_spellbooks:evasion` | 5 | epic |
| `irons_spellbooks:fang_strike` | 10 | common |
| `irons_spellbooks:fang_swirl` | 8 | epic |
| `irons_spellbooks:fang_ward` | 8 | common |
| `irons_spellbooks:fire_arrow` | 10 | rare |
| `irons_spellbooks:fire_breath` | 10 | common |
| `irons_spellbooks:fireball` | 5 | rare |
| `irons_spellbooks:firebolt` | 10 | common |
| `irons_spellbooks:firecracker` | 10 | common |
| `irons_spellbooks:firefly_swarm` | 10 | uncommon |
| `irons_spellbooks:flaming_barrage` | 5 | rare |
| `irons_spellbooks:flaming_strike` | 5 | common |
| `irons_spellbooks:fortify` | 10 | common |
| `irons_spellbooks:frost_step` | 8 | rare |
| `irons_spellbooks:frostbite` | 5 | epic |
| `irons_spellbooks:frostwave` | 8 | common |
| `irons_spellbooks:gluttony` | 5 | common |
| `irons_spellbooks:gravity_fissure` | 5 | epic |
| `irons_spellbooks:greater_heal` | 1 | rare |
| `irons_spellbooks:guiding_bolt` | 10 | common |
| `irons_spellbooks:gust` | 10 | uncommon |
| `irons_spellbooks:haste` | 4 | epic |
| `irons_spellbooks:heal` | 8 | uncommon |
| `irons_spellbooks:healing_circle` | 10 | common |
| `irons_spellbooks:heartstop` | 5 | rare |
| `irons_spellbooks:heat_surge` | 6 | common |
| `irons_spellbooks:ice_block` | 6 | rare |
| `irons_spellbooks:ice_spikes` | 10 | common |
| `irons_spellbooks:ice_tomb` | 8 | uncommon |
| `irons_spellbooks:icicle` | 10 | common |
| `irons_spellbooks:invisibility` | 6 | rare |
| `irons_spellbooks:lightning_bolt` | 10 | epic |
| `irons_spellbooks:lightning_lance` | 10 | uncommon |
| `irons_spellbooks:lob_creeper` | 10 | uncommon |
| `irons_spellbooks:magic_arrow` | 10 | rare |
| `irons_spellbooks:magic_missile` | 10 | common |
| `irons_spellbooks:magma_bomb` | 8 | uncommon |
| `irons_spellbooks:oakskin` | 8 | common |
| `irons_spellbooks:planar_sight` | 3 | legendary |
| `irons_spellbooks:pocket_dimension` | 1 | legendary |
| `irons_spellbooks:poison_arrow` | 10 | common |
| `irons_spellbooks:poison_breath` | 10 | common |
| `irons_spellbooks:poison_splash` | 10 | uncommon |
| `irons_spellbooks:portal` | 3 | uncommon |
| `irons_spellbooks:raise_dead` | 6 | uncommon |
| `irons_spellbooks:raise_hell` | 5 | legendary |
| `irons_spellbooks:ray_of_frost` | 5 | common |
| `irons_spellbooks:ray_of_siphoning` | 10 | common |
| `irons_spellbooks:recall` | 1 | uncommon |
| `irons_spellbooks:root` | 10 | uncommon |
| `irons_spellbooks:sacrifice` | 5 | rare |
| `irons_spellbooks:scapegoat` | 3 | rare |
| `irons_spellbooks:scorch` | 10 | uncommon |
| `irons_spellbooks:sculk_tentacles` | 4 | legendary |
| `irons_spellbooks:shadow_slash` | 5 | common |
| `irons_spellbooks:shield` | 10 | common |
| `irons_spellbooks:shockwave` | 8 | common |
| `irons_spellbooks:slow` | 4 | epic |
| `irons_spellbooks:snowball` | 5 | uncommon |
| `irons_spellbooks:sonic_boom` | 3 | legendary |
| `irons_spellbooks:soulfire_ray` | 5 | legendary |
| `irons_spellbooks:spectral_hammer` | 5 | uncommon |
| `irons_spellbooks:spider_aspect` | 8 | rare |
| `irons_spellbooks:starfall` | 10 | uncommon |
| `irons_spellbooks:stomp` | 5 | uncommon |
| `irons_spellbooks:summon_ender_chest` | 1 | rare |
| `irons_spellbooks:summon_horse` | 5 | common |
| `irons_spellbooks:summon_polar_bear` | 10 | rare |
| `irons_spellbooks:summon_swords` | 5 | rare |
| `irons_spellbooks:summon_vex` | 5 | rare |
| `irons_spellbooks:sunbeam` | 10 | uncommon |
| `irons_spellbooks:telekinesis` | 5 | legendary |
| `irons_spellbooks:teleport` | 5 | uncommon |
| `irons_spellbooks:throw` | 5 | common |
| `irons_spellbooks:thunder_step` | 5 | uncommon |
| `irons_spellbooks:thunderstorm` | 8 | rare |
| `irons_spellbooks:touch_dig` | 3 | rare |
| `irons_spellbooks:volt_strike` | 10 | common |
| `irons_spellbooks:wall_of_fire` | 5 | common |
| `irons_spellbooks:wisp` | 10 | common |
| `irons_spellbooks:wither_skull` | 10 | uncommon |
| `irons_spellbooks:wololo` | 1 | legendary |
