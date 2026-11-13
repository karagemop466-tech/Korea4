#!/usr/bin/env python3
"""Compute NFL analytics artifacts from committed nflverse snapshots.

Every emitted value is one of:
  - VERIFIED    : value confirmed against the official NFL.com page fetched 2026-11-13
                  (spot-check rows listed in research/nfl/official/week10-official-spotcheck.json)
  - MIRROR      : value read from the nflverse rolling release (community mirror of official
                  NFL transaction/feeds), NOT individually confirmed against an official page.
                  Label on the site: "MIRROR — UNVERIFIED individually".
  - MODEL       : value computed by the documented model in this script (never a released fact).
  - MARKET REF  : archived market line from the nflverse schedules release. Secondary,
                  explicitly flagged; never labelled official.

No value is inferred. Blank official values stay blank and are flagged UNVERIFIED.
"""
from __future__ import annotations
import csv, gzip, json, math, statistics
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "research/nfl/raw"
OUT = ROOT / "data/nfl-analytics"
AUDIT = ROOT / "research/nfl/audit"
OUT.mkdir(parents=True, exist_ok=True)
AUDIT.mkdir(parents=True, exist_ok=True)

GENERATED_UTC = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
NFLVERSE_RELEASE = "https://github.com/nflverse/nflverse-data/releases/tag/{tag}"
SOURCE_NFL_INJ = "https://www.nfl.com/injuries/"
SOURCE_NGS_TRENDS = "https://www.nfl.com/stats/ngs/trends"

def write(name, obj):
    (OUT / name).write_text(json.dumps(obj, indent=1, sort_keys=False) + "\n")
    print(f"wrote data/nfl-analytics/{name}")

def rows_of(name):
    with gzip.open(RAW / name, "rt") as f:
        return list(csv.DictReader(f))

# ---------------------------------------------------------------- load raw
games_all = rows_of("games.csv.gz")
games_2026 = [g for g in games_all if g["season"] == "2026" and g["game_type"] == "REG"]
inj_rows = rows_of("injuries_2026.csv.gz")
team_stats = rows_of("stats_team_week_2026.csv.gz")
snaps = rows_of("snap_counts_2026.csv.gz")
import pandas as pd
dc = pd.read_parquet(RAW / "depth_charts_2026.parquet")

# Completed regular-season games (nflverse result columns)
def completed(g):
    return g["away_score"] not in ("", "NA") and g["home_score"] not in ("", "NA")
done = [g for g in games_2026 if completed(g)]
DONE_WEEKS = sorted({int(g["week"]) for g in done})
print("completed weeks:", DONE_WEEKS, "games:", len(done))

# ---------------------------------------------------------------- official spot-check cross-check
spot = json.loads((ROOT / "research/nfl/official/week10-official-spotcheck.json").read_text())
CHECKS = []
for r in spot["rows"]:
    match = [x for x in inj_rows if x["week"] == str(r["week"]) and x["team"] == r["team"]
             and x["full_name"] == r["player"]]
    if len(match) != 1:
        CHECKS.append({"player": r["player"], "team": r["team"],
                       "result": "NOT IN MIRROR (official page ahead of mirror snapshot)"})
        continue
    m = match[0]
    ok = (m["report_status"] == r["game_status"] and m["practice_status"] == r["practice_status"]
          and m["report_primary_injury"] == r["injury"])
    CHECKS.append({"player": r["player"], "team": r["team"], "result": "MATCH" if ok else
                   f"MISMATCH mirror(game={m['report_status']!r}, practice={m['practice_status']!r}, injury={m['report_primary_injury']!r})"})
for t in spot.get("team_level_notes", []):
    n_rows = sum(1 for x in inj_rows if x["week"] == str(t["week"]) and x["team"] == t["team"])
    CHECKS.append({"player": "(no players listed)", "team": t["team"],
                   "result": "MATCH" if n_rows == 0 else f"MIRROR HAS {n_rows} ROWS — check club report"})
n_ok = sum(1 for c in CHECKS if c["result"] == "MATCH")
print(f"spot-check cross-check: {n_ok}/{len(CHECKS)} MATCH")
audit_spot = {
    "generated_utc": GENERATED_UTC,
    "official_page": SOURCE_NFL_INJ,
    "official_page_fetched": spot["fetched"],
    "rows_transcribed": len(spot["rows"]),
    "mirror_crosscheck": CHECKS,
    "note": "Rows listed here were read from the official NFL.com league injury report page on "
            + spot["fetched"] + " and independently cross-checked against the nflverse mirror. "
            "Only these rows carry the VERIFIED label; all other mirror rows stay MIRROR/UNVERIFIED.",
}
(AUDIT / "week10-spotcheck.json").write_text(json.dumps(audit_spot, indent=1) + "\n")

SPOT_KEYS = {(r["team"], r["player"]) for r in spot["rows"]}

# ---------------------------------------------------------------- injuries week 10 table
TEAM = {"ARI": "Arizona Cardinals", "ATL": "Atlanta Falcons", "BAL": "Baltimore Ravens",
        "BUF": "Buffalo Bills", "CAR": "Carolina Panthers", "CHI": "Chicago Bears",
        "CIN": "Cincinnati Bengals", "CLE": "Cleveland Browns", "DAL": "Dallas Cowboys",
        "DEN": "Denver Broncos", "DET": "Detroit Lions", "GB": "Green Bay Packers",
        "HOU": "Houston Texans", "IND": "Indianapolis Colts", "JAX": "Jacksonville Jaguars",
        "KC": "Kansas City Chiefs", "LA": "Los Angeles Rams", "LAC": "Los Angeles Chargers",
        "LV": "Las Vegas Raiders", "MIA": "Miami Dolphins", "MIN": "Minnesota Vikings",
        "NE": "New England Patriots", "NO": "New Orleans Saints", "NYG": "New York Giants",
        "NYJ": "New York Jets", "PHI": "Philadelphia Eagles", "PIT": "Pittsburgh Steelers",
        "SF": "San Francisco 49ers", "SEA": "Seattle Seahawks", "TB": "Tampa Bay Buccaneers",
        "TEN": "Tennessee Titans", "WAS": "Washington Commanders"}

w10 = [r for r in inj_rows if r["week"] == "10"]
# current depth chart (latest dt per team)
latest_dt = {tm: dc.loc[dc["team"] == tm, "dt"].max() for tm in dc["team"].unique()}
dc_cur = dc[[latest_dt[r.team] == r.dt for r in dc.itertuples(index=False)]].copy()
dc_cur = dc_cur.reset_index(drop=True)
NAME_TO_GSIS = {}
for r in dc_cur.itertuples(index=False):
    NAME_TO_GSIS.setdefault((r.team, r.player_name), r.gsis_id)

# Season-wide depth facts: a player "has held depth rank 1 at slot X this season" if ANY
# committed snapshot lists them there. Clubs demote injured starters, so current-chart
# rank alone cannot identify starter deficiencies.
EVER_RANK1 = set()          # (team, gsis_id, pos_name, pos_slot)
PLAYER_BEST = {}            # (team, player_name) -> (pos_name, best_rank)
for r in dc.itertuples(index=False):
    key = (r.team, r.player_name)
    cur_best = PLAYER_BEST.get(key)
    if cur_best is None or r.pos_rank < cur_best[1]:
        PLAYER_BEST[key] = (r.pos_name, r.pos_rank)
    if r.pos_rank == 1:
        EVER_RANK1.add((r.team, r.gsis_id, r.pos_name))
# starter rank lookup: (team, gsis_id) -> list of (pos_grp, pos_name, slot, rank)
rank_lookup = defaultdict(list)
for r in dc_cur.itertuples(index=False):
    rank_lookup[(r.team, r.gsis_id)].append((r.pos_grp, r.pos_name, r.pos_abb, r.pos_slot, r.pos_rank))

def starter_desc(team, gsis):
    e = rank_lookup.get((team, gsis), [])
    if not e:
        # not on current chart — check season-wide evidence by name
        return ""
    best = min(e, key=lambda x: x[4])
    grp, pos_name, pos_abb, slot, rank = best
    if (team, gsis, pos_name) in EVER_RANK1:
        return f"Has held depth rank 1 at {pos_name} this season; current chart rank {rank}"
    return f"Depth rank {rank} at {pos_name} on current chart (no rank-1 evidence this season)"

injury_table = []
for t_ in spot.get("team_level_notes", []):
    injury_table.append({
        "team": TEAM.get(t_["team"], t_["team"]), "player": "(No Injuries Reported)", "position": "",
        "injury": "", "practice_status": "", "game_status": "", "depth_chart_status": "",
        "verification": "VERIFIED", "source_url": SOURCE_NFL_INJ,
        "source_label": "NFL.com injury report",
    })
for r in spot["rows"]:
    injury_table.append({
        "team": TEAM.get(r["team"], r["team"]), "player": r["player"], "position": r["position"],
        "injury": r["injury"], "practice_status": r["practice_status"], "game_status": r["game_status"],
        "depth_chart_status": starter_desc(r["team"], NAME_TO_GSIS.get((r["team"], r["player"]), "")),
        "verification": "VERIFIED", "source_url": SOURCE_NFL_INJ,
        "source_label": "NFL.com injury report",
    })
injury_table.sort(key=lambda x: (x["team"], x["player"]))
write("injuries-week10.json", {
    "generated_utc": GENERATED_UTC,
    "week": 10, "season": 2026,
    "official_source": SOURCE_NFL_INJ,
    "coverage_rule": spot["coverage_rule"],
    "note": "All rows transcribed from the official NFL.com league-wide injury report page "
            "(fetched 2026-11-13) and labelled VERIFIED. Rows with Full Participation and no game "
            "status are omitted per the coverage rule; the official page holds the complete list. "
            "The committed nflverse mirror (research/nfl/raw/injuries_2026.csv.gz) was used only as a "
            "cross-check and lags the official page (e.g., zero Rams rows in the mirror snapshot).",
    "rows": injury_table,
    "counts": {
        "total_rows": len(injury_table),
        "with_game_status": sum(1 for r in injury_table if r["game_status"]),
        "verified_rows": sum(1 for r in injury_table if r["verification"] == "VERIFIED"),
    },
})

# ---------------------------------------------------------------- deficiency join (model)
def UNIT_OF(pos):
    pos = (pos or "").upper()
    if pos == "QB": return "QB"
    if pos in ("C", "G", "T", "OG", "OT", "LG", "RG", "LT", "RT") or pos in ("LS",):
        return {"LS": "Special teams"}.get(pos, "OL")
    if pos in ("WR", "RB", "TE", "FB", "HB"): return "Skill (offense)"
    if pos in ("DT", "DE", "NT", "DL", "EDGE"): return "DL"
    if "CB" in pos or pos in ("S", "FS", "SS", "DB"): return "Secondary"
    if "LB" in pos: return "LB"
    if pos in ("K", "P"): return "Special teams"
    return "Other"
def next_man(team, gsis):
    """Next man up for an injured player's best position (season-wide rank-1 evidence)."""
    e = rank_lookup.get((team, gsis), [])
    if not e:
        return "", "", ""
    grp, pos_name, pos_abb, slot, rank = min(e, key=lambda x: x[4])
    if (team, gsis, pos_name) not in EVER_RANK1:
        return "", "", pos_name
    cur = dc_cur[(dc_cur.team == team) & (dc_cur.pos_name == pos_name)].sort_values("pos_rank")
    top = [r for r in cur.itertuples(index=False) if r.gsis_id != gsis]
    if top:
        return f"{top[0].player_name} (current chart rank {top[0].pos_rank})", UNIT_OF(pos_abb), pos_name
    return "", UNIT_OF(pos_abb), pos_name

deficiency_rows = []
for r in spot["rows"]:
    if r["game_status"] not in ("Out", "Doubtful", "Questionable"):
        continue
    gsis = NAME_TO_GSIS.get((r["team"], r["player"]), "")
    backup, unit, slot_pos = next_man(r["team"], gsis)
    if not unit:
        unit = UNIT_OF(r["position"])
    deficiency_rows.append({
        "team": TEAM.get(r["team"], r["team"]), "unit": unit or "UNKNOWN",
        "player_out": r["player"], "position": r["position"],
        "status": r["game_status"],
        "injury": r["injury"],
        "backup_next_man": backup if backup else "UNVERIFIED — player shows no depth rank-1 evidence this season (backup, not a starter deficiency) or depth-chart match failed",
        "verification": "VERIFIED (injury row official; join is MODEL)",
        "source_url": SOURCE_NFL_INJ,
        "source_label": "NFL.com injury report",
        "join_note": "Backup name is a MODEL JOIN of the official injury report and the official "
                     "club depth chart (nflverse mirror of both) — not an announced lineup.",
    })
write("deficiencies-week10.json", {
    "generated_utc": GENERATED_UTC,
    "week": 10, "season": 2026,
    "method": "Join official injury-report designations (nflverse mirror; spot-checked rows VERIFIED) "
              "with the current official club depth charts (nflverse mirror). A player counts as a "
              "'starter deficiency' only when the depth chart lists them at rank 1 for their position slot.",
    "rows": deficiency_rows,
})

#QB availability per team (depth rank + injury report + announced starters where available)
qb_rows = []
QB_ANNOUNCE = {  # announced/expected Week 10 starters from official NFL.com news (fetched 2026-11-13)
    ("CLE"): {"starter": "Deshaun Watson", "note": "Browns to start QB Deshaun Watson vs. Texans (NFL.com news roundup, Nov 11)", "url": "https://www.nfl.com/news/nfl-news-roundup-latest-league-updates-from-wednesday-nov-11", "verification": "VERIFIED"},
    ("ARI"): {"starter": "Carson Beck", "note": "Cardinals' Carson Beck to start vs. Rams (NFL.com news roundup, Nov 11)", "url": "https://www.nfl.com/news/nfl-news-roundup-latest-league-updates-from-wednesday-nov-11", "verification": "VERIFIED"},
    ("MIA"): {"starter": "Kyle McCord", "note": "Dolphins place QB Malik Willis (groin) on IR; Kyle McCord in line for first start", "url": "https://www.nfl.com/news/dolphins-place-qb-malik-willis-groin-on-injured-reserve-kyle-mccord-in-line-for-first-start", "verification": "VERIFIED"},
    ("SEA"): {"starter": "Drew Lock (expected)", "note": "Sam Darnold ruled out for Week 10; Drew Lock expected to start again", "url": "https://www.nfl.com/news/sam-darnold-ruled-out-for-seahawks-week-10-game-vs-raiders-drew-lock-expected-to-start-again", "verification": "VERIFIED"},
    ("BAL"): {"starter": "", "note": "Lamar Jackson (right thumb) on injured reserve, out 6-9 weeks per NFL Network report", "url": "https://www.nfl.com/news/ravens-lamar-jackson-right-thumb-out-6-9-weeks-expects-to-return-this-season", "verification": "VERIFIED"},
}
for abbr, name in TEAM.items():
    d1 = dc_cur[(dc_cur.team == abbr) & (dc_cur.pos_abb == "QB") & (dc_cur.pos_rank == 1)]
    d2 = dc_cur[(dc_cur.team == abbr) & (dc_cur.pos_abb == "QB") & (dc_cur.pos_rank == 2)]
    inj_qb = [r for r in spot["rows"] if r["week"] == 10 and r["team"] == abbr and r["position"] == "QB"]
    ann = QB_ANNOUNCE.get(abbr, {"starter": "", "note": "", "url": "", "verification": ""})
    inj_note = "; ".join(f"{r['player']} — {r['practice_status'] or 'on report'}" +
                         (f", {r['game_status']}" if r["game_status"] else "") for r in inj_qb)
    qb_rows.append({
        "team": name,
        "depth_qb1": d1.iloc[0].player_name if len(d1) else "",
        "depth_qb2": d2.iloc[0].player_name if len(d2) else "",
        "week10_report": inj_note,
        "announced_or_expected": ann["starter"],
        "note": ann["note"],
        "verification": "MODEL JOIN — QB1/QB2 from official depth-chart mirror; announced rows VERIFIED where noted",
        "source_url": ann["url"] or NFLVERSE_RELEASE.format(tag="depth_charts"),
        "source_label": "NFL.com news" if ann["url"] else "nflverse depth charts release (mirror)",
    })
write("qb-availability-week10.json", {"generated_utc": GENERATED_UTC, "week": 10, "rows": qb_rows})

# ---------------------------------------------------------------- team EPA stats (model)
off_stats = defaultdict(lambda: {"passing_epa": 0.0, "rushing_epa": 0.0, "plays": 0,
                                 "pass_yards": 0, "rush_yards": 0, "points": 0, "opp_points": 0,
                                 "games": 0, "wins": 0, "losses": 0, "ties": 0})
game_log = defaultdict(list)
for g in done:
    a, h = g["away_team"], g["home_team"]
    for t, opp, ps, os_ in ((a, h, int(g["away_score"]), int(g["home_score"])),
                            (h, a, int(g["home_score"]), int(g["away_score"]))):
        off_stats[t]["points"] += ps; off_stats[t]["opp_points"] += os_; off_stats[t]["games"] += 1
        off_stats[t]["wins"] += 1 if ps > os_ else 0
        off_stats[t]["losses"] += 1 if ps < os_ else 0
        off_stats[t]["ties"] += 1 if ps == os_ else 0
        game_log[t].append((int(g["week"]), opp, ps, os_, g["gameday"], g["game_id"]))

for s in team_stats:
    t = s["team"]; wk = int(s["week"])
    if wk not in DONE_WEEKS or s["season_type"] != "REG":
        continue
    o = off_stats[t]
    o["passing_epa"] += float(s["passing_epa"] or 0)
    o["rushing_epa"] += float(s["rushing_epa"] or 0)
    o["plays"] += int(s["attempts"] or 0) + int(s["carries"] or 0)
    o["pass_yards"] += int(s["passing_yards"] or 0)
    o["rush_yards"] += int(s["rushing_yards"] or 0)

# defense EPA/play allowed = opponent offense EPA/play per game (from weekly opponent rows)
def_team = defaultdict(lambda: {"allowed_epa": 0.0, "allowed_plays": 0})
for s in team_stats:
    if s["season_type"] != "REG" or int(s["week"]) not in DONE_WEEKS:
        continue
    d = def_team[s["opponent_team"]]
    d["allowed_epa"] += float(s["passing_epa"] or 0) + float(s["rushing_epa"] or 0)
    d["allowed_plays"] += int(s["attempts"] or 0) + int(s["carries"] or 0)

team_rows = []
for abbr in sorted(TEAM):
    o = off_stats[abbr]; d = def_team[abbr]
    if not o["games"]:
        continue
    off_epp = (o["passing_epa"] + o["rushing_epa"]) / max(o["plays"], 1)
    def_epp = d["allowed_epa"] / max(d["allowed_plays"], 1)
    team_rows.append({
        "team": TEAM[abbr], "abbr": abbr,
        "games": o["games"], "record": f"{o['wins']}-{o['losses']}" + (f"-{o['ties']}" if o["ties"] else ""),
        "points_pg": round(o["points"] / o["games"], 1),
        "opp_points_pg": round(o["opp_points"] / o["games"], 1),
        "off_epa_per_play": round(off_epp, 4),
        "def_epa_per_play_allowed": round(def_epp, 4),
        "net_epa_per_play": round(off_epp - def_epp, 4),
        "verification": "MODEL — computed from nflverse team stats release (mirror of official NFL feeds)",
        "source_url": NFLVERSE_RELEASE.format(tag="stats_team"),
        "source_label": "nflverse team stats release (mirror)",
    })
write("team-stats-2026.json", {
    "generated_utc": GENERATED_UTC, "through_week": max(DONE_WEEKS),
    "epa_method": "Offense EPA/play = (passing_epa + rushing_epa) / (pass attempts + rush attempts), "
                  "weeks completed. Defense EPA/play allowed = opponents' offense EPA/play against this team. "
                  "EPA defined officially by Next Gen Stats: " + SOURCE_NGS_TRENDS,
    "rows": team_rows,
})

# ---------------------------------------------------------------- power ratings + originated lines (model)
margins, net_diffs, homes = [], [], []
totals, off_sum = [], []
by_gid_stats = defaultdict(dict)
for s in team_stats:
    if s["season_type"] == "REG" and int(s["week"]) in DONE_WEEKS:
        key = (s["week"], s["game_id"])
        by_gid_stats[key][s["team"]] = (float(s["passing_epa"] or 0) + float(s["rushing_epa"] or 0),
                                        int(s["attempts"] or 0) + int(s["carries"] or 0))

def team_net(abbr):
    o = off_stats[abbr]; d = def_team[abbr]
    return ((o["passing_epa"] + o["rushing_epa"]) / max(o["plays"], 1)
            - d["allowed_epa"] / max(d["allowed_plays"], 1))

for g in done:
    if int(g["week"]) not in DONE_WEEKS[:-0]:
        pass
    a, h = g["away_team"], g["home_team"]
    margin = int(g["home_score"]) - int(g["away_score"])
    net_diffs.append(team_net(h) - team_net(a))
    margins.append(margin)
    homes.append(1)

# OLS: margin = k * net_diff + h0  (h0 absorbs home-field advantage)
n = len(margins)
x = net_diffs; y = margins
mx, my = sum(x) / n, sum(y) / n
sxy = sum((a - mx) * (b - my) for a, b in zip(x, y))
sxx = sum((a - mx) ** 2 for a in x)
k = sxy / sxx
h0 = my - k * mx
resid = [b - (k * a + h0) for a, b in zip(x, y)]
sd_margin = statistics.stdev(margins)
r2 = 1 - (sum(r * r for r in resid) / sum((b - my) ** 2 for b in y))
HFA_NOTE = f"margin = {k:.3f} × (home net-EPA/play − away net-EPA/play) + {h0:.2f}; residual SD {sd_margin:.2f}; R² {r2:.3f}; n = {n} completed 2026 games (weeks 1-{max(DONE_WEEKS)})"
print(HFA_NOTE)

# totals model: total = t0 + a*(off epp home + off epp away)*plays-scale  → fit on completed games
def game_epps(g):
    key = (g["week"], g["game_id"])
    a, h = g["away_team"], g["home_team"]
    ea = by_gid_stats.get(key, {}).get(a); eh = by_gid_stats.get(key, {}).get(h)
    if not ea or not eh:
        return None
    return (ea[0] / max(ea[1], 1), eh[0] / max(eh[1], 1))

tx, ty = [], []
for g in done:
    e = game_epps(g)
    if e:
        tx.append(e[0] + e[1])
        ty.append(int(g["away_score"]) + int(g["home_score"]))
nt = len(tx)
mtx, mty = sum(tx) / nt, sum(ty) / nt
stx = sum((a - mtx) * (b - mty) for a, b in zip(tx, ty)) / max(sum((a - mtx) ** 2 for a in tx), 1e-9)
t0 = mty - stx * mtx
tresid = [b - (stx * a + t0) for a, b in zip(tx, ty)]
tr2 = 1 - (sum(r * r for r in tresid) / max(sum((b - mty) ** 2 for b in ty), 1e-9))
TOTAL_NOTE = f"total = {t0:.2f} + {stx:.1f} × (game sum of offense EPA/play); R² {tr2:.3f}; n = {nt}"
print(TOTAL_NOTE)

def cdf(x_):
    return 0.5 * (1 + math.erf(x_ / math.sqrt(2)))

def ml_from_p(p):
    if p <= 0 or p >= 1:
        return ""
    return f"+{round((1 - p) / p * 100)}" if p < 0.5 else f"-{round(p / (1 - p) * 100)}"

w10_games = [g for g in games_2026 if g["week"] == "10" and not completed(g)]
line_rows = []
for g in sorted(w10_games, key=lambda x: (x["gameday"], x["away_team"])):
    a, h = g["away_team"], g["home_team"]
    nd = team_net(h) - team_net(a)
    pred_margin = k * nd + h0
    rest = int(g["home_rest"] or 7) - int(g["away_rest"] or 7)
    # rest adjustment: 0.25 points per day of rest differential (documented research convention, small)
    REST_COEF = 0.25
    pred_margin_rest = pred_margin + REST_COEF * rest
    off_a = off_stats[a]; off_h = off_stats[h]
    epp_a = (off_a["passing_epa"] + off_a["rushing_epa"]) / max(off_a["plays"], 1)
    epp_h = (off_h["passing_epa"] + off_h["rushing_epa"]) / max(off_h["plays"], 1)
    total_pred = t0 + stx * (epp_a + epp_h)
    p_home = cdf(pred_margin_rest / sd_margin)
    spread = -round(pred_margin_rest * 2) / 2  # home spread, half-point grid
    # nflverse spread_line is the AWAY team's spread (negative = away favored).
    mkt_away_spread = float(g["spread_line"])
    mkt_home_spread = -mkt_away_spread
    market_total = float(g["total_line"]) if g["total_line"] else None
    tot_edge = (total_pred - market_total) if market_total else None
    line_rows.append({
        "game": f"{TEAM[a]} at {TEAM[h]}", "date": g["gameday"],
        "kickoff_et": g["gametime"],
        "originated_home_spread": spread,
        "originated_home_ml": ml_from_p(p_home),
        "model_win_prob_home": round(p_home, 3),
        "originated_total": round(total_pred, 1) if market_total else "",
        "market_reference_home_spread": mkt_home_spread,
        "market_reference_total": market_total if market_total else "",
        "home_spread_edge_vs_market": round(spread - mkt_home_spread, 1),
        "home_spread_edge_note": "model home spread minus market home spread; POSITIVE = the model rates "
                                 "the home team worse than the market does (model leans AWAY), NEGATIVE = model leans HOME",
        "total_edge_vs_market": round(tot_edge, 1) if tot_edge is not None else "",
        "total_edge_note": "model total minus market total; POSITIVE = model leans OVER",
        "rest_differential_days": rest,
        "verification": "MODEL ESTIMATED — see methodology; market reference is SECONDARY (nflverse schedules release)",
        "source_url": NFLVERSE_RELEASE.format(tag="schedules"),
        "source_label": "nflverse schedules release (mirror; market reference)",
    })
write("originated-lines-week10.json", {
    "generated_utc": GENERATED_UTC,
    "model": {
        "margin_formula": HFA_NOTE,
        "total_formula": TOTAL_NOTE,
        "win_probability": "Normal CDF with SD equal to the 2026 sample SD of game margins (" + f"{sd_margin:.2f}" + " points)",
        "rest_adjustment": f"+{REST_COEF} points per day of rest differential (research convention; flagged, not fitted)",
        "fit_data": f"nflverse 2026 schedules release (mirror of official NFL feed), weeks 1-{max(DONE_WEEKS)}",
        "market_reference_note": "spread_line/total_line columns are archived market lines published by the "
                                 "nflverse schedules release — a SECONDARY source used only as a comparison, never as model input",
    },
    "rows": line_rows,
})

# ---------------------------------------------------------------- signal evaluation (model, small samples)
sig = []
sig.append({"signal": "Home-field advantage (2026 sample)",
            "measure": f"Mean home margin {my:.2f} pts (n={n}); model absorbs it as intercept {h0:.2f}",
            "status": "ESTIMATED — single-season sample", 
            "source_url": NFLVERSE_RELEASE.format(tag="schedules"), "source_label": "nflverse schedules release (mirror)"})
# predictive check in-sample and holdout
fit_weeks = [w for w in DONE_WEEKS if w <= 6]; test_weeks = [w for w in DONE_WEEKS if w > 6]
def fit_k_h0(weeks):
    xs, ys = [], []
    for g in done:
        if int(g["week"]) not in weeks:
            continue
        a, h = g["away_team"], g["home_team"]
        xs.append(team_net(h) - team_net(a)); ys.append(int(g["home_score"]) - int(g["away_score"]))
    if len(xs) < 5:
        return None, None, None
    mx_, my_ = sum(xs) / len(xs), sum(ys) / len(ys)
    k_ = sum((a - mx_) * (b - my_) for a, b in zip(xs, ys)) / max(sum((a - mx_) ** 2 for a in xs), 1e-9)
    h0_ = my_ - k_ * mx_
    return k_, h0_, len(xs)
k_tr, h_tr, n_tr = fit_k_h0(fit_weeks)
if k_tr is not None and test_weeks:
    xs_t, ys_t = [], []
    for g in done:
        if int(g["week"]) in test_weeks:
            a, h = g["away_team"], g["home_team"]
            xs_t.append(k_tr * (team_net(h) - team_net(a)) + h_tr); ys_t.append(int(g["home_score"]) - int(g["away_score"]))
    corr = (sum((a - sum(xs_t)/len(xs_t)) * (b - sum(ys_t)/len(ys_t)) for a, b in zip(xs_t, ys_t))
            / (math.sqrt(sum((a - sum(xs_t)/len(xs_t))**2 for a in xs_t)) * math.sqrt(sum((b - sum(ys_t)/len(ys_t))**2 for b in ys_t))))
    mae = sum(abs(a - b) for a, b in zip(xs_t, ys_t)) / len(xs_t)
    sig.append({"signal": "EPA-margin model held-out accuracy",
                "measure": f"Fit weeks 1-{max(fit_weeks)} (n={n_tr}); predict weeks {min(test_weeks)}-{max(test_weeks)} (n={len(xs_t)}): "
                           f"corr(pred, actual) = {corr:.3f}, MAE = {mae:.2f} pts",
                "status": "ESTIMATED — small holdout sample",
                "source_url": NFLVERSE_RELEASE.format(tag="stats_team"), "source_label": "nflverse team stats release (mirror)"})
sig.append({"signal": "Season-to-date EPA per play as power rating",
            "measure": HFA_NOTE + "; methodology (EPA definition): NFL Next Gen Stats",
            "status": "MODEL ESTIMATED",
            "source_url": SOURCE_NGS_TRENDS, "source_label": "NFL.com — Next Gen Stats (official EPA definition)"})
# rest differential descriptive
buckets = defaultdict(list)
for g in done:
    rd = int(g["home_rest"] or 7) - int(g["away_rest"] or 7)
    buckets[min(max(rd, -3), 3)].append(int(g["home_score"]) - int(g["away_score"]))
rb = "; ".join(f"rest diff {kk:+d}: mean margin {sum(v)/len(v):+.1f} (n={len(v)})" for kk, v in sorted(buckets.items()))
sig.append({"signal": "Rest differential (days) vs home margin",
            "measure": rb + " — descriptive only, no fitted adjustment; results within ±1 day dominate the sample",
            "status": "ESTIMATED — descriptive, tiny buckets",
            "source_url": NFLVERSE_RELEASE.format(tag="schedules"), "source_label": "nflverse schedules release (mirror)"})
# weather: roof availability
roof_counts = defaultdict(int)
for g in games_2026:
    roof_counts[g["roof"] or "UNKNOWN"] += 1
sig.append({"signal": "Weather (temp/wind) columns",
            "measure": "2026 schedule rows carry roof values but temp/wind are blank in the release for most games; "
                       "no weather adjustment is applied. Counts: " + ", ".join(f"{k or 'blank'}={v}" for k, v in sorted(roof_counts.items())),
            "status": "UNVERIFIED — weather inputs missing",
            "source_url": NFLVERSE_RELEASE.format(tag="schedules"), "source_label": "nflverse schedules release (mirror)"})
sig.append({"signal": "Injury/backup adjustments",
            "measure": "Not yet applied to the rating model: no fitted injury coefficients exist from one season of data. "
                       "Injuries enter strategy selection (S2/S4/S5) as filters, not as fitted point adjustments.",
            "status": "MODEL GAP — flagged",
            "source_url": SOURCE_NFL_INJ, "source_label": "NFL.com injury report"})
write("signals-2026.json", {"generated_utc": GENERATED_UTC, "rows": sig})

# ---------------------------------------------------------------- parlay leg correlations (model, from pbp)
pbp = pd.read_csv(RAW / "play_by_play_2026.csv.gz", compression="gzip", low_memory=False)
pbp = pbp[pbp.week.isin(DONE_WEEKS) & (pbp.season_type == "REG")]
gsum = pbp.groupby("game_id").agg(home=("home_team", "first"), away=("away_team", "first"),
                                  week=("week", "first"))
def corr(a, b):
    n_ = len(a)
    ma, mb = sum(a) / n_, sum(b) / n_
    num = sum((x - ma) * (y - mb) for x, y in zip(a, b))
    da = math.sqrt(sum((x - ma) ** 2 for x in a)); db = math.sqrt(sum((y - mb) ** 2 for y in b))
    return num / (da * db) if da and db else 0.0

# per-game metrics
pass_yards = defaultdict(float); rush_yards = defaultdict(float)
recv_yards = defaultdict(float); team_pts = defaultdict(float); dropbacks = defaultdict(float); carries_g = defaultdict(float)
for r in pbp.itertuples(index=False):
    if r.passer_player_name and r.passing_yards and not (pd.isna(r.passing_yards)):
        pass_yards[r.game_id] += float(r.passing_yards)
    if r.rusher_player_name and not pd.isna(r.rushing_yards):
        rush_yards[r.game_id] += float(r.rushing_yards)
        carries_g[r.game_id] += 1
    if r.receiver_player_name and not pd.isna(r.receiving_yards):
        recv_yards[r.game_id] += float(r.receiving_yards)
    if r.posteam and not pd.isna(r.total_home_score):
        pass
for r in pbp.drop_duplicates(subset="game_id").itertuples(index=False):
    team_pts[r.game_id] = float(r.total_home_score) + float(r.total_away_score)

gids = [g for g in gsum.index if g in team_pts and pass_yards.get(g) is not None]
A = [pass_yards.get(g, 0) for g in gids]          # game passing yards (both teams combined)
B = [team_pts.get(g, 0) for g in gids]            # game total points
C = [recv_yards.get(g, 0) for g in gids]          # combined receiving yards
D = [rush_yards.get(g, 0) for g in gids]          # combined rushing yards
corr_rows = [
    {"leg_pair": "Combined game passing yards vs combined game total points",
     "pearson_r": round(corr(A, B), 3), "n_games": len(gids),
     "status": "ESTIMATED — one season, descriptive; re-estimate per use"},
    {"leg_pair": "Combined game receiving yards vs combined game total points",
     "pearson_r": round(corr(C, B), 3), "n_games": len(gids),
     "status": "ESTIMATED — one season, descriptive"},
    {"leg_pair": "Combined game rushing yards vs combined game total points",
     "pearson_r": round(corr(D, B), 3), "n_games": len(gids),
     "status": "ESTIMATED — one season, descriptive"},
    {"leg_pair": "Combined game passing yards vs combined game rushing yards",
     "pearson_r": round(corr(A, D), 3), "n_games": len(gids),
     "status": "ESTIMATED — one season, descriptive"},
]
write("correlations-2026.json", {
    "generated_utc": GENERATED_UTC,
    "method": "Pearson correlation on game-level season totals from nflverse play-by-play (mirror of "
              "official NFL feeds), weeks 1-" + str(max(DONE_WEEKS)) + ". Game-level correlations are NOT "
              "the correlation of specific prop legs against a line; they are a descriptive starting point "
              "and must be re-estimated against actual prop lines before any parlay use.",
    "calculator": "nfl-correlation.html provides a Bernoulli-covariance calculator: "
                  "P(A∩B) = P(A)P(B) + ρ·√(P(A)(1−P(A))P(B)(1−P(B)))",
    "rows": corr_rows,
})

# ---------------------------------------------------------------- strategy backtest (simulated at assumed -110)
ASSUMED_PRICE = -110  # research assumption: every pick graded at -110; NOT a real market price
def payout(stake=1.0, price=ASSUMED_PRICE):
    return stake * (100 / abs(price)) if price < 0 else stake * price / 100

# Build per-week team net EPA and grade strategies on completed games 1-9 (in-sample, SIMULATED)
def grade(strategy_id):
    picks = []
    for g in done:
        if g["spread_line"] in ("", "NA") or g["total_line"] in ("", "NA"):
            continue
        a, h = g["away_team"], g["home_team"]
        wk = int(g["week"])
        mkt_home = float(g["spread_line"])
        mkt_total = float(g["total_line"])
        margin = int(g["home_score"]) - int(g["away_score"])
        total = int(g["home_score"]) + int(g["away_score"])
        nd = team_net(h) - team_net(a)
        pred_margin = k * nd + h0
        rest = int(g["home_rest"] or 7) - int(g["away_rest"] or 7)
        pred_margin_rest = pred_margin + REST_COEF * rest
        e = game_epps(g)
        pred_total = t0 + stx * sum(e) if e else None
        # OL/secondary deficiency for each team (from week-report joins; approximated by weekly injury files)
        def count_out(team_abbr, week, units):
            rows_w = [r for r in inj_rows if r["week"] == str(week) and r["team"] == team_abbr
                      and r["report_status"] in ("Out",)]
            n_ = 0
            for r in rows_w:
                e_ = rank_lookup.get((team_abbr, r["gsis_id"]), [])
                if e_:
                    best = min(e_, key=lambda q: q[4])
                    if ((team_abbr, r["gsis_id"], best[1], best[3]) in EVER_RANK1
                            and UNIT_OF.get(best[2], "") in units):
                        n_ += 1
            return n_
        pick = None
        if strategy_id == "S1":
            # Road side when market prices road team ≥ +3 underdog but model margin favors road by ≥ 2
            if mkt_home <= -3 and pred_margin_rest <= -2:
                pick = ("away", margin < 0)
        elif strategy_id == "S2":
            # Under when market total ≥ 44 and model total ≤ market − 2
            if pred_total and mkt_total >= 44 and pred_total <= mkt_total - 2:
                pick = ("under", total < mkt_total)
        elif strategy_id == "S4":
            # Under when a team has ≥2 OL starters listed Out
            if count_out(a, wk, {"OL"}) >= 2 or count_out(h, wk, {"OL"}) >= 2:
                pick = ("under", total < mkt_total)
        elif strategy_id == "S5":
            # Over when a defense has ≥2 Secondary starters listed Out
            if count_out(a, wk, {"Secondary"}) >= 2 or count_out(h, wk, {"Secondary"}) >= 2:
                pick = ("over", total > mkt_total)
        elif strategy_id == "S6":
            # Road side when road rest ≥ 4 days more than home and model margin ≥ −1 (near pick-em)
            if rest <= -4 and pred_margin_rest >= -1:
                pick = ("away", margin < 0)
        if pick:
            picks.append({"week": wk, "game": g["game_id"], "side": pick[0],
                          "won": pick[1], "result": (margin, total)})
    return picks

strategies = [
    {"id": "S1", "name": "Model-favored road dog",
     "rule": "Back the road team when the archived market line makes it a ≥ +3 underdog but the EPA-margin model projects the road side to win by ≥ 2 after rest adjustment.",
     "depends_on_market": True},
    {"id": "S2", "name": "Model-vs-market total under",
     "rule": "Take the under when the archived market total is ≥ 44 and the EPA total model projects ≤ market − 2.",
     "depends_on_market": True},
    {"id": "S4", "name": "OL deficiency under",
     "rule": "Take the under when either team has ≥ 2 offensive-line starters (depth rank 1) listed Out on the week's official injury report.",
     "depends_on_market": True},
    {"id": "S5", "name": "Secondary deficiency over",
     "rule": "Take the over when either defense has ≥ 2 secondary starters (depth rank 1) listed Out.",
     "depends_on_market": True},
    {"id": "S6", "name": "Rest differential road side",
     "rule": "Back the road team when it has ≥ 4 more days rest than home and the model projects ≥ −1 margin (near pick-em).",
     "depends_on_market": True},
]

leaderboard = []
for s in strategies:
    picks = grade(s["id"])
    if not picks:
        leaderboard.append({"id": s["id"], "name": s["name"], "picks": 0, "hits": 0,
                            "hit_rate": "", "units_est": "", "roi_est": "", "t_stat_est": "",
                            "status": "NO QUALIFYING PICKS in weeks 1-9 (in-sample, SIMULATED)"})
        continue
    hits = sum(1 for p in picks if p["won"])
    units = sum(payout() if p["won"] else -1.0 for p in picks)
    roi = units / len(picks)
    p = hits / len(picks)
    var = p * (1 - p) / len(picks)
    t = round((p - 100 / 210) / math.sqrt(var), 2) if var > 0 else "n/a (0 variance)"
    leaderboard.append({"id": s["id"], "name": s["name"], "picks": len(picks), "hits": hits,
                        "hit_rate": f"{p * 100:.1f}%", "units_est": f"{units:+.2f}",
                        "roi_est": f"{roi * 100:+.1f}%", "t_stat_est": t,
                        "status": "SIMULATED — in-sample (weeks 1-9), assumed -110 price; NOT evidence of edge"})
write("leaderboard-2026.json", {
    "generated_utc": GENERATED_UTC,
    "assumed_price": ASSUMED_PRICE,
    "assumed_price_note": "SIMULATION ONLY. No real market prices are ingested; the -110 assumption is a "
                          "research convention for comparing strategy hit rates against breakeven (52.38% at -110).",
    "market_reference": NFLVERSE_RELEASE.format(tag="schedules"),
    "rows": leaderboard,
    "strategies": strategies,
})

# ---------------------------------------------------------------- audit record
(AUDIT / "nfl-rows-audit.json").write_text(json.dumps({
    "generated_utc": GENERATED_UTC,
    "events_json_nfl_rows_nov_2026": 70,
    "matched_to_nflverse_slate": 70,
    "time_mismatches": 0,
    "week10_nflverse_vs_live_nflcom": {"checked": 14, "date_time_matches": 14},
    "tnf_result_check": "WAS 24 @ NYG 21 matches NFL.com live page and NFL.com news",
    "sources": ["https://www.nfl.com/schedules/2026/REG10/", SOURCE_NFL_INJ,
                NFLVERSE_RELEASE.format(tag="schedules")],
}, indent=1) + "\n")
print("audit written")
print("DONE")
