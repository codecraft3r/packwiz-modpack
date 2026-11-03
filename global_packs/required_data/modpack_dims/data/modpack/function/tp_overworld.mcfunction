# Player-scoped OP command: /function modpack:tp_overworld
# Teleports the executing player (@s) back to the main Overworld and snaps to the safe top surface block.
execute if entity @s[type=minecraft:player] at @s in minecraft:overworld run tp @s ~ 320 ~
execute if entity @s[type=minecraft:player] at @s in minecraft:overworld run spreadplayers ~ ~ 0 1 false @s
execute if entity @s[type=minecraft:player] run tellraw @s [{"text":"[Modpack] ","color":"gold"},{"text":"Teleported to ","color":"gray"},{"text":"Main Overworld (minecraft:overworld)","color":"yellow"}]
