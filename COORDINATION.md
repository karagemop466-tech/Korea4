# Coordination board — FREE TIME VACATION

Session ID: `arena-72e6d3f7-korea4`
Branch: `arena/72e6d3f7-korea4`
Board created: 2026-11-02 (UTC)

## Branch constraint
Arena fixes this session to branch `arena/72e6d3f7-korea4` and forbids switching to, creating, or pushing other branches. The requested `session-<id>/<task>` branch/worktree convention and a separate integration branch therefore cannot be used here. This session acts as the sole worker and, once all tasks are complete, as the final integration session. All work, the PR, and the merge are performed from the fixed branch. Other sessions: do not start a task listed as `in progress` or `done` below; add a handoff note here instead.

## Task board

| Task | Status | Owner | File scope | Sources / verification | Irregularities / notes |
|---|---|---|---|---|---|
| C0 — Create board, claim scope, publish claim | in progress | `arena-72e6d3f7-korea4` | `COORDINATION.md` | n/a | Repo initially contained only `README.md`; no existing site/data to merge. Fixed-branch constraint noted above. |
| C1 — Audit supplied reference sites and repo history | unclaimed | | `research/reference-sites.md`, `data/` | pending | To be claimed before research begins. |
| C2 — Official schedule research (MLB/NFL/NCAAF/teams/Westwood One/radio) | unclaimed | | `research/sources.md`, `data/official_sources.json` | pending | Official source links required for every official value. |
| C3 — Generate verified schedule data, estimates, and coverage flags | unclaimed | | `data/*.json`, `scripts/*.py` | pending | Unverified values must be blank and flagged; estimates must be isolated from official values. |
| C4 — Free-time analysis and vacation-window analysis (2027–2029) | unclaimed | | `site/analysis/*`, `data/analysis/*.json` | pending | Must not claim future schedules are released unless verified. |
| C5 — Build dashboard: landing page, category pages, day scoreboard/calendar, tables, flagged review page | unclaimed | | `site/**`, `scripts/build_site.py`, `.github/workflows/pages.yml` | pending | Shared navigation/data/index are integrated by this session because no other session has claimed work. |
| C6 — Line-by-line verification, broken-link/build check, live deployment | unclaimed | | `COORDINATION.md`, `site/**`, `.github/workflows/pages.yml`, `scripts/verify.py` | pending | Run after C5; every table row must carry a source link to an official site or an explicit unverified flag with a blank official value. |
| C7 — PR, merge, GitHub Pages deployment confirmation, record result | unclaimed | | `COORDINATION.md` | pending | PR from fixed branch to `main`; merge only after a successful build/deploy check. |

## Change log / handoffs
- 2026-11-02 — Session `arena-72e6d3f7-korea4` created board and claimed C0. No other claims existed.
