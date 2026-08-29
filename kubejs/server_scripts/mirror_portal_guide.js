// Server script for Mirror Dimension portal feedback & guidance

ItemEvents.rightClicked('minecraft:bone_meal', event => {
  const { player, level, target, server } = event
  if (!target || !target.block) return

  const clickedBlock = target.block

  function isFlower(b) {
    if (!b) return false
    return b.hasTag('minecraft:flowers') ||
           b.hasTag('minecraft:small_flowers') ||
           b.hasTag('c:flowers') ||
           b.hasTag('neoforge:flowers')
  }

  // Check if player clicked a flower block while sneaking
  if (player.isCrouching() && isFlower(clickedBlock)) {
    const currentDim = String(level.dimension)
    const isMirror = currentDim.includes('overworldmirror')
    const targetDim = isMirror ? 'minecraft:overworld' : 'overworldmirror:overworld'

    const username = player.username || player.name.string
    const x = player.x.toFixed(2)
    const y = player.y.toFixed(2)
    const z = player.z.toFixed(2)

    // Consume 1 Bone Meal if not in Creative mode
    if (!player.isCreative() && event.item) {
      event.item.count--
    }

    // Display action bar message
    if (isMirror) {
      player.setStatusMessage(Text.of("§d[Dark Mirror Portal] §fReturning to the Sunlit Overworld..."))
    } else {
      player.setStatusMessage(Text.of("§d[Dark Mirror Portal] §fOpening gateway to the Perpetual Night Overworld..."))
    }

    // Audio & Particle Effects
    player.playSound('minecraft:block.portal.trigger', 0.8, 1.2)
    player.playSound('minecraft:block.amethyst_block.chime', 1.0, 1.0)

    try {
      level.spawnParticles('minecraft:portal', false, player.x, player.y + 1, player.z, 0.5, 0.5, 0.5, 30, 0.2)
      level.spawnParticles('minecraft:end_rod', false, player.x, player.y + 1, player.z, 0.8, 0.5, 0.8, 15, 0.05)
    } catch (_e) {}

    // Place portal block above clicked flower if empty
    try {
      const aboveBlock = clickedBlock.above
      if (aboveBlock && (aboveBlock.id === 'minecraft:air' || aboveBlock.id === 'minecraft:cave_air')) {
        aboveBlock.set('overworldmirror:portal')
      }
    } catch (_e) {}

    // Teleport player to target dimension
    const srv = server || (level && level.server) || (player && player.server)
    if (srv) {
      srv.runCommandSilent(`execute in ${targetDim} run tp ${username} ${x} ${y} ${z}`)
    }
  }
})
