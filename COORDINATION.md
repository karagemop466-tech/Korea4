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
