"""Verification gate for the lines/ site.

Checks (exit code 1 on any failure):
  1. Every internal link and asset resolves to a file under lines/.
  2. Every external link uses an allowed host (official NFL/government sites, GitHub, and the
     nflverse documentation host used for definitions).
  3. Every body row of a data table (DATA_PAGES) contains at least one source link. The
     questions and suggestions pages are decision lists, not data tables, and are not checked.
  4. No template placeholders leaked into the output ({{ }} or {% %}).
"""
from __future__ import annotations

import sys
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parents[2]
SITE = ROOT / "lines"

ALLOWED_HOSTS = {
    "www.nfl.com", "nfl.com",                 # official NFL
    "www.gra.gov.sg",                         # official Singapore gambling regulator
    "sso.agc.gov.sg",                         # official Singapore statutes
    "github.com", "karagemop466-tech.github.io",  # this repository
    "nflreadr.nflverse.com",                  # documentation for the data fields used
    "api.github.com",                         # GitHub Pages API record (repository facts)
}
# Pages whose tables are data tables must have a source link on every body row.
DATA_PAGES = {"strategies.html", "seasons.html", "correlation.html", "games-2026.html",
              "injuries.html", "repo-review.html", "flagged.html", "sources.html"}


class Doc(HTMLParser):
    def __init__(self):
        super().__init__()
        self.links: list[str] = []
        self.tables: list[dict] = []
        self._in_tbody = False
        self._row = None
        self._table_class = ""

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if tag in ("a", "link", "script", "img") and ("href" in a or "src" in a):
            self.links.append(a.get("href") or a.get("src"))
        if tag == "table":
            self.tables.append({"class": a.get("class", ""), "rows": []})
        if tag == "tbody":
            self._in_tbody = True
        if tag == "tr" and self._in_tbody:
            self._row = {"html": "", "links": 0}
        if self._row is not None and tag == "a":
            self._row["links"] += 1
            self._row["html"] += "<a>"

    def handle_endtag(self, tag):
        if tag == "tbody":
            self._in_tbody = False
        if tag == "tr" and self._row is not None:
            self.tables[-1]["rows"].append(self._row)
            self._row = None

    def handle_data(self, data):
        if self._row is not None:
            self._row["html"] += data


def main() -> int:
    errors: list[str] = []
    pages = sorted(SITE.glob("*.html"))
    if not pages:
        print("no pages under lines/")
        return 1
    for page in pages:
        text = page.read_text(encoding="utf-8")
        if "{{" in text or "{%" in text:
            errors.append(f"{page.name}: template placeholder leaked")
        d = Doc()
        d.feed(text)
        for href in d.links:
            if href is None:
                continue
            u = urlparse(href)
            if u.scheme in ("http", "https"):
                if u.netloc not in ALLOWED_HOSTS:
                    errors.append(f"{page.name}: disallowed host {u.netloc} in {href}")
            elif u.scheme == "" and href and not href.startswith("#"):
                target = (page.parent / u.path).resolve()
                if not target.exists():
                    errors.append(f"{page.name}: broken internal link {href}")
        if page.name in DATA_PAGES:
            for t in d.tables:
                if "data-exempt" in t["class"]:
                    continue
                for i, row in enumerate(t["rows"]):
                    if row["links"] == 0:
                        errors.append(f"{page.name}: table row {i + 1} has no source link")
    summary = {"pages": len(pages), "errors": len(errors)}
    print(summary)
    for err in errors[:200]:
        print("ERROR", err)
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
