"""Unit and leakage tests for the NFL Lines Lab pipeline (scripts/nfl_lines)."""
import csv
import datetime as dt
import math
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts" / "nfl_lines"))

import backtest  # noqa: E402
import model  # noqa: E402


def game(home, away, hs, as_, spread=None, total=None):
    return {"home": home, "away": away, "home_score": hs, "away_score": as_,
            "spread_line": spread, "total_line": total, "game_type": "REG"}


class GradingTests(unittest.TestCase):
    def test_home_covers_when_margin_exceeds_spread(self):
        g = game("BAL", "JAX", 10, 33, spread=-8.5)  # JAX favoured by 8.5 under nfldata convention
        self.assertEqual(backtest.grade_spread(g, "away"), True)  # JAX won by 23 > 8.5
        self.assertEqual(backtest.grade_spread(g, "home"), False)

    def test_push_on_equal_margin(self):
        g = game("A", "B", 24, 17, spread=7.0)
        self.assertIsNone(backtest.grade_spread(g, "home"))

    def test_total_grading(self):
        g = game("A", "B", 20, 20, total=40.5)
        self.assertFalse(backtest.grade_total(g, "over"))
        self.assertTrue(backtest.grade_total(g, "under"))


class StatisticsTests(unittest.TestCase):
    def test_holm_is_monotone_and_capped(self):
        adj = backtest.holm([0.01, 0.04, 0.03])
        self.assertTrue(all(0 <= a <= 1 for a in adj))
        self.assertAlmostEqual(adj[0], 0.03)  # 3 * 0.01
        self.assertAlmostEqual(adj[2], 0.06)  # 2 * 0.03 (rank 1)

    def test_binomial_tail_matches_small_case(self):
        # P(X >= 3) for n=3, p=0.5 is 1/8
        self.assertAlmostEqual(backtest.binom_sf(3, 3, 0.5), 0.125)

    def test_wilson_interval_contains_point_estimate(self):
        lo, hi = backtest.wilson(520, 1000)
        self.assertLess(lo, 0.52)
        self.assertGreater(hi, 0.52)


class LeakageTests(unittest.TestCase):
    """A stored prediction must equal a refit that uses only games played before its week."""

    def test_prediction_uses_only_prior_games(self):
        games = model.load_games()
        with (model.OUT_DIR / "predictions.csv").open(newline="") as fh:
            preds = {r["game_id"]: r for r in csv.DictReader(fh)}
        reg = [g for g in games if g["season"] == 2024 and g["game_type"] == "REG" and g["week"] == 5]
        self.assertTrue(reg, "2024 week 5 games missing")
        g = reg[0]
        week_start = min(x["gameday"] for x in reg if x["gameday"])
        train = [x for x in games if x["home_score"] is not None and x["gameday"] is not None and x["gameday"] < week_start]
        teams = sorted({x["home"] for x in games} | {x["away"] for x in games})
        ratings, hfa = model.fit_margin(train, teams, week_start)
        expected = ratings[g["home"]] - ratings[g["away"]] + hfa
        self.assertAlmostEqual(expected, float(preds[g["game_id"]]["model_home_margin"]), places=1)
        self.assertTrue(all(x["gameday"] < week_start for x in train))


class OfficialRecordTests(unittest.TestCase):
    def test_week9_official_scores_match_source_data(self):
        import gzip
        with (ROOT / "research/nfl-lines/official/nfl_2026_week9_final_scores.csv").open(newline="") as fh:
            off = list(csv.DictReader(fh))
        with gzip.open(ROOT / "research/nfl-lines/raw/games.csv.gz", "rt", newline="") as fh:
            src = {(r["season"], r["week"], r["away_team"], r["home_team"]): r for r in csv.DictReader(fh)}
        for o in off:
            r = src[(o["season"], o["week"], o["away_team"], o["home_team"])]
            self.assertEqual((r["away_score"], r["home_score"]), (o["away_score"], o["home_score"]))


if __name__ == "__main__":
    unittest.main()
