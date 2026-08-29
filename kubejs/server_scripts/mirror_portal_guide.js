// Server script for Mirror Dimension portal feedback & guidance

ItemEvents.rightClicked('minecraft:bone_meal', event => {
  const { player, level, target } = event
  if (!target || !target.block) return
  
  // Check if player clicked a flower block while sneaking
  if (player.isCrouching() && target.block.hasTag('minecraft:flowers')) {
    player.setStatusMessage(Text.of("§d[Dark Mirror Portal] §fOpening gateway to the Perpetual Night Overworld...").gold())
  }
})
