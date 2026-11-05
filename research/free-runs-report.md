# Free-run analysis — verification record

Generated from the snapshot dated 2026-11-03T23:27:13+00:00 (snapshot 'today' = 2026-11-02).
Recomputed by `python3 scripts/build_free_runs.py`; published as `data/official/free-runs.json`.

## Method

A day is FREE only when the snapshot contains no block of any class for it. A day with a published game, an officially anchored all-day event of unknown start time, or only the released-season model does not count as free. This is stricter than asking whether some minutes are free.

| Class | Meaning |
|---|---|
| `PUBLISHED_OFFICIAL` | At least one published official game row (official start + estimated duration, official network window, or official date with TBD start). |
| `UNVERIFIED_ANCHOR` | No published time, but an officially anchored event occupies the whole day (e.g. Super Bowl, CFP championship, dated college game). |
| `MODEL_ONLY` | Only the clearly-labelled 364-day model of unreleased seasons. Still treated as a candidate block. |
| `NO_BLOCK` | No block at all in the snapshot. |

## Counts

- `days_examined`: 1096
- `strict_free_runs`: 95
- `no_published_runs`: 15
- `published_runs`: 15
- `max_strict_free_run_days`: 5

## Per year

| Year | Days | Strict free days | Published days | Longest strict-free run | Longest stretch with no published game |
|---|---|---|---|---|---|
| 2027 | 365 | 54 | 235 | 4 | 96 |
| 2028 | 366 | 58 | 0 | 5 | 366 |
| 2029 | 365 | 59 | 0 | 5 | 365 |

## Longest strict-free runs (no published game of any monitored category)

| Rank | Start | End | Days | Block before (date) | Block after (date) |
|---|---|---|---|---|---|
| 1 | 2027-01-19 (Tuesday) | 2027-01-22 (Friday) | 4 | Utah at San Jose (2027-01-18) | Edmonton at San Jose (2027-01-23) |
| 2 | 2027-01-11 (Monday) | 2027-01-12 (Tuesday) | 2 | Week 18 Sunday Night Football - Teams TBA (2027-01-10) | San Jose at Edmonton (2027-01-13) |
| 3 | 2027-02-11 (Thursday) | 2027-02-12 (Friday) | 2 | Chicago at San Jose (2027-02-10) | Detroit at San Jose (2027-02-13) |
| 4 | 2027-07-14 (Wednesday) | 2027-07-15 (Thursday) | 2 | American League All-Stars at National League All-Stars (2027-07-13) | Tampa Bay Rays at Miami Marlins (2027-07-16) |
| 5 | 2027-01-05 (Tuesday) | 2027-01-05 (Tuesday) | 1 | Houston Texans at Green Bay Packers (2027-01-04) | Dallas at San Jose (2027-01-06) |
| 6 | 2027-01-07 (Thursday) | 2027-01-07 (Thursday) | 1 | Dallas at San Jose (2027-01-06) | Washington at San Jose (2027-01-08) |
| 7 | 2027-01-15 (Friday) | 2027-01-15 (Friday) | 1 | San Jose at Calgary (2027-01-14) | San Jose at Seattle (2027-01-16) |
| 8 | 2027-01-29 (Friday) | 2027-01-29 (Friday) | 1 | Nashville at San Jose (2027-01-28) | Chicago at San Jose (2027-01-30) |
| 9 | 2027-02-08 (Monday) | 2027-02-09 (Tuesday) | 2 | WWO season-pattern model (2027-02-07) | Chicago at San Jose (2027-02-10) |
| 10 | 2027-01-27 (Wednesday) | 2027-01-27 (Wednesday) | 1 | WWO season-pattern model (2027-01-26) | Nashville at San Jose (2027-01-28) |
| 11 | 2027-02-16 (Tuesday) | 2027-02-16 (Tuesday) | 1 | Winnipeg at San Jose (2027-02-15) | WWO season-pattern model (2027-02-17) |
| 12 | 2027-02-18 (Thursday) | 2027-02-18 (Thursday) | 1 | WWO season-pattern model (2027-02-17) | Atlanta Braves at Baltimore Orioles (2027-02-19) |
| 13 | 2028-01-17 (Monday) | 2028-01-21 (Friday) | 5 | WWO season-pattern model (2028-01-16) | WWO season-pattern model (2028-01-22) |
| 14 | 2028-02-07 (Monday) | 2028-02-11 (Friday) | 5 | WWO season-pattern model (2028-02-06) | WWO season-pattern model (2028-02-12) |

## Season density (why long summer gaps cannot exist)

| League | Season | First published | Last published | Calendar days | Days with a game | Share |
|---|---|---|---|---|---|---|
| MLB | 2026 | 2026-02-20 | 2026-10-28 | 251 | 242 | 96.4% |
| MLB | 2027 | 2027-02-19 | 2027-09-26 | 220 | 216 | 98.2% |

## Other Bay Area radio sports included as busy days

- Status: **CAPTURED FROM OFFICIAL LEAGUE FEEDS**
- Rows: {'NHL': 88, 'NBA': 0, 'total': 88}
- NHL coverage: 2026-09-20 → 2027-04-10
- NBA coverage: — → —

## Why the long empty stretches exist (official sources)

- **S-01 MLB 2027** — 2027 MLB regular season ends (last official Stats API game date) (2027-09-26 → 2027-09-26): VERIFIED — official schedule last game date. No published 2027 MLB rows after this date in the snapshot. Source: <https://statsapi.mlb.com/api/v1/schedule?sportId=1&season=2027>
- **S-02 MLB 2028** — 2028 MLB schedule not released (Stats API returns zero games) (2028-01-01 → 2028-12-31): UNVERIFIED — no official game rows exist to publish. Every 2028 day is empty of MLB rows because the schedule is unreleased, not because MLB is idle. Source: <https://statsapi.mlb.com/api/v1/schedule?sportId=1&season=2028>
- **S-03 MLB 2029** — 2029 MLB schedule not released (Stats API returns zero games) (2029-01-01 → 2029-12-31): UNVERIFIED — no official game rows exist to publish. Every 2029 day is empty of MLB rows because the schedule is unreleased, not because MLB is idle. Source: <https://statsapi.mlb.com/api/v1/schedule?sportId=1&season=2029>
- **S-04 NFL 2027** — Super Bowl LXI — last 2026-season NFL game (2027-02-14 → 2027-02-14): VERIFIED — official NFL important dates. 2026-season NFL ends here; the 2027 NFL schedule is not released. Source: <https://www.nfl.com/news/2026-27-national-football-league-important-dates>
- **S-05 NFL 2027** — 2027 NFL game-by-game schedule not released (2027-02-15 → 2027-12-31): UNVERIFIED — official selector shows no 2027 game data. NFL preseason/regular/postseason 2027 is unmodelled in the snapshot; late-2027 days are not evidence of free time. Source: <https://www.nfl.com/schedules/2027/by-team>
- **S-06 NFL 2028** — 2028 NFL schedule not released (2028-01-01 → 2028-12-31): UNVERIFIED — official selector shows no 2028 game data. No 2028 NFL rows exist to publish. Source: <https://www.nfl.com/schedules/2027/by-team>
- **S-07 NFL 2029** — 2029 NFL schedule not released (2029-01-01 → 2029-12-31): UNVERIFIED — official selector shows no 2029 game data. No 2029 NFL rows exist to publish. Source: <https://www.nfl.com/schedules/2027/by-team>
- **S-08 WWO 2027** — Westwood One official schedule published only through 2027-01-10 (2027-01-11 → 2027-12-31): UNVERIFIED — later 2027 network windows not published. WWO windows after 2027-01-10 are blank, not free. Source: <https://www.westwoodonesports.com/nfl-schedule/>
- **S-09 NCAAF 2027** — 2027 Stanford/Cal season dates not released (only nonconference dates and Notre Dame 11-27) (2027-01-01 → 2027-12-31): UNVERIFIED — opponents published, dates pending. Only 4 dated 2027 college rows exist; the other ~8 games per team are undated. Source: <https://calbears.com/news/2026/9/16/california-football-announces-2027-conference-opponents>
- **S-10 NCAAF 2028** — 2028 Stanford/Cal schedule not released (Notre Dame 2028-10-14 is the only dated game) (2028-01-01 → 2028-12-31): UNVERIFIED — single dated game only. No other 2028 college dates are published. Source: <https://gostanford.com/news/2026/05/20/two-dates-added-to-notre-dame-rivalry>
- **S-11 NCAAF 2029** — 2029 Stanford/Cal schedule not released (2029-01-01 → 2029-12-31): UNVERIFIED — no 2029 college dates published. No 2029 college dates exist to publish; CFP title date only. Source: <https://gostanford.com/sports/football/schedule>

## Conclusion

No 7-, 14- or 21-day stretch of consecutive days inside 2027-2029 is free under the strict reading. The longest runs with no published game are short early-winter gaps (see shortlist); every longer empty stretch is empty only because the 2027 NFL/WWO, 2028 and 2029 schedules have not been released, so it cannot be called free.

What the data supports: early winter (January to mid-February) repeatedly produces two-to-four day gaps between a published Sharks game and the next published NFL playoff weekend, because baseball is out of season and college football has ended. The longest such gap bracketed by two published official games is listed at the top of the ranked table. From late February to early October, at least one MLB game is published nearly every day, so no gap longer than a day or two can exist even in the model.

## Known limitation (flagged, not hidden)

The published per-day scoreboards contain no row after 2027-09-26 for baseball, and the 2027 NFL, Westwood One, 2028 and 2029 season windows are unreleased. Long empty stretches late in 2027 and throughout 2028-2029 are therefore **absence of data**, not absence of games. They are never presented as verified free time.
