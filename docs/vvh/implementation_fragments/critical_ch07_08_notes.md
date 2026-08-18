# Critical Chapter 7–8 implementation notes

## Structural changes

- Chapter 7 keeps its optional Chapter 5 entry and now presents six equal event cards in a symmetric fan. Every format points back to the preparation node. The archive and sanctioned skirmish are sibling any-two outcomes; neither gates the other.
- Chapter 8 has one preparation node (`7A11C0DE18000001`), six optional contribution alternatives (`18000002`–`18000007`), an any-three capstone (`18000009`), and an optional archive aftermath (`18000102`). The obsolete `SET THE TABLES` node (`18000101`) was merged into the preparation node and deleted.
- Chapter 8 preparation now awards one personal Bevel (`10207008`); the deleted preparation payout of three Bevels is gone. `SEAL SEASON ONE` retains its existing three personal Bevel reward (`18220009`). Net change: -3 personal Bevels from the prior Chapter 8 graph.
- All Chapter 7 event rewards and Chapter 8 contribution/preparation/aftermath choice rewards use event table `7A11C0DEF0000009` (decimal `8796023610973093897`). No table was created or edited.

## Event design

Chapter 7 formats have distinct preparation, objective, and result requirements in the accompanying localization fragment. Each has an honest solo/small-group audit: timed run, environmental ward test, clue-course record, procurement benchmark, or rubric-judged build. A solo audit is never described as a faction victory.

The preferred Chapter 8 experience is a shared fair with visitors and hosts. Each contribution also has a solo exhibition audit using a staged display, signed test log, written result, or NPC audience where applicable, so a late or absent player can still make a truthful contribution without pretending the fair happened.

## Canon anchors

- The Greybridge truce collapsed during a public demonstration.
- Mirelle Voss and Elias Rook remember the same bell differently.
- Nessa Quill archived both accounts instead of resolving the contradiction.
- The fair asks players to present the unresolved evidence—the bell fragment, demonstration ledger, route map, and two incompatible witness notes—rather than declaring a generic celebration or a definitive historical answer.

## Layout checks

Chapter 7 positions the preparation at `(0,-5)`, six event cards at `(-6,-1.2)`, `(-3.6,-1.2)`, `(-1.2,-1.2)`, `(1.2,-1.2)`, `(3.6,-1.2)`, `(6,-1.2)`, archive at `(0,4)`, and skirmish at `(4.6,4)`. Terminal dependency lines remain hidden, preventing fan crossings.

Chapter 8 positions preparation at `(0,-5)`, six optional contributions at the same symmetric x positions and `y=-0.6`, the seal at `(0,4.5)`, and archive aftermath at `(0,7.2)`. All six contribution cards are optional and the seal requires any three.

## Validation checklist

1. Parse both SNBT files.
2. Assert Chapter 7 event nodes all depend directly on preparation; archive and skirmish each have six event dependencies with minimum 2; no `17000008 -> 17000009` edge exists.
3. Assert Chapter 8 has no `18000101`, exactly six optional contribution nodes, capstone minimum 3, and aftermath depends on capstone.
4. Count direct personal Bevels: Chapter 8 prep = 1, seal = 3; deleted SET THE TABLES = 0.
5. Assert all changed event choice rewards use table `8796023610973093897`; capstone thematic choice tables remain intentionally separate.
6. Run `git diff --check`. Client screenshots remain the final manual geometry check.
