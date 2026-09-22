# Create'a Colony deployment

This branch prepares upstream Create'a Colony **1.1**, CurseForge project `1026019` / file `8773452`, as Packwiz **4.0.0**. It requires Minecraft **1.21.1**, NeoForge **21.1.234**, and Java **21**. All 122 mods are required on their supported sides; client-only mods are excluded by the server installer.

This replaces the Poiesis pack. Use a new instance with an empty data directory and a fresh world. Preserve the current server and its backups separately; changing only its Packwiz URL is not a world migration.

## Pin the prepared pack

The branch URL is:

```text
https://raw.githubusercontent.com/codecraft3r/packwiz-modpack/codex/createa-colony-1.1/pack.toml
```

After checkout of the reviewed branch commit, derive a fixed URL:

```sh
PACK_COMMIT=$(git rev-parse HEAD)
export PACKWIZ_URL="https://raw.githubusercontent.com/codecraft3r/packwiz-modpack/${PACK_COMMIT}/pack.toml"
```

Use that same URL for server and client installation. The commit must have been pushed before GitHub can serve it.

## Isolated Docker staging

The provided Compose file selects the [itzg NeoForge settings](https://docker-minecraft-server.readthedocs.io/en/latest/types-and-platforms/server-types/forge/): `TYPE=NEOFORGE`, `VERSION=1.21.1`, and `NEOFORGE_VERSION=21.1.234`. Its `java21` image uses Java 21. The default host port is **25566** and its dedicated volume is `createa-colony-1-1-data`; do not substitute the existing Poiesis data volume. Memory defaults to 8 GiB and must fit the staging host.

On a host selected for staging, after setting the pinned URL above:

```sh
docker compose -p createa-colony-staging config
docker compose -p createa-colony-staging up -d
docker compose -p createa-colony-staging logs -f minecraft
```

Connect to the staging host on port `25566`. Starting this container accepts the Minecraft EULA through the supplied Compose setting. These are operator instructions; no container start or hosted-server restart is part of branch preparation.

## Panel or manual installation

Create a separate server allocation with Java 21, the exact Minecraft and NeoForge versions above, and an empty data directory. Where the hosting egg supports Packwiz, set its pack URL to the pinned URL and ensure the installer uses server mode. For a [manual Packwiz install](https://packwiz.infra.link/tutorials/installing/packwiz-installer/), place the bootstrap jar in that new server directory and run:

```sh
java -jar packwiz-installer-bootstrap.jar -g -s server "$PACKWIZ_URL"
```

Then launch the NeoForge server using the host's normal NeoForge start command. Packwiz installs the mod/config set; the host must also install the matching loader. Do not point this command at the live server directory.

## Acceptance before promotion

Repository checks validate metadata, exact upstream file coverage, required-mod settings, SNBT grammar, and Packwiz index consistency. They do **not** prove dedicated-server or client runtime compatibility. No boot test has been performed as part of this preparation.

Before scheduling a live change:

1. Finish a dedicated-server boot on the isolated instance; resolve loader or side-related errors and confirm the server reaches its ready state.
2. Boot a fresh client from the same commit, join, and check Create, MineColonies, recipes, world generation, and configured resource packs.
3. Save and restart the staging instance; confirm the fresh world and player progress persist.
4. Keep the existing server files, world, and configuration intact for rollback. Schedule any live replacement separately with explicit restart authorization.

## Maintainer checks and exports

Run the validation commands in the repository README before committing. The pre-commit hook refreshes Packwiz and validates the pack and SNBT; CI repeats these checks. Historical VvH campaign generators do not define this upstream pack's questbook and are not run by this branch's checks.

`Build CurseForge Artifact` and `Build Modrinth Artifact` are manual GitHub Actions. Select this branch in the workflow picker to build downloadable Actions artifacts. They do not create or publish GitHub Releases, push tags, or update the hosted server. Keep any locally generated exports in `dist/`, which is excluded from Packwiz distribution.
