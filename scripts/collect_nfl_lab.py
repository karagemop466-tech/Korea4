#!/usr/bin/env python3
"""Capture official NFL source snapshots for the NFL Strategy Lab.

The sandbox cannot reach nfl.com (or team sites) directly; this script is
executed by GitHub Actions, where the requests succeed. It stores gzipped raw
responses plus a manifest with the exact URL, HTTP status, byte count and
SHA-256 of every captured payload. Nothing is parsed or inferred here: the
downstream parser (`scripts/build_nfl_lab.py`) reads only these raw official
responses.

Official hosts captured:
  * www.nfl.com            — schedules, results, official injury report,
                             team/player statistics, team directory, game center
  * static.www.nfl.com     — official gamebook PDFs (linked from game center)
  * official team websites  — official depth charts (links discovered from the
                             NFL.com team directory, never guessed)

Usage:
    python scripts/collect_nfl_lab.py [--out DIR] [--max-weeks N] [--workers N]
"""
from __future__ import annotations

import argparse
import concurrent.futures
import gzip
import hashlib
import json
import re
import time
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "research" / "official" / "raw" / "nfl_lab"
MANIFEST = ROOT / "research" / "official" / "manifest-nfl-lab.json"

UA = ("Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) "
      "Chrome/124.0.0.0 Safari/537.36 Korea4NflLabResearch/1.0")

NFL_TEAMS_URL = "https://www.nfl.com/teams/"

# NFL.com team-stat pages used as model inputs. Each is an official NFL page.
TEAM_STAT_PAGES = {
    "nfl_team_off_pass": "https://www.nfl.com/stats/team-stats/offense/passing/2026/reg/all",
    "nfl_team_off_rush": "https://www.nfl.com/stats/team-stats/offense/rushing/2026/reg/all",
    "nfl_team_off_recv": "https://www.nfl.com/stats/team-stats/offense/receiving/2026/reg/all",
    "nfl_team_off_score": "https://www.nfl.com/stats/team-stats/offense/scoring/2026/reg/all",
    "nfl_team_def_pass": "https://www.nfl.com/stats/team-stats/defense/passing/2026/reg/all",
    "nfl_team_def_rush": "https://www.nfl.com/stats/team-stats/defense/rushing/2026/reg/all",
    "nfl_team_def_score": "https://www.nfl.com/stats/team-stats/defense/scoring/2026/reg/all",
    "nfl_team_st_score": "https://www.nfl.com/stats/team-stats/special-teams/scoring/2026/reg/all",
}

# NFL.com player-stat pages used as player-prop model inputs.
PLAYER_STAT_PAGES = {
    "nfl_player_pass": "https://www.nfl.com/stats/player-stats/category/passing/2026/reg/all/passingyards/desc",
    "nfl_player_rush": "https://www.nfl.com/stats/player-stats/category/rushing/2026/reg/all/rushingyards/desc",
    "nfl_player_recv": "https://www.nfl.com/stats/player-stats/category/receiving/2026/reg/all/receivingreceptions/desc",
}


def log(msg: str) -> None:
    print(f"[collect-nfl-lab] {msg}", flush=True)


class Store:
    """Raw payload store with a source manifest."""

    def __init__(self, out: Path, manifest: Path) -> None:
        self.out = out
        self.manifest = manifest
        self.out.mkdir(parents=True, exist_ok=True)
        self.entries: list[dict] = []
        if manifest.exists():
            try:
                self.entries = json.loads(manifest.read_text()).get("sources", [])
            except Exception:
                self.entries = []

    def seen(self, key: str) -> bool:
        return any(e.get("key") == key for e in self.entries)

    def put(self, key: str, url: str, status: int, data: bytes, content_type: str = "") -> dict:
        path = self.out / f"{key}.gz"
        payload = gzip.compress(data, 9)
        path.write_bytes(payload)
        entry = {
            "key": key,
            "url": url,
            "http_status": status,
            "bytes": len(data),
            "sha256": hashlib.sha256(data).hexdigest(),
            "gzip_sha256": hashlib.sha256(payload).hexdigest(),
            "content_type": content_type,
            "retrieved_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        }
        self.entries = [e for e in self.entries if e.get("key") != key]
        self.entries.append(entry)
        return entry

    def write_manifest(self) -> None:
        self.entries.sort(key=lambda e: e.get("key", ""))
        out = {
            "generated_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
            "generator": "scripts/collect_nfl_lab.py",
            "note": (
                "Raw official NFL / team-site responses captured by GitHub Actions. "
                "Each entry records the exact URL, HTTP status, byte count and SHA-256 "
                "of the payload. Rows that cannot be confirmed from these responses are "
                "left blank and flagged UNVERIFIED downstream."
            ),
            "source_count": len(self.entries),
            "sources": self.entries,
        }
        self.manifest.write_text(json.dumps(out, indent=1, sort_keys=False) + "\n")


def fetch(url: str, timeout: int = 45, retries: int = 3) -> tuple[int, bytes, str]:
    headers = {
        "User-Agent": UA,
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.9",
        "Cache-Control": "no-cache",
    }
    last_err = ""
    for attempt in range(1, retries + 1):
        try:
            req = urllib.request.Request(url, headers=headers)
            with urllib.request.urlopen(req, timeout=timeout) as resp:
                data = resp.read()
                return resp.status, data, resp.headers.get("Content-Type", "")
        except urllib.error.HTTPError as exc:
            if exc.code in (404, 403, 410):
                return exc.code, b"", "error"
            last_err = f"HTTP {exc.code}"
        except Exception as exc:  # network/DNS/TLS
            last_err = f"{type(exc).__name__}: {exc}"
        time.sleep(1.5 * attempt)
    log(f"  ! failed {url} ({last_err})")
    return 0, b"", "error"


def capture(store: Store, key: str, url: str, force: bool = False) -> dict | None:
    if not force and store.seen(key):
        return None
    status, data, ctype = fetch(url)
    if status == 200 and data:
        entry = store.put(key, url, status, data, ctype)
        log(f"  ok {key} <- {url} ({len(data)} bytes)")
        return entry
    store.put(key, url, status, b"", ctype)
    log(f"  -- {key} status={status} <- {url}")
    return None


def game_hrefs(html: str) -> list[str]:
    hrefs = set(re.findall(r'href="(/games/[^"?#]+)"', html))
    return sorted(hrefs)


def team_directory(html: str) -> list[dict]:
    """Official team websites linked from the NFL.com team directory."""
    rows: dict[str, dict] = {}
    for m in re.finditer(r'href="(https?://(?!www\.nfl\.com|static\.www\.nfl\.com|media\.nfl\.com)[^"]+)"[^>]*>([^<]{0,80})<', html):
        url, text = m.group(1), m.group(2).strip()
        if not url.startswith("https://www."):
            continue
        if any(t in url for t in ("ticketmaster", "marriott", "hilton", "nfl.com/shop", "shop.", "yelp", "facebook", "twitter", "x.com", "instagram", "youtube", "linkedin", "google", "apple", "spotify", "amazon")):
            continue
        host = url.split("/")[2].lower()
        if host in rows:
            continue
        rows[host] = {"url": url, "label": text}
    return sorted(rows.values(), key=lambda r: r["url"])


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--max-weeks", type=int, default=12)
    ap.add_argument("--workers", type=int, default=8)
    ap.add_argument("--force", action="store_true")
    args = ap.parse_args()

    store = Store(RAW, MANIFEST)
    log(f"raw dir: {RAW}")

    # 1. NFL.com by-week schedules (schedule + official final results).
    log("by-week schedules")
    week_urls = {
        f"nfl_lab_week_{w:02d}": f"https://www.nfl.com/schedules/2026/by-week/week-{w}"
        for w in range(1, args.max_weeks + 1)
    }
    for key, url in week_urls.items():
        capture(store, key, url, args.force)

    # 2. NFL.com official weekly injury report.
    log("official injury report")
    for w in range(1, args.max_weeks + 1):
        capture(store, f"nfl_lab_injuries_reg{w:02d}", f"https://www.nfl.com/injuries/league/2026/reg{w}", args.force)

    # 3. NFL.com team and player statistics.
    log("team / player statistics")
    for key, url in {**TEAM_STAT_PAGES, **PLAYER_STAT_PAGES}.items():
        capture(store, key, url, args.force)

    # 4. NFL.com team directory (source of official team websites).
    log("team directory")
    capture(store, "nfl_lab_teams", NFL_TEAMS_URL, args.force)

    # 5. NFL.com game center pages for every game discovered in the schedules.
    log("game center pages")
    slugs: list[str] = []
    for w in range(1, args.max_weeks + 1):
        path = RAW / f"nfl_lab_week_{w:02d}.gz"
        if not path.exists():
            continue
        html = gzip.decompress(path.read_bytes()).decode("utf-8", "replace")
        for slug in game_hrefs(html):
            if slug not in slugs:
                slugs.append(slug)
    log(f"  {len(slugs)} game pages discovered")
    with concurrent.futures.ThreadPoolExecutor(max_workers=args.workers) as pool:
        futures = {
            pool.submit(capture, store, f"nfl_lab_game_{slug.strip('/games/').replace('/', '_')}", f"https://www.nfl.com{slug}", args.force): slug
            for slug in slugs
        }
        for fut in concurrent.futures.as_completed(futures):
            fut.result()

    # 6. Official gamebook PDFs linked from the game-center pages.
    log("official gamebook PDFs")
    pdf_jobs: dict[str, str] = {}
    for path in sorted(RAW.glob("nfl_lab_game_*.gz")):
        html = gzip.decompress(path.read_bytes()).decode("utf-8", "replace")
        for pdf in set(re.findall(r'https://static\.www\.nfl\.com/[^"\']*gamecenter/[^"\']+\.pdf', html)):
            pdf_jobs[pdf] = pdf
    log(f"  {len(pdf_jobs)} gamebooks linked")
    with concurrent.futures.ThreadPoolExecutor(max_workers=args.workers) as pool:
        futures = {
            pool.submit(capture, store, f"nfl_lab_gamebook_{i:03d}", url, args.force): url
            for i, url in enumerate(sorted(pdf_jobs))
        }
        for fut in concurrent.futures.as_completed(futures):
            fut.result()

    # 7. Official team depth charts (links discovered from the NFL.com team
    #    directory; the common /team/depth-chart path is tried first and the
    #    team homepage is searched for a "depth" link when that path is absent).
    log("official depth charts")
    teams_path = RAW / "nfl_lab_teams.gz"
    if teams_path.exists():
        html = gzip.decompress(teams_path.read_bytes()).decode("utf-8", "replace")
        sites = team_directory(html)
        log(f"  {len(sites)} official team sites discovered")

        def depth_for(site: dict) -> tuple[str, str]:
            base = site["url"].rstrip("/")
            key = re.sub(r"[^a-z0-9]+", "_", base.split("//", 1)[1].split("/")[0].lower()).strip("_")
            candidates = [f"{base}/team/depth-chart", f"{base}/team/depth-charts", f"{base}/depth-chart"]
            for cand in candidates:
                status, data, _ = fetch(cand, retries=1)
                if status == 200 and data:
                    return f"nfl_lab_depth_{key}", cand, data
            status, data, _ = fetch(base, retries=1)
            if status == 200 and data:
                text = data.decode("utf-8", "replace")
                links = set(re.findall(r'href="([^"]*depth[^"]*)"', text, re.I))
                for link in sorted(links):
                    if link.startswith("/"):
                        link = base + link
                    elif not link.startswith("http"):
                        continue
                    st, d, _ = fetch(link, retries=1)
                    if st == 200 and d:
                        return f"nfl_lab_depth_{key}", link, d
            return f"nfl_lab_depth_{key}", base, b""

        with concurrent.futures.ThreadPoolExecutor(max_workers=args.workers) as pool:
            futures = [pool.submit(depth_for, site) for site in sites]
            for fut in concurrent.futures.as_completed(futures):
                key, url, data = fut.result()
                if data:
                    store.put(key, url, 200, data, "text/html")
                    log(f"  ok {key} <- {url} ({len(data)} bytes)")
                else:
                    store.put(key, url, 404, b"", "error")
                    log(f"  -- {key} no official depth chart <- {url}")

    store.write_manifest()
    log(f"manifest written: {MANIFEST} ({len(store.entries)} sources)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
