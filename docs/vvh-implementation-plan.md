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
| Cross-faction territory | Hard | FTB Chunks per-team mode + server-wide 1/2 cap divided across 2 factions + outside-border unclaimable | Solo: 8 claim, 0 force-load. Per-faction claim: floor(in_border/4) = (1/2 server cap) / 2 factions, 16 force-load. See §7 |
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
| ≥ 7 | 3 | 1.75× (capped) |

mean_size 6 (= 6 active factioned players, 3/3 split) is the practical maximum for a 6-player cap. Any server beyond ~8 players is out of scope. The cap-row at mean ≥ 7 prevents unbounded growth; the design doesn't need finer tiers above 1.75×.

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

NeoForge 1.21.1 has no good automatic-revert mods. GriefLogger provides **logging only** — block / container / entity / item events, but no rollback command. Modded internal state (machine connections, channel allocation, schematic ownership, AE2 quantum rings, mob AI memory, tamed-mob inventories, Curios slots, Iron's Spells spellbooks, etc.) lives outside blocks, so even a working block-rollback would restore visible chunks while scrambling the world's causal graph. This is a structural property of modded worlds, not a mod-quality issue. **Inventory-snapshot tools are not a workaround** — coverage of "every inventory a player can hold things in" is unbounded and integration breakage is silent: a snapshot that misses the Curios slot shows the items in place because the live inventory screen reads live state, not the snapshot.

**The grief-handling layer:**

| Layer | Tool | Trust model | What it answers |
|---|---|---|---|
| Prevention | FTB Chunks per-team claims | Hard (mod-enforced) | "Can grief happen here?" → No, inside claims. |
| Forensics | GriefLogger | Hard, positive-only | "Who did this?" → Reliable when logged. Absence is not meaningful. |
| Restoration | Scheduled world snapshots (§ below) | Hard, atomic, file-level | "How do we undo severe grief?" → Restore from snapshot, accept partial progress loss. |
| Minor incidents | Friend-trust + manual | Soft | "What about a few broken blocks?" → Offender fixes it, or admin acts on authority. |

Outside-border grief is in renewable wilderness (§8) — rebuild cost is near-zero. In-claim grief is rare if claims are properly enforced. Disputes that reach the admin get GriefLogger evidence where available; admin judgment fills the rest. Restoration of griefed content is **manual** — the offender does it, or the admin does it.

### Restore Mechanism: Scheduled World Snapshots

A cron-style job (external to the MC server) snapshots the world directory every 6 hours. On severe grief, restore is from the most recent known-good snapshot — chosen by the admin, manually. Snapshots are atomic, file-level, version-coupled.

**Configuration defaults:**

| Parameter | Default | Note |
|---|---|---|
| Frequency | Every 6 hours | ~6 hours of progress loss per restore. |
| Retention | 24 hourly + 7 daily + 4 weekly | ~31 snapshots; 1 month of rolling history. |
| Stored path | `~/server/backups/` or external volume | Off-disk recommended. |
| Automation | Yes (cron) | Set-and-forget. |

**Why not git?** Worlds are tens of thousands of regions; git isn't designed for binary tree diff. Filesystem snapshot tools do this better.

**Why not grief logs?** Logs are forensic records, not world state. They don't restore the destroyed chunks; snapshot does.

**Implementation tools** (verify availability on NeoForge 1.21.1 at implementation time):

- **MCA Selector** — external, offline-mode, admin-triggered. Standard community tool.
- **A Bukkit-like API plugin** — NeoForge's API exposes chunk data but not "regenerate chunk" natively. A small plugin / mod could implement it.
- **A dedicated chunk-reset mod** — e.g., "Reset" or equivalent. Verify NeoForge 1.21.1 availability.

The design is tool-agnostic. Pick whichever is available; if none, this becomes a v2 item — the rest of the design works without it.

---

## 7. Faction & Claim Configuration

### Factions

- Always exactly 2 factions: **vampires** and **hunters**.
- Faction = FTB Teams team. Members granted by `/ftbteams join` or equivalent.
- **One party per player.** A player cannot be in two parties. A solo player is the leader (and sole member) of their solo party. A faction player is a member of a faction party. Each party owns a single FTB Chunks team.

### Claims

- FTB Chunks per-team mode: each team's claim is its territory.
- Inside claims: block break/place by non-members forbidden, PvP requires explicit opt-in, TNT off.
- Outside claims: fair game. Pranks, skirmishes, mercenary activity all happen here.
- **Outside the world border is unclaimable.** Configured at the FTB Chunks level (per-dimension / per-coordinate restriction). If players could claim there, the renewable wilderness property would erode over time as players permanently claimed what was meant to be wild.
- **Starter zone (admin-claimed at launch):** small area around spawn pre-claimed so new players are protected while learning the claim system.

### Claim budget

| Entity | Claim budget | Force-loading budget |
|---|---|---|
| Solo player | 8 chunks | 0 (cannot force-load) |
| Vampire faction | `floor(in_border_chunks / 4)` | 16 chunks (subset of claimed) |
| Hunter faction | `floor(in_border_chunks / 4)` | 16 chunks (subset of claimed) |

**Force-loading is a flag on a claimed chunk — never a separate budget.** A chunk must be claimed before the force-load flag can be set. Force-loadable ≤ claimable, always.

**Team-swap mechanics (design policy — verify §10.3):**

- **Solo → faction:** solo party dissolves; its 8 claimed chunks transfer ownership to the joined faction party. Player is now a faction member with 0 personal claims.
- **Faction → solo:** player leaves the faction (or last member leaves, faction party dissolves). The player is fresh solo — FTB Chunks auto-recreates a solo party with a fresh 8-chunk budget. *Previously-transferred claims do not return; they remain with the (now-empty or dissolved) faction party.*
- **Faction → faction:** no claim transport. The player joins the new faction with 0 personal claims. Their old contributions stay with the old faction.

### Allies mechanic

The Allies system is a technical capability of FTB Chunks + FTB Teams. The design endorses it for **solo → faction resource sharing**, and forbids it as a personal-territory mechanism inside factions.

**Mechanic:**

- **Directional access.** Adding Party B as ally of Party A grants Party B's members ally access into Party A's claimed territory. The reverse is not automatic. Both directions require both sides' actions.
- **Multiple allies fine.** A party can have as many allies as it wants.
- **Two granularities.** Allies can be per-player (target a specific individual) or per-party (target whole team).
- **Minimap location sync at any distance** between allies.
- **Recommended access level:** full in-territory access (break/place/containers/interact), no claim or admin operations.

**Endorsed use cases:**

- Solo player allied into vampires (or hunters, or both): gains access to faction territory / machines and minimap visibility. Fine.
- Faction-to-faction alliance: technically possible, no design rationale.

**Forbidden use case:**

- Personal territory inside a faction via Allies. A player joining a faction transfers all solo claims to the faction party, regardless of any Allies team. **One-party-per-player** is the mechanical reason this path is closed (a player in the vampires party cannot simultaneously lead a personal allied sub-party) — design policy reinforces it.

**Reward tier is unaffected by Allies.** A solo player allied to vampires is still classified as solo for §4's reward tier purposes — they get tier 0.

### §7.3 — Per-faction budget = 1/4 (derives from 1/2 server cap over 2 factions)

The always-2-factions invariant drives the per-faction budget:

```
max_chunks_per_main_faction = (floor(in_border_chunks / 2)) / 2
                           = floor(in_border_chunks / 4)
```

The 1/2 server-wide cap (sum of faction claim budgets) is split evenly across the two main factions. If a third faction were added, each faction's budget would become `floor((in_border / 2) / 3) = floor(in_border / 6)` — the formula generalises; the 1/4 is a special case for N=2.

**Sole exception: the 8-chunk solo budget.** This is a flat per-player constant, not derived from the 1/2 server cap. Why not part of the cap-divided-among-factions math: at our 1000+ chunk server scale, the 8-chunk solo budget is too small to make a meaningful difference — 63 solo players would be needed to fully allocate a 1000-chunk world, which would already require the design to change for many other reasons first. A dynamic allocation scheme (proportional caps, percent-of-leftover, etc.) is unjustified until solo population approaches 30 active players — at which point the design should be revisited as a whole, not patched at the chunk-budget layer.

If both factions hit 1/4 *and* the world is otherwise saturated, solos have no headroom. That's a soft pressure to faction up, consistent with the design's nudge.

**Scale check** (in_border_chunks = 1000):

- Server cap (factions): 500 chunks = 2 × 250.
- Each faction: 250 chunks.
- Solo: 8 chunks each. With 4–6 players, full saturation is rare.
- Border expansion to 2000 chunks: each faction gets 500, server cap 1000. Headroom still ample.

### §7.4 — Force-loading: party-dynamic by default, always-tick override

Force-loaded chunks always tick. Default FTB Chunks behavior is "always tick, even when no players are online" — measurable server load for a modded modpack at 16 force-loaded chunks per faction.

| Chunk type | Force-load behavior | Why |
|---|---|---|
| Base / spawn / hotel | Party-dynamic | Loads on demand; saves resources |
| Item farms | Party-dynamic (or off) | Items pile offline; farm jams on next load |
| Power generation | **Always-tick** | Continuous output expected; offline = no power |
| Processing facilities (long-running modded cycles) | **Always-tick** | Cycle continuity matters |
| Mob / XP farms | Party-dynamic | Mob ticking can wait |

Two settings per chunk: `force-loaded` (default false; tick regardless of online state) and `force-load party-tied` (default true; tick when any party member is online, release when all offline — the usual mode).

**Why item farms shouldn't always-tick:** items pile faster than players can collect offline. Chests fill, item entities spawn on the ground, hoppers jam. Party-dynamic loading avoids this — farm only runs while the team is online.

**Caveat:** whether FTB Chunks exposes three distinct modes (off / party-dynamic / always-tick) or only a binary (on / off) depends on the version. Verify at implementation (§10.3). Binary is acceptable; less elegant, still solves the resource-cost problem.

### Faction-flipping

**No cooldown.** With the §4 reward math, switching factions produces no mathematical advantage. Faction-flipping is soft-story content — a player hopping vampires → hunters → vampires is a beat, not an exploit. Friend-trust handles the social consequences; no code needed.

---

## 8. World Border & Spawn

### Spawn

- Central island, surrounded by ocean. World border at island edge.
- `worldborder set <radius>` once at world creation. Vanilla command, no mod dependency.

### Nether / End policy (launch-time)

**Policy (confirmed):**

- **Stronghold within world border, before launch.** Locate the stronghold; if the natural seed doesn't place one inside the world border, pre-generate or regenerate until one is. Avoids the "End fight impossible" failure mode.
- **Main End island is NOT reset.** Obsidian pillars, exit portal, dragon egg pedestal preserved indefinitely. End is a one-shot fight, then an endgame resource dimension (elytra, shulker shells).
- **End outer islands ARE reset weekly.** Once the dragon is dead, chorus islands, end cities, elytra shrines, and the outer ring become renewable endgame resources. Main island is the single exempt zone in End.
- **Nether reset:** none. Players build permanent infrastructure.
- **Nether portals:** build anywhere. Outside-border (Overworld-side) portals are destroyed by the weekly reset, since resetting the chunk destroys everything in it. Inside-border portals survive.

| Dimension | Behavior | Reset |
|---|---|---|
| Overworld (in-border) | Permanent base territory | No reset |
| Overworld (outside-border) | Renewable wilderness | Weekly |
| Nether | Permanent second base | No reset |
| End (main island) | One-shot fight + preserved hub | No reset |
| End (outer islands) | Renewable endgame resources | Weekly |

The Overworld's main island and the End's main island are the two preservation zones; everything else resets weekly.

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
- Outside-border chunks in the Overworld **cannot be claimed** (FTB Chunks is configured to deny claims in outside-border coordinates). This is the reason: claiming would permanently exempt portions of the renewable ring from weekly regen, defeating the property. See §7 for the claim-policy rationale.

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

- KubeJS server-side script: command registration (`/vvh claim <id>`, `/vvh reward <player> <id>`); block-count validation against rubric (scan claim chunk bounding box, count block types); reward tables keyed to tier index (4 tiers → 4 reward sets); per-player persistent tracking of completed milestones (prevents double-claim).
- In-game book (admin-editable) documenting rubrics. **The book is the user's documentation surface** — they update rubrics without restarting the server.

**Admin's recurring work:** write rubrics; define reward sets; run one `/vvh reward` per completion. The system computes tier automatically from §4's scoreboard, so no math on the admin's side.

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

§7's claim policy has to be enforced by the actual FTB Chunks version in the packwiz. Verify on a test world that:

- Per-team claim limits (8 solo, `floor(in_border / 4)` per faction) and force-load limits (0 solo, 16 faction) can be set per-team via config or NBT.
- Force-loadable chunks are a strict subset of claimed chunks (chunk must be claimed before the force-load flag applies).
- The three force-load modes (off / party-dynamic / always-tick) are exposed per chunk. If the deployed version is binary only (on / off), fall back to that — less elegant, still solves the resource-cost problem.
- Coordinate-based claim denial works (claims inside the world border are allowed; outside are denied). If not exposed, the chunk-reset mechanism (§8) must additionally force-unclaim outside-border claims on each weekly reset.
- Per-team chunk limits apply globally across dimensions (Overworld + Nether + End) — confirm this is what the version defaults to.

**One-party-per-player enforcement.** Critical design rule. Verify that the deployed FTB Teams fork does not allow multi-party membership. If it does, the reward-tier logic must classify players solely by their main-faction membership, ignoring allies.

**Team-swap mechanics are design policy.** Solo → faction join: solo party dissolves, claims transfer to the joined party. Faction → solo leave: solo auto-recreates with fresh 8-chunk budget, prior claims do not return. Verify the deployed FTB Chunks + FTB Teams behaves this way. If not, KubeJS orchestration enforces it.

### 4. FTB Quests reward tier structure

- **Defer to content-design phase.** Structure first, reward tables later.
- Open question: are rewards items (e.g., diamond gear), recipe unlocks (custom crafting table gates), or both?

### 5. GriefLogger support on NeoForge 1.21.1

Verify on test world:

- GriefLogger is published for NeoForge 1.21.1 (or usable via Forgified Fabric API on this modpack).
- It logs blocks, containers, entity-kills, item pickups (whatever the version covers is what we have for forensics).
- Log retention is configurable (30 days default).

If GriefLogger isn't available on this version, fall back to claims-only prevention plus manual-restoration dispute resolution. Acceptable on a friend server; the consequences are described in §6.

---

## 11. Soft-Rule Notes

The friend-trust layer governs the following. Admin arbitration is the escalation path; there is no in-game enforcement and the modpack does not encode these rules.

### Pranks

- Players can prank each other outside of claimed territory.
- "Harmless / reversible" is descriptive, not prescriptive. The hard rule — "claims are inviolable" — provides the actual boundary.
- Escalation: if a prank crosses a line, admin arbitrates. GriefLogger lookup supports the decision; the consequence is soft. Restoration is manual (offender or admin).

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
