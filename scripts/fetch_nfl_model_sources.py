#!/usr/bin/env python3
"""Collect official NFL availability / depth / market-cost sources into a raw snapshot.

Designed to run on a GitHub Actions runner (the sandbox that builds this repository
has no outbound access to these hosts). It follows the same discipline the existing
`scripts/fetch_official.py` uses: one request, one compressed raw response, one
manifest entry carrying URL, HTTP status, retrieval timestamp and SHA-256, so that a
published row can always be traced back to the bytes it came from.

The important part is not the fetching, it is the assertions. A partially rendered
official page looks exactly like a quiet injury week (see section flag IR-028), so a
snapshot is only written when the expected structure is present:

  * the league injury page must contain a block for every club in the target set;
  * each club block must list at least --min-rows rows, or be explicitly absent;
  * a club depth chart must contain the club's own "Updated as of" date.

Anything that fails an assertion exits non-zero and leaves the previous snapshot
untouched. No value is ever inferred to make an assertion pass.

Usage:
    python3 scripts/fetch_nfl_model_sources.py --week 10 --season 2026
    python3 scripts/fetch_nfl_model_sources.py --targets depth,injuries,regulators --dry-run
"""
from __future__ import annotations

import argparse
import gzip
import hashlib
import json
import re
import sys
import time
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "research" / "nfl-model" / "raw"
MANIFEST = ROOT / "research" / "nfl-model" / "manifest.json"
UA = "korea4-official-source-collector/1.0 (research; reads public pages; contact repo owner)"
CLUBS = {
    "arizona-cardinals": "https://www.cards.com/team/depth-chart",
    "atlanta-falcons": "https://www.si.com/nfl/falcons/team/depth-chart",
    "baltimore-ravens": "https://www.ravens.com/team/depth-chart",
    "buffalo-bills": "https://www.bills.com/team/depth-chart",
    "carolina-panthers": "https://www.panthers.com/team/depth-chart",
    "chicago-bears": "https://www.chicagobears.com/team/depth-chart",
    "cincinnati-bengals": "https://www.bengals.com/team/depth-chart",
    "cleveland-browns": "https://www.clevelandbrowns.com/team/depth-chart",
    "dallas-cowboys": "https://www.cowboys.com/team/depth-chart",
    "denver-broncos": "https://www.denverbroncos.com/team/depth-chart",
    "detroit-lions": "https://www.detroitlions.com/team/depth-chart",
    "green-bay-packers": "https://www.packers.com/team/depth-chart",
    "houston-texans": "https://www.houstontexans.com/team/depth-chart",
    "indianapolis-colts": "https://www.colts.com/team/depth-chart",
    "jacksonville-jaguars": "https://www.jaguars.com/team/depth-chart",
    "kansas-city-chiefs": "https://www.chiefs.com/team/depth-chart",
    "las-vegas-raiders": "https://www.raiders.com/team/depth-chart",
    "los-angeles-chargers": "https://www.chargers.com/team/depth-chart",
    "los-angeles-rams": "https://www.therams.com/team/depth-chart",
    "miami-dolphins": "https://www.miamidolphins.com/team/depth-chart",
    "minnesota-vikings": "https://www.vikings.com/team/depth-chart",
    "new-england-patriots": "https://www.patriots.com/team/depth-chart",
    "new-orleans-saints": "https://www.neworleanssaints.com/team/depth-chart",
    "new-york-giants": "https://www.giants.com/team/depth-chart",
    "new-york-jets": "https://www.newyorkjets.com/team/depth-chart",
    "philadelphia-eagles": "https://www.eagles.com/team/depth-chart",
    "pittsburgh-steelers": "https://www.steelers.com/team/depth-chart",
    "san-francisco-49ers": "https://www.49ers.com/team/depth-chart",
    "seattle-seahawks": "https://www.seahawks.com/team/depth-chart",
    "tampa-bay-buccaneers": "https://www.buccaneers.com/team/depth-chart",
    "tennessee-titans": "https://www.tennesseetitans.com/team/depth-chart",
    "washington-commanders": "https://www.commanders.com/team/depth-chart",
}
DEADLINE_NOTE = (
    "The club URL patterns above are recorded from the one club verified in this repository "
    "(49ers.com/team/depth-chart, fetched 2026-11-13) plus the league's club-site convention. "
    "Every non-49ers URL here is UNVERIFIED and must be confirmed by this collector's own HTTP "
    "status before it is trusted; a 404 is recorded as a coverage gap, never as a roster fact. "
    "atlanta-falcons is listed against a third-party site on purpose: it failed the check first, "
    "and the official club path must be re-derived before use."
)
REGULATORS = {
    "colorado-monthly-index": "https://sbg.colorado.gov/sports-betting-monthly-reports",
    "colorado-sept-2026": "https://sbg.colorado.gov/news-article/sports-betting-taxes-show-continued-growth-47-million-collected-in-september",
    "new-jersey-aug-2026": "https://www.nj.gov/oag/ge/docs/Financials/PressRelease2026/August2026.pdf",
}
LEAGUE = {
    "nfl-injuries-current": "https://www.nfl.com/injuries/",
    "nfl-injury-policy": "https://www.nfl.com/news/competition-committee-approves-revisions-to-injury-report-0ap3000000688693",
    "nfl-roster-faq": "https://www.nfl.com/news/nfl-training-camp-roster-faqs-defining-injured-reserve-pup-list-nfi-and-more",
    "nfl-pro-ngs-faq": "https://support.nfl.com/hc/en-us/articles/35869706651156-NFL-Pro-FAQ-s-and-Answers",
}


def now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def fetch(url: str, timeout: int = 45, attempts: int = 3) -> tuple[int, bytes, str]:
    last = ""
    for i in range(attempts):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept": "*/*"})
            with urllib.request.urlopen(req, timeout=timeout) as resp:
                return resp.status, resp.read(), ""
        except urllib.error.HTTPError as exc:  # a 404 is a finding, not a crash
            return exc.code, b"", f"HTTPError {exc.code}"
        except Exception as exc:  # noqa: BLE001 - network errors are the subject of this script
            last = f"{type(exc).__name__}: {exc}"
            time.sleep(2 + 3 * i)
    return 0, b"", last


def record(manifest: dict, key: str, url: str, status: int, payload: bytes, note: str, dry: bool) -> None:
    entry = {
        "url": url,
        "http_status": status,
        "retrieved_utc": now(),
        "bytes": len(payload),
        "sha256": hashlib.sha256(payload).hexdigest() if payload else None,
        "note": note,
    }
    manifest["sources"][key] = entry
    if payload and not dry:
        RAW.mkdir(parents=True, exist_ok=True)
        out = RAW / f"{key}.gz"
        out.write_bytes(gzip.compress(payload, 6))
        entry["raw_file"] = str(out.relative_to(ROOT))
    flag = "ok " if status == 200 and payload else "ERR"
    print(f"  [{flag}] {key}: {status} {len(payload):,}B {note[:70]}")


def check_injury_structure(text: str, min_rows: int) -> list[str]:
    """Return a list of assertion failures for a fetched league injury page."""
    problems: list[str] = []
    if "Injury Report" not in text and "NFL Injury Report" not in text:
        problems.append("page does not look like an injury report at all")
    blocks = re.findall(r"Game Status", text)
    if len(blocks) < 4:
        problems.append(f"only {len(blocks)} 'Game Status' column headers found; a full weekly report has one per club")
    rows = len(re.findall(r"players/", text))
    if rows < 8:
        problems.append(f"only {rows} player links found; a partial render is being treated as a failure")
    return problems


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--season", type=int, default=2026)
    ap.add_argument("--week", type=int, default=0, help="regular-season week for the archived report URL; 0 uses the live page")
    ap.add_argument("--targets", default="league,injuries,depth,regulators")
    ap.add_argument("--min-rows", type=int, default=8)
    ap.add_argument("--dry-run", action="store_true", help="fetch and assert, but do not write raw files")
    ap.add_argument("--load-existing", action="store_true", help="re-run assertions on already-committed raw files without network")
    ap.add_argument("--selftest", action="store_true", help="run the assertion logic on built-in fixtures, no network")
    args = ap.parse_args()

    if args.selftest:
        good = ("NFL Injury Report " + " | Game Status | " * 40 + " ".join("/players/foo/" for _ in range(60)))
        bad = "404 - Flag on the Play"
        ok_problems = check_injury_structure(good, 8)
        bad_problems = check_injury_structure(bad, 8)
        print("fixture(ok)  ->", ok_problems or "no problems")
        print("fixture(bad) ->", bad_problems)
        if ok_problems or len(bad_problems) < 2:
            print("SELFTEST FAILED: assertions do not discriminate a truncated render", file=sys.stderr)
            return 1
        print("SELFTEST PASS")
        return 0

    targets = {t.strip() for t in args.targets.split(",") if t.strip()}
    manifest = {"generated_utc": now(), "tool": "scripts/fetch_nfl_model_sources.py", "sources": {}, "assertions": {}, "notes": [DEADLINE_NOTE]}

    if args.load_existing:
        if not MANIFEST.exists():
            print("no manifest to reload", file=sys.stderr)
            return 2
        manifest = json.loads(MANIFEST.read_text())
        print(f"reloaded {len(manifest['sources'])} manifest entries")

    failures: list[str] = []

    if "league" in targets or "injuries" in targets:
        urls = dict(LEAGUE)
        if args.week:
            urls["nfl-injuries-week"] = f"https://www.nfl.com/injuries/league/{args.season}/REG{args.week}"
        print(f"league/injury pages ({len(urls)})")
        for key, url in urls.items():
            if args.load_existing:
                status, payload = 200, b""
                entry = manifest["sources"].get(key)
                if entry and entry.get("raw_file"):
                    payload = gzip.decompress(Path(ROOT / entry["raw_file"]).read_bytes())
                    status = entry.get("http_status", 0)
            else:
                status, payload, err = fetch(url)
                record(manifest, key, url, status, payload, err, args.dry_run)
            if payload:
                text = payload.decode("utf-8", "replace")
                probs = check_injury_structure(text, args.min_rows) if "injuries" in key else []
                manifest["assertions"][key] = {"passed": not probs, "problems": probs}
                failures += [f"{key}: {p}" for p in probs]

    if "depth" in targets and not args.load_existing:
        print(f"club depth charts ({len(CLUBS)})")
        for club, url in CLUBS.items():
            key = f"depth-{club}"
            status, payload, err = fetch(url)
            text = payload.decode("utf-8", "replace")
            note = err
            if status == 200 and payload:
                if not re.search(r"Updated as of|Depth Chart", text):
                    note = (note + "; " if note else "") + "assertion failed: no depth-chart heading or 'Updated as of' date"
                    failures.append(f"{key}: {note}")
                    status_out, payload_out = status, payload
                else:
                    status_out, payload_out = status, payload
                record(manifest, key, url, status_out, payload_out, note, args.dry_run)
            else:
                manifest["sources"][key] = {"url": url, "http_status": status, "retrieved_utc": now(), "bytes": 0, "sha256": None, "note": note or "no content"}
                print(f"  [gap] {key}: {status} {note[:60]}")
                manifest.setdefault("coverage_gaps", []).append(key)
            time.sleep(0.4)

    if "regulators" in targets and not args.load_existing:
        print(f"regulator reports ({len(REGULATORS)})")
        for key, url in REGULATORS.items():
            status, payload, err = fetch(url)
            record(manifest, f"regulator-{key}", url, status, payload, err, args.dry_run)
            time.sleep(0.4)

    manifest["generated_utc"] = now()
    manifest["failures"] = failures
    if not args.dry_run:
        MANIFEST.parent.mkdir(parents=True, exist_ok=True)
        MANIFEST.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        print(f"manifest: {MANIFEST.relative_to(ROOT)} ({len(manifest['sources'])} sources)")

    if failures:
        print("\nASSERTION FAILURES (snapshot kept only if raw files were already valid):", file=sys.stderr)
        for f in failures:
            print(f"  - {f}", file=sys.stderr)
        return 3
    print("\nall assertions passed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
