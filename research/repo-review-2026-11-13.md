# Repository review — 2026-11-13

## Scope and method

Reviewed the current repository's root dashboard generators, NFL-specific scripts/data/pages, verification gate, tests, and publishing configuration. Checked local Git state and the live GitHub Pages configuration. The existing root dashboard's data snapshot remains dated 2026-11-02 / build 2026-11-05; the NFL Lines work is a separate namespace and does not replace that dashboard's source records. Current review is a code/data-structure audit; values are independently verified only where the official source was actually compared. A link or successful structural gate is not proof of a value.

## Findings

| ID | Severity | Finding | Impact / action | Official/manual source |
|---|---|---|---|---|
| RV-01 | High | NFL schedule snapshots were retrieved 2026-11-02. They contain 272 regular-season matchups, 120 captured finals through Week 8, and 16 Week 18 matchups with no dates/times. | The schedule page identifies snapshot age; Week 18 dates/times remain blank. Refresh official pages before relying on future scheduling or current results. | [NFL Week 1 schedule](https://www.nfl.com/schedules/2026/by-week/week-1); [Week 18](https://www.nfl.com/schedules/2026/by-week/week-18) |
| RV-02 | High | 2026 standings are a partial-season capture as of 2026-11-13, so they are appropriate only as current-form inputs, not a completed-season persistence sample. | Persistence analysis now excludes 2026 and compares only complete 2024–2025 seasons (32 team pairs). The entire standings CSV still needs field-by-field audit. | [2024](https://www.nfl.com/standings/league/2024/REG), [2025](https://www.nfl.com/standings/league/2025/REG), [2026](https://www.nfl.com/standings/league/2026/REG) |
| RV-03 | High | The NFL Week 10 injury report transcription has 298 rows but has not completed independent row-by-row comparison; the data's source URL does not itself certify the name/designation values. | Published with a provisional-source-fidelity flag. Do not interpret a missing player as healthy or assume the weekly report covers injured reserve. | [Official Week 10 injury report](https://www.nfl.com/injuries/league/2026/reg10) |
| RV-04 | High | Only the 49ers, Dolphins and Ravens have depth-chart captures (173 rows total); 29 clubs are not captured. | Unknown depth/replacement/penalty values stay blank. No missing depth penalty is silently set to zero in the displayed availability detail; the fair-line pages disclose that no availability adjustment was applied. | [49ers](https://www.49ers.com/team/depth-chart), [Dolphins](https://www.miamidolphins.com/team/depth-chart), [Ravens](https://www.baltimoreravens.com/team/depth-chart) |
| RV-05 | High | No official NFL page contains sportsbook prices, and no timestamped owner bet log is present. | Market prices, edges, ROI, points and rankings remain blank; all strategies are gated from the rewards leaderboard. | [NFL official schedule](https://www.nfl.com/schedules/2026/REG1) |
| RV-06 | Medium | The first exploratory game-level model explains 20.5% of the captured score-margin variance; 79.5% remains in residuals. | Published as exploratory only; this is neither a profitability test nor a clean skill/luck decomposition. No multiple-testing correction is claimed. | [NFL captured Week 8 schedule/results](https://www.nfl.com/schedules/2026/by-week/week-8) |
| RV-07 | Medium | Rest/congestion features can leak information if later games are included. | The 11-day count is now limited to games on or before the game date. Model inputs are described; the current data remains exploratory and not approved by walk-forward gates. | [Official schedule snapshots](https://www.nfl.com/schedules/2026/by-week/week-1) |
| RV-08 | Medium | Previously identified standings split/streak discrepancies were present in the provisional CSV. | Applied the seven confirmed corrections captured in this session. Full row-by-row reconciliation remains open and is shown on the flagged page. | [NFL 2024 standings](https://www.nfl.com/standings/league/2024/REG), [2025](https://www.nfl.com/standings/league/2025/REG), [2026](https://www.nfl.com/standings/league/2026/REG) |
| RV-09 | Low | Existing `scripts/verify.py` checks structure and source hosts but does not verify each value against primary source content. | Extended structural validation to all NFL Lines tables and JSON files; report explicitly labels its limit. Separate row-by-row content audit remains open. | [NFL injury report](https://www.nfl.com/injuries/league/2026/reg10) |
| RV-10 | High | GitHub Pages is configured as legacy publishing from `main:/`; the active session branch is not live until merged. | The new pages are locally served and verified. A PR merge to `main` is required for publication; deployment remains pending. | [Repository Pages configuration](https://github.com/karagemop466-tech/Korea4/settings/pages) |

## Verification run

- NFL engine successfully generated 272 schedule rows, 10 deficiency rows, 13 current-week prospective fair lines, 13 next-week lines and 10 registered strategies.
- The 120-game captured panel: home-win rate 52.08% (approximate 95% CI 43.14%–61.02%); average home margin +0.72 (approximate CI −1.61 to +3.04).
- Complete-season persistence panel: 32 2024→2025 team pairs; net-points/game r=0.3223, r²=0.1039.
- `python3 -m unittest discover -s tests -p 'test_nfl_site.py' -v`: 6 pass.
- `npm test`: pass.
- `python3 scripts/verify.py`: 0 errors, 0 warnings; 352 NFL Lines table rows with allowlisted official links; 0 broken internal links; 21 JSON files parsed.
- No end-to-end comparison of every captured injury/depth/standings value against its live official page has yet been completed. RV-02–RV-04 and RV-08 remain visible flags, not implied passes.
