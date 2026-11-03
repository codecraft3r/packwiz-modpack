# LuckPerms Permission & Group Architecture Guide

This document describes the permission hierarchy, group roles, promotion tracks, privacy protection policies, and in-game/console administration commands configured for this modpack.

LuckPerms integrates natively with NeoForge's `PermissionAPI`, providing granular permission control across **Sidekick**, **Better Item Ban**, **spark**, and the **FTB Suite** (FTB Essentials, FTB Chunks, FTB Teams, FTB Ultimine).

---

## 1. Group Hierarchy & Role Architecture

```
                  ┌──────────────────────┐
                  │        admin         │  (All OPs: luckperms.autoop, "*", instakill)
                  └──────────▲───────────┘
                             │  (Promotion via 'staff' track)
                  ┌──────────┴───────────┐
                  │       manager        │  (Non-OP High Power: ban bypass, moderation tools)
                  └──────────▲───────────┘
                             │  (Inherits)
                  ┌──────────┴───────────┐
                  │         base         │  (All Players: standard utilities, NO instakill)
                  └──────────▲───────────┘
                             │  (Inherits)
                  ┌──────────┴───────────┐
                  │       default        │  (Entry point for new player joins)
                  └──────────────────────┘
```

### A. `base` (All Players)
- **Target Audience**: All regular server players.
- **Inheritance**: Base group; inherited by `default` and `manager`.
- **Sidekick Instant Kill**: **Explicitly Disabled** (`sidekick.power.instakill: false`, `sidekick.instakill: false`).
- **Better Item Ban**: **Bypass Disabled** (`betteritemban.bypass: false`, `itemban.bypass: false`).
- **Standard Player Features**:
  - **FTB Essentials**: `/home`, `/sethome`, `/spawn`, `/tpa`, `/tpahere`, `/back`, `/trashcan`, `/rtp`, `/warp`.
  - **FTB Chunks**: Claiming chunks (`ftbchunks.claim`, `ftbchunks.chunk.claim`).
  - **FTB Ultimine**: Vein mining permission (`ftbultimine.allow`).
  - **FTB Teams**: Party creation and management (`ftbteams.party`).
  - **spark**: Player latency and tick rate checks (`spark.tps`, `spark.ping`).

### B. `default` (LuckPerms Join Group)
- Inherits `base` directly so newly connected players immediately receive all standard player nodes without manual administrator intervention.

### C. `manager` (Non-OP High Power)
- **Target Audience**: Server staff, moderators, and community managers who require high power without full console/root server operator status.
- **Inheritance**: Inherits `base`.
- **Sidekick Instant Kill**: Kept disabled (`sidekick.power.instakill: false`).
- **Better Item Ban**: **Bypass Allowed** (`betteritemban.bypass: true`, `itemban.bypass: true`), plus item-ban administrative commands (`command.itemban`, `command.itemunban`, `command.itembanlist`, `command.itembanstatus`, `command.itembanreload`, `command.itembancleanupworld`).
- **Staff Utilities**:
  - **FTB Chunks**: Admin bypass and management (`ftbchunks.admin`, `ftbchunks.claim_bypass`).
  - **FTB Essentials**: Moderation tools (`ftbessentials.kick`, `ftbessentials.mute`, `ftbessentials.teleport`, `ftbessentials.tpa.silent`, `ftbessentials.tp.offline`, `ftbessentials.fly`, `ftbessentials.heal`, `ftbessentials.feed`, `ftbessentials.invsee`, `ftbessentials.speed`, `ftbessentials.vanish`, `ftbessentials.nickname.others`).
  - **Sidekick**: General utilities and powers (`sidekick.*`).
  - **spark**: Diagnostic monitors and health reports (`spark`, `spark.health`, `spark.tickmonitor`, `spark.gcmonitor`).

### D. `admin` (All Operators)
- **Target Audience**: Server administrators and operators.
- **Inheritance**: Inherits `manager` (and transitively `base`).
- **Permissions**:
  - Root wildcard `*` (full access across all mods and commands).
  - Operator Auto-Synchronization: `luckperms.autoop: true`.
  - Sidekick Instant Kill: `sidekick.power.instakill: true`, `sidekick.instakill: true`.
  - Severe Moderation: `ftbessentials.ban: true`, `command.itembanclear: true`.

---

## 2. Staff Track & OP Synchronization

### A. Staff Track (`staff`)
The promotion ladder for staff is kept completely separate from the base player group:
- **Track Definition**: `manager` ➔ `admin`
- Promoting a user along this ladder:
  ```text
  /lp user <player> promote staff
  ```
- Demoting a user along this ladder:
  ```text
  /lp user <player> demote staff
  ```

### B. OP Synchronization (`auto-op = true`)
- In `config/luckperms/luckperms.conf`, `auto-op = true` is enabled.
- Any player assigned to the `admin` group automatically inherits `luckperms.autoop`.
- Upon joining or world change, LuckPerms automatically grants vanilla Server Operator (OP) status to anyone with `luckperms.autoop`.
- De-opping a player strips OP status unless they possess `luckperms.autoop`.

---

## 3. Data Storage & Player Privacy Protection

To prevent leaking player data (such as player UUIDs, usernames, IP logs, or action history) into Git or exported modpack distributions:

1. **Separated YAML Storage**:
   - Stored in `config/luckperms/yaml-storage/`.
   - Only `groups/` (`base.yml`, `default.yml`, `manager.yml`, `admin.yml`) and `tracks/` (`staff.yml`) are tracked and distributed.
2. **Server UUID Lookup**:
   - `use-server-uuid-cache = true` is set in `luckperms.conf`, preventing LuckPerms from needing a static flatfile UUID-to-name database.
3. **Strict Ignore Rules (`.gitignore` & `.packwizignore`)**:
   - `**/luckperms/**/users/` (dynamic per-player YAML files)
   - `**/luckperms/**/uuidcache.txt`
   - `**/luckperms/**/actions.txt` & `actions.json`
   - `**/luckperms/*.db*`, `*.mv.db`
   - Player data directories: `**/usercache.json`, `**/playerdata/`, `**/stats/`, `**/advancements/`, `**/sessions/`

---

## 4. Manual Console & In-Game Commands Reference

If an administrator prefers to configure or recreate the groups and tracks entirely via in-game or console commands, use the following sequence:

### Step 1: Create Groups
```text
/lp creategroup base
/lp creategroup default
/lp creategroup manager
/lp creategroup admin
```

### Step 2: Establish Inheritance
```text
/lp group default parent add base
/lp group manager parent add base
/lp group admin parent add manager
```

### Step 3: Create Staff Track
```text
/lp createtrack staff
/lp track staff append manager
/lp track staff append admin
```

### Step 4: Configure `base` Permissions
```text
# Sidekick - Disable Instant Kill
/lp group base permission set sidekick.power.instakill false
/lp group base permission set sidekick.instakill false

# Better Item Ban - Disable bypass
/lp group base permission set betteritemban.bypass false
/lp group base permission set itemban.bypass false

# FTB Essentials
/lp group base permission set ftbessentials.home true
/lp group base permission set ftbessentials.spawn true
/lp group base permission set ftbessentials.tpa true
/lp group base permission set ftbessentials.tpahere true
/lp group base permission set ftbessentials.back true
/lp group base permission set ftbessentials.trashcan true
/lp group base permission set ftbessentials.rtp true
/lp group base permission set ftbessentials.warp true

# FTB Chunks, Ultimine, Teams
/lp group base permission set ftbchunks.claim true
/lp group base permission set ftbchunks.chunk.claim true
/lp group base permission set ftbultimine.allow true
/lp group base permission set ftbteams.party true

# spark Diagnostics
/lp group base permission set spark.tps true
/lp group base permission set spark.ping true
```

### Step 5: Configure `manager` Permissions
```text
# Better Item Ban - Allow Bypass & Management
/lp group manager permission set betteritemban.bypass true
/lp group manager permission set itemban.bypass true
/lp group manager permission set command.itemban true
/lp group manager permission set command.itemunban true
/lp group manager permission set command.itembanlist true
/lp group manager permission set command.itembanstatus true
/lp group manager permission set command.itembanreload true
/lp group manager permission set command.itembancleanupworld true

# Sidekick - General access (instakill disabled)
/lp group manager permission set sidekick.* true
/lp group manager permission set sidekick.power.instakill false
/lp group manager permission set sidekick.instakill false

# FTB Moderation
/lp group manager permission set ftbchunks.admin true
/lp group manager permission set ftbchunks.claim_bypass true
/lp group manager permission set ftbessentials.kick true
/lp group manager permission set ftbessentials.mute true
/lp group manager permission set ftbessentials.teleport true
/lp group manager permission set ftbessentials.tpa.silent true
/lp group manager permission set ftbessentials.tp.offline true
/lp group manager permission set ftbessentials.fly true
/lp group manager permission set ftbessentials.heal true
/lp group manager permission set ftbessentials.feed true
/lp group manager permission set ftbessentials.invsee true
/lp group manager permission set ftbessentials.speed true
/lp group manager permission set ftbessentials.vanish true
/lp group manager permission set ftbessentials.nickname.others true

# spark Diagnostic Monitoring
/lp group manager permission set spark true
/lp group manager permission set spark.health true
/lp group manager permission set spark.tickmonitor true
/lp group manager permission set spark.gcmonitor true
```

### Step 6: Configure `admin` Permissions
```text
# Root Wildcard
/lp group admin permission set * true

# Operator Auto-Sync
/lp group admin permission set luckperms.autoop true

# Instant Kill Access
/lp group admin permission set sidekick.power.instakill true
/lp group admin permission set sidekick.instakill true

# Severe Admin Powers
/lp group admin permission set ftbessentials.ban true
/lp group admin permission set command.itembanclear true
```

### Step 7: Assigning Players
```text
# Add a player to Manager
/lp user <player> parent add manager

# Promote along the staff track (manager -> admin)
/lp user <player> promote staff

# Demote along the staff track (admin -> manager)
/lp user <player> demote staff
```
