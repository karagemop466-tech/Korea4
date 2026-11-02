# Final verification report

Generated: 2026-11-02T18:00:25+00:00

- JSON files checked: 9
- Primary generated pages: 15
- Static primary table rows with source URL: 9350
- HTML pages link-checked (including legacy trees): 87
- Internal links checked: 674
- Broken internal links: 0
- JavaScript syntax: PASS
- Errors: 0
- Warnings: 0

## Rules verified

1. Every static primary `<tbody>` data row has `data-source-url` and an external official link.
2. Dynamic daily/calendar table rows are constructed with an official source link in `js/app.js`.
3. Blank official values render as UNVERIFIED badges in generated tables.
4. ESTIMATED and UNVERIFIED labels are distinct from VERIFIED.
5. Internal links include root, `site/`, `site/pages/`, `docs/`, and data assets.
6. Unreleased 2028/2029 schedules are labelled ESTIMATED in meta, vacation, and methodology tables.

## Result

PASS — no broken internal links, source-row failures, JSON errors, merge markers, or JS syntax errors.

## Final deployment confirmation

- PR [#13](https://github.com/karagemop466-tech/Korea4/pull/13) merged at `849839f`.
- GitHub Pages build run `41497635594` succeeded; API `status=built`, legacy `main:/`.
- Live URL: https://karagemop466-tech.github.io/Korea4/
- Live pages fetched: root dashboard (cache-busted), `daily.html`, `mlb.html`, `flagged.html`.
- Superseded PRs #6 and #12 closed.
