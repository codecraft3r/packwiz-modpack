// kubejs/server_scripts/blocked_spawns.js

// List of entity types to block from spawning (add more entity IDs here as needed)
const BLOCKED_SPAWN_ENTITIES = [
  'minecraft:wither',
  'minecraft:ender_dragon',
];

EntityEvents.spawned(BLOCKED_SPAWN_ENTITIES, event => {
  const entityType = event.entity.type;
  event.cancel();

  // Notify server/players when a blocked spawn is prevented
  if (event.server) {
    if (entityType === 'minecraft:wither') {
      event.server.tell('§c[Server] The Wither is disabled on this server.');
      return;
    }
    if (entityType === 'minecraft:ender_dragon') {
      event.server.tell('§c[Server] The Ender Dragon is disabled on this server.');
      return;
    }
    event.server.tell(`§c[Server] ${entityType} cannot spawn as it is disabled on this server.`);
  }
});
