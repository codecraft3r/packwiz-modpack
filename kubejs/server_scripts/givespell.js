// /givespell <spell_id> <level> [validate]
//
// ⚠ DEPRECATED — prefer the mod's built-in `/createScroll <spell> <level>`.
// It produces identical output and is maintained by the Iron's Spells team.
// This command is kept only for its validate=false escape hatch (minting a
// scroll above the spell's max level). Do not use for quest-authoring tests.
//
// Gives the executing player a correctly-formed irons_spellbooks:scroll
// containing the requested spell, using Iron's Spells 'n Spellbooks' own
// public API (verified against v1.21.1-3.16.2 source):
//
//   ISpellContainer.createScrollContainer(spell, level, stack)
//     -> builds SpellContainer(maxSpells=1, spellWheel=false, mustEquip=false)
//        with one locked slot {id: irons_spellbooks:<path>, index: 0, level: N}
//        stored under the data component "irons_spellbooks:spell_container".
//
// Validation rules (per quest-dev spec):
//   - Unknown spell id ......... ALWAYS fatal (never gives an item).
//   - level < 1 ................ ALWAYS fatal.
//   - level > spell max level .. validate=true  -> hard error naming allowed range
//                                validate=false -> warning only, item still given.
//
// Mirrors the mod's own /createScroll command (CreateScrollCommand.java),
// which also accepts bare paths ("heal") and normalizes them to
// "irons_spellbooks:heal".
//
// NOTE: must live in server_scripts/ — ServerEvents.commandRegistry is a
// SERVER script type, not STARTUP.

ServerEvents.commandRegistry((event) => {
  const { commands: Commands, arguments: Arguments } = event

  // Lazily-loaded Java classes (Iron's Spells public API + vanilla).
  // Loaded on first command use so we never touch mod classes during
  // startup-script evaluation.
  let Classes = null
  function classes() {
    if (!Classes) {
      Classes = {
        ResourceLocation: Java.loadClass('net.minecraft.resources.ResourceLocation'),
        ItemStack: Java.loadClass('net.minecraft.world.item.ItemStack'),
        Component: Java.loadClass('net.minecraft.network.chat.Component'),
        SpellRegistry: Java.loadClass('io.redspace.ironsspellbooks.api.registry.SpellRegistry'),
        ISpellContainer: Java.loadClass('io.redspace.ironsspellbooks.api.spells.ISpellContainer'),
        ItemRegistry: Java.loadClass('io.redspace.ironsspellbooks.registries.ItemRegistry'),
      }
    }
    return Classes
  }

  const MODID = 'irons_spellbooks'

  /** Normalize "heal" -> "irons_spellbooks:heal" */
  function normalizeId(raw) {
    return raw.indexOf(':') === -1 ? MODID + ':' + raw : raw
  }

  event.register(
    Commands.literal('givespell')
      .requires((source) => source.hasPermission(2))
      .then(
        Commands.argument('spell_id', Arguments.STRING.create(event))
          .suggests((ctx, builder) => {
            // Tab-complete from the live spell registry (skip the placeholder "none").
            const C = classes()
            const keys = C.SpellRegistry.REGISTRY.keySet()
            for (const key of keys) {
              const s = key.toString()
              if (s !== MODID + ':none') {
                builder.suggest(s.substring(MODID.length + 1))
                builder.suggest(s)
              }
            }
            return builder.buildFuture()
          })
          .then(
            Commands.argument('level', Arguments.INTEGER.create(event))
              .then(
                Commands.argument('validate', Arguments.BOOLEAN.create(event)).executes((cmd) =>
                  give(cmd))
              )
              .executes((cmd) => give(cmd))
          )
      )
  )

  function give(cmd) {
    const C = classes()
    const source = cmd.source

    let spellIdRaw = ''
    let level = 1
    let validate = true
    try {
      spellIdRaw = Arguments.STRING.getResult(cmd, 'spell_id')
      level = Arguments.INTEGER.getResult(cmd, 'level')
    } catch (_e) {}
    try {
      validate = Arguments.BOOLEAN.getResult(cmd, 'validate')
    } catch (_e) {}

    // --- Hard sanity gate (always runs, regardless of validate flag) ---
    const fullName = normalizeId(String(spellIdRaw).trim())
    let resource
    try {
      resource = C.ResourceLocation.parse(fullName)
    } catch (_e) {
      source.sendFailure(C.Component.literal('Invalid resource location: ' + fullName))
      return 0
    }

    const spell = C.SpellRegistry.REGISTRY.get(resource)
    // REGISTRY.get returns null for unknown ids; the placeholder "none" is not a real spell either.
    if (spell == null || spell == C.SpellRegistry.none()) {
      source.sendFailure(
        C.Component.literal('Unknown spell "' + fullName + '". Use tab completion, or browse https://github.com/iron431/irons-spells-n-spellbooks (SpellRegistry).')
      )
      return 0
    }

    const spellName = String(spell.getSpellName())
    // spell.<ns>.<name> translation key -> localized display name
    const displayName = '§b' + C.Component.translatable(String(spell.getComponentId())).getString() + '§r'
    const maxLevel = spell.getMaxLevel()

    if (level < 1) {
      source.sendFailure(C.Component.literal('Level must be >= 1 (got ' + level + ').'))
      return 0
    }

    if (level > maxLevel) {
      if (validate) {
        // Strict mode: out-of-range level is a hard error.
        source.sendFailure(
          C.Component.literal(displayName + ' allows levels 1..' + maxLevel + ' (got ' + level + '). Re-run with "false" to force it anyway.')
        )
        return 0
      }
      // Lenient mode: warn but proceed.
      source.sendSuccess(() => C.Component.literal('§e[warn] ' + displayName + ' normally allows levels 1..' + maxLevel + '; forcing level ' + level + '.'), false)
    }

    // --- Build the scroll using the mod's own factory (guaranteed-correct components) ---
    const stack = new C.ItemStack(C.ItemRegistry.SCROLL.get())
    C.ISpellContainer.createScrollContainer(spell, level, stack)

    const player = source.getPlayerOrException()
    const added = player.getInventory().add(stack)
    if (!added) {
      player.drop(stack, false)
      source.sendSuccess(() => C.Component.literal('§e[warn] Inventory full - dropped scroll at your feet.'), false)
    }

    source.sendSuccess(
      () => C.Component.literal('Gave §b' + String(stack.getHoverName().getString()) + '§r (spell=' + spellName + ', level=' + level + ') to ' + String(player.getGameProfile().getName())),
      true
    )
    return 1
  }
})
