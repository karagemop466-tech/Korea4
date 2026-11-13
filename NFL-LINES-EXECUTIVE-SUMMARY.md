# NFL Lines — executive summary

**As of 2026-11-13 (UTC)** · Detailed pages start at [`nfl-lines.html`](nfl-lines.html). This is a research and decision-support prototype, not a sportsbook feed or betting advice.

## What is built

- A 2026 official-schedule panel with **272 regular-season matchups** across 18 weeks. The snapshot was retrieved on **2026-11-02**; 120 captured final-score cards cover Weeks 1–8. Week 18's official cards contain matchups only, so dates and kickoff times remain blank.
- Model-originated **fair spreads, totals and win probabilities** for the 13 Week 10 games not yet kicked off at this run, plus 13 Week 11 games. These are model estimates, not market lines. No sportsbook price or edge is supplied.
- A Week 10 injury dataset with **298 rows** across 32 teams, including 296 player entries and two league “No Injuries Reported” entries. Its source page is official, but row-by-row transcription is still provisional and flagged for review.
- **173 depth rows** for the 49ers, Dolphins and Ravens, including second-, third- and fourth-string tiers. Depth coverage for the other 29 teams is unverified. Injury/depth availability adjustments are therefore missing for the current games; the engine currently applied no penalty.
- **10 registered strategies** spanning singles, parlays and player props, with 12 validation gates. The leaderboard is intentionally unscored because there is no price feed or timestamped bet log; all actual score fields remain blank.
- A 120-game exploratory result analysis, season-to-season persistence measures, explicit review flags, an 18-item suggestions register, and a 24-item open-decision / research register.

## What the evidence currently says

The home win rate in the captured 120 completed games is **52.1%** (95% approximate interval **43.1%–61.0%**); the interval includes 50%. Mean home margin is **+0.72 points** (95% approximate interval **−1.61 to +3.04**). These are descriptive statistics, not a demonstrated edge.

An exploratory regression using only information available before each game—the prior-game rolling net-point differential, rest differential and previous-11-day game count—has **R² 0.205** and residual standard deviation **11.58 points**. Roughly **79.5% of observed margin variance remains unexplained**. It has not been tested on priced bets, and no multiple-testing correction or walk-forward profitability test has been passed.

The year-to-year points-differential correlation is **r = 0.322 (r² = 0.104, n = 32 clubs)** for the **completed 2024-to-2025 seasons only**. The partial 2026 season is excluded. This is a small, descriptive persistence statistic—not a causal decomposition of skill and luck.

## Blocks before any strategy can be scored

1. **Prices:** no official league source publishes betting prices. A timestamped owner bet log or licensed feed is needed to calculate edge, ROI and leaderboard points.
2. **Availability:** only 3 of 32 official club depth charts have been captured; unverified players are not assigned a tier or penalty.
3. **Historical evaluation:** only one weekly injury report is captured, so availability strategies lack a historical walk-forward panel.
4. **Player props:** official per-player usage histories are not yet ingested; player-prop numeric lines remain untestable.
5. **Risk policy:** bankroll, weekly exposure and owner-specific limits remain open; do not treat draft rules as an approved bankroll plan.
6. **Source fidelity:** row-level audits remain open for the injury transcription, depth names, and the complete 2024–2026 standings fields. Known split/streak corrections are applied and disclosed.

## Site map and decision path

[`NFL Lines landing page`](nfl-lines.html) → [schedule/results](nfl-schedule.html) · [fair lines](nfl-fair-lines.html) · [injuries/depth](nfl-availability.html) · [analysis](nfl-analysis.html) · [strategies/gates](nfl-strategies.html) · [leaderboard](nfl-leaderboard.html) · [suggestions](nfl-suggestions.html) · [questions/information needed](nfl-questions.html) · [flagged review](nfl-flagged.html).

Every data table row has an official-source link. Missing or uncertain values are blank and marked unverified. Structural validation confirms the official-host links and internal links; it does **not** independently prove that each parsed value matches its source.

## Manual source review

- [Official NFL 2026 schedule, Week 1](https://www.nfl.com/schedules/2026/by-week/week-1) and [Week 18](https://www.nfl.com/schedules/2026/by-week/week-18)
- [Official NFL 2026 standings](https://www.nfl.com/standings/league/2026/REG), [2025](https://www.nfl.com/standings/league/2025/REG), and [2024](https://www.nfl.com/standings/league/2024/REG)
- [Official Week 10 injury report](https://www.nfl.com/injuries/league/2026/reg10)
- [49ers](https://www.49ers.com/team/depth-chart), [Dolphins](https://www.miamidolphins.com/team/depth-chart), and [Ravens](https://www.baltimoreravens.com/team/depth-chart) depth charts
- [NFL official important dates and reporting windows](https://www.nfl.com/news/2026-27-national-football-league-important-dates)

## Quality checks

- `python3 scripts/nfl_signals.py` — refreshes derived NFL outputs from the captured local files.
- `python3 scripts/build_nfl_site.py` — builds the NFL Lines pages.
- `python3 -m unittest discover -s tests -p 'test_nfl_site.py' -v` — **6 tests pass**.
- `npm test` — existing dashboard tests pass.
- `python3 scripts/verify.py` — **0 errors, 0 warnings; 352 NFL Lines table rows linked to official allowlisted sources; 0 broken internal links**. This is structural validation, not row-value auditing.
