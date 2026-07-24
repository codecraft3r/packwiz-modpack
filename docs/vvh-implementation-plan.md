# VvH (Vampires vs Hunters) Implementation Plan

**Status:** Design Phase — **DO NOT IMPLEMENT** before resolving the verification items in **Section 10**.

| Parameter | Specification |
| :--- | :--- |
| **Source** | Review of `~/Downloads/server-plan.txt` (Vampires vs Hunters pitch by H.) |
| **Target Loader / Version** | NeoForge 1.21.1 |
| **Target Population** | 4–6 trusted friends across 2 fixed factions |
| **Enforcement Model** | Two-layer hybrid (Mod-enforced hard bounds + Social soft rules) |

## 1. Core Philosophy

The implementation adheres strictly to the user's standing constraints:

1. **KISS by Default:** Keep technical implementations as simple as possible.
2. **Two Exceptions to KISS:**
   - **Hard Rules:** Prefer technical/mod enforcement over social rules for non-negotiable boundaries.
   - **User Experience:** Accept internal script/config complexity if it reduces end-user headache.
3. **Trust Model:** The server is operated by a primary admin/coordinator (the user) for a small group of trusted friends.

*Note: The original pitch mixed social rules and hard rules. This plan categorizes every requirement into its proper layer and introduces technical mechanisms for hard boundaries previously framed as social rules.*

## 2. Two-Layer Enforcement Model

Every rule in the server design lands in one of two distinct layers. Assigning a rule to the wrong layer is the primary design failure mode.

```
┌─────────────────────────────────────────────────────────────────────────┐
│                           SERVER DESIGN LAYERS                          │
├───────────────────────────────────┬─────────────────────────────────────┤
│  LAYER 1: Hard Rules (Mod-System) │  LAYER 2: Soft Rules (Friend-Trust) │
│                                   │                                     │
│  - System-enforced & automated    │  - Socially negotiated              │
│  - Cheating/griefing impossible   │  - Admin arbitration fallback       │
│  - Claims, borders, scoreboards   │  - Pranks, skirmishes, roleplay     │
└───────────────────────────────────┴─────────────────────────────────────┘
```

* **Layer 1 — Hard Rules (Mod-Enforced):** Violations are technically impossible or unrewarding without admin intervention.  
  *Examples:* Claim protection, world borders, quest rewards, faction-flip tracking, playtime scoreboards.
* **Layer 2 — Soft Rules (Friend-Trust):** Violations carry social consequences among friends; admin acts only as an arbitrator of last resort.  
  *Examples:* Harmless pranks, mercenary contracts, skirmish scheduling, roleplay dynamics.

> **The Enforcement Litmus Test:**  
> *Is this rule **pretending to be enforced by a system**, or **actually enforced by a system**?*  
> If it pretends, rewrite it or move it to Layer 2. If it actually enforces, keep, document, and ship it.

## 3. Master Rule & Feature Mapping

| Pitch Element | Layer | Mechanism | Notes & Architectural Rationale |
| :--- | :---: | :--- | :--- |
| **Faction Join Incentive** | **Hard** | FTB Quests reward tables + scoreboards | Tier set server-wide, applied equally to both factions. |
| **Territory & Claims** | **Hard** | FTB Chunks per-team limits + unclaimable wilderness | Solos: 8 claims (0 force-load). Factions: `floor(in_border / 4)` claims (16 force-load). See §7. |
| **Grief & Theft Protection** | **Soft Tool + Admin** | GriefLogger + scheduled 6h world snapshots | **No rollback mod on NeoForge 1.21.1.** Severe grief restored via full snapshot; minor via social repair. |
| **Faction-Flip Cooldown** | **Soft** | None (no cooldown by design) | Math prevents exploitation; switching is treated as narrative. See §7. |
| **Sanctioned Skirmishes** | **Soft** | Admin scheduling + opt-in PvP toggle | Escalation path documented; no forced schedule mod. |
| **Non-Destructive Pranks** | **Soft** | Hard claim boundaries + friend trust | Hard rule ("No pranks inside claimed territory") eliminates subjective policing. |
| **Mercenary Economy** | **Soft** | Player agreement | Player-driven trading; zero admin code. |
| **Neutrals & Mediators** | **Soft** | Social roleplay | Voluntary player roles. |
| **Creative Milestones** | **Hard** | Rubric checklist + `/vvh reward` command | Objective checks where feasible; admin command triggers math-derived rewards. See §9. |
| **Island World Border** | **Hard** | Vanilla `/worldborder` | Hard border set once at spawn island edge. See §8. |
| **Active Player Definition** | **Hard** | Vanilla playtime scoreboard | 14-day rolling window, ≥ 1 hr threshold. See §5. |

## 4. Faction Join Incentive (Reward Scaling Math)

### Objectives
* Incentivize joining a faction without forcing players onto a specific side.
* Baseline solo play without harsh penalties.
* Eliminate migration pressure (players trying to join the larger team for better loot).

### Mathematical Formula

```
active_factioned  = count(players active AND in any faction)
reward_multiplier = min(2.00, 1.00 + (active_factioned * 0.167))
reward_tier       = active_factioned
```

> **Solo Player Handling:** Solo players are excluded from `active_factioned`. Their playtime is tracked continuously, so if they later join a faction, their activity counts immediately. Solo quest completion defaults to Tier 0 (1.00×).

> **Rounding & Truncation:** Reward calculations **MUST ALWAYS round down (floor)** as minimally as possible to the smallest valid atomic unit of the reward type being dispensed:
> * **Discrete Items (e.g., Diamonds, Ingots):** Round down to the nearest whole integer.  
>   *Example:* $64 \text{ diamonds} \times 1.833 = 117.312 \rightarrow \mathbf{117\text{ diamonds}}$ (not 118, nor 117.312).
> * **Divisible Quantities (e.g., Currency Mods):** Round down to the lowest common denominator unit (e.g., cents).  
>   *Example:* $\$5.00 \times 1.833 = \$9.165 \rightarrow \mathbf{\$9.16}$ (not $\$9.17$, nor $\$9.165$).

### Stepped Tier Table

| Active Faction Players (`active_factioned`) | Reward Tier | Quest Reward Multiplier |
| :---: | :---: | :---: |
| **0** (No factioned players) | Tier 0 | **1.000×** (Baseline) |
| **1** | Tier 1 | **1.167×** |
| **2** | Tier 2 | **1.333×** |
| **3** | Tier 3 | **1.500×** |
| **4** | Tier 4 | **1.667×** |
| **5** | Tier 5 | **1.833×** |
| **6** | Tier 6 | **2.000×** |
| **≥ 6** | Tier 6 | **2.000×** (Capped) |

### Worked Population Scenarios (6-Player Server Cap)

| Faction Split | Active Players | `active_factioned` | Tier | Reward Multiplier |
| :---: | :---: | :---: | :---: | :---: |
| **1 vs 1** | 2 active | 2 | Tier 2 | **1.333×** |
| **2 vs 2** | 4 active | 4 | Tier 4 | **1.667×** |
| **3 vs 3** | 6 active | 6 | Tier 6 | **2.000×** |
| **5 vs 1** | 6 active | 6 | Tier 6 | **2.000×** |
| **4 vs 2** | 6 active | 6 | Tier 6 | **2.000×** |
| **2 vs 1 (1 away)** | 3 active | 3 | Tier 3 | **1.500×** |
| **0 vs 0 (All Solo)** | 6 active | 0 | Tier 0 | **1.000×** |
| **4 vs 1 + 1 Solo** | 5 active factioned | 5 | Tier 5 | **1.833×** |

### Mathematical Design Guarantees
1. **Zero Migration Pressure:** A balanced 3 vs 3 split and an imbalanced 5 vs 1 split yield the exact same multiplier (**2.000×**). Players gain no benefit by piling onto the dominant faction.
2. **Solo is Baseline:** Solo play grants standard 1.000× rewards without dragging down faction calculations.
3. **Every Joined Player Counts:** Each additional active player who joins a faction directly increases the reward multiplier by **+0.167× (+16.7%)**, eliminating dead-zone plateaus.
4. **Stable & Dynamic Scaling:** Simple linear scaling cleanly handles absent or uneven player counts up to the 2.000× cap.

### Rejected Alternatives
* **Exponential Compounding ($1.5^n$):** A 6-player server would result in faction-aligned players getting a 7.59× reward multiplier, destroying game balance.
* **Per-Faction Multipliers ($f(\text{faction\_size})$):** Calculating rewards based on individual faction sizes rather than the server average penalizes the smaller team. Players on the underdog team earn lower reward rates directly correlated with how far behind they are in player count, creating a compounding mechanical incentive to join the larger faction.
* **Imbalance Penalties (e.g., -200%):** Negative rewards add unnecessary complexity for players and admins alike. Deductive reward logic is also bad UX—seeing `"150 - 50 points"` feels like a penalty compared to simply earning `"100 points"`, even though the net result is identical.
* **Real-Time Online Count:** Causes multipliers to swing wildly between gaming sessions.


## 5. Active Population Definition

A player is classified as **Active** if they have accumulated **≥ 1 hour of playtime in the last 14 days**.

* **14-Day Rolling Window:** Prevents rewards from fluctuating mid-session; only the 14-day boundary shifts status.
* **1-Hour Cumulative Floor:** Filters out players who logged in for 2 minutes to AFK or check a chest.

### Scoreboard Data Source
* **Objective:** Vanilla scoreboard `minecraft.custom:minecraft.play_one_minute`.
* **Tick Math:** Ticks once per in-game minute (20 seconds of real-world time).
* **Threshold Value:** A score of `60` equals ~20 real-world minutes of playtime. For server purposes, this initial session threshold qualifies a player as active.

### Server Lifecycle & Edge Cases

```
                                  SERVER START (Day 1)
                                           │
                    ┌──────────────────────┴──────────────────────┐
                    ▼                                             ▼
        Playtime < 60 (~20 mins)                      Playtime ≥ 60 (~20 mins)
                    │                                             │
            Status: INACTIVE                              Status: ACTIVE
                    │                                             │
      (Excluded from active_factioned)              (Included in active_factioned)
```

* **Day 1–14 Bootstrap:** No special catch-up code needed. Playing ≥ 20 minutes on day 1 activates the player immediately.
* **Solo Players:** Playtime is continuously tracked in NBT/scoreboards. Solo players receive 1.00× rewards and are excluded from `active_factioned` until they join a faction.
* **Absences & Vacations:** 14-day grace window ensures players taking a week off do not drop active status or hurt faction multipliers.
* **Persistence Requirement:** Playtime scoreboards **MUST** persist across server restarts (`/scoreboard objectives ... persistent: true`). Verify in §10.

## 6. Architecture & Implementation Surface

### Mod Manifest

| Mod | Purpose | Layer | Configuration Scope |
| :--- | :--- | :---: | :--- |
| **FTB Chunks** | Land claims, team permissions, chunk loading | **Hard** | Claim limits, PvP rules, border restrictions |
| **FTB Quests** | Milestone progression, quest delivery | **Hard** | Quest tree, reward hooks |
| **GriefLogger** | Forensic event logging (block/container/kill) | **Soft Tool** | Logging filters, 30-day retention |
| **KubeJS** *(Installed)* | Reward calculations, custom `/vvh` commands | **Glue** | Server scripts for tier & rubric logic |

### File Surface Matrix
* `config/ftbchunks-common.toml` — Team claim caps, claim protection settings, coordinate restrictions.
* `config/ftbquests-common.toml` — Quest definitions and command reward execution.
* `config/grieflogger-common.toml` — Forensic event tracking filters.
* `kubejs/server_scripts/faction_rewards.js` — Scoreboard calculation, tier resolution, reward delivery.
* `kubejs/server_scripts/vvh_commands.js` — `/vvh claim` and `/vvh reward` command registration.

### Backup & Grief Restoration Architecture

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                        GRIEF PREVENTION & RESTORATION                       │
├───────────────────┬───────────────────┬───────────────────┬─────────────────┤
│    PREVENTION     │    FORENSICS      │   RESTORATION     │ MINOR DISPUTES  │
│                   │                   │                   │                 │
│  FTB Chunks       │  GriefLogger      │ 3-Hour Snapshots  │ Friend Trust    │
│  Claims enforce   │  Logs event data  │ Full world revert │ Offender fixes  │
│  hard protection  │  (No auto-revert) │ for severe grief  │ or admin steps  │
└───────────────────┴───────────────────┴───────────────────┴─────────────────┘
```

#### World Backups (Recovery & Grief Restoration)

On a modded server, a robust world backup system is not only useful for recovering from mod issues or data corruption, but also as the primary mechanism for reverting severe grief damage.

#### Why CoreProtect-Style Rollback Mods Aren't Viable

Attempting block-level rollbacks risks corrupting world state because doing so requires the rollback mod to have native awareness and support for every modded block, item, and entity state it restores—practically requiring custom-built integrations for every mod in existence.

Inventory snapshots suffer a similar flaw: without explicit mod integration, they silently miss custom equipment slots (such as those from Curios or Accessories). Due to these fundamental limitations, CoreProtect-style rollback mods are not a viable option for modpacks.

#### Limitations of Forensic Logging (GriefLogger)

GriefLogger and similar tools cannot log 100% of world events because custom mod logic frequently bypasses standard event hooks. Furthermore, automated machines—such as Create contraptions/deployers or Mekanism digital miners—operate using "fake player" profiles.

Fake player actions obscure accountability in two key ways:
* **Attribution Masking:** Actions are logged under the machine's fake player profile rather than the player who placed or powered it.
* **Shared Identifiers:** Fake player UUIDs are often shared globally across a mod (e.g., all Create deployers on the server log actions under the exact same fake player identity).

Despite these limitations, GriefLogger should provide sufficient data to investigate and resolve the vast majority of day-to-day disputes. While a determined griefer can certainly circumvent event logging, at that point you probably already know who to ban. 

#### Scheduled World Snapshots
* **Mechanism:** Host-level automated script (cron) backing up the world folder (via `rsync`).
* **Cadence:** Every **3 hours**.
* **Retention:** 224 3-hourly snapshots (4 weeks @ 3-hour cadence) + 16 weekly snapshots (~4 months history).
* **Restoration:** Admin manually restores a full world backup upon severe grief or data corruption.

## 7. Faction & Territory Setup

### Faction Structure
* Exactly 2 core factions: **Vampires** and **Hunters** (managed via FTB Teams).
* **One Party Per Player:** A player can belong to only one party at a time. Solo players form their own 1-person party. Faction players belong to the shared faction party.

### Territory & Claim Limits

| Parameter | Solo Player | Vampire Faction | Hunter Faction |
| :--- | :---: | :---: | :---: |
| **Claim Cap** | **8 chunks** | `floor(chunks_in_border / 4)` | `floor(chunks_in_border / 4)` |
| **Force-Load Cap** | **0 chunks** | **16 chunks** (Subset of claims) | **16 chunks** (Subset of claims) |
| **Outside Border** | Unclaimable | Unclaimable | Unclaimable |

**Claim Budget Math:**  
To guarantee that **50% of the world remains unclaimed wilderness** for PvP and resource gathering, the total claim budget for all factions combined is capped at half of `chunks_within_border`. The general formula for each faction's claim cap is:

```
faction_claim_cap = floor(chunks_within_border / (total_factions * 2))
```

For our 2-faction setup (`total_factions = 2`), this simplifies to `floor(chunks_within_border / 4)`.

*Example (1,000 in-border chunks):* Vampires get 250 chunks, Hunters get 250 chunks, and 500 chunks remain wild wilderness. Solo 8-chunk caps do not count against this cap due to their minimal overall footprint.

#### Why Solo Players Are Exempt From the 50% Server Cap

Solo players are not counted against the 50% faction claim pool because their 8-chunk limit is negligible at the player counts this design is intended for. In a 1,000-chunk world, it would take at least **31 solo players** to equal the claiming power of a single faction ($31 \times 8 = 248\text{ chunks} \approx 250\text{ chunks}$), and at least **63 total solo players** to fully saturate the remaining 50% of wilderness ($63 \times 8 = 504\text{ chunks}$).

This design isn't intended to support more than 10–15 total players before requiring major architectural overhauls (since the "trusted player" paradigm breaks down beyond that scale), and realistically the server will only ever see 4–8 players. Over-engineering claim-pooling rules that would only be applicable with server populations that exceed this design's scope would be pointless.

### Force-Loading Rules

```
                      FORCE-LOADING CHUNK POLICY
                      
┌──────────────────────────────────┐  ┌──────────────────────────────────┐
│          ALWAYS-TICK             │  │          PARTY-DYNAMIC           │
├──────────────────────────────────┤  ├──────────────────────────────────┤
│  - Ticks 24/7 (Online & Offline) │  │  - Ticks ONLY when team online   │
│  - Power Generation              │  │  - Item & Mob Farms (prevents    │
│  - Long-cycle Processing (AE2)   │  │    hopper jams & entity buildup) │
└──────────────────────────────────┘  └──────────────────────────────────┘
```

### Team Transfer & Alliance Rules

#### Team Swapping Behavior
* **Solo → Faction:** Solo party dissolves. The 8 solo claimed chunks transfer to the joined faction.
* **Faction → Solo:** Player leaves faction. FTB Chunks generates a new solo party with 8 fresh claims. *Previously contributed claims remain with the faction.*
* **Faction → Faction:** No claim transfer. Old claims stay with the original faction.
* **Faction Flipping:** **No cooldown.** Switching is soft narrative roleplay; reward scaling (§4) prevents mechanical exploits.

#### Allies System Guidelines
* **Permitted:** Solo players allying with a faction to gain shared base/machine access and minimap visibility.
* **Prohibited:** Creating personal sub-territories inside a faction using allies.
* **Reward Impact:** Allies do not affect faction size math. An allied solo player remains Tier 0.

## 8. World Border, Dimensions & Weekly Resets

### Spawn & Border Configuration
* **Spawn:** Central island surrounded by ocean.
* **Border:** Fixed circular/square border set via Vanilla command (`/worldborder set <radius>`).

### Dimensional Reset Matrix

| Dimension | Scope | Policy | Reset Schedule |
| :--- | :--- | :--- | :---: |
| **Overworld** | In-Border | Main base territory, protected land | **Never** |
| **Overworld** | Outside-Border | Renewable wilderness, resource farming | **Weekly** |
| **Nether** | All | Permanent infrastructure & travel routes | **Never** |
| **End** | Main Island | Dragon fight arena & central hub | **Never** |
| **End** | Outer Islands | Elytra, Shulker shells, endgame resources | **Weekly** |

```
                       OVERWORLD ZONING MAP
      ┌────────────────────────────────────────────────────┐
      │  WEEKLY RENEWABLE WILDERNESS (Outside Border)      │
      │  - Unclaimable territory                           │
      │  - Weekly chunk regeneration                       │
      │  ┌──────────────────────────────────────────────┐  │
      │  │  PERMANENT CLAIMABLE ZONE (Inside Border)    │  │
      │  │  - Fixed bases & faction claims              │  │
      │  │  - Spawn Protection Island                   │  │
      │  └──────────────────────────────────────────────┘  │
      └────────────────────────────────────────────────────┘
```

**Why Reset Outside-Border Chunks Weekly?**  
1. Prevents world border generation from permanently cutting off essential structures (villages, ancient cities).  
2. Provides infinite renewable resources without bloating world file sizes.  
3. Ensures players build permanent structures inside the border while treating the exterior as wild wilderness.

## 9. Creative Milestones (Admin Rubric & Commands)

While technical quests (kill mob, craft item) auto-detect via FTB Quests, creative objectives (build a base, design a vehicle) use an **Admin Rubric System** backed by automated reward math.

### Workflow Sequence

```
 ┌──────────────┐     /vvh claim <id>     ┌──────────────────┐
 │  Player      ├────────────────────────►│ KubeJS Checklist │
 └──────────────┘                         └────────┬─────────┘
                                                   │ Scan chunks
                                                   ▼
 ┌──────────────┐    /vvh reward <player> ┌──────────────────┐
 │  Admin       │◄────────────────────────┤  PASS / FAIL     │
 └──────┬───────┘    @admin notification  └──────────────────┘
        │
        ▼
 ┌──────────────┐     Reads scoreboard    ┌──────────────────┐
 │ Reward Multi │◄────────────────────────┤ Apply Mult Tier  │
 └──────────────┘                         └──────────────────┘
```

1. **Published Rubric:** Requirements are published in an in-game handbook (e.g., *House = 4 walls, roof, floor, bed, chest, crafting table*).
2. **Player Claim:** Player runs `/vvh claim <milestone_id>`.
3. **Automated Scan:** Script verifies computable block counts in player claims. Returns PASS or FAIL-with-reason.
4. **Admin Alert:** Admin receives notification: `@admin Player passed build_house. Issue reward?`
5. **Admin Approval:** Admin executes `/vvh reward <player> <milestone_id>`.
6. **Automated Calculation:** Script queries `active_factioned`, determines multiplier tier from §4, and awards the items. **Zero manual math for admin.**

## 10. Pre-Implementation Verification Checklist

*Note: Every item in this checklist **MUST be tested and verified on a NeoForge 1.21.1 test server** before authoring modpack configs or KubeJS scripts.*

- [ ] **10.1 Scoreboard Playtime Tracking**  
  *Task:* Verify `minecraft.custom:minecraft.play_one_minute` ticks on NeoForge 1.21.1.  
  *Command:* `/scoreboard objectives add playtime minecraft.custom:minecraft.play_one_minute`  
  *Fallback:* KubeJS player login/logout accumulator (~40 lines).

- [ ] **10.2 14-Day Playtime Window Mechanics**  
  *Task:* Confirm storage method for rolling 14-day active check.  
  *Decision:* **Path A (Per-player NBT timestamp array)** is recommended over scoreboard decay timers.

- [ ] **10.3 FTB Chunks & Teams Feature Parity**  
  *Task:* Verify FTB Chunks config parameters on 1.21.1:  
  * Per-team claim limits (`floor(in_border / 4)`) and force-load limits (16).  
  * Force-load sub-setting (chunk must be claimed to be force-loaded).  
  * Coordinate-based claim denial outside world border.  
  * Single-party membership enforcement.

- [ ] **10.4 FTB Quests Reward Tier Hooks**  
  *Task:* Test dynamic reward modification via KubeJS event hooks on quest completion.

- [ ] **10.5 GriefLogger Compatibility**  
  *Task:* Confirm GriefLogger (or Forgified Fabric equivalent) installs cleanly on NeoForge 1.21.1 and logs block/container/entity events with configurable retention.

## 11. Soft-Rule Guidelines (Friend-Trust Layer)

The following guidelines are social conventions enforced by friend trust. Admin arbitration serves as the final resort; no mod code is written for these rules.

* **Prank Policy:** Pranks are allowed **only outside claimed territory**. Claims remain strictly inviolable. Disputes are resolved socially or via admin rollback using GriefLogger evidence.
* **Sanctioned Skirmishes:** Opt-in PvP events scheduled by the admin. Outside of events, claim protection keeps PvP disabled.
* **Mercenary Contracts:** Player-negotiated trades, hiring, and favors. Fully player-driven.
* **Diplomacy & Mediators:** Player roleplay interactions without administrative interference.

## 12. Phased Implementation Roadmap

```
 ┌─────────────────────────────────────────────────────────────────────────┐
 │                       IMPLEMENTATION PHASES                             │
 ├──────────────────┬──────────────────┬──────────────────┬────────────────┤
 │ Phase 1: Test    │ Phase 2: Setup   │ Phase 3: Logic   │ Phase 4: World │
 │ Verification     │ & Core Configs   │ & Commands       │ & Launch       │
 │                  │                  │                  │                │
 │ - §10 checklist  │ - FTB Chunks     │ - KubeJS Tier    │ - World border │
 │ - Playtime tests │ - GriefLogger    │   Reward Script  │ - Spawn island │
 │ - FTB caps test  │ - Snapshot cron  │ - `/vvh` claims  │ - Quest trees  │
 └──────────────────┴──────────────────┴──────────────────┴────────────────┘
```

1. **[ ] Phase 1 — Verification:** Complete all test items in [Section 10](#10-pre-implementation-verification).
2. **[ ] Phase 2 — Base Configuration:**  
   * Configure `config/ftbchunks-common.toml` (claim caps, wilderness protection).  
   * Install and configure GriefLogger.  
   * Deploy server-level 6-hour backup cron job.
3. **[ ] Phase 3 — Scripting & Automation:**  
   * Write `kubejs/server_scripts/faction_rewards.js` (tier formula & active player tracking).  
   * Write `kubejs/server_scripts/vvh_commands.js` (`/vvh claim` and `/vvh reward`).
4. **[ ] Phase 4 — World Preparation & Launch:**  
   * Set world border and verify stronghold location inside border.  
   * Build spawn island claim protection.  
   * Populate FTB Quests trees and creative milestone rubrics.  
   * Configure outside-border weekly reset script.

## 13. Reference Documents

* **Parent Pitch Review:** `~/Downloads/server-plan.txt`
* **User System Context:** `~/.claude/memory`
* **Repository Guidelines:** [AGENTS.md](file:///Users/nathanmitchell/packwiz-modpack/AGENTS.md)
* **Design Pattern Skill:** `minecraft-server-design-review`
