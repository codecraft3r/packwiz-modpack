# VvH Verification Matrix

Status: current.

| Layer | Evidence | Result |
|---|---|---|
| Generator ownership | `scripts/vvh_campaign_v3.py --check` | pass |
| Python syntax | `python -m py_compile` | pass |
| Graph reachability and cycles | `vvh_campaign_v3_validate.py` | pass |
| Charter closure | semantic validator | pass |
| Neutral opt-out | semantic validator | pass |
| Faction breadth truth | semantic validator | pass |
| Hunter/Vampire parity | semantic validator | pass |
| Reward descendant collision | semantic validator | pass |
| Exact registry/component/art allowlists | semantic validator and `ID_CATALOG.md` | pass |
| Generated Packwiz file hashes | semantic validator vs `index.toml` | pass |
| Packwiz index digest | semantic validator vs `pack.toml` | pass |
| Repeatable economy | semantic validator | pass |
| Node overlap and source-line crossings | semantic validator | pass |
| Repository SNBT parser | GitHub validation workflow | required |
| SNBT parser test suite | GitHub validation workflow | required |
| Packwiz refresh/list/idempotency | GitHub validation workflow | required |
| Pinned art archive entry resolution | client/resource-pack environment | pending |
| Minecraft client/server smoke test | human/client environment | pending |

The canonical structured static report is `docs/vvh/evidence/current/campaign-validation.json`.
