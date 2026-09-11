# Connected quest maps — September 11, 2026

The owner's follow-up exposed a design and validation failure in `bfc416a`: most milestones were independent nodes in a uniform grid, and the validator prohibited dependencies on those milestones. A clean crossing count on that sparse graph did not establish a useful questbook. This pass replaces that design with authored routes and checks the resulting connections.

## Native behavior and corrections

The exact Packwiz-pinned FTB Quests build is `2101.1.33`. Its `TeamData.canStartTasks` bypasses dependency completion in flexible progression, and `Quest.isCompletedRaw` uses that check. Dependencies in flexible mode therefore guide a route but do not enforce access. The prior ferry gate was not effective while flexible mode was set; contracts and orders already used linear progression.

- Existing-advancement and equipment milestones stay flexible, with meaningful suggested progression lines. Veterans can credit achievements they already hold without replaying earlier nodes.
- Crew projects now join repeat contracts and paid orders in using linear progression. Their immediate prerequisites must complete before their tasks start. The ferry requires both aircraft equipment milestones; cooking requires the feast; boss rematches and specialist purchases retain their relevant gates.
- Cross-chapter dependencies have native `quest_links` with stable unique IDs. Each link references an existing quest through `linked_quest`; it does not copy a task, create another completion or issue another reward. The installed `QuestButton.buildDependencies` resolves link buttons through their underlying quest, so these are native line endpoints.
- All Frontier dependency lines are visible. Opposing faction paths remain separate, and ordinary purchases do not require buying another parcel first.

The pinned metadata, artifact hash, shipped shape names and native method evidence are recorded in `evidence/graph-runtime.json`. The generator emits explicit coordinates, sizes and shapes instead of assigning an automatic grid. The validator checks reachability, cycles, real link targets, source/output agreement and progression modes; renderer regressions check actual lines, node footprints and labels.

## Authored routes and shapes

The adventure maps now branch from clear entry points; magic and engineering use vertical workshop routes; transport forks between flight and rail and rejoins at the ferry project. The Boss Board groups encounter routes around destination links. Contracts show four separate prerequisite/rematch pairs. The supply board separates its open supply fan from a descending specialist workshop route. Several local lanes can belong to one globally connected book without forcing unrelated encounters into a mandatory chain.

Circles mark introductory discoveries, squares equipment and orders, gears working systems, diamonds route destinations, hexagons major encounters or advanced milestones, and hearts social or character milestones. Native cross-chapter links are smaller diamonds. These are visual cues; progression mode determines whether the displayed prerequisites are required. All authored shapes exist in the pinned FTB resource bundle.

## Save and economy boundary

This correction preserves quest, task and reward identities, reward contents, payment amounts and repeat cooldowns. Additional IDs belong only to visual Quest Links. All 59 archived quest objects retain their reviewed source, including protected coordinates and the archive Market's deliberate hidden dependency lines. Four native links now display the existing external prerequisites above the archive chapter entry nodes; those chapter-level additions leave the quest objects intact.

## Verification

- All 81 new quests are reachable from welcome; the full 140-quest dependency graph has no cycles or unresolved references.
- 24 Frontier links and four archive links are added. All 1,064 prior global IDs remain, for 1,092 total. All 140 task/reward arrays are unchanged; all 59 archived quest objects remain identical.
- The nine Frontier maps render 94 visible dependency segments, with zero node overlaps, estimated label collisions, crossed or overlapping edges, lines through unrelated node footprints, missing endpoints or clipped labels. The complete 14-chapter geometry also has no node overlaps, crossed edges, node interceptions or missing endpoints.
- All 63 campaign regression tests pass. All 21 SNBT files parse; the grammar suite passes 34 tests with its one existing skip. Generation, source synchronization, complete semantic audit and catalog checks pass. Packwiz refresh/list checks pass.
- Currency remains 4,704 personal one-time Spurs, zero shared one-time currency, 480 per team per six-hour repeat window and a 2,400-Spur complete purchase board. The five pre-existing archive economy/stack warnings remain reported.

See `evidence/layout-summary.json` for per-chapter geometry and the source hash. Selected pinned mod textures improve the diagnostic renders; unresolved vanilla/dynamic icons still require a real client check.

## Runtime acceptance

Source diagrams are diagnostic artifacts, not Minecraft client captures. Before production promotion, open the chapters in the pinned client, follow cross-chapter links, confirm existing advancements credit through flexible routes, and test a locked project/contract/order before and after its required milestone. Retain the two-account payment, reward, cooldown, overflow and team-change tests listed in the README. This dev push does not load the new book on production or restart the server.
