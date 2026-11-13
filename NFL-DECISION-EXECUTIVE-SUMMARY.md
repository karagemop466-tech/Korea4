# NFL decision support — executive summary (2026-11-13 UTC)

Decision-support section for NFL line origination. Live pages: [NFL Lab — overview](nfl-decision.html), [Strategies & leaderboard](nfl-decision-strategies.html), [Validation gates](nfl-decision-validation.html), [Correlation & luck](nfl-decision-correlation.html), [Injuries & depth](nfl-decision-injuries.html), [Suggestions](nfl-decision-suggestions.html), [Open questions](nfl-decision-questions.html), [Decision register](nfl-decision-decisions.html), [Repo audit](nfl-decision-audit.html), [Flagged for review](nfl-decision-flags.html), [Executive summary](nfl-decision-executive.html).

## Headline metrics

- **NFL rows in the dashboard**: 329 — 272 regular season, 48 preseason, plus postseason anchors
- **Week-10 rows re-read against NFL.com**: 14 of 14 match — matchup, kickoff and home/away
- **Strategies designed**: 12 — singles, parlays, player-prop combos, derivatives
- **Strategies that passed every gate**: 0 — leaderboard is empty by design
- **Validation gates defined**: 10 — 3 structural, 6 data, 1 process
- **Open questions**: 22 — 7 answered from official sources
- **Suggestions published**: 12 — 2 already implemented in this section
- **Injury rows transcribed**: 27 — nfl.com Week 10, source-linked
- **49ers depth slots captured**: 28 — official chart dated 11/10/26
- **Depth slots with no documented backup**: 9 — flags FL-05
- **Repo findings**: 14 — 1 fixed, 3 pass, 10 open

## Key points

### What was asked and what now exists

You asked for a requirements-driven collection and analysis build, suggestions with a reviewable section, an explicit list of questions and missing information, an own-line origination system run as a leaderboard with validation gates, correlation analysis, luck removal, injury and backup-depth tracking, an executive summary, a clean category-organized site and a line-by-line repo review. This section delivers each as a page: Landing, Strategies and leaderboard, Validation gates, Injuries and depth, Suggestions, Open questions, Decision register and Repo audit — all reachable from the single 'NFL decision' navigation entry.

### The one honest headline

No strategy can currently be shown to be skill-based. The repository stores schedules and it stores no results and no market prices, so the gates that separate skill from luck (sample size, holdout, closing-line benchmark, bootstrap luck test) cannot run. Rather than publish a leaderboard of unvalidated picks, this section publishes the gates, the reward rules and an empty leaderboard, and states exactly what is missing.

### Own-line origination

A line is a probability in points. Producing one requires a scoring baseline, the measured effect of each input, and a price to test against. The NFL publishes the inputs (schedule, records, injury designations, player volume) but not a baseline, not effect sizes and not prices. The worksheet for one game (49ers at Cowboys, Week 10) shows 7 inputs available, 2 partial and 4 missing, so the originated number is left blank by rule instead of fabricated.

### Injuries and backup depth

Injury tracking is now source-linked: 27 transcribed rows from the league's own Week-10 report, joined to the 49ers' official depth chart (updated 11/10/26). The join produces the number you asked for: 6 of 23 starting slots were on the report as Did Not Participate and one more as Limited at capture. It also produces an uncomfortable answer: at 9 slots the official chart names no backup at all, including left cornerback and nickel back — precisely where a third-string player would have to appear. That gap is flagged rather than filled in.

### Correlation and luck

Eight correlation pairs are registered with expected sign, the affected strategies and an explicit reason the value is blank. The rule is pre-registered: no combo is priced until its correlation is measured on settled legs, and the proposed rejection threshold (|rho| > 0.30) must be fixed before measurement, not after. Luck is handled by construction: the ranking metric is closing-line value, not profit, and the score subtracts the strategy's own 5th-percentile bootstrap result.

### What the review found

The dashboard's 'today' had gone stale (2026-11-05 while the date was 2026-11-13) and is fixed in this branch. The source snapshot is 11 days old because the refresh workflow is bound to a superseded branch name. 14 of 14 Week-10 rows match the league page exactly. A legacy file still calls non-official data 'verified'. Large pages (4.9 MB and 2.3 MB) are slow to review. Five concurrent sessions claimed overlapping NFL work today, which is called out on the board.

### What you must decide

Ten decisions are registered; four are truly blocking. (1) Capture results now (D-01). (2) Snapshot injury reports with timestamps (D-02). (3) Either license line data or accept that profitability can never be claimed (D-03/D-04). (4) Fix the refresh pipeline (D-09). The rest — reward currency, ranking metric, correlation threshold, depth-chart coverage — are choices only you can make, and each is written out with a recommendation and the evidence behind it.

### What is deliberately not claimed

No profit, no edge, no correlation value, no effect size, no third-string identification, no 'best path'. Every one of those would have required a number that no official source provides. Blank cells are evidence of a gap, not a missing feature.

## Sources used

- [NFL.com — Injuries — Week 10 of the 2026 season (official injury report)](https://www.nfl.com/injuries/) — Injury and depth section; starting-slot availability cross-reference.
- [San Francisco 49ers (official club site) — 49ers Depth Chart — updated as of 11/10/26](https://www.49ers.com/team/depth-chart) — Backup-depth model; detecting slots with no listed backup.
- [San Francisco 49ers (official club site) — 49ers Injury Report (weekly news index)](https://www.49ers.com/team/injury-report/) — Confirming club-level (as opposed to league-level) designation history.
- [San Francisco 49ers (official club site) — 49ers 2026 Schedule](https://www.49ers.com/schedule/) — Home/away and venue checks; radio matrix; the Week 11 venue flag.
- [NFL.com — 2026 NFL schedule — Week 10 (by week)](https://www.nfl.com/schedules/2026/by-week/week-10) — Line-by-line audit of the 14 Week-10 rows in data/official/events.json.
- [NFL.com — 2026-27 National Football League important dates](https://www.nfl.com/news/2026-27-national-football-league-important-dates) — Why report timing (not just content) is a usable signal; filing deadlines.
- [NFL.com — 2026 NFL player statistics — passing](https://www.nfl.com/stats/player-stats/) — Player-prop strategies: the only officially published player performance series available.
- [NFL.com — NFL official 2026 schedule index](https://www.nfl.com/schedules/) — Repo audit context for the existing NFL rows.
- [NFL Football Operations (media.nfl.com PDF) — 2026 Official Playing Rules of the NFL (PDF)](https://media.nfl.com/content/dam/communications/Official%20Playing%20Rules/2026%20Official%20Playing%20Rules.pdf) — Duration provenance on NFL rows (the repo's `duration_source_url`).
- [This repository — data/official/events.json](https://github.com/karagemop466-tech/Korea4/blob/main/data/official/events.json) — Audit measurements (counts, field coverage, duplicate ids).
- [This repository — data/official/meta.json](https://github.com/karagemop466-tech/Korea4/blob/main/data/official/meta.json) — Stale-date finding; snapshot-age disclosure.
- [This repository — .github/workflows/fetch-official.yml](https://github.com/karagemop466-tech/Korea4/blob/main/.github/workflows/fetch-official.yml) — Refresh-coverage finding (branch-bound trigger, no schedule).
- [This repository — data/nfl-2026.json (legacy snapshot)](https://github.com/karagemop466-tech/Korea4/blob/main/data/nfl-2026.json) — Irregularity FL-01 (non-official sources labelled verified).
- [This repository — scripts/verify.py (static gate)](https://github.com/karagemop466-tech/Korea4/blob/main/scripts/verify.py) — What the existing gate does and does not prove.
- [This repository — scripts/collect_official.py (collector)](https://github.com/karagemop466-tech/Korea4/blob/main/scripts/collect_official.py) — Stale-date root cause and fix.
- [This repository — data/nfl/ (NFL decision module merged in PR #45)](https://github.com/karagemop466-tech/Korea4/tree/main/data/nfl) — Reconciliation: checking where the two captures agree and where this section adds something the merged module lacks.
- [This repository — research/nfl-module/README.md (merged module's verification record)](https://github.com/karagemop466-tech/Korea4/blob/main/research/nfl-module/README.md) — Cross-checking this session's reading of the same official pages; recording where the two sessions agree.
- [This repository — COORDINATION.md (parallel-session board)](https://github.com/karagemop466-tech/Korea4/blob/main/COORDINATION.md) — Avoiding duplicate work with the four other 2026-11-13 NFL sessions.

## Verification performed

- All 14 Week-10 NFL rows re-read against NFL.com's Week-10 page: matchup, kickoff and home/away all match.
- 27 injury rows and the full 49ers depth chart transcribed from official pages on 2026-11-13.
- Every row on this section's pages carries an official or repository source, enforced by `scripts/verify_nfl_lab.py`.
- `scripts/verify.py` (existing structural gate) re-run after the rebuild: 0 errors, 0 warnings, 0 broken links.

## Flagged

- **FL-01** — `data/nfl-2026.json` says `verified: true` but cites three non-official sites and contradicts the official home/away for Week 1 (Melbourne). *(UNRESOLVED — recommended for deletion (D-10))*
- **FL-02** — Official-source snapshot is 11 days old at rebuild (2026-11-02 vs 2026-11-13); the scheduled refresh workflow is bound to a superseded branch name. *(UNRESOLVED — fix recommended (SUG-08))*
- **FL-03** — 49ers.com lists Week 11 (2026-11-22, vs Vikings) at Estadio Banorte, 5:20 PM PST, NBC, while the league-sourced row in `events.json` carries no venue and no international marker. *(FLAGGED AS UNVERIFIED — venue not confirmed on the league page in this session)*
- **FL-04** — Injury report was captured mid-week: all 49ers and Cowboys game-status fields were blank while 15 players combined were listed as Did Not Participate. *(TIME-SENSITIVE — re-capture required before any game-day decision)*
- **FL-05** — The official 49ers depth chart lists no backup at 9 slots (LCB, NB, RG, RT, FB, P, K, H, LS). *(UNVERIFIABLE FROM OFFICIAL SOURCE — replacement quality unknown)*
- **FL-06** — Every correlation value in this section is blank, and every strategy fails at least one gate; the leaderboard has no entries. *(BY DESIGN — not a defect)*
