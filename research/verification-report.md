# Final verification report

Audit run: 2026-11-03T19:40:08.009291+00:00
Data snapshot: 2026-11-02T18:00:25+00:00
- Compressed official snapshots integrity-checked: 675
- Event source domains checked: 6607

- JSON files checked: 9
- Primary generated pages: 15
- Static primary table rows with source URL: 9350
- HTML pages link-checked (including legacy trees): 87
- Internal links checked: 691
- Broken internal links: 0
- JavaScript syntax: PASS
- Errors: 0
- Warnings: 0

## Automated checks and limits

These checks validate stored file integrity, source-link structure and syntax. They do NOT re-fetch official pages, verify each fact against page content, establish complete radio carriage, or certify vacation availability.

1. Every static primary `<tbody>` row has a source attribute matching a visible external link. Historical review rows can link to explicitly flagged nonofficial evidence.
2. Dynamic daily/calendar table rows are constructed with an official source link in `js/app.js`.
3. Snapshot decompressed SHA-256 hashes and byte lengths match the stored manifest.
4. Event source URLs use explicitly approved official domains.
5. Internal links include root, `site/`, `site/pages/`, `docs/`, and data assets.
6. Labels and substantive schedule completeness still require human/source-content review; no completeness certification is produced.

## Result

PASS — no broken internal links, source-row failures, JSON errors, merge markers, or JS syntax errors.
