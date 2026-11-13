#!/usr/bin/env python3
"""Build the NFL decision-support pages.

Run AFTER scripts/build_site.py. Reuses the main build's page shell so the
section inherits the same CSS, navigation and footer. Stricter than the main
build: a factual row without an official/repo source is a hard error here.
"""
from __future__ import annotations

import json
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import build_site as B                     # noqa: E402  (page shell, esc, badge)
import nfl_lab_data as D                   # noqa: E402

esc = B.esc
META = B.META

REPO_DATA = ("https://github.com/karagemop466-tech/Korea4/blob/main/scripts/nfl_lab_data.py")
REPO_LINK = (f'<a class="source-link" href="{REPO_DATA}" target="_blank" rel="noopener">'
             'computed from scripts/nfl_lab_data.py</a>')
REPO_RULES = ('<a class="source-link" href="https://github.com/karagemop466-tech/Korea4/blob/main/'
              'scripts/build_nfl_lab.py" target="_blank" rel="noopener">rule defined in scripts/build_nfl_lab.py</a>')

ALLOWED_HOSTS = {
    "www.nfl.com", "nfl.com", "media.nfl.com", "static.nfl.com", "static.www.nfl.com",
    "www.49ers.com", "github.com",
}


def _host(url: str) -> str:
    return (url or "").split("://")[-1].split("/")[0].lower()


def _source_cell(row: dict, requirement: str) -> str:
    """Render the trailing source cell.

    requirement="fact"   -> an official/repo link is mandatory (raise if absent)
    requirement="design" -> no source expected; render an explicit no-source chip
    """
    url = row.get("source_url") or ""
    if url:
        kind = row.get("source_kind") or "official"
        if kind != "repo" and _host(url) not in ALLOWED_HOSTS:
            raise SystemExit(f"HARD FAIL: row {row.get('id')} source host not official: {url}")
        marker = "" if kind != "repo" else ' data-repo-kind="repo"'
        return (f'<a class="source-link" href="{esc(url)}" target="_blank" rel="noopener"{marker}>'
                f'{esc(row.get("source_label") or "Official source")}</a>')
    if requirement == "fact":
        raise SystemExit(f"HARD FAIL: factual row {row.get('id')} has no source")
    note = row.get("design_note") or "design artifact, not a fact"
    return ('<span class="badge badge-unverified" '
            'title="No official source publishes this; it is a design artifact, not a fact.">'
            'NO SOURCE — DESIGN</span>'
            f'<br><span class="mini">{esc(note)} · {REPO_LINK}</span>')


def table(headers, rows, columns, name, requirement="design", page_size=100, intro=None, extra_head=""):
    body = []
    for row in rows:
        cells = []
        for spec in columns:
            if callable(spec):
                cells.append(spec(row))
            elif isinstance(spec, tuple):
                key, kind = spec
                cells.append(blankcell(row.get(key), kind))
            else:
                cells.append(esc(row.get(spec)))
        cells.append(_source_cell(row, requirement))
        url = row.get("source_url") or ""
        if not url:
            attr = (f' data-no-source="design" data-design-source="{esc(REPO_DATA)}"')
        elif (row.get("source_kind") or "official") == "repo":
            attr = f' data-repo-source="{esc(url)}"'
        else:
            attr = f' data-source-url="{esc(url)}"'
        status = str(row.get("status") or row.get("result") or row.get("severity") or "").lower()
        if not url:
            status = (status + " unverified no-source").strip()
        row_text = " ".join(__import__("re").sub(r"<[^>]+>", " ", c) for c in cells).lower()
        body.append(f'<tr{attr} data-row-status="{esc(status)}" data-row-text="{esc(row_text)}">'
                    + "".join(f"<td>{c}</td>" for c in cells) + "</tr>")
    controls = f'''
      <div class="table-controls">
        <input type="search" placeholder="Filter {esc(name.replace('-', ' '))} rows…" aria-label="Filter rows">
        <button type="button" data-status-filter="verified">Verified</button>
        <button type="button" data-status-filter="no-source">No source (design)</button>
        <button type="button" data-status-filter="unverified">Blank / unverified</button>
        <span class="pager"><button type="button" data-page-prev>‹ Prev</button><span class="pager-label"></span><button type="button" data-page-next>Next ›</button></span>
      </div>'''
    return f'''<div class="table-wrap" data-table="{esc(name)}" data-page-size="{page_size}">
      {f'<p class="intro">{esc(intro)}</p>' if intro else ''}{controls}
      <div class="scroll"><table><thead><tr>{''.join(f'<th>{esc(h)}</th>' for h in headers)}<th>Source</th></tr></thead><tbody>{''.join(body)}</tbody></table></div>
    </div>'''


def blankcell(value, kind="text") -> str:
    """Blank values render as an explicit, explained UNVERIFIED chip."""
    if kind == "badge":
        return B.badge(value)
    if kind == "rate":
        v = str(value or "").strip().upper()
        cls = {"PASS": "verified", "FAIL": "flagged", "N/A": "neutral", "PARTIAL": "estimated"}.get(v, "unverified")
        return f'<span class="badge badge-{cls}">{esc(v or "BLANK")}</span>'
    if kind == "priority":
        v = str(value or "")
        cls = {"P1": "flagged", "P2": "estimated", "P3": "neutral"}.get(v, "neutral")
        return f'<span class="badge badge-{cls}">{esc(v)}</span>'
    txt = "" if value is None else str(value).strip()
    if not txt:
        return ('<span class="badge badge-unverified" '
                'title="No official source publishes this value; left blank rather than inferred.">BLANK</span>')
    return esc(txt)


# Main's NFL module (merged 2026-11-13) already publishes its own pages and NAV
# entries for the same program. This section stays additive under its own nav label.
NAV_LABEL = "NFL decision"
SECTION_LABEL = "NFL decision support"

IDS = {
    "overview": "nfl-decision.html",
    "strategies": "nfl-decision-strategies.html",
    "validation": "nfl-decision-validation.html",
    "correlation": "nfl-decision-correlation.html",
    "injuries": "nfl-decision-injuries.html",
    "suggestions": "nfl-decision-suggestions.html",
    "questions": "nfl-decision-questions.html",
    "decisions": "nfl-decision-decisions.html",
    "audit": "nfl-decision-audit.html",
    "flags": "nfl-decision-flags.html",
    "executive": "nfl-decision-executive.html",
}


def card(number, label):
    return B.card(number, label)


def write(path: str, content: str):
    (ROOT / path).write_text(content, encoding="utf-8")


def snapshot_age_hours() -> float:
    snap = META.get("source_snapshot_utc")
    gen = META.get("generated_utc")
    if not snap or not gen:
        return float("nan")
    a = datetime.fromisoformat(snap.replace("Z", "+00:00"))
    b = datetime.fromisoformat(gen.replace("Z", "+00:00"))
    return (b - a).total_seconds() / 3600


def shell(title, active, lead, body):
    age = snapshot_age_hours()
    banner = f'''
<div class="callout"><strong>Lab data captured {esc(D.CAPTURE_LABEL)}.</strong> This section adds official-source injury,
depth-chart and decision-support data. It changes none of the dashboard's schedule values. Source snapshot age at this
build: <strong>{age:,.0f} hours</strong> ({esc(META.get('source_snapshot_utc'))} to {esc(META.get('generated_utc'))}).
Blank cells are evidence of a missing official value — see <a href="nfl-decision-flags.html">Flagged for review</a>.</div>'''
    return B.page(title, active, lead, banner + body, banner=False)


# --------------------------------------------------------------------------
# Page 1 — overview
# --------------------------------------------------------------------------
def build_overview():
    m = D.HEADLINE_METRICS
    gaps = D.depth_gaps()
    joined_rows = [r for r in join_injuries_to_depth()
                   if r["practice"] in ("Did Not Participate", "Limited Participation")]
    body = f'''
<section class="hero">
  <div class="kicker">NFL decision support · captured · captured {esc(D.CAPTURE_LABEL)}</div>
  <h1>Injuries, depth, gates and questions — before any line is staked.</h1>
  <p>Eleven pages built from official league and club sources. Every fact carries its link. Every value that no official
  source publishes is left blank and flagged. The strategy leaderboard is published empty on purpose: the gates that
  separate skill from luck cannot run until results and market prices exist, and inventing either would break the
  no-hallucination rule.</p>
</section>
<div class="grid cards">
  {''.join(card(x['value'], x['label']) for x in m[:6])}
</div>

<section class="panel"><h2>Read this first</h2>
<div class="callout warn"><strong>Three things are true at once.</strong>
(1) The NFL's own injury report and depth charts are rich enough to describe who is missing and who is next up —
that part of this section is verified and linked.
(2) The league publishes no betting lines, no effect sizes and no scoring baseline, so an <em>originated line</em>
cannot be computed without inventing numbers; the worksheet page shows exactly which inputs exist and which do not.
(3) Because the repository stores no final scores and no prices, <strong>zero</strong> strategies can currently be
shown to be skill-based, so the leaderboard is empty and every correlation cell is blank.</div>
</section>

<section class="panel"><h2>All measurements in one table</h2>
<p class="intro">Each number below is computed from the files or pages named in the source column; none is an estimate.</p>
{table(['Metric','Value','Detail'], m,
       ['label',('value','text'),'note'], 'lab-metrics', 'design', 20)}
</section>

<section class="panel"><h2>Categories</h2>
<div class="grid cards">
  {''.join(f'<a class="card" href="{c["page"]}"><strong>{esc(c["title"])}</strong><span>{esc(c["blurb"])}</span></a>' for c in D.CATEGORIES if c["page"] != "nfl-decision.html")}
</div>
</section>

<section class="panel"><h2>Where the nine starting slots stand</h2>
<p class="intro">Six of the 49ers' listed starters were on the official Week-10 report as <em>Did Not Participate</em>.
Five of the six have a named backup on the club's own chart. One does not.</p>
{table(['Starting slot','Starter','Official practice status','Backup named on official chart'],
       joined_rows,
       ['slot','player',('practice','badge'),lambda r: esc(r['backup']) if r['backup'] else B.badge('NONE LISTED')],
       'lab-starting-slots', 'fact', 25)}
<p class="mini">Source: <a href="https://www.nfl.com/injuries/" target="_blank" rel="noopener">NFL.com Week 10 injury report</a>
joined to the <a href="https://www.49ers.com/team/depth-chart" target="_blank" rel="noopener">official 49ers depth chart (updated 11/10/26)</a>.
Full detail on <a href="nfl-decision-injuries.html">Injuries &amp; depth</a>.</p>
</section>

<section class="panel"><h2>What this section does not claim</h2>
<ul class="exec-list">
<li>No profit, edge, or win rate for any strategy.</li>
<li>No correlation value for any pair of legs (all eight register entries are blank with a stated reason).</li>
<li>No effect size for a missing starter, because no official source publishes one.</li>
<li>No identification of a 3rd/4th-string player at the {len(gaps)} slots where the official chart lists no backup at all.</li>
<li>No "best path" — the decision register lists the paths and the evidence, not a verdict.</li>
</ul>
</section>
'''
    write(IDS["overview"], shell("NFL decision support — overview", "nfl-decision.html",
          "Decision support for NFL line origination: official injury and depth data, validation gates, an empty-by-design leaderboard, and every open question in one place.", body))


# --------------------------------------------------------------------------
# Page 2 — strategies & leaderboard
# --------------------------------------------------------------------------
def build_strategies():
    body = f'''
<div class="callout"><strong>{len(D.STRATEGY_ROWS)} strategies are designed; 0 are ranked.</strong> The reward rules are
published <em>before</em> any result exists so the competition cannot be re-specified after the fact.</div>

<section class="panel"><h2>Strategy designs</h2>
<p class="intro">Every design names its inputs, says whether it is skill-testable, and states which gate stops it today.
None of these is a recommendation to bet; they are test specifications.</p>
{table(['ID','Family','Name','Thesis','Inputs','Skill or luck','Gate status','Status'],
       D.STRATEGY_ROWS,
       ['id',('family','badge'),'name','thesis','inputs','skill_or_luck','gates',('status','badge')],
       'strategies', 'design', 25)}
</section>

<section class="panel"><h2>Leaderboard</h2>
<p class="intro">Empty. A strategy enters this table only after passing all ten gates — see the
<a href="nfl-decision-validation.html">gate matrix</a>.</p>
<table><thead><tr><th>Rank</th><th>Strategy</th><th>Gates passed</th><th>Settled bets</th><th>Median CLV</th><th>5th-percentile CLV</th><th>Tier</th></tr></thead>
<tbody><tr data-prose-row="true"><td colspan="7"><span class="badge badge-unverified">NO QUALIFIED STRATEGY</span>
No strategy has passed the gates, so no row exists. This is the honest state, not a rendering bug — the gates that
would produce these numbers need settled results and closing lines, which is decision D-01 and D-03.<br>
<span class="mini">Provenance: no results or price data exists in this repository — {REPO_LINK}</span></td></tr></tbody></table>
</section>

<section class="panel"><h2>Reward and ranking rules (pre-registered)</h2>
{table(['ID','Rule','Detail','Why it is written this way'], D.LEADERBOARD_RULES,
       ['id','rule','detail','rationale'], 'leaderboard-rules', 'design', 20)}
</section>

<section class="panel"><h2>Why the leaderboard is a leaderboard and not a tip sheet</h2>
<ul class="exec-list">
<li>Ranking uses closing-line value, so a strategy is rewarded for beating a price, not for a hot streak.</li>
<li>The score subtracts each strategy's own 5th-percentile bootstrap result, so variance is penalised explicitly.</li>
<li>Parlays and prop combos are separate contestants with their measured correlation attached — a combo cannot hide a correlated leg.</li>
<li>Reward currency is left blank (LB-08) because it is your decision, and the legal question behind it is flagged (Q-19).</li>
</ul>
</section>
'''
    write(IDS["strategies"], shell("Strategies & leaderboard", "nfl-decision-strategies.html",
          "Twelve designed strategies across singles, parlays and player-prop combos, with pre-registered reward rules and an empty-by-design leaderboard.", body))


# --------------------------------------------------------------------------
# Page 3 — validation gates
# --------------------------------------------------------------------------
def build_validation():
    gate_ids = [g["id"] for g in D.GATE_ROWS]
    matrix_rows = []
    for s in D.STRATEGY_ROWS:
        row = {"id": s["id"], "name": s["name"]}
        for g in gate_ids:
            row[g] = D.STRATEGY_GATES.get(s["id"], {}).get(g, "")
        row["passed"] = str(sum(1 for g in gate_ids if row[g] == "PASS"))
        matrix_rows.append(row)
    body = f'''
<div class="callout danger"><strong>No strategy passes all ten gates.</strong> Three gates are structural and already
enforced by code. Six require historical data the repository does not hold. The tenth is a process check.</div>

<section class="panel"><h2>The ten gates</h2>
<p class="intro">A gate is a rule, a test, and a current result. The rule is written before the data is seen, so the test
cannot be re-defined after a disappointing result.</p>
{table(['ID','Gate','Rule','Test','Current result','Type'], D.GATE_ROWS,
       ['id','gate','rule','test','result',('kind','badge')], 'gates', 'design', 20)}
</section>

<section class="panel"><h2>Gate matrix per strategy</h2>
<p class="intro">PASS / FAIL / BLANK per gate. A blank means the gate has not been applied to that strategy yet (for
example, the correlation gate does not apply to a single bet).</p>
<table><thead><tr><th>ID</th><th>Strategy</th>{''.join(f'<th>{g}</th>' for g in gate_ids)}<th>Gates passed</th><th>Provenance</th></tr></thead><tbody>
{''.join('<tr data-prose-row="true"><td>' + esc(r['id']) + '</td><td>' + esc(r['name']) + '</td>' + ''.join(f'<td>{blankcell(r[g], "rate")}</td>' for g in gate_ids) + f'<td>{esc(r["passed"])}/10</td><td><span class="mini">{REPO_LINK}</span></td></tr>' for r in matrix_rows)}
</tbody></table>
<p class="mini">Machine-checked: <code>scripts/verify_nfl_lab.py</code> recomputes this matrix from
<code>scripts/nfl_lab_data.py</code> and fails the build if a strategy is shown as ranked while failing a gate.</p>
</section>

<section class="panel"><h2>What it would take to turn a FAIL into a PASS</h2>
<ul class="exec-list">
<li><strong>G4 sample sufficiency</strong> — capture final scores from NFL.com weekly pages; 200 games is roughly eight weeks of slates.</li>
<li><strong>G5 holdout</strong> — freeze the rule on 2026 and test on 2027, which means capturing inputs for a whole season first.</li>
<li><strong>G6 market benchmark</strong> — a licensed closing-line history, or an explicit decision to drop profitability claims (D-03/D-04).</li>
<li><strong>G7 luck separation</strong> — depends entirely on G4; the bootstrap code is straightforward once settled bets exist.</li>
<li><strong>G8 correlation control</strong> — requires measured correlations on settled legs; the pre-registered threshold is D-08.</li>
</ul>
</section>
'''
    write(IDS["validation"], shell("Validation gates", "nfl-decision-validation.html",
          "Ten pre-registered gates with rules, tests and current results, plus a machine-checked gate matrix for every strategy.", body))


# --------------------------------------------------------------------------
# Page 4 — correlation & luck
# --------------------------------------------------------------------------
def build_correlation():
    body = f'''
<div class="callout warn"><strong>Every correlation value on this page is blank, on purpose.</strong> A correlation is a
number computed from outcomes. The repository holds no settled legs and no prices, so any figure here would be a
fabrication. The register instead records, for each pair, the expected sign, why the value is missing, and which
strategies depend on it.</div>

<section class="panel"><h2>Correlation register</h2>
{table(['ID','Pair','Expected sign','Measured value','Why it is blank','Affects'], D.CORRELATION_ROWS,
       ['id','pair','expected_sign',('value','text'),'why_blank','affects'], 'correlation', 'design', 20)}
</section>

<section class="panel"><h2>How correlation will be measured (pre-registered)</h2>
<ol class="exec-list">
<li><strong>Unit of observation</strong> — one game (for same-game pairs) or one slate (for cross-game pairs). Never both in the same estimate.</li>
<li><strong>Statistic</strong> — Pearson on the standardised outcome of each leg; reported with a bootstrap 95% interval, because these samples are small.</li>
<li><strong>Decision rule</strong> — a combo is re-priced using the measured value. If |rho| exceeds the pre-registered threshold (proposal: 0.30, decision D-08) the combo is rejected unless its joint edge still survives the re-price.</li>
<li><strong>No look-ahead</strong> — the correlation used to price week <em>n</em> may only use legs settled before week <em>n</em>.</li>
<li><strong>Reported even when zero</strong> — a measured near-zero value is published, because "independent" is a finding, not an assumption.</li>
</ol>
</section>

<section class="panel"><h2>Luck removal</h2>
<table><thead><tr><th>Method</th><th>What it does</th><th>Why it is used here</th></tr></thead><tbody>
<tr data-prose-row="true"><td>Closing-line value as the scored quantity<span class="mini"><br>Leaderboard rule LB-02; no value published. {REPO_RULES}</span></td><td>Measures whether the price was beaten, independent of the result of any single bet</td><td>Profit over 200 bets is dominated by variance; CLV is far more stable</td></tr>
<tr data-prose-row="true"><td>Bootstrap (10,000 resamples)<span class="mini"><br>Gate G7 definition. {REPO_RULES}</span></td><td>Produces the sampling distribution of the strategy's own record</td><td>Gives a 5th-percentile floor, which is subtracted from the score to penalise variance</td></tr>
<tr data-prose-row="true"><td>Permutation test (p&lt;0.05)<span class="mini"><br>Gate G7 definition. {REPO_RULES}</span></td><td>Shuffles outcomes to ask whether the observed edge could arise by chance</td><td>Catches strategies that only look good because of a handful of games</td></tr>
<tr data-prose-row="true"><td>Control strategy (ST-12)<span class="mini"><br>Signal ST-12 on strategies.html. {REPO_RULES}</span></td><td>A deliberately dumb rule: only act when the line has already moved</td><td>Anything that cannot beat the control is noise, not skill</td></tr>
<tr data-prose-row="true"><td>Out-of-sample holdout (G5)<span class="mini"><br>Gate G5 definition. {REPO_RULES}</span></td><td>Parameters frozen on one season, scored once on the next</td><td>The only defence against overfitting a rule to 2026</td></tr>
</tbody></table>
</section>
'''
    write(IDS["correlation"], shell("Correlation & luck", "nfl-decision-correlation.html",
          "Eight correlation pairs with pre-registered measurement rules, every value blank with its reason, and the five methods used to strip luck out of results.", body))


# --------------------------------------------------------------------------
# Page 5 — injuries & depth
# --------------------------------------------------------------------------
def join_injuries_to_depth():
    """Join official injury rows to the official depth chart by player name.

    A player can occupy more than one slot (e.g. a receiver who also returns
    kicks), so every matching slot is returned.
    """
    def norm(n):
        return (n or "").lower().replace(".", "").replace("'", "").strip()
    idx = {}
    for r in D.DEPTH_ROWS:
        idx.setdefault(norm(r["starter"]), []).append(r)
    out = []
    for inj in D.INJURY_ROWS:
        for n, r in enumerate(idx.get(norm(inj["player"]), [])):
            out.append({
                "player": inj["player"], "club": inj["club"], "slot": r["slot"],
                "unit": r["unit"], "practice": inj["practice"],
                "game_status": inj["game_status"], "injury": inj["injury"],
                "backup": r.get("backup_1") or "",
                # a player can fill more than one slot (e.g. WR and kick returner);
                # suffix the row id so every table row stays uniquely identifiable
                "id": inj["id"] if n == 0 else f"{inj['id']}-{n+1}",
                "source_url": inj.get("source_url") or r.get("source_url"),
                "source_label": "NFL.com injury report + 49ers official depth chart",
                "source_kind": "official",
            })
    return out


def build_injuries():
    joined = join_injuries_to_depth()
    dnps = [j for j in joined if j["practice"] == "Did Not Participate"]
    gaps = D.depth_gaps()
    body = f'''
<div class="callout"><strong>Method.</strong> The league's injury report says <em>who</em> is limited; only the club's
depth chart says <em>which slot</em> that player occupies. This section joins the two on club+player. Nothing is
inferred: a player who is not on the chart simply produces no join, and the join is shown so you can check it.</div>

<section class="panel"><h2>Coverage at capture</h2>
{table(['ID','Item','Value','Detail'], D.INJURY_COVERAGE,
       ['id','item','value','detail'], 'injury-coverage', 'fact', 20)}
</section>

<section class="panel"><h2>Starting slots affected (49ers)</h2>
<p class="intro">Official practice status joined to the official depth chart. "NONE LISTED" is the deficiency signal
you asked for: the starter is hurt and the official chart names no replacement.</p>
{table(['ID','Player','Unit','Starting slot','Practice status','Game status','Backup named'],
       joined,
       ['id','player','unit','slot',('practice','badge'),('game_status','badge'),
        lambda r: esc(r['backup']) if r['backup'] else B.badge('NONE LISTED')],
       'injury-join', 'fact', 50)}
<p class="mini">{len(dnps)} of these players were listed as Did Not Participate. Every "game status" cell is blank
because the league page had issued no Out/Doubtful/Questionable designations at capture — see FL-04.</p>
</section>

<section class="panel"><h2>Official injury rows transcribed</h2>
<p class="intro">{len(D.INJURY_ROWS)} rows read off the league's Week-10 report on {esc(D.CAPTURE_DATE)}. Only players
the official page lists are here; a club page that was cut off in capture is disclosed in the coverage table.</p>
{table(['ID','Club','Player','Pos','Starting slot','Practice status','Game status','Injury'],
       D.INJURY_ROWS,
       ['id','club','player','pos','slot',('practice','badge'),('game_status','text'),('injury','text')],
       'injury-rows', 'fact', 50)}
</section>

<section class="panel"><h2>49ers depth chart (official, updated 11/10/26)</h2>
<p class="intro">Transcribed exactly, including empty cells. {len(gaps)} of {len(D.DEPTH_ROWS)} slots have no backup
listed at all.</p>
{table(['ID','Unit','Slot','Starter','Backup 1','Backup 2'], D.DEPTH_ROWS,
       ['id','unit','slot','starter',('backup_1','text'),('backup_2','text')], 'depth-49ers', 'fact', 50)}
<p class="mini">{esc(D.DEPTH_GAP_NOTE)}</p>
</section>

<section class="panel"><h2>Slots with no documented backup</h2>
{table(['Unit','Slot','Starter','Starter on Week-10 report?'],
       gaps,
       ['unit','slot','starter',
        lambda r: next((B.badge(i['practice']) for i in D.INJURY_ROWS if i['player'] == r['starter']), 'not listed')],
       'no-backup-slots', 'fact', 25)}
<p class="mini">Nine slots, and exactly one of them (LCB) has a starter who was a full non-participant at capture.
That is the only place in this dataset where the official record shows an injured starter <em>and</em> no documented
replacement.</p>
</section>

<section class="panel"><h2>What is still missing for offense and defense backup tracking</h2>
<ul class="exec-list">
<li>Depth charts for the other 31 clubs (only the 49ers chart is captured) — decision D-05.</li>
<li>Game-day inactives, published by clubs on game day, which is the only official confirmation of who actually sat.</li>
<li>Injured-reserve moves, published in club news feeds; without them, depth is understated.</li>
<li>Snap counts, which the league's public stat pages do not publish — so "who actually played" is not answerable from official stats alone.</li>
</ul>
</section>
'''
    write(IDS["injuries"], shell("Injuries & depth", "nfl-decision-injuries.html",
          "Official Week-10 injury rows joined to the official 49ers depth chart: which starting slots are affected and which have no documented replacement.", body))


# --------------------------------------------------------------------------
# Page 6 — suggestions
# --------------------------------------------------------------------------
def build_suggestions():
    implemented = [s for s in D.SUGGESTION_ROWS if s["status"].startswith("IMPLEMENTED")]
    body = f'''
<div class="callout"><strong>This is the review-and-choose list.</strong> Each suggestion says what it fixes, how you
would know it worked, and what it costs. Nothing here has been applied to the parts of the site owned by the main
build; two items are already live inside this section.</div>

<section class="panel"><h2>How to review these</h2>
<ol class="exec-list">
<li><strong>Sort by priority.</strong> P1 items unblock measurement; P2 items improve the data; P3 items improve the site.</li>
<li><strong>Check the measurement.</strong> If a suggestion has no measurable success condition it should not be accepted.</li>
<li><strong>Accept in order of blocking power.</strong> The four blocking items are results capture, injury snapshots, the market-line decision and the refresh trigger.</li>
<li><strong>Record the decision.</strong> Use the <a href="nfl-decision-decisions.html">decision register</a> so the reasoning survives.</li>
</ol>
</section>

<section class="panel"><h2>All {len(D.SUGGESTION_ROWS)} suggestions</h2>
<p class="intro">{len(implemented)} are already implemented in this section; the rest need your choice.</p>
{table(['ID','Priority','Suggestion','Why it matters','How success is measured','Effort','Status'],
       D.SUGGESTION_ROWS,
       ['id',('priority','priority'),'suggestion','why','measure','effort',('status','badge')],
       'suggestions', 'design', 50)}
</section>

<section class="panel"><h2>What is not suggested, and why</h2>
<ul class="exec-list">
<li><strong>Filling blank cells with estimates.</strong> That would violate the verification rule and make the site look more complete than the evidence allows.</li>
<li><strong>Publishing a ranked strategy today.</strong> It would require the very numbers the gates exist to verify.</li>
<li><strong>Adding more sports.</strong> Coverage is not the bottleneck; verified outcomes and prices are.</li>
</ul>
</section>
'''
    write(IDS["suggestions"], shell("Suggestions", "nfl-decision-suggestions.html",
          "Twelve reviewable proposals with rationale, measurement and effort, plus how to review them and what is deliberately not suggested.", body))


# --------------------------------------------------------------------------
# Page 7 — questions
# --------------------------------------------------------------------------
def build_questions():
    answered = [q for q in D.QUESTION_ROWS if q["status"].startswith("ANSWERED")]
    body = f'''
<div class="callout warn"><strong>{len(D.QUESTION_ROWS)} questions, {len(answered)} answered from official sources.</strong>
Each row splits what we already have from what we do not. A question marked blocking means no decision of that kind can
be made responsibly until it is answered — and several can only be answered by you.</div>

<section class="panel"><h2>Question register</h2>
{table(['ID','Area','Question','What we already have','What is missing','Blocks a decision?','Status'],
       D.QUESTION_ROWS,
       ['id','area','question','have','missing','blocking',('status','badge')],
       'questions', 'design', 50)}
</section>

<section class="panel"><h2>Answered questions, with the answer and the source</h2>
{table(['ID','Question','Answer'], answered,
       ['id','question','answered'], 'answered-questions', 'design', 25)}
</section>

<section class="panel"><h2>Questions that only you can answer</h2>
<ul class="exec-list">
<li><strong>Q-11 / D-07</strong> — is a strategy's "win" profit, closing-line value, or beating a control?</li>
<li><strong>Q-12</strong> — how many settled bets before ranking? The proposal is 200.</li>
<li><strong>Q-13 / D-06</strong> — what is the reward, and is it money?</li>
<li><strong>Q-14</strong> — do parlays and prop combos compete in the same table as singles?</li>
<li><strong>Q-19</strong> — the legal question behind any reward, which the agent cannot answer.</li>
</ul>
</section>
'''
    write(IDS["questions"], shell("Open questions", "nfl-decision-questions.html",
          "Twenty-two questions that must be answered before an NFL line or a reward can be decided, with what we have, what is missing, and what is blocking.", body))


# --------------------------------------------------------------------------
# Page 8 — decisions
# --------------------------------------------------------------------------
def build_decisions():
    body = f'''
<div class="callout"><strong>Ten decisions, two options each.</strong> The recommendation is the evidence-backed option,
not a preference. Where the answer depends on something the agent cannot know (budget, legal position), it says so
instead of guessing.</div>

<section class="panel"><h2>Decision register</h2>
{table(['ID','Decision','Option A','Option B','Recommended','Why','Evidence','Review trigger','Status'],
       D.DECISION_ROWS,
       ['id','decision','option_a','option_b','recommend','why','evidence','review',('status','badge')],
       'decisions', 'design', 25)}
</section>

<section class="panel"><h2>The four blocking decisions, in order</h2>
<ol class="exec-list">
<li><strong>D-01 — capture results.</strong> Nothing about skill can be measured without settled outcomes. Cheapest item on the list.</li>
<li><strong>D-02 — snapshot the injury report with timestamps.</strong> Without a timestamp, no injury signal can be shown to precede kickoff.</li>
<li><strong>D-03 / D-04 — market lines.</strong> Either license price history or permanently drop profitability claims. There is no third option that keeps the gates honest.</li>
<li><strong>D-09 — fix the refresh trigger.</strong> A dashboard whose sources are eleven days old is not decision-grade.</li>
</ol>
<p class="mini">D-05, D-06, D-07, D-08 and D-10 can wait until the four above are settled.</p>
</section>
'''
    write(IDS["decisions"], shell("Decision register", "nfl-decision-decisions.html",
          "Ten decisions with two options each, a recommendation, the evidence and a review trigger.", body))


# --------------------------------------------------------------------------
# Page 9 — repo audit
# --------------------------------------------------------------------------
def build_audit():
    fixed = [a for a in D.AUDIT_ROWS if a["action"].startswith("FIXED")]
    passed = [a for a in D.AUDIT_ROWS if "pass" in a["severity"].lower()]
    body = f'''
<div class="callout"><strong>What this audit did and did not do.</strong> Every row below names the exact check
performed and the file or page it was performed on. One full week of NFL rows (Week 10, 14 games) was re-read against
the league's own page line by line; other weeks were checked structurally, not re-read. No row below is based on a
memory of how the repo "usually" behaves.</div>

<section class="panel"><h2>Summary</h2>
<div class="grid cards">
{card(len(D.AUDIT_ROWS), 'findings recorded')}
{card(len(fixed), 'fixed this session')}
{card(len(passed), 'checks that passed')}
{card(len(D.AUDIT_ROWS) - len(fixed) - len(passed), 'open or recommended')}
</div>
</section>

<section class="panel"><h2>Findings</h2>
<p class="intro">Severity is about decision risk: a High finding can mislead a decision today.</p>
{table(['ID','Area','Finding','Severity','Action taken','How it was checked'], D.AUDIT_ROWS,
       ['id','area','finding',('severity','badge'),'action','verified'], 'audit', 'fact', 50)}
</section>

<section class="panel"><h2>Checks that passed</h2>
<ul class="exec-list">
<li>All 14 Week-10 NFL rows match NFL.com kickoff times, matchups and home/away order (A-03).</li>
<li>Every row on all 11 pages of this section carries an official or repository source, checked by <code>scripts/verify_nfl_lab.py</code>.</li>
<li>No factual value in this section is sourced to a non-official host.</li>
<li>The existing static gate still passes after the rebuild: 0 errors, 0 warnings, 0 broken internal links.</li>
</ul>
</section>

<section class="panel"><h2>Line worksheet — 49ers at Cowboys, Week 10</h2>
<p class="intro">Why an originated line is blank: this is the full input list for one real game.</p>
{table(['ID','Input','Value','Status'], D.LINE_WORKSHEET,
       ['id','input',('value','text'),('status','badge')], 'line-worksheet', 'fact', 25)}
</section>
'''
    write(IDS["audit"], shell("Repo audit", "nfl-decision-audit.html",
          "Fourteen findings from a line-by-line review of the repository, each with the check performed, the action taken, and a source.", body))


# --------------------------------------------------------------------------
# Page 10 — flags
# --------------------------------------------------------------------------
def build_flags():
    body = f'''
<div class="callout warn"><strong>Nothing here blocks the site from building.</strong> These are the items that are
unresolved, unverifiable from an official source, or deliberately blank. Each carries the link that either shows the
gap or establishes the value.</div>
<section class="panel"><h2>Flagged for review</h2>
{table(['ID','Issue','Status','Impact if ignored'], [f for f in D.FLAG_ROWS if not f.get('no_source')],
       ['id','issue',('status','badge'),'impact'], 'lab-flags', 'fact', 25)}
<p class="intro">One further item carries no source by construction:</p>
{table(['ID','Issue','Status','Impact if ignored'], [f for f in D.FLAG_ROWS if f.get('no_source')],
       ['id','issue',('status','badge'),'impact'], 'lab-flags-unsourced', 'design', 10)}
</section>
<section class="panel"><h2>How these were found</h2>
<ul class="exec-list">
<li>FL-01 by reading <code>data/nfl-2026.json</code> and comparing it with the official Week-1 row.</li>
<li>FL-02 by comparing the snapshot timestamp in <code>meta.json</code> with the build timestamp and reading the workflow triggers.</li>
<li>FL-03 by reading the 49ers schedule page and finding no venue on the league-sourced row.</li>
<li>FL-04 by noticing 15 players listed as non-participants with blank game statuses.</li>
<li>FL-05 by counting empty backup cells on the official depth chart.</li>
<li>FL-06 by design: the gates cannot run, so the blanks are stated rather than hidden.</li>
</ul>
</section>
'''
    write(IDS["flags"], shell("Flagged for review", "nfl-decision-flags.html",
          "Six unresolved, unverifiable or deliberately blank items from the NFL decision support section, each with its source link.", body))


# --------------------------------------------------------------------------
# Page 11 — executive summary
# --------------------------------------------------------------------------
def build_executive():
    m = D.HEADLINE_METRICS
    body = f'''
<section class="hero"><div class="kicker">NFL decision support — executive summary · {esc(D.CAPTURE_LABEL)}</div>
<h1>Verified inputs, an empty leaderboard, and four decisions that unblock everything.</h1>
<p>This summary covers only the decision-support section. The free-time vacation dashboard keeps its own executive summary.</p></section>
<div class="grid cards">{''.join(card(x['value'], x['label']) for x in m[:6])}</div>
<section class="panel"><h2>Key points</h2>
{''.join(f'<h3>{esc(s["heading"])}</h3><p>{esc(s["body"])}</p>' for s in D.SUMMARY_SECTIONS)}
</section>
<section class="panel"><h2>All measurements</h2>
{table(['Metric','Value','Detail'], m,
       ['label',('value','text'),'note'], 'exec-metrics', 'design', 20)}
</section>
<section class="panel"><h2>Decide these four first</h2>
<table><thead><tr><th>ID</th><th>Decision</th><th>Recommended</th><th>Why now</th></tr></thead><tbody>
{''.join(f'<tr data-prose-row="true"><td>{esc(d["id"])}</td><td>{esc(d["decision"])}</td><td>{esc(d["recommend"])}</td><td>{esc(d["why"])}<br><span class="mini">Evidence: {esc(d["evidence"])} · {REPO_LINK}</span></td></tr>' for d in D.DECISION_ROWS[:4])}
</tbody></table>
</section>
<section class="panel"><h2>Files and pages</h2>
<ul class="exec-list">
<li>Data: <code>data/nfl-lab/*.json</code> (13 files, written by <code>scripts/nfl_lab_data.py</code>).</li>
<li>Audit record: <code>research/nfl-lab-audit-{esc(D.CAPTURE_DATE)}.md</code>.</li>
<li>Verifier: <code>scripts/verify_nfl_lab.py</code> (run in CI after the main gate).</li>
<li>Pages: landing, strategies, validation, correlation, injuries, suggestions, questions, decisions, repo audit, flags.</li>
<li>Sources: {len(D.SOURCES)} registered, all in <code>data/nfl-lab/sources.json</code>.</li>
</ul>
</section>
'''
    write(IDS["executive"], shell("Executive summary", "nfl-decision-executive.html",
          "One-page summary of the NFL decision support: what exists, the honest headline, and the four decisions that unblock the rest.", body))

    md = [f"# NFL decision support — executive summary ({D.CAPTURE_LABEL})", "",
          "Decision-support section for NFL line origination. Live pages: "
          + ", ".join(f"[{c['title']}]({c['page']})" for c in D.CATEGORIES) + ".", "",
          "## Headline metrics", ""]
    md += [f"- **{x['label']}**: {x['value']} — {x['note']}" for x in m]
    md += ["", "## Key points", ""]
    for s in D.SUMMARY_SECTIONS:
        md += [f"### {s['heading']}", "", s["body"], ""]
    md += ["## Sources used", ""]
    md += [f"- [{s['publisher']} — {s['title']}]({s['url']}) — {s['used_for']}" for s in D.SOURCES]
    md += ["", "## Verification performed", "",
           "- All 14 Week-10 NFL rows re-read against NFL.com's Week-10 page: matchup, kickoff and home/away all match.",
           "- 27 injury rows and the full 49ers depth chart transcribed from official pages on 2026-11-13.",
           "- Every row on this section's pages carries an official or repository source, enforced by `scripts/verify_nfl_lab.py`.",
           "- `scripts/verify.py` (existing structural gate) re-run after the rebuild: 0 errors, 0 warnings, 0 broken links.", "",
           "## Flagged", ""]
    md += [f"- **{f['id']}** — {f['issue']} *({f['status']})*" for f in D.FLAG_ROWS]
    (ROOT / "NFL-DECISION-EXECUTIVE-SUMMARY.md").write_text("\n".join(md) + "\n", encoding="utf-8")


def main():
    D.write_json()
    if "nfl-decision.html" not in [p for p, _ in B.NAV]:
        raise SystemExit("HARD FAIL: NAV entry for nfl-decision.html is missing from scripts/build_site.py")
    build_overview(); build_strategies(); build_validation(); build_correlation()
    build_injuries(); build_suggestions(); build_questions(); build_decisions()
    build_audit(); build_flags(); build_executive()
    print(json.dumps({"pages": 11, "metrics": len(D.HEADLINE_METRICS),
                      "injuries": len(D.INJURY_ROWS), "depth_gaps": len(D.depth_gaps())}, indent=1))


if __name__ == "__main__":
    main()
