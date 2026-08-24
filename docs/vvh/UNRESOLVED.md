# VvH Six-Chapter Runtime Gates

Static campaign evidence currently passes. The checks below are still required before calling the campaign playtested or runtime-verified.

- [ ] Materialize the exact Packwiz pack on a disposable dedicated server, reload FTB Quests, and review logs for parser, missing-ID, advancement, and data-component errors.
- [ ] Open all six chapters in the shipped client and inspect node layout, title wrapping, icons, tooltips, and red error badges at normal UI scale.
- [ ] Trigger `become_vampire` and `become_hunter` with fresh and already-completed states, including faction switching and FTB Teams synchronization.
- [ ] Verify Cobblemon first-catch, first-victory, and witnessed raid participation tasks with real gameplay.
- [ ] Complete the Chapter 05 shared Create attestations and public-build capstone with a team.
- [ ] Compare every claimed Iron's Spells scroll and affinity ring with a native in-game item and confirm the full data components and tooltips survive FTB Quests claim serialization.
- [ ] With two disposable accounts, distinguish personal Bevel rewards from team Bevel rewards and test party join, leave, switch, and fragmented-team behavior.
- [ ] For each Chapter 06 crate, have one teammate pay and another claim; confirm exact Bevel consumption, team delivery, the 604800-second cooldown, and rejection of a second weekly claim.
- [ ] Exercise optional skirmish start/stop controls, protected spectators, backup, and restore on a disposable world.
- [ ] Confirm permanent-building boundaries and any future reset procedure on a disposable world.

Client screenshots, server logs, and two-account claim observations should be stored under `docs/vvh/evidence/`. Until those artifacts exist, the evidence is static-only.
