# TBD Modpack

Auto-updating Minecraft modpack using [packwiz](https://packwiz.infra.link/).

## MultiMC Installation

1. **Create a new MultiMC instance**
   - Name: `TBD`
   - Minecraft: `1.21.1`
   - NeoForge: `21.1.219`

2. **Download packwiz-installer-bootstrap**
   - Download from: https://github.com/packwiz/packwiz-installer-bootstrap/releases
   - Place `packwiz-installer-bootstrap.jar` in the instance `.minecraft` folder

3. **Set up the pre-launch command**
   - Go to: Edit Instance → Settings → Custom Commands
   - Check "Custom Commands"
   - Set **Pre-launch command** to:
   ```
   "$INST_JAVA" -jar packwiz-installer-bootstrap.jar https://raw.githubusercontent.com/codecraft3r/packwiz-modpack/master/pack.toml
   ```

4. **Export the instance**
   - Right-click instance → Export Instance
   - Save as `.zip` file
   - Share the zip or host it for easy distribution

5. **For users to install**
   - MultiMC: Add Instance → Import from zip
   - The pack auto-updates every time the game launches!

## Manual Installation

Download from [GitHub Releases](https://github.com/codecraft3r/packwiz-modpack/releases).

## Modpack Info
- Minecraft: 1.21.1
- NeoForge: 21.1.219
- Mods: 212
- Resourcepacks: 10
