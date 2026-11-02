import json
import re
import unittest
from datetime import datetime
from pathlib import Path
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parents[1]

class SnapshotTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data = json.loads((ROOT / 'site/data/events.json').read_text())

    def test_every_event_has_unique_id_and_official_https_source(self):
        ids = set()
        domains = {'statsapi.mlb.com', 'www.nfl.com', 'media.nfl.com', 'gostanford.com', 'calbears.com', 'www.westwoodonesports.com', 'www.nba.com', 'www.sjearthquakes.com', 'vucommodores.com', 'valkyries.wnba.com', 'sjsuspartans.com'}
        for row in self.data['events']:
            self.assertFalse(row['id'] in ids, f"Duplicate event ID: {row['id']}")
            ids.add(row['id'])
            url = urlparse(row['source'])
            self.assertEqual(url.scheme, 'https', row['id'])
            self.assertIn(url.netloc, domains, row['source'])
            if row.get('start'):
                self.assertIsNotNone(datetime.fromisoformat(row['start'].replace('Z', '+00:00')).tzinfo, row['id'])
            if row.get('date'):
                self.assertRegex(row['date'], r'^202[6-9]-\d{2}-\d{2}$')

    def test_future_team_coverage_and_unknown_dates_are_honest(self):
        games = self.data['events']
        sf = [r for r in games if r['group'] == 'warriors' and r['date'] in ('2027-02-15', '2027-02-17')]
        if self.data['sources'].get('warriors', {}).get('ok') and self.data['sources']['warriors'].get('season') == '2026-27':
            self.assertEqual({x['date'] for x in sf}, {'2027-02-15', '2027-02-17'})
        sb = next(r for r in games if r['id'] == 'nfl-super-bowl-lxi')
        self.assertIsNone(sb['start'])
        self.assertEqual(sb['date'], '2027-02-14')
        self.assertFalse(any('stanford' in x['title'].lower() and 'tcu' in x['title'].lower() and x.get('date', '').startswith('2027') for x in games if x.get('date')))

    def test_terrestrial_basketball_is_not_omitted_or_confused_with_streaming(self):
        games = {e['id']: e for e in self.data['events']}
        self.assertEqual(games['cal-mbb-2026-11-02']['station'], 'KSFO 810 AM')
        self.assertEqual(games['wnba-valkyries-2026-08-07']['station'], 'KGMZ 95.7 FM')
        self.assertIn('gameday-preview-20260807', games['wnba-valkyries-2026-08-07']['source'])
        self.assertEqual(games['wnba-valkyries-2026-10-29']['start'], '2026-10-29T16:30:00Z')
        self.assertNotIn('wnba-valkyries-2026-07-04', games, 'app-only match is not a terrestrial broadcast')

    def test_prior_nfl_season_games_played_in_2026_are_included(self):
        history = [e for e in self.data['events'] if e.get('group') == 'nfl_history']
        self.assertEqual(len(history), 30)
        self.assertEqual(sum(e['category'] == 'Regular season' for e in history), 16)
        self.assertEqual(sum(e['category'] == 'Postseason' for e in history), 13)
        pro = next(e for e in history if e['id'] == 'nfl-history-pro-bowl-flag')
        self.assertEqual(pro['start'], '2026-02-04T01:00:00Z')
        self.assertIsNone(pro['durationMinutes'])
        disagreement = next(e for e in history if e['id'] == 'nfl-history-wild-texans-steelers')
        self.assertIsNone(disagreement['start'])
        self.assertIn('conflict', disagreement['dateBasis'])
        self.assertTrue(any('49ers' in e['title'] and e['date'] == '2026-01-11' for e in history))

    def test_restrictions_are_source_linked(self):
        for r in self.data['restrictions']:
            self.assertLess(r['startDate'], r['endDate'])
            self.assertEqual(urlparse(r['source']).scheme, 'https')

if __name__ == '__main__':
    unittest.main()
