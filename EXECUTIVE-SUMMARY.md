# Executive summary — FREE TIME VACATION

Dashboard rebuilt 2026-11-13T13:09:05+00:00; official source snapshots last refreshed 2026-11-02T17:41:45+00:00. Uses 748 captured official-source records.

## Scope
- All 30 MLB clubs; Giants and Athletics FOCUS; all MLB games HIGH.
- All released 2026 NFL preseason/regular/postseason/special rows; 49ers FOCUS.
- Stanford and Cal 2026 NCAAF games and official 2027–2029 future anchors.
- All captured official Westwood One Sports event windows across nine categories.
- Other confirmed Bay Area AM/FM radio sports, including the full official 2026 Earthquakes radio schedule.
- Estimated Pacific-time gaps, not verified free time, for each day from 2026-11-01 through 2029-12-31.

## NFL decision module (added 2026-11-13, session `arena/a7381587-korea4`)

**Purpose.** Collect, organize and analyze NFL information to support originating the site's own betting lines; run a rewarded, gated strategy leaderboard (singles, parlays, player-prop combos); and track injuries/depth so lineup deficiencies (2nd/3rd/4th-string replacements) are known before lines are made. All of it is a research framework: no verified win probabilities, no recommendations.

**Important details.**
- 13 official sources fetched live on 2026-11-13 and recorded with URLs in `research/nfl-module/README.md` and `data/nfl/sources.json`: [NFL.com injury report](https://www.nfl.com/injuries/) (Week 10 live), [rosters](https://www.nfl.com/teams/san-francisco-49ers/roster), [transactions](https://www.nfl.com/transactions/) (12 trades Nov 6–10), [team stats](https://www.nfl.com/stats/team-stats/), [Next Gen Stats](https://nextgenstats.nfl.com/) (Week 10 charts), [Football Operations](https://operations.nfl.com/), [Week 11 schedule change](https://www.nfl.com/news/week-11-schedule-change), [sports-betting integrity policy](https://media.nfl.com/lsb/), [NFLPA CBA](https://www.nflpa.com/cba), [Big Data Bowl](https://www.nfl.com/news/big-data-bowl-returns-powered-by-aws).
- **Line origination** (`nfl-lines.html`): 8-step pipeline L-01…L-08; publication is gated on the validation gates; the Week 11 official change vs the captured snapshot is shown row by row.
- **Strategy leaderboard** (`nfl-strategies.html`): competition design B-01…B-10 (Big Data Bowl as official precedent), signal candidates G-01…G-08 (none backtested), gates V-01…V-08 (none run), correlation research C-01…C-07 (all values intentionally blank — no official source publishes correlations, IR-025).
- **Injuries/depth** (`nfl-injuries.html`): Week 10 snapshot for 15 clubs transcribed from the official report on 2026-11-13 (e.g., IND both DTs DNP; MIN two QBs listed; NE 12 limited); deficiency framework D-01…D-04 with verbatim observations E-01…E-06.
- **Suggestions** (`nfl-suggestions.html`): dedicated review section — 10 improvement suggestions S-01…S-10, 10 open questions Q-01…Q-10 (what we have / what is missing / how to discover), a decision-readiness checklist, and discovery suggestions. Nothing is implemented until a decision is recorded.
- **Irregularities opened:** IR-022 (two Week 11 rows stale after the official Nov 9 change — correction linked, captured values not hand-edited), IR-023 (no official team depth-chart/injury URLs; no published depth order), IR-024 (dead 2017 policy PDF), IR-025 (no official odds/correlation source; values blank), IR-026 (one verbatim report oddity: DET K. Joseph Full practice but Game Status Out).
- **Integrity constraints honored:** the module excludes the wager categories the NFL's official policy flags (player-injury markets, officiating-related, one-play-determinable, pre-determined outcomes) and treats prediction-market contracts as excluded ([official policy page](https://media.nfl.com/lsb/)).

## Verification rules
1. Official/league/team/network sources only for VERIFIED values.
2. Unconfirmable values are blank and flagged UNVERIFIED with an official source link.
3. Official TBD start times are blank; planning estimates are separate and explicitly labelled.
4. 2028/2029 (and unreleased 2027 NFL/WWO) rows are ESTIMATED models, not real verified released schedules.
5. Every table row carries an official source link.

## Headline conclusion
Using official rows plus separately labelled 2026-pattern estimates, no 7-, 14-, or 21-day fully free strict window appears in 2027–2029. The best short officially anchored gap is Feb 15–18, 2027; all longer vacation recommendations are least-conflict ESTIMATED candidates and must be rechecked when schedules are released.

No 7-, 14- or 21-day trip can be certified free from all requested radio sports from this incomplete snapshot. In 2027, the [NFL lists Super Bowl LXI on February 14](https://www.nfl.com/news/2026-27-national-football-league-important-dates), and the [Phillies list a spring-training game on February 19](https://www.mlb.com/press-release/press-release-2027-phillies-spring-training-schedule-announced). The intervening dates are only a review candidate, not a verified radio-free interval: other broadcasts, future changes and local carriage remain unknown. [Westwood One warns not every affiliate carries every network broadcast](https://www.westwoodonesports.com/station-finder/). The 2028 and 2029 candidates are model-based and unverified.


## Counts
- Official event / anchor rows: 6591
- Official sources: 748
- Daily scoreboards: 1461
- Merged busy/free intervals: 14303
- Prior generated-data lines reviewed: 2419

## Manual review
- [Sources page](sources.html)
- [Flagged for Review](flagged.html)
- [Line-by-line repo review](review.html)
- [NFL module pages](nfl-lines.html) (lines / strategies / injuries / suggestions)
- [Official event JSON](data/official/events.json)
- [Official-source manifest](research/official/manifest.json)
- [NFL module verification record](research/nfl-module/README.md)
