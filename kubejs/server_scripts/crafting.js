ServerEvents.recipes(event => {
  event.remove({ output: 'mekanism:mekasuit_helmet' })
  event.remove({ output: 'mekanism:mekasuit_bodyarmor' })
  event.remove({ output: 'mekanism:mekasuit_pants' })
  event.remove({ output: 'mekanism:mekasuit_boots' })

  // --- Mekanism Recipe Modifications ---

  // 1. basic_control_circuit requires create:precision_mechanism instead of osmium ingot in Metallurgic Infuser (crafting table recipe removed)
  event.replaceInput({ output: 'mekanism:basic_control_circuit' }, 'mekanism:ingot_osmium', 'create:precision_mechanism')
  event.replaceInput({ output: 'mekanism:basic_control_circuit' }, '#c:ingots/osmium', 'create:precision_mechanism')
  event.replaceInput({ output: 'mekanism:basic_control_circuit' }, '#neoforge:ingots/osmium', 'create:precision_mechanism')
  event.replaceInput({ output: 'mekanism:basic_control_circuit' }, '#forge:ingots/osmium', 'create:precision_mechanism')

  event.remove({ type: 'minecraft:crafting_shaped', output: 'mekanism:basic_control_circuit' })
  event.remove({ type: 'minecraft:crafting_shapeless', output: 'mekanism:basic_control_circuit' })

  event.custom({
    type: 'mekanism:metallurgic_infusing',
    chemical_input: {
      amount: 20,
      tag: 'mekanism:redstone'
    },
    item_input: {
      count: 1,
      item: 'create:precision_mechanism'
    },
    output: {
      count: 1,
      id: 'mekanism:basic_control_circuit'
    }
  })

  // 2. alloy_infused requires create:brass_ingot instead of copper ingot in Metallurgic Infuser (crafting table recipe removed)
  event.replaceInput({ output: 'mekanism:alloy_infused' }, 'minecraft:copper_ingot', 'create:brass_ingot')
  event.replaceInput({ output: 'mekanism:alloy_infused' }, '#c:ingots/copper', 'create:brass_ingot')
  event.replaceInput({ output: 'mekanism:alloy_infused' }, '#neoforge:ingots/copper', 'create:brass_ingot')
  event.replaceInput({ output: 'mekanism:alloy_infused' }, '#forge:ingots/copper', 'create:brass_ingot')

  event.remove({ type: 'minecraft:crafting_shaped', output: 'mekanism:alloy_infused' })
  event.remove({ type: 'minecraft:crafting_shapeless', output: 'mekanism:alloy_infused' })

  event.custom({
    type: 'mekanism:metallurgic_infusing',
    chemical_input: {
      amount: 10,
      tag: 'mekanism:redstone'
    },
    item_input: {
      count: 1,
      item: 'create:brass_ingot'
    },
    output: {
      count: 1,
      id: 'mekanism:alloy_infused'
    }
  })

  // --- Construction Wands Modifications ---

  // Replace constructionwand:infinity_wand recipe with 2 sticks and 1 mekanism:ingot_refined_obsidian on diagonal (bottom-left to top-right)
  event.remove({ output: 'constructionwand:infinity_wand' })
  event.shaped('constructionwand:infinity_wand', [
    '  O',
    ' S ',
    'S  '
  ], {
    S: 'minecraft:stick',
    O: 'mekanism:ingot_refined_obsidian'
  })
})
