# COORDINATION.md — Shared Task Board

> **Session ID:** arena/c697ef7b-korea4  
> **Branch:** `arena/c697ef7b-korea4` (all work on this branch)  
> **Created:** 2026-11-02  
> **Status:** Single-session integration — no parallel sessions detected. This session owns all tasks.

## Task Board

| # | Task | Status | Owner Session | Files / Scope | Notes |
|---|------|--------|---------------|---------------|-------|
| 01 | Repo audit & methodology | in progress | arena/c697ef7b-korea4 | `COORDINATION.md`, `README.md`, `docs/`, `data/`, `verify/` | Review existing repo, define verification protocol |
| 02 | Data collection — MLB 2026 verified | in progress | arena/c697ef7b-korea4 | `data/mlb-2026.json`, `site/pages/mlb.html` | Official MLB 2026 schedule released Aug 26 2025 |
| 03 | Data collection — MLB 2027-2029 estimates | unclaimed | arena/c697ef7b-korea4 | `data/mlb-2027.json`, `data/mlb-2028.json`, `data/mlb-2029.json` | Estimated per historical patterns — flagged as ESTIMATED |
| 04 | Data collection — NFL 2026 (49ers + all 32) | in progress | arena/c697ef7b-korea4 | `data/nfl-2026.json`, `site/pages/nfl.html` | 49ers schedule released May 2025 |
| 05 | Data collection — NFL 2027-2029 estimates | unclaimed | arena/c697ef7b-korea4 | `data/nfl-2027.json`, etc. | ESTIMATED — not yet released |
| 06 | Data collection — NCAAF Stanford & Cal 2026 | in progress | arena/c697ef7b-korea4 | `data/ncaaf-2026.json`, `site/pages/ncaaf.html` | Cal & Stanford schedules verified |
| 07 | Data collection — NCAAF 2027-2029 estimates | unclaimed | arena/c697ef7b-korea4 | `data/ncaaf-2027.json`, etc. | ESTIMATED |
| 08 | Data collection — Westwood One national NFL radio | in progress | arena/c697ef7b-korea4 | `data/westwood-one.json`, `site/pages/westwood-one.html` | Source: westwoodonesports.com |
| 09 | Radio guide — Bay Area AM/FM receivable in 94122 | unclaimed | arena/c697ef7b-korea4 | `data/radio-guide.json`, `site/pages/radio-guide.html` | KNBR 680/104.5, KNEW 960, KGO 810, etc. |
| 10 | Vacation window analysis 2027-2029 | unclaimed | arena/c697ef7b-korea4 | `data/vacation-windows.json`, `site/pages/vacation-windows.html` | 7/14/21-day windows computed from busy calendars |
| 11 | Site creation — landing + navigation + CSS/JS | unclaimed | arena/c697ef7b-korea4 | `index.html`, `assets/`, `site/` | Dashboard UI, scoreboard calendar |
| 12 | Site creation — executive summary & methodology | unclaimed | arena/c697ef7b-korea4 | `site/pages/executive-summary.html`, `methodology.html` | |
| 13 | Site creation — calendar / free-time scoreboard | unclaimed | arena/c697ef7b-korea4 | `site/pages/calendar.html`, `assets/js/calendar.js` | Interactive day/week view, PST |
| 14 | Verification — line-by-line source audit | unclaimed | arena/c697ef7b-korea4 | `site/pages/sources.html`, `site/pages/flagged.html`, `VERIFY.md` | Every row needs source link |
| 15 | Final integration — build check & deploy | unclaimed | arena/c697ef7b-korea4 | `index.html`, all pages | Run build, check links, publish to GH Pages |

## Log

| Timestamp (UTC) | Session | Action |
|-----------------|---------|--------|
| 2026-11-02 17:17 | arena/c697ef7b-korea4 | Created COORDINATION.md, claimed all tasks as single integration session (no competing sessions found). |
| | | Branch is `arena/c697ef7b-korea4`; will commit frequently and push to origin. |

## Claim Protocol

- To claim a task, write your session ID in Owner Session, set Status to `in progress`, commit & push immediately.
- Never edit files outside your claimed scope — log a request here instead.
- Mark `done` only after verification against official source with link.
- `needs review` = published on Flagged for Review page, does not block integration.
- Integration session merges branches, re-verifies combined data, confirms site builds, then opens PR to main and merges.

## Integration Notes (for final session)

- Shared outputs (`index.html`, `site/`, `data/`, navigation) are changed only by final integration.
- Must confirm `gh pages` deploy succeeds before merging.
- Record PR link + merge result here.

---
*This file is the shared task board for parallel sessions. Keep scopes non-overlapping.*
