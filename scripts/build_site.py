#!/usr/bin/env python3
"""Generate the clean static FREE TIME VACATION dashboard from official data."""
from __future__ import annotations

import html
import json
import re
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
META = json.loads((ROOT / "data/official/meta.json").read_text())
EVENTS = json.loads((ROOT / "data/official/events.json").read_text())
REVIEW = json.loads((ROOT / "research/line_by_line.json").read_text())
DAYS_2026 = json.loads((ROOT / "data/official/days-2026.json").read_text())
FREE_RUNS = json.loads((ROOT / "data/official/free-runs.json").read_text())
OTHER_SPORTS_PATH = ROOT / "data/official/other-sports.json"
OTHER_SPORTS = json.loads(OTHER_SPORTS_PATH.read_text()) if OTHER_SPORTS_PATH.exists() else None
SOURCES = META["source_catalogue"]
DEFAULT_SOURCE = SOURCES[0]["url"] if SOURCES else "https://statsapi.mlb.com/api/v1/schedule?sportId=1&season=2027"

NAV = [
    ("index.html", "Dashboard"), ("daily.html", "Daily scoreboard"), ("calendar.html", "Calendar"),
    ("vacation.html", "Vacation windows"), ("free-runs.html", "Longest free runs"),
    ("mlb.html", "MLB"), ("nfl.html", "NFL"),
    ("ncaaf.html", "Stanford / Cal"), ("wwo.html", "Westwood One"), ("radio.html", "Radio map"),
    ("sources.html", "Sources"), ("flagged.html", "Flagged"), ("methodology.html", "Method"),
    ("review.html", "Repo review"), ("executive-summary.html", "Executive summary"),
]

PAGES_WITH_ARIA = {p for p, _ in NAV}


def esc(v) -> str:
    return html.escape(str(v if v is not None else ""), quote=True)


def badge(value, kind=None) -> str:
    text = str(value or "UNVERIFIED")
    up = text.upper()
    cls = kind or "neutral"
    if kind is None:
        if "UNVERIFIED" in up or "TBD" in up or "NOT RELEASED" in up: cls = "unverified"
        elif "ESTIMATED" in up or "MODEL" in up: cls = "estimated"
        elif "VERIFIED" in up: cls = "verified"
        elif "FOCUS" in up: cls = "focus"
        elif "HIGH" in up: cls = "high"
        elif "CORRECTED" in up: cls = "corrected"
        elif "FLAGGED" in up or "REPLACED" in up: cls = "flagged"
        elif "REVIEWED" in up: cls = "reviewed"
    return f'<span class="badge badge-{cls}">{esc(text)}</span>'


def blank(value, status="UNVERIFIED") -> str:
    if value is None or str(value).strip() == "" or "TBD" in str(value).upper():
        return f'<span class="badge badge-unverified" title="{esc(status)}">UNVERIFIED</span>'
    return esc(value)


def listval(value) -> str:
    if isinstance(value, list):
        return esc(", ".join(str(v) for v in value)) if value else badge("BLANK / UNVERIFIED", "unverified")
    return esc(value)


def num(value) -> str:
    if value is None or value == "":
        return badge("BLANK / UNVERIFIED", "unverified")
    return f'<span class="num">{esc(value)}</span>'


def status_of(row: dict) -> str:
    for key in ("verification", "status", "time_status", "planning_status", "duration_status"):
        value = row.get(key)
        if value:
            return str(value)
    return "UNVERIFIED"


def source_of(row: dict) -> str:
    for key in ("source_url", "url", "source_api", "planning_source_url", "duration_source_url"):
        value = row.get(key)
        if isinstance(value, list) and value:
            return str(value[0])
        if value:
            return str(value)
    urls = row.get("source_urls")
    if isinstance(urls, list) and urls:
        return str(urls[0])
    return DEFAULT_SOURCE


def cell(row: dict, spec) -> str:
    if callable(spec):
        return spec(row)
    if isinstance(spec, tuple):
        key, kind = spec
    else:
        key, kind = spec, "text"
    value = row.get(key, "")
    if kind == "badge": return badge(value)
    if kind == "blank": return blank(value, status_of(row))
    if kind == "num": return num(value)
    if kind == "list": return listval(value)
    if kind == "status": return badge(status_of(row))
    if kind == "time": return blank(value)
    if kind == "text": return esc(value)
    if kind == "raw": return str(value)
    return esc(value)


def table(headers, rows, columns, name, page_size=100, intro=None, with_source=True):
    body = []
    for row in rows:
        cells = [cell(row, c) for c in columns]
        source_url = source_of(row)
        source_label = row.get("source_label") or row.get("source_label_") or "Official source"
        if with_source:
            cells.append(f'<a class="source-link" href="{esc(source_url)}" target="_blank" rel="noopener">{esc(source_label)}</a>')
        row_text = " ".join(re.sub(r"<[^>]+>", " ", c) for c in cells).lower()
        status = status_of(row).lower()
        attrs = f' data-source-url="{esc(source_url)}" data-row-status="{esc(status)}"' if with_source else f' data-row-status="{esc(status)}"'
        body.append(f'<tr{attrs} data-row-text="{esc(row_text)}">' + "".join(f"<td>{c}</td>" for c in cells) + "</tr>")
    controls = f'''
      <div class="table-controls">
        <input type="search" placeholder="Filter {esc(name.replace('-', ' '))} rows…" aria-label="Filter rows">
        <button type="button" data-status-filter="verified">Verified</button>
        <button type="button" data-status-filter="estimated">Estimated</button>
        <button type="button" data-status-filter="unverified">Unverified</button>
        <span class="pager"><button type="button" data-page-prev>‹ Prev</button><span class="pager-label"></span><button type="button" data-page-next>Next ›</button></span>
      </div>'''
    return f'''<div class="table-wrap" data-table="{esc(name)}" data-page-size="{page_size}">
      {f'<p class="intro">{esc(intro)}</p>' if intro else ''}{controls}
      <div class="scroll"><table><thead><tr>{''.join(f'<th>{esc(h)}</th>' for h in headers)}{'<th>Official source</th>' if with_source else ''}</tr></thead><tbody>{''.join(body)}</tbody></table></div>
    </div>'''


def page(title, active, lead, body, extra_head=""):
    nav = "".join(f'<a href="{p}" class="{"active" if p == active else ""}"{" aria-current=page" if p == active else ""}>{esc(label)}</a>' for p, label in NAV)
    meta_small = {
        "system_today": META.get("system_today"), "date_range": META.get("date_range"),
        "data_start": META.get("data_start"), "counts": META.get("counts", {}),
        "durations": META.get("durations", {}), "default_source_url": DEFAULT_SOURCE,
        "timezone": META.get("timezone"),
    }
    return f'''<!doctype html>
<html lang="en"><head>
<meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{esc(title)} — FREE TIME VACATION</title>
<meta name="description" content="Official-source Bay Area sports radio free-time dashboard, 2026–2029.">
<link rel="stylesheet" href="css/style.css">
{extra_head}
<script>window.K4_META={json.dumps(meta_small, separators=(',',':'))};</script>
<script src="js/app.js" defer></script>
</head><body>
<header class="topbar"><div class="topbar-inner">
  <a class="brand" href="index.html">FREE TIME VACATION</a>
  <span class="tz">America/Los_Angeles · PST/PDT · 94122 AM/FM</span>
  <nav class="main-nav">{nav}</nav>
</div></header>
<main>
  <h1 class="page-title">{esc(title)}</h1>
  <p class="page-lead">{lead}</p>
  <div class="callout warn"><strong>Snapshot, not a live feed.</strong> Data captured {esc(META["generated_utc"])}. Schedules, broadcast carriage and actual game lengths can change; some sports and future schedules are missing. Gaps are planning estimates, not verified free time. Check the <a href="flagged.html">review flags</a> and original sources before booking.</div>
  {body}
  <footer class="footer">
    <strong>Every table row links to an official source.</strong> Blank official values are flagged UNVERIFIED. Estimates are never presented as released schedules.<br>
    <a href="docs/index.html">Docs HTML edition (parallel session)</a>
    <a href="site/index.html">Legacy anchor site</a>
    <a href="site/pages/sources.html">Legacy category pages</a>
    <a href="data/official/events.json">Raw official event JSON</a>
    <a href="research/line_by_line.json">Line-by-line audit JSON</a>
    <br><span class="mini">Built {esc(META['generated_utc'])} from {len(SOURCES)} captured official-source records. Deployment: GitHub Pages <code>main:/</code>.</span>
  </footer>
</main></body></html>'''


def fmt_hm(m):
    m = max(0, min(1440, int(m)))
    return f"{m//60:02d}:{m%60:02d}"


def merge(rows):
    out = []
    for r in sorted(rows, key=lambda x: (x["start"], x["end"])):
        r = dict(r)
        if out and r["start"] <= out[-1]["end"]:
            out[-1]["end"] = max(out[-1]["end"], r["end"])
        else:
            out.append(r)
    return out


def free_windows(busy):
    free, cursor = [], 0
    for b in busy:
        if b["start"] > cursor: free.append({"start": cursor, "end": b["start"]})
        cursor = max(cursor, b["end"])
    if cursor < 1440: free.append({"start": cursor, "end": 1440})
    return free


def nearest_source(rows, pos):
    if not rows: return {"source_url": DEFAULT_SOURCE, "source_label": "Official source catalogue"}
    return min(rows, key=lambda r: min(abs(r["start"]-pos), abs(r["end"]-pos)))


def free_rows_for_today():
    rows = merge(DAYS_2026.get(META["system_today"], []))
    free = free_windows(rows)
    out = []
    for f in free:
        src = nearest_source(rows, f["start"])
        out.append({
            "start": fmt_hm(f["start"]), "end": fmt_hm(f["end"]),
            "minutes": f["end"]-f["start"], "status": "ESTIMATED GAP — UNVERIFIED",
            "source_url": src.get("source_url", DEFAULT_SOURCE),
            "source_label": src.get("source_label", "Bounding official game source"),
            "verification": "ESTIMATED / UNVERIFIED",
        })
    return out


def card(number, label):
    return f'<div class="card"><div class="number">{esc(number)}</div><div class="label">{esc(label)}</div></div>'


def write(path: str, content: str):
    (ROOT / path).write_text(content, encoding="utf-8")


def preserve_legacy():
    legacy = ROOT / "research" / "legacy"
    legacy.mkdir(parents=True, exist_ok=True)
    for src, dst in [("EXECUTIVE-SUMMARY.md", "EXECUTIVE-SUMMARY-97161ae7.md"), ("README.md", "README-before-final-integration.md")]:
        p = ROOT / src
        if p.exists() and not (legacy / dst).exists():
            (legacy / dst).write_text(p.read_text("utf-8", "replace"), encoding="utf-8")



def safe_findings():
    rows = [dict(row) for row in META["findings"]]
    for row in rows:
        if row["topic"] == "Official 2026 NFL regular season":
            row.update(finding="272 captured regular-season matchup rows, including 24 with TBD kickoff/date; consult the individual rows and their sources.", status="UNVERIFIED — AGGREGATE NOT INDEPENDENTLY RECHECKED")
    return rows

def build_index():
    c = META["counts"]
    today_rows = free_rows_for_today()
    findings_rows = safe_findings()
    window_rows = META["vacation_windows"]
    flag_rows = META["flags"][:8]
    source_rows = SOURCES[:8]
    body = f'''
<section class="hero">
  <div class="kicker">Official-source verified dashboard · 2026–2029</div>
  <h1>Find a minute with no live sports radio.</h1>
  <p>Strict free-time planning for standard AM/FM radio in Outer Sunset, San Francisco 94122. All MLB clubs, all released NFL games, 49ers, Stanford, Cal, Westwood One Sports, and other confirmed Bay Area radio games are tracked. Every table row carries an official link; unverified values stay blank and flagged.</p>
</section>
<div class="grid cards">
  {card(c['official_event_rows'], 'official event / anchor rows')}
  {card(c['official_sources'], 'captured official sources')}
  {card(c['days'], 'daily scoreboards')}
  {card(c['mlb_teams'], 'all 30 MLB clubs')}
  {card(c['line_by_line_audit_rows'], 'prior data lines reviewed')}
</div>
<div class="callout warn"><strong>Read this first.</strong> 2028/2029 MLB and NFL game-by-game schedules are not officially released. The site shows ESTIMATED planning models separately; they are not real verified released schedules. TBD official start times are blank with UNVERIFIED flags.</div>
<section class="panel"><h2>Snapshot example: estimated Pacific gaps</h2><p class="intro">{esc(META['system_today'])} · America/Los_Angeles · computed from merged official busy intervals and flagged planning estimates.</p>
{table(['Start PT','End PT','Free minutes','Status'], today_rows, ['start','end',('minutes','num'),('status','badge')], 'today-free', 20)}
<p><a class="control-btn" href="daily.html?date={esc(META['system_today'])}">Open scoreboard for snapshot date →</a></p></section>
<section class="panel"><h2>Executive findings</h2><p class="intro">Every finding links to the official source used. Full analysis is on the Executive Summary and Methodology pages.</p>
{table(['Topic','Finding','Status'], findings_rows, ['topic','finding',('status','badge')], 'findings', 20)}</section>
{free_runs_panel(compact=True)}
<section class="panel"><h2>Best 1-, 2-, and 3-week candidates</h2><p class="intro">Least-conflict windows from exact official rows plus separately labelled unreleased-season models. “Strict free” means zero busy blocks; no window is certified free until future schedules are released.</p>
{table(['Year','Length','Start','End','Busy days','Strict free','Status'], window_rows, ['year',('length_days','num'),'start','end',('busy_days','num'),('strict_free','text'),('status','badge')], 'best-windows', 20)}</section>
<section class="panel"><h2>Flagged irregularities</h2>{table(['ID','Issue','Status','Action'], flag_rows, ['id','issue',('status','badge'),'action'], 'flags-index', 20)}
<p><a class="control-btn" href="flagged.html">See all {len(META['flags'])} flags →</a></p></section>
<section class="panel"><h2>Official sources for manual review</h2>{table(['ID','Title','Purpose','HTTP','Status'], source_rows, ['id','title','purpose',('http_status','num'),('status','badge')], 'sources-index', 20)}
<p><a class="control-btn" href="sources.html">See all {len(SOURCES)} sources →</a></p></section>
'''
    write("index.html", page("Dashboard", "index.html", "Dashboard with executive summary, estimated gaps, and category navigation.", body))


def build_daily():
    body = f'''
<section class="panel"><h2>Date controls</h2>
  <div class="day-nav">
    <button type="button" data-day-step="-1">← Yesterday</button>
    <button type="button" id="today-btn">Today</button>
    <button type="button" data-day-step="1">Tomorrow →</button>
    <label>Date <input type="date" id="selected-date" min="{esc(META['date_range'][0])}" max="{esc(META['date_range'][1])}" value="{esc(META['system_today'])}"></label>
  </div>
  <div class="controls-grid">
    <label><input class="filter-toggle" type="checkbox" id="show-tbd" checked> TBD planning estimates</label>
    <label><input class="filter-toggle" type="checkbox" id="show-models" checked> Unreleased-season models</label>
    <label><input class="filter-toggle" type="checkbox" id="show-unverified" checked> Unverified blocks</label>
    <label><input class="filter-toggle" type="checkbox" data-cat="MLB" checked> MLB</label>
    <label><input class="filter-toggle" type="checkbox" data-cat="NFL" checked> NFL</label>
    <label><input class="filter-toggle" type="checkbox" data-cat="NCAAF" checked> NCAAF</label>
    <label><input class="filter-toggle" type="checkbox" data-cat="WWO" checked> WWO</label>
    <label><input class="filter-toggle" type="checkbox" data-cat="MLS" checked> MLS</label>
  </div>
  <p class="mini">Durations are planning assumptions, not guaranteed broadcast end times. Filters change the scenario, not the underlying source data.</p>
</section>
<section class="panel"><h2 id="day-heading">Daily scoreboard</h2><div class="callout">All times are Pacific (PST in winter, PDT in summer). Green shows gaps in the selected snapshot, not confirmed free time; other colors represent modeled or captured busy blocks.</div><div id="day-content"></div></section>
<section class="panel"><h2>Duration research</h2>{table(['Sport','Average duration','Halftime','Regulation','Status'], META['durations_table'], ['sport','average_game_duration','halftime','regulation',('status','badge')], 'duration-research', 20)}</section>
'''
    write("daily.html", page("Daily scoreboard", "daily.html", "Yesterday / today / tomorrow scoreboard with estimated intraday gaps and captured or modeled game presence.", body))


def build_calendar():
    body = f'''
<section class="panel"><h2>Month controls</h2>
  <div class="day-nav">
    <button type="button" id="calendar-prev">← Previous month</button>
    <label>Year <select id="calendar-year"><option>2026</option><option>2027</option><option>2028</option><option>2029</option></select></label>
    <label>Month <select id="calendar-month">{''.join(f'<option value="{i}">{n}</option>' for i,n in enumerate(['January','February','March','April','May','June','July','August','September','October','November','December']))}</select></label>
    <button type="button" id="calendar-next">Next month →</button>
    <a class="control-btn" href="daily.html">Daily scoreboard</a>
  </div>
  <p class="mini">Calendar covers {esc(META['date_range'][0])} through {esc(META['date_range'][1])}. Earlier 2026 game data is retained in the event tables.</p>
</section>
<section class="panel"><h2>Month grid</h2><div id="calendar-content"></div></section>
<section class="panel"><h2>Unreleased-season planning models</h2>{table(['Year','Model intervals','Method','Status'], META['model_seasons'], ['year',('model_intervals','num'),'method',('status','badge')], 'model-seasons', 20)}</section>
'''
    write("calendar.html", page("Calendar", "calendar.html", "Everyday month scoreboard with estimated gap minutes and links to each day’s scoreboard.", body))


def build_vacation():
    conclusion = META["analysis_conclusion"]
    body = f'''
<div class="callout danger"><strong>Answer: no 7-, 14- or 21-day window exists in 2027–2029.</strong>
The longest gap bracketed by two published official games is <strong>{FREE_RUNS["published_bounded"][0]["days"]} days</strong>
({FREE_RUNS["published_bounded"][0]["start"]} → {FREE_RUNS["published_bounded"][0]["end"]}), and the longest run with no published game at all is
{FREE_RUNS["counts"]["max_strict_free_run_days"]} days — but those runs exist only because the 2027 NFL/WWO, 2028 and 2029 schedules are unreleased.
<a href="free-runs.html">Full free-run analysis →</a></div>
<div class="callout warn"><strong>Important distinction the older analysis did not make.</strong> A vacation is not only "is a game scheduled today" — it is also
"can I leave the house without missing a game I want to hear". Baseball is on air almost every day from late February to early October, so every weekday in that
span contains a live game somewhere in MLB even when no game is in San Francisco. Those days are busy here, and that is why the strict answer is {FREE_RUNS['published_bounded'][0]['days']} consecutive days and not 3 weeks.</div>
<div class="callout danger"><strong>Strict conclusion (unchanged):</strong> {esc(conclusion['conclusion'])} {badge('ESTIMATED / UNVERIFIED','unverified')} <a href="{esc(conclusion['source_url'])}" target="_blank" rel="noopener">Official NFL date anchor</a></div>
<section class="panel"><h2>Best 1-, 2-, and 3-week windows (least conflict)</h2><p class="intro">Computed from exact official rows plus separately labelled 2026-pattern estimates. Busy days include official dates with TBD times and unverified conservative blocks.</p>
{table(['Year','Length','Start','End','Busy days','Busy minutes','Model days','Strict free','Status'], META['vacation_windows'], ['year',('length_days','num'),'start','end',('busy_days','num'),('busy_minutes','num'),('model_days','num'),('strict_free','text'),('status','badge')], 'vacation-windows', 20)}</section>
<section class="panel"><h2>2027 anchors for manual review</h2><p class="intro">These dates do not establish an empty week or confirm local radio coverage. Other broadcasts may occur between the anchors.</p>{table(['Event','Official date','Status'], [
 {'event':'NFL Super Bowl LXI','date':'2027-02-14','status':'VERIFIED DATE — KICKOFF / RADIO COVERAGE NOT CHECKED','source_url':'https://www.nfl.com/news/2026-27-national-football-league-important-dates','source_label':'NFL important dates'},
 {'event':'Phillies at Tigers spring training','date':'2027-02-19','status':'VERIFIED DATE — START / SF AM/FM CARRIAGE UNVERIFIED','source_url':'https://www.mlb.com/press-release/press-release-2027-phillies-spring-training-schedule-announced','source_label':'Phillies official release'}], ['event','date',('status','badge')], 'manual-anchors', 20)}</section>
{free_runs_panel(compact=False)}
<section class="panel"><h2>Officially anchored short gaps and scenarios</h2>{table(['Year','Window','Days','Label','Status','Notes'], META['anchor_windows'], ['year',('window','blank'),('length_days','num'),'label',('status','badge'),'notes'], 'anchor-windows', 20)}</section>
<section class="panel"><h2>Schedule availability 2026–2029</h2>{table(['Season','League','Official rows','TBD times','Status','Verification'], META['season_availability'], ['season','league',('official_rows','num'),('tbd_times','num'),'status',('verification','badge')], 'season-availability', 50)}</section>
<section class="panel"><h2>Model provenance</h2>{table(['Year','Intervals','Method','Status','Notes'], META['model_seasons'], ['year',('model_intervals','num'),'method',('status','badge'),'notes'], 'model-provenance', 20)}</section>
'''
    write("vacation.html", page("Vacation windows", "vacation.html", "Best 7-, 14-, and 21-day free-time candidates for 2027, 2028 and 2029, with strict verified/estimated/unverified labels.", body))

EVIDENCE_ORDER = {"PUBLISHED-BOUNDED": 0, "MIXED": 1, "MODEL-BOUNDED": 2}


def evidence_label(evidence: str) -> str:
    return {
        "PUBLISHED-BOUNDED": "PUBLISHED-BOUNDED — gap between two published official games",
        "MIXED": "MIXED — one side published, one side model/anchor only",
        "MODEL-BOUNDED": "MODEL-BOUNDED — exists only because the schedule is unreleased",
    }.get(evidence, evidence)


def free_runs_rows(kind="shortlist", limit=None):
    """Rows for the free-run tables. Every row keeps its official source link."""
    if kind == "published":
        source = FREE_RUNS.get("published_bounded", [])
        rows_in = [dict(r, evidence="PUBLISHED-BOUNDED") for r in source][: limit or None]
    else:
        rows_in = FREE_RUNS["shortlist"][: limit or len(FREE_RUNS["shortlist"])]
    rows = []
    for item in rows_in:
        src = item.get("block_before_source") or item.get("block_after_source") or item.get("source_url")
        rows.append({
            "start": item["start"],
            "end": item["end"],
            "days": item["days"],
            "bounded": (f"{item['block_before'] or 'no earlier captured game'} ({item['block_before_date'] or '—'})"
                        " → "
                        f"{item['block_after'] or 'no later captured game'} ({item['block_after_date'] or '—'})"),
            "evidence": evidence_label(item.get("evidence", "")),
            "status": item.get("status", "CANDIDATE — NO PUBLISHED GAME / UNRELEASED-SEASON CAVEAT"),
            "source_url": src,
            "source_label": "Bounding official source",
        })
    return rows


FREE_RUN_COLUMNS = ["Start", "End", "Days", "Officially bounded by (before → after)", "Evidence strength", "Status"]
FREE_RUN_SPECS = ["start", "end", ("days", "num"), "bounded", "evidence", ("status", "badge")]


def free_runs_table(kind="shortlist", limit=None, name="free-runs-shortlist"):
    return table(FREE_RUN_COLUMNS, free_runs_rows(kind, limit), FREE_RUN_SPECS, name, 20)


def other_sports_line():
    other = FREE_RUNS.get("other_sports", {})
    if str(other.get("status", "")).startswith("NOT CAPTURED"):
        return ("Warriors (NBA) and Sharks (NHL) game rows were not captured in this snapshot, so a &quot;free&quot; day here "
                "is free only of MLB, NFL, Stanford/Cal and Westwood One. Flagged as F-018.")
    counts = other.get("counts", {})
    cov = other.get("coverage", {})
    nba = counts.get("NBA", 0)
    nba_note = ("NBA/Warriors game rows are still missing (the official NBA CDN refuses datacenter requests); flagged as F-021."
                if not nba else f"NBA/Warriors rows: {nba}.")
    return (f"Official NHL game rows for the Sharks included as busy days: {counts.get('NHL', 0)} "
            f"({cov.get('NHL', {}).get('first', '—')} → {cov.get('NHL', {}).get('last', '—')}). {nba_note}")


def strongest_answer():
    pb = FREE_RUNS.get("published_bounded") or []
    if not pb:
        return None
    return pb[0]


def free_runs_panel(compact=False):
    counts = FREE_RUNS["counts"]
    best = strongest_answer()
    strict_max = counts["max_strict_free_run_days"]
    limit = 3 if compact else None
    more = ('<p><a class="control-btn" href="free-runs.html">Full free-run analysis and official season boundaries →</a></p>'
            if compact else "")
    best_line = ""
    if best:
        best_line = (f'<br><br><strong>Best-supported short break: {best["days"]} days, {best["start"]} → {best["end"]}</strong> '
                     f'— it sits between two published official games: {esc(best["block_before"])} on {best["block_before_date"]} '
                     f'and {esc(best["block_after"])} on {best["block_after_date"]}.')
    return f'''
<section class="panel"><h2>Longest run of consecutive days with no published game</h2>
<div class="callout warn"><strong>No 7-, 14- or 21-day window exists.</strong> The longest run of consecutive days with no published game of any monitored
category is <strong>{strict_max} days</strong>, and every {strict_max}-day run happens only because a schedule has not been released — not because the sport is idle.
The longest gap that is bracketed by two <em>published</em> official games is <strong>{best["days"] if best else 0} days</strong>.{best_line}<br><br>{other_sports_line()}</div>
{free_runs_table("published" if compact else "shortlist", limit, "free-runs-compact" if compact else "free-runs-shortlist")}
{more}</section>'''


def build_free_runs():
    per_year = FREE_RUNS["per_year"]
    counts = FREE_RUNS["counts"]
    best = strongest_answer()
    year_rows = []
    for year, rec in per_year.items():
        top = FREE_RUNS["year_runs"][year]["top_runs"]
        year_rows.append({
            "year": year,
            "days": rec["days_in_snapshot"],
            "free_days": rec["strict_free_days"],
            "published_days": rec["published_days"],
            "run": f"{rec['longest_strict_free_run']} days",
            "empty_run": f"{rec['longest_no_published_run']} days (absence of schedule, not free time)",
            "top": ", ".join(f"{r['start']}→{r['end']}" for r in top[:3]),
            "status": "ESTIMATED GAP — UNVERIFIED",
            "source_url": "https://www.nfl.com/news/2026-27-national-football-league-important-dates",
            "source_label": "NFL official 2026–27 important dates",
        })
    other_rows = []
    if OTHER_SPORTS:
        for row in OTHER_SPORTS["rows"]:
            other_rows.append({
                "date": row["date"],
                "time": row["official_time_pt"],
                "league": row["league"],
                "matchup": row["matchup"],
                "venue": row.get("venue", ""),
                "radio": row.get("radio", ""),
                "planning": f"{row['planning_start_pt']}–{row['planning_end_pt']}",
                "status": row["duration_status"],
                "source_url": row["source_url"],
                "source_label": row["source_label"],
                "verification": row["verification"],
            })
    availability_rows = OTHER_SPORTS["availability"] if OTHER_SPORTS else [{
        "league": "NBA / NHL", "season": "", "official_rows": "",
        "status": "NOT CAPTURED — UNVERIFIED (scripts/fetch_nba_nhl_sources.py runs in CI)",
        "source_url": "https://www.nba.com/warriors/schedule",
        "source_label": "NBA Warriors official schedule page",
        "verification": "UNVERIFIED",
    }]
    classes = [{"k": k, "v": v} for k, v in FREE_RUNS["classes"].items()]
    best_block = f'''
<section class="panel"><h2>Best-supported short break (both ends are published games)</h2>
<div class="callout"><strong>{best['days']} days: {best['start']} → {best['end']}</strong><br>
Last published game before: <strong>{esc(best['block_before'])}</strong> on {best['block_before_date']}.
First published game after: <strong>{esc(best['block_after'])}</strong> on {best['block_after_date']}.<br>
This is the only kind of window the data can actually support: a real gap between two real, officially published games. It is still a
<em>candidate</em>, because late changes, flex scheduling and unmodelled broadcasts are always possible.</div>
{free_runs_table("published", None, "free-runs-published")}
</section>''' if best else ""
    body = f'''
<section class="panel"><h2>Answer</h2>
<div class="callout danger"><strong>No 7-, 14- or 21-day stretch of consecutive days in 2027, 2028 or 2029 is free</strong> under the strict reading
(no published MLB, NFL, Stanford/Cal, Westwood One or captured NBA/NHL game, and no officially anchored all-day event).<br><br>
The longest run of consecutive days with no published game of any monitored category is <strong>{counts['max_strict_free_run_days']} days</strong>
(2027: {per_year['2027']['longest_strict_free_run']}, 2028: {per_year['2028']['longest_strict_free_run']}, 2029: {per_year['2029']['longest_strict_free_run']}),
but every one of those runs exists because a schedule has not been released, so it is not evidence that no game is on.<br><br>
The longest gap bracketed by two <em>published</em> official games is <strong>{best['days'] if best else 0} days</strong>
({best['start'] if best else '—'} → {best['end'] if best else '—'}). That is the honest answer to "how long can I go away".</div>
<p class="intro">{esc(FREE_RUNS['practical_reading'])}</p>
<p class="intro">{esc(FREE_RUNS['strict_conclusion'])} {esc(other_sports_line())}</p></section>
{best_block}
<section class="panel"><h2>Definition used on this page</h2>
<p class="intro">{esc(FREE_RUNS['definition'])}</p>
{table(["Day class", "Meaning"], classes, ["k", "v"], "free-run-classes", 20, with_source=False)}
</section>
<section class="panel"><h2>Why a long summer window cannot exist</h2>
<p class="intro">This is the core reason the answer is days, not weeks. Counting only <em>published</em> official game rows, MLB plays on almost every
calendar day of its season, so nearly every summer day is busy no matter which club is involved. The days without a game are the All-Star break and the day
before Opening Night — exactly the short gaps ranked below.</p>
{table(["League", "Season", "First published", "Last published", "Calendar days", "Days with a game", "Share", "Days without a game", "Verification"],
      FREE_RUNS["sport_density"], ["league", "season", "first", "last", ("calendar_days", "num"), ("days_with_game", "num"), "share", "days_without_game", ("status", "badge")],
      "sport-density", 20)}</section>
<section class="panel"><h2>Per-year summary</h2>
{table(["Year", "Days in snapshot", "Days with no block", "Days with a published game", "Longest strict-free run", "Longest stretch with no published game", "Top three runs"],
      year_rows, ["year", ("days", "num"), ("free_days", "num"), ("published_days", "num"), "run", "empty_run", "top"],
      "free-runs-years", 20)}</section>
<section class="panel"><h2>All runs, ranked by evidence then length</h2>
<p class="intro">Evidence strength matters more than length: a 5-day gap that exists because a schedule is unreleased tells you nothing, while a
4-day gap between two published games is checkable. Every row links the official source of its bounding game.</p>
{free_runs_table("shortlist")}
<p class="mini">Recomputed by <code>scripts/build_free_runs.py</code> from <code>data/official/days-*.json</code> plus
<code>data/official/other-sports.json</code>; published as <a href="data/official/free-runs.json">data/official/free-runs.json</a>.
Verification record: <a href="research/free-runs-report.md">research/free-runs-report.md</a>.</p>
</section>
<section class="panel"><h2>Other Bay Area live radio sports: Sharks (NHL) and Warriors (NBA)</h2>
<div class="callout"><strong>Why this matters.</strong> 95.7 The Game and 98.5 KFOX carry NBA and NHL games that the original dashboard only listed as stations.
A day is only free if the Sharks and Warriors are also not on air. Their rows come from the leagues' own feeds; neither league publishes a broadcast length, so the
window end is a clearly labelled ESTIMATED planning length, never an official end time.</div>
{table(["League", "Season", "Official rows", "Status", "Verification"], availability_rows,
      ["league", "season", ("official_rows", "num"), "status", ("verification", "badge")], "other-sports-availability", 20)}
</section>
'''
    if other_rows:
        body += table(
            ["Date PT", "Official start", "League", "Matchup", "Venue", "Radio home", "Planning window", "Length status", "Verification"],
            other_rows, ["date", "time", "league", "matchup", "venue", "radio", "planning", ("status", "badge"), ("verification", "badge")],
            "other-sports-games", 100,
        )
    body += f'''
<section class="panel"><h2>Official season boundaries behind the empty stretches</h2>
<p class="intro">Each row explains why a stretch of days has no published game. None of them is evidence that no game is scheduled.</p>
{table(["ID", "League / season", "What the official source says", "Dates", "Effect on free time", "Status"],
      FREE_RUNS["season_notes"], ["id", lambda r: f"{r['league']} {r['season']}", "label", lambda r: f"{r['start']} → {r['end']}", "effect", ("status", "badge")],
      "free-run-notes", 50)}
</section>
'''
    write("free-runs.html", page(
        "Longest free runs (vacation answer)", "free-runs.html",
        "How many consecutive days in 2027, 2028 and 2029 have no published live-radio sports game, ranked by evidence strength.",
        body))


def build_mlb():
    mlb = [e for e in EVENTS if e["category"] == "MLB"]
    cols = [("date","blank"),("official_time_pt","time"),("time_status","badge"),"subcategory","matchup",("venue","blank"),("priority","badge"),("planning_start_pt","blank"),("planning_end_pt","blank"),("planning_status","badge")]
    body = f'''
<div class="callout"><strong>All 30 MLB clubs shown.</strong> Giants and Athletics rows are FOCUS; every MLB game is HIGH priority. Official TBD start times are blank and flagged; planning estimates are separate.</div>
<section class="panel"><h2>All 30 MLB clubs</h2>{table(['ID','Club','Abbr','League','Division','Venue','Priority','Verification'], META['teams'], [('id','num'),'name','abbreviation','league','division','venue',('priority','badge'),('verification','badge')], 'mlb-teams', 50)}</section>
<section class="panel"><h2>Official MLB season availability</h2>{table(['Season','League','Official rows','TBD times','Status'], [r for r in META['season_availability'] if r['league']=='MLB'], ['season','league',('official_rows','num'),('tbd_times','num'),'status'], 'mlb-seasons', 20)}</section>
<section class="panel"><h2>Every official MLB game row</h2><p class="intro">{len(mlb)} rows. Blank official time = UNVERIFIED. Estimated planning windows use official 2026 median starts and official MLB average duration.</p>{table(['Date PT','Official time','Time status','Type','Matchup','Venue','Priority','Est. start','Est. end','Planning status'], mlb, cols, 'mlb-games', 100)}</section>
'''
    write("mlb.html", page("MLB", "mlb.html", "All 30 clubs and every released 2026/2027 MLB Stats API game row, with TBD times blank + UNVERIFIED and official links.", body))
    write("teams.html", page("All 30 MLB clubs", "mlb.html", "All 30 official MLB clubs; Giants and Athletics are high-priority focus teams.", f'<section class="panel"><h2>Official MLB club list</h2>{table(["ID","Club","Abbr","League","Division","Venue","Priority","Verification"], META["teams"], [("id","num"),"name","abbreviation","league","division","venue",("priority","badge"),("verification","badge")], "teams-page", 50)}</section>'))


def build_nfl():
    nfl = [e for e in EVENTS if e["category"] == "NFL"]
    focus = [e for e in nfl if e.get("focus")]
    cols = [("date","blank"),("date_range","blank"),("official_time_pt","time"),("time_status","badge"),"subcategory","matchup",("priority","badge"),("verification","badge")]
    body = f'''
<div class="callout"><strong>Official 2026 NFL coverage:</strong> 272 regular-season game rows parsed from 18 NFL by-week pages, 49 preseason matchups from the official schedule PDF, postseason date anchors, and 49ers exact radio/kickoff rows.</div>
<section class="panel"><h2>49ers high-priority focus</h2>{table(['Date PT','Official time','Subcategory','Matchup','Venue','Stations','Priority'], focus, [('date','blank'),('official_time_pt','time'),'subcategory','matchup',('venue','blank'),('stations','list'),('priority','badge')], 'nflers-focus', 50)}</section>
<section class="panel"><h2>Every NFL row (preseason / regular / postseason / special)</h2><p class="intro">{len(nfl)} rows. Empty official date or time means UNVERIFIED; conservative all-day blocks are visible on the daily scoreboard.</p>{table(['Date PT','Official range','Official time','Time status','Subcategory','Matchup / anchor','Priority','Verification'], nfl, cols, 'nfl-all', 100)}</section>
'''
    write("nfl.html", page("NFL", "nfl.html", "All 2026 preseason, regular-season, postseason and special NFL rows; 49ers focus; official links on every row.", body))


def build_ncaaf():
    games = [e for e in EVENTS if e["category"] == "NCAAF"]
    anchors = [a for a in META["anchors"] if a["category"] == "NCAAF"]
    body = f'''
<div class="callout"><strong>Stanford and Cal are FOCUS priorities.</strong> 2026 exact kickoffs/radio are official; 2027–2029 dates/times are blank unless an official article confirms them.</div>
<section class="panel"><h2>Stanford / Cal 2026 official games</h2>{table(['Date PT','Official time','Team','Matchup','Venue','Radio','Priority','Verification'], games, [('date','blank'),('official_time_pt','time'),'subcategory','matchup',('venue','blank'),('stations','list'),('priority','badge'),('verification','badge')], 'ncaaf-games', 50)}</section>
<section class="panel"><h2>Future official anchors, 2027–2029</h2>{table(['ID','Event','Official date','Official time','Status','Verification'], anchors, ['id','event',('official_date','blank'),('official_time_pt','blank'),'status',('verification','badge')], 'ncaaf-anchors', 50)}</section>
'''
    write("ncaaf.html", page("Stanford / Cal NCAAF", "ncaaf.html", "Stanford and Cal official 2026 games, future NCAAF/ACC/CFP anchors, and blank UNVERIFIED values for unreleased dates/times.", body))


def build_wwo():
    wwo = [e for e in EVENTS if e["category"] == "WWO"]
    station_rows = [r for r in META["stations"] if str(r.get("sport","")).startswith("WWO ")]
    body = f'''
<div class="callout warn"><strong>Affiliate caveat:</strong> the official Westwood One station finder warns local affiliates may not air every network broadcast. All WWO network events are still treated as HIGH priority busy candidates.</div>
<section class="panel"><h2>San Francisco WWO affiliates by sport</h2>{table(['Sport','Station / call sign','Frequency','Status','Notes'], station_rows, ['sport','station',('frequency','blank'),('status','badge'),'notes'], 'wwo-affiliates', 50)}</section>
<section class="panel"><h2>Every official WWO 2026–2027 event window</h2><p class="intro">{len(wwo)} rows across all nine WWO categories. Exact Unix timestamps are converted to Pacific; JSON-LD timezone inconsistency and 11:59 PM end placeholders are flagged.</p>{table(['Date PT','Start PT','End PT','Category','Event','Venue','SF affiliates','Priority','Verification'], wwo, ['date',('official_time_pt','time'),('official_end_pt','blank'),'subcategory','matchup',('venue','blank'),('sf_affiliates','list'),('priority','badge'),('verification','badge')], 'wwo-events', 100)}</section>
'''
    write("wwo.html", page("Westwood One Sports", "wwo.html", "All captured official WWO event windows across nine sports categories, SF affiliates, and local-carriage caveats.", body))


def build_radio():
    station_schedule = [s for s in SOURCES if any(k in s["id"] for k in ("knbr", "ksfo", "game957", "warriors", "sharks", "earthquakes"))]
    body = f'''
<div class="callout"><strong>Standard AM/FM only.</strong> Reception in Outer Sunset 94122 is not independently field-tested here; station mappings come from official team, league, and station pages. Unverified reception/game rows are blank + flagged.</div>
<section class="panel"><h2>Bay Area sports radio matrix</h2>{table(['Sport / schedule','Station','Call sign','Frequency','Priority','Status','Notes'], META['stations'], ['sport','station','call_sign',('frequency','blank'),('priority','badge'),('status','badge'),'notes'], 'radio-stations', 100)}</section>
<section class="panel"><h2>Official station / team schedule links</h2>{table(['ID','Title','Purpose','Status','Retrieved'], station_schedule, ['id','title','purpose',('status','badge'),'retrieved_utc'], 'radio-schedules', 50)}</section>
<section class="panel"><h2>Official Earthquakes terrestrial radio matches</h2>{table(['Date PT','Time PT','Matchup','Stations','Verification'], [e for e in EVENTS if e['category']=='MLS'], ['date',('official_time_pt','time'),'matchup',('stations','list'),('verification','badge')], 'earthquakes-games', 50)}</section>
'''
    write("radio.html", page("Radio map & other sports", "radio.html", "KNBR / Westwood One / KSFO / 95.7 The Game / other Bay Area sports radio sources, with official links and high-priority flags.", body))


def build_sources():
    cols = ['id','title','purpose',('http_status','num'),('bytes','num'),'sha256',('status','badge'),'retrieved_utc']
    body = f'''
<div class="callout"><strong>Manual review:</strong> {len(SOURCES)} official captured/curated source rows. Every row’s last column opens the official page. Raw gzip snapshots are retained in <code>research/official/raw/</code> and <code>research/probe/raw/</code>.</div>
<section class="panel"><h2>All official sources</h2>{table(['ID','Title','Purpose','HTTP','Bytes','SHA-256','Status','Retrieved UTC'], SOURCES, cols, 'all-sources', 100)}</section>
'''
    write("sources.html", page("Official sources", "sources.html", "Every captured official response, URL, HTTP status, byte count, SHA-256, and raw snapshot path for line-by-line manual review.", body))


def build_flagged():
    body = f'''
<div class="callout danger"><strong>Review warning:</strong> Snapshot gaps cannot prove all broadcasts were captured; the older parallel dashboards may have conflicting claims. A source link is not proof that every cell was independently checked. These are published here with official source links. Unverified values remain blank in the main tables.</div>
<section class="panel"><h2>Follow-up audit flags</h2>{table(['ID','Issue','Status','Action'], [
        {'id':'D1-01','issue':'Warriors, Sharks, Valkyries and other terrestrial radio game-by-game coverage is incomplete; local carriage and reception are not confirmed for each event.','status':'UNVERIFIED','action':'Do not treat displayed gaps as verified free time. Consult station and team schedules.','source_url':'https://www.nba.com/warriors/schedule'},
        {'id':'D1-02','issue':'The dashboard uses a static 2026-11-02 snapshot; future schedules and broadcast details may have changed. The automated structural checker does not independently verify each source value.','status':'UNVERIFIED','action':'Refresh and independently compare individual rows before relying on them.','source_url':'https://www.nfl.com/schedules/'},
        {'id':'D1-03','issue':'Archived parallel dashboards and the primary snapshot may differ in coverage and conclusions.','status':'FLAGGED','action':'Use them as historical research only; independently review official sources.','source_url':'https://www.westwoodonesports.com/nfl-schedule/'},
        {'id':'D1-04','issue':'Legacy planner build tests expect a superseded redirect artifact and fail against the root-dashboard configuration.','status':'FLAGGED','action':'Tests are not evidence of a successful legacy build; root static checks and focused dashboard tests are run separately.','source_url':'https://www.westwoodonesports.com/station-finder/'},
        {'id':'F-018','issue':'Snapshot has station rows for the Warriors (95.7 The Game) and Sharks (98.5 KFOX) but no game rows, so days without MLB/NFL/NCAAF/WWO games were being called free while NBA/NHL games could be on air.','status':'REPAIRED IN ANALYSIS — PENDING DATA CAPTURE','action':'scripts/fetch_nba_nhl_sources.py + scripts/collect_other_sports.py capture official NBA/NHL game rows in CI; the Longest free runs page adds them as busy days and says so when they are missing.','source_url':'https://www.nba.com/warriors/schedule'},
        {'id':'F-019','issue':'Snapshot contains no MLB game row after 2027-09-26 (2027 postseason absent) and no 2027 NFL, 2027 Westwood One, 2028 or 2029 season rows at all. Long empty stretches late in 2027 and throughout 2028–2029 are absence of data, not absence of games.','status':'UNVERIFIED','action':'These stretches are published as CANDIDATES only, never as verified free time; each is bounded by the official date where the released schedule stops.','source_url':'https://statsapi.mlb.com/api/v1/schedule?sportId=1&season=2028'},
        {'id':'F-021','issue':'The official NBA league schedule feed (cdn.nba.com/static/json/staticData/scheduleLeagueV2_1.json) returns HTTP 403 to GitHub Actions runners, so Warriors game rows could not be captured even though the Warriors are a live 95.7 FM radio team.','status':'UNVERIFIED — BLOCKED BY SOURCE','action':'Warriors days remain covered only by MLB/NFL/NCAAF/WWO rows; the free-run page states this on every run. Do not read a free day as Warrior-free.','source_url':'https://www.nba.com/warriors/schedule'},
        {'id':'F-020','issue':'The "unreleased season" model is built only from 2026 windows that fall after 2026-11-01, so 2028–2029 MODEL_ONLY days in February–September reflect no real baseball, hockey or basketball calendar.','status':'FLAGGED — MODEL LIMITATION','action':'Model rows never count as free and never count as a confirmed game; the free-run analysis treats them as "not verified free" only.','source_url':'https://statsapi.mlb.com/api/v1/schedule?sportId=1&season=2026'}], ['id','issue',('status','badge'),'action'], 'follow-up-flags', 20)}</section>
<section class="panel"><h2>Irregularities and corrections</h2>{table(['ID','Issue','Status','Action'], META['flags'], ['id','issue',('status','badge'),'action'], 'all-flags', 100)}</section>
<section class="panel"><h2>Unverified official anchors</h2>{table(['ID','Event','Official date','Status','Verification'], [a for a in META['anchors'] if a['verification']=='UNVERIFIED'], ['id','event',('official_date','blank'),'status',('verification','badge')], 'unverified-anchors', 100)}</section>
'''
    write("flagged.html", page("Flagged for Review", "flagged.html", "Clearly labelled irregularities, dead links, secondary-source corrections, TBD values, and unreleased schedules.", body))


def build_methodology():
    body = f'''
<div class="callout"><strong>Verification rule:</strong> official/league/team/network sources only for VERIFIED values. If a value cannot be confirmed, leave it blank and publish UNVERIFIED with an official source link. Estimates are never presented as released schedules.</div>
<section class="panel"><h2>Average durations and halftime research</h2>{table(['Sport','Average duration','Halftime','Regulation','Status','Notes'], META['durations_table'], ['sport','average_game_duration','halftime','regulation',('status','badge'),'notes'], 'durations-method', 50)}</section>
<section class="panel"><h2>Planning models — not released schedules</h2>{table(['Year','Model intervals','Method','Status','Notes'], META['model_seasons'], ['year',('model_intervals','num'),'method',('status','badge'),'notes'], 'models-method', 50)}</section>
<section class="panel"><h2>Free-run method (consecutive free days)</h2>
<p class="intro">The daily scoreboard answers "which minutes today are free". The vacation question is different: "how many <em>consecutive days</em> can I be away".
Both are computed from the same published rows, but a day is only counted as free when it contains no published game, no officially anchored all-day event and no
unreleased-season model block. Counting a day as free because the schedule is unknown would be an invention, so the strict count refuses to do it.</p>
{table(["Day class", "Meaning"], [{"k": k, "v": v} for k, v in FREE_RUNS["classes"].items()], ["k", "v"], "method-free-classes", 20, with_source=False)}
<p class="mini">Recompute: <code>python3 scripts/build_free_runs.py</code> → <a href="data/official/free-runs.json">data/official/free-runs.json</a> and
<a href="research/free-runs-report.md">research/free-runs-report.md</a>. Official NBA/NHL capture runs in CI via
<code>scripts/fetch_nba_nhl_sources.py</code> and <code>scripts/collect_other_sports.py</code>.</p></section>
<section class="panel"><h2>Verification rules</h2><ol class="exec-list">
<li>Official/league/team/network sources only for VERIFIED values.</li>
<li>Unconfirmable values are blank and flagged UNVERIFIED with an official source link.</li>
<li>Official TBD times are blank; separately labelled planning estimates use documented 2026 official medians and researched durations.</li>
<li>2028/2029 and unreleased 2027 NFL/WWO rows are ESTIMATED models, not real verified released schedules.</li>
<li>Every table row carries a source link; internal links and static assets are checked before merge.</li>
</ol></section>
<section class="panel"><h2>Analysis findings</h2>{table(['Topic','Finding','Status'], safe_findings(), ['topic','finding',('status','badge')], 'method-findings', 50)}</section>
'''
    write("methodology.html", page("Methodology & durations", "methodology.html", "Official verification rules, average game durations, halftime research, estimation model, and analysis findings.", body))


def build_review():
    body = f'''
<div class="callout warn"><strong>Line-by-line repo review:</strong> {len(REVIEW)} prior generated-data and documentation lines were audited. Secondary sources, estimates, TBD values, and source lines are replaced or flagged with official links.</div>
<section class="panel"><h2>Prior data line audit</h2>{table(['ID','File','Line','Prior line text','Finding','Status'], REVIEW, ['id','file',('line','num'),'text','finding',('status','badge')], 'line-by-line', 100)}</section>
'''
    write("review.html", page("Repo review", "review.html", "Line-by-line audit of prior generated data, docs, and source claims, with official replacement links and flags.", body))


def other_sports_summary():
    other = FREE_RUNS.get('other_sports', {})
    counts = other.get('counts', {})
    cov = other.get('coverage', {})
    nhl = cov.get('NHL', {})
    return (
        f"- Sharks (NHL) official game rows now included as busy days: {counts.get('NHL', 0)} "
        f"({nhl.get('first', '—')} to {nhl.get('last', '—')}).\n"
        f"- Warriors (NBA) game rows are still missing: the official NBA schedule feed returns HTTP 403 to CI runners (flag F-021).\n"
        f"- Every free-run row is ranked by evidence strength, so a gap between two published games is never confused with a gap caused by an unreleased schedule.\n"
    )


def build_executive():
    body = f'''
<section class="hero"><div class="kicker">Executive summary</div><h1>Verified rows, blank unknowns, clearly labelled estimates.</h1><p>{esc(META['executive_summary'])}</p></section>
<div class="grid cards">{card(META['counts']['official_event_rows'],'official rows')}{card(META['counts']['official_sources'],'official sources')}{card(META['counts']['days'],'daily scoreboards')}{card(META['counts']['line_by_line_audit_rows'],'prior lines reviewed')}</div>
<section class="panel"><h2>Key findings</h2>{table(['Topic','Finding','Status'], safe_findings(), ['topic','finding',('status','badge')], 'exec-findings', 50)}</section>
<section class="panel"><h2>Vacation conclusion</h2><div class="callout danger">{esc(META['analysis_conclusion']['conclusion'])}</div>{table(['Year','Length','Start','End','Busy days','Status'], META['vacation_windows'], ['year',('length_days','num'),'start','end',('busy_days','num'),('status','badge')], 'exec-windows', 50)}</section>
<section class="panel"><h2>Irregularities</h2>{table(['ID','Issue','Status'], META['flags'], ['id','issue',('status','badge')], 'exec-flags', 100)}</section>
'''
    write("executive-summary.html", page("Executive summary", "executive-summary.html", "Concise executive summary of sources, verification, findings, vacation windows, and flagged irregularities.", body))
    md = f'''# Executive summary — FREE TIME VACATION

Generated {META['generated_utc']} from {len(SOURCES)} official-source records.

## Scope
- All 30 MLB clubs; Giants and Athletics FOCUS; all MLB games HIGH.
- All released 2026 NFL preseason/regular/postseason/special rows; 49ers FOCUS.
- Stanford and Cal 2026 NCAAF games and official 2027–2029 future anchors.
- All captured official Westwood One Sports event windows across nine categories.
- Other confirmed Bay Area AM/FM radio sports, including the full official 2026 Earthquakes radio schedule.
- Estimated Pacific-time gaps, not verified free time, for each day from {META['date_range'][0]} through {META['date_range'][1]}.

## Verification rules
1. Official/league/team/network sources only for VERIFIED values.
2. Unconfirmable values are blank and flagged UNVERIFIED with an official source link.
3. Official TBD start times are blank; planning estimates are separate and explicitly labelled.
4. 2028/2029 (and unreleased 2027 NFL/WWO) rows are ESTIMATED models, not real verified released schedules.
5. Every table row carries an official source link.

## Headline conclusion — vacation

**No 7-, 14- or 21-day window in 2027, 2028 or 2029 is free.** The longest run of consecutive days with no published game of any monitored
category is {FREE_RUNS['counts']['max_strict_free_run_days']} days, but every such run exists because the 2027 NFL/Westwood One, 2028 and 2029
schedules have not been released. The longest gap bracketed by two *published* official games is
{FREE_RUNS['published_bounded'][0]['days']} days ({FREE_RUNS['published_bounded'][0]['start']} to {FREE_RUNS['published_bounded'][0]['end']},
between {FREE_RUNS['published_bounded'][0]['block_before']} on {FREE_RUNS['published_bounded'][0]['block_before_date']} and
{FREE_RUNS['published_bounded'][0]['block_after']} on {FREE_RUNS['published_bounded'][0]['block_after_date']}).

Why the answer is short rather than three weeks: MLB publishes a game almost every day from late February to early October, so a baseball game
is on the radio nearly every day of the year's best weather. Winter gaps between the NFL playoffs and the start of spring training are the only
real openings, and they are two to four days long.

{other_sports_summary}

## Older stricter statement (kept for continuity)
{META['analysis_conclusion']['conclusion']}

No 7-, 14- or 21-day trip can be certified free from all requested radio sports from this incomplete snapshot. In 2027, the [NFL lists Super Bowl LXI on February 14](https://www.nfl.com/news/2026-27-national-football-league-important-dates), and the [Phillies list a spring-training game on February 19](https://www.mlb.com/press-release/press-release-2027-phillies-spring-training-schedule-announced). The intervening dates are only a review candidate, not a verified radio-free interval: other broadcasts, future changes and local carriage remain unknown. [Westwood One warns not every affiliate carries every network broadcast](https://www.westwoodonesports.com/station-finder/). The 2028 and 2029 candidates are model-based and unverified.


## Counts
- Official event / anchor rows: {META['counts']['official_event_rows']}
- Official sources: {META['counts']['official_sources']}
- Daily scoreboards: {META['counts']['days']}
- Merged busy/free intervals: {META['counts']['intervals']}
- Prior generated-data lines reviewed: {META['counts']['line_by_line_audit_rows']}

## Manual review
- [Sources page](sources.html)
- [Flagged for Review](flagged.html)
- [Line-by-line repo review](review.html)
- [Official event JSON](data/official/events.json)
- [Official-source manifest](research/official/manifest.json)
'''
    write("EXECUTIVE-SUMMARY.md", md)


def build_readme():
    readme = f'''# Korea4 — FREE TIME VACATION

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
{FREE_RUNS['counts']['max_strict_free_run_days']} days, but each of those runs exists only because the 2027 NFL / Westwood One, 2028 and 2029
schedules are unreleased. The longest gap **bracketed by two published official games** is {FREE_RUNS['published_bounded'][0]['days']} days
({FREE_RUNS['published_bounded'][0]['start']} → {FREE_RUNS['published_bounded'][0]['end']}). Full analysis: `free-runs.html`.

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
'''
    write("README.md", readme)


def main():
    preserve_legacy()
    build_index(); build_daily(); build_calendar(); build_vacation(); build_mlb(); build_nfl()
    build_ncaaf(); build_wwo(); build_radio(); build_sources(); build_flagged(); build_methodology()
    build_free_runs()
    build_review(); build_executive(); build_readme()
    print(json.dumps({"pages": len(NAV) + 1, "source_rows": len(SOURCES), "event_rows": len(EVENTS), "audit_rows": len(REVIEW)}, indent=2))


if __name__ == "__main__":
    main()
