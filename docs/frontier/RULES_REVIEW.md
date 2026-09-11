# Frontier quest rules review — September 11, 2026

**Historical review of `bfc416a`.** The subsequent graph pass found that the uniform grid and independent milestones were poor route design, and that flexible progression bypassed the claimed ferry prerequisites. Its earlier clean layout metrics did not establish a useful connected graph. See `GRAPH_REVIEW.md` for the correction and current verification. The figures below describe the earlier review.

Reviewed the 81 new quests against `skills/ftb-quest-authoring/SKILL.md`, both authoring references, `skills/snbt-validation/SKILL.md`, `docs/vvh/SERVER_RULES.md`, source authority, and the human quest preferences. The owner's balanced, progression-aware rebuild brief governs the new optional chapters; the preserved five-chapter faction campaign retains its existing rules and reviewed exceptions.

## Findings and fixes

| Finding | Correction |
| --- | --- |
| Bulk rewards were only capped at 64, despite the rule requiring each item's actual stack limit. | Added pinned registry/constructor receipts for all 37 bulk reward item types. Missing evidence fails closed. Singleton-only rewards use the safe bound of one item, without guessing their actual maximum. Film's 16-item limit and singleton Vista cassettes have regression tests. No existing bulk entry exceeded the verified limit. |
| Registry existence alone did not establish survival obtainability. | Added 46 direct modded task, observation and reward paths from pinned recipes/native interactions. Bound the custom Icarus recipe evidence to the KubeJS file hash. Lightning Bottles come from using glass bottles on charged creepers; no invented recipe or creative-only reward was substituted. |
| A future source edit could turn a paid order into a free inventory check, misstate its price, or make an ordinary milestone repeatable without failing the old audit. | Added explicit consumed/manual/positive coin-payment checks, price-to-denomination matching, one-time/repeat boundaries, income ceilings, and book-component/level checks. |
| Cooking income was open immediately and paid only currency. | Gate it behind the existing feast milestone; retain 32 shared Spurs and the six-hour cooldown, with 16 shared Bottles o' Enchanting for equipment upkeep. Neither meals nor their ingredients are returned. |
| A weak ferry check awarded 64 envelopes with no equipment prerequisites. | Require both flight equipment milestones, reduce the shared reward to 16 envelopes, retain explicit passenger attestation, and keep it nonrepeatable and currency-free. Move the node below its prerequisites so the lines do not run through another quest. |
| MCA's bouquet initiates a romantic relationship despite the friendship quest promising no required romance. | Replace it with four chairs for a gathering place. |
| Some advanced rewards were generic XP or small starter-material parcels. | Give a Mending book with the QIO milestone and a full stack of andesite alloy with automated crafting. These help equipment upkeep and further automation without handing out a decisive machine or boss drop. |
| Several descriptions implied manual contract acceptance or a stronger detector than the installed task provides. | Explain automatic fresh-kill counting while a contract is available; name both crossbows required by Hunter Technology; state that Automated Crafting checks possession of the Formulaic Assemblicator; distinguish food submission from delivery into a public chest. |
| Long graph titles and scattered implementation prose made the book harder to scan. | Shorten every new title to at most four words, retain useful completion instructions, and restate claims, consent, neutral opt-out and public entrances in the opener. |

## Economy and progression boundary

Currency budgets are unchanged: at most 4,704 new one-time personal Spurs, zero one-time team currency, and 480 shared Spurs per team per six-hour repeat window. The complete new purchase board costs 2,400 Spurs. The weekly repeat ceiling is 13,440 Spurs per team or 67,200 for five independent teams. The cooking XP addition has a separate ceiling of 448 bottles per team per week, or 2,240 across five teams. These bounds assume a fixed set of teams and require every cooldown window; they are not forecasts of normal activity. Team leave/rejoin claim handling remains a runtime acceptance check.

The stores do not sell the meals accepted by the galley. Their reward IDs do not directly overlap consumed contract inputs. The cooking recipes still require raw beef/crops, not the store's cooked steaks. No recipe or KubeJS change introduces coin minting or an NPC buyback. Inspection of the two installed Numismatics artifacts found no villager/emerald trade replacement references; the vendor economy exchanges player-funded balances. Player-set prices and future admin-created exchanges can still create arbitrage, so this is a review of the shipped book and current pack, not a universal economy guarantee.

Boss rematches retain kill-based fresh work and six-hour shared cooldowns. Dead King follows Catacombs discovery and requires a real boss kill; Ignis and Leviathan follow their corresponding victory milestones. Cooking follows the feast. No repeatable is a checkmark or a nonconsuming item test. Already-earned advancements still count in the optional milestone lanes, and no prerequisite chain forces veterans through the combat warm-up.

Finite reward continuity remains within the server rule: boss-earned ink may unlock the Legendary Ink recognition milestone; that is earned access to a material, not proof of a new boss kill. The specialist ink purchase requires that milestone and therefore cannot be the first direct source unlocking itself. Repeatable trades cannot pay their own coin input. The new chapter structure does not fake faction locks, force conversion or opposing-faction cooperation, or change Vampirism's faction state.

All 1,063 existing global chapter, quest, task and reward IDs from `a1368b2` are retained. One reward ID is added for the galley's XP bottles. All 59 archived quest objects remain identical to their authoritative source. The six disabled Mekanism equipment items remain absent from new requirements/rewards; no custom quest logic, world data or player data was changed.

## Verification and limits

- Authoritative generation/check-only pass, complete campaign semantic audit, catalog provenance and Packwiz checks pass.
- All 21 SNBT files parse. The grammar regression suite runs 34 tests with its existing one skip; all 50 campaign regression tests pass.
- New audit: 81 quests, 181 resource references, 37 bulk-stack receipts, 46 modded survival paths, zero errors. Complete book: 140 quests and 1,064 unique global IDs.
- Nine source layout renders have zero node overlaps, estimated label collisions, visible edge crossings or clipping. Reviewed the contact sheet and transport prerequisite layout. Placeholder icons in these source renders are not client asset evidence.
- Five pre-existing archive warnings remain visible: the four-Blood-Bottle baseline stack exception, two blood-bottle continuity overlaps, and the two recorded faction currency differences. This pass neither hides those warnings nor rewrites archived claim identities to remove them.

This is a dev candidate. Production has not been reloaded or restarted. Actual client rendering, existing-advancement credit, payer/teammate reward claims, cooldown/reset behavior, team leave/rejoin claims, inventory overflow and runtime logs still need an in-game check before promotion. Static parsing and read-only registry probes are not a substitute for that playtest.
