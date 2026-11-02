import unittest
from unittest.mock import patch
import sys
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import refresh

class SourcesTest(unittest.TestCase):
    def test_fetch_failure_keeps_last_stored_events_and_marks_stale(self):
        old = {"events": [{"id": "mlb-old", "group": "mlb", "date": "2027-04-01", "start": None, "title": "Stored game", "source": "https://statsapi.mlb.com/api/v1/schedule?gamePk=1"}], "sources": {"mlb": {"lastSuccess": "2026-11-01T00:00:00Z"}}}
        with patch.object(refresh, "request", side_effect=OSError("source unavailable")):
            snapshot = refresh.build_snapshot(old)
        self.assertFalse(snapshot["sources"]["mlb"]["ok"])
        self.assertEqual(snapshot["sources"]["mlb"]["lastSuccess"], "2026-11-01T00:00:00Z")
        self.assertTrue(any(e["id"] == "mlb-old" for e in snapshot["events"]))

    def test_mlb_tbd_never_uses_placeholder(self):
        game = {"gamePk": 123, "gameType": "R", "officialDate": "2027-04-01", "gameDate": "2027-04-01T08:33:00Z", "status": {"startTimeTBD": True}, "teams": {"away": {"team": {"id": 137, "name": "San Francisco Giants"}}, "home": {"team": {"id": 133, "name": "Athletics"}}}}
        row = refresh.parse_mlb({"dates": [{"date": "2027-04-01", "games": [game]}]})[0]
        self.assertIsNone(row["start"])
        self.assertEqual(row["possibleOffsetDays"], [-1, 0, 1])
        self.assertTrue(row["priority"])
        self.assertIn("gamePk=123", row["source"])
        game["status"]["startTimeTBD"] = False
        self.assertEqual(refresh.parse_mlb({"dates": [{"games": [game]}]})[0]["start"], "2027-04-01T08:33:00Z")

    def test_mlb_resumed_game_keeps_both_segments(self):
        game = {"gamePk": 77, "gameType": "R", "officialDate": "2026-06-16", "gameDate": "2026-06-16T23:15:00Z", "status": {"startTimeTBD": False}, "teams": {"away": {"team": {"name": "Giants"}}, "home": {"team": {"name": "Braves"}}}}
        resumed = {**game, "gameDate": "2026-06-17T18:00:00Z", "resumedFrom": game["gameDate"]}
        rows = refresh.parse_mlb({"dates": [{"date": "2026-06-16", "games": [game]}, {"date": "2026-06-17", "games": [resumed]}]})
        self.assertNotEqual(rows[0]["id"], rows[1]["id"])
        self.assertEqual(rows[1]["date"], "2026-06-17")
        self.assertEqual(rows[1]["dateBasis"], "Official resumed game start")

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
        self.assertEqual(row["possibleOffsetDays"], [-1, 0, 1])

    def test_network_real_times_are_utc(self):
        event = {"id": 1, "formatted_date": "NOVEMBER 02, 2026", "start_time": 1793664000, "end_time": 1793681940, "title": "Bears at Seahawks", "description": "7:00 PM ET", "url": "https://www.westwoodonesports.com/events/1"}
        row = refresh.parse_westwood({"events": [event]})[0]
        self.assertEqual(row["start"], "2026-11-03T00:00:00Z")
        self.assertEqual(row["end"], "2026-11-03T04:59:00Z")

    def test_stanford_visible_tba_overrides_datetime(self):
        page = '''<div class="schedule-event-item" data-x="1"><div class="schedule-event-date--time-tba"><time datetime="2026-11-14T16:00:00-08:00"></time><span class="schedule-event-item-team__opponent-name">Virginia Tech</span>'''
        row = refresh.parse_stanford(page, "2026-11-01")[0]
        self.assertIsNone(row["start"])
        away_page = page.replace('data-x="1"', 'data-x="1"><div class="schedule-event-item__top--away"')
        away_row = refresh.parse_stanford(away_page, "2026-11-01")[0]
        self.assertEqual(away_row["possibleOffsetDays"], [-1, 0, 1])

    def test_cal_pacific_time_converts_during_standard_time(self):
        page = '''<div tabindex="0" aria-label="Game information for California Golden Bears Athletics Football versus Virginia on November 14, 2026" class="c-scoreboard__item c-scoreboard__item--away"><p class="c-scoreboard__time">12:30 PM</p>'''
        row = refresh.parse_cal(page, "2026-11-01")[0]
        self.assertEqual(row["start"], "2026-11-14T20:30:00Z")
        self.assertEqual(row["title"], "California at Virginia")

    def test_cal_text_schedule_retains_known_start_and_tbd(self):
        page = """<h1>2026 Football Schedule</h1><table><tr><td>Nov 14 (Sat)</td><td>12:30 PM</td><td>Away</td><td>Virginia</td></tr><tr><td>Nov 21 (Sat)</td><td></td><td>Home</td><td>Stanford</td></tr><tr><td>Nov 28 (Sat)</td><td></td><td>Away</td><td>Boston College</td></tr></table>"""
        rows = refresh.parse_cal_text(page)
        self.assertEqual(rows[0]["start"], "2026-11-14T20:30:00Z")
        self.assertIsNone(rows[1]["start"])
        self.assertEqual(rows[0]["source"], refresh.CAL_TEXT)
        self.assertEqual(rows[2]["possibleOffsetDays"], [-1, 0, 1])

    def test_postponed_mlb_does_not_reuse_old_date(self):
        game = {"gamePk": 88, "gameType": "R", "officialDate": "2026-04-01", "gameDate": "2026-04-01T20:00:00Z", "status": {"startTimeTBD": False, "detailedState": "Postponed"}, "teams": {"away": {"team": {"name": "A"}}, "home": {"team": {"name": "B"}}}}
        row = refresh.parse_mlb({"dates": [{"date": "2026-04-01", "games": [game]}]})[0]
        self.assertIsNone(row["date"])
        self.assertIsNone(row["start"])
        self.assertIn("Postponed", row["dateBasis"])

    def test_cal_basketball_rolls_season_year_and_uses_only_pt(self):
        source = """<h1>2026-27 Men's Basketball Schedule</h1><table><tr><td>Nov 2 (Mon)</td><td>5 p.m. PT</td><td>Home</td><td>Adams State</td></tr><tr><td>Jan 2 (Sat)</td><td>11:15 a.m. PT / 2:15 p.m. ET</td><td>Away</td><td>Duke</td></tr><tr><td>Jan 5 (Tue)</td><td>7 p.m. ET</td><td>Away</td><td>Virginia</td></tr><tr><td>Oct 16 (Fri)</td><td>6 p.m. PT</td><td>Away</td><td>LMU (exhib.)</td></tr></table>"""
        rows = refresh.parse_cal_basketball(source)
        self.assertEqual(len(rows), 3)
        self.assertEqual(rows[0]['start'], '2026-11-03T01:00:00Z')
        self.assertEqual(rows[1]['date'], '2027-01-02')
        self.assertEqual(rows[1]['start'], '2027-01-02T19:15:00Z')
        self.assertIsNone(rows[2]['start'])
        self.assertEqual(rows[2]['possibleOffsetDays'], [-1, 0, 1])

    def test_valkyries_omits_app_only_rows_and_keeps_fm(self):
        source = """<table><tr><td>Friday, May 8</td><td>at Seattle</td><td>7:00 p.m.</td><td>ION</td><td>95.7 The Game, The Audacy App</td></tr><tr><td>Saturday, July 4</td><td>at Atlanta</td><td>10:00 a.m.</td><td>CBS</td><td>The Audacy App</td></tr></table>"""
        rows = refresh.parse_valkyries(source)
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]['start'], '2026-05-09T02:00:00Z')
        self.assertEqual(rows[0]['station'], 'KGMZ 95.7 FM')

    def test_earthquakes_team_table_is_pacific_and_source_linked(self):
        page = """<table><tr><td>Saturday, Nov. 7, 2026</td><td>Minnesota United FC</td><td>Away</td><td>4:00 PM</td><td>810 / 1370</td></tr></table>"""
        row = refresh.parse_earthquakes(page)[0]
        self.assertEqual(row["start"], "2026-11-08T00:00:00Z")
        self.assertEqual(row["station"], "KSFO 810 AM / KZSF 1370 AM")
        self.assertEqual(row["source"], refresh.QUAKES)

    def test_warriors_filter_excludes_preseason(self):
        game = {"gameId": "0022600001", "gameDateTimeUTC": "2027-02-16T03:00:00Z", "awayTeam": {"teamId": 1, "teamCity": "Indiana", "teamName": "Pacers"}, "homeTeam": {"teamId": 1610612744, "teamCity": "Golden State", "teamName": "Warriors"}}
        payload = {"leagueSchedule": {"gameDates": [{"games": [game, {**game, "gameId": "0012600001"}]}]}}
        rows = refresh.parse_warriors(payload)
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]["date"], "2027-02-15")
        self.assertEqual(rows[0]["source"], "https://www.nba.com/game/0022600001")

if __name__ == "__main__":
    unittest.main()
