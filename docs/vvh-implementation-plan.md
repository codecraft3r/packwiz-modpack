# VvH Implementation Plan

> **Source:** Review of `~/Downloads/server-plan.txt` (Vampires vs Hunters pitch by H.)
> **Loader / version:** NeoForge 1.21.1
> **Population target:** 4–6 trusted friend players, always exactly 2 factions
> **Status:** Design phase, NOT implementation. Do not implement before verification items at the bottom of this doc are resolved.

---

## 1. Philosophy

The user's standing constraints (from `~/.claude/memory`):
- KISS by default for all technical implementation.
- Two exceptions: (a) prefer enforceable tech over social rules for **hard** rules, (b) accept complexity to reduce end-user headache.
- Server is run by a primary admin/coordinator (the user). Players are trusted friends.

The friend's pitch is mostly-correct in direction but mixes soft rules and hard rules. The job of this plan is to sort each rule into the correct layer and propose a tech-backed replacement for any hard rule that the pitch treats as social.

---

## 2. Two-Layer Enforcement (Summary)

Every rule in the design lands in one of two layers. A rule in the wrong layer is the design's biggest failure mode.

### Layer 1 — Hard rules (mod-enforced, automatic)

Rule-breaking should be technically impossible or unrewarding without admin action.

Examples: claim borders, block logging, structure detection, faction-flip cooldown, anti-AFK.

### Layer 2 — Soft rules (friend-trust, optional admin arbitration)

Rule-breaking has social consequences within the player base.

Examples: "harmless pranks," mercenary-for-hire dynamics, skirmish timing, faction roleplay.

### Litmus test

> Is this rule **pretending to be enforced by a system**, or **actually enforced by a system**?

If pretending: rewrite or move to layer 2. If actually enforcing: keep, document, ship.

---

## 3. Final Map of Pitch Elements

| Pitch element | Final layer | Mechanism | Notes |
|---|---|---|---|
| Faction join incentive | Hard | FTB Quests reward tables keyed to scoreboard | Tier chosen by server, applied equally to both factions |
| Cross-faction territory | Hard | FTB Chunks per-team mode | Bases inside claims are inviolable; outside is fair game |
| Grief / theft disputes | Soft-tool + ops | GriefLogger (logging only) + scheduled world snapshots | **No rollback on NeoForge 1.21.1.** Logs are positive-confirmation only; severe grief restore from snapshot (covers *all* modded inventories because they're world state); minor grief via social/manual restoration. Inventory-snapshot tools deliberately excluded — see §6. |
| Faction-flip cooldown | Soft (no cooldown by design) | Friend-trust | See §7 for the no-cooldown rationale |
| Skirmishes (admin-overseen) | Soft | Friend-trust + admin scheduling | Escalation path documented; no in-game enforcement |
| Pranks (non-destructive) | Soft | Friend-trust | Hard-enforce "no pranks in claimed zones" instead of policing harmfulness |
| Mercenary / bribery economy | Soft | Friend-trust | Player-driven; no admin rules |
| Neutrals as spies / mediators | Soft | Friend-trust | No policy |
| Milestones with depleting rewards | Hard | FTB Quests reward tiers | Use objective-detection where possible; admin-judged for creative ones (see §9) |
| Island + world border | Hard | Vanilla `worldborder` | Set once; see §8 for per-dimension reset policy |
| Active player definition | Hard (data) | Vanilla playtime scoreboard | See §5 |

---

## 4. Faction Join Incentive — Math

### Goal

Incentivise players to join a faction. Don't care which side. Don't penalise solo beyond a flat baseline. Don't trigger migration pressure.

### Formula

```
active_factioned     = count(players who are active AND in any faction)
mean_size            = floor(active_factioned / 2)        # always 2 factions
reward_tier          = tier_table[mean_size]              # stepped at integer mean
```

**Solo players** are excluded from `active_factioned_count` while solo. Their playtime is still tracked, so when they join a faction their history is immediately included.

### Tier table (stepped at integer mean)

| mean_size | tier | quest reward mult |
|-----------|------|-------------------|
| 0 (zero factioned) | 0 | 1.00× |
| 1 | 0 | 1.00× |
| 2 | 1 | 1.25× |
| 3 | 1 | 1.25× |
| 4 | 2 | 1.50× |
| 5 | 2 | 1.50× |
| 6 | 3 | 1.75× |
| ≥ 4 (cap) | 3 | 1.75× (capped) |

**Note on capping:** capped at mean=4 because that's the maximum realistic for a 6-player server (6/2=3) plus one extra tier for larger servers. Anything beyond is server-misconfigured territory.

### Worked scenarios for a 6-player cap

| Scenario | active_factioned | mean_size | tier | mult |
|---|---|---|---|---|
| 2/2 split, all active | 4 | 2 | 1 | 1.25× |
| 3/3 split, all active | 6 | 3 | 2 | 1.50× |
| 5/1 split, all active | 6 | 3 | 2 | 1.50× |
| 4/2 split, all active | 6 | 3 | 2 | 1.50× |
| 2/2 split, one on vacation | 3 (one drops below 1-hr threshold) | 1 | 0 | 1.00× |
| 6/0 (entirely solo) | 0 | 0 | 0 | 1.00× |
| 4/2 split, 1 solo | 5 | 2 | 1 | 1.25× |

### Properties

1. **No migration pressure.** A 2/2 split and a 5/1 split (all 6 active) both produce mult=1.50×. Players don't optimise by joining the bigger side.
2. **Solo is baseline, not penalty.** Solo players get 1.00×. They don't drag anyone else down.
3. **Late joiners are welcomed.** Mean goes up; mult goes up; everyone benefits.
4. **Floor on odd populations** documented and stable.

### What was rejected

- Friend's original `1.5^n` compounding (a 6-player faction gets 7.59×). Breaks math, breaks cap, drives migration pressure.
- Per-faction-size multipliers (`reward = f(this_faction_size)`). Triggers migration pressure automatically.
- Negative penalty for imbalance (`-200%/excess-player`). Negative rewards are an arbitrary hard rule with no clean delivery.
- Raw player count (online now). Wobbles between sessions; treats AFK as engaged.

---

## 5. Active Population Definition

### Policy

> **Active** = player has ≥ 1 hour cumulative playtime in the past 14 days.

Why:
- 14-day window freezes the input; only the boundary moves. Players don't see their rewards wobble mid-session.
- 1-hour floor prevents AFK-from-a-week-ago credit.
- Cumulative, not "logged in at least once," because a player who logged in for 5 minutes 13 days ago has effectively abandoned the server.

### Data source (intended)

Vanilla scoreboard objective: `minecraft.custom:minecraft.play_one_minute`.

- Ticks once per **in-game minute** the player is online (20-second real time, since one Minecraft day is 24000 ticks = 20 real minutes).
- Score 60 corresponds to roughly **20 real minutes** of online time, NOT 60.
- This means the "1-hour" threshold via this objective is actually closer to ~3 in-game hours / ~20 real minutes first session. Acceptable for our purposes: a player's first play session usually exceeds this.

### Transition behaviour (first 14 days of server life)

No player has 14 days of history on day 1. Default behaviour:

- Players with `playtime < 60` are not active yet.
- Players with `playtime ≥ 60` ARE active.

No special day-1 fallback code. Players who play 20+ real minutes their first session are immediately classified as active. Players who log in once and leave stay inactive until they come back.

The user accepted the "rising tide lifts all ships" effect: rewards grow with engagement in the first two weeks. Expected.

### Solo player handling

Solo players:
- Have their playtime tracked (so history exists if they later join a faction).
- Are **not counted** in `active_factioned`.
- Get the 1.00× baseline reward for any quest they complete alone.

### Why this population definition is right

- It survives vacation, illness, lost-interest-for-a-week (which is the most common failure mode on friend servers).
- It does not wobble between sessions, only at the 14-day boundary.
- It does not require "online now" prediction, which a 4–6 player server can't reliably do.

### Persistence requirement

The playtime scoreboard MUST persist across server restart. Verify with `scoreboard objectives ... persistent: true` (or the equivalent in NeoForge 1.21.1). **This is a verify-before-implement item.** See §10.

---

## 6. Implementation Surface (What's Actually Going Into The Modpack)

### Mods (added or already present)

| Mod | Purpose | Layer | Mod-side complexity |
|---|---|---|---|
| **FTB Chunks** | Per-team land claims, load-and-forget | Hard | Low — config once |
| **FTB Quests** | Task system, reward tiers, milestone tracking | Hard | Medium — content layer requires design later |
| **GriefLogger** (or equivalent) | Block / container / entity log for grief **lookup only** — no rollback | Soft-tool | Low — load-and-forget, install + configure |
| **KubeJS** (already present) | Tier computation, playtime tracking fallback if needed | Glue | Low–medium — see §9 |

### Config files (intended, not yet authored)

- `config/ftbchunks-common.toml` — per-team mode, claim block list, PvP in claims config.
- `config/ftbquests-common.toml` — reward tiers (deferred until §10 verification).
- `config/grieflogger-common.toml` (or relevant config path) — what to log, log retention window, query tool access.

### Scripts (intended, not yet authored)

- `kubejs/server_scripts/faction_rewards.js` — quest-completion hook, scoreboard lookup, reward tier application.
- (Optional) `kubejs/server_scripts/playtime_decay.js` — 14-day window logic if we choose path B in §10.

### Grief / Disputes: Logging Without Rollback

**Constraint (confirmed):** NeoForge 1.21.1 has no good automatic-revert mods. GriefLogger provides **logging only** — no rollback. This is the only grief-tool layer we get.

**What GriefLogger gives us:**

- **Block break / place log** — who broke / placed /this block/ and when.
- **Container access log** — who opened /this chest/ and what they took.
- **Entity-kill log** — who killed /this mob/ and with what.
- **Item pickup / drop log** — for catching item theft out in the open.

**What GriefLogger does NOT give us:**

- **Automatic rollback.** A grief event requires the offender (or the admin) to manually restore the world. There is no `/co restore` equivalent.
- **Block-item restoration across versions.** Even manual restoration is annoying for large incidents because of NBT/enchantment mismatches.

**Why this is acceptable on a friend server:**

- Friend-trust is high. Most incidents will resolve via acknowledgement + manual restoration by the offender without admin intervention.
- **Claims are the primary defense.** FTB Chunks keeps grief out of in-border bases entirely. GriefLogger only matters for *outside-border* grief (the renewable wilderness) and *post-incident* resolution on claimed territory the offender got into (rare if claims are properly enforced).
- **Disputes are slow and rare.** When they happen, manual restoration by the offender is the natural response on a friend server.

**Why this is acceptable on the boundaries:**

- If an offender refuses to restore, the admin acts on authority. The admin has GriefLogger logs to confirm what was destroyed and what should be restored.
- If grief recurs, escalation comes from social consequences, not from automatic ban logic.

**Implementation note:** GriefLogger requires the player to issue a lookup query to retrieve logs (e.g., `/grieflogger` or similar command). This means grief evidence is **available on demand** but not **surfaced proactively**. The friend-trust layer assumes players will report issues; GriefLogger answers "who did what" once a report is filed.

**Compare to CoreProtect-era design:** the original design assumed we could resolve disputes from a forensic UI and auto-revert damage. We cannot. Adjust the design accordingly:
- Treat prevention (claims) as the dominant defense.
- Treat logging (GriefLogger) as a forensic tool, not a restoration tool.
- Treat restoration as a social consequence, not an automated undo.

### Why Player-Inventory Snapshot Tools Don't Help Here

**A common pitch:** "add a per-player inventory snapshot tool that hooks into mod inventories too — Curios, Iron's Spells spellbooks, accessory slots, backpack mod contents." Intuition: "more hooks = more complete snapshot = better restore."

**Why this is wrong in modded contexts:**

- **"Player inventory" is not a single thing.** It's at minimum: vanilla main inventory, ender chest, shulker contents (nested), Curios slots, mod-specific slot systems (Iron's Spells spellbook, Accessories ring slots, backpack mod inventories), shared-network inventory containers, mount inventories, tamed-mob inventories, modded trash-void bags, and any inventory attached to modded blocks within reach (chests, barrels, etc.). Each is its own NBT tree with its own mod's event API.
- **Coverage is unknowable in advance.** A snapshot tool that integrates with Curios, Iron's Spells, and Accessories today misses whatever mod the user adds next month. As mods rotate in/out of the packwiz, integrations break. Each integration is maintenance debt.
- **Failure mode is silent.** A snapshot that misses the main inventory fails loudly — the visible inventory is empty, the issue is obvious. A snapshot that misses Curios slots shows a "full" inventory with the inserted items present, because the inventory screen reads the live slots — *not* the snapshot. The grief surfaces only when the player logs back in, finds an inconsistent restore, and reports it. By then the restore window has closed.
- **Block-rollback and inventory-snapshot share the same blindness.** Both attempt to undo at event level in a system where events are not exhaustive. Both produce silently-incorrect restores.

**Conclusion:** inventory-snapshot tools have the same falsifiable-false-friend property as block-rollback. We don't add them. We don't recommend them. If a community tool claims to handle this on modded, take it on faith only after testing it on a *known-bad* restore where you've deliberately griefed yourself.

### Restore Mechanism: Scheduled World Snapshots

**Why this exists:** in a modded world, no in-game undo is trustworthy. Block restore is straightforward, but modded internal state (machine connections, schematic ownership, network channel allocation, AE2 quantum states, mob AI memory, etc.) lives outside blocks. Restoration of a chunk restores the visible chunk; the world's causal graph has drifted.

**Solution: scheduled full-world snapshots.** A cron-style job (external to the MC server) snapshots the world directory every X hours. When severe grief happens, restore is from the most recent known-good snapshot.

**Operational properties:**

- **Atomicity.** Each snapshot is a complete world state at one instant. Restoration restores the whole snapshot, not a chunk — no partial restoration drift.
- **Cost.** Snapshot size ≈ world-on-disk. For a friend-sized world (a few hundred MB to a few GB), this is manageable. Disk space is the only budget — typical retention policy: 24 hourly + 7 daily + 4 weekly, then prune.
- **Caveat: gameplay loss is total, not partial.** If the snapshot was 2 hours old, anything progressed in those 2 hours is lost too. Choose snapshot cadence against the cost of losing progress.
- **Caveat: cross-server version compatibility.** Snapshots are version-coupled. Don't try to restore from a snapshot taken under MC 1.21.1 into a world now running 1.22 — block IDs may differ. The snapshot is bound to the version that created it.

**Why this beats any in-game rollback mod:**

- Snapshot is exactly what the world's filesystem looked like at T₀. No event subscription drift, no state-tracking gaps.
- It works with mods because it doesn't try to understand them — it just copies files.
- It covers **all** player state — main inventory, ender chest, modded inventory slots, curios, modded slot systems, tamed-mob inventories — because all of that is stored as NBT inside the world data. There is no per-mod integration to write or maintain.
- The price is "lose more than you wanted to restore," which is a clean tradeoff that's predictable.

**Implementation surface:**

- Server-side cron job (e.g., `cron`, systemd timer, or scheduled task).
- `tar` or `rsync` snapshot of the world directory (or a Copy-on-Write filesystem backing the world for cheap incrementals).
- Retention script that prunes old snapshots per the policy above.
- **Manual invocation only for restore.** Even when grief happens, the admin makes the call to restore, picks the snapshot, and merges any in-flight progress the snapshot lost. There's no automation around this.

**Configuration defaults:**

| Parameter | Default | Why |
|---|---|---|
| Frequency | Every 6 hours | Acceptable progress loss (~6h of building). 4 snapshots/day. |
| Retention | 24 hourly + 7 daily + 4 weekly | ~31 snapshots; ~3 days of recent hourly, week of daily, month of weekly. |
| Stored path | `~/server/backups/` or external volume | Configurable; off-disk backups recommended. |
| Automation | Yes (cron) | Set-and-forget; admin doesn't touch this daily. |

**Why not just say "version the world via git"?** Worlds are tens of thousands of regions; git isn't designed for binary tree diff. Filesystem snapshot tools do this better. Use the right tool.

**Why not just rely on GriefLogger's logs?** Because the logs are not the world. Even if you have a forensic record of what was destroyed, you can't replay the destruction in reverse — you have to recreate the lost state from snapshot, not from logs.

**Trade-off summary:**

- GriefLogger = "we know what happened; useful for adjudicating *who did what*."
- World snapshots = "we can return to a known-good state; useful for *undoing severe grief*."
- Manual restoration by offender or admin = "social path; the friend-trust answer for small incidents."

These three layers complement each other. None alone is sufficient; together they cover the grief prevention/identification/restoration problem.

---

## 7. Faction & Claim Configuration

### Factions

- Always exactly 2 factions: **vampires** and **hunters**.
- Faction = FTB Teams team. Members granted by `/ftbteams join` or equivalent. Server-side, no UI in base game.
- Membership is the only hard-side property used by reward math.

### Claims

- FTB Chunks per-team mode: each team's claim is its territory.
- Inside claims: block break/place by non-members forbidden, PvP requires explicit opt-in, TNT off (default for safety).
- Outside claims: fair game. Pranks, skirmishes, mercenary activity all happen here.
- Players can't claim across the world border (set in §8).
- **Starter zone (admin-claimed at launch):** a small area around spawn is pre-claimed by both factions (or by the admin on behalf of any player) so new players have automatic protection while they learn the claim system. Without this, grief hits unprotected starter territory in week one, and GriefLogger can't undo it. The starter zone is a one-time admin setup at launch; not part of §6's per-day operation.

### Faction-flipping

**Decision: no cooldown.** Soft rule. Players can switch teams at-will.

**Reasoning (lifted from the friendly-side comment in §3):** with the new reward math, switching doesn't game the system. The mean is a global value applied equally, and a solo player is baseline. Switching produces no mathematical advantage — the only reason to switch is roleplay, which is the soft layer.

**Side effects (intentional):** Faction-flipping becomes a source of "fun drama." A player hopping vampires → hunters → vampires is a soft-story beat, not a tactical exploit. The friend-trust layer handles this with social consequence, not code.

**No KubeJS needed.** Drop the planned cooldown implementation entirely.

---

## 8. World Border & Spawn

### Spawn

- Central island, surrounded by ocean. World border at island edge.
- `worldborder set <radius>` once at world creation. Vanilla command, no mod dependency.

### Nether / End policy (launch-time)

**Policy (confirmed):**

- **Stronghold within world border, before launch.** The admin team locates and confirms at least one stronghold spawn exists inside the world border before launch. If it doesn't exist in the natural seed, the admin regenerates chunks / pre-generates until one is within the border. This avoids the "End fight impossible" failure mode mid-game.
- **Main End island is NOT reset.** The obsidian pillars, exit portal, and dragon egg pedestal are preserved indefinitely. The End is a one-shot dimension for the dragon fight, then becomes an End-game resource dimension (elytra, shulker shells).
- **End outer islands ARE reset weekly.** Once the dragon fight is complete, the chorus-fruit islands, end cities, elytra shrines, and outer End ring become a renewable resource dimension — same weekly cadence as the Overworld outside-border reset. Players can re-farm shulkers, chorus, elytra, etc., on a fresh rotation. The main End island is the single exempt zone.
- **Nether reset:** no reset. Players can build permanent infrastructure there.
- **Nether portals:** players can build portals anywhere they like, **but portals placed outside the world border (Overworld side) get deleted on the weekly reset.** This is enforced naturally — anything inside a chunk that gets reset to vanilla is destroyed. So a portal inside the border survives forever; a portal in an outside-border chunk is part of the renewable wilderness and goes with the reset.

**What this means in practice:**

| Dimension | Behavior | Reset | Notes |
|---|---|---|---|
| Overworld (in-border) | Permanent base territory | No reset | Main island, claim zones, faction infrastructure. Grows indefinitely. |
| Overworld (outside-border) | Renewable wilderness | Weekly | Resources, monuments, structures, outside-border portals. |
| Nether | Permanent second base | No reset | Players build freely. Portals anywhere. |
| End (main island) | One-shot fight + preserved hub | No reset | Dragon fight, exit portal. |
| End (outer islands) | Renewable endgame resources | Weekly | Chorus, end cities, elytra, shulkers. The main island is the single exempt zone in End. |

The "outside the main hub = renewable wilderness" rule is now consistent across both dimensions that have a hub. The Overworld's main island and the End's main island are the two preservation zones; everything else resets.

### Automatic weekly reset of chunks outside the world border

**Status:** *in-scope, designed as part of v1.*

**Mechanism:** A scheduled KubeJS / datapack job that, on a weekly cadence (e.g., every Friday at off-hours), resets chunks outside the world border to their original generation state in the Overworld only.

**What this solves:**

1. **World border cutting off progression-required structures.** If a village, ancient city, shipwreck, or other valuable structure happens to spawn just outside the border, the players are locked out. Weekly reset shifts that — structures regen, players get a chance to discover them next week.
2. **Forcing in-border sprawl.** Without outside-border regen, players eventually face a choice between "build outside the border (and lose it to resets)" or "build cramped in-border." Weekly reset makes outside-border essentially wilderness to explore, not territory to claim.
3. **Resource exhaustion.** Outside-border is the renewable resource farm zone. Reset every week means new mines, new trees, new monuments. The in-border main island stays built-up; the exterior stays wild.

**What stays safe:**

- The Nether and End dimensions are NOT subject to this reset.
- The main End island (where the dragon fight happens) is explicitly NOT reset.
- Chunks that are *claimed* by a faction (FTB Chunks) outside the border are NOT reset — claiming outside the border is permitted (encouraged, even), but claims reset on the same weekly cadence only if the player unclaims first.

**Implementation surface:**

- KubeJS server-side weekly tick (`onEvent('server.tick')` with a date check, or `player.json` cron-like).
- The actual chunk reset is the only non-trivial piece. Options:
  - **Pre-existing tooling:** "MCA Selector" (external) is the standard community tool for this, but it's offline-mode / admin-triggered.
  - **Bukkit-like API:** NeoForge's API doesn't natively expose "regenerate chunk" but does expose chunk data. A custom plugin / mod could implement this.
  - **A small dedicated mod:** e.g., "Reset" mod or similar (verify availability on NeoForge 1.21.1 at implementation time).
- **Caveat:** the actual regeneration mechanism is the implementation question, not the design question. Design accepts "some mechanism that resets outside-border chunks to vanilla default on a weekly schedule, excluding claimed chunks and excluding Nether/End."

**Design rule:** weekly reset applies to **Overworld only, outside-border only, claimed chunks exempted**. Anything else is implementation flexibility.

---

## 9. Creative Milestones — Admin Rubric + Command-Issued Rewards

Most quests auto-detect through FTB Quests (kill X, place Y blocks, craft Z). But the pitch's "creative" content (build a house, build a vehicle, design a farm) cannot be auto-detected reliably. This is where the system bridges to soft judgement while keeping the reward math hard.

### Rubric model

Each creative quest lists a checklist of structural requirements, e.g.:

> *Build a house* = enclosed structure with ≥ 4 walls, a roof, a floor, ≥ 1 chest, ≥ 1 crafting table.

The rubric is **published and stable**. Players know exactly what they need to satisfy. No surprises.

### Workflow

1. Player claims completion via a chat command: `/vvh claim <milestone_id>` (e.g., `/vvh claim build_house`).
2. The script scans the player's claim chunks for the rubric conditions, where computable (block counts, block types). Returns PASS or FAIL-with-reason.
3. On PASS, a notification posts to admin chat: `@admin <player> has passed <milestone_id>. Issue reward?`
4. Admin runs `/vvh reward <player> <milestone_id>`. The script **reads the current `active_factioned` scoreboard**, computes tier per §4, issues the appropriate reward. **No math on the admin side.**
5. The script records the milestone as completed for that player in persistent data so it can't be claimed twice.

### Where hard meets soft

- **Rubric validation: hard.** Code runs the checklist, returns pass/fail.
- **"Looks good enough" judgement: soft.** Admin can override a FAIL → reward (e.g., the rubric missed a creative interpretation the player found). Admin can refuse a PASS → no reward. Both are admin prerogative. The script just makes the common case zero-effort.
- **Reward tier: hard.** Set by `floor(active_factioned / 2)` from §4. The admin's command can't pick a different tier — the system applies the rule.

### Worked example

Server state: 4 active factioned players (2/2 split). Mean = 2 → tier 1 → 1.25× reward.

1. Sarah runs `/vvh claim build_house`.
2. Script scans her claim chunks: 4 walls, 1 roof, 1 floor, 3 chests, 1 crafting table. PASS.
3. Admin chat: `@admin Sarah passed build_house. Issue reward?`
4. Admin runs `/vvh reward sarah build_house`.
5. Script reads `active_factioned = 4`, computes tier = 1, awards the 1.25× reward set.
6. Sarah has her reward. **Admin typed one command. Total time: ~10 seconds.**

### Implementation surface

- KubeJS server-side script for:
  - Command registration (`/vvh claim <id>`, `/vvh reward <player> <id>`).
  - Block-count validation against rubric (scan claim chunk bounding box, count block types, compare to rubric thresholds).
  - Reward tables keyed to tier index (4 tiers: 0, 1, 2, 3 → 4 reward sets).
  - Per-player NBT or scoreboard objective tracking completed milestones (to prevent double-claim).
- An in-game book (admin-editable) documenting rubrics. **The book is the user's documentation surface** — they update rubrics without restarting the server.

### What this changes for the user (admin)

The creative quest subsystem is:
- **Writing rubrics** (one paragraph per quest).
- **Defining reward sets** (4 tiers × N creative quests = N reward sets, each tier-multiplied).
- **Running a one-line command per completion** when a player passes.

No napkin math. No manual lookup tables. The system enforces tier automatically.

---

## 10. Open Questions / Verify-Before-Implementing

Each item below must be resolved before any code is written.

### 1. Vanilla `play_one_minute` on NeoForge 1.21.1

- **Question:** Does the objective tick on NeoForge 1.21.1 servers as documented in vanilla?
- **Verify:** Drop into a test world, run:
  ```
  /scoreboard objectives add playtime minecraft.custom:minecraft.play_one_minute
  /scoreboard objectives setdisplay list playtime
  ```
  Log in, play 5 minutes, check `/scoreboard players get @p playtime`.
- **Fallback if broken:** KubeJS accumulator pattern (log on/off events, sum to scoreboard). ~40 lines.

### 2. 14-day window mechanism

Three viable paths. **Choose one explicitly before implementing.**

| Path | What it is | Surface area | Failure mode |
|---|---|---|---|
| A. Per-player NBT | Store `last_active_timestamps` in player persistent data; query on quest completion | Low if NBT fits; ~30 lines | NBT bloat if too many timestamps stored |
| B. KubeJS scheduled task | Decay scoreboard every 14 in-game days | Medium; requires scheduled events | Timer drift if server restarts mid-window |
| C. Approximate (recent-login yes/no) | Replace 1-hour cumulative with "logged in within last 14 days" | Lowest | Loses the "actually played" nuance; one-tap visit satisfies |

**Recommendation:** Path A. It's the only one that exactly matches the stated policy.

### 3. FTB Chunks per-team config

- Verify claim block allow-list (no end-of-game items, no Dragon Egg, etc.).
- Verify PvP-in-claim defaults.
- Confirm: outside-claim is "anything goes," not "PVP-only-when-on."

### 4. FTB Quests reward tier structure

- **Defer to content-design phase.** Structure first, reward tables later.
- Open question: are rewards items (e.g., diamond gear), recipe unlocks (custom crafting table gates), or both?

### 5. GriefLogger support on NeoForge 1.21.1

**Confirmed constraint (from user):** NeoForge 1.21.1 has no good rollback mods. GriefLogger provides logging only; no automatic revert.

**Verify (per §13's wider GriefLogger note):**

- Confirm GriefLogger is published for NeoForge 1.21.1 (or via Forgified Fabric API on this modpack).
- Check what it logs: blocks, containers, entity-kills, item pickups. Whatever it covers is what we have for forensics.
- Confirm log retention / size bound (30 days typical, must be configurable).

**Fallback if GriefLogger is not on NeoForge 1.21.1:**
- Log nothing about grief (rely entirely on claims for prevention, soft rules for resolution).
- Accept that "evidence" in a dispute resolution becomes testimony, not data. Friend-trust and admin judgment carry the burden.

**Implication:** any restoration of griefed content is **manual** — the offender does it, or the admin does it on their authority. The "automatic revert" property that rollback mods provide on Bukkit/Paper server stacks is unavailable here.

---

## 11. Soft-Rule Notes

The friend-trust layer governs the following. Admin arbitration is the escalation path; there is no in-game enforcement and the modpack does not encode these rules.

### Pranks

- Players can prank each other outside of claimed territory.
- "Harmless / reversible" is descriptive, not prescriptive. The hard rule — "claims are inviolable" — provides the actual boundary.
- Escalation: if a prank genuinely crosses a line, admin uses GriefLogger logs to assess, then arbitrates. The log lookup is a **soft-tool** (it provides data, not automatic rollback); the consequence is **soft**. Restoration of griefed blocks requires either the offender doing it manually or the admin making an executive judgement call and acting on it.

### Skirmishes

- PvP off by default. Sanctioned skirmishes are opt-in per event.
- Admin announces start time in chat; players opt in via a flag.
- After the event, all flags reset to default.
- Implementation can be: FTB Teams per-team war-mode toggle, or a small KubeJS event-triggered script.
- **Defer to the first need.**

### Mercenaries / bribery

- Player-driven economy. No admin rules.
- If it becomes a drama source, the hard-layer solution is "you must be in a faction to take cross-faction jobs," not "admin mediates every deal."

### Neutrals as spies / mediators

- Soft social role. No policy.

---

## 12. Implementation Order (When Ready)

In rough dependency order:

1. **Verify §10.1 and §10.2.** Without resolved data source and 14-day window mechanism, nothing downstream is well-defined.
2. **FTB Chunks config.** Setup-side; happens before launch.
3. **GriefLogger load.** Setup-side; happens before launch. Confirms what we can actually log.
4. **External-world-snapshot cron job.** Setup-side; happens before launch. Note: this is host-level, not modpack-level.
5. **KubeJS faction-tier reward script.** Reads `active_factioned`, computes tier, applies reward. Depends on §10.1.
6. **KubeJS `/vvh claim` and `/vvh reward` commands.** Depends on §10.1 (uses the same scoreboard) and §4 (uses the same tier table).
7. **World border + spawn island + Nether portal placement.** Setup-side.
8. **Stronghold-in-border verification.** Admin-side check before launch.
9. **FTB Quests auto-detected content** (kill X, craft Y, place Z). Tier-aware reward sets.
10. **FTB Quests creative content** with rubrics (§9). The `/vvh claim` script handles this layer.
11. **Chunk reset mechanism** for outside-border weekly reset. Verify the available tool (MCA Selector vs. mod vs. custom) before locking the design in.
12. **Soft-rule escalation paths** (skirmishes, prank disputes). Defer until first need.

A note on #10: the design accepts "some mechanism that resets outside-border chunks." The implementation is selectable based on what's available on NeoForge 1.21.1 at implementation time. If no suitable tool exists, this becomes a v2 item — the rest of the design works without it.

---

## 13. Cross-References

- Parent review: `~/Downloads/server-plan.txt` (the pitch)
- User context: `~/.claude/memory` (KISS philosophy + Poiesis + mc1.poiesis.link)
- Repo conventions: `agents.md` (packwiz CLI rules, file ignore patterns)
- Design-review skill: `minecraft-server-design-review` (patterns used)
