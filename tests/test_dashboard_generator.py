import importlib.util
import unittest
from pathlib import Path

path = Path(__file__).resolve().parents[1] / 'scripts' / 'build_site.py'
spec = importlib.util.spec_from_file_location('dashboard_generator', path)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)

class DashboardGeneratorTest(unittest.TestCase):
    def test_estimates_and_unknowns_are_not_verified_badges(self):
        self.assertIn('badge-estimated', module.badge('ESTIMATED — NOT A REAL VERIFIED RELEASED SCHEDULE'))
        self.assertIn('badge-unverified', module.badge('ESTIMATED / UNVERIFIED'))
        self.assertIn('badge-verified', module.badge('VERIFIED'))

    def test_snapshot_gaps_not_certified(self):
        for row in module.free_rows_for_today():
            self.assertIn('UNVERIFIED', row['status'])

class FreeRunAnalysisTest(unittest.TestCase):
    """Guards the vacation answer against silent drift."""

    def setUp(self):
        self.data = module.FREE_RUNS

    def test_every_day_has_exactly_one_class(self):
        for year, rec in self.data['per_year'].items():
            self.assertEqual(sum(rec['class_counts'].values()), rec['days_in_snapshot'], year)

    def test_no_seven_day_window_and_no_hidden_overclaim(self):
        self.assertLess(self.data['counts']['max_strict_free_run_days'], 7)
        self.assertEqual(self.data['counts']['max_strict_free_run_days'], 5)

    def test_published_bounded_runs_have_sources_on_both_ends(self):
        for row in self.data['published_bounded']:
            self.assertTrue(row['block_before_source'].startswith('https://'), row)
            self.assertTrue(row['block_after_source'].startswith('https://'), row)
            self.assertLess(row['days'], 7)

    def test_every_shortlist_row_links_an_official_source(self):
        for row in self.data['shortlist']:
            self.assertTrue((row.get('block_before_source') or row.get('block_after_source') or '').startswith('https://'), row)

    def test_other_sports_missing_is_stated_not_hidden(self):
        status = self.data['other_sports']['status']
        self.assertTrue(status)
        if str(status).startswith('NOT CAPTURED'):
            self.assertIn('F-018', module.other_sports_line())


if __name__ == '__main__': unittest.main()
