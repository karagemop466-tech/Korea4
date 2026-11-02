# Coordination board

| Task | Status | Owner | File scope |
|---|---|---|---|
| Research, initial static dashboard and integration | needs review | arena/4c938fb2-korea4 | README.md, index.html, vacation.html, sources.html, review.html, assets/, tests/, COORDINATION.md |

The Arena-assigned branch is fixed; it cannot be renamed to the requested session pattern. No other claims existed when this work began. The site is an explicitly partial, provisional integration, not a complete schedule or a verified vacation recommendation. The unresolved coverage issues are published on `review.html` and do not constitute verified free time.

## Research and checks

- Reviewed 2026-11-02: [MLB 2027 schedule announcement](https://www.mlb.com/press-release/pirates-announce-2027-regular-season-schedule), [MLB events](https://www.mlb.com/events), and [MLB schedule feed example](https://statsapi.mlb.com/api/v1/schedule?sportId=1&startDate=2027-03-25&endDate=2027-03-26). The feed includes both actual starts and TBD placeholder timestamps; the latter are not displayed as real starts. Not every future schedule has been released.
- Compared the manually entered upcoming 2026–27 Westwood One NFL and NCAA football listings to [Westwood One NFL](https://www.westwoodonesports.com/nfl-schedule/) and [college football](https://www.westwoodonesports.com/ncaa-football/) on 2026-11-02. Each event links to its network event page. The schedule can change; affiliate carriage is not guaranteed per the [station finder](https://www.westwoodonesports.com/station-finder/).
- Compared the manually entered upcoming 49ers matchups and times with the [49ers schedule](https://www.49ers.com/schedule/). Compared dated college entries with [Cal](https://calbears.com/sports/football/schedule/2026), [Stanford](https://gostanford.com/sports/football/schedule), and [Stanford future dates](https://gostanford.com/news/2026/05/20/two-dates-added-to-notre-dame-rivalry); unconfirmed times remain TBD. [Warriors game notes](https://www.nba.com/gamenotes/warriors.pdf) and [NBA game page](https://www.nba.com/warriors/game/0022600193-magic-vs-warriors-san-francisco-ca-11-07-2026) support the two NBA examples.
- MLB end estimate uses the [2025 nine-inning average](https://www.mlb.com/news/mlb-average-game-time-under-three-hours-third-straight-year); other ends are explicitly planning assumptions, not verified game averages.
- `node tests/test.mjs` and `node tests/ui.mjs`: pass. Checked local page and asset links and HTTP 200 responses from a static server. Tests cover DST, midnight, unknown starts, overlap, empty feed, and failed feed. External pages were researched but not exhaustively rechecked by an automated link crawler; MLB browser/CORS availability varies by client and is flagged.
- Irregularities: not all NFL games or non-MLB radio schedules are ingested; future seasons and postseasons are incomplete; Westwood One carriage and exact 94122 reception are unverified; actual end and pre/postgame times are unknown. No 1-, 2-, or 3-week vacation window is certified. [Stanford's 2027 conference grid](https://gostanford.com/news/2026/09/16/acc-announces-2027-conference-opponents) supersedes the old model, and [TCU 2027 was canceled](https://gostanford.com/news/2026/04/17/tcu-series-update).

## Pull request / publication

- Preliminary integration PR: https://github.com/karagemop466-tech/Korea4/pull/6
- Merge result: **not merged**. The requested complete non-MLB schedule coverage and exhaustive external-link verification were not achieved, so the final-integration conditions have not been met. GitHub Pages has not been updated with this branch. The live preview serves the provisional site directly from this branch.
