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

if __name__ == '__main__': unittest.main()
