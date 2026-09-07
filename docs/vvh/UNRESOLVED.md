# VvH Unresolved Checks

Status: static implementation passes locally; runtime/client verification is
still required.

The static validator reports five chapters, 59 quests, zero errors, and five
visible review warnings. Pinned JAR evidence and the generated catalogue are
synchronized. The stack receipt comes from bytecode; it does not establish
that other mods or live server configuration leave those values unchanged.
None of this is proof of in-game behaviour.

Open these gates in a disposable client/server built from the exact Packwiz
revision:

- open all five chapters at normal GUI scale and inspect red `!` indicators,
  title wrapping, node labels, dependency lines, and chapter art;
- enable the intended resource pack and confirm every `poiesis:` image and
  namespaced icon resolves;
- complete checkmark, item, and advancement tasks, including already-earned
  Hunter/Vampire advancements and late joiners;
- test a fresh solo player, a mixed team, a faction switch, and the protected
  Neutral path;
- buy one 180-second and one 300-second Market service as payer and teammate;
  interleave partial reward claims, reconnect, and fill inventories to test
  the FTB reward-claim boundary;
- verify the 604800-second Rumour Ledger cooldown and its team-scoped payout;
- claim every Iron's Spells scroll and inspect its spell-container codec;
- confirm First Thirst still delivers all four Blood Bottles despite its
  explicitly preserved multi-count reward; verify Broadcast's eight separate
  hollow-cassette rewards;
- build Red Measure's altar and run the grinder, Sieve, reserve, and Alchemist
  Cauldron workflows; verify the component-bearing bottle output and the
  player-confirmed assembly/service boundaries;
- rehearse the offline save migration against a disposable backup, including
  already-claimed personal rewards, partial Market claims, and split rewards;
- inspect loaded recipes, dynamic currency issuance, NPC offers, and recycling
  of the supplied decorative metals before closing the economy release gate;
- inspect server and client logs for missing IDs, parser errors, codec errors,
  reward errors, and missing assets.

Record the exact Packwiz revision, Minecraft/NeoForge/FTB Quests versions,
resource-pack SHA-256, GUI scale, language, player/team state, and commands in
the runtime evidence directory. Do not promote static, preview, fixture, or
synthetic evidence to a runtime or production claim.
