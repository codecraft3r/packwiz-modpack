# VvH Quest Map

Status: current generated graph. Quest IDs and dependencies are authoritative
in the chapter SNBT and `campaign_manifest.json`.

## Global flow

```text
Island Charter
  ├─ Name Public Doors
  ├─ Consent First
  └─ Leave Work Standing
        any 2 of 3 ──> Sign the Charter
                         └─> Three Callings
                              ├─ Join the House ──> House of Night core
                              ├─ Choose Neutral ──> protected opt-out
                              └─ Join the Order ──> Lantern Order core
                                    any 1 calling ──> Keep Doors Open
                                                         └─> Market Services
```

## Lantern Order

```text
Join the Order
  └─ Salt and Steel
      └─ Building Supplies
          └─ Long Watch
              ├─ Arcane Spire ──> Mercy Manual / Pure Defense
              ├─ Apothecary Lab ──> Consecrated Work / Refuge Stores
              ├─ Survey Outpost ──> Field Ledger / Patrol Transit
              └─ Garrison Armory ──> Hunter Armament / Siege Artillery
```

## House of Night

```text
Join the House
  └─ First Thirst
      └─ Red Measure
          └─ House Charter
              ├─ Dark Spire Commission ──> Dawn Watch / Nocturnal Broadcast
              ├─ Blood Foundry Commission ──> Sieve Extraction / Sunproof Transit
              ├─ Guest Hall Commission ──> Remedy Counter / Open House
              └─ Blood Vault Commission ──> Crimson Reserve / Scarlet Script
```

All four hubs and their leaves are optional. The current graph has no
any-three-of-eight breadth gate and no team capstone.

## Market Services

```text
Keep Doors Open ──> Read the Board
  ├─ 10 building palettes on the left
  ├─ 5 utility purchases on the right
  ├─ Concord Bond (central civic purchase)
  ├─ Rumour Ledger (weekly team faucet)
  └─ Know the Coins (one-time lesson)
```

The 19-node Market hides dependency lines at chapter level. Each payment
creates one shared reward entitlement for the team. Building purchases reset
after 180 seconds; utility purchases after 300 seconds; the Rumour Ledger
after 604800 seconds. Neutral has no
dedicated faction tree and still reaches Market through `Keep Doors Open`.
