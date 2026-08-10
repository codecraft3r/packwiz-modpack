# VvH Original Asset Queue

The campaign uses the current Poiesis art release for every VvH chapter panorama and the complete Blood/Holy/mediator support set.

## ASSET-001 — Season crest
- Status: accepted, generated, reviewed, installed in living-atlas-art-v5
- Intended use: VvH chapter-group navigation identity / season announcement
- Final output path: `assets/poiesis/textures/questpics/vvh/season_one_crest.png`
- Canvas: 512x512 px
- Aspect ratio: 1:1
- Alpha: required
- Safe area: central 78%; no content touching outer 24 px
- Visual continuity: dark-fantasy guild ledger; chunky woodcut linework; crimson/bone Vampire half, steel-blue/gold Hunter half, parchment-green Neutral knot joining both; Minecraft-block-aware silhouette, not official Minecraft branding
- Subject and composition: circular heraldic seal split by a vertical lantern, left motif a stylized bat/fang and chalice silhouette, right motif garlic/lantern and watchtower silhouette, lower centre a map/contract knot representing neutrals; balanced visual weight, no weapons as dominant motif
- Generation prompt: Transparent heraldic crest for a small Minecraft-style social RPG campaign, hand-cut woodblock and illuminated-ledger aesthetic, circular seal, left crimson and bone vampire faction represented by abstract bat wings, fang and ceremonial vessel, right steel-blue and antique-gold hunter faction represented by garlic sprig, lantern and watchtower, lower parchment-green neutral contract/map knot bridging the sides, strong 2–4 px equivalent ink line, simplified shapes readable at 32 pixels, no words, no official game logo, slightly imperfect hand-printed texture
- Negative prompt: text, letters, logos, photorealism, anime, gore, realistic blood, guns, crossbows dominating the image, tiny clutter, gradients that disappear at icon scale, watermark, copyrighted logo
- Post-processing: chroma-key removal; alpha/fringe audit; nearest-neighbor resize to 512x512; test at 128/64/32 px; keep transparent margin; optimize PNG
- Acceptance checks: all three roles readable; no side looks more powerful; recognizable at 32 px; clean alpha; no text; verified in v5 ZIP
- Release asset: vvh-season-one-art-20260809-253445c/poiesis-living-atlas-art-v5.zip
- Temporary fallback: `minecraft:textures/item/compass_16.png`

## ASSET-002 — House of Night key art
- Status: accepted, generated, reviewed, installed in the current living-atlas-art release
- Intended use: Vampire foundation chapter background
- Final output path: `assets/poiesis/textures/questpics/vvh/house_of_night.png`
- Canvas: 1280x720 px
- Aspect ratio: 16:9
- Alpha: not required
- Safe area: central 46% low-detail for quest nodes
- Visual continuity: crimson, black-brown wood, bone, dim gold; gouache-over-woodcut; visual cues drawn from actual Vampirism altar/coffin/blood-container vocabulary without copying UI screenshots
- Subject and composition: block-built manor interior and courtyard at blue hour, side vignettes of a coffin room, altar chamber, labelled pantry, night kitchen and lantern route, players hosting a visitor rather than fighting; centre kept quiet
- Generation prompt: Wide production key art for a Minecraft-like vampire civic guild chapter, block-aware gothic manor at blue hour, warm crimson and dim gold windows, side vignettes showing functional coffin room, ritual altar chamber, labelled blood pantry, supernatural kitchen and a lantern-lit public route, several blocky adventurers hosting a guest and maintaining the building, no central combat, painterly gouache plus engraved woodcut texture, central 46 percent deliberately low detail for UI nodes, atmospheric but readable in dark UI
- Negative prompt: gore, feeding close-up, seductive vampire portrait, one overpowered hero, combat scene, text, logo, photorealism, muddy black centre, UI elements, watermark
- Post-processing: lower centre contrast; vignette edges; palette match to faction crimson/bone; 16:9 crop check; PNG optimize
- Acceptance checks: reads as vampire infrastructure/hospitality before combat; centre remains legible; no embedded text
- Temporary fallback: Vampirism fang + vanilla lantern textures

## ASSET-003 — Lantern Order key art
- Status: accepted, generated, reviewed, installed in the current living-atlas-art release
- Intended use: Hunter foundation chapter background
- Final output path: `assets/poiesis/textures/questpics/vvh/lantern_order.png`
- Canvas: 1280x720 px
- Aspect ratio: 16:9
- Alpha: not required
- Safe area: central 46% low-detail
- Visual continuity: steel-blue, parchment, garlic green, antique gold; woodcut/gouache companion piece to ASSET-002
- Subject and composition: block-built watchhouse/workshop with lantern route, Hunter Table/alchemy silhouettes, garlic reserve and refuge map; players helping an escorted traveler, not posing as monster slayers
- Generation prompt: Wide production key art for a Minecraft-like hunter civic order, sturdy block-built watchhouse and shared workshop at dusk, steel-blue roof accents, antique-gold lantern route, garlic drying rack, alchemical workspace and public refuge signage shapes, several blocky adventurers escorting a traveler and checking supplies, vigilant but non-militaristic mood, hand-printed woodcut plus gouache texture, central area quiet for quest nodes, matched composition weight to a vampire manor companion image
- Negative prompt: firing squad, gore, trophies of dead vampires, giant weapon, modern military gear, police aesthetic, photorealism, text, watermark, cluttered centre
- Post-processing: palette harmonization with House art; reduce centre detail; readability test at chapter scale; PNG optimize
- Acceptance checks: public-service identity is obvious; no glorification of killing; equal visual prestige to Vampire art
- Temporary fallback: Vampirism garlic + vanilla lantern textures

## ASSET-004 — Free Company writ crest
- Status: accepted, generated, reviewed, installed in living-atlas-art-v5
- Intended use: Neutral foundation chapter icon/background motif
- Final output path: `assets/poiesis/textures/questpics/vvh/free_company_writ.png`
- Canvas: 512x512 px
- Aspect ratio: 1:1
- Alpha: required
- Safe area: 80% central
- Visual continuity: parchment, moss green, copper, ink-black; same woodcut linework as faction crest
- Subject and composition: folded route map, sealed contract, courier satchel, market awning and small bell arranged as a compact civic emblem; no weapons
- Generation prompt: Transparent guild emblem for a neutral Free Company in a block-world fantasy server, woodcut ledger illustration, folded map and route line behind a sealed contract, small courier satchel, market awning and civic bell, parchment and moss-green palette with copper accents, chunky simple silhouette readable at 32 pixels, no text, no money pile, no weapon motif
- Negative prompt: corporate logo, national flag, bank icon, realistic currency, sword, gun, tiny illegible writing, photorealism, watermark
- Post-processing: chroma-key removal; alpha/fringe audit; nearest-neighbor resize to 512x512; simplify route marks; palette reduction; icon-scale tests
- Acceptance checks: communicates trade/routes/mediation; equal status to faction crests; no text; verified in v5 ZIP
- Release asset: vvh-season-one-art-20260809-253445c/poiesis-living-atlas-art-v5.zip
- Temporary fallback: `minecraft:textures/item/filled_map.png`

## ASSET-005 — Public works panorama
- Status: accepted, generated, reviewed, installed in the current living-atlas-art release
- Intended use: The Island Remembers chapter background
- Final output path: `assets/poiesis/textures/questpics/vvh/island_remembers.png`
- Canvas: 1280x720 px
- Aspect ratio: 16:9
- Alpha: not required
- Safe area: central upper 45% subdued
- Visual continuity: warm parchment-gold nightfall, all faction colors present only as accents
- Subject and composition: one inhabited island showing connected road/rail, market, archive, kitchen, workshop, airship dock, refuge, meeting hall; visual lines converge but centre stays calm
- Generation prompt: Wide illustrated block-world island town at dusk showing accumulated public infrastructure rather than a hero, connected road and short rail line, market, archive/map room, community kitchen, shared mechanical workshop, small airship dock/test field, emergency refuge and public meeting hall, tiny crimson vampire, steel-blue hunter and green-neutral accents distributed evenly, warm lanterns, hand-painted woodcut/gouache style, central upper area low detail for quest UI nodes, sense of history and repeated use
- Negative prompt: empty pristine city, giant castle dominating scene, combat, text labels, official Minecraft logo, photorealism, cluttered centre, watermark
- Post-processing: centre contrast reduction; slight paper texture; sharpen infrastructure silhouettes; PNG optimize
- Acceptance checks: at least six public-work types visible; world feels lived-in; no one faction owns the composition
- Temporary fallback: vanilla lantern/rail/book imagery

## ASSET-006 — Rivalry without ruin woodcut
- Status: accepted, generated, reviewed, installed in the current living-atlas-art release
- Intended use: safe-rivalry chapter background
- Final output path: `assets/poiesis/textures/questpics/vvh/rivalry_without_ruin.png`
- Canvas: 1024x576 px
- Aspect ratio: 16:9
- Alpha: not required
- Safe area: central 50% quiet
- Visual continuity: satirical illuminated-manuscript marginalia; faction colors; warm parchment
- Subject and composition: Vampire and Hunter teams at far edges presenting absurd food, mascots, banners and race contraptions; neutral referee at lower centre; scavenger clues and fireworks; no battle in focus
- Generation prompt: Wide satirical woodcut illustration for harmless faction rivalry in a block-world fantasy server, crimson vampire team at far left and steel-blue hunter team at far right presenting absurd mascots, Blood-versus-Holy ward demonstrations, propaganda banners and overengineered race contraptions, parchment-green neutral referee with clipboard at lower centre, scavenger clues and fireworks in background, theatrical friendly tension, central area deliberately low-detail for quest nodes, aged manuscript texture, no text
- Negative prompt: warfare, gore, angry mob, griefed buildings, realistic weapons, text, official logos, photorealism, cluttered centre, watermark
- Post-processing: reduce centre contrast; palette harmonize; vignette; PNG optimize
- Acceptance checks: funny before threatening; multiple safe formats readable; no text
- Temporary fallback: firework/garlic/fang/map textures

## ASSET-007 — Long Night Fair key art
- Status: accepted, generated, reviewed, installed in the current living-atlas-art release
- Intended use: Season One capstone background and announcement
- Final output path: `assets/poiesis/textures/questpics/vvh/long_night_fair.png`
- Canvas: 1280x720 px
- Aspect ratio: 16:9
- Alpha: not required
- Safe area: central upper 45% subdued; strongest activity along lower third/edges
- Visual continuity: warm gold against blue-black night; crimson, steel-blue and green identities mixed rather than segregated; woodcut-gouache finish
- Subject and composition: lantern procession through the actual kinds of works the campaign created—market, workshop, archive, kitchen, routes, dock—plus Vampire hospitality, Hunter public-service exhibit, neutral contract desk, small airship/vehicle demonstration and fireworks; no central hero
- Generation prompt: Production key art for a block-world social RPG finale called a long-night fair, inhabited island town at deep blue night lit by hundreds of warm lanterns, mixed procession passing public market, mechanical workshop, archive, community kitchen, mapped road and small airship dock, crimson vampire hosts with supernatural food table, steel-blue hunter stewards with public safety exhibit, parchment-green neutral traders and contract desk, controlled whimsical vehicle demonstration and fireworks over water, collective celebration without a central hero, painterly woodcut-gouache hybrid, central upper area quiet for quest nodes, no text
- Negative prompt: title lettering, logo, lone warrior, combat, gore, dark unreadable image, chaotic centre, photorealism, watermark
- Post-processing: preserve UI-safe centre; blacks lifted for dark UI; 16:9 and 2:1 crop tests; PNG optimize
- Acceptance checks: communicates accumulated world history and all three identities; multiple contribution types visible; readable at chapter scale
- Temporary fallback: lantern/firework/fang/garlic textures
