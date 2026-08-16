# VvH Season One Questline Expansion Handoff

## Purpose

This document is the working brief for the next Codex instance or human author extending the VvH Season One FTB Quests campaign. Continue from the current campaign; do not replace it with a new generic questline.

Repository: `codecraft3r/packwiz-modpack`

Working branch at handoff: `dev`

Current reward-economy commit: `77f6b30` (`Implement Bevel-first quest reward economy`)

The desired result is a week-long campaign made from satisfying one-session events. It should produce shared history, useful public infrastructure, faction identity, and reasons to spend Bevels. It should not become a conventional checklist that rewards the player with the most free time.

The commit above is a locator, not a complete reproducibility claim. Before editing, capture `git status`, `git rev-parse HEAD`, the checked-out branch, and Packwiz state. The live SNBT and localization on that exact checkout are the implementation baseline.

## Canon and Source Hierarchy

Future writing must account for the original pitch and accumulated notes. When sources disagree, use this order and record material resolutions in `docs/vvh/DECISIONS.md`:

1. Verified installed-pack IDs and observed NeoForge/FTB Quests behavior decide technical facts.
2. `C:\Users\Windows\Downloads\VvH Server pitch finalized.pdf` decides the original intended experience, setting premise, and any explicit original lore.
3. Current player feedback and later explicit owner decisions decide current product direction.
4. Live localization and quest SNBT express the active season's established names, events, motifs, and characterization.
5. `DECISIONS.md`, `QUEST_EDIT_REQUESTS.md`, `QUEST_MAP.md`, `BALANCE.md`, and the verification documents govern current implementation constraints, except where they demonstrably lag the live files.
6. `vvh_autonomous_quest_build_prompt.md` is a process/product brief. The historical implementation plan is a source of risk questions and discarded hypotheses, not current authority.
7. Historical drop-in ZIPs and generated prompt documents are regression references, never automatic canon.

The original `server-plan.txt` referenced by the historical plan is no longer present at its recorded Downloads path. Do not reconstruct missing lore from memory. Re-open the finalized pitch PDF before settling a setting-specific dispute.

### Established continuity

- The island's permanent spaces, renewable wilderness, public routes, faction halls, records, and shared works are reasons to return.
- Vampires and Hunters are real Vampirism factions; neutral and independent players remain viable.
- The Living Atlas is an established dry, observant, practical voice. Infrastructure-as-memory, charters, archives, routes, and contradictory records are established motifs.
- House of Night means etiquette, inheritance, hunger under control, hospitality, nocturnal infrastructure, and Blood-aligned ritual.
- Lantern Order means preparation, refuge, stewardship, medicine, readable safety, and Holy-aligned wards—not simply killing vampires.
- Free Companies mean trade, courier work, mediation, mapping, civic relationships, workshops, archives, and limited cross-school utility.
- Combat is optional. Rivalry belongs in markets, races, scavenger hunts, demonstrations, architecture, and supervised opt-in skirmishes—not theft, griefing, harassment, or irreversible sabotage.
- The chapter sequence from Charter through After the Bells is established Season One chronology.

### Proposed, not yet canon

The recurring quartermaster, vampire host, courier, elderly archivist, young spell researcher, treaty incidents, and central historical mystery proposed later in this document are expansion fiction. Introduce them on-screen before referring to them as known people or past founders. Mark every new name, place, event, and historical claim as one of: inherited canon, an expansion of an open thread, or new Season One fiction.

### Explicitly superseded material

Do not revive the historical implementation plan's dynamic faction reward multipliers, exactly-two-fixed-faction architecture, custom `/vvh` KubeJS commands, scoreboard reward system, automated claim scans, claim-budget formula, or unverified reset automation. Current decisions make Free Companies a first-class route, keep Vampirism and FTB Teams state separate, use native FTB Quests plus human review, and use a Bevel-first economy.

## Player and Server Context

- Audience: mostly experienced modded-Minecraft players.
- Population: usually 3–4 active players, occasionally up to 8 during vacations or special events.
- Current progression baseline when this campaign was revised: early Create; one windmill exists; diamond tools are available; players generally do not yet have full diamond armour.
- Recurring failure mode: one player grinds far ahead, obtains exceptional equipment or powers, and demotivates everyone else. Design against this explicitly.
- Preferred activities, roughly in order: supernatural/magic combat, Create or technical factories, cooperative encounters, exploration and building, economy, social events.
- Cooking is a weak interest and should not become a major progression lane.
- Social format: individual identity and optional faction routes, backed by whole-server projects. Competitive events are welcome when contained and consensual.
- Challenge: medium, with occasional harder events. Quests should rarely hard-gate mod progression, but completing them should materially improve convenience and community resources.
- Quest progress should use native FTB Quests and FTB Teams. Vampirism faction state remains owned by Vampirism.
- Do not add custom KubeJS quest synchronization unless a later request explicitly requires it. Native tasks, dependencies, checkmarks, cooldowns, scopes, and reward tables are preferred.

## Campaign Identity

Three perspectives share the island:

1. House of Night: vampire culture, hospitality, inheritance, restraint, nocturnal infrastructure, and Blood-school magic.
2. Lantern Order: hunters, refuge, public safety, discipline, medicine, wards, and Holy-school magic.
3. Free Companies: neutral trade, transport, mediation, workshops, archives, and limited cross-school utility.

Players may explore any spell school. Factions create narrative alignment and stronger thematic milestones, not mechanical class locks. The Free Companies may use limited Blood and Holy utility but should not receive each faction's most prestigious combat milestones.

## Current Chapter Structure

- Chapter 0 — The Island Charter: rules, land use, team/faction expectations, and consent boundaries.
- Chapter 1 — Three Invitations: House, Lantern, or Free Company entry and personal trade lens.
- Chapter 2 — House of Night: separate progression and world-building lanes, Blood-school integration, faction charter.
- Chapter 3 — Lantern Order: separate progression and world-building lanes, Holy-school integration, faction charter.
- Chapter 4 — Free Companies: civic infrastructure, mediation, trade, neutral magical services, faction charter.
- Chapter 5 — The Work Each Hand Knows: civic specialties and the shared `THREE HANDS' WORTH` capstone.
- Chapter 6 — The Island Remembers: simple public works and a shared infrastructure capstone.
- Chapter 7 — Rivalry Without Ruin: contained social and competitive events.
- Chapter 8 — The Long Night Fair: season finale and public showcase.
- Chapter 9 — After the Bells: Bevel sinks, post-season services, and slow weekly civic fallback.

Read the current SNBT and localization before editing. The localization contains the intended prose; chapter SNBT contains layout, tasks, dependencies, images, and rewards.

## Non-Negotiable Design Rules

### Structure

- In faction chapters, the main world-building route should read as a clear central spine.
- Personal equipment, spellcraft, workstation, and mod-progression quests should branch as optional side routes.
- Do not make a public build a disguised item tutorial.
- Separate `Lore`, `Objective`, and `Build Standard` in player-facing copy when a build is involved.
- Lore must not repeat the objective verbatim.
- Avoid meta-commentary such as “this is balanced,” “this encourages cooperation,” or restating the author's design intent.
- Merge quests that duplicate the same action, reward purpose, or story beat.

### Progress and Social Balance

- Balance for the slowest regular player, not the most advanced outlier.
- Prefer complementary contributions over raw volume.
- Use any-N-of-M dependencies for flexible attendance and specialty choice.
- Keep faction participation optional where possible.
- World-building quests should be simple to understand and leave a useful or memorable object in the world.
- Trust-based checkmarks are correct for human-reviewed builds, hosted events, archives, and social actions.

### Rewards

- Bevels are the primary/default reward for substantive one-time progression.
- Thematic materials are additional rewards, not replacements for Bevels.
- Routine substantive progression is generally personal-scoped.
- Shared capstones and public treasuries are team-scoped.
- Chapter 5 specialties use 2 personal Bevels because they represent larger multi-part contributions.
- `SEAL SEASON ONE` uses 3 personal Bevels plus a fair-themed utility choice.
- Low-effort introductions, lane labels, and trust-only micro-activities may be utility-only.
- Do not put Bevels back into choice tables `7A11C0DEF0000002`, `7A11C0DEF0000003`, or `7A11C0DEF0000004`. Bevel income should be guaranteed rather than competing with a thematic choice.
- The only repeatable Bevel source should remain `ARCHIVE A NEW RUMOUR` (`7A11C0DE19000007`), paying exactly 1 team-scoped Bevel on a seven-day cooldown through reward `7A11C0DE19200048`.
- Never create a loop where a reward can fund its own input, rapidly compound, or outpace ordinary progression.
- Do not hand out major armour tiers, rare boss gear, high-tier spells, Vampirism levels, or permanent power skips.

The live chapter SNBT audit on 2026-08-15 calculates 18 one-time personal Bevels on the minimum intended route and 50 personal Bevels for full one-time completion. Both meet the original targets. The same audit calculates 6 team Bevels on a normal selected route, 14 team Bevels if one progress container completes every available faction and capstone branch, and exactly 1 repeatable team Bevel per week. Choice tables #2–#4 contain zero Bevels. Do not add a new personal Bevel without offsetting an existing optional payout or intentionally revising the 50-Bevel ceiling.

There is still a team-policy decision to document: the live all-branches ceiling is 14 because Chapter 1's invitation junction contributes an additional 2-team-Bevel payout beyond the three faction charters and Chapters 5–7 capstones. Either preserve 14 as the explicit completionist treasury ceiling or remove that extra payout after human review; do not change it accidentally.

## Integrated Repair Status (2026-08-15)

The implementation pass completed the graph and economy repairs that previously blocked expansion:

1. `BALANCE.md` and `VALIDATION.md` now describe the live Bevel-first economy and strict issuance bands.
2. Chapter counts and route descriptions in `QUEST_MAP.md` match the live 109-quest graph.
3. Chapter 5's `THREE HANDS' WORTH` gate now accepts a true any three of eight specialties; Archivist is optional.
4. Chapter 6's capstone sees all eight public works and accepts any three.
5. Chapter 7's archive and opt-in skirmish independently require any two noncombat formats, with no reverse gate.
6. Chapters 2–5 and 8 gained optional post-charter/mastery/aftermath depth without delaying the campaign spine.
7. Chapter 9 has seven paid weekly sinks costing ten Bevels total; the one-Bevel weekly fallback cannot self-fund them.
8. The manifest is synchronized from live SNBT, referenced IDs are checked against the materialized mod index, and art paths are checked against the verified resource archive.

The legacy Chapter 8 opener reward ID remains stable because changing a valid global ID adds migration risk without player-facing benefit. The finalized pitch PDF should still be reopened before introducing additional named historical canon; the new quests in this pass deliberately extend existing motifs without inventing a definitive past.

## Recommended Expansion: Priority Order

### Phase 1 — Make Bevels Desirable

Expand Chapter 9 into a compelling, capped public-services catalogue. Verify every item ID and recipe against the installed pack before authoring.

Candidate sinks:

- Building-palette crates: civic stone, dark manor, sacred refuge, industrial workshop, and market decoration.
- Travel kits: rails, maps, boats, scaffolding, safe lighting, and verified transport components.
- Magical research choices: modest Blood, Holy, or Arcane material bundles.
- Event kits: seating materials, banners, fireworks, bells, lighting, and writable records.
- Recovery kits: food, healing, repair supplies, and modest replacement equipment.
- Prestige purchases: decorative faction displays, trophies, plaques, or custom-textured civic objects where the resource pack supports them.
- Expensive team purchases: 6–10 Bevel public-works crates that cannot be self-funded by the weekly one-Bevel fallback.

Every repeatable sink needs an explicit consumed Bevel price, deliberate cooldown, deliberate reward scope, and worst-case weekly economy calculation.

### Phase 2 — Three-Stage Public Projects

Give the largest communal structures a compact project arc:

1. Establish: create the basic structure.
2. Improve: install one useful public service.
3. Consecrate: host a small event there and add a faction-specific finishing feature.

Strong candidates:

- House of Night manor/refuge.
- Lantern watchhouse/refuge.
- Free Company market and contract hall.
- Shared workshop.
- Archive and memorial.
- Road or wayfinding spine.
- Vehicle or airship port, only if the installed pack provides verified relevant content.

Do not require architectural scale. Use concise standards: accessible entrance, labelled public storage, lighting, one faction-specific feature, and a screenshot or player review where appropriate.

### Phase 3 — Cross-Faction Treaty Quests

Add six optional one-time projects where two roles contribute different things:

- Blood and Holy representatives establish a neutral recovery room.
- Lantern players reinforce a night route; House players test and document it.
- A Free Company transports sealed ritual materials between faction sites.
- Engineer and Arcanist create a public magical workshop.
- Quartermaster and Pathfinder establish an expedition depot.
- Archivist and Diplomat record and resolve one disputed piece of island history.

These should reward participation and useful supplies, not reward the largest material donation.

### Phase 4 — Event Card Library

Create eight event cards that administrators can schedule whenever enough players are online. Each event should take roughly one session and contain preparation, event, and aftermath beats.

Suggested cards:

- Midnight courier relay.
- Public equipment-assembly night.
- Fortification sprint.
- Magical first-aid or ward drill.
- Faction-clue scavenger hunt.
- Auction and barter night.
- Road-repair caravan.
- Vehicle rally or expedition launch, if supported by verified pack content.

Use checkmarks for hosted social actions. Make most cards one-time seasonal achievements. Avoid adding additional repeatable Bevel sources.

### Phase 5 — Persistent Specialties

Extend Chapter 5 specialties with optional mastery follow-ups requiring three distinct contributions across the season:

- Engineer: install or maintain three shared services.
- Arcanist: demonstrate, document, and safely store magical knowledge.
- Faction Specialist: translate supernatural mechanics into useful public guidance.
- Aeronaut: prepare, launch, and document a vehicle expedition.
- Diplomat: host a meeting, resolve a dispute, and publish the result.
- Quartermaster: create, issue, and restock public field kits.
- Pathfinder: survey, mark, and maintain a route.
- Archivist: preserve a discovery, a failure, and a faction disagreement.

Mastery rewards should be recognition, Bevels, and role-specific utility—not exclusive power.

### Phase 6 — Season Mystery and Recurring Characters

Thread one question through existing chapters: what forced the island's previous factions to cooperate, what failed, and who altered the record?

Each route should reveal a biased fragment:

- House of Night remembers inheritance, etiquette, hunger, and betrayal.
- Lantern Order remembers containment, sacrifice, stewardship, and incomplete testimony.
- Free Companies remember supply failures, political compromises, and contracts with missing signatures.
- The archive contains mutually incompatible accounts.
- The Long Night Fair reveals a final piece but allows multiple interpretations.

Suggested recurring voices:

- A practical Lantern quartermaster who distrusts ceremony.
- A vampire host obsessed with etiquette and unable to admit fear directly.
- A Free Company courier whose marginal notes become increasingly personal and irritated.
- An elderly archivist who preserves contradictory memories rather than resolving them.
- A young spell researcher whose translations are clever, useful, and occasionally unsafe.

Write them as people with preferences, errors, omissions, and relationships. Do not turn every character into a quest dispenser or omniscient narrator.

### Phase 7 — Finale Upgrade

Make the Long Night Fair a scheduled multi-part capstone:

- House hospitality booth or night refuge.
- Lantern public service or ward station.
- Free Company market and mediation desk.
- Engineering or vehicle exhibition.
- Public performance, story, or demonstration.
- Archive reading and season memorial.
- Final interpretation of the season mystery.

Require a reasonable subset rather than perfect attendance. The fair should celebrate what exists in the world, not demand a new grind immediately before the finale.

## Additional High-Value Ideas

- Catch-up commissions for late joiners: tour public facilities, contribute to one existing project, receive a modest participation kit, and earn a few early Bevels without skipping equipment tiers.
- Expedition dossiers: named patron, destination clue, purpose, two optional discoveries, and a written or visual field report.
- Public trophy cabinet: one-time relics and records displayed in a communal archive.
- Consequence quests: small follow-ups showing what changed after a manor, market, workshop, refuge, or route opened.
- Maintenance milestones: one-time restoration achievements for public spaces; routine maintenance should mostly pay utility rather than currency.
- Secret discoveries: optional unlocks tied to verified items or advancements already present in the pack.
- Illustrated interludes: a few strong panoramas, maps, correspondence objects, seals, and character portraits at emotional transitions rather than decorative images on every routine task.

## Art and Audio Direction

Existing prompt and asset references are located under `docs/vvh/`, including:

- `ASSET_PROMPTS.md`
- `IRON_SPELLS_IMAGE_BATCH.txt`
- `ASSET_SOURCES.md`
- `SUNO_INSTRUMENTAL_PROMPTS.txt` (currently an untracked local file; preserve it unless explicitly asked to add it)

Art should be pixelated Minecraft-style illustration with transparent backgrounds for icons and controlled UI-safe composition for panoramas. Do not embed text, official logos, or an overpowered central hero. Faction palettes should remain distinct: blood/wine/night, holy/lantern/ivory, and neutral/brass/green/civic parchment.

Before adding an image:

1. Confirm it materially improves orientation or an emotional beat.
2. Confirm its exact namespace and resource-pack destination.
3. Check dimensions, alpha, case, extension, and UI crop.
4. Update hosted resource-pack metadata/digests if the distribution model requires it.
5. Open the actual quest screen and inspect contrast and composition.

Custom music and ambience can reinforce major locations and events, but should not be required for quest completion. Confirm licensing and distribution rights before committing generated audio.

## Implementation Map

Primary quest files:

- `config/ftbquests/quests/chapters/vvh_00_island_charter.snbt`
- `config/ftbquests/quests/chapters/vvh_01_three_invitations.snbt`
- `config/ftbquests/quests/chapters/vvh_02_house_of_night.snbt`
- `config/ftbquests/quests/chapters/vvh_03_lantern_order.snbt`
- `config/ftbquests/quests/chapters/vvh_04_free_companies.snbt`
- `config/ftbquests/quests/chapters/vvh_05_work_each_hand_knows.snbt`
- `config/ftbquests/quests/chapters/vvh_06_island_remembers.snbt`
- `config/ftbquests/quests/chapters/vvh_07_rivalry_without_ruin.snbt`
- `config/ftbquests/quests/chapters/vvh_08_long_night_fair.snbt`
- `config/ftbquests/quests/chapters/vvh_09_after_the_bells.snbt`

Supporting files:

- `config/ftbquests/quests/lang/en_us.snbt`
- `config/ftbquests/quests/reward_tables/*.snbt`
- `docs/vvh/campaign_manifest.json`
- `docs/vvh/BALANCE.md`
- `docs/vvh/QUEST_MAP.md`
- `scripts/vvh_build.py`
- `scripts/vvh_sync_manifest.py`
- `scripts/vvh_validate.py`
- `scripts/vvh_render_layouts.py`
- `scripts/vvh_server_smoke.sh`

The authored SNBT and localization are the live source of truth. Run
`python scripts/vvh_sync_manifest.py .` after editing them, then use `--check`
in validation or CI. `vvh_build.py` is a legacy full-campaign generator whose
model predates this depth pass; it now refuses to overwrite live files unless
`--overwrite-live` is explicitly supplied. Do not use that escape hatch until
its output has been generated elsewhere and reviewed as a full diff. Preserve
current prose, IDs, layout, and dependency intent unless a specific change
requires them.

### Parallel authoring protocol

If multiple agents work at once, assign exclusive ownership by file or chapter. Do not let two agents edit localization, the manifest, reward tables, or the same chapter concurrently. Reserve non-overlapping ID blocks before writing and keep a temporary ledger containing agent, chapter, quest IDs, task IDs, reward IDs, and localization keys. Use one integration owner to reconcile generated files, run the validator, render layouts, update Packwiz metadata, and stage the final diff. Parallel agents must never commit, merge, push, regenerate the full campaign, or revert other agents' work unless explicitly assigned that responsibility.

## Research and ID Verification

The installed pack is the source of truth. Before authoring any new objective or reward:

1. Inspect the Packwiz modlist and installed JAR versions.
2. Resolve the exact item, advancement, spell, image, and recipe IDs from the installed artifacts.
3. Copy task and reward syntax from a nearby working quest using the same task family.
4. Confirm whether the task observes inventory, consumes items, or relies on a trust-based checkmark.
5. Confirm personal versus team reward scope explicitly.

Do not guess an ID from a display name. Do not import SNBT from another modpack without adapting it to this FTB Quests version, installed mods, ID namespace, economy, and layout conventions.

## Layout Standard

- Render every edited chapter with `scripts/vvh_render_layouts.py`.
- Inspect the individual chapter image and contact sheet.
- Avoid node overlap, dependency-line crossings, extremely long lines, and branches that appear to reconnect incorrectly.
- Make the shared world-building spine visually dominant.
- Keep personal/faction progression as readable side branches.
- Use size, shape, icon, and spacing consistently to distinguish openers, labels, ordinary quests, specialties, and capstones.
- Test background art with the actual quest nodes over it. A good standalone panorama can still make icons unreadable.

Existing layout evidence is under `docs/vvh/evidence/layout-revision/`.

## Validation and Acceptance

Do not claim completion from text inspection alone.

### Static checks

- Parse every edited SNBT file.
- Check globally unique quest, task, and reward IDs.
- Check dependencies for missing nodes, cycles, reachability, and valid minimum-dependency counts.
- Check every localization key.
- Resolve every item, advancement, image, and spell reference against a materialized JAR/resource index.
- Verify reward scopes and counts.
- Verify choice-table semantics as one selected entry per choice claim; do not multiply exposure by `loot_size`.
- Verify choice tables #2–#4 contain no Bevels.
- Verify the weekly rumour is the only repeatable Bevel issuer and pays one per team per seven days.
- Calculate normal-route and completionist Bevel issuance.
- Calculate maximum weekly sink spending and ensure fallback income cannot self-fund the requisition board.
- Confirm no new VvH KubeJS quest logic appeared.
- Run `packwiz refresh`, then run it again to check idempotency.
- Run `git diff --check` and inspect the staged diff.

### Runtime checks

- Load the exact Packwiz pack in a disposable environment.
- Check logs for FTB Quests parsing, missing IDs, missing textures, and reward errors.
- Open every changed chapter and capture screenshots at a normal usable zoom.
- Claim one personal Bevel reward.
- Claim one team capstone reward.
- Exercise one Blood, Holy, and neutral magical objective.
- Complete one human-reviewed build objective.
- Use one choice reward.
- Test the weekly rumour as a solo player and as a shared team; verify the cooldown prevents a second claim.
- Test a paid Bevel requisition and confirm the input is consumed once.

The current `static-validation-bevel.json` was generated without a materialized mod JAR index and therefore reports unresolved mod item/image references. Those results are not proof of missing content, but they are also not a passing resource-resolution test. Re-run validation with the actual dev JAR index before release.

### Current verification status

| Layer | Current status | Required evidence before release |
|---|---|---|
| SNBT parse and graph audit | Historical evidence exists; new handoff adds identified graph repairs | Fresh validator report from the release checkout |
| Economy accounting | Live read-only audit: 18 normal personal, 50 completionist personal, 6 normal-route team, 14 all-branches team | Regenerated `BALANCE.md`, strict validator bounds, and an explicit 12-versus-14 team policy decision |
| Installed item/image resolution | Not currently passed by `static-validation-bevel.json` because its JAR index was not materialized | Fresh materialized JAR/resource index and zero unresolved references |
| Source-rendered layout | Existing review boards and contact sheets exist | Fresh renders for every edited chapter and a crossing/overlap review |
| In-client Prism layout | Not evidenced | Dated screenshots at usable zoom showing backgrounds, icons, branches, and text wrapping |
| Dedicated-server load | Historical smoke evidence exists | Fresh smoke result for any edited release surface |
| Solo/team reward scope | Not fully evidenced | Two-account claims for personal reward, team capstone, season seal, weekly fallback, and paid sink |
| Audio distribution | Local SUNO archive exists | Provenance/license note, normalized filenames, loop/transcode evidence, sounds registration, Packwiz metadata, and an in-client audio check |

## Working Tree Safety

At this handoff, the repository also contains unrelated untracked local material:

- `docs/vvh/SUNO_INSTRUMENTAL_PROMPTS.txt`
- `docs/vvh/evidence/static-validation-v5-check.json`
- `tmp/`
- `tools/`

Preserve these unless the user explicitly asks to add or remove them. Stage files explicitly. Do not use destructive Git cleanup commands.

## Supporting Audit Pack

The 2026-08-15 parallel audit produced focused evidence under `docs/vvh/handoff_work/`:

- `CANON_SOURCE_AUDIT.md`: source inventory, canon hierarchy, recovered motifs, and superseded rules.
- `LIVE_QUEST_AUDIT.md`: chapter-by-chapter graph, prose, layout, and extension-seam audit.
- `BEVEL_ECONOMY_AUDIT.md`: direct payout ledger, normal/completionist totals, repeatables, sinks, and policy drift.
- `DEPTH_DESIGN.md`: grounded project tiers, treaties, event cards, mastery, catch-up, mystery, and finale proposals.
- `ART_AUDIO_AUDIT.md`: current asset continuity, high-impact additions, provenance, and validation needs.
- `VALIDATION_RELEASE_RUNBOOK.md`: exact ordered validation layers and release gates.
- `HANDOFF_CRITIQUE.md`: hostile review of ambiguity, reproducibility, economy, canon, and parallel-authoring risks.

Read the relevant focused audit before editing that surface. These reports document evidence and proposals; the main handoff remains the integrated brief.

## Suggested First Assignment for the Next Instance

Begin with a read-only audit and then implement one contained vertical slice:

1. Audit Chapter 9's current Bevel sinks and calculate their actual value against recipes.
2. Resolve the repair gate above, especially stale balance copy and Chapter 6/7 dependencies.
3. Propose five attractive capped sink bundles with verified IDs and prices.
4. Implement two new sinks and improve two existing sinks.
5. Update localization, source authoring data, campaign manifest, and balance documentation.
6. Run static validation with the materialized JAR index.
7. Render and inspect Chapter 9.
8. Perform a disposable-client claim test before pushing.

After that slice is proven, proceed to three-stage public projects and treaty quests. This order creates immediate purpose for the currency before adding more ways to earn it.

## Definition of Done for the Expansion

The expansion is complete when:

- Players can name several things they actively want to buy with Bevels.
- Every major public structure has a use after its initial build quest.
- At least six quests require complementary social contributions rather than raw grinding.
- At least eight one-session events can be scheduled independently while feeding the same season arc.
- Blood, Holy, and neutral routes feel different but comparably valuable.
- Late joiners have a useful, non-tier-skipping path into current play.
- The finale showcases things players actually built and stories that actually happened.
- All SNBT, dependencies, localization, IDs, economy rules, assets, Packwiz metadata, and runtime loading have been verified with recorded evidence.
