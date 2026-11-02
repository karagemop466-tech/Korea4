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
