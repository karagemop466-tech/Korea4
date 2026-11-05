#!/usr/bin/env python3
"""Parse the official NBA/NHL snapshots into per-game rows (Warriors, Sharks).

Input : research/free_runs/raw/*.gz  (written by scripts/fetch_nba_nhl_sources.py)
Output: data/official/other-sports.json

Rules:
  * Only values present in the official response are filled.
  * Start times are converted from the official UTC timestamp to Pacific.
  * Broadcast LENGTH is not published by the leagues; the planning duration used
    to close a radio window is labelled ESTIMATED with its own flag row.
    It is never presented as an official broadcast time.
  * Any season whose official feed returned no games is reported as UNVERIFIED,
    not as "no games played".
"""
from __future__ import annotations

import gzip
import json
from datetime import datetime, timedelta, timezone
from pathlib import Path
from zoneinfo import ZoneInfo

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "research" / "free_runs" / "raw"
MANIFEST = ROOT / "research" / "free_runs" / "manifest.json"
OUT = ROOT / "data" / "official" / "other-sports.json"

PT = ZoneInfo("America/Los_Angeles")

# Planning-only lengths, flagged everywhere they are used.
PLANNING_MINUTES = {
    "NBA": {
        "minutes": 135,
        "status": "ESTIMATED — NOT AN OFFICIAL BROADCAST LENGTH",
        "label": "Planning assumption 2h15m for an NBA game including breaks; the NBA does not publish a broadcast length.",
        "source_url": "https://official.nba.com/rulebook/",
    },
    "NHL": {
        "minutes": 150,
        "status": "ESTIMATED — NOT AN OFFICIAL BROADCAST LENGTH",
        "label": "Planning assumption 2h30m for an NHL game including intermissions; the NHL does not publish a broadcast length.",
        "source_url": "https://www.nhl.com/info/rules",
    },
}

NHL_GAME_TYPE = {1: "Preseason", 2: "Regular Season", 3: "Postseason"}
NBA_WARRIORS_PAGE = "https://www.nba.com/warriors/schedule"


def load_raw(key: str) -> bytes | None:
    path = RAW / f"{key}.gz"
    if not path.exists():
        return None
    return gzip.decompress(path.read_bytes())


def pt_fields(utc_iso: str) -> tuple[str, str, str] | None:
    try:
        clean = utc_iso.replace("Z", "+00:00")
        dt = datetime.fromisoformat(clean).astimezone(PT)
    except (ValueError, TypeError):
        return None
    return dt.date().isoformat(), dt.strftime("%-I:%M %p %Z"), dt.strftime("%H:%M")


def nhl_rows() -> tuple[list[dict], list[dict]]:
    rows, availability = [], []
    for season in ("20262027", "20272028", "20282029", "20292030"):
        key = f"nhl_SJS_{season}"
        body = load_raw(key)
        source = f"https://api-web.nhle.com/v1/club-schedule-season/SJS/{season}"
        if body is None:
            availability.append({
                "league": "NHL", "season": f"{season[:4]}-{season[4:]}", "official_rows": "",
                "status": "NOT CAPTURED — UNVERIFIED", "source_url": source,
                "source_label": "NHL official club schedule API (San Jose Sharks)",
                "verification": "UNVERIFIED",
            })
            continue
        try:
            payload = json.loads(body)
        except json.JSONDecodeError:
            availability.append({
                "league": "NHL", "season": f"{season[:4]}-{season[4:]}", "official_rows": "",
                "status": "RESPONSE NOT JSON — UNVERIFIED", "source_url": source,
                "source_label": "NHL official club schedule API (San Jose Sharks)",
                "verification": "UNVERIFIED",
            })
            continue
        games = payload.get("games") or []
        availability.append({
            "league": "NHL", "season": f"{season[:4]}-{season[4:]}", "official_rows": len(games),
            "status": "OFFICIAL RELEASED SCHEDULE" if games else "NO OFFICIAL GAME ROWS RETURNED",
            "source_url": source,
            "source_label": "NHL official club schedule API (San Jose Sharks)",
            "verification": "VERIFIED" if games else "UNVERIFIED",
        })
        for game in games:
            when = game.get("startTimeUTC") or ""
            parsed = pt_fields(when)
            if not parsed:
                continue
            date_pt, time_pt, clock = parsed
            away = (game.get("awayTeam") or {}).get("abbrev", "")
            home = (game.get("homeTeam") or {}).get("abbrev", "")
            away_name = ((game.get("awayTeam") or {}).get("placeName") or {}).get("default", away)
            home_name = ((game.get("homeTeam") or {}).get("placeName") or {}).get("default", home)
            venue = (game.get("venue") or {}).get("default", "")
            gtype = NHL_GAME_TYPE.get(game.get("gameType"), "")
            start_min = int(clock[:2]) * 60 + int(clock[3:])
            end_min = min(1440, start_min + PLANNING_MINUTES["NHL"]["minutes"])
            rows.append({
                "id": f"nhl-{game.get('id')}",
                "category": "NHL",
                "league": "NHL",
                "team": "San Jose Sharks",
                "season": int(season[:4]),
                "date": date_pt,
                "official_time_pt": time_pt,
                "official_start_utc": when,
                "matchup": f"{away_name} at {home_name}",
                "away": away,
                "home": home,
                "venue": venue,
                "subcategory": gtype,
                "priority": "HIGH — other Bay Area live radio sport (98.5 KFOX / Sharks audio network)",
                "focus": False,
                "radio": "98.5 KFOX (KUFX-FM) per official Sharks broadcast release",
                "radio_source_url": "https://www.nhl.com/sharks/news/san-jose-sharks-announce-2018-19-broadcast-schedule-300119102",
                "duration_min": PLANNING_MINUTES["NHL"]["minutes"],
                "duration_status": PLANNING_MINUTES["NHL"]["status"],
                "planning_note": PLANNING_MINUTES["NHL"]["label"],
                "planning_start_pt": clock,
                "planning_end_pt": f"{end_min // 60:02d}:{end_min % 60:02d}",
                "time_status": f"VERIFIED — official NHL start time ({gtype or 'game type not stated'})",
                "verification": "VERIFIED — official NHL schedule API",
                "source_url": source,
                "source_label": "NHL official club schedule API (San Jose Sharks)",
                "page_url": "https://www.nhl.com/sharks/schedule",
            })
    return rows, availability


def nba_rows() -> tuple[list[dict], list[dict]]:
    rows, availability = [], []
    body = load_raw("nba_league_schedule")
    manifest = json.loads(MANIFEST.read_text()) if MANIFEST.exists() else {}
    feed_url = manifest.get("nba_feed_url") or "https://cdn.nba.com/static/json/staticData/scheduleLeagueV2_1.json"
    if body is None:
        for season in ("2026-27", "2027-28"):
            availability.append({
                "league": "NBA", "season": season, "official_rows": "",
                "status": "OFFICIAL LEAGUE FEED NOT CAPTURED — UNVERIFIED", "source_url": feed_url,
                "source_label": "NBA official static schedule feed (Warriors rows filtered locally)",
                "verification": "UNVERIFIED",
            })
        return rows, availability
    try:
        payload = json.loads(body)
    except json.JSONDecodeError:
        payload = {}
    season_year = ((payload.get("leagueSchedule") or {}).get("seasonYear") or "")
    game_dates = ((payload.get("leagueSchedule") or {}).get("gameDates") or [])
    seen = set()
    for day in game_dates:
        for game in day.get("games") or []:
            home = (game.get("homeTeam") or {}).get("teamTricode", "")
            away = (game.get("awayTeam") or {}).get("teamTricode", "")
            if NBA_TEAM not in (home, away):
                continue
            when = game.get("gameDateTimeUTC") or ""
            parsed = pt_fields(when)
            if not parsed:
                continue
            date_pt, time_pt, clock = parsed
            gid = str(game.get("gameId") or game.get("gameCode") or "")
            if gid in seen:
                continue
            seen.add(gid)
            if date_pt < "2026-08-01":
                continue  # previous season's tail inside the same feed
            start_min = int(clock[:2]) * 60 + int(clock[3:])
            end_min = min(1440, start_min + PLANNING_MINUTES["NBA"]["minutes"])
            home_name = (game.get("homeTeam") or {}).get("teamName", home)
            away_name = (game.get("awayTeam") or {}).get("teamName", away)
            rows.append({
                "id": f"nba-{gid}",
                "category": "NBA",
                "league": "NBA",
                "team": "Golden State Warriors",
                "season": int(season_year.split("-")[0]) if season_year[:4].isdigit() else 2026,
                "date": date_pt,
                "official_time_pt": time_pt,
                "official_start_utc": when,
                "matchup": f"{away_name} at {home_name}" if home == NBA_TEAM else f"{away_name} at {home_name}",
                "away": away,
                "home": home,
                "venue": (game.get("arenaName") or ""),
                "subcategory": "Regular Season",
                "priority": "HIGH — other Bay Area live radio sport (95.7 The Game KGMZ-FM)",
                "focus": False,
                "radio": "95.7 The Game KGMZ-FM per official Warriors radio announcement",
                "radio_source_url": "https://www.nba.com/warriors/news/957-the-game-extension-20190827",
                "duration_min": PLANNING_MINUTES["NBA"]["minutes"],
                "duration_status": PLANNING_MINUTES["NBA"]["status"],
                "planning_note": PLANNING_MINUTES["NBA"]["label"],
                "planning_start_pt": clock,
                "planning_end_pt": f"{end_min // 60:02d}:{end_min % 60:02d}",
                "time_status": "VERIFIED — official NBA start time",
                "verification": "VERIFIED — official NBA league schedule feed",
                "source_url": feed_url,
                "source_label": "NBA official static schedule feed",
                "page_url": NBA_WARRIORS_PAGE,
            })
    availability.append({
        "league": "NBA", "season": season_year or "unknown", "official_rows": len(rows),
        "status": "OFFICIAL RELEASED SCHEDULE (Warriors rows filtered from league feed)" if rows else "NO WARRIORS ROWS RETURNED",
        "source_url": feed_url,
        "source_label": "NBA official static schedule feed",
        "verification": "VERIFIED" if rows else "UNVERIFIED",
    })
    if rows:
        dates = sorted({r["date"] for r in rows})
        availability.append({
            "league": "NBA", "season": season_year or "unknown", "official_rows": len(rows),
            "status": f"Coverage {dates[0]} to {dates[-1]}",
            "source_url": feed_url, "source_label": "NBA official static schedule feed",
            "verification": "VERIFIED",
        })
    return rows, availability


def main() -> None:
    nhl, nhl_avail = nhl_rows()
    nba, nba_avail = nba_rows()
    rows = sorted(nhl + nba, key=lambda r: (r["date"], r["planning_start_pt"]))
    payload = {
        "generated_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "definition": (
            "'Free' means no monitored live radio sport is on air. The Warriors (95.7 The Game) and Sharks "
            "(98.5 KFOX) are live AM/FM sports in San Francisco, so their games must block a 'free' day even "
            "though the original dashboard only carried their station listings."
        ),
        "planning_lengths": PLANNING_MINUTES,
        "counts": {"NHL": len(nhl), "NBA": len(nba), "total": len(rows)},
        "coverage": {
            league: {
                "first": min((r["date"] for r in rows if r["league"] == league), default=""),
                "last": max((r["date"] for r in rows if r["league"] == league), default=""),
            } for league in ("NHL", "NBA")
        },
        "availability": nhl_avail + nba_avail,
        "rows": rows,
    }
    OUT.write_text(json.dumps(payload, indent=1) + "\n", encoding="utf-8")
    print(json.dumps({"out": str(OUT.relative_to(ROOT)), "counts": payload["counts"], "coverage": payload["coverage"]}, indent=2))


if __name__ == "__main__":
    main()
