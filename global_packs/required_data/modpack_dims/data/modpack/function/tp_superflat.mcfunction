# Player-scoped OP command: /function modpack:tp_superflat
# Teleports the executing player (@s) to the custom Superflat dimension surface (Y = 1, above grass at Y = 0).
execute if entity @s[type=minecraft:player] in modpack:superflat run tp @s 0.5 1.0 0.5 0 0
execute if entity @s[type=minecraft:player] run tellraw @s [{"text":"[Modpack] ","color":"gold"},{"text":"Teleported to ","color":"gray"},{"text":"Superflat (modpack:superflat)","color":"aqua"}]
