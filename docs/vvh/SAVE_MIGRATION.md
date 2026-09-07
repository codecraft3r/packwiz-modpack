# FTB Quests save migration

`scripts/vvh_migrate_claims.py` is an offline, review-first migrator for an
FTB Quests `TeamData` SNBT export. It is intentionally separate from the quest
generator and does not discover or guess campaign IDs. A reviewed mapping from
the live baseline to the new quest output is required.

The persisted shape is from the pinned FTB Quests `v2101.1.33` source in
`evidence/20260907-infrastructure-audit/upstream`. `TeamData.serializeNBT()`
stores `task_progress`, `started`, `completed`, `repeatable`, and
`completion_count` as compact quest-ID maps, and stores `claimed_rewards` as
`QuestKey` strings. `QuestKey.forReward` uses the all-zero UUID for a team
reward and the player's compact UUID for a personal reward. Thus changing a
reward from personal to shared while retaining its reward ID does not migrate
the old personal claim: the old key remains claimable under the new scope.

## Mapping file

The mapping file is JSON and should be produced from an inspected baseline and
current quest-ID report. It may contain these fields:

```json
{
  "quest_ids": { "OLD_QUEST_ID": "NEW_QUEST_ID" },
  "task_ids": { "OLD_TASK_ID": "NEW_TASK_ID" },
  "reward_ids": { "OLD_REWARD_ID": "NEW_REWARD_ID" },
  "reward_claim_copies": {
    "OLD_REWARD_ID": ["NEW_REWARD_ID_1", "NEW_REWARD_ID_2"]
  },
  "scope_transitions": [
    {
      "old_reward_id": "REWARD_ID",
      "new_reward_id": "REWARD_ID",
      "from": "personal",
      "to": "shared"
    }
  ]
}
```

The `new_reward_id` field is optional when `reward_ids` already maps the ID.
The transition is still required when the ID is unchanged but `team_reward`
changed. Personal-to-shared transitions collapse every personal key for that
reward to `00000000000000000000000000000000:REWARD_ID`; the earliest claim
timestamp is retained. This means a team that has already claimed a commission
currency grant cannot claim it again merely because its scope changed.

`reward_claim_copies` is for a deliberate one-to-many split. Every target is
written as claimed when the old claim exists. For example, the reviewed fixture
[`save-migration-mapping.json`](evidence/save-migration-mapping.json) fans the
historical Chapter 3 rabbit-stew reward `7A11C2DF0030005E` out to that retained
ID plus `7A11C2DF00305001` through `7A11C2DF0030500F`. It also covers the Market
Transit saddle, oak-boat, and Frontier Watch spyglass count splits. This
prevents old claims from reissuing newly split items. Chapter 4 Nocturnal
Broadcast also fans the personal `7A11C2DF00400036` cassette entitlement out
to its retained ID plus `7A11C2DF00405100` through `7A11C2DF00405106`; its
scope remains personal. The same timestamp is retained for each fanout target.

The compact review fixture [`save-migration-baseline.json`](evidence/save-migration-baseline.json)
contains only the necessary baseline quest/reward IDs, item counts, scope
flags, and SHA-256 provenance for the three reviewed chapter files. Tests use
that checked-in subset plus the current generator output, so CI does not need
the original personal-machine evidence path. It includes the four Chapter 4
commission scope transitions (`...00400061`, `...00400063`, `...00400065`, and
`...00400067`) and all retained Market reward IDs whose scope changes from
personal to shared. Empty `quest_ids`, `task_ids`, and `reward_ids` are
intentional: redesigned objects have no proven historical identity mapping.
Village brick and oak rewards are deliberately unmapped because their item
identities changed to stone and spruce.

Shared-to-personal is rejected because TeamData contains no player identity to
assign to a shared historical claim. Resolve that case with an explicitly
reviewed player mapping before changing the save.

When multiple old IDs map to one target, the migration preserves progress
conservatively: task progress and completion counts use the maximum, started and
completed timestamps use the earliest value, and repeatable cooldown expiry
uses the latest value. These rules avoid reducing recorded progress or making a
cooldown expire early. They are only safe when the mapping review confirms the
old objects are the same logical object.

## Dry-run and apply

Dry-run is the default and never writes the input:

```powershell
$py = 'C:\Users\Windows\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe'
& $py scripts/vvh_migrate_claims.py C:\path\to\team-data.snbt `
  --mapping C:\path\to\reviewed-mapping.json
```

To inspect a candidate without touching the save, use `--output` (this is still
not an in-place world write):

```powershell
& $py scripts/vvh_migrate_claims.py C:\path\to\team-data.snbt `
  --mapping C:\path\to\reviewed-mapping.json `
  --output C:\path\to\team-data.migrated.snbt
```

Apply is deliberately more explicit. Stop the server, calculate the hash of
the stopped save, and pass that exact hash. The tool rechecks the hash before
writing, refuses to overwrite an existing backup, writes and fsyncs a sibling
temporary file, rechecks the source hash immediately before replacement, and
atomically replaces the input. The default backup is
`team-data.snbt.bak`.

```powershell
$hash = (Get-FileHash C:\path\to\team-data.snbt -Algorithm SHA256).Hash.ToLowerInvariant()
& $py scripts/vvh_migrate_claims.py C:\path\to\team-data.snbt `
  --mapping C:\path\to\reviewed-mapping.json `
  --apply --expected-sha256 $hash
```

Do not point the tool at a live running world. This utility does not issue
Minecraft commands, does not edit quest definitions, and does not perform
world discovery. If the server stores TeamData in a binary NBT container,
obtain an SNBT export using a version-matched tool first; this script does not
invent a binary schema.

## Verification boundary

`scripts/test_vvh_migrate_claims.py` covers parsing TeamData-shaped SNBT,
duplicate-key rejection, personal-to-shared claim consolidation, one-to-many
claim fanout, changed IDs, pinned quest IDs, long timestamp preservation,
round-tripping compact UUID keys, stale-hash rejection, corrupt-input
no-mutation, backup creation, and atomic apply. The tests use an in-memory
fixture and do not prove the actual
world's file path, player membership, inventory, claim UI, repeat reset, or
cooldown behavior. After a reviewed migration, validate the candidate with the
repository SNBT validator and perform a separate stopped-server backup restore
and in-game claim check.

Source provenance: `evidence/20260907-infrastructure-audit/upstream/source.json`
identifies the upstream source as FTB Quests tag `v2101.1.33` at commit
`22fbbb57812a58034a1a561d7cc22f6beae3ca4c`. It is source evidence, not proof
that a particular running server has the same binary or file layout.
