# VvH Validation

The generated package includes `scripts/vvh_validate.py`, `scripts/vvh_render_layouts.py`, `scripts/vvh_discover.py`, and `scripts/vvh_server_smoke.sh`.

Static validation must cover:

- all edited SNBT parses;
- unique global FTB object IDs;
- acyclic/reachable VvH graph and valid any-N-of-M minima;
- all localization keys;
- all item/icon/image/advancement references against the materialized dev JAR index;
- all VvH references resolve against the installed pack;
- no new VvH KubeJS files;
- explicit personal/team reward scope;
- verified Blood, Holy, and neutral mediator Iron's Spells item/image references;
- no primary paper-only reward remains in VvH campaign pages;
- manifest-level playtest covers one Blood objective, one Holy objective, one neutral objective, one world-build objective, and one school-material choice cache;
- repeatable Bevel prices/cooldowns and zero Bevel issuance;
- source-level layout overlap/crossing checks.

The dedicated-server stage must materialize the exact Packwiz pack, launch NeoForge 21.1.233 in a disposable world, wait for startup, execute FTB Quests reload, and fail on targeted quest/config/missing-ID errors. Client visual tests and multi-account interaction tests remain distinct manual checks; they are never described as completed merely because the server parsed the files.
