#!/usr/bin/env python3
"""Fetch compressed official-source snapshots for line-by-line verification.

The sandbox cannot reach most official sports hosts directly; this script is
executed by GitHub Actions, where the requests succeed. It stores gzipped raw
responses and a manifest with exact URL, status, byte count and SHA-256. No
schedule values are inferred here: downstream parsing reads only these raw
official responses plus the earlier `research/probe/raw` snapshots.
"""
from __future__ import annotations

import argparse
import gzip
import hashlib
import json
import re
import threading
import time
import urllib.error
import urllib.parse
import urllib.request
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "research" / "official" / "raw"
MANIFEST = ROOT / "research" / "official" / "manifest.json"
CATEGORY_MAP = ROOT / "research" / "official" / "wwo_event_categories.json"
PROBE_SUMMARY = ROOT / "research" / "probe" / "summary.json"

UA = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/124 Safari/537.36 Korea4OfficialResearch/1.0"

MLB_FIELDS = (
    "copyright,totalGames,dates,date,totalGames,games,gamePk,gameDate,officialDate,"
    "gameType,season,teams,away,team,id,name,home,team,id,name,venue,id,name,"
    "status,startTimeTBD,detailedState,seriesDescription,doubleHeader,dayNight,"
    "description,ifNecessary,gameNumber"
)

STATIC_SOURCES = {
    # Machine-readable MLB schedules and all 30 clubs.
    "mlb_2026_all": "https://statsapi.mlb.com/api/v1/schedule?sportId=1&season=2026&fields=" + urllib.parse.quote(MLB_FIELDS, safe=","),
    "mlb_2027_all": "https://statsapi.mlb.com/api/v1/schedule?sportId=1&season=2027&fields=" + urllib.parse.quote(MLB_FIELDS, safe=","),
    "mlb_2028_all": "https://statsapi.mlb.com/api/v1/schedule?sportId=1&season=2028&fields=" + urllib.parse.quote(MLB_FIELDS, safe=","),
    "mlb_2029_all": "https://statsapi.mlb.com/api/v1/schedule?sportId=1&season=2029&fields=" + urllib.parse.quote(MLB_FIELDS, safe=","),
    "mlb_teams_2027": "https://statsapi.mlb.com/api/v1/teams?sportId=1&season=2027",
    "mlb_schedule_2027_03_25": "https://www.mlb.com/schedule/2027-03-25",
    "mlb_2027_spring_release": "https://www.mlb.com/press-release/press-release-mlb-announces-2027-spring-training-schedule",
    "mlb_2027_regular_release": "https://www.mlb.com/tigers/news/mlb-2027-schedule-released",
    "mlb_2027_all_star": "https://www.mlb.com/news/2027-mlb-all-star-game-at-wrigley-field",
    "mlb_future_all_star": "https://www.mlb.com/all-star/future-locations",
    "mlb_duration_2025": "https://www.mlb.com/news/mlb-average-game-time-under-three-hours-third-straight-year",
    # NFL official schedule, dates, rules, postseason and 2027 unavailability.
    "nfl_2026_release": "https://media.nfl.com/football-information/2026/news/2026-nfl-schedule-announced",
    "nfl_preseason_pdf": "https://media.nfl.com/content/dam/communications/football-communications/2026/news/05%2014%2026%20-%20Preseason%20Schedule.pdf",
    "nfl_preseason_pdf_http": "http://media.nfl.com/content/dam/communications/football-communications/2026/news/05%2014%2026%20-%20Preseason%20Schedule.pdf",
    "nfl_2026_by_week_pdf": "https://media.nfl.com/content/dam/communications/football-communications/2026/news/05%2014%2026%20-%202026%20NFL%20Schedule%20-%20By%20Week.pdf",
    "nfl_important_dates": "https://www.nfl.com/news/2026-27-national-football-league-important-dates",
    "nfl_2027_by_team": "https://www.nfl.com/schedules/2027/by-team",
    "nfl_2027_prime": "https://www.nfl.com/schedules/2027/prime-time",
    "nfl_2028_super_bowl": "https://www.nfl.com/news/mercedes-benz-stadium-in-atlanta-to-host-super-bowl-lxii-in-2028",
    "nfl_pro_bowl_discontinued": "https://www.nfl.com/news/nfl-elevates-pro-bowl-selection-game-s-will-cease-being-contested",
    "nfl_2026_rulebook_pdf": "https://media.nfl.com/content/dam/communications/Official%20Playing%20Rules/2026%20Official%20Playing%20Rules.pdf",
    # CFP official future dates.
    "cfp_2029_dates": "https://collegefootballplayoff.com/news/2025/10/29/tampabay-29",
    "cfp_2027_broadcast": "https://collegefootballplayoff.com/news/2026/6/1/26-27-broadcast-sked",
    "cfp_2027_championship": "https://collegefootballplayoff.com/news/2026/4/7/lv-april-newsconf",
    # Stanford/Cal current and future official sources.
    "stanford_schedule_current": "https://gostanford.com/sports/football/schedule",
    "stanford_2026_schedule_release": "https://gostanford.com/news/2026/01/26/complete-2026-schedule-unveiled",
    "stanford_2027_conference_opponents": "https://gostanford.com/news/2026/09/16/acc-announces-2027-conference-opponents",
    "stanford_2027_2028_notre_dame": "https://gostanford.com/news/2026/05/20/two-dates-added-to-notre-dame-rivalry",
    "stanford_2027_tcu_canceled": "https://gostanford.com/news/2026/04/17/tcu-series-update",
    "stanford_future_model": "https://gostanford.com/news/2023/10/30/acc-announces-football-schedule-model",
    "stanford_radio": "https://gostanford.com/news/2026/07/30/2026-football-radio-broadcast-team-announced",
    "cal_schedule_current": "https://calbears.com/sports/football/schedule/2026",
    "cal_2026_schedule_release": "https://calbears.com/news/2026/1/26/california-football-announces-2026-schedule.aspx",
    "cal_2027_nonconference": "https://calbears.com/news/2026/6/25/football-cal-announces-matchups-against-odu-sac-state",
    "cal_2027_conference_opponents": "https://calbears.com/news/2026/9/16/california-football-announces-2027-conference-opponents",
    "cal_future_model": "https://calbears.com/news/2023/10/30/acc-announces-conference-football-matchups-for-2024-30.aspx",
    "ncaa_football_rules": "https://www.ncaa.org/championships/playing-rules/football-playing-rules/",
    "ncaa_game_length_2016": "https://www.ncaa.com/news/football/article/2017-02-28/competition-committee-advise-football-rules",
    # Official radio / station / other Bay Area sports sources.
    "giants_radio": "https://www.mlb.com/giants/schedule/tv",
    "athletics_radio": "https://www.mlb.com/athletics/schedule/affiliates",
    "nflers_schedule": "https://www.49ers.com/schedule/",
    "wwo_station_finder": "https://www.westwoodonesports.com/station-finder/",
    "wwo_nfl_schedule": "https://www.westwoodonesports.com/nfl-schedule/",
    "knbr_schedule": "https://www.knbr.com/shows/",
    "ksfo_schedule": "https://www.ksfo.com/shows/",
    "game957_schedule": "https://www.957thegame.com/",
    "warriors_radio": "https://www.nba.com/warriors/news/957-the-game-extension-20190827",
    "sharks_radio": "https://www.nhl.com/sharks/news/san-jose-sharks-announce-2018-19-broadcast-schedule-300119102",
    "earthquakes_radio_2026": "https://www.sjearthquakes.com/news/news-earthquakes-announce-radio-stations-for-2026-mls-season",
    "ifab_laws": "https://www.theifab.com/laws/latest/the-players/",
}

WWO_GRIDS = {
    "NFL": "47029",
    "NCAA Football": "47030",
    "NCAA Basketball": "47031",
    "Soccer": "47032",
    "Golf": "47033",
    "NCAA Hockey": "47044",
    "NCAA Lacrosse": "47418",
    "NCAA WCWS": "47419",
    "NCAA MCWS": "47420",
}

GRID_NAME = {
    "NFL": "nfl",
    "NCAA Football": "ncaaf",
    "NCAA Basketball": "ncaab",
    "Soccer": "soccer",
    "Golf": "golf",
    "NCAA Hockey": "hockey",
    "NCAA Lacrosse": "lacrosse",
    "NCAA WCWS": "wcws",
    "NCAA MCWS": "mcws",
}

_lock = threading.Lock()
_manifest_entries: dict[str, dict] = {}
_force_keys: set[str] = set()


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def fetch_url(url: str, timeout: int = 35) -> tuple[int | None, bytes, str | None]:
    last_error = None
    for attempt in range(3):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept": "*/*"})
            with urllib.request.urlopen(req, timeout=timeout) as resp:
                return resp.status, resp.read(), None
        except urllib.error.HTTPError as exc:
            body = exc.read()
            # Save 404 payloads too; downstream parsers must know a source is unavailable.
            return exc.code, body, f"HTTP {exc.code}"
        except Exception as exc:  # DNS, TLS, timeout
            last_error = str(exc)
            time.sleep(0.5 * (attempt + 1))
    return None, b"", last_error


def save_raw(key: str, url: str, data: bytes, status: int | None, error: str | None) -> None:
    RAW.mkdir(parents=True, exist_ok=True)
    out = RAW / f"{key}.gz"
    compressed = gzip.compress(data, compresslevel=9, mtime=0)
    out.write_bytes(compressed)
    entry = {
        "key": key,
        "url": url,
        "http_status": status,
        "error": error,
        "bytes": len(data),
        "sha256": sha256(data),
        "compressed_bytes": len(compressed),
        "raw_file": f"research/official/raw/{key}.gz",
        "retrieved_utc": utc_now(),
    }
    with _lock:
        _manifest_entries[key] = entry


def fetch_and_save(key: str, url: str, refresh: bool = False) -> bytes:
    out = RAW / f"{key}.gz"
    if out.exists() and not refresh and key not in _force_keys:
        data = gzip.decompress(out.read_bytes())
        with _lock:
            prev = _manifest_entries.get(key)
            if prev:
                prev["url"] = url
                prev["retrieved_utc"] = prev.get("retrieved_utc") or utc_now()
        return data
    status, data, error = fetch_url(url)
    save_raw(key, url, data, status, error)
    return data


def grid_url(grid_id: str, offset: int) -> str:
    query = urllib.parse.urlencode({
        "id": grid_id,
        "range": "all",
        "offset": offset,
        "limit": 100,
        "timezone": "America/New_York",
        "widgetTitle": "Event Display",
    })
    return "https://www.westwoodonesports.com/more/eventGrid/?" + query


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--refresh", action="store_true", help="refetch all cached raw responses")
    parser.add_argument("--refresh-errors", action="store_true", help="retry cached error/empty responses")
    parser.add_argument("--max-events", type=int, default=1000)
    args = parser.parse_args()

    if MANIFEST.exists():
        old = json.loads(MANIFEST.read_text())
        _manifest_entries.update({entry["key"]: entry for entry in old.get("files", [])})
        if args.refresh_errors:
            _force_keys.update(
                entry["key"] for entry in old.get("files", [])
                if entry.get("error") or not entry.get("http_status") or entry.get("http_status", 0) >= 400 or entry.get("bytes", 0) == 0
            )

    # Static official pages and MLB APIs.
    jobs = [(key, url) for key, url in STATIC_SOURCES.items()]
    for week in range(1, 19):
        jobs.append((f"nfl_2026_week_{week:02d}", f"https://www.nfl.com/schedules/2026/by-week/week-{week}"))
    with ThreadPoolExecutor(max_workers=6) as pool:
        futures = [pool.submit(fetch_and_save, key, url, args.refresh) for key, url in jobs]
        for fut in as_completed(futures):
            fut.result()

    # WWO event grids. Walk offsets until no additional event IDs are exposed.
    event_categories: dict[str, list[str]] = {}
    grid_jobs = []
    for category, grid_id in WWO_GRIDS.items():
        for offset in (0, 100, 200):
            key = f"wwo_grid_{GRID_NAME[category]}_{offset}"
            grid_jobs.append((key, category, grid_url(grid_id, offset)))
    with ThreadPoolExecutor(max_workers=6) as pool:
        futmap = {pool.submit(fetch_and_save, key, url, args.refresh): (key, category, url) for key, category, url in grid_jobs}
        for fut in as_completed(futmap):
            key, category, url = futmap[fut]
            body = fut.result().decode("utf-8", "replace")
            ids = sorted(set(re.findall(r"/events/(\d+)", body)))
            for event_id in ids:
                event_categories.setdefault(event_id, [])
                if category not in event_categories[event_id]:
                    event_categories[event_id].append(category)

    # Fetch one official detail page per event, preserving exact on-air timestamps.
    ids = sorted(event_categories, key=int)[: args.max_events]
    event_jobs = [
        (f"wwo_event_{event_id}", f"https://www.westwoodonesports.com/events/{event_id}/")
        for event_id in ids
    ]
    with ThreadPoolExecutor(max_workers=4) as pool:
        futures = [pool.submit(fetch_and_save, key, url, args.refresh) for key, url in event_jobs]
        for fut in as_completed(futures):
            fut.result()

    # Merge probe manifest URLs for all earlier official snapshots.
    probe_sources = {}
    if PROBE_SUMMARY.exists():
        probe_sources = json.loads(PROBE_SUMMARY.read_text())

    MANIFEST.parent.mkdir(parents=True, exist_ok=True)
    manifest = {
        "generated_utc": utc_now(),
        "source_count": len(_manifest_entries),
        "wwo_event_count": len(ids),
        "wwo_categories": WWO_GRIDS,
        "probe_snapshot": "research/probe/summary.json",
        "probe_source_count": len(probe_sources),
        "files": sorted(_manifest_entries.values(), key=lambda x: x["key"]),
    }
    MANIFEST.write_text(json.dumps(manifest, indent=2, sort_keys=False) + "\n")
    CATEGORY_MAP.write_text(json.dumps({
        "generated_utc": utc_now(),
        "truncated_to_max_events": len(event_categories) > len(ids),
        "events": event_categories,
    }, indent=2, sort_keys=True) + "\n")
    print(json.dumps({
        "static_sources": len(STATIC_SOURCES),
        "nfl_weeks": 18,
        "wwo_grid_pages": len(grid_jobs),
        "wwo_event_pages": len(ids),
        "raw_files": len(list(RAW.glob("*.gz"))),
        "http_errors": [e["key"] for e in _manifest_entries.values() if e.get("error")],
    }, indent=2))


if __name__ == "__main__":
    main()
