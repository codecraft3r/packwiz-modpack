# All the Mons Packwiz Modpack

Auto-updating Minecraft modpack using [packwiz](https://packwiz.infra.link/).

This repository was migrated from the CurseForge release `All the Mons-1.0.0-rc.6.zip` and is structured after `codecraft3r/packwiz-modpack`.

## MultiMC Installation

1. Create a new MultiMC instance.
   - Name: `All the Mons`
   - Minecraft: `1.21.1`
   - NeoForge: `21.1.229`

2. Download `packwiz-installer-bootstrap`.
   - Download from: https://github.com/packwiz/packwiz-installer-bootstrap/releases
   - Place `packwiz-installer-bootstrap.jar` in the instance `.minecraft` folder.

3. Set up the pre-launch command.
   - Go to: Edit Instance -> Settings -> Custom Commands
   - Check `Custom Commands`
   - Set the pre-launch command to:

   ```sh
   "$INST_JAVA" -jar packwiz-installer-bootstrap.jar https://raw.githubusercontent.com/REPLACE_ME/all-the-mons-packwiz/main/pack.toml
   ```

4. Export or share the instance after replacing the `REPLACE_ME` URL with the published repository location.

## Server

`docker-compose.yml` follows the upstream template and uses `itzg/minecraft-server`.
Set `PACKWIZ_URL` to the raw `pack.toml` URL after publishing this repository.

## Modpack Info

- Minecraft: `1.21.1`
- NeoForge: `21.1.229`
- CurseForge project: `1356598`
- CurseForge file: `8120591`
- Pack version: `1.0.0-rc.6`
- Packwiz metadata files: `395`
- Mods: `389`
- Resource packs: `2`
- Shader metadata files at root: `4`
- Override files: `3226`

See `agents.md` for migration state, validation notes, and update rules.
