#!/usr/bin/env python3
"""Fetch official NBA / NHL schedule snapshots for the two Bay Area radio teams.

Why: KNBR/KSFO/95.7 The Game/98.5 KFOX carry more than baseball and football.
The Warriors (98.5/95.7) and Sharks (98.5 KFOX) are live on AM/FM in San
Francisco too, so a "free" day must also contain no Warriors or Sharks game.
The dashboard snapshot never captured their game rows (see flagged IR/F-xx), so
this script captures them from the leagues' own machine-readable feeds.

Nothing is inferred: the raw response is stored byte-for-byte, gzipped, with its
URL, HTTP status, byte count and SHA-256, exactly like `fetch_official.py`.

Run inside GitHub Actions (the sandbox cannot reach these hosts):
    python3 scripts/fetch_nba_nhl_sources.py --refresh
"""
from __future__ import annotations

import argparse
import gzip
import hashlib
import json
import threading
import time
import urllib.error
import urllib.request
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "research" / "free_runs" / "raw"
MANIFEST = ROOT / "research" / "free_runs" / "manifest.json"

UA = (
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/124.0 Safari/537.36 Korea4FreeRunsResearch/1.0"
)

# NHL: one request per club-season returns every game (home and away) with an
# exact UTC start time. Season key format is YYYYYYYY.
NHL_SEASONS = ("20262027", "20272028", "20282029", "20292030")
NHL_TEAMS = {"SJS": "San Jose Sharks", "ANA": "Anaheim Ducks", "LAK": "Los Angeles Kings", "VGK": "Vegas Golden Knights"}
NHL_PRIMARY = "SJS"

# NBA: the league-wide static schedule JSON is the only public machine-readable
# feed. Several historical paths exist; the first that returns usable JSON wins.
NBA_CANDIDATES = (
    "https://cdn.nba.com/static/json/staticData/scheduleLeagueV2_1.json",
    "https://cdn.nba.com/static/json/staticData/scheduleLeagueV2.json",
    "https://cdn.nba.com/static/json/staticData/scheduleLeagueV1_1.json",
)
NBA_SEASONS = ("2026-27", "2027-28")
NBA_TEAM_TRICODE = "GSW"

# Human-facing official schedule pages, stored so every published row can also
# link a page a person can open and read.
PAGES = {
    "nba_warriors_schedule_page": "https://www.nba.com/warriors/schedule",
    "nba_warriors_2026_27_pdf": "https://cdn.nba.com/teams/uploads/sites/1610612744/2026/09/2627Schedule_8.5x11_v2.pdf",
    "nhl_sharks_schedule_page": "https://www.nhl.com/sharks/schedule",
    "nhl_sharks_2026_27_club_page": "https://www.nhl.com/sharks/team/schedule",
}

_lock = threading.Lock()
entries: dict[str, dict] = {}


def now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def fetch(url: str, timeout: int = 40) -> tuple[int | None, bytes, str | None]:
    headers = {
        "User-Agent": UA,
        "Accept": "application/json,text/html,*/*",
        "Accept-Language": "en-US,en;q=0.9",
        "Referer": "https://www.nba.com/",
        "Origin": "https://www.nba.com",
    }
    last = None
    for attempt in range(3):
        try:
            req = urllib.request.Request(url, headers=headers)
            with urllib.request.urlopen(req, timeout=timeout) as resp:
                return resp.status, resp.read(), None
        except urllib.error.HTTPError as exc:
            return exc.code, exc.read(), f"HTTP {exc.code}"
        except Exception as exc:  # DNS/TLS/timeout
            last = f"{type(exc).__name__}: {exc}"
            time.sleep(0.6 * (attempt + 1))
    return None, b"", last


def save(key: str, url: str, data: bytes, status: int | None, error: str | None) -> dict:
    RAW.mkdir(parents=True, exist_ok=True)
    out = RAW / f"{key}.gz"
    out.write_bytes(gzip.compress(data, compresslevel=9, mtime=0))
    entry = {
        "key": key,
        "url": url,
        "http_status": status,
        "error": error,
        "bytes": len(data),
        "sha256": hashlib.sha256(data).hexdigest(),
        "raw_file": f"research/free_runs/raw/{key}.gz",
        "retrieved_utc": now(),
    }
    with _lock:
        entries[key] = entry
    return entry


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--refresh", action="store_true", help="refetch even when a cached response exists")
    args = ap.parse_args()

    if MANIFEST.exists():
        try:
            entries.update({e["key"]: e for e in json.loads(MANIFEST.read_text()).get("files", [])})
        except json.JSONDecodeError:
            pass

    def cached(key: str) -> bool:
        return (RAW / f"{key}.gz").exists() and not args.refresh

    jobs: list[tuple[str, str]] = []
    for season in NHL_SEASONS:
        for tricode in (NHL_PRIMARY,):
            jobs.append((f"nhl_{tricode}_{season}", f"https://api-web.nhle.com/v1/club-schedule-season/{tricode}/{season}"))
    jobs += list(PAGES.items())

    with ThreadPoolExecutor(max_workers=6) as pool:
        futures = {}
        for key, url in jobs:
            if cached(key):
                continue
            futures[pool.submit(fetch, url)] = (key, url)
        for fut in as_completed(futures):
            key, url = futures[fut]
            status, data, error = fut.result()
            save(key, url, data, status, error)

    # NBA: try candidates in order until one returns a large JSON document.
    nba_ok = None
    if not (cached("nba_league_schedule") and json.loads(MANIFEST.read_text() if MANIFEST.exists() else "{}")
            .get("nba_feed_url")):
        for idx, url in enumerate(NBA_CANDIDATES, 1):
            status, data, error = fetch(url)
            key = f"nba_league_schedule_attempt{idx}"
            save(key, url, data, status, error)
            if status == 200 and data.lstrip()[:1] in (b"{",) and len(data) > 200_000:
                (RAW / "nba_league_schedule.gz").write_bytes(gzip.compress(data, compresslevel=9, mtime=0))
                entries["nba_league_schedule"] = dict(entries[key], key="nba_league_schedule",
                                                      raw_file="research/free_runs/raw/nba_league_schedule.gz")
                nba_ok = url
                break

    manifest = {
        "generated_utc": now(),
        "purpose": "Official NBA/NHL schedule snapshots so Warriors and Sharks radio games can block 'free' days.",
        "nba_feed_url": nba_ok or (json.loads(MANIFEST.read_text()).get("nba_feed_url") if MANIFEST.exists() else ""),
        "nba_seasons": list(NBA_SEASONS),
        "nhl_seasons": list(NHL_SEASONS),
        "nhl_primary_team": NHL_PRIMARY,
        "files": sorted(entries.values(), key=lambda e: e["key"]),
    }
    MANIFEST.parent.mkdir(parents=True, exist_ok=True)
    MANIFEST.write_text(json.dumps(manifest, indent=1) + "\n", encoding="utf-8")
    print(json.dumps({
        "manifest": str(MANIFEST.relative_to(ROOT)),
        "files": len(manifest["files"]),
        "nba_feed_url": manifest["nba_feed_url"],
        "errors": [e["key"] for e in manifest["files"] if e.get("error") or not e.get("http_status")],
    }, indent=2))


if __name__ == "__main__":
    main()
