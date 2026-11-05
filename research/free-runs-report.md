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
| 1 | 2028-01-17 (Monday) | 2028-01-21 (Friday) | 5 | WWO season-pattern model (2028-01-16) | WWO season-pattern model (2028-01-22) |
| 2 | 2028-02-07 (Monday) | 2028-02-11 (Friday) | 5 | WWO season-pattern model (2028-02-06) | WWO season-pattern model (2028-02-12) |
| 3 | 2029-01-15 (Monday) | 2029-01-19 (Friday) | 5 | WWO season-pattern model (2029-01-14) | WWO season-pattern model (2029-01-20) |
| 4 | 2029-02-05 (Monday) | 2029-02-09 (Friday) | 5 | WWO season-pattern model (2029-02-04) | WWO season-pattern model (2029-02-10) |
| 5 | 2027-01-19 (Tuesday) | 2027-01-22 (Friday) | 4 | Utah at San Jose (2027-01-18) | Edmonton at San Jose (2027-01-23) |
| 6 | 2028-01-11 (Tuesday) | 2028-01-14 (Friday) | 4 | WWO season-pattern model (2028-01-10) | WWO season-pattern model (2028-01-15) |
| 7 | 2029-01-09 (Tuesday) | 2029-01-12 (Friday) | 4 | WWO season-pattern model (2029-01-08) | WWO season-pattern model (2029-01-13) |
| 8 | 2029-12-28 (Friday) | 2029-12-31 (Monday) | 4 | WWO season-pattern model (2029-12-27) | — (—) |
| 9 | 2027-02-03 (Wednesday) | 2027-02-05 (Friday) | 3 | WWO season-pattern model (2027-02-02) | WWO season-pattern model (2027-02-06) |
| 10 | 2028-01-05 (Wednesday) | 2028-01-07 (Friday) | 3 | WWO season-pattern model (2028-01-04) | WWO season-pattern model (2028-01-08) |
| 11 | 2028-01-26 (Wednesday) | 2028-01-28 (Friday) | 3 | WWO season-pattern model (2028-01-25) | WWO season-pattern model (2028-01-29) |
| 12 | 2028-02-02 (Wednesday) | 2028-02-04 (Friday) | 3 | WWO season-pattern model (2028-02-01) | WWO season-pattern model (2028-02-05) |

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

If 'free' is relaxed to 'not known to contain a game', the longest stretches are the annual late-December/January gap after the college national championship until the next published spring-training or NFL date, and the day ranges that sit between two officially dated events. Those are published explicitly on this page as CANDIDATES, never as verified free time.

## Known limitation (flagged, not hidden)

The published per-day scoreboards contain no row after 2027-09-26 for baseball, and the 2027 NFL, Westwood One, 2028 and 2029 season windows are unreleased. Long empty stretches late in 2027 and throughout 2028-2029 are therefore **absence of data**, not absence of games. They are never presented as verified free time.
