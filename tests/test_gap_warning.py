import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class RecommendationSafetyTests(unittest.TestCase):
    def test_metadata_withdraws_gap(self):
        meta = json.loads((ROOT / 'data/official/meta.json').read_text())
        anchor = meta['anchor_windows'][0]
        self.assertIn('Withdrawn', anchor['label'])
        self.assertIn('2027-02-15', anchor['window'])
        self.assertIn('calbears.com', anchor['source_url'])
        self.assertIn('omit known games', meta['analysis_conclusion']['conclusion'])

    def test_pages_warn_of_missing_game_and_uncertain_reception(self):
        for name in ('index.html', 'daily.html', 'calendar.html', 'vacation.html', 'flagged.html'):
            text = (ROOT / name).read_text()
            self.assertIn('Feb 17, 2027', text, name)
            self.assertIn('not included in this snapshot', text, name)
            self.assertIn('calbears.com/sports/mens-basketball/schedule/2026-27', text, name)
        flagged = (ROOT / 'flagged.html').read_text()
        self.assertIn('id="cal-radio-gap"', flagged)
        self.assertIn('KSFO 810 AM', flagged)

    def test_collector_does_not_restore_withdrawn_claim(self):
        text = (ROOT / 'scripts/collect_official.py').read_text()
        self.assertNotIn('The best short officially anchored gap is Feb 15–18', text)
        self.assertIn('Withdrawn: contains known radio conflict', text)


if __name__ == '__main__':
    unittest.main()
