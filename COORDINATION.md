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
| 2 | Research & verify season anchors (MLB/NFL/NCAAF/Westwood One, 2026–2029) from official sources | done | arena-97161ae7 | research-notes.md, docs/data.js |
| 3 | Bay Area radio map (KNBR, KGO 810, KTCT 1050, 95.7 The Game, A's/Giants/49ers/Stanford/Cal/Westwood One affiliates) | done | arena-97161ae7 | docs/radio.html, research-notes.md |
| 4 | Average game-duration research (MLB, NFL, NCAAF, others) with sources | done | arena-97161ae7 | research-notes.md, docs/data.js |
| 5 | Vacation-window analysis (1/2/3-week zero-conflict windows, 2027–2029) | done | arena-97161ae7 | docs/vacation.html, docs/index.html |
| 6 | Scoreboard/calendar site (day view, prev/next, free-window computation) | done | arena-97161ae7 | docs/*.html, docs/style.css, docs/app.js, docs/data.js |
| 7 | Executive summary | done | arena-97161ae7 | EXECUTIVE-SUMMARY.md, docs/index.html |
| 8 | Flagged-for-Review page | done | arena-97161ae7 | docs/flagged.html |
| 9 | Line-by-line verification pass + link check | done | arena-97161ae7 | (read-only) — Node engine tests (9 assertions, all days) + jsdom render test (8 pages) + internal link check: all passed 2026-11-02 |
| 10 | Final integration: PR to main, merge, GitHub Pages deploy | in progress | arena-97161ae7 (sole active session; also acting as integration session per user instruction) | docs/, repo settings |

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

## Verification log (continued)
- 2026-11-02 — Westwood One official NFL schedule page captured line-by-line (Nov 2026–Jan 2027, ~50 broadcasts, westwoodonesports.com/nfl-schedule). One truncated time (Dec 27 SNF) flagged F-7.
- 2026-11-02 — MLB anchors verified vs official releases: 2026 (Opening Night Mar 25 NYY@SF; ASG Jul 14 Philadelphia; season ended Sep 27; WS from Oct 23) and 2027 schedule released Jul 16, 2026 (ST Feb 19–Mar 23; OD Mar 25; ASG Jul 13 Wrigley; ends Sep 26). 2028 ASG host = Oracle Park (announced Aug 2026); 11-day Olympic break publicly "envisioned," not agreed → scenario toggle. 2028/29 calendars are ESTIMATES.
- 2026-11-02 — NFL: 2026 Week 18 ends Jan 10, 2027 (Westwood One); SB LXI Feb 14, 2027 SoFi (announced); SB LXII Atlanta (announced Oct 2024, date expected); SB LXIII site unverified. Pro Bowl Games 2027 date/carriage unverified → estimated, flagged F-5.
- 2026-11-02 — 49ers remaining 2026 cross-checked vs Westwood One + 3 schedule listings; one 1:05 vs 1:25 PM kickoff discrepancy flagged F-6. Stanford/Cal remaining 2026 from official athletics sites (calbears.com fetched; gostanford deep link 404 → F-14); late-Nov kickoffs TBD → modeled midday, flagged F-8. CFP 2026-27 dates verified (semis Jan 14/15; championship Jan 25, 2027 Las Vegas).
- 2026-11-02 — Radio: KNBR 680/104.5 = Giants flagship, 49ers co-flagship (+107.7 KSAN, 810 KSFO; Cumulus extension Apr 2026), SF affiliate of Westwood One Sports; A's KNEW 960 BA / KSTE 650 Sacramento (mlb.com official affiliate list); Stanford KTCT 1050; Cal 810 AM (official game notes); Warriors/Valkyries KGMZ 95.7; Sharks KUFX 98.5 (flagship long-standing; affiliate-list currency F-12); Earthquakes KSFO 810/KZSF 1370 (official, Feb 2026).
- 2026-11-02 — Durations: MLB 2:38 (MLB official, 2025); NFL ~3:03 kickoff-to-final-snap (nflverse timing) / 3:12 broadcast compilations, modeled 3:10; NCAAF 3:26 (NCAA stats compilation, 2025). Halftime: NFL 12 min / NCAA 20 min (never counted as free).
- 2026-11-02 — Engine test (tools/test-engine.cjs): 9/9 assertions PASS, all 1,156 model days compute. Computed headline: max strictly-free streak = 6 days (playoff corridors); Feb 15–18, 2027 = only both-sides-verified window; conditional 9-day Jul 12–20, 2028 under Olympic-break scenario. jsdom render test: 8/8 pages PASS, zero JS errors. Internal link check: no broken links.

## Irregularities flagged (continued)
- F-1…F-15 published on docs/flagged.html (dead prior sites; 2027 CBA risk; unreleased 2028/29 schedules; unconfirmed 2028 Olympic break; Pro Bowl/SB exact dates; 49ers kickoff discrepancy; one truncated Westwood One time; TBD Stanford/Cal kickoffs; A's 2027 opener unconfirmed; 2027 first-pitch/postseason times pending; Stanford/Cal 2027+ byes; Sharks affiliate-list currency; Westwood One 2027+ pattern windows; gostanford 404; college all-star bowls not modeled).
