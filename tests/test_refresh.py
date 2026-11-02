import unittest
import sys
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import refresh

class SourcesTest(unittest.TestCase):
    def test_mlb_tbd_never_uses_placeholder(self):
        game = {"gamePk": 123, "gameType": "R", "officialDate": "2027-04-01", "gameDate": "2027-04-01T08:33:00Z", "status": {"startTimeTBD": True}, "teams": {"away": {"team": {"id": 137, "name": "San Francisco Giants"}}, "home": {"team": {"id": 133, "name": "Athletics"}}}}
        row = refresh.parse_mlb({"dates": [{"date": "2027-04-01", "games": [game]}]})[0]
        self.assertIsNone(row["start"])
        self.assertEqual(row["possibleOffsetDays"], [-1, 0, 1])
        self.assertTrue(row["priority"])
        self.assertIn("gamePk=123", row["source"])
        game["status"]["startTimeTBD"] = False
        self.assertEqual(refresh.parse_mlb({"dates": [{"games": [game]}]})[0]["start"], "2027-04-01T08:33:00Z")

    def test_nfl_requires_requested_season_and_preserves_tbd(self):
        page = '''<li><a aria-label="Game Card" href="/games/raiders-at-49ers-2026-reg-18"><img alt="Las Vegas Raiders Team Logo"><img alt="San Francisco 49ers Team Logo"></a></li>'''
        self.assertEqual(refresh.parse_nfl(page, 2027), [])
        row = refresh.parse_nfl(page, 2026)[0]
        self.assertIsNone(row["start"])
        self.assertIsNone(row["date"])
        self.assertTrue(row["priority"])

    def test_network_tbd_ignores_fake_epochs(self):
        event = {"id": 7, "formatted_date": "NOVEMBER 14, 2026", "start_time": 1794632460, "end_time": 1794632520, "title": "Texas Tech at Oklahoma State", "description": "Air time TBD", "url": "https://www.westwoodonesports.com/events/7"}
        row = refresh.parse_westwood({"events": [event]})[0]
        self.assertIsNone(row["start"])
        self.assertIsNone(row["end"])
        self.assertEqual(row["possibleOffsetDays"], [-1, 0])

    def test_network_real_times_are_utc(self):
        event = {"id": 1, "formatted_date": "NOVEMBER 02, 2026", "start_time": 1793664000, "end_time": 1793681940, "title": "Bears at Seahawks", "description": "7:00 PM ET", "url": "https://www.westwoodonesports.com/events/1"}
        row = refresh.parse_westwood({"events": [event]})[0]
        self.assertEqual(row["start"], "2026-11-03T00:00:00Z")
        self.assertEqual(row["end"], "2026-11-03T04:59:00Z")

    def test_stanford_visible_tba_overrides_datetime(self):
        page = '''<div class="schedule-event-item" data-x="1"><div class="schedule-event-date--time-tba"><time datetime="2026-11-14T16:00:00-08:00"></time><span class="schedule-event-item-team__opponent-name">Virginia Tech</span>'''
        row = refresh.parse_stanford(page, "2026-11-01")[0]
        self.assertIsNone(row["start"])

    def test_cal_pacific_time_converts_during_standard_time(self):
        page = '''<div tabindex="0" aria-label="Game information for California Golden Bears Athletics Football versus Virginia on November 14, 2026" class="c-scoreboard__item c-scoreboard__item--away"><p class="c-scoreboard__time">12:30 PM</p>'''
        row = refresh.parse_cal(page, "2026-11-01")[0]
        self.assertEqual(row["start"], "2026-11-14T20:30:00Z")
        self.assertEqual(row["title"], "California at Virginia")

    def test_warriors_filter_excludes_preseason(self):
        game = {"gameId": "0022600001", "gameDateTimeUTC": "2027-02-16T03:00:00Z", "awayTeam": {"teamId": 1, "teamCity": "Indiana", "teamName": "Pacers"}, "homeTeam": {"teamId": 1610612744, "teamCity": "Golden State", "teamName": "Warriors"}}
        payload = {"leagueSchedule": {"gameDates": [{"games": [game, {**game, "gameId": "0012600001"}]}]}}
        rows = refresh.parse_warriors(payload)
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]["date"], "2027-02-15")
        self.assertEqual(rows[0]["source"], "https://www.nba.com/game/0022600001")

if __name__ == "__main__":
    unittest.main()
