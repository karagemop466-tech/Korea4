# Final verification report

Generated: 2026-11-05T21:10:04+00:00

- JSON files checked: 9
- Primary generated pages: 15
- Static primary table rows with source URL: 10086
- HTML pages link-checked (including legacy trees): 87
- Internal links checked: 689
- Broken internal links: 0
- JavaScript syntax: PASS
- Errors: 0
- Warnings: 0

## Structural checks (not a source-value audit)

1. Static primary data rows with `data-source-url` have an HTTP link; this check does not validate the domain, the source content, or every table row.
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
