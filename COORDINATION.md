# COORDINATION.md — Shared Task Board

## Session: arena/cab47657-korea4
Branch: `arena/cab47657-korea4`

## Task Board

| Task | Status | Owner | Files | Notes |
|------|--------|-------|-------|-------|
| COORDINATION.md setup | done | arena/cab47657-korea4 | COORDINATION.md | Initial setup |
| Research MLB schedules (2026-2029) | done | arena/cab47657-korea4 | data/schedules.js | 2026 verified, 2027-29 estimated |
| Research NFL schedules (2026-2029) | done | arena/cab47657-korea4 | data/schedules.js | 2026 verified, 2027-29 estimated |
| Research NCAAF Stanford/Cal schedules | done | arena/cab47657-korea4 | data/schedules.js | 2026 verified from official sites |
| Research Westwood One Sports broadcasts | done | arena/cab47657-korea4 | data/schedules.js | Verified from westwoodonesports.com |
| Research SF Bay Area radio stations | done | arena/cab47657-korea4 | radio.html | KNBR, KGMZ, etc. documented |
| Build web application | done | arena/cab47657-korea4 | index.html + all pages | 8-page dashboard |
| Create executive summary | done | arena/cab47657-korea4 | executive-summary.html | Full analysis with sources |
| Deploy to GitHub Pages | done | arena/cab47657-korea4 | .github/workflows/pages.yml | Workflow created, PRs merged |
| Final integration & verification | done | arena/cab47657-korea4 | all | Merged PR #3 and #4 to main |

## Log

- 2026-11-02: Session started. Set up coordination and began research.
- 2026-11-02: Researched MLB 2026 schedule (verified, released Aug 26, 2025). Source: CBS Sports/MLB.com
- 2026-11-02: Researched NFL 2026 schedule (verified, released May 2026). Source: NFL.com
- 2026-11-02: Researched 49ers 2026 schedule (all 18 games verified). Source: NFL.com
- 2026-11-02: Researched Stanford NCAAF 2026 (12 games verified). Source: GoStanford.com
- 2026-11-02: Researched Cal NCAAF 2026 (12 games verified). Source: CalBears.com
- 2026-11-02: Researched Westwood One NFL broadcasts (TNF/MNF/SNF verified). Source: westwoodonesports.com
- 2026-11-02: Researched SF Bay Area radio stations. Source: knbr.com, Wikipedia
- 2026-11-02: Researched game durations (MLB 2:38, NFL 3:12, NCAAF 3:26). Multiple verified sources.
- 2026-11-02: Built complete web application (8 pages) with schedule data
- 2026-11-02: PR #3 merged to main (full site + data)
- 2026-11-02: PR #4 merged to main (GitHub Pages workflow)
- 2026-11-02: Note: GitHub Pages API (403) - user needs to enable Pages in repo Settings > Pages > Source > GitHub Actions

## Verified Sources

| Data | Source URL | Status |
|------|-----------|--------|
| MLB 2026 Schedule | https://www.cbssports.com/mlb/news/mlb-releases-2026-schedule/ | ✓ Verified |
| NFL 2026 Schedule | https://www.nfl.com/nfl-schedule-release/ | ✓ Verified |
| 49ers 2026 Schedule | https://www.nfl.com/nfl-schedule-release/ | ✓ Verified |
| Stanford NCAAF 2026 | https://gostanford.com/sports/football/schedule | ✓ Verified |
| Cal NCAAF 2026 | https://calbears.com/news/2026/1/26/california-football-announces-2026-schedule.aspx | ✓ Verified |
| Westwood One NFL | https://www.westwoodonesports.com/nfl-schedule/ | ✓ Verified |
| KNBR Schedule | https://www.knbr.com/shows/ | ✓ Verified |
| Athletics 2026 | https://sactownsports.com/mlb/athletics-baseball/athletics-release-2026-mlb-schedule-sac | ✓ Verified |
| MLB Game Duration | https://www.lines.com/guides/how-long-is-baseball-game/1523 | ✓ Verified (2:38) |
| NFL Game Duration | https://www.underarmour.com/en-us/t/playbooks/football/the-real-length-of-a-football-game/ | ✓ Verified (3:12) |
| NCAAF Game Duration | https://www.academicjobs.com/en-us/higher-education-news/how-long-is-a-college-football-game-average-326-explained | ✓ Verified (3:26) |

## Irregularities / Flagged Items

1. **MLB 2027-2029**: Estimated - schedules not yet released (typically Aug of prior year)
2. **NFL 2027-2029**: Estimated - schedules not yet released (typically May of season year)
3. **NCAAF 2027-2029**: Estimated - schedules not yet released (typically Jan/Feb of season year)
4. **49ers Week 18**: Time TBD (NFL flex scheduling)
5. **Stanford/Cal late-season times**: Several Nov games have TBA kickoff times
6. **Athletics relocation**: Moving to Las Vegas in 2028 - future broadcast details uncertain
7. **ACC realignment**: Stanford/Cal in ACC since 2024 - future conference changes possible
8. **GitHub Pages**: API 403 - user must manually enable Pages in Settings > Source > GitHub Actions
