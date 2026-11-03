"""Regression tests for the independent primary-site provenance audit."""
import gzip
import hashlib
import importlib.util
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('verify', ROOT / 'scripts/verify.py')
verify = importlib.util.module_from_spec(spec)
spec.loader.exec_module(verify)


class VerificationTests(unittest.TestCase):
    def test_missing_attribute_is_not_skipped(self):
        with tempfile.TemporaryDirectory() as d:
            p = Path(d) / 'a.html'
            p.write_text('<table><tbody><tr><td>No source</td></tr></tbody></table>')
            rows = verify.parse_primary_rows(p)
            self.assertEqual(len(rows), 1)
            self.assertFalse(verify.source_row_valid(rows[0]))

    def test_source_must_match_visible_link(self):
        row = {'attrs': {'data-source-url': 'https://www.mlb.com/'}, 'links': ['https://example.com/']}
        self.assertFalse(verify.source_row_valid(row))
        row['links'] = ['https://www.mlb.com/']
        self.assertTrue(verify.source_row_valid(row))

    def test_approved_domains_are_exact(self):
        self.assertTrue(verify.official_url('https://www.49ers.com/schedule/'))
        for url in ['https://www.vividseats.com/', 'https://www.mlb.com.evil.test/', 'https://user@www.mlb.com/', 'javascript:alert(1)']:
            self.assertFalse(verify.official_url(url))

    def test_corruption_is_detected(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            (root / 'raw.gz').write_bytes(gzip.compress(b'official snapshot'))
            record = {'key': 'test', 'url': 'https://www.mlb.com/', 'raw_file': 'raw.gz',
                      'bytes': 17, 'sha256': hashlib.sha256(b'official snapshot').hexdigest()}
            self.assertEqual(verify.snapshot_errors({'files': [record]}, root), [])
            (root / 'raw.gz').write_bytes(gzip.compress(b'altered'))
            self.assertTrue(verify.snapshot_errors({'files': [record]}, root))

    def test_49ers_parser_cites_captured_schedule(self):
        spec = importlib.util.spec_from_file_location('collector', ROOT / 'scripts/collect_official.py')
        collector = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(collector)
        from collections import defaultdict
        rows, _ = collector.parse_49ers_events(defaultdict(list))
        self.assertEqual(len(rows), 19)
        self.assertTrue(all(r['source_url'] == 'https://www.49ers.com/schedule/' for r in rows))


if __name__ == '__main__':
    unittest.main()
