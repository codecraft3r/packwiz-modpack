# VvH asset-path audit

Audit date: 2026-08-14

## Result

- 18 custom VvH chapter image references resolve in `poiesis-living-atlas-art-v5.zip`.
- The ZIP entry prefix is `assets/poiesis/textures/questpics/vvh/`, matching FTB Quests references of `poiesis:textures/questpics/vvh/...`.
- Case and extension checks passed for Blood, Holy, mediator, chapter panorama, and season crest art.
- Iron's Spellbooks item texture references resolve in the installed `irons_spellbooks-1.21.1-3.16.1.jar` client artifact.
- Numismatics' bevel texture resolves in `CreateNumismatics-1.0.20+neoforge-mc1.21.1.jar`.
- Vampirism's garlic and vampire-fang textures resolve in `Vampirism-1.21-1.10.12.jar` from the disposable pack materialization.
- Vanilla references (`minecraft:textures/item/...`) are client-JAR resources and are not expected in the Poiesis ZIP.

## Static-board evidence

`scripts/vvh_render_layouts.py` was run with the v5 Poiesis ZIP. The resulting PNGs and contact sheet are in `docs/vvh/evidence/layout-revision/`, with provenance in `render-metadata.json`. That metadata deliberately reports mod and vanilla references as unresolved when their JARs are not passed to the source renderer; this is a limitation of the renderer, not evidence of a missing client texture. No in-client screenshot is claimed here.

## Remaining manual gate

Open each chapter in the target Prism client and capture the fit/detail screenshots described in `QUEST_LAYOUT_SCREENSHOTS.md`. Check chapter logo/background crop, custom art, item icons, branch spacing, and missing-texture tiles at normal UI scale.
