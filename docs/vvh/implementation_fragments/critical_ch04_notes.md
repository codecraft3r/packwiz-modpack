# Chapter 4 critical revision

Exactly eight charter alternatives remain: four central world-building works (`14000002`-`14000005`) and four right-side progression/service works (`14000006`-`14000009`). The charter (`1400000A`) requires five of eight, so every valid completion includes both lanes. All eight alternatives are optional and depend directly on the founder.

The founder (`14000001`) now depends on the Chapter 1 Free Company Register (`11000004`). Empty lane-label quests `1400000C` and `1400000D` were removed. Duplicate same-item tasks were removed from the contract hall, waystation, courier service, and spellwright objectives; each keeps one representative item task plus a review checkmark where appropriate.

The main spine is `x=0`; service branches use `x=5`. Decorative art is now three low-alpha, non-node images with unique positions/orders: the writ at `(-4.8,-1.5)`, a wide mediator panorama at `(0,5)`, and the translation desk at `(5.2,4)`. Redundant Iron's Spells item sprites and the old seven-image scatter were removed.

Removed IDs: `7A11C0DE1400000C`, `7A11C0DE1400000D`, `7A11C0DE14000101`-`7A11C0DE14000105`. Their localization may remain harmlessly stale until the root localization pass; the new lines are in `critical_ch04_lang.snbtfrag`.

Validation targets: parse the chapter and fragment; assert exactly eight direct founder children, all `optional: true`, charter `min_required_dependencies: 5`, four world IDs at `x=0`, four service IDs at `x=5`, no duplicate coordinates or crossing dependency geometry, no removed IDs in the chapter, no duplicate item IDs per quest, `git diff --check`, normal VvH validation, manifest regeneration, and Packwiz refresh.
