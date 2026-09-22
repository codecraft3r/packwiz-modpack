# Create'a Colony — Packwiz

Packwiz conversion of [Create'a Colony 1.1](https://www.curseforge.com/minecraft/modpacks/createa-colony/files/8773452), prepared on branch `codex/createa-colony-1.1` in `codecraft3r/packwiz-modpack`.

| Setting | Value |
| --- | --- |
| Packwiz version | `4.0.0` |
| Upstream release | `1.1` — CurseForge project `1026019`, file `8773452` |
| Minecraft | `1.21.1` |
| NeoForge | `21.1.234` |
| Java | `21` |
| Mods | `122`, all required on their supported sides |

Optional mods are included as required. Client-only mods remain client-only and are excluded from dedicated-server installation. This is a full replacement of the previous Poiesis pack: use a **fresh world and separate server data directory**. Existing-world compatibility is not established.

## Install a client

Create a fresh Prism Launcher or MultiMC instance with the versions above. Place [packwiz-installer-bootstrap.jar](https://github.com/packwiz/packwiz-installer-bootstrap/releases) in its `.minecraft` directory and configure this pre-launch command:

```sh
"$INST_JAVA" -jar packwiz-installer-bootstrap.jar https://raw.githubusercontent.com/codecraft3r/packwiz-modpack/codex/createa-colony-1.1/pack.toml
```

For a reproducible deployment, replace the branch in that URL with the reviewed commit SHA, on both server and clients.

## Prepare a server

See [deployment instructions](docs/deployment-usage.md) for the isolated Docker staging setup, server installer command, and runtime acceptance checks. The branch preparation does not start or restart the hosted server. Static validation does not establish a successful client or dedicated-server boot.

## Validate changes

With Python 3.11+ and [packwiz](https://packwiz.infra.link/tutorials/installing/) installed:

```sh
python3 scripts/validate_colony.py
python3 scripts/validate_snbt.py config/
python3 scripts/test_validate_snbt.py
packwiz refresh
packwiz list
packwiz refresh
git diff --exit-code -- index.toml pack.toml
```

Enable local checks with `git config core.hooksPath .githooks`. CI validates this pack on pushes and pull requests; manual export workflows upload build artifacts without publishing a release or creating tags. The upstream file versions remain pinned: do not run a blanket mod update while preparing this release.
