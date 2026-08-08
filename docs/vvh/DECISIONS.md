# VvH Decisions — dev retune

## D-001 — Vampires and Hunters are now real Vampirism factions

- Previous campaign assumption: no Vampirism faction mod was installed, so Vampire/Hunter were purely civic identities.
- New evidence: dev ships Vampirism 1.10.12 plus Godly Vampirism, Vampire's Delight, integrations, and Iron's Spells compatibility. Exact `become_vampire` and `become_hunter` advancements are present in the installed JAR.
- Corrected decision: the allegiance chapter now uses real Vampirism faction-entry advancements and the foundation chapters use actual faction workstations/resources.
- Player-facing effect: faction choice has genuine mechanics while the quest campaign still pushes those mechanics toward buildings, hospitality, routes, public service, and stories instead of a kill ladder.
- Migration: old VvH artifact should not be installed over dev; use this retuned drop-in.

## D-002 — Vampirism faction state and FTB Teams state remain separate

- Evidence: the installed systems do not provide a proven native synchronization layer between Vampirism factions and FTB Teams quest/claim parties.
- Decision: do not invent one in KubeJS. FTB Teams owns quest progress/claims; Vampirism owns supernatural faction state. Shared foundation-cache claims require a short peer/host confirmation of current alignment.
- Important nuance: `become_vampire` / `become_hunter` advancements are historical achievements. They do not erase themselves if a player later changes faction, so they cannot be treated as permanent live-state locks.

## D-003 — Keep Neutral as a full path

- Evidence: the product brief explicitly needs neutral traders, mediators, mercenaries, and diplomats.
- Decision: Free Companies have the same five-of-seven foundation workload and the same utility cache as the supernatural factions, using contracts, markets, routes, MCA civic play, rescue, and mediation.

## D-004 — No dynamic faction reward multiplier

- Original draft: reward scaling up to 2× based on active faction population.
- Decision: rejected again. Vampirism itself now supplies faction differentiation, making an extra loot multiplier even less necessary. Dynamic scaling would accelerate progression, complicate faction switching, and make neutral play economically second-class.
- Replacement: fixed reward classes—personal keepsakes/favors, one team utility cache per foundation/public milestone, and priced/cooldown-limited postgame requisitions.

## D-005 — Preserve and migrate Living Atlas object IDs

- Evidence: dev removed Cobblemon but still shipped old Atlas files containing `cobblemon:` tasks, icons, images, and rewards.
- Decision: repair those pages in-place and preserve existing quest/task/reward IDs so saved FTB quest progress remains attached.
- Player-facing effect: old pages now point to Vampirism/Create/current social objectives instead of deleted systems.

## D-006 — Creative work is human-reviewed

- Original draft: automated block-count scans for houses/vehicles.
- Decision: rejected as too brittle for modded blocks, contraptions, unusual architecture, and moving vehicles. Creative projects use concise function/access/safety/story/maintenance rubrics and checkmarks with two-player peer review or one host review.

## D-007 — Noncombat rivalry must precede any skirmish

- Decision: the optional skirmish is gated behind at least two completed noncombat rivalry formats. It can never become the first or default expression of faction identity.
- Rewards are participation/story supplies only; kills and wins grant no progression power.

## D-008 — No destructive reset automation ships in the quest package

- The original reset-zone concept remains operationally useful, but safe chunk regeneration across every dev mod was not proven by the quest build itself.
- Decision: document zones and recovery procedures; do not ship a destructive reset script merely because the pitch imagined one.
