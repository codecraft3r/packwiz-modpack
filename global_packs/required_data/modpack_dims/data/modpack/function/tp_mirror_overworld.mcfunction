# Player-scoped OP command: /function modpack:tp_mirror_overworld
# Teleports the executing player (@s) to the Mirror Overworld and snaps to the safe top surface block.
execute if entity @s[type=minecraft:player] at @s in modpack:mirror_overworld run tp @s ~ 320 ~
execute if entity @s[type=minecraft:player] at @s in modpack:mirror_overworld run spreadplayers ~ ~ 0 1 false @s
execute if entity @s[type=minecraft:player] run tellraw @s [{"text":"[Modpack] ","color":"gold"},{"text":"Teleported to ","color":"gray"},{"text":"Mirror Overworld (modpack:mirror_overworld)","color":"green"}]
