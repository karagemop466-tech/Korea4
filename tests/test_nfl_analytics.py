"""NFL analytics module integrity tests: pages, provenance rows, data sanity."""
import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
NA = ROOT / "data/nfl-analytics"
PAGES = ["nfl-analytics.html", "nfl-analytics-injuries.html", "nfl-signals.html", "nfl-analytics-lines.html",
         "nfl-analytics-strategies.html", "nfl-correlation.html", "suggestions.html", "open-questions.html"]


class PageTests(unittest.TestCase):
    def test_pages_exist_with_tables_and_sources(self):
        for rel in PAGES:
            p = ROOT / rel
            self.assertTrue(p.is_file(), f"missing page {rel}")
            text = p.read_text()
            self.assertIn("<thead>", text, rel)
            self.assertIn('data-source-url="https://', text, rel)
            self.assertIn("main-nav", text, rel)

    def test_nav_links_all_pages(self):
        text = (ROOT / "index.html").read_text()
        for rel in PAGES:
            self.assertIn(f'href="{rel}"', text, f"index nav missing {rel}")

    def test_correlation_calculator_present(self):
        text = (ROOT / "nfl-correlation.html").read_text()
        self.assertIn("bernoulliJoint", text)
        self.assertIn("Fréchet", text)


class DataTests(unittest.TestCase):
    def test_injuries_rows_all_sourced(self):
        d = json.loads((NA / "injuries-week10.json").read_text())
        self.assertTrue(d["rows"])
        for r in d["rows"]:
            self.assertTrue(r["source_url"].startswith("https://"), r["player"])
            self.assertIn(r["verification"], ("VERIFIED", "MIRROR — UNVERIFIED individually"))
        self.assertEqual(d["counts"]["verified_rows"], len(d["rows"]))
        # the 9 official game-status designations captured on 2026-11-13
        self.assertEqual(d["counts"]["with_game_status"], 9)

    def test_deficiencies_flag_unverified_joins(self):
        d = json.loads((NA / "deficiencies-week10.json").read_text())
        for r in d["rows"]:
            if not r["backup_next_man"].startswith("UNVERIFIED"):
                self.assertIn("depth", r["backup_next_man"] + "depth", r["player_out"])
            self.assertIn("MODEL JOIN", r["join_note"])

    def test_lines_are_labelled_model(self):
        d = json.loads((NA / "originated-lines-week10.json").read_text())
        self.assertEqual(len(d["rows"]), 13)  # week 10 minus completed TNF
        for r in d["rows"]:
            self.assertIn("MODEL ESTIMATED", r["verification"])
            self.assertIn("SECONDARY", r["verification"])
            self.assertIsNotNone(r["market_reference_home_spread"])

    def test_team_ratings_complete(self):
        d = json.loads((NA / "team-stats-2026.json").read_text())
        self.assertEqual(len(d["rows"]), 32)
        nets = [r["net_epa_per_play"] for r in d["rows"]]
        self.assertLessEqual(max(nets), 0.5)
        self.assertGreaterEqual(min(nets), -0.5)

    def test_leaderboard_is_spec_only(self):
        d = json.loads((NA / "leaderboard-2026.json").read_text())
        self.assertEqual(d["assumed_price"], -110)
        for r in d["rows"]:
            status = r["status"]
            self.assertTrue(("SPEC" in status) or ("SIMULATED" in status), r["id"])

    def test_strategies_gates_and_registry(self):
        s = json.loads((NA / "strategies.json").read_text())
        self.assertEqual(len(s["validation_gates"]), 7)
        ids = [g["id"] for g in s["validation_gates"]]
        self.assertEqual(ids, ["G1", "G2", "G3", "G4", "G5", "G6", "G7"])
        for r in s["starter_strategies"] + s["reward_tiers"] + s["validation_gates"]:
            self.assertTrue(r["source_url"].startswith("https://"))
        self.assertIn("never real-money payouts", " ".join(s["reward_principles"]))

    def test_suggestions_and_questions_sourced(self):
        s = json.loads((NA / "suggestions.json").read_text())
        self.assertTrue(len(s["rows"]) >= 10)
        for r in s["rows"]:
            self.assertTrue(r["source_url"].startswith("https://"), r["id"])
            allowed = ("PROPOSED", "UNDER REVIEW", "APPROVED", "IMPLEMENTED", "REJECTED/DEFERRED")
            self.assertTrue(r["status"].startswith(allowed), (r["id"], r["status"]))
        q = json.loads((NA / "open-questions.json").read_text())
        self.assertTrue(len(q["questions"]) >= 12)
        for r in q["questions"]:
            self.assertTrue(r["source_url"].startswith("https://"), r["id"])
            for key in ("known", "missing", "discovery", "blocks"):
                self.assertTrue(r[key], (r["id"], key))

    def test_meta_flags_registered(self):
        m = json.loads((ROOT / "data/official/meta.json").read_text())
        ids = {f["id"] for f in m["flags"]}
        for flag in ("IR-042", "IR-043", "IR-044", "IR-045"):
            self.assertIn(flag, ids)

    def test_snapshot_hashes_recorded(self):
        text = (ROOT / "research/nfl/raw/sha256sums.txt").read_text()
        for name in ("games.csv.gz", "injuries_2026.csv.gz", "depth_charts_2026.parquet",
                     "play_by_play_2026.csv.gz", "snap_counts_2026.csv.gz", "stats_team_week_2026.csv.gz"):
            self.assertIn(name, text)


if __name__ == "__main__":
    unittest.main()
