# Create the version-tracking scoreboard objective if it does not exist yet
scoreboard objectives add modpack.init dummy

# Only run modpack:init if #datapack_version does not match the current schema version (1).
# Bump this integer (e.g. from 1 to 2) in BOTH load.mcfunction and init.mcfunction
# whenever datapack updates require re-applying gamerules on existing worlds.
execute unless score #datapack_version modpack.init matches 1 run function modpack:init
