# COORDINATION.md — Shared Task Board (Free Time Vacation / Bay Area Sports Radio)

This is the shared task board for all agent sessions working on this repo.
Status values: `unclaimed`, `in progress`, `done`, `needs review`.
A status of `needs review` means the item is published on the site's "Flagged for Review" page and does not block anything.

## Session log

| Session ID | Branch | Notes |
|---|---|---|
| arena-97161ae7 | `arena/97161ae7-korea4` (fixed by Arena platform — this session cannot create a `session-<id>/<task>` branch, so all its work lands here) | Started 2026-11-02. Claim commit pushed before any other work. |

## Findings logged before claiming work (2026-11-02, arena-97161ae7)

- The repo contained only a stub `README.md` ("# Korea4"). No prior project files exist here.
- The three earlier project sites were checked and are **dead (GitHub Pages 404, repos not found)**:
  - https://buffedlizard55-lab.github.io/VacationSchedule/site/ → 404, repo not found
  - https://buffedlizard55-lab.github.io/ScheduleFreeTime/ → 404, repo not found
  - https://buffedlizard55-lab.github.io/RADIOSF/ → 404, repo not found
  No data could be recovered from them. This project is rebuilt from scratch from official sources.

## Task board

| # | Task | Status | Owner | Files in scope |
|---|---|---|---|---|
| 1 | COORDINATION.md + repo review + prior-site audit | done | arena-97161ae7 | COORDINATION.md |
| 2 | Research & verify season anchors (MLB/NFL/NCAAF/Westwood One, 2026–2029) from official sources | in progress | arena-97161ae7 | research-notes.md, docs/data.js |
| 3 | Bay Area radio map (KNBR, KGO 810, KTCT 1050, 95.7 The Game, A's/Giants/49ers/Stanford/Cal/Westwood One affiliates) | in progress | arena-97161ae7 | docs/radio.html, research-notes.md |
| 4 | Average game-duration research (MLB, NFL, NCAAF, others) with sources | in progress | arena-97161ae7 | research-notes.md, docs/data.js |
| 5 | Vacation-window analysis (1/2/3-week zero-conflict windows, 2027–2029) | in progress | arena-97161ae7 | docs/vacation.html, docs/index.html |
| 6 | Scoreboard/calendar site (day view, prev/next, free-window computation) | in progress | arena-97161ae7 | docs/*.html, docs/style.css, docs/app.js, docs/data.js |
| 7 | Executive summary | in progress | arena-97161ae7 | EXECUTIVE-SUMMARY.md, docs/index.html |
| 8 | Flagged-for-Review page | in progress | arena-97161ae7 | docs/flagged.html |
| 9 | Line-by-line verification pass + link check | unclaimed | — | (read-only) |
| 10 | Final integration: PR to main, merge, GitHub Pages deploy | unclaimed | — | docs/, repo settings |

## Scope / ownership rules
- Session arena-97161ae7 owns all files it creates on its branch this session. Other sessions: log change requests here instead of editing those files.
- Shared outputs (site index/nav, data tables) are changed only by the final integration session once the above tasks are done. (This session is running end-to-end as the sole active session and will also perform the integration step, per the user's autonomous instruction.)

## Verification log
(Filled in as work proceeds. Every VERIFIED row must link an official source. Anything not confirmable from an official source is labeled ESTIMATE or UNVERIFIED and listed on the Flagged for Review page.)

- 2026-11-02 — Prior repos/sites checked: all three return GitHub 404 / repository-not-found. See above.

## Irregularities flagged
(Also published on docs/flagged.html)

1. **Prior project sites/repo copies are gone** (VacationSchedule, ScheduleFreeTime, RADIOSF under buffedlizard55-lab). No data recoverable; rebuilt from official sources.
2. MLB 2028/2029 and NFL 2027–2029 schedules are **not yet officially released** — all such dates are ESTIMATES based on verified prior-year patterns and are labeled as such everywhere they appear. (Details and pattern sources on each page.)
