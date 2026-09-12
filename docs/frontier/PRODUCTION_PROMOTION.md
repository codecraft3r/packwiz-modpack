# Production publication — September 11, 2026

The owner explicitly requested the complete questbook and artwork on the production branch so the server could be restarted. The repository default branch and the live container PACKWIZ_URL both resolve to `master`.

The promotion merges the validated dev quest source and nine generated backgrounds with the existing production changes: AppleSkin, Overflowing Bars, Inv View, Cataclysm: Spellbooks 1.1.14, the Excelsius smithing recipe and the numeric scroll-recycling config correction. Production version metadata remains 3.0.3; no tag is created.

The crafting override evidence hash was refreshed after verifying that the production diff only adds the Excelsius recipe and leaves the previously proved Icarus recipes intact. Cataclysm: Spellbooks is not one of the 27 Frontier resource-evidence namespaces; no existing pinned quest resource receipt was replaced by a guessed addon ID.

All 56 production quest IDs remain in the 140-quest combined book. The archived dev redesign predates the Frontier addition and changes some archived task/reward identities relative to production; preservation of all 1,064 prior IDs refers to the reviewed dev baseline, not every historical production task/reward object. No player save or claim migration is performed by this publication.

Server and clients must receive the updated pack. An already-running client cannot acquire the new backgrounds from server quest synchronization alone. In-client verification of credit, paid claims, resources and team behavior remains pending. No server restart is performed by the publication operation.

The subsequently authorized restart exposed a localization defect: FTB Quests 2101.1.33 migrates inline text before loading language files, and loading an empty `lang/en_us.snbt` clears the migrated text. Deploy a complete generated language table together with the chapter definitions; never replace only the language file with an empty authoring placeholder after FTB has serialized the chapters. The server was restored with all 140 quest titles and loaded 14 chapters successfully. The canonical language table additionally restores the book title and nine chapter subtitles on the next approved update. Gameplay claims and client artwork still require in-client verification.

After the repeated maintenance interruptions, the owner required explicit agreement from the players before any further restart. A countdown or warning alone does not authorize one.
