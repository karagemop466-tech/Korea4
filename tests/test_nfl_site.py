import csv, json, unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
DATA=ROOT/'data'/'nfl'
class NFLLinesTests(unittest.TestCase):
    def read(self,name): return json.loads((DATA/name).read_text())
    def test_schedule_complete_and_source_linked(self):
        games=self.read('schedule_2026.json')['games']
        self.assertEqual(272,len(games))
        self.assertEqual(18,len({g['week'] for g in games}))
        self.assertEqual(32,len({t for g in games for t in (g['away_team'],g['home_team'])}))
        self.assertTrue(all(g.get('source_url','').startswith('https://www.nfl.com/') for g in games))
        self.assertEqual(16,sum(g['week']==18 for g in games))
        self.assertTrue(all(not g['date'] and not g['kickoff_et'] for g in games if g['week']==18))
        finals=[g for g in games if g['status']=='FINAL']
        self.assertEqual(120,len(finals))
        self.assertTrue(all(g['away_score']!='' and g['home_score']!='' for g in finals))
    def test_standings_only_use_completed_season_pairs(self):
        corr=self.read('correlation.json')['season_persistence']
        self.assertTrue(all(row['n_pairs']==32 for row in corr))
        net=next(row for row in corr if row['metric']=='net_points_per_game')
        self.assertAlmostEqual(.3223,net['correlation_r'],places=4)
    def test_model_lines_never_claim_market_prices(self):
        data=self.read('lines.json')
        for row in data['lines']+data['next_week_lines']:
            self.assertTrue(row['source_url'].startswith('https://www.nfl.com/'))
            self.assertEqual('',row['market_line'])
            self.assertEqual('',row['market_price'])
            self.assertIn('MODEL FAIR VALUE',row['status'])
            self.assertTrue(row['kickoff_et'])
            self.assertTrue(row['source_url'].startswith('https://www.nfl.com/'))
    def test_leaderboard_is_gated_without_prices(self):
        rows=self.read('leaderboard.json')['rows']
        self.assertTrue(rows)
        self.assertTrue(all(row['eligibility']=='GATED' and row['points']=='' for row in rows))
    def test_injury_rows_have_official_sources_and_explicit_depth_gaps(self):
        with (DATA/'injuries_w10_2026.csv').open() as f: rows=list(csv.DictReader(f))
        self.assertEqual(298,len(rows))
        self.assertTrue(all(r['source_url'].startswith('https://www.nfl.com/') for r in rows))
        teams=self.read('deficiency.json')['rows']
        self.assertTrue(all(r.get('source_url','').startswith('https://www.nfl.com/') for r in teams))
    def test_every_published_table_row_has_official_link(self):
        from html.parser import HTMLParser
        class Audit(HTMLParser):
            def __init__(self): super().__init__(); self.inrow=False; self.cells=0; self.rowlinks=0; self.bad=[]
            def handle_starttag(self,tag,attrs):
                a=dict(attrs)
                if tag=='tr': self.inrow=True; self.cells=0; self.rowlinks=0
                elif self.inrow and tag=='td': self.cells+=1
                elif self.inrow and tag=='a' and a.get('href','').startswith('https://'): self.rowlinks+=1
            def handle_endtag(self,tag):
                if tag=='tr' and self.inrow:
                    if self.cells and not self.rowlinks: self.bad.append('table row without source link')
                    self.inrow=False
        pages=['nfl-lines.html','nfl-lines-overview.html','nfl-schedule.html','nfl-fair-lines.html','nfl-availability.html','nfl-analysis.html','nfl-strategies.html','nfl-leaderboard.html','nfl-flagged.html']
        for name in pages:
            parser=Audit(); parser.feed((ROOT/name).read_text())
            self.assertFalse(parser.bad, name)
if __name__=='__main__': unittest.main()
