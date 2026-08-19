# Player-Facing Campaign Design

Read this reference when a request involves quest prose, onboarding topology, reward usefulness, persistent-world pacing, faction eligibility, trust-based tasks, or player complaints that quests feel broken, cluttered, railroaded, or trivial.

Treat named mods, factions, currencies, and chapter numbers from prior packs as examples only. Re-discover the current pack's recipes, task support, progression state, and economy before applying the principles.

## 1. Player-facing prose

Quest text belongs to the player experience. Do not put design guarantees, balance assertions, implementation status, validator notes, administrative reasoning, or phrases such as "this is intentionally balanced" into titles, subtitles, or bodies. Put those facts in authoring notes, manifests, comments, or validation reports.

Use the quest book as a framework for player-created stories inside a sandbox:

- Prefer roles, choices, public works, conflicts, handoffs, and consequences that players can make their own.
- Do not invent an elaborate fixed cast, town history, or canonical plot unless the user explicitly requests authored lore.
- If lore is desired, keep it local and actionable: a disputed record, a place players actually built, an unresolved pressure, a witnessed failure, or a public promise.
- Do not restate the objective as lore. Lore supplies motive or consequence; the task states the action.

A strong quest body answers, in natural player-facing prose:

1. Why should I do this?
2. What does this action enable, improve, or unlock?
3. What changes for me, my team, or the world afterward?

Keep one quest focused on one coherent action or outcome. Use one continuous body by default. If the body needs several headings, a long checklist, or multiple unrelated bullet groups, split it into smaller quests. A short build standard or proof sentence is acceptable when the action cannot be understood without it.

Keep graph titles short, normally two to four words. Move lane labels, difficulty, suitability, and explanatory qualifiers into subtitles or descriptions. A price, cooldown, or consent warning may remain in the title when omitting it would mislead the player. Render the graph and set a pack-appropriate title-length ceiling; crowded or multi-line labels are a defect even when the SNBT parses.

## 2. Persistent world versus seasonal framing

Identify the intended lifetime before naming chapters or capstones.

For a persistent SMP:

- Frame progress as civic milestones, durable infrastructure, institutions, specialties, services, archives, maintenance, and new pressures.
- End a chapter by opening the next layer of play, not by declaring the world finished.
- Avoid "season finale," "wrap-up," "aftermath," or wipe-cycle language unless the user explicitly uses seasons as an in-world organizational device and confirms that it will not imply a reset.
- Give completed work a maintenance owner, public use, future extension, or next operator so it remains relevant.
- Prefer emotional investment in player-built places over a prewritten conclusion.

For a genuinely seasonal/event pack, finale language is fine, but it should match the real cadence and deployment plan.

## 3. Topology must match meaning

Classify each decision as mandatory understanding, optional choice, or breadth selection before drawing dependencies.

### Closed-loop onboarding

Rules, safety policy, claims boundaries, team semantics, eligibility rules, and other mandatory onboarding form a closed loop:

- The opener branches into every required clause.
- The final acknowledgement depends directly on every required clause.
- Required clauses are not marked optional.
- If onboarding is meant to gate the campaign, every later chapter descends from its terminal acknowledgement.
- Simulate the shortest path and prove that no clause can be skipped by reading one sibling or clicking the final checkmark.

Do not reward players for agreeing to unread rules. Rule acknowledgements may use checkmarks, but the dependencies must prove that all required reference nodes were traversed.

### Open choice branches and faction campaigns

Factions, specialties, professions, and optional play styles may fan out:

- For multi-faction packs, organize starting progression into four foundational chapters:
  1. **Introduction & Rules:** Compact, closed-loop onboarding for rules and claim boundaries.
  2. **Choosing a Faction:** Symmetrical presentation of the core factions alongside an explicit, protected Neutral / Civic path.
  3. **Primary Faction A Line:** Core progression, palette builds, and claim-safe rivalry.
  4. **Primary Faction B Line:** Symmetrical progression, palette builds, and claim-safe rivalry.
- Place equivalent choices symmetrically around a clear center or spine.
- Put the neutral/default route on the center axis when the visual logic is a three-way choice. Give neutral players practical survival jump-starts (full iron armor and tools, bed, food, currency) rather than token items, and protect them from faction combat/pranking quests.
- Re-converge parallel specialties at an explicit any-N-of-M breadth gate when cooperation or team composition matters.
- Do not force every specialty merely because the graph reconnects.
- Separate short-term starter/world tasks from longer workshop, progression, or charter milestones.

A graph can be acyclic and still lie about choice. Validate actual minimum paths and inspect the rendered layout.

## 4. Completion criteria and immediate feedback

Substantive progression should use a hard native criterion whenever possible: items, blocks, advancements, statistics, entities, recipes, or another task type confirmed in the installed FTB Quests version.

Detect faction joining via native items and advancements (e.g. vampire fang / garlic injection + native mod advancements) rather than invented lore rituals.

### Palette quests versus untrackable multiblock placement

FTB Quests cannot reliably verify multi-block structures placed in the world. Rather than creating frustrating or impossible placement tasks:
- Require gathering or crafting an accessible starter palette of thematic blocks (e.g. stone bricks, logs, fences, lanterns; avoiding tedious materials like tinted glass or soul lanterns in early/mid game).
- Reward with abundant matching building blocks (2x-3x multiplier, stonecutter) plus high-value crafting materials (diamonds, iron, obsidian, andesite alloy).
- This establishes a clear visual theme so players build authentic faction architecture instead of random sheds, provides ample stock to build, and provides genuine progression rewards.

For workstations and progression altars, detect acquisition/crafting of the core item components and tanks in inventory, not world assembly.

Use a trust-based checkmark only when native detection is unsuitable, especially for builds, social agreements, tours, demonstrations, or human review. A checkmark-only quest should normally satisfy all of these:

- It is optional, explanatory, social, or primarily world-building.
- Its prerequisites represent meaningful effort, or its reward is modest.
- Server currency is not its primary reward.
- The text tells the player exactly what clicking the checkmark attests.

Never ship a placeholder action that looks functional. If a starter-kit choice, faction registration, or social service has no delivery/verification mechanism, implement a verified native choice/checkmark, explicitly mark it as a manual attestation, or remove/hide it until ready.

For every item-oriented task, make the semantics explicit:

- **Inspect/carry:** the item must be in inventory and is not consumed.
- **Submit/hand in:** the item is consumed.
- **Place/build:** the player uses it in the world; normally verify with a checkmark or supported block task rather than charging a duplicate bundle.
- **Public stock contribution:** consumption is intentional because the item becomes shared supplies.

Advancement and faction triggers must be tested for late joins, team sync delay, already-completed state, and faction switching. If a reliable native trigger cannot be proven, provide a clear manual fallback or redesign the gate.

Do not create progression tasks that auto-complete from rewards handed out immediately beforehand. Test a mod mechanic, crafted output, advancement, installed workstation, or later consequence rather than simple possession of the free prerequisite.

## 5. Eligibility, claim safety, and anti-conditions

Every visible quest must be completable by at least one intended player, and the UI must not present currently impossible work as ordinary active progression.

- Keep playful conflict, sabotage, and reconnaissance quests strictly claim-safe under FTB Chunks / FTB Teams protections. Never mandate griefing, invasion of claimed chunks, or untrackable mock duels. Use tangible, survival-friendly mechanics (such as black-and-white photography via Exposure camera and film for recon/propaganda, harmless throwables, or craftable prank tools).
- Respect neutrality: neutral players and civilian crafters are left alone unless they actively provoke conflict; do not target them in faction rivalry quests.

When a quest requires a mutually exclusive faction/class/state:

1. Verify whether the shipped FTB Quests/mod integration can hide or gate it against live state.
2. If supported, apply the condition so ineligible players do not see it as currently completable.
3. If unsupported or unreliable, avoid a hard anti-condition. Use an accessible alternative, a faction-neutral proof, an optional lore marker, or a clearly separated route that does not block the player.
4. Test switching, team membership changes, already-earned advancements, and single-player behavior.

Never claim a faction lock exists because the description says so. Copy is not synchronization.

## 6. Reward usefulness and thresholds

Reward value is measured by what the player can do with it now, not by rarity or thematic relevance alone.

Be as generous as the verified challenge and current progression band safely allow. A reward should feel earned, immediately useful, non-compounding, and comparable across factions. Substantive quests should normally pair central currency with a useful thematic item or choice bundle; omit the item only when no safe bundle exists.

### Survival obtainability

Verify that every task and reward item is obtainable in regular survival gameplay. Never award backend, internal, or creative-only items (such as blank scrolls or debug items). Keep domain-specific utility items in their intended lanes (e.g. Create super glue belongs to Create/aeronautics quests, not generic building or faction rewards).

### Central currency and dynamic scaling

When the pack/server has a central issued currency—such as Create: Numismatics Bevels—use it as the default reward for substantive one-time progression only when desirable server-controlled sinks exist.

- Standard quest progression should be the fastest normal source.
- The currency should let players choose what is valuable to them.
- Scale currency rewards dynamically across the quest tree: do not pay flat starter pocket change (1-2 low coins) on deep milestone quests. Increase coin volume or step up coin denominations (e.g., Bevel -> Sprocket -> Cog -> Crown) as quests advance deeper.
- The server must exchange it for useful goods, infrastructure, services, cosmetics/status, or capped progression support.
- A currency with no sinks is decorative clutter.
- Thematic items should usually supplement currency, not replace it with a weaker random object.

### Full-set threshold rule

Inspect real recipes and the current progression band before choosing quantities. Award enough to cross a useful threshold: complete one relevant craft, start one meaningful service, operate a workstation, or make a visible contribution.

- **Full Gear Sets:** If awarding specialized materials (such as armor runes or portal obsidian), award enough to craft a full functional set (e.g. 4 runes for a 4-piece armor set, 16 obsidian for a nether portal with corners, 2 blood-infused iron + 2 iron blocks for a weapon) rather than a frustrating single fragment.
- **Meaningful Consumables:** Provide consumables and crafting supplies in high-utility batches (e.g. 16 rare ink + 4 epic ink, animal leads + pen fencing alongside blood altars, brewing stands + potion supplies for alchemy) rather than token scraps (2 common ink, 1 stake, 4 emeralds).
- **Practical Spells:** For magic mods (like Iron's Spells), award useful early/mid utility and combat spells (e.g., Heal, Smite, Recall, Spectral Hammer, Blood Slash) rather than non-existent or game-breaking spells.

Do not scatter tiny amounts of future-tier materials through early onboarding. They occupy storage, advertise distant progression, and feel like speedrun bait without enabling play.

### Stage and variety

- Early rewards should solve immediate friction: food, navigation, survival, a usable starter tool, or a complete introductory kit.
- Mid-game rewards should save time or unlock choice: recipe-scale materials, workstation components, transport, construction support, or currency.
- Late-game/capstone rewards should feel consequential: significant currency, specialized machinery, high-value service bundles, permanent-but-balanced perks, substantial public construction support, or rare cosmetic/status rewards.
- Do not pay late milestones with loose torches, token scaffolding, or one or two generic raw materials.
- Avoid repeating the same utility in adjacent quests. If one quest gives lighting, the next should solve a different problem.
- Building rewards should support structure and function, not encourage decorative spam. Prefer structural blocks, utility furniture, storage, transport, or a deliberate choice bundle over repeated light sources.
- One-time quests may be the fastest route to selected resources if the payout is earned, finite, non-compounding, and comparable across factions.

### Repeatables

Repeatable currency sources are fallback income, not the primary progression engine:

- Gate them behind substantial one-time progress or campaign completion.
- Use a meaningful cooldown, team scope, cost, stock, or other native limiter.
- Model one shared team and fragmented solo teams.
- Ensure repeatables cannot outpace normal play, self-fund the full sink board, or compound into the dominant strategy.
- Test that no reward reproduces its own input.

## 7. Review matrix

Before release, answer all of these with evidence:

| Area | Required proof |
| --- | --- |
| Player voice | No admin/design guarantees or implementation commentary in player text |
| Focus | One coherent action/outcome per quest; oversized lists split |
| Purpose | Text explains motive, effect/unlock, and consequence |
| Lore scale | Fiction supports player agency and does not overwrite the sandbox without explicit request |
| Titles | Graph labels remain short and readable in a source render and the client |
| Mandatory topology | Every required rule/onboarding clause reaches the terminal gate |
| Optional topology | Specialty/faction choices are symmetric, optional as advertised, and reconverge correctly |
| Criteria | Substantive progression uses hard native checks where possible |
| Trust checks | Optional/explanatory or modestly rewarded; explicit attestation; no default currency payout |
| Palette quests | Building incentives use item gathering + stock multipliers/crafting rewards instead of untrackable multiblock placement |
| Claim safety | Prank, conflict, and recon quests respect FTB Chunks protections (e.g. photography via Exposure) |
| Task semantics | Inspect, consume, place, and contribute are unambiguous |
| Functional feedback | No placeholder or unresponsive task; choice rewards actually deliver |
| Survival check | All tasks and rewards verified obtainable in regular survival (no backend/creative items) |
| Eligibility | No visible quest is impossible for its intended current audience |
| Full-set threshold | Specialized crafting materials meet full-set requirements (e.g. 4 runes for armor, 16 obsidian for portal) |
| Reward threshold | Every item bundle enables a real craft, service, or current-stage contribution |
| Reward variety | Adjacent quests do not repeat filler; late milestones are not paid in starter scraps |
| Currency scaling | Progression issuance scales with quest depth; sinks, repeatables, cooldowns, and team fragmentation are modeled |
| Autocomplete | A prerequisite reward cannot trivially complete the next progression test |
| World lifetime | Finale language matches persistent versus seasonal intent |
| Runtime | Edited task types, advancement/faction state, choice delivery, and visibility are tested in a disposable client/world |

Record static, server, client, and multi-account evidence separately. A rendered source graph proves geometry and copy density, not runtime completion behavior.

