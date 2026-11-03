// kubejs/server_scripts/blocked_spawns.js

// List of entity types to block from spawning (add more entity IDs here as needed)
const BLOCKED_SPAWN_ENTITIES = [
  'minecraft:wither',
  'minecraft:ender_dragon',
];

EntityEvents.spawned(event => {
  const entityType = event.entity.type;

  if (BLOCKED_SPAWN_ENTITIES.includes(entityType)) {
    event.cancel();

    // Notify server/players when a blocked spawn is prevented
    if (event.server) {
      if (entityType === 'minecraft:wither') {
        event.server.tell('§c[Server] Wither spawning is strictly disabled on this server.');
      } else {
        event.server.tell(`§c[Server] Spawning of ${entityType} is strictly disabled on this server.`);
      }
    }
  }
});
