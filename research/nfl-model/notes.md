# nfl-model verification notes

Companion to `nfl-model/data/sources.json` (the machine-readable registry) and
`verification-report.md` (the gate's output). This file records the *judgement* calls the
gate cannot make, so a later reader can disagree with a decision instead of rediscovering it.

Retrieval window for everything below: **2026-11-13 (UTC)**, through the agent's page-fetch
tool inside the Arena sandbox. `curl` from that sandbox reaches only
`github.com`/`api.github.com`/`registry.npmjs.org`/`pypi.org`/`files.pythonhosted.org`, so no
`raw/*.gz` byte capture exists yet — see `raw/CAPTURE-STATUS.md`. IR-030 records this.

## What was read, and what it was allowed to establish

| Source | Read as | Establishes | Deliberately not claimed |
|---|---|---|---|
| `nfl.com/injuries/league/2026/REG10` | fetched, 3 of 7 chunks | the Week 10 report exists, is organised per game, and lists 12 SF / 18 DAL players with the practice-status vocabulary populated | any league-wide availability picture; the `Injuries`/`Game Status` cells render empty in the fetched text, so no status value is published from it |
| `nfl.com/injuries/` | fetched, 2 chunks | the schema (Player, Position, Injuries, Practice Status, Game Status), week selector 1–10, season selector 1965–2026 | it is a live view — it cannot be cited for a historical week |
| `nfl.com/news/competition-committee-approves-revisions-to-injury-report…` | fetched | official definitions: DNP / Limited (<100% reps) / Full (100%); Out / Doubtful / Questionable; Probable removed; certain-to-play players omitted from the game status report | nothing — this is the load-bearing document for the blank policy |
| `nfl.com/news/nfl-training-camp-roster-faqs…` | fetched | IR unlimited placements, ≤8 designated returns per club, ≤2 per player, 4-game minimum; PUP/NFI eligible after 4 games; 16-man practice squad | currency: written for the 2022 offseason, so the 2026 wording is unconfirmed (IR-029, Q-09) |
| `support.nfl.com … NFL Pro FAQ` | fetched | NGS data is published the day after the game; box score and play-by-play are same-day; matchup-advantage is a composite of success rate and EPA | that NFL Pro's product terms bind a research pipeline |
| `49ers.com/team/depth-chart` | fetched | one complete club depth chart with its own `Updated as of 11/10/26` stamp; several positions show 1–2 names only | anything about the other 31 clubs; the two reported players missing from the chart |
| `nj.gov/oag/ge/docs/Financials/PressRelease2026/August2026.pdf` | fetched, chunk 0 of 3 | August 2026 gross revenue $61,445,421 (−25.0% YoY), online $59,749,699, lounge $1,695,722, YTD $671,371,105, taxes $12,767,931 | statewide hold % and parlay hold % — they sit in an unretrieved chunk, so `M-07` stays blank |
| `sbg.colorado.gov/…47-million-collected-in-september` + monthly-reports index | fetched | Sept 2026 handle $546,819,852.87 / tax $4,743,419.32; Aug 2026 $388,148,758.21 / $3,154,842.89; FYTD $1,421,300,215.65 / $12,461,150.92 | operator-level split; and no figure here is treated as final, because the state reissues revisions ("April 2026 … revised November 2026") |
| `the-odds-api.com/sports-odds-data/nfl-odds.html` | fetched | endpoint, market list, regions, `point`/`price` payload shape, historical depth from mid-2020 | that the vendor's numbers are official; a vendor document certifies the vendor's product only, so SG-01 needs a live trial |
| `arxiv.org/abs/1211.4000` | fetched | 2,560 games 2002–2011; home teams 47% ATS; home-underdog 53.5% against a 52.38% break-even; line movement predicts divisional winners ≥75% | the full-text-only claims (opening ≈ closing line, ~10% of games move ≥2 points) stay PARTIAL |
| `api.github.com/repos/NFL/Next-Gen-Stats` | queried from the sandbox | HTTP 404 — there is no official public bulk tracking repo | this is a verified absence, which is why `LM-07` is blocked rather than thin |
| Golden Nugget retail house rules v15 (operator PDF), Indiana 68 IAC 27 | search snippet only | direction of the rule: correlated non-SGP parlays may be voided; a void/push SGP leg reprices | any numeric or wording claim. Both are on the follow-up list; the section cites them as reference-only hosts |

## Interpretation decisions

1. **Blank ≠ zero, and blank ≠ missing.** Because the league omits certain-to-play players by
   design, an empty `Game Status` cell encodes "available without a designation". It is
   published as `not confirmed`, and no model input may be derived from it. This is the single
   most consequential rule in the section (IR-038).
2. **Same-day features may not use NGS.** Tracking-derived features exist only from T+1, so any
   pre-kickoff gate depending on them is unimplementable as specified. Gates were written against
   box score / play-by-play instead.
3. **Correlation may not be estimated from bounds.** The Fréchet interval for a two-leg parlay
   spans almost the whole [0,1] range (computed in `line-origination.html`), so bounds cannot price
   a ticket; `G-11` requires a measured ρ. Only structurally nested pairs carry an exact ρ = 1 by
   identity, and those are marked as such.
4. **No strategy is described as validated.** Results columns are empty by construction and a test
   fails if anyone fills them before a bet ledger exists. The break-even, required-n and ROI
   standard-error tables are labelled DERIVED — they are arithmetic on published odds notation, not
   measurements of any market.
5. **The 162-row Week 10 capture was not published.** It is the largest temptation in this
   section: real data that cannot be re-derived from a stored artifact. Publishing it would make
   the section unverifiable, so `injuries.json` contains only the 30 rows the fetched text supports
   and the shortfall is an explicit coverage table plus IR-034.
6. **`nfl.com` club depth-chart and transactions paths 404**, so depth is collected club-by-club.
   The club URL set in the collector is a convention, not verified data, and says so in
   `DEADLINE_NOTE`; a 404 is recorded as a coverage gap, never as an absent player.

## Derived numbers, recomputable

- Break-even at −110: `110/210` = **52.381%**.
- A −110/−110 market implies **4.76%** total vig; a balanced book holds **2.38%**.
- Two-sided α = 5%, power 80%, `n ≈ (z₀.₉₇₅ + z₀.₈)² p(1−p) / e²`: **19,578** bets to detect a
  1% edge, 4,894 at 2%, 2,175 at 3%, 783 at 5%, 306 at 8%, 196 at 10%.
- ROI standard error with a 55% hit rate: **5.48 pts** at n = 300 (±10.8 pts at 95%), 2.12 pts at
  n = 2,000. Consequence: a 300-bet backtest cannot distinguish a real 2% edge from noise, which
  is why the leaderboard weights calibration and gate compliance rather than raw ROI.

## Follow-ups for whoever picks this up

1. Run `python3 scripts/fetch_nfl_model_sources.py --week <w> --season <y>` in CI so the injury and
   depth rows gain byte-level captures, then re-derive Week 10 from the manifest.
2. Retrieve NJ August 2026 chunk 1 (handle / win / parlay table) to fill `M-07`.
3. Re-read the settling operator's house rules and codified 68 IAC 27 from the primary PDFs, then
   convert the `G-12` legality note from PARTIAL to a citable rule.
4. Re-confirm the roster-rule wording against the current league bylaw; the FAQ is a 2022 document.
5. Run the SG-01 odds-vendor trial before any `line-origination` step is claimed as implemented.

## Cross-section reconciliation (added after merging `main`)

`main` advanced during this work: PR #45 and PR #48 each landed an NFL decision-support section with
their own verification gates. Two consequences were handled here rather than ignored:

1. **Flag ids renumbered.** Those sections took `IR-022…IR-026`, which this section had originally
   used for its own irregularities. Every id in this tree was shifted to `IR-027…IR-041` so the site
   has one global sequence with no collisions, and the verifier/test now enforce a floor of 26.
2. **Overlap disclosed on the page, not hidden.** `nfl-model/index.html` gained a panel naming the
   sibling sections and explaining that a coverage difference (1 club structured here, 26 of 28
   clubs with a visible table there) is a difference of capture standard, not a contradiction. The
   question of which section is canonical is published as **SG-21** and flagged as **IR-041**, both
   left for the owner; no file in either sibling tree was edited.
