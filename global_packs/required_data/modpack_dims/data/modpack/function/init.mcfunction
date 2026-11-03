# ============================================================================
# Modpack One-Time / Versioned Initialization (Schema Version: 1)
# ============================================================================

# Core server/world gamerules that cannot be set via static dimension JSON
gamerule doInsomnia false
gamerule doPatrolSpawning false
gamerule doTraderSpawning false
gamerule playersSleepingPercentage 50
gamerule forgiveDeadPlayers true
gamerule universalAnger false

# Record the applied datapack init version so this function does not run again
# until the version number is bumped in a future datapack update.
scoreboard players set #datapack_version modpack.init 1

tellraw @a[tag=admin] [{"text":"[Modpack] ","color":"gold"},{"text":"Initialized world gamerules (v1).","color":"green"}]
