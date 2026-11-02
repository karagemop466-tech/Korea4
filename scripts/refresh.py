#!/usr/bin/env python3
"""Create a source-linked snapshot from league, team and network feeds.

No guessed fixture, start time, or local station assignment is invented. A
source failure retains the last successful group's events and reports staleness.
The browser only sees the compact, public data, not source HTML.
"""
from __future__ import annotations

import argparse
import concurrent.futures
import gzip
import html
import json
import re
import sys
import time
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from urllib.error import HTTPError
from urllib.parse import urlencode
from urllib.request import Request, urlopen
from zoneinfo import ZoneInfo

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "site/data/events.json"
ANNOUNCED = ROOT / "site/data/announced-events.json"
INSPECT = ROOT / "site/data/_source-inspection"
PACIFIC = ZoneInfo("America/Los_Angeles")
UTC = timezone.utc
MLB = "https://statsapi.mlb.com/api/v1/schedule"
NFL = "https://www.nfl.com/schedules"
CAL = "https://calbears.com/sports/football/schedule"
STANFORD = "https://gostanford.com/sports/football/schedule"
WWO = "https://www.westwoodonesports.com/ajax/eventCalendar"
NBA = "https://nba-prod-us-east-1-mediaops-stats.s3.amazonaws.com/NBA/staticData/scheduleLeagueV2.json"
GROUPS = ("mlb", "nfl", "cal", "stanford", "westwood", "warriors")


def stamp(dt=None):
    return (dt or datetime.now(UTC)).astimezone(UTC).isoformat(timespec="seconds").replace("+00:00", "Z")


def request(url, attempts=2):
    for attempt in range(attempts):
        try:
            req = Request(url, headers={"User-Agent": "Mozilla/5.0 (compatible; FreeTimeVacation/1.0; schedule research)", "Accept": "application/json,text/html,*/*"})
            with urlopen(req, timeout=35) as res:
                return res.read().decode("utf-8")
        except Exception:
            if attempt + 1 == attempts:
                raise
            time.sleep(1 + attempt)


def season_url(year):
    return MLB + "?" + urlencode({"sportId": 1, "startDate": f"{year}-01-01", "endDate": f"{year}-12-31", "hydrate": "broadcasts(all)"})


def event_source_mlb(pk):
    return MLB + "?" + urlencode({"sportId": 1, "gamePk": pk})


def parse_mlb(payload):
    result = []
    for bucket in payload.get("dates", []):
        for g in bucket.get("games", []):
            if g.get("status", {}).get("detailedState", "").lower() in {"cancelled", "canceled", "postponed"}:
                continue
            # MLB lists S spring, E exhibition, R regular, A all-star and postseason.
            typ = g.get("gameType", "")
            if typ not in {"S", "E", "R", "A", "F", "D", "L", "W", "C"}:
                continue
            teams = g.get("teams", {})
            away = teams.get("away", {}).get("team", {})
            home = teams.get("home", {}).get("team", {})
            if not away.get("name") or not home.get("name"):
                # Do not fill placeholders for TBD competitors.
                title = g.get("description") or g.get("seriesDescription") or "MLB special game · teams TBD"
            else:
                title = f"{away['name']} at {home['name']}"
            priority = bool({away.get("id"), home.get("id")} & {133, 137})
            tbd = bool(g.get("status", {}).get("startTimeTBD", True))
            start = None if tbd else g.get("gameDate")
            day = g.get("officialDate") or bucket.get("date")
            if not day:
                continue
            row = {
                "id": f"mlb-{g['gamePk']}", "group": "mlb", "sport": "MLB", "title": title,
                "date": day, "start": start, "priority": priority,
                "category": {"S": "Spring training", "E": "Exhibition", "R": "Regular season", "A": "All-Star", "F": "Postseason", "D": "Postseason", "L": "Postseason", "W": "World Series", "C": "Postseason"}.get(typ, "MLB"),
                "durationMinutes": 158, "source": event_source_mlb(g["gamePk"]),
                "dateBasis": "Venue-local date; first pitch TBD" if tbd else "Official first pitch",
                "radio": "unverified",
            }
            if tbd:
                # Venue date may differ from Pacific date when no time is known.
                row["possibleOffsetDays"] = [-1, 0, 1]
            result.append(row)
    return result


def parse_nfl(source, season):
    result = []
    # Server-rendered schedule cards expose exact UTC times and game links.
    pattern = re.compile(r'<a\b(?P<attrs>[^>]*\bhref="/games/(?P<slug>[^"/]+)-(?P<season>\d{4})-(?P<phase>pre|reg|post)-(?P<week>\d+)"[^>]*)>', re.I)
    seen = set()
    for m in pattern.finditer(source):
        if int(m.group("season")) != int(season) or "Game Card" not in html.unescape(m.group("attrs")):
            continue
        slug = m.group("slug") + f"-{season}-{m.group('phase')}-{m.group('week')}"
        if slug in seen:
            continue
        seen.add(slug)
        end = source.find("</li>", m.end())
        block = source[m.end():end if end > m.end() else m.end() + 15000]
        labels = re.findall(r'<img\b[^>]*\balt="([^"]+?) Team Logo"', block, re.I)
        labels = list(dict.fromkeys(html.unescape(x) for x in labels))
        if len(labels) < 2:
            continue
        times = re.findall(r'<time\b[^>]*\bdatetime="([^"]+)"', block, re.I)
        start = times[0] if times else None
        try:
            day = datetime.fromisoformat(start.replace("Z", "+00:00")).astimezone(PACIFIC).date().isoformat() if start else None
        except ValueError:
            start, day = None, None
        result.append({
            "id": "nfl-" + slug, "group": "nfl", "sport": "NFL", "title": f"{labels[0]} at {labels[1]}",
            "date": day, "start": start, "priority": any("49ers" in name for name in labels),
            "category": {"pre": "Preseason", "reg": "Regular season", "post": "Postseason"}[m.group("phase").lower()],
            "durationMinutes": 192, "source": "https://www.nfl.com/games/" + slug,
            "dateBasis": "Official kickoff" if start else "Date and kickoff TBD", "radio": "unverified",
        })
    return result


def parse_stanford(source, today):
    result = []
    # The team page's visible time-TBA flag overrides its placeholder datetime.
    blocks = re.split(r'<div class="schedule-event-item"\s', source)
    for block in blocks[1:]:
        date_m = re.search(r'<time\s+datetime="([^"]+)"', block)
        opp_m = re.search(r'class="schedule-event-item-team__opponent-name"[^>]*>([^<]+)', block)
        if not date_m or not opp_m:
            continue
        val = date_m.group(1)
        try:
            dt = datetime.fromisoformat(val)
        except ValueError:
            continue
        day = dt.date().isoformat()
        if day < today:
            continue
        tbd = "schedule-event-date--time-tba" in block[:3000] or bool(re.search(r'schedule-event-date__clock">\s*(?:TBA|TBD)', block[:3500], re.I))
        away = "schedule-event-item__top--away" in block[:300]
        opponent = html.unescape(opp_m.group(1).strip())
        title = f"Stanford at {opponent}" if away else f"{opponent} at Stanford"
        result.append({"id": f"stanford-{day}", "group": "stanford", "sport": "NCAAF", "title": title,
                       "date": day, "start": None if tbd else stamp(dt), "priority": True, "category": "Stanford",
                       "durationMinutes": 210, "source": STANFORD,
                       "dateBasis": "Kickoff TBD or a choice of times" if tbd else "Official kickoff", "radio": "unverified"})
    return result


def parse_cal(source, today):
    result = []
    # The scoreboard explicitly spells out opponent and date. Do not use hidden
    # date objects for TBA games: some contain placeholder start times.
    pat = re.compile(r'<div tabindex="0" aria-label="Game information for California Golden Bears Athletics Football versus ([^"]+?) on ([^"]+)" class="([^"]+)">')
    hits = list(pat.finditer(source))
    for idx, m in enumerate(hits):
        try:
            day = datetime.strptime(html.unescape(m.group(2)), "%B %d, %Y").date().isoformat()
        except ValueError:
            continue
        if day < today:
            continue
        block = source[m.end():hits[idx + 1].start() if idx + 1 < len(hits) else m.end() + 8000]
        tm = re.search(r'<p class="c-scoreboard__time">\s*([^<]+)', block)
        start = None
        if tm and re.fullmatch(r"\d{1,2}(?::\d{2})?\s*[AP]M", tm.group(1).strip(), re.I):
            raw = tm.group(1).strip().upper()
            for fmt in ("%I:%M %p", "%I %p"):
                try:
                    parsed = datetime.strptime(day + " " + raw, "%Y-%m-%d " + fmt).replace(tzinfo=PACIFIC)
                    start = stamp(parsed)
                    break
                except ValueError:
                    pass
        opponent = html.unescape(m.group(1).strip())
        away = "--away" in m.group(3)
        title = f"California at {opponent}" if away else f"{opponent} at California"
        result.append({"id": f"cal-{day}", "group": "cal", "sport": "NCAAF", "title": title,
                       "date": day, "start": start, "priority": True, "category": "California", "durationMinutes": 210,
                       "source": CAL, "dateBasis": "Official kickoff" if start else "Kickoff TBD", "radio": "unverified"})
    return result


def parse_westwood(payload):
    result = []
    for g in payload.get("events", []):
        desc = html.unescape(re.sub(r'<[^>]+>', '', g.get("description", ""))).strip()
        title = html.unescape(g.get("title", "")).strip()
        try:
            date_et = datetime.strptime(g["formatted_date"], "%B %d, %Y").date().isoformat()
        except (ValueError, KeyError):
            continue
        tbd = bool(re.search(r'\b(TBD|TBA)\b', desc, re.I)) or not g.get("start_time")
        start = None if tbd else stamp(datetime.fromtimestamp(int(g["start_time"]), UTC))
        end = None if tbd or not g.get("end_time") else stamp(datetime.fromtimestamp(int(g["end_time"]), UTC))
        if start and end and end <= start:
            end = None
        source = g.get("url", "")
        if not source.startswith("https://www.westwoodonesports.com/events/") or not title:
            continue
        result.append({"id": f"wwo-{g['id']}", "group": "westwood", "sport": "RADIO", "title": title,
                       "date": date_et, "start": start, "end": end, "priority": True, "category": "Westwood One",
                       "source": source, "dateBasis": "Network airtime; scheduled end can change" if start else "Network date in ET; airtime TBD",
                       "possibleOffsetDays": [-1, 0] if not start else [0], "description": desc, "radio": "affiliate-unconfirmed"})
    return result


def parse_warriors(payload):
    result = []
    for bucket in payload.get("leagueSchedule", {}).get("gameDates", []):
        for g in bucket.get("games", []):
            away, home = g.get("awayTeam", {}), g.get("homeTeam", {})
            if 1610612744 not in {home.get("teamId"), away.get("teamId")}:
                continue
            if g.get("postponedStatus") in {"P", "C"}:
                continue
            game_id = g.get("gameId", "")
            # A preseason game is not presumed to be on ordinary radio.
            if not (game_id.startswith("002") or game_id.startswith("004")):
                continue
            raw_start = g.get("gameDateTimeUTC")
            try:
                start_dt = datetime.fromisoformat(raw_start.replace("Z", "+00:00"))
                day = start_dt.astimezone(PACIFIC).date().isoformat()
                start = stamp(start_dt)
            except (AttributeError, ValueError):
                continue
            away_name = " ".join((away.get("teamCity", ""), away.get("teamName", ""))).strip()
            home_name = " ".join((home.get("teamCity", ""), home.get("teamName", ""))).strip()
            if not away_name or not home_name:
                continue
            result.append({"id": "nba-" + game_id, "group": "warriors", "sport": "NBA", "title": f"{away_name} at {home_name}",
                           "date": day, "start": start, "priority": True, "category": "Warriors",
                           "durationMinutes": 150, "source": f"https://www.nba.com/game/{game_id}",
                           "dateBasis": "Official tipoff", "radio": "team-network"})
    return result


def build_snapshot(offline=False, previous=None):
    previous = previous or {}
    old_events = previous.get("events", [])
    old_status = previous.get("sources", {})
    results, states = [], {}
    now = datetime.now(UTC)
    today = now.astimezone(PACIFIC).date().isoformat()

    def preserve(group, exc):
        retained = [e for e in old_events if e.get("group") == group]
        results.extend(retained)
        states[group] = {"ok": False, "checkedAt": stamp(now), "lastSuccess": old_status.get(group, {}).get("lastSuccess"),
                         "count": len(retained), "error": f"{type(exc).__name__}: {str(exc)[:180]}"}

    def success(group, rows, extra=None):
        results.extend(rows)
        states[group] = {"ok": True, "checkedAt": stamp(now), "lastSuccess": stamp(now), "count": len(rows), **(extra or {})}

    # MLB supports a complete calendar-year query. A partial failure is treated
    # as stale rather than silently replacing a previously successful year.
    try:
        if offline:
            payloads = [json.loads(gzip.decompress((INSPECT / "mlb.json.gz").read_bytes()))]
        else:
            with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:
                payloads = list(pool.map(lambda y: json.loads(request(season_url(y))), range(2026, 2030)))
        rows = [e for p in payloads for e in parse_mlb(p)]
        if not rows:
            raise ValueError("MLB returned no events for all requested years")
        success("mlb", rows, {"years": sorted({int(e['date'][:4]) for e in rows})})
    except Exception as exc:
        preserve("mlb", exc)

    try:
        if offline:
            pages = [(2026, gzip.decompress((INSPECT / "nfl.html.gz").read_bytes()).decode())]
        else:
            # Probe first: unsupported future-year URLs may redirect to this year.
            def get_page(pair):
                y, week = pair
                return y, request(f"{NFL}/{y}/by-week/{week}")
            with concurrent.futures.ThreadPoolExecutor(max_workers=6) as pool:
                first = list(pool.map(get_page, [(y, "week-1") for y in range(2026, 2030)]))
            available = [y for y, text in first if parse_nfl(text, y)]
            # Follow the actual official navigation instead of guessing postseason
            # slugs. It also discovers Hall of Fame and playoff rounds when added.
            pairs = []
            for y, text in first:
                if y not in available:
                    continue
                paths = set(re.findall(rf"/schedules/{y}/by-week/([a-z0-9-]+)", text, re.I))
                paths.discard("week-1")
                pairs.extend((y, w) for w in sorted(paths))
            pages = first[:]
            # Failed weeks are reported, not treated as evidence of no games.
            def safe_page(pair):
                try:
                    return get_page(pair), None
                except Exception as exc:
                    return None, f"{pair}: {type(exc).__name__}"
            with concurrent.futures.ThreadPoolExecutor(max_workers=6) as pool:
                fetched = list(pool.map(safe_page, pairs))
            pages += [p for p, err in fetched if p]
            errors = [err for _, err in fetched if err]
            if errors:
                raise ValueError("NFL week fetch incomplete: " + "; ".join(errors[:5]))
        by_id = {}
        for year, page in pages:
            by_id.update({e["id"]: e for e in parse_nfl(page, year)})
        if not by_id:
            raise ValueError("No NFL schedule cards could be parsed")
        success("nfl", list(by_id.values()), {"seasons": sorted({int(x['id'].split('-')[-3]) for x in by_id.values()})})
    except Exception as exc:
        preserve("nfl", exc)

    for group, parse, url, fixture in [("cal", parse_cal, CAL, "cal.html.gz"), ("stanford", parse_stanford, STANFORD, "stanford.html.gz")]:
        try:
            text = gzip.decompress((INSPECT / fixture).read_bytes()).decode() if offline else request(url)
            rows = parse(text, today)
            if not rows:
                raise ValueError("No upcoming team schedule cards parsed")
            success(group, rows)
        except Exception as exc:
            preserve(group, exc)

    if not offline:
        try:
            url = WWO + "?" + urlencode({"id": "all", "range": "current", "offset": 0, "limit": 100, "timezone": "America/New_York", "accountID": 3757, "artistID": 0})
            rows = parse_westwood(json.loads(request(url)))
            # An empty response is allowed but remains an incomplete network schedule.
            success("westwood", rows)
        except Exception as exc:
            preserve("westwood", exc)
        try:
            payload = json.loads(request(NBA))
            rows = parse_warriors(payload)
            if len(rows) < 20:
                raise ValueError("Warriors feed has too few regular-season games")
            success("warriors", rows, {"season": payload.get("leagueSchedule", {}).get("seasonYear")})
        except Exception as exc:
            preserve("warriors", exc)
    else:
        for group in ("westwood", "warriors"):
            preserve(group, ValueError("not included in offline fixture"))

    handbook = json.loads(ANNOUNCED.read_text())
    for row in handbook["events"]:
        row = dict(row, group="announced", start=None, radio="unverified")
        if row["sport"] == "NCAAF":
            row["durationMinutes"] = 210
        elif row["sport"] == "NFL":
            row["durationMinutes"] = 192
        results.append(row)
    results.sort(key=lambda e: (e.get("date") or "9999", e.get("start") or "", e["id"]))
    return {"generatedAt": stamp(now), "sources": states, "announcedReviewedAt": handbook["reviewedAt"],
            "restrictions": handbook["restrictions"], "events": results}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--offline", action="store_true", help="Use saved source inspection fixtures")
    ap.add_argument("--output", type=Path, default=OUT)
    args = ap.parse_args()
    previous = json.loads(args.output.read_text()) if args.output.exists() else {}
    payload = build_snapshot(args.offline, previous)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(payload, separators=(",", ":"), ensure_ascii=False) + "\n")
    print(json.dumps({k: {"ok": v["ok"], "count": v["count"], "error": v.get("error")} for k, v in payload["sources"].items()}, indent=2))
    print("Total:", len(payload["events"]), "events")
    if not payload["events"]:
        sys.exit("Refusing to produce an empty schedule")

if __name__ == "__main__":
    main()
