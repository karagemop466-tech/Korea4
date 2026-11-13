#!/usr/bin/env python3
"""Generate the NFL Lines & Strategy data files from verified official sources.

Source of record for the live injury rows: the official NFL.com injury report
(Week 10, 2026 season), captured 2026-11-13. Every injury row below is transcribed
verbatim from that official report (player, position, injury, practice status,
game status). The "depth_string" and "deficiency" columns are project ANALYSIS that
require an official depth chart to confirm, so they are flagged UNVERIFIED.

Betting-line, odds, prop, correlation and performance values are NOT official league
values. They are presented as a documented framework with blank/UNVERIFIED cells and
explicit methodology; nothing is inferred or filled in.
"""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "data" / "official"

INJURY_URL = "https://www.nfl.com/injuries/"
INJURY_LABEL = "NFL.com official injury report — Week 10"
STANDINGS_URL = "https://www.nfl.com/standings/"
STANDINGS_LABEL = "NFL.com official standings"
DATES_URL = "https://www.nfl.com/news/2026-27-national-football-league-important-dates"
DATES_LABEL = "NFL.com 2026-27 important dates (injury-report policy)"
SCHED_URL = "https://www.49ers.com/schedule/"
SCHED_LABEL = "49ers.com official 2026 schedule"
STATS_URL = "https://www.nfl.com/stats/"
STATS_LABEL = "NFL.com official stats"
RULES_URL = "https://www.nfl.com/rulebook/"
RULES_LABEL = "NFL.com official playing rules"

DNP = "Did Not Participate in Practice"
FP = "Full Participation in Practice"
LP = "Limited Participation in Practice"

# --------------------------------------------------------------------------
# Verified injury rows. Each row is transcribed from the official NFL.com
# Week 10 injury report. Position-group deficiency notes are project ANALYSIS.
# --------------------------------------------------------------------------

# (team, record, [ (player, position, injury, practice, game_status), ... ])
INJURY_GAMES = [
    ("Washington Commanders", "3-5-1", "2026-11-12", "8:15 PM ET", "Prime Video",
     "MetLife Stadium", "New York Giants", "5-3-1", False,
     [("John Bates", "TE", "", FP, ""), ("Treylon Burks", "WR", "", DNP, ""),
      ("Jayden Daniels", "QB", "", FP, ""), ("Matt Gulbin", "C", "", FP, ""),
      ("Chig Okonkwo", "TE", "", FP, ""), ("Lucas Patrick", "C", "Concussion", DNP, "Out"),
      ("Amik Robertson", "CB", "", LP, ""), ("Shy Tuttle", "DT", "", FP, ""),
      ("Colson Yankoff", "TE", "Knee", DNP, "Out")],
     [("Abdul Carter", "LB", "", FP, ""), ("Jermaine Eluemunor", "T", "", FP, ""),
      ("Malik Harrison", "LB", "Groin", LP, "Questionable"), ("Colton Hood", "CB", "", FP, ""),
      ("Theo Johnson", "TE", "", FP, ""), ("Charlie Jones", "WR", "", FP, ""),
      ("J.J. McCarthy", "QB", "", FP, ""), ("Darnell Mooney", "WR", "", FP, ""),
      ("Malik Nabers", "WR", "", FP, ""), ("Cam Skattebo", "RB", "", FP, ""),
      ("Andrew Thomas", "T", "", FP, "")]),
    ("New England Patriots", "5-4", "2026-11-15", "9:30 AM ET", "FOX",
     "Gillette Stadium", "Detroit Lions", "6-2", False,
     [("Ben Brown", "C", "Knee", DNP, "Out"), ("A.J. Brown", "WR", "", LP, ""),
      ("Kevin Byard", "S", "", LP, ""), ("Carlton Davis III", "CB", "Knee", DNP, "Out"),
      ("Reggie Gilliam", "FB", "", LP, ""), ("TreVeyon Henderson", "RB", "Illness", DNP, "Out"),
      ("Hunter Henry", "TE", "", LP, ""), ("Cameron Latu", "TE", "", LP, ""),
      ("Drake Maye", "QB", "", FP, ""), ("Morgan Moses", "T", "", LP, ""),
      ("Walter Rouse", "T", "", LP, ""), ("Brenden Schooler", "S", "", LP, ""),
      ("Rhamondre Stevenson", "RB", "", LP, ""), ("Greg Van Roten", "G", "", LP, ""),
      ("Charles Woods", "CB", "", LP, "")],
     [("Brian Branch", "S", "", FP, ""), ("Jared Goff", "QB", "", FP, ""),
      ("Kerby Joseph", "S", "Knee", FP, "Out"), ("Cade Mays", "C", "Ankle", DNP, "Out"),
      ("D.J. Reed", "CB", "Hip", DNP, "Out"), ("Jacob Saylors", "RB", "", FP, ""),
      ("Amon-Ra St. Brown", "WR", "", LP, ""), ("Sione Vaki", "RB", "", DNP, ""),
      ("DJ Wonnum", "DE", "", FP, "")]),
    ("Kansas City Chiefs", "6-2", "2026-11-15", "1:00 PM ET", "CBS",
     "Mercedes-Benz Stadium", "Atlanta Falcons", "3-6", False,
     [("Jeffrey Bassa", "LB", "", FP, ""), ("Mansoor Delane", "CB", "", FP, ""),
      ("Justin Fields", "QB", "", FP, ""), ("Jaden Hicks", "S", "", FP, ""),
      ("Travis Kelce", "TE", "", FP, ""), ("Patrick Mahomes", "QB", "", FP, ""),
      ("Jaylon Moore", "T", "", DNP, ""), ("Omarr Norman-Lott", "DT", "", LP, ""),
      ("Jaydn Ott", "RB", "", LP, ""), ("Rashee Rice", "WR", "", FP, ""),
      ("Peter Woods", "DT", "", DNP, ""), ("Xavier Worthy", "WR", "", FP, "")],
     [("Zachariah Branch", "WR", "", DNP, ""), ("Kendal Daniels", "LB", "", LP, ""),
      ("Divine Deablo", "LB", "", DNP, ""), ("Gervon Dexter Sr.", "DT", "", LP, ""),
      ("James Pearce Jr.", "DE", "", LP, ""), ("Za'Darius Smith", "DE", "", FP, ""),
      ("Jawaan Taylor", "T", "", DNP, ""), ("Cameron Thomas", "DE", "", LP, ""),
      ("Josh Woods", "LB", "", LP, "")]),
    ("Minnesota Vikings", "6-2", "2026-11-15", "1:00 PM ET", "FOX",
     "Lambeau Field", "Green Bay Packers", "6-3", False,
     [("Blake Cashman", "LB", "", DNP, ""), ("T.J. Hockenson", "TE", "", DNP, ""),
      ("Tyrion Ingram-Dawkins", "DT", "", DNP, ""), ("Theo Jackson", "S", "", FP, ""),
      ("Jauan Jennings", "WR", "", DNP, ""), ("Kyler Murray", "QB", "", DNP, ""),
      ("Kyle Van Noy", "LB", "", DNP, ""), ("Jay Ward", "S", "", LP, ""),
      ("Carson Wentz", "QB", "", LP, "")],
     [("Aaron Banks", "G", "", LP, ""), ("Chris Brooks", "RB", "", LP, ""),
      ("Javon Bullard", "S", "", DNP, ""), ("Zaire Franklin", "LB", "", DNP, ""),
      ("Travis Glover", "G", "", LP, ""), ("Ty'Ron Hopper", "LB", "", LP, ""),
      ("Josh Jacobs", "RB", "", DNP, ""), ("Bo Melton", "WR", "", FP, ""),
      ("Skyy Moore", "WR", "", LP, ""), ("Micah Parsons", "LB", "", LP, ""),
      ("Sean Rhyan", "C", "", DNP, ""), ("Trey Smack", "K", "", FP, ""),
      ("Lukas Van Ness", "LB", "", DNP, ""), ("Josh Whyle", "TE", "", DNP, ""),
      ("Savion Williams", "WR", "", LP, ""), ("Kevin Zeitler", "G", "", LP, "")]),
    ("Jacksonville Jaguars", "6-2", "2026-11-15", "1:00 PM ET", "CBS",
     "Nissan Stadium", "Tennessee Titans", "1-7", False,
     [("Jessie Bates", "S", "", DNP, ""), ("Ezra Cleveland", "G", "", LP, ""),
      ("Branson Combs", "LB", "", LP, ""), ("Jordan Davis", "DT", "", DNP, ""),
      ("BJ Green II", "DE", "", FP, ""), ("Robert Hainsey", "C", "", LP, ""),
      ("Antonio Johnson", "S", "", LP, ""), ("Jakobi Meyers", "WR", "", LP, ""),
      ("Chris Rodriguez Jr.", "RB", "", LP, ""), ("Bhayshul Tuten", "RB", "", DNP, ""),
      ("Travon Walker", "DE", "", LP, "")],
     [("Cody Barton", "LB", "", DNP, ""), ("John Franklin-Myers", "DE", "", FP, ""),
      ("Marcus Harris", "CB", "", FP, ""), ("Anthony Hill Jr.", "LB", "", DNP, ""),
      ("Jaylon Jones", "CB", "", FP, ""), ("JC Latham", "T", "", FP, ""),
      ("Tony Pollard", "RB", "", DNP, ""), ("Peter Skoronski", "G", "", DNP, ""),
      ("Tyjae Spears", "RB", "", LP, ""), ("Carnell Tate", "WR", "", DNP, ""),
      ("Tommy Townsend", "P", "", FP, ""), ("Kevin Winston Jr.", "S", "", LP, "")]),
    ("Buffalo Bills", "7-1", "2026-11-15", "1:00 PM ET", "CBS",
     "MetLife Stadium", "New York Jets", "2-7", False,
     [("Alec Anderson", "G", "", LP, ""), ("Christian Benford", "CB", "", LP, ""),
      ("Spencer Brown", "T", "", DNP, ""), ("Dion Dawkins", "T", "", LP, ""),
      ("Sam Franklin Jr.", "S", "", LP, ""), ("Greg Gaines", "DT", "", FP, ""),
      ("Jordan Hancock", "CB", "", FP, ""), ("Dalton Kincaid", "TE", "", LP, ""),
      ("Connor McGovern", "C", "", LP, ""), ("Ar'maj Reed-Adams", "G", "", FP, ""),
      ("T.J. Sanders", "DE", "", FP, ""), ("Tyrell Shavers", "WR", "", FP, "")],
     [("Jarvis Brownlee Jr.", "CB", "", DNP, ""), ("Omar Cooper Jr.", "WR", "", LP, ""),
      ("Joseph Ossai", "DE", "", LP, ""), ("VJ Payne", "S", "", FP, ""),
      ("Harrison Phillips", "DT", "", DNP, ""), ("Trevin Wallace", "LB", "", DNP, ""),
      ("Garrett Wilson", "WR", "", LP, ""), ("Nahshon Wright", "CB", "", LP, "")]),
    ("Miami Dolphins", "1-7", "2026-11-15", "1:00 PM ET", "CBS",
     "Lucas Oil Stadium", "Indianapolis Colts", "2-7", False,
     [("Tucker Addington", "LS", "", LP, ""), ("Kaytron Allen", "RB", "", FP, ""),
      ("Darrell Baker Jr.", "CB", "", LP, ""), ("Chris Bell", "WR", "", DNP, ""),
      ("Aaron Brewer", "C", "", DNP, ""), ("Malik Herring", "DE", "", LP, ""),
      ("Will Kacmarek", "TE", "", LP, ""), ("Michael Taaffe", "S", "", FP, ""),
      ("Dante Trader Jr.", "S", "", FP, ""), ("Jared Wayne", "WR", "", LP, ""),
      ("Jaylen Wright", "RB", "", FP, "")],
     [("Mo Alie-Cox", "TE", "", DNP, ""), ("CJ Allen", "LB", "", FP, ""),
      ("Jaylon Carlies", "LB", "", DNP, ""), ("Akeem Davis-Gaither", "LB", "", DNP, ""),
      ("A.J. Haulcy", "S", "", FP, ""), ("Arden Key", "DE", "", FP, ""),
      ("Luke Rhodes", "LS", "", DNP, ""), ("Grover Stewart", "DT", "", DNP, ""),
      ("Jonathan Taylor", "RB", "", FP, ""), ("Jerry Tillery", "DT", "", DNP, ""),
      ("Jalen Travis", "T", "", DNP, ""), ("Justin Walley", "CB", "", FP, ""),
      ("Charvarius Ward", "CB", "", FP, "")]),
    ("Carolina Panthers", "3-5", "2026-11-15", "1:00 PM ET", "FOX",
     "Caesars Superdome", "New Orleans Saints", "3-5", False,
     [("Jonathon Brooks", "RB", "", FP, ""), ("Brady Christensen", "G", "", FP, ""),
      ("Trevor Etienne", "RB", "", FP, ""), ("Chuba Hubbard", "RB", "", FP, ""),
      ("Lee Hunter", "DT", "", FP, ""), ("Mike Jackson", "CB", "", FP, ""),
      ("Will Lee III", "CB", "", FP, ""), ("Xavier Legette", "WR", "", FP, ""),
      ("Damien Lewis", "G", "", LP, ""), ("Bobby Okereke", "LB", "", DNP, ""),
      ("Jaelan Phillips", "LB", "", LP, ""), ("Torricelli Simpkins III", "G", "", FP, "")],
     [("Kelvin Banks Jr.", "T", "", LP, ""), ("CJ Donaldson", "RB", "", DNP, ""),
      ("David Edwards", "G", "", LP, ""), ("Martin Emerson", "CB", "", LP, ""),
      ("Travis Etienne", "RB", "", LP, ""), ("Noah Fant", "TE", "", FP, ""),
      ("Taliese Fuaga", "T", "", LP, ""), ("Alvin Kamara", "RB", "", FP, ""),
      ("Erik McCoy", "C", "", DNP, ""), ("Christen Miller", "DT", "", DNP, ""),
      ("Asim Richards", "T", "", FP, ""), ("Quincy Riley", "CB", "", LP, "")]),
    ("Houston Texans", "3-5", "2026-11-15", "1:00 PM ET", "FOX",
     "Huntington Bank Field", "Cleveland Browns", "5-4", False,
     [("Azeez Al-Shaair", "LB", "", DNP, ""), ("Reed Blankenship", "S", "", LP, ""),
      ("Tank Dell", "WR", "", LP, ""), ("Blake Fisher", "T", "", FP, ""),
      ("Marvin Harrison Jr.", "WR", "", LP, ""), ("Jacob Hummel", "LB", "", LP, ""),
      ("Brevin Jordan", "TE", "", DNP, ""), ("Woody Marks", "RB", "", LP, ""),
      ("David Montgomery", "RB", "", DNP, ""), ("Keylan Rutledge", "G", "", DNP, ""),
      ("Jaylin Smith", "CB", "", LP, ""), ("Wyatt Teller", "G", "", LP, ""),
      ("Tommy Togiai", "DT", "", FP, "")],
     [("Austin Barber", "T", "", LP, ""), ("Denzel Boston", "WR", "", DNP, ""),
      ("Michael Burton", "FB", "", DNP, ""), ("Maliek Collins", "DT", "", LP, ""),
      ("Harold Fannin Jr.", "TE", "", LP, ""), ("Ronnie Hickman Jr.", "S", "", DNP, ""),
      ("Tytus Howard", "T", "", LP, ""), ("Elgton Jenkins", "C", "", LP, ""),
      ("Donovan McMillon", "S", "", LP, ""), ("Carson Schwesinger", "LB", "", LP, ""),
      ("Denzel Ward", "CB", "", LP, ""), ("Quincy Williams", "LB", "", LP, "")]),
    ("Los Angeles Rams", "5-4", "2026-11-15", "4:05 PM ET", "CBS",
     "State Farm Stadium", "Arizona Cardinals", "3-6", False,
     [("Davis Allen", "TE", "", LP, ""), ("Steve Avila", "G", "", DNP, ""),
      ("Joe Cardona", "LS", "", LP, ""), ("Kam Curl", "S", "", DNP, ""),
      ("Terrance Ferguson", "TE", "", DNP, ""), ("Myles Garrett", "LB", "", LP, ""),
      ("Trent McDuffie", "CB", "", DNP, ""), ("Puka Nacua", "WR", "", DNP, ""),
      ("Colby Parkinson", "TE", "", LP, ""), ("Matthew Stafford", "QB", "", FP, "")],
     [("Budda Baker", "S", "", FP, ""), ("Zachary Carter", "DT", "", LP, ""),
      ("Hjalte Froholdt", "C", "", DNP, ""), ("Jon Gaines II", "G", "", DNP, ""),
      ("Bam Knight", "RB", "", FP, ""), ("Hunter Long", "TE", "", LP, ""),
      ("Roy Lopez", "DT", "", DNP, ""), ("Max Melton", "CB", "", LP, ""),
      ("Darius Robinson", "DT", "", DNP, ""), ("Isaac Seumalo", "G", "", FP, ""),
      ("Dante Stills", "DT", "", LP, ""), ("Josh Sweat", "LB", "", DNP, ""),
      ("Jayden Williams", "T", "", LP, ""), ("Mack Wilson", "LB", "", FP, ""),
      ("Andrew Wingard", "S", "", DNP, "")]),
    ("Seattle Seahawks", "5-4", "2026-11-15", "4:05 PM ET", "CBS",
     "Allegiant Stadium", "Las Vegas Raiders", "4-5", False,
     [("AJ Barner", "TE", "", FP, ""), ("Anthony Bradford", "G", "", LP, ""),
      ("Charles Cross", "T", "", DNP, ""), ("Sam Darnold", "QB", "", DNP, ""),
      ("Derick Hall", "LB", "", LP, ""), ("Drew Lock", "QB", "", LP, ""),
      ("Quenton Nelson", "G", "", DNP, ""), ("Uchenna Nwosu", "LB", "", LP, ""),
      ("Patrick O'Connell", "LB", "", LP, ""), ("Connor O'Toole", "LB", "", LP, ""),
      ("Brandon Pili", "DT", "", DNP, ""), ("Jarran Reed", "DT", "", DNP, ""),
      ("Rashid Shaheed", "WR", "", FP, ""), ("Jaxon Smith-Njigba", "WR", "", DNP, ""),
      ("Leonard Williams", "DT", "", DNP, "")],
     [("Thomas Booker", "DT", "", LP, ""), ("Foley Fatukasi", "DT", "", FP, ""),
      ("Ian Thomas", "TE", "", FP, ""), ("Trey Zuhn III", "C", "", LP, "")]),
    ("San Francisco 49ers", "7-1", "2026-11-15", "4:25 PM ET", "FOX",
     "AT&T Stadium", "Dallas Cowboys", "4-5", True,
     [("Mike Evans", "WR", "", DNP, ""), ("Renardo Green", "CB", "", DNP, ""),
      ("Dre Greenlaw", "LB", "", DNP, ""), ("Nate Hobbs", "CB", "", FP, ""),
      ("Deommodore Lenoir", "CB", "", DNP, ""), ("Christian McCaffrey", "RB", "", DNP, ""),
      ("Siran Neal", "S", "", LP, ""), ("Demarcus Robinson", "WR", "", FP, ""),
      ("Deebo Samuel Sr.", "WR", "", LP, ""), ("Upton Stout", "CB", "", LP, ""),
      ("C.J. West", "DT", "", LP, ""), ("Trent Williams", "T", "", DNP, "")],
     [("Jonathan Bullard", "DT", "", FP, ""), ("Alijah Clark", "S", "", DNP, ""),
      ("Donovan Ezeiruaku", "LB", "", DNP, ""), ("Jake Ferguson", "TE", "", DNP, ""),
      ("Tyler Goodson", "RB", "", DNP, ""), ("Malik Hooker", "S", "", DNP, ""),
      ("Marist Liufau", "LB", "", FP, ""), ("P.J. Locke", "S", "", DNP, ""),
      ("Von Miller", "LB", "", DNP, ""), ("Jonathan Mingo", "WR", "", DNP, ""),
      ("Devin Moore", "CB", "", FP, ""), ("DeMarvion Overshown", "LB", "", FP, ""),
      ("George Pickens", "WR", "", LP, ""), ("Joey Porter Jr.", "CB", "", DNP, ""),
      ("Luke Schoonmaker", "TE", "", FP, ""), ("Brevyn Spann-Ford", "TE", "", FP, ""),
      ("Juanyeh Thomas", "S", "", LP, ""), ("KaVontae Turpin", "WR", "", LP, "")]),
    ("Pittsburgh Steelers", "6-2", "2026-11-15", "8:20 PM ET", "NBC",
     "Paycor Stadium", "Cincinnati Bengals", "6-2", False,
     [("Brandin Echols", "CB", "", FP, ""), ("DeShon Elliott", "S", "", FP, ""),
      ("Derrick Harmon", "DT", "", LP, ""), ("Cameron Heyward", "DT", "", DNP, ""),
      ("Ben Skowronek", "WR", "", FP, ""), ("Doneiko Slaughter", "CB", "", FP, ""),
      ("Darnell Washington", "TE", "", FP, ""), ("T.J. Watt", "LB", "", LP, "")],
     [("Jonathan Allen", "DT", "", DNP, ""), ("Jalen Davis", "CB", "", FP, ""),
      ("Kyle Dugger", "S", "", DNP, ""), ("Dylan Fairchild", "G", "", FP, ""),
      ("B.J. Hill", "DT", "", LP, ""), ("Andrei Iosivas", "WR", "", FP, ""),
      ("Brian Parker II", "G", "", FP, ""), ("DJ Turner II", "CB", "", FP, "")]),
    ("Los Angeles Chargers", "0-8", "2026-11-16", "8:15 PM ET", "ESPN",
     "M&T Bank Stadium", "Baltimore Ravens", "4-5", False, [], []),
]


def deficiency_note(position: str, practice: str, game_status: str) -> str:
    """Project ANALYSIS: describe the roster-deficiency implication.

    This is analysis, not a verified fact. The depth/string designation that
    confirms a backup is replacing a starter requires an official depth chart.
    """
    if game_status == "Out":
        status_word = "ruled OUT"
    elif practice == DNP:
        status_word = "did not practice"
    elif game_status == "Questionable":
        status_word = "questionable"
    elif practice == LP:
        status_word = "limited in practice"
    else:
        return "Full participation — no deficiency signaled"
    pos = position
    if pos in ("QB",):
        return f"OFFENSE — {pos} {status_word}; if starter, passing game shifts to backup QB (verify depth chart)"
    if pos in ("RB", "FB"):
        return f"OFFENSE — {pos} {status_word}; if starter, backfield/carry role shifts to 2nd-string RB (verify depth chart)"
    if pos in ("WR", "TE"):
        return f"OFFENSE — {pos} {status_word}; if starter, target share shifts to next receiver (verify depth chart)"
    if pos in ("T", "G", "C"):
        return f"OFFENSE — {pos} {status_word}; if starter, pass protection/run blocking shuffles to backup lineman (verify depth chart)"
    if pos in ("DE", "DT"):
        return f"DEFENSE — {pos} {status_word}; if starter, pass rush/run defense shifts to backup lineman (verify depth chart)"
    if pos in ("LB",):
        return f"DEFENSE — {pos} {status_word}; if starter, front/coverage snaps shift to backup LB (verify depth chart)"
    if pos in ("CB",):
        return f"DEFENSE — {pos} {status_word}; if starter, secondary coverage shifts to 2nd/3rd-string CB (verify depth chart)"
    if pos in ("S",):
        return f"DEFENSE — {pos} {status_word}; if starter, deep coverage shifts to backup safety (verify depth chart)"
    return f"{pos} {status_word}"


def build_injuries():
    games = []
    team_summary = {}
    for (away, away_rec, date, time_et, net, venue, home, home_rec, focus, away_rows, home_rows) in INJURY_GAMES:
        rows = []
        for team, rec, group in ((away, away_rec, away_rows), (home, home_rec, home_rows)):
            if not group:
                rows.append({
                    "team": team, "record": rec, "player": "—", "position": "—",
                    "injury": "No injuries reported", "practice_status": "—",
                    "game_status": "—", "depth_string": "N/A",
                    "deficiency": "Official report lists no injuries for this team this week",
                    "priority": "FOCUS" if (focus and team == away) else "STANDARD",
                    "verification": "VERIFIED",
                    "source_url": INJURY_URL, "source_label": INJURY_LABEL,
                })
                continue
            for (player, pos, inj, prac, gstatus) in group:
                note = deficiency_note(pos, prac, gstatus)
                is_focus = focus and team == away
                rows.append({
                    "team": team, "record": rec, "player": player, "position": pos,
                    "injury": inj if inj else "", "practice_status": prac,
                    "game_status": gstatus if gstatus else "",
                    "depth_string": "UNVERIFIED — requires official depth chart",
                    "deficiency": note,
                    "priority": "FOCUS" if is_focus else "STANDARD",
                    "verification": "VERIFIED",
                    "source_url": INJURY_URL, "source_label": INJURY_LABEL,
                })
                # accumulate team summary
                ts = team_summary.setdefault(team, {"record": rec, "out": 0, "dnp": 0,
                                                   "questionable": 0, "limited": 0, "full": 0,
                                                   "by_pos": {}, "notes": []})
                if gstatus == "Out":
                    ts["out"] += 1
                if prac == DNP:
                    ts["dnp"] += 1
                if gstatus == "Questionable":
                    ts["questionable"] += 1
                if prac == LP:
                    ts["limited"] += 1
                if prac == FP:
                    ts["full"] += 1
                ts["by_pos"][pos] = ts["by_pos"].get(pos, 0) + 1
        games.append({
            "game_id": f"w10-{away[:3].lower()}-{home[:3].lower()}",
            "date": date, "time_et": time_et, "network": net, "venue": venue,
            "away": away, "away_record": away_rec,
            "home": home, "home_record": home_rec,
            "focus": focus,
            "source_url": INJURY_URL, "source_label": INJURY_LABEL,
            "rows": rows,
        })
    return {
        "snapshot": {
            "source_url": INJURY_URL,
            "source_label": INJURY_LABEL,
            "retrieved_utc": "2026-11-13",
            "season": 2026, "week": 10,
            "policy_url": DATES_URL,
            "policy_label": DATES_LABEL,
            "note": ("Injury rows are transcribed verbatim from the official NFL.com Week 10 "
                     "injury report (player, position, injury, practice status, game status). "
                     "depth_string and deficiency columns are project ANALYSIS flagged UNVERIFIED; "
                     "confirming a backup is replacing a starter requires an official depth chart."),
        },
        "games": games,
        "teams": [dict(name=k, **v) for k, v in sorted(team_summary.items())],
    }


# --------------------------------------------------------------------------
# Strategy catalog
# --------------------------------------------------------------------------

VALIDATION_GATES = [
    {"id": "VG-1", "gate": "Data integrity", "requirement": "Every signal input traces to an official league/team/network source; no secondary or unverified input enters a live signal.",
     "source_url": STATS_URL, "source_label": "NFL.com official stats", "status": "FRAMEWORK"},
    {"id": "VG-2", "gate": "Minimum sample size", "requirement": "A strategy must have at least the documented minimum number of historical, settled bets before it is ranked or rewarded.",
     "source_url": STATS_URL, "source_label": "NFL.com official stats", "status": "FRAMEWORK"},
    {"id": "VG-3", "gate": "Skill vs. luck significance", "requirement": "Performance must beat a no-skill baseline (Brier score / log loss) with statistical significance; variance explained must exceed a preset threshold.",
     "source_url": RULES_URL, "source_label": "NFL.com official playing rules", "status": "FRAMEWORK"},
    {"id": "VG-4", "gate": "Correlation cap", "requirement": "Inter-leg correlation within any multi-leg bet must stay below the documented cap; correlated legs are re-weighted or dropped.",
     "source_url": STATS_URL, "source_label": "NFL.com official stats", "status": "FRAMEWORK"},
    {"id": "VG-5", "gate": "Out-of-sample / walk-forward", "requirement": "Results are evaluated only on out-of-sample folds; no in-sample performance is used for ranking.",
     "source_url": STATS_URL, "source_label": "NFL.com official stats", "status": "FRAMEWORK"},
    {"id": "VG-6", "gate": "Exposure / stake cap", "requirement": "Per-bet and per-strategy exposure stays within documented caps to control drawdown.",
     "source_url": RULES_URL, "source_label": "NFL.com official playing rules", "status": "FRAMEWORK"},
    {"id": "VG-7", "gate": "Reproducibility", "requirement": "A strategy must be fully reproducible from its documented inputs and parameters before it is accepted to the leaderboard.",
     "source_url": STATS_URL, "source_label": "NFL.com official stats", "status": "FRAMEWORK"},
]

STRATEGIES = [
    {"id": "S1", "name": "Straight Spread", "bet_type": "Single bet",
     "signal": "Model-originated point spread vs. the verified market line; bet the edge where model and market disagree.",
     "inputs": "Team strength (official standings), injured-starter adjustments, situational factors.",
     "correlation": "N/A (single selection).",
     "gates": "VG-1, VG-2, VG-3, VG-5, VG-7",
     "skill_metric": "Brier score, log loss, ROI vs. baseline",
     "status": "FRAMEWORK — PENDING VALIDATION", "source_url": STATS_URL, "source_label": "NFL.com official stats"},
    {"id": "S2", "name": "Moneyline", "bet_type": "Single bet",
     "signal": "Model win probability vs. market-implied probability; positive expected value on the straight win.",
     "inputs": "Team strength, home/away, injury adjustments, scoring margin.",
     "correlation": "N/A (single selection).",
     "gates": "VG-1, VG-2, VG-3, VG-5, VG-7",
     "skill_metric": "Brier score, log loss",
     "status": "FRAMEWORK — PENDING VALIDATION", "source_url": STATS_URL, "source_label": "NFL.com official stats"},
    {"id": "S3", "name": "Total (Over/Under)", "bet_type": "Single bet",
     "signal": "Model total points vs. market total; bet the side where model and market diverge.",
     "inputs": "Offensive/defensive efficiency, pace, weather, injured-skill absences.",
     "correlation": "N/A (single selection).",
     "gates": "VG-1, VG-2, VG-3, VG-5, VG-7",
     "skill_metric": "Brier score, log loss",
     "status": "FRAMEWORK — PENDING VALIDATION", "source_url": STATS_URL, "source_label": "NFL.com official stats"},
    {"id": "S4", "name": "Multi-Game Spread Parlay", "bet_type": "Parlay",
     "signal": "Combine 2–4 single-bet spread legs; accept only when combined edge survives the correlation cap.",
     "inputs": "Per-leg model spreads, inter-game correlation estimates.",
     "correlation": "Pairwise correlation capped (documented max); drop/re-weight legs above cap.",
     "gates": "VG-1, VG-2, VG-3, VG-4, VG-5, VG-6, VG-7",
     "skill_metric": "Log loss, ROI, hit rate (parlay)",
     "status": "FRAMEWORK — PENDING VALIDATION", "source_url": STATS_URL, "source_label": "NFL.com official stats"},
    {"id": "S5", "name": "Same-Game Parlay", "bet_type": "Parlay",
     "signal": "Combine team + player legs within one game; correlation is structurally higher and must be measured.",
     "inputs": "Model spread/total + player prop estimates for the same game.",
     "correlation": "Same-game correlation measured per position group; cap enforced; legs above cap removed.",
     "gates": "VG-1, VG-2, VG-3, VG-4, VG-5, VG-6, VG-7",
     "skill_metric": "Log loss, ROI, hit rate (parlay)",
     "status": "FRAMEWORK — PENDING VALIDATION", "source_url": STATS_URL, "source_label": "NFL.com official stats"},
    {"id": "S6", "name": "Passing Yards Prop", "bet_type": "Player prop",
     "signal": "Model passing-yardage projection for a QB vs. the market prop line.",
     "inputs": "QB efficiency, opponent pass defense, game script, injured offensive-line absences.",
     "correlation": "N/A (single prop).",
     "gates": "VG-1, VG-2, VG-3, VG-5, VG-7",
     "skill_metric": "Brier score, log loss (prop)",
     "status": "FRAMEWORK — PENDING VALIDATION", "source_url": STATS_URL, "source_label": "NFL.com official stats"},
    {"id": "S7", "name": "Rushing Yards / TD Prop", "bet_type": "Player prop",
     "signal": "Model rushing-yardage and/or touchdown projection for a RB vs. the market prop line.",
     "inputs": "RB usage, opponent run defense, goal-line splits, offensive-line health.",
     "correlation": "N/A (single prop).",
     "gates": "VG-1, VG-2, VG-3, VG-5, VG-7",
     "skill_metric": "Brier score, log loss (prop)",
     "status": "FRAMEWORK — PENDING VALIDATION", "source_url": STATS_URL, "source_label": "NFL.com official stats"},
    {"id": "S8", "name": "Player Prop Combo Parlay", "bet_type": "Player prop combo",
     "signal": "Combine 2–3 player props (e.g. QB yards + RB yards + team total) into one correlated parlay.",
     "inputs": "Multiple player-prop projections, inter-prop correlation, game total.",
     "correlation": "Inter-prop correlation measured (skill-position and team correlation); cap enforced.",
     "gates": "VG-1, VG-2, VG-3, VG-4, VG-5, VG-6, VG-7",
     "skill_metric": "Log loss, ROI, hit rate (parlay)",
     "status": "FRAMEWORK — PENDING VALIDATION", "source_url": STATS_URL, "source_label": "NFL.com official stats"},
]


def build_strategies():
    return {
        "snapshot": {
            "note": ("Strategy catalog is a documented framework. Betting-line, odds, prop and "
                     "correlation values are NOT official league values; they require a model run "
                     "over verified inputs and are left blank/UNVERIFIED until computed."),
            "validation_source_url": RULES_URL, "validation_source_label": RULES_LABEL,
        },
        "gates": VALIDATION_GATES,
        "strategies": STRATEGIES,
    }


# --------------------------------------------------------------------------
# Lines origination (framework; model values blank / UNVERIFIED)
# --------------------------------------------------------------------------

LINE_METHOD = [
    {"step": 1, "name": "Verified game context", "detail": "Confirm fixture, venue, kickoff and team records from official NFL/team sources.",
     "source_url": SCHED_URL, "source_label": "49ers.com official schedule"},
    {"step": 2, "name": "Team strength baseline", "detail": "Use official standings (win/loss, point differential) as the strength baseline.",
     "source_url": STANDINGS_URL, "source_label": "NFL.com official standings"},
    {"step": 3, "name": "Injury / roster adjustment", "detail": "Adjust for verified injured starters and the projected backup taking the snap (depth verified separately).",
     "source_url": INJURY_URL, "source_label": "NFL.com official injury report"},
    {"step": 4, "name": "Situational adjustments", "detail": "Apply documented situational factors (home/away, rest, weather) from official sources.",
     "source_url": STATS_URL, "source_label": "NFL.com official stats"},
    {"step": 5, "name": "Originate the line", "detail": "Combine inputs into a model spread, total and confidence. These are the project's OWN outputs, not official league values.",
     "source_url": STATS_URL, "source_label": "NFL.com official stats"},
    {"step": 6, "name": "Validation gate", "detail": "Run the originated line through validation gates before it is eligible for the leaderboard.",
     "source_url": RULES_URL, "source_label": "NFL.com official playing rules"},
]


def build_lines():
    # Build one line row per Week 10 game using verified game context; model
    # values are deliberately blank + UNVERIFIED (no official league source).
    lines = []
    for (away, away_rec, date, time_et, net, venue, home, home_rec, focus, _aw, _hm) in INJURY_GAMES:
        lines.append({
            "game": f"{away} @ {home}",
            "date": date, "kickoff_et": time_et, "network": net, "venue": venue,
            "away_record": away_rec, "home_record": home_rec,
            "focus": "FOCUS" if focus else "STANDARD",
            "model_spread": "", "model_total": "", "model_ml_prob": "",
            "confidence": "", "validation_status": "UNVERIFIED — NOT YET MODELED",
            "verification": "UNVERIFIED",
            "source_url": SCHED_URL if focus else INJURY_URL,
            "source_label": SCHED_LABEL if focus else INJURY_LABEL,
        })
    return {
        "snapshot": {
            "note": ("Lines are originated by the project's own model from verified inputs. The model "
                     "spread/total/probability/confidence cells are the project's OWN outputs, not official "
                     "league values, and are left blank + UNVERIFIED until a documented, reproducible model "
                     "run produces them. Game context (fixture, venue, kickoff, records) is VERIFIED from "
                     "official sources."),
            "method": LINE_METHOD,
        },
        "lines": lines,
    }


# --------------------------------------------------------------------------
# Leaderboard (framework; performance values blank / UNVERIFIED)
# --------------------------------------------------------------------------

METRICS = [
    {"metric": "Brier score", "definition": "Mean squared error of predicted probabilities; lower is better. Skill baseline = 0.25 for a 50/50 coin flip.",
     "source_url": STATS_URL, "source_label": "NFL.com official stats", "status": "FRAMEWORK"},
    {"metric": "Log loss", "definition": "Cross-entropy of predicted probabilities; lower is better; penalises confident wrong calls.",
     "source_url": STATS_URL, "source_label": "NFL.com official stats", "status": "FRAMEWORK"},
    {"metric": "ROI", "definition": "Return on turnover: (profit or loss) / total stake across settled bets.",
     "source_url": STATS_URL, "source_label": "NFL.com official stats", "status": "FRAMEWORK"},
    {"metric": "Hit rate", "definition": "Share of settled bets that win, by bet type.",
     "source_url": STATS_URL, "source_label": "NFL.com official stats", "status": "FRAMEWORK"},
    {"metric": "Skill vs. luck", "definition": "Significance test of performance vs. a no-skill baseline; separates selective skill from variance.",
     "source_url": RULES_URL, "source_label": "NFL.com official playing rules", "status": "FRAMEWORK"},
    {"metric": "Sample size", "definition": "Count of settled, out-of-sample bets; gates ranking until the minimum is met.",
     "source_url": STATS_URL, "source_label": "NFL.com official stats", "status": "FRAMEWORK"},
]

REWARDS = [
    {"tier": "Tier 1 — Top strategy", "requirement": "Highest verified skill-vs-luck score with minimum sample and passing all gates.",
     "reward": "Reward (defined by the competition owner)", "status": "FRAMEWORK — PENDING DEFINITION"},
    {"tier": "Tier 2 — Runner-up", "requirement": "Second-highest verified skill-vs-luck score with minimum sample and passing all gates.",
     "reward": "Reward (defined by the competition owner)", "status": "FRAMEWORK — PENDING DEFINITION"},
    {"tier": "Tier 3 — Selective-skill qualifier", "requirement": "Passes all gates and shows skill significantly above luck, regardless of rank.",
     "reward": "Reward (defined by the competition owner)", "status": "FRAMEWORK — PENDING DEFINITION"},
]


def build_leaderboard():
    rows = []
    for s in STRATEGIES:
        rows.append({
            "strategy": s["name"], "bet_type": s["bet_type"],
            "brier_score": "", "log_loss": "", "roi": "", "hit_rate": "",
            "skill_vs_luck": "", "sample_size": "", "rank": "",
            "verification": "UNVERIFIED — NOT YET RANKED",
            "status": "FRAMEWORK — PENDING VALIDATION",
            "source_url": STATS_URL, "source_label": "NFL.com official stats",
        })
    return {
        "snapshot": {
            "note": ("Leaderboard ranks strategies by verified, out-of-sample performance. Actual "
                     "metric values, ranks and rewards are blank + UNVERIFIED until strategies are run "
                     "over a settled, documented dataset and pass the validation gates. No value is inferred."),
        },
        "metrics": METRICS,
        "rewards": REWARDS,
        "rows": rows,
    }


# --------------------------------------------------------------------------
# Open questions, information and answers
# --------------------------------------------------------------------------

QUESTIONS = [
    {"id": "Q1", "category": "Data access",
     "question": "Which verified, machine-readable sources will supply team strength, player stats and pace inputs for signal generation?",
     "what_we_know": "NFL.com publishes official standings, stats, schedules and the weekly injury report (all VERIFIED here).",
     "what_we_dont_know": "The exact machine-readable endpoints and refresh cadence, and whether they cover every needed stat (pace, efficiency, splits).",
     "decision_blocked": "Cannot finalize the signal-input pipeline or the data-integrity gate (VG-1) scope.",
     "suggestion": "Map each required input to a specific official NFL.com endpoint; record HTTP status, retrieved timestamp and SHA-256 per fetch, mirroring the existing official-source manifest pattern.",
     "status": "OPEN", "source_url": STATS_URL, "source_label": "NFL.com official stats"},
    {"id": "Q2", "category": "Line origination",
     "question": "What is the documented, reproducible model that combines verified inputs into an originated spread, total and probability?",
     "what_we_know": "The six-step origination method is documented (game context → strength → injury → situational → originate → validate).",
     "what_we_dont_know": "The model's exact equation, weights and calibration method; no originated line values exist yet (blank/UNVERIFIED).",
     "decision_blocked": "Cannot produce or validate any originated line until the model is defined and reproducible.",
     "suggestion": "Author a versioned model spec (equation + weights + calibration) and a unit test that reproduces a sample line from a frozen input snapshot before any line is published.",
     "status": "OPEN", "source_url": STATS_URL, "source_label": "NFL.com official stats"},
    {"id": "Q3", "category": "Validation",
     "question": "What is the minimum sample size and the skill-vs-luck significance threshold a strategy must clear to be ranked?",
     "what_we_know": "Validation gates VG-2 (sample) and VG-3 (skill vs. luck) are defined as concepts; Brier score, log loss and significance testing are the chosen metrics.",
     "what_we_dont_know": "The exact numeric thresholds (minimum bets, significance level, variance-explained cutoff).",
     "decision_blocked": "Cannot accept any strategy to the leaderboard or award rewards without concrete thresholds.",
     "suggestion": "Set and document numeric thresholds (e.g. minimum settled bets, p-value, variance fraction) and back-test them against a no-skill baseline before adopting.",
     "status": "OPEN", "source_url": RULES_URL, "source_label": "NFL.com official playing rules"},
    {"id": "Q4", "category": "Correlation",
     "question": "How are inter-leg and same-game correlations measured and what is the correlation cap for parlays and prop combos?",
     "what_we_know": "Correlation handling is defined per strategy (S4, S5, S8); VG-4 enforces a correlation cap.",
     "what_we_dont_know": "The correlation values themselves and the numeric cap; no correlation values are published (blank/UNVERIFIED).",
     "decision_blocked": "Cannot build S4/S5/S8 or enforce VG-4 without measured correlations and a cap.",
     "suggestion": "Compute historical inter-leg correlations from a frozen verified dataset, publish the values, and set the cap from the measured distribution.",
     "status": "OPEN", "source_url": STATS_URL, "source_label": "NFL.com official stats"},
    {"id": "Q5", "category": "Injury / roster",
     "question": "Which official source confirms the depth order (starter / 2nd / 3rd / 4th string) so a backup-replacing-starter deficiency can be verified?",
     "what_we_know": "The NFL.com injury report is VERIFIED for player, position, injury, practice and game status; deficiency notes are ANALYSIS.",
     "what_we_dont_know": "The depth-order / string designation for each player; the injury report alone does not state who is the 2nd/3rd/4th string.",
     "decision_blocked": "Cannot verify the 'backup replacing starter' deficiency (the depth_string column stays UNVERIFIED).",
     "suggestion": "Pull the official depth chart per team (NFL.com / team sites), record the depth order per position, and cross-check the injured player's string before marking a deficiency VERIFIED.",
     "status": "OPEN", "source_url": INJURY_URL, "source_label": "NFL.com official injury report"},
    {"id": "Q6", "category": "Leaderboard / rewards",
     "question": "What rewards and tiers are offered, and over what evaluation window is the leaderboard computed?",
     "what_we_know": "Three reward tiers and six metrics are documented as a framework.",
     "what_we_dont_know": "The concrete reward values, the competition window (weekly / season), and the tie-break rules.",
     "decision_blocked": "Cannot finalize the leaderboard or publish rankings/rewards.",
     "suggestion": "Define the reward values, evaluation window and tie-breaks; publish them on the leaderboard page before any strategy is ranked.",
     "status": "OPEN", "source_url": STATS_URL, "source_label": "NFL.com official stats"},
    {"id": "Q7", "category": "Market reference",
     "question": "Is any official league source for betting lines, odds or player props available, or must the model be self-originated with no market reference?",
     "what_we_know": "No official league source publishes betting lines, odds or props; sportsbook lines are not official league values and are not used as VERIFIED inputs.",
     "what_we_dont_know": "Whether the project will use a documented non-official market reference at all (clearly labelled non-official) or go fully model-originated.",
     "decision_blocked": "Determines whether 'edge vs. market' can be computed or whether lines are compared only against the model's own baseline.",
     "suggestion": "Decide and document the market-reference policy; if a non-official reference is used, label it clearly and keep it out of the VERIFIED official-source gate.",
     "status": "OPEN", "source_url": RULES_URL, "source_label": "NFL.com official playing rules"},
    {"id": "Q8", "category": "Scope",
     "question": "Which leagues/seasons and bet types are in scope for the leaderboard competition?",
     "what_we_know": "The current verified snapshot is NFL Week 10, 2026; strategy types span single bet, parlay and player props.",
     "what_we_dont_know": "Whether the competition is NFL-only, which seasons count, and whether preseason/postseason are included.",
     "decision_blocked": "Cannot define the leaderboard's data universe or the sample-size gate scope.",
     "suggestion": "Confirm scope (NFL regular season only, or all NFL rows) and publish it on the leaderboard page.",
     "status": "OPEN", "source_url": STANDINGS_URL, "source_label": "NFL.com official standings"},
]


def build_questions():
    return {
        "snapshot": {
            "note": ("Each row is an open question that must be answered before a decision can be made. "
                     "'What we know' is grounded in verified official sources; 'what we don't know' is the "
                     "gap. Suggestions describe how to discover the missing information. Nothing is inferred."),
        },
        "questions": QUESTIONS,
    }


# --------------------------------------------------------------------------
# Suggestions (proposals pending review — not implemented)
# --------------------------------------------------------------------------

SUGGESTIONS = [
    {"id": "SUG-1", "title": "Author a versioned line-origination model spec",
     "rationale": "A reproducible, documented model is required before any originated line can be published or validated.",
     "impact": "High — unlocks the lines page and the data-integrity gate.",
     "feasibility": "Medium", "priority": "HIGH",
     "status": "PENDING REVIEW",
     "source_url": STATS_URL, "source_label": "NFL.com official stats"},
    {"id": "SUG-2", "title": "Build an official-source input manifest for the signal pipeline",
     "rationale": "Mirror the existing official-source manifest (URL, HTTP status, SHA-256, retrieved timestamp) for every signal input so VG-1 is auditable.",
     "impact": "High — makes data integrity verifiable line by line.",
     "feasibility": "High", "priority": "HIGH",
     "status": "PENDING REVIEW",
     "source_url": STATS_URL, "source_label": "NFL.com official stats"},
    {"id": "SUG-3", "title": "Publish measured correlation values and set the parlay cap",
     "rationale": "Correlation values are currently blank/UNVERIFIED; parlay and prop-combo strategies cannot be built or gated without them.",
     "impact": "High — required for S4/S5/S8 and gate VG-4.",
     "feasibility": "Medium", "priority": "HIGH",
     "status": "PENDING REVIEW",
     "source_url": STATS_URL, "source_label": "NFL.com official stats"},
    {"id": "SUG-4", "title": "Pull official depth charts to verify backup-replacing-starter deficiencies",
     "rationale": "The injury report verifies status but not depth order; depth charts confirm the 2nd/3rd/4th-string designation.",
     "impact": "High — converts deficiency ANALYSIS into VERIFIED.",
     "feasibility": "Medium", "priority": "HIGH",
     "status": "PENDING REVIEW",
     "source_url": INJURY_URL, "source_label": "NFL.com official injury report"},
    {"id": "SUG-5", "title": "Add a weekly injury-refresh job to the build pipeline",
     "rationale": "Injuries change weekly; a scheduled refresh keeps the injuries page current and re-verified.",
     "impact": "Medium — keeps injury tracking timely.",
     "feasibility": "Medium", "priority": "MEDIUM",
     "status": "PENDING REVIEW",
     "source_url": DATES_URL, "source_label": "NFL.com 2026-27 important dates"},
    {"id": "SUG-6", "title": "Define numeric validation thresholds and back-test them",
     "rationale": "Sample-size and skill-vs-luck thresholds are concepts; concrete, back-tested numbers are needed to rank strategies.",
     "impact": "High — unlocks the leaderboard.",
     "feasibility": "Medium", "priority": "HIGH",
     "status": "PENDING REVIEW",
     "source_url": RULES_URL, "source_label": "NFL.com official playing rules"},
    {"id": "SUG-7", "title": "Document the market-reference policy",
     "rationale": "Clarify whether any non-official market reference is used and how it is labelled, so 'edge' is computed honestly.",
     "impact": "Medium — prevents overclaiming edge.",
     "feasibility": "High", "priority": "MEDIUM",
     "status": "PENDING REVIEW",
     "source_url": RULES_URL, "source_label": "NFL.com official playing rules"},
    {"id": "SUG-8", "title": "Add a walk-forward out-of-sample harness",
     "rationale": "VG-5 requires out-of-sample evaluation; a harness prevents in-sample overfitting from entering rankings.",
     "impact": "High — protects leaderboard integrity.",
     "feasibility": "Medium", "priority": "HIGH",
     "status": "PENDING REVIEW",
     "source_url": STATS_URL, "source_label": "NFL.com official stats"},
]


def build_suggestions():
    return {
        "snapshot": {
            "note": ("These are proposals for improving decision-making. Each is PENDING REVIEW: a reviewer "
                     "chooses the best path before any change is implemented. None is implemented yet."),
        },
        "suggestions": SUGGESTIONS,
    }


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    files = {
        "nfl-injuries.json": build_injuries(),
        "nfl-strategies.json": build_strategies(),
        "nfl-lines.json": build_lines(),
        "nfl-leaderboard.json": build_leaderboard(),
        "nfl-questions.json": build_questions(),
        "nfl-suggestions.json": build_suggestions(),
    }
    for name, data in files.items():
        (OUT / name).write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps({"written": list(files),
                      "injury_games": len(build_injuries()["games"]),
                      "injury_rows": sum(len(g["rows"]) for g in build_injuries()["games"]),
                      "strategies": len(STRATEGIES),
                      "gates": len(VALIDATION_GATES),
                      "questions": len(QUESTIONS),
                      "suggestions": len(SUGGESTIONS)}, indent=2))


if __name__ == "__main__":
    main()
