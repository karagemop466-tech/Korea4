"""Walk-forward NFL team-rating model that produces OUR OWN predicted spread and total.

Inputs : research/nfl-lines/raw/games.csv.gz  (nfldata games table, third-party; see manifest)
Outputs: research/nfl-lines/analysis/predictions.csv (one row per regular-season game, 2005+)

Rules (fixed before the backtest was run; see methodology page):
  * For each game, the model is refit using ONLY games whose gameday is strictly before
    the game's week start (no same-week or future information).
  * Margin model: ridge regression of (home - away) points on team strength columns
    (+1 home team, -1 away team) plus a home-field column that is NOT penalised.
  * Total model: ridge regression of total points on offense/defense columns.
  * Recency weights: exponential decay with a 365-day half-life.
  * Penalty LAMBDA = 20 for both models (chosen a priori; not tuned on test seasons).
"""
from __future__ import annotations

import csv
import gzip
import math
import datetime as dt
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
GAMES_GZ = ROOT / "research/nfl-lines/raw/games.csv.gz"
OUT_DIR = ROOT / "research/nfl-lines/analysis"

LAMBDA = 20.0
HALF_LIFE_DAYS = 365.0
FIRST_TEST_SEASON = 2005  # warm-up seasons before this are only used as training data

ODDS_FREE = {"REG"}


def load_games(path: Path = GAMES_GZ) -> list[dict]:
    with gzip.open(path, "rt", newline="") as fh:
        rows = list(csv.DictReader(fh))
    out = []
    for r in rows:
        if r["game_type"] not in ODDS_FREE and r["game_type"] != "POST":
            continue
        if r["home_score"] == "" or r["away_score"] == "":
            played = False
        else:
            played = True
        g = {
            "game_id": r["game_id"],
            "season": int(r["season"]),
            "game_type": r["game_type"],
            "week": int(r["week"]),
            "gameday": dt.date.fromisoformat(r["gameday"]) if r["gameday"] else None,
            "away": r["away_team"],
            "home": r["home_team"],
            "away_score": int(r["away_score"]) if played else None,
            "home_score": int(r["home_score"]) if played else None,
            "spread_line": float(r["spread_line"]) if r["spread_line"] else None,  # + = home favored
            "total_line": float(r["total_line"]) if r["total_line"] else None,
            "home_moneyline": r["home_moneyline"] or None,
            "away_moneyline": r["away_moneyline"] or None,
            "away_rest": int(r["away_rest"]) if r["away_rest"] else None,
            "home_rest": int(r["home_rest"]) if r["home_rest"] else None,
            "div_game": r["div_game"] == "1",
            "roof": r["roof"],
            "location": r["location"],
        }
        out.append(g)
    return out


def _weights(games_train, ref_date):
    w = []
    for g in games_train:
        age = (ref_date - g["gameday"]).days
        w.append(0.5 ** (age / HALF_LIFE_DAYS))
    return np.array(w)


def fit_margin(train, teams, ref_date):
    idx = {t: i for i, t in enumerate(teams)}
    n = len(teams)
    X = np.zeros((len(train), n + 1))
    y = np.zeros(len(train))
    for k, g in enumerate(train):
        X[k, idx[g["home"]]] += 1.0
        X[k, idx[g["away"]]] -= 1.0
        X[k, n] = 1.0  # home-field indicator (unpenalised)
        y[k] = g["home_score"] - g["away_score"]
    W = _weights(train, ref_date)
    P = np.eye(n + 1) * LAMBDA
    P[n, n] = 0.0
    A = X.T @ (X * W[:, None]) + P
    b = X.T @ (W * y)
    beta = np.linalg.solve(A, b)
    return {t: beta[idx[t]] for t in teams}, beta[n]


def fit_total(train, teams, ref_date):
    idx = {t: i for i, t in enumerate(teams)}
    n = len(teams)
    # columns: offense[0..n-1], defense[n..2n-1], intercept (unpenalised)
    X = np.zeros((len(train), 2 * n + 1))
    y = np.zeros(len(train))
    for k, g in enumerate(train):
        for t in (g["home"], g["away"]):
            X[k, idx[t]] += 1.0
        # defence: the OPPONENT's defence affects points scored by this team
        X[k, n + idx[g["away"]]] += 1.0
        X[k, n + idx[g["home"]]] += 1.0
        X[k, 2 * n] = 1.0
        y[k] = g["home_score"] + g["away_score"]
    W = _weights(train, ref_date)
    P = np.eye(2 * n + 1) * LAMBDA
    P[2 * n, 2 * n] = 0.0
    A = X.T @ (X * W[:, None]) + P
    b = X.T @ (W * y)
    beta = np.linalg.solve(A, b)
    return beta[:n], beta[n:2 * n], beta[2 * n], idx


def predict_total(home, away, off, dfn, intercept, idx, n):
    return intercept + off[idx[home]] + off[idx[away]] + dfn[idx[home]] + dfn[idx[away]]


def run(games: list[dict]) -> list[dict]:
    teams = sorted({g["home"] for g in games} | {g["away"] for g in games})
    reg = [g for g in games if g["game_type"] == "REG"]
    preds = []
    # group test games by (season, week) so the model is refit once per week
    keys = sorted({(g["season"], g["week"]) for g in reg if g["season"] >= FIRST_TEST_SEASON})
    for season, week in keys:
        week_games = [g for g in reg if g["season"] == season and g["week"] == week]
        week_start = min(g["gameday"] for g in week_games if g["gameday"])
        train = [g for g in games
                 if g["home_score"] is not None and g["gameday"] is not None and g["gameday"] < week_start]
        if len(train) < 100:
            continue
        ratings, hfa = fit_margin(train, teams, week_start)
        off, dfn, icpt, tidx = fit_total(train, teams, week_start)
        n = len(teams)
        for g in week_games:
            pm = ratings.get(g["home"], 0.0) - ratings.get(g["away"], 0.0) + hfa
            pt = predict_total(g["home"], g["away"], off, dfn, icpt, tidx, n)
            preds.append({
                "game_id": g["game_id"], "season": season, "week": week,
                "gameday": g["gameday"].isoformat() if g["gameday"] else "",
                "away": g["away"], "home": g["home"],
                "model_home_margin": round(float(pm), 2),
                "model_total": round(float(pt), 2),
                "train_games": len(train),
            })
    return preds


def main() -> None:
    games = load_games()
    preds = run(games)
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    out = OUT_DIR / "predictions.csv"
    with out.open("w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(preds[0].keys()))
        w.writeheader()
        w.writerows(preds)
    print(f"wrote {len(preds)} predictions -> {out.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
