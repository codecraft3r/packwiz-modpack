# Frontier chapter backgrounds

Nine generated illustrations now give the questbook a consistent dark explorer-atlas style. Each chapter's `dc29d49` source-map image was supplied to the built-in image-generation tool as a placement guide. The opener established the visual style; subsequent images used it as a second reference. The final prompt set is in `art-prompts.json`.

The backgrounds contain no quest labels, nodes or dependency lines. FTB draws the real graph over the art, so completion states, links and future quest edits remain interactive. Scenic detail sits around the margins; the paths occupy the quieter charcoal center. Engineering uses brass machinery and teal equipment, transport uses an airship and railway, shared places use a lantern-lit settlement, and the other chapters have their own adventure, boss, library, contract or warehouse imagery.

## Attachment and delivery

`art-source.json` owns each texture's native position, size, opacity, draw order, dimensions and SHA-256. Position was fitted from the corresponding pre-art map projection; every background preserves its 3:2 aspect ratio. The places background has a wider quiet area and slightly lower opacity to keep its photography lane clear.

The installed FTB Quests `2101.1.33` implementation uses image-center `x/y` coordinates when `corner` is omitted. `ChapterImageButton` is on the background draw layer, before dependency lines and quest buttons. Negative `order` sorts background images; no click action is attached. We emit one image per Frontier chapter at order `-100`, with no gameplay or coordinate changes to any quest.

The existing required resource pack provides the files:

`global_packs/required_resources/vvh_backgrounds/assets/poiesis/textures/questpics/frontier/`

Each native reference is `poiesis:textures/questpics/frontier/<chapter-key>.png`. `config/global_packs.toml` already requires `global_packs/required_resources/`, and the pack metadata already uses Minecraft 1.21.1 resource format 34. These are ordinary tracked PNG assets indexed directly by Packwiz; no remote image service, custom quest code, resource-pack ZIP or server restart is introduced.

Nine static 1536 × 1024 PNGs cost about 19 MiB on disk. That is one texture per chapter, rather than one per quest; all nine decoded RGBA images would contain about 54 MiB of texels before any driver overhead. The generated pixel data is retained without upscaling or lossy recompression. A client must receive the updated pack resources and reload them or restart for the new textures to become available; changing only the server quest definitions is insufficient.

## Verification and limits

The semantic audit checks all nine files, exact case-sensitive references, PNG dimensions, SHA-256, aspect ratio, resource-pack version and emitted native image fields. Staged generation receives the same art files as the final pack. Regression tests cover missing manifests/assets, stale digests, image geometry and unchanged quest tasks.

Source previews resolve all nine custom textures. The renderer preserves the graph's diagnostic zoom when fitting larger background extents, so background margins do not squeeze the quest labels together. Full-book grammar, graph, identity and economy checks still apply. `evidence/art-readability.json` records a limited texture-brightness sample at node positions; it is not a runtime contrast certification.

These previews are not Minecraft screenshots. In the pinned client, verify normal zoom, small-screen panning, resource reload, node/label readability, hover/click behavior and absence of missing textures before promoting to production. Publishing the pack does not restart the live server or update already-running clients.
