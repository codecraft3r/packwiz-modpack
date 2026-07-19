# Changelog

All notable changes to the Poiesis 2 modpack will be documented in this file.

## [2.4.0] - 2026-07-18

### Added
- Added **Living Atlas Quest 02 - The Weathered Ledger**, a week-long, five-route chapter tuned for the server's early Create and diamond-tool milestone. Players complete any three routes for capped horizontal utility rewards; diamond armor, brass, XP, enchantments, rare Pokemon, and factory skips are deliberately excluded.
- Added **The Atlas Exchange**, a 7-day, small-team-safe Bevel sink. Physical Bevels can now be consumed for one shared, horizontal utility cache per offer, with rewards that support early Create, building, exploration, magic, and Cobblemon without creating a progression loop.
- Added original Weathered Ledger quest art to the required Living Atlas resource pack.

## [2.3.2] - 2026-07-17

### Fixed
- Corrected the Explorer's Compass choice reward to use the mod's registered item ID.
- Repacked the required Living Atlas Art resource pack with valid forward-slash asset paths so both custom quest images load.

## [2.3.1] - 2026-07-17

### Added
- Added **Living Atlas Quest 01 - The First Resonance**, a week-long chapter where players complete any three of five activity lenses for capped, choice-driven rewards.
- Added the client-required **Living Atlas Art v1** resource pack for the chapter's original illustrated visuals.

### Fixed
- Restored the live-tested flat FTB Quests `lang/en_us.snbt` localization layout; the nested layout released in 2.3.0 loaded an empty translation table on FTB Quests 2101.1.27.
- Restored the FTB Quest Book in the default StarterKit and its onboarding description.
- Restored the tested Session 00 chapter layout and accurate Cobblemon battle-start wording.

## [2.3.0] - 2026-07-14

### Added
- Added the **FTB Quests** mod (`ftb-quests-forge.pw.toml`) with side `both`. Required for the Living Atlas quest system.
- Imported **Living Atlas Quest 00 - A Blank Page** (`config/ftbquests/`): 1 chapter, 7 quests, 1 reward table. Server-side content only; clients receive quest data through FTB Quests sync.

## [2.2.2] - 2026-07-04

### Added
- Added the **E19 - Cobblemon Minimap Icons** resourcepack (`e19_cobblemon_minimap_icons.pw.toml`) with side `client`.

## [2.2.1] - 2026-06-26

### Added
- Added the **Cubes Without Borders** mod (`cubes-without-borders.pw.toml`) with side `client`.

## [2.2.0] - 2026-06-25

### Changed
- Updated the **Tree Physics** mod (`tree-physics.pw.toml`) to the latest version `neoforge-2.2` (`lWSUJlHs`).
- Verified that the **Sable** library mod and other dependencies are at their latest versions.

## [2.1.0] - 2026-06-23

### Added
- Added the **Burnt Basic** mod (`burnt-basic.pw.toml`) with side `both`.
- Added the **Create Cardan Shafts** mod (`create-cardan-shafts.pw.toml`) with side `both`.
- Added the **Farmer's Delight** mod (`farmers-delight.pw.toml`) with side `both`.
- Added the **Potions Master** mod (`potionsmaster.pw.toml`) with side `both`.
- Added the **Tom's Simple Storage Mod** mod (`toms-storage.pw.toml`) with side `both`.

## [2.0.13] - 2026-06-20

### Changed
- [Iron's Spells and Spellbooks / Server] - Configuration update
    - **Alchemical Cauldron:** Always return ink from scrolls
    - **Upgrade Orbs:** Increase limit from 3 to 6
    - **Respawn Logic:** Have players respawn with their mana bar at 50% instead of 0%
- [Cobblemon / Server] - Spawn configuration update
    - Increase `ultra-rare` spawning odds from 0.2 to 0.5
    - Decrease `common` spawning odds from 94.3 to 94

## [2.0.12] - 2026-06-20

### Changed
- Moved the **AllTheMons [Cobblemon]** resourcepack (`allthemons.pw.toml`) from `resourcepacks/` to `global_packs/required_resources/`.
- Configured the **AllTheMons [Cobblemon]** resourcepack as client-only (`side = "client"`).

## [2.0.11] - 2026-06-20

### Added
- Added the **ModernFix** mod (`modernfix.pw.toml`) with side `both`.
- Added the **FerriteCore** mod (`ferrite-core.pw.toml`) with side `both`.

## [2.0.10] - 2026-06-20

### Added
- Added the **AllTheMons [Cobblemon]** resourcepack (`allthemons.pw.toml`) under `resourcepacks/`.

## [2.0.9] - 2026-06-20

### Added
- Added the **FTB Chunks x Xaero's Compat** mod (`ftbxaerocompat`).

### Changed
- Changed the side of **FTB Essentials** from `server` to `both`.

## [2.0.8] - 2026-06-20

### Changed
- Changed side of **Cobblemon Spawn Notification** and **Cobblemon Tim Core** library from `server` to `both` so they are installed on the client side.

## [2.0.7] - 2026-06-20

### Removed
- Completely removed the **FTB Backups 3** mod from the modpack due to server-side packet delivery validation crashes on clients without the mod installed.

## [2.0.6] - 2026-06-20

### Changed
- Changed side of **FTB Backups 3** from `server` to `both` to fix a server packet crash when backup progress packets were sent (later reverted in 2.0.7).

## [2.0.5] - 2026-06-20

### Fixed
- Downgraded **Cobblemon Raid Dens** from `0.11.1+1.21.1` to `0.11.0+1.21.1` to fix a NullPointerException server startup crash during spawn chunk generation.

## [2.0.0] - 2026-06-20

### Added
- Replaced "All the Mons" modpack with **Poiesis 2**.
- Cleaned up configuration overrides (`config/`, `kubejs/`, `local/`) and root shader files.
- Loader upgraded to **NeoForge 21.1.233**.
- Set up automated packwiz migration and import scripts.
