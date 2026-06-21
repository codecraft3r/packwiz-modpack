# Changelog

All notable changes to the Poiesis 2 modpack will be documented in this file.

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
