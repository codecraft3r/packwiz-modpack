# Disposable Server Smoke Test

- Result: **PASS**
- NeoForge: `21.1.233`
- Dedicated server reached the vanilla/NeoForge `Done` state: **yes**
- `ftbquests reload` was sent after startup.
- Clean commanded shutdown exit code: `0`
- Targeted VvH/FTB Quests parse, registry, task, reward, or reload errors: `0`
- Full console: `docs/vvh/evidence/server/server-console.log`
- Latest log: `docs/vvh/evidence/server/latest.log`

This verifies headless dedicated-server startup and a post-start quest reload. Client rendering, actual task completion, reward claiming, two-account team semantics, allegiance changes, claim transfer, skirmish controls, and backup restore **requires runtime verification**.
