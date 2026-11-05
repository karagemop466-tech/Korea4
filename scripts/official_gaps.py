#!/usr/bin/env python3
"""Officially-released-only free-window audit for Jan 1 – Mar 31, 2027.

Reads data/official/days-2027.json (produced by scripts/collect_official.py) and
writes research/analysis/official_gaps.json. No network access.

Three definitions are reported for each run of consecutive free days:
  strict_no_rows : no row of any kind (official, estimate, or UNVERIFIED block).
  ignore_models  : ESTIMATED season-pattern model rows ignored; UNVERIFIED blocks still busy.
  released_only  : model rows and UNVERIFIED blocks ignored (released official rows only).

Free time is never inferred: a day with no row is only "free in the snapshot".
Every run lists the source URLs of the rows that bound it.
"""
from __future__ import annotations

import json
from datetime import date, timedelta
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DAYS_2027 = ROOT / "data" / "official" / "days-2027.json"
OUT = ROOT / "research" / "analysis" / "official_gaps.json"
START = date(2027, 1, 1)
END = date(2027, 3, 31)
MODEL = "ESTIMATED_UNRELEASED_SEASON_MODEL"
UNVERIFIED = "UNVERIFIED_BLOCK"

DEFINITIONS = {
    "strict_no_rows": lambda r: False,
    "ignore_models": lambda r: r.get("status") == MODEL,
    "released_only": lambda r: r.get("status") in (MODEL, UNVERIFIED),
}


def runs_for(days: dict[str, list], ignore) -> list[dict]:
    out, cur, d = [], None, START
    while d <= END:
        busy = [r for r in days.get(d.isoformat(), []) if not ignore(r)]
        if not busy:
            cur = [d, d] if cur is None else [cur[0], d]
        elif cur is not None:
            out.append(cur)
            cur = None
        d += timedelta(days=1)
    if cur is not None:
        out.append(cur)
    result = []
    for a, b in out:
        bounds = []
        for edge in (a - timedelta(days=1), b + timedelta(days=1)):
            if START <= edge <= END:
                for r in days.get(edge.isoformat(), []):
                    if not ignore(r) and r.get("source_url") and r["source_url"] not in bounds:
                        bounds.append(r["source_url"])
        result.append({
            "start": a.isoformat(), "end": b.isoformat(), "length_days": (b - a).days + 1,
            "bounding_source_urls": bounds[:6],
        })
    return result


def day_summary(days: dict[str, list]) -> list[dict]:
    rows = []
    d = START
    while d <= END:
        items = days.get(d.isoformat(), [])
        released = sorted({r.get("category", "") for r in items if r.get("status") not in (MODEL, UNVERIFIED)})
        unverified = sorted({r.get("category", "") for r in items if r.get("status") == UNVERIFIED})
        models = sorted({r.get("category", "") for r in items if r.get("status") == MODEL})
        rows.append({
            "date": d.isoformat(), "weekday": d.strftime("%a"),
            "released_categories": released, "unverified_categories": unverified,
            "model_categories": models,
            "status": "RELEASED BUSY" if released else ("UNVERIFIED BUSY" if unverified else ("MODEL ONLY" if models else "NO ROWS")),
        })
        d += timedelta(days=1)
    return rows


def main() -> None:
    days = json.loads(DAYS_2027.read_text(encoding="utf-8"))
    runs = {name: runs_for(days, ignore) for name, ignore in DEFINITIONS.items()}
    longest = {name: max(rs, key=lambda r: r["length_days"]) if rs else None for name, rs in runs.items()}
    runs_3plus = {name: [r for r in rs if r["length_days"] >= 3] for name, rs in runs.items()}
    payload = {
        "generated_by": "scripts/official_gaps.py",
        "scope": f"{START.isoformat()} to {END.isoformat()}",
        "input": "data/official/days-2027.json",
        "definitions": {
            "strict_no_rows": "No row of any kind, including ESTIMATED models and UNVERIFIED blocks.",
            "ignore_models": "ESTIMATED season-pattern models ignored; UNVERIFIED blocks still count as busy.",
            "released_only": "Released official rows only; models and UNVERIFIED blocks ignored.",
        },
        "longest_run": longest,
        "runs_3_days_or_longer": runs_3plus,
        "runs": runs,
        "days": day_summary(days),
        "conclusion": (
            f"Longest free run under the strict definition: {longest['strict_no_rows']['length_days']} day(s) "
            f"({longest['strict_no_rows']['start']} to {longest['strict_no_rows']['end']}). "
            f"Longest under released-only: {longest['released_only']['length_days']} day(s). "
            "Warriors home games on Feb 15 and Feb 17 (95.7 The Game) rule out the earlier Feb 15–18 gap. "
            "Sharks (NHL) games have no Bay Area AM/FM carriage on the official list and are not radio-busy. Earthquakes 2027 Sprint Season games are official rows (radio carriage UNVERIFIED). These runs are not certified free."
        ),
        "not_covered": [
            "Sharks 2026–27 games: all carried on the Sharks Audio Network; no Bay Area AM/FM affiliate on the official list, so they are not counted as radio-busy. Sharks TV/NTN games are not added to the busy calendar.",
            "San Jose Earthquakes 2027 Sprint Season (14 official games, Feb 20 – May 8): busy blocks kept conservatively; Bay Area radio carriage is UNVERIFIED.",
            "25 Warriors dates (including Mar 3 and Mar 9 onward) are UNVERIFIED and count as busy only as UNVERIFIED blocks.",
            "WWO 2027 February schedule and NCAAF 2027 schedule are unreleased; their Feb blocks are ESTIMATED models.",
        ],
        "note": "Free time is never inferred. A run is free only in the captured official snapshot.",
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps({k: (v["length_days"] if v else 0) for k, v in longest.items()}, indent=2))


if __name__ == "__main__":
    main()
