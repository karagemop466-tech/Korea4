#!/usr/bin/env python3
"""One-time official-source connectivity/shape probe.

This script runs on a GitHub-hosted runner because the Arena sandbox permits
outbound network access only to GitHub/npm/PyPI hosts.  It saves raw official
responses to an artifact for offline inspection.  It does not infer values or
generate public schedule rows.
"""
from __future__ import annotations

import gzip
import hashlib
import json
import re
import ssl
import sys
import urllib.error
import urllib.request
from pathlib import Path
from urllib.parse import urlencode

OUT = Path("probe_out")
OUT.mkdir(parents=True, exist_ok=True)
UA = "Mozilla/5.0 (compatible; Korea4OfficialSourceProbe/1.0; +https://github.com/karagemop466-tech/Korea4)"
CTX = ssl.create_default_context()

MLB_FIELDS = (
    "copyright,totalGames,dates,date,totalGames,games,gamePk,gameDate,officialDate,"
    "gameType,season,teams,away,team,id,name,home,team,id,name,venue,id,name,"
    "status,startTimeTBD,detailedState,seriesDescription,doubleHeader,dayNight,"
    "description,ifNecessary,gameNumber"
)

URLS: dict[str, str] = {
    "mlb_teams_2027": "https://statsapi.mlb.com/api/v1/teams?sportId=1&season=2027",
    "wwo_nfl_schedule": "https://www.westwoodonesports.com/nfl-schedule/",
    "wwo_ncaa_football": "https://www.westwoodonesports.com/ncaa-football/",
    "wwo_ncaa_basketball": "https://www.westwoodonesports.com/ncaa-basketball/",
    "wwo_golf": "https://www.westwoodonesports.com/golf/",
    "wwo_us_soccer": "https://www.westwoodonesports.com/us-soccer/",
    "wwo_mcws": "https://www.westwoodonesports.com/ncaa-mcws/",
    "wwo_wcws": "https://www.westwoodonesports.com/ncaa-wcws/",
    "wwo_lacrosse": "https://www.westwoodonesports.com/ncaa-lacrosse/",
    "wwo_hockey": "https://www.westwoodonesports.com/ncaa-hockey/",
    "wwo_station_finder": "https://www.westwoodonesports.com/station-finder/",
    "wwo_event_sample": "https://www.westwoodonesports.com/events/548540/",
    "wwo_event_grid_ncaaf": "https://www.westwoodonesports.com/more/eventGrid?id=47030&range=current&offset=0&limit=100&timezone=America/New_York&widgetTitle=Upcoming+NCAA+Football+Broadcasts",
    "nfl_2027_by_team": "https://www.nfl.com/schedules/2027/by-team",
    "nfl_2027_prime": "https://www.nfl.com/schedules/2027/prime-time",
    "nfl_2026_by_week": "https://www.nfl.com/schedules/2026/by-week/week-1",
    "nfl_2026_reg1": "https://www.nfl.com/schedules/2026/REG1/",
    "nfl_2026_release": "https://media.nfl.com/football-information/2026/news/2026-nfl-schedule-announced",
    "nfl_important_dates": "https://www.nfl.com/news/2026-27-national-football-league-important-dates",
    "nfl_scorestrip_reg1": "https://static.nfl.com/ajax/scorestrip?season=2026&seasonType=REG&week=1",
    "nfl_scorestrip_pre1": "https://static.nfl.com/ajax/scorestrip?season=2026&seasonType=PRE&week=1",
    "nfl_scorestrip_post1": "https://static.nfl.com/ajax/scorestrip?season=2026&seasonType=POST&week=1",
    "nfl_ss_xml": "https://static.nfl.com/liveupdate/scorestrip/ss.xml",
    "nfl_reg_schedule_htm": "https://static.www.nfl.com/static/content/public/static/html/schedules/2026/regSeasonSchedule.htm",
    "nflers_schedule": "https://www.49ers.com/schedule/",
    "giants_radio": "https://www.mlb.com/giants/schedule/tv",
    "athletics_radio": "https://www.mlb.com/athletics/schedule/affiliates",
    "stanford_schedule_2026": "https://gostanford.com/sports/football/schedule/2026",
    "stanford_schedule_2027": "https://gostanford.com/sports/football/schedule/2027",
    "stanford_radio": "https://gostanford.com/news/2026/07/30/2026-football-radio-broadcast-team-announced",
    "cal_schedule_2026": "https://calbears.com/sports/football/schedule/2026",
    "cal_schedule_2027": "https://calbears.com/sports/football/schedule/2027",
    "mlb_2027_schedule_page": "https://www.mlb.com/schedule/2027-03-25",
    "mlb_2027_spring_release": "https://www.mlb.com/press-release/press-release-mlb-announces-2027-spring-training-schedule",
    "mlb_2027_reg_release": "https://www.mlb.com/tigers/news/mlb-2027-schedule-released",
}

for season in (2026, 2027, 2028, 2029):
    URLS[f"mlb_{season}_all"] = (
        "https://statsapi.mlb.com/api/v1/schedule?"
        + urlencode({"sportId": 1, "season": season, "fields": MLB_FIELDS})
    )


def safe_name(key: str) -> str:
    return re.sub(r"[^a-z0-9_.-]", "_", key)


def fetch(url: str) -> tuple[int | None, dict[str, str], bytes, str | None]:
    req = urllib.request.Request(
        url,
        headers={
            "User-Agent": UA,
            "Accept": "text/html,application/json,application/xml,text/xml,*/*",
            "Accept-Language": "en-US,en;q=0.9",
        },
    )
    try:
        with urllib.request.urlopen(req, timeout=30, context=CTX) as resp:
            data = resp.read()
            headers = {k.lower(): v for k, v in resp.headers.items()}
            if headers.get("content-encoding") == "gzip":
                data = gzip.decompress(data)
            return resp.status, headers, data, None
    except urllib.error.HTTPError as exc:
        try:
            body = exc.read()
        except Exception:
            body = b""
        return exc.code, dict(exc.headers.items()), body, f"HTTPError: {exc.reason}"
    except Exception as exc:  # noqa: BLE001 - probe must continue across hosts
        return None, {}, b"", f"{type(exc).__name__}: {exc}"


def text_excerpt(data: bytes, limit: int = 600) -> str:
    try:
        return data.decode("utf-8", "replace")[:limit]
    except Exception:  # noqa: BLE001
        return repr(data[:limit])


summary: dict[str, dict] = {}
for key, url in URLS.items():
    status, headers, data, error = fetch(url)
    stem = safe_name(key)
    suffix = ".json" if key.startswith("mlb_2") and "statsapi" in url else (
        ".xml" if "scorestrip" in url or url.endswith(".xml") else ".html"
    )
    raw_path = OUT / f"{stem}{suffix}"
    raw_path.write_bytes(data)
    item = {
        "url": url,
        "http_status": status,
        "error": error,
        "content_type": headers.get("content-type"),
        "bytes": len(data),
        "sha256": hashlib.sha256(data).hexdigest(),
        "raw_file": str(raw_path),
        "excerpt": text_excerpt(data),
    }
    if data and key.startswith("mlb_2") and "statsapi" in url:
        try:
            payload = json.loads(data)
            item["totalGames"] = payload.get("totalGames")
            dates = payload.get("dates", [])
            item["date_count"] = len(dates)
            item["first_date"] = dates[0].get("date") if dates else ""
            item["last_date"] = dates[-1].get("date") if dates else ""
            game_types: dict[str, int] = {}
            tbd = 0
            samples = []
            for day in dates:
                for game in day.get("games", []):
                    gt = game.get("gameType", "?")
                    game_types[gt] = game_types.get(gt, 0) + 1
                    if game.get("status", {}).get("startTimeTBD"):
                        tbd += 1
                    if len(samples) < 3:
                        samples.append({
                            "gamePk": game.get("gamePk"),
                            "officialDate": game.get("officialDate"),
                            "gameDate": game.get("gameDate"),
                            "gameType": gt,
                            "away": game.get("teams", {}).get("away", {}).get("team", {}).get("name"),
                            "home": game.get("teams", {}).get("home", {}).get("team", {}).get("name"),
                            "startTimeTBD": game.get("status", {}).get("startTimeTBD"),
                            "description": game.get("description"),
                        })
            item["game_types"] = game_types
            item["start_time_tbd_count"] = tbd
            item["samples"] = samples
        except Exception as exc:  # noqa: BLE001
            item["json_parse_error"] = f"{type(exc).__name__}: {exc}"
    if data and ("westwoodonesports" in url or "nfl.com" in url or "49ers.com" in url or "gostanford.com" in url or "calbears.com" in url):
        text = data.decode("utf-8", "replace")
        item["event_grid_links"] = sorted(set(re.findall(r"https?[^\"'<> ]*eventGrid[^\"'<> ]*|/more/eventGrid[^\"'<> ]*", text)))[:20]
        item["event_links"] = sorted(set(re.findall(r"https://www\.westwoodonesports\.com/events/\d+", text)))[:10]
        item["react_query_markers"] = [m for m in ("__NEXT_DATA__", "__REACT_QUERY_STATE__", "react-query", "gamedetail", "gameDetail", "schedule") if m in text]
        item["sf_mentions"] = [line.strip()[:300] for line in text.splitlines() if re.search(r"San Francisco|KNBR|KTCT|KSFO|KNEW|107\.7", line, re.I)][:30]
    summary[key] = item
    print(f"{key}: status={status} bytes={len(data)} error={error or ''}", flush=True)

(OUT / "summary.json").write_text(json.dumps(summary, indent=2, sort_keys=True), encoding="utf-8")
print(f"Wrote {len(URLS)} probe files and summary.json")
