// Server script for Mirror Dimension portal feedback & guidance

ItemEvents.rightClicked('minecraft:bone_meal', event => {
  const { player, level, target } = event
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
    const x = clickedBlock.x
    const y = clickedBlock.y
    const z = clickedBlock.z

    // Relative offsets for 8 perimeter blocks around a center
    const perimeterOffsets = [
      [-1, -1], [-1, 0], [-1, 1],
      [ 0, -1],          [ 0, 1],
      [ 1, -1], [ 1, 0], [ 1, 1]
    ]

    // Candidate centers relative to clicked block
    // The clicked block could be any of the 8 perimeter flowers, or the center itself
    const candidateCenterOffsets = [
      [ 0,  0],
      [-1, -1], [-1, 0], [-1, 1],
      [ 0, -1],          [ 0, 1],
      [ 1, -1], [ 1, 0], [ 1, 1]
    ]

    let bestCandidate = null
    let maxFlowerCount = -1
    let bestMissingPositions = []

    for (const [cxOff, czOff] of candidateCenterOffsets) {
      const cx = x + cxOff
      const cz = z + czOff
      let flowerCount = 0
      let missingPos = []

      for (const [pxOff, pzOff] of perimeterOffsets) {
        const px = cx + pxOff
        const pz = cz + pzOff
        const b = level.getBlock(px, y, pz)
        if (isFlower(b)) {
          flowerCount++
        } else {
          missingPos.push({ x: px, y: y, z: pz })
        }
      }

      if (flowerCount > maxFlowerCount) {
        maxFlowerCount = flowerCount
        bestCandidate = { x: cx, y: y, z: cz }
        bestMissingPositions = missingPos
      }
    }

    if (maxFlowerCount === 8) {
      // Complete flower ring!
      player.setStatusMessage(Text.of("§d[Dark Mirror Portal] §fOpening gateway to the Perpetual Night Overworld..."))
      
      // Play portal activation sounds
      player.playSound('minecraft:block.portal.trigger', 0.8, 1.2)
      player.playSound('minecraft:block.amethyst_block.chime', 1.0, 1.0)

      // Spawn decorative particles around the portal center
      if (bestCandidate) {
        const { x: cx, y: cy, z: cz } = bestCandidate
        try {
          level.spawnParticles('minecraft:portal', false, cx + 0.5, cy + 0.5, cz + 0.5, 0.5, 0.5, 0.5, 30, 0.2)
          level.spawnParticles('minecraft:end_rod', false, cx + 0.5, cy + 1.0, cz + 0.5, 0.8, 0.2, 0.8, 15, 0.05)
        } catch (_e) {}
      }
    } else {
      // Incomplete flower ring
      player.setStatusMessage(
        Text.of(`§e[Dark Mirror Portal] §fIncomplete portal frame (${maxFlowerCount}/8 flowers). Surround a 3x3 area with 8 flowers on soil.`)
      )
      
      player.playSound('minecraft:block.dispensable.fail', 0.8, 0.9)

      // Highlight missing flower positions with subtle particles
      for (const pos of bestMissingPositions) {
        try {
          level.spawnParticles('minecraft:smoke', false, pos.x + 0.5, pos.y + 0.5, pos.z + 0.5, 0.1, 0.1, 0.1, 3, 0.02)
        } catch (_e) {}
      }
    }
  }
})
