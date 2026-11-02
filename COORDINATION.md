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
