# Free Time — Outer Sunset vacation planner

**Site:** https://karagemop466-tech.github.io/Korea4/

A source-linked, static GitHub Pages planner for Pacific-time sports schedules and possible free-time intervals in 2026–2029. It tracks all available MLB and NFL games; Stanford, Cal, Warriors and Earthquakes games; and Westwood One network events. The radio guide distinguishes published team flagships from confirmation that a specific game is actually carried on ordinary AM/FM at a particular address.

> **No vacation window is verified conflict-free.** Future schedules, precise game ends, local carriage, pre/postgame coverage and reception remain incomplete. “Potential gaps” and vacation leads are calculations from the records currently available, not booking recommendations.

The prior integration's claim that **February 15–18, 2027 is verified free** is superseded: the official Warriors schedule lists games on [February 15](https://www.nba.com/warriors/schedule) and February 17. The earlier sites and research are retained in the repository for audit; their published URLs redirect to the corrected planner rather than presenting old conclusions as fact.

## Use the site

- **Overview:** snapshot status, a selected day, and priority teams.
- **Calendar:** choose a Pacific date, browse MLB, NFL, Stanford/Cal, Warriors, Earthquakes or Westwood One, and open each official event source. Filters affect the list, not the all-category gap calculation.
- **Vacation windows:** examine unverified 7-, 14-, and 21-day leads. Years with too little published MLB coverage are withheld instead of filled with invented fixtures.
- **Radio guide:** source-linked team and network information; station assignments and reception are not guaranteed.
- **Flagged for Review:** stale/failed feeds, undated and time-TBD records, canceled or changed announcements, local radio uncertainty and other caveats.
- **Methodology:** sources, assumptions and the difference between game time and network airtime.

All civil times use `America/Los_Angeles`, including daylight-saving transitions. A game with no confirmed start marks all possible Pacific dates as uncertain. Intervals are merged, not split at halftime. Game ends use clearly labeled planning assumptions (MLB 158 minutes; NFL 192; college football 210; NBA 150; soccer 120), or a published Westwood One network slot. These are **not** verified game ends; overtime, delays and pre/postgame programming can extend coverage.

## Sources and coverage

| Feed | Official source | Important limit |
| --- | --- | --- |
| MLB | [MLB Stats API](https://statsapi.mlb.com/api/v1/schedule?sportId=1&startDate=2027-01-01&endDate=2027-12-31) | Future first pitches, postseason games and individual local radio carriage may be TBD. |
| NFL | [NFL schedule](https://www.nfl.com/schedules/) and [important dates](https://www.nfl.com/news/2026-27-national-football-league-important-dates) | Flexible weeks and playoff matchups may have no date or kickoff; published windows are reserved as uncertain. |
| College football | [Stanford](https://gostanford.com/sports/football/schedule), [Cal](https://calbears.com/sports/football/schedule/text) | Some future opponents are known but undated. Old announcements need rechecking. |
| Warriors | [NBA schedule](https://www.nba.com/warriors/schedule), [team radio network](https://www.nba.com/warriors/news/warriors-audacys-95-7-the-game-announce-multi-year-contract-extension-20251023) | The current NBA feed does not establish future seasons or every possible playoff game. |
| Earthquakes | [2026 team radio schedule](https://www.sjearthquakes.com/news/news-earthquakes-announce-radio-stations-for-2026-mls-season) | Dates, times, and station assignments may change; future seasons may not be published. |
| Westwood One | [Network schedule](https://www.westwoodonesports.com/nfl-schedule/) and [station finder](https://www.westwoodonesports.com/station-finder/) | Network airtime is not necessarily kickoff, the scheduled slot is not the actual end, and local affiliates can preempt games. |

The NFL [no longer stages an AFC–NFC Pro Bowl game beginning with the 2026 season](https://www.nfl.com/news/nfl-elevates-pro-bowl-selection-game-s-will-cease-being-contested); its 2027 celebration is not invented as a game. Current [Sharks audio information](https://www.nhl.com/sharks/team/broadcast) does not establish ordinary-FM carriage, so internet audio or historical affiliate lists are not counted as terrestrial broadcasts.

## Build and test

Requirements: Python 3.11+ (standard library only) and Node 20+; no install step.

```sh
python3 -m unittest discover -s tests -v
node tests/test_core.mjs
python3 scripts/build_site.py
python3 -m http.server 8000 --bind 0.0.0.0 --directory _site
```

Open `http://localhost:8000/`. The build copies only the current planner and data into `_site/`, and makes safe redirects for previous HTML URLs. Historical files under `docs/`, `data/`, and older site trees remain in the repository, but are not deployed as the current planner.

`python3 scripts/refresh.py` fetches the official feeds and updates `site/data/events.json`; it needs network access to the source hosts. On a fetch or parsing failure it keeps the last successful **committed snapshot** for that source and reports the failure instead of treating missing data as empty. Manually reviewed future announcements live in `site/data/announced-events.json` and include a review date. GitHub Actions rebuilds and publishes an updated Pages artifact daily, on pushes to `main`, and on manual dispatch. The source-health page reports stale snapshots as well as failed fetches.

## Project layout

- `index.html`, `site/planner/` — current dashboard, pages, styling and Pacific-time calculation engine.
- `site/data/events.json` — current committed source-linked snapshot.
- `site/data/announced-events.json` — individually sourced future announcements and uncertain date ranges.
- `scripts/refresh.py` — source ingestion and explicit failure retention.
- `scripts/build_site.py` — isolated Pages artifact and safe legacy redirects.
- `tests/` — parser, source-link, DST, interval and local-link checks.
- `COORDINATION.md` — shared session, conflict, source and integration history.

Not affiliated with the leagues, teams, stations or networks named here.
