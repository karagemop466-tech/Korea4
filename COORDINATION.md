# Coordination board — FREE TIME VACATION

Session ID: `arena-72e6d3f7-korea4`
Branch: `arena/72e6d3f7-korea4`
Board created: 2026-11-02 (UTC)

## Branch constraint
Arena fixes this session to branch `arena/72e6d3f7-korea4` and forbids switching to, creating, or pushing other branches. The requested `session-<id>/<task>` branch/worktree convention and a separate integration branch therefore cannot be used here. This session acts as the sole worker and, once all tasks are complete, as the final integration session. All work, the PR, and the merge are performed from the fixed branch. Other sessions: do not start a task listed as `in progress` or `done` below; add a handoff note here instead.

## Task board

| Task | Status | Owner | File scope | Sources / verification | Irregularities / notes |
|---|---|---|---|---|---|
| C0 — Create board, claim scope, publish claim | done | `arena-72e6d3f7-korea4` | `COORDINATION.md` | Board claim pushed as commit `99376cd`. | Repo initially contained only `README.md`; no existing site/data to merge. Fixed-branch constraint noted above. |
| C1 — Audit supplied reference sites and repo history | in progress | `arena-72e6d3f7-korea4` | `research/reference-sites.md`, `data/` | Initial audit: all three supplied GitHub Pages URLs return GitHub Pages 404; the matching GitHub repository URLs/API endpoints return 404. Search-engine cache still shows earlier repository/PR descriptions, which are not treated as authoritative. Repo history has only `a6e22c4` ("Initial commit") plus C0. | **IR-001:** supplied reference sites and repositories are currently unavailable; flagging for manual review. |
| C2 — Official schedule research (MLB/NFL/NCAAF/teams/Westwood One/radio) | in progress | `arena-72e6d3f7-korea4` | `research/sources.md`, `data/official_sources.json`, `scripts/probe_sources.py`, `.github/workflows/probe-sources.yml` | Confirmed reachable official leads: MLB Stats API 2026/2027 schedule and teams endpoints, MLB schedule/press-release pages, NFL 2026 schedule/important-dates pages, 49ers schedule, Stanford/Cal future-schedule articles, Westwood One NFL/NCAAF schedule, event detail, and station-finder pages, MLB Giants/A's radio pages. NFL 2027 official schedule pages show "SCHEDULE DATA UNAVAILABLE" as of 2026-11-02. | **IR-002:** NFL 2027 schedule appears under the 2026 season year on nfl.com; 2027 team/prime-time selectors have no schedule data. **IR-003:** Westwood One station finder warns affiliates may not carry every broadcast due to local blackouts/programming conflicts. |
| C3 — Generate verified schedule data, estimates, and coverage flags | unclaimed | | `data/*.json`, `scripts/*.py` | pending | Unverified values must be blank and flagged; estimates must be isolated from official values. |
| C4 — Free-time analysis and vacation-window analysis (2027–2029) | unclaimed | | `site/analysis/*`, `data/analysis/*.json` | pending | Must not claim future schedules are released unless verified. |
| C5 — Build dashboard: landing page, category pages, day scoreboard/calendar, tables, flagged review page | unclaimed | | `site/**`, `scripts/build_site.py`, `.github/workflows/pages.yml` | pending | Shared navigation/data/index are integrated by this session because no other session has claimed work. |
| C6 — Line-by-line verification, broken-link/build check, live deployment | unclaimed | | `COORDINATION.md`, `site/**`, `.github/workflows/pages.yml`, `scripts/verify.py` | pending | Run after C5; every table row must carry a source link to an official site or an explicit unverified flag with a blank official value. |
| C7 — PR, merge, GitHub Pages deployment confirmation, record result | unclaimed | | `COORDINATION.md` | pending | PR from fixed branch to `main`; merge only after a successful build/deploy check. |

## Change log / handoffs
- 2026-11-02 — Session `arena-72e6d3f7-korea4` created board and claimed C0. No other claims existed.
