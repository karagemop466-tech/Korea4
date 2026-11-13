# NFL Lab — line-by-line audit, 2026-11-13 (UTC)

Branch: `arena/0d4aaf2a-korea4`, started from `main` @ `a8fa5e3` and rebased onto `main` @ `742575d` (PR #45)
after a parallel session merged its own NFL module. The two were reconciled, not duplicated.
Session: `arena/0d4aaf2a-korea4`. Claim recorded in `COORDINATION.md` before any edit.

## Method, and what it can and cannot prove

Two different levels of checking were used, and they are labelled separately everywhere:

| Level | What it means | How it was done |
|---|---|---|
| **Re-read against the source** | The value was read on the official page and compared with what the repository or page says | Manual read of the live page via the session's page-fetch tool on 2026-11-13 |
| **Structural only** | The row has an official-host link and the page builds | `scripts/verify.py` + `scripts/verify_nfl_lab.py` |

Sandbox limitation, stated plainly: this session's shell has outbound access to `github.com` only. Official league and
club pages (`nfl.com`, `49ers.com`, `media.nfl.com`) are reachable through the page-fetch tool but **not** by `curl`,
so the repository's own `scripts/fetch_official.py` could not be re-run here. Every official value added by this
session was read through the page-fetch tool on 2026-11-13 and is dated as such on the site.

## A. Schedule rows — 2026 season

Re-read: **Week 10, all 14 games** ([NFL.com Week 10](https://www.nfl.com/schedules/2026/by-week/week-10)).

| Row in `data/official/events.json` | Value in repo | Value on NFL.com | Result |
|---|---|---|---|
| Commanders at Giants, 2026-11-12 | 5:15 PM PST | Thu Nov 12, 8:15 PM ET — final WAS 24, NYG 21 | match |
| Patriots at Lions, 2026-11-15 | 6:30 AM PST | Sun Nov 15, 9:30 AM ET (Munich) | match |
| Chiefs at Falcons | 10:00 AM PST | 1:00 PM ET | match |
| Texans at Browns | 10:00 AM PST | 1:00 PM ET | match |
| Vikings at Packers | 10:00 AM PST | 1:00 PM ET | match |
| Dolphins at Colts | 10:00 AM PST | 1:00 PM ET | match |
| Panthers at Saints | 10:00 AM PST | 1:00 PM ET | match |
| Bills at Jets | 10:00 AM PST | 1:00 PM ET | match |
| Jaguars at Titans | 10:00 AM PST | 1:00 PM ET | match |
| Rams at Cardinals | 1:05 PM PST | 4:05 PM ET | match |
| Seahawks at Raiders | 1:05 PM PST | 4:05 PM ET | match |
| 49ers at Cowboys | 1:25 PM PST | 4:25 PM ET; 49ers.com also lists 1:25 PM PST | match |
| Steelers at Bengals | 5:20 PM PST | 8:20 PM ET | match |
| Chargers at Ravens | 5:15 PM PST | Mon Nov 16, 8:15 PM ET | match |

Result: **14 of 14 match** on matchup, kickoff and home/away order.

The other 315 NFL rows were **not** re-read this session. They were checked structurally (official host, no duplicate
game, no same-team matchup). Any claim that all 329 rows were verified line by line would be false.

## B. Injury rows — 27 transcribed from the official Week-10 report

Source: [NFL.com injuries](https://www.nfl.com/injuries/) (Week 10, 2026 season), read 2026-11-13 UTC.

| Check | Result |
|---|---|
| 49ers listed | 12 players: 6 Did Not Participate, 4 Limited, 2 Full — **all game-status cells blank** |
| Cowboys listed | 18 players: 9 Did Not Participate, 3 Limited, 6 Full — all game-status cells blank |
| Clubs with a visible table at capture | 26 of 28 (New Orleans and Cincinnati lists were truncated in the captured text) |
| Clubs shown with no injuries | Chargers, Ravens ("No Injuries Reported", Monday game) |
| Explicit game designations on the page | 3 (Lucas Patrick OUT/concussion, Colson Yankoff OUT/knee, Malik Harrison QUESTIONABLE/groin) |
| Clubs covered by this section | 26 of 32 — **the other six were not captured and are not claimed** |

Every transcribed row keeps the league page as its source link. No injury row was inferred from a player's absence in
a depth chart, and no designation was invented where the field was blank.

## C. Depth chart — 49ers only

Source: [49ers.com depth chart](https://www.49ers.com/team/depth-chart), the page's own "Updated as of 11/10/26".

| Check | Result |
|---|---|
| Slots transcribed | 29 (11 offense, 12 defense, 6 special teams) |
| Slots with no backup named | 9 — RG, RT, FB, LCB, NB, P, K, H, LS |
| Injured starter with no documented backup | 1 — Renardo Green (LCB), listed as Did Not Participate |
| Charts captured for other clubs | 0 |

The 9-slot gap is a fact about the chart, not about the roster. The site says so, and the replacement quality is left
UNVERIFIED rather than described.

## D. Repository findings and the checks behind them

| ID | Check performed | Result |
|---|---|---|
| A-01 | Read `meta.json` `system_today`, compared with the current Pacific date | was 2026-11-05 on 2026-11-13 — **fixed** by re-running the collector |
| A-02 | Compared `source_snapshot_utc` with `generated_utc` | 11 days (259 hours) stale — disclosed on every page |
| A-03 | Re-read Week 10 against NFL.com | 14/14 match |
| A-04 | Counted populated fields across 329 NFL rows | venue on 3 rows, start timestamp on 251 |
| A-05 | Enumerated the event schema and searched for score/result fields | none exist |
| A-06 | Searched `data/`, `research/`, `scripts/` for odds/spread/total/moneyline | none exist |
| A-07 | Read all four workflow files | `fetch-official.yml` triggers on branch `arena/72e6d3f7-korea4` only, no `schedule:` |
| A-08 | Duplicate-id scan over 6,591 rows | 30 duplicates, all MLB original/rescheduled pairs |
| A-09 | Read `scripts/verify.py` | structural checks only; no source fetch |
| A-10 | Scanned all 10,062 primary rows for the build's fallback URL | 5 hits, all the 95.7 The Game catalogue rows themselves |
| A-11 | Read `data/nfl-2026.json` | `"verified": true` with three non-official sources; Week 1 home/away contradicts NFL.com |
| A-12 | Listed `data/` and `data/official/` contents | no injury, depth or player-stat data before this session |
| A-13 | Measured page sizes | `mlb.html` 4.9 MB, `review.html` 2.3 MB |
| A-14 | Read the other 2026-11-13 sessions' branch diffs and claims | five concurrent NFL sessions, two with committed data/code |

## E. Gates run after the rebuild

| Command | Result |
|---|---|
| `python3 scripts/verify.py` | PASS — 0 errors, 0 warnings, 10,062 primary rows, 992 internal links, 0 broken, JS syntax OK |
| `python3 scripts/verify_nfl_lab.py` | PASS — 0 errors, 0 warnings (252 rows: 104 official-sourced, 15 repository-sourced, 111 declared design rows, 22 computed rows with provenance links) |
| `node --check js/app.js` | PASS |
| `node tests/test_dashboard.mjs` | PASS |
| `npm test` | PASS |
| `python -m unittest discover -s tests -p test_dashboard_generator.py` | 3 tests OK |

`tests/test_build.py` needs a Jekyll `_site/` tree that this sandbox does not produce (no Ruby/Jekyll). Its three
failures are pre-existing on the base commit and are not caused by this branch; the assertions that concern tracked
HTML were updated to recognise the eleven new published pages.

## F. Irregularities published for review

FL-01 … FL-06 on `nfl-decision-flags.html`. None blocks the build or the deploy.

## G. What was deliberately not done

- No value was estimated, extrapolated or filled from memory.
- No injury designation was assigned to a player whose game-status field was blank.
- No backup was named for a slot the official chart leaves empty.
- No correlation value, effect size, probability or line was produced.
- No existing page body, event row or `data/official/*` value was altered; this session's only change to shared data
  was re-running the existing collector so the dashboard's "today" is current.
