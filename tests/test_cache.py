import sys
import unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
from reconcile_snapshot import reconcile

class CacheTest(unittest.TestCase):
    def test_committed_new_source_survives_an_older_cache(self):
        baseline = {'events': [{'id':'fresh', 'group':'cal_mbb'}, {'id':'old-mlb','group':'mlb'}], 'sources': {'cal_mbb': {'lastSuccess':'2026-11-02T10:00:00Z'}, 'mlb': {'lastSuccess':'2026-10-01T00:00:00Z'}}}
        cached = {'events': [{'id':'new-mlb','group':'mlb'}], 'sources': {'mlb': {'lastSuccess':'2026-11-02T12:00:00Z'}}}
        merged = reconcile(baseline, cached)
        self.assertEqual({e['id'] for e in merged['events']}, {'fresh','new-mlb'})
        self.assertEqual(merged['sources']['cal_mbb']['lastSuccess'], '2026-11-02T10:00:00Z')

if __name__ == '__main__':
    unittest.main()
