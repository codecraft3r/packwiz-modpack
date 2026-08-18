# Critical Chapter 3 repair notes — Lantern Order

## Graph repair

- Founder `7A11C0DE13000001` now depends on the live Lantern Oath `7A11C0DE11000003`.
- Removed the empty lane-label quests `7A11C0DE1300000C` and `7A11C0DE1300000D`; their children now depend directly on the founder.
- The eight works `13000002`–`13000009` are direct founder alternatives and all carry `optional: true`.
- Charter `1300000A` depends on all eight works and uses `min_required_dependencies: 5`. The localization states that five works must include at least one Progression work and one World-Building work; its two review tasks verify that claim.
- The optional post-charter branch `13000101` → `13000102` → `13000103` remains outside the required charter path and is marked optional.

## Layout

The founder and charter stay on the central x=0 spine. World-building works use x=0 at y=-1.0, 1.4, 3.8, and 6.2. Progression works use x=5.0 at the same y values. The optional depth arc continues on x=0 at 11.2 and 13.8, with its final treaty consequence at x=5.0/y=13.8. Node centres are unique and separated by at least 2.4 vertical units; there are no node overlaps or diagonal dependency crossings.

## Holy progression

The Hunter Table, stakes, and Alchemical Cauldron use existing live item tasks plus installation/review checkmarks. The Holy Ward uses the live `irons_spellbooks:holy_rune` item plus a reviewed ward demonstration. The response drill is a real field-medicine, cleansing, evacuation, or shelter test; when attendance fails, the player records a solo test log and one corrected failure. Nothing requires killing vampires or grants faction rank/high-tier gear.

## Canon voice

The Lantern Order remembers Warden Elias Rook saving civilians at Greybridge while abandoning a vampire refuge. He calls it triage because he has to; Nessa Quill's route record says the refuge was still reachable. The chapter uses that contradiction as a recurring consequence: a watchhouse is not complete until a stranger can find help, and a route is not safe until someone tests the handoff.

## Reward scope

Existing direct Bevel rewards are preserved. The optional branch uses the requested Lantern-specific utility choice table ID `8796023610973093894` (table #6), with `team_reward: true` and no Bevel or high-tier power reward. The table must exist in the shared reward-table pass before release; this chapter intentionally does not author shared table files.
