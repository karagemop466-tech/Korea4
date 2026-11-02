# COORDINATION.md — Shared Task Board

Session ID: `ccb3febc-korea4` (Arena branch `arena/ccb3febc-korea4` — fixed by Arena; do not rename/switch)
Started: 2026-11-02

| # | Task | Status | Owner | Files |
|---|------|--------|-------|-------|
| 1 | Coordination board + repo review | done | ccb3febc-korea4 | COORDINATION.md, README.md |
| 2 | Verify official schedule availability 2026-2029 (MLB/NFL/Stanford/Cal/Westwood One) | done | ccb3febc-korea4 | docs/sources.md, site/sources.html |
| 3 | Estimate game durations (MLB/NFL/NCAAF) from official/trusted sources | done | ccb3febc-korea4 | docs/durations.md |
| 4 | Compute vacation windows 2027/2028/2029 (1/2/3-week, estimated where unreleased) | done | ccb3febc-korea4 | docs/vacation-windows.md, site/vacation.html |
| 5 | SF Bay Area radio availability (94122, AM/FM: KNBR etc., Westwood One affiliate) | done | ccb3febc-korea4 | docs/radio.md, site/radio.html |
| 6 | Build GitHub Pages site (landing + subpages, tables, executive summary) | done | ccb3febc-korea4 | site/, .github/workflows/pages.yml |
| 7 | Final integration: line-by-line re-verify, build check, PR + merge, Pages deploy | done | ccb3febc-korea4 | all |

## Log
- 2026-11-02 ccb3febc: Repo reviewed — only README.md ("# Korea4"), single initial commit a6e22c4. No prior site/data. All work is greenfield.
- Note: prompt asks for branches named session-<id>/<task>; Arena fixes this session to `arena/ccb3febc-korea4`, so all work stays there (system rule wins).

## Rules
- Every table row needs an official source link. Unconfirmable = blank + "UNVERIFIED" flag, published on Flagged for Review page. Never infer.
- Estimated schedules (unreleased years) must be labelled ESTIMATED, never presented as verified.

- 2026-11-02 ccb3febc: Sources verified via official MLB.com/NFL.com/CFP/Stanford/Cal/Westwood One pages (see docs/sources.md, 19 rows). Durations: MLB 2:38 official; NFL/NCAAF secondary estimates flagged F6.
- Finding: no 7/14/21-day free window 2027-2029 (strict def.); best Feb 15-18 2027 verified; Feb 2028/2029 estimated. 12 irregularities in docs/flagged.md / site/flagged.html (F1-F12).
- Site built in site/ (6 pages), internal-link check passed (1 false positive from JS template string in calendar.html). Pages: repo already has Pages enabled (legacy, main:/, status built, https://karagemop466-tech.github.io/Korea4/). Token cannot switch it to workflow type (403), so site is served at /site/ with a root index.html redirect; Actions workflow removed to avoid a failing deploy.

- FINAL: PR https://github.com/karagemop466-tech/Korea4/pull/1 MERGED to main 2026-11-02T17:21Z. GitHub Pages build status=built, live verified: https://karagemop466-tech.github.io/Korea4/site/ (also /vacation.html, /calendar.html, /radio.html, /sources.html, /flagged.html). All tasks done; F1-F12 published on Flagged page, non-blocking.
