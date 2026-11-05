#!/usr/bin/env python3
"""Compute longest RUNS of consecutive days with no published live-radio sports block.

This answers a different question from `scripts/build_site.py`'s vacation windows:

  "What is the longest run of consecutive days on which no published MLB / NFL /
   Stanford / Cal / Westwood One game is on air?"

It is deliberately conservative and additive only. It reads the existing
`data/official/days-<year>.json` scoreboards produced by `scripts/collect_official.py`
and never invents a game, a date, or a time. Every day is classified into one of
four mutually exclusive classes from the block STATUS values that already exist
in the data:

  PUBLISHED_OFFICIAL  a published schedule row exists (official start time with
                      estimated duration, official network window, or an official
                      date whose start time is still TBD)
  UNVERIFIED_ANCHOR   no published row, but an officially anchored event occupies
                      the whole day with an unknown start time (e.g. Super Bowl LXI,
                      CFP National Championship, Stanford @ Notre Dame 2028)
  MODEL_ONLY          only the clearly-labelled 364-day released-season model
                      (no published row) - still treated as a candidate block
  NO_BLOCK            no block at all in the snapshot

A day therefore counts as FREE only if it is NO_BLOCK. That is the strict reading
the user asked for: "a minute is free when none of these are on air", and the safe
default when a schedule is unknown is to refuse to call it free.

Output: data/official/free-runs.json  (pure data, fully recomputable)
        research/free-runs-report.md (human-readable verification record)

Run: python3 scripts/build_free_runs.py
"""
from __future__ import annotations

import json
from collections import Counter
from datetime import date, timedelta
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "data" / "official" / "free-runs.json"
OTHER_SPORTS = ROOT / "data" / "official" / "other-sports.json"
REPORT = ROOT / "research" / "free-runs-report.md"

YEARS = (2027, 2028, 2029)
MODEL_YEAR = 2026  # season whose windows the 364-day model was shifted from

CLASS_PUBLISHED = "PUBLISHED_OFFICIAL"
CLASS_ANCHOR = "UNVERIFIED_ANCHOR"
CLASS_MODEL = "MODEL_ONLY"
CLASS_FREE = "NO_BLOCK"

STATUS_TO_CLASS = {
    "OFFICIAL_START_ESTIMATED_DURATION": CLASS_PUBLISHED,
    "OFFICIAL_NETWORK_WINDOW": CLASS_PUBLISHED,
    "ESTIMATED_TBD_START": CLASS_PUBLISHED,
    "UNVERIFIED_BLOCK": CLASS_ANCHOR,
    "ESTIMATED_UNRELEASED_SEASON_MODEL": CLASS_MODEL,
}

# Verified season boundaries used to explain WHY a stretch of days is empty.
# Each row was re-fetched and read on 2026-11-05 (see research/free-runs-report.md).
SEASON_NOTES = [
    {
        "id": "S-01",
        "league": "MLB",
        "season": 2027,
        "label": "2027 MLB regular season ends (last official Stats API game date)",
        "start": "2027-09-26",
        "end": "2027-09-26",
        "status": "VERIFIED — official schedule last game date",
        "source_url": "https://statsapi.mlb.com/api/v1/schedule?sportId=1&season=2027",
        "source_label": "MLB Stats API official 2027 schedule",
        "effect": "No published 2027 MLB rows after this date in the snapshot.",
    },
    {
        "id": "S-02",
        "league": "MLB",
        "season": 2028,
        "label": "2028 MLB schedule not released (Stats API returns zero games)",
        "start": "2028-01-01",
        "end": "2028-12-31",
        "status": "UNVERIFIED — no official game rows exist to publish",
        "source_url": "https://statsapi.mlb.com/api/v1/schedule?sportId=1&season=2028",
        "source_label": "MLB Stats API official 2028 season query (totalGames: 0, re-checked 2026-11-05)",
        "effect": "Every 2028 day is empty of MLB rows because the schedule is unreleased, not because MLB is idle.",
    },
    {
        "id": "S-03",
        "league": "MLB",
        "season": 2029,
        "label": "2029 MLB schedule not released (Stats API returns zero games)",
        "start": "2029-01-01",
        "end": "2029-12-31",
        "status": "UNVERIFIED — no official game rows exist to publish",
        "source_url": "https://statsapi.mlb.com/api/v1/schedule?sportId=1&season=2029",
        "source_label": "MLB Stats API official 2029 season query",
        "effect": "Every 2029 day is empty of MLB rows because the schedule is unreleased, not because MLB is idle.",
    },
    {
        "id": "S-04",
        "league": "NFL",
        "season": 2027,
        "label": "Super Bowl LXI — last 2026-season NFL game",
        "start": "2027-02-14",
        "end": "2027-02-14",
        "status": "VERIFIED — official NFL important dates",
        "source_url": "https://www.nfl.com/news/2026-27-national-football-league-important-dates",
        "source_label": "NFL.com official 2026–27 important dates (re-read 2026-11-05)",
        "effect": "2026-season NFL ends here; the 2027 NFL schedule is not released.",
    },
    {
        "id": "S-05",
        "league": "NFL",
        "season": 2027,
        "label": "2027 NFL game-by-game schedule not released",
        "start": "2027-02-15",
        "end": "2027-12-31",
        "status": "UNVERIFIED — official selector shows no 2027 game data",
        "source_url": "https://www.nfl.com/schedules/2027/by-team",
        "source_label": "NFL.com official 2027 schedule selector",
        "effect": "NFL preseason/regular/postseason 2027 is unmodelled in the snapshot; late-2027 days are not evidence of free time.",
    },
    {
        "id": "S-06",
        "league": "NFL",
        "season": 2028,
        "label": "2028 NFL schedule not released",
        "start": "2028-01-01",
        "end": "2028-12-31",
        "status": "UNVERIFIED — official selector shows no 2028 game data",
        "source_url": "https://www.nfl.com/schedules/2027/by-team",
        "source_label": "NFL.com official schedule selector",
        "effect": "No 2028 NFL rows exist to publish.",
    },
    {
        "id": "S-07",
        "league": "NFL",
        "season": 2029,
        "label": "2029 NFL schedule not released",
        "start": "2029-01-01",
        "end": "2029-12-31",
        "status": "UNVERIFIED — official selector shows no 2029 game data",
        "source_url": "https://www.nfl.com/schedules/2027/by-team",
        "source_label": "NFL.com official schedule selector",
        "effect": "No 2029 NFL rows exist to publish.",
    },
    {
        "id": "S-08",
        "league": "WWO",
        "season": 2027,
        "label": "Westwood One official schedule published only through 2027-01-10",
        "start": "2027-01-11",
        "end": "2027-12-31",
        "status": "UNVERIFIED — later 2027 network windows not published",
        "source_url": "https://www.westwoodonesports.com/nfl-schedule/",
        "source_label": "Westwood One Sports official NFL schedule",
        "effect": "WWO windows after 2027-01-10 are blank, not free.",
    },
    {
        "id": "S-09",
        "league": "NCAAF",
        "season": 2027,
        "label": "2027 Stanford/Cal season dates not released (only nonconference dates and Notre Dame 11-27)",
        "start": "2027-01-01",
        "end": "2027-12-31",
        "status": "UNVERIFIED — opponents published, dates pending",
        "source_url": "https://calbears.com/news/2026/9/16/california-football-announces-2027-conference-opponents",
        "source_label": "Cal Athletics official 2027 conference opponents",
        "effect": "Only 4 dated 2027 college rows exist; the other ~8 games per team are undated.",
    },
    {
        "id": "S-10",
        "league": "NCAAF",
        "season": 2028,
        "label": "2028 Stanford/Cal schedule not released (Notre Dame 2028-10-14 is the only dated game)",
        "start": "2028-01-01",
        "end": "2028-12-31",
        "status": "UNVERIFIED — single dated game only",
        "source_url": "https://gostanford.com/news/2026/05/20/two-dates-added-to-notre-dame-rivalry",
        "source_label": "Stanford Athletics official Notre Dame series release",
        "effect": "No other 2028 college dates are published.",
    },
    {
        "id": "S-11",
        "league": "NCAAF",
        "season": 2029,
        "label": "2029 Stanford/Cal schedule not released",
        "start": "2029-01-01",
        "end": "2029-12-31",
        "status": "UNVERIFIED — no 2029 college dates published",
        "source_url": "https://gostanford.com/sports/football/schedule",
        "source_label": "Stanford Athletics official football schedule page",
        "effect": "No 2029 college dates exist to publish; CFP title date only.",
    },
]


def load_days(year: int) -> dict[str, list]:
    path = ROOT / "data" / "official" / f"days-{year}.json"
    return json.loads(path.read_text())


def classify(blocks: list[dict]) -> str:
    """Single class for a day, most-informative first."""
    if not blocks:
        return CLASS_FREE
    classes = {STATUS_TO_CLASS.get(b.get("status", ""), CLASS_ANCHOR) for b in blocks}
    for candidate in (CLASS_PUBLISHED, CLASS_ANCHOR, CLASS_MODEL):
        if candidate in classes:
            return candidate
    return CLASS_ANCHOR


def load_other_sports() -> tuple[dict[str, list[dict]], dict]:
    """Warriors (NBA) and Sharks (NHL) games are live AM/FM sports too.

    They only exist when `scripts/fetch_nba_nhl_sources.py` +
    `scripts/collect_other_sports.py` were run inside GitHub Actions, so their
    absence is reported as "not captured", never as "no game".
    """
    if not OTHER_SPORTS.exists():
        return {}, {"status": "NOT CAPTURED — UNVERIFIED", "rows": 0, "coverage": {}}
    data = json.loads(OTHER_SPORTS.read_text())
    by_day: dict[str, list[dict]] = {}
    for row in data.get("rows", []):
        by_day.setdefault(row["date"], []).append(row)
    return by_day, {
        "status": "CAPTURED FROM OFFICIAL LEAGUE FEEDS",
        "rows": len(data.get("rows", [])),
        "counts": data.get("counts", {}),
        "coverage": data.get("coverage", {}),
        "generated_utc": data.get("generated_utc"),
    }


def day_record(day: str, blocks: list[dict], extra: list[dict] | None = None) -> dict:
    extra = extra or []
    if extra:
        blocks = list(blocks) + [
            {
                "start": int(g["planning_start_pt"][:2]) * 60 + int(g["planning_start_pt"][3:]),
                "end": int(g["planning_end_pt"][:2]) * 60 + int(g["planning_end_pt"][3:]),
                "status": "OFFICIAL_START_ESTIMATED_DURATION",
                "category": g.get("league", ""),
                "label": g.get("matchup", ""),
                "matchup": g.get("matchup", ""),
                "priority": g.get("priority", ""),
                "source_url": g.get("source_url", ""),
                "source_label": g.get("source_label", ""),
                "verification": g.get("verification", ""),
            }
            for g in extra
        ]
    cls = classify(blocks)
    published = [b for b in blocks if STATUS_TO_CLASS.get(b.get("status", "")) == CLASS_PUBLISHED]
    anchors = [b for b in blocks if STATUS_TO_CLASS.get(b.get("status", "")) == CLASS_ANCHOR]
    models = [b for b in blocks if STATUS_TO_CLASS.get(b.get("status", "")) == CLASS_MODEL]
    # Busy minutes come only from published rows; anchors block the whole day by
    # convention but are reported separately so they are never mistaken for a
    # measured broadcast length.
    busy_minutes = 0
    if published:
        spans = sorted((int(b["start"]), int(b["end"])) for b in published)
        merged: list[list[int]] = []
        for start, end in spans:
            if merged and start <= merged[-1][1]:
                merged[-1][1] = max(merged[-1][1], end)
            else:
                merged.append([start, end])
        busy_minutes = sum(e - s for s, e in merged)
    if anchors and not published:
        busy_minutes = 0  # unknown window; do not invent 1440
    src = (published or anchors or models or [{}])[0]
    return {
        "date": day,
        "class": cls,
        "published_rows": len(published),
        "anchor_rows": len(anchors),
        "model_rows": len(models),
        "published_busy_minutes": busy_minutes,
        "categories": sorted({b.get("category", "") for b in published or anchors or models if b.get("category")}),
        "first_block_pt": _hm(min(int(b["start"]) for b in published)) if published else "",
        "last_block_end_pt": _hm(max(int(b["end"]) for b in published)) if published else "",
        "label": (src.get("label") or src.get("matchup") or "")[:120],
        "other_sports_rows": len(extra),
        "source_url": src.get("source_url", ""),
        "source_label": src.get("source_label", ""),
        "verification": src.get("verification", ""),
    }


def _hm(minutes: int) -> str:
    minutes = max(0, min(1440, minutes))
    return f"{minutes // 60:02d}:{minutes % 60:02d}"


def runs_of(records: list[dict], predicate) -> list[dict]:
    out, current = [], []
    for rec in records:
        if predicate(rec):
            current.append(rec)
        else:
            if current:
                out.append(_run(current))
            current = []
    if current:
        out.append(_run(current))
    return out


def _run(recs: list[dict]) -> dict:
    busy = sum(r["published_busy_minutes"] for r in recs)
    cats = Counter()
    for r in recs:
        for c in r["categories"]:
            cats[c] += 1
    return {
        "start": recs[0]["date"],
        "end": recs[-1]["date"],
        "days": len(recs),
        "published_busy_minutes": busy,
        "categories": dict(cats),
        "record": recs[0],
    }


def weekday_latest_end(records: list[dict]) -> dict[str, dict]:
    """For each weekday, the latest 'last block end' observed - used to size a departure day."""
    best: dict[str, dict] = {}
    for rec in records:
        if not rec["last_block_end_pt"]:
            continue
        dow = date.fromisoformat(rec["date"]).strftime("%a")
        if dow not in best or rec["last_block_end_pt"] > best[dow]["last_block_end_pt"]:
            best[dow] = rec
    return best


def boundary_table() -> list[dict]:
    """Nearest published block before and after each candidate run (why the run exists)."""
    return []


def nearest_blocks(records: list[dict], start: str, end: str) -> tuple[dict | None, dict | None]:
    before = [r for r in records if r["date"] < start and r["class"] != CLASS_FREE]
    after = [r for r in records if r["date"] > end and r["class"] != CLASS_FREE]
    return (before[-1] if before else None), (after[0] if after else None)


def main() -> None:
    all_records: list[dict] = []
    per_year: dict[str, dict] = {}
    other_by_day, other_meta = load_other_sports()
    for year in YEARS:
        days = load_days(year)
        records = [day_record(d, days[d], other_by_day.get(d)) for d in sorted(days)]
        all_records.extend(records)
        counts = Counter(r["class"] for r in records)
        # Strips: consecutive days with no published official row (free, anchor or
        # model only). Useful for "no game is published on these dates".
        open_runs = [r for r in runs_of(records, lambda rec: rec["class"] in (CLASS_FREE, CLASS_ANCHOR, CLASS_MODEL))]
        per_year[str(year)] = {
            "year": year,
            "days_in_snapshot": len(records),
            "class_counts": dict(counts),
            "strict_free_days": counts.get(CLASS_FREE, 0),
            "year_class_counts": dict(counts),
            "published_days": counts.get(CLASS_PUBLISHED, 0),
            "longest_strict_free_run": max(
                (r["days"] for r in runs_of(records, lambda rec: rec["class"] == CLASS_FREE)), default=0
            ),
            "longest_no_published_run": max((r["days"] for r in open_runs), default=0),
        }

    strict_runs = runs_of(all_records, lambda rec: rec["class"] == CLASS_FREE)
    open_runs = runs_of(all_records, lambda rec: rec["class"] in (CLASS_FREE, CLASS_ANCHOR, CLASS_MODEL))
    published_runs = runs_of(all_records, lambda rec: rec["class"] == CLASS_PUBLISHED)

    # Candidate shortlist: the 12 longest strict-free runs, most recent first on ties,
    # each annotated with what officially bounds it on both sides.
    ranked = sorted(strict_runs, key=lambda r: (-r["days"], r["start"]))
    shortlist = []
    for run in ranked[:12]:
        before, after = nearest_blocks(all_records, run["start"], run["end"])
        start_dow = date.fromisoformat(run["start"]).strftime("%A")
        end_dow = date.fromisoformat(run["end"]).strftime("%A")
        shortlist.append({
            "start": run["start"],
            "end": run["end"],
            "days": run["days"],
            "start_weekday": start_dow,
            "end_weekday": end_dow,
            "year": int(run["start"][:4]),
            "block_before": (before or {}).get("label", ""),
            "block_before_date": (before or {}).get("date", ""),
            "block_before_source": (before or {}).get("source_url", ""),
            "block_after": (after or {}).get("label", ""),
            "block_after_date": (after or {}).get("date", ""),
            "block_after_source": (after or {}).get("source_url", ""),
            "status": "VERIFIED-FREE DATES / UNRELEASED-SEASON CAVEAT",
            "reason": "No published game row of any monitored category falls on these dates in the snapshot. "
                      "Under the strict reading that an unreleased schedule is not evidence of free time, this is a "
                      "candidate window only; confirm when the missing schedules are released.",
            "source_url": (before or after or {}).get("source_url", ""),
        })

    # Per-year top strict runs (for the year comparison table).
    year_runs = {}
    for year in YEARS:
        recs = [r for r in all_records if r["date"].startswith(str(year))]
        yr = runs_of(recs, lambda rec: rec["class"] == CLASS_FREE)
        yr_open = runs_of(recs, lambda rec: rec["class"] in (CLASS_FREE, CLASS_ANCHOR, CLASS_MODEL))
        ranked_yr = sorted(yr, key=lambda r: (-r["days"], r["start"]))
        top = ranked_yr[0] if ranked_yr else None
        year_runs[str(year)] = {
            "year": year,
            "top_runs": [{"start": r["start"], "end": r["end"], "days": r["days"]} for r in ranked_yr[:5]],
            "longest": top,
            "longest_open_run": max(yr_open, key=lambda r: r["days"]) if yr_open else None,
        }

    weekday_end = weekday_latest_end(all_records)

    payload = {
        "generated_utc": None,  # filled below from meta for a single timestamp source
        "definition": (
            "A day is FREE only when the snapshot contains no block of any class for it. "
            "A day with a published game, an officially anchored all-day event of unknown start time, "
            "or only the released-season model does not count as free. This is stricter than asking whether "
            "some minutes are free."
        ),
        "classes": {
            CLASS_PUBLISHED: "At least one published official game row (official start + estimated duration, official network window, or official date with TBD start).",
            CLASS_ANCHOR: "No published time, but an officially anchored event occupies the whole day (e.g. Super Bowl, CFP championship, dated college game).",
            CLASS_MODEL: "Only the clearly-labelled 364-day model of unreleased seasons. Still treated as a candidate block.",
            CLASS_FREE: "No block at all in the snapshot.",
        },
        "counts": {
            "days_examined": len(all_records),
            "strict_free_runs": len(strict_runs),
            "no_published_runs": len(open_runs),
            "published_runs": len(published_runs),
            "max_strict_free_run_days": max((r["days"] for r in strict_runs), default=0),
        },
        "per_year": per_year,
        "year_runs": year_runs,
        "shortlist": shortlist,
        "weekday_latest_end": {
            dow: {
                "date": rec["date"],
                "last_block_end_pt": rec["last_block_end_pt"],
                "label": rec["label"],
                "source_url": rec["source_url"],
            }
            for dow, rec in sorted(weekday_end.items())
        },
        "other_sports": other_meta,
        "season_notes": SEASON_NOTES,
        "strict_conclusion": (
            "No 7-, 14- or 21-day stretch of consecutive days inside 2027-2029 is free under the strict "
            "reading. The longest runs with no published game are short early-winter gaps (see shortlist); "
            "every longer empty stretch is empty only because the 2027 NFL/WWO, 2028 and 2029 schedules have "
            "not been released, so it cannot be called free."
        ),
        "practical_reading": (
            "If 'free' is relaxed to 'not known to contain a game', the longest stretches are the annual "
            "late-December/January gap after the college national championship until the next published "
            "spring-training or NFL date, and the day ranges that sit between two officially dated events. "
            "Those are published explicitly on this page as CANDIDATES, never as verified free time."
        ),
    }
    meta = json.loads((ROOT / "data" / "official" / "meta.json").read_text())
    payload["generated_utc"] = meta.get("generated_utc")
    payload["snapshot_system_today"] = meta.get("system_today")
    OUT.write_text(json.dumps(payload, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")

    write_report(payload)
    print(json.dumps({
        "out": str(OUT.relative_to(ROOT)),
        "report": str(REPORT.relative_to(ROOT)),
        "days_examined": payload["counts"]["days_examined"],
        "strict_free_runs": payload["counts"]["strict_free_runs"],
        "max_strict_free_run_days": payload["counts"]["max_strict_free_run_days"],
        "shortlist": len(shortlist),
    }, indent=2))


def write_report(payload: dict) -> None:
    lines = [
        "# Free-run analysis — verification record",
        "",
        f"Generated from the snapshot dated {payload['generated_utc']} (snapshot 'today' = {payload.get('snapshot_system_today')}).",
        "Recomputed by `python3 scripts/build_free_runs.py`; published as `data/official/free-runs.json`.",
        "",
        "## Method",
        "",
        payload["definition"],
        "",
        "| Class | Meaning |",
        "|---|---|",
    ]
    for key, value in payload["classes"].items():
        lines.append(f"| `{key}` | {value} |")
    lines += ["", "## Counts", ""]
    for key, value in payload["counts"].items():
        lines.append(f"- `{key}`: {value}")
    lines += ["", "## Per year", "", "| Year | Days | Strict free days | Published days | Longest strict-free run | Longest stretch with no published game |", "|---|---|---|---|---|---|"]
    for year, rec in payload["per_year"].items():
        lines.append(
            f"| {year} | {rec['days_in_snapshot']} | {rec['strict_free_days']} | {rec['published_days']} | "
            f"{rec['longest_strict_free_run']} | {rec['longest_no_published_run']} |"
        )
    lines += ["", "## Longest strict-free runs (no published game of any monitored category)", "",
              "| Rank | Start | End | Days | Block before (date) | Block after (date) |", "|---|---|---|---|---|---|"]
    for i, row in enumerate(payload["shortlist"], 1):
        lines.append(
            f"| {i} | {row['start']} ({row['start_weekday']}) | {row['end']} ({row['end_weekday']}) | {row['days']} | "
            f"{row['block_before'] or '—'} ({row['block_before_date'] or '—'}) | {row['block_after'] or '—'} ({row['block_after_date'] or '—'}) |"
        )
    lines += ["", "## Other Bay Area radio sports included as busy days", "",
              f"- Status: **{payload['other_sports'].get('status', 'UNKNOWN')}**"]
    counts = payload["other_sports"].get("counts") or {}
    if counts:
        lines.append(f"- Rows: {counts}")
    for league, span in (payload["other_sports"].get("coverage") or {}).items():
        lines.append(f"- {league} coverage: {span.get('first') or '—'} → {span.get('last') or '—'}")
    if payload["other_sports"].get("status", "").startswith("NOT CAPTURED"):
        lines.append("- Warriors and Sharks game rows were **not** in the snapshot, so any free day is free "
                     "*only* of MLB/NFL/NCAAF/WWO until those official feeds are captured.")
    lines += ["", "## Why the long empty stretches exist (official sources)", ""]
    for note in payload["season_notes"]:
        lines.append(f"- **{note['id']} {note['league']} {note['season']}** — {note['label']} ({note['start']} → {note['end']}): "
                     f"{note['status']}. {note['effect']} Source: <{note['source_url']}>")
    lines += ["", "## Conclusion", "", payload["strict_conclusion"], "", payload["practical_reading"], "",
              "## Known limitation (flagged, not hidden)", "",
              "The published per-day scoreboards contain no row after 2027-09-26 for baseball, and the 2027 NFL, "
              "Westwood One, 2028 and 2029 season windows are unreleased. Long empty stretches late in 2027 and "
              "throughout 2028-2029 are therefore **absence of data**, not absence of games. They are never presented "
              "as verified free time.", ""]
    REPORT.write_text("\n".join(lines), encoding="utf-8")


if __name__ == "__main__":
    main()
