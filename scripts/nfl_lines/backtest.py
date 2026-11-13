"""Strategy backtest, validation gates, correlation and leaderboard for the NFL lines project.

Pre-registered (fixed in this file BEFORE the first run; do not edit thresholds after seeing results):

Grading convention
  * Regular-season games with final scores and a closing spread (spread_line) / total (total_line).
  * Spread convention (nfldata): spread_line > 0 means the HOME team is favoured by that many points.
    Home covers if (home - away) > spread_line; away covers if < spread_line; equal = push.
  * Total: over if (home + away) > total_line; under if < total_line; equal = push.
  * Stake 1 unit at -110 on both sides (ASSUMED price; not an observed price). Win = +0.9091u, loss = -1u.
  * Out-of-sample test window: 2005-2025 seasons (+2026 weeks already played, reported separately).
    Models are walk-forward (see model.py); thresholds below are a-priori, not fitted.

Strategies (single bets)
  SPREAD_EDGE_1 / _2 / _3 : bet home if model_margin - spread_line >= t, away if <= -t (t = 1, 2, 3)
  TOTAL_EDGE_2 / _3 / _4  : bet over if model_total - total_line >= t, under if <= -t (t = 2, 3, 4)
  REST_3                  : bet the team with >= 3 more rest days (ATS); skip if none
  DIV_DOG                 : bet the underdog in divisional games (ATS)
  BASE_HOME               : always bet home (ATS)           [control]
  BASE_FAV                : always bet the favourite (ATS)  [control]
  BASE_RANDOM             : random side each game, seed 1..1000 [null distribution / luck control]

Validation gates (ALL must pass for a strategy to earn a reward)
  G1 sample size      : >= 400 graded bets in the test window
  G2 edge             : hit rate >= breakeven 52.38% AND Wilson 95% lower bound > 50%
  G3 significance     : one-sided exact binomial test of H0 "hit rate <= 52.38%" with Holm correction
                        across all strategies tested (family-wise alpha = 0.05)
  G4 stability        : positive ROI in >= 60% of test seasons
  G5 luck control     : hit rate exceeds the 95th percentile of the BASE_RANDOM null (same bet count)
  G6 forward          : 2026 forward slice (weeks already played) has ROI > 0 (reported, not used to select)

Correlation
  * phi coefficient between win/loss indicators of two bets on the same game (spread vs total)
  * phi between bets on different games in the same week (should be ~0 if independent)
  * Parlay joint hit rates are computed from observed outcomes, not assumed independence.
"""
from __future__ import annotations

import csv
import json
import math
import random
import datetime as dt
from collections import defaultdict
from pathlib import Path

import numpy as np

from model import load_games, ROOT

ANALYSIS = ROOT / "research/nfl-lines/analysis"
BREAKEVEN = 110 / 210  # 0.5238 at -110
PAYOUT = 100 / 110
TEST_START, TEST_END = 2005, 2025
FWD_SEASON = 2026
MIN_BETS = 400


def load_predictions():
    with (ANALYSIS / "predictions.csv").open() as fh:
        return {r["game_id"]: r for r in csv.DictReader(fh)}


def grade_spread(g, side):
    margin = g["home_score"] - g["away_score"]
    line = g["spread_line"]
    if margin == line:
        return None  # push
    if side == "home":
        return margin > line
    return margin < line


def grade_total(g, side):
    t = g["home_score"] + g["away_score"]
    line = g["total_line"]
    if t == line:
        return None
    return (t > line) if side == "over" else (t < line)


def build_bets(games, preds):
    """Return list of dicts: one per (game, strategy) with outcome in {True, False, None}."""
    bets = []
    for g in games:
        if g["game_type"] != "REG" or g["home_score"] is None:
            continue
        if g["season"] < TEST_START:
            continue
        p = preds.get(g["game_id"])
        if p is None or g["spread_line"] is None:
            continue
        ed_s = float(p["model_home_margin"]) - g["spread_line"]
        has_total = g["total_line"] is not None
        ed_t = float(p["model_total"]) - g["total_line"] if has_total else None
        base = {"game_id": g["game_id"], "season": g["season"], "week": g["week"],
                "home": g["home"], "away": g["away"], "gameday": g["gameday"].isoformat(),
                "spread_line": g["spread_line"], "total_line": g["total_line"],
                "model_home_margin": float(p["model_home_margin"]), "model_total": float(p["model_total"]),
                "home_score": g["home_score"], "away_score": g["away_score"]}

        def add(strategy, side_label, outcome, market):
            d = dict(base)
            d.update({"strategy": strategy, "bet": side_label, "market": market,
                      "outcome": outcome, "edge": None})
            bets.append(d)

        # spread edges
        for t in (1, 2, 3):
            if ed_s >= t:
                add(f"SPREAD_EDGE_{t}", "home", grade_spread(g, "home"), "spread")
            elif ed_s <= -t:
                add(f"SPREAD_EDGE_{t}", "away", grade_spread(g, "away"), "spread")
        # totals edges
        if has_total:
            for t in (2, 3, 4):
                if ed_t >= t:
                    add(f"TOTAL_EDGE_{t}", "over", grade_total(g, "over"), "total")
                elif ed_t <= -t:
                    add(f"TOTAL_EDGE_{t}", "under", grade_total(g, "under"), "total")
        # rest differential (positive = home has more rest)
        if g["home_rest"] is not None and g["away_rest"] is not None:
            diff = g["home_rest"] - g["away_rest"]
            if diff >= 3:
                add("REST_3", "home", grade_spread(g, "home"), "spread")
            elif diff <= -3:
                add("REST_3", "away", grade_spread(g, "away"), "spread")
        # divisional underdog
        if g["div_game"]:
            dog = "away" if g["spread_line"] > 0 else "home"
            if g["spread_line"] != 0:
                add("DIV_DOG", dog, grade_spread(g, dog), "spread")
        # baselines
        add("BASE_HOME", "home", grade_spread(g, "home"), "spread")
        fav = "home" if g["spread_line"] > 0 else "away"
        if g["spread_line"] != 0:
            add("BASE_FAV", fav, grade_spread(g, fav), "spread")
    return bets


def wilson(k, n, z=1.96):
    if n == 0:
        return (0.0, 0.0)
    p = k / n
    den = 1 + z * z / n
    centre = (p + z * z / (2 * n)) / den
    half = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / den
    return centre - half, centre + half


def binom_sf(k, n, p):
    """P(X >= k) for X ~ Binomial(n, p), exact, computed in log space."""
    if n == 0:
        return 1.0
    total = 0.0
    for i in range(k, n + 1):
        lc = math.lgamma(n + 1) - math.lgamma(i + 1) - math.lgamma(n - i + 1)
        total += math.exp(lc + i * math.log(p) + (n - i) * math.log(1 - p))
    return min(1.0, total)


def summarize(bets):
    graded = [b for b in bets if b["outcome"] is not None]
    wins = sum(1 for b in graded if b["outcome"])
    losses = len(graded) - wins
    pushes = len(bets) - len(graded)
    roi = (wins * PAYOUT - losses) / len(graded) if graded else 0.0
    return {"bets": len(bets), "graded": len(graded), "wins": wins, "losses": losses,
            "pushes": pushes, "hit_rate": wins / len(graded) if graded else 0.0, "roi": roi}


def holm(pvals):
    """Holm step-down adjusted p-values, returned in the same order as pvals."""
    m = len(pvals)
    order = sorted(range(m), key=lambda i: pvals[i])
    adj = [0.0] * m
    running = 0.0
    for rank, i in enumerate(order):
        val = min(1.0, (m - rank) * pvals[i])
        running = max(running, val)
        adj[i] = running
    return adj


def season_roi(bets):
    by = defaultdict(list)
    for b in bets:
        if b["outcome"] is not None:
            by[b["season"]].append(b)
    out = {}
    for s in sorted(by):
        out[s] = summarize(by[s])["roi"]
    return out


def random_null(games_bets_by_game, n_bets, seeds=1000):
    """Null: pick a random side for every game in the base set; record hit rate."""
    rates = []
    games = list(games_bets_by_game.values())
    for seed in range(1, seeds + 1):
        rng = random.Random(seed)
        sample = rng.sample(games, min(n_bets, len(games)))
        wins = losses = 0
        for g in sample:
            side = rng.choice(["home", "away"])
            outcome = grade_spread(g, side)
            if outcome is None:
                continue
            if outcome:
                wins += 1
            else:
                losses += 1
        if wins + losses:
            rates.append(wins / (wins + losses))
    return rates


def main():
    games = load_games()
    preds = load_predictions()
    bets = build_bets(games, preds)
    ANALYSIS.mkdir(parents=True, exist_ok=True)

    test_bets = [b for b in bets if TEST_START <= b["season"] <= TEST_END]
    fwd_bets = [b for b in bets if b["season"] == FWD_SEASON]

    strategies = sorted({b["strategy"] for b in test_bets})
    stats = {}
    pvals = {}
    for s in strategies:
        sb = [b for b in test_bets if b["strategy"] == s]
        st = summarize(sb)
        st["wilson95"] = wilson(st["wins"], st["graded"])
        st["p_value_vs_breakeven"] = binom_sf(st["wins"], st["graded"], BREAKEVEN) if st["graded"] else 1.0
        st["season_roi"] = season_roi(sb)
        pos = sum(1 for v in st["season_roi"].values() if v > 0)
        st["seasons_positive"] = pos
        st["seasons_total"] = len(st["season_roi"])
        st["forward_2026"] = summarize([b for b in fwd_bets if b["strategy"] == s])
        stats[s] = st
        pvals[s] = st["p_value_vs_breakeven"]

    adj = holm(list(pvals.values()))
    for (s, _), a in zip(pvals.items(), adj):
        stats[s]["p_holm"] = a

    # luck control: random-side null with the same number of games as BASE_HOME
    base_games = {}
    for b in test_bets:
        if b["strategy"] == "BASE_HOME":
            base_games[b["game_id"]] = next(g for g in games if g["game_id"] == b["game_id"])
    null_rates = random_null(base_games, len(base_games), seeds=1000)
    null_rates.sort()
    p95 = null_rates[int(0.95 * len(null_rates)) - 1]

    for s, st in stats.items():
        st["gates"] = {
            "G1_min_sample": st["graded"] >= MIN_BETS,
            "G2_edge_breakeven_and_wilson": st["hit_rate"] >= BREAKEVEN and st["wilson95"][0] > 0.5,
            "G3_holm_significant": st["p_holm"] < 0.05,
            "G4_stability_60pct_seasons": st["seasons_total"] > 0 and st["seasons_positive"] / st["seasons_total"] >= 0.6,
            "G5_beats_random_null_p95": st["hit_rate"] > p95,
            "G6_forward_2026_roi_positive": st["forward_2026"]["graded"] > 0 and st["forward_2026"]["roi"] > 0,
        }
        st["gates_passed"] = sum(st["gates"].values())
        st["all_gates_pass"] = all(st["gates"].values())

    # correlations ---------------------------------------------------------
    def phi(a, b):
        pairs = [(x, y) for x, y in zip(a, b) if x is not None and y is not None]
        if len(pairs) < 2:
            return None
        xs = np.array([1.0 if p[0] else 0.0 for p in pairs])
        ys = np.array([1.0 if p[1] else 0.0 for p in pairs])
        if xs.std() == 0 or ys.std() == 0:
            return None
        return float(np.corrcoef(xs, ys)[0, 1]), len(pairs)

    def fisher_ci(r, n):
        if r is None or n <= 3 or abs(r) >= 1:
            return None
        z = math.atanh(r); se = 1 / math.sqrt(n - 3)
        return [round(math.tanh(z - 1.96 * se), 4), round(math.tanh(z + 1.96 * se), 4)]

    # same-game: spread-edge bet vs total-edge bet for the same game (edge-selected sides)
    by_game = defaultdict(dict)
    for b in test_bets:
        by_game[b["game_id"]].setdefault(b["market"], {})[b["strategy"]] = b
    same_s, same_t = [], []
    for gid, d in by_game.items():
        sp = d.get("spread", {}).get("BASE_HOME")
        tt = d.get("total", {}).get("TOTAL_EDGE_2")
        if sp and tt and sp["outcome"] is not None and tt["outcome"] is not None:
            same_s.append(sp["outcome"])
            same_t.append(tt["outcome"])
    same_game_phi = phi(same_s, same_t)

    # cross-game within same week: BASE_HOME outcome of game i vs game j (sampled pairs)
    wk = defaultdict(list)
    for b in test_bets:
        if b["strategy"] == "BASE_HOME" and b["outcome"] is not None:
            wk[(b["season"], b["week"])].append(b["outcome"])
    rng = random.Random(7)
    cross_pairs = []
    for key, outs in wk.items():
        if len(outs) >= 2:
            i, j = rng.sample(range(len(outs)), 2)
            cross_pairs.append((outs[i], outs[j]))
    cross_phi = phi([p[0] for p in cross_pairs], [p[1] for p in cross_pairs])

    # parlays -------------------------------------------------------------
    # Two construction types, both using OBSERVED joint outcomes (no independence assumption):
    #   SAME_GAME : leg 1 = spread strategy bet, leg 2 = total strategy bet, same game
    #   CROSS_GAME: leg 1 and leg 2 on different games in the same week
    # Only non-baseline strategies with >= 100 graded bets are eligible.
    cand = [s for s in strategies if stats[s]["graded"] >= 100 and not s.startswith("BASE_")]
    spread_c = [s for s in cand if s.startswith(("SPREAD_", "REST_", "DIV_"))]
    total_c = [s for s in cand if s.startswith("TOTAL_")]
    parlay_rows = []
    for s1 in spread_c:
        for s2 in total_c:
            m1 = {b["game_id"]: b["outcome"] for b in test_bets if b["strategy"] == s1 and b["outcome"] is not None}
            m2 = {b["game_id"]: b["outcome"] for b in test_bets if b["strategy"] == s2 and b["outcome"] is not None}
            common = [g for g in m1 if g in m2]
            if len(common) < 100:
                continue
            both = sum(1 for g in common if m1[g] and m2[g])
            p1 = sum(m1[g] for g in common) / len(common)
            p2 = sum(m2[g] for g in common) / len(common)
            pj = both / len(common)
            parlay_rows.append({"type": "SAME_GAME", "leg_1": s1, "leg_2": s2, "n": len(common),
                                "p_leg1": round(p1, 4), "p_leg2": round(p2, 4),
                                "p_joint_observed": round(pj, 4),
                                "p_joint_if_independent": round(p1 * p2, 4)})
    # cross-game: all ordered pairs of distinct-game bets in the same week, per strategy pair
    week_bets = defaultdict(list)
    for b in test_bets:
        if b["outcome"] is not None and b["strategy"] in cand:
            week_bets[(b["season"], b["week"])].append(b)
    pair_stats = defaultdict(lambda: [0, 0, 0, 0])  # n, both, s1 wins, s2 wins
    for key, bl in week_bets.items():
        for i in range(len(bl)):
            for j in range(i + 1, len(bl)):
                a, c = bl[i], bl[j]
                if a["game_id"] == c["game_id"] or a["strategy"] == c["strategy"]:
                    continue
                k = tuple(sorted([a["strategy"], c["strategy"]]))
                wa = a["outcome"] if a["strategy"] == k[0] else c["outcome"]
                wc = c["outcome"] if a["strategy"] == k[0] else a["outcome"]
                ps = pair_stats[k]
                ps[0] += 1; ps[1] += int(wa and wc); ps[2] += int(wa); ps[3] += int(wc)
    for k, (n, both, w1, w2) in pair_stats.items():
        if n < 100:
            continue
        p1, p2, pj = w1 / n, w2 / n, both / n
        parlay_rows.append({"type": "CROSS_GAME", "leg_1": k[0], "leg_2": k[1], "n": n,
                            "p_leg1": round(p1, 4), "p_leg2": round(p2, 4),
                            "p_joint_observed": round(pj, 4),
                            "p_joint_if_independent": round(p1 * p2, 4)})
    for r in parlay_rows:
        pj = r["p_joint_observed"]
        r["parlay_ev_per_unit_observed"] = round(pj * (1 + PAYOUT) ** 2 - 1, 4)
        r["parlay_breakeven_joint"] = round(1 / (1 + PAYOUT) ** 2, 4)

    # model vs market diagnostics (skill of our own line compared with the closing spread)
    diag = {}
    for label, lo, hi in (("test_2005_2025", TEST_START, TEST_END), ("forward_2026", FWD_SEASON, FWD_SEASON)):
        rows = []
        for g in games:
            if g["game_type"] != "REG" or g["home_score"] is None or g["spread_line"] is None:
                continue
            if not (lo <= g["season"] <= hi):
                continue
            p_ = preds.get(g["game_id"])
            if p_ is None:
                continue
            rows.append((float(p_["model_home_margin"]), g["spread_line"], g["home_score"] - g["away_score"]))
        if len(rows) < 10:
            continue
        m = np.array([r[0] for r in rows]); l = np.array([r[1] for r in rows]); a = np.array([r[2] for r in rows])
        diag[label] = {
            "games": len(rows),
            "mae_model": round(float(np.mean(np.abs(m - a))), 3),
            "mae_market_closing_spread": round(float(np.mean(np.abs(l - a))), 3),
            "corr_model_vs_actual_margin": round(float(np.corrcoef(m, a)[0, 1]), 4),
            "corr_market_vs_actual_margin": round(float(np.corrcoef(l, a)[0, 1]), 4),
            "corr_model_vs_market": round(float(np.corrcoef(m, l)[0, 1]), 4),
        }

    result = {
        "generated_for_test_window": f"{TEST_START}-{TEST_END}",
        "forward_window": f"{FWD_SEASON} weeks already played",
        "breakeven_hit_rate": round(BREAKEVEN, 4),
        "assumed_price": -110,
        "n_strategies_tested": len(strategies),
        "luck_null": {"seeds": len(null_rates), "p50": round(float(np.percentile(null_rates, 50)), 4),
                      "p95": round(p95, 4), "p99": round(float(np.percentile(null_rates, 99)), 4),
                      "n_games": len(base_games)},
        "strategies": stats,
        "correlation": {
            "same_game_spread_vs_total_phi": None if same_game_phi is None else {"phi": round(same_game_phi[0], 4), "n": same_game_phi[1], "ci95": fisher_ci(*same_game_phi)},
            "cross_game_same_week_phi": None if cross_phi is None else {"phi": round(cross_phi[0], 4), "n": cross_phi[1], "ci95": fisher_ci(*cross_phi)},
        },
        "parlays": parlay_rows,
        "model_diagnostics": diag,
    }
    (ANALYSIS / "backtest.json").write_text(json.dumps(result, indent=2, default=str))

    with (ANALYSIS / "bets.csv").open("w", newline="") as fh:
        fields = ["strategy", "season", "week", "gameday", "away", "home", "bet", "market",
                  "spread_line", "total_line", "model_home_margin", "model_total",
                  "home_score", "away_score", "outcome"]
        w = csv.DictWriter(fh, fieldnames=fields, extrasaction="ignore")
        w.writeheader()
        for b in test_bets + fwd_bets:
            row = dict(b)
            row["outcome"] = "push" if b["outcome"] is None else ("win" if b["outcome"] else "loss")
            w.writerow(row)

    print(json.dumps({k: {kk: stats[k][kk] for kk in ("graded", "hit_rate", "roi", "p_holm", "gates_passed", "all_gates_pass")} for k in stats}, indent=1, default=str))
    print("luck null p95:", p95)
    print("correlation:", result["correlation"])
    print("parlays:", len(parlay_rows))


if __name__ == "__main__":
    main()
