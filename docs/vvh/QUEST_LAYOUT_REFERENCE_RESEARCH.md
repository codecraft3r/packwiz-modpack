# VvH Quest Layout Reference Research

This note records reusable structural patterns observed in publicly available
FTB Quests chapter data. It is a design reference, not a source for copied
quest prose, art, IDs, or pack-specific progression.

## Player-provided target

The target layout is a clean central progression line with repeated geometric
clusters. Major hubs are visually dominant, related quests radiate from each
hub, and decorative art sits behind the functional graph. The VvH adaptation
keeps the shared world-building lane on the central spine and places personal,
faction, and magical progression in optional side clusters.

## Public SNBT references

### All The Mods 10 — Create

- Repository chapter index: https://github.com/AllTheMods/ATM-10/tree/main/config/ftbquests/quests/chapters
- Create chapter: https://raw.githubusercontent.com/AllTheMods/ATM-10/main/config/ftbquests/quests/chapters/create.snbt
- Main questline: https://raw.githubusercontent.com/AllTheMods/ATM-10/main/config/ftbquests/quests/chapters/mainquestline_part_1.snbt

Reusable patterns:

- a visually dominant spine with hubs every few nodes;
- side content offset into clearly separated clusters;
- larger shapes for anchors and convergence points;
- normal spacing around 1.5–2.5 coordinate units;
- decorative shafts, cogs, and emblems behind quest nodes with a negative
  render order and no click action;
- practical milestone rewards attached throughout the main route.

### All The Mods 10 — Iron's Spells 'n Spellbooks

- Chapter: https://raw.githubusercontent.com/AllTheMods/ATM-10/main/config/ftbquests/quests/chapters/iron_spells_and_spellbooks.snbt

Reusable patterns:

- one shared material or rune hub feeding school-specific branches;
- distinct shapes and sizes for shared materials, schools, equipment, and
  major upgrades;
- optional utility equipment kept off the primary progression line;
- rewards that support the next spellcraft action without skipping a tier.

VvH mapping:

- House of Night uses a Blood-oriented side cluster;
- Lantern Order uses a Holy-oriented side cluster;
- Free Companies use a limited shared-material and translation cluster;
- all three reconnect to civic milestones rather than replacing the common
  world-building spine.

### Enigmatica 6 — Powah

- Chapter index: https://github.com/EnigmaticaModpacks/Enigmatica6/tree/master/config/ftbquests/quests/chapters
- Powah chapter: https://raw.githubusercontent.com/EnigmaticaModpacks/Enigmatica6/master/config/ftbquests/quests/chapters/powah.snbt

Reusable patterns:

- a clear contextual opener followed by resource and machine branches;
- optional side routes explicitly marked optional;
- immediate, practical rewards on meaningful crafts;
- flexible "any tier" objectives instead of duplicated grind nodes;
- quest descriptions provide context without merely repeating the task.

## VvH layout rules

1. Put the world-building route on a straight central spine.
2. Space central nodes consistently and insert a visible hub every four to
   seven meaningful objectives.
3. Place personal progression and faction specialization in offset side
   clusters with generous negative space.
4. Reconnect side clusters at shared milestones when that relationship is
   real; do not add decorative dependencies.
5. Use a consistent shape language:
   - gear: chapter anchor;
   - hexagon: ordinary civic milestone;
   - pentagon: faction or spell-school milestone;
   - rounded square: optional side quest;
   - diamond: specialization or reward-heavy convergence;
   - large octagon: major shared capstone.
6. Keep background art below quest nodes and disable its click action.
7. Reward every meaningful milestone, but leave pure exposition and tiny
   acknowledgement nodes unrewarded.
8. Prefer complementary materials, construction support, consumables, and
   capped choices over returning the exact objective input.
9. Preserve a readable route at normal GUI scale; static layout boards are
   planning evidence, not a substitute for in-client screenshots.

## Release acceptance

- The shared spine is visually obvious without reading every title.
- Side clusters cannot be mistaken for mandatory shared progression.
- No branch crosses through an unrelated cluster.
- Logos and backgrounds remain subdued behind icons and dependency lines.
- Every meaningful milestone exposes a useful, non-looping reward.
- Client screenshots confirm the layout at fit-to-page and readable zoom.

