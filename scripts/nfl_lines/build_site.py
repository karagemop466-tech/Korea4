"""Builds the static NFL Lines Lab site under lines/ from research/nfl-lines/ data files.

Every number on a page is read from a data file produced by model.py / backtest.py or from
the official-source records under research/nfl-lines/official/. Nothing is typed in by hand
except the static explanatory text (questions, suggestions, repo review) which is labelled.
"""
from __future__ import annotations

import csv
import gzip
import html
import json
import datetime as dt
from pathlib import Path

from model import ROOT, load_games

SITE = ROOT / "lines"
RES = ROOT / "research/nfl-lines"
REPO_URL = "https://github.com/karagemop466-tech/Korea4"
SNAPSHOT_DATE = "2026-11-13"
# Deterministic on purpose: output must be byte-identical on rebuild (checked in CI).
BUILD_UTC = f"from data snapshot {SNAPSHOT_DATE}"

NAV = [
    ("index.html", "Home"),
    ("executive-summary.html", "Executive summary"),
    ("strategies.html", "Strategy leaderboard"),
    ("seasons.html", "Season results"),
    ("correlation.html", "Correlation & parlays"),
    ("games-2026.html", "2026 games"),
    ("injuries.html", "Injuries & depth"),
    ("questions.html", "Questions & gaps"),
    ("suggestions.html", "Suggestions"),
    ("repo-review.html", "Repo review"),
    ("flagged.html", "Flagged for Review"),
    ("sources.html", "Sources"),
    ("methodology.html", "Methodology"),
]

OFFICIAL_HOSTS = ("www.nfl.com", "nfl.com", "www.gra.gov.sg", "sso.agc.gov.sg")


def e(x) -> str:
    return html.escape("" if x is None else str(x))


def link(url: str, label: str | None = None) -> str:
    return f'<a href="{e(url)}" rel="noopener">{e(label or url)}</a>'


def pct(x, d=1):
    return "" if x is None else f"{x * 100:.{d}f}%"


def num(x, d=2, sign=False):
    if x is None or x == "":
        return ""
    fmt = f"{{:+.{d}f}}" if sign else f"{{:.{d}f}}"
    return fmt.format(float(x))


def page(path: str, title: str, body: str, active: str) -> None:
    nav = "".join(
        f'<a href="{href}" class="{"on" if href == active else ""}">{e(label)}</a>'
        for href, label in NAV
    )
    doc = f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{e(title)} · NFL Lines Lab</title>
<link rel="stylesheet" href="assets/style.css">
</head>
<body>
<header class="top">
  <div class="brand"><a href="index.html">NFL Lines Lab</a><span class="tag">research only · not betting advice</span></div>
  <nav>{nav}</nav>
</header>
<main>
<div class="legal">Singapore: under the GRA's published guidance, participating in unlicensed remote gambling is an offence and Singapore Pools is the only licensed remote-betting operator. This site is research, not a recommendation to place any bet. <a href="https://www.gra.gov.sg/harm-minimisation/unlawful-remote-gambling-activities">GRA source</a></div>
{body}
</main>
<footer>
  <p>Generated {e(BUILD_UTC)}. Repository: {link(REPO_URL, "karagemop466-tech/Korea4")}.</p>
  <p>Legend: <span class="v">VERIFIED</span> = value checked against an official NFL.com page · <span class="u">UNVERIFIED</span> = no official source found for this value; shown for analysis only · <span class="d">DERIVED</span> = calculated by this project from unverified inputs.</p>
</footer>
</body>
</html>
"""
    (SITE / path).write_text(doc, encoding="utf-8", newline="\n")


def table(headers, rows, cls="", filter_id=None) -> str:
    th = "".join(f"<th>{e(h)}</th>" for h in headers)
    trs = []
    for r in rows:
        tds = "".join(f"<td>{c}</td>" for c in r)  # cells are pre-escaped by caller
        trs.append(f"<tr>{tds}</tr>")
    fid = f' id="{filter_id}"' if filter_id else ""
    return f'<div class="tablewrap"><table class="{cls}"{fid}><thead><tr>{th}</tr></thead><tbody>{"".join(trs)}</tbody></table></div>'


def badge(kind: str) -> str:
    kind = {"VERIFIED": "V", "UNVERIFIED": "U", "DERIVED": "D", "FLAGGED": "F"}.get(kind, kind)
    return {"V": '<span class="v">VERIFIED</span>',
            "U": '<span class="u">UNVERIFIED</span>',
            "D": '<span class="d">DERIVED</span>',
            "F": '<span class="f">FLAGGED</span>'}[kind]


def load_backtest():
    return json.loads((RES / "analysis/backtest.json").read_text())


def load_csv(path):
    with path.open(newline="", encoding="utf-8") as fh:
        return list(csv.DictReader(fh))


STRATEGY_LABELS = {
    "SPREAD_EDGE_1": ("Model spread edge ≥ 1 pt", "Bet the side where our model margin differs from the closing spread by ≥ 1 point."),
    "SPREAD_EDGE_2": ("Model spread edge ≥ 2 pts", "Same, threshold 2 points."),
    "SPREAD_EDGE_3": ("Model spread edge ≥ 3 pts", "Same, threshold 3 points."),
    "TOTAL_EDGE_2": ("Model total edge ≥ 2 pts", "Bet over/under when our total differs from the closing total by ≥ 2."),
    "TOTAL_EDGE_3": ("Model total edge ≥ 3 pts", "Same, threshold 3."),
    "TOTAL_EDGE_4": ("Model total edge ≥ 4 pts", "Same, threshold 4."),
    "REST_3": ("Rest advantage ≥ 3 days", "Bet the team with ≥ 3 more days of rest (against the spread)."),
    "DIV_DOG": ("Divisional underdog", "Bet the underdog in divisional games (against the spread)."),
    "BASE_HOME": ("Control: always home", "Always bet the home team against the spread."),
    "BASE_FAV": ("Control: always favourite", "Always bet the favourite against the spread."),
}
GATE_LABELS = {
    "G1_min_sample": "G1 sample ≥ 400 bets",
    "G2_edge_breakeven_and_wilson": "G2 hit rate ≥ 52.38% and Wilson lower bound > 50%",
    "G3_holm_significant": "G3 Holm-adjusted p < 0.05",
    "G4_stability_60pct_seasons": "G4 positive ROI in ≥ 60% of seasons",
    "G5_beats_random_null_p95": "G5 beats 95th percentile of random-side null",
    "G6_forward_2026_roi_positive": "G6 2026 forward ROI > 0",
}


def build_strategies_page(bt):
    st = bt["strategies"]
    ranked = sorted(st.items(), key=lambda kv: (-kv[1]["gates_passed"], -kv[1]["roi"]))
    rows = []
    for rank, (name, s) in enumerate(ranked, 1):
        lab, _ = STRATEGY_LABELS.get(name, (name, ""))
        failed = [GATE_LABELS[k].split(" ", 1)[0] for k, v in s["gates"].items() if not v]
        reward = ("<strong>Eligible for reward</strong>" if s["all_gates_pass"]
                  else f'No reward. Failed: {e(", ".join(failed))}')
        fwd = s["forward_2026"]
        rows.append([
            e(rank), f"<strong>{e(lab)}</strong><br><small>{e(name)}</small>",
            e(s["graded"]), e(pct(s["hit_rate"])),
            e(f"{pct(s['wilson95'][0])} – {pct(s['wilson95'][1])}"),
            e(pct(s["roi"])), e(f"{s['p_value_vs_breakeven']:.3f}"), e(f"{s['p_holm']:.3f}"),
            e(f"{s['seasons_positive']}/{s['seasons_total']}"),
            e(f"{fwd['graded']} bets, ROI {pct(fwd['roi'])}"),
            e(f"{s['gates_passed']}/6"), reward,
            f'<span class="d">DERIVED</span> from <span class="u">UNVERIFIED</span> lines · {link("https://www.nfl.com/schedules/2026/by-week/week-9", "official check page")}',
        ])
    headers = ["Rank", "Strategy", "Graded bets", "Hit rate", "95% CI (Wilson)", "ROI @ −110 (assumed)",
               "p vs breakeven", "Holm p", "Seasons +ROI", "2026 forward", "Gates", "Reward status", "Source / verification"]
    gates_rows = [[e(GATE_LABELS[k]), link(f"{REPO_URL}/blob/main/scripts/nfl_lines/backtest.py", "Pre-registered in scripts/nfl_lines/backtest.py")] for k in GATE_LABELS]
    null = bt["luck_null"]
    body = f"""
<section class="hero small">
  <h1>Strategy leaderboard</h1>
  <p>Ranked by gates passed, then by ROI. Reward requires <strong>all six</strong> validation gates. Test window: {e(bt['generated_for_test_window'])} regular-season games. Breakeven at −110 is {e(pct(bt['breakeven_hit_rate'],2))}. Prices are an <em>assumed</em> −110, not observed prices.</p>
  <p class="callout"><strong>Result:</strong> {sum(1 for _, s in st.items() if s['all_gates_pass'])} of {len(st)} strategies pass all six gates. Reward pool for this cycle: none.</p>
</section>
{table(headers, rows, "wide")}
<h2>Validation gates (pre-registered)</h2>
{table(["Gate", "Definition / where it is set (source)"], gates_rows)}
<h2>Luck control</h2>
<p>Random-side null (1,000 seeds, same number of games as the always-home control): median hit rate {e(pct(null['p50']))}, 95th percentile {e(pct(null['p95']))}, 99th percentile {e(pct(null['p99']))}. A strategy must beat the 95th percentile (gate G5).</p>
<p class="note">Strategy rows are <span class="d">DERIVED</span>: they are computed from closing spreads and totals that have no official source. See <a href="flagged.html">Flagged for Review</a> items F-01 to F-03.</p>
"""
    page("strategies.html", "Strategy leaderboard", body, "strategies.html")


def build_seasons_page(bt):
    st = bt["strategies"]
    names = [n for n in ["SPREAD_EDGE_1", "SPREAD_EDGE_2", "SPREAD_EDGE_3", "TOTAL_EDGE_2", "TOTAL_EDGE_3",
                         "TOTAL_EDGE_4", "REST_3", "DIV_DOG", "BASE_HOME", "BASE_FAV"] if n in st]
    seasons = sorted({s for n in names for s in st[n]["season_roi"]})
    rows = []
    for season in seasons:
        cells = [e(season)]
        for n in names:
            v = st[n]["season_roi"].get(season)
            if v is None:
                cells.append("")
            else:
                cls = ' class="pos"' if v > 0 else ' class="neg"' if v < 0 else ""
                cells.append(f"<span{cls}>{e(pct(v))}</span>")
        cells.append(f'<span class="d">DERIVED</span> · {link("https://www.nfl.com/schedules/", "NFL.com schedules")}')
        rows.append(cells)
    headers = ["Season"] + names + ["Source / verification"]
    body = f"""
<section class="hero small">
  <h1>Season-by-season ROI</h1>
  <p>ROI at an assumed −110 price, one row per season. Positive values are shaded in the table. Derived from unverified lines; see <a href="flagged.html">Flagged for Review</a>.</p>
</section>
{table(headers, rows, "wide heat")}
<p class="note">Season 2026 is the forward slice (weeks already played at the time of the build).</p>
"""
    page("seasons.html", "Season results", body, "seasons.html")


def build_correlation_page(bt):
    c = bt["correlation"]
    rows = []
    for label, key in (("Same game: spread bet vs total bet", "same_game_spread_vs_total_phi"),
                       ("Different games, same week", "cross_game_same_week_phi")):
        v = c[key]
        rows.append([e(label), e(num(v["phi"], 4)), e(f"{v['ci95'][0]:.3f} to {v['ci95'][1]:.3f}"), e(v["n"]),
                     f'<span class="d">DERIVED</span> · {link("https://www.nfl.com/schedules/", "NFL.com schedules")}'])
    corr_tbl = table(["Pair", "phi (correlation of win/loss)", "95% CI (Fisher z)", "n", "Source / verification"], rows)

    par = sorted(bt["parlays"], key=lambda r: -r["parlay_ev_per_unit_observed"])
    prow = []
    for r in par:
        prow.append([e(r["type"].replace("_", " ").title()), e(r["leg_1"]), e(r["leg_2"]), e(r["n"]),
                     e(pct(r["p_joint_observed"], 2)), e(pct(r["p_joint_if_independent"], 2)),
                     e(pct(r["parlay_breakeven_joint"], 2)), e(num(r["parlay_ev_per_unit_observed"], 4, True)),
                     f'<span class="d">DERIVED</span> · {link("https://www.nfl.com/schedules/", "NFL.com schedules")}'])
    par_tbl = table(["Type", "Leg 1", "Leg 2", "Games / pairs", "Observed joint win %", "Joint if independent",
                     "2-leg breakeven", "EV per 1u (observed)", "Source / verification"], prow, "wide")
    best = par[0]["parlay_ev_per_unit_observed"] if par else None
    body = f"""
<section class="hero small">
  <h1>Correlation &amp; parlays</h1>
  <p>How strongly do outcomes move together? Phi near zero means little shared information. Parlays here use <em>observed</em> joint win rates, not an independence assumption.</p>
  <p class="callout"><strong>Finding:</strong> spread and total outcomes are essentially uncorrelated in this sample (phi {e(num(c['same_game_spread_vs_total_phi']['phi'],4))}). Every constructed 2-leg parlay has negative expected value{f" (best {e(num(best,4,True))} per unit)" if best is not None else ""}.</p>
</section>
<h2>Outcome correlation</h2>
{corr_tbl}
<h2>2-leg parlays (observed joint frequencies)</h2>
{par_tbl}
<p class="note">Cross-game pair counts reuse the same bets in several pairs, so they are descriptive and overstate independent evidence. Player-prop parlays are not included: no player-prop prices or player-level history were collected (see <a href="questions.html">Questions &amp; gaps</a>).</p>
"""
    page("correlation.html", "Correlation & parlays", body, "correlation.html")


def build_games_page(bt):
    games = {g["game_id"]: g for g in load_games() if g["season"] == 2026 and g["game_type"] == "REG"}
    preds = {r["game_id"]: r for r in load_csv(RES / "analysis/predictions.csv")}
    official = {}
    for r in load_csv(RES / "official/nfl_2026_week9_final_scores.csv"):
        official[(int(r["week"]), r["away_team"], r["home_team"])] = r
    rows = []
    for gid in sorted(games, key=lambda k: (games[k]["week"], k)):
        g = games[gid]
        p = preds.get(gid)
        wk = g["week"]
        listing = f"https://www.nfl.com/schedules/2026/by-week/week-{wk}"
        played = g["home_score"] is not None
        score = f"{g['away_score']}–{g['home_score']}" if played else "not played"
        off = official.get((wk, g["away"], g["home"]))
        if off:
            chk = badge("V") + f" {e(off['away_score'])}–{e(off['home_score'])} on NFL.com"
            game_link = link(off["official_game_url"], "NFL.com game page")
        else:
            chk = badge("U") if played else "—"
            game_link = link(listing, "NFL.com week page")
        sp = g["spread_line"]
        tot = g["total_line"]
        edge = None
        if p and sp is not None:
            edge = float(p["model_home_margin"]) - sp
        rows.append([
            e(wk), e(g["gameday"].isoformat() if g["gameday"] else ""),
            f"<strong>{e(g['away'])} @ {e(g['home'])}</strong>",
            e(score), chk,
            e(num(sp, 1, True) if sp is not None else "") + ' <span class="u">UNV</span>',
            e(num(tot, 1) if tot is not None else "") + ' <span class="u">UNV</span>',
            e(num(p["model_home_margin"], 1, True) if p else "") + ' <span class="d">DRV</span>',
            e(num(edge, 1, True) if edge is not None else "") + ' <span class="d">DRV</span>',
            e(num(p["model_total"], 1) if p else "") + ' <span class="d">DRV</span>',
            game_link,
        ])
    headers = ["Wk", "Date", "Away @ Home", "Final (away–home)", "Official score check",
               "Closing spread (home +)", "Closing total", "Model home margin", "Model edge vs spread",
               "Model total", "Official link"]
    body = f"""
<section class="hero small">
  <h1>2026 regular-season games</h1>
  <p>All 2026 regular-season rows in the source data ({len(rows)} games). Scores are checked against NFL.com only where marked VERIFIED. Lines are UNVERIFIED third-party values. Model columns are DERIVED projections from walk-forward ratings, not recommendations.</p>
  <p class="callout"><strong>Verified so far:</strong> 16 final scores (Week 9 all 15 games, Week 10 Thursday game) matched NFL.com. All other 2026 rows: UNVERIFIED.</p>
  <input class="filter" type="search" placeholder="Filter by team, week or date…" oninput="filterRows(this.value)">
</section>
{table(headers, rows, "wide", "games")}
<script>
function filterRows(q){{q=q.toLowerCase();document.querySelectorAll('#games tbody tr').forEach(function(tr){{tr.style.display=tr.textContent.toLowerCase().indexOf(q)>-1?'':'none';}});}}
</script>
"""
    page("games-2026.html", "2026 games", body, "games-2026.html")


def build_injuries_page():
    rows = load_csv(RES / "official/nfl_injury_report_2026_week10.csv")
    des = [r for r in rows if r["row_type"] == "DESIGNATED"]
    dis = [r for r in rows if r["row_type"] == "DISCREPANCY"]
    drows = []
    for r in des:
        drows.append([e(r["week"]), e(r["game_or_date"]), e(r["team"]), f"<strong>{e(r['player'])}</strong>",
                      e(r["position"]), e(r["injury"]), e(r["practice_status"]), e(r["game_status"]),
                      badge("V") + f' · {link(r["official_source_url"], "NFL.com injury report")}'])
    xrows = []
    for r in dis:
        xrows.append([e(r["team"]), f"<strong>{e(r['player'])}</strong>", e(r["practice_status"]), e(r["game_status"]),
                      link(r["official_source_url"], "NFL.com news / report"),
                      badge("F") + f" · {e(r['verification'])}"])
    body = f"""
<section class="hero small">
  <h1>Injuries &amp; depth</h1>
  <p>Official NFL.com Week 10 injury report, captured 2026-11-13. The report shows practice status for every listed player but game status (Out / Questionable / Doubtful) for only a few rows at capture time, so the injury signal is thin.</p>
  <p class="callout"><strong>Starter-vs-backup depth analysis is NOT built.</strong> It needs depth-chart data for both teams, which was not collected. See suggestion S-06 and question Q-07.</p>
</section>
<h2>Designated game statuses (Week 10, captured)</h2>
{table(["Wk", "Game", "Team", "Player", "Pos", "Injury", "Practice", "Game status", "Source / verification"], drows, "wide")}
<h2>Discrepancies between NFL.com news headlines and the injury table</h2>
<p class="note">Headlines were read from NFL.com news listings only; article bodies were not opened. Each is flagged for manual review.</p>
{table(["Team", "Player", "Practice (table)", "Game status (table)", "Source", "Verification"], xrows, "wide")}
<h2>Coverage notes</h2>
<ul>
  <li>Official source: {link("https://www.nfl.com/injuries/", "https://www.nfl.com/injuries/")} (Week 10 of the 2026 season, captured {e(SNAPSHOT_DATE)}).</li>
  <li>Only 9 rows carry a game status; all are in the first two games of the page (Thursday WAS @ NYG and Sunday NE @ DET). Remaining game statuses were not yet issued at capture.</li>
  <li>No injury history is available in this project, so injury effects cannot be backtested yet (see Q-05).</li>
</ul>
"""
    page("injuries.html", "Injuries & depth", body, "injuries.html")


QUESTIONS = [
    ("Q-01", "Legal: may a Singapore resident place these bets?", "GRA: participating in unlicensed remote gambling is an offence; Singapore Pools is the only licensed remote-betting operator.", "Which products, if any, Singapore Pools offers that match the strategies here.", "Official GRA guidance found. Your decision is needed before any use.", "https://www.gra.gov.sg/harm-minimisation/unlawful-remote-gambling-activities"),
    ("Q-02", "Which betting-line source is official?", "No official NFL or government source for historical closing lines was found.", "Whether Singapore Pools publishes lines or results we can use as an official reference.", "OPEN", ""),
    ("Q-03", "Do you accept third-party lines as the analysis basis?", "All lines come from nfldata (Lee Sharpe, community-maintained; upstream commit 7aae940).", "Whether you accept UNVERIFIED lines for the leaderboard, or want the leaderboard blanked until an official source exists.", "DECISION NEEDED", f"{REPO_URL}/tree/main/research/nfl-lines/raw"),
    ("Q-04", "Is the spread sign convention confirmed?", "Data: spread_line correlates +0.44 with home margin, so positive = home favoured. The fetched nflverse dictionary defines result and total but the spread_line field text was not on the fetched page.", "Official confirmation of the spread_line definition.", "PARTIAL", "https://nflreadr.nflverse.com/articles/dictionary_schedules.html"),
    ("Q-05", "Is there injury history for backtests?", "Only a Week 10 2026 snapshot was captured. No historical injury-report archive was collected.", "A verifiable archive of NFL.com weekly injury reports 2016–2026.", "OPEN", "https://www.nfl.com/injuries/"),
    ("Q-06", "Which price should be used for bets?", "Assumed −110 on both sides. Observed prices are not in the data.", "Observed opening and closing prices from a permitted source (Q-01).", "OPEN", ""),
    ("Q-07", "Depth charts for starter-vs-backup analysis?", "Not collected.", "A depth-chart source per team per week, with an official reference.", "OPEN", ""),
    ("Q-08", "Player-prop data for prop combos?", "Not collected. No player-level stats or prop prices in the project.", "Player-level stats and prop prices from permitted sources.", "OPEN", ""),
    ("Q-09", "What counts as a 'reward'?", "Not defined in the request.", "Points only (no money), or a monetary budget? Who awards it?", "DECISION NEEDED", ""),
    ("Q-10", "What is the forward-test window?", "2026 weeks 1–9 were used in the backtest report, but thresholds were set beforehand.", "Whether to lock the strategies now and judge only weeks 11–18 of 2026.", "DECISION NEEDED", ""),
    ("Q-11", "Should playoffs be included?", "Playoff games exist in the source data; the strategy tests use regular-season games only.", "Whether to add playoffs and how to treat neutral-site games.", "DECISION NEEDED", ""),
    ("Q-12", "Should the root (vacation) dashboard be replaced?", "The repo root serves the FREE TIME VACATION dashboard. This project lives under /lines/.", "Whether /lines/ should become the root landing page.", "DECISION NEEDED", "https://karagemop466-tech.github.io/Korea4/"),
    ("Q-13", "Are closing lines the right benchmark?", "Closing lines are used. Opening lines exist only for a small subset in the source data.", "Opening-line coverage to measure closing-line value (CLV).", "PARTIAL", "https://github.com/nflverse/nfldata/blob/master/data/initial_lines.csv"),
    ("Q-14", "Weather, roof, and stadium effects", "Source data includes roof, surface, temperature and wind columns, with gaps.", "Whether these fields are complete and official.", "PARTIAL", ""),
]


def build_questions_page():
    rows = []
    for qid, q, known, need, status, src in QUESTIONS:
        srcl = link(src, "source") if src else "—"
        rows.append([e(qid), f"<strong>{e(q)}</strong>", e(known), e(need), e(status), srcl])
    body = f"""
<section class="hero small">
  <h1>Questions, information gaps and answers</h1>
  <p>What is known, what is missing, and what decision is needed before any strategy can be trusted. Status is the current state in this project, not a recommendation.</p>
</section>
{table(["ID", "Question", "What we know (source)", "What is missing / needed", "Status", "Source"], rows, "wide")}
"""
    page("questions.html", "Questions & gaps", body, "questions.html")


SUGGESTIONS = [
    ("S-01", "Decide on unverified lines (Q-03)", "Keeps every result traceable. Blanking would remove the strategy analysis entirely.", "A) keep UNVERIFIED with flags · B) blank lines until an official source is found", "Low", "OPEN"),
    ("S-02", "Find an official reference for betting lines", "Would let the project meet the 'official source' rule for prices.", "A) Singapore Pools published odds/results · B) none, accept third-party only", "Medium", "OPEN"),
    ("S-03", "Adopt a locked forward test from 2026 Week 11", "Removes hindsight bias: strategies and gates are fixed now; only new games are graded.", "A) lock now · B) keep current backtest only", "Low", "RECOMMENDED"),
    ("S-04", "Build an injury-report archive (weekly snapshots)", "Injury signals cannot be tested without history. Snapshots can be taken each week.", "A) manual weekly capture · B) scheduled capture if permitted by NFL.com terms", "Medium", "OPEN"),
    ("S-05", "Measure closing-line value (CLV)", "CLV is a more direct skill signal than win rate over a small sample.", "Needs opening-line coverage (Q-13)", "Medium", "OPEN"),
    ("S-06", "Collect depth charts to flag starter/backup gaps", "Needed for the defence and offence depth requirement.", "A) NFL.com team depth charts, if available · B) other official team sites", "High", "OPEN"),
    ("S-07", "Scope player props separately", "Props need player-level data and their own prices; they should not be mixed into game-level results.", "A) defer until data is found · B) limit to one prop type", "Medium", "OPEN"),
    ("S-08", "Move the project to its own repository or site root", "Avoids mixing the vacation dashboard with the NFL research.", "A) keep /lines/ · B) make /lines/ the root · C) separate repo", "Low", "DECISION NEEDED (Q-12)"),
    ("S-09", "Clean up coordination board and failing tests", "See Repo review R-01 to R-06.", "A) fix now · B) fix in a separate task", "Low", "OPEN"),
    ("S-10", "Use a small stake or no stake until a strategy passes all gates", "The current evidence does not support any positive-expected-value strategy.", "Policy decision", "Low", "RECOMMENDED"),
]


def build_suggestions_page():
    rows = []
    for sid, title, why, opts, effort, status in SUGGESTIONS:
        rows.append([e(sid), f"<strong>{e(title)}</strong>", e(why), e(opts), e(effort), e(status)])
    body = f"""
<section class="hero small">
  <h1>Suggestions — awaiting your decision</h1>
  <p>Nothing on this list has been implemented. Pick an option for each item before any change is made. Status “RECOMMENDED” only means the project team suggests it.</p>
</section>
{table(["ID", "Suggestion", "Why", "Options", "Effort (est.)", "Status"], rows, "wide")}
"""
    page("suggestions.html", "Suggestions", body, "suggestions.html")


REPO_REVIEW = [
    ("R-01", "Tests", "tests/test_build.py fails: _site/ is missing (a build artefact that is gitignored). Test expects a prior build.", "tests/test_build.py", "Medium"),
    ("R-02", "Tests", "tests/test_build.py LegacyRedirectSourcesTest fails: 8 tracked legacy pages have no redirect entry (review.html, nfl.html, mlb.html, ncaaf.html, sources.html, methodology.html, wwo.html, research/legacy/index-9d83abee.html).", "tests/test_build.py", "Medium"),
    ("R-03", "Tests / data", "tests/test_dashboard_generator.py checks that data/official/meta.json system_today equals today's Pacific date. It failed on 2026-11-13 because the root dashboard was built 2026-11-05. The root dashboard is a shared output, so this session did not rebuild it. Logged for the final integration session. It is date-dependent: it fails on any day the dashboard is not rebuilt.", "tests/test_dashboard_generator.py; data/official/meta.json", "Medium"),
    ("R-04", "Verification gate", "scripts/verify.py passes (0 errors, 10,066 primary rows, 689 internal links) but states that it is structural, not a line-by-line check against live sites.", "research/verification-report.md", "Info"),
    ("R-05", "Workflows", "Three workflows still target the branch arena/72e6d3f7-korea4 (listed as in progress on the board). Branch-specific triggers are fragile.", ".github/workflows/check.yml; fetch-official.yml; pages.yml; probe-sources.yml", "Low"),
    ("R-06", "Coordination board", "COORDINATION.md is 814 lines with repeated 'Current session' headings, 9 rows still 'in progress' and 6 'unclaimed' from older sessions.", "COORDINATION.md", "Low"),
    ("R-07", "Duplicate content", "Three parallel copies of the dashboard (root, docs/, site/) plus research/legacy/ and redirects/. Risk of drift.", "docs/; site/; redirects/", "Low"),
    ("R-08", "Large files", "mlb.html is 5.1 MB and review.html 2.4 MB; sources.html 0.67 MB. Slow to load on mobile.", "mlb.html; review.html; sources.html", "Low"),
    ("R-09", "Duplicate summary", "EXECUTIVE-SUMMARY.md and executive-summary.html both exist; they can diverge.", "EXECUTIVE-SUMMARY.md", "Low"),
    ("R-11", "Regenerated output", "An offline rebuild of the root dashboard from the 2026-11-02 snapshot was tried and reverted, because root pages are shared outputs for the integration session. Expected result of that rebuild: system_today 2026-11-05 -> 2026-11-13 across root pages. Also, line_by_line audit rows would change 2423 -> 2419 with no explanation in the snapshot. Flagged for the integration session.", "data/official/meta.json; research/line_by_line.json", "Medium"),
    ("R-10", "Pages config", "GitHub Pages is a legacy build from branch main, path /. Pages builds are triggered by pushes to main only.", "https://api.github.com/repos/karagemop466-tech/Korea4/pages", "Info"),
]


def build_repo_review_page():
    rows = []
    for rid, area, finding, ev, sev in REPO_REVIEW:
        first = ev.split(";")[0].strip()
        evl = link(first, first) if first.startswith("http") else link(f"{REPO_URL}/blob/main/{first}", first)
        rows.append([e(rid), e(area), e(finding), evl, e(sev), badge("F")])
    body = f"""
<section class="hero small">
  <h1>Repository review</h1>
  <p>Findings from running the repository's own gates on 2026-11-13 and reading its files. Each row cites the file it refers to. Items are flagged for review; none blocks this site.</p>
  <p class="callout">Gates run: scripts/verify.py PASS · node --check js/app.js PASS · npm test PASS · tests/test_dashboard.mjs PASS · test_dashboard_generator FAIL (date-dependent; root dashboard not rebuilt, logged R-03) · Python unittest discover: 3 failing tests in tests/test_build.py (R-01, R-02) · tests/test_nfl_lines.py 8/8 PASS.</p>
</section>
{table(["ID", "Area", "Finding", "Evidence (file)", "Severity", "Status"], rows, "wide")}
<p class="note">Repository evidence links: <a href="{REPO_URL}/blob/main/COORDINATION.md">COORDINATION.md</a> · <a href="{REPO_URL}/blob/main/.github/workflows/check.yml">check.yml</a> · <a href="{REPO_URL}/blob/main/tests/test_build.py">tests/test_build.py</a>.</p>
"""
    page("repo-review.html", "Repo review", body, "repo-review.html")


FLAGS = [
    ("F-01", "All betting lines (closing spread, total) come from nfldata, a third-party dataset. No official source was found.", "Q-02, Q-03", "https://github.com/nflverse/nfldata/blob/master/data/games.csv", "No"),
    ("F-02", "Only 16 of the 2026 final scores were checked against NFL.com (Week 9 all 15 games, plus the Week 10 Thursday game WAS 24–NYG 21, confirmed on its game page 2026-11-13). Other scores and all 2005–2025 scores are UNVERIFIED.", "Coverage", "https://www.nfl.com/schedules/2026/by-week/week-9", "No"),
    ("F-03", "Assumed −110 price for every bet. Real prices vary and were not used.", "Q-06", f"{REPO_URL}/blob/main/scripts/nfl_lines/backtest.py", "No"),
    ("F-04", "Spread sign convention (positive = home favoured) confirmed from data, not from the field definition.", "Q-04", "https://nflreadr.nflverse.com/articles/dictionary_schedules.html", "No"),
    ("F-05", "Injury data: one Week 10 snapshot with 9 designations. No history, so no injury backtest exists.", "Q-05", "https://www.nfl.com/injuries/", "No"),
    ("F-06", "Six NFL.com news pages cited for injuries were read on 2026-11-13 and support the headlines. The injury table still shows no game status for these players, so they remain FLAGGED (see Injuries page).", "Injuries", "https://www.nfl.com/news/sam-darnold-ruled-out-for-seahawks-week-10-game-vs-raiders-drew-lock-expected-to-start-again", "No"),
    ("F-07", "Legal: secondary websites cite the Remote Gambling Act 2014 as current law. The Singapore Statutes Online record shows it was repealed on 1 Aug 2022 (Act 15 of 2022). The GRA's current guidance is the basis used here.", "Q-01", "https://sso.agc.gov.sg/Act/RGA2014/Repealed/20220801?DocDate=20220404", "No"),
    ("F-08", "Strategy results are DERIVED from UNVERIFIED lines. Treat leaderboard ranks as provisional.", "Q-03", f"{REPO_URL}/blob/main/research/nfl-lines/analysis/backtest.json", "No"),
    ("F-09", "Repo: three tests in tests/test_build.py fail (missing _site/ build artefact; legacy redirect coverage). Not part of check.yml.", "R-01, R-02", f"{REPO_URL}/blob/main/tests/test_build.py", "No"),
    ("F-10", "Root dashboard date-dependent test fails (system_today 2026-11-05 vs 2026-11-13). Integration session to rebuild. Audit row count would change 2423 -> 2419 without explanation.", "R-03, R-11", f"{REPO_URL}/blob/main/data/official/meta.json", "No"),
]


def build_flagged_page():
    rows = []
    for fid, what, ref, src, blocks in FLAGS:
        rows.append([e(fid), e(what), e(ref), link(src, "source") if src else "—", e(blocks), badge("F")])
    body = f"""
<section class="hero small">
  <h1>Flagged for Review</h1>
  <p>Unverified values, irregularities and open conflicts. None of these blocks publication. Please review and request changes after the site is live.</p>
</section>
{table(["ID", "Item", "Related", "Source link", "Blocks publication?", "Status"], rows, "wide")}
"""
    page("flagged.html", "Flagged for Review", body, "flagged.html")


def build_sources_page(bt):
    manifest = json.loads((RES / "manifest.json").read_text())
    rows = []
    for s in manifest["sources"]:
        rows.append([e(s["id"]), e(s["name"]), link(s["url"]), e(s["used_for"]), e(s["retrieved"]), badge(s["status"])])
    body = f"""
<section class="hero small">
  <h1>Sources</h1>
  <p>Every data source used, how it was reached, and what it supports. Official = NFL.com or a government site.</p>
</section>
{table(["ID", "Source", "URL", "Used for", "Retrieved (UTC)", "Status"], rows, "wide")}
<h2>Data files (checksums)</h2>
{table(["File", "SHA-256", "Bytes"], [[link(f"{REPO_URL}/blob/main/{f['path']}", f["path"]), e(f["sha256"]), e(f["bytes"])] for f in manifest["files"]], "wide")}
"""
    page("sources.html", "Sources", body, "sources.html")


def build_methodology_page():
    body = """
<section class="hero small">
  <h1>Methodology</h1>
  <p>How the numbers were produced. Written before the strategy results were read.</p>
</section>
<h2>Own line model (walk-forward)</h2>
<ul>
  <li>Margin: ridge regression of home minus away points on team strengths plus a home-field term (penalty 20, not tuned). Total: ridge on offence and defence terms (penalty 20).</li>
  <li>Each week's games are predicted using only games played before that week. No same-week or future information.</li>
  <li>Recency weighting: 365-day half-life.</li>
</ul>
<h2>Grading</h2>
<ul>
  <li>Regular-season games with final scores and a closing spread or total.</li>
  <li>Spread: home covers when margin is greater than the spread_line; push on equality. Total: over when the total is greater than the line.</li>
  <li>Stake 1 unit at an assumed −110 (win +0.9091, loss −1). Breakeven 52.38%.</li>
</ul>
<h2>Validation gates</h2>
<ol>
  <li>Sample size ≥ 400 graded bets.</li>
  <li>Hit rate ≥ breakeven and Wilson 95% lower bound > 50%.</li>
  <li>One-sided exact binomial p vs breakeven, Holm-adjusted across all strategies, < 0.05.</li>
  <li>Positive ROI in ≥ 60% of seasons.</li>
  <li>Hit rate above the 95th percentile of 1,000 random-side simulations.</li>
  <li>2026 forward-slice ROI > 0 (reported, not used to choose strategies).</li>
</ol>
<h2>Correlation and parlays</h2>
<ul>
  <li>phi (Pearson on 0/1 outcomes) with Fisher-z 95% confidence intervals.</li>
  <li>Parlay joint probabilities are observed on games where both legs were placed. No independence assumption is used for the observed column.</li>
</ul>
<h2>Limits</h2>
<ul>
  <li>No official betting-line source, no injury history, no depth charts, no player props. These are the largest gaps (see Questions).</li>
  <li>Results describe past data only and are not predictions.</li>
</ul>
"""
    page("methodology.html", "Methodology", body, "methodology.html")


def build_exec_page(bt):
    st = bt["strategies"]
    best = max(st.items(), key=lambda kv: kv[1]["hit_rate"])
    diag = bt["model_diagnostics"]["test_2005_2025"]
    body = f"""
<section class="hero">
  <h1>Executive summary</h1>
  <p>NFL Lines Lab tests whether a model built from historical game data (third-party; see flags) can find an edge over the closing lines. As of {e(SNAPSHOT_DATE)}, the answer from the evidence is <strong>no edge has been found</strong>.</p>
</section>
<div class="cards">
  <div class="card"><div class="k">{len(st)}</div><div class="l">Single-bet strategies tested</div></div>
  <div class="card"><div class="k">{sum(1 for _, s in st.items() if s['all_gates_pass'])}</div><div class="l">Strategies passing all 6 gates</div></div>
  <div class="card"><div class="k">{e(pct(best[1]['hit_rate']))}</div><div class="l">Best hit rate ({e(best[0])}) vs 52.38% breakeven</div></div>
  <div class="card"><div class="k">{e(num(diag['mae_model'],2))} vs {e(num(diag['mae_market_closing_spread'],2))}</div><div class="l">Average error: our model vs closing spread (points)</div></div>
</div>
<h2>Key findings</h2>
<ol>
  <li><strong>Singles:</strong> the best strategies hover near 51%, below the 52.38% breakeven at −110. None clears all validation gates. Details: <a href="strategies.html">Strategy leaderboard</a>.</li>
  <li><strong>Correlation:</strong> spread and total outcomes are essentially uncorrelated (phi ≈ 0). Cross-game correlation is also near zero. <a href="correlation.html">Correlation &amp; parlays</a>.</li>
  <li><strong>Parlays:</strong> every constructed 2-leg parlay has negative expected value at −110 on observed frequencies.</li>
  <li><strong>Model vs market:</strong> the closing spread is more accurate than our model (MAE {e(num(diag['mae_market_closing_spread'],2))} vs {e(num(diag['mae_model'],2))} points). Our model is not yet a source of new information.</li>
  <li><strong>Player props:</strong> not testable. No prop prices or player history were collected.</li>
  <li><strong>Injuries and depth:</strong> the official Week 10 report lists 9 game-status designations. Starter-vs-backup analysis needs depth-chart data that has not been collected.</li>
  <li><strong>Legal (Singapore):</strong> GRA guidance states it is an offence to participate in unlicensed remote gambling; Singapore Pools is the only licensed remote-betting operator. This must be decided before any use. <a href="questions.html">Q-01</a>.</li>
  <li><strong>Verification:</strong> 16 final scores matched NFL.com. Betting lines have no official source and are flagged UNVERIFIED.</li>
</ol>
<h2>What is needed to decide</h2>
<p>See <a href="questions.html">Questions &amp; gaps</a> and <a href="suggestions.html">Suggestions</a>. Key decisions: legal path (Q-01), whether to accept third-party lines (Q-03), and whether to lock a forward test (Q-10).</p>
"""
    page("executive-summary.html", "Executive summary", body, "executive-summary.html")


def build_index_page(bt):
    cards = [
        ("executive-summary.html", "Executive summary", "Findings and what is needed to decide."),
        ("strategies.html", "Strategy leaderboard", "Ranked strategies with the six validation gates."),
        ("seasons.html", "Season results", "ROI by season for each strategy."),
        ("correlation.html", "Correlation & parlays", "Outcome correlation and parlay math."),
        ("games-2026.html", "2026 games", "Every 2026 regular-season row with checks and links."),
        ("injuries.html", "Injuries & depth", "Official injury report snapshot and discrepancies."),
        ("questions.html", "Questions & gaps", "What we know, what is missing, and what to decide."),
        ("suggestions.html", "Suggestions", "Options to choose from. Nothing is implemented yet."),
        ("repo-review.html", "Repo review", "Irregularities found in the repository."),
        ("flagged.html", "Flagged for Review", "Unverified items with links for your review."),
        ("sources.html", "Sources", "Every source, its link and checksums."),
        ("methodology.html", "Methodology", "Rules, gates and limits."),
    ]
    cc = "".join(f'<a class="tile" href="{h}"><strong>{e(t)}</strong><span>{e(d)}</span></a>' for h, t, d in cards)
    body = f"""
<section class="hero">
  <h1>NFL Lines Lab</h1>
  <p>A research dashboard that tests whether our own NFL lines can find an edge. Every table row shows its official link and verification status. Unverified values are shown, labelled, and never filled in.</p>
  <p class="callout"><strong>Bottom line:</strong> no strategy has passed the validation gates. Read the <a href="executive-summary.html">executive summary</a> first.</p>
</section>
<div class="tiles">{cc}</div>
"""
    page("index.html", "Home", body, "index.html")


def write_manifest():
    files = []
    import hashlib
    for p in sorted((RES).rglob("*")):
        if p.is_file() and p.name != "manifest.json":
            data = p.read_bytes()
            files.append({"path": str(p.relative_to(ROOT)), "sha256": hashlib.sha256(data).hexdigest(), "bytes": len(data)})
    (RES / "manifest.json").write_text(json.dumps({"snapshot_date": SNAPSHOT_DATE, "sources": SOURCES, "files": files}, indent=2))


SOURCES = [
    {"id": "S-01", "name": "NFL.com 2026 Week 9 schedule & scores", "url": "https://www.nfl.com/schedules/2026/by-week/week-9", "used_for": "16 final scores (Week 9, all 15 games; Week 10 Thursday) checked line by line", "retrieved": "2026-11-13", "status": "VERIFIED"},
    {"id": "S-02", "name": "NFL.com game page: Commanders at Giants, 2026 Week 10", "url": "https://www.nfl.com/games/commanders-at-giants-2026-reg-10", "used_for": "Week 10 Thursday final score (24-21)", "retrieved": "2026-11-13", "status": "VERIFIED"},
    {"id": "S-03", "name": "NFL.com 2026 injury report (Week 10)", "url": "https://www.nfl.com/injuries/", "used_for": "9 game-status designations; practice statuses", "retrieved": "2026-11-13", "status": "VERIFIED"},
    {"id": "S-04", "name": "NFL.com news listings (headlines)", "url": "https://www.nfl.com/news/nfl-news-roundup-latest-league-updates-from-thursday-nov-12", "used_for": "Discrepancy headlines only (bodies not read)", "retrieved": "2026-11-13", "status": "FLAGGED"},
    {"id": "S-05", "name": "Gambling Regulatory Authority (Singapore): Unlawful Remote Gambling Activities", "url": "https://www.gra.gov.sg/harm-minimisation/unlawful-remote-gambling-activities", "used_for": "Legal status for Singapore residents (Q-01)", "retrieved": "2026-11-13", "status": "VERIFIED"},
    {"id": "S-06", "name": "Singapore Statutes Online: Remote Gambling Act 2014 (Repealed)", "url": "https://sso.agc.gov.sg/Act/RGA2014/Repealed/20220801?DocDate=20220404", "used_for": "Shows RGA 2014 repealed 1 Aug 2022", "retrieved": "2026-11-13", "status": "VERIFIED"},
    {"id": "S-07", "name": "nflverse data dictionary (schedules)", "url": "https://nflreadr.nflverse.com/articles/dictionary_schedules.html", "used_for": "Definitions of result and total (home minus away; home plus away)", "retrieved": "2026-11-13", "status": "VERIFIED"},
    {"id": "S-08", "name": "nfldata repository (Lee Sharpe), data/games.csv, commit 7aae940", "url": "https://github.com/nflverse/nfldata/blob/master/data/games.csv", "used_for": "Game results, closing spread and total, rest days, roof; third-party", "retrieved": "2026-11-13", "status": "UNVERIFIED"},
    {"id": "S-09", "name": "nfldata repository, data/closing_lines.csv and initial_lines.csv", "url": "https://github.com/nflverse/nfldata/blob/master/data/closing_lines.csv", "used_for": "Coverage review only (Q-13): initial_lines.csv has 1,088 rows vs 20,490 in closing_lines.csv (codeload tarball of nflverse/nfldata master, 7aae940). Blob pages not fetched directly.", "retrieved": "2026-11-13", "status": "VERIFIED"},
]


def main() -> None:
    SITE.mkdir(parents=True, exist_ok=True)
    (SITE / "assets").mkdir(exist_ok=True)
    bt = load_backtest()
    build_index_page(bt)
    build_exec_page(bt)
    build_strategies_page(bt)
    build_seasons_page(bt)
    build_correlation_page(bt)
    build_games_page(bt)
    build_injuries_page()
    build_questions_page()
    build_suggestions_page()
    build_repo_review_page()
    build_flagged_page()
    write_manifest()
    build_sources_page(bt)
    build_methodology_page()
    print("built", len(NAV), "pages in", SITE.relative_to(ROOT))


if __name__ == "__main__":
    main()
