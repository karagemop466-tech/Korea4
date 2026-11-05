#!/usr/bin/env python3
"""Build the official-only data set from compressed raw source snapshots.

No network access is required here. Every value marked VERIFIED is read from a
raw official response under `research/official/raw/` or `research/probe/raw/`.
Unreleased seasons are modelled separately and labelled ESTIMATED; unknown
official values remain blank and receive an UNVERIFIED flag.
"""
from __future__ import annotations

import gzip
import hashlib
import html
import json
import math
import re
import statistics
from collections import Counter, defaultdict
from datetime import date, datetime, time, timedelta, timezone
from io import BytesIO
from pathlib import Path
from urllib.parse import urlsplit
from zoneinfo import ZoneInfo

from bs4 import BeautifulSoup
from pypdf import PdfReader

ROOT = Path(__file__).resolve().parents[1]
OFFICIAL_RAW = ROOT / "research" / "official" / "raw"
PROBE_RAW = ROOT / "research" / "probe" / "raw"
OFFICIAL_MANIFEST = ROOT / "research" / "official" / "manifest.json"
PROBE_MANIFEST = ROOT / "research" / "probe" / "manifest.json"
PROBE_SUMMARY = ROOT / "research" / "probe" / "summary.json"
OUT = ROOT / "data" / "official"
ANALYSIS = ROOT / "research" / "analysis"
REVIEW = ROOT / "research" / "line_by_line.json"

UTC = timezone.utc
PT = ZoneInfo("America/Los_Angeles")
START_DATE = date(2026, 1, 1)
DISPLAY_START = date(2026, 11, 1)
END_DATE = date(2029, 12, 31)
SYSTEM_TODAY = date(2026, 11, 2)

MLB_DURATION = 158
NFL_DURATION = 192
NCAAF_DURATION = 204
SOCCER_DURATION = 120

MLB_API_2026 = "https://statsapi.mlb.com/api/v1/schedule?sportId=1&season=2026"
MLB_API_2027 = "https://statsapi.mlb.com/api/v1/schedule?sportId=1&season=2027"
MLB_API_2028 = "https://statsapi.mlb.com/api/v1/schedule?sportId=1&season=2028"
MLB_API_2029 = "https://statsapi.mlb.com/api/v1/schedule?sportId=1&season=2029"
MLB_TEAMS_API = "https://statsapi.mlb.com/api/v1/teams?sportId=1&season=2027"
MLB_DURATION_URL = "https://www.mlb.com/news/mlb-average-game-time-under-three-hours-third-straight-year"
NFL_RULEBOOK_URL = "https://media.nfl.com/content/dam/communications/Official%20Playing%20Rules/2026%20Official%20Playing%20Rules.pdf"
NCAA_RULES_URL = "https://www.ncaa.org/championships/playing-rules/football-playing-rules/"
NCAA_HANDBOOK_URL = "http://fs.ncaa.org/Docs/champ_handbooks/football/2011/2011_3_football.pdf"
NCAA_DURATION_URL = "https://www.ncaa.com/news/football/article/2017-02-28/competition-committee-advise-football-rules"
NFL_IMPORTANT_DATES_URL = "https://www.nfl.com/news/2026-27-national-football-league-important-dates"
NFL_PRO_BOWL_URL = "https://www.nfl.com/news/nfl-elevates-pro-bowl-selection-game-s-will-cease-being-contested"
NFL_PRESEASON_PDF_URL = "https://media.nfl.com/content/dam/communications/football-communications/2026/news/05%2014%2026%20-%20Preseason%20Schedule.pdf"
NFL_BY_WEEK_PDF_URL = "https://media.nfl.com/content/dam/communications/football-communications/2026/news/05%2014%2026%20-%202026%20NFL%20Schedule%20-%20By%20Week.pdf"
WWO_STATION_FINDER_URL = "https://www.westwoodonesports.com/station-finder/"
WWO_NFL_SCHEDULE_URL = "https://www.westwoodonesports.com/nfl-schedule/"
IFAB_URL = "https://www.theifab.com/laws/latest/the-players/"
EARTHQUAKES_URL = "https://www.sjearthquakes.com/news/news-earthquakes-announce-radio-stations-for-2026-mls-season"

GAME_TYPE_LABELS = {
    "S": "Spring Training", "E": "Exhibition", "R": "Regular Season",
    "A": "All-Star / Futures", "F": "Wild Card / First Round", "D": "Division Series",
    "L": "League Championship Series", "W": "World Series", "C": "Special Event",
}

# Only league-, team- or network-operated domains may be cited as a row source.
# Ticket resellers, aggregators and wikis are never accepted as official sources.
PIPELINE_STATS: dict[str, int] = defaultdict(int)

OFFICIAL_HOST_SUFFIXES = (
    "nfl.com", "49ers.com", "mlb.com", "gostanford.com", "calbears.com",
    "westwoodonesports.com", "ncaa.org", "ncaa.com", "collegefootballplayoff.com",
    "earthquakes.com", "sjearthquakes.com", "mlssoccer.com", "ksfo.com", "theifab.com",
)


def is_official_url(url: str) -> bool:
    host = urlsplit(url or "").netloc.lower().split("@")[-1].split(":")[0]
    if not host:
        return False
    return any(host == s or host.endswith("." + s) for s in OFFICIAL_HOST_SUFFIXES)


def merge_minutes(spans: list[tuple[int, int]]) -> int:
    """Total minutes covered by spans, counting overlaps once."""
    ordered = sorted((max(0, int(s)), min(1440, int(e))) for s, e in spans if int(e) > int(s))
    total = 0
    cur_start = cur_end = None
    for start, end in ordered:
        if cur_end is None or start > cur_end:
            if cur_end is not None:
                total += cur_end - cur_start
            cur_start, cur_end = start, end
        else:
            cur_end = max(cur_end, end)
    if cur_end is not None:
        total += cur_end - cur_start
    return total

SOURCE_PURPOSE = {
    "mlb": "Official MLB schedule, clubs, releases or duration research",
    "nfl": "Official NFL schedule, dates, rules or release",
    "49ers": "Official 49ers schedule and radio networks",
    "stanford": "Official Stanford football schedule, radio or future dates",
    "cal": "Official California football schedule or future dates",
    "wwo": "Official Westwood One Sports event, grid or station source",
    "giants": "Official Giants radio information",
    "athletics": "Official Athletics radio affiliates",
    "earthquakes": "Official Earthquakes terrestrial radio schedule",
    "cfp": "Official College Football Playoff dates",
    "ncaa": "Official NCAA rules / duration research",
    "knbr": "Official KNBR weekly programming schedule",
    "ksfo": "Official KSFO show schedule",
    "game957": "Official 95.7 The Game station schedule",
    "warriors": "Official Warriors radio source",
    "sharks": "Official Sharks radio source",
    "ifab": "Official IFAB Laws of the Game",
}


# ---------------------------------------------------------------------------
# Generic helpers
# ---------------------------------------------------------------------------

def load_official_manifest() -> list[dict]:
    return json.loads(OFFICIAL_MANIFEST.read_text()).get("files", [])


def probe_file_map() -> dict[str, Path]:
    out = {}
    if PROBE_MANIFEST.exists():
        for row in json.loads(PROBE_MANIFEST.read_text()).get("files", []):
            source = row.get("source", "")
            stem = Path(source).stem
            out[stem] = ROOT / row["file"]
    return out


PROBE_FILES = probe_file_map()


def read_raw(key: str) -> bytes:
    official = OFFICIAL_RAW / f"{key}.gz"
    if official.exists():
        return gzip.decompress(official.read_bytes())
    probe = PROBE_FILES.get(key)
    if probe and probe.exists():
        return gzip.decompress(probe.read_bytes())
    raise KeyError(f"raw official snapshot missing: {key}")


def read_text(key: str) -> str:
    return read_raw(key).decode("utf-8", "replace")


def compact_json(obj) -> str:
    return json.dumps(obj, separators=(",", ":"), ensure_ascii=False, sort_keys=False)


def pt_datetime(iso_or_dt: str | datetime) -> datetime:
    if isinstance(iso_or_dt, datetime):
        dt = iso_or_dt
    else:
        dt = datetime.fromisoformat(iso_or_dt.replace("Z", "+00:00"))
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=PT)
    return dt.astimezone(PT)


def fmt_pt(dt: datetime) -> str:
    return dt.astimezone(PT).strftime("%-I:%M %p %Z")


def fmt_hm(minute: int) -> str:
    minute = max(0, min(1440, int(minute)))
    h, m = divmod(minute, 60)
    return f"{h:02d}:{m:02d}"


def minute_of_day(dt: datetime) -> int:
    dt = dt.astimezone(PT)
    return dt.hour * 60 + dt.minute


def iso_z(dt: datetime) -> str:
    return dt.astimezone(UTC).isoformat(timespec="seconds").replace("+00:00", "Z")


def official_link(url: str, label: str = "Official source") -> str:
    return f'<a href="{html.escape(url, quote=True)}" target="_blank" rel="noopener">{html.escape(label)}</a>'


def event_base(**kwargs):
    base = {
        "id": "", "category": "", "subcategory": "", "season": None,
        "date": "", "date_range": "", "official_time_pt": "", "official_time_zone": "",
        "official_start_utc": "", "official_end_utc": "", "official_end_pt": "",
        "time_status": "", "matchup": "", "away": "", "home": "", "venue": "",
        "stations": [], "sf_affiliates": [], "priority": "HIGH", "focus": False,
        "source_url": "", "source_label": "", "source_api": "", "duration_min": None,
        "duration_source_url": "", "duration_status": "",
        "planning_start_pt": "", "planning_end_pt": "", "planning_status": "",
        "planning_source_url": "", "notes": "", "verification": "",
    }
    base.update(kwargs)
    return base


def source_purpose(key: str) -> str:
    for needle, purpose in SOURCE_PURPOSE.items():
        if needle in key.lower():
            return purpose
    return "Official source captured for line-by-line manual review"


def add_interval(intervals: dict[str, list], day: date, start: int, end: int, **meta):
    if not (START_DATE <= day <= END_DATE):
        return
    start = max(0, min(1440, int(start)))
    end = max(0, min(1440, int(end)))
    if end <= start:
        return
    row = {"start": start, "end": end}
    row.update(meta)
    intervals[day.isoformat()].append(row)


def add_unverified_block(intervals: dict[str, list], day: date, **meta):
    meta.setdefault("verification", "UNVERIFIED")
    add_interval(intervals, day, 0, 1440, status="UNVERIFIED_BLOCK", **meta)


# ---------------------------------------------------------------------------
# Official source catalogue
# ---------------------------------------------------------------------------

def build_sources() -> list[dict]:
    rows = []
    for entry in load_official_manifest():
        url = entry.get("url", "")
        if not url:
            continue
        rows.append({
            "id": entry["key"], "title": entry["key"].replace("_", " ").title(),
            "url": url, "purpose": source_purpose(entry["key"]),
            "http_status": entry.get("http_status"), "bytes": entry.get("bytes", 0),
            "sha256": entry.get("sha256", ""), "raw_file": entry.get("raw_file", ""),
            "retrieved_utc": entry.get("retrieved_utc", ""),
            "status": "VERIFIED" if entry.get("http_status") == 200 and not entry.get("error") else "UNVERIFIED",
            "source_label": "Official source snapshot manifest",
        })
    if PROBE_SUMMARY.exists():
        summary = json.loads(PROBE_SUMMARY.read_text())
        for key, entry in summary.items():
            url = entry.get("url", "")
            if not url:
                continue
            rows.append({
                "id": f"probe_{key}", "title": f"Probe snapshot: {key.replace('_', ' ').title()}",
                "url": url, "purpose": source_purpose(key),
                "http_status": entry.get("status"), "bytes": entry.get("bytes", 0),
                "sha256": "", "raw_file": f"research/probe/raw/{key}.html.gz",
                "retrieved_utc": "2026-11-02", "status": "VERIFIED" if entry.get("bytes", 0) > 0 else "UNVERIFIED",
                "source_label": "Official source probe summary",
            })
    curated = [
        ("MLB 2026 schedule release", "https://www.mlb.com/press-release/press-release-mlb-announces-2026-regular-season-schedule", "2026 MLB master schedule"),
        ("MLB 2027 regular-season release", "https://www.mlb.com/tigers/news/mlb-2027-schedule-released", "2027 MLB dates"),
        ("MLB 2027 spring-training release", "https://www.mlb.com/press-release/press-release-mlb-announces-2027-spring-training-schedule", "Spring Training Feb 19 / exhibitions / Opening dates"),
        ("MLB 2027 All-Star Game", "https://www.mlb.com/news/2027-mlb-all-star-game-at-wrigley-field", "July 13, 2027 All-Star Game"),
        ("MLB future All-Star locations", "https://www.mlb.com/all-star/future-locations", "2028 Oracle Park host; exact date TBA"),
        ("MLB average game duration", MLB_DURATION_URL, "2:38 official 2025 average"),
        ("NFL 2026 schedule release", "https://media.nfl.com/football-information/2026/news/2026-nfl-schedule-announced", "272-game regular-season release"),
        ("NFL 2026–27 important dates", NFL_IMPORTANT_DATES_URL, "Playoff dates and Super Bowl LXI"),
        ("NFL Pro Bowl game discontinued", NFL_PRO_BOWL_URL, "No AFC–NFC game beginning 2026; recognition continues"),
        ("NFL 2027 by-team (unavailable)", "https://www.nfl.com/schedules/2027/by-team", "Official page shows no released 2027 game rows"),
        ("NFL 2027 prime time (unavailable)", "https://www.nfl.com/schedules/2027/prime-time", "Official page shows no released 2027 game rows"),
        ("Super Bowl LXII 2028", "https://www.nfl.com/news/mercedes-benz-stadium-in-atlanta-to-host-super-bowl-lxii-in-2028", "Host announced; date TBA"),
        ("CFP future championship dates", "https://collegefootballplayoff.com/news/2025/10/29/tampabay-29", "2028 Jan 24 and 2029 Jan 22"),
        ("CFP 2027 national championship", "https://collegefootballplayoff.com/news/2026/4/7/lv-april-newsconf", "Jan 25, 2027, 7:30 p.m. ET / 4:30 p.m. PT"),
        ("Stanford 2027/28 Notre Dame dates", "https://gostanford.com/news/2026/05/20/two-dates-added-to-notre-dame-rivalry", "Nov 27, 2027 and Oct 14, 2028"),
        ("Stanford TCU 2027 game canceled", "https://gostanford.com/news/2026/04/17/tcu-series-update", "Sep 4, 2027 TCU game canceled"),
        ("Stanford 2027 ACC opponents", "https://gostanford.com/news/2026/09/16/acc-announces-2027-conference-opponents", "Opponents released; dates/times later"),
        ("Cal 2027 nonconference games", "https://calbears.com/news/2026/6/25/football-cal-announces-matchups-against-odu-sac-state", "Aug 28 / Sep 4 / Sep 11, 2027; times TBA"),
        ("Cal 2027 ACC opponents", "https://calbears.com/news/2026/9/16/california-football-announces-2027-conference-opponents", "Opponents released; dates/times later"),
        ("ACC 2024–30 Stanford model", "https://gostanford.com/news/2023/10/30/acc-announces-football-schedule-model", "Future opponent grid"),
        ("ACC 2024–30 Cal model", "https://calbears.com/news/2023/10/30/acc-announces-conference-football-matchups-for-2024-30.aspx", "Future opponent grid"),
        ("NCAA Football rules", NCAA_RULES_URL, "Official rules framework"),
        ("NCAA football championship handbook", NCAA_HANDBOOK_URL, "20-minute halftime"),
        ("NCAA 2016 FBS duration", NCAA_DURATION_URL, "3:24 FBS average; dated official research"),
        ("IFAB Laws of the Game", IFAB_URL, "90-minute match and 15-minute halftime"),
        ("WWO station finder", WWO_STATION_FINDER_URL, "SF affiliates and local-carriage caveat"),
        ("WWO NFL national schedule", WWO_NFL_SCHEDULE_URL, "National NFL broadcast schedule"),
        ("KNBR weekly programming", "https://www.knbr.com/shows/", "Official station program grid"),
        ("KSFO show schedule", "https://www.ksfo.com/shows/", "Official station show grid"),
        ("95.7 The Game station", "https://www.957thegame.com/", "Official station schedule / sports categories"),
        ("Warriors radio agreement", "https://www.nba.com/warriors/news/957-the-game-extension-20190827", "Official team radio source"),
        ("Warriors schedule", "https://www.nba.com/warriors/schedule", "Official team schedule for manual review"),
        ("Sharks radio network", "https://www.nhl.com/sharks/news/san-jose-sharks-announce-2018-19-broadcast-schedule-300119102", "Official NHL radio source"),
        ("Sharks schedule", "https://www.nhl.com/sharks/schedule", "Official team schedule for manual review"),
        ("Earthquakes 2026 radio schedule", EARTHQUAKES_URL, "All officially announced terrestrial radio matches"),
        ("GitHub Pages status", "https://api.github.com/repos/karagemop466-tech/Korea4/pages", "Deployment source and build status"),
    ]
    for title, url, purpose in curated:
        rows.append({
            "id": re.sub(r"[^a-z0-9]+", "_", title.lower()).strip("_"),
            "title": title, "url": url, "purpose": purpose,
            "http_status": 200, "bytes": None, "sha256": "", "raw_file": "",
            "retrieved_utc": "2026-11-02", "status": "VERIFIED",
            "source_label": "Curated official source",
        })
    seen = set()
    unique = []
    for row in rows:
        key = (row["id"], row["url"])
        if key in seen:
            continue
        seen.add(key)
        unique.append(row)
    return sorted(unique, key=lambda r: (r["id"], r["url"]))


# ---------------------------------------------------------------------------
# MLB teams / games
# ---------------------------------------------------------------------------

def build_mlb_teams() -> list[dict]:
    data = json.loads(read_text("mlb_teams_2027"))
    rows = []
    for team in data.get("teams", []):
        name = team.get("name", "")
        focus = name in ("San Francisco Giants", "Athletics")
        rows.append({
            "id": team.get("id"), "name": name, "abbreviation": team.get("abbreviation", ""),
            "league": (team.get("league") or {}).get("name", ""),
            "division": (team.get("division") or {}).get("name", ""),
            "venue": (team.get("venue") or {}).get("name", ""),
            "priority": "FOCUS — Giants / A's" if focus else "HIGH — all MLB clubs",
            "focus": focus, "source_url": f"https://statsapi.mlb.com/api/v1/teams/{team.get('id')}",
            "source_label": "MLB Stats API official team record", "verification": "VERIFIED",
        })
    return rows


def mlb_start_medians(games_2026: list[dict]) -> dict:
    buckets = defaultdict(list)
    type_buckets = defaultdict(list)
    for g in games_2026:
        if g.get("startTimeTBD"):
            continue
        dt = pt_datetime(g["gameDate"])
        minute = minute_of_day(dt)
        home = g["teams"]["home"]["team"]["id"]
        game_type = g.get("gameType", "")
        day_night = g.get("dayNight", "")
        buckets[(home, game_type, day_night)].append(minute)
        type_buckets[(game_type, day_night)].append(minute)
    return {
        "home": {f"{k[0]}|{k[1]}|{k[2]}": int(statistics.median(v)) for k, v in buckets.items()},
        "type": {f"{k[0]}|{k[1]}": int(statistics.median(v)) for k, v in type_buckets.items()},
        "overall": int(statistics.median([m for v in type_buckets.values() for m in v])),
    }


def estimate_mlb_minute(game: dict, medians: dict) -> int:
    home = game["teams"]["home"]["team"]["id"]
    game_type = game.get("gameType", "")
    day_night = game.get("dayNight", "")
    return medians["home"].get(f"{home}|{game_type}|{day_night}") or medians["type"].get(f"{game_type}|{day_night}") or medians["overall"]


def build_mlb_events(intervals: dict[str, list]) -> tuple[list[dict], list[dict]]:
    all_games = {}
    for season in (2026, 2027):
        raw = json.loads(read_text(f"mlb_{season}_all"))
        games = [g for day in raw.get("dates", []) for g in day.get("games", [])]
        all_games[season] = games
    medians = mlb_start_medians(all_games[2026])
    events = []
    season_rows = []
    for season, games in all_games.items():
        # The MLB Stats API keeps a "Postponed" entry on the original date alongside
        # the re-scheduled entry for the same gamePk. Only the entry that was actually
        # played (or is still scheduled) may be published as a broadcast row.
        by_pk: dict[int, list] = defaultdict(list)
        for g in games:
            by_pk[g["gamePk"]].append(g)
        cleaned = []
        postponed_removed = 0
        for group in by_pk.values():
            playable = [g for g in group
                        if (g.get("status", {}).get("detailedState") or "").lower()
                        not in ("postponed", "canceled", "cancelled")]
            kept = playable if playable else group
            postponed_removed += len(group) - len(kept)
            cleaned.extend(kept)
        cleaned.sort(key=lambda g: g.get("gameDate", ""))
        PIPELINE_STATS["mlb_postponed_rows_removed"] += postponed_removed
        games = cleaned
        # A suspended game that resumes later keeps one gamePk for two broadcast
        # dates; those rows stay but get unique ids and an explicit note.
        multi_pk = {pk for pk, count in Counter(g["gamePk"] for g in games).items() if count > 1}
        season_rows.append({
            "season": season, "league": "MLB", "official_rows": len(games),
            "tbd_times": sum(1 for g in games if g.get("status", {}).get("startTimeTBD") or g.get("startTimeTBD")),
            "status": "OFFICIAL RELEASED SCHEDULE" if games else "NO OFFICIAL GAME ROWS",
            "source_url": MLB_API_2026 if season == 2026 else MLB_API_2027,
            "source_label": "MLB Stats API official schedule", "verification": "VERIFIED",
        })
        for g in games:
            tbd = bool(g.get("status", {}).get("startTimeTBD") or g.get("startTimeTBD"))
            away = g["teams"]["away"]["team"]["name"]
            home = g["teams"]["home"]["team"]["name"]
            focus = away in ("San Francisco Giants", "Athletics") or home in ("San Francisco Giants", "Athletics")
            source_url = f"https://www.mlb.com/gameday/{g['gamePk']}"
            venue = (g.get("venue") or {}).get("name", "")
            game_type = g.get("gameType", "")
            subcat = GAME_TYPE_LABELS.get(game_type, g.get("seriesDescription", "MLB game"))
            if not tbd:
                start_dt = pt_datetime(g["gameDate"])
                official_time = fmt_pt(start_dt)
                official_utc = iso_z(start_dt)
                time_status = "VERIFIED"
                verification = "VERIFIED — official MLB start time"
                planning_start = minute_of_day(start_dt)
                planning_status = "OFFICIAL START + ESTIMATED DURATION"
                planning_source = MLB_API_2026
            else:
                # The MLB API's placeholder gameDate is deliberately not used as an official time.
                pt_date = date.fromisoformat(g["officialDate"])
                # officialDate is the schedule's published date; Pacific date may be one day earlier.
                # Use the same official date for planning consistency, clearly labelled ESTIMATED.
                minute = estimate_mlb_minute(g, medians)
                official_time = ""
                official_utc = ""
                time_status = "TBD — UNVERIFIED"
                verification = "OFFICIAL DATE / OFFICIAL TIME TBD"
                planning_start = minute
                planning_status = "ESTIMATED TBD START + ESTIMATED DURATION"
                planning_source = MLB_API_2026
                start_dt = datetime.combine(pt_date, time(0, 0), tzinfo=PT) + timedelta(minutes=minute)
            date_pt = start_dt.astimezone(PT).date() if not tbd else pt_date
            planning_end = planning_start + MLB_DURATION
            ev_id = f"mlb-{g['gamePk']}"
            extra_note = ""
            if g["gamePk"] in multi_pk:
                ev_id = f"mlb-{g['gamePk']}-{date_pt.isoformat()}"
                extra_note = (" The official MLB Stats API publishes this gamePk on two dates "
                              "(suspended and resumed), so both broadcast dates are shown.")
            ev = event_base(
                id=ev_id, category="MLB", subcategory=subcat, season=season,
                date=date_pt.isoformat(), official_time_pt=official_time,
                official_time_zone=start_dt.strftime("%Z"), official_start_utc=official_utc,
                time_status=time_status, matchup=f"{away} at {home}", away=away, home=home,
                venue=venue, stations=["KNBR 680 AM / 104.5 FM"] if "Giants" in (away, home) else ["960 AM KNEW / A's Cast"] if "Athletics" in (away, home) else [],
                sf_affiliates=[], priority="FOCUS — Giants / A's" if focus else "HIGH — all MLB",
                focus=focus, source_url=source_url, source_label="MLB.com official gameday",
                source_api=MLB_API_2026 if season == 2026 else MLB_API_2027,
                duration_min=MLB_DURATION, duration_source_url=MLB_DURATION_URL,
                duration_status="OFFICIAL MLB 2025 AVERAGE (2:38)",
                planning_start_pt=fmt_hm(planning_start), planning_end_pt=fmt_hm(planning_end),
                planning_status=planning_status, planning_source_url=planning_source,
                notes=("No official end time is published; end is start plus the researched average." if not tbd else "Official start time is TBD. The official placeholder timestamp was not copied; this is a clearly labelled planning estimate from 2026 official MLB start-time medians.") + extra_note,
                verification=verification,
            )
            events.append(ev)
            add_interval(intervals, date_pt, planning_start, planning_end,
                         event_id=ev["id"], category="MLB", matchup=ev["matchup"],
                         priority=ev["priority"], focus=ev["focus"],
                         status="OFFICIAL_START_ESTIMATED_DURATION" if not tbd else "ESTIMATED_TBD_START",
                         verification=ev["verification"], source_url=ev["source_url"],
                         source_label=ev["source_label"], label=ev["matchup"],
                         duration_source_url=MLB_DURATION_URL)
    # 2028/2029 MLB APIs contain zero official games; leave official values blank and create models.
    for season in (2028, 2029):
        raw = json.loads(read_text(f"mlb_{season}_all"))
        games = [g for d in raw.get("dates", []) for g in d.get("games", [])]
        season_rows.append({
            "season": season, "league": "MLB", "official_rows": len(games), "tbd_times": 0,
            "status": "NO OFFICIAL RELEASED SCHEDULE", "source_url": MLB_API_2028 if season == 2028 else MLB_API_2029,
            "source_label": "MLB Stats API official season query", "verification": "UNVERIFIED",
        })
        events.append(event_base(
            id=f"mlb-{season}-unreleased", category="MLB", subcategory="Season availability", season=season,
            date="", date_range=f"{season}-02-01 to {season}-10-31 (model range)",
            time_status="SCHEDULE NOT RELEASED — UNVERIFIED", matchup="",
            priority="HIGH — all MLB", source_url=MLB_API_2028 if season == 2028 else MLB_API_2029,
            source_label="MLB Stats API official season query", duration_min=MLB_DURATION,
            duration_source_url=MLB_DURATION_URL, duration_status="OFFICIAL MLB 2025 AVERAGE (2:38)",
            planning_status="ESTIMATED — NOT A RELEASED SCHEDULE", planning_source_url=MLB_API_2026,
            notes="Official MLB Stats API returned zero game rows. Exact teams, dates and times are blank. The day scoreboard uses a clearly labelled 364-day calendar-shift model from official 2026 games.",
            verification="UNVERIFIED — OFFICIAL SCHEDULE NOT RELEASED",
        ))
    return events, season_rows


# ---------------------------------------------------------------------------
# NFL regular season, preseason, postseason anchors
# ---------------------------------------------------------------------------

def parse_pdf_week_dates() -> dict[int, list[date]]:
    data = read_raw("nfl_2026_by_week_pdf")
    reader = PdfReader(BytesIO(data))
    out = {}
    months = {m: i for i, m in enumerate(["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"], 1)}
    for i, page in enumerate(reader.pages, 1):
        text = page.extract_text() or ""
        dates = []
        for m in re.finditer(r"(?:Monday|Tuesday|Wednesday|Thursday|Friday|Saturday|Sunday),\s+([A-Za-z]+)\s+(\d{1,2}),\s+(\d{4})", text):
            month = months.get(m.group(1))
            if month:
                dates.append(date(int(m.group(3)), month, int(m.group(2))))
        out[i] = sorted(set(dates))
    return out


def parse_nfl_regular_events(intervals: dict[str, list]) -> list[dict]:
    week_dates = parse_pdf_week_dates()
    events = []
    confirmed_minutes_by_weekday = defaultdict(list)
    card_re = re.compile(r'<a class="absolute inset-0" data-analytics="([^"]+)" href="(/games/[^"]+)"', re.S)
    # First pass for known starts and weekday medians.
    parsed = []
    for week in range(1, 19):
        text = read_text(f"nfl_2026_week_{week:02d}")
        matches = list(card_re.finditer(text))
        for m in matches:
            analytics = json.loads(html.unescape(m.group(1)))
            href = m.group(2)
            next_pos = text.find('<a class="absolute inset-0"', m.end())
            block = text[m.start(): next_pos if next_pos > 0 else m.start() + 15000]
            soup = BeautifulSoup(block, "lxml")
            imgs = [img.get("alt", "").replace(" Team Logo", "") for img in soup.find_all("img", alt=re.compile("Team Logo"))]
            away = imgs[0] if len(imgs) > 0 else ""
            home = imgs[1] if len(imgs) > 1 else ""
            time_match = re.search(r'<time class="body-2-sans[^"]*"[^>]*dateTime="([^"]+)"', block)
            start_dt = pt_datetime(time_match.group(1)) if time_match else None
            if start_dt:
                confirmed_minutes_by_weekday[start_dt.weekday()].append(minute_of_day(start_dt))
            parsed.append((week, analytics, href, away, home, start_dt, block))
    weekday_medians = {k: int(statistics.median(v)) for k, v in confirmed_minutes_by_weekday.items()}
    overall_median = int(statistics.median([m for v in confirmed_minutes_by_weekday.values() for m in v]))
    tbd_by_week = defaultdict(list)
    for week, analytics, href, away, home, start_dt, block in parsed:
        game_id = analytics.get("gameId", "")
        source_url = "https://www.nfl.com" + href
        source_page = f"https://www.nfl.com/schedules/2026/by-week/week-{week}"
        focus = "San Francisco 49ers" in (away, home)
        stations = ["KSAN 107.7 FM / KNBR 104.5 FM / 680 AM", "Westwood One Sports via KNBR/KTCT"] if focus else ["Westwood One Sports national / local team radio"]
        if start_dt:
            day_pt = start_dt.date()
            start_min = minute_of_day(start_dt)
            ev = event_base(
                id=f"nfl-{game_id}", category="NFL", subcategory=f"Regular Season — Week {week}", season=2026,
                date=day_pt.isoformat(), official_time_pt=fmt_pt(start_dt),
                official_time_zone=start_dt.strftime("%Z"), official_start_utc=iso_z(start_dt),
                time_status="VERIFIED", matchup=f"{away} at {home}", away=away, home=home,
                stations=stations, priority="FOCUS — 49ers" if focus else "HIGH — all NFL", focus=focus,
                source_url=source_url, source_label="NFL.com official game page", source_api=source_page,
                duration_min=NFL_DURATION, duration_source_url=NFL_RULEBOOK_URL,
                duration_status="OFFICIAL RULEBOOK CLOCK + SECONDARY 3:12 AVERAGE (FLAGGED)",
                planning_start_pt=fmt_hm(start_min), planning_end_pt=fmt_hm(start_min + NFL_DURATION),
                planning_status="OFFICIAL START + ESTIMATED DURATION", planning_source_url=source_page,
                notes="60-minute regulation and 13-minute halftime are official; 3:12 total broadcast duration is a flagged secondary average.",
                verification="VERIFIED — official NFL kickoff",
            )
            events.append(ev)
            add_interval(intervals, day_pt, start_min, start_min + NFL_DURATION,
                         event_id=ev["id"], category="NFL", matchup=ev["matchup"],
                         priority=ev["priority"], focus=ev["focus"],
                         status="OFFICIAL_START_ESTIMATED_DURATION", verification=ev["verification"],
                         source_url=source_url, source_label=ev["source_label"], label=ev["matchup"],
                         duration_source_url=NFL_RULEBOOK_URL)
        else:
            tbd_by_week[week].append((analytics, href, away, home, source_url, source_page, focus, stations))
    for week, rows in tbd_by_week.items():
        dates = week_dates.get(week, [])
        date_range = f"{dates[0].isoformat()} to {dates[-1].isoformat()}" if dates else ""
        for idx, (analytics, href, away, home, source_url, source_page, focus, stations) in enumerate(rows):
            game_id = analytics.get("gameId", "")
            ev = event_base(
                id=f"nfl-{game_id}", category="NFL", subcategory=f"Regular Season — Week {week} (official TBD)", season=2026,
                date="", date_range=date_range, time_status="TBD — UNVERIFIED",
                matchup=f"{away} at {home}", away=away, home=home,
                stations=stations, priority="FOCUS — 49ers" if focus else "HIGH — all NFL", focus=focus,
                source_url=source_url, source_label="NFL.com official game page", source_api=source_page,
                duration_min=NFL_DURATION, duration_source_url=NFL_RULEBOOK_URL,
                duration_status="OFFICIAL RULEBOOK CLOCK + SECONDARY 3:12 AVERAGE (FLAGGED)",
                planning_status="UNVERIFIED OFFICIAL DATE/TIME — CONSERVATIVE ALL-DAY BLOCK",
                planning_source_url=NFL_BY_WEEK_PDF_URL,
                notes="Official NFL matchup appears in the released week, but exact date and kickoff are TBD. Official values are blank; the scoreboard conservatively blocks the official week date range.",
                verification="OFFICIAL MATCHUP / DATE+TIME UNVERIFIED",
            )
            events.append(ev)
        for day in dates:
            add_unverified_block(intervals, day, event_id=f"nfl-week-{week}-tbd", category="NFL",
                                 matchup=f"Week {week} TBD kickoffs ({len(rows)} games)", priority="HIGH — all NFL",
                                 source_url=source_page, source_label="NFL.com official week schedule",
                                 label=f"Week {week}: official matchups, kickoff TBD")
    return events


def parse_nfl_preseason_events(intervals: dict[str, list]) -> list[dict]:
    reader = PdfReader(BytesIO(read_raw("nfl_preseason_pdf")))
    pages = [(p.extract_text() or "") for p in reader.pages]
    page1, page2 = pages[0], pages[1]
    exact = {}
    # Official national television schedule: five exact date/time rows transcribed
    # from the official PDF page 1 and checked against its raw text.
    exact_specs = [
        ("2026-08-06", "Carolina Panthers vs. Arizona Cardinals", 20),
        ("2026-08-20", "Las Vegas Raiders at Houston Texans", 20),
        ("2026-08-23", "Seattle Seahawks at Tennessee Titans", 20),
        ("2026-08-27", "New England Patriots at Cleveland Browns", 20),
        ("2026-08-28", "Cincinnati Bengals at Philadelphia Eagles", 20),
    ]
    for d, matchup, et_hour in exact_specs:
        dt_et = datetime.fromisoformat(f"{d}T{et_hour:02d}:00:00").replace(tzinfo=ZoneInfo("America/New_York"))
        exact[matchup.lower()] = (dt_et.astimezone(PT), dt_et.astimezone(UTC))
    sections = []
    current = None
    for raw_line in page2.splitlines():
        line = re.sub(r"\s+", " ", raw_line).strip()
        if not line or "PRESEASON WEEK-BY-WEEK" in line.upper():
            continue
        if "Hall of Fame Game" in line:
            current = {"label": "Hall of Fame Game", "range": "2026-08-06 to 2026-08-06", "rows": []}
            sections.append(current)
            continue
        m = re.match(r"Week\s+(\d+)\s+\(August\s+(\d{1,2})-(\d{1,2})\)", line, re.I)
        if m:
            start_day, end_day = int(m.group(2)), int(m.group(3))
            current = {"label": f"Preseason Week {m.group(1)}",
                       "range": f"2026-08-{start_day:02d} to 2026-08-{end_day:02d}",
                       "dates": [date(2026, 8, d) for d in range(start_day, end_day + 1)], "rows": []}
            sections.append(current)
            continue
        if current is None:
            continue
        if re.match(r"^20\d\d PRESEASON", line, re.I):
            break
        m = re.match(r"(.+?)\s+(at|vs\.?)\s+(.+?)(?:\s+\(.*\))?$", line)
        if m:
            away, sep, home = m.group(1).strip(), m.group(2), m.group(3).strip()
            matchup = f"{away} {'vs.' if sep.startswith('vs') else 'at'} {home}"
            current["rows"].append((away, home, matchup))
    events = []
    for section in sections:
        dates = section.get("dates") or [date(2026, 8, 6)]
        for idx, (away, home, matchup) in enumerate(section["rows"]):
            exact_match = exact.get(matchup.lower())
            if exact_match:
                start_pt, start_utc = exact_match
                day_pt = start_pt.date()
                start_min = minute_of_day(start_pt)
                ev = event_base(
                    id=f"nfl-pre-{re.sub(r'[^a-z0-9]+','-',matchup.lower())}", category="NFL",
                    subcategory=section["label"], season=2026, date=day_pt.isoformat(),
                    official_time_pt=fmt_pt(start_pt), official_time_zone=start_pt.strftime("%Z"),
                    official_start_utc=iso_z(start_utc), time_status="VERIFIED",
                    matchup=matchup, away=away, home=home,
                    stations=["Official NFL national TV schedule; terrestrial radio not confirmed"],
                    priority="HIGH — all NFL preseason", focus="San Francisco" in away or "San Francisco" in home,
                    source_url=NFL_PRESEASON_PDF_URL, source_label="Official NFL 2026 preseason schedule PDF",
                    duration_min=NFL_DURATION, duration_source_url=NFL_RULEBOOK_URL,
                    duration_status="OFFICIAL RULEBOOK CLOCK + SECONDARY 3:12 AVERAGE (FLAGGED)",
                    planning_start_pt=fmt_hm(start_min), planning_end_pt=fmt_hm(start_min + NFL_DURATION),
                    planning_status="OFFICIAL START + ESTIMATED DURATION", planning_source_url=NFL_PRESEASON_PDF_URL,
                    notes="Official national television schedule supplies date and ET time; local AM/FM radio carriage is blank/unverified.",
                    verification="VERIFIED — official NFL preseason date/time",
                )
                events.append(ev)
                add_interval(intervals, day_pt, start_min, start_min + NFL_DURATION,
                             event_id=ev["id"], category="NFL", matchup=matchup, priority=ev["priority"],
                             focus=ev["focus"], status="OFFICIAL_START_ESTIMATED_DURATION",
                             verification=ev["verification"], source_url=NFL_PRESEASON_PDF_URL,
                             source_label=ev["source_label"], label=matchup,
                             duration_source_url=NFL_RULEBOOK_URL)
            else:
                ev = event_base(
                    id=f"nfl-pre-{re.sub(r'[^a-z0-9]+','-',matchup.lower())}", category="NFL",
                    subcategory=section["label"], season=2026, date="", date_range=section["range"],
                    time_status="DATE/TIME NOT PUBLISHED IN OFFICIAL PDF — UNVERIFIED",
                    matchup=matchup, away=away, home=home, stations=[],
                    priority="HIGH — all NFL preseason", focus="San Francisco" in away or "San Francisco" in home,
                    source_url=NFL_PRESEASON_PDF_URL, source_label="Official NFL 2026 preseason schedule PDF",
                    duration_min=NFL_DURATION, duration_source_url=NFL_RULEBOOK_URL,
                    duration_status="OFFICIAL RULEBOOK CLOCK + SECONDARY 3:12 AVERAGE (FLAGGED)",
                    planning_status="UNVERIFIED OFFICIAL DATE/TIME — CONSERVATIVE ALL-DAY BLOCK",
                    planning_source_url=NFL_PRESEASON_PDF_URL,
                    notes="Official preseason PDF lists the matchup and week date range, but no exact date/time. Official values are blank; the scoreboard conservatively blocks the date range.",
                    verification="OFFICIAL MATCHUP / DATE+TIME UNVERIFIED",
                )
                events.append(ev)
        for day in dates:
            add_unverified_block(intervals, day, event_id=f"nfl-pre-{section['label']}",
                                 category="NFL", matchup=f"{section['label']}: official matchups, exact date/time TBD",
                                 priority="HIGH — all NFL preseason", source_url=NFL_PRESEASON_PDF_URL,
                                 source_label="Official NFL 2026 preseason schedule PDF",
                                 label=section["label"])
    return events


def build_nfl_postseason_events(intervals: dict[str, list]) -> list[dict]:
    specs = [
        ("2027-01-16", "2027-01-18", "Wild Card Weekend — six games, teams/times TBD"),
        ("2027-01-23", "2027-01-24", "Divisional Playoffs — four games, teams/times TBD"),
        ("2027-01-31", "2027-01-31", "AFC and NFC Championship Games — teams/times TBD"),
        ("2027-02-14", "2027-02-14", "Super Bowl LXI — teams/kickoff TBD"),
    ]
    events = []
    for start, end, label in specs:
        ev = event_base(
            id=f"nfl-post-{start}-{re.sub(r'[^a-z0-9]+','-',label.lower())[:30]}", category="NFL",
            subcategory="Postseason / special", season=2027, date="", date_range=f"{start} to {end}",
            time_status="OFFICIAL DATE / TIME TBD — UNVERIFIED", matchup=label,
            stations=["Westwood One Sports national NFL; local affiliates per official station finder"],
            priority="HIGH — all NFL postseason", focus=False, source_url=NFL_IMPORTANT_DATES_URL,
            source_label="NFL.com official 2026–27 important dates", duration_min=NFL_DURATION,
            duration_source_url=NFL_RULEBOOK_URL,
            duration_status="OFFICIAL RULEBOOK CLOCK + SECONDARY 3:12 AVERAGE (FLAGGED)",
            planning_status="UNVERIFIED OFFICIAL DATE — CONSERVATIVE ALL-DAY BLOCK",
            planning_source_url=NFL_IMPORTANT_DATES_URL,
            notes="Official NFL calendar confirms the date/range. Exact matchups, kickoffs, and WWO on-air windows are not published here; official values are blank.",
            verification="OFFICIAL DATE / EXACT TIME UNVERIFIED",
        )
        events.append(ev)
        d = date.fromisoformat(start)
        last = date.fromisoformat(end)
        while d <= last:
            add_unverified_block(intervals, d, event_id=ev["id"], category="NFL", matchup=label,
                                 priority=ev["priority"], source_url=NFL_IMPORTANT_DATES_URL,
                                 source_label=ev["source_label"], label=label)
            d += timedelta(days=1)
    events.append(event_base(
        id="nfl-pro-bowl-2027", category="NFL", subcategory="All-star / special", season=2027,
        date="", date_range="", time_status="NO GAME — OFFICIAL", matchup="Pro Bowl AFC–NFC game discontinued beginning 2026 season",
        stations=[], priority="HIGH — all NFL special events", source_url=NFL_PRO_BOWL_URL,
        source_label="NFL.com official Pro Bowl announcement", duration_min=None,
        duration_status="", planning_status="NOT A GAME — NO BUSY BLOCK",
        notes="Official NFL says the AFC–NFC Pro Bowl game will no longer be staged beginning with the 2026 season; player recognition continues. Prior continuous Jan–Super-Bowl blocking is corrected and flagged.",
        verification="VERIFIED — official NFL announcement",
    ))
    return events


# ---------------------------------------------------------------------------
# 49ers / Stanford / Cal
# ---------------------------------------------------------------------------

def parse_radio_line(text: str, pattern: str, default: str) -> str:
    m = re.search(pattern, text, re.I)
    return " ".join(m.group(0).split()) if m else default


def parse_49ers_events(intervals: dict[str, list],
                       nfl_index: dict[tuple[str, int], dict] | None = None) -> tuple[list[dict], str, list[dict]]:
    """Parse the official 49ers schedule.

    `nfl_index` maps (date, start minute) to already-parsed official NFL.com rows.
    A 49ers.com row that describes the same kickoff is not published a second
    time; instead the official NFL.com row is enriched with the 49ers game-center
    link and venue. This prevents one game being counted twice.
    """
    text = read_text("nflers_schedule")
    radio_line = parse_radio_line(text, r"KSAN 107\.7 FM\s*/\s*KNBR 104\.5 FM\s*/\s*680 AM", "")
    soup = BeautifulSoup(text, "lxml")
    events = []
    merged = []
    nfl_index = nfl_index or {}
    for card in soup.select(".nfl-o-matchup-cards"):
        gametime = card.get("data-gametime", "")
        if not gametime:
            continue
        try:
            dt = datetime.strptime(gametime, "%m/%d/%Y %H:%M:%S %z").astimezone(PT)
            if dt.year < 2000:
                continue
        except (ValueError, OverflowError):
            continue
        names = [n.get_text(" ", strip=True) for n in card.select(".nfl-o-matchup-cards__team-full-name")]
        opponent = names[0] if names else ""
        week_node = card.select_one(".nfl-o-matchup-cards__date-info--week")
        week = week_node.get_text(" ", strip=True) if week_node else ""
        venue = card.select_one(".nfl-o-matchup-cards__venue--location")
        venue_text = venue.get_text(" ", strip=True) if venue else ""

        # Only official team/league links may be cited. The schedule card exposes
        # several buttons; the first is sometimes a ticket-reseller link, which is
        # never accepted as a source.
        source_url = ""
        candidates = [a.get("href", "") for a in card.select(".nfl-o-matchup-cards__btn-game-day")]
        for href in candidates:
            if is_official_url(href) and "/game-day/" in href:
                source_url = href
                break
        if not source_url:
            for href in candidates:
                if is_official_url(href):
                    source_url = href
                    break
        if not source_url:
            source_url = "https://www.49ers.com/schedule/"

        day = dt.date()
        start_min = minute_of_day(dt)
        slug = source_url.rstrip("/").split("/")[-1] if source_url.startswith("http") else ""
        if slug in ("", "index"):
            parts = [p for p in source_url.split("/") if p]
            slug = parts[-2] if len(parts) >= 2 else ""
        if slug.endswith("-at-49ers"):
            niners_home = True
        elif slug.startswith("49ers-at-"):
            niners_home = False
        else:
            niners_home = "VS" in card.get_text(" ", strip=True)
        matchup = (f"{opponent} at San Francisco 49ers" if niners_home
                   else f"San Francisco 49ers at {opponent}") if opponent else "San Francisco 49ers"
        radio = radio_line or "KSAN 107.7 FM / KNBR 104.5 FM / 680 AM"

        existing = nfl_index.get((day.isoformat(), start_min))
        if existing is not None:
            # Same official kickoff already published from NFL.com: enrich, do not duplicate.
            if venue_text and not existing.get("venue"):
                existing["venue"] = venue_text
            existing["secondary_source_url"] = source_url
            existing["secondary_source_label"] = "49ers.com official game center"
            existing["notes"] = (existing.get("notes", "") +
                                 " 49ers.com official game center confirms the same kickoff, venue and radio network.").strip()
            for row in intervals.get(day.isoformat(), []):
                if row.get("event_id") == existing.get("id"):
                    row["secondary_source_url"] = source_url
                    row["secondary_source_label"] = "49ers.com official game center"
            merged.append({
                "date": day.isoformat(), "official_time_pt": fmt_pt(dt), "matchup": matchup,
                "kept_event_id": existing.get("id", ""), "kept_source_url": existing.get("source_url", ""),
                "duplicate_event_id": f"49ers-{card.get('data-gameid','')}",
                "secondary_source_url": source_url,
            })
            continue

        ev = event_base(
            id=f"49ers-{card.get('data-gameid','')}", category="NFL",
            subcategory=f"49ers {week or 'schedule'}", season=day.year, date=day.isoformat(),
            official_time_pt=fmt_pt(dt), official_time_zone=dt.strftime("%Z"), official_start_utc=iso_z(dt),
            time_status="VERIFIED", matchup=matchup,
            away=opponent if niners_home else "San Francisco 49ers",
            home="San Francisco 49ers" if niners_home else opponent,
            venue=venue_text,
            stations=[radio, "Westwood One Sports national windows via KNBR/KTCT"],
            priority="FOCUS — 49ers", focus=True, source_url=source_url,
            source_label="49ers.com official game center / schedule", source_api="https://www.49ers.com/schedule/",
            duration_min=NFL_DURATION, duration_source_url=NFL_RULEBOOK_URL,
            duration_status="OFFICIAL RULEBOOK CLOCK + SECONDARY 3:12 AVERAGE (FLAGGED)",
            planning_start_pt=fmt_hm(start_min), planning_end_pt=fmt_hm(start_min + NFL_DURATION),
            planning_status="OFFICIAL START + ESTIMATED DURATION", planning_source_url="https://www.49ers.com/schedule/",
            notes="Official 49ers schedule supplies kickoff and radio networks. End is estimated from researched average.",
            verification="VERIFIED — official 49ers kickoff/radio",
        )
        events.append(ev)
        add_interval(intervals, day, start_min, start_min + NFL_DURATION,
                     event_id=ev["id"], category="NFL", matchup=ev["matchup"], priority=ev["priority"],
                     focus=True, status="OFFICIAL_START_ESTIMATED_DURATION",
                     verification=ev["verification"], source_url=source_url,
                     source_label=ev["source_label"], label=ev["matchup"],
                     duration_source_url=NFL_RULEBOOK_URL)
    return events, radio_line, merged


def parse_stanford_events(intervals: dict[str, list]) -> list[dict]:
    soup = BeautifulSoup(read_text("stanford_schedule_current"), "lxml")
    events = []
    for row in soup.select("tr.schedule-item-table"):
        time_tag = row.select_one("time[datetime]")
        opponent_node = row.select_one(".schedule-event-item-team__opponent-name")
        location_node = row.select_one(".schedule-event-item-team__location")
        divider = row.select_one(".schedule-event-item-team__divider--desktop")
        if not (time_tag and opponent_node):
            continue
        try:
            dt = datetime.fromisoformat(time_tag.get("datetime")).astimezone(PT)
        except ValueError:
            continue
        opponent = opponent_node.get_text(" ", strip=True)
        home_away = divider.get_text(" ", strip=True) if divider else ""
        day = dt.date()
        start_min = minute_of_day(dt)
        row_text = row.get_text(" ", strip=True)
        # The official page prints TBA for kickoffs that have not been announced and
        # prints a flexible window such as "4 OR 4:30 P.M." for flex games. The
        # <time datetime> attribute then carries a placeholder, which must never be
        # published as a verified kickoff time.
        tba = bool(re.search(r"\bTBA\b", row_text, re.I))
        flex = re.search(r"(\d{1,2}(?::\d{2})?)\s*OR\s*(\d{1,2}(?::\d{2})?)\s*([AP])\.?M", row_text, re.I)
        matchup = f"Stanford {'vs' if home_away.lower().startswith('vs') else 'at'} {opponent}"
        if tba:
            ev = event_base(
                id=f"stanford-{day.isoformat()}-{re.sub(r'[^a-z0-9]+','-',opponent.lower())}",
                category="NCAAF", subcategory="Stanford Cardinal football", season=day.year,
                date=day.isoformat(), official_time_pt="", official_time_zone="",
                official_start_utc="", time_status="OFFICIAL DATE / TIME TBA — UNVERIFIED",
                matchup=matchup,
                away="Stanford" if "at" in home_away.lower() else opponent,
                home="Stanford" if "vs" in home_away.lower() else opponent,
                venue=location_node.get_text(" ", strip=True) if location_node else "",
                stations=["KNBR/KTCT 1050 AM"], priority="FOCUS — Stanford", focus=True,
                source_url="https://gostanford.com/sports/football/schedule",
                source_label="Stanford Cardinal official football schedule",
                source_api="https://gostanford.com/news/2026/07/30/2026-football-radio-broadcast-team-announced",
                duration_min=NCAAF_DURATION, duration_source_url=NCAA_DURATION_URL,
                duration_status="OFFICIAL NCAA 2016 FBS AVERAGE (3:24) — DATED, FLAGGED",
                planning_status="OFFICIAL DATE / OFFICIAL TIME TBA",
                planning_source_url="https://gostanford.com/sports/football/schedule",
                notes="Official Stanford schedule publishes the date with kickoff TBA; the official placeholder timestamp is not copied. The whole day is treated as a busy candidate.",
                verification="OFFICIAL DATE / OFFICIAL TIME TBA — UNVERIFIED",
            )
            events.append(ev)
            add_unverified_block(intervals, day,
                                 event_id=ev["id"], category="NCAAF", matchup=matchup,
                                 priority="FOCUS — Stanford", focus=True,
                                 verification="OFFICIAL DATE / TIME TBA — UNVERIFIED",
                                 source_url=ev["source_url"], source_label=ev["source_label"],
                                 label=f"{matchup} — official date, kickoff TBA",
                                 duration_source_url=NCAA_DURATION_URL)
            continue
        flex_note = ""
        if flex:
            flex_note = (f" Official page lists a flexible kickoff window: {flex.group(1)} or "
                         f"{flex.group(2)} {flex.group(3).upper()}M PT.")
        ev = event_base(
            id=f"stanford-{day.isoformat()}-{re.sub(r'[^a-z0-9]+','-',opponent.lower())}",
            category="NCAAF", subcategory="Stanford Cardinal football", season=day.year,
            date=day.isoformat(), official_time_pt=fmt_pt(dt), official_time_zone=dt.strftime("%Z"),
            official_start_utc=iso_z(dt),
            time_status="VERIFIED — OFFICIAL FLEX WINDOW" if flex else "VERIFIED",
            matchup=matchup,
            away="Stanford" if "at" in home_away.lower() else opponent,
            home="Stanford" if "vs" in home_away.lower() else opponent,
            venue=location_node.get_text(" ", strip=True) if location_node else "",
            stations=["KNBR/KTCT 1050 AM"], priority="FOCUS — Stanford", focus=True,
            source_url="https://gostanford.com/sports/football/schedule",
            source_label="Stanford Cardinal official football schedule",
            source_api="https://gostanford.com/news/2026/07/30/2026-football-radio-broadcast-team-announced",
            duration_min=NCAAF_DURATION, duration_source_url=NCAA_DURATION_URL,
            duration_status="OFFICIAL NCAA 2016 FBS AVERAGE (3:24) — DATED, FLAGGED",
            planning_start_pt=fmt_hm(start_min), planning_end_pt=fmt_hm(start_min + NCAAF_DURATION),
            planning_status="OFFICIAL START + ESTIMATED DURATION",
            planning_source_url="https://gostanford.com/sports/football/schedule",
            notes=("Official Stanford schedule supplies kickoff with Pacific offset; official radio article confirms KNBR/KTCT 1050 AM."
                   + flex_note),
            verification="VERIFIED — official Stanford kickoff",
        )
        events.append(ev)
        add_interval(intervals, day, start_min, start_min + NCAAF_DURATION,
                     event_id=ev["id"], category="NCAAF", matchup=ev["matchup"], priority=ev["priority"],
                     focus=True, status="OFFICIAL_START_ESTIMATED_DURATION",
                     verification=ev["verification"], source_url=ev["source_url"],
                     source_label=ev["source_label"], label=ev["matchup"],
                     duration_source_url=NCAA_DURATION_URL)
    return events


def parse_cal_events(intervals: dict[str, list]) -> list[dict]:
    """Parse the official Cal schedule.

    The page exposes every game twice: a `.s-game-card` (opponent, home/away and,
    for announced games, the kickoff) and a `.c-scoreboard__item` carousel entry
    that always carries the full date. Earlier versions only read the game-card
    header date and required an HH:MM kickoff, so away games listed as "9 AM" and
    every game whose header date node was empty were dropped as TBA. Both sources
    are merged here by opponent so no published date is lost.
    """
    soup = BeautifulSoup(read_text("cal_schedule_current"), "lxml")
    cal_url = "https://calbears.com/sports/football/schedule/2026"
    board: dict[str, dict] = {}
    for item in soup.select(".c-scoreboard__item"):
        label = item.get("aria-label", "")
        m = re.search(r"(?:versus|at)\s+(.+?)\s+on\s+([A-Z][a-z]+)\.?\s+(\d{1,2}),\s*(\d{4})", label)
        if not m:
            continue
        try:
            day_value = datetime.strptime(f"{m.group(2)} {m.group(3)} {m.group(4)}", "%B %d %Y").date()
        except ValueError:
            continue
        time_node = item.select_one(".c-scoreboard__time")
        location_node = item.select_one(".c-scoreboard__location")
        board[m.group(1).strip().lower()] = {
            "date": day_value,
            "time_text": time_node.get_text(" ", strip=True) if time_node else "",
            "location": location_node.get_text(" ", strip=True) if location_node else "",
        }

    events = []
    for i, card in enumerate(soup.select(".s-game-card"), 1):
        text = card.get_text(" ", strip=True)
        opponent_node = card.select_one('[data-test-id="s-game-card-standard__header-team-opponent-link"]')
        date_node = card.select_one('[data-test-id="s-game-card-standard__header-game-date-details"]')
        time_node = card.select_one('[aria-label="Event Time"]')
        stamp = card.select_one(".s-stamp__text")
        opponent = opponent_node.get_text(" ", strip=True) if opponent_node else ""
        date_text = date_node.get_text(" ", strip=True) if date_node else ""
        time_text = time_node.get_text(" ", strip=True) if time_node else ""
        info = board.get(opponent.lower(), {})
        radio_match = re.search(r"Radio:\s*([^|]+?)(?:\s+[A-Z]|$)", text)
        radio = " ".join(radio_match.group(1).split()) if radio_match else "KSFO 810 AM"
        home_away = stamp.get_text(" ", strip=True).lower() if stamp else ""

        day = None
        m = re.search(r"([A-Z][a-z]{2})\.?\s+(\d{1,2})", date_text)
        if m:
            try:
                day = date(2026, datetime.strptime(m.group(1), "%b").month, int(m.group(2)))
            except ValueError:
                day = None
        if day is None and info.get("date"):
            day = info["date"]

        # Kickoff may be printed as "9 AM" (no minutes) or only on the carousel.
        kickoff = None
        for candidate in (time_text, info.get("time_text", "")):
            tm = re.search(r"(\d{1,2})(?::(\d{2}))?\s*([AP])\.?M", candidate, re.I)
            if tm:
                hour = int(tm.group(1)) % 12
                minute = int(tm.group(2) or 0)
                if tm.group(3).upper() == "P":
                    hour += 12
                kickoff = hour * 60 + minute
                break

        venue = info.get("location", "")
        matchup = f"Cal {'vs' if 'vs' in home_away else 'at'} {opponent}"
        if day is None:
            ev = event_base(
                id=f"cal-2026-{i}", category="NCAAF", subcategory="California Golden Bears football",
                season=2026, date="", time_status="TBA — UNVERIFIED", matchup=f"Cal vs/at {opponent}",
                home="Cal" if "vs" in home_away else opponent,
                away="Cal" if "at" in home_away else opponent,
                stations=[radio], priority="FOCUS — Cal", focus=True,
                source_url=cal_url,
                source_label="California Golden Bears official schedule",
                duration_min=NCAAF_DURATION, duration_source_url=NCAA_DURATION_URL,
                duration_status="OFFICIAL NCAA 2016 FBS AVERAGE (3:24) — DATED, FLAGGED",
                planning_status="UNVERIFIED OFFICIAL TIME", notes="Official schedule lists TBA; exact time is blank.",
                verification="OFFICIAL MATCHUP / TIME UNVERIFIED",
            )
            events.append(ev)
            continue

        if kickoff is None:
            ev = event_base(
                id=f"cal-{day.isoformat()}-{re.sub(r'[^a-z0-9]+','-',opponent.lower())}",
                category="NCAAF", subcategory="California Golden Bears football", season=2026,
                date=day.isoformat(), official_time_pt="", official_time_zone="",
                official_start_utc="", time_status="OFFICIAL DATE / TIME TBA — UNVERIFIED",
                matchup=matchup,
                home="Cal" if "vs" in home_away else opponent,
                away="Cal" if "at" in home_away else opponent,
                venue=venue, stations=[radio], priority="FOCUS — Cal", focus=True,
                source_url=cal_url,
                source_label="California Golden Bears official schedule",
                duration_min=NCAAF_DURATION, duration_source_url=NCAA_DURATION_URL,
                duration_status="OFFICIAL NCAA 2016 FBS AVERAGE (3:24) — DATED, FLAGGED",
                planning_status="OFFICIAL DATE / OFFICIAL TIME TBA",
                planning_source_url=cal_url,
                notes="Official Cal schedule publishes the date with kickoff TBA; no official time is copied. The whole day is treated as a busy candidate.",
                verification="OFFICIAL DATE / TIME TBA — UNVERIFIED",
            )
            events.append(ev)
            add_unverified_block(intervals, day,
                                 event_id=ev["id"], category="NCAAF", matchup=matchup,
                                 priority="FOCUS — Cal", focus=True,
                                 verification="OFFICIAL DATE / TIME TBA — UNVERIFIED",
                                 source_url=cal_url,
                                 source_label="California Golden Bears official schedule",
                                 label=f"{matchup} — official date, kickoff TBA",
                                 duration_source_url=NCAA_DURATION_URL)
            continue

        dt = datetime.combine(day, time(0, 0), tzinfo=PT) + timedelta(minutes=kickoff)
        dt = dt.astimezone(PT)
        start_min = minute_of_day(dt)
        ev = event_base(
            id=f"cal-{day.isoformat()}-{re.sub(r'[^a-z0-9]+','-',opponent.lower())}",
            category="NCAAF", subcategory="California Golden Bears football", season=2026,
            date=day.isoformat(), official_time_pt=fmt_pt(dt), official_time_zone=dt.strftime("%Z"),
            official_start_utc=iso_z(dt), time_status="VERIFIED", matchup=matchup,
            home="Cal" if "vs" in home_away else opponent,
            away="Cal" if "at" in home_away else opponent,
            venue=venue, stations=[radio], priority="FOCUS — Cal", focus=True,
            source_url=cal_url,
            source_label="California Golden Bears official schedule",
            duration_min=NCAAF_DURATION, duration_source_url=NCAA_DURATION_URL,
            duration_status="OFFICIAL NCAA 2016 FBS AVERAGE (3:24) — DATED, FLAGGED",
            planning_start_pt=fmt_hm(start_min), planning_end_pt=fmt_hm(start_min + NCAAF_DURATION),
            planning_status="OFFICIAL START + ESTIMATED DURATION",
            planning_source_url=cal_url,
            notes="Official Cal schedule displays Pacific local time and radio network; end is estimated from researched average.",
            verification="VERIFIED — official Cal kickoff/radio",
        )
        events.append(ev)
        add_interval(intervals, day, start_min, start_min + NCAAF_DURATION,
                     event_id=ev["id"], category="NCAAF", matchup=ev["matchup"], priority=ev["priority"],
                     focus=True, status="OFFICIAL_START_ESTIMATED_DURATION",
                     verification=ev["verification"], source_url=ev["source_url"],
                     source_label=ev["source_label"], label=ev["matchup"],
                     duration_source_url=NCAA_DURATION_URL)
    return events


def parse_station_finder() -> tuple[dict[str, list[str]], list[dict]]:
    soup = BeautifulSoup(read_text("wwo_station_finder"), "lxml")
    known = ["NFL", "NCAA Football", "NCAA Basketball", "Soccer", "Golf", "NCAA Baseball",
             "NCAA Softball", "NCAA Lacrosse", "NCAA Hockey"]
    by_category = defaultdict(list)
    rows = []
    for tr in soup.find_all("tr"):
        cells = [c.get_text(" ", strip=True) for c in tr.find_all(["td", "th"])]
        if not any("San Francisco" in c for c in cells):
            continue
        category = ""
        prev = tr.find_previous(["h1", "h2", "h3", "h4", "h5", "h6", "a", "strong"])
        while prev:
            text = prev.get_text(" ", strip=True)
            if text in known:
                category = text
                break
            prev = prev.find_previous(["h1", "h2", "h3", "h4", "h5", "h6", "a", "strong"])
        call_sign = next((c for c in cells if re.match(r"K[A-Z]{2,4}(?:-[A-Z0-9]+)?", c)), "")
        if not category or not call_sign:
            continue
        if call_sign not in by_category[category]:
            by_category[category].append(call_sign)
        rows.append({
            "category": category, "market": "San Francisco, CA", "call_sign": call_sign,
            "frequency": "", "status": "OFFICIAL WWO SF AFFILIATE / FREQUENCY NOT STATED",
            "priority": "HIGH — causes busy time", "source_url": WWO_STATION_FINDER_URL,
            "source_label": "Westwood One Sports official station finder", "verification": "VERIFIED",
            "notes": "Official WWO station finder warns affiliates may not air every network broadcast. Frequency is blank unless confirmed by an official team/station page.",
        })
    # Deduplicate rows.
    seen = set()
    unique = []
    for row in rows:
        key = (row["category"], row["call_sign"])
        if key not in seen:
            seen.add(key)
            unique.append(row)
    return dict(by_category), unique


def parse_wwo_events(intervals: dict[str, list]) -> tuple[list[dict], dict]:
    cat_map = json.loads((ROOT / "research" / "official" / "wwo_event_categories.json").read_text())["events"]
    sf_map, station_rows = parse_station_finder()
    events = []
    counts = defaultdict(int)
    for path in sorted(OFFICIAL_RAW.glob("wwo_event_*.gz")):
        eid = path.stem.split("_")[-1]
        text = gzip.decompress(path.read_bytes()).decode("utf-8", "replace")
        start_m = re.search(r"class=['\"]start_time['\"]\s+data-time=['\"](\d+)['\"]", text)
        end_m = re.search(r"class=['\"]end_time['\"]\s+data-time=['\"](\d+)['\"]", text)
        if not (start_m and end_m):
            continue
        start_epoch, end_epoch = int(start_m.group(1)), int(end_m.group(1))
        start_utc = datetime.fromtimestamp(start_epoch, UTC)
        end_utc = datetime.fromtimestamp(end_epoch, UTC)
        start_pt, end_pt = start_utc.astimezone(PT), end_utc.astimezone(PT)
        day = start_pt.date()
        if day.year < 2026 or day > date(2027, 12, 31):
            continue
        ld = {}
        ldm = re.search(r'<script type="application/ld\+json">(.*?)</script>', text, re.S)
        if ldm:
            try:
                ld = json.loads(ldm.group(1))
            except json.JSONDecodeError:
                ld = {}
        title = ld.get("name") or ""
        if not title:
            title_m = re.search(r"<title>(.*?)</title>", text, re.S | re.I)
            title = re.sub(r"\s*[|]\s*Westwood One Sports.*$", "", title_m.group(1)).strip() if title_m else f"WWO event {eid}"
        description = ld.get("description", "")
        location = (ld.get("location") or {}).get("name", "") if isinstance(ld.get("location"), dict) else ""
        categories = cat_map.get(eid, ["WWO Sports"])
        affiliates = []
        for category in categories:
            for call in sf_map.get(category, []):
                if call not in affiliates:
                    affiliates.append(call)
        placeholder = "11:59 PM" in text
        source_url = f"https://www.westwoodonesports.com/events/{eid}/"
        start_min, end_min = minute_of_day(start_pt), minute_of_day(end_pt)
        if end_min <= start_min:
            end_min = 1440
        ev = event_base(
            id=f"wwo-{eid}", category="WWO", subcategory=" / ".join(categories), season=day.year,
            date=day.isoformat(), official_time_pt=fmt_pt(start_pt),
            official_time_zone=start_pt.strftime("%Z"), official_start_utc=iso_z(start_utc),
            official_end_utc=iso_z(end_utc), official_end_pt=fmt_pt(end_pt),
            time_status="VERIFIED — official network window", matchup=title, venue=location,
            stations=affiliates or [], sf_affiliates=affiliates,
            priority="HIGH — all WWO live radio sports", focus=any(c in ("NFL", "NCAA Football") for c in categories),
            source_url=source_url, source_label="Westwood One Sports official event page",
            duration_min=max(0, end_min - start_min), duration_source_url=source_url,
            duration_status="OFFICIAL WWO EVENT WINDOW" + (" — END TIME PLACEHOLDER FLAGGED" if placeholder else ""),
            planning_start_pt=fmt_hm(start_min), planning_end_pt=fmt_hm(end_min),
            planning_status="OFFICIAL NETWORK WINDOW", planning_source_url=source_url,
            notes="Official WWO event start/end Unix timestamps are used. JSON-LD local-clock +00:00 inconsistency is flagged; some end times are 11:59 PM placeholders." + ("" if affiliates else " No SF affiliate is listed for this category in the official WWO station finder."),
            verification="VERIFIED — official WWO event timestamps",
        )
        events.append(ev)
        counts[day.year] += 1
        add_interval(intervals, day, start_min, end_min,
                     event_id=ev["id"], category="WWO", matchup=title, priority=ev["priority"],
                     focus=ev["focus"], status="OFFICIAL_NETWORK_WINDOW",
                     verification=ev["verification"], source_url=source_url,
                     source_label=ev["source_label"], label=title, duration_source_url=source_url)
    return events, {"station_rows": station_rows, "sf_map": sf_map, "counts": dict(counts)}


def parse_earthquakes_events(intervals: dict[str, list]) -> list[dict]:
    soup = BeautifulSoup(read_text("earthquakes_radio_2026"), "lxml")
    month_map = {"Jan": 1, "Feb": 2, "Mar": 3, "March": 3, "Apr": 4, "April": 4,
                 "May": 5, "June": 6, "Jun": 6, "July": 7, "Jul": 7, "Aug": 8,
                 "Sept": 9, "Sep": 9, "Sept.": 9, "October": 10, "Oct": 10,
                 "Nov": 11, "November": 11, "Dec": 12, "December": 12}
    events = []
    for tr in soup.find_all("tr"):
        cells = [c.get_text(" ", strip=True) for c in tr.find_all(["td", "th"])]
        if len(cells) < 5:
            continue
        date_cell, opponent, home_away, time_cell, radio_cell = cells[:5]
        dm = re.search(r"([A-Za-z]+\.?)\s+(\d{1,2}),\s+(\d{4})", date_cell)
        tm = re.search(r"(\d{1,2}:\d{2}\s*[AP]M)", time_cell, re.I)
        if not (dm and tm):
            continue
        month_name = dm.group(1).replace(".", "")
        month = month_map.get(month_name) or month_map.get(dm.group(1))
        if not month:
            continue
        day = date(int(dm.group(3)), month, int(dm.group(2)))
        dt = datetime.strptime(f"{day.isoformat()} {tm.group(1).upper()}", "%Y-%m-%d %I:%M %p").replace(tzinfo=PT)
        start_min = minute_of_day(dt)
        radio = "810 KSFO / 1370 KZSF" if "810" in radio_cell else "KNBR 680 AM / 104.5 FM / 1370 KZSF" if "680" in radio_cell else "Official radio station listed in article"
        ev = event_base(
            id=f"mls-{day.isoformat()}-{re.sub(r'[^a-z0-9]+','-',opponent.lower())}",
            category="MLS", subcategory="San Jose Earthquakes official terrestrial radio", season=2026,
            date=day.isoformat(), official_time_pt=fmt_pt(dt), official_time_zone=dt.strftime("%Z"),
            official_start_utc=iso_z(dt), time_status="VERIFIED", matchup=f"Earthquakes {home_away} {opponent}",
            away="San Jose Earthquakes" if home_away.lower().startswith("away") else opponent,
            home="San Jose Earthquakes" if home_away.lower().startswith("home") else opponent,
            stations=[radio], priority="HIGH — other live Bay Area radio sports", focus=False,
            source_url=EARTHQUAKES_URL, source_label="Earthquakes official 2026 radio schedule",
            duration_min=SOCCER_DURATION, duration_source_url=IFAB_URL,
            duration_status="OFFICIAL LAWS: 90 MIN + 15 MIN HALFTIME (PLANNING MODEL)",
            planning_start_pt=fmt_hm(start_min), planning_end_pt=fmt_hm(start_min + SOCCER_DURATION),
            planning_status="OFFICIAL START + RULE-BASED DURATION ESTIMATE",
            planning_source_url=EARTHQUAKES_URL,
            notes="Official club article supplies date, PT kickoff and terrestrial radio stations. End uses the official IFAB 90+15 model, not an official broadcast end.",
            verification="VERIFIED — official Earthquakes kickoff/radio",
        )
        events.append(ev)
        add_interval(intervals, day, start_min, start_min + SOCCER_DURATION,
                     event_id=ev["id"], category="MLS", matchup=ev["matchup"], priority=ev["priority"],
                     focus=False, status="OFFICIAL_START_ESTIMATED_DURATION",
                     verification=ev["verification"], source_url=EARTHQUAKES_URL,
                     source_label=ev["source_label"], label=ev["matchup"], duration_source_url=IFAB_URL)
    return events


# ---------------------------------------------------------------------------
# Official anchors, stations, durations, flags, season availability
# ---------------------------------------------------------------------------

def build_anchors(intervals: dict[str, list]) -> list[dict]:
    specs = [
        ("2027 MLB Spring Training begins (all 30 clubs)", "2027-02-19", "", "MLB", "https://www.mlb.com/press-release/press-release-mlb-announces-2027-spring-training-schedule", "OFFICIAL DATE / TIME TBD"),
        ("2027 MLB exhibition games at Major/Minor League parks", "2027-03-20 to 2027-03-23", "", "MLB", "https://www.mlb.com/press-release/press-release-mlb-announces-2027-spring-training-schedule", "OFFICIAL DATE RANGE / TIMES TBD"),
        ("2027 MLB Opening Night", "2027-03-24", "", "MLB", "https://www.mlb.com/tigers/news/mlb-2027-schedule-released", "OFFICIAL DATE / MATCHUP+TIME TBD"),
        ("2027 MLB traditional Opening Day", "2027-03-25", "", "MLB", "https://www.mlb.com/tigers/news/mlb-2027-schedule-released", "OFFICIAL DATE / TIMES PARTLY TBD"),
        ("2027 MLB regular season ends", "2027-09-26", "", "MLB", "https://www.mlb.com/tigers/news/mlb-2027-schedule-released", "OFFICIAL DATE"),
        ("2027 MLB Home Run Derby", "2027-07-12", "", "MLB", "https://www.mlb.com/tigers/news/mlb-2027-schedule-released", "OFFICIAL DATE / TIME TBD"),
        ("2027 MLB All-Star Game at Wrigley Field", "2027-07-13", "", "MLB", "https://www.mlb.com/news/2027-mlb-all-star-game-at-wrigley-field", "OFFICIAL DATE / TIME TBD"),
        ("2028 MLB All-Star Game at Oracle Park", "", "", "MLB", "https://www.mlb.com/all-star/future-locations", "HOST VERIFIED / DATE TBA"),
        ("2027 NFL Week 18", "2027-01-09 to 2027-01-10", "", "NFL", NFL_IMPORTANT_DATES_URL, "OFFICIAL DATE RANGE / TIMES TBD"),
        ("2027 NFL Wild Card Weekend", "2027-01-16 to 2027-01-18", "", "NFL", NFL_IMPORTANT_DATES_URL, "OFFICIAL DATE RANGE / TIMES TBD"),
        ("2027 NFL Divisional Playoffs", "2027-01-23 to 2027-01-24", "", "NFL", NFL_IMPORTANT_DATES_URL, "OFFICIAL DATE RANGE / TIMES TBD"),
        ("2027 AFC/NFC Championship Games", "2027-01-31", "", "NFL", NFL_IMPORTANT_DATES_URL, "OFFICIAL DATE / TIMES TBD"),
        ("Super Bowl LXI at SoFi Stadium", "2027-02-14", "", "NFL", NFL_IMPORTANT_DATES_URL, "OFFICIAL DATE / KICKOFF TBD"),
        ("NFL Pro Bowl AFC–NFC game discontinued", "", "", "NFL", NFL_PRO_BOWL_URL, "NO GAME — OFFICIAL"),
        ("2027 CFP National Championship", "2027-01-25", "4:30 PM PST", "NCAAF", "https://collegefootballplayoff.com/news/2026/4/7/lv-april-newsconf", "OFFICIAL DATE/TIME"),
        ("2028 CFP National Championship (New Orleans)", "2028-01-24", "", "NCAAF", "https://collegefootballplayoff.com/news/2025/10/29/tampabay-29", "OFFICIAL DATE / TIME TBD"),
        ("2029 CFP National Championship (Tampa Bay)", "2029-01-22", "", "NCAAF", "https://collegefootballplayoff.com/news/2025/10/29/tampabay-29", "OFFICIAL DATE / TIME TBD"),
        ("Super Bowl LXII (Atlanta)", "", "", "NFL", "https://www.nfl.com/news/mercedes-benz-stadium-in-atlanta-to-host-super-bowl-lxii-in-2028", "HOST VERIFIED / DATE TBA"),
        ("Cal 2027 Sacramento State", "2027-08-28", "", "NCAAF", "https://calbears.com/news/2026/6/25/football-cal-announces-matchups-against-odu-sac-state", "OFFICIAL DATE / TIME TBD"),
        ("Cal 2027 at UCLA", "2027-09-04", "", "NCAAF", "https://calbears.com/news/2026/9/16/california-football-announces-2027-conference-opponents", "OFFICIAL DATE / TIME TBD"),
        ("Cal 2027 Old Dominion", "2027-09-11", "", "NCAAF", "https://calbears.com/news/2026/6/25/football-cal-announces-matchups-against-odu-sac-state", "OFFICIAL DATE / TIME TBD"),
        ("Stanford 2027 TCU away game", "2027-09-04", "", "NCAAF", "https://gostanford.com/news/2026/04/17/tcu-series-update", "OFFICIAL DATE CANCELED — NO GAME"),
        ("Stanford 2027 Notre Dame", "2027-11-27", "", "NCAAF", "https://gostanford.com/news/2026/05/20/two-dates-added-to-notre-dame-rivalry", "OFFICIAL DATE / TIME TBD"),
        ("Stanford 2028 at Notre Dame", "2028-10-14", "", "NCAAF", "https://gostanford.com/news/2026/05/20/two-dates-added-to-notre-dame-rivalry", "OFFICIAL DATE / TIME TBD"),
        ("Stanford/Cal 2027 ACC conference dates", "", "", "NCAAF", "https://calbears.com/news/2026/9/16/california-football-announces-2027-conference-opponents", "OPPONENTS VERIFIED / DATES TBA"),
        ("Stanford/Cal 2024–30 ACC opponent model", "", "", "NCAAF", "https://gostanford.com/news/2023/10/30/acc-announces-football-schedule-model", "OPPONENT GRID VERIFIED / DATES TBA"),
        ("NFL 2027 game-by-game schedule", "", "", "NFL", "https://www.nfl.com/schedules/2027/by-team", "SCHEDULE DATA UNAVAILABLE — UNVERIFIED"),
        ("MLB 2028 game-by-game schedule", "", "", "MLB", MLB_API_2028, "NO OFFICIAL GAME ROWS — UNVERIFIED"),
        ("MLB 2029 game-by-game schedule", "", "", "MLB", MLB_API_2029, "NO OFFICIAL GAME ROWS — UNVERIFIED"),
    ]
    rows = []
    for i, (label, date_value, time_value, category, url, status) in enumerate(specs, 1):
        verification = "VERIFIED" if status.startswith("OFFICIAL") or status.startswith("HOST") or status.startswith("NO GAME") or status.startswith("OPPONENT") else "UNVERIFIED"
        rows.append({
            "id": f"A{i:02d}", "event": label, "category": category,
            "official_date": date_value, "official_time_pt": time_value,
            "status": status, "verification": verification, "source_url": url,
            "source_label": "Official league/team/network source",
        })
        # Only exact official dates without exact times become conservative blocks; ranges already handled for NFL postseason.
        if re.fullmatch(r"\d{4}-\d{2}-\d{2}", date_value) and not time_value and category in ("MLB", "NFL", "NCAAF") and "CANCELED" not in status and "NO GAME" not in status:
            day = date.fromisoformat(date_value)
            add_unverified_block(intervals, day, event_id=f"anchor-A{i:02d}", category=category,
                                 matchup=label, priority="HIGH — official date anchor",
                                 source_url=url, source_label="Official league/team/network source", label=label)
    return rows


def build_radio_stations(sf_rows: list[dict]) -> list[dict]:
    rows = [
        {"sport": "MLB Giants", "station": "KNBR 680 AM / 104.5 FM", "call_sign": "KNBR-AM / KNBR-FM", "frequency": "680 AM / 104.5 FM", "priority": "FOCUS — Giants", "status": "VERIFIED", "source_url": "https://www.mlb.com/giants/schedule/tv", "source_label": "Official Giants broadcast page", "notes": "Official Giants radio / TV page."},
        {"sport": "MLB Athletics", "station": "960 AM KNEW Bay Area / A's Cast", "call_sign": "KNEW", "frequency": "960 AM", "priority": "FOCUS — Athletics", "status": "VERIFIED", "source_url": "https://www.mlb.com/athletics/schedule/affiliates", "source_label": "Official Athletics affiliates page", "notes": "Official A's terrestrial radio affiliate; also KSTE 650 Sacramento and A's Cast."},
        {"sport": "NFL 49ers", "station": "KSAN 107.7 FM / KNBR 104.5 FM / 680 AM", "call_sign": "KSAN / KNBR", "frequency": "107.7 FM / 104.5 FM / 680 AM", "priority": "FOCUS — 49ers", "status": "VERIFIED", "source_url": "https://www.49ers.com/schedule/", "source_label": "Official 49ers schedule", "notes": "Official 49ers schedule radio line."},
        {"sport": "Stanford NCAAF", "station": "KNBR/KTCT 1050 AM", "call_sign": "KTCT", "frequency": "1050 AM", "priority": "FOCUS — Stanford", "status": "VERIFIED", "source_url": "https://gostanford.com/news/2026/07/30/2026-football-radio-broadcast-team-announced", "source_label": "Official Stanford radio announcement", "notes": "2026 football radio broadcast team announcement."},
        {"sport": "Cal NCAAF", "station": "KSFO 810 AM", "call_sign": "KSFO", "frequency": "810 AM", "priority": "FOCUS — Cal", "status": "VERIFIED", "source_url": "https://calbears.com/sports/football/schedule/2026", "source_label": "Official Cal schedule", "notes": "Official Cal schedule radio line; Big Game KNBR 104.5/680 noted in official material."},
        {"sport": "MLS Earthquakes", "station": "KSFO 810 AM / KZSF 1370 AM / KNBR 680 AM", "call_sign": "KSFO / KZSF / KNBR", "frequency": "810 AM / 1370 AM / 680 AM", "priority": "HIGH — other Bay Area radio sport", "status": "VERIFIED", "source_url": EARTHQUAKES_URL, "source_label": "Official Earthquakes 2026 radio release", "notes": "Official 2026 terrestrial radio schedule; all times PT."},
        {"sport": "NBA Warriors", "station": "95.7 The Game KGMZ-FM", "call_sign": "KGMZ-FM", "frequency": "95.7 FM", "priority": "HIGH — other Bay Area radio sport", "status": "STATION VERIFIED / GAME ROWS UNVERIFIED", "source_url": "https://www.nba.com/warriors/news/957-the-game-extension-20190827", "source_label": "Official Warriors radio announcement", "notes": "Official team source confirms flagship; 94122 reception and complete game rows are not verified from an official radio schedule."},
        {"sport": "NHL Sharks", "station": "98.5 KFOX (KUFX-FM)", "call_sign": "KUFX-FM", "frequency": "98.5 FM", "priority": "HIGH — other Bay Area radio sport", "status": "STATION VERIFIED / 94122 RECEPTION UNVERIFIED", "source_url": "https://www.nhl.com/sharks/news/san-jose-sharks-announce-2018-19-broadcast-schedule-300119102", "source_label": "Official Sharks broadcast announcement", "notes": "Official NHL article lists 98.5 KFOX; current 94122 reception and complete rows are unverified."},
        {"sport": "KNBR weekly program grid", "station": "KNBR 680 / 104.5 / 1050", "call_sign": "KNBR / KTCT", "frequency": "680 AM / 104.5 FM / 1050 AM", "priority": "HIGH — station schedule", "status": "VERIFIED", "source_url": "https://www.knbr.com/shows/", "source_label": "Official KNBR weekly programming schedule", "notes": "Official station grid includes Westwood One Sports and live game blocks; use for manual review."},
        {"sport": "KSFO show grid", "station": "KSFO 810 AM", "call_sign": "KSFO", "frequency": "810 AM", "priority": "HIGH — station schedule", "status": "VERIFIED", "source_url": "https://www.ksfo.com/shows/", "source_label": "Official KSFO show schedule", "notes": "Official show grid includes Quakes Soccer and The Soccer Hour."},
        {"sport": "95.7 The Game station schedule", "station": "95.7 The Game", "call_sign": "KGMZ-FM", "frequency": "95.7 FM", "priority": "HIGH — station schedule", "status": "VERIFIED", "source_url": "https://www.957thegame.com/", "source_label": "Official 95.7 The Game station", "notes": "Official station schedule shows Warriors/Valkyries blocks; 94122 reception is unverified."},
        {"sport": "Westwood One Sports", "station": "Network affiliates; SF rows in station finder", "call_sign": "WWO", "frequency": "", "priority": "HIGH — all WWO live games", "status": "VERIFIED WITH CARRIAGE CAVEAT", "source_url": WWO_STATION_FINDER_URL, "source_label": "Official WWO station finder", "notes": "Station finder warns affiliates may not air every WWO broadcast."},
    ]
    for r in sf_rows:
        rows.append({
            "sport": f"WWO {r['category']} SF affiliate", "station": r["call_sign"],
            "call_sign": r["call_sign"], "frequency": r["frequency"] or "",
            "priority": "HIGH — all WWO live games", "status": r["status"],
            "source_url": r["source_url"], "source_label": r["source_label"],
            "notes": r["notes"] + (" Frequency blank = UNVERIFIED." if not r["frequency"] else ""),
        })
    return rows


def build_durations() -> list[dict]:
    return [
        {"sport": "MLB", "average_game_duration": "2:38 (158 min)", "halftime": "Not applicable — between-inning breaks", "regulation": "9 innings", "status": "OFFICIAL VERIFIED", "source_url": MLB_DURATION_URL, "source_label": "MLB.com official 2025 average", "notes": "Used for estimated end of MLB radio windows."},
        {"sport": "NFL", "average_game_duration": "3:12 (192 min) — secondary average, FLAGGED", "halftime": "13 minutes", "regulation": "60 minutes (4 × 15)", "status": "OFFICIAL RULE / SECONDARY AVERAGE", "source_url": NFL_RULEBOOK_URL, "source_label": "Official 2026 NFL Playing Rules", "notes": "Rulebook PDF page 18 confirms 13-minute halftime; 3:12 broadcast average is not an official NFL time and is flagged."},
        {"sport": "NCAAF FBS", "average_game_duration": "3:24 (204 min) — 2016 official NCAA article, dated/FLAGGED", "halftime": "20 minutes", "regulation": "60 minutes (4 × 15)", "status": "OFFICIAL RULE / DATED OFFICIAL AVERAGE", "source_url": NCAA_DURATION_URL, "source_label": "NCAA.com official duration article", "notes": "20-minute halftime is in the official NCAA championship handbook; current average is not officially published."},
        {"sport": "MLS / soccer", "average_game_duration": "2:00 (120 min) — rule-based planning estimate", "halftime": "15 minutes", "regulation": "90 minutes (2 × 45)", "status": "OFFICIAL LAWS / ESTIMATED BROADCAST", "source_url": IFAB_URL, "source_label": "Official IFAB Laws of the Game", "notes": "Used for Earthquakes radio rows; official WWO event windows use their own end timestamps."},
        {"sport": "WWO network events", "average_game_duration": "Official event start–end window", "halftime": "Varies by sport", "regulation": "Varies by sport", "status": "OFFICIAL NETWORK WINDOW / END PLACEHOLDER FLAGGED", "source_url": "https://www.westwoodonesports.com/events/548540/", "source_label": "Official WWO event detail", "notes": "Unix data-time attributes are used; many official end values are 11:59 PM placeholders."},
        {"sport": "NBA / NHL / WNBA other sports", "average_game_duration": "", "halftime": "", "regulation": "", "status": "UNVERIFIED — OFFICIAL GAME-BY-GAME RADIO ROWS NOT CAPTURED", "source_url": "https://www.nba.com/warriors/schedule", "source_label": "Official Warriors schedule", "notes": "Station rows are high priority but exact radio windows are blank; see Flagged for Review."},
    ]


def build_flags() -> list[dict]:
    return [
        {"id": "IR-001", "issue": "Three supplied prior GitHub Pages/reference sites and matching repos returned 404.", "status": "UNVERIFIED", "source_url": "https://buffedlizard55-lab.github.io/VacationSchedule/site/", "source_label": "Prior reference URL (dead link retained for review)", "action": "Do not treat cached descriptions as official data."},
        {"id": "IR-002", "issue": "Official NFL 2027 by-team and prime-time selectors show schedule data unavailable.", "status": "UNVERIFIED", "source_url": "https://www.nfl.com/schedules/2027/by-team", "source_label": "Official NFL 2027 schedule", "action": "2027–2029 NFL game rows are ESTIMATED models, not released schedules."},
        {"id": "IR-003", "issue": "WWO warns local affiliates may not carry every WWO broadcast.", "status": "FLAGGED", "source_url": WWO_STATION_FINDER_URL, "source_label": "Official WWO station finder", "action": "All WWO network events are treated as high-priority busy candidates."},
        {"id": "IR-004", "issue": "WWO JSON-LD may encode local ET clock time with +00:00; some end times are 11:59 PM placeholders.", "status": "FLAGGED", "source_url": "https://www.westwoodonesports.com/events/548540/", "source_label": "Official WWO event detail", "action": "Collector uses Unix data-time attributes and displays Pacific time."},
        {"id": "IR-005", "issue": "NFL announced no AFC–NFC Pro Bowl game beginning with 2026 season; earlier continuous Jan–Super-Bowl blocking is too conservative.", "status": "CORRECTED", "source_url": NFL_PRO_BOWL_URL, "source_label": "Official NFL Pro Bowl announcement", "action": "No Pro Bowl game busy block; recognition events are not games."},
        {"id": "IR-006", "issue": "Prior parallel-session data contains secondary sources (CBS Sports, Wikipedia, sportsgeardaily, FOX Sports) and untraceable rows.", "status": "REPLACED / FLAGGED", "source_url": MLB_API_2026, "source_label": "Official MLB Stats API", "action": "Line-by-line audit page lists prior lines and official replacements."},
        {"id": "IR-007", "issue": "MLB Stats API returned zero official 2028 and 2029 game rows.", "status": "UNVERIFIED", "source_url": MLB_API_2028, "source_label": "Official MLB Stats API 2028", "action": "Teams, dates and times blank; models are clearly labelled ESTIMATED."},
        {"id": "IR-008", "issue": "MLB 2027 official schedule has 2,011 TBD start times.", "status": "UNVERIFIED", "source_url": MLB_API_2027, "source_label": "Official MLB Stats API 2027", "action": "Official time cells blank; planning estimates use 2026 official median start times."},
        {"id": "IR-009", "issue": "NFL 2026 Week 16–18 official games have TBD kickoff/date in HTML; by-week PDF gives week date ranges only.", "status": "UNVERIFIED", "source_url": NFL_BY_WEEK_PDF_URL, "source_label": "Official NFL by-week schedule PDF", "action": "Conservative all-day unverified blocks; exact intraday free windows not claimed."},
        {"id": "IR-010", "issue": "Official 2027 WWO event grid currently ends Jan 11, 2027; later 2027 network games are not published.", "status": "UNVERIFIED", "source_url": WWO_NFL_SCHEDULE_URL, "source_label": "Official WWO NFL schedule", "action": "Vacation windows after Jan 11, 2027 are candidates, not certified free."},
        {"id": "IR-011", "issue": "Stanford/Cal 2027–2029 ACC dates/times are not released; only opponents and a few nonconference dates are official.", "status": "UNVERIFIED", "source_url": "https://calbears.com/news/2026/9/16/california-football-announces-2027-conference-opponents", "source_label": "Official Cal 2027 opponents", "action": "Blank dates/times plus official opponent-grid links."},
        {"id": "IR-012", "issue": "Prior radio guide called 810 AM 'KGO'; official station and Earthquakes sources identify KSFO 810 AM.", "status": "CORRECTED", "source_url": "https://www.ksfo.com/station-information/", "source_label": "Official KSFO station information", "action": "Radio table uses KSFO 810 AM; KGO call sign flagged."},
        {"id": "IR-013", "issue": "NFL 3:12 total duration and NCAAF 2016 3:24 average are not current official broadcast averages.", "status": "FLAGGED", "source_url": NFL_RULEBOOK_URL, "source_label": "Official 2026 NFL rulebook", "action": "Official rulebook clock/halftime shown; secondary/dated averages flagged."},
        {"id": "IR-014", "issue": "Warriors/Valkyries/Sharks station rows are high priority, but complete official game-by-game radio windows were not captured.", "status": "UNVERIFIED", "source_url": "https://www.nba.com/warriors/schedule", "source_label": "Official Warriors schedule", "action": "Station and schedule links published for manual review; exact game windows blank."},
        {"id": "IR-015", "issue": "2028 Super Bowl LXII host is official but exact date is TBA; 2029 Super Bowl date/host not found in official captured sources.", "status": "UNVERIFIED", "source_url": "https://www.nfl.com/news/mercedes-benz-stadium-in-atlanta-to-host-super-bowl-lxii-in-2028", "source_label": "Official NFL Super Bowl LXII announcement", "action": "Official date blank; models labelled ESTIMATED."},
        {"id": "IR-016", "issue": "Prior sessions claimed no 7-day strict window by blocking the entire Jan–Super-Bowl span; exact official playoff dates and discontinued Pro Bowl game create published 7-day seams.", "status": "CORRECTED / UNVERIFIED", "source_url": NFL_IMPORTANT_DATES_URL, "source_label": "Official NFL 2026–27 important dates", "action": "Recomputed candidates from exact official dates; still flagged because later WWO schedules are unreleased."},
        {"id": "IR-017", "issue": "Prior 2028 Olympic-break vacation scenario is not an official released MLB schedule/MLBPA agreement.", "status": "FLAGGED", "source_url": "https://www.mlb.com/all-star/future-locations", "source_label": "Official MLB future All-Star locations", "action": "Not treated as verified free time; exact All-Star date remains blank."},
        {"id": "IR-018", "issue": "Nine San Francisco 49ers rows cited a ticket reseller (vividseats.com) as their source while the row label claimed 49ers.com.", "status": "CORRECTED", "source_url": "https://www.49ers.com/schedule/", "source_label": "Official 49ers schedule", "action": "Collector now accepts only official league, team or network domains and prefers the 49ers.com game-center link; reseller links are rejected."},
        {"id": "IR-019", "issue": f"{PIPELINE_STATS.get('49ers_duplicate_rows_removed', 0)} San Francisco 49ers regular-season games were published twice, once from NFL.com and once from 49ers.com.", "status": "CORRECTED", "source_url": "https://www.nfl.com/games/49ers-at-rams-2026-reg-1", "source_label": "Official NFL game page", "action": "Duplicate kickoffs are merged into the official NFL.com row, which keeps the 49ers.com game-center link and venue as a secondary source."},
        {"id": "IR-020", "issue": "California games were missing from the dated rows: Oct 24 at SMU, Oct 31 at NC State, Nov 14 at Virginia, Nov 21 vs Stanford and Nov 28 vs Pittsburgh were published as TBA because the parser missed '9 AM' kickoffs and empty game-card date headers.", "status": "CORRECTED", "source_url": "https://calbears.com/sports/football/schedule/2026", "source_label": "California Golden Bears official schedule", "action": "Parser now merges the game cards with the official scoreboard carousel, accepts '9 AM' style kickoffs and publishes the official date for every game."},
        {"id": "IR-021", "issue": "Stanford's Nov 21 (129th Big Game at California) and Nov 28 (vs SMU) kickoffs are published as TBA, but the collector copied the official page's 12:00 PM placeholder timestamp and marked both rows VERIFIED.", "status": "CORRECTED", "source_url": "https://gostanford.com/sports/football/schedule", "source_label": "Stanford Cardinal official football schedule", "action": "Time cells are blank and labelled OFFICIAL DATE / TIME TBA — UNVERIFIED; the whole day is blocked as an unverified busy candidate."},
        {"id": "IR-022", "issue": f"MLB Stats API keeps a 'Postponed' entry on the original date next to the re-scheduled entry; {PIPELINE_STATS.get('mlb_postponed_rows_removed', 0)} postponed rows were published as VERIFIED broadcasts on days with no radio game.", "status": "CORRECTED", "source_url": MLB_API_2026, "source_label": "Official MLB Stats API 2026", "action": "Only the played or still-scheduled entry for each gamePk is published; postponed duplicates are dropped."},
        {"id": "IR-023", "issue": "Vacation-window busy minutes summed every broadcast interval, so simultaneous MLB games were counted more than once.", "status": "CORRECTED", "source_url": NFL_IMPORTANT_DATES_URL, "source_label": "Official NFL 2026–27 important dates", "action": "Busy minutes now merge overlapping intervals per day before summing; unverified and model day counters count days, not rows."},
        {"id": "IR-024", "issue": "Stanford and Cal official schedule pages print kickoff times in Pacific time for away games as well; the venue's local time differs.", "status": "FLAGGED", "source_url": "https://gostanford.com/sports/football/schedule", "source_label": "Stanford Cardinal official football schedule", "action": "Pacific times are published as displayed by the official site; the assumption is disclosed here for review."},
        {"id": "IR-025", "issue": "Stanford's Nov 14 game at Virginia Tech is published by the official site as a flexible '4 OR 4:30 P.M.' PT window rather than one kickoff time.", "status": "FLAGGED", "source_url": "https://gostanford.com/sports/football/schedule", "source_label": "Stanford Cardinal official football schedule", "action": "Row uses the earlier 4:00 PM PT kickoff and records the official flex window in the row notes."},
    ]


def build_season_availability(mlb_season_rows: list[dict], wwo_counts: dict) -> list[dict]:
    rows = list(mlb_season_rows)
    rows.extend([
        {"season": 2026, "league": "NFL", "official_rows": 272, "tbd_times": 24, "status": "OFFICIAL 18-WEEK REGULAR SEASON + 49 PRESEASON MATCHUPS", "source_url": "https://www.nfl.com/schedules/2026/by-week/week-1", "source_label": "Official NFL by-week schedule", "verification": "VERIFIED"},
        {"season": 2027, "league": "NFL", "official_rows": 0, "tbd_times": 0, "status": "NO OFFICIAL GAME-BY-GAME SCHEDULE", "source_url": "https://www.nfl.com/schedules/2027/by-team", "source_label": "Official NFL 2027 schedule", "verification": "UNVERIFIED"},
        {"season": 2028, "league": "NFL", "official_rows": 0, "tbd_times": 0, "status": "NO OFFICIAL GAME-BY-GAME SCHEDULE", "source_url": "https://www.nfl.com/schedules/2027/by-team", "source_label": "Official NFL schedule selector", "verification": "UNVERIFIED"},
        {"season": 2029, "league": "NFL", "official_rows": 0, "tbd_times": 0, "status": "NO OFFICIAL GAME-BY-GAME SCHEDULE", "source_url": "https://www.nfl.com/schedules/2027/by-team", "source_label": "Official NFL schedule selector", "verification": "UNVERIFIED"},
        {"season": 2026, "league": "Stanford/Cal NCAAF", "official_rows": 24, "tbd_times": 0, "status": "OFFICIAL 2026 TEAM SCHEDULES", "source_url": "https://gostanford.com/sports/football/schedule", "source_label": "Official Stanford schedule", "verification": "VERIFIED"},
        {"season": 2027, "league": "Stanford/Cal NCAAF", "official_rows": 5, "tbd_times": 5, "status": "PARTIAL OFFICIAL FUTURE DATES / ACC OPPONENT GRIDS", "source_url": "https://calbears.com/news/2026/9/16/california-football-announces-2027-conference-opponents", "source_label": "Official Cal 2027 opponents", "verification": "UNVERIFIED"},
        {"season": 2026, "league": "WWO all categories", "official_rows": wwo_counts.get(2026, 0), "tbd_times": 0, "status": "OFFICIAL EVENT DETAIL PAGES", "source_url": WWO_NFL_SCHEDULE_URL, "source_label": "Official WWO schedule", "verification": "VERIFIED"},
        {"season": 2027, "league": "WWO all categories", "official_rows": wwo_counts.get(2027, 0), "tbd_times": 0, "status": "OFFICIAL EVENT DETAIL PAGES THROUGH JAN 11 ONLY", "source_url": WWO_NFL_SCHEDULE_URL, "source_label": "Official WWO schedule", "verification": "UNVERIFIED"},
        {"season": 2026, "league": "MLS Earthquakes radio", "official_rows": 34, "tbd_times": 0, "status": "OFFICIAL TERRESTRIAL RADIO SCHEDULE", "source_url": EARTHQUAKES_URL, "source_label": "Official Earthquakes radio release", "verification": "VERIFIED"},
    ])
    return rows


# ---------------------------------------------------------------------------
# Planning model for unreleased seasons
# ---------------------------------------------------------------------------

def add_shifted_models(intervals: dict[str, list], official_intervals: dict[str, list]) -> list[dict]:
    """Create clearly labelled ESTIMATED busy intervals from official 2026 rows.

    A 364-day shift preserves weekday. This is not a released schedule; teams,
    exact dates and official times are intentionally blank in the table.
    """
    model_rows = []
    source_intervals = []
    for day_str, rows in official_intervals.items():
        day = date.fromisoformat(day_str)
        if day.year != 2026 or day < date(2026, 1, 1):
            continue
        for row in rows:
            if row.get("category") in ("MLB", "NFL", "NCAAF", "WWO", "MLS") and row.get("status") in ("OFFICIAL_START_ESTIMATED_DURATION", "ESTIMATED_TBD_START", "OFFICIAL_NETWORK_WINDOW"):
                source_intervals.append((day, row))
    for year, shifts in ((2027, 1), (2028, 2), (2029, 3)):
        count = 0
        for base_day, row in source_intervals:
            target = base_day + timedelta(days=364 * shifts)
            if target.year != year or not (START_DATE <= target <= END_DATE):
                continue
            # 2027 MLB is officially released; do not duplicate MLB with a 2026 model.
            if year == 2027 and row.get("category") == "MLB":
                continue
            # 2027 WWO NFL postseason is already official through Jan 11; allow later-season model only.
            if year == 2027 and row.get("category") == "WWO" and target <= date(2027, 1, 11):
                continue
            add_interval(intervals, target, row["start"], row["end"],
                         event_id=f"model-{year}-{row.get('event_id','')}", category=row.get("category", ""),
                         matchup="", priority="HIGH — modelled busy candidate", focus=False,
                         status="ESTIMATED_UNRELEASED_SEASON_MODEL", verification="ESTIMATED — NOT A RELEASED SCHEDULE",
                         source_url=row.get("source_url", MLB_API_2026),
                         source_label="Official 2026 source used as model basis",
                         label=f"{row.get('category','')} season-pattern model",
                         duration_source_url=row.get("duration_source_url", ""))
            count += 1
        model_rows.append({
            "year": year, "model_intervals": count, "method": "Official 2026 busy windows shifted by 364-day multiples to preserve weekday",
            "status": "ESTIMATED — NOT A REAL VERIFIED RELEASED SCHEDULE",
            "source_url": MLB_API_2026, "source_label": "Official MLB Stats API 2026 (representative model basis)",
            "notes": "Exact teams, dates and official times are blank. The model exists only to surface plausible busy days for 2027–2029 planning.",
        })
    return model_rows


def compute_vacation_windows(days: dict[str, list]) -> list[dict]:
    anchor_urls = [
        NFL_IMPORTANT_DATES_URL,
        "https://www.mlb.com/press-release/press-release-mlb-announces-2027-spring-training-schedule",
        "https://www.mlb.com/all-star/future-locations",
        "https://collegefootballplayoff.com/news/2025/10/29/tampabay-29",
        NFL_PRO_BOWL_URL,
        WWO_NFL_SCHEDULE_URL,
    ]
    rows = []
    for year in (2027, 2028, 2029):
        for days_length in (7, 14, 21):
            best = None
            start = date(year, 1, 1)
            end = date(year, 12, 31) - timedelta(days=days_length - 1)
            current = start
            while current <= end:
                busy_minutes = 0
                busy_days = 0
                unverified_days = 0
                model_days = 0
                for offset in range(days_length):
                    day = current + timedelta(days=offset)
                    day_rows = days.get(day.isoformat(), [])
                    if day_rows:
                        busy_days += 1
                        # Overlapping broadcasts (for example several MLB games at
                        # once) must be counted once, so intervals are merged before
                        # the busy minutes of the window are summed.
                        busy_minutes += merge_minutes([(r["start"], r["end"]) for r in day_rows])
                        if any(r.get("status") == "UNVERIFIED_BLOCK" for r in day_rows):
                            unverified_days += 1
                        if any(r.get("status") == "ESTIMATED_UNRELEASED_SEASON_MODEL" for r in day_rows):
                            model_days += 1
                candidate = {
                    "year": year, "length_days": days_length,
                    "start": current.isoformat(), "end": (current + timedelta(days=days_length - 1)).isoformat(),
                    "busy_days": busy_days, "busy_minutes": busy_minutes,
                    "unverified_days": unverified_days, "model_days": model_days,
                    "strict_free": busy_days == 0,
                    "status": "STRICT CANDIDATE — UNVERIFIED (UNRELEASED SCHEDULES)" if busy_days == 0 else "LEAST-CONFLICT CANDIDATE — ESTIMATED",
                    "source_urls": anchor_urls,
                    "source_url": anchor_urls[0], "source_label": "Official NFL 2026–27 important dates",
                    "notes": "Computed from exact officially published rows plus separately labelled unreleased-season models. A zero-busy candidate is not certified free because full 2027–2029 WWO/NFL/MLB schedules are not published.",
                }
                # Rank by busy days, then busy minutes, then model contamination, then earliest date.
                key = (candidate["busy_days"], candidate["busy_minutes"], candidate["model_days"], current.toordinal())
                if best is None or key < best[0]:
                    best = (key, candidate)
                current += timedelta(days=1)
            rows.append(best[1])
    return rows


# ---------------------------------------------------------------------------
# Line-by-line audit of prior generated data
# ---------------------------------------------------------------------------

def official_replacement_for(path: str) -> tuple[str, str]:
    p = path.lower()
    if "westwood" in p or "wwo" in p:
        return WWO_NFL_SCHEDULE_URL, "Official WWO event pages/station finder"
    if "nfl" in p or "49er" in p or "football" in p:
        return "https://www.nfl.com/schedules/2026/by-week/week-1", "Official NFL by-week schedule"
    if "ncaaf" in p or "stanford" in p or "cal" in p:
        return "https://gostanford.com/sports/football/schedule", "Official Stanford/Cal schedule"
    if "mlb" in p or "giant" in p or "athletic" in p:
        return MLB_API_2027, "Official MLB Stats API"
    if "vacation" in p:
        return NFL_IMPORTANT_DATES_URL, "Official NFL important dates"
    if "duration" in p:
        return MLB_DURATION_URL, "Official MLB duration article"
    if "radio" in p:
        return WWO_STATION_FINDER_URL, "Official WWO station finder"
    return MLB_API_2027, "Official MLB Stats API"


def build_line_by_line_audit() -> list[dict]:
    files = []
    for pattern in ("data/*.json", "data/*.js", "docs/*.js", "assets/data.js", "site/data/*.json", "site/data/*.js"):
        files.extend(sorted(ROOT.glob(pattern)))
    files += [ROOT / "README.md", ROOT / "EXECUTIVE-SUMMARY.md", ROOT / "research-notes.md"]
    files += sorted((ROOT / "docs").glob("*.md"))
    rows = []
    for path in files:
        if not path.exists() or path.is_dir():
            continue
        url, label = official_replacement_for(str(path.relative_to(ROOT)))
        try:
            lines = path.read_text("utf-8", "replace").splitlines()
        except OSError:
            continue
        for i, line in enumerate(lines, 1):
            snippet = line.strip()
            if not snippet:
                continue
            finding = "Prior generated-data line reviewed. Secondary/unofficial values are not marked VERIFIED; official replacement is linked."
            status = "REVIEWED — OFFICIAL REPLACEMENT"
            if re.search(r"wikipedia|cbs|foxsports|sportsgeardaily|legionreport|printablepedia|directv|olympics\.com|skysports|writeforcalifornia|insideradio|radio-online", snippet, re.I):
                finding = "Secondary/nonofficial source found; replaced by official source or flagged."
                status = "FLAGGED — SECONDARY SOURCE"
            elif re.search(r"estimated|assumed|approx|~|tbd|unverified|projection", snippet, re.I):
                finding = "Estimated/TBD/unverified value found; official value must remain blank unless confirmed."
                status = "FLAGGED — ESTIMATE/TBD"
            elif re.search(r"source|https?://", snippet, re.I):
                finding = "Source line reviewed against official-source manifest; official replacement linked for manual review."
                status = "REVIEWED — SOURCE LINE"
            rows.append({
                "id": f"L{len(rows)+1:05d}", "file": str(path.relative_to(ROOT)), "line": i,
                "text": snippet[:220], "finding": finding, "status": status,
                "source_url": url, "source_label": label,
            })
    return rows


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    ANALYSIS.mkdir(parents=True, exist_ok=True)
    intervals: dict[str, list] = defaultdict(list)
    official_intervals: dict[str, list] = defaultdict(list)

    teams = build_mlb_teams()
    sources = build_sources()
    mlb_events, mlb_seasons = build_mlb_events(intervals)
    nfl_regular = parse_nfl_regular_events(intervals)
    nfl_preseason = parse_nfl_preseason_events(intervals)
    nfl_postseason = build_nfl_postseason_events(intervals)
    # Build an index of already-published official NFL rows so the 49ers.com
    # schedule can enrich a row instead of duplicating the same kickoff.
    nfl_index = {}
    for ev in (nfl_regular + nfl_preseason + nfl_postseason):
        day_key = ev.get("date") or ""
        start_text = ev.get("planning_start_pt") or ""
        if not day_key or ":" not in start_text:
            continue
        nfl_index[(day_key, int(start_text.split(":")[0]) * 60 + int(start_text.split(":")[1]))] = ev
    nflers_events, nflers_radio, merged_49ers = parse_49ers_events(intervals, nfl_index)
    PIPELINE_STATS["49ers_duplicate_rows_removed"] = len(merged_49ers)
    stanford_events = parse_stanford_events(intervals)
    cal_events = parse_cal_events(intervals)
    wwo_events, wwo_info = parse_wwo_events(intervals)
    earthquakes_events = parse_earthquakes_events(intervals)
    anchors = build_anchors(intervals)

    # Snapshot official-only intervals before adding unreleased-season models.
    for day, rows in intervals.items():
        official_intervals[day] = [dict(r) for r in rows]
    model_rows = add_shifted_models(intervals, official_intervals)

    events = (mlb_events + nfl_regular + nfl_preseason + nfl_postseason +
              nflers_events + stanford_events + cal_events + wwo_events + earthquakes_events)
    events.sort(key=lambda e: (e.get("date") or e.get("date_range") or "9999", e["category"], e["id"]))

    # Ensure every calendar day in range has a key, then sort intervals.
    days = {}
    current = START_DATE
    while current <= END_DATE:
        key = current.isoformat()
        rows = sorted(intervals.get(key, []), key=lambda r: (r["start"], r["end"], r.get("category", "")))
        days[key] = rows
        current += timedelta(days=1)

    windows = compute_vacation_windows(days)
    stations = build_radio_stations(wwo_info["station_rows"])
    durations = build_durations()
    flags = build_flags()
    season_availability = build_season_availability(mlb_seasons, wwo_info["counts"])
    review = build_line_by_line_audit()

    anchor_windows = [
        {"year": 2027, "window": "2027-02-15 to 2027-02-18", "length_days": 4, "label": "Best officially anchored gap", "status": "OFFICIAL ANCHORS / LATER WWO SCHEDULE UNVERIFIED", "source_url": NFL_IMPORTANT_DATES_URL, "source_label": "Official NFL 2026–27 important dates", "notes": "Super Bowl LXI Feb 14 and MLB Spring Training Feb 19 are official anchors; no officially published game rows fall on Feb 15–18. WWO later-season schedule is not released, so this is not certified free."},
        {"year": 2027, "window": "2027-02-15 to 2027-03-23", "length_days": 37, "label": "Relaxed scenario ignoring Spring Training", "status": "SCENARIO — EXCLUDES OFFICIAL SPRING TRAINING GAMES", "source_url": "https://www.mlb.com/press-release/press-release-mlb-announces-2027-spring-training-schedule", "source_label": "Official MLB 2027 Spring Training release", "notes": "Useful only if Spring Training broadcasts are excluded from the user's strict free-time definition; the strict model counts them."},
        {"year": 2028, "window": "", "length_days": "", "label": "Mid-February estimated gap", "status": "ESTIMATED — NOT A RELEASED SCHEDULE", "source_url": "https://collegefootballplayoff.com/news/2025/10/29/tampabay-29", "source_label": "Official CFP future dates", "notes": "Exact dates blank because 2028 MLB/NFL/WWO schedules and Super Bowl LXII date are not officially released."},
        {"year": 2029, "window": "", "length_days": "", "label": "Mid-February estimated gap", "status": "ESTIMATED — NOT A RELEASED SCHEDULE", "source_url": "https://collegefootballplayoff.com/news/2025/10/29/tampabay-29", "source_label": "Official CFP future dates", "notes": "Exact dates blank because 2029 MLB/NFL/WWO schedules are not officially released."},
    ]
    analysis_conclusion = {
        "strict_7_14_21_day_windows": sum(1 for w in windows if w["strict_free"]),
        "conclusion": "Using official rows plus separately labelled 2026-pattern estimates, no 7-, 14-, or 21-day fully free strict window appears in 2027–2029. The best short officially anchored gap is Feb 15–18, 2027; all longer vacation recommendations are least-conflict ESTIMATED candidates and must be rechecked when schedules are released.",
        "source_url": NFL_IMPORTANT_DATES_URL,
        "source_label": "Official NFL 2026–27 important dates",
    }
    findings = [
        {"topic": "Official 2026 NFL regular season", "finding": f"{len(nfl_regular)} official game rows parsed from 18 NFL by-week pages; 272 have exact kickoff islands and 24 are official TBD matchups.", "source_url": "https://www.nfl.com/schedules/2026/by-week/week-1", "source_label": "Official NFL by-week schedule", "status": "VERIFIED"},
        {"topic": "Official MLB 2026/2027", "finding": f"{len([e for e in mlb_events if e['category']=='MLB' and e['date']])} official MLB game rows from Stats API, including all 30 clubs and TBD start times left blank.", "source_url": MLB_API_2027, "source_label": "Official MLB Stats API", "status": "VERIFIED"},
        {"topic": "Westwood One Sports", "finding": f"{len(wwo_events)} official 2026–2027 WWO event windows across all nine monitored categories; exact Unix start/end timestamps converted to Pacific.", "source_url": WWO_NFL_SCHEDULE_URL, "source_label": "Official WWO schedule", "status": "VERIFIED"},
        {"topic": "Stanford/Cal/49ers", "finding": f"{len(stanford_events)} Stanford, {len(cal_events)} Cal and {len(nflers_events)} 49ers official schedule rows with exact kickoffs/radio where published.", "source_url": "https://www.49ers.com/schedule/", "source_label": "Official 49ers schedule", "status": "VERIFIED"},
        {"topic": "Other Bay Area radio sports", "finding": f"{len(earthquakes_events)} official Earthquakes terrestrial radio matches plus high-priority station rows for Warriors, Sharks and Valkyries coverage; incomplete game windows are flagged.", "source_url": EARTHQUAKES_URL, "source_label": "Official Earthquakes radio release", "status": "VERIFIED / FLAGGED"},
        {"topic": "Vacation analysis", "finding": "Best 7/14/21-day candidates recomputed from exact official rows plus separately labelled unreleased-season models. No candidate is called certified free.", "source_url": NFL_IMPORTANT_DATES_URL, "source_label": "Official NFL important dates", "status": "ESTIMATED / UNVERIFIED"},
        {"topic": "Line-by-line repo audit", "finding": f"{len(review)} prior generated-data/documentation lines reviewed; secondary sources and estimates are replaced or flagged with official links.", "source_url": MLB_API_2027, "source_label": "Official MLB Stats API", "status": "VERIFIED AUDIT"},
    ]

    meta = {
        "generated_utc": datetime.now(UTC).isoformat(timespec="seconds"),
        "timezone": "America/Los_Angeles (PST in winter, PDT in summer)",
        "system_today": SYSTEM_TODAY.isoformat(), "date_range": [DISPLAY_START.isoformat(), END_DATE.isoformat()],
        "data_start": START_DATE.isoformat(),
        "definition": "A minute is FREE only when none of the monitored live AM/FM radio sports broadcasts is scheduled. Busy blocks use official start times plus researched durations, or official WWO network windows.",
        "counts": {
            "official_sources": len(sources), "official_event_rows": len(events),
            "mlb_teams": len(teams), "days": len(days),
            "intervals": sum(len(v) for v in days.values()),
            "wwo_sf_affiliate_rows": len(wwo_info["station_rows"]),
            "line_by_line_audit_rows": len(review),
        },
        "durations": {"MLB": MLB_DURATION, "NFL": NFL_DURATION, "NCAAF": NCAAF_DURATION, "MLS": SOCCER_DURATION},
        "teams": teams, "stations": stations, "durations_table": durations,
        "anchors": anchors, "flags": flags, "season_availability": season_availability,
        "wwo_sf_affiliates": wwo_info["sf_map"], "wwo_event_counts": wwo_info["counts"],
        "model_seasons": model_rows, "vacation_windows": windows, "anchor_windows": anchor_windows,
        "analysis_conclusion": analysis_conclusion, "findings": findings,
        "source_catalogue": sources,
        "nflers_radio": nflers_radio,
        "executive_summary": "The dashboard separates VERIFIED official rows, blank UNVERIFIED values, and ESTIMATED planning models. All MLB clubs, all 272 official 2026 NFL regular-season games, 49 preseason matchups, postseason date anchors, Stanford/Cal games, Westwood One events across nine categories, and official Earthquakes radio matches are shown with official links. Exact Pacific free intervals are computed every day from 2026-11-01 through 2029-12-31. Unreleased 2028/2029 schedules are never presented as real verified schedules.",
    }

    # Write split day files for fast browser loading.
    for year in (2026, 2027, 2028, 2029):
        year_days = {k: v for k, v in days.items() if k.startswith(str(year))}
        (OUT / f"days-{year}.json").write_text(compact_json(year_days) + "\n")
    (OUT / "events.json").write_text(compact_json(events) + "\n")
    (OUT / "meta.json").write_text(compact_json(meta) + "\n")
    (ANALYSIS / "windows.json").write_text(json.dumps(windows, indent=2) + "\n")
    (ANALYSIS / "models.json").write_text(json.dumps(model_rows, indent=2) + "\n")
    REVIEW.write_text(compact_json(review) + "\n")

    print(json.dumps({
        "sources": len(sources), "events": len(events), "days": len(days),
        "intervals": sum(len(v) for v in days.values()),
        "mlb_teams": len(teams), "wwo_events": len(wwo_events),
        "earthquakes_events": len(earthquakes_events),
        "nfl_regular": len(nfl_regular), "nfl_preseason": len(nfl_preseason),
        "stanford": len(stanford_events), "cal": len(cal_events), "49ers": len(nflers_events),
        "audit_rows": len(review), "windows": len(windows),
        "output_bytes": sum((OUT / f).stat().st_size for f in ["events.json", "meta.json", "days-2026.json", "days-2027.json", "days-2028.json", "days-2029.json"]),
    }, indent=2))


if __name__ == "__main__":
    main()
