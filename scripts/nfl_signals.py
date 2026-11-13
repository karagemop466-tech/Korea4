#!/usr/bin/env python3
"""NFL Lines engine.

Turns captured official sources into:

* ``data/nfl/schedule_2026.json``  - the official 2026 NFL schedule parsed from the
  already-snapshotted official nfl.com by-week pages, with schedule-derived features
  (rest days, short week, games in 11, byes, kickoff in ET/PT).
* ``data/nfl/deficiency.json``    - injury / depth-chart availability analysis: which
  starters are unavailable and which string replaces them (offense and defense).
* ``data/nfl/lines.json``          - originated fair lines (spread, total, win
  probability) for the games in the captured weeks, with every input traced to an
  official source.
* ``data/nfl/correlation.json``    - measured correlations: season-to-season
  persistence (skill vs luck) and the signal-correlation matrix used to gate parlays.
* ``data/nfl/gate_results.json``   - validation-gate outcome per strategy.
* ``data/nfl/leaderboard-register.json``    - leaderboard rows, reward tiers and eligibility.

Rules honoured everywhere:
* No value is invented. A value that no official source confirms is blank and flagged
  UNVERIFIED.
* Model outputs are labelled MODEL and never presented as official or as market prices.
* Every emitted row carries the official URL of the source it was read from.
"""
from __future__ import annotations

import csv
import gzip
import json
import math
import re
from datetime import datetime, timedelta, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data" / "nfl"
RAW = ROOT / "research" / "official" / "raw"
OUT = DATA

# ---------------------------------------------------------------------------
# Model parameters. Every value here is an assumption of this program, not an
# official NFL value, and is reported as MODEL wherever it is used.
# ---------------------------------------------------------------------------
PYTHAGOREAN_EXPONENT = 2.37      # standard NFL Pythagorean exponent
MARGIN_SIGMA = 12.0               # assumed game-margin standard deviation (points)
HOME_EDGE_POINTS = 1.8            # added directly to the home margin (points)
REST_POINT_PER_DAY = 0.25         # points per extra rest day, capped
SHORT_WEEK_PENALTY = 1.0          # points lost on a 3-day week
AVAILABILITY_WEIGHTS = {          # points of expected margin per position group
    "QB": 4.0, "OL": 1.5, "WR": 0.8, "TE": 0.6, "RB": 0.7,
    "CB": 0.7, "S": 0.7, "DB": 0.7, "DL": 0.6, "LB": 0.6, "EDGE": 0.6, "K": 0.3, "P": 0.3,
}
DEPTH_MULTIPLIER = {2: 1.0, 3: 1.5, 4: 2.0}   # deeper replacement -> larger drop
GATE_MIN_SAMPLES = 100            # minimum settled bets before a strategy may score
GATE_MAX_LEG_CORRELATION = 0.30   # |rho| allowed between parlay legs
GATE_MAX_PARLAY_LEGS = 4
GATE_MAX_KELLY = 0.25

PRACTICE_LABEL = {
    "F": "Full Participation in Practice",
    "L": "Limited Participation in Practice",
    "D": "Did Not Participate In Practice",
    "": "",
}
POSITION_GROUP = {
    "QB": "QB", "T": "OL", "G": "OL", "C": "OL",
    "WR": "WR", "TE": "TE", "RB": "RB", "FB": "RB",
    "CB": "CB", "S": "S", "DB": "CB", "NT": "DL", "DT": "DL", "DE": "EDGE",
    "LB": "LB", "ILB": "LB", "MLB": "LB", "WILL": "LB", "WLB": "LB", "SAM": "LB",
    "RUSH": "EDGE", "EDGE": "EDGE", "NB": "S", "LS": "OL", "K": "K", "P": "P",
}


# ---------------------------------------------------------------------------
# Small statistics helpers (no third-party dependency in this repository).
# ---------------------------------------------------------------------------
def normal_cdf(x: float) -> float:
    return 0.5 * (1.0 + math.erf(x / math.sqrt(2.0)))


def normal_inv(p: float) -> float:
    """Inverse standard-normal CDF (Acklam's rational approximation)."""
    if p <= 0.0 or p >= 1.0:
        raise ValueError("p must be in (0,1)")
    a = [-3.969683028665376e+01, 2.209460984245205e+02, -2.759285104469687e+02,
         1.383577518672690e+02, -3.066479806614716e+01, 2.506628277459239e+00]
    b = [-5.447609879822406e+01, 1.615858368580409e+02, -1.556989798598866e+02,
         6.680131188771972e+01, -1.328068155288572e+01]
    c = [-7.784894002430293e-03, -3.223964580411365e-01, -2.400758277161838e+00,
         -2.549732539343734e+00, 4.374664141464968e+00, 2.938163982698783e+00]
    d = [7.784695709041462e-03, 3.224671290700398e-01, 2.445134137142996e+00,
         3.754408661907416e+00]
    plow, phigh = 0.02425, 1 - 0.02425
    if p < plow:
        q = math.sqrt(-2 * math.log(p))
        return (((((c[0]*q+c[1])*q+c[2])*q+c[3])*q+c[4])*q+c[5]) / ((((d[0]*q+d[1])*q+d[2])*q+d[3])*q+1)
    if p > phigh:
        q = math.sqrt(-2 * math.log(1 - p))
        return -(((((c[0]*q+c[1])*q+c[2])*q+c[3])*q+c[4])*q+c[5]) / ((((d[0]*q+d[1])*q+d[2])*q+d[3])*q+1)
    q = p - 0.5
    r = q * q
    return (((((a[0]*r+a[1])*r+a[2])*r+a[3])*r+a[4])*r+a[5])*q / (((((b[0]*r+b[1])*r+b[2])*r+b[3])*r+b[4])*r+1)


def pearson(xs, ys):
    n = len(xs)
    if n < 3 or n != len(ys):
        return None
    mx, my = sum(xs) / n, sum(ys) / n
    sxy = sum((x - mx) * (y - my) for x, y in zip(xs, ys))
    sxx = sum((x - mx) ** 2 for x in xs)
    syy = sum((y - my) ** 2 for y in ys)
    if sxx <= 0 or syy <= 0:
        return None
    r = sxy / math.sqrt(sxx * syy)
    slope = sxy / sxx
    intercept = my - slope * mx
    r2 = r * r
    return {"r": round(r, 4), "r2": round(r2, 4), "slope": round(slope, 4),
            "intercept": round(intercept, 4), "n": n}


def ols(xs, ys):
    """Least squares fit of ys on xs with a standard error of the slope."""
    n = len(xs)
    if n < 4 or n != len(ys):
        return None
    mx, my = sum(xs) / n, sum(ys) / n
    sxx = sum((x - mx) ** 2 for x in xs)
    if sxx <= 0:
        return None
    slope = sum((x - mx) * (y - my) for x, y in zip(xs, ys)) / sxx
    intercept = my - slope * mx
    resid = [y - (intercept + slope * x) for x, y in zip(xs, ys)]
    sse = sum(e * e for e in resid)
    sst = sum((y - my) ** 2 for y in ys)
    se = math.sqrt(sse / (n - 2) / sxx) if n > 2 and sxx > 0 else None
    t = slope / se if se else None
    return {"slope": round(slope, 4), "intercept": round(intercept, 4), "n": n,
            "stderr": round(se, 4) if se else None,
            "t": round(t, 4) if t is not None else None,
            "r2": round(1 - sse / sst, 4) if sst > 0 else None}


def logistic(x: float) -> float:
    return 1.0 / (1.0 + math.exp(-x))


def logit(p: float) -> float:
    p = min(max(p, 1e-6), 1 - 1e-6)
    return math.log(p / (1 - p))


def read_csv(path: Path):
    with path.open(newline="", encoding="utf-8") as fh:
        return list(csv.DictReader(fh))


# ---------------------------------------------------------------------------
# Official 2026 schedule, parsed from the already-captured official nfl.com
# by-week snapshots (research/official/raw/nfl_2026_week_*.gz).
# ---------------------------------------------------------------------------
CARD_RE = re.compile(
    r'linkModule&quot;:&quot;Game Card&quot;,&quot;linkName&quot;:&quot;([^&]*)&quot;.*?href="/games/([a-z0-9\-]+)"',
    re.S)
DT_RE = re.compile(r'dateTime="([^"]+)"')
SLUG_RE = re.compile(r"([a-z0-9\-]+)-2026-(reg|post|preseason)-(\d+)")


def us_dst_bounds(year: int):
    """US daylight-saving start and end dates (2nd Sunday March, 1st Sunday November)."""
    def nth_sunday(year, month, n):
        d = datetime(year, month, 1)
        offset = (6 - d.weekday()) % 7
        return d + timedelta(days=offset + 7 * (n - 1))
    return nth_sunday(year, 3, 2), nth_sunday(year, 11, 1)


def to_local(utc_dt: datetime, year: int):
    """Return (ET offset hours, PT offset hours) for an aware UTC datetime."""
    start, end = us_dst_bounds(year)
    naive = utc_dt.replace(tzinfo=None)
    dst = (start <= naive < end)
    return (-4 if dst else -5), (-7 if dst else -8)


def manifest_index():
    manifest = json.loads((ROOT / "research" / "official" / "manifest.json").read_text())
    return {f["key"]: f for f in manifest["files"]}


def parse_schedule():
    """Parse the official 2026 by-week snapshots into game rows.

    Two card formats appear in the official nfl.com by-week HTML:
      completed: "Panthers 19, Packers 27, FINAL, Thursday, October 29th"
      upcoming : "Jaguars at Ravens, Thursday, November 5th, 8:15 PM, PRIME"
    Completed cards carry the official final score; upcoming cards carry the
    official kickoff time and network. Nothing is inferred: a field that the
    official card does not state stays empty.
    """
    index = manifest_index()
    rows = []
    for week in range(1, 19):
        key = f"nfl_2026_week_{week:02d}"
        path = RAW / f"{key}.gz"
        if not path.exists():
            continue
        meta = index.get(key, {})
        html = gzip.open(path, "rb").read().decode("utf-8", "replace")
        for match in CARD_RE.finditer(html):
            link_name, slug = match.group(1), match.group(2)
            parts = [p.strip() for p in link_name.split(", ")]
            if len(parts) < 3 and " at " not in parts[0] and " vs " not in parts[0]:
                continue
            tail = html[match.end(): match.end() + 9000]
            dt = DT_RE.search(tail)
            utc = None
            if dt:
                try:
                    utc = datetime.strptime(dt.group(1)[:19], "%Y-%m-%dT%H:%M:%S").replace(tzinfo=timezone.utc)
                except ValueError:
                    utc = None
            row = {
                "week": week, "slug": slug,
                "away_team": "", "home_team": "",
                "date": "", "kickoff_et": "", "kickoff_pt": "", "kickoff_utc": "",
                "network": "", "status": "", "away_score": "", "home_score": "",
                "source_url": f"https://www.nfl.com/games/{slug}",
                "snapshot_source_url": meta.get("url", f"https://www.nfl.com/schedules/2026/by-week/week-{week}"),
                "snapshot_sha256": meta.get("sha256", ""),
                "snapshot_retrieved_utc": meta.get("retrieved_utc", ""),
                "verification": "VERIFIED - official nfl.com by-week snapshot",
            }
            if len(parts) > 2 and parts[2] == "FINAL" and len(parts) >= 5:
                row["away_team"] = " ".join(parts[0].split()[:-1])
                row["away_score"] = parts[0].split()[-1]
                row["home_team"] = " ".join(parts[1].split()[:-1])
                row["home_score"] = parts[1].split()[-1]
                row["date"] = parse_card_date(parts[3] + ", " + parts[4])
                row["status"] = "FINAL"
            else:
                matchup = parts[0]
                if " at " in matchup:
                    away, home = [s.strip() for s in matchup.split(" at ", 1)]
                elif " vs " in matchup:
                    away, home = [s.strip() for s in matchup.split(" vs ", 1)]
                else:
                    continue
                row["away_team"], row["home_team"] = away, home
                if len(parts) >= 5:
                    row["date"] = parse_card_date(parts[1] + ", " + parts[2])
                    row["network"] = parts[4]
                row["status"] = "SCHEDULED"
            if utc is not None:
                et_off, pt_off = to_local(utc, 2026)
                et = utc + timedelta(hours=et_off)
                row["kickoff_utc"] = utc.strftime("%Y-%m-%dT%H:%M:%SZ")
                row["kickoff_et"] = et.strftime("%Y-%m-%d %H:%M ET")
                row["kickoff_pt"] = (utc + timedelta(hours=pt_off)).strftime("%Y-%m-%d %H:%M PT")
                if not row["date"]:
                    row["date"] = et.strftime("%Y-%m-%d")
            rows.append(row)
    rows.sort(key=lambda r: (r["week"], r["kickoff_utc"] or r["date"]))
    return rows


MONTHS = {m: i + 1 for i, m in enumerate(
    ["January", "February", "March", "April", "May", "June", "July", "August",
     "September", "October", "November", "December"])}


def parse_card_date(text):
    """'Thursday, October 29th' -> '2026-10-29' (2026 season)."""
    text = text.strip().rstrip(",")
    if "," in text:
        _, rest = text.split(",", 1)
    else:
        rest = text
    parts = rest.strip().split()
    if len(parts) < 2:
        return ""
    month = MONTHS.get(parts[0])
    day = re.sub(r"[^0-9]", "", parts[1])
    if not month or not day:
        return ""
    return f"2026-{month:02d}-{int(day):02d}"


def schedule_features(rows):
    """Rest days, short weeks, games in 11 and byes, computed from the official schedule."""
    by_team = {}
    for row in rows:
        for team in (row["away_team"], row["home_team"]):
            by_team.setdefault(team, []).append(row)
    for team, games in by_team.items():
        games.sort(key=lambda r: r["kickoff_utc"])
        played_weeks = {int(g["week"]) for g in games}
        byes = [w for w in range(1, 19) if w not in played_weeks]
        for i, row in enumerate(games):
            if not row["date"]:
                # Official schedule publishes no date for this row (Week 18 is TBD).
                row["_rest_" + team] = None
                row["_g11_" + team] = None
                continue
            date = datetime.strptime(row["date"], "%Y-%m-%d").date()
            prev = None
            for j in range(i - 1, -1, -1):
                if games[j]["date"] and games[j]["date"] != row["date"]:
                    prev = datetime.strptime(games[j]["date"], "%Y-%m-%d").date()
                    break
            row["_rest_" + team] = (date - prev).days if prev else None
            # Only count games already played by this date, including today;
            # looking ahead would leak future schedule into a backtest feature.
            row["_g11_" + team] = sum(
                1 for g in games
                if g["date"] and 0 <= (date - datetime.strptime(g["date"], "%Y-%m-%d").date()).days <= 10)
            row["_bye_" + team] = ",".join(str(w) for w in byes)
    out = []
    for row in rows:
        away, home = row["away_team"], row["home_team"]
        out.append({
            "week": row["week"], "slug": row["slug"], "away_team": away, "home_team": home,
            "date": row["date"], "kickoff_et": row["kickoff_et"], "kickoff_pt": row["kickoff_pt"],
            "network": row["network"], "status": row["status"], "kickoff_utc": row["kickoff_utc"],
            "away_score": row["away_score"], "home_score": row["home_score"],
            "rest_days_away": row.get("_rest_" + away), "rest_days_home": row.get("_rest_" + home),
            "rest_diff_home_minus_away": (row.get("_rest_" + home) or 0) - (row.get("_rest_" + away) or 0),
            "games_in_11_away": row.get("_g11_" + away), "games_in_11_home": row.get("_g11_" + home),
            "bye_week_away": row.get("_bye_" + away), "bye_week_home": row.get("_bye_" + home),
            "source_url": row["source_url"], "snapshot_source_url": row["snapshot_source_url"],
            "snapshot_sha256": row["snapshot_sha256"], "snapshot_retrieved_utc": row["snapshot_retrieved_utc"],
            "verification": row["verification"],
        })
    return out


# ---------------------------------------------------------------------------
# Availability: official injury designations joined to official team depth charts.
# ---------------------------------------------------------------------------
def depth_index(depth_rows):
    index = {}
    for row in depth_rows:
        key = (row["team"], row["player"])
        index[key] = {"unit": row["unit"], "position": row["position"], "tier": int(row["tier"]),
                      "source_url": row["source_url"], "depth_updated": row["depth_updated"]}
    teams = {}
    for row in depth_rows:
        teams.setdefault(row["team"], []).append(row)
    return index, teams


def team_depth_captures():
    return {r["team"]: r for r in read_csv(DATA / "depth.csv")}


def deficiency_rows(injury_rows, depth_rows, short_to_full):
    index, _ = depth_index(depth_rows)
    rows = []
    for inj in injury_rows:
        team = inj["team"]
        full_team = short_to_full.get(team, team)
        player = inj["player"]
        if player == "No Injuries Reported":
            continue
        status = inj["game_status"]
        if not status:
            continue
        entry = index.get((full_team, player))
        group = POSITION_GROUP.get(inj["position"], "OTHER")
        base = AVAILABILITY_WEIGHTS.get(group)
        row = {
            "week": int(inj["week"]), "away_team": inj["away_team"], "home_team": inj["home_team"],
            "team": team, "team_full_name": full_team, "player": player, "position": inj["position"],
            "position_group": group, "injury": inj["injury"],
            "practice_status": PRACTICE_LABEL.get(inj["practice_code"], ""),
            "game_status": status,
            "depth_tier": entry["tier"] if entry else "",
            "depth_unit": entry["unit"] if entry else "",
            "depth_position": entry["position"] if entry else "",
            "is_starter": (entry["tier"] == 1) if entry else "",
            "replacement_tier": (entry["tier"] + 1) if entry else "",
            "replacement_player": "", "expected_margin_penalty": "",
            "injury_source_url": inj["source_url"], "captured_utc": inj["captured_utc"],
        }
        if entry:
            # Next name down the same official position row is the listed replacement.
            same_pos = [r for r in depth_rows if r["team"] == full_team and r["unit"] == entry["unit"]
                        and r["position"] == entry["position"] and int(r["tier"]) == entry["tier"] + 1]
            if same_pos:
                row["replacement_player"] = same_pos[0]["player"]
            if base is not None and entry["tier"] == 1:
                mult = DEPTH_MULTIPLIER.get(entry["tier"] + 1, 2.0)
                row["expected_margin_penalty"] = round(base * mult, 2)
                row["source_url"] = entry["source_url"]
            else:
                row["source_url"] = inj["source_url"]
        else:
            row["source_url"] = inj["source_url"]
            row["depth_status"] = "UNVERIFIED — official depth chart for this team not captured"
        rows.append(row)
    return rows


def team_penalties(def_rows):
    penalties = {}
    for row in def_rows:
        if row["expected_margin_penalty"] == "":
            continue
        penalties.setdefault(row["team"], 0.0)
        penalties[row["team"]] += float(row["expected_margin_penalty"])
    return {k: round(v, 2) for k, v in penalties.items()}


# ---------------------------------------------------------------------------
# Ratings and originated lines.
# ---------------------------------------------------------------------------
def ratings(standings_rows, season=2026):
    rows = [r for r in standings_rows if int(r["season"]) == season]
    team_games = sum(int(r["w"]) + int(r["l"]) + int(r["t"]) for r in rows)
    total_pf = sum(int(r["pf"]) for r in rows)
    league_pf_per_game = total_pf / team_games if team_games else None
    league_pa_per_game = (sum(int(r["pa"]) for r in rows) / team_games) if team_games else None
    out = {}
    for r in rows:
        games = int(r["w"]) + int(r["l"]) + int(r["t"])
        pf, pa = int(r["pf"]), int(r["pa"])
        p_base = (pf ** PYTHAGOREAN_EXPONENT) / ((pf ** PYTHAGOREAN_EXPONENT) + (pa ** PYTHAGOREAN_EXPONENT))
        out[r["team"]] = {
            "team": r["team"], "slug": r["slug"], "games": games, "pf": pf, "pa": pa,
            "pythagorean_win_pct": round(p_base, 4),
            "points_for_per_game": round(pf / games, 2), "points_against_per_game": round(pa / games, 2),
            "net_points_per_game": round((pf - pa) / games, 2),
            "source_url": r["source_url"], "captured_utc": r["captured_utc"],
        }
    return out, league_pf_per_game, league_pa_per_game


def home_field_delta(standings_rows):
    """League home-vs-road win-rate gap from the official standings panel."""
    home_w = home_l = road_w = road_l = 0
    for r in standings_rows:
        home_w += int(r["home_w"]); home_l += int(r["home_l"])
        road_w += int(r["road_w"]); road_l += int(r["road_l"])
    hwr = home_w / (home_w + home_l) if (home_w + home_l) else None
    rwr = road_w / (road_w + road_l) if (road_w + road_l) else None
    if hwr is None or rwr is None:
        return None
    return {
        "home_win_rate": round(hwr, 4), "road_win_rate": round(rwr, 4),
        "logit_gap": round(logit(hwr) - logit(rwr), 4),
        "home_games": home_w + home_l, "road_games": road_w + road_l,
        "source_url": "https://www.nfl.com/standings/league/2026/REG",
    }


def originate_lines(games, rating, league_pa, hf, penalties, week, short_to_full):
    """Originated fair lines for one week. All values are MODEL outputs."""
    lines = []
    now_utc = datetime.now(timezone.utc)
    for game in games:
        if game["week"] != week:
            continue
        # Never publish a prospective fair line for a game whose kickoff is past.
        kickoff = game.get("kickoff_utc") or ""
        if kickoff:
            kickoff_dt = datetime.fromisoformat(kickoff.replace("Z", "+00:00"))
            if kickoff_dt <= now_utc:
                continue
        home_s, away_s = game["home_team"], game["away_team"]
        home = short_to_full.get(home_s, home_s)
        away = short_to_full.get(away_s, away_s)
        rh, ra = rating.get(home), rating.get(away)
        if not rh or not ra:
            continue
        margin_home = rh["net_points_per_game"] - ra["net_points_per_game"]
        rest_diff = game.get("rest_diff_home_minus_away")
        rest_adj = 0.0
        if rest_diff is not None:
            rest_adj = max(-1.5, min(1.5, rest_diff * REST_POINT_PER_DAY))
        short_week = 0.0
        if game.get("rest_days_home") == 3:
            short_week -= SHORT_WEEK_PENALTY
        if game.get("rest_days_away") == 3:
            short_week += SHORT_WEEK_PENALTY
        pen_home = penalties.get(home, 0.0)
        pen_away = penalties.get(away, 0.0)
        pen_home_s = penalties.get(home_s, 0.0)
        pen_away_s = penalties.get(away_s, 0.0)
        availability_adj = (pen_away_s or pen_away) - (pen_home_s or pen_home)
        fair_margin = margin_home + HOME_EDGE_POINTS + rest_adj + short_week + availability_adj
        base_total = 2 * league_pa
        fair_total = base_total + (rh["net_points_per_game"] + ra["net_points_per_game"]) / 2
        home_win_p = normal_cdf(fair_margin / MARGIN_SIGMA)
        avail_status = ("MODEL - availability adjusted (official injury report + official depth chart)"
                        if (pen_home or pen_away) else
                        "UNVERIFIED - no official depth chart captured for either club; no availability adjustment applied")
        lines.append({
            "week": week, "game_slug": game["slug"],
            "away_team": away, "home_team": home,
            "kickoff_et": game["kickoff_et"], "kickoff_pt": game["kickoff_pt"], "network": game["network"],
            "model_fair_spread_home": round(fair_margin, 2),
            "model_fair_total": round(fair_total, 2),
            "model_home_win_probability": round(home_win_p, 4),
            "model_away_win_probability": round(1 - home_win_p, 4),
            "market_line": "", "market_price": "",
            "edge": "",
            "input_net_points_home": rh["net_points_per_game"], "input_net_points_away": ra["net_points_per_game"],
            "input_home_advantage_points": HOME_EDGE_POINTS,
            "input_rest_adjustment": round(rest_adj + short_week, 2),
            "input_availability_adjustment": round(availability_adj, 2),
            "availability_status": avail_status,
            "status": "MODEL FAIR VALUE - not a market line; edge requires a price source (see decisions register)",
            "source_url": game["source_url"],
            "supporting_source_url": rating[home]["source_url"],
        })
    return lines


# ---------------------------------------------------------------------------
# Correlation analysis.
# ---------------------------------------------------------------------------
def persistence_analysis(standings_rows):
    by = {}
    for r in standings_rows:
        by.setdefault(int(r["season"]), {})[r["team"]] = r
    # A partially played current season is not comparable to completed seasons.
    # Only retain seasons where every recorded team completed 17 games.
    seasons = [season for season in sorted(by) if len(by[season]) == 32 and all(
        int(r["w"]) + int(r["l"]) + int(r["t"]) == 17 for r in by[season].values())]
    pairs = []
    for a, b in zip(seasons, seasons[1:]):
        for team in by[a]:
            if team in by[b]:
                pairs.append((by[a][team], by[b][team], f"{a}->{b}"))
    metrics = {
        "net_points_per_game": (lambda r: (int(r["pf"]) - int(r["pa"])) / (int(r["w"]) + int(r["l"]) + int(r["t"]))),
        "points_for_per_game": (lambda r: int(r["pf"]) / (int(r["w"]) + int(r["l"]) + int(r["t"]))),
        "points_against_per_game": (lambda r: int(r["pa"]) / (int(r["w"]) + int(r["l"]) + int(r["t"]))),
        "win_pct": (lambda r: (int(r["w"]) + 0.5 * int(r["t"])) / (int(r["w"]) + int(r["l"]) + int(r["t"]))),
        "home_win_pct": (lambda r: int(r["home_w"]) / (int(r["home_w"]) + int(r["home_l"]) + int(r["home_t"]))),
    }
    out = []
    for name, fn in metrics.items():
        xs = [fn(a) for a, b, _ in pairs]
        ys = [fn(b) for a, b, _ in pairs]
        stats = pearson(xs, ys)
        fit = ols(xs, ys)
        out.append({
            "metric": name, "n_pairs": len(pairs),
            "correlation_r": stats["r"] if stats else "",
            "r_squared": stats["r2"] if stats else "",
            "regression_slope": fit["slope"] if fit else "",
            "regression_intercept": fit["intercept"] if fit else "",
            "slope_stderr": fit["stderr"] if fit else "",
            "slope_t_stat": fit["t"] if fit else "",
            "persistence_share_of_variance": stats["r2"] if stats else "",
            "interpretation": ("Descriptive year-to-year persistence on complete seasons only; not a causal "
                                "decomposition of skill and luck."),
            "status": "MODEL - computed from official NFL standings",
            "source_url": "https://www.nfl.com/standings/league/2025/REG",
            "source_urls": [f"https://www.nfl.com/standings/league/{season}/REG" for season in seasons],
        })
    return out, pairs


def signal_correlation_matrix(lines):
    """Correlation between the model inputs of the originated lines."""
    if len(lines) < 3:
        return []
    fields = [
        ("net_rating_gap", lambda l: l["input_net_points_home"] - l["input_net_points_away"]),
        ("availability_gap", lambda l: l["input_availability_adjustment"]),
        ("rest_gap", lambda l: l["input_rest_adjustment"]),
        ("home_advantage", lambda l: l["input_home_advantage_points"]),
    ]
    matrix = []
    for i, (name_i, fn_i) in enumerate(fields):
        for j, (name_j, fn_j) in enumerate(fields):
            if j < i:
                continue
            xs = [fn_i(l) for l in lines]
            ys = [fn_j(l) for l in lines]
            stats = pearson(xs, ys)
            matrix.append({
                "signal_a": name_i, "signal_b": name_j, "n_games": len(lines),
                "correlation_r": stats["r"] if stats else "UNVERIFIED - insufficient variation",
                "status": "MODEL - pilot sample from the captured week only",
            })
    return matrix




# ---------------------------------------------------------------------------
# Backtest on the official completed games captured in the by-week snapshots.
# ---------------------------------------------------------------------------
def solve(matrix, vector):
    """Gaussian elimination with partial pivoting; returns the solution vector."""
    n = len(vector)
    aug = [list(matrix[i]) + [vector[i]] for i in range(n)]
    for col in range(n):
        pivot = max(range(col, n), key=lambda r: abs(aug[r][col]))
        if abs(aug[pivot][col]) < 1e-12:
            return None
        aug[col], aug[pivot] = aug[pivot], aug[col]
        piv = aug[col][col]
        for r in range(n):
            if r == col:
                continue
            factor = aug[r][col] / piv
            for c in range(col, n + 1):
                aug[r][c] -= factor * aug[col][c]
    return [aug[i][n] / aug[i][i] for i in range(n)]


def multiple_ols(y, xs, names):
    """Least squares with intercept. xs is a list of equal-length feature lists."""
    n = len(y)
    k = len(xs)
    if n < k + 3:
        return None
    design = [[1.0] + [xs[j][i] for j in range(k)] for i in range(n)]
    p = k + 1
    xtx = [[sum(design[i][a] * design[i][b] for i in range(n)) for b in range(p)] for a in range(p)]
    xty = [sum(design[i][a] * y[i] for i in range(n)) for a in range(p)]
    beta = solve(xtx, xty)
    if beta is None:
        return None
    fitted = [sum(beta[a] * design[i][a] for a in range(p)) for i in range(n)]
    resid = [y[i] - fitted[i] for i in range(n)]
    sse = sum(e * e for e in resid)
    my = sum(y) / n
    sst = sum((v - my) ** 2 for v in y)
    dof = n - p
    sigma2 = sse / dof if dof > 0 else None
    # standard errors from the inverse of X'X (recomputed by solving for each column)
    inv = []
    for a in range(p):
        e = [1.0 if i == a else 0.0 for i in range(p)]
        inv.append(solve(xtx, e))
    stderr = []
    tstat = []
    for a in range(p):
        if inv[a] is None or sigma2 is None:
            stderr.append(None); tstat.append(None); continue
        se = math.sqrt(max(sigma2 * inv[a][a], 0.0))
        stderr.append(se)
        tstat.append(beta[a] / se if se else None)
    return {
        "n": n, "coefficients": {
            names[a]: {"estimate": round(beta[a], 4),
                       "stderr": round(stderr[a], 4) if stderr[a] is not None else "",
                       "t_stat": round(tstat[a], 4) if tstat[a] is not None else ""}
            for a in range(p)},
        "r_squared": round(1 - sse / sst, 4) if sst > 0 else "",
        "residual_std_points": round(math.sqrt(sigma2), 3) if sigma2 else "",
        "total_std_points": round(math.sqrt(sst / n), 3) if sst else "",
        "residual_variance_share": round(sse / sst, 4) if sst else "",
    }


def mean_test(values):
    n = len(values)
    if n < 2:
        return None
    m = sum(values) / n
    var = sum((v - m) ** 2 for v in values) / (n - 1)
    se = math.sqrt(var / n) if var > 0 else 0.0
    t = (m / se) if se else None
    return {"n": n, "mean": round(m, 4),
            "stdev": round(math.sqrt(var), 4),
            "stderr": round(se, 4), "t_stat": round(t, 4) if t is not None else "",
            "ci95_low": round(m - 1.96 * se, 4), "ci95_high": round(m + 1.96 * se, 4)}


def backtest(games):
    """Leakage-free backtest of the schedule features on the official final scores."""
    completed = [g for g in games if g.get("status") == "FINAL" and g.get("away_score") and g.get("home_score")]
    completed.sort(key=lambda g: (g["date"], g["kickoff_utc"] or ""))
    rolling = {}
    rows = []
    for g in completed:
        home, away = g["home_team"], g["away_team"]
        hs, as_ = int(g["home_score"]), int(g["away_score"])
        margin = hs - as_
        rh = rolling.get(home, {"g": 0, "pf": 0, "pa": 0})
        ra = rolling.get(away, {"g": 0, "pf": 0, "pa": 0})
        home_rating = (rh["pf"] - rh["pa"]) / rh["g"] if rh["g"] else None
        away_rating = (ra["pf"] - ra["pa"]) / ra["g"] if ra["g"] else None
        rows.append({
            "week": g["week"], "date": g["date"], "slug": g["slug"],
            "home_team": home, "away_team": away,
            "home_score": hs, "away_score": as_, "margin_home": margin,
            "home_win": 1 if margin > 0 else (0 if margin < 0 else 0.5),
            "rest_home": g.get("rest_days_home"), "rest_away": g.get("rest_days_away"),
            "rest_diff": g.get("rest_diff_home_minus_away"),
            "g11_home": g.get("games_in_11_home"), "g11_away": g.get("games_in_11_away"),
            "pre_game_rating_home": round(home_rating, 3) if home_rating is not None else "",
            "pre_game_rating_away": round(away_rating, 3) if away_rating is not None else "",
            "source_url": g["source_url"],
        })
        for team, pf, pa in ((home, hs, as_), (away, as_, hs)):
            cur = rolling.setdefault(team, {"g": 0, "pf": 0, "pa": 0})
            cur["g"] += 1
            cur["pf"] += pf
            cur["pa"] += pa
    margins = [r["margin_home"] for r in rows]
    home_wins = [r["home_win"] for r in rows]
    rest_home_more = [r["margin_home"] for r in rows if r["rest_diff"] and r["rest_diff"] > 0]
    rest_away_more = [r["margin_home"] for r in rows if r["rest_diff"] and r["rest_diff"] < 0]
    rest_equal = [r["margin_home"] for r in rows if r["rest_diff"] == 0]
    short_week = [r["margin_home"] for r in rows if r["rest_home"] == 3 or r["rest_away"] == 3]
    g11_heavy = [r["margin_home"] for r in rows if (r["g11_home"] or 0) >= 3]
    usable = [r for r in rows if r["pre_game_rating_home"] != "" and r["pre_game_rating_away"] != ""]
    rating_gap = [r["pre_game_rating_home"] - r["pre_game_rating_away"] for r in usable]
    rest_gap = [(r["rest_diff"] or 0) for r in usable]
    g11_gap = [((r["g11_home"] or 0) - (r["g11_away"] or 0)) for r in usable]
    model = multiple_ols([r["margin_home"] for r in usable], [rating_gap, rest_gap, g11_gap],
                          ["intercept", "pre_game_rating_gap", "rest_diff_home_minus_away", "games_in_11_gap"])
    home_n = len(home_wins)
    home_p = sum(home_wins) / home_n if home_n else None
    home_se = math.sqrt(home_p * (1 - home_p) / home_n) if home_n and 0 < home_p < 1 else 0.0
    home_rate = ({"n": home_n, "mean": round(home_p, 4), "stdev": round(math.sqrt(home_p * (1-home_p)), 4),
                  "stderr": round(home_se, 4), "z_vs_50pct": round((home_p-0.5)/home_se, 4) if home_se else "",
                  "ci95_low": round(max(0, home_p-1.96*home_se), 4), "ci95_high": round(min(1, home_p+1.96*home_se), 4)}
                 if home_n else None)
    summary = {
        "home_field": {
            "home_win_rate_test": home_rate,
            "mean_home_margin_test": mean_test(margins),
            "note": "Measured on every official completed game captured in the by-week snapshots.",
            "source_url": "https://www.nfl.com/schedules/2026/by-week/week-8",
            "source_urls": [f"https://www.nfl.com/schedules/2026/by-week/week-{w}" for w in range(1, 9)],
        },
        "rest": {
            "home_had_more_rest_mean_margin": mean_test(rest_home_more),
            "away_had_more_rest_mean_margin": mean_test(rest_away_more),
            "equal_rest_mean_margin": mean_test(rest_equal),
            "short_week_mean_margin": mean_test(short_week),
        },
        "games_in_11": {
            "home_third_game_in_11_mean_margin": mean_test(g11_heavy),
        },
        "model": model,
        "model_note": ("Least squares on the official final margins with a leakage-free rolling "
                       "pre-game rating built only from the official scores of earlier games."),
    }
    return rows, summary


# ---------------------------------------------------------------------------
# Gates, strategies, leaderboard.
# ---------------------------------------------------------------------------
def load_json(path: Path, default):
    if not path.exists():
        return default
    return json.loads(path.read_text())


def gate_results(strategy_rows, gate_defs, lines, correlation_rows):
    defs = {g["id"]: g for g in gate_defs}
    results = []
    for strat in strategy_rows:
        gates = []
        for gate in strat.get("gates", []):
            definition = defs.get(gate["id"], {})
            state = gate.get("state", "NOT TESTABLE")
            evidence = gate.get("evidence", "")
            if gate["id"] == "G2" and len(lines) > 0:
                evidence = f"{len(lines)} originated games in the captured week; no settled priced bets recorded."
            if gate["id"] == "G7":
                evidence = f"{len(correlation_rows)} measured signal correlations from the captured week."
            gates.append({
                "gate_id": gate["id"], "gate": definition.get("name", gate["id"]),
                "criterion": definition.get("criterion", ""),
                "state": state, "evidence": evidence,
            })
        passed = [g for g in gates if g["state"] == "PASS"]
        failed = [g for g in gates if g["state"] == "FAIL"]
        results.append({
            "strategy_id": strat["id"], "strategy": strat["name"],
            "gates_total": len(gates), "gates_passed": len(passed), "gates_failed": len(failed),
            "eligible_for_points": bool(strat.get("gates_passed") and strat["gates_passed"] == strat.get("gates_total")),
            "state": "ELIGIBLE" if strat.get("gates_passed") and strat["gates_passed"] == strat.get("gates_total") else "GATED",
            "gates": gates,
            "source_url": strat.get("source_url", "https://www.nfl.com/"),
        })
    return results


def build_leaderboard(strategy_rows, gate_rows, reward_tiers):
    by_id = {g["strategy_id"]: g for g in gate_rows}
    rows = []
    for strat in strategy_rows:
        g = by_id.get(strat["id"], {})
        rows.append({
            "strategy_id": strat["id"], "strategy": strat["name"], "bet_class": strat.get("bet_class", ""),
            "points": "", "bets_settled": "", "roi_pct": "", "rank": "",
            "eligibility": g.get("state", "GATED"),
            "reason": g.get("reason", "Awaiting settled priced bets and a price source"),
            "reward_tier": "",
            "source_url": strat.get("source_url", "https://www.nfl.com/"),
        })
    return {"rows": rows, "reward_tiers": reward_tiers}


def main():
    standings = read_csv(DATA / "standings.csv")
    teams = read_csv(DATA / "teams.csv")
    injuries = read_csv(DATA / "injuries_w10_2026.csv")
    depth = read_csv(DATA / "depth.csv")
    strategies = load_json(DATA / "strategies.json", {"strategies": []})["strategies"]
    gates_cfg = load_json(DATA / "gates.json", {"gates": []})
    rewards = load_json(DATA / "leaderboard_rules.json", {"reward_tiers": [], "scoring": {}})

    schedule_raw = parse_schedule()
    games = schedule_features(schedule_raw)
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "schedule_2026.json").write_text(json.dumps({
        "generated_utc": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "source": "official nfl.com by-week snapshots already captured in research/official/raw",
        "games": games,
    }, indent=2), encoding="utf-8")

    short_to_full = {r["short_name"]: r["full_name"] for r in teams}
    def_rows = deficiency_rows(injuries, depth, short_to_full)
    penalties = team_penalties(def_rows)
    (OUT / "deficiency.json").write_text(json.dumps({
        "generated_utc": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "model_parameters": {
            "position_group_weights_points": AVAILABILITY_WEIGHTS,
            "depth_multiplier": {str(k): v for k, v in DEPTH_MULTIPLIER.items()},
            "note": "MODEL parameters of this program, not official NFL values.",
        },
        "rows": def_rows,
        "team_penalty_points": penalties,
    }, indent=2), encoding="utf-8")

    rating, league_pf, league_pa = ratings(standings, 2026)
    hf = home_field_delta(standings)
    lines = originate_lines(games, rating, league_pa, hf, penalties, 10, short_to_full)
    lines_week11 = originate_lines(games, rating, league_pa, hf, penalties, 11, short_to_full)
    (OUT / "lines.json").write_text(json.dumps({
        "generated_utc": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "model_parameters": {
            "pythagorean_exponent": PYTHAGOREAN_EXPONENT,
            "margin_sigma_points": MARGIN_SIGMA,
            "home_edge_points": HOME_EDGE_POINTS,
            "rest_point_per_day": REST_POINT_PER_DAY,
            "short_week_penalty_points": SHORT_WEEK_PENALTY,
            "league_average_points_allowed_per_team_game": round(league_pa, 3),
            "note": "MODEL parameters of this program, not official NFL values and not market prices.",
        },
        "home_field": hf,
        "lines": lines,
        "next_week_lines": lines_week11,
    }, indent=2), encoding="utf-8")

    backtest_rows, backtest_summary = backtest(games)
    (OUT / "backtest.json").write_text(json.dumps({
        "generated_utc": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "panel": "official completed 2026 regular-season games read from the official nfl.com by-week snapshots",
        "summary": backtest_summary,
        "rows": backtest_rows,
    }, indent=2), encoding="utf-8")

    persistence, pairs = persistence_analysis(standings)
    corr_matrix = signal_correlation_matrix(lines)
    (OUT / "correlation.json").write_text(json.dumps({
        "generated_utc": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "season_persistence": persistence,
        "signal_matrix": corr_matrix,
        "parlay_rules": {
            "max_leg_correlation_abs": GATE_MAX_LEG_CORRELATION,
            "max_legs": GATE_MAX_PARLAY_LEGS,
            "effective_sample_size": "n_eff = n / (1 + (k - 1) * mean_rho)",
        },
        "source_url": "https://www.nfl.com/standings/league/2026/REG",
    }, indent=2), encoding="utf-8")

    gate_rows = gate_results(strategies, gates_cfg.get("gates", []), lines, corr_matrix)
    (OUT / "gate_results.json").write_text(json.dumps({
        "generated_utc": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "gate_definitions": gates_cfg.get("gates", []),
        "results": gate_rows,
    }, indent=2), encoding="utf-8")

    board = build_leaderboard(strategies, gate_rows, rewards.get("reward_tiers", []))
    board["scoring"] = rewards.get("scoring", {})
    (OUT / "leaderboard-register.json").write_text(json.dumps(board, indent=2), encoding="utf-8")

    print(json.dumps({
        "schedule_games": len(games),
        "deficiency_rows": len(def_rows),
        "teams_with_penalty": penalties,
        "lines": len(lines), "next_week_lines": len(lines_week11),
        "strategies": len(strategies),
    }, indent=2))


if __name__ == "__main__":
    main()
