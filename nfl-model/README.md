# nfl-model — NFL line origination & signal leaderboard

Self-contained section of the Korea4 dashboard for originating NFL lines, specifying
betting-prediction strategies, and documenting the injuries / depth / market facts a
decision needs. Published at
<https://karagemop466-tech.github.io/Korea4/nfl-model/index.html>.

## Start here

| Page | What it answers |
|---|---|
| `executive-summary.html` | The one-page read for the decision-maker. |
| `questions.html` | What must be answered before any decision is reasonable, split into have / missing / cheapest way to find out. |
| `suggestions.html` | Improvement proposals with options, cost, risk and a recommendation — held unimplemented until someone chooses. |
| `requirements.html` | The full requirements register with an acceptance test per row. |
| `strategies.html`, `gates.html`, `correlation.html`, `leaderboard.html` | The programme: strategies, the tests they must pass, correlation treatment, and the competition design. |
| `injuries.html`, `depth-deficiency.html`, `market.html` | Verified source data: official injury report rows, the club depth chart, market/regulatory facts. |
| `sources.html`, `flagged.html` | Provenance registry and the irregularity list (the root pages use `IR-001..IR-026`; this section continues the shared sequence at `IR-027` so no id is doubled). |

## How it is built

```bash
python3 scripts/build_nfl_model.py          # renders every page from nfl-model/data/*.json
python3 scripts/verify_nfl_model.py         # the gate; exit 0 = publishable
python3 -m unittest discover -s tests -p 'test_nfl_model.py'
python3 scripts/fetch_nfl_model_sources.py --selftest   # collector assertion logic, no network
```

Nothing is hand-written in the HTML. Edit the JSON, rebuild, and the gate decides whether
it can be published. CI reruns the build with the committed `built_utc` stamp and fails if
the working tree changes, which is what proves nobody edited a page directly.

## The rules the gate enforces

1. Every table row carries `data-source-url`, `data-row-status` and `data-src-id`; the id must exist in `data/sources.json`.
2. A row may only claim `VERIFIED` when its source tier is official/academic/vendor/repo-internal **and** the source's retrieval method is an actual fetch (`page-fetched`, `pdf-fetched`, `repo-snapshot`, `github-api`). A `search-snippet` citation can never certify a value.
3. Hosts such as an operator's rules page or an injury aggregator are citable for audit context but are refused on `VERIFIED` rows.
4. A blank cell is `not confirmed`, never `0`, `—` or a guess. A `VERIFIED` row may contain a blank only when it asserts `_blank_ok` — that is how an official document's own blank (a player with no game-status designation) is preserved without being invented into signal.
5. Strategy `results` must stay empty while there is no bet ledger; the test suite asserts it.
6. Every page must carry the disclosure block (no profit guarantee, not betting advice, jurisdiction caveat, help line) or the build fails.
7. All internal links resolve; every page must reach every other page from its nav.

## Data files

| File | Rows |
|---|---|
| `sources.json` | source registry: publisher, tier, URL, retrieval date, method, what it establishes |
| `requirements.json` | R-01… R-28 with acceptance tests and named gaps |
| `questions.json` | Q-01… Q-22 decision-readiness register |
| `suggestions.json` | SG-01…SG-21 proposals with options and recommendations |
| `strategies.json` | ST-00… ST-15 catalogue, each with result columns blank by rule |
| `gates.json` | G-01… G-18 validation gates |
| `correlation.json` | C-01… C-14 leg pairs, nesting and bounds method |
| `leaderboard.json` | tiers, scoring metrics, discipline rules, reward options |
| `injuries.json` | official Week 10, 2026 report rows plus coverage accounting |
| `depth.json` | dated official depth chart rows and the findings they produced |
| `market.json` | M-01… M-20 market/regulatory/roster facts |
| `line_model.json` | LM-01… LM-13 origination pipeline and validation protocol |
| `flagged.json` | IR-027…IR-041 irregularities |
| `meta.json` | build stamp, counts, per-dataset snapshot ages (generated; do not hand-edit) |

## Scope discipline for parallel sessions

This tree is additive. It does not touch `data/official/**`, `scripts/collect_official.py`,
`scripts/build_site.py`, or the dashboard's own pages, so it can be built and verified without
colliding with the free-time workstream. Claim work here in `COORDINATION.md` before editing.

## Relationship to the other NFL sections

`main` also carries two sibling workstreams: `nfl-lines/nfl-strategies/nfl-injuries/nfl-suggestions` (PR #45) and
the `nfl-decision-*` set (PR #48). They are not edited by, or edited into, this section. This tree is the
**register** layer — requirements with acceptance tests, the question set that gates a decision, the suggestions
backlog, the gate definitions and the source registry; their trees are published renderings of overlapping data.
The overlap is disclosed on `nfl-model/index.html` and tracked as **IR-041**, with **SG-21** proposing how to
resolve it. Choosing a canonical home is an owner decision, not something this section applied to itself.
