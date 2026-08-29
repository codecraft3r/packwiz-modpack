// Server script for Mirror Dimension portal feedback, guidance, crafting & mob modifications

// Ensure all spawning Zombies, Husks, and Drowneds are equipped with helmets so they do not burn in perpetual day
EntityEvents.spawned(event => {
  const { entity } = event
  if (!entity || !entity.isLiving()) return

  const type = String(entity.type)
  if (type.includes('zombie') || type.includes('husk') || type.includes('drowned') || type.includes('skeleton')) {
    try {
      const headItem = entity.headArmorItem
      if (!headItem || headItem.isEmpty()) {
        const helmets = ['minecraft:iron_helmet', 'minecraft:golden_helmet', 'minecraft:chainmail_helmet', 'minecraft:leather_helmet']
        const chosenHelmet = helmets[Math.floor(Math.random() * helmets.length)]
        entity.headArmorItem = Item.of(chosenHelmet)
      }
    } catch (_e) {
      try {
        const EquipmentSlot = Java.loadClass('net.minecraft.world.entity.EquipmentSlot')
        const ItemStack = Java.loadClass('net.minecraft.world.item.ItemStack')
        const ItemRegistry = Java.loadClass('net.minecraft.core.registries.BuiltInRegistries').ITEM
        const ResourceLocation = Java.loadClass('net.minecraft.resources.ResourceLocation')
        const item = ItemRegistry.get(ResourceLocation.parse('minecraft:iron_helmet'))
        if (item) {
          entity.setItemSlot(EquipmentSlot.HEAD, new ItemStack(item))
        }
      } catch (_e2) {}
    }
  }
})

// Active hostile mob spawner loop for the Mirror Overworld dimension
LevelEvents.tick(event => {
  const { level, server } = event
  if (!level || !server) return

  const dim = String(level.dimension)
  if (!dim.includes('overworldmirror')) return

  // Run every 100 ticks (5 seconds)
  if (server.tickCount % 100 !== 0) return

  const players = level.players
  if (!players || players.length === 0) return

  const mobTypes = [
    'minecraft:zombie',
    'minecraft:skeleton',
    'minecraft:creeper',
    'minecraft:spider',
    'minecraft:witch',
    'minecraft:phantom',
    'minecraft:cave_spider',
    'minecraft:pillager'
  ]

  for (const p of players) {
    if (!p || p.isSpectator()) continue

    const px = Math.floor(p.x)
    const py = Math.floor(p.y)
    const pz = Math.floor(p.z)

    // Count nearby living monsters within 48 blocks
    const nearbyEntities = level.entities
    let hostileCount = 0
    if (nearbyEntities) {
      for (const e of nearbyEntities) {
        if (e && e.isMonster && e.isMonster()) {
          if (Math.abs(e.x - px) < 48 && Math.abs(e.z - pz) < 48) {
            hostileCount++
          }
        }
      }
    }

    if (hostileCount < 16) {
      const needed = 16 - hostileCount
      const spawnCount = Math.min(needed, 4)

      for (let i = 0; i < spawnCount; i++) {
        const angle = Math.random() * Math.PI * 2
        const dist = 20 + Math.random() * 20
        const spawnX = Math.floor(px + Math.cos(angle) * dist)
        const spawnZ = Math.floor(pz + Math.sin(angle) * dist)

        let spawnY = py
        for (let dy = 12; dy >= -12; dy--) {
          const bGround = level.getBlock(spawnX, py + dy, spawnZ)
          const bAbove = level.getBlock(spawnX, py + dy + 1, spawnZ)
          if (bGround && bGround.solid && bAbove && (!bAbove.solid)) {
            spawnY = py + dy + 1
            break
          }
        }

        const chosenType = mobTypes[Math.floor(Math.random() * mobTypes.length)]
        if (chosenType.includes('zombie') || chosenType.includes('skeleton')) {
          server.runCommandSilent(
            `execute in ${dim} run summon ${chosenType} ${spawnX + 0.5} ${spawnY} ${spawnZ + 0.5} {ArmorItems:[{},{},{},{id:"minecraft:iron_helmet",count:1}]}`
          )
        } else {
          server.runCommandSilent(
            `execute in ${dim} run summon ${chosenType} ${spawnX + 0.5} ${spawnY} ${spawnZ + 0.5}`
          )
        }
      }
    }
  }
})

// Recipe to craft the Dark Mirror Portal Guide book (Book + Poppy + Stone Brick)
ServerEvents.recipes(event => {
  event.shapeless(
    Item.of('minecraft:written_book', {
      written_book_content: {
        title: 'Dark Mirror Portal Guide',
        author: 'Lantern Order Scholar',
        pages: [
          JSON.stringify([
            { text: "  Dark Mirror Portal\n", bold: true, color: "dark_purple" },
            { text: "   Construction Guide\n\n", italic: true, color: "gold" },
            { text: "To open a gateway to the Perpetual Day Mirror Overworld:\n\n", color: "black" },
            { text: "1. ", bold: true, color: "dark_red" },
            { text: "Plant 8 Poppies in a 3x3 ring on soil.\n\n", color: "black" },
            { text: "2. ", bold: true, color: "dark_gray" },
            { text: "Build 3-wide Stone Brick walls on all 4 sides, leaving corners open.", color: "black" }
          ]),
          JSON.stringify([
            { text: " Activation\n\n", bold: true, color: "dark_purple" },
            { text: "3. ", bold: true, color: "dark_green" },
            { text: "Crouch (Shift) and Right-Click any Poppy in the ring while holding ", color: "black" },
            { text: "Bone Meal", bold: true, color: "dark_blue" },
            { text: ".\n\n", color: "black" },
            { text: "If constructed properly, a portal will manifest and transport you to the Dark Mirror dimension.", color: "dark_gray", italic: true }
          ])
        ]
      }
    }),
    ['minecraft:book', 'minecraft:poppy', 'minecraft:stone_bricks']
  )
})

// Right-click event for Bone Meal on Poppy blocks
ItemEvents.rightClicked('minecraft:bone_meal', event => {
  const { player, level, target, server } = event
  if (!target || !target.block) return

  const clickedBlock = target.block

  function isPoppy(b) {
    if (!b) return false
    return b.id === 'minecraft:poppy'
  }

  function isStoneBrick(b) {
    if (!b) return false
    return b.id === 'minecraft:stone_bricks' || b.hasTag('minecraft:stone_bricks')
  }

  // Check if player clicked a Poppy while sneaking
  if (player.isCrouching() && isPoppy(clickedBlock)) {
    const x = clickedBlock.x
    const y = clickedBlock.y
    const z = clickedBlock.z

    // Candidate centers relative to clicked Poppy
    const candidateCenterOffsets = [
      [ 0,  0],
      [-1, -1], [-1, 0], [-1, 1],
      [ 0, -1],          [ 0, 1],
      [ 1, -1], [ 1, 0], [ 1, 1]
    ]

    // Offsets for 8 poppies in 3x3 ring
    const poppyOffsets = [
      [-1, -1], [-1, 0], [-1, 1],
      [ 0, -1],          [ 0, 1],
      [ 1, -1], [ 1, 0], [ 1, 1]
    ]

    // Offsets for 12 stone brick wall blocks (3-wide on each of 4 sides at distance 2)
    const wallOffsets = [
      // North wall (Z = -2, X in -1..1)
      [-1, -2], [0, -2], [1, -2],
      // South wall (Z = 2, X in -1..1)
      [-1,  2], [0,  2], [1,  2],
      // West wall (X = -2, Z in -1..1)
      [-2, -1], [-2, 0], [-2, 1],
      // East wall (X = 2, Z in -1..1)
      [ 2, -1], [ 2, 0], [ 2, 1]
    ]

    // Offsets for 4 corners at distance 2 (must be open gaps)
    const cornerOffsets = [
      [-2, -2], [2, -2], [-2, 2], [2, 2]
    ]

    let bestCandidate = null
    let bestScore = -1
    let bestPoppyCount = 0
    let bestWallCount = 0
    let bestCornersValid = false

    for (const [cxOff, czOff] of candidateCenterOffsets) {
      const cx = x + cxOff
      const cz = z + czOff

      let poppyCount = 0
      for (const [pxOff, pzOff] of poppyOffsets) {
        if (isPoppy(level.getBlock(cx + pxOff, y, cz + pzOff))) {
          poppyCount++
        }
      }

      let wallCount = 0
      for (const [wxOff, wzOff] of wallOffsets) {
        const bSame = level.getBlock(cx + wxOff, y, cz + wzOff)
        const bAbove = level.getBlock(cx + wxOff, y + 1, cz + wzOff)
        if (isStoneBrick(bSame) || isStoneBrick(bAbove)) {
          wallCount++
        }
      }

      let cornersValid = true
      for (const [cornX, cornZ] of cornerOffsets) {
        const bSame = level.getBlock(cx + cornX, y, cz + cornZ)
        const bAbove = level.getBlock(cx + cornX, y + 1, cz + cornZ)
        if (isStoneBrick(bSame) || isStoneBrick(bAbove)) {
          cornersValid = false
          break
        }
      }

      const score = (poppyCount * 2) + wallCount + (cornersValid ? 2 : 0)
      if (score > bestScore) {
        bestScore = score
        bestCandidate = { x: cx, y: y, z: cz }
        bestPoppyCount = poppyCount
        bestWallCount = wallCount
        bestCornersValid = cornersValid
      }
    }

    const isComplete = (bestPoppyCount === 8 && bestWallCount === 12 && bestCornersValid)

    if (isComplete && bestCandidate) {
      const currentDim = String(level.dimension)
      const isMirror = currentDim.includes('overworldmirror')
      const targetDim = isMirror ? 'minecraft:overworld' : 'overworldmirror:overworld'

      const username = player.username || player.name.string
      const px = player.x.toFixed(2)
      const py = player.y.toFixed(2)
      const pz = player.z.toFixed(2)

      if (!player.isCreative() && event.item) {
        event.item.count--
      }

      if (isMirror) {
        player.setStatusMessage(Text.of("§d[Dark Mirror Portal] §fReturning to the Sunlit Overworld..."))
      } else {
        player.setStatusMessage(Text.of("§d[Dark Mirror Portal] §fOpening gateway to the Perpetual Day Mirror Overworld..."))
      }

      player.playSound('minecraft:block.portal.trigger', 0.8, 1.2)
      player.playSound('minecraft:block.amethyst_block.chime', 1.0, 1.0)

      try {
        level.spawnParticles('minecraft:portal', false, bestCandidate.x + 0.5, bestCandidate.y + 0.5, bestCandidate.z + 0.5, 0.5, 0.5, 0.5, 30, 0.2)
        level.spawnParticles('minecraft:end_rod', false, bestCandidate.x + 0.5, bestCandidate.y + 1.0, bestCandidate.z + 0.5, 0.8, 0.5, 0.8, 15, 0.05)
      } catch (_e) {}

      try {
        const centerBlock = level.getBlock(bestCandidate.x, bestCandidate.y, bestCandidate.z)
        if (centerBlock) {
          centerBlock.set('overworldmirror:portal')
        }
      } catch (_e) {}

      const srv = server || (level && level.server) || (player && player.server)
      if (srv) {
        srv.runCommandSilent(`execute in ${targetDim} run tp ${username} ${px} ${py} ${pz}`)
      }
    } else {
      // Diagnostic guidance for incomplete structure
      if (bestPoppyCount < 8) {
        player.setStatusMessage(
          Text.of(`§e[Dark Mirror Portal] §fIncomplete ring! Plant 8 Poppies in a 3x3 ring (found ${bestPoppyCount}/8).`)
        )
      } else if (bestWallCount < 12) {
        player.setStatusMessage(
          Text.of(`§e[Dark Mirror Portal] §fIncomplete walls! Build 3-wide Stone Brick walls on all 4 sides (found ${bestWallCount}/12).`)
        )
      } else if (!bestCornersValid) {
        player.setStatusMessage(
          Text.of("§e[Dark Mirror Portal] §fInvalid corners! Keep the 4 outer corners of the Stone Brick frame empty.")
        )
      }

      player.playSound('minecraft:block.dispensable.fail', 0.8, 0.9)
    }
  }
})
