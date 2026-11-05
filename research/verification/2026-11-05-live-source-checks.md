# Live official source re-checks — 2026-11-05

These pages were re-fetched on 2026-11-05 (America/Los_Angeles) and compared line by
line with the published rows in `data/official/events.json`. The build sandbox has no
outbound access to league sites, so these checks are manual and are recorded here as
evidence; checks A1–A7 in `audit-log.json` are automated and recompute every published
value from the captured raw responses of 2026-11-02.

## 1. San Francisco 49ers — https://www.49ers.com/schedule/

Fetched 2026-11-05. Published rows match:

| Week | Official page | Published row |
|---|---|---|
| 9 | Sun 11/08 · 1:25 PM PST · VS Las Vegas Raiders · FOX · KSAN 107.7 FM / KNBR 104.5 FM / 680 AM · Levi's® Stadium | `2026-11-08 1:25 PM PST — Las Vegas Raiders at San Francisco 49ers` |
| 10 | Sun 11/15 · 1:25 PM PST · AT Dallas Cowboys · FOX · AT&T Stadium | `2026-11-15 1:25 PM PST — San Francisco 49ers at Dallas Cowboys` |
| 11 | Sun 11/22 · 5:20 PM PST · VS Minnesota Vikings · NBC · Estadio Banorte | `2026-11-22 5:20 PM PST — Minnesota Vikings at San Francisco 49ers` |
| 12 | Sun 11/29 · 1:25 PM PST · VS Seattle Seahawks · FOX · Levi's® Stadium | `2026-11-29 1:25 PM PST — Seattle Seahawks at San Francisco 49ers` |
| 13 | Sun 12/06 · 10:00 AM PST · AT New York Giants · FOX · MetLife Stadium | `2026-12-06 10:00 AM PST — San Francisco 49ers at New York Giants` |
| 14 | Sun 12/13 · 1:25 PM PST · VS Los Angeles Rams · FOX · Levi's® Stadium | `2026-12-13 1:25 PM PST — Los Angeles Rams at San Francisco 49ers` |
| 15 | Thu 12/17 · 5:15 PM PST · AT Los Angeles Chargers · Prime Video · SoFi Stadium | `2026-12-17 5:15 PM PST — San Francisco 49ers at Los Angeles Chargers` |
| 16 | Sun 12/27 · 1:25 PM PST · AT Kansas City Chiefs · CBS · Arrowhead Stadium | `2026-12-27 1:25 PM PST — San Francisco 49ers at Kansas City Chiefs` |
| 17 | Sun 01/03 · 5:20 PM PST · VS Philadelphia Eagles · NBC · Levi's® Stadium | `2027-01-03 5:20 PM PST — Philadelphia Eagles at San Francisco 49ers` |
| 18 | TBD · AT Arizona Cardinals · State Farm Stadium | official TBD row, blank date/time |

Earlier weeks (1–7) are marked FINAL on the official page and match the published
kickoffs; Week 8 is the bye. The official page also confirms the radio line
"KSAN 107.7 FM / KNBR 104.5 FM / 680 AM" used on every 49ers row.

Defect found and corrected: the schedule card's first button is a ticket-reseller
("FAN EXPERIENCE PACKAGES" → vividseats.com). Nine rows had been published with that
reseller URL while the row label claimed 49ers.com. The collector now accepts only
official league/team/network domains and prefers the 49ers.com game-center link; the
reseller URL is rejected (IR-018).

## 2. Westwood One Sports NFL schedule — https://www.westwoodonesports.com/nfl-schedule/

Fetched 2026-11-05. All 18 upcoming broadcasts listed on the live page match published
rows exactly (date and Pacific start time):

| Live event | Official time (ET) | Published row (PT) |
|---|---|---|
| 548561 Jacksonville Jaguars at Baltimore Ravens (TNF) | Nov 5, 7:30 PM | 2026-11-05 4:30 PM PST |
| 548500 Tampa Bay Buccaneers at Chicago Bears (SNF) | Nov 8, 7:30 PM | 2026-11-08 4:30 PM PST |
| 548562 Washington Commanders at New York Giants (TNF) | Nov 12, 7:30 PM | 2026-11-12 4:30 PM PST |
| 548501 Pittsburgh Steelers at Cincinnati Bengals (SNF) | Nov 15, 7:30 PM | 2026-11-15 4:30 PM PST |
| 548564 Indianapolis Colts at Houston Texans (TNF) | Nov 19, 7:30 PM | 2026-11-19 4:30 PM PST |
| 548543 Cincinnati Bengals at Washington Commanders (MNF) | Nov 23, 7:00 PM | 2026-11-23 4:00 PM PST |
| 548512 Chicago Bears at Detroit Lions (Thanksgiving) | Nov 26, 12:30 PM | 2026-11-26 9:30 AM PST |
| 548514 Kansas City Chiefs at Buffalo Bills (Thanksgiving) | Nov 26, 8:00 PM | 2026-11-26 5:00 PM PST |
| 548502 New England Patriots at Los Angeles Chargers (SNF) | Nov 29, 7:30 PM | 2026-11-29 4:30 PM PST |
| 548566 Kansas City Chiefs at Los Angeles Rams (TNF) | Dec 3, 7:30 PM | 2026-12-03 4:30 PM PST |
| 548545 Dallas Cowboys at Seattle Seahawks (MNF) | Dec 7, 7:00 PM | 2026-12-07 4:00 PM PST |
| 548505 Buffalo Bills at Green Bay Packers (SNF) | Dec 13, 7:30 PM | 2026-12-13 4:30 PM PST |
| 548568 San Francisco 49ers at Los Angeles Chargers (TNF) | Dec 17, 7:30 PM | 2026-12-17 4:30 PM PST |
| 548518 Chicago Bears at Buffalo Bills (Sat doubleheader) | Dec 19, 8:00 PM | 2026-12-19 5:00 PM PST |
| 548548 New England Patriots at Kansas City Chiefs (MNF) | Dec 21, 7:00 PM | 2026-12-21 4:00 PM PST |
| 548528 Green Bay Packers at Chicago Bears (Christmas) | Dec 25, 12:30 PM | 2026-12-25 9:30 AM PST |
| 548534 Los Angeles Rams at Seattle Seahawks (Christmas) | Dec 25, 8:00 PM | 2026-12-25 5:00 PM PST |
| 548520 Week 16 Saturday Doubleheader TBA | Dec 26, 8:00 PM | 2026-12-26 5:00 PM PST |

## 3. California Golden Bears — https://calbears.com/sports/football/schedule/2026

Fetched 2026-11-05. The official page lists the full 2026 season. Five games had been
published as TBA because the parser required an `HH:MM` kickoff (the official page
prints "9 AM" for the two road day games) and because upcoming game cards omit the
header date node:

| Official page | Before this session | Now published |
|---|---|---|
| Oct 24 at SMU, 9 AM (Dallas, Texas) | TBA — UNVERIFIED, no date | `2026-10-24 9:00 AM PDT — Cal at SMU` |
| Oct 31 at NC State, 9 AM (Raleigh, NC) | TBA — UNVERIFIED, no date | `2026-10-31 9:00 AM PDT — Cal at NC State University` |
| Nov 14 at Virginia, 12:30 PM (Charlottesville, Va.) | TBA — UNVERIFIED, no date | `2026-11-14 12:30 PM PST — Cal at Virginia` |
| Nov 21 vs Stanford (Berkeley, Calif.), kickoff TBA | TBA — UNVERIFIED, no date | `2026-11-21` date row, blank time, whole day blocked |
| Nov 28 vs Pittsburgh, kickoff TBA | TBA — UNVERIFIED, no date | `2026-11-28` date row, blank time, whole day blocked |

The parser now merges the game cards with the official scoreboard carousel, accepts
"9 AM"-style kickoffs and publishes the official date for every game (IR-020).

## 4. Stanford Cardinal — https://gostanford.com/sports/football/schedule

Fetched 2026-11-05.

| Official page | Before this session | Now published |
|---|---|---|
| Sat Nov 14 at Virginia Tech — "4 OR 4:30 P.M." (flexible) | 4:00 PM PST, VERIFIED, no mention of the flex window | 4:00 PM PST, status "VERIFIED — OFFICIAL FLEX WINDOW", note records the official 4:00 or 4:30 PM PT window |
| Sat Nov 21 at California — TBA (129th Big Game) | 12:00 PM PST, VERIFIED (copied from the page's placeholder timestamp) | date row, blank time, whole day blocked |
| Sat Nov 28 vs SMU — TBA | 12:00 PM PST, VERIFIED (placeholder) | date row, blank time, whole day blocked |

Publishing a placeholder as a verified kickoff could have shown a free morning that is
actually a game day, so both rows are now blank and block the day (IR-021).

## Not re-verified this session

- 2028/2029 MLB, 2027–2029 NFL and post-Jan-2027 Westwood One schedules remain
  officially unreleased. They are blank in the tables and modelled separately as
  ESTIMATED, never as released schedules (IR-002, IR-007, IR-010, IR-011, IR-015).
- Warriors, Sharks and Valkyries radio windows (IR-014) and 94122 reception for any
  station remain unverified.
