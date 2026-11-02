#!/usr/bin/env python3
"""Create a source-linked snapshot from league, team and network feeds.

No guessed fixture, start time, or local station assignment is invented. A
source failure retains the last successful group's events and reports staleness.
The browser only sees the compact, public data, not source HTML.
"""
from __future__ import annotations

import argparse
import concurrent.futures
import html
import json
import re
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from html.parser import HTMLParser
from urllib.error import HTTPError
from urllib.parse import urlencode
from urllib.request import Request, urlopen
from zoneinfo import ZoneInfo

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "site/data/events.json"
ANNOUNCED = ROOT / "site/data/announced-events.json"
PACIFIC = ZoneInfo("America/Los_Angeles")
UTC = timezone.utc
MLB = "https://statsapi.mlb.com/api/v1/schedule"
NFL = "https://www.nfl.com/schedules"
CAL = "https://calbears.com/sports/football/schedule"
CAL_TEXT = CAL + "/text"
STANFORD = "https://gostanford.com/sports/football/schedule"
WWO = "https://www.westwoodonesports.com/ajax/eventCalendar"
NBA = "https://nba-prod-us-east-1-mediaops-stats.s3.amazonaws.com/NBA/staticData/scheduleLeagueV2.json"
QUAKES = "https://www.sjearthquakes.com/news/news-earthquakes-announce-radio-stations-for-2026-mls-season"
def quakes_url(year):
    return QUAKES.replace("2026-mls-season", f"{year}-mls-season")
GROUPS = ("mlb", "nfl", "cal", "stanford", "westwood", "warriors", "earthquakes")


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
            status = g.get("status", {}).get("detailedState", "").lower()
            if status in {"cancelled", "canceled"}:
                continue
            postponed = status == "postponed"
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
            tbd = postponed or bool(g.get("status", {}).get("startTimeTBD", True))
            start = None if tbd else g.get("gameDate")
            bucket_day = bucket.get("date") or g.get("officialDate")
            day = None if postponed else bucket_day
            if not bucket_day:
                continue
            row = {
                "id": f"mlb-{g['gamePk']}-{bucket_day}", "group": "mlb", "sport": "MLB", "title": title,
                "date": day, "start": start, "priority": priority,
                "category": {"S": "Spring training", "E": "Exhibition", "R": "Regular season", "A": "All-Star", "F": "Postseason", "D": "Postseason", "L": "Postseason", "W": "World Series", "C": "Postseason"}.get(typ, "MLB"),
                "durationMinutes": 158, "source": event_source_mlb(g["gamePk"]),
                "dateBasis": "Postponed; new date TBD" if postponed else ("Venue-local date; first pitch TBD" if tbd else ("Official resumed game start" if g.get("resumedFrom") else "Official first pitch")),
                "radio": "unverified",
            }
            if tbd and day:
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
        row = {"id": f"stanford-{day}", "group": "stanford", "sport": "NCAAF", "title": title,
               "date": day, "start": None if tbd else stamp(dt), "priority": True, "category": "Stanford",
               "durationMinutes": 210, "source": STANFORD,
               "dateBasis": "Kickoff TBD or a choice of times" if tbd else "Official kickoff", "radio": "unverified"}
        if tbd and away:
            row["possibleOffsetDays"] = [-1, 0, 1]
        result.append(row)
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
                if not "2026-01-01" <= day <= "2029-12-31":
                    continue
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



class TableRows(HTMLParser):
    """Extract text cells without relying on page-specific CSS or third-party libraries."""
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.in_row = self.in_cell = False
        self.rows, self.row, self.cell = [], [], []

    def handle_starttag(self, tag, attrs):
        if tag == "tr":
            self.in_row, self.row = True, []
        elif self.in_row and tag in ("td", "th"):
            self.in_cell, self.cell = True, []

    def handle_data(self, text):
        if self.in_cell:
            self.cell.append(text)

    def handle_endtag(self, tag):
        if self.in_cell and tag in ("td", "th"):
            self.row.append(" ".join(" ".join(self.cell).split()))
            self.in_cell = False
        elif tag == "tr" and self.in_row:
            self.rows.append(self.row)
            self.in_row = False



def parse_cal_text(source):
    heading = re.search(r"(20\d{2}) Football Schedule", source, re.I)
    if not heading:
        raise ValueError("Cal text schedule season not found")
    year = int(heading.group(1))
    if year not in range(2026, 2030):
        return []
    parser = TableRows()
    parser.feed(source)
    rows = []
    for cells in parser.rows:
        if len(cells) < 4 or cells[2].lower() not in {"home", "away", "neutral"}:
            continue
        raw_date = re.sub(r"\s*\([A-Za-z]+\)", "", cells[0]).strip()
        try:
            day = datetime.strptime(f"{raw_date} {year}", "%b %d %Y").date().isoformat()
        except ValueError:
            continue
        start = None
        for fmt in ("%Y-%m-%d %I:%M %p", "%Y-%m-%d %I %p"):
            try:
                start = stamp(datetime.strptime(day + " " + cells[1].upper(), fmt).replace(tzinfo=PACIFIC))
                break
            except ValueError:
                pass
        opp = cells[3]
        title = f"California at {opp}" if cells[2].lower() == "away" else f"{opp} at California"
        rows.append({"id": f"cal-{day}", "group": "cal", "sport": "NCAAF", "title": title,
                     "date": day, "start": start, "priority": True, "category": "California",
                     "durationMinutes": 210, "source": CAL_TEXT,
                     "dateBasis": "Official kickoff" if start else "Kickoff not shown / TBD", "radio": "unverified"})
    return rows


def parse_earthquakes(source, season=2026, url=QUAKES):
    parser = TableRows()
    parser.feed(source)
    rows = []
    for cells in parser.rows:
        if len(cells) < 5 or cells[2].strip().lower() not in {"home", "away"}:
            continue
        # This source explicitly labels the table's kickoff values as PT.
        d = cells[0].replace("Sept.", "Sep").replace(".", "")
        parsed = None
        for fmt in ("%A, %b %d, %Y %I:%M %p", "%A, %B %d, %Y %I:%M %p"):
            try:
                parsed = datetime.strptime(d + " " + cells[3].upper(), fmt).replace(tzinfo=PACIFIC)
                break
            except ValueError:
                pass
        if not parsed or parsed.year != season:
            continue
        opponent, away = cells[1], cells[2].lower() == "away"
        title = f"San Jose Earthquakes at {opponent}" if away else f"{opponent} at San Jose Earthquakes"
        station = {"810 / 1370": "KSFO 810 AM / KZSF 1370 AM", "680 / 1370": "KNBR 680 AM / KZSF 1370 AM"}.get(cells[4])
        rows.append({"id": "mls-quakes-" + parsed.date().isoformat(), "group": "earthquakes", "sport": "MLS",
                     "title": title, "date": parsed.date().isoformat(), "start": stamp(parsed), "priority": True,
                     "category": "Earthquakes", "durationMinutes": 120, "source": url,
                     "dateBasis": "Team's announced kickoff; check for changes", "radio": "announced-station" if station else "unverified",
                     "station": station})
    return rows


def build_snapshot(previous=None):
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
        with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:
            payloads = list(pool.map(lambda y: json.loads(request(season_url(y))), range(2026, 2030)))
        rows = [e for p in payloads for e in parse_mlb(p)]
        if not rows:
            raise ValueError("MLB returned no events for all requested years")
        success("mlb", rows, {"years": sorted({int(e['date'][:4]) for e in rows if e.get('date')})})
    except Exception as exc:
        preserve("mlb", exc)

    try:
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

    for group in ("cal", "stanford"):
        try:
            rows = parse_cal_text(request(CAL_TEXT)) if group == "cal" else parse_stanford(request(STANFORD), "2026-01-01")
            # Team pages roll forward to a new season. Preserve historical rows
            # captured on an earlier refresh, without overwriting current rows.
            ids = {r["id"] for r in rows}
            rows.extend(e for e in old_events if e.get("group") == group and e.get("date") and e["date"] < today and e["id"] not in ids)
            if not rows:
                raise ValueError("No upcoming team schedule cards parsed")
            success(group, rows)
        except Exception as exc:
            preserve(group, exc)

    try:
        rows = []
        # Include past 2026 broadcasts as well as future entries. The past
        # endpoint is reverse chronological, so stop when it reaches 2025.
        for range_name in ("current", "past"):
            previous_page = set()
            for offset in range(0, 3000, 100):
                url = WWO + "?" + urlencode({"id": "all", "range": range_name, "offset": offset, "limit": 100, "timezone": "America/New_York", "accountID": 3757, "artistID": 0})
                payload = json.loads(request(url))
                page = parse_westwood(payload)
                page_ids = {r["id"] for r in page}
                if offset and page_ids and page_ids == previous_page:
                    raise ValueError("Westwood pagination repeated a page")
                previous_page = page_ids
                existing = {r["id"] for r in rows}
                rows.extend(r for r in page if r["id"] not in existing and "2026-01-01" <= r["date"] <= "2029-12-31")
                if len(payload.get("events", [])) < 100 or (range_name == "past" and page and min(r["date"] for r in page) < "2026-01-01"):
                    break
            else:
                raise ValueError("Westwood calendar exceeds the 3,000-event safety limit")
        ids = {r["id"] for r in rows}
        rows.extend(e for e in old_events if e.get("group") == "westwood" and e.get("date") and e["date"] < today and e["id"] not in ids)
        # An empty response is allowed but remains an incomplete network schedule.
        success("westwood", rows)
    except Exception as exc:
        preserve("westwood", exc)
    try:
        rows, seasons = [], []
        for year in range(2026, 2030):
            url = quakes_url(year)
            try:
                season_rows = parse_earthquakes(request(url, attempts=1), year, url)
            except HTTPError as exc:
                if exc.code == 404 and year > 2026:
                    continue
                raise
            if season_rows:
                if len(season_rows) < 20:
                    raise ValueError(f"Earthquakes {year} radio table appears incomplete")
                rows.extend(season_rows)
                seasons.append(year)
        if 2026 not in seasons:
            raise ValueError("Earthquakes 2026 radio table could not be parsed completely")
        success("earthquakes", rows, {"seasons": seasons, "note": "Team announcements are subject to changes; check each match"})
    except Exception as exc:
        preserve("earthquakes", exc)
    try:
        payload = json.loads(request(NBA))
        rows = parse_warriors(payload)
        if len(rows) < 20:
            raise ValueError("Warriors feed has too few regular-season games")
        success("warriors", rows, {"season": payload.get("leagueSchedule", {}).get("seasonYear")})
    except Exception as exc:
        preserve("warriors", exc)

    handbook = json.loads(ANNOUNCED.read_text())
    for row in handbook["events"]:
        replacement = row.get("replaceIfScheduled")
        if replacement and any(e.get("group") == replacement["group"] and (e.get("date") or "").startswith(str(replacement["season"])) and replacement["opponent"].casefold() in e.get("title", "").casefold() for e in results):
            # Prefer the subsequently published team schedule over an older
            # undated or historically announced opponent record.
            continue
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
    ap.add_argument("--output", type=Path, default=OUT)
    args = ap.parse_args()
    previous = json.loads(args.output.read_text()) if args.output.exists() else {}
    payload = build_snapshot(previous)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(payload, separators=(",", ":"), ensure_ascii=False) + "\n")
    print(json.dumps({k: {"ok": v["ok"], "count": v["count"], "error": v.get("error")} for k, v in payload["sources"].items()}, indent=2))
    print("Total:", len(payload["events"]), "events")
    if not payload["events"]:
        sys.exit("Refusing to produce an empty schedule")

if __name__ == "__main__":
    main()
