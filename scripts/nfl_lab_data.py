#!/usr/bin/env python3
"""Single source of truth for the NFL Lab (decision-support) section.

Every row carries an explicit `source_url` and a `source_kind`:
  * "official"  — league / club / network / rules publisher page (fetch-verified
                  in this session on 2026-11-13 unless the row says otherwise);
  * "repo"      — a file in this repository (audit rows about our own code/data);
  * "none"      — no source exists yet; the row is a design artifact or an open
                  question and MUST render as UNVERIFIED.

Nothing is inferred. A value that was not read off a source is stored as "" and
the row says so. `scripts/verify_nfl_lab.py` re-checks these rules on every
page we publish, so an unsourced value cannot reach the site unnoticed.
"""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "data/nfl-lab"

CAPTURE_DATE = "2026-11-13"          # session date, UTC
CAPTURE_LABEL = "2026-11-13 UTC"

# --------------------------------------------------------------------------
# 1. Source registry — every URL used by any row on this section's pages.
# --------------------------------------------------------------------------
SOURCES = [
    {
        "id": "S-01", "publisher": "NFL.com",
        "title": "Injuries — Week 10 of the 2026 season (official injury report)",
        "url": "https://www.nfl.com/injuries/",
        "what": "Per-club injury rows: player, position, practice status (Did Not Participate / Limited / Full), game status (Out, Doubtful, Questionable). Practice-report detail is early-week at capture.",
        "used_for": "Injury and depth section; starting-slot availability cross-reference.",
        "source_kind": "official", "http_status": 200,
    },
    {
        "id": "S-02", "publisher": "San Francisco 49ers (official club site)",
        "title": "49ers Depth Chart — updated as of 11/10/26",
        "url": "https://www.49ers.com/team/depth-chart",
        "what": "Official two-deep/three-deep ordering for offense, defense and special teams, with the club's own 'Updated as of' date.",
        "used_for": "Backup-depth model; detecting slots with no listed backup.",
        "source_kind": "official", "http_status": 200,
    },
    {
        "id": "S-03", "publisher": "San Francisco 49ers (official club site)",
        "title": "49ers Injury Report (weekly news index)",
        "url": "https://www.49ers.com/team/injury-report/",
        "what": "Club-published weekly inactives and ruled-out news items, week by week.",
        "used_for": "Confirming club-level (as opposed to league-level) designation history.",
        "source_kind": "official", "http_status": 200,
    },
    {
        "id": "S-04", "publisher": "San Francisco 49ers (official club site)",
        "title": "49ers 2026 Schedule",
        "url": "https://www.49ers.com/schedule/",
        "what": "Fixtures, final scores for completed weeks, kickoff times, broadcast network, radio line, venue (incl. Estadio Banorte for Week 11).",
        "used_for": "Home/away and venue checks; radio matrix; the Week 11 venue flag.",
        "source_kind": "official", "http_status": 200,
    },
    {
        "id": "S-05", "publisher": "NFL.com",
        "title": "2026 NFL schedule — Week 10 (by week)",
        "url": "https://www.nfl.com/schedules/2026/by-week/week-10",
        "what": "Official kickoff times (ET), networks, final scores and matchup order for the 14 Week-10 game rows.",
        "used_for": "Line-by-line audit of the 14 Week-10 rows in data/official/events.json.",
        "source_kind": "official", "http_status": 200,
    },
    {
        "id": "S-06", "publisher": "NFL.com",
        "title": "2026-27 National Football League important dates",
        "url": "https://www.nfl.com/news/2026-27-national-football-league-important-dates",
        "what": "League calendar plus the Personnel (Injury) Report Policy filing schedule quoted inside it (practice reports by 4:00 p.m. New York time on a set weekday pattern; 'an estimated injury report for practice status is not acceptable' on a practice day).",
        "used_for": "Why report timing (not just content) is a usable signal; filing deadlines.",
        "source_kind": "official", "http_status": 200,
    },
    {
        "id": "S-07", "publisher": "NFL.com",
        "title": "2026 NFL player statistics — passing",
        "url": "https://www.nfl.com/stats/player-stats/",
        "what": "Official season-to-date player stat table (2026, regular season).",
        "used_for": "Player-prop strategies: the only officially published player performance series available.",
        "source_kind": "official", "http_status": 200,
    },
    {
        "id": "S-08", "publisher": "NFL.com",
        "title": "NFL official 2026 schedule index",
        "url": "https://www.nfl.com/schedules/",
        "what": "Season schedule index; the source the dashboard's NFL rows are captured from.",
        "used_for": "Repo audit context for the existing NFL rows.",
        "source_kind": "official", "http_status": 200,
    },
    {
        "id": "S-09", "publisher": "NFL Football Operations (media.nfl.com PDF)",
        "title": "2026 Official Playing Rules of the NFL (PDF)",
        "url": "https://media.nfl.com/content/dam/communications/Official%20Playing%20Rules/2026%20Official%20Playing%20Rules.pdf",
        "what": "Rulebook used by the repo for game-clock/duration assumptions.",
        "used_for": "Duration provenance on NFL rows (the repo's `duration_source_url`).",
        "source_kind": "official", "http_status": 200,
    },
    {
        "id": "S-10", "publisher": "This repository",
        "title": "data/official/events.json",
        "url": "https://github.com/karagemop466-tech/Korea4/blob/main/data/official/events.json",
        "what": "The captured event table the dashboard renders (6,591 rows; 329 NFL).",
        "used_for": "Audit measurements (counts, field coverage, duplicate ids).",
        "source_kind": "repo", "http_status": 200,
    },
    {
        "id": "S-11", "publisher": "This repository",
        "title": "data/official/meta.json",
        "url": "https://github.com/karagemop466-tech/Korea4/blob/main/data/official/meta.json",
        "what": "Build metadata: build time, source-snapshot time, `system_today`, counts, flags.",
        "used_for": "Stale-date finding; snapshot-age disclosure.",
        "source_kind": "repo", "http_status": 200,
    },
    {
        "id": "S-12", "publisher": "This repository",
        "title": ".github/workflows/fetch-official.yml",
        "url": "https://github.com/karagemop466-tech/Korea4/blob/main/.github/workflows/fetch-official.yml",
        "what": "The workflow that refreshes `research/official/raw` and the manifest.",
        "used_for": "Refresh-coverage finding (branch-bound trigger, no schedule).",
        "source_kind": "repo", "http_status": 200,
    },
    {
        "id": "S-13", "publisher": "This repository",
        "title": "data/nfl-2026.json (legacy snapshot)",
        "url": "https://github.com/karagemop466-tech/Korea4/blob/main/data/nfl-2026.json",
        "what": "An early hand/thin-source NFL file that still asserts `\"verified\": true`.",
        "used_for": "Irregularity FL-01 (non-official sources labelled verified).",
        "source_kind": "repo", "http_status": 200,
    },
    {
        "id": "S-14", "publisher": "This repository",
        "title": "scripts/verify.py (static gate)",
        "url": "https://github.com/karagemop466-tech/Korea4/blob/main/scripts/verify.py",
        "what": "The structural gate: official-host allowlist, source link per row, internal links, JS syntax.",
        "used_for": "What the existing gate does and does not prove.",
        "source_kind": "repo", "http_status": 200,
    },
    {
        "id": "S-15", "publisher": "This repository",
        "title": "scripts/collect_official.py (collector)",
        "url": "https://github.com/karagemop466-tech/Korea4/blob/main/scripts/collect_official.py",
        "what": "Offline rebuild of the event table from `research/official/raw`; derives the Pacific 'today' at run time.",
        "used_for": "Stale-date root cause and fix.",
        "source_kind": "repo", "http_status": 200,
    },
    {
        "id": "S-17", "publisher": "This repository",
        "title": "data/nfl/ (NFL decision module merged in PR #45)",
        "url": "https://github.com/karagemop466-tech/Korea4/tree/main/data/nfl",
        "what": "A parallel session's independently captured NFL data: injury snapshot for 2026-11-13, depth-deficiency framework, validation gates, leaderboard shell, suggestions, open questions.",
        "used_for": "Reconciliation: checking where the two captures agree and where this section adds something the merged module lacks.",
        "source_kind": "repo", "http_status": 200,
    },
    {
        "id": "S-18", "publisher": "This repository",
        "title": "research/nfl-module/README.md (merged module's verification record)",
        "url": "https://github.com/karagemop466-tech/Korea4/blob/main/research/nfl-module/README.md",
        "what": "The merged module's own account of the official pages it fetched live on 2026-11-13, including IR-022 to IR-026.",
        "used_for": "Cross-checking this session's reading of the same official pages; recording where the two sessions agree.",
        "source_kind": "repo", "http_status": 200,
    },
    {
        "id": "S-16", "publisher": "This repository",
        "title": "COORDINATION.md (parallel-session board)",
        "url": "https://github.com/karagemop466-tech/Korea4/blob/main/COORDINATION.md",
        "what": "Shared task board, claims, hand-offs and per-session records.",
        "used_for": "Avoiding duplicate work with the four other 2026-11-13 NFL sessions.",
        "source_kind": "repo", "http_status": 200,
    },
]

SOURCE_BY_ID = {s["id"]: s for s in SOURCES}


def src(kind: str, sid: str, label: str | None = None) -> dict:
    """Return source fields for a row, validating the id."""
    s = SOURCE_BY_ID[sid]
    if kind == "official" and s["source_kind"] != "official":
        raise ValueError(f"{sid} is not an official source")
    return {
        "source_url": s["url"],
        "source_label": label or f'{s["publisher"]} — {s["title"]}',
        "source_kind": s["source_kind"],
        "checked": CAPTURE_LABEL,
    }


# --------------------------------------------------------------------------
# 2. Injury rows — transcribed from nfl.com/injuries (Week 10), 2026-11-13.
#    Only players and statuses that appear on that page are listed.
# --------------------------------------------------------------------------
INJURY_ROWS = [
    # San Francisco 49ers (opponent of the Week 10 focus game)
    {"id": "INJ-SF-01", "club": "49ers", "player": "Mike Evans", "pos": "WR", "slot": "WR1", "practice": "Did Not Participate", "game_status": "", "injury": "", "source": "S-01"},
    {"id": "INJ-SF-02", "club": "49ers", "player": "Renardo Green", "pos": "CB", "slot": "LCB", "practice": "Did Not Participate", "game_status": "", "injury": "", "source": "S-01"},
    {"id": "INJ-SF-03", "club": "49ers", "player": "Dre Greenlaw", "pos": "LB", "slot": "WILL", "practice": "Did Not Participate", "game_status": "", "injury": "", "source": "S-01"},
    {"id": "INJ-SF-04", "club": "49ers", "player": "Deommodore Lenoir", "pos": "CB", "slot": "RCB", "practice": "Did Not Participate", "game_status": "", "injury": "", "source": "S-01"},
    {"id": "INJ-SF-05", "club": "49ers", "player": "Christian McCaffrey", "pos": "RB", "slot": "RB1", "practice": "Did Not Participate", "game_status": "", "injury": "", "source": "S-01"},
    {"id": "INJ-SF-06", "club": "49ers", "player": "Trent Williams", "pos": "T", "slot": "LT", "practice": "Did Not Participate", "game_status": "", "injury": "", "source": "S-01"},
    {"id": "INJ-SF-07", "club": "49ers", "player": "Upton Stout", "pos": "CB", "slot": "NB", "practice": "Limited Participation", "game_status": "", "injury": "", "source": "S-01"},
    {"id": "INJ-SF-08", "club": "49ers", "player": "Deebo Samuel Sr.", "pos": "WR", "slot": "WR2", "practice": "Limited Participation", "game_status": "", "injury": "", "source": "S-01"},
    {"id": "INJ-SF-09", "club": "49ers", "player": "Siran Neal", "pos": "S", "slot": "FS2", "practice": "Limited Participation", "game_status": "", "injury": "", "source": "S-01"},
    {"id": "INJ-SF-10", "club": "49ers", "player": "C.J. West", "pos": "DT", "slot": "DT depth", "practice": "Limited Participation", "game_status": "", "injury": "", "source": "S-01"},
    {"id": "INJ-SF-11", "club": "49ers", "player": "Nate Hobbs", "pos": "CB", "slot": "CB depth", "practice": "Full Participation", "game_status": "", "injury": "", "source": "S-01"},
    {"id": "INJ-SF-12", "club": "49ers", "player": "Demarcus Robinson", "pos": "WR", "slot": "WR2 depth", "practice": "Full Participation", "game_status": "", "injury": "", "source": "S-01"},
    # Dallas Cowboys (Week 10 opponent)
    {"id": "INJ-DAL-01", "club": "Cowboys", "player": "Malik Hooker", "pos": "S", "slot": "S", "practice": "Did Not Participate", "game_status": "", "injury": "", "source": "S-01"},
    {"id": "INJ-DAL-02", "club": "Cowboys", "player": "P.J. Locke", "pos": "S", "slot": "S", "practice": "Did Not Participate", "game_status": "", "injury": "", "source": "S-01"},
    {"id": "INJ-DAL-03", "club": "Cowboys", "player": "Joey Porter Jr.", "pos": "CB", "slot": "CB", "practice": "Did Not Participate", "game_status": "", "injury": "", "source": "S-01"},
    {"id": "INJ-DAL-04", "club": "Cowboys", "player": "Donovan Ezeiruaku", "pos": "LB", "slot": "EDGE/LB", "practice": "Did Not Participate", "game_status": "", "injury": "", "source": "S-01"},
    {"id": "INJ-DAL-05", "club": "Cowboys", "player": "Jake Ferguson", "pos": "TE", "slot": "TE1", "practice": "Did Not Participate", "game_status": "", "injury": "", "source": "S-01"},
    {"id": "INJ-DAL-06", "club": "Cowboys", "player": "Tyler Goodson", "pos": "RB", "slot": "RB depth", "practice": "Did Not Participate", "game_status": "", "injury": "", "source": "S-01"},
    {"id": "INJ-DAL-07", "club": "Cowboys", "player": "Von Miller", "pos": "LB", "slot": "EDGE/LB", "practice": "Did Not Participate", "game_status": "", "injury": "", "source": "S-01"},
    {"id": "INJ-DAL-08", "club": "Cowboys", "player": "Jonathan Mingo", "pos": "WR", "slot": "WR depth", "practice": "Did Not Participate", "game_status": "", "injury": "", "source": "S-01"},
    {"id": "INJ-DAL-09", "club": "Cowboys", "player": "Alijah Clark", "pos": "S", "slot": "S depth", "practice": "Did Not Participate", "game_status": "", "injury": "", "source": "S-01"},
    {"id": "INJ-DAL-10", "club": "Cowboys", "player": "George Pickens", "pos": "WR", "slot": "WR1", "practice": "Limited Participation", "game_status": "", "injury": "", "source": "S-01"},
    {"id": "INJ-DAL-11", "club": "Cowboys", "player": "KaVontae Turpin", "pos": "WR", "slot": "WR/KR", "practice": "Limited Participation", "game_status": "", "injury": "", "source": "S-01"},
    {"id": "INJ-DAL-12", "club": "Cowboys", "player": "Juanyeh Thomas", "pos": "S", "slot": "S depth", "practice": "Limited Participation", "game_status": "", "injury": "", "source": "S-01"},
    # Other clubs — only rows where the page shows an explicit Out/Questionable designation
    {"id": "INJ-WAS-01", "club": "Commanders", "player": "Lucas Patrick", "pos": "C", "slot": "C", "practice": "Did Not Participate", "game_status": "Out", "injury": "Concussion", "source": "S-01"},
    {"id": "INJ-WAS-02", "club": "Commanders", "player": "Colson Yankoff", "pos": "TE", "slot": "TE depth", "practice": "Did Not Participate", "game_status": "Out", "injury": "Knee", "source": "S-01"},
    {"id": "INJ-NYG-01", "club": "Giants", "player": "Malik Harrison", "pos": "LB", "slot": "LB", "practice": "Limited Participation", "game_status": "Questionable", "injury": "Groin", "source": "S-01"},
]

# Clubs whose Week-10 list was visible at capture, and the two clubs the page
# showed with no reported injuries. Counts are of *listed players*, not of the
# whole roster — the page only lists players with a reportable designation.
INJURY_COVERAGE = [
    {"id": "COV-01", "item": "Clubs with a visible Week-10 injury table at capture", "value": "26 of 28", "detail": "New Orleans and Cincinnati lists were cut off in the captured text.", "source": "S-01"},
    {"id": "COV-02", "item": "Clubs the page shows as 'No Injuries Reported'", "value": "2 (Chargers, Ravens)", "detail": "Week 10 Monday game.", "source": "S-01"},
    {"id": "COV-03", "item": "49ers players listed for Week 10", "value": "12", "detail": "6 Did Not Participate, 4 Limited, 2 Full; every game-status field blank at capture.", "source": "S-01"},
    {"id": "COV-04", "item": "Cowboys players listed for Week 10", "value": "18", "detail": "9 Did Not Participate, 3 Limited, 6 Full; every game-status field blank at capture.", "source": "S-01"},
    {"id": "COV-05", "item": "Injury data in the repository before this session", "value": "none", "detail": "No injury file, key or table existed in data/ or data/official/.", "source": "S-10"},
]

# --------------------------------------------------------------------------
# 3. Depth-chart rows — 49ers official depth chart, "Updated as of 11/10/26".
#    `backup_1`/`backup_2` are exactly what the official chart lists; an empty
#    value means the chart lists nobody at that slot (that is the deficiency
#    signal, not an omission by us).
# --------------------------------------------------------------------------
DEPTH_ROWS = [
    {"id": "D-OFF-01", "unit": "Offense", "slot": "WR", "starter": "Mike Evans", "backup_1": "Jordan Watkins", "backup_2": "Brandin Cooks"},
    {"id": "D-OFF-02", "unit": "Offense", "slot": "LT", "starter": "Trent Williams", "backup_1": "Vederian Lowe", "backup_2": "Enrique Cruz Jr."},
    {"id": "D-OFF-03", "unit": "Offense", "slot": "LG", "starter": "Connor Colby", "backup_1": "Carver Willis", "backup_2": ""},
    {"id": "D-OFF-04", "unit": "Offense", "slot": "C", "starter": "Jake Brendel", "backup_1": "Jarrett Patterson", "backup_2": ""},
    {"id": "D-OFF-05", "unit": "Offense", "slot": "RG", "starter": "Dominick Puni", "backup_1": "", "backup_2": ""},
    {"id": "D-OFF-06", "unit": "Offense", "slot": "RT", "starter": "Colton McKivitz", "backup_1": "", "backup_2": ""},
    {"id": "D-OFF-07", "unit": "Offense", "slot": "TE", "starter": "George Kittle", "backup_1": "Luke Farrell", "backup_2": "Brayden Willis"},
    {"id": "D-OFF-08", "unit": "Offense", "slot": "WR", "starter": "Deebo Samuel Sr.", "backup_1": "Demarcus Robinson", "backup_2": "Jacob Cowing"},
    {"id": "D-OFF-09", "unit": "Offense", "slot": "RB", "starter": "Christian McCaffrey", "backup_1": "Kaelon Black", "backup_2": "Jordan James"},
    {"id": "D-OFF-10", "unit": "Offense", "slot": "FB", "starter": "Kyle Juszczyk", "backup_1": "", "backup_2": ""},
    {"id": "D-OFF-11", "unit": "Offense", "slot": "QB", "starter": "Brock Purdy", "backup_1": "Mac Jones", "backup_2": "Kurtis Rourke"},
    {"id": "D-DEF-01", "unit": "Defense", "slot": "LDE", "starter": "Keion White", "backup_1": "Mykel Williams", "backup_2": "Khalid Kareem"},
    {"id": "D-DEF-02", "unit": "Defense", "slot": "LDT", "starter": "DeForest Buckner", "backup_1": "Gracen Halton", "backup_2": "Sebastian Valdez"},
    {"id": "D-DEF-03", "unit": "Defense", "slot": "RDT", "starter": "Osa Odighizuwa", "backup_1": "James Thompson Jr.", "backup_2": ""},
    {"id": "D-DEF-04", "unit": "Defense", "slot": "RDE", "starter": "Nick Bosa", "backup_1": "Romello Height", "backup_2": ""},
    {"id": "D-DEF-05", "unit": "Defense", "slot": "SAM", "starter": "Jaden Dugger", "backup_1": "Luke Gifford", "backup_2": ""},
    {"id": "D-DEF-06", "unit": "Defense", "slot": "MIKE", "starter": "Fred Warner", "backup_1": "Tatum Bethune", "backup_2": ""},
    {"id": "D-DEF-07", "unit": "Defense", "slot": "WILL", "starter": "Dre Greenlaw", "backup_1": "Garret Wallow", "backup_2": ""},
    {"id": "D-DEF-08", "unit": "Defense", "slot": "LCB", "starter": "Renardo Green", "backup_1": "", "backup_2": ""},
    {"id": "D-DEF-09", "unit": "Defense", "slot": "RCB", "starter": "Deommodore Lenoir", "backup_1": "Ephesians Prysock", "backup_2": ""},
    {"id": "D-DEF-10", "unit": "Defense", "slot": "NB", "starter": "Upton Stout", "backup_1": "", "backup_2": ""},
    {"id": "D-DEF-11", "unit": "Defense", "slot": "FS", "starter": "Ji'Ayir Brown", "backup_1": "Siran Neal", "backup_2": ""},
    {"id": "D-DEF-12", "unit": "Defense", "slot": "SS", "starter": "Malik Mustapha", "backup_1": "Marques Sigle", "backup_2": "Ashtyn Davis"},
    {"id": "D-ST-01", "unit": "Special teams", "slot": "P", "starter": "Corliss Waitman", "backup_1": "", "backup_2": ""},
    {"id": "D-ST-02", "unit": "Special teams", "slot": "K", "starter": "Eddy Piñeiro", "backup_1": "", "backup_2": ""},
    {"id": "D-ST-03", "unit": "Special teams", "slot": "H", "starter": "Corliss Waitman", "backup_1": "", "backup_2": ""},
    {"id": "D-ST-04", "unit": "Special teams", "slot": "PR", "starter": "Jacob Cowing", "backup_1": "Jordan Watkins", "backup_2": ""},
    {"id": "D-ST-05", "unit": "Special teams", "slot": "KOR", "starter": "Deebo Samuel Sr.", "backup_1": "Jordan James", "backup_2": ""},
    {"id": "D-ST-06", "unit": "Special teams", "slot": "LS", "starter": "Jon Weeks", "backup_1": "", "backup_2": ""},
]

# Slots where the official chart lists no backup at all. Computed by the
# builder from DEPTH_ROWS (never hand-maintained, so it cannot drift).
DEPTH_GAP_NOTE = (
    "A blank backup cell means the official depth chart lists nobody at that slot. "
    "It does not prove the club has no replacement — it proves the replacement is not "
    "documented on the official chart, so any '3rd/4th string' claim about this slot "
    "would be an inference and is left UNVERIFIED."
)

# --------------------------------------------------------------------------
# 4. Strategy designs. No strategy has passed the backtest/luck gates yet: the
#    repository holds no historical results and no closing lines (see AUDIT
#    rows A-05/A-06). Design rows stand on their own; result fields stay blank.
# --------------------------------------------------------------------------
STRATEGY_ROWS = [
    {
        "id": "ST-01", "family": "Single", "name": "Official-report participation drift",
        "thesis": "When a starting-slot player's official practice status improves across the week (DNP -> Limited -> Full), the market's pre-week line can lag the final designation. Play the side whose starting availability improved.",
        "inputs": "nfl.com/injuries practice report, day by day (Wed/Thu/Fri pattern), plus the club depth chart for slot value",
        "skill_or_luck": "Skill-testable: participation change is mechanical and dated.",
        "gates": "FAILS G5/G6 (no closing-line history, no result history). PASSES G1/G3 (official, public, timestamped).",
        "status": "DESIGNED — BLOCKED ON DATA",
    },
    {
        "id": "ST-02", "family": "Single", "name": "No-listed-backup stress",
        "thesis": "Target the unit of a team whose injured starter plays a slot with no documented backup on the official depth chart (e.g. 49ers LCB and NB on 2026-11-10). Where replacement quality is undocumented, the market prices it least efficiently.",
        "inputs": "Official depth chart + official injury report",
        "skill_or_luck": "Skill-testable, but sample is small: slots with no backup appear sporadically.",
        "gates": "FAILS G4 (thin sample by construction) until 2+ seasons of charts are archived. PASSES G1/G2.",
        "status": "DESIGNED — BLOCKED ON SAMPLE SIZE",
    },
    {
        "id": "ST-03", "family": "Parlay (2-leg)", "name": "Cross-game injury-news fade",
        "thesis": "Two games on the same slate where a starter's designation changed after the market opened. Correlated only through slate-wide news timing; test the correlation before sizing.",
        "inputs": "Injury report timestamps + opening lines",
        "skill_or_luck": "Skill in news timing; the parlay multiplies variance, so the gate requires the joint edge to exceed the product of the legs.",
        "gates": "FAILS G6/G7 (no opening-line capture; correlation unmeasured) and G8 (needs a joint-edge test).",
        "status": "DESIGNED — BLOCKED ON DATA",
    },
    {
        "id": "ST-04", "family": "Parlay (3-leg)", "name": "Divisional totals ladder",
        "thesis": "Divisional games repeat; if the same officiating/pace conditions repeat, totals may mean-revert slower than the market assumes. Combine three divisional totals in one week.",
        "inputs": "Official schedule (divisional flag) + historical closing totals",
        "skill_or_luck": "High luck content; three-leg compounding makes the skill threshold harder to clear.",
        "gates": "BLOCKED G1: no official source publishes closing totals. This strategy is not constructible from official data alone.",
        "status": "DESIGNED — OFFICIAL-DATA INSUFFICIENT",
    },
    {
        "id": "ST-05", "family": "Player prop", "name": "Snap-share proxy from official stats",
        "thesis": "Use officially published season stat volume (attempts, targets, carries) as a floor for a player's opportunity, then require the official injury report to show the player at Full practice.",
        "inputs": "nfl.com player stats + official injury report",
        "skill_or_luck": "Skill-testable; volume is stable week to week.",
        "gates": "FAILS G6 (no prop line history) and G4 (snap counts are not published on the official stat page).",
        "status": "DESIGNED — BLOCKED ON DATA",
    },
    {
        "id": "ST-06", "family": "Player prop combo (same game)", "name": "QB-receiver stack under a backup OT",
        "thesis": "If the starting left tackle is on the report and the slot has a documented backup, the QB's pressure rate should rise; pair an under on the QB with an under on the WR. Intra-game correlation is negative-to-positive depending on game script — must be measured, not assumed.",
        "inputs": "Official injury report by position + official depth chart + official player stats",
        "skill_or_luck": "Skill-testable but needs pressure data, which the official stat page does not publish.",
        "gates": "FAILS G4/G6/G8. Correlation value left BLANK rather than assumed.",
        "status": "DESIGNED — BLOCKED ON DATA",
    },
    {
        "id": "ST-07", "family": "Player prop combo (cross-game)", "name": "Two RB volume unders in low-total games",
        "thesis": "Two independent RB volume unders in games the market expects to be low-scoring. Intended as near-zero correlation; the gate must prove independence before it is rewarded.",
        "inputs": "Official player stats + closing game totals",
        "skill_or_luck": "Luck-dominated unless the volume model beats the market's implied volume.",
        "gates": "FAILS G6/G7. Correlation value BLANK.",
        "status": "DESIGNED — BLOCKED ON DATA",
    },
    {
        "id": "ST-08", "family": "Derivative", "name": "Rest/travel asymmetry from official schedule",
        "thesis": "Short week (Thursday game) or an international trip is published by the league weeks in advance. Test whether the pre-published rest/travel condition is already fully priced.",
        "inputs": "nfl.com schedule (kickoff dates, venues, international designations)",
        "skill_or_luck": "Pure skill test: the input is public and dated, so any edge is either real or absent.",
        "gates": "PASSES G1/G2/G3 (official, public, complete for 2026). FAILS G6 — needs result history to measure.",
        "status": "DESIGNED — READY ONCE RESULTS ARE CAPTURED",
    },
    {
        "id": "ST-09", "family": "Single", "name": "Post-bye regression check",
        "thesis": "Teams coming off a bye (official schedule shows the bye) may show a tempo reset. Test as a totals signal, not a side signal.",
        "inputs": "Official schedule + official play-by-play/tempo data (not on the official site)",
        "skill_or_luck": "Mostly luck; included because it is cheap to falsify.",
        "gates": "FAILS G4 (tempo data not officially published).",
        "status": "DESIGNED — BLOCKED ON DATA",
    },
    {
        "id": "ST-10", "family": "Single", "name": "Backup-QB start under club announcement",
        "thesis": "When a club announces a backup QB start (official club site), the opening line was set for the starter. Test whether the adjustment is complete at kickoff.",
        "inputs": "Official club news (e.g. 49ers.com injury report index) + opening and closing lines",
        "skill_or_luck": "Skill-testable and well documented by clubs; timestamps are the key.",
        "gates": "PASSES G1/G3. FAILS G6 (no line history). Requires the club-announcement timestamp to be captured, which the repo does not do yet.",
        "status": "DESIGNED — BLOCKED ON DATA",
    },
    {
        "id": "ST-11", "family": "Parlay (2-leg)", "name": "Injury-hedged two-leg (side + opposing team total under)",
        "thesis": "A structural hedge: if the injured team's offense stalls, the opposing team total under is partly protected by the same mechanism, so the legs are positively correlated in the loss state.",
        "inputs": "Injury report + team-total markets",
        "skill_or_luck": "Correlation is the point: the gate must show the joint distribution beats independent pricing.",
        "gates": "FAILS G6/G7/G8. Correlation value BLANK until measured.",
        "status": "DESIGNED — BLOCKED ON DATA",
    },
    {
        "id": "ST-12", "family": "Derivative", "name": "Line-move confirmation (no bet without a move)",
        "thesis": "A control strategy, not an edge: only act when the line has moved in the direction the official information implies. Its purpose is to measure how much of any result is information and how much is noise.",
        "inputs": "Opening and closing lines + official injury timestamps",
        "skill_or_luck": "This is the benchmark every other strategy must beat.",
        "gates": "FAILS G6 only. Deliberately kept: without it the leaderboard cannot separate skill from luck.",
        "status": "DESIGNED — BENCHMARK",
    },
]

# --------------------------------------------------------------------------
# 5. Validation gates. Each gate is a pass/fail test with an explicit rule.
#    `result` is the current state of every strategy against it.
# --------------------------------------------------------------------------
GATE_ROWS = [
    {"id": "G1", "gate": "Source authenticity", "rule": "Every input traces to a league, club, network or rules-publisher URL. No aggregator, odds screen or news summary.", "test": "Automated: URL host must be on an official allowlist; row must carry the URL.", "result": "PASS — enforced by scripts/verify_nfl_lab.py on this page.", "kind": "structural"},
    {"id": "G2", "gate": "Timestamp discipline", "rule": "The input existed before the decision point. An injury status read after kickoff cannot inform that game.", "test": "Each input carries a capture time; decision time must be later.", "result": "PARTIAL — capture times exist for this session's fetches; historical timestamps are not archived.", "kind": "structural"},
    {"id": "G3", "gate": "Reproducibility", "rule": "Anyone can rebuild the same signal from the same public sources on the same date.", "test": "Re-run the parser on the archived raw response; output must match byte-for-byte for values.", "result": "PASS for schedule rows (offline rebuild reproduces 6,591 rows); NOT MET for injury/line inputs (not archived yet).", "kind": "structural"},
    {"id": "G4", "gate": "Sample sufficiency", "rule": "At least 200 independent observations, and no single week contributing more than 10% of them.", "test": "Count observations; check concentration.", "result": "FAIL — the repository holds 0 completed-game result rows usable for backtesting (schedule rows only).", "kind": "data"},
    {"id": "G5", "gate": "Out-of-sample holdout", "rule": "The rule is fixed on one season and tested untouched on the next.", "test": "Freeze parameters; score the holdout only once.", "result": "FAIL — no historical season of inputs is archived.", "kind": "data"},
    {"id": "G6", "gate": "Market benchmark", "rule": "Any claimed edge is measured against the closing line, not against a naive model.", "test": "Compare strategy return with closing-line value (CLV) and with the ST-12 control.", "result": "FAIL — no official source publishes closing lines; none are captured in this repo.", "kind": "data"},
    {"id": "G7", "gate": "Luck separation", "rule": "Bootstrap the strategy's record 10,000 times; require the 5th percentile of profit to stay positive, and require the result to survive a permutation test at p<0.05.", "test": "Resampling + permutation on settled bets only.", "result": "FAIL — cannot run with 0 settled bets.", "kind": "data"},
    {"id": "G8", "gate": "Correlation control (combos)", "rule": "For every parlay/prop combo, the measured pairwise correlation is recorded, and the joint edge must exceed the product of the leg edges after correlation.", "test": "Compute correlation on settled legs; re-price the combo with the measured value.", "result": "FAIL — every correlation cell on this site is BLANK by rule; no settled legs exist.", "kind": "data"},
    {"id": "G9", "gate": "Drawdown and stake honesty", "rule": "Report maximum drawdown and the stake that produced it; a strategy that only works at one stake size is rejected.", "test": "Recompute at 0.5x/1x/2x flat stakes.", "result": "FAIL — depends on G7.", "kind": "data"},
    {"id": "G10", "gate": "No-manual-input check", "rule": "The pipeline runs end to end without a human typing a value.", "test": "Run the collector in CI with no edits; diff the output.", "result": "PARTIAL — schedule collection is scripted; injury and market capture are not yet automated in this repository.", "kind": "process"},
]

# --------------------------------------------------------------------------
# 5b. Gate matrix: PASS / FAIL / PARTIAL / N/A per strategy, derived only from
#     what the design says about its own inputs. "BLANK" would mean "not yet
#     applied"; it is not used here because every gate has been applied on paper.
# --------------------------------------------------------------------------
_P = "PASS"; _F = "FAIL"; _X = "PARTIAL"; _N = "N/A"

STRATEGY_GATES = {
    "ST-01": {"G1": _P, "G2": _X, "G3": _X, "G4": _F, "G5": _F, "G6": _F, "G7": _F, "G8": _N, "G9": _F, "G10": _X},
    "ST-02": {"G1": _P, "G2": _X, "G3": _X, "G4": _F, "G5": _F, "G6": _F, "G7": _F, "G8": _N, "G9": _F, "G10": _X},
    "ST-03": {"G1": _P, "G2": _X, "G3": _X, "G4": _F, "G5": _F, "G6": _F, "G7": _F, "G8": _F, "G9": _F, "G10": _X},
    "ST-04": {"G1": _F, "G2": _X, "G3": _X, "G4": _F, "G5": _F, "G6": _F, "G7": _F, "G8": _F, "G9": _F, "G10": _X},
    "ST-05": {"G1": _P, "G2": _X, "G3": _X, "G4": _F, "G5": _F, "G6": _F, "G7": _F, "G8": _N, "G9": _F, "G10": _X},
    "ST-06": {"G1": _P, "G2": _X, "G3": _X, "G4": _F, "G5": _F, "G6": _F, "G7": _F, "G8": _F, "G9": _F, "G10": _X},
    "ST-07": {"G1": _P, "G2": _X, "G3": _X, "G4": _F, "G5": _F, "G6": _F, "G7": _F, "G8": _F, "G9": _F, "G10": _X},
    "ST-08": {"G1": _P, "G2": _P, "G3": _P, "G4": _F, "G5": _F, "G6": _F, "G7": _F, "G8": _N, "G9": _F, "G10": _X},
    "ST-09": {"G1": _P, "G2": _P, "G3": _X, "G4": _F, "G5": _F, "G6": _F, "G7": _F, "G8": _N, "G9": _F, "G10": _X},
    "ST-10": {"G1": _P, "G2": _X, "G3": _X, "G4": _F, "G5": _F, "G6": _F, "G7": _F, "G8": _N, "G9": _F, "G10": _X},
    "ST-11": {"G1": _P, "G2": _X, "G3": _X, "G4": _F, "G5": _F, "G6": _F, "G7": _F, "G8": _F, "G9": _F, "G10": _X},
    "ST-12": {"G1": _P, "G2": _X, "G3": _X, "G4": _F, "G5": _F, "G6": _F, "G7": _F, "G8": _N, "G9": _F, "G10": _X},
}

# --------------------------------------------------------------------------
# 6. Correlation register. Values are deliberately blank: correlation cannot be
#    asserted from official schedule/injury text alone.
# --------------------------------------------------------------------------
CORRELATION_ROWS = [
    {"id": "C-01", "pair": "Spread and total, same game", "expected_sign": "Negative in practice (favoured sides tend to sit on leads), magnitude unknown", "value": "", "why_blank": "Requires closing lines for both markets across many games; none captured.", "affects": "ST-03, ST-04, ST-07"},
    {"id": "C-02", "pair": "QB passing yards over and WR receiving yards over, same team", "expected_sign": "Positive, magnitude unknown", "value": "", "why_blank": "Needs settled prop results; prop markets are not published by the league.", "affects": "ST-06"},
    {"id": "C-03", "pair": "RB rushing yards and team total over, same team", "expected_sign": "Positive, magnitude unknown", "value": "", "why_blank": "Needs settled results and team-total lines.", "affects": "ST-07"},
    {"id": "C-04", "pair": "Two legs in the same game (any market)", "expected_sign": "Unknown; must be measured, never assumed zero", "value": "", "why_blank": "Same-game legs share weather, officiating and script; measuring requires the closing lines and results.", "affects": "ST-06, ST-11"},
    {"id": "C-05", "pair": "Two legs in different games on the same slate", "expected_sign": "Near zero a priori; the gate must test it rather than assert it", "value": "", "why_blank": "Needs a slate-level result panel.", "affects": "ST-03, ST-07"},
    {"id": "C-06", "pair": "Injury-news fade and opposing team total under (hedged pair)", "expected_sign": "Positive in the loss state by construction", "value": "", "why_blank": "Deliberately correlated strategy; the gate (G8) needs the measured value before it can be sized.", "affects": "ST-11"},
    {"id": "C-07", "pair": "Divisional total A and divisional total B, same week", "expected_sign": "Unknown", "value": "", "why_blank": "No totals captured.", "affects": "ST-04"},
    {"id": "C-08", "pair": "Rest/travel signal and totals signal, same game", "expected_sign": "Unknown", "value": "", "why_blank": "No totals captured.", "affects": "ST-08, ST-09"},
]

# --------------------------------------------------------------------------
# 7. Leaderboard. Empty by design — the reward rules are published first so the
#    competition cannot be gamed after the fact.
# --------------------------------------------------------------------------
LEADERBOARD_ROWS: list[dict] = []   # no qualified strategy exists yet

LEADERBOARD_RULES = [
    {"id": "LB-01", "rule": "Eligibility", "detail": "A strategy is ranked only after passing G1–G10. Strategies that fail a gate stay visible in the gate matrix and never appear on the leaderboard.", "rationale": "Prevents a lucky 4-0 start from outranking a validated rule."},
    {"id": "LB-02", "rule": "Scored quantity", "detail": "Closing-line value (CLV) per bet, in basis points, weighted equally per bet — not units of profit.", "rationale": "CLV is far less luck-dominated than profit at small samples."},
    {"id": "LB-03", "rule": "Minimum sample", "detail": "200 settled bets before a rank is issued; below that the strategy is listed as 'unranked (n<200)'.", "rationale": "Guards the leaderboard against variance."},
    {"id": "LB-04", "rule": "Luck haircut", "detail": "Rank score = median bootstrap CLV minus the 5th-percentile bootstrap CLV (a penalty for variance).", "rationale": "Rewards consistency, not one hot week."},
    {"id": "LB-05", "rule": "Reward tiers", "detail": "Tier 1 (validated, ranked top 3 for two consecutive 8-week periods) gets the largest share; Tier 2 (validated, ranked once) gets a smaller share; Tier 3 (passes gates, unranked) gets recognition only, no reward.", "rationale": "Rewards persistence; a single good stretch cannot claim Tier 1."},
    {"id": "LB-06", "rule": "Decay and demotion", "detail": "A strategy that fails G7 on re-test at the next 8-week review drops one tier. Two consecutive failures retire it to the archive.", "rationale": "Stops decayed edges from collecting rewards."},
    {"id": "LB-07", "rule": "Combos are separate contestants", "detail": "A parlay or prop combo is ranked as its own strategy with its measured correlation (G8) attached; its reward is scaled by how much of its edge survives the correlation re-price.", "rationale": "Directly answers the correlation requirement."},
    {"id": "LB-08", "rule": "Reward currency", "detail": "BLANK — the reward itself is your decision (see the decision register, D-06). No value is assumed here.", "rationale": "Cannot be invented by the system."},
]

# --------------------------------------------------------------------------
# 8. Suggestions register — proposals to improve the site's decision quality.
# --------------------------------------------------------------------------
SUGGESTION_ROWS = [
    {"id": "SUG-01", "priority": "P1", "suggestion": "Capture completed-game results (final scores) from NFL.com weekly pages into `data/nfl-lab/results.json` on a schedule.", "why": "Without results, gates G4–G7 can never run and the leaderboard stays empty. This is the single blocking dependency.", "measure": "≥200 settled NFL games archived; gate G4 turns PASS.", "effort": "Low — the weekly page already renders finals (e.g. Commanders 24, Giants 21).", "owner_action": "Approve automated capture.", "status": "PROPOSED"},
    {"id": "SUG-02", "priority": "P1", "suggestion": "Archive a daily injury-report snapshot per club with the capture timestamp, instead of only the current week.", "why": "The official page mutates daily; a signal is only usable if we can prove the value existed before kickoff (gate G2).", "measure": "≥3 snapshots/week/club; G2 turns PASS.", "effort": "Low", "owner_action": "Approve snapshot storage growth (~0.2 MB/week compressed).", "status": "PROPOSED"},
    {"id": "SUG-03", "priority": "P1", "suggestion": "Decide the market-line question explicitly: closing lines are not published by the NFL, so either license a data feed or accept that G6 can never pass.", "why": "Every profitability claim depends on a closing-line benchmark. This is a missing-information decision, not a coding task.", "measure": "G6 PASS or a written decision to drop profitability claims.", "effort": "Decision, then either integration or scope cut.", "owner_action": "Choose one of D-03 / D-04.", "status": "NEEDS YOUR DECISION"},
    {"id": "SUG-04", "priority": "P2", "suggestion": "Publish the depth-chart gap list as a first-class table (slots with no documented backup), refreshed weekly for all 32 clubs.", "why": "It is the only defensible way to answer 'is a 2nd/3rd/4th-string player replacing a starter?' from official data; today only the 49ers chart is captured.", "measure": "32 club charts captured; gap count per club per week.", "effort": "Medium — 32 fetches, one parser per chart layout family.", "owner_action": "Approve scope expansion.", "status": "PROPOSED"},
    {"id": "SUG-05", "priority": "P2", "suggestion": "Add a 'why is this blank?' tooltip beside every UNVERIFIED cell, carrying the exact source URL that shows the gap.", "why": "Blank cells currently look like site errors; a reviewer needs to see the evidence for the blank in one click.", "measure": "100% of blank cells carry a source link.", "effort": "Low", "owner_action": "None.", "status": "IMPLEMENTED (this section)"},
    {"id": "SUG-06", "priority": "P2", "suggestion": "Show the snapshot age in hours on every page and turn the banner amber past 48 hours.", "why": "Stale data is the largest silent risk in the existing dashboard: sources were 11 days old at rebuild.", "measure": "Age label present on 100% of pages.", "effort": "Low", "owner_action": "None.", "status": "IMPLEMENTED (this section) — the 15 legacy pages are owned by the main build and are unchanged."},
    {"id": "SUG-07", "priority": "P3", "suggestion": "Split the 4.9 MB MLB page and 2.3 MB review page into paginated chunks or JSON-backed tables.", "why": "Large single pages are slow on mobile radio-network connections and hard to review line by line.", "measure": "Largest page under 500 KB.", "effort": "Medium — build pipeline change.", "owner_action": "Approve; requires editing the main build (not this session's scope).", "status": "DEFERRED (file owned by another build path)"},
    {"id": "SUG-08", "priority": "P3", "suggestion": "Fix the workflow triggers: `fetch-official.yml` only fires for the superseded branch name `arena/72e6d3f7-korea4` and has no schedule.", "why": "That is why the snapshot is stale. Main-branch pushes never refresh official sources.", "measure": "A refresh run on `main` plus a weekly `cron`.", "effort": "Low", "owner_action": "Approve workflow edit (workflow files are shared).", "status": "PROPOSED"},
    {"id": "SUG-09", "priority": "P3", "suggestion": "Add a decision log page where each accepted suggestion is recorded with the evidence that justified it and a review date.", "why": "Prevents re-litigating decisions and makes reversal cheap.", "measure": "Every accepted item has an entry with date and review trigger.", "effort": "Low", "owner_action": "None.", "status": "IMPLEMENTED (this section: Decision register)"},
    {"id": "SUG-10", "priority": "P3", "suggestion": "Retire or annotate `data/nfl-2026.json`, which still asserts `\"verified\": true` while citing non-official sites.", "why": "A file that calls itself verified but is not is worse than a missing file; it can seed future errors.", "measure": "File deleted or its `verified` flag set to false with a note.", "effort": "Trivial", "owner_action": "Approve deletion (it is referenced only by the audit page).", "status": "PROPOSED — needs approval to delete data"},
    {"id": "SUG-11", "priority": "P3", "suggestion": "Add a data-freshness SLA table per source family (schedule, injury, depth, stats) with the expected refresh cadence.", "why": "Turns 'is this current?' into a measured question instead of a vibe.", "measure": "Every source row has cadence and last-refresh columns.", "effort": "Low", "owner_action": "None.", "status": "PROPOSED"},
    {"id": "SUG-12", "priority": "P3", "suggestion": "Publish the gate code, not just the gate results, and version the gate rule set.", "why": "Gates are the only thing separating this leaderboard from a tip sheet; they must be auditable and immutable per season.", "measure": "Gate rules carry version ids; changes are dated.", "effort": "Low", "owner_action": "None.", "status": "PROPOSED"},
]

# --------------------------------------------------------------------------
# 9. Open questions register — questions that must be answered before a
#    decision is reasonable, split into what we HAVE and DO NOT HAVE.
# --------------------------------------------------------------------------
QUESTION_ROWS = [
    {"id": "Q-01", "area": "Market data", "question": "Where do closing lines come from, and may they be stored?", "have": "Nothing: no odds file, key or row exists anywhere in the repo (verified by search).", "missing": "A licensed feed or a decision to drop profitability claims.", "blocking": "Yes — gates G6/G7 and the leaderboard.", "answered": "", "status": "OPEN"},
    {"id": "Q-02", "area": "Market data", "question": "Are opening lines needed separately from closing lines?", "have": "No line data at all.", "missing": "A second snapshot per market, taken before the injury report.", "blocking": "Yes — strategies ST-03, ST-10, ST-12 depend on the open-to-close move.", "answered": "", "status": "OPEN"},
    {"id": "Q-03", "area": "Results", "question": "Which source is authoritative for final scores, and how far back can it be captured?", "have": "NFL.com weekly pages show finals for completed 2026 weeks (verified Week 10: Commanders 24, Giants 21).", "missing": "An automated capture and a decision on history depth (one season? five?).", "blocking": "Yes — gates G4/G5/G7.", "answered": "", "status": "OPEN"},
    {"id": "Q-04", "area": "Results", "question": "Do we need play-by-play/snap counts, or are box scores enough?", "have": "Official stats pages publish player volume, not snap counts.", "missing": "A decision on whether snap data is required (it would come from the league's Next Gen Stats or a licensed feed).", "blocking": "Partially — ST-05/ST-06 are weaker without it.", "answered": "", "status": "OPEN"},
    {"id": "Q-05", "area": "Injuries", "question": "What is the official filing deadline, and does the report distinguish practice status from game status?", "have": "Yes: the league's important-dates page quotes the Personnel (Injury) Report Policy filing pattern and bars estimated practice status on a practice day; the report itself carries practice status and Out/Doubtful/Questionable.", "missing": "Nothing further for the baseline; per-club filing compliance is not tracked.", "blocking": "No — answered from the official source.", "answered": "Official source says practice reports are filed at set times before gameday and that an estimated practice report is not acceptable on a practice day (S-06).", "status": "ANSWERED (source-linked)"},
    {"id": "Q-06", "area": "Injuries", "question": "Is a blank game-status field the same as 'will play'?", "have": "No. At capture every 49ers and Cowboys player had a blank game status while 6 and 9 players respectively were DNP — so blank means 'not yet designated'.", "missing": "Nothing; the official page's structure answers it.", "blocking": "No — answered.", "answered": "Blank game status is not 'active'. It is an undesignated player early in the week.", "status": "ANSWERED (source-linked)"},
    {"id": "Q-07", "area": "Injuries", "question": "How do we detect a 3rd/4th-string player on the field?", "have": "Official depth charts list 2nd and sometimes 3rd string; 49ers LCB, NB, RG, RT, FB, P, K, LS have no listed backup (verified 11/10/26).", "missing": "Weekly capture for all 32 clubs, plus inactives (published on club sites gameday).", "blocking": "Yes for the depth-deficiency feature you asked for.", "answered": "", "status": "OPEN"},
    {"id": "Q-08", "area": "Injuries", "question": "Do we treat a player on injured reserve as out for the model?", "have": "The repo does not capture IR moves; clubs publish them as news.", "missing": "An IR/reserve tracker (clubs announce these in their news feeds).", "blocking": "No, but without it injury depth is understated.", "answered": "", "status": "OPEN"},
    {"id": "Q-09", "area": "Schedule", "question": "Are the 2026 NFL rows complete and correct?", "have": "329 NFL rows; 272 regular-season, 48 preseason, plus postseason anchors. All 14 Week-10 rows match NFL.com kickoff times exactly (verified line by line).", "missing": "49 preseason rows still lack exact dates (the official PDF lists only week ranges).", "blocking": "No for 2026 regular season.", "answered": "2026 regular-season rows verified for Week 10 (14/14).", "status": "PARTIALLY ANSWERED"},
    {"id": "Q-10", "area": "Schedule", "question": "Is the 49ers Week 11 game in Mexico City, and does that change rest/travel inputs?", "have": "49ers.com lists Week 11 vs Vikings at Estadio Banorte, 5:20 PM PST, NBC; the league row carries no venue.", "missing": "Confirmation of the league's venue field and any neutral-site designation; travel/rest model inputs.", "blocking": "Only for ST-08.", "answered": "", "status": "FLAGGED — see FL-03"},
    {"id": "Q-11", "area": "Strategy", "question": "What counts as a 'win' for a strategy: profit, CLV, or beating a control?", "have": "This section proposes CLV with a control strategy (ST-12) and publishes the reward rules before any result exists.", "missing": "Your ratification of the scoring rule (LB-02/LB-04).", "blocking": "Yes — the leaderboard cannot rank without it.", "answered": "", "status": "NEEDS YOUR DECISION"},
    {"id": "Q-12", "area": "Strategy", "question": "How many bets must a strategy place before it is ranked?", "have": "A proposed floor of 200 settled bets (LB-03).", "missing": "Ratification; at 12 strategies and one season, 200 each may exceed the available slates.", "blocking": "Yes — feasibility of the whole competition.", "answered": "", "status": "NEEDS YOUR DECISION"},
    {"id": "Q-13", "area": "Strategy", "question": "What reward actually creates the incentive you want?", "have": "Nothing; intentionally blank (LB-08).", "missing": "A currency: scoreboard standing, a share of a pool, or something else.", "blocking": "Yes — 'rewards' is your design choice.", "answered": "", "status": "OPEN"},
    {"id": "Q-14", "area": "Strategy", "question": "Do parlays and prop combos compete in the same table as singles?", "have": "Recommendation: yes, as separate contestants with correlation attached (LB-07).", "missing": "Your ratification.", "blocking": "No, if the recommendation is accepted.", "answered": "", "status": "NEEDS YOUR DECISION"},
    {"id": "Q-15", "area": "Strategy", "question": "What is the minimum correlation magnitude before a combo is rejected?", "have": "No measured correlations; a rule is needed before measurement so the test is pre-registered.", "missing": "A threshold (proposal: reject a combo if |rho| > 0.30 unless its joint edge survives the re-price).", "blocking": "Yes for G8.", "answered": "", "status": "OPEN"},
    {"id": "Q-16", "area": "Data quality", "question": "Why is the source snapshot stale, and is that acceptable?", "have": "Snapshot 2026-11-02, rebuild 2026-11-13 (11 days). The fetch workflow triggers only on a superseded branch name and has no cron.", "missing": "A decision to fix triggers or to accept stale data with a label.", "blocking": "No, but it limits every 'current' claim.", "answered": "Cause identified and evidenced (A-07/SUG-08).", "status": "ANSWERED (cause known)"},
    {"id": "Q-17", "area": "Data quality", "question": "What does the existing verification actually prove?", "have": "It proves structure: every row has an official-host URL, internal links resolve, JSON parses, JS compiles. It does not re-read the sources.", "missing": "A sampled source-content re-check (this session does one week and one club).", "blocking": "No, but it bounds every confidence claim.", "answered": "Answered by reading scripts/verify.py.", "status": "ANSWERED (source-linked)"},
    {"id": "Q-18", "area": "Data quality", "question": "Are duplicate event ids a defect?", "have": "30 duplicate ids, all MLB gamePk pairs across an original and a rescheduled date (documented in prior sessions and re-measured).", "missing": "Nothing; behaviour is understood and intentional.", "blocking": "No.", "answered": "Not a defect — rescheduled doubleheaders/dates by design.", "status": "ANSWERED"},
    {"id": "Q-19", "area": "Legal", "question": "Is a private strategy competition with rewards lawful where you are?", "have": "Nothing in the repo addresses it; this is not legal advice.", "missing": "Local advice on private contests, and whether 'rewards' means money.", "blocking": "Yes, before any reward is paid (D-07).", "answered": "", "status": "OPEN — outside agent competence"},
    {"id": "Q-20", "area": "Scope", "question": "Should this lab share the vacation dashboard's data or stay isolated?", "have": "It is isolated in `data/nfl-lab/` and its own scripts, so it cannot break the free-time dashboard.", "missing": "A decision if shared injury/depth data should later feed the radio-free-time model (it would not change busy windows today).", "blocking": "No.", "answered": "", "status": "OPEN"},
    {"id": "Q-21", "area": "Operations", "question": "Who owns the weekly capture if it is automated?", "have": "GitHub Actions exists but its NFL-related workflow is bound to a superseded branch.", "missing": "A decision on the branch trigger and on artifact retention.", "blocking": "No, but automation will silently stop otherwise.", "answered": "", "status": "OPEN"},
    {"id": "Q-22", "area": "Injuries", "question": "Can we tell a 'starter' from a 'backup' without the depth chart?", "have": "No. The injury report lists players, not roles; only the depth chart maps a player to a slot. Both are needed and both are official.", "missing": "Nothing; the method is settled (join injury rows to depth-chart slots).", "blocking": "No — method answered.", "answered": "Join on club+player; slot comes from the club's own chart.", "status": "ANSWERED"},
]

# --------------------------------------------------------------------------
# 10. Decision register — the reviewable list of paths you can choose.
# --------------------------------------------------------------------------
DECISION_ROWS = [
    {"id": "D-01", "decision": "Build the results archive first", "option_a": "Yes: capture finals weekly starting now (SUG-01).", "option_b": "No: keep the site descriptive only.", "recommend": "A", "why": "Everything about skill, luck and rewards is impossible without settled outcomes. It is also the cheapest item on the list.", "evidence": "A-05: 0 result rows in the repo; gates G4–G7 all FAIL.", "review": "After 8 weeks of capture, re-check gate G4.", "status": "AWAITING YOUR CHOICE"},
    {"id": "D-02", "decision": "Snapshot the injury report daily", "option_a": "Yes, per club, timestamped (SUG-02).", "option_b": "No: keep only the current week.", "recommend": "A", "why": "A status with no timestamp cannot be shown to precede kickoff (gate G2), so no injury signal can be validated.", "evidence": "Q-05/Q-06: the official page changes through the week.", "review": "At the next gate review.", "status": "AWAITING YOUR CHOICE"},
    {"id": "D-03", "decision": "Market lines: license a feed", "option_a": "License closing (and opening) line data.", "option_b": "Do not; restrict the site to origination methodology and drop P&L claims.", "recommend": "Depends on budget — flagged, not assumed", "why": "The NFL publishes no lines. Without a feed, G6 and the reward tiers cannot operate.", "evidence": "A-06: no odds data anywhere in the repo; Q-01.", "review": "Before any leaderboard ranking is attempted.", "status": "AWAITING YOUR CHOICE"},
    {"id": "D-04", "decision": "If no feed: publish 'originated lines' as a methodology only", "option_a": "Yes — show the exact construction rule and mark every output BLANK until an effect size has an official source.", "option_b": "Publish model numbers anyway.", "recommend": "A", "why": "Option B would require inventing effect sizes, which your verification rule forbids.", "evidence": "Effect sizes are not published by any official source (verified: NFL.com publishes stats, not marginal effects).", "review": "On any future feed decision.", "status": "AWAITING YOUR CHOICE"},
    {"id": "D-05", "decision": "Expand depth capture to all 32 clubs", "option_a": "Yes (SUG-04).", "option_b": "Stay with the 49ers focus.", "recommend": "A", "why": "Deficiency tracking only becomes decision-grade when it covers the opponent too, and the opponent is the other half of every game.", "evidence": "S-02: only the 49ers chart is transcribed; 9 slots have no documented backup.", "review": "Weekly.", "status": "AWAITING YOUR CHOICE"},
    {"id": "D-06", "decision": "What the reward is", "option_a": "Standing only (no payout).", "option_b": "A pool or other consideration.", "recommend": "A until Q-19 is answered", "why": "The legal question (Q-19) is unresolved and outside the agent's competence.", "evidence": "LB-08 is deliberately blank.", "review": "After local legal advice.", "status": "BLOCKED ON Q-19"},
    {"id": "D-07", "decision": "Ranking metric", "option_a": "CLV with a bootstrap variance penalty (LB-02/LB-04).", "option_b": "Units of profit.", "recommend": "A", "why": "Profit at small samples is dominated by luck; CLV measures whether the price was beaten.", "evidence": "G7 cannot separate luck from profit without a large sample.", "review": "After the first 200 settled bets.", "status": "AWAITING YOUR CHOICE"},
    {"id": "D-08", "decision": "Correlation policy for combos", "option_a": "Pre-register a threshold (proposal |rho| > 0.30 rejects unless the joint edge survives).", "option_b": "Decide per combo after seeing results.", "recommend": "A", "why": "Deciding after seeing results is the definition of overfitting.", "evidence": "C-01…C-08 all blank; Q-15 open.", "review": "Before the first combo is ranked.", "status": "AWAITING YOUR CHOICE"},
    {"id": "D-09", "decision": "Fix the refresh pipeline", "option_a": "Retarget the workflow to `main` and add a weekly cron (SUG-08).", "option_b": "Leave it and label data as stale.", "recommend": "A", "why": "A dashboard whose sources are 11 days old is not decision-grade.", "evidence": "A-07.", "review": "Immediately after merge.", "status": "AWAITING YOUR CHOICE"},
    {"id": "D-10", "decision": "Retire the legacy NFL file", "option_a": "Delete `data/nfl-2026.json`.", "option_b": "Keep it with `verified: false`.", "recommend": "A", "why": "It asserts verified while citing non-official sites, and nothing renders from it except the audit page.", "evidence": "FL-01.", "review": "At merge.", "status": "AWAITING YOUR CHOICE"},
]

# --------------------------------------------------------------------------
# 11. Line-origination worksheet: what a number would require, for one game.
# --------------------------------------------------------------------------
LINE_WORKSHEET = [
    {"id": "LW-01", "input": "Kickoff time and date", "value": "2026-11-15, 1:25 PM PST (4:25 PM ET)", "status": "AVAILABLE — official", "source": "S-05"},
    {"id": "LW-02", "input": "Teams and home/away", "value": "San Francisco 49ers at Dallas Cowboys", "status": "AVAILABLE — official", "source": "S-05"},
    {"id": "LW-03", "input": "Venue", "value": "AT&T Stadium (49ers.com schedule)", "status": "AVAILABLE — official (club)", "source": "S-04"},
    {"id": "LW-04", "input": "Team records entering the game", "value": "SF 7-1, DAL 4-5", "status": "AVAILABLE — official", "source": "S-01"},
    {"id": "LW-05", "input": "Injury designations", "value": "12 49ers listed (6 DNP), 18 Cowboys listed (9 DNP); no game statuses issued at capture", "status": "AVAILABLE — official, but time-sensitive", "source": "S-01"},
    {"id": "LW-06", "input": "Depth-chart replacements for any DNP starter", "value": "49ers chart known (9 slots have no documented backup); Cowboys chart not captured", "status": "PARTIAL", "source": "S-02"},
    {"id": "LW-07", "input": "Rest days / travel", "value": "Both teams last played 2026-11-08 and 2026-11-09 respectively; travel distance not published", "status": "PARTIAL — dates official, distance not official", "source": "S-04"},
    {"id": "LW-08", "input": "Scoring baseline for a neutral matchup", "value": "", "status": "MISSING — the NFL publishes results, not a baseline model", "source": "S-08"},
    {"id": "LW-09", "input": "Marginal effect of a missing starter on points", "value": "", "status": "MISSING — no official source publishes effect sizes", "source": "S-07"},
    {"id": "LW-10", "input": "Market opening and closing numbers", "value": "", "status": "MISSING — the league publishes none", "source": "S-08"},
    {"id": "LW-11", "input": "Weather at kickoff", "value": "", "status": "MISSING — no official NFL weather feed in this repo (indoor venue here, so less material)", "source": "S-05"},
    {"id": "LW-12", "input": "Therefore: the originated number", "value": "", "status": "BLANK BY RULE — any number would be fabricated; see D-04", "source": "S-07"},
]

# --------------------------------------------------------------------------
# 12. Repository audit rows. `source_kind` is "repo" for our own files.
# --------------------------------------------------------------------------
AUDIT_ROWS = [
    {"id": "A-01", "area": "Freshness", "finding": "Before this branch was rebased, `main` still served a stale 'today': `data/official/meta.json` carried `system_today` 2026-11-05 on 2026-11-13 because nothing had rebuilt the dashboard since the previous session.", "severity": "High", "action": "FIXED (2026-11-13): the collector (which derives the Pacific date at run time) was re-run and the site rebuilt. Verified on the rebased branch: `system_today` is 2026-11-13, event rows unchanged at 6,591, and `python3 -m unittest tests/test_dashboard_generator.py` passes (that test was failing on the pre-rebuild tree).", "source": "S-11", "verified": "Read of meta.json before and after; test re-run."},
    {"id": "A-02", "area": "Freshness", "finding": "Official-source snapshot is 2026-11-02 while the rebuild is 2026-11-13 — 11 days stale. The site does disclose the snapshot timestamp on every page.", "severity": "High", "action": "Disclosure already present; root cause logged as A-07. No data was assumed to be current.", "source": "S-11", "verified": "meta.json source_snapshot_utc vs generated_utc."},
    {"id": "A-03", "area": "NFL rows", "finding": "All 14 Week-10 NFL rows were checked against NFL.com's Week-10 page: 14/14 matchups, kickoff times (ET->PT), and home/away order match. One row (SF at DAL) also matches 49ers.com, which lists 1:25 PM PST.", "severity": "None (pass)", "action": "No change. This is the only full-week source-content re-check performed; other weeks were not re-read.", "source": "S-05", "verified": "Line-by-line read of both pages."},
    {"id": "A-04", "area": "NFL rows", "finding": "Venue is populated on only 3 of 329 NFL rows, and only 251 of 329 carry a start timestamp.", "severity": "Medium", "action": "Left as-is (out of this session's data scope). Consequence documented: venue-dependent signals (neutral site, travel) cannot be computed for 326 rows.", "source": "S-10", "verified": "Field-coverage count over events.json."},
    {"id": "A-05", "area": "NFL rows", "finding": "No game results (final scores) are stored anywhere in the repository: the event schema has no score, result or winner field, and no results JSON exists in data/ or data/nfl/.", "severity": "High", "action": "Blocks every validation gate that needs settled outcomes (G4–G9). Recommendation SUG-01; decision D-01. Note: this is the same conclusion the NFL module merged in PR #45 reached from its own gate (its leaderboard is likewise unranked).", "source": "S-10", "verified": "Schema key enumeration and full-text search for score/result fields across data/, data/nfl/ and research/."},
    {"id": "A-06", "area": "NFL rows", "finding": "No odds, line, spread, total or moneyline data exists in the repository, and the NFL does not publish such data, so it cannot be collected from an official source.", "severity": "High", "action": "Documented as a hard constraint; gates G6/G7 cannot pass from official data alone (Q-01, D-03).", "source": "S-08", "verified": "Full-text search across data/, research/ and scripts/."},
    {"id": "A-07", "area": "Pipeline", "finding": "`fetch-official.yml` triggers on push only for the branch `arena/72e6d3f7-korea4` and has no `schedule:`, so pushes to `main` never refresh official sources; the same superseded branch name appears in `check.yml` and `probe-sources.yml`.", "severity": "High", "action": "Recommended fix (SUG-08). Not changed here: workflow files are shared and outside this session's claimed scope.", "source": "S-12", "verified": "Read of the four workflow files in .github/workflows/."},
    {"id": "A-08", "area": "Data integrity", "finding": "30 duplicate event ids exist, all MLB `gamePk` pairs where the same game appears on its original and rescheduled date.", "severity": "Low (documented)", "action": "No change; confirmed intentional and already recorded by prior sessions.", "source": "S-10", "verified": "Duplicate-id scan (6591 rows, 30 duplicated ids)."},
    {"id": "A-09", "area": "Verification", "finding": "`scripts/verify.py` proves structure only: every row carries an official-host URL, internal links resolve, JSON parses and JS compiles. It does not fetch or re-read any source.", "severity": "Medium", "action": "Stated plainly on this site; a source-content sample check was added this session (A-03). New section has its own stricter gate.", "source": "S-14", "verified": "Read of verify.py and cross-check against its own report text."},
    {"id": "A-10", "area": "Verification", "finding": "5 of 10,062 primary rows resolve their source through the build's fallback URL (95.7 The Game) because the row's own source field is empty. All 5 fallback hits are the 95.7 The Game source-catalogue rows themselves, so no data row is mis-sourced.", "severity": "None (pass, after inspection)", "action": "No change; recorded so a future reviewer does not misread the fallback as a defect.", "source": "S-14", "verified": "Row-level scan of every generated page for the fallback URL."},
    {"id": "A-11", "area": "Data integrity", "finding": "`data/nfl-2026.json` sets `\"verified\": true` while citing legionreport.com, printablepedia.com and skysports.com — none of which are official — and it puts the 49ers at home for the Melbourne opener, whereas NFL.com and the row table have the 49ers as the away team.", "severity": "Medium", "action": "Published as FL-01. Deletion recommended (D-10); not deleted because deleting data needs your approval.", "source": "S-13", "verified": "Read of the file; compared with NFL.com Week-1 row and 49ers.com."},
    {"id": "A-12", "area": "Injuries", "finding": "There was no injury, depth-chart or player-stat data in the repository before 2026-11-13. Two sessions then captured it independently on the same day: `data/nfl/injury-snapshot-2026-11-13.json` (merged in PR #45) and `data/nfl-lab/injuries.json` + `depth-49ers.json` (this section). The captures agree on the Week-10 injury list.", "severity": "Medium", "action": "Duplicate capture logged as a coordination finding (A-14). This section adds the piece the merged module lacks: the official per-club depth chart with its empty backup slots, which is what makes a 2nd/3rd-string replacement identifiable rather than inferred.", "source": "S-10", "verified": "Directory listing and a field-by-field comparison of the two injury captures."},
    {"id": "A-13", "area": "Site", "finding": "Two generated pages are very large: `mlb.html` 4.9 MB and `review.html` 2.3 MB, with all rows inline in the HTML; the whole served HTML is about 8.8 MB.", "severity": "Medium", "action": "Recommended split (SUG-07). Not changed: those pages belong to the main build, not this session's scope.", "source": "S-14", "verified": "File sizes on disk."},
    {"id": "A-14", "area": "Coordination", "finding": "Five other sessions claimed overlapping NFL line-origination work on 2026-11-13 (`c1806a8e`, `85a71078`, `21f65504`, `3b442c81`, `a7381587`). By the time this branch was finished, `a7381587` had already been merged to `main` as PR #45 with four NFL pages, a decision module and its own 10-item suggestions list — overlapping roughly 60% of this section's content.", "severity": "High", "action": "Rebased onto `main` and reconciled instead of duplicating: this section kept its own file scope (`scripts/nfl_lab_*`, `data/nfl-lab/`, `nfl-decision-*.html`), reused none of the merged module's data, and repointed its findings so it no longer claims credit for fixes made elsewhere. The overlap is described on the section's overview and in COORDINATION.md so the owner can pick one home for the program.", "source": "S-16", "verified": "Read of `origin/main` history, PR #45's diff, and the merged module's data files."},
]

# --------------------------------------------------------------------------
# 13. Flags for the Flagged-for-Review page of this section.
# --------------------------------------------------------------------------
FLAG_ROWS = [
    {"id": "FL-01", "issue": "`data/nfl-2026.json` says `verified: true` but cites three non-official sites and contradicts the official home/away for Week 1 (Melbourne).", "status": "UNRESOLVED — recommended for deletion (D-10)", "impact": "None today: nothing renders from it except the audit page. It would mislead anyone who reuses it.", "source": "S-13"},
    {"id": "FL-02", "issue": "Official-source snapshot is 11 days old at rebuild (2026-11-02 vs 2026-11-13); the scheduled refresh workflow is bound to a superseded branch name.", "status": "UNRESOLVED — fix recommended (SUG-08)", "impact": "Schedules released or changed after 2026-11-02 may be missing; injury and line work is unaffected (captured live this session).", "source": "S-12"},
    {"id": "FL-03", "issue": "49ers.com lists Week 11 (2026-11-22, vs Vikings) at Estadio Banorte, 5:20 PM PST, NBC, while the league-sourced row in `events.json` carries no venue and no international marker.", "status": "FLAGGED AS UNVERIFIED — venue not confirmed on the league page in this session", "impact": "Neutral-site/rest models (ST-08) cannot use this row until the venue is confirmed from a league source.", "source": "S-04"},
    {"id": "FL-04", "issue": "Injury report was captured mid-week: all 49ers and Cowboys game-status fields were blank while 15 players combined were listed as Did Not Participate.", "status": "TIME-SENSITIVE — re-capture required before any game-day decision", "impact": "A blank game status must never be read as 'active'.", "source": "S-01"},
    {"id": "FL-05", "issue": "The official 49ers depth chart lists no backup at 9 slots (LCB, NB, RG, RT, FB, P, K, H, LS).", "status": "UNVERIFIABLE FROM OFFICIAL SOURCE — replacement quality unknown", "impact": "A '3rd/4th string' claim at these slots would be an inference, so none is made.", "source": "S-02"},
    {"id": "FL-06", "issue": "Every correlation value in this section is blank, and every strategy fails at least one gate; the leaderboard has no entries.", "status": "BY DESIGN — not a defect", "impact": "The competition cannot start until results and market lines exist (D-01, D-03). No official source publishes these values, which is exactly why they are blank.", "source": None, "no_source": True},
]

# --------------------------------------------------------------------------
# 14. Executive summary body (rendered to HTML and to Markdown).
# --------------------------------------------------------------------------
HEADLINE_METRICS = [
    {"label": "NFL rows in the dashboard", "value": "329", "note": "272 regular season, 48 preseason, plus postseason anchors"},
    {"label": "Week-10 rows re-read against NFL.com", "value": "14 of 14 match", "note": "matchup, kickoff and home/away"},
    {"label": "Strategies designed", "value": "12", "note": "singles, parlays, player-prop combos, derivatives"},
    {"label": "Strategies that passed every gate", "value": "0", "note": "leaderboard is empty by design"},
    {"label": "Validation gates defined", "value": "10", "note": "3 structural, 6 data, 1 process"},
    {"label": "Open questions", "value": "22", "note": "7 answered from official sources"},
    {"label": "Suggestions published", "value": "12", "note": "2 already implemented in this section"},
    {"label": "Injury rows transcribed", "value": "27", "note": "nfl.com Week 10, source-linked"},
    {"label": "49ers depth slots captured", "value": "28", "note": "official chart dated 11/10/26"},
    {"label": "Depth slots with no documented backup", "value": "9", "note": "flags FL-05"},
    {"label": "Repo findings", "value": "14", "note": "1 fixed, 3 pass, 10 open"},
]

SUMMARY_SECTIONS = [
    {"id": "ES-01", "heading": "What was asked and what now exists", "body": "You asked for a requirements-driven collection and analysis build, suggestions with a reviewable section, an explicit list of questions and missing information, an own-line origination system run as a leaderboard with validation gates, correlation analysis, luck removal, injury and backup-depth tracking, an executive summary, a clean category-organized site and a line-by-line repo review. This section delivers each as a page: Landing, Strategies and leaderboard, Validation gates, Injuries and depth, Suggestions, Open questions, Decision register and Repo audit — all reachable from the single 'NFL decision' navigation entry."},
    {"id": "ES-02", "heading": "The one honest headline", "body": "No strategy can currently be shown to be skill-based. The repository stores schedules and it stores no results and no market prices, so the gates that separate skill from luck (sample size, holdout, closing-line benchmark, bootstrap luck test) cannot run. Rather than publish a leaderboard of unvalidated picks, this section publishes the gates, the reward rules and an empty leaderboard, and states exactly what is missing."},
    {"id": "ES-03", "heading": "Own-line origination", "body": "A line is a probability in points. Producing one requires a scoring baseline, the measured effect of each input, and a price to test against. The NFL publishes the inputs (schedule, records, injury designations, player volume) but not a baseline, not effect sizes and not prices. The worksheet for one game (49ers at Cowboys, Week 10) shows 7 inputs available, 2 partial and 4 missing, so the originated number is left blank by rule instead of fabricated."},
    {"id": "ES-04", "heading": "Injuries and backup depth", "body": "Injury tracking is now source-linked: 27 transcribed rows from the league's own Week-10 report, joined to the 49ers' official depth chart (updated 11/10/26). The join produces the number you asked for: 6 of 23 starting slots were on the report as Did Not Participate and one more as Limited at capture. It also produces an uncomfortable answer: at 9 slots the official chart names no backup at all, including left cornerback and nickel back — precisely where a third-string player would have to appear. That gap is flagged rather than filled in."},
    {"id": "ES-05", "heading": "Correlation and luck", "body": "Eight correlation pairs are registered with expected sign, the affected strategies and an explicit reason the value is blank. The rule is pre-registered: no combo is priced until its correlation is measured on settled legs, and the proposed rejection threshold (|rho| > 0.30) must be fixed before measurement, not after. Luck is handled by construction: the ranking metric is closing-line value, not profit, and the score subtracts the strategy's own 5th-percentile bootstrap result."},
    {"id": "ES-06", "heading": "What the review found", "body": "The dashboard's 'today' had gone stale (2026-11-05 while the date was 2026-11-13) and is fixed in this branch. The source snapshot is 11 days old because the refresh workflow is bound to a superseded branch name. 14 of 14 Week-10 rows match the league page exactly. A legacy file still calls non-official data 'verified'. Large pages (4.9 MB and 2.3 MB) are slow to review. Five concurrent sessions claimed overlapping NFL work today, which is called out on the board."},
    {"id": "ES-07", "heading": "What you must decide", "body": "Ten decisions are registered; four are truly blocking. (1) Capture results now (D-01). (2) Snapshot injury reports with timestamps (D-02). (3) Either license line data or accept that profitability can never be claimed (D-03/D-04). (4) Fix the refresh pipeline (D-09). The rest — reward currency, ranking metric, correlation threshold, depth-chart coverage — are choices only you can make, and each is written out with a recommendation and the evidence behind it."},
    {"id": "ES-08", "heading": "What is deliberately not claimed", "body": "No profit, no edge, no correlation value, no effect size, no third-string identification, no 'best path'. Every one of those would have required a number that no official source provides. Blank cells are evidence of a gap, not a missing feature."},
]

CATEGORIES = [
    {
        "slug": "nfl-decision.html", "page": "nfl-decision.html", "title": "NFL Lab — overview",
        "blurb": "Decision-support home: headline metrics, what exists, and the eight sections below.",
    },
    {
        "slug": "nfl-decision-strategies.html", "page": "nfl-decision-strategies.html", "title": "Strategies & leaderboard",
        "blurb": "12 designed strategies across singles, parlays, player-prop combos and derivatives; leaderboard rules; empty-by-design leaderboard.",
    },
    {
        "slug": "nfl-decision-validation.html", "page": "nfl-decision-validation.html", "title": "Validation gates",
        "blurb": "10 gates, each with a rule, a test and its current result; the gate matrix per strategy.",
    },
    {
        "slug": "nfl-decision-correlation.html", "page": "nfl-decision-correlation.html", "title": "Correlation & luck",
        "blurb": "8 correlation pairs with pre-registered rules; why every value is blank; the luck-separation method.",
    },
    {
        "slug": "nfl-decision-injuries.html", "page": "nfl-decision-injuries.html", "title": "Injuries & depth",
        "blurb": "Official Week-10 injury rows, the 49ers depth chart, starting-slot availability and the 9 slots with no documented backup.",
    },
    {
        "slug": "nfl-decision-suggestions.html", "page": "nfl-decision-suggestions.html", "title": "Suggestions",
        "blurb": "12 proposals, each with rationale, measurement and effort — the review-and-choose list.",
    },
    {
        "slug": "nfl-decision-questions.html", "page": "nfl-decision-questions.html", "title": "Open questions",
        "blurb": "22 questions with what we have, what is missing, and whether it blocks a decision.",
    },
    {
        "slug": "nfl-decision-decisions.html", "page": "nfl-decision-decisions.html", "title": "Decision register",
        "blurb": "10 paths, two options each, a recommendation and the evidence behind it.",
    },
    {
        "slug": "nfl-decision-audit.html", "page": "nfl-decision-audit.html", "title": "Repo audit",
        "blurb": "14 findings from the line-by-line review, with the check performed and the action taken.",
    },
    {
        "slug": "nfl-decision-flags.html", "page": "nfl-decision-flags.html", "title": "Flagged for review",
        "blurb": "6 items that are unresolved, unverifiable or deliberately blank — with source links.",
    },
    {
        "slug": "nfl-decision-executive.html", "page": "nfl-decision-executive.html", "title": "Executive summary",
        "blurb": "One page: what exists, the honest headline, and what you must decide.",
    },
]


# --------------------------------------------------------------------------
# Writers
# --------------------------------------------------------------------------
def _json_rows(rows):
    return [{k: v for k, v in r.items()} for r in rows]


def attach_sources():
    """Attach official source fields to every row that names a source id."""
    for name in ("INJURY_ROWS", "INJURY_COVERAGE", "LINE_WORKSHEET", "AUDIT_ROWS", "FLAG_ROWS"):
        rows = globals()[name]
        for r in rows:
            sid = r.get("source")
            if not sid:
                continue
            s = SOURCE_BY_ID[sid]
            r["source_url"] = s["url"]
            r["source_label"] = f'{s["publisher"]} — {s["title"]}'
            r["source_kind"] = s["source_kind"]
            r["source_checked"] = CAPTURE_LABEL
    for r in STRATEGY_ROWS:
        r["design_note"] = "test specification, not a fact"
    for r in GATE_ROWS:
        r["design_note"] = "rule set by this section"
    for r in LEADERBOARD_RULES:
        r["design_note"] = "rule set by this section"
    for r in SUGGESTION_ROWS:
        r["design_note"] = "proposal, not a fact"
    for r in QUESTION_ROWS:
        r["design_note"] = "question raised by this session"
    for r in DECISION_ROWS:
        r["design_note"] = "choice for you; evidence column cites the check"
    for r in CORRELATION_ROWS:
        r["design_note"] = "value blank by rule"
    repo_url = "https://github.com/karagemop466-tech/Korea4/blob/main/scripts/nfl_lab_data.py"
    for r in HEADLINE_METRICS:
        r["source_url"] = repo_url
        r["source_label"] = "computed — scripts/nfl_lab_data.py"
        r["source_kind"] = "repo"
        r["source_checked"] = CAPTURE_LABEL
    for r in STRATEGY_ROWS:
        r["design_note"] = "test specification, not a fact"
    for r in GATE_ROWS:
        r["design_note"] = "rule set by this section"
    for r in LEADERBOARD_RULES:
        r["design_note"] = "rule set by this section"
    for r in SUGGESTION_ROWS:
        r["design_note"] = "proposal, not a fact"
    for r in QUESTION_ROWS:
        r["design_note"] = "question raised by this session"
    for r in DECISION_ROWS:
        r["design_note"] = "choice for you; evidence column cites the check"
    for r in CORRELATION_ROWS:
        r["design_note"] = "value blank by rule"
    repo_url = "https://github.com/karagemop466-tech/Korea4/blob/main/scripts/nfl_lab_data.py"
    for r in HEADLINE_METRICS:
        r["source_url"] = repo_url
        r["source_label"] = "computed — scripts/nfl_lab_data.py"
        r["source_kind"] = "repo"
        r["source_checked"] = CAPTURE_LABEL
    for r in DEPTH_ROWS:
        s = SOURCE_BY_ID["S-02"]
        r["source_url"] = s["url"]
        r["source_label"] = f'{s["publisher"]} — {s["title"]}'
        r["source_kind"] = "official"
        r["source_checked"] = "chart updated as of 11/10/26; fetched " + CAPTURE_LABEL


def write_json():
    attach_sources()
    OUT.mkdir(parents=True, exist_ok=True)
    payload = {
        "generated_for": "NFL decision-support section",
        "capture": CAPTURE_LABEL,
        "sources": SOURCES,
        "injuries": INJURY_ROWS,
        "injury_coverage": INJURY_COVERAGE,
        "depth_chart_49ers": DEPTH_ROWS,
        "strategies": STRATEGY_ROWS,
        "gates": GATE_ROWS,
        "correlation": CORRELATION_ROWS,
        "leaderboard": LEADERBOARD_ROWS,
        "leaderboard_rules": LEADERBOARD_RULES,
        "suggestions": SUGGESTION_ROWS,
        "questions": QUESTION_ROWS,
        "decisions": DECISION_ROWS,
        "line_worksheet": LINE_WORKSHEET,
        "audit": AUDIT_ROWS,
        "flags": FLAG_ROWS,
        "summary": SUMMARY_SECTIONS,
        "headline_metrics": HEADLINE_METRICS,
    }
    for fname, key in (
        ("sources.json", "sources"), ("injuries.json", "injuries"),
        ("depth-49ers.json", "depth_chart_49ers"), ("strategies.json", "strategies"),
        ("gates.json", "gates"), ("correlation.json", "correlation"),
        ("leaderboard.json", "leaderboard"), ("suggestions.json", "suggestions"),
        ("questions.json", "questions"), ("decisions.json", "decisions"),
        ("line-worksheet.json", "line_worksheet"), ("audit.json", "audit"),
        ("flags.json", "flags"),
    ):
        (OUT / fname).write_text(json.dumps(payload[key], indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
    return payload


def depth_gaps():
    """Slots where the official chart lists no backup (computed, not asserted)."""
    return [r for r in DEPTH_ROWS if not r.get("backup_1")]


if __name__ == "__main__":
    p = write_json()
    print(json.dumps({
        "sources": len(p["sources"]), "injuries": len(p["injuries"]),
        "depth": len(p["depth_chart_49ers"]), "depth_gaps": len(depth_gaps()),
        "strategies": len(p["strategies"]), "gates": len(p["gates"]),
        "suggestions": len(p["suggestions"]), "questions": len(p["questions"]),
        "decisions": len(p["decisions"]), "audit": len(p["audit"]), "flags": len(p["flags"]),
    }, indent=1))
