# Korea4 — FREE TIME VACATION

Official-source dashboard for finding Pacific-time minutes with **no monitored live sports broadcast on standard AM/FM radio in Outer Sunset, San Francisco 94122**.

Live site: <https://karagemop466-tech.github.io/Korea4/>

## What is tracked
- All 30 MLB clubs and every officially released 2026/2027 MLB Stats API game row; Giants & Athletics are FOCUS.
- All released 2026 NFL preseason, regular-season, postseason and special-event rows; 49ers are FOCUS.
- Stanford and Cal NCAAF games; future ACC/CFP/Notre Dame official anchors.
- Westwood One Sports national broadcasts across all nine official categories; SF station-finder affiliates and carriage caveat.
- KNBR, KSFO, 95.7 The Game, KNBR/KTCT 1050, 680/104.5/107.7, 960 KNEW, and other confirmed Bay Area radio mappings.
- Other official Bay Area radio sports, including the complete 2026 San Jose Earthquakes terrestrial radio schedule.

## NFL decision module (2026-11-13)
- `nfl-lines.html` — how the site originates its own NFL numbers from official sources only (8-step pipeline, official inputs, Week 11 schedule-currency check).
- `nfl-strategies.html` — strategy leaderboard competition framework: divisions (singles / parlays / player-prop combos), scoring, signal research, 8 validation gates, correlation research (values intentionally blank, IR-025), integrity exclusions from the official NFL policy.
- `nfl-injuries.html` — official Week 10 injury-report snapshot (15 clubs, captured 2026-11-13), roster/transaction sources, starter-to-backup deficiency framework with verbatim observations.
- `nfl-suggestions.html` — dedicated suggestions section: 10 improvement proposals, 10 open questions (what is known / missing / how to discover), decision-readiness checklist. Implemented only after a decision is recorded on COORDINATION.md.
- Module data: `data/nfl/*.json`; verification record: `research/nfl-module/README.md`; new flags: IR-022…IR-026 on `flagged.html`.

## Verification labels
- **VERIFIED** — read from an official raw response; source link on the row.
- **UNVERIFIED** — official value blank/TBD/not released; source link establishes the gap.
- **ESTIMATED** — documented planning model from official 2026 rows; never a released schedule.

## Pages
`index.html`, `daily.html`, `calendar.html`, `vacation.html`, `mlb.html`, `nfl.html`, `nfl-lines.html`, `nfl-strategies.html`, `nfl-injuries.html`, `nfl-suggestions.html`, `ncaaf.html`, `wwo.html`, `radio.html`, `sources.html`, `flagged.html`, `methodology.html`, `review.html`, `executive-summary.html`.

Parallel-session dashboards are preserved at `docs/`, `site/`, and `site/pages/` and linked from every page footer.

## Reproduce
```bash
python -m pip install -r requirements.txt
python scripts/fetch_official.py --refresh-errors   # GitHub Actions runner has outbound access
python scripts/collect_official.py
python scripts/build_site.py
python scripts/verify.py
```

Raw official responses, SHA-256 hashes, and source URLs are in `research/official/manifest.json` and `research/probe/manifest.json`.
