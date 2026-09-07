# VvH Quest Layout Review

The PNGs from `scripts/vvh_render_layouts.py` are deterministic source-level
diagnostics, not Minecraft or FTB Quests screenshots. They preserve stored
coordinates and effective dependency visibility while making every title
readable. The detail boards use measured wrapping and collision-aware label
placement; dense crops isolate the tightest clusters. Only captures made in a
running client satisfy the visual acceptance gate.

## Current board

Each chapter uses one full-size panorama centered on its quest composition.
Widths are 24 units for onboarding, 34 for the factions, and 40 for the Market;
heights retain the source images' 16:9 proportions. Opacity is 105–150 out of
255. The viewport fits both nodes and complete image bounds, so artwork is not
clipped by a frame calculated from quest positions alone. Chapter 4's protected
quest coordinates remain unchanged.

The supplied `poiesis-living-atlas-art-v5.zip` contains these existing assets
(SHA-256 `d6d273dae29ab294618a1fae0738b99b1b9c176910cc75a572dcde7f81a95b4a`).
The renders use that archive; no ZIP or new resource-pack installation is
included in this source change. A client must have the Poiesis artwork loaded
to display its namespaced images.

The current campaign has five chapters and 59 quests:

1. `ch01_island_charter` — 5 quests
2. `ch02_callings` — 5 quests
3. `ch03_lantern_order` — 15 quests
4. `ch04_house_night` — 15 quests
5. `ch05_market_services` — 19 quests

Render from the Packwiz repository root after regenerating the manifest. The
baseline is read from the actual live SNBT snapshot, never from a stale
manifest:

```powershell
python scripts/vvh_render_layouts.py `
  docs/vvh/campaign_manifest.json `
  docs/vvh/evidence/current/layouts `
  --baseline-root C:\path\to\baseline\quests `
  --live-root config\ftbquests\quests `
  --resource-zip C:\path\to\resourcepack.zip
```

`--resource-zip` accepts resource-pack ZIPs and mod JARs. The output metadata
records each SHA-256, resolved icon/art keys, model-reference coverage,
unresolved art/icon references, and the baseline/live SNBT file hashes. Missing
background art is shown as a dim labelled placeholder so it cannot be mistaken
for loaded client art; unresolved item icons are reported explicitly while the
stable quest-ID suffix remains visible.

Each chapter produces an overview, a readable detail board, and a dense crop
when needed. `contact_sheet.png` contains the overviews. `render-metadata.json`
records before/after/live metrics for node overlaps, estimated label
collisions, visible-edge crossings and lengths, spacing, cluster separation,
spine alignment, disconnected components, and deliberately hidden dependency
edges. The default edge view is source-faithful stored geometry. Use
`--edge-view orthogonal` for the Manhattan diagnostic, or `--edge-view both`
to emit both families with `_orthogonal` filenames; the routed view must not
replace source-faithful evidence.

## Source-board rubric

- no quest-node overlaps or unreadable labels;
- configured circles, squares, diamonds, hexagons, gears, and other shapes are
  drawn as configured, with size differences preserved;
- item icons are shown when supplied resource archives contain the referenced
  texture;
- dependency lines attach to the intended nodes and avoid crossings;
- the Charter and faction spines read in order;
- optional branches remain visually subordinate and do not look mandatory;
- Market dependency lines are hidden because its chapter default requests it,
  while faction chapter lines remain visible. A quest-level
  `hide_dependency_lines: false` explicitly re-enables its own edge.
- artwork does not obscure nodes, labels, or junctions;
- every unresolved image is listed in `unresolved_references`.

## Client capture gate

Create `docs/vvh/evidence/client-layout/<session>/` from a disposable client
using the exact Packwiz revision. Record Minecraft, NeoForge, FTB Quests,
resource-pack SHA-256, resolution, GUI scale, language, and pack order.

Capture a fit view and a readable detail view for each of the five chapters
(ten PNGs minimum), plus branch captures when labels cannot be judged in the
detail view. Do not crop or resize the source screenshots. Record pass/fail
observations in `RESULTS.md` beside the PNGs.

Client acceptance covers chapter identity, art, icons, spine readability,
optional branches, dependency state styling, title wrapping, and red `!`
indicators. Static boards and parser output cannot convert a failed client
capture into a pass.
