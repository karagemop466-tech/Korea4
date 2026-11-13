# Final verification report

Generated: 2026-11-13T13:09:05+00:00

- JSON files checked: 15
- Primary generated pages: 21
- Static primary table rows with source URL: 10596
- HTML pages link-checked (including legacy trees): 104
- Internal links checked: 1332
- Broken internal links: 0
- JavaScript syntax: PASS
- NFL decision-support gate (scripts/verify_nfl_lab.py): PASS (report: research/nfl-lab-verification.md)
- Event rows checked: 6591; row source domains checked against the official allowlist: 34069
- Errors: 0
- Warnings: 0

## Structural checks (not a source-value audit)

1. Static primary data rows with `data-source-url` have an HTTP link and an official-domain host (allowlist in `scripts/verify.py`); this check does not validate the source content of every row.
1b. Event rows: no same-team matchups, no duplicate NFL games on a date, and every row source/duration URL on the official allowlist. vividseats.com (ticket reseller), buffedlizard55-lab.github.io (dead prior reference) are rejected; repo-internal process URLs (COORDINATION.md, live Pages data/flag pages) are allowed only as FLAG_ONLY audit/process references, never as value sources.
2. Dynamic daily/calendar table renderer contains source-link code.
3. Blank-value and status-label behavior is exercised separately by dashboard tests, not exhaustively proven here.
4. A link to a source does not establish the accuracy or completeness of its row.
5. Internal links include root, `site/`, `site/pages/`, `docs/`, and data assets.
6. Future schedule and radio coverage gaps remain unverified; this checker does not fetch official sources.

## Result

PASS — structural checks only: no detected broken internal links, missing sampled source links, JSON errors, merge markers, or JS syntax errors. This does not certify the schedule data.

## Previous deployment (historical)

- PR [#13](https://github.com/karagemop466-tech/Korea4/pull/13) merged at `849839f`; Pages build run `41497635594` succeeded.
- PR [#14](https://github.com/karagemop466-tech/Korea4/pull/14) recorded the earlier result. These facts do not certify the current deployment.
