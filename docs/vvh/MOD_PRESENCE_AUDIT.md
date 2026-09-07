# VvH Current-Pack Mod Presence Audit

## Finding

The current campaign references only namespaces that are bound to indexed
Packwiz metadata. Earlier ID discovery could read unrelated PrismLauncher JARs,
so a valid model from an external inventory was not proof that the current pack
contained that mod.

## Current release gate

`scripts/vvh_sync_catalog.py` derives campaign references from the live chapter
SNBT. Every non-vanilla namespace must resolve to a `.pw.toml` present in
`index.toml`. It verifies the metadata file's SHA-256 against the index and
records the declared download hash. When an exact JAR is materialized, its bytes
must match that download hash before new item or spell evidence can be added.

The current catalog contains these campaign-used namespaces:

`abyssal_decor`, `create`, `createbigcannons`, `createdeco`,
`explorerscompass`, `exposure`, `irons_spellbooks`, `mannequins`, `numismatics`,
`sophisticatedbackpacks`, `supplementaries`, `vampirism`, and `vista`.

Unrelated downloaded JAR inventories are excluded. The PowerShell discovery
helper applies the same Packwiz download-hash check to every candidate path and
reports hash-mismatched files as missing.

## Evidence boundary

Static Packwiz membership and exact JAR-entry checks prove that a referenced
namespace and evidence entry belong to the pinned pack. They do not prove
client rendering, runtime registry registration, already-earned advancement
synchronization, reward delivery, or two-account team behaviour. Those checks
remain in `UNRESOLVED.md`.
