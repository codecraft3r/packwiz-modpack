# Your Next Good Evening

The `dev` questbook adds 81 progression-aware quests across nine chapters. The 59 quests already authored on `dev` remain in **Previous Questbook**, with their quest, task and reward identities unchanged. This preserves newer repository work rather than replacing it with the older 56-quest server snapshot.

The brief is a fresh engagement-focused book with balanced adventures, machines and shared projects, adjusted for players who have already progressed far into the pack. Existing advancements count; an achievement holder must be online for FTB detection. Existing machinery can be inspected without dismantling or rebuilding it. New kill contracts require new kills. No world, inventory, bank or team reset is included.

## Routes

- **Start Here:** portable bank access, an optional combat warm-up, and an existing enchanting workshop.
- **Go Somewhere Worth Going:** photographs, printing, an End postcard, and new expedition destinations.
- **Boss Board:** thirteen boss-victory milestones plus Azazel's relic milestone. The installed Azazel advancement checks possession of a Manipulator Stick, not a recorded kill.
- **Build a Spell Loadout:** books, scroll crafting, equipment upgrades and optional faction mastery.
- **Machines That Change the Server:** recognition for established Create/Mekanism work, followed by automated crafting, QIO, steam improvements and controls.
- **Flight, Freight, and Arrival:** aircraft, passenger transport, trains, logistics and roads.
- **Places People Come Back To:** photography, food, friendship, workshops, shops and shared spaces.
- **Crew Contracts:** three boss rematches and a small cooking contract.
- **Spend It on Your Next Project:** thirteen paid supply parcels and specialist upgrades.

The five-player snapshot supports 20 retrospective milestones for one existing team and 13 for the other. The resulting forecast is 1,184 or 880 Spurs per teammate after detection and manual claiming. This is a one-time opening budget, not money already present in the bank. Team progress acknowledges access to a team's achievements; it does not claim every member personally accomplished them.

## Connected routes and credit

Every new quest is connected to the welcome route. Chapters use authored spines, forks and destination nodes, with small native Quest Links displaying relevant prerequisites from another chapter. Those links point to the original quest and do not create another claim or reward.

Milestone lines are suggested next steps: flexible progression preserves direct credit for achievements veterans already hold. Crew projects, contracts and purchases have enforced prerequisites through linear progression. Optional faction routes remain separate. The welcome quest explains the distinction.

## Economy and deliberate scope

New personal one-time currency has a 4,704-Spur completionist ceiling. There is no required route or minimum mandatory payout. Opposing faction branches mean the mathematical ceiling is not a normal expected path. Welcome and crew-confirmed checkmarks give useful items but **no currency**, following the repository's stronger rule for weak verification. Those social projects cannot repeat.

New repeat contracts have six-hour cooldowns, explicit shared rewards, and at most 480 Spurs per team per complete cooldown window. The mathematical weekly ceiling is 13,440 per team, or 67,200 across five independent solo teams; reaching it would require completing every boss/food contract in all 28 windows. This is a conservative issuance bound, not a participation prediction. The first Ignis contract requires the existing Ignis milestone; the Leviathan rematch requires its victory; the Dead King contract follows Catacombs discovery; cooking commissions require the feast milestone. Cooking also pays 16 shared Bottles o’ Enchanting per completion (448 per team at the weekly upper bound). Real reward claiming and team fragmentation still need playtesting.

Buying one of each new parcel costs 2,400 Spurs. Building/furniture parcels cost 32, ordinary spell supplies 64, airframe/rail parcels 128, advanced ink 192, enchantments 256, specialist upgrade orbs 384 and Legendary Ink 512. Orders have a 60-second purchase delay, explicit manual coin submission, and one shared reward set. Existing archive stores keep their reviewed prices, 180/300-second delays and weekly Rumour Ledger; the new source does not silently change those balances. The new shop does not sell the meals accepted by the cooking contract.

Recipe restrictions remain intact, including the disabled MekaSuit, Antiprotonic Nucleosynthesizer and Quantum Entangloporter. There is no new KubeJS quest logic, third faction, mandatory faction conversion, forced PvP or wipe framing. Optional shared projects need not involve opposing factions. Single-block observation deliberately recognizes already-installed equipment; it does not pretend to verify a complete multiblock or functioning program.

Every bulk reward is checked against the item's verified stack limit, with 37 item types covered by pinned registry/constructor evidence in `evidence/reward-stack-limits.json`. Singleton entries fit any valid registered item; no exact maximum is inferred for singleton-only rewards. The native ItemReward delivery loop also splits physical stacks, but that behavior is not used to excuse oversized authoring entries. Source evidence for 46 modded survival paths lives in `evidence/survival-paths.json`, including custom Icarus recipes and Lightning Bottles' charged-creeper interaction.

The graph correction enforces the ferry's modest, shared 16-envelope reward behind its equipment milestones by changing crew projects to linear progression. The preceding rules pass added the ferry dependencies but left flexible mode enabled, which bypassed that gate. Cooking already uses linear progression and remains gated behind the feast. Friendship awards seating rather than MCA's romance-triggering bouquet. The QIO milestone supplies a Mending book, and automated crafting supplies a full stack of andesite alloy. Quest titles are at most four words, prices must match consumed coins, and unsupported book components or repeatable one-time milestones block validation. See `GRAPH_REVIEW.md` for the current graph findings and `RULES_REVIEW.md` for the preceding economy review.

## Chapter artwork

All nine Frontier chapters have generated, route-aware atlas backgrounds attached through native FTB images. Artwork occupies the outer areas while the real quest graph remains interactive above it. The existing required resource pack supplies the PNGs; see `BACKGROUNDS.md` for placement, asset budget and client acceptance checks.

## Source ownership

1. `docs/frontier/quest-source.json` owns the 81 new quests.
2. `scripts/frontier_campaign.py` composes their chapters over `vvh_campaign_v3.py`'s reviewed legacy output. It changes archived chapter placement and titles and adds four visual prerequisite links; legacy quest objects remain identical.
3. The existing `vvh_campaign_v3.py` entry point, output hash ledger and staged-write guard own the combined generation. Calling the old command cannot erase the new book.
4. `scripts/frontier_validate.py` validates the new source, emitted files, full-book ID/dependency boundary, currency scopes and exact-artifact evidence. The existing VvH validator still checks its archived source and invokes the Frontier audit.
5. VvH's original ID catalog remains scoped to its reviewed archived content. Frontier has a separate pinned-artifact and live-query evidence ledger; unknown new namespaces are not accepted merely because the old allowlist omits them.

The live proof matches 27 namespaces to the exact downloaded JAR hashes pinned by Packwiz, including embedded Aeronautics/Simulated modules. The evidence includes native advancement criteria and read-only server registry queries. Player saves, coordinates, credentials and individual inventories are not included in this repository.

```sh
python scripts/vvh_campaign_v3.py --root .
packwiz refresh
python scripts/vvh_campaign_v3.py --root . --check
python scripts/vvh_campaign_v3_validate.py --root . --output /tmp/campaign-validation.json
python scripts/frontier_validate.py --root .
python scripts/vvh_sync_catalog.py --check .
python scripts/validate_snbt.py config/
python scripts/test_validate_snbt.py
python -m unittest discover -s scripts -p 'test_vvh*.py'
packwiz list
packwiz refresh
```

## Runtime status

The owner requested publication to the production branch, `master`, for the next server restart. Publication does not restart the server or install client resources. The live server is configured to pull `master`. Its installed FTB Quests build rejects editor commands from non-player sources, so a previous direct RCON hot-reload attempt restored the original server files. An authorized operator can reload the installed definitions while logged in, or the owner can arrange a restart. This commit does neither.

Static grammar, source synchronization, exact mod artifact matching and registry query evidence are distinct from playtesting. Still required before production promotion: open the new chapters in the real client; verify an existing advancement credits; claim one reward; test one order as payer and teammate; verify cooldown/reset behavior, team leave/rejoin claims and overflow; inspect the runtime logs. Source layout renders cannot prove client icons or text wrapping.
