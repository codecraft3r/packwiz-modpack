# VvH Administrator Runbook

## Launch

1. Back up world + FTB quest/team data.
2. Verify the live pack commit matches the release being deployed.
3. Run `packwiz refresh`; an unexpected diff means the checkout is stale or incompletely copied.
4. Launch a disposable server and inspect FTB Quests loading before touching the live world.
5. Open all VvH pages on a client and verify the current Poiesis art release is present.
6. Publish the permanent-building boundary. Do not advertise automated resets until separately proven on disposable chunks.

## Faction onboarding

Vampirism and FTB Teams are separate systems.

- Vampirism Vampire/Hunter state determines supernatural mechanics.
- FTB Teams determines shared quest progress and FTB Chunks ownership.
- Finish the personal Charter before joining a shared faction FTB party when practical.
- House of Night and Lantern Order foundation caches require a second player/host to confirm the FTB team is presently aligned with the claimed Vampirism faction.
- A past `become_vampire` / `become_hunter` advancement is historical evidence only; do not use it alone to approve a post-switch cache.
- Blood and Holy materials reinforce the House and Order stories but remain usable by any player. Free Companies use the translation desk for limited cross-school utility; no KubeJS state bridge or hard school lock exists.
- Free Companies use personal/neutral FTB parties unless the server intentionally creates a shared neutral company.

## Faction switch

1. Record old Vampirism faction, FTB party, claims, shared storage obligations, contracts, and public-project ownership.
2. Complete the actual Vampirism cure/betrayal/switch process through normal mod mechanics.
3. Before leaving the old FTB party, remove personal items and identify who owns each claim/public responsibility.
4. Change FTB party only after the claim plan is understood.
5. Verify quest progress/reward visibility after the switch. Do not reset old foundation quests to mint a second cache.
6. The old charter remains historical. Complete the new branch/foundation only when the new team does the actual work.

Exact claim-transfer behavior still **requires runtime verification** with disposable accounts on the live config.

## Creative review

A project passes with two-player peer review or one host review using:

1. Function — does the stated service actually work?
2. Access — can intended users reach/use/understand it?
3. Safety — does it avoid obvious grief/entity/TPS hazards?
4. Story — is it named, contextualized, or connected to server life?
5. Maintenance — is an owner/rotation/restock expectation clear?

Do not enforce palette, block counts, or one architectural solution.

## Rivalry / skirmish

Run noncombat formats first. A skirmish is disabled in practice until the host has proven:

- explicit roster consent;
- arena/boundary;
- loadout ceiling;
- protected spectators/noncombatants;
- inventory/death rule;
- fresh verified backup;
- PvP start/stop controls;
- stop command/condition;
- restore/rebuild owner.

No kill/win reward is issued by VvH.

## Weekly requisitions

One teammate pays the Bevel cost; the cache is a team reward. Stand beside the intended public destination chest before claiming. Never refund the Bevel while leaving the cache in circulation.

## Progress repair

Take a backup. Identify the exact FTB team and object ID from `campaign_manifest.json`. Use targeted FTB Quests progress commands/editor tools only. Avoid reset-all/complete-all on the live world.
