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

## Verification labels
- **VERIFIED** — read from an official raw response; source link on the row.
- **UNVERIFIED** — official value blank/TBD/not released; source link establishes the gap.
- **ESTIMATED** — documented planning model from official 2026 rows; never a released schedule.

## Vacation answer (2027–2029)

No 7-, 14- or 21-day stretch is free. The longest run of consecutive days with **no published game** of any monitored category is
5 days, but each of those runs exists only because the 2027 NFL / Westwood One, 2028 and 2029
schedules are unreleased. The longest gap **bracketed by two published official games** is 4 days
(2027-01-19 → 2027-01-22). Full analysis: `free-runs.html`.

Recompute the whole chain locally:

```bash
python3 scripts/build_free_runs.py   # consecutive-day classes + ranked runs -> data/official/free-runs.json
python3 scripts/build_site.py        # rebuild every page
python3 scripts/verify.py            # links, source rows, JSON, JS
```

Official NBA/NHL rows for the Sharks and Warriors are captured in CI (`scripts/fetch_nba_nhl_sources.py`,
`scripts/collect_other_sports.py`, workflow `free-runs.yml`). The Sharks feed works; the NBA CDN returns HTTP 403 to CI runners (flag F-021).

## Pages
`index.html`, `daily.html`, `calendar.html`, `vacation.html`, `free-runs.html`, `mlb.html`, `nfl.html`, `ncaaf.html`, `wwo.html`, `radio.html`, `sources.html`, `flagged.html`, `methodology.html`, `review.html`, `executive-summary.html`.

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
