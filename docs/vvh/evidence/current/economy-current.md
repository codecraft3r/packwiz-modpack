# VvH Economy Report

Source: `scripts/vvh_campaign_v3.py::build_campaign`. This is a deterministic source-level diagnostic; it is not client or server proof.

Campaign: 59 quests across 5 chapters.
One-time issuance: 84 personal + 16 team Bevel-equivalents.
Repeatables: 16 paid sinks costing 53 Bevel-equivalents in total; 1 weekly faucet(s) yielding 1 per team per week.
Faction chapter one-time issuance: ch03_lantern_order 47 personal/0 team; ch04_house_night 31 personal/16 team.

## Repeatables

| Kind | Quest | Price | Cooldown | Reward scope candidate |
|---|---|---:|---:|---|
| paid_sink | Works Kit (`7A11C0DF00500003`) | 1 Sprocket | 180s | shared entitlement; 14.375 64-stack eq. |
| paid_sink | Village Timber Kit (`7A11C0DF0050000F`) | 1 Sprocket | 180s | shared entitlement; 12.6562 64-stack eq. |
| paid_sink | Fortress Kit (`7A11C0DF00500016`) | 2 Sprocket | 180s | shared entitlement; 13 64-stack eq. |
| paid_sink | Celestial Spire Crate (`7A11C0DF00500011`) | 2 Sprocket | 180s | shared entitlement; 13.375 64-stack eq. |
| paid_sink | Sanctified Brewery Crate (`7A11C0DF00500012`) | 2 Sprocket | 180s | shared entitlement; 12.5625 64-stack eq. |
| paid_sink | Frontier Watch Crate (`7A11C0DF00500013`) | 2 Sprocket | 180s | shared entitlement; 15.2812 64-stack eq. |
| paid_sink | Heavy Bastion Crate (`7A11C0DF00500014`) | 2 Sprocket | 180s | shared entitlement; 13 64-stack eq. |
| paid_sink | Create Builder's Palette (`7A11C0DF00500017`) | 2 Sprocket | 180s | shared entitlement; 12 64-stack eq. |
| paid_sink | Create Deco Palette (`7A11C0DF00500015`) | 2 Sprocket | 180s | shared entitlement; 13.5 64-stack eq. |
| paid_sink | Abyssal Deepworks Palette (`7A11C0DF00500018`) | 2 Sprocket | 180s | shared entitlement; 12.5 64-stack eq. |
| paid_sink | Field Kit (`7A11C0DF00500002`) | 1 Bevel | 300s | shared entitlement; 0.828125 64-stack eq. |
| paid_sink | Create Starter Kit (`7A11C0DF00500005`) | 2 Sprocket | 300s | shared entitlement; 0.890625 64-stack eq. |
| paid_sink | Iron's Spells Starter Kit (`7A11C0DF00500004`) | 1 Sprocket | 300s | shared entitlement; 0.34375 64-stack eq. |
| paid_sink | Recovery Crate (`7A11C0DF00500009`) | 1 Sprocket | 300s | shared entitlement; 1.0625 64-stack eq. |
| paid_sink | Transit Crate (`7A11C0DF0050000A`) | 2 Sprocket | 300s | shared entitlement; 0.90625 64-stack eq. |
| paid_sink | Concord Bond (`7A11C0DF00500007`) | 2 Sprocket | 300s | shared entitlement; 24.5 64-stack eq. |
| weekly_faucet | Rumour Ledger (`7A11C0DF00500006`) | none | 604800s | shared entitlement; 0 64-stack eq. |

## Affordability model

Paid board cost: 53 Bevel-equivalents. At fixed population 2, one 2-player team has 184 one-time currency and 1 Bevel-equivalent faucet per week; 2 one-player teams have 200 aggregate and 2 per week. Currency items can transfer/trade, so this compares issuance and claim scope rather than a hard economic pooling barrier.
Optional larger-population scenario (2 teams x 2 members = 4 players): 368 aggregate one-time currency and 2 Bevel-equivalents per week.

| Faction completion | Personal | Team | Team pool with modeled members |
|---|---:|---:|---:|
| Lantern Order | 49 | 0 | 98 |
| House of Night | 33 | 16 | 82 |

## Concord versus Works

Concord Bond costs 4 Bevel-equivalents and supplies 24.5 64-stack equivalents of shaped civic stock. Works Kit costs 2 and supplies 14.375; at Concord's price, Works would supply 28.75. Current Concord is therefore 85.2% of Works by this coarse volume metric, justified only as a curated roads/bridges convenience bundle. A one-Cog version would be about 43% at equal currency and should be rebalanced or explicitly approved as a premium.

## Findings

No source-level findings.

## External audit

- `configured_currency_source_candidates`: 6 source match(es); inspect each before treating it as an active faucet, exchange, or conversion.
- `recycling_npc_exchange_or_denomination_candidates`: 0 source match(es); inspect each before treating it as an active faucet, exchange, or conversion.
- `currency_references_needing_review`: 130 source match(es); inspect each before treating it as an active faucet, exchange, or conversion.

### Review matrix

- `recipe_or_kubejs_currency_changes`: **configured_candidate** (1 evidence line(s); files: config/ftbquests/quests/chapters/ch05_market_services.snbt); Static configuration is a review lead only; recipe registration, NPC offers, recycling outputs, and denomination behavior require registry/recipe inspection and a live client/server check.
- `recycling`: **configured_candidate** (2 evidence line(s); files: config/irons_spellbooks-server.toml); Static configuration is a review lead only; recipe registration, NPC offers, recycling outputs, and denomination behavior require registry/recipe inspection and a live client/server check.
- `npc_trading`: **configured_candidate** (8 evidence line(s); files: config/infinitetrading.json5, config/irons_spellbooks-server.toml, config/mca.json); Static configuration is a review lead only; recipe registration, NPC offers, recycling outputs, and denomination behavior require registry/recipe inspection and a live client/server check.
- `denomination_conversion`: **no_static_candidate_found** (0 evidence line(s); files: none); Static configuration is a review lead only; recipe registration, NPC offers, recycling outputs, and denomination behavior require registry/recipe inspection and a live client/server check.

### Packaged archive review

- Numismatics candidate `C:\Users\Windows\Documents\Codex\2026-07-10\goa\work\packwiz-modpack\mods\CreateNumismatics-1.0.20+neoforge-mc1.21.1.jar`: **unverified_missing**, SHA-256 `missing`.
- Numismatics archive recipes: 0 JSON recipes; 0 recipes reference a Numismatics coin; 0 output a Numismatics coin; 0 loot tables reference a Numismatics coin; packaged config entries: 0. 
- Decor/alloy recycling audit: **unverified_runtime_gate**; 0 packaged recipe references across installed mod archives, 0 direct Numismatics-coin output loop(s). 
- Archive inspection confirms packaged JSON only. Dynamic recipe registration, loot behavior, NPC offers, config defaults, and runtime recycling still require a loaded server/client check.

## Limitations

- Source rewards do not prove FTB claim keys, payment consumption, cooldown timing, inventory overflow, or late-join behaviour.
- A paid service is a shared-entitlement candidate only when every reward entry has team_reward=true; confirm this in a two-account client test.
- Configured-source matches are review leads. Recipe, NPC, recycling, denomination, and obtainability evidence still require registry/recipe inspection and runtime verification.
- Item counts are reported as authored entries; maximum stack size and component decoding require the installed client and registry.
