# VvH Authoring Index

Status: current entry point.

The live campaign is a five-chapter persistent-SMP quest world. Before editing it, read:

1. `skills/ftb-quest-authoring/SKILL.md`
2. `skills/ftb-quest-authoring/references/player-facing-campaign-design.md`
3. `skills/ftb-quest-authoring/references/ftb-quests-patterns.md`
4. `skills/snbt-validation/SKILL.md`
5. `docs/vvh/SERVER_RULES.md`
6. `docs/vvh/SOURCE_AUTHORITY.md`
7. `docs/vvh/CAMPAIGN_DESIGN.md`
8. `docs/vvh/BALANCE.md`
9. `docs/vvh/ID_CATALOG.md`
10. `docs/vvh/VALIDATION.md`

## Current implementation

- Authoritative generator: `scripts/vvh_campaign_v3.py`
- Semantic gauntlet: `scripts/vvh_campaign_v3_validate.py`
- Live manifest: `docs/vvh/campaign_manifest.json`
- Structured evidence: `docs/vvh/evidence/current/campaign-validation.json`
- Source-level layout review: `docs/vvh/evidence/current/layouts/`

## Historical warning

Documents describing eight to ten chapters, a 109-quest graph, a dedicated Free Companies/Neutral progression chapter, forced treaty progression, or a disposable season are historical research only. They do not override the current generator, live SNBT, server rules, or source-authority document.

In particular, treat `QUESTLINE_EXPANSION_HANDOFF.md`, `QUEST_EDIT_REQUESTS.md`, and the top-level `docs/vvh-implementation-plan.md` as superseded wherever they conflict with the current five-chapter architecture.
