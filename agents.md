# Packwiz Modpack Import & Release Skill

This document is a custom agent skill file detailing the standard operating procedures for importing mods/packs and releasing new versions of the modpack. 

> [!NOTE]
> This file is excluded from the Minecraft modpack distribution via `.packwizignore` to avoid installing developer context on client/server installations.

---

## 1. Import Workflows

We use the automated Python helper script [packwiz_helper.py](file:///c:/Users/nmitc/packwiz-modpack/scripts/packwiz_helper.py) located at `scripts/packwiz_helper.py` to handle all imports.

### A. CurseForge Imports (URL / ZIP)
To import an official CurseForge zip release or from a direct download URL:
1. Run the helper script:
   ```sh
   python scripts/packwiz_helper.py --source "<URL_or_ZIP_path>" --type curseforge
   ```
2. The helper script automatically downloads URL files to a temporary location, extracts them, runs `packwiz curseforge import`, and refreshes the index.

### B. Modrinth Imports (URL / `.mrpack` file)
To import a Modrinth modpack from a URL or an `.mrpack` file:
1. Run the helper script:
   ```sh
   python scripts/packwiz_helper.py --source "<URL_or_mrpack_path>" --type modrinth
   ```
2. The helper script extracts the package index, queries Modrinth API (`v2/version_files`) in bulk, downloads and calculates hashes for unmatched files to resolve them via CurseForge, copies config overrides, and adds matches using the `packwiz` CLI.

### C. Raw File Imports (Installed `.minecraft` folder / Prism Launcher ZIP)
To import from a raw folder structure or a Prism Launcher instance export ZIP:
1. Run the helper script:
   ```sh
   python scripts/packwiz_helper.py --source "<Folder_or_ZIP_path>" --type raw
   ```
2. **Matching & Resolution Rules**:
   - **Hash Match**: Every `.jar` and resourcepack is hashed (SHA-1, SHA-512, Murmur2).
   - **Lookup Priority**: Search **Modrinth** first. If not matched, search **CurseForge** (using the embedded public developer key, or `CURSEFORGE_API_KEY` environment variable).
   - **Large Files Exclusion**: Large files (`.jar` and resourcepack/shaderpack `.zip`s) **MUST NEVER** be committed to the Git repository or saved locally. If a large file cannot be matched to a hosted version on Modrinth/CurseForge, print a warning list of the unmatched files and instruct the user to host them externally.
   - **Small Files Inclusion**: Small files (configs in `config/`, KubeJS scripts in `kubejs/`, or custom datapacks/local overrides) that do not match hosted files **CAN** be copied to the workspace override directories and committed to Git.
   - **Sidedness Logic**: Exclude mods from a side only if they are incompatible. If it can run on both sides, default it to `both`. Use the hosting provider metadata and filename keywords to determine:
     - **Client-Only Mods**: HUDs, Minimaps, Iris, Sodium, controlling, keybinds, etc. (Side: `client`).
     - **Server-Only Mods**: Backup tools, chunk pre-generators, admin essentials, etc. (Side: `server`).
     - **Default**: Side: `both`.

---

## 2. Packwiz CLI Rules

- **ALWAYS** use the packwiz CLI for creation, deletion, and interaction with packwiz `.toml` files. Do not edit `.pw.toml` files manually unless setting the `side` parameter or other settings that do not have CLI commands.
- If you edit any non-packwiz override files (configs, scripts, etc.) manually, you **MUST** run `packwiz refresh` to regenerate file hashes in the `index.toml` before adding and committing them to Git.

---

## 3. Release and Tagging Guidelines

### A. Pre-Release Verification
Run these validation commands from the repository root:
```sh
packwiz refresh
packwiz list
```
Check that the count of generated metadata files matches the expected number:
- `find mods -maxdepth 1 -name '*.pw.toml' | wc -l`
- `find resourcepacks -maxdepth 1 -name '*.pw.toml' | wc -l`

### B. SemVer Spec for Releases
Always format releases according to the following SemVer guidelines:
- **MAJOR**: Bump on full pack replacement OR other world-breaking changes (world continuity is not guaranteed across MAJOR versions).
- **MINOR**: Bump on a client-incompatible server change AND/OR server-incompatible client change (i.e. "both client and server must be updated to connect").
- **PATCH**: Bump on backwards-compatible server changes AND/OR backwards-compatible client changes (i.e. clients or servers on prior MINOR versions can still connect without issue).

### C. Git Tagging
- **NEVER** replace or modify existing git tags.
- Always create a new git tag corresponding to the new version (e.g. `v1.0.1` or `v2.0.0`) and push it.
  ```sh
  git add .
  git commit -m "release: v1.0.1"
  git tag v1.0.1
  git push origin main --tags
  ```
