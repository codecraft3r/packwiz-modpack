# VvH Questline Edit Requests

## Goal

Refine the VvH campaign so the central server-wide building arc stays easy to read and welcoming, while optional faction and progression quests give individuals meaningful side goals. The revision should reward shared spaces, small cooperative events, and consistent participation without creating a runaway power or currency advantage.

## Quest-map layout

- Make the **World-Building lane** the primary vertical spine, centered in the chapter layout.
- Place **Progression and faction quests** to the side as optional branches and sidequests.
- Keep faction branches from interrupting or hard-gating the shared server progression. Examples include establishing a villager town, preparing a vampire manor, assembling a workshop, or advancing personal equipment.
- Review every branched section for visual clarity: avoid awkward crossings, isolated nodes, overly long dependency lines, cramped labels, and branches that appear to dead-end unexpectedly.
- Use consistent spacing, alignment, and visual hierarchy so players can immediately distinguish the central communal path from optional personal routes.
- Capture screenshots of each revised chapter layout at a readable zoom, including the way chapter logos, backgrounds, icons, and lane groupings work together. Treat these screenshots as acceptance-test evidence.

## World-building lane

- Keep world-building objectives simple, concrete, and easy to understand.
- Add specialties that give each shared project a distinct identity, such as a public workshop, supply depot, road stop, watch post, archive, market stall, or communal gathering space.
- Favor persistent common-space improvements over private optimization.
- Add optional standards for useful placement, access, lighting, storage, signage, and connection to public routes without requiring elaborate architectural builds.
- Include team-wide or server-wide milestones where a shared completion unlocks a modest utility, convenience, cosmetic status, or public service.

## Cooperative events

- Add short, low-friction events that bring players together without requiring everyone to be online at once.
- Include occasional group activities centered on making or assembling equipment, preparing supplies, outfitting a work site, or completing a public installation.
- Make events completable by a small subset of the active player base, with team/server rewards that benefit everyone without granting a permanent tier skip.
- Use native FTB Quests tasks and checkmarks for human-reviewed social or build milestones; do not add custom KubeJS quest logic.

## Rewards and economy

- Make quest-completion rewards more generous where the reward saves time, supports construction, improves convenience, or gives meaningful player choice.
- Prefer capped choice bundles, useful materials, workstation components, transport/lighting supplies, consumables, modest equipment support, and civic currency with clear sinks.
- Give especially strong value to cooperative and public-space milestones so group participation feels worthwhile.
- Do not grant major armor tiers, rare boss gear, high-tier spell power, permanent faction levels, duplicable currency inputs, or rewards that create a self-funding loop.
- Keep repeatable or event rewards capped, priced, cooldown-limited, or milestone-limited as appropriate.
- Check the worst case in which every active player completes every generous reward and verify that no single route becomes dominant.

## Unique content and shared progression

- Add more distinctive build objects and destinations where the installed pack supports them: public workshops, notice boards, route markers, supply caches, warded gates, signal towers, communal kitchens only where appropriate, and faction-themed civic structures.
- Give each object a clear gameplay purpose or social use; avoid decorative checklist padding.
- Add a small number of server-wide progression milestones that reflect shared upkeep, connected routes, stocked public facilities, or completed common works.
- Keep individual progression meaningful through optional sidequests while ensuring the central lane remains useful to players who contribute through building, logistics, magic, combat, or collecting.

## Merge and cleanup pass

- Merge quests that repeat the same action, lore beat, construction requirement, or reward purpose.
- Separate equipment/workstation assembly from base/defense assembly.
- Keep lore specific and atmospheric, but do not repeat the objective verbatim or include meta-commentary about design or balance.
- Ensure each quest has a single direct objective and, where needed, a short build standard.
- Preserve faction identity for Blood, Holy, and neutral routes while keeping school access optional and non-locking.

## Acceptance checks

- Render screenshots for every revised chapter and inspect the central spine, side branches, logos, backgrounds, icons, and dependency lines.
- Verify the revised SNBT parses with the installed FTB Quests version.
- Verify every item, block, advancement, currency, reward, icon, and image path against the installed pack.
- Test one central build objective, one specialty project, one cooperative equipment event, one faction sidequest, one server-wide milestone, and one generous reward choice in both solo and team contexts.
- Confirm no custom KubeJS quest logic was introduced.
- Record screenshots and any parser/server log evidence with the revision before release.
