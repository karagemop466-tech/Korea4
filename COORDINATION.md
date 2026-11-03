# COORDINATION.md — unified shared task board

Last integration update: 2026-11-02 (UTC)
Active final verification session: `arena/72e6d3f7-korea4`
Fixed working branch: `arena/72e6d3f7-korea4`

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

## 2026-11-03 audit — arena/aea8720a-korea4

Fixed branch: `arena/aea8720a-korea4` (platform constraint; no alternate task branches).

| Task | Status | Owner | Files |
|---|---|---|---|
| A1 independent safety / provenance audit and integration | in progress | arena/aea8720a-korea4 | scripts/verify.py, tests/test_verification.py, scripts/build_site.py, js/app.js, .github/workflows/check.yml, .github/workflows/pages.yml, research/audit-2026-11-03.md; generated root HTML if needed |

Prior task claims are completed; prior snapshots and historical editions will be preserved. Official-source network access from this sandbox is restricted; do not represent local snapshot validation as a fresh official website check. Any newly discovered limitations will be published on Flagged for Review. Claim published before work.
