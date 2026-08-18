# Critical Chapter 00 / 01 / 09 handoff

## Onboarding correction

- `READ THE THREE INVITATIONS` remains quest `7A11C0DE11000001` and now depends on `SIGN THE CHARTER`, `7A11C0DE10000008`.
- Invitation IDs remain stable: Crimson `11000002`, Lantern `11000003`, Free Company `11000004`.
- `THREE INVITATIONS` is `11000005`; its starter-kit successor is `11000006`.
- The three faction quests still depend on `11000001`. The trade choice depends on `11000005`.

## Moved early requisitions

The existing quest objects were moved, not cloned, from Chapter 09 into Chapter 01:

| Quest | New chapter coordinates | Dependency | Price | Cooldown | Output scope |
| --- | --- | --- | ---: | ---: | --- |
| `7A11C0DE19000002` Lighting | `(-5.5, 8.0)` | `11000005` | 1 Bevel | 604800 seconds | team |
| `7A11C0DE19000003` Transit | `(0.0, 8.0)` | `11000005` | 2 Bevels | 604800 seconds | team |
| `7A11C0DE19000005` Repair | `(5.5, 8.0)` | `11000005` | 1 Bevel | 604800 seconds | team |

They form a small optional row beneath the invitation/trade path. They do not issue Bevels and retain their existing reward IDs and item IDs.

## Chapter 09 boundary

Chapter 09 remains gated by `SEAL SEASON ONE`, `7A11C0DE18000009`. It now contains only post-season services: Festival (`19000004`), Hospitality (`19000006`), Public Works (`19000101`), Neutral Arcane (`19000102`), the weekly rumour fallback (`19000007`), and the Season Two pressure (`19000009`).

The economy wording is intentionally precise: progression is the primary one-time Bevel source; early and post-season requisitions spend Bevels for utility; ordinary Numismatics play may supplement the purse; the rumour archive returns exactly one team Bevel on a seven-day cooldown. No requisition output creates Bevels.

## Lore guardrails

Nessa Quill is a recurring neutral courier who annotates routes and carries practical requests. The Atlas remains the narrator of the season's wider record. Greybridge is referenced only as a past failed truce, never as a live-world prerequisite or required destination.

Localization updates are in `critical_ch00_01_09_lang.snbtfrag`; merge them into the root language compound without editing this fragment into the pack directly.

## Validation evidence

- All three owned chapters parse with `scripts/vvh_validate.py`'s `parse_snbt`.
- Chapter 01 contains nine quests after the three moved objects; Chapter 09 contains seven quests after their removal.
- Moved sink IDs, dependencies, coordinates, `604800` cooldowns, exact consumed Bevel prices, and `team_reward: true` outputs were inspected after parsing.
- No manifest generation, Packwiz refresh, KubeJS, reward-table, validator, or root localization changes are part of this handoff.
