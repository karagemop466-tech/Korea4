#!/usr/bin/env python3
"""Static site verification: JSON, internal links, source rows, merge markers, JS syntax."""
from __future__ import annotations

import json
import gzip
import hashlib
from datetime import datetime, timezone
import re
import subprocess
import sys
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urlsplit

ROOT = Path(__file__).resolve().parents[1]
PRIMARY_PAGES = [
    "index.html", "daily.html", "calendar.html", "vacation.html", "mlb.html", "nfl.html",
    "ncaaf.html", "wwo.html", "radio.html", "sources.html", "flagged.html",
    "methodology.html", "review.html", "executive-summary.html", "teams.html",
]
REPORT = ROOT / "research/verification-report.md"


class LinkParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.links = []
        self.tbody_depth = 0
        self.in_tr = False
        self.current_row = None
        self.rows = []
    def handle_starttag(self, tag, attrs):
        d = dict(attrs)
        for attr in ("href", "src"):
            if d.get(attr):
                self.links.append(d[attr])
        if self.in_tr and tag == "a" and d.get("href"):
            self.current_row["links"].append(d["href"])
        if tag == "tbody": self.tbody_depth += 1
        if tag == "tr" and self.tbody_depth:
            self.in_tr = True
            self.current_row = {"attrs": d, "links": [], "text": ""}
    def handle_startendtag(self, tag, attrs):
        self.handle_starttag(tag, attrs)
    def handle_data(self, data):
        if self.in_tr and self.current_row is not None:
            self.current_row["text"] += data
    def handle_endtag(self, tag):
        if tag == "tr" and self.in_tr and self.current_row is not None:
            self.rows.append(self.current_row)
            self.in_tr = False
            self.current_row = None
        if tag == "tbody" and self.tbody_depth:
            self.tbody_depth -= 1
    def handle_starttag_link(self, tag, attrs):
        pass


def parse_primary_rows(path: Path):
    parser = LinkParser()
    parser.feed(path.read_text("utf-8", "replace"))
    return parser.rows


OFFICIAL_HOSTS = {
    "calbears.com", "collegefootballplayoff.com", "gostanford.com", "media.nfl.com",
    "statsapi.mlb.com", "www.49ers.com", "www.957thegame.com", "www.knbr.com",
    "www.ksfo.com", "www.mlb.com", "www.nba.com", "www.ncaa.com", "www.ncaa.org",
    "www.nfl.com", "www.nhl.com", "www.sjearthquakes.com", "www.theifab.com",
    "www.westwoodonesports.com", "static.nfl.com", "static.www.nfl.com", "fs.ncaa.org",
}


def official_url(url):
    parsed = urlsplit(url or "")
    return parsed.scheme in ("https", "http") and parsed.hostname in OFFICIAL_HOSTS and not parsed.username


def source_row_valid(row):
    source = row["attrs"].get("data-source-url", "")
    return urlsplit(source).scheme in ("https", "http") and source in row["links"]


def snapshot_errors(manifest, root=ROOT):
    errors = []
    for record in manifest["files"]:
        try:
            path = (root / record["raw_file"]).resolve()
            path.relative_to(root.resolve())
            raw = gzip.decompress(path.read_bytes())
            if hashlib.sha256(raw).hexdigest() != record["sha256"] or len(raw) != record["bytes"]:
                errors.append(f"Snapshot integrity mismatch: {record['key']}")
            if not official_url(record["url"]):
                errors.append(f"Non-official snapshot URL: {record['key']}")
        except Exception as exc:
            errors.append(f"Snapshot unreadable: {record.get('key')}: {exc}")
    return errors


def local_target(base: Path, href: str) -> Path | None:
    href = href.strip()
    if not href or href.startswith("#") or href.startswith("mailto:") or href.startswith("tel:"):
        return None
    parts = urlsplit(href)
    if parts.scheme in ("http", "https", "data", "javascript"):
        return None
    path = unquote(parts.path)
    if not path:
        return None
    if path.startswith("/"):
        # GitHub Pages project path is not known to the static checker; treat as external.
        return None
    target = (base.parent / path).resolve()
    try:
        target.relative_to(ROOT.resolve())
    except ValueError:
        return None
    return target


def main():
    errors, warnings = [], []
    # 1. JSON validity.
    json_files = sorted((ROOT / "data/official").glob("*.json")) + [ROOT / "research/line_by_line.json", ROOT / "research/official/manifest.json", ROOT / "research/probe/manifest.json"]
    for p in json_files:
        try: json.loads(p.read_text())
        except Exception as e: errors.append(f"Invalid JSON {p.relative_to(ROOT)}: {e}")
    # 2. Primary page source-row verification.
    primary_row_count = 0
    for rel in PRIMARY_PAGES:
        p = ROOT / rel
        if not p.exists():
            errors.append(f"Missing primary page {rel}")
            continue
        rows = parse_primary_rows(p)
        primary_row_count += len(rows)
        missing = [r for r in rows if not source_row_valid(r)]
        if missing:
            errors.append(f"{rel}: {len(missing)} table rows without official source URL/link")
        if "<thead>" not in p.read_text("utf-8", "replace") and "table" in p.read_text("utf-8", "replace").lower():
            warnings.append(f"{rel}: table markup without <thead>")
    # Stored evidence integrity is not live source verification.
    manifest = json.loads((ROOT / "research/official/manifest.json").read_text())
    errors.extend(snapshot_errors(manifest))
    events = json.loads((ROOT / "data/official/events.json").read_text())
    for event in events:
        if not official_url(event.get("source_url")):
            errors.append(f"Event lacks approved official source: {event.get('id')}")
    # 3. Internal links across every HTML page, preserving legacy dashboards.
    html_files = sorted(p for p in ROOT.rglob("*.html") if ".git" not in p.parts and "node_modules" not in p.parts)
    checked_links = 0
    broken = []
    for p in html_files:
        parser = LinkParser()
        parser.feed(p.read_text("utf-8", "replace"))
        for href in parser.links:
            target = local_target(p, href)
            if target is None:
                continue
            checked_links += 1
            if not target.exists():
                broken.append((str(p.relative_to(ROOT)), href, str(target.relative_to(ROOT))))
    if broken:
        errors.append(f"{len(broken)} broken internal links")
    # 4. Merge markers and obvious unresolved placeholders.
    for p in ROOT.rglob("*"):
        if not p.is_file() or ".git" in p.parts or p.suffix in (".gz", ".png", ".jpg", ".jpeg", ".webp", ".gif", ".pdf"):
            continue
        try: text = p.read_text("utf-8")
        except (UnicodeDecodeError, OSError): continue
        if re.search(r"^<<<<<<< |^=======$|^>>>>>>> ", text, re.M):
            errors.append(f"Unresolved merge markers in {p.relative_to(ROOT)}")
    # 5. JavaScript syntax.
    try:
        proc = subprocess.run(["node", "--check", str(ROOT / "js/app.js")], capture_output=True, text=True, timeout=30)
        if proc.returncode:
            errors.append(f"js/app.js syntax error: {proc.stderr.strip()}")
        js_ok = proc.returncode == 0
    except Exception as e:
        js_ok = False
        warnings.append(f"Node syntax check unavailable: {e}")
    # 6. Dynamic table rows must include source links in JS.
    js = (ROOT / "js/app.js").read_text()
    if "data-source-url" not in js or "externalLink" not in js:
        errors.append("Dynamic daily/calendar table renderer lacks explicit official source links")
    meta = json.loads((ROOT / "data/official/meta.json").read_text())
    lines = [
        "# Final verification report", "",
        f"Audit run: {datetime.now(timezone.utc).isoformat()}",
        f"Data snapshot: {meta['generated_utc']}",
        f"- Compressed official snapshots integrity-checked: {len(manifest['files'])}",
        f"- Event source domains checked: {len(events)}", "",
        f"- JSON files checked: {len(json_files)}",
        f"- Primary generated pages: {len(PRIMARY_PAGES)}",
        f"- Static primary table rows with source URL: {primary_row_count}",
        f"- HTML pages link-checked (including legacy trees): {len(html_files)}",
        f"- Internal links checked: {checked_links}",
        f"- Broken internal links: {len(broken)}",
        f"- JavaScript syntax: {'PASS' if js_ok else 'NOT CHECKED / FAIL'}",
        f"- Errors: {len(errors)}",
        f"- Warnings: {len(warnings)}", "",
        "## Automated checks and limits", "",
        "These checks validate stored file integrity, source-link structure and syntax. They do NOT re-fetch official pages, verify each fact against page content, establish complete radio carriage, or certify vacation availability.", "",
        "1. Every static primary `<tbody>` row has a source attribute matching a visible external link. Historical review rows can link to explicitly flagged nonofficial evidence.",
        "2. Dynamic daily/calendar table rows are constructed with an official source link in `js/app.js`.",
        "3. Snapshot decompressed SHA-256 hashes and byte lengths match the stored manifest.",
        "4. Event source URLs use explicitly approved official domains.",
        "5. Internal links include root, `site/`, `site/pages/`, `docs/`, and data assets.",
        "6. Labels and substantive schedule completeness still require human/source-content review; no completeness certification is produced.", "",
    ]
    if broken:
        lines += ["## Broken internal links", ""] + [f"- `{page}`: `{href}` → `{target}`" for page, href, target in broken[:200]] + [""]
    if warnings:
        lines += ["## Warnings", ""] + [f"- {w}" for w in warnings] + [""]
    if errors:
        lines += ["## Errors", ""] + [f"- {e}" for e in errors] + [""]
    else:
        lines += ["## Result", "", "PASS — no broken internal links, source-row failures, JSON errors, merge markers, or JS syntax errors.", ""]
    REPORT.write_text("\n".join(lines))
    print(json.dumps({"errors": len(errors), "warnings": len(warnings), "primary_rows": primary_row_count, "internal_links": checked_links, "broken": len(broken), "js_ok": js_ok, "report": str(REPORT.relative_to(ROOT))}, indent=2))
    if errors:
        for e in errors[:30]: print("ERROR:", e, file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
