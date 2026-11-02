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
| #6 `arena/4c938fb2-korea4` | OPEN | Provisional planner branch; not merged into this verification pass because it deletes shared site pages. To be closed/superseded by final integration. |
| `arena/9d83abee-korea4` | branch-local | Official source-inspection snapshots, `scripts/refresh.py`, Pacific-time interval tests; used as a cross-check, not bulk-merged. |
| `arena/97161ae7-korea4` | branch-local | Board/claim only. |
| `arena/72e6d3f7-korea4` | this session | `research/probe/` official runner snapshots, compressed collector, deeper line-by-line official-source verification, final generated site/data, PR + merge + Pages confirmation. |

**Conflict resolution 2026-11-02:** merging `origin/main` (through `47bfbeb`) into this branch produced another add/add conflict in `COORDINATION.md`. No other session content was discarded: the full `main` board and this session's previous unified board are reproduced verbatim in the appendices below. All site/data/doc files from merged PRs were retained in the working tree.

## Unified task board
| Task | Status | Owner | File scope | Verification | Notes |
|---|---|---|---|---|---|
| C0 — Shared board and published claim | done | `arena/72e6d3f7-korea4` | `COORDINATION.md` | Initial claim `99376cd`, research claim `53af657`. | Multiple sessions started from the same initial commit. |
| C1 — Repo/history/prior-site audit | done | integration | `research/reference-sites.md`, board | Git history, GitHub API, direct fetches. | IR-001: all three supplied reference GitHub Pages URLs and matching repos returned 404. |
| C2 — Official-source research/probe | done | `arena/72e6d3f7-korea4` | `scripts/probe_sources.py`, `scripts/compact_probe.py`, `.github/workflows/probe-sources.yml`, `research/probe/` | 39 official raw responses with URL/status/SHA-256; Actions runs `41490904739` and `41491175465` succeeded. | IR-002: NFL 2027 selectors show no schedule data. IR-003: WWO affiliates may not air every network broadcast. |
| C3 — Official schedule ingestion | in progress | integration | `scripts/collect_official.py`, `data/official/*`, `research/official/raw/*` | Parse MLB Stats API 2026/2027, NFL 2026 weekly/preseason/postseason anchors, WWO event grids/details, Stanford/Cal 2026, official future-date articles. | Every row needs official source URL; TBD times blank; 2028/2029 unreleased rows blank + UNVERIFIED. |
| C4 — Free-time/vacation-window analysis 2027–2029 | claimed | integration | `research/analysis/*`, site analysis pages | Recompute from official rows and separately labelled planning estimates; exact Pacific-time free intervals. | Strict definition: any MLB/NFL/Stanford/Cal/WWO/live Bay Area radio sports game makes the minute busy. |
| C5 — Dashboard, category subpages, scoreboard calendar, tables, flags | claimed | integration | root HTML, `css/`, `js/`, `data/`, `site/**`, `docs/**` | Final integration unifies navigation, keeps legacy trees for traceability, publishes all findings. | Shared outputs edited only in this final verification pass. |
| C6 — Line-by-line verification, internal-link checker, build/deploy check | unclaimed pending C5 | integration | `scripts/verify.py`, all site files | Every table row: official source link; blank official value + UNVERIFIED/ESTIMATED flag where needed. | Must run before merge. |
| C7 — PR, merge, Pages deployment confirmation, record result | unclaimed pending C6 | integration | board | PR from fixed branch to `main`, merge, then GitHub Pages build status. | Flagged items do not block merge; broken build does. |

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
- Pending: expanded official collector run, generated data/site, line-by-line verification, build/link check, PR/merge and Pages deployment confirmation.

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

