# Manually resets the version gate and re-applies modpack:init
scoreboard objectives add modpack.init dummy
scoreboard players reset #datapack_version modpack.init
function modpack:init
tellraw @s [{"text":"[Modpack] ","color":"gold"},{"text":"Forced re-initialization of world gamerules.","color":"green"}]
