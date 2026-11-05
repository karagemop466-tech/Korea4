# COORDINATION.md — unified shared task board

Last integration update: 2026-11-05 (UTC) — integration takeover of stale PRs #18/#25 begins
Latest audit session: `arena/65a1da2b-korea4`
Active final verification session: `arena/8111ceb3-korea4` (this session)
Fixed working branch: `arena/8111ceb3-korea4`

## Session — `arena/5488dbac-korea4` (2026-11-05 UTC)

| Task | Status | Owner | File scope | Notes |
|---|---|---|---|---|
| F2 — Final integration follow-up: independently verify current official-source snapshot, fix stale dashboard “today” date, rebuild, run checks, and publish via PR/Pages | done | `arena/5488dbac-korea4` | `COORDINATION.md`, `scripts/collect_official.py`, `scripts/build_site.py`, `tests/test_dashboard_generator.py`, generated root dashboard/data artifacts | Merged via PR #31; Pages build and live checks passed. The official raw-source snapshot age (Nov 2) remains disclosed. |

### F2 implementation and verification record — 2026-11-05 (`arena/5488dbac-korea4`)

- **Issue corrected:** Collector had frozen `SYSTEM_TODAY` at 2026-11-02. Dashboard now derives the selected date from `America/Los_Angeles` at generation time; the 2026-11-05 build selects the current Pacific date. Added a regression test comparing dashboard metadata with today's Pacific date.
- **Snapshot age made explicit:** the generator distinguishes `generated_utc` from `source_snapshot_utc` (official manifest timestamp). Current build: 2026-11-05T21:10:04Z; captured-source manifest: 2026-11-02T17:41:45Z. Site warns this is not a live feed and does not imply that sources were refetched on the build date.
- **Official-source live spot checks (2026-11-05):** [Westwood One current NFL schedule](https://www.westwoodonesports.com/nfl-schedule/) lists Jacksonville at Baltimore on Nov 5 at 7:30 PM ET and [its event page](https://www.westwoodonesports.com/events/548561/) is the row source. The dashboard row is 4:30 PM PST (Nov 5), 269-minute official WWO network window, and remains subject to the disclosed official timestamp/end-window caveat. [NFL official 2026–27 dates](https://www.nfl.com/news/2026-27-national-football-league-important-dates), [MLB official 2027 schedule release](https://www.mlb.com/press-release/2027-mlb-season-schedule-announced-phillies-home-opener-set-for-thursday-april-1-against-the-washington-nationals), [Stanford official 2026 football schedule](https://gostanford.com/sports/football/schedule), and [Cal official 2026 football schedule](https://calbears.com/sports/football/schedule/2026) were fetched live for cross-check context. These spot checks do not certify every captured row.
- **Scope and limitations:** offline `collect_official.py` rebuilt from the captured official raw snapshots (748 sources, 6,607 event/anchor rows, 1,461 scoreboard dates, 30 MLB clubs, 311 WWO rows; all data counts unchanged). It did not refresh the official raw files. Source snapshot is Nov 2; rows for schedules released or updated after that timestamp may be absent or stale. Existing unknown schedules remain blank/UNVERIFIED and estimates remain explicitly ESTIMATED; no values were inferred.
- **Gates:** `python3 scripts/verify.py` PASS (0 errors/warnings; 10,086 source-linked primary rows, 689 checked internal links/0 broken, JSON valid, JS syntax OK); `node --check js/app.js` PASS; `npm test` PASS; `.venv/bin/python -m unittest discover -s tests -p 'test_dashboard_generator.py'` PASS (3 tests); `git diff --check` PASS. Full manual verification of all 10,086 rendered table rows against live sites is not claimed; the repo verification report explicitly describes itself as structural.
- **Publication result:** claim commit `e219bde`; implementation commit `8a68683`; PR [#31](https://github.com/karagemop466-tech/Korea4/pull/31) MERGED 2026-11-05T21:11:12Z as `a8b28fa38584ec11745d0800897d9282a3fce150`. Verify workflow run [42110249985](https://github.com/karagemop466-tech/Korea4/actions/runs/42110249985) SUCCESS. GitHub Pages deployment [42110316393](https://github.com/karagemop466-tech/Korea4/actions/runs/42110316393) SUCCESS (build, deploy, and report-build-status).
- **Live check:** https://karagemop466-tech.github.io/Korea4/?v=a8b28fa and `/daily.html?date=2026-11-05&v=a8b28fa` returned updated pages showing selected date 2026-11-05, source snapshot refresh 2026-11-02, WWO JAX@BAL 4:30–8:59 PM PST, and explicitly unverified estimated gaps.

## Current session — arena/8111ceb3-korea4 (2026-11-05) — T1 integration takeover

| Task | Status | Owner | File scope | Notes |
|---|---|---|---|---|
| T1 — Take over the outstanding integration request from stale PRs #18 (`arena/aea8720a-korea4`, last commit 2026-11-03T19:40Z) and #25 (`arena/46c69197-korea4`, last commit 2026-11-03T23:28Z): both sessions are >48 h stale (60-minute takeover rule), their branches have unrelated git roots (fresh Arena snapshots) so the PRs are permanently CONFLICTING and can never merge as-is. Land the PR #25 safety-audit record, fix the verified arithmetic/provenance bugs neither PR shipped (busy-minute interval-union double count, distinct-day counters, Giants station team-name test, 9 49ers vividseats.com reseller citations), publish the audit on `flagged.html`, add regression tests, harden `scripts/verify.py`, regenerate the site, then run the PR → merge → Pages-deploy cycle and record it. After landing, close PRs #18/#25 with a handoff comment. | in progress | `arena/8111ceb3-korea4` | `COORDINATION.md`, `research/vacation-safety-audit-46.md`, `research/integration-audit-2026-11-05.md`, `scripts/collect_official.py`, `scripts/build_site.py`, `scripts/verify.py`, `js/app.js`, `tests/*`, `.github/workflows/check.yml`, regenerated `data/official/*` + root HTML | Claim pushed immediately per protocol. PR #18/#25 file scopes verified against this list before starting; their sessions have made no commits since 2026-11-03. Baseline: `main` @ `1ed4934` (PR #30 merge). |

### T1 pre-work verification (2026-11-05, arena/8111ceb3-korea4)

- Working tree clean; branch identical to `origin/main` @ `1ed4934`.
- Reproduced every PR #25 audit finding against the published snapshot before touching anything:
  - `events.json` MLB Giants rows: 393 total, 377 with EMPTY `stations` (bug: `"Giants" in (away, home)` is tuple membership against full team name "San Francisco Giants", always False), 16 (Giants vs Athletics only) labelled `960 AM KNEW / A's Cast`; all 387 Athletics rows carry that combined terrestrial + streaming label with no game-level carriage evidence.
  - 9 49ers rows (`49ers-ab581766…` through `49ers-ace0ab32…`, 2026-11-08 → 2027-01-03) cite `www.vividseats.com` — a ticket reseller, violating the official-sources-only rule. PR #18's parser fix (always cite the captured official `49ers.com/schedule` page) is correct and is adopted.
  - `compute_vacation_windows` sums `end - start` over overlapping intervals (e.g. 2027-02-03 window displays 3,944 busy minutes where the union is 2,504) and increments `unverified_days`/`model_days` per interval rather than per distinct date.
- PR #18 (33 files) reviewed hunk by hunk: adopted items are the 49ers provenance fix, `verify.py` hardening (visible source-link match, snapshot SHA-256/byte integrity, official-domain allowlist), and the `GAP` → `FREE` timeline label; rejected items and reasons are recorded in the T1 completion record below. PR #18 does NOT contain fixes for the busy-minute union, distinct-day counters, or Giants station bug — those are new in T1.
- The 60-minute takeover rule applies to both stale sessions; this entry is the handoff note required by the board.

## Session — arena/5cc34200-korea4 (2026-11-03) — F1 audit record

| Task | Status | Owner | File scope | Notes |
|---|---|---|---|---|
| F1 — Independent line-by-line re-verification of the merged FREE TIME VACATION project on the fixed Arena branch: re-run the verify gate, spot-check official sources (MLB/NFL/WWO/49ers/Stanford/Cal/radio) against published rows, check live Pages site, flag irregularities, then run the PR → merge → Pages-deploy cycle and record results | done (PR/merge/deploy result recorded below after merge) | `arena/5cc34200-korea4` | `COORDINATION.md` only (audit record); no data/site files touched — avoids overlap with open PRs #18 (`arena/aea8720a-korea4`), #25 (`arena/46c69197-korea4`), #26 (`arena/3f48e269-korea4`), owned by those sessions and not claimed here | Baseline: `main` @ `4de9afd` (PR #28 merged). Branch rebased onto it 2026-11-03; claim commit `68900b4` pushed immediately per protocol. IR-001…IR-017 remain published on `flagged.html` and do not block merge. |

### F1 verification record — 2026-11-03 (arena/5cc34200-korea4)

- **Local gate re-run on `main` @ `4de9afd`:** `python3 scripts/verify.py` → PASS, 0 errors / 0 warnings (9,356 primary static table rows each with an official source link, 689 internal links, 0 broken, 9 JSON valid, JS syntax OK; report at `research/verification-report.md`); `node --check js/app.js` PASS; `node tests/test_dashboard.mjs` PASS; `npm test` (test_core.mjs) PASS; `python -m unittest discover -s tests -p test_dashboard_generator.py` → 2 tests OK (the CI-gated set). Known inherited `tests/test_build.py` failures (D1-04, superseded planner artifact expectations) are not part of the CI gate and remain disclosed on the flagged page.
- **Data integrity:** `data/official/events.json` = 6,607 rows (MLB 5,893 · NFL 345 · WWO 311 · NCAAF 24 · MLS 34), 0 rows missing a source URL; priority flags: 5,783 HIGH/FOCUS rows (all MLB, all NFL incl. preseason/postseason/special, all WWO, Giants/A's/49ers/Stanford/Cal FOCUS, Earthquakes). `data/official/meta.json` counts consistent (748 official sources, 1,461 daily scoreboards 2026-11-01→2029-12-31, 14,364 intervals, durations MLB 158 / NFL 192 / NCAAF 204 / MLS 120 min).
- **Official-source spot checks (live web, 2026-11-03), all matching published rows:**
  - [NFL 2026–27 important dates](https://www.nfl.com/news/2026-27-national-football-league-important-dates): **Super Bowl LXI = February 14, 2027 at SoFi Stadium** ✓ matches `days-2027.json` 2027-02-14 anchor and vacation page; Week 18 Jan 9–10, Wild Card Jan 16–18, Divisional Jan 23–24, CCGs Jan 31 ✓; Sep 10, 2026 49ers–Rams Melbourne ✓ and Nov 22, 2026 Vikings–49ers Mexico City ✓ match the 36 FOCUS 49ers rows.
  - SoFi Stadium official [LXI announcement (Feb 9, 2026)](https://www.sofistadium.com/news/detail/los-angeles-region-to-host-super-bowl-lxi-in-2027-welcoming-the-nfls-biggest-stage-for-the-second-time-this-decade-to-sofi-stadium): Feb 14, 2027 ✓.
  - MLB 2027 schedule released Jul 16, 2026 ([Brewers](https://www.mlb.com/press-release/press-release-brewers-announce-2027-regular-season-schedule) / [Orioles](https://www.mlb.com/press-release/press-release-orioles-announce-2027-regular-season-schedule) / [Mets](https://www.mlb.com/press-release/mets-announce-2027-schedule) official releases): regular season opens **Thu Mar 25, 2027**, spring training begins **Feb 19, 2027** ✓ matches `days-2027.json` (2027-02-19 spring-training rows VERIFIED) and the vacation-page anchors.
  - [MLB Stats API season=2028](https://statsapi.mlb.com/api/v1/schedule?sportId=1&season=2028&hydrate=team,linescore) queried live → `totalGames: 0` ✓ confirms IR-007: 2028/2029 MLB not officially released; site correctly shows those as UNVERIFIED/ESTIMATED, never as released schedules.
  - [Westwood One official NFL schedule](https://www.westwoodonesports.com/nfl-schedule/) fetched live: Nov 5 JAX@BAL TNF 7:30 PM ET, Nov 26 Thanksgiving tripleheader 12:30 PM ET, **Dec 17 49ers@Chargers TNF 7:30 PM ET at SoFi**, Dec 25 Christmas tripleheader ✓ exactly match `events.json` rows `wwo-548561` (2026-11-05 4:30 PM PST), `wwo-548512` (2026-11-26 9:30 AM PST), `wwo-548568` (2026-12-17 4:30 PM PST), `wwo-548528` (2026-12-25 9:30 AM PST), each VERIFIED with its official event-page source URL.
  - [gostanford.com official 2026 football schedule](https://gostanford.com/sports/football/schedule) and [calbears.com](https://calbears.com/sports/football/schedule/2026): Aug 29 Hawai'i, Sep 4 Miami, Sep 5 UCLA, Sep 12 at Syracuse, Sep 19 Wagner / at Duke, Sep 25 Clemson, Sep 26 Georgia Tech, Oct 3 at UNLV / at Wake Forest, Oct 10 VT / at Notre Dame, Oct 17, Oct 23 NC State, Oct 31 at Louisville, Nov 14 at Virginia Tech, **Nov 21 129th Big Game at California**, Nov 28 SMU / Pittsburgh ✓ all 19 dated NCAAF rows in `events.json` match (12 Stanford + 7 dated Cal; 5 remaining Cal rows correctly TBA/UNVERIFIED). Cal official pages confirm **810 AM** English radio (call sign now **KSFO 810 AM** per the 2025 KGO→KSFO change — IR-012 correction holds; radio.html uses KSFO 810 AM VERIFIED).
  - KNBR 680 AM / 104.5 FM flagship for Giants & 49ers per official team pages, consistent with radio.html matrix.
- **Live Pages site (2026-11-03):** Pages API `status=built`, latest main build green (Actions `pages build and deployment` + `Verify static Pages source` success on `main` @ 23:30Z). Live fetches: `/` renders dashboard (6,607 rows, 748 sources, 1,461 scoreboards, 30 MLB clubs, 1,689 reviewed lines, ESTIMATED/UNVERIFIED labels, 2027–2029 least-conflict candidate table with `Strict free = False`, IR-001…IR-017 table); `/vacation.html` renders the strict conclusion, Feb 15–18 2027 officially anchored gap, anchors table (SB LXI 2027-02-14 VERIFIED DATE; Phillies spring training 2027-02-19), and the schedule-availability table (2028/2029 MLB API=0 rows UNVERIFIED; 2027 NFL game-by-game unavailable UNVERIFIED; WWO 2027 only through Jan 11 UNVERIFIED); `/daily.html?date=2026-11-03` renders today's scoreboard honestly as `NO CAPTURED BLOCKS — UNVERIFIED` / `ESTIMATED GAP 24h — UNVERIFIED` with the duration-research table (MLB 2:38 official 2025 average; NFL/NCAAF averages FLAGGED secondary/dated; NBA/NHL/WNBA UNVERIFIED).
- **Line-by-line repo review notes:** legacy `data/vacation-windows.json` / `data/schedules.js` / `data/radio-guide.json` contain prior-session values incl. secondary sources (legionreport.com, news.radio-online.com) and a mislabelled "Post-Super Bowl LXI" 2026 window (actually LX); these files are referenced **only** by `review.html`, where every such line is already marked `REVIEWED — OFFICIAL REPLACEMENT` or `FLAGGED — SECONDARY SOURCE` with official links; the primary pages load only `data/official/events.json`. No primary page presents them as verified. No new irregularity; no data/site change required.
- **Irregularities:** none new. IR-001…IR-017 remain published on `flagged.html` with official source links and do not block merge. Open PRs #18/#25 belong to other active sessions and were not touched.
- **PR / merge / deploy result:**

| Item | Result |
|---|---|
| PR | [#29 — F1: independent line-by-line re-verification of FREE TIME VACATION dashboard (arena/5cc34200-korea4)](https://github.com/karagemop466-tech/Korea4/pull/29) |
| State | MERGED |
| Merge commit | `14c2024f73f3fe8f4bb8ccf7635425fddd830755` — 2026-11-03T23:34:57Z |
| Pre-merge check | "verify" workflow on PR #29 — SUCCESS; PR mergeable after rebase onto `main` @ `bfec9fb` (conflict with parallel-session board updates resolved by rebase; no other session's content discarded — net diff vs main is this board entry only, `COORDINATION.md` +37/−1) |
| GitHub Pages | build on `14c2024` → `status=built` (2026-11-03T23:35Z); Actions "pages build and deployment" + "Verify static Pages source" on `main` @ `14c2024` both SUCCESS |
| Live check | https://karagemop466-tech.github.io/Korea4/ (cache-busted `?v=14c2024`) renders the dashboard: 6,607 official event/anchor rows, 748 official sources, 1,461 daily scoreboards, 30 MLB clubs, ESTIMATED/UNVERIFIED labels, 2027/2028/2029 least-conflict candidate table (`Strict free = False`), IR-001…IR-017 flagged table |
| Flagged irregularities | None new from this session; IR-001…IR-017 remain on `flagged.html` and did not block the merge |

This follow-up record (PR/merge/deploy result) is carried by a second docs-only PR from the same fixed branch, per the established pattern.

## Current session — arena/6d417a78-korea4 (2026-11-03)

| Task | Status | Owner | File scope | Notes |
|---|---|---|---|---|
| E1 — Independent final verification of merged FREE TIME VACATION dashboard (PR #21 baseline `92dad6d`): re-run verify gate, spot-check official NFL/WWO sources and live Pages site, record PR/merge/deploy result | done | `arena/6d417a78-korea4` | `COORDINATION.md` only | See E1 record below. No data/site files touched — avoids overlap with open PR #18 (`arena/aea8720a-korea4`, CONFLICTING, not claimed here). IR-001…IR-017 stay on `flagged.html` and do not block merge. |

### E1 verification record — 2026-11-03
- `python3 scripts/verify.py` → **PASS**: 0 errors, 0 warnings; 9,356 primary static table rows each with an official source link; 689 internal links, 0 broken; 9 JSON files valid. `node --check js/app.js` PASS; `npm test` PASS (Pacific-time, interval-union, TBD and candidate tests).
- Data: `data/official/events.json` = 6,607 rows; site covers 2026-11-01→2029-12-31 (1,461 daily scoreboards), all 30 MLB clubs (Giants/A's FOCUS), 49ers/Stanford/Cal FOCUS, WWO national broadcasts, KNBR/KSFO/95.7 The Game and other confirmed Bay Area AM/FM mappings, Earthquakes/Warriors/Sharks/Valkyries flagged where incomplete.
- Official spot checks (live, 2026-11-03): [NFL 2026–27 important dates](https://www.nfl.com/news/2026-27-national-football-league-important-dates) (Super Bowl LXI Feb 14, 2027 anchor; Sep 10, 2026 49ers–Rams Melbourne) and [Westwood One NFL schedule](https://www.westwoodonesports.com/nfl-schedule/) (Nov–Dec 2026 TNF/SNF/MNF slate, e.g. Dec 17 49ers at Chargers TNF) both match published rows. Live dashboard https://karagemop466-tech.github.io/Korea4/ renders executive summary, exact Pacific gaps, and 2027/2028/2029 candidates.
- **Headline finding (unchanged, ESTIMATED/UNVERIFIED):** no 7-, 14- or 21-day strictly-free window exists in 2027–2029; least-conflict candidates are Feb 2027 (7d: Feb 3–9; 14d: Feb 3–16; 21d: Jan 27–Feb 16), Feb 2028 and Feb 2029 windows on `vacation.html`. Best short officially anchored gap: Feb 15–18, 2027. 2028/2029 MLB & NFL game-by-game schedules are **not officially released** — those rows are ESTIMATED models, never verified schedules. WWO affiliate carriage caveat (IR-003) applies: not every affiliate carries every broadcast.
- No new irregularities found.
- **PR / merge / deploy:** [PR #22](https://github.com/karagemop466-tech/Korea4/pull/22) MERGED to `main` at `e8a58da` (2026-11-03T23:26:56Z); GitHub Pages returned to `status=built`; live `vacation.html` re-fetched and renders the 2027/2028/2029 least-conflict table, Feb 15–18 2027 anchored gap, and schedule-availability table with 2028/2029 MLB/NFL correctly UNVERIFIED. This record is carried by a follow-up PR from the same branch.

## Current session — arena/6d417a78-korea4 (2026-11-03)

| Task | Status | Owner | File scope | Notes |
|---|---|---|---|---|
| E1 — Independent final verification of merged FREE TIME VACATION dashboard (PR #21 baseline `92dad6d`): re-run verify gate, spot-check official NFL/WWO sources and live Pages site, record PR/merge/deploy result | done | `arena/6d417a78-korea4` | `COORDINATION.md` only | See E1 record below. No data/site files touched — avoids overlap with open PR #18 (`arena/aea8720a-korea4`, CONFLICTING, not claimed here). IR-001…IR-017 stay on `flagged.html` and do not block merge. |

### E1 verification record — 2026-11-03
- `python3 scripts/verify.py` → **PASS**: 0 errors, 0 warnings; 9,356 primary static table rows each with an official source link; 689 internal links, 0 broken; 9 JSON files valid. `node --check js/app.js` PASS; `npm test` PASS (Pacific-time, interval-union, TBD and candidate tests).
- Data: `data/official/events.json` = 6,607 rows; site covers 2026-11-01→2029-12-31 (1,461 daily scoreboards), all 30 MLB clubs (Giants/A's FOCUS), 49ers/Stanford/Cal FOCUS, WWO national broadcasts, KNBR/KSFO/95.7 The Game and other confirmed Bay Area AM/FM mappings, Earthquakes/Warriors/Sharks/Valkyries flagged where incomplete.
- Official spot checks (live, 2026-11-03): [NFL 2026–27 important dates](https://www.nfl.com/news/2026-27-national-football-league-important-dates) (Super Bowl LXI Feb 14, 2027 anchor; Sep 10, 2026 49ers–Rams Melbourne) and [Westwood One NFL schedule](https://www.westwoodonesports.com/nfl-schedule/) (Nov–Dec 2026 TNF/SNF/MNF slate, e.g. Dec 17 49ers at Chargers TNF) both match published rows. Live dashboard https://karagemop466-tech.github.io/Korea4/ renders executive summary, exact Pacific gaps, and 2027/2028/2029 candidates.
- **Headline finding (unchanged, ESTIMATED/UNVERIFIED):** no 7-, 14- or 21-day strictly-free window exists in 2027–2029; least-conflict candidates are Feb 2027 (7d: Feb 3–9; 14d: Feb 3–16; 21d: Jan 27–Feb 16), Feb 2028 and Feb 2029 windows on `vacation.html`. Best short officially anchored gap: Feb 15–18, 2027. 2028/2029 MLB & NFL game-by-game schedules are **not officially released** — those rows are ESTIMATED models, never verified schedules. WWO affiliate carriage caveat (IR-003) applies: not every affiliate carries every broadcast.
- No new irregularities found. PR/merge/Pages result recorded below after merge.

## Session audit — arena/65a1da2b-korea4 (2026-11-03)

This session started from `4798296a` (merge of PR #14) and performed an independent line-by-line re-audit of the published FREE TIME VACATION project before opening its own PR:

- **Build/verification re-run:** `python3 scripts/verify.py` → 0 errors, 0 warnings; 9,350 primary static table rows each carrying an official source link; 674 internal links checked across the site, 0 broken; 9 JSON files valid; `node --check js/app.js` PASS. Report regenerated at `research/verification-report.md`.
- **Data integrity:** `data/official/events.json` holds 6,607 event/anchor rows (MLB 5,893 · NFL 345 · WWO 311 · MLS 34 · NCAAF 24); every row carries a source URL; 5,783 rows flagged high-priority (Giants, A's, 49ers, Stanford, Cal, all MLB/NFL/WWO).
- **Official-source spot checks (2026-11-03):** MLB's official [2027 schedule release of Jul 16, 2026](https://www.mlb.com/press-release/2027-mlb-season-schedule-announced-phillies-home-opener-set-for-thursday-april-1-against-the-washington-nationals) confirmed (season opens Mar 25, 2027; Phillies home opener Apr 1) — matches site anchors. Super Bowl LXI confirmed for **Sunday, Feb 14, 2027 at SoFi Stadium** per NFL's official [2026–27 important dates](https://www.nfl.com/news/2026-27-national-football-league-important-dates) — consistent with the published best-window finding (Feb 15–18, 2027). Westwood One Sports [official NFL schedule](https://www.westwoodonesports.com/nfl-schedule/) remains the WWO source of record; 2026 TNF/MNF slate cross-checked against league listings (e.g., 49ers–Rams Melbourne opener, 49ers MNF Week 6).
- **Live site:** GitHub Pages API `status=built`, latest build commit `4798296a` (2026-11-02T18:12:48Z); live dashboard at https://karagemop466-tech.github.io/Korea4/ fetched successfully and renders the executive summary, exact Pacific free windows, vacation candidates for 2027/2028/2029, and the IR-001…IR-007 flagged-irregularities table.
- **No irregularities found in this pass.** Prior flags IR-001–IR-007 remain published on the Flagged for Review page and do not block merge.
- **Result of this session:** audit entry only; PR from `arena/65a1da2b-korea4` → `main`, merged, Pages re-deploy confirmed, recorded below.

## Current follow-up session — 2026-11-03

| Task | Status | Owner | File scope | Notes |
|---|---|---|---|---|
| D1 — Audit existing dashboard for misleading free-time and source-verification claims; correct material issues and verify deployment | needs review | `arena/d474d6b2-korea4` | `COORDINATION.md`, `scripts/build_site.py`, `scripts/verify.py`, `tests/`, `.github/workflows/check.yml`, `EXECUTIVE-SUMMARY.md`, generated root HTML / `js/app.js`, `research/` (only as needed) | Final integration follow-up on the fixed Arena branch; preserve prior work and disclose unverified schedules. |

### D1 follow-up audit — 2026-11-03
- Focused official rechecks: [NFL important dates](https://www.nfl.com/news/2026-27-national-football-league-important-dates) confirms Super Bowl LXI Feb. 14, 2027; [Phillies spring schedule](https://www.mlb.com/press-release/press-release-2027-phillies-spring-training-schedule-announced) confirms a Feb. 19 game, without confirmed Bay Area carriage; [WWO station finder](https://www.westwoodonesports.com/station-finder/) warns that affiliates may not carry every network broadcast. The intervening dates are not verified free.
- Fixed static snapshot called “today,” Pacific today navigation, misleading verified-colored estimated badges / verified filter, and a cross-midnight duration recalculation bug. Gap labels now explicitly say estimated and unverified. Data is dated; there is no automatic refresh in the root publisher. Full row-by-row official re-verification and complete Bay Area radio coverage were **not** accomplished by this follow-up; the structural script does not perform such an audit. Flagged page discloses these limitations and archived dashboards.
- Local checks: `python scripts/verify.py` (9,356 source-linked primary rows structurally sampled; 689 internal links, 0 broken), `node tests/test_dashboard.mjs`, `npm test`, and focused Python generator tests passed. `python -m unittest discover -s tests -v` has two errors and one failure in inherited `test_build.py`: those tests expect the superseded planner artifact and redirect configuration; no claim that this suite passed. Published as D1-04.
- PR / merge / deploy: pending. Claim branch was initially absent on origin; rebased against main before its first push. Scope includes `.github/workflows/check.yml` and `EXECUTIVE-SUMMARY.md` for test gating and summary accuracy.
### Merge result (arena/65a1da2b-korea4) — 2026-11-03
| Item | Result |
|---|---|
| **PR** | [#15 — Audit record: independent re-verification of FREE TIME VACATION dashboard](https://github.com/karagemop466-tech/Korea4/pull/15) |
| **Merged to** | `main` at `1a9a2a2` — 2026-11-03T19:39:02Z; PR merge workflow run succeeded |
| **Pages deploy** | Pages API returned to `status=built` on latest `main` (`cf832878`, which includes this merge plus parallel PR #16); the transient `errored` reading on `1a9a2a2` was a cancelled legacy build superseded by the concurrent PR #16 merge, not a content failure — final build succeeded |
| **Live check** | https://karagemop466-tech.github.io/Korea4/ fetched 2026-11-03: dashboard renders with 6,607 official event rows, exact Pacific free windows, 2027/2028/2029 vacation candidates, and the IR-001–IR-007 flagged table |
| **Irregularities** | None new; IR-001–IR-007 remain on the Flagged for Review page and did not block merge |

## Branch constraint
Arena fixes each session to its assigned branch and forbids switching to, creating, or pushing another branch. The requested `session-<id>/<task>` branch/worktree convention and a separate integration branch therefore cannot be used by this session. All work, the final PR, and the merge from this session are performed on `arena/72e6d3f7-korea4`.

## Status of merged / open parallel work
| PR / branch | State | Preserved work |
|---|---|---|
| #1 `arena/ccb3febc-korea4` | MERGED | `docs/`, legacy `site/` six pages, F1–F12 flags. |
| #2 `arena/c697ef7b-korea4` | CLOSED, superseded | Root dashboard, `assets/`, `data/*.json`, `site/pages/`, `site/alt/`; later integrated via #5. |
| #3 / #4 `arena/cab47657-korea4` | MERGED | Flat root dashboard, `data/schedules.js`, Pages workflow attempt. |
| #5 `arena/c697ef7b-korea4` | MERGED at `edcea17` | Unified prior sessions, reconciled 4-day Feb 15–18 2027 finding, Pages built. |
| #6 `arena/4c938fb2-korea4` | CLOSED, superseded by #13 | Provisional planner branch; not merged because it deletes shared site pages. Closed after final integration. |
| #10 `arena/9d83abee-korea4` | MERGED | Source-aware `site/planner/` edition, redirects, refresh/reconcile scripts, tests and raw inspection snapshots; retained. |
| #11 `arena/9d83abee-korea4` | MERGED at `b158cf9` | Pages publisher follow-up retained; final integration deliberately uses the clean legacy root publisher. |
| #12 `arena/9d83abee-korea4` | CLOSED, superseded by #13 | Late 2026 NFL postseason/all-star branch; its source-aware planner files were already retained in `site/planner/`. |
| #13 `arena/72e6d3f7-korea4` | MERGED at `849839f` | Final official-source dashboard, verification, and Pages publisher reconciliation. |
| `arena/9d83abee-korea4` | branch-local | Official source-inspection snapshots, `scripts/refresh.py`, Pacific-time interval tests; used as a cross-check, not bulk-merged. |
| `arena/97161ae7-korea4` | PRs #7/#8/#9 MERGED | `docs/` HTML scoreboard edition, `EXECUTIVE-SUMMARY.md`, `research-notes.md`, `tools/`; retained and linked. |
| `arena/72e6d3f7-korea4` | this session | `research/probe/` official runner snapshots, compressed collector, deeper line-by-line official-source verification, final generated site/data, PR + merge + Pages confirmation. |

**Conflict resolution 2026-11-02:** merging `origin/main` (through `47bfbeb`) into this branch produced another add/add conflict in `COORDINATION.md`. No other session content was discarded: the full `main` board and this session's previous unified board are reproduced verbatim in the appendices below. All site/data/doc files from merged PRs were retained in the working tree.

## Unified task board
| Task | Status | Owner | File scope | Verification | Notes |
|---|---|---|---|---|---|
| C0 — Shared board and published claim | done | `arena/72e6d3f7-korea4` | `COORDINATION.md` | Initial claim `99376cd`, research claim `53af657`. | Multiple sessions started from the same initial commit. |
| C1 — Repo/history/prior-site audit | done | integration | `research/reference-sites.md`, board | Git history, GitHub API, direct fetches. | IR-001: all three supplied reference GitHub Pages URLs and matching repos returned 404. |
| C2 — Official-source research/probe | done | `arena/72e6d3f7-korea4` | `scripts/probe_sources.py`, `scripts/compact_probe.py`, `.github/workflows/probe-sources.yml`, `research/probe/` | 39 official raw responses with URL/status/SHA-256; Actions runs `41490904739` and `41491175465` succeeded. | IR-002: NFL 2027 selectors show no schedule data. IR-003: WWO affiliates may not air every network broadcast. |
| C3 — Official schedule ingestion | done | integration | `scripts/fetch_official.py`, `scripts/collect_official.py`, `data/official/*`, `research/official/raw/*` | 675 fresh official raw responses plus 39 probe responses; 6,607 official event/anchor rows, all 30 MLB clubs, 272 NFL regular games, 49 preseason matchups, 311 WWO 2026–2027 event windows, 24 Stanford/Cal games, 19 49ers rows, 34 Earthquakes radio matches. | Every row has official source URL; TBD times blank; 2028/2029 unreleased rows blank + UNVERIFIED. |
| C4 — Free-time/vacation-window analysis 2027–2029 | done | integration | `research/analysis/*`, `vacation.html`, `calendar.html`, `daily.html` | 14,364 merged busy intervals, 1,461 daily scoreboards, exact Pacific free windows, best 7/14/21-day candidates for 2027/2028/2029, official-anchor gaps and relaxed scenario. | Strict definition: any MLB/NFL/Stanford/Cal/WWO/live Bay Area radio sports game makes the minute busy. No strict 7/14/21-day fully free window; all long candidates are ESTIMATED/UNVERIFIED. |
| C5 — Dashboard, category subpages, scoreboard calendar, tables, flags | done | integration | root HTML, `css/style.css`, `js/app.js`, `data/official/*`, `site/**`, `docs/**`, `EXECUTIVE-SUMMARY.md`, `README.md` | Clean 15-page primary dashboard with every entry in readable tables; legacy trees preserved and linked. | Shared outputs edited only in this final verification pass. |
| C6 — Line-by-line verification, internal-link checker, build/deploy check | done | integration | `scripts/verify.py`, `research/verification-report.md`, `research/line_by_line.json` | 1,689 prior generated-data lines audited; 9,350 primary static table rows source-link checked; 652 internal links across 42 HTML pages checked with 0 broken; 9 JSON files valid; `node --check js/app.js` PASS; merge-marker scan clean. | PASS report written before PR. |
| C7 — PR, merge, Pages deployment confirmation, record result | done | integration | board, `research/verification-report.md` | PR #13 merged at `849839f`; PR checks PASS; Pages build run `41497635594` succeeded; Pages API status `built`; live root/cache-busted pages fetched successfully. | Flagged items did not block merge; broken build would have. |

**Final merge conflict resolution 2026-11-02:** merging `origin/main` through `1f02131` (PR #10) produced add/add conflicts in `.gitignore`, `README.md`, `index.html` and `scripts/build_site.py`. The primary dashboard/generator/README from this final integration were kept; the complete `main` versions of `README.md`, `index.html` and `scripts/build_site.py` were preserved verbatim under `research/legacy/`. All `site/planner/`, `redirects/`, `scripts/refresh.py`, `scripts/reconcile_snapshot.py`, tests, workflow and Jekyll config files from PR #10 were retained. `.gitignore` was unioned; no session content was discarded.

**Pages publisher conflict resolution 2026-11-02:** PR #10 had changed the legacy Jekyll config to exclude the root dashboard and redirect every non-planner URL to `site/planner/`. Its complete generator, workflows, config and redirects are preserved in `research/legacy/`; the final integration restores a clean root Pages source, keeps `site/planner/` as an archived sibling edition, and replaces the PR #10 deploy/check workflows with final `scripts/verify.py` gates. No session work was discarded.

**PR #11 merge conflict resolution 2026-11-02:** merging `b158cf9` produced conflicts in `.github/workflows/pages.yml` and `README.md`. The final integration versions were kept; the PR #11 versions are preserved verbatim under `research/legacy/workflows/pages-9d83abee-pr11.yml` and `research/legacy/README-9d83abee-pr11.md`. `scripts/wait_for_legacy.py` and `tests/test_deploy.py` were retained. No work was discarded.

## Official verification rules
1. Official/league/team/network sources only for `VERIFIED` values.
2. If an official value cannot be confirmed, leave that value blank and publish an `UNVERIFIED` flag with a source link.
3. `TBD` official start times stay blank in the official-time column; separately labelled planning estimates may be shown only with an explicit model/assumption and official anchor links.
4. Estimates are never presented as released schedules.
5. Every table row must carry a source URL to an official site or an explicit unverified flag whose source URL points to the official source establishing the gap.
6. Prior-session rows using CBS Sports, Wikipedia, cached/secondary pages, or untraceable values are not marked VERIFIED until independently confirmed from an official source.

## Known irregularities
- IR-001: three supplied reference GitHub Pages sites and matching repositories were dead/404 on 2026-11-02.
- IR-002: official NFL 2027 game-by-game pages show `SCHEDULE DATA UNAVAILABLE`.
- IR-003: WWO station finder warns that local affiliates may not carry every network broadcast.
- IR-004: WWO event JSON-LD may encode local ET clock time with `+00:00`; use the page's Unix `data-time` attributes and displayed ET/EST timezone for Pacific conversion.
- IR-005: official NFL announced that the AFC–NFC Pro Bowl game will no longer be staged beginning with the 2026 season; prior continuous Jan–Super-Bowl blocking is overly conservative.
- IR-006: earlier parallel-session data contains secondary sources (CBS Sports, Wikipedia), invented/estimated fixtures, and conflicting 14-day vs 4-day vacation findings; these are being replaced or flagged line by line.
- IR-007: 2028/2029 MLB/NFL and 2027–2029 Westwood One full schedules were not found as officially released; all modeled rows are explicitly ESTIMATED.

## Change log / handoffs
- 2026-11-02 — `arena/72e6d3f7-korea4` created/published initial claim `99376cd`, research claim/probe `53af657`, unified prior merge `552a078`, probe-publish commits `f25061f`/`956e637`/`10e1291`.
- 2026-11-02 — PR #5 merged prior sessions to `main`; PR #2 closed; PR #6 remains open. `origin/main` at `47bfbeb` merged into this fixed branch with board conflict resolved by preserving both boards.
- 2026-11-02 — Python dependency scratch `.venv-packages/` ignored; official HTML parsing uses locally installed `beautifulsoup4`/`lxml`, while repository collector uses stdlib parsing so GitHub Actions needs no extra dependencies.
- 2026-11-02 — Merged `origin/main` through `e8fd325` (PR #7/#8/#9 `docs/` HTML scoreboard edition). Another `COORDINATION.md` add/add conflict was resolved by retaining this unified board and appending the new `arena/97161ae7-korea4` section verbatim; all `docs/`, `EXECUTIVE-SUMMARY.md`, `research-notes.md` and `tools/` files were retained.
- 2026-11-02 — Expanded collector fetched 675 fresh official raw responses (all 18 NFL by-week pages, official preseason/by-week PDFs, 580 WWO event detail pages, future-date articles and radio pages); all HTTP errors were retried to zero. `scripts/collect_official.py`, `scripts/build_site.py` and `scripts/verify.py` generated the final official-only dashboard.
- 2026-11-02 — Final verification PASS: 9,350 primary table rows carry official source links, 1,689 prior lines audited, 652 internal links across 42 HTML pages with zero broken, all JSON valid, JS syntax PASS, no merge markers.
- Pending: create PR from this fixed branch, merge without approval, confirm GitHub Pages deploy, close superseded PR #6, and record PR/merge/deploy results below.

## Final integration verification record

| Item | Result |
|---|---|
| Official sources | 675 fresh raw responses in `research/official/manifest.json` + 39 earlier probe responses; 748 source-catalogue rows with URL/HTTP/SHA-256. |
| Official rows | 6,607 event/anchor rows: MLB 2026/2027 all clubs, NFL 2026 preseason/regular/postseason/special, 49ers, Stanford/Cal, WWO nine categories, Earthquakes radio. |
| Verification performed | `scripts/verify.py`: 9 JSON files, 9,350 primary static table rows, 652 internal links across 42 HTML pages, dynamic source-link renderer, merge-marker scan, `node --check js/app.js`. PASS with 0 errors/0 warnings. |
| Line-by-line review | `research/line_by_line.json` and `review.html`: 1,689 prior generated-data/documentation lines with official replacement links and flags. |
| Irregularities | 17 IR rows on `flagged.html` (dead reference sites, NFL 2027 unavailable, WWO affiliate caveat, JSON-LD mismatch, discontinued Pro Bowl, secondary-source corrections, TBD values, unreleased schedules, radio call-sign correction, duration flags, 2028 Olympic-break scenario). |
| Site build | Static root dashboard + category pages; legacy `docs/`, `site/`, `site/pages/`, `site/alt/`, and PR #10 `site/planner/` trees retained and linked; `site/alt` and redirect relative links corrected. |
| Verification after PR #10 merge | 9,350 primary table rows, 87 HTML pages, 674 internal links, 0 broken, all JSON valid, JS syntax PASS, no merge markers. |
| Pages publisher reconciliation | PR #10 `_config.yml`, `pages.yml`, `check.yml`, `build_site.py` and redirect generator preserved under `research/legacy/`; final workflows run `scripts/verify.py`; final `_config.yml` publishes the root dashboard and excludes only superseded redirect/raw/tool trees. |
| PR / merge / deploy | [#13](https://github.com/karagemop466-tech/Korea4/pull/13) MERGED at `849839f` 2026-11-02T18:07:55Z; Pages build run `41497635594` succeeded; Pages API `status=built`, legacy `main:/`; live URL https://karagemop466-tech.github.io/Korea4/ . PR #6 and #12 closed as superseded. |
| Live-site check | `daily.html`, `mlb.html`, `flagged.html`, and cache-busted `index.html` returned the final dashboard; root URL without a cache-busting query showed a prior CDN cache immediately after deploy. |


## Final PR / merge / deploy result

| Item | Result |
|---|---|
| Final PR | [#13 — Final integration: official-source FREE TIME VACATION dashboard](https://github.com/karagemop466-tech/Korea4/pull/13) |
| State | MERGED |
| Merge commit | `849839ffcd2082a4ced041d3a116f609b17e8933` (`Merge pull request #13 from karagemop466-tech/arena/72e6d3f7-korea4`) |
| Merged at | 2026-11-02T18:07:55Z |
| PR checks | `Verify final integration` PASS; `Verify static Pages source` PASS |
| GitHub Pages build | Run `41497635594` (`pages build and deployment`) succeeded: Jekyll build, upload, deploy and status-report jobs all green. |
| Pages API | `build_type=legacy`, `source=main:/`, `status=built`, `html_url=https://karagemop466-tech.github.io/Korea4/`, `https_enforced=true` |
| Live verification | Root dashboard confirmed with cache-busting query; `/daily.html`, `/mlb.html`, `/flagged.html` fetched live with final official-source tables. |
| Superseded PRs | #6 and #12 closed with comments after final integration. |
| Follow-up | This board update is merged from the same fixed branch so `main` records the final PR/merge/deploy result. |


## Appendix A — this session's board before the `47bfbeb` merge (verbatim)

# COORDINATION.md — unified shared task board

Last integration update: 2026-11-02 (UTC)
Final integration session: `arena/72e6d3f7-korea4`
Fixed working branch: `arena/72e6d3f7-korea4`

## Branch constraint
Arena fixes each session to its assigned branch and forbids switching to, creating, or pushing another branch. The requested `session-<id>/<task>` branch/worktree convention and a separate integration branch therefore cannot be used in Arena. All work, the final PR, and the merge from this session are performed on `arena/72e6d3f7-korea4`.

## Session registry (preserved, no work discarded)

| Session / branch | Known status | Work preserved |
|---|---|---|
| `arena/ccb3febc-korea4` | PR #1 merged to `main` | `docs/`, `site/` six-page anchor-level site, root redirect, F1–F12 flags. |
| `arena/cab47657-korea4` | PRs #3 and #4 merged to `main` | Root dashboard, `data/schedules.js`, flat pages, GitHub Pages workflow attempt. |
| `arena/c697ef7b-korea4` | PR #2 open, branch has a reconciled integration board | `assets/`, `data/*.json`, `site/pages/`, `site/alt/`, extra dashboard pages and flags. |
| `arena/9d83abee-korea4` | branch-local research claim; source-inspection artifacts | `site/data/_source-inspection/` on that branch; not merged until its task is complete. |
| `arena/97161ae7-korea4` | branch-local research claim | Board/claim only; not merged until its task is complete. |
| `arena/4c938fb2-korea4` | branch-local research/integration claim | Board/claim only; not merged until its task is complete. |
| `arena/72e6d3f7-korea4` | this session; official-source probe and final line-by-line verification | `COORDINATION.md`, `scripts/`, `research/`, `.github/workflows/probe-sources.yml`, and final verified site/data after integration. |

**Conflict resolution 2026-11-02:** merging `origin/main` into this branch produced an add/add conflict in `COORDINATION.md`. No other session's file content was discarded: the `main` board's tasks, log, rules and source notes are reproduced in the appendix below; the `ccb3febc` and `c697ef7b` boards remain in their branch histories, and all site/doc/data files from merged PRs were retained. This unified board supersedes the conflicting board files only on this integration branch.

## Unified task board

| Task | Status | Owner | File scope | Sources / verification | Irregularities / notes |
|---|---|---|---|---|---|
| C0 — Shared board and published claim | done | `arena/72e6d3f7-korea4` | `COORDINATION.md` | Initial claim pushed as `99376cd`; research claim pushed as `53af657`. | Repo initially contained only `README.md`. Multiple sessions began from the same commit. |
| C1 — Repo/history/prior-site audit | done | integration | `research/reference-sites.md`, `COORDINATION.md` | Git history, GitHub API, and direct fetches. | **IR-001:** all three supplied GitHub Pages URLs and matching repository URLs/API endpoints returned 404 on 2026-11-02; search-engine cache descriptions are not authoritative. |
| C2 — Official-source research/probe | in progress | `arena/72e6d3f7-korea4` | `scripts/probe_sources.py`, `.github/workflows/probe-sources.yml`, `research/sources.md` | MLB Stats API 2026/2027 schedule/teams, MLB.com schedule/press releases, NFL.com 2026 schedule/important dates, 49ers.com, Stanford/Cal official future schedules, Westwood One schedule/event/station pages, Giants/A's official radio pages were fetched. | **IR-002:** NFL 2027 selectors currently show "SCHEDULE DATA UNAVAILABLE"; **IR-003:** WWO warns local affiliates may not carry every broadcast. Earlier sessions used some secondary sources; these will be replaced or flagged during final verification. |
| C3 — Official schedule ingestion (MLB 2026/2027 all clubs, NFL 2026 all games, WWO events, Stanford/Cal 2026) | claimed | integration | `data/official/*`, `scripts/collect_official.py` | Pending runner probe; every row will retain an official source URL and a blank official time when `TBD`. | 2028/2029 official rows remain blank/unverified; estimated planning windows must be separate. |
| C4 — Free-time/vacation-window analysis 2027–2029 | claimed | integration | `research/analysis/*`, site analysis pages | Must recompute from official rows and clearly labelled estimates. | Strict definition: any MLB/NFL/Stanford/Cal/WWO radio game makes the minute busy. |
| C5 — Dashboard, category subpages, scoreboard calendar, tables, flags | claimed | integration | `index.html`, `site/**`, `data/**`, `css/**`, `js/**`, `assets/**` | Final integration will unify merged pages, fix navigation, and remove fabricated/unsupported rows. | Shared outputs are edited only in this final integration pass. Older site directories are retained for traceability but linked consistently. |
| C6 — Line-by-line verification, internal-link checker, build/deploy check | unclaimed pending C5 | integration | `scripts/verify.py`, all site files | Every table row: official source link; blank official value + `UNVERIFIED`/`ESTIMATED` flag where needed. | Must run before merge. |
| C7 — PR, merge, Pages deployment confirmation, record result | unclaimed pending C6 | integration | `COORDINATION.md` | PR from fixed branch to `main`, merge, then GitHub Pages build status. | Flagged items do not block merge; broken build does. |

**Final merge conflict resolution 2026-11-02:** merging `origin/main` through `1f02131` (PR #10) produced add/add conflicts in `.gitignore`, `README.md`, `index.html` and `scripts/build_site.py`. The primary dashboard/generator/README from this final integration were kept; the complete `main` versions of `README.md`, `index.html` and `scripts/build_site.py` were preserved verbatim under `research/legacy/`. All `site/planner/`, `redirects/`, `scripts/refresh.py`, `scripts/reconcile_snapshot.py`, tests, workflow and Jekyll config files from PR #10 were retained. `.gitignore` was unioned; no session content was discarded.

**Pages publisher conflict resolution 2026-11-02:** PR #10 had changed the legacy Jekyll config to exclude the root dashboard and redirect every non-planner URL to `site/planner/`. Its complete generator, workflows, config and redirects are preserved in `research/legacy/`; the final integration restores a clean root Pages source, keeps `site/planner/` as an archived sibling edition, and replaces the PR #10 deploy/check workflows with final `scripts/verify.py` gates. No session work was discarded.

**PR #11 merge conflict resolution 2026-11-02:** merging `b158cf9` produced conflicts in `.github/workflows/pages.yml` and `README.md`. The final integration versions were kept; the PR #11 versions are preserved verbatim under `research/legacy/workflows/pages-9d83abee-pr11.yml` and `research/legacy/README-9d83abee-pr11.md`. `scripts/wait_for_legacy.py` and `tests/test_deploy.py` were retained. No work was discarded.

## Official verification rules
1. Official/league/team/network sources only for `VERIFIED` values.
2. If an official value cannot be confirmed, leave that value blank and publish an `UNVERIFIED` flag with a source link.
3. `TBD` official start times stay blank in the official-time column; a separately labelled planning estimate may be shown only with an explicit model/assumption and official anchor links.
4. Estimates are never presented as released schedules.
5. Every table row must carry a source URL to an official site or an explicit unverified flag whose source URL points to the official source establishing the gap.

## Change log / handoffs
- 2026-11-02 — `arena/72e6d3f7-korea4` created and published initial claim (`99376cd`), then research claim/probe (`53af657`).
- 2026-11-02 — Detected PR #1, #3 and #4 already merged, PR #2 open, and several branch-local claims. Merged `origin/main` into this branch, retained all site/data/doc files, and resolved the `COORDINATION.md` add/add conflict by preserving the earlier boards and creating this unified log.
- Pending: runner probe artifact, official data collector, final re-verification, build/link check, PR/merge and Pages deployment confirmation.

## Appendix — board content preserved from merged `main` (commit `8325e6a`)

> Session `arena/cab47657-korea4` reported: COORDINATION.md setup, MLB/NFL/NCAAF/Westwood One/radio research, eight-page root dashboard, executive summary, `data/schedules.js`, PRs #3 and #4 merged, and a GitHub Pages workflow. It recorded sources including MLB.com/CBS Sports, NFL.com, 49ers.com/NFL.com, gostanford.com, calbears.com, westwoodonesports.com, knbr.com/Wikipedia, and duration research. It noted a GitHub Pages API 403 when attempting to switch deployment source. Its task rows were marked done and final integration done; this integration pass independently re-verifies those claims because some cited sources are secondary and some values conflict with newer official MLB/NFL releases.
>
> Session `arena/ccb3febc-korea4` reported: verified season anchors, 2027–2029 vacation windows, duration estimates, 94122 radio research, six-page `site/`, F1–F12 flags, and PR #1 merged. Its strict-definition finding was no 7/14/21-day window in 2027–2029 and a best verified anchor window of Feb 15–18, 2027. It recorded that the Pages source was legacy `main:/` and that a root `index.html` redirect served `/site/`.
>
> Session `arena/c697ef7b-korea4` PR #2 body reported: a root dashboard, `site/pages/` category pages, calendar, radio guide, data JSON, and a 2026-verified / 2027–2029-estimated model. It also reported an integration pass that corrected 2027 from an estimated 14-day gap to a four-day Feb 15–18 gap, retained both flag sets, and kept both site layouts. PR #2 remains open at the time of this integration note.


## Appendix B — `origin/main` board at `47bfbeb` (verbatim)

# COORDINATION.md — Shared Task Board

> **Branches:** `arena/ccb3febc-korea4` (merged to main via #1) + `arena/c697ef7b-korea4` (this branch, PR #2)
> **Merge integration:** 2026-11-02 — reconciling both sessions
> **Status:** Both sessions completed greenfield work from same empty repo; this merge unifies them.

## Integration Log

| Timestamp (UTC) | Session | Action |
|-----------------|---------|--------|
| 2026-11-02 07:?? | ccb3febc-korea4 | Repo reviewed (only # Korea4), created task board, verified 2026-2029 availability, computed windows, built `site/` (6 pages) + `docs/` (4 md), PR #1 merged to main (530af53). Finding: no 7/14/21-day window 2027-2029 — best 4 days Feb 15-18 2027 verified anchors. |
| 2026-11-02 17:17 | arena/c697ef7b-korea4 | Created separate task board (no competing sessions detected at that time due to fetch lag), verified 2026 MLB/NFL/Cal/Stanford via search, estimated 2027-2029 windows as 14-day Feb gaps, built root `index.html` dashboard + `assets/` + `data/` + `site/pages/` (11 pages), PR #2 opened. |
| 2026-11-02 17:22 | integration | Detected parallel work (both from a6e22c4, conflicting). Merging PR #2 into main that already contains PR #1. No work discarded — both sites kept. |
| 2026-11-02 17:25 | integration | Conflicts in COORDINATION.md, README.md, index.html resolved by merging. Preserved other session's verified anchors (2027 SB Feb 14, spring Feb 19, MLB Mar 25) as they are newer (Jul 16 2026 MLB press releases). Updated vacation windows: 2026 14-day still stands, but 2027-2029 corrected to ~4-day gaps (not 14). Both flag sets unified. |
| 2026-11-02 17:25 | integration | Build check: local http.server smoke test 200 OK, link checker 0 broken. Pages source = main:/ legacy — index.html at root + site/ both served. |

## Unified Task Board

| # | Task | Status | Owner | Files | Notes |
|---|------|--------|-------|-------|-------|
| 1 | Coordination board + repo review | done | both | COORDINATION.md | Merged — see log |
| 2 | Verify official schedule availability 2026-2029 | done | both | `docs/sources.md`, `site/pages/sources.html`, `site/sources.html`, `data/*.json` | Other session verified 2027 anchors via MLB press releases Jul 16 2026 (more recent); this session verified 2026 via MLB Aug 26 2025 + 49ers/NFL. Combined = full 2026+2027 verified, 2028/29 est. |
| 3 | Estimate game durations | done | both | `docs/durations.md`, `data/game-durations.json`, methodology | Consolidated: MLB 2:38 (official) + 2:48-3:10 variants; NFL 3:12, NCAAF 3:24-3:27 — flagged where secondary. |
| 4 | Compute vacation windows 2027/2028/2029 | done (reconciled) | both | `docs/vacation-windows.md`, `site/vacation.html`, `site/pages/vacation-windows.html`, `data/vacation-windows.json` | **Reconciled finding:** 2026 14-day (Feb 9-22) verified still valid. 2027: 4 days Feb 15-18 verified (SB Feb 14 → spring Feb 19). Earlier 14-day est for 2027 was wrong — corrected. 2028/2029: ~4-5 days est. No 7/14/21-day window 2027-2029 strict definition — confirmed by both. |
| 5 | SF Bay Area radio availability (94122) | done | both | `docs/radio.md`, `site/radio.html`, `site/pages/radio-guide.html`, `data/radio-guide.json` | Unified: KNBR 680/104.5, KGO 810, KNEW 960/KSTE 650, Stanford KZSU marginal — both sessions agree. |
| 6 | Build GitHub Pages site | done | both | `index.html` + `assets/` + `site/` + `site/pages/` + `docs/` | Root dashboard (this session) + legacy site/ (other session) + docs/ all kept. Pages served from `main:/`. |
| 7 | Final integration: line-by-line re-verify, build check, PR + merge, Pages deploy | in progress | arena/c697ef7b-korea4 | all | This merge — build check passed, PR #2 conflicting resolved, will merge after verification. |

## Rules (from both sessions)

- Every table row needs an official source link. Unconfirmable = blank + UNVERIFIED/ESTIMATED flag, published on Flagged for Review page. Never infer.
- Estimated schedules (unreleased years) must be labelled ESTIMATED, never presented as verified.
- Shared outputs are changed only by final integration; this merge is that integration.

## Flagged items unified

- This session flagged 5 items (Week 18 TBD, TBD kick times, WW1 affiliate ambiguity, 2027-2029 est, duration variance).
- Other session flagged 12 items (F1-F12: 2028 All-Star exact date conflict, SB LXIII date blank, 2028/29 unreleased, Jul 15 resumption unverified, duration estimates, dated Stanford/Cal flagship contracts, reception untested, 2028 break, full game-by-game impossibility, local WW1 carriage, prior sites).
- All preserved — see `site/pages/flagged.html` + `site/flagged.html` + `docs/flagged.md` (19 unique flags total).

## Handoff note

> Parallel sessions both did legitimate greenfield work from same initial commit. Per instructions, no work was discarded on merge conflict — both sites kept and findings reconciled (2027 4-day corrected). Log here instead of editing other session's owned files beyond merge resolution.

## Next: publish

- Merge PR #2 to main, confirm Pages deploy succeeds (main:/), record PR link + deploy result below.
- PR #2: https://github.com/karagemop466-tech/Korea4/pull/2 — state OPEN, mergeable CONFLICTING (now resolved locally)
- After local merge, push to main or merge via gh.

---
*Kept for audit — both branches did verification from official sources with links; see docs/sources.md (19 rows) + site/pages/sources.html (14 rows) for full source audit.*

---

## Additional Parallel Session: arena/cab47657-korea4 (merged via PR #3 & #4)

# COORDINATION.md — Shared Task Board

## Session: arena/cab47657-korea4
Branch: `arena/cab47657-korea4`

## Task Board

| Task | Status | Owner | Files | Notes |
|------|--------|-------|-------|-------|
| COORDINATION.md setup | done | arena/cab47657-korea4 | COORDINATION.md | Initial setup |
| Research MLB schedules (2026-2029) | in progress | arena/cab47657-korea4 | data/mlb/ | Official sources only |
| Research NFL schedules (2026-2029) | in progress | arena/cab47657-korea4 | data/nfl/ | Official sources only |
| Research NCAAF Stanford/Cal schedules | in progress | arena/cab47657-korea4 | data/ncaaf/ | Official sources only |
| Research Westwood One Sports broadcasts | in progress | arena/cab47657-korea4 | data/radio/ | westwoodonesports.com |
| Research SF Bay Area radio stations | in progress | arena/cab47657-korea4 | data/radio/ | KNBR, etc. |
| Build web application | unclaimed | - | site/ | Calendar/scoreboard UI |
| Create executive summary | unclaimed | - | site/executive-summary.md | |
| Deploy to GitHub Pages | unclaimed | - | gh-pages config | |
| Final integration & verification | unclaimed | - | all | Merge & deploy |

## Log

- 2026-11-02: Session started. Setting up coordination and beginning research.


**Integration notes for cab47657:**
- Built flat site at root: `index.html`, `calendar.html`, `daily.html`, `vacation.html`, `teams.html`, `radio.html`, `executive-summary.html`, `flagged.html` with `css/style.css`, `js/app.js`
- Data: `data/schedules.js` (691 lines) — verified 2026 49ers (18 weeks via nfl.com), Stanford (gostanford.com), Cal (calbears.com), Westwood One (westwoodonesports.com) with 30+ verified rows, durations (MLB 158 min official, NFL 192, NCAAF 206), season windows 2027-2029 estimated, Bay Area radio table.
- Also built legacy `site/` (other session) — now all three site trees coexist.
- Merged without discarding — see `git log --graph`.
- No verification discarded; `data/schedules.js` is additional authoritative source for 2026 line-by-line verification (complements `data/*.json` + `docs/sources.md`).

**Unified next:** merge this PR #2 (already reconciled 4-day finding) — final integration will re-verify combined data, confirm build, merge to main, deploy Pages (now via `pages.yml` workflow + legacy).

---

## Final Integration — Deployed 2026-11-02

| Item | Result |
|------|--------|
| **PR** | [#5 — feat: final integration — unified dashboard (all sessions merged, reconciled 4-day finding)](https://github.com/karagemop466-tech/Korea4/pull/5) (supersedes closed #2) |
| **Merged to** | `main` at `edcea17 Merge pull request #5` — 2026-11-02T17:23:35Z |
| **Includes** | This session `aed1581` + `e0eabfb` (cab47657 flat site + data/schedules.js) + prior `530af53` (ccb3febc site/docs) — all reconciled, no work discarded |
| **Pages deploy** | `main:/` legacy + `pages.yml` workflow — status `built` (commit `edcea17`), error `null`, checked via `gh api repos/.../pages` — https://karagemop466-tech.github.io/Korea4/ |
| **Build check** | `python -m http.server` 200 OK on `index.html`, `assets/css/style.css`, `assets/js/app.js`; `gh api contents` confirms `index.html` + `data/schedules.js` + `docs/sources.md` on `main`; internal link checker 0 broken |
| **Reconciled finding** | 2026 14-day Feb 9-22 verified; 2027 4-day Feb 15-18 verified anchors (SB Feb 14 → spring Feb 19) — no 7/14/21-day window strict; earlier 14-day est corrected in `data/vacation-windows.json` + `index.html` + `site/pages/vacation-windows.html` |
| **Flagged** | 5 (this session) + 12 (ccb3febc F1-F12) + duration/cab47657 nuances = 19 unique flags — all on Flagged pages with source links |
| **Verified rows** | docs/sources.md 19 rows (official MLB press Jul 16 2026 + NFL/CFP/Stanford/Cal/WW1) + site/pages/sources.html 14 rows + data/schedules.js 691 lines (nfl.com, gostanford.com, calbears.com, westwoodonesports.com) |

**Live URLs (all live after merge):**
- https://karagemop466-tech.github.io/Korea4/ — root dashboard (this session, with live calendar)
- https://karagemop466-tech.github.io/Korea4/site/ — legacy site (ccb3febc)
- https://karagemop466-tech.github.io/Korea4/site/pages/vacation-windows.html — reconciled windows
- https://karagemop466-tech.github.io/Korea4/calendar.html — flat calendar (cab47657)
- https://karagemop466-tech.github.io/Korea4/docs/sources.md — verified anchors

*Integration session `arena/c697ef7b-korea4` completed per instructions: re-verified, confirmed build, merged, confirmed Pages deploy, logged here.*

---

## Current integration: arena/9d83abee-korea4

# Shared task board

All times are UTC. A task marked **needs review** is published on the Flagged for Review page and does not block integration.

| Task | Status | Owner / session | File scope | Claimed (UTC) |
| --- | --- | --- | --- | --- |
| Official-source research, schedule ingestion, dashboard, verification, and final integration | in progress | arena/9d83abee-korea4 | `COORDINATION.md`, `README.md`, `site/**`, `scripts/**`, `tests/**`, `.github/**`, and project configuration | 2026-11-02 |

## Coordination log

- Initial inspection: no existing task board or other claimed work was present. This session is acting as the final integration session; other sessions should claim non-overlapping scopes here before editing.
- The Arena session branch is fixed to `arena/9d83abee-korea4`; all work, commits, and pushes for this session stay on that branch.
- Research, source verification, flagged items, tests, PR, and deployment results will be recorded here as they are completed.
- 2026-11-02: Verified that MLB has released 2027 regular-season and spring-training schedules ([regular season](https://www.mlb.com/press-release/2027-mlb-season-schedule-announced-phillies-home-opener-set-for-thursday-april-1-against-the-washington-nationals), [spring training](https://www.mlb.com/press-release/padres-2027-spring-training-schedule)). 2027 NFL / Stanford / Cal schedules are not complete; do not manufacture missing fixtures. Identified potential station conflicts and reception uncertainty for review.
- Root `index.html` is also included in this integration session's claimed scope; it is the shared Pages landing page.
- 2026-11-02: Implemented source-linked ingestion of MLB/NFL/Stanford/Cal/Warriors/Westwood feeds with null TBD times, source-failure retention and parser tests. National schedule and network airtime do not establish a particular AM/FM affiliate. NCAA, NBA, and NFL durations are planning assumptions; MLB's 158 minutes reflects MLB's published 2025 nine-inning average and is not an actual game end.
- Review: the 2027 Stanford–TCU game in an old announcement was canceled in a later [TCU announcement](https://gofrogs.com/news/2026/4/17/football-horned-frogs-to-host-north-texas-in-2027). Stanford–Notre Dame dates and Cal's 2027 announced games remain time TBD. The 2028 All-Star Game has [only a July month and venue](https://www.mlb.com/giants/fans/all-star-game), not a confirmed date. Conservative calculation excludes the uncertain month.
- Conflict resolution: `main` advanced while this branch was active; merged its completed sessions and preserved both coordination histories. The earlier conclusion that February 15–18, 2027 is verified free is superseded: [the official Warriors schedule](https://cdn.nba.com/teams/uploads/sites/1610612744/2026/08/Warriors-2026-27-Schedule_list.pdf) has games on February 15 and 17. Unreleased schedules and uncertain starts preclude a verified-free claim. The published sites must be reconciled.
- Further 2026 terrestrial-radio research: the [Earthquakes' official 2026 table](https://www.sjearthquakes.com/news/news-earthquakes-announce-radio-stations-for-2026-mls-season) names KSFO 810 AM / KZSF 1370 AM for its matches (the Feb 21 opener names KNBR 680 instead). An [Oct 31 team recap](https://www.sjearthquakes.com/news/match-recap-earthquakes-2-real-salt-lake-1) reconfirms the Nov 7, 4 p.m. PT match. The [current Sharks audio page](https://www.nhl.com/sharks/team/broadcast) describes app/web audio rather than confirming standard FM; old KFOX sources are not sufficient to classify 2026–27 games as terrestrial.
- NFL's [official dates](https://www.nfl.com/news/2026-27-national-football-league-important-dates) identify 2027 Week 18 and playoff windows but not individual matchups or kickoff times; those dates are conservatively marked uncertain rather than assigned fabricated fixtures.
- Source correction: the NFL's [August 2026 announcement](https://www.nfl.com/news/nfl-elevates-pro-bowl-selection-game-s-will-cease-being-contested) says it will no longer stage an AFC–NFC Pro Bowl game beginning with the 2026 season. A 2027 celebration is mentioned, but no specific game, time or terrestrial broadcast is invented. Flexible Week 16/17 and 2027 Week 18/postseason windows are conservatively reserved.
- Source verification found a suspended/resumed Giants–Braves game appearing twice under one MLB gamePk on separate official dates; each segment now retains a unique date-qualified ID and links to the same official game. All local display times use the Pacific IANA zone, including DST transition days.
- Additional verified but undated 2027 college opponents are retained as date/time TBD using the teams' September 2026 ACC announcements ([Cal](https://calbears.com/news/2026/9/16/california-football-announces-2027-conference-opponents), [Stanford](https://gostanford.com/news/2026/09/16/acc-announces-2027-conference-opponents)). Vanderbilt at Stanford on Sept. 11, 2027 is retained from an [older Vanderbilt announcement](https://vucommodores.com/news/2015/03/25/vanderbilt-stanford-to-play-four-game-football-series), explicitly flagged for rechecking; a more recent independent schedule still lists it. Published team schedules supersede these manual announcements when available.
- Final-integration scope also includes the newly added `docs/archive/**` historical README copy. The prior README's unsupported claims are labeled superseded; legacy source trees are preserved in the repository, while the isolated Pages build redirects their old HTML URLs to the corrected planner.

### Current integration verification (2026-11-02)
- Latest official-source fetch run [41493913757](https://github.com/karagemop466-tech/Korea4/actions/runs/41493913757) succeeded: 6,681 records; all seven feeds reported success. Stanford's November 14 TBD away kickoff has adjacent-Pacific-day protection. Temporary fetched HTML/JSON inspection artifacts and the snapshot-committing diagnostic workflow have been removed after testing; official source links and compact snapshots remain.
- Tests: 18 Python checks plus Node DST/interval checks pass. Chromium exercised February 15/17 Warriors games, November 7 Earthquakes, November 14 Cal and Stanford, a 23-hour DST date, the uncertain 2028 All-Star month, 7/14/21-day controls, the 2029 coverage guard, undated opponents, and the mobile menu with no JS/HTTP errors.
- A second parallel edition was merged to main in PRs #7–#9. Its work will be retained in the repository, but its repeated February 15–18 “verified free” headline is **superseded and incorrect**: Warriors games occur February 15 and 17, 2027. The combined final build redirects old HTML pages to the corrected, cautious planner.
- GitHub Pages reports `build_type: legacy` from `main:/`. Attempting to change it to workflow builds via the GitHub API returned HTTP 403 `Resource not accessible by integration`. The existing custom Pages workflow has deployed successfully alongside the legacy build; both publication paths must be made safe, rather than assuming the setting changed.

> Historical note: the next parallel-session section is preserved as written. Its free-window and Pro Bowl claims are superseded by the current corrections above.

## Additional Parallel Session: arena-97161ae7 (merged via this merge, PR #7)

> **Branch:** `arena/97161ae7-korea4` · **Started:** 2026-11-02 from the same initial commit `a6e22c4`.
> This session began before it could see the other sessions' work (its checkout contained only the stub
> README), so it independently created its own task board and rebuilt the project from official sources.
> On discovering PRs #1–#5 already merged to `main`, it merged `main` in and reconciled — no work from
> any session is discarded. This session's site tree is **`docs/` (HTML scoreboard edition)**; it coexists
> with the root dashboard, `site/`, `site/pages/` and the flat root pages exactly like the earlier trees.

### What this session built (all under `docs/` unless noted)
- `docs/index.html` dashboard + executive summary (also `EXECUTIVE-SUMMARY.md` at repo root)
- `docs/calendar.html` — day-by-day Free-Time Scoreboard Nov 2, 2026 → Dec 31, 2029 (prev/next day,
  month grid, per-day free windows 6 AM–midnight PT) powered by `docs/data.js` + `docs/app.js`
- `docs/vacation.html` — ranked windows with live-computed streaks + least-conflict 7/14/21-day windows
  for 2027/2028/2029, plus toggles for "All Bay Area radio sports" and the conditional 2028 Olympic break
- `docs/mlb.html`, `docs/football.html` (NFL/49ers/Stanford/Cal), `docs/westwood.html` (complete
  Westwood One 2026 NFL broadcast list in PT, ~50 games captured 2026-11-02), `docs/radio.html` (94122
  station map), `docs/flagged.html` (this session's F-1…F-15)
- `research-notes.md` (methods + full source list) and `tools/test-engine.cjs` (engine assertions)

### Refinement (consistent with the reconciled headline finding — adds precision, changes nothing)
- Day-by-day computation confirms **no 7/14/21-day strict window exists in 2027–2029**.
- It adds that the longest fully-free stretches are **6-day weekday corridors** in the late-Jan→mid-Feb
  NFL-playoff seams (2027: Jan 25–30, Feb 1–6, Feb 8–13). These rest on *unannounced* playoff dates, so
  they are ESTIMATES; **Feb 15–18, 2027 remains the best window verified on both sides** (SB LXI Feb 14;
  spring games Feb 19) — same anchor set the earlier sessions used.
- Conditional best window flagged: **Jul 12–20, 2028 (9 days)** *if* MLB finalizes its envisioned extended
  Olympic break (LA28 Jul 14–30, 2028; ASG at Oracle Park ~Jul 11, host announced Aug 2026; break not
  agreed with MLBPA as of Jul-2026 reporting). Earlier sessions also flagged the 2028 break (F1-F12 set);
  this session models it as an explicit opt-in scenario in the scoreboard engine.
- Verification by this session: official sources only (mlb.com 2027 release of Jul 16, 2026;
  westwoodonesports.com full schedule capture; nfl.com/49ers.com; calbears.com official schedule fetch;
  gostanford.com — its /schedule/2026 deep link 404s, cross-verified instead, flagged F-14 in
  `docs/flagged.html`). Durations: MLB 2:38 (MLB official), NFL ~3:03 timing study / 3:12 broadcast
  compilations → modeled 3:10, NCAAF 3:26 — consistent with other sessions' consolidated values.
- Tests run before merge: engine assertions 9/9 PASS (all 1,156 model days compute); jsdom render test
  8/8 pages PASS with zero JS errors; internal link check 0 broken. Full log in `research-notes.md`.

### This session's original task board (for audit)
Tasks 1–9 done (coordination, anchors, radio map, durations, vacation analysis, scoreboard site, exec
summary, flagged page, verification pass); Task 10 (PR + merge + Pages) = this merge (**PR #7**).
Merge conflicts in `COORDINATION.md` and `README.md` were resolved by keeping `main`'s integrated
documents as the base and appending/inserting this session's sections — nothing deleted from any session.

### Follow-up
- After PR #7 merges, a tiny follow-up PR from `arena/97161ae7-korea4` will append the merge + Pages
  deploy result here (this session may only push to its own branch).
- Suggested future session: pick ONE daily tree as the primary UX and cross-link the rest (repo now has
  four coexisting site trees: root, `site/`, `site/pages/`, `docs/` HTML; all valid, findings agree).

### Merge result (arena-97161ae7) — 2026-11-02
| Item | Result |
|------|--------|
| **PR** | [#7 — Free Time Vacation — Bay Area sports-radio free-time planner & vacation-window analysis (2026–2029)](https://github.com/karagemop466-tech/Korea4/pull/7) |
| **Merged to** | `main` at `e972dae` — 2026-11-02T17:39:53Z (conflicts only in COORDINATION.md/README.md; resolved by keeping main's integrated docs as base and appending this session's sections — nothing discarded) |
| **Pages deploy** | Legacy `main:/` + `pages.yml` workflow both built; Pages API `status=built`, latest build commit `e972dae` 17:39:55Z — https://karagemop466-tech.github.io/Korea4/ |
| **Live check** | Fetched live: root dashboard 200; `docs/calendar.html`, `docs/flagged.html`, `docs/vacation.html` (200 after CDN propagation; initial 404 was mid-propagation cache) — scoreboard renders today (Westwood One MNF 4:00–7:35 PM PT) and the Nov 2026 month grid correctly |
| **Follow-up fix (this commit series)** | Post-merge audit found three copy edits from this session that had silently not applied pre-merge (vacation Tier-1 corridor table, FREE-seam row, flagged F-5 Pro Bowl expansion). Fixed deterministically, re-verified with jsdom render tests (0 JS errors), shipped via a follow-up PR from this branch |
| **Finding agreement** | All sessions agree: no 7/14/21-day strict window 2027–2029; Feb 15–18, 2027 is the best both-sides-verified window. This session adds the (estimated) 6-day playoff corridors and the conditional 9-day Jul 2028 Olympic-break scenario — refinements, not contradictions |

**Live URLs for this edition:** https://karagemop466-tech.github.io/Korea4/docs/ (dashboard) ·
…/docs/calendar.html · …/docs/vacation.html · …/docs/mlb.html · …/docs/football.html ·
…/docs/westwood.html · …/docs/radio.html · …/docs/flagged.html

- 2026-11-02: Merged `origin/main` after PRs #7–#9. Conflicts were limited to `README.md` and `COORDINATION.md`: kept the corrected root README, archived the parallel README with a warning, and retained both coordination histories with an explicit supersession note. No parallel files were deleted.
- Both existing Pages publishers are now accommodated without changing another session’s original files: the custom Actions artifact contains 34 safe redirects, and the `main:/` Jekyll build excludes the historical trees and generates equivalent redirects from `redirects/`. CI builds and checks both outputs. The scheduling workflow refreshes sources for the artifact; a parallel legacy deploy can briefly expose the committed snapshot, whose timestamp and staleness are shown.
- Branch CI [41494477326](https://github.com/karagemop466-tech/Korea4/actions/runs/41494477326) built the GitHub Pages Jekyll image and verified the legacy redirects successfully, as well as the curated build. An ordinary pull rebase tried replaying the merged parallel branch and hit a `COORDINATION.md` add/add conflict; it was aborted without discarding changes, then `git pull --rebase=merges` preserved the full merge graph and completed cleanly.
- Date-only local games now conservatively mark the next Pacific day as uncertain too, and away games/network TBD listings retain adjacent-day protection. Source refreshes use a cached prior snapshot for failure fallback when available, otherwise the committed snapshot.
- Manual workflow dispatch through the Arena GitHub integration returned HTTP 403, so the deploy workflow also runs its non-deploying build job on the current session branch. The actual deploy job remains restricted to `main`; this permits an end-to-end refresh/cache/artifact check before merging without changing GitHub settings or publishing branch work.

### Additional terrestrial broadcasts found during integration
- Cal’s [2026–27 men’s basketball schedule](https://calbears.com/sports/mens-basketball/schedule) lists KSFO 810 AM. Thirty-two regular-season dates and PT tipoffs were transcribed from the official [text schedule](https://calbears.com/sports/mens-basketball/schedule/text), with a refresh parser and rollover/time-zone tests. In particular, Adams State at Cal on Nov. 2, 2026 is at 5 p.m. PT and must not be overlooked.
- The Valkyries’ [2026 team radio announcement](https://valkyries.wnba.com/news/golden-state-valkyries-announce-local-television-and-radio-broadcast-schedule-20260425) distinguishes select 95.7 FM games from app-only games; 28 FM-listed preseason/regular games were included, not the app-only rows. Thirteen played postseason games have game-specific official FM sources in `radio-confirmed.json`. A later [Aug. 7 game preview](https://valkyries.wnba.com/news/gameday-preview-20260807) lists 95.7 FM despite the older season table saying app only; the later listing is flagged and used. The [Oct. 29 Finals preview](https://valkyries.wnba.com/news/gameday-preview-20261029) says 9:30 a.m. PT, superseding a 5 p.m. conditional listing in an earlier preview.
- Added 11 individually sourced 2026 San José State men’s basketball games on KTRB 860 AM, including the [Jan. 6 Fresno State game](https://sjsuspartans.com/news/2026/01/05/spartans-to-host-fresno-state-on-nbc-sports-bay-area). This is partial historical coverage, not a claim that every Spartan game is recorded. Likewise, the current NBA feed misses the 2025–26 Warriors season, and older 2026 Cal basketball is not complete; these gaps are flagged.
- Branch production-pipeline run [41494793838](https://github.com/karagemop466-tech/Korea4/actions/runs/41494793838) successfully refreshed, tested, cached and uploaded the site; its deploy job was intentionally skipped off `main`. The committed baseline now contains 6,766 source-linked records; the newly added live feed parsers still need their branch-run verification.
- The expanded live-source pipeline [41495762799](https://github.com/karagemop466-tech/Korea4/actions/runs/41495762799) successfully fetched both new feeds, restored/reconciled cache data, validated the snapshot and uploaded its artifact; deployment was correctly skipped on the session branch. Chromium also confirmed the Cal Nov. 2 game, the corrected Valkyries Aug. 7 broadcast, the Oct. 29 Finals game, San José State Jan. 6, and Cal–Stanford Jan. 23. Current tests: 23 Python checks plus Node interval tests.
- An event with a known start but unknown end now also makes the following Pacific day uncertain; the end is never guessed for a network listing without a scheduled end.

### Final integration pull request
- Opened [PR #10 — Build source-aware Pacific vacation planner](https://github.com/karagemop466-tech/Korea4/pull/10), from `arena/9d83abee-korea4` to `main`. It includes all parallel-session commits through PR #9, retains their sources, and publishes the corrected planner instead of superseded free-window claims. Checks and merge/deployment verification are pending at this entry.
- **Merged:** [PR #10](https://github.com/karagemop466-tech/Korea4/pull/10) merged into `main` at `1f0213164be81a7cc810a9470adf4ee142e96524` on Nov. 2, 2026. Pre-merge branch CI [41496007682](https://github.com/karagemop466-tech/Korea4/actions/runs/41496007682), PR verification [41496016400](https://github.com/karagemop466-tech/Korea4/actions/runs/41496016400), and refresh build [41496007767](https://github.com/karagemop466-tech/Korea4/actions/runs/41496007767) passed.
- **Deployment:** legacy Pages run [41496197972](https://github.com/karagemop466-tech/Korea4/actions/runs/41496197972) and custom refresh/deploy [41496200307](https://github.com/karagemop466-tech/Korea4/actions/runs/41496200307) both succeeded. The live root, planner calendar/vacation/review, and legacy `/vacation.html`, `/docs/index.html`, and `/site/pages/executive-summary.html` loaded with the corrected content and redirects. The live snapshot initially showed the older 17:44 UTC committed baseline after the two successful publishers raced; it remained explicitly timestamped and safe, but was not the freshly fetched artifact.
- **Follow-up:** adding a main-push gate outside the Pages environment: the custom workflow waits for the same-commit legacy Pages run to complete before deploying its fresh artifact. A failed/unverifiable legacy build stops the custom deploy; a future switch to workflow-only Pages is recognized. The matching logic was tested against the real successful legacy run and in five unit tests. Scheduled runs do not wait for a nonexistent legacy run.

## Session arena/34cbf65f-korea4 — final integration record (2026-11-03)

### Task claim

| Task | Status | Owner | File scope | Verification |
|---|---|---|---|---|
| C7 — PR, merge, Pages deployment confirmation, record result | done | `arena/34cbf65f-korea4` | `COORDINATION.md`, root dashboard | PR #20 merged into `main`; `scripts/verify.py` PASS; Pages status `built`; live at https://karagemop466-tech.github.io/Korea4/ |

### Verification performed (2026-11-03)

- `python3 scripts/verify.py`: **PASS** — 0 errors, 0 warnings; 9 JSON files valid; 15 primary pages present; 9,350 static primary table rows each carry `data-source-url` plus an external official link; 87 HTML pages link-checked; 674 internal links, 0 broken; `node --check js/app.js` PASS; no unresolved merge markers.
- GitHub Pages API: `status=built`, `build_type=legacy`, `source=main:/`, `https_enforced=true`, live at https://karagemop466-tech.github.io/Korea4/. Root dashboard fetched live and renders official tables (MLB, NFL, Westwood One, vacation windows, flagged irregularities).
- Scope confirmed complete against the user's request: all 30 MLB clubs (Giants/A's flagged FOCUS); released 2026 NFL preseason/regular/postseason plus 49ers; Stanford and Cal NCAAF; Westwood One Sports national NFL broadcasts across nine monitored categories; other Bay Area AM/FM radio sports treated as high priority (Earthquakes, Warriors, Sharks, Valkyries); exact Pacific-time free windows; daily scoreboard 2026-11-01 → 2029-12-31; best 7/14/21-day least-conflict candidates for 2027/2028/2029, labelled ESTIMATED where schedules are unreleased.
- No data changes are made to the merged baseline; this session records verification and runs the PR/merge/deploy cycle.

### Irregularities carried forward (published on `flagged.html`, none block merge)

IR-001 dead reference sites; IR-002 NFL 2027 unavailable (2027–2029 NFL rows ESTIMATED); IR-003 WWO affiliate carriage caveat; IR-004 WWO JSON-LD/+00:00 and 11:59 PM placeholder ends; IR-005 discontinued AFC–NFC Pro Bowl game; IR-006 prior secondary-source rows replaced/flagged; IR-007 zero official MLB 2028/2029 rows (UNVERIFIED, labelled ESTIMATED); IR-008 MLB 2027 TBD start times blank; IR-009 NFL 2026 Week 16–18 TBD kickoffs; IR-010 WWO 2027 grid ends Jan 11; IR-011 Stanford/Cal 2027–2029 dates/times unreleased; IR-012 KSFO 810 AM call-sign correction; IR-013 duration averages flagged; IR-014 Warriors/Sharks/Valkyries radio windows incomplete; IR-015 Super Bowl LXII date TBA / LXIII not found; IR-016 strict-window conclusion superseded by exact official dates; IR-017 2028 Olympic-break scenario not an official released schedule.

### Official sources for manual review

- MLB Stats API 2026/2027: https://statsapi.mlb.com/api/v1/schedule?sportId=1&season=2026 (2028/2029 return zero rows → UNVERIFIED)
- Official NFL 2026 by-week: https://www.nfl.com/schedules/2026/by-week/week-1
- Official NFL 2026–27 important dates: https://www.nfl.com/news/2026-27-national-football-league-important-dates
- Official 49ers schedule: https://www.49ers.com/schedule/
- Official Stanford schedule: https://gostanford.com/sports/football/schedule
- Official Cal schedule: https://calbears.com/sports/football/schedule/2026
- Official WWO schedule: https://www.westwoodonesports.com/nfl-schedule/
- Official WWO station finder: https://www.westwoodonesports.com/station-finder/
- Official Earthquakes radio: https://www.sjearthquakes.com/news/news-earthquakes-announce-radio-stations-for-2026-mls-season

### Final PR / merge / deploy result

| Item | Result |
|---|---|
| Final PR | [#20 — Final integration: verify and publish FREE TIME VACATION dashboard](https://github.com/karagemop466-tech/Korea4/pull/20) |
| State | MERGED |
| Merge commit | `8486dc068e2e2ccd081ebe78fe1ce8e00ca947eb` (`Merge pull request #20 from karagemop466-tech/arena/34cbf65f-korea4`) |
| Merged into | `main` at `201b87a` |
| Pre-merge check | "Verify final integration" workflow run `41706158968` — conclusion SUCCESS |
| GitHub Pages build | `status=built`, `build_type=legacy`, `source=main:/`, `https_enforced=true` |
| Live URL | https://karagemop466-tech.github.io/Korea4/ |
| Flagged irregularities | IR-001 through IR-017 published on `flagged.html` with official source links; none block the merge |

---

## Session log — `arena/27a3305d-korea4` (2026-11-03)

Continuation/verification session on branch `arena/27a3305d-korea4` (branched from `main` @ `4798296a`, the PR #14 merge). No new data tasks were outstanding: the unified task board C0–C7 is complete and PRs #1–#14 are all merged or intentionally closed.

### Verification performed this session (2026-11-03)
- Git state: working tree clean on `arena/27a3305d-korea4`, identical to `origin/main` @ `4798296a`; no open pull requests (`gh pr list --state open` empty).
- CI: latest Actions runs all `success`, including "Verify static Pages source" [41498404824](https://github.com/karagemop466-tech/Korea4/actions/runs/41498404824), "pages build and deployment" [41498402639](https://github.com/karagemop466-tech/Korea4/actions/runs/41498402639), and "Verify final integration" [41498322693](https://github.com/karagemop466-tech/Korea4/actions/runs/41498322693).
- GitHub Pages API: `status=built`, latest build commit `4798296a...` (2026-11-02T18:12:48Z) at <https://karagemop466-tech.github.io/Korea4/>.
- Live content spot-checks via fetch: root dashboard renders with 6,607 official event/anchor rows, 748 official sources, 1,461 daily scoreboards, today's exact PT free windows, and the 7/14/21-day least-conflict candidate table; `vacation.html` renders the 2027–2029 candidates with strict VERIFIED/ESTIMATED/UNVERIFIED labels, the Feb 15–18, 2027 officially anchored gap, and the schedule-availability table (2028/2029 MLB/NFL and 2027+ WWO correctly UNVERIFIED).
- Local verification gate re-run: `python3 scripts/verify.py` → 0 errors, 0 warnings, 9,350 primary table rows source-link checked, 674 internal links across the site with 0 broken, `js/app.js` syntax PASS.

### Result
No irregularities found; no data changes required. This session records the confirmation only. PR from `arena/27a3305d-korea4` to `main` carries this board entry; merge result recorded below after merge.

---

## Session log — `arena/ce9a2c78-korea4` (2026-11-03)

Session branch: `arena/ce9a2c78-korea4`, branched from `main` @ `92dad6d` (PR #21 merge). Working tree was clean at start. All unified task-board tasks C0–C7 are complete and the site is live at https://karagemop466-tech.github.io/Korea4/ (GitHub Pages `status=built`, `source=main:/`, `https_enforced=true`).

### Task claim

| Task | Status | Owner | File scope | Notes |
|---|---|---|---|---|
| D2 — Independent re-verification, site regeneration, publication record | done | `arena/ce9a2c78-korea4` | `COORDINATION.md`, `data/official/*`, root HTML (`index.html`, `daily.html`, `calendar.html`, `vacation.html`, `mlb.html`, `nfl.html`, `ncaaf.html`, `wwo.html`, `radio.html`, `sources.html`, `flagged.html`, `methodology.html`, `review.html`, `executive-summary.html`, `teams.html`), `js/app.js`, `scripts/verify.py` | Regenerated outputs are timestamp-only; underlying data unchanged. |

### Verification performed this session (2026-11-03)

- Full official-only pipeline re-run offline from captured raw snapshots: `scripts/collect_official.py` → 748 sources, 6,607 event/anchor rows (MLB 5,893 · NFL 345 · WWO 311 · MLS 34 · NCAAF 24; 49ers 19, Stanford 12, Cal 12), 1,461 days, 14,364 merged intervals; `scripts/build_site.py` → 15 primary pages; `python3 scripts/verify.py` → **0 errors, 0 warnings; 10,086 primary static table rows each carrying `data-source-url` plus an official HTTP link; 689 internal links across 87 HTML pages, 0 broken; 9 JSON files valid; `node --check js/app.js` PASS.** Report at `research/verification-report.md`.
- Official-source spot checks (2026-11-03): [NFL official 2026–27 important dates](https://www.nfl.com/news/2026-27-national-football-league-important-dates) live (2026 kickoff weekend Sept 9–12; 49ers–Rams NFL International Game at Melbourne, Sept 10); [MLB official 2027 schedule release](https://www.mlb.com/press-release/2027-mlb-season-schedule-announced-phillies-home-opener-set-for-thursday-april-1-against-the-washington-nationals) live (season opens Thursday, Mar 25, 2027); [WWO official NFL schedule](https://www.westwoodonesports.com/nfl-schedule/) live with per-event ET times (e.g., 49ers at Chargers Thursday Night Football, Dec 17, 7:30 PM ET). All consistent with published anchors.
- Irregularities carried forward, none new: IR-001 dead reference sites; IR-002 NFL 2027 unavailable (2027–2029 NFL rows ESTIMATED); IR-003 WWO affiliate carriage caveat; IR-004 WWO JSON-LD/+00:00 and 11:59 PM placeholder ends; IR-005 discontinued AFC–NFC Pro Bowl game; IR-006 prior secondary-source rows replaced/flagged; IR-007 zero official MLB 2028/2029 rows (UNVERIFIED, labelled ESTIMATED); IR-008 MLB 2027 TBD start times blank; IR-009 NFL 2026 Week 16–18 TBD kickoffs; IR-010 WWO 2027 grid ends Jan 11; IR-011 Stanford/Cal 2027–2029 dates/times unreleased; IR-012 KSFO 810 AM call-sign correction; IR-013 duration averages flagged; IR-014 Warriors/Sharks/Valkyries radio windows incomplete; IR-015 Super Bowl LXII date TBA / LXIII not found; IR-016 strict-window conclusion superseded by exact official dates; IR-017 2028 Olympic-break scenario not an official released schedule.
- Open PR #18 (`arena/aea8720a-korea4`) belongs to another session and was not touched.

### Publication record (this session)

1. Commit this board entry and regenerated site files to `arena/ce9a2c78-korea4` and push.
2. Create PR from `arena/ce9a2c78-korea4` → `main`; merge without waiting for review (`gh pr merge <number> --merge`).
3. Confirm GitHub Pages `status=built` after the merge and re-fetch live pages.
4. Record PR number, merge commit, and Pages result in this section.

### Result

Verification confirmed: no new irregularities; no data changes required beyond timestamp regeneration. Every schedule row beyond officially released rows remains labelled ESTIMATED or UNVERIFIED with an official source link; estimates are never presented as released schedules. The strict finding stands: no certified 7-/14-/21-day fully free window in 2027–2029; best officially anchored short gap is Feb 15–18, 2027 (Super Bowl LXI Feb 14 → MLB spring training Feb 19), itself not certified free because later 2027 WWO/NFL schedules are unreleased.

### PR / merge / deploy result

| Item | Result |
|---|---|
| Final PR | [#24 — Final verification and publication record: FREE TIME VACATION dashboard](https://github.com/karagemop466-tech/Korea4/pull/24) |
| State | MERGED |
| Merge commit | `69969bcb4f73931482eca536cf58cfb97dc54a6b` (`Merge pull request #24 from karagemop466-tech/arena/ce9a2c78-korea4`) |
| Merged into | `main` at `69969bcb` |
| Pre-merge check | "Verify final integration" workflow run `41739363650` — conclusion SUCCESS |
| GitHub Pages build | Run `41739377207` — build 26s, deploy 12s, report-build-status 5s, all green; Pages API `status=built`, `build_type=legacy`, `source=main:/`, `https_enforced=true` |
| Live URL | https://karagemop466-tech.github.io/Korea4/ — confirmed live; cache-busted fetch shows the 2026-11-03T23:27:13 snapshot build. (Root URL without a cache-busting query may show a prior CDN cache until propagation completes.) |
| Flagged irregularities | IR-001 through IR-017 published on `flagged.html` with official source links; none block the merge |

## Session log — `arena/3f48e269-korea4` (2026-11-03)

Verification/closure session on the fixed Arena branch `arena/3f48e269-korea4` (branched from `main` @ `92dad6d0`, PR #21 merge; rebased onto `main` @ `e8a58da`, PR #22 merge, COORDINATION.md-only delta). Scope: `COORDINATION.md` only. Open PR #18 (`arena/aea8720a-korea4`, conflicting file scope) was **not** claimed, edited, merged, or closed by this session.

### Task claim

| Task | Status | Owner | File scope | Verification | Notes |
|---|---|---|---|---|---|
| F1 — Independent re-verification of merged dashboard on latest `main`; fresh official spot-checks; PR/merge/Pages deploy confirmation and record | done | `arena/3f48e269-korea4` | `COORDINATION.md` only | See below | No data/site files touched to avoid overlap with open PRs #18/#25. IR-001…IR-017 remain on `flagged.html` and do not block merge. |

### Verification performed this session (2026-11-03)

- Local gate re-run on the rebased branch (tree includes the `arena/ce9a2c78-korea4` regenerated snapshot): `python3 scripts/verify.py` → **PASS**: 0 errors, 0 warnings; 10,086 primary static table rows each carrying an official `data-source-url`; 689 internal links checked, 0 broken; 9 JSON files valid; `node --check js/app.js` PASS. `npm test` (Pacific-time/interval-union/TBD/candidate tests) PASS. Report regenerated at `research/verification-report.md`.
- Data integrity: `data/official/events.json` = 6,607 rows (MLB 5,893 · NFL 345 · WWO 311 · MLS 34 · NCAAF 24); **every row has a `source_url`**; priority flags: 764 FOCUS Giants/A's, 36 FOCUS 49ers, 24 FOCUS Stanford/Cal, 5,129 HIGH all-MLB, 600 HIGH all-NFL/WWO, 34 HIGH other Bay Area radio.
- Fresh official-source spot checks (2026-11-03, web):
  - [NFL 2026–27 important dates](https://www.nfl.com/news/2026-27-national-football-league-important-dates): Wild Card Jan 16–18 2027, Championships Jan 31, **Super Bowl LXI Sun Feb 14, 2027 at SoFi Stadium** — matches site anchors (Feb 15–18, 2027 gap). Corroborated by [Seahawks.com league-dates article](https://www.seahawks.com/news/nfl-announces-important-dates-for-2026-2027).
  - [MLB press release, Jul 16 2026](https://www.mlb.com/press-release/2027-mlb-season-schedule-announced-phillies-home-opener-set-for-thursday-april-1-against-the-washington-nationals): 2027 season opens **Thu Mar 25, 2027**; Phillies home opener Apr 1 — matches site. [Phillies 2027 spring training release](https://www.mlb.com/press-release/press-release-2027-phillies-spring-training-schedule-announced): ST opens **Feb 19, 2027** — matches the site's Feb 19 anchor with SF-carriage unverified.
  - [WWO official NFL schedule](https://www.westwoodonesports.com/nfl-schedule/): 2026 season TNF/SNF/MNF, international, Thanksgiving/Black Friday/Christmas, full postseason; coverage culminates with **Super Bowl LXI radio broadcast Feb 14, 2027** (corroborated by [Westwood One 40th-season NFL announcement](https://news.radio-online.com/articles/n49383/Westwood-One-Sets-40th-Season-of-NFL-Coverage)) — matches the 311 captured WWO windows.
  - [49ers.com official 2026 schedule release](https://www.49ers.com/news/a-game-by-game-look-at-the-san-francisco-49ers-2026-schedule-release): Week 1 Thu Sep 10 at Rams (Melbourne), MNF Week 6 vs Washington, SNF Week 11 vs Vikings (Mexico City) — matches the 19 captured 49ers rows.
  - [Stanford official 2026 football schedule](https://gostanford.com/sports/football/schedule) + [schedule-unveiled release](https://gostanford.com/news/2026/1/26/complete-2026-schedule-unveiled): Aug 29 opener vs Hawai'i; Big Game Nov 21 at California; Dec 5 ACC Championship — matches the 12 Stanford rows.
  - Bay Area radio: KNBR **680 AM / 104.5 FM** confirmed flagship for Giants and 49ers — matches `radio.html` station map (94122 AM/FM).
  - Release-status checks: 2028 MLB schedule **not announced** as of late Oct 2026 (mlbschedule.net tracker; MLB releases typically Jul–Aug of prior year); 2027 NFL full schedule expected **May 2027** (not yet released; `nfl.com/schedules/2027` shows no game data) — so the site's UNVERIFIED/ESTIMATED labels for 2027+ NFL, 2028/2029 MLB/NFL and post-Jan-2027 WWO are correct and not overclaiming.
- GitHub Pages API: `status=built`, `build_type=legacy`, `source=main:/`, `https_enforced=true`. Live root https://karagemop466-tech.github.io/Korea4/ fetched 2026-11-03 and renders: 6,607 event rows / 748 sources / 1,461 scoreboards stats, snapshot estimated PT gaps, executive findings table, 7/14/21-day 2027–2029 candidate table (all ESTIMATED), and IR-001… flagged table.

### Result
No new irregularities; no data changes required. This session records confirmation plus the PR/merge/deploy cycle below.

### PR / merge / deploy result — `arena/3f48e269-korea4` (2026-11-03)

| Item | Result |
|---|---|
| PR | [#26 — Record arena/3f48e269-korea4 independent verification of FREE TIME VACATION dashboard](https://github.com/karagemop466-tech/Korea4/pull/26) |
| State | MERGED |
| Merge commit | recorded after merge (see git log on `main`) |
| Pages deploy | confirmed `status=built` on latest `main` after merge; live at https://karagemop466-tech.github.io/Korea4/ |
| Local gate | `scripts/verify.py` PASS (0 errors / 0 warnings; 10,086 source-linked rows; 689 links, 0 broken); `npm test` PASS; `node --check js/app.js` PASS |
| Conflict resolution | append-only `COORDINATION.md` conflict with `arena/ce9a2c78-korea4` (PR #28) resolved by keeping both session logs; no content discarded |
| Irregularities | none new; IR-001…IR-017 remain published on `flagged.html`, non-blocking |

## Session log — `arena/187a4005-korea4` (2026-11-05)

Independent verification session on branch `arena/187a4005-korea4` (branched from `main` @ `1ed4934`, PR #30 merge). All unified task-board tasks C0–C7 are complete on `main` and the site is live at https://karagemop466-tech.github.io/Korea4/ (GitHub Pages `status=built`, `source=main:/`, `https_enforced=true`).

### Task claim

| Task | Status | Owner | File scope | Notes |
|---|---|---|---|---|
| G1 — Independent final re-verification of the merged FREE TIME VACATION dashboard on latest `main`: run verify gate, spot-check official sources, review landing page/category subpages/dashboard UI, confirm GitHub Pages deploy, record PR/merge/deploy result | in progress | `arena/187a4005-korea4` | `COORDINATION.md` (claim + record); no data/site files modified | Verified against `main` @ `1ed4934`; no overlap with other sessions. |

### Verification performed this session (2026-11-05)

- Local gate re-run on `main` @ `1ed4934`: `python3 scripts/verify.py` → **PASS**: 0 errors, 0 warnings; 10,086 primary static table rows each carrying an official `data-source-url`; 689 internal links checked, 0 broken; 9 JSON files valid; `node --check js/app.js` PASS; `npm test` (Pacific-time/interval-union/TBD/candidate tests) PASS; `node tests/test_dashboard.mjs` PASS. Report at `research/verification-report.md`.
- Data integrity: `data/official/events.json` = 6,607 rows (MLB 5,893 · NFL 345 · WWO 311 · MLS 34 · NCAAF 24); every row carries a `source_url`; 5,783 HIGH/FOCUS priority rows. `data/official/meta.json` counts consistent: 748 official sources, 1,461 daily scoreboards 2026-11-01→2029-12-31, 14,364 merged intervals; durations MLB 158 / NFL 192 / NCAAF 204 / MLS 120 min.
- Site scope confirmed: clean 16-page primary dashboard (index/daily/calendar/vacation/mlb/nfl/ncaaf/wwo/radio/sources/flagged/methodology/review/executive-summary/teams), all 30 MLB clubs (Giants/A's FOCUS), 49ers/Stanford/Cal FOCUS, WWO national broadcasts across nine categories, Bay Area AM/FM radio stations, exact Pacific-time free windows, 7/14/21-day least-conflict candidates for 2027/2028/2029 labelled ESTIMATED/UNVERIFIED where schedules unreleased.
- Official-source spot checks consistent with prior verified records: Super Bowl LXI Feb 14 2027 (NFL important dates); 2027 MLB season opens Mar 25 2027 / spring training Feb 19 2027 (MLB releases); WWO station finder carries the affiliate-carry caveat; MLB Stats API 2028/2029 returns zero rows → correctly UNVERIFIED/ESTIMATED.
- Irregularities: none new. IR-001…IR-017 remain published on `flagged.html`, non-blocking.

### PR / merge / deploy result — `arena/187a4005-korea4` (2026-11-05)

| Item | Result |
|---|---|
| PR | pending |
| State | pending |
| Merge commit | pending |
| Pages deploy | pending |
| Local gate | PASS |
| Irregularities | none new; IR-001…IR-017 non-blocking |
