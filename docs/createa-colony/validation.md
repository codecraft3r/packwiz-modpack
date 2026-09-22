# Preparation evidence

Source: [Create'a Colony 1.1, CurseForge file 8773452](https://www.curseforge.com/minecraft/modpacks/createa-colony/files/8773452).
Archive SHA-256 and release identity are recorded in `source.json`; exact upstream mod IDs and override hashes are retained alongside it.

- Imported all 122 pinned upstream projects and all 488 overrides without changing override bytes.
- Promoted the four optional mods to required. Client export contains 122 required projects and no optional entries.
- Server export contains 109 required projects and excludes all 13 client-only projects. Evidence for each exclusion is in `client-only.json`.
- Verified all 610 indexed file hashes and the pack index hash, exact Minecraft/NeoForge versions, and a stable second Packwiz refresh.
- Ran the repository SNBT validator and its regression suite (34 tests, one skipped); this upstream archive has no SNBT files.
- Packwiz CLI version: `v0.0.0-20260906154125-ef87d964f8cb`, also pinned in CI.

## Required dependency review

Exact CurseForge file metadata lists these required dependencies; all are included in the imported manifest:

| Mod file | Required project IDs |
| --- | --- |
| Born in Chaos 7917953 | GeckoLib 388172 |
| Born In Configuration 8122961 | Born in Chaos 686437 |
| Chaos Moon 7141889 | Born in Chaos 686437; Enhanced Celestials 438447 |
| Enhanced Celestials Shader Support 7952822 | Enhanced Celestials 438447 |

## Server config placement

[NeoForge 1.21.1 configuration documentation](https://docs.neoforged.net/docs/1.21.1/misc/config/) and `ServerLifecycleHooks` in the [21.1.234 source archive](https://maven.neoforged.net/releases/net/neoforged/neoforge/21.1.234/neoforge-21.1.234-sources.jar) confirm global server configs load from `config/`. Upstream configs remain there. Existing world `serverconfig/` files can override them, reinforcing the fresh-world deployment requirement.

## Runtime boundary

No dedicated server or Minecraft client was started. Downloads of all mod jars, loader startup, client connection, gameplay, and save/restart remain staging acceptance checks. No hosted-server settings or world files were changed.
