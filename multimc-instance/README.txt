TBD MultiMC Instance
====================

HOW TO USE:
1. Install MultiMC from https://multimc.org/
2. Create new instance → Name: "TBD" → Minecraft: 1.21.1 → NeoForge: 21.1.219
3. Download packwiz-installer-bootstrap.jar from:
   https://github.com/packwiz/packwiz-installer-bootstrap/releases/latest/download/packwiz-installer-bootstrap.jar
4. Place packwiz-installer-bootstrap.jar in the instance's .minecraft folder
5. Go to Edit Instance → Settings → Custom Commands
6. Check "Custom Commands" and set Pre-launch command to:
   "$INST_JAVA" -jar packwiz-installer-bootstrap.jar https://raw.githubusercontent.com/codecraft3r/packwiz-modpack/master/pack.toml
7. Launch the instance - mods will auto-download and update!
