"""Tests for the nfl-model section: the gate, the derived math, and the blank policy.

These exist so that the honesty machinery itself can regress. If a future edit fills a
result column, drops a source link, or lets a search-snippet-only citation back a
VERIFIED row, one of these tests fails.
"""
from __future__ import annotations

import json
import math
import re
import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SEC = ROOT / "nfl-model"
DATA = SEC / "data"
PAGES = sorted(SEC.glob("*.html"))


def data(name: str):
    return json.loads((DATA / f"{name}.json").read_text(encoding="utf-8"))


class GateTest(unittest.TestCase):
    def test_pages_exist(self) -> None:
        self.assertGreaterEqual(len(PAGES), 15, "the section should publish at least 15 pages")
        for needed in ("index.html", "suggestions.html", "questions.html", "flagged.html", "executive-summary.html"):
            self.assertTrue((SEC / needed).exists(), needed)

    def test_verification_gate_passes(self) -> None:
        proc = subprocess.run([sys.executable, "scripts/verify_nfl_model.py"], cwd=ROOT, capture_output=True, text=True)
        self.assertEqual(proc.returncode, 0, proc.stdout + proc.stderr)
        self.assertIn("PASS", proc.stdout)

    def test_every_row_carries_a_source_url(self) -> None:
        for page in PAGES:
            html = page.read_text(encoding="utf-8")
            rows = re.findall(r"<tbody>.*?</tbody>", html, flags=re.S)
            body = "".join(rows)
            trs = len(re.findall(r"<tr ", body))
            sourced = len(re.findall(r'data-source-url="https?://', body))
            self.assertEqual(trs, sourced, f"{page.name}: {trs - sourced} rows without a source link")

    def test_mandatory_disclosure_on_every_page(self) -> None:
        for page in PAGES:
            html = page.read_text(encoding="utf-8")
            for token in ("1-800-GAMBLER", "not betting advice", "does not guarantee"):
                self.assertIn(token, html, f"{page.name} missing {token!r}")

    def test_relative_assets_resolve(self) -> None:
        for page in PAGES:
            html = page.read_text(encoding="utf-8")
            for href in re.findall(r'(?:href|src)="([^"#]+)"', html):
                if href.startswith(("http", "mailto:", "data:")):
                    continue
                self.assertTrue((page.parent / href).exists(), f"{page.name}: broken link {href}")


class DerivedMathTest(unittest.TestCase):
    def test_break_even_and_required_n(self) -> None:
        p0 = 110 / 210
        self.assertAlmostEqual(p0, 0.52381, places=5)
        za, zb = 1.959963985, 0.841621234
        n2 = (za + zb) ** 2 * p0 * (1 - p0) / 0.02**2
        self.assertAlmostEqual(n2, 4894, delta=3)
        page = (SEC / "line-origination.html").read_text(encoding="utf-8")
        self.assertIn(f"{n2:,.0f}", page, "the required-n table must match the formula")
        self.assertIn("52.38%", page)

    def test_roi_standard_error(self) -> None:
        dec = 1 + 100 / 110
        se = dec * math.sqrt(0.55 * 0.45 / 300)
        self.assertAlmostEqual(se * 100, 5.48, places=1)
        page = (SEC / "line-origination.html").read_text(encoding="utf-8")
        self.assertIn(f"{se*100:.2f} pts", page)

    def test_frechet_bounds_are_wider_than_any_decision(self) -> None:
        pa = pb = 0.5238
        sd = math.sqrt(pa * (1 - pa) * pb * (1 - pb))
        lo = (max(0.0, pa + pb - 1) - pa * pb) / sd
        self.assertLess(lo, -0.9, "the lower bound should be near -1, which is why bounds cannot price a ticket")


class PolicyTest(unittest.TestCase):
    def test_no_strategy_has_results(self) -> None:
        for st in data("strategies")["strategies"]:
            self.assertEqual(st.get("results"), {}, f"{st['id']} has results without a bet ledger")

    def test_search_snippets_never_certify(self) -> None:
        reg = data("sources")["sources"]
        for s in reg:
            if s["status"] == "VERIFIED":
                self.assertIn(
                    s["method"],
                    {"page-fetched", "pdf-fetched", "github-api-404", "github-api", "repo-snapshot"},
                    f"{s['id']} claims VERIFIED from {s['method']}",
                )

    def test_suggestions_are_unimplemented_by_default(self) -> None:
        for s in data("suggestions")["suggestions"]:
            if s["status"] == "AWAITING-DECISION":
                self.assertTrue(s["decide"], f"{s['id']} awaits a decision but names none")
            self.assertIn(s["status"], {"AWAITING-DECISION", "AUTO-DONE", "NOT-RECOMMENDED"})

    def test_flags_do_not_collide_with_the_dashboard(self) -> None:
        for f in data("flagged")["items"]:
            self.assertGreater(int(f["id"].split("-")[1]), 26, f["id"])   # root pages use IR-001..IR-026

    def test_meta_counts_match_data(self) -> None:
        meta = data("meta")["counts"]
        self.assertEqual(meta["questions"], len(data("questions")["questions"]))
        self.assertEqual(meta["strategies"], len(data("strategies")["strategies"]))
        self.assertIsNone(data("meta")["data_snapshots"]["market_price_feed"])

    def test_injury_blanks_are_declared_not_filled(self) -> None:
        rows = data("injuries")["rows"]
        self.assertTrue(rows)
        for r in rows:
            self.assertIn(r["game_status"], {"", "Out", "Doubtful", "Questionable"})


class CollectorTest(unittest.TestCase):
    def test_assertions_reject_a_partial_render(self) -> None:
        proc = subprocess.run(
            [sys.executable, "scripts/fetch_nfl_model_sources.py", "--selftest"], cwd=ROOT, capture_output=True, text=True
        )
        self.assertEqual(proc.returncode, 0, proc.stdout + proc.stderr)
        self.assertIn("SELFTEST PASS", proc.stdout)


if __name__ == "__main__":
    unittest.main()
