#!/usr/bin/env python3
"""Build the static NFL Lines decision-support pages from the reviewed data files."""
from __future__ import annotations
import csv, html, json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / 'data' / 'nfl'
NAV = [
    ('NFL Lines','nfl-lines.html'), ('Model overview','nfl-lines-overview.html'), ('Schedule & results','nfl-schedule.html'),
    ('Fair lines','nfl-fair-lines.html'), ('Availability','nfl-availability.html'),
    ('Backtest & luck','nfl-analysis.html'), ('Strategies & gates','nfl-strategies.html'),
    ('Leaderboard','nfl-leaderboard.html'), ('Suggestions','nfl-suggestions.html'),
    ('Questions','nfl-questions.html'), ('Flagged review','nfl-flagged.html')]
SCHEDULE='https://www.nfl.com/schedules/2026/by-week/week-8'
STANDINGS='https://www.nfl.com/standings/league/2026/REG'
INJURY='https://www.nfl.com/injuries/league/2026/reg10'
TEAM='https://www.nfl.com/standings/league/2024/REG'

def load(name): return json.loads((DATA/name).read_text(encoding='utf-8'))
def esc(x): return html.escape(str(x), quote=True)
def link(url,label=None):
    if not url: return '<span class="missing">UNVERIFIED — no source link available</span>'
    return f'<a href="{esc(url)}" target="_blank" rel="noopener">{esc(label or url)}</a>'
def pill(text):
    s=str(text or 'UNVERIFIED')
    cls='good' if s in ('VERIFIED','PASS','FINAL') or s.startswith('PASS') else 'model' if 'MODEL' in s or s in ('PARTIAL','GATED') else 'bad'
    return f'<span class="tag {cls}">{esc(s)}</span>'
def table(headers, rows):
    out=['<div class="tablebox"><table><thead><tr>'+''.join(f'<th>{esc(h)}</th>' for h in headers)+'</tr></thead><tbody>']
    for row in rows:
        cells=[]
        for v in row:
            if isinstance(v, Safe): cells.append('<td>'+str(v)+'</td>')
            elif v in (None, ''): cells.append('<td><span class="missing">— UNVERIFIED</span></td>')
            else: cells.append('<td>'+esc(v)+'</td>')
        out.append('<tr>'+''.join(cells)+'</tr>')
    out.append('</tbody></table></div>')
    return ''.join(out)

class Safe(str): pass
def src(url,label='Official source'): return Safe(link(url,label))
def tag(v): return Safe(pill(v))
def fmt(v):
    if isinstance(v,float): return f'{v:.3f}'.rstrip('0').rstrip('.')
    return str(v)
def page(title,lead,body):
    nav=''.join(f'<a href="{u}"'+(' aria-current="page"' if n==title else '')+f'>{esc(n)}</a>' for n,u in NAV)
    return f'''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta name="description" content="NFL Lines: official-source research, model fair values, decision framework and validation gates."><title>{esc(title)} · NFL Lines</title><style>
:root{{--ink:#172638;--muted:#5d6b79;--line:#dce3eb;--panel:#fff;--bg:#f4f7fa;--blue:#165c9f;--green:#087443;--amber:#8d5700;--red:#a32132}}*{{box-sizing:border-box}}body{{margin:0;background:var(--bg);color:var(--ink);font:16px/1.55 system-ui,-apple-system,Segoe UI,sans-serif}}header{{background:#142b43;color:white;padding:18px max(calc((100vw - 1180px)/2),20px)}}.brand{{font-size:19px;font-weight:850;letter-spacing:.02em;color:white;text-decoration:none}}nav{{display:flex;gap:8px;flex-wrap:wrap;margin-top:13px}}nav a{{color:#dce9f6;text-decoration:none;padding:5px 9px;border-radius:7px;font-size:13px}}nav a:hover,nav a[aria-current]{{background:#294968;color:#fff}}main{{max-width:1180px;margin:26px auto;padding:0 18px 56px}}h1{{font-size:clamp(28px,4vw,40px);margin:0 0 5px}}h2{{font-size:22px;margin:0 0 8px}}h3{{font-size:18px;margin:0 0 6px}}.lead{{color:var(--muted);max-width:900px;margin:0 0 18px}}.panel,.card{{background:var(--panel);border:1px solid var(--line);border-radius:13px;padding:18px;margin:14px 0;box-shadow:0 3px 12px #132c4310}}.note{{padding:13px 15px;border-left:4px solid var(--blue);background:#eaf3fc;border-radius:0 9px 9px 0;margin:12px 0}}.warn{{border-color:#bc800d;background:#fff7e8}}.danger{{border-color:var(--red);background:#fff0f1}}.grid{{display:grid;grid-template-columns:repeat(auto-fit,minmax(215px,1fr));gap:12px}}.stat{{font-size:27px;font-weight:800}}.muted,.small{{color:var(--muted)}}.small{{font-size:13px}}.tablebox{{overflow:auto;max-height:680px;border:1px solid var(--line);border-radius:10px;margin:10px 0 16px}}table{{border-collapse:collapse;background:white;width:100%;font-size:13px}}th{{position:sticky;top:0;background:#edf2f7;text-align:left;white-space:nowrap;z-index:1}}td,th{{padding:9px 10px;border-bottom:1px solid #e7ecf1;vertical-align:top}}tbody tr:hover{{background:#f7faff}}a{{color:var(--blue)}}.tag{{display:inline-block;border-radius:30px;padding:2px 8px;font-size:11px;font-weight:800;white-space:nowrap;background:#eef1f4;color:#334}}.good{{background:#e3f5e9;color:var(--green)}}.model{{background:#e7f0fc;color:var(--blue)}}.bad{{background:#fff0d4;color:var(--amber)}}.missing{{color:#864a00;font-style:italic}}.cards{{display:grid;grid-template-columns:repeat(auto-fit,minmax(290px,1fr));gap:12px}}.card{{margin:0}}.card p{{margin:6px 0}}ul{{padding-left:22px}}details{{margin:10px 0}}summary{{cursor:pointer;font-weight:700}}footer{{border-top:1px solid var(--line);padding-top:18px;margin-top:30px;color:var(--muted);font-size:13px}}@media(max-width:650px){{main{{padding:0 12px 40px}}.panel{{padding:13px}}}}
</style></head><body><header><a class="brand" href="nfl-lines.html">NFL LINES · DECISION DESK</a><nav>{nav}</nav></header><main><h1>{esc(title)}</h1><p class="lead">{esc(lead)}</p>{body}<footer>Research and model outputs are not official NFL values or betting advice. Empty values are not guessed. Check the official source and its current version before making a decision. · <a href="README.md">Repository README</a></footer></main></body></html>'''
def write(filename,title,lead,body): (ROOT/filename).write_text(page(title,lead,body),encoding='utf-8')
def box(title,content,cls=''):
    return f'<section class="panel {cls}"><h2>{title}</h2>{content}</section>'
def source_list(urls): return ' · '.join(link(x) for x in dict.fromkeys(u for u in urls if u)) or '<span class="missing">No official source captured — UNVERIFIED</span>'
def integrate_hub():
    """Add/rewrite a links panel on the existing NFL Lines landing without replacing it."""
    path=ROOT/'nfl-lines.html'
    if not path.exists(): return
    text=path.read_text(encoding='utf-8')
    start='<!-- NFL-LINES-DATA-NAV:START -->'; end='<!-- NFL-LINES-DATA-NAV:END -->'
    items=[('Model overview','nfl-lines-overview.html'),('Schedule & results','nfl-schedule.html'),
           ('Fair lines','nfl-fair-lines.html'),('Availability','nfl-availability.html'),
           ('Backtest & luck','nfl-analysis.html'),('Strategies & gates','nfl-strategies.html'),
           ('Leaderboard','nfl-leaderboard.html'),('Suggestions','nfl-suggestions.html'),
           ('Questions','nfl-questions.html'),('Flagged review','nfl-flagged.html'),
           ('Executive summary','NFL-LINES-EXECUTIVE-SUMMARY.md'),
           ('Source/repository audit','research/repo-review-2026-11-13.md'),
           ('Data provenance manifest','data/nfl/manifest.json')]
    block=start+'\n<section class="panel" id="nfl-lines-research"><h2>Research, model outputs &amp; review</h2><p>Expanded decision-support pages. Fair values are model outputs, not market odds; unverified inputs stay blank. The links below preserve the main NFL Lines landing page and add the detailed, source-linked analysis.</p><div class="cards">'+''.join(f'<div class="card"><a href="{u}">{esc(n)}</a></div>' for n,u in items)+'</div></section>\n'+end
    if start in text and end in text:
        before=text.index(start); after=text.index(end,before)+len(end)
        text=text[:before]+block+text[after:]
    else:
        marker='</main>'
        if marker in text: text=text.replace(marker,block+'\n'+marker,1)
        else: text=text.replace('</body>',block+'\n</body>',1)
    path.write_text(text,encoding='utf-8')


def main():
    sched=load('schedule_2026.json'); lines=load('lines.json'); avail=load('deficiency.json'); back=load('backtest.json'); corr=load('correlation.json'); gates=load('gate_results.json'); lb=load('leaderboard.json'); sugg=load('suggestions.json'); dec=load('decisions.json'); strategies=load('strategies.json')
    games=sched['games']; finals=[g for g in games if g.get('status')=='FINAL']; summary=back['summary']
    body='<div class="note warn"><b>Important limits.</b> Fair values below are model-originated, not market odds. This dataset is a captured snapshot, not a live feed. Injury and depth availability is incomplete; unsupported adjustments are left blank. Strategy leaderboard scoring is gated until prices and settled bet records exist. <a href="nfl-flagged.html">Review flagged items</a>.</div>'
    stats=[(len(games),'2026 regular-season schedule rows'),(len(finals),'official completed games with captured scores'),(len(strategies['strategies']),'registered strategies'),(sum(1 for r in lb['rows'] if r.get('eligibility')=='ELIGIBLE'),'strategies eligible for leaderboard points')]
    body+='<div class="grid">'+''.join('<div class="panel"><div class="stat">'+esc(n)+'</div><div class="muted">'+esc(label)+'</div></div>' for n,label in stats)+'</div>' 
    persistence_r = next(x['correlation_r'] for x in corr['season_persistence'] if x['metric']=='net_points_per_game')
    source_summary = '<p>Source: ' + link(SCHEDULE, 'official NFL schedule snapshot') + '; ' + link(STANDINGS, 'official NFL standings') + '.</p>'
    body+=box('What the captured evidence says',f'<ul><li>Home win rate: <b>{fmt(summary["home_field"]["home_win_rate_test"]["mean"]*100)}%</b> across n={summary["home_field"]["home_win_rate_test"]["n"]}; descriptive only.</li><li>Mean home margin: <b>{fmt(summary["home_field"]["mean_home_margin_test"]["mean"])} points</b>; its 95% interval is {fmt(summary["home_field"]["mean_home_margin_test"]["ci95_low"])} to {fmt(summary["home_field"]["mean_home_margin_test"]["ci95_high"])} points, including zero.</li><li>Model R² using the available pre-game features: <b>{fmt(summary["model"]["r_squared"])}</b>; residual margin standard deviation {fmt(summary["model"]["residual_std_points"])} points.</li><li>Season net-point persistence r={fmt(persistence_r)}; this is a descriptive season-to-season correlation, not a direct estimate that any particular bet is skill.</li></ul>'+source_summary)
    body+=box('Decision paths', '<div class="cards">'+''.join(f'<div class="card"><h3><a href="{u}">{n}</a></h3><p>{t}</p></div>' for n,u,t in [('Schedule & results','nfl-schedule.html','Official matchups and captured final results.'),('Fair lines','nfl-fair-lines.html','Model outputs and assumptions; no market prices.'),('Availability','nfl-availability.html','Injury/depth coverage and replacement tiers.'),('Backtest & luck','nfl-analysis.html','Effect sizes, uncertainty and variance controls.'),('Strategies & gates','nfl-strategies.html','Hypotheses and validation blockers.'),('Leaderboard','nfl-leaderboard.html','Reward competition; gated pending prices.'),('Suggestions','nfl-suggestions.html','Prioritized proposals waiting for review.'),('Questions','nfl-questions.html','Known, unknown, contradictory and how to research.'),('Executive summary','NFL-LINES-EXECUTIVE-SUMMARY.md','Findings, blockers, and manual-review links.')])+'</div>')
    body+=box('Provenance and executive summary', '<p><a href="data/nfl/manifest.json">NFL data provenance manifest (SHA-256)</a> · <a href="NFL-LINES-EXECUTIVE-SUMMARY.md">Full executive summary</a> · <a href="research/repo-review-2026-11-13.md">Repository review findings</a>.</p><p class="small">The hash manifest records local artifact fingerprints and source URLs. It explicitly distinguishes official raw snapshots from captures whose response bodies are not stored.</p>')
    body+=box('First decisions to unblock the programme','<ol><li><b>Price source:</b> connect a timestamped bet log or licensed feed; absent that, keep the competition unscored.</li><li><b>Availability:</b> obtain dated official depth captures for all clubs before applying comparative penalties.</li><li><b>Historical panel:</b> capture past official injury reports and time-stamped sources before validating injury strategies.</li><li><b>Exposure policy:</b> set bankroll and weekly risk limits before any competition is actionable.</li></ol>')
    write('nfl-lines-overview.html','Model overview','Executive findings, evidence limits, and decision paths for the NFL Lines program.',body)
    integrate_hub()

    rows=[]
    for g in games:
        status=f'{g.get("status","")} · {g.get("verification","")}'
        result=(f'{g.get("away_score")}–{g.get("home_score")}' if g.get('status')=='FINAL' else '— UNVERIFIED')
        rows.append([g.get('week'),g.get('date') or '— UNVERIFIED',f"{g['away_team']} at {g['home_team']}",result,g.get('kickoff_et') or '— UNVERIFIED',tag(status),Safe(source_list([g.get('source_url'), g.get('snapshot_source_url')]))])
    body=box('2026 regular season',f'<p>Snapshot has {len(games)} distinct scheduled matchups. Week 18 cards have no published date or kickoff; those values remain blank and unverified. The schedule snapshots were retrieved 2026-11-02. Recheck current NFL listings before relying on future dates.</p>'+table(['Week','Date','Matchup','Final score','Kickoff ET','Source status','Row source'],rows))
    sched_source = link('https://www.nfl.com/schedules/2026/by-week/week-1', 'NFL.com official by-week schedule snapshots')
    body+=box('Schedule snapshot provenance',f'<p>{sched_source}</p><p>Every matchup row links to its official NFL game-center URL. Score and status are as parsed from that capture, not a real-time scoreboard.</p>')
    write('nfl-schedule.html','Schedule & results','Official 2026 regular-season matchups, score cards, and explicit gaps.',body)

    rows=[]
    all_lines=lines['lines']+lines['next_week_lines']
    for x in all_lines:
        rows.append([x['week'],x['kickoff_et'],f"{x['away_team']} at {x['home_team']}",x.get('model_fair_spread_home'),x.get('model_fair_total'),x.get('model_home_win_probability'),x.get('market_line') or '— UNVERIFIED',x.get('availability_status'),Safe(source_list([x.get('source_url'), x.get('supporting_source_url')]))])
    pars=lines['model_parameters']
    body=box('Model-originated fair lines',f'<div class="note warn">These are MODEL FAIR VALUES, not market lines. No bookmaker price was captured, so market line, price and edge are blank. Availability adjustments are zero when the source depth chart is missing, and the row explicitly says so.</div><p>Model parameters: {html.escape(json.dumps(pars,ensure_ascii=False))}. These are program assumptions, not official NFL values.</p>'+table(['Week','Kickoff ET','Matchup','Fair home spread (pts)','Fair total (pts)','Home win probability','Market line','Availability coverage','Official row source'],rows))
    body+=box('Interpretation', '<p>Positive home spread means the home side is favoured in the engine’s sign convention. A model number is not a recommendation and cannot be called an edge without a contemporaneous market line and price. The source is linked per game; standings are a supporting input in the raw JSON.</p>')
    write('nfl-fair-lines.html','Fair lines','Model fair spread, total, and home win probability. Not bookmaker lines, and not validated betting advice.',body)

    rows=[]
    for x in avail['rows']:
        inj=x.get('injury_source_url'); dep=x.get('depth_source_url') or ''
        links=source_list([inj,dep])
        rows.append([x.get('week'),x.get('team_full_name'),x.get('player'),x.get('position'),x.get('injury'),x.get('game_status'),x.get('depth_tier') or '— UNVERIFIED',x.get('replacement_tier') or '— UNVERIFIED',x.get('replacement_player') or '— UNVERIFIED',x.get('expected_margin_penalty') or '— UNVERIFIED',x.get('depth_status') or 'UNVERIFIED',Safe(links)])
    body=box('Injury and replacement detail',f'<div class="note warn">Week 10 injury data is a provisional row-level transcription from a point-in-time official NFL report; the values have not yet completed a second independent row-by-row audit. A missing player row does not establish availability; the weekly report does not contain all injured-reserve status. Depth tier, replacement and penalty stay blank where an official chart was not captured. Chart coverage: 3 of 32 clubs verified.</div>'+table(['Week','Club','Player','Position','Injury','Game status','Depth tier','Replacement tier','Replacement','Penalty (model pts)','Depth status','Official sources'],rows))
    body+=box('Coverage and limitations','<ul><li>Official depth chart rows are captured for San Francisco, Miami and Baltimore only. The other 29 clubs are explicitly unverified.</li><li>Second-, third- and fourth-string names are listed only where the official team chart captured them.</li><li>Injury designation and depth-chart rank are separate facts. A replacement is not inferred from an injury alone.</li><li>Official sources: '+source_list([INJURY,'https://www.49ers.com/team/depth-chart','https://www.miamidolphins.com/team/depth-chart','https://www.baltimoreravens.com/team/depth-chart'])+'</li></ul>')
    write('nfl-availability.html','Availability','Official injury designations with replacement-tier coverage; unknown depth remains blank.',body)

    home=summary['home_field']; model=summary['model']; rest=summary['rest']; g11=summary['games_in_11']
    mrows=[]
    for nm,obj in [('Home win rate vs 50% baseline',home['home_win_rate_test']),('Mean home point margin',home['mean_home_margin_test']),('Home had more rest',rest['home_had_more_rest_mean_margin']),('Away had more rest',rest['away_had_more_rest_mean_margin']),('Equal rest',rest['equal_rest_mean_margin']),('Home played 3rd game in 11 days',g11['home_third_game_in_11_mean_margin'])]:
        if obj: mrows.append([nm,obj['n'],fmt(obj['mean']),fmt(obj['ci95_low']),fmt(obj['ci95_high']),fmt(obj.get('z_vs_50pct', obj.get('t_stat', ''))),Safe(source_list(back['summary']['home_field'].get('source_urls',[SCHEDULE])))])
    coeff=[]
    for name,c in model['coefficients'].items(): coeff.append([name,fmt(c['estimate']),fmt(c['stderr']),fmt(c['t_stat']),src(SCHEDULE,'Official schedule/results')])
    pers=[]
    for x in corr['season_persistence']:
        pers.append([x['metric'],x['n_pairs'],fmt(x['correlation_r']),fmt(x['r_squared']),fmt(x['slope_t_stat']),x['status'],Safe(source_list(x.get('source_urls',[x.get('source_url')])))])
    body=box('Descriptive game-level checks', '<div class="note warn">These are exploratory, unadjusted summaries of 120 captured official finals (Weeks 1–8). They do not establish betting value. Interval estimates use a normal approximation; the schedule-feature regression is not a walk-forward betting backtest and has not passed the strategy gates.</div>'+table(['Effect','n','Mean / rate','95% CI low','95% CI high','z / t statistic','Official source'],mrows))
    body+=box('Exploratory multivariable model',f'<p>Outcome: home score margin. Inputs are the pre-game rolling net-point rating gap, rest-day differential and games-in-11-days differential. Rolling team ratings use prior final scores only.</p><p>n={model["n"]}; R²={fmt(model["r_squared"])}; residual SD={fmt(model["residual_std_points"])} points; {fmt(model["residual_variance_share"]*100)}% of observed margin variance remains unexplained.</p>'+table(['Term','Estimate (points)','Std. error','t statistic','Official source'],coeff))
    body+=box('Luck / persistence baseline', '<p>The 2024–2026 team-season panel has one year-to-year transition per club. Net-points-per-game persistence on the complete 2024–2025 panel (32 clubs, one transition) is a context statistic, not an individual wager outcome or a causal skill/luck decomposition.</p>'+table(['Metric','Pairs','Correlation r','r²','Slope t','Status','Official source'],pers))
    body+=box('Read with care','<ul><li>Rest effects are observational: travel, opponent strength, injuries and game quality are not adjusted in the simple subgroup means.</li><li>The home win-rate 95% range uses a large-sample proportion approximation; ties are coded as one-half.</li><li>Multiple comparisons exist; no Holm correction has been applied to these exploratory summaries.</li><li>Game margins are noisy. The model residual standard deviation is an empirical snapshot, not the assumed sigma parameter in the fair-line engine.</li></ul>')
    write('nfl-analysis.html','Backtest & luck','Exploratory descriptive analysis on captured official results. No strategy has been shown profitable.',body)

    rows=[]
    for r in gates['results']:
        rows.append([r['strategy_id'],r['strategy'],r['state'],f"{r['gates_passed']}/{r['gates_total']}",r['reason'] if 'reason' in r else ('Eligible' if r['eligible_for_points'] else 'Gated'),src(r.get('source_url'),'Official source')])
    body=box('Strategy registry', '<p>Hypotheses are registered before evidence of performance. NOT TESTABLE is neither pass nor fail. Gated strategies cannot earn points.</p>'+table(['ID','Strategy','State','Gates passed','Interpretation','Official source'],rows))
    for r in gates['results']:
        details=''.join(f'<details><summary>{esc(g["gate_id"])} · {esc(g["gate"])} — {pill(g["state"])}</summary><p>{esc(g["criterion"])}</p><p>{esc(g["evidence"])}</p></details>' for g in r['gates'])
        body+=f'<section class="panel"><h2>{esc(r["strategy_id"])} · {esc(r["strategy"])}</h2><p>{pill(r["state"])} · {r["gates_passed"]}/{r["gates_total"]} checks passed</p>{details}<p>Source: {link(r.get("source_url"))}</p></section>'
    write('nfl-strategies.html','Strategies & gates','Hypotheses, inputs and the 12 validation gates. A non-testable strategy is not a validated strategy.',body)

    lrows=[]
    for r in lb['rows']:
        lrows.append([r['strategy_id'],r['strategy'],r['bet_class'],r.get('bets_settled') or '— UNVERIFIED',r.get('roi_pct') or '— UNVERIFIED',r.get('points') or '— UNVERIFIED',r.get('rank') or '— UNVERIFIED',tag(r['eligibility']),r.get('reason') or '',src(r.get('source_url'),'Official source')])
    body=box('Leaderboard', '<div class="note warn">No placed-bet log or official prices were supplied. Settled bets, ROI, points and ranks are intentionally blank; no fictional contestants or rewards are shown. Reward tiers are rules only, not currently earned.</div>'+table(['Strategy','Name','Class','Settled bets','ROI','Points','Rank','Eligibility','Why','Source'],lrows))
    rule=load('leaderboard_rules.json')
    rule_source = link(rule.get('source_url'), 'Official settlement results source')
    rule_json = esc(json.dumps({k:rule.get(k) for k in ('scoring','reward_tiers','eligibility_rules')},indent=2,ensure_ascii=False))
    body+=box('Scoring and reward rules',f'<p>Rules source: {rule_source}.</p><pre>{rule_json}</pre><p>Every reward is contingent on passing all required gates. No reward has been awarded.</p>')
    design=lb.get('competition_design', [])
    if design:
        body+=box('Competition design proposals carried forward from the existing NFL Lines module',
                  '<p>These proposals remain proposals; they are not participant results or approved reward terms.</p>'+table(['ID','Element','Proposal','Status','Official source'],[[r.get('id'),r.get('element'),r.get('proposal'),r.get('status'),src(r.get('source_url'),r.get('source_label','Official source'))] for r in design]))
    write('nfl-leaderboard.html','Leaderboard','Reward competition framework; actual scores stay blank until timestamped prices and settled records exist.',body)

    cards=[]
    for s in sorted(sugg['suggestions'], key=lambda item:(item.get('suggested_priority','P9'),item['id'])):
        opts=''.join(f'<li>{esc(o)}</li>' for o in s['options'])
        deps=esc(', '.join(s.get('dependencies',[])) or 'none')
        evidence_links=source_list(s.get('evidence_source_urls', []))
        suggested_priority=esc(s.get('suggested_priority','UNRANKED'))
        cards.append(f'<article class="card"><h2>{esc(s["id"])} · {esc(s["title"])}</h2><p>{pill(s["status"])} · Suggested {suggested_priority} · {esc(s["category"])} · Impact: {esc(s["impact"])} · Effort: {esc(s["effort"])}</p><p><b>Problem:</b> {esc(s["problem"])}</p><p><b>Evidence:</b> {esc(s.get("evidence", "No evidence statement supplied."))}</p><details><summary>Options considered</summary><ol>{opts}</ol></details><p><b>Recommendation:</b> {esc(s["recommendation"])}</p><p><b>Decision needed before implementation:</b> {esc(s["decision_needed"])}</p><p><b>Manual-review sources:</b> {evidence_links}</p><p class="small">Dependencies: {deps}</p></article>')
    body='<div class="note">Suggestions are proposals, not approved changes. Suggested P1/P2 ranks are a review aid based on evidence readiness and decision risk; change the JSON priority before implementation if the review order differs. Each entry names options, impact/effort, a recommendation, official manual-review sources and a decision needed. No proposal is silently implemented by this register.</div><div class="cards">'+''.join(cards)+'</div>'
    write('nfl-suggestions.html','Suggestions','A prioritized change register: proposed improvements remain reviewable before implementation.',body)

    cards=[]
    for d in dec['decisions']:
        known=''.join(f'<li>{esc(x)}</li>' for x in d['information_held']) or '<li>None recorded.</li>'
        missing=''.join(f'<li>{esc(x)}</li>' for x in d['information_missing']) or '<li>None recorded.</li>'
        how=esc(d.get('how_to_obtain','No research path supplied.'))
        urls=[]
        for url in [INJURY,STANDINGS,SCHEDULE,'https://www.49ers.com/team/depth-chart','https://www.miamidolphins.com/team/depth-chart','https://www.baltimoreravens.com/team/depth-chart','https://www.nfl.com/news/2026-27-national-football-league-important-dates']:
            if any(token in (d['decision']+' '+d['why_it_matters']+' '+' '.join(d['information_held'])).lower() for token in (['injur','availability','roster'] if url==INJURY else ['standings','points','persistence'] if url==STANDINGS else ['schedule','game','rest'] if url==SCHEDULE else ['depth','replacement','chart'] if 'depth-chart' in url else ['designation','deadline','rule'] if 'important-dates' in url else [])): urls.append(url)
        answer = esc(d.get('answer') or 'OPEN — no answer recorded.')
        cards.append(f'<article class="card"><h2>{esc(d["id"])} · {esc(d["decision"])}</h2><p>{pill(d["status"])}</p><p><b>Question:</b> {esc(d["question"])}</p><p><b>Why it matters:</b> {esc(d["why_it_matters"])}</p><div class="grid"><div><b>Known</b><ul>{known}</ul></div><div><b>Unknown / contradictory</b><ul>{missing}</ul></div></div><p><b>Research path:</b> {how}</p><p><b>Official manual-review links:</b> {source_list(urls)}</p><p><b>Answer:</b> {answer}</p></article>')
    body='<div class="note warn"><b>Decision framework:</b> Known values are distinguished from missing information. OPEN questions have no default answer. Contradictory claims are explicitly called out in the relevant question; verify at source before resolving. The research path is a suggestion, not evidence that the missing value has been obtained.</div><div class="cards">'+''.join(cards)+'</div>'
    write('nfl-questions.html','Questions','Known, unknown, contradictory and required information before a reasonable decision can be made.',body)

    flagged=[('F-01','Only 3 of 32 clubs have captured, verified depth charts. No other teams receive guessed tiers.','https://www.49ers.com/team/depth-chart'),('F-02','Week 10 Baltimore says no injuries reported while an official roster announcement placed Lamar Jackson on injured reserve. Weekly injury report absence is not proof of availability.','https://www.nfl.com/injuries/league/2026/reg10'),('F-03','No price source or timestamped placed-bet log exists. Market price, edge, ROI, ranks and reward points remain blank.','https://www.nfl.com/schedules/2026/REG1'),('F-04','Week 18 official schedule cards are matchup-only; dates, times and networks are not supplied and are blank.','https://www.nfl.com/schedules/2026/by-week/week-18'),('F-05','Exploratory regression is based on only 120 completed games in Weeks 1–8, with about 79% residual variance; it is not an out-of-sample profitable-strategy test.','https://www.nfl.com/schedules/2026/by-week/week-8'),('F-06','The injury dataset and depth captures are single-snapshot evidence and can be stale; recapture official pages before decisions.','https://www.nfl.com/injuries/league/2026/reg10'),('F-07','The identified standings split and streak discrepancies have been corrected in the CSV; a complete field-by-field comparison against all three annual source tables remains open.','https://www.nfl.com/standings/league/2026/REG'),('F-08','The 298-row Week 10 injury transcription has an official row source but has not completed an independent row-by-row value audit; treat status and name mappings as provisional.','https://www.nfl.com/injuries/league/2026/reg10'),('F-09','The 173-row depth capture covers only 49ers, Dolphins and Ravens; captures are provisional and should be compared with the linked current official charts before applying penalties.','https://www.49ers.com/team/depth-chart')]
    body='<div class="note warn">These flags are non-blocking for publication but material for interpretation. They are published here rather than silently filled. Recheck linked primary sources; do not rely on an old snapshot.</div>'+table(['Flag','Issue / limitation','Manual review — official source'],[[a,b,src(c)] for a,b,c in flagged])
    write('nfl-flagged.html','Flagged review','Open data gaps, irregularities, and model limitations requiring human review.',body)

if __name__=='__main__': main()
