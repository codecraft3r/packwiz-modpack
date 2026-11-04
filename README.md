# Poiesis Creative — Packwiz

A creative multiplayer experience designed in the spirit of a shared SMP world rather than a rigid plot server. Players build collaboratively or independently across a natural, unified world with chunk claiming, deep mechanical automation, expansive architectural palettes, and specialized dimension rules.

| Setting | Value |
| --- | --- |
| Minecraft | `1.21.1` |
| NeoForge | `21.1.265` |
| Java | `21` |
| Tracked Branch | `master` |

---

## Modpack Philosophy & Features

### Creative Multiplayer a-la SMP
* **Shared Open World**: No sterile plot grids or artificial zoning systems. Players share a vast, natural landscape with terrain generation, natural biomes, and collective infrastructure.
* **Land & Chunk Protection**: Managed through **FTB Teams** and **FTB Chunks**, paired with **FTB Xaero Compat** for live map overlays. Players claim and protect land directly from their map and manage team permissions seamlessly.
* **Custom Dimension Spawning Rules & Datapacks**: Spawning configurations and custom datapacks decouple entity pressure from primary building areas, directing specialized spawns to appropriate dimensions and keeping creative spaces performant.

### Core Mod Highlights
* **Management Wanted**: [Five Nights at Freddy's: Management Wanted](https://modrinth.com/mod/management-wanted) bringing interactive animatronics, pizzeria props, stage decorations, and custom themed mechanics.
* **Cobblemon in a Dedicated World**: Full Cobblemon integration configured with dedicated world/dimension spawning rules, allowing Pokémon catching, battling, and training without cluttering mainline creative cities and builds.
* **Create + Create Aeronautics**: Complete engineering contraption suite featuring Create, Create Aeronautics, Aeroworks, Big Cannons, Steam 'n Rails, and Simulated Propulsion for airships, trains, and moving structures.
* **Mekanism Suite**: High-tier tech, processing, energy networks, and tools with Mekanism, Generators, Additions, and Applied Mekanistics.
* **Comprehensive Furniture**: Rich interior design options featuring Handcrafted, Another Furniture, Immersive Furniture, Interiors, Let's Do Furniture, and the full Macaw's design suite.
* **More Extra Blocks Than You Can Shake a Stick At**: Massive decorative variety with Chipped, Rechiseled (including Create, Cobblemon, and AE2 cross-compat sets), Builder's Delight, Copycats+, and Macaw's construction series.
* **Effortless Building & Creative QoL**: Rapid placement tools with Effortless Building, Sidekick creative utility suite, EMI recipe lookup, and Sophisticated Storage.

---

## Install a Client

Create a fresh Prism Launcher or MultiMC instance with Minecraft **1.21.1** and NeoForge **21.1.265**. Place [packwiz-installer-bootstrap.jar](https://github.com/packwiz/packwiz-installer-bootstrap/releases) in its `.minecraft` directory and configure this pre-launch command:

```sh
"$INST_JAVA" -jar packwiz-installer-bootstrap.jar https://raw.githubusercontent.com/codecraft3r/packwiz-modpack/master/pack.toml
```

For reproducible deployments, you can replace the branch name in that URL with a specific commit SHA.

---

## Prepare a Server

See [deployment instructions](docs/deployment-usage.md) for local Docker Compose staging, server sync configurations, and runtime checks. Dedicated servers automatically mount and sync with `pack.toml` via the local runtime stack.

---

## Validate Changes

With Python 3.11+ and [packwiz](https://packwiz.infra.link/tutorials/installing/) installed:

```sh
python3 scripts/validate_snbt.py config/
python3 scripts/test_validate_snbt.py
packwiz refresh
git diff --exit-code -- index.toml pack.toml
```
