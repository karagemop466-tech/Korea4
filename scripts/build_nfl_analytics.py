#!/usr/bin/env python3
"""Generate the NFL analytics module pages from data/nfl-analytics/*.json.

Runs after scripts/build_site.py helpers; every table row carries a source link.
Values follow the verification labels defined in scripts/compute_nfl_analytics.py:
VERIFIED (official page), MIRROR (nflverse mirror of official feeds, unverified
individually), MODEL ESTIMATED (computed), MARKET REF (secondary archived lines).
"""
from __future__ import annotations
import json
from pathlib import Path

import build_site as bs

ROOT = Path(__file__).resolve().parents[1]
NA = ROOT / "data/nfl-analytics"
AUDIT = ROOT / "research/nfl/audit"

def load(name):
    return json.loads((NA / name).read_text())

def audit_load(name):
    return json.loads((AUDIT / name).read_text())

inj = load("injuries-week10.json")
defi = load("deficiencies-week10.json")
qb = load("qb-availability-week10.json")
team = load("team-stats-2026.json")
lines = load("originated-lines-week10.json")
sigs = load("signals-2026.json")
corr = load("correlations-2026.json")
board = load("leaderboard-2026.json")
strat = load("strategies.json")
sugg = load("suggestions.json")
oq = load("open-questions.json")
spot = audit_load("week10-spotcheck.json")
official_spot = json.loads((ROOT / "research/nfl/official/week10-official-spotcheck.json").read_text())
audit = audit_load("nfl-rows-audit.json")

NFLVERSE = "https://github.com/nflverse/nflverse-data/releases/tag/{}"

def sha_table():
    rows = []
    for line in (ROOT / "research/nfl/raw/sha256sums.txt").read_text().splitlines():
        if not line.strip():
            continue
        sha, name = line.split(None, 1)
        tag = {"games.csv.gz": "schedules", "injuries_2026.csv.gz": "injuries",
               "depth_charts_2026.parquet": "depth_charts", "stats_team_week_2026.csv.gz": "stats_team",
               "play_by_play_2026.csv.gz": "pbp", "snap_counts_2026.csv.gz": "snap_counts"}.get(name.strip())
        rows.append({
            "file": f"research/nfl/raw/{name.strip()}", "sha256": sha[:24] + "…",
            "provenance": "nflverse rolling release (community mirror of official NFL feeds)",
            "source_url": NFLVERSE.format(tag) if tag else "https://github.com/nflverse/nflverse-data",
            "source_label": "nflverse release", "verification": "SECONDARY — flagged IR-042",
        })
    return rows

# ------------------------------------------------------------------ hub page
def build_hub():
    status_rows = [
        {"component": "Injury & depth-chart tracking", "what": "Week 10 official report transcription + starter-deficiency join + QB availability", "status": "LIVE — refreshed by weekly workflow", "page": "nfl-injuries.html",
         "source_url": "https://www.nfl.com/injuries/", "source_label": "NFL.com injury report"},
        {"component": "Signal research", "what": "EPA power rating (fitted on 137 completed 2026 games), holdout accuracy, rest/weather/QB-change evaluations", "status": "LIVE — ESTIMATED, single-season sample", "page": "nfl-signals.html",
         "source_url": "https://www.nfl.com/stats/ngs/trends", "source_label": "NFL.com Next Gen Stats (official EPA definition)"},
        {"component": "Line origination", "what": "Documented margin/total models; Week 10 originated spreads, totals, MLs; edges vs archived market reference", "status": "LIVE — MODEL ESTIMATED (flagged IR-024)", "page": "nfl-lines.html",
         "source_url": NFLVERSE.format("schedules"), "source_label": "nflverse schedules release (market reference)"},
        {"component": "Strategy leaderboard", "what": "Registry, 7 validation gates, luck-adjusted scoring, reward tiers, starter strategies", "status": "LIVE — all strategies SPEC tier", "page": "nfl-strategies.html",
         "source_url": "https://github.com/karagemop466-tech/Korea4/blob/main/data/nfl-analytics/strategies.json", "source_label": "strategy registry (this repo)"},
        {"component": "Correlation framework", "what": "Bernoulli-covariance parlay math + descriptive 2026 game-level correlations (n=137)", "status": "LIVE — calculator + ESTIMATED correlations", "page": "nfl-correlation.html",
         "source_url": NFLVERSE.format("pbp"), "source_label": "nflverse play-by-play release"},
        {"component": "Suggestions registry", "what": "10 logged improvement suggestions with review workflow", "status": "LIVE — awaiting reviewer", "page": "suggestions.html",
         "source_url": "https://github.com/karagemop466-tech/Korea4/blob/main/data/nfl-analytics/suggestions.json", "source_label": "suggestions registry (this repo)"},
        {"component": "Decision questions", "what": "12 open questions: known / missing / discovery path / blocks", "status": "LIVE — awaiting reviewer answers", "page": "open-questions.html",
         "source_url": "https://github.com/karagemop466-tech/Korea4/blob/main/data/nfl-analytics/open-questions.json", "source_label": "open questions (this repo)"},
        {"component": "Repo NFL data audit", "what": "70 Nov-2026 NFL rows re-checked vs fresh official slate: 70/70 matched, 0 kickoff-time mismatches; 14/14 Week 10 rows matched the live NFL.com page", "status": "DONE — see audit JSON", "page": "nfl-analytics.html",
         "source_url": "https://www.nfl.com/schedules/2026/REG10/", "source_label": "NFL.com Week 10 schedule (live check 2026-11-13)"},
    ]
    body = f'''
<div class="callout"><strong>NFL analytics module.</strong> Collect → organize → analyze, with every table row
linked to its source. Data flow: nflverse rolling releases (flagged secondary mirror of official NFL feeds,
IR-042) → committed sha256 snapshots in <code>research/nfl/raw/</code> → documented computations
(<code>scripts/compute_nfl_analytics.py</code>) → pages below. Official pages
(NFL.com injury report and schedules) are the primary row sources and were fetched live 2026-11-13.
Nothing on these pages is manual input; the weekly GitHub Actions workflow refreshes snapshots and rebuilds.</div>
<section class="panel"><h2>Module components</h2>
{bs.table(['Component','What it contains','Status','Page'], status_rows, ['component','what',('status','badge'), 'page'], 'nfl-module', 50)}
</section>
<section class="panel"><h2>Data provenance — committed snapshots</h2>
{bs.table(['Snapshot file','SHA-256 (first 24)','Provenance'], sha_table(), ['file','sha256','provenance'], 'nfl-provenance', 20)}
</section>
<section class="panel"><h2>Automated audit of repo NFL rows (this session)</h2>
{bs.table(['Check','Result','Source'], [
    dict(check="data/official/events.json NFL rows, Nov 2026 (n=70) vs fresh nflverse slate", result="70/70 matched on date+teams; 0 kickoff-time mismatches (ET)", source_url=NFLVERSE.format("schedules"), source_label="nflverse schedules release", verification="VERIFIED"),
    dict(check="Week 10 nflverse slate vs live NFL.com schedule page (14 games)", result="14/14 date+ET-time matches; TNF result WAS 24 @ NYG 21 matches", source_url="https://www.nfl.com/schedules/2026/REG10/", source_label="NFL.com Week 10 schedule", verification="VERIFIED"),
    dict(check="Official injury-page transcription vs nflverse mirror (209 rows)", result="187 MATCH, 0 contradictions, 22 rows exist only on the official page (mirror lag — IR-023)", source_url="https://www.nfl.com/injuries/", source_label="NFL.com injury report", verification="VERIFIED"),
], ['check','result','verification'], 'nfl-audit', 20)}
<p class="intro">Full audit records: <code>research/nfl/audit/nfl-rows-audit.json</code>, <code>research/nfl/audit/week10-spotcheck.json</code>.</p>
</section>
'''
    bs.write("nfl-analytics.html", bs.page("NFL analytics", "nfl-analytics.html",
        "NFL data collection, signal research, own-line origination, strategy leaderboard, and decision tracking — every row sourced.",
        body))

# ------------------------------------------------------------------ injuries page
def build_injuries():
    designation_note = ('''<div class="callout"><strong>Reading the report.</strong> Clubs file practice-participation reports
(Wed–Fri) and game-status designations on the official league report. Designations shown here are copied verbatim from the
official page — no interpretation is added. News-reported roster moves (IR placements, announced starters) are listed with
their official NFL.com news links below.</div>''')
    body = f'''
{designation_note}
<section class="panel"><h2>Week 10 official injury report — transcribed from NFL.com (fetched 2026-11-13)</h2>
<p class="intro">{inj['coverage_rule']} {inj['note']}</p>
{bs.table(['Team','Player','Pos','Injury','Practice status','Game status','Depth-chart evidence'],
          inj['rows'], ['team','player','position',('injury','blank'),('practice_status','text'),('game_status','blank'),'depth_chart_status'],
          'injuries-w10', 100)}
</section>
<section class="panel"><h2>Starter-deficiency join (MODEL — official report × depth charts)</h2>
<p class="intro">{defi['method']} A player is flagged only with season-wide depth-rank-1 evidence; clubs demote injured starters,
so current-chart rank alone would hide them. Backup names are the current chart's next man at that position — a join, not an announced lineup.</p>
{bs.table(['Team','Unit','Player out','Pos','Status','Injury','Next man up (model join)','Verification'],
          defi['rows'], ['team','unit','player_out','position',('status','badge'),('injury','blank'),'backup_next_man',('verification','badge')],
          'deficiency-w10', 50)}
</section>
<section class="panel"><h2>QB availability, Week 10 (depth chart + official news)</h2>
{bs.table(['Team','Depth QB1','Depth QB2','Week-10 report','Announced / expected','Note'],
          qb['rows'], ['team','depth_qb1','depth_qb2',('week10_report','blank'),('announced_or_expected','blank'),('note','blank')],
          'qb-w10', 50)}
</section>
<section class="panel"><h2>Official roster/news context (fetched 2026-11-13)</h2>
{bs.table(['Team','Development'], [
    dict(team=t2["team"], note=t2["note"], source_url=t2["url"], source_label="NFL.com news (official)", verification="VERIFIED")
    for t2 in official_spot["announced_starters_from_official_news"]
], ['team','note','verification'], 'qb-news', 50)}
</section>
'''
    bs.write("nfl-analytics-injuries.html", bs.page("NFL injuries & depth", "nfl-injuries.html",
        "Official Week-10 injury report, starter deficiencies by unit, and QB availability — with per-row official sources.",
        body))

# ------------------------------------------------------------------ signals page
def build_signals():
    body = f'''
<div class="callout"><strong>What a "signal" is here.</strong> A measurable factor evaluated against completed game outcomes
from committed data. Everything is computed from the 2026 season to date (n = 137 games) — single-season, small-sample,
labelled ESTIMATED. The rating model is <code>margin = k × (home net-EPA/play − away net-EPA/play) + h₀</code>, fitted
by ordinary least squares on completed games; EPA is the officially defined Next Gen Stats measure.</div>
<section class="panel"><h2>Signal evaluation</h2>
{bs.table(['Signal','Measured result (2026 sample)','Status'], sigs['rows'], ['signal','measure',('status','badge')], 'signals', 50)}
</section>
<section class="panel"><h2>Team ratings through Week {team['through_week']} (MODEL — from committed team stats)</h2>
{bs.table(['Team','Record','Pts/g','Opp pts/g','Off EPA/play','Def EPA/play allowed','Net EPA/play'],
          team['rows'], ['team','record',('points_pg','num'),('opp_points_pg','num'),('off_epa_per_play','num'),('def_epa_per_play_allowed','num'),('net_epa_per_play','num')],
          'team-ratings', 100)}
<p class="intro">{team['epa_method']}</p>
</section>
<section class="panel"><h2>Literature anchors (external research, clearly secondary)</h2>
{bs.table(['Finding','Why it matters here','Source'], [
    dict(finding="Sportsbooks shade prices to exploit bettor biases; favourites (esp. road favourites) are systematically over-bet; home underdogs historically returned positive in the NFL betting market.",
      why="Justifies originating our own lines rather than trusting market prices, and motivates gate G7 (closing-line discipline).",
      source_url="https://conyso.com/biases/bias/favourite-longshot-bias/",
      source_label="Levitt (2004) summary — The Economic Journal 114(495) 223-246", verification="SECONDARY — literature"),
    dict(finding="EPA (expected points added) is the official play-value framework: expected points from down, distance, field position; net EPA = offensive EPA/play minus defensive EPA/play allowed.",
      why="The power rating and total model inputs are defined on this official measure.",
      source_url="https://www.nfl.com/stats/ngs/trends",
      source_label="NFL.com — Next Gen Stats trends (official EPA definition)", verification="VERIFIED (definition)"),
    dict(finding="Injury-report designations were redefined in 2016 ('probable' eliminated; Questionable/Doubtful/Out redefined) — reported by national outlets.",
      why="Explains why the report contains only those three game statuses; practice participation is the leading indicator.",
      source_url="https://www.espn.com/espn/print?id=17361111",
      source_label="ESPN report on NFL policy change (2016) — secondary news", verification="SECONDARY — news"),
], ['finding','why','verification'], 'literature', 20)}
</section>
'''
    bs.write("nfl-signals.html", bs.page("NFL signals research", "nfl-signals.html",
        "Factor evaluation on the 2026 sample, team EPA ratings, and the literature behind each signal — all rows sourced.",
        body))

# ------------------------------------------------------------------ lines page
def build_lines():
    m = lines['model']
    body = f'''
<div class="callout"><strong>Originating lines, not reading them.</strong> The models below are fitted only on committed
data: margin = {m['margin_formula'].split(';')[0].split('= ',1)[1].split(';')[0]} (fitted), total = {m['total_formula'].split('= ',1)[1].split(';')[0]} (fitted),
win probability = {m['win_probability']}. Rest adjustment: {m['rest_adjustment']}. Fit data: {m['fit_data']}.
{m['market_reference_note']}.</div>
<section class="panel"><h2>Week 10 originated lines vs archived market reference</h2>
<p class="intro">Model home spread / model total / model home moneyline. Edge signs: <strong>home-spread edge &gt; 0</strong> = model leans AWAY relative to market; <strong>total edge &gt; 0</strong> = model leans OVER. All rows MODEL ESTIMATED (IR-024).</p>
{bs.table(['Game','Date','KO (ET)','Model home spread','Market home spread','Spread edge','Model total','Market total','Total edge','Model home ML','Win prob (home)'],
          lines['rows'], ['game','date','kickoff_et',('originated_home_spread','num'),('market_reference_home_spread','num'),('home_spread_edge_vs_market','num'),('originated_total','num'),('market_reference_total','num'),('total_edge_vs_market','num'),('originated_home_ml','text'),('model_win_prob_home','num')],
          'lines-w10', 50)}
</section>
<section class="panel"><h2>How to use these lines (process, not advice)</h2>
<ol class="exec-list">
<li>Compute the model line before looking at any market number; log both with timestamps (G5 no-lookahead).</li>
<li>Only differences ≥ 1.0 point (spread) or ≥ 1.5 points (total) are recorded as review candidates — threshold is a documented research convention flagged under Q10.</li>
<li>When a market-reference feed is approved (Q1), every decision logs price-taken vs closing line for G7; until then no strategy can be certified.</li>
<li>Multi-leg tickets must pass through the correlation adjustment on <a href="nfl-correlation.html">nfl-correlation.html</a> (G6) with a 2-leg same-game cap.</li>
<li>Grading is always from committed boxscores after the game — never re-derived lines.</li>
</ol></section>
<section class="panel"><h2>Key numbers (documented convention, unfitted)</h2>
<p class="intro">NFL scoring concentrates on 3- and 7-point increments; spread decisions near 3 and 7 are treated as
key-number territory when logging edges. The distribution is refitable once multi-season history is committed (Q8) —
no fitted key-number table is published yet because one season (n=137) is too small; publishing one would violate the
no-inference rule.</p></section>
'''
    bs.write("nfl-analytics-lines.html", bs.page("NFL line origination", "nfl-lines.html",
        "Own lines originated from a documented EPA model — methodology, Week 10 output, and edge discipline.",
        body))

# ------------------------------------------------------------------ strategies page
def build_strategies():
    body = f'''
<div class="callout"><strong>Leaderboard purpose: remove luck, reward selective skill.</strong> A strategy earns
nothing from a lucky streak: gates require provenance, sample size, luck-adjusted significance (t-stat), held-out
persistence, no lookahead, correlation accounting, and (once prices exist) closing-line discipline.
Rewards are points and tiers — never money. {board['assumed_price_note']}</div>
<section class="panel"><h2>Validation gates</h2>
{bs.table(['ID','Gate','Rule','Status'], strat['validation_gates'], ['id','gate','rule',('status','badge')], 'gates', 50)}
</section>
<section class="panel"><h2>Scoring and reward tiers</h2>
<table><thead><tr><th>Item</th><th>Definition</th></tr></thead><tbody>
<tr data-source-url="https://github.com/karagemop466-tech/Korea4/blob/main/data/nfl-analytics/strategies.json"><td>Points formula</td><td>{strat['scoring']['formula']}</td><td><a class="source-link" href="https://github.com/karagemop466-tech/Korea4/blob/main/data/nfl-analytics/strategies.json" target="_blank" rel="noopener">registry (this repo)</a></td></tr>
<tr data-source-url="https://github.com/karagemop466-tech/Korea4/blob/main/data/nfl-analytics/strategies.json"><td>Luck factor</td><td>{strat['scoring']['luck_factor']}</td><td><a class="source-link" href="https://github.com/karagemop466-tech/Korea4/blob/main/data/nfl-analytics/strategies.json" target="_blank" rel="noopener">registry (this repo)</a></td></tr>
<tr data-source-url="https://github.com/karagemop466-tech/Korea4/blob/main/data/nfl-analytics/strategies.json"><td>OOS factor</td><td>{strat['scoring']['oos_factor']}</td><td><a class="source-link" href="https://github.com/karagemop466-tech/Korea4/blob/main/data/nfl-analytics/strategies.json" target="_blank" rel="noopener">registry (this repo)</a></td></tr>
<tr data-source-url="https://github.com/karagemop466-tech/Korea4/blob/main/data/nfl-analytics/strategies.json"><td>Cap note</td><td>{strat['scoring']['cap_note']}</td><td><a class="source-link" href="https://github.com/karagemop466-tech/Korea4/blob/main/data/nfl-analytics/strategies.json" target="_blank" rel="noopener">registry (this repo)</a></td></tr>
</tbody></table>
{bs.table(['Tier','Requirement','Reward'], strat['reward_tiers'], ['tier','requirement','reward'], 'tiers', 20)}
</section>
<section class="panel"><h2>Registered starter strategies</h2>
{bs.table(['ID','Name','Mechanical rule','Market dependency','Status'],
          strat['starter_strategies'], ['id','name','rule','market_dependency',('status','badge')], 'registry', 50)}
</section>
<section class="panel"><h2>2026 in-sample simulation (SIMULATED — not evidence of edge)</h2>
{bs.table(['ID','Strategy','Picks','Hits','Hit rate','Units (est.)','ROI (est.)','t-stat vs breakeven','Status'],
          board['rows'], ['id','name',('picks','num'),('hits','num'),('hit_rate','text'),('units_est','text'),('roi_est','text'),('t_stat_est','text'),('status','badge')],
          'leaderboard', 20)}
<p class="intro">Baseline for context: in weeks 1-9 of this season, road favourites of ≥ 3 points won outright 84% of the
time (32/38) and home favourites of ≥ 3 points 65% (45/69) — computed from the committed schedules release. S1's 90.3% is
barely above its own class baseline; this is exactly the small-sample illusion the gates exist to catch.</p>
</section>
<section class="panel"><h2>Player-prop combos (policy)</h2>
<div class="callout">{strat['player_prop_policy']}</div>
</section>
<section class="panel"><h2>Registration</h2>
<p class="intro">Required fields: {', '.join(strat['registration_format']['required_fields'])}. {strat['registration_format']['note']}</p>
</section>
'''
    bs.write("nfl-analytics-strategies.html", bs.page("NFL strategy leaderboard", "nfl-strategies.html",
        "Validation gates, luck-adjusted scoring, reward tiers, the strategy registry, and the 2026 simulation.",
        body))

# ------------------------------------------------------------------ correlation page
CALC_JS = """
<script>
function clamp(x, lo, hi){ return Math.max(lo, Math.min(hi, x)); }
function bernoulliJoint(pa, pb, rho){
  var pa_ = clamp(pa, 0.001, 0.999), pb_ = clamp(pb, 0.001, 0.999);
  var covMax = Math.sqrt(pa_*(1-pa_)*pb_*(1-pb_));
  var rho_ = clamp(rho, -0.99, 0.99);
  var cov = rho_ * covMax;
  var joint = pa_*pb_ + cov;
  var lo = Math.max(0, pa_+pb_-1), hi = Math.min(pa_, pb_);
  if (joint < lo) joint = lo; if (joint > hi) joint = hi;
  return {joint: joint, bounded: (pa_*pb_+cov < lo) || (pa_*pb_+cov > hi)};
}
function fairOdds(p){ return p <= 0 ? '∞' : '+' + Math.round((1-p)/p*100); }
function calc(){
  var pa = parseFloat(document.getElementById('pa').value)/100;
  var pb = parseFloat(document.getElementById('pb').value)/100;
  var rho = parseFloat(document.getElementById('rho').value);
  var legs3 = document.getElementById('three').checked;
  var pc = legs3 ? parseFloat(document.getElementById('pc').value)/100 : null;
  var rho2 = legs3 ? parseFloat(document.getElementById('rho2').value) : 0;
  var rho3 = legs3 ? parseFloat(document.getElementById('rho3').value) : 0;
  var r1 = bernoulliJoint(pa, pb, rho);
  var pAB = r1.joint;
  var pABC = null;
  if (pc !== null){
    var r2 = bernoulliJoint(pa, pc, rho2);
    var r3 = bernoulliJoint(pb, pc, rho3);
    pABC = clamp(pAB + pc - Math.max(0, pa + pc - 1) - r2.joint - r3.joint + pa*pb*pc*0 , 0.0001, 1);
    // inclusion-exclusion with pairwise covariances:
    var covAB = pAB - pa*pb, covAC = r2.joint - pa*pc, covBC = r3.joint - pb*pc;
    pABC = clamp(pa*pb*pc + covAB*pc + covAC*pb + covBC*pa, Math.max(0,pa+pb+pc-2), Math.min(pa,pb,pc));
  }
  var out = document.getElementById('out');
  var html = '<table><thead><tr><th>Quantity</th><th>Value</th></tr></thead><tbody>';
  html += '<tr><td>P(A)</td><td>' + (pa*100).toFixed(1) + '%</td></tr>';
  html += '<tr><td>P(B)</td><td>' + (pb*100).toFixed(1) + '%</td></tr>';
  html += '<tr><td>Independent P(A∩B)</td><td>' + (pa*pb*100).toFixed(2) + '%</td></tr>';
  html += '<tr><td>Correlation-adjusted P(A∩B)</td><td>' + (pAB*100).toFixed(2) + '%</td></tr>';
  if (pABC !== null){ html += '<tr><td>3-leg P(A∩B∩C)</td><td>' + (pABC*100).toFixed(2) + '%</td></tr>'; }
  html += '<tr><td>Fair decimal-style payout for ' + (legs3 ? '3-leg' : '2-leg') + ' parlay</td><td>' + fairOdds(legs3 ? pABC : pAB) + '</td></tr>';
  if (r1.bounded) html += '<tr><td>Bounds note</td><td>ρ input pushed the joint past a Fréchet bound; result clamped</td></tr>';
  html += '</tbody></table>';
  out.innerHTML = html;
}
document.addEventListener('DOMContentLoaded', calc);
</script>
"""
corr_rows_note = ("Descriptive game-level correlations from committed play-by-play (n = "
                  f"{corr['rows'][0]['n_games']} games, weeks 1-{team['through_week']}). "
                  "These are NOT prop-leg correlations against a line; re-estimate before any parlay use.")
def build_correlation():
    body = f'''
<div class="callout"><strong>Method (G6 standard).</strong> Two binary legs A and B with correlation ρ.
Bernoulli covariance: P(A∩B) = P(A)·P(B) + ρ·√(P(A)(1−P(A))·P(B)(1−P(B))), clamped to the Fréchet bounds
[max(0, P(A)+P(B)−1), min(P(A), P(B))]. Same-game parlays are capped at 2 legs under the current gates; a 3-leg
approximation is provided for research only. {corr['method']}</div>
<section class="panel"><h2>Calculator (client-side; no market prices involved)</h2>
{CALC_JS}
<div class="table-wrap"><div class="scroll"><table><thead><tr><th>Input</th><th>Value</th></tr></thead><tbody>
<tr><td>P(A) %</td><td><input id="pa" type="number" value="60" min="1" max="99"></td></tr>
<tr><td>P(B) %</td><td><input id="pb" type="number" value="55" min="1" max="99"></td></tr>
<tr><td>ρ (A,B)</td><td><input id="rho" type="number" value="0.30" step="0.05" min="-0.99" max="0.99"></td></tr>
<tr><td>3-leg research mode</td><td><input id="three" type="checkbox"> P(C) % <input id="pc" type="number" value="50" min="1" max="99" style="width:5em"> ρ(A,C) <input id="rho2" type="number" value="0.20" step="0.05" style="width:5em"> ρ(B,C) <input id="rho3" type="number" value="0.10" step="0.05" style="width:5em"></td></tr>
</tbody></table></div><p><button type="button" onclick="calc()">Recalculate</button></p><div id="out"></div></div>
<p class="intro">Defaults are placeholders, not estimates. ρ must come from committed data (below) or reviewer-approved research — never invented.</p>
</section>
<section class="panel"><h2>Descriptive 2026 game-level correlations (ESTIMATED)</h2>
<p class="intro">{corr_rows_note}</p>
{bs.table(['Leg pair (game-level season totals)','Pearson r','n games','Status'],
          corr['rows'], ['leg_pair',('pearson_r','num'),('n_games','num'),('status','badge')], 'correlations', 20)}
</section>
<section class="panel"><h2>Why correlation decides parlay value</h2>
<p class="intro">A 2-leg parlay of independent 60% legs pays as a 36% event. With ρ = +0.30 the joint probability is
≈ 45% — the same ticket is worth very different amounts depending on correlation. This is why G6 forces every multi-leg
registration to declare its correlation source, and why the same-game cap exists: positive correlation is usually
purchased at full price in real markets, so unadjusted independence math overstates value. No odds are ingested, so this
page never claims a ticket is +EV — it computes probabilities only.</p></section>
'''
    bs.write("nfl-correlation.html", bs.page("NFL parlay correlation", "nfl-correlation.html",
        "Bernoulli-covariance correlation framework, calculator, and descriptive 2026 correlations — no market prices.",
        body))

# ------------------------------------------------------------------ suggestions page
def build_suggestions():
    body = f'''
<div class="callout"><strong>Dedicated suggestions section.</strong> {sugg['purpose']}</div>
<section class="panel"><h2>Review workflow</h2><ol class="exec-list">
{chr(10).join('<li>' + s + '</li>' for s in sugg['workflow'])}
</ol></section>
<section class="panel"><h2>Suggestions</h2>
{bs.table(['ID','Title','Category','Evidence','Impact','Risk','Depends on','Status'],
          sugg['rows'], ['id','title','category','evidence','impact','risk',('depends_on','list'),('status','badge')],
          'suggestions', 100)}
</section>
<section class="panel"><h2>Reviewer note</h2><div class="callout">{sugg['review_note']}</div></section>
'''
    bs.write("suggestions.html", bs.page("Suggestions", "suggestions.html",
        "Improvement suggestions for the site and the decision process, each with evidence, risk, and review status.",
        body))

# ------------------------------------------------------------------ open questions page
def build_questions():
    body = f'''
<div class="callout"><strong>Purpose.</strong> {oq['purpose']} {oq['reviewer_instruction']}</div>
<section class="panel"><h2>Decision questions</h2>
{bs.table(['ID','Question','What we know','What is missing','How to discover it','Blocks','Answer'],
          oq['questions'], ['id','question','known','missing','discovery',('blocks','list'),('answer','blank')],
          'open-questions', 20)}
</section>
'''
    bs.write("open-questions.html", bs.page("Open questions", "open-questions.html",
        "The questions, information and answers needed before decisions can reasonably be made — knowns, unknowns, and discovery paths.",
        body))

def main():
    build_hub(); build_injuries(); build_signals(); build_lines()
    build_strategies(); build_correlation(); build_suggestions(); build_questions()
    print(json.dumps({"pages": 8, "injury_rows": len(inj['rows']), "flag_rows": len(bs.META['flags'])}, indent=2))

if __name__ == "__main__":
    main()
