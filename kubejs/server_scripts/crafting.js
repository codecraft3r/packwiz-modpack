ServerEvents.recipes(event => {
  event.remove({ output: 'mekanism:mekasuit_helmet' })
  event.remove({ output: 'mekanism:mekasuit_bodyarmor' })
  event.remove({ output: 'mekanism:mekasuit_pants' })
  event.remove({ output: 'mekanism:mekasuit_boots' })

  // --- Mekanism Recipe Modifications ---

  // 1. basic_control_circuit requires create:precision_mechanism instead of osmium ingot
  event.replaceInput({ output: 'mekanism:basic_control_circuit' }, 'mekanism:ingot_osmium', 'create:precision_mechanism')
  event.replaceInput({ output: 'mekanism:basic_control_circuit' }, '#c:ingots/osmium', 'create:precision_mechanism')
  event.replaceInput({ output: 'mekanism:basic_control_circuit' }, '#neoforge:ingots/osmium', 'create:precision_mechanism')
  event.replaceInput({ output: 'mekanism:basic_control_circuit' }, '#forge:ingots/osmium', 'create:precision_mechanism')

  event.remove({ output: 'mekanism:basic_control_circuit' })
  event.shaped('mekanism:basic_control_circuit', ['RCR'], {
    R: 'minecraft:redstone',
    C: 'create:precision_mechanism'
  })
  if (event.recipes && event.recipes.mekanism) {
    event.recipes.mekanism.infusing('mekanism:basic_control_circuit', 'create:precision_mechanism', 'mekanism:redstone', 20)
  }

  // 2. alloy_infused requires create:brass_ingot instead of copper ingot
  event.replaceInput({ output: 'mekanism:alloy_infused' }, 'minecraft:copper_ingot', 'create:brass_ingot')
  event.replaceInput({ output: 'mekanism:alloy_infused' }, '#c:ingots/copper', 'create:brass_ingot')
  event.replaceInput({ output: 'mekanism:alloy_infused' }, '#neoforge:ingots/copper', 'create:brass_ingot')
  event.replaceInput({ output: 'mekanism:alloy_infused' }, '#forge:ingots/copper', 'create:brass_ingot')

  event.remove({ output: 'mekanism:alloy_infused' })
  event.shaped('mekanism:alloy_infused', ['RCR'], {
    R: 'minecraft:redstone',
    C: 'create:brass_ingot'
  })
  if (event.recipes && event.recipes.mekanism) {
    event.recipes.mekanism.infusing('mekanism:alloy_infused', 'create:brass_ingot', 'mekanism:redstone', 10)
  }
})
