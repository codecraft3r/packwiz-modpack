---
name: ftb-quest-authoring
description: Design, implement, balance, validate, and release FTB Quests chapters for any Minecraft modpack. Use when an agent must turn a modlist, player goals, progression state, economy, or art assets into playable quests; edit or generate FTB Quests SNBT and localization; audit quest graphs, layouts, reward economies, or image paths; run static and in-game checks; or prepare a Packwiz/Git release. Treat the installed pack as the source of truth and avoid custom KubeJS by default.
---

# FTB Quest Authoring

Build quests that give a server a reason to play together without letting a grinder, a lucky drop, or a reward loop decide who wins. Keep the method pack-agnostic: discover IDs, recipes, currencies, task syntax, and art conventions from the supplied pack instead of carrying assumptions from another pack.

## 1. Establish the brief

Collect only the missing decisions that could change the design. Record:

- audience, active headcount, expected absences, and veteran/new-player mix;
- current progression (tools, armor, machines, bosses, Pokemon/creatures, magic tiers, and known outliers);
- preferred activities and activities the group avoids;
- social shape: solo, teams, server-wide cooperation, or optional competition;
- cadence: one-session events, a linked week, or a longer chapter; typical session length;
- challenge and gating: casual, meaningful, or expert; optional, guiding, or mandatory;
- reward currency, existing sinks, and rewards that would damage the economy;
- desired art/lore polish and the acceptance test (local parse, server smoke test, or live playtest).

Do not repeat answers already present in the request. If a high-impact value is unknown, state a reasonable assumption and make it easy to revise.

## 2. Inspect the actual pack before writing

Use the repository and installed artifacts as the authority.

1. Check git status and preserve unrelated work.
2. Locate the modlist/version files (pack.toml, index.toml, launcher manifests, or equivalent) and list the installed mods. Prefer the pack's existing helper scripts and packwiz list; run packwiz refresh after edits when Packwiz is present.
3. Identify the authoritative authoring representation before writing: live SNBT/localization, a generator, or another source model. Compare generated output with live files. Never run a whole-campaign generator over richer authored files merely because the generator exists; update it, generate into a scratch directory for review, or protect it behind an explicit overwrite flag.
4. Read several existing FTB Quests chapters, reward tables, translations, and resource-pack definitions. Copy their SNBT shape, ID conventions, layout, and version-specific fields rather than inventing a new dialect.
5. Resolve every proposed item, block, entity, advancement, statistic, recipe, currency, and reward from actual JARs, data packs, configs, recipe viewers, or authoritative mod docs. Never guess an ID because its display name looks plausible.
6. Inspect kubejs/ only to understand available behavior. Do not add custom KubeJS for quest logic unless the user explicitly changes that requirement.
7. Inventory image references and the JAR/resource-pack paths that can satisfy them. Keep resource paths POSIX-style (/) even when working on Windows.

If the pack has no existing quest examples, use the FTB Quests version shipped by the pack and validate a tiny throwaway chapter before building the full one.

## 3. Design the chapter around the server

Translate the brief into a compact loop:

1. Hook/session opener - a short, completable first quest that explains the fiction and gives a useful but non-snowballing nudge.
2. Choice routes - usually three to five routes across the group's preferred activities. Make routes roughly equivalent in time and power, not identical in materials.
3. Shared or capstone moment - a co-op build, raid, expedition, showcase, or other event that creates a story without forcing every player to grind the same item.
4. Utility sink - a repeatable, clearly priced exchange using the pack's real currency. Give player choice among convenience, infrastructure, cosmetic/status, and modest combat/collection help.

Use dependencies and "complete any N of M" patterns to reward breadth without making attendance a prerequisite. Separate personal progression from server-wide milestones. Use honor-system checkmarks for social/build/showcase verification when no standard task detector exists.

### Graph-truth rules

- For a true any-N-of-M gate, attach all M alternatives to the same intended predecessor, make the capstone depend on all M, and set its minimum to N. Simulate the shortest path: a hidden shared prerequisite must not turn “any three” into “this mandatory quest plus three.”
- Mark non-gating side quests with the installed schema's explicit optional flag when available. Being absent from the main capstone dependencies makes a quest mechanically optional, but may not communicate that in the UI.
- Keep world-building, equipment/workstations, and mod progression as visibly separate lanes when they serve different player motivations. Do not disguise a build as an item tutorial.
- Re-check reachability, dependency direction, minimum counts, and layout after every graph edit; a parseable acyclic graph can still express the wrong progression.

Balance against the slowest regular player and the server's current state, not its most advanced outlier. Let questing make life meaningfully easier while preserving the value of ordinary play.

### Anti-runaway rules

- Avoid currency-positive loops, buy/sell arbitrage, duplication routes, and rewards that generate their own input.
- Do not skip an entire progression tier, hand out early armor/rare drops, or make one route strictly best.
- Cap repeatable value by cooldown, price, stock, or a weekly/server milestone; choose the least disruptive limiter supported by the installed schema.
- Prefer player choice over a single optimal reward and keep team rewards intentional. Decide whether progress and rewards are individual or team-scoped for every quest.
- Give catch-up utility (tools, ingredients, transport, information) rather than a permanent power lead.
- Budget the worst-case reward if every active player completes every repeatable quest.
- Keep separate ledgers for one-time personal issuance, one-time team issuance, the minimum intended route, completionism, repeatable income, and paid sinks. Model team fragmentation as well as one shared team.
- Treat a native choice claim as the number of entries the installed implementation actually grants. Do not multiply currency exposure by unrelated table metadata such as display/loot size without verifying the semantics.

Write titles, descriptions, and lore in a specific human voice. Name the action, the reason it matters, and the next useful choice; do not pad the chapter with generic "collect X" text.

## 4. Implement with native FTB Quests features

Copy a nearby working SNBT object and change the smallest possible surface area. Keep IDs unique, stable, and easy to trace. Use only task/reward types supported by the installed FTB Quests build.

- Use item/block/entity tasks for observable inventory or world state.
- Use advancement tasks for mod progression; include the schema-required criterion field (an empty criterion commonly means the whole advancement, but verify against the installed version).
- Use stat tasks only with a real statistic ID and text that matches its trigger (for example, a battle-start statistic should say "enter/start a battle," not "win").
- Use checkmark tasks for trust-based completion, social verification, or a human-reviewed build rather than introducing a script.
- For a human-reviewed build, do not also consume a duplicate material bundle unless the quest is intentionally a donation. Placed blocks already cost resources; an extra consumed task can charge players twice. Use a non-consuming item preview, a checkmark, or a deliberate public-stock contribution.
- For an any-of-many branch, set the installed schema's minimum dependency count and test the actual shortest and maximum paths.
- Set an explicit optional quest flag for side stories when supported; do not rely only on the absence of downstream dependencies.
- For a repeatable currency exchange, make the input an item task that consumes exactly the displayed price, set a deliberate cooldown, and set team_reward deliberately on every reward. A team-scoped task can let one payer unlock rewards for others if this is left implicit.
- Use existing reward tables or native item/command/reputation rewards. Resolve every item component, count, and namespace before committing.

When multiple agents author in parallel, assign exclusive chapter/file ownership and reserve non-overlapping quest, task, and reward ID ranges. Keep localization, manifests, indexes, and shared reward tables under one integration owner. Subtasks should not regenerate the campaign, commit, push, or revert another worker's edits unless explicitly assigned.

Read references/ftb-quests-patterns.md for portable templates and an audit checklist. Treat examples there as patterns, not as pack-specific IDs.

## 5. Add art without creating fragile assets

Reuse the pack's existing resource-pack namespace, dimensions, typography, and naming. Add custom art only when it improves orientation or the emotional beat of a quest.

- Keep image namespace:path references exact and use forward slashes.
- Put files at the path the client actually loads; check case and extension.
- Validate pack.mcmeta for the target Minecraft version and update hosted asset metadata/digests whenever a .pw.toml points to a new release.
- Search every quest image reference across the JARs and resource-pack ZIPs; a visually polished chapter with one missing texture is not complete.
- Distinguish an unresolved custom-resource reference from an unresolved built-in mod/Minecraft texture. A renderer given only a custom resource ZIP cannot prove native textures are missing; validate each namespace against the resource source that owns it.
- Do not commit generated binaries that the pack's distribution rules exclude; publish large assets through the project's established release mechanism.

## 6. Validate before calling it done

Run the narrowest useful checks, then expand them in proportion to risk:

1. Repository/Packwiz: inspect the diff, run packwiz refresh and packwiz list when available, then run refresh a second time and confirm the index hash is stable. Confirm only intended files changed.
2. SNBT/schema: parse the edited files with the pack's parser or a supported FTB Quests loader. Check unique IDs, valid task/reward types, required fields, resolvable namespaces, dependency acyclicity, reachable quests, and translation keys.
3. Graph/layout: verify the advertised any-N-of-M minimum by simulation, not hand-counting. Render each edited chapter, detect node overlap and dependency-line crossings, and inspect the central spine, side-lane direction, labels, background contrast, and long text. A source render is review evidence, not an in-client screenshot.
4. Economy: calculate minimum-route and completionist one-time issuance separately for personal and team rewards. Calculate worst-case repeatable issuance, fragmented-team issuance, and the cost of the complete sink board. Test that no reward can reproduce its input, self-fund the board, or dominate normal play. Count choice rewards using verified claim semantics.
5. Assets: resolve all icons and images against actual client resources, check ZIP entry separators, verify Packwiz hashes, and confirm no stale URL/digest remains.
6. Source synchronization: regenerate or synchronize derived manifests/localization/indexes from the chosen authority, run a check-only/idempotency pass, and prevent a stale generator from clobbering live content.
7. KubeJS boundary: confirm no custom quest logic was added. If existing scripts are involved, test them as-is and document the dependency.
8. Small playtest: load a disposable world/server, open the chapter, claim the opener, complete one task from each task family used, trigger advancement/stat tasks, complete the minimum dependency path, run one repeatable exchange, and inspect the result as both a payer and a teammate. Check logs for parser, missing-ID, or reward errors.
9. Failure evidence: record commands, exit codes, screenshots/log excerpts, and the one remaining manual check. Do not report a playtest as successful when only static text inspection happened. State separately whether static parsing, server loading, client visual inspection, and two-account reward testing passed or remain pending.

## 7. Ship safely

Update translations, changelog/version metadata, Packwiz indexes, and hosted asset references only when the change requires them. Stage only the quest/art/release files in scope. Fetch the target branch before committing or pushing; if it advanced, inspect and integrate it without discarding unrelated work, then refresh Packwiz metadata again. Commit with a focused message, push the requested branch, and use a draft pull request unless the user explicitly asks for a merge. Preserve existing tags and unrelated user changes.

## 8. Hand off clearly

Report:

- the chapter's player-facing loop and intended audience/progression band;
- files changed and any new asset URLs/digests;
- validation and playtest results, including what was not run;
- economy guardrails and team-scope decisions;
- the branch/commit/PR or release link and the next safe playtest step.
