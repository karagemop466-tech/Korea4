# NFL decision module — official-source verification record

Session: `arena/a7381587-korea4` · verified live on **2026-11-13 (UTC)** · branch `arena/a7381587-korea4`.

All observations below were made by fetching the official pages live on 2026-11-13. Nothing was inferred; values that could not be confirmed are left blank and flagged in `data/nfl/*.json` and on the site's Flagged for Review page.

## Official pages fetched live (2026-11-13)

| # | Official page | What was observed live |
|---|---|---|
| 1 | [NFL.com injury report](https://www.nfl.com/injuries/) | Title "Official Latest NFL Injury Report for Players — Week 10 of the 2026 Season". Week selector shows WEEK 1–WEEK 10 for 2026. Per-game tables (Player, Position, Injuries, Practice Status, Game Status) for the Week 10 slate: Thu Nov 12 WAS@NYG 8:15 PM ET; Sun Nov 15 NE@DET 9:30 AM ET, KC@ATL 1:00 PM ET, MIN@GB, JAX@TEN, BUF@NYJ, MIA@IND, CAR@NO… Matchups/dates agree with the repo's captured Week 10 schedule rows. |
| 2 | [49ers official roster on NFL.com](https://www.nfl.com/teams/san-francisco-49ers/roster) | "San Francisco 49ers 2026 Player Roster": per-player number, position, status (`ACT`), height/weight, experience, college. Header shows 49ers 7-1-0, 1st NFC West. No explicit depth-order column is present. |
| 3 | [NFL.com team injury page (guessed URL)](https://www.nfl.com/teams/san-francisco-49ers/injuries) | **404 "Flag on the Play"** — team-level injury pages do not exist at this URL pattern. → IR-023. |
| 4 | [NFL.com team depth chart (guessed URL)](https://www.nfl.com/teams/san-francisco-49ers/depth-chart) | **404 "Flag on the Play"** — team-level depth-chart pages do not exist at this URL pattern. → IR-023. |
| 5 | [NFL.com transactions](https://www.nfl.com/transactions/) | "2026 NFL League Transactions" with per-month Trades / Signings / Reserve List / Waivers / Terminations / Other. November 2026 trades listed: 11/10 Jessie Bates ATL→JAX; 11/10 Jordan Davis PHI→JAX; 11/10 Amani Hooker TEN→BUF; 11/10 Keenan Allen IND→SF; 11/10 Kirk Cousins LV→MIN; 11/10 Daiyan Henley LAC→DEN; 11/10 Josh Downs IND→KC; 11/10 Ryan Neuzil ATL→BAL; 11/10 Andrew Vorhees BAL→ATL; 11/09 Andre Cisco NYJ→DET; 11/09 Davon Godchaux NO→JAX; 11/06 Jacoby Brissett AZ→BAL. |
| 6 | [NFL.com team stats](https://www.nfl.com/stats/team-stats/) | "2026 Team Stats — Offense: Passing" for all 32 clubs (e.g., 49ers first row: 236 att / 163 comp / 69.1% / 8.4 Y/A / 1980 yds / 17 TD / 5 INT / 109.8 rating, as displayed 2026-11-13). Official stats hub is live and current through 2026 REG. |
| 7 | [Next Gen Stats](https://nextgenstats.nfl.com/) | Official NGS hub live with 2026 Week 10 content: route/carry/pass charts (e.g., Jayden Daniels Week 10 23/33, 249 yds, 3 TD, 2 INT pass chart), top plays (fastest ball carriers, fastest sacks), receiving separation leaders, and the 2026 advanced-metrics article link. |
| 8 | [NFL Football Operations](https://operations.nfl.com/) | Official hub live: "2026 NFL RULEBOOK", important-dates calendar, and headline links incl. "Week 11 Schedule Change" and "Big Data Bowl returns, powered by AWS". |
| 9 | [Week 11 Schedule Change (NFL.com news)](https://www.nfl.com/news/week-11-schedule-change) | Dated **Nov. 9, 2026**: JAX@NYG moves to 4:25 PM ET; PIT@PHI moves to 1:00 PM ET (both CBS, Sun Nov 22). Full final Week 11 slate (13 games) published — cross-checked against the repo's 13 Week 11 rows: 11 match exactly; **2 repo rows are stale** → IR-022. |
| 10 | [NFL approach to legalized sports betting & game integrity](https://media.nfl.com/lsb/) | Official league page: prohibited wager categories (inherently objectionable incl. player injuries; officiating-related; determinable by one person in one play; pre-determined), prediction markets treated as sports betting, key gambling-policy rules for players, integrity representatives, Genius Sports third-party monitoring. |
| 11 | [NFLPA Collective Bargaining Agreement](https://www.nflpa.com/cba) | Official NFLPA-hosted 2020 CBA (March 15, 2020 executed copy) — full text with table of contents (contracts, free agency, franchise/transition tenders, etc.). |
| 12 | [Historical NFL Injury Report Policy PDF (2017)](https://operations.nfl.com/media/2683/2017-nfl-injury-report-policy.pdf) | **404** — the historical policy PDF link is dead. Current official league statements verified at media.nfl.com/lsb instead. → IR-024. |
| 13 | [Big Data Bowl returns, powered by AWS](https://www.nfl.com/news/big-data-bowl-returns-powered-by-aws) | Official: ninth-annual league analytics competition on NGS player-tracking data; shared prize of **$100,000**; hosted on Kaggle; two entry tracks; prior winning concepts became official Next Gen Stats metrics (expected rushing yards, route recognition, coverage classification). |

## Cross-checks against the repo's captured data (snapshot 2026-11-02)

- Week 10 schedule rows (14 games, Nov 12–16) agree in matchups and dates with the live injury report and Next Gen Stats "2026 Week 10" game labels (WAS@NYG played Thu Nov 12 — NGS carries Week 10 highlights for it).
- Week 11 rows: 11 of 13 match the official Nov 9 final slate exactly (IND@HOU 8:15 PM ET, MIA@BUF 1:00, BAL@CAR 1:00, NO@CHI 1:00, TEN@DAL 1:00, TB@DET 1:00, ARI@KC 1:00, NYJ@LAC 4:05, LV@DEN 4:25, MIN@SF 8:20 Mexico City, CIN@WAS MNF 8:15). **JAX@NYG and PIT@PHI kickoff times changed after the snapshot** → IR-022 (stale rows published on flagged.html with the official correction link; captured data not hand-edited).
- Injury-report games (7 fully captured) all match repo Week 10 rows in matchup and date.

## Irregularities opened by this session

| ID | Irregularity | Official evidence |
|---|---|---|
| IR-022 | Two repo Week 11 rows stale after the official Nov 9, 2026 schedule change | [Week 11 Schedule Change](https://www.nfl.com/news/week-11-schedule-change) |
| IR-023 | NFL.com team-level injury/depth-chart URL patterns 404; depth ordering not published on NFL.com roster pages | [team injuries URL](https://www.nfl.com/teams/san-francisco-49ers/injuries) / [team depth-chart URL](https://www.nfl.com/teams/san-francisco-49ers/depth-chart) / [roster](https://www.nfl.com/teams/san-francisco-49ers/roster) |
| IR-024 | Historical injury-report policy PDF dead link | [dead PDF URL](https://operations.nfl.com/media/2683/2017-nfl-injury-report-policy.pdf); live policy statements at [media.nfl.com/lsb](https://media.nfl.com/lsb/) |
| IR-025 | Betting-market odds and correlation values are not published by any official NFL source; all correlation cells in this module are intentionally blank | [NFL integrity page](https://media.nfl.com/lsb/) (no odds publication; integrity monitoring via partners only) |
| IR-026 | Week 10 report oddity (transcribed verbatim, not interpreted): DET Kerby Joseph listed "Full Participation in Practice" yet Game Status "Out" — knee | [NFL.com injury report](https://www.nfl.com/injuries/) |

## Module design constraints (from official sources)

1. The NFL's own integrity policy flags specific wager categories as integrity-sensitive (player-injury markets, officiating-related, one-play-determinable, pre-determined outcomes) and treats prediction markets as sports betting ([media.nfl.com/lsb](https://media.nfl.com/lsb/)). This module's competition framework excludes modeling those categories.
2. The league's own precedent for a rewarded analytics leaderboard is the official Big Data Bowl ($100,000 shared prize, NGS data, Kaggle) ([official announcement](https://www.nfl.com/news/big-data-bowl-returns-powered-by-aws)).
3. No official source publishes betting odds, closing lines, or pair-correlation statistics — so the leaderboard's CLV/correlation gates cannot run on official data alone; a licensed market-data source is an owner decision (see Suggestions page, Q2/Q5).
