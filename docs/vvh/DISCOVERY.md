# VvH Discovery Record

Status: current implementation basis.

## Repository and pack

- Repository: `codecraft3r/packwiz-modpack`
- Target branch: `dev`
- Baseline inspected for this rebuild: `4936b447a0f00f3e9a109e27c164f9215cfbfa92`
- Pack format: Packwiz 1.1.0
- Minecraft line: 1.21.1 / NeoForge

The Packwiz index and current repository artifacts are the source of truth. Historical display names or remembered registry IDs are not accepted as evidence.

## Confirmed campaign-facing systems

The current campaign uses IDs already present in the live campaign, current ID catalogue, or installed-pack evidence from these namespaces:

- `minecraft`
- `vampirism`
- `irons_spellbooks`
- `numismatics`
- `exposure`
- `explorerscompass`
- `create`
- `poiesis` for chapter art references

The generated campaign does not introduce a new custom item namespace or custom quest-state KubeJS layer.

## Native progression evidence

Faction entry uses the current Vampirism items and advancements:

- Vampire: `vampirism:vampire_fang` plus `vampirism:vampire/become_vampire`
- Hunter: `vampirism:injection_garlic` plus `vampirism:hunter/become_hunter`

Late-join and already-earned advancement behaviour still requires an in-client smoke test on the final generated files.

## Currency evidence

The installed Numismatics denominations used by the campaign are:

- `numismatics:spur`
- `numismatics:bevel`
- `numismatics:sprocket`
- `numismatics:cog`
- `numismatics:crown`
- `numismatics:sun`

The current campaign issues and consumes only Bevel, Sprocket, and Cog.

## Complex item handling

Iron's Spells scroll rewards serialize the complete component structure used by the current campaign source, including spell data, maximum spell count, equip requirement, and spell-wheel flag. Grammar validation alone does not prove runtime codec acceptance; current-client inspection remains required.

## Source ownership finding

The former whole-campaign drift was resolved by making `scripts/vvh_campaign_v3.py` the bounded five-chapter generator and documenting all older multi-chapter campaign material as historical. Generation is deterministic, checkable, and non-destructive toward unknown chapter files by default.
