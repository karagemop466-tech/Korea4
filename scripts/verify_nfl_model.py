#!/usr/bin/env python3
"""Verification gate for the nfl-model section.

This is the check that makes the section's honesty claim machine-enforced rather
than rhetorical. It fails when a rendered row:

  * has no source URL, or a source id missing from the registry;
  * claims VERIFIED while its source was only seen in a search snippet, or comes
    from a publisher tier that is not official;
  * contains a blank cell while claiming VERIFIED, unless the row explicitly says
    the blank is how the official document published it;
  * points at a host outside the allowlist, or a relative link that does not exist;
  * reports a strategy result value (there is no ledger, so a filled result cell is
    by definition fabricated);
  * drops the mandatory disclosure block.

Exit code 0 with zero errors means the pages can be published; flagged or unverified
rows are allowed and expected, they are what the blanks are for.
"""
from __future__ import annotations

import json
import re
import sys
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlsplit

ROOT = Path(__file__).resolve().parents[1]
SEC = ROOT / "nfl-model"
DATA = SEC / "data"

ALLOWED_HOSTS = {
    "www.nfl.com", "nfl.com", "static.www.nfl.com", "static.clubs.nfl.com", "support.nfl.com",
    "www.49ers.com", "49ers.com",
    "sbg.colorado.gov", "www.nj.gov", "www.in.gov", "iar.iga.in.gov",
    "the-odds-api.com", "api.the-odds-api.com",
    "arxiv.org", "github.com", "api.github.com",
}
# Hosts that may be cited so a reader can audit a partial or secondary claim, but
# that can never carry a VERIFIED row: an operator's rules page hosted by a casino,
# and injury aggregators that carry detail the league does not publish.
REFERENCE_ONLY_HOSTS = {
    "lb.goldennugget.com", "www.goldennugget.com", "beta.goldennugget.com",
    "www.sharpfootballanalysis.com",
}
CITABLE_HOSTS = ALLOWED_HOSTS | REFERENCE_ONLY_HOSTS
OFFICIAL_TIERS = {
    "official-league", "official-team", "official-government",
    "official-operator", "official-vendor", "academic", "repo-internal", "official-platform",
}
FETCH_METHODS = {"page-fetched", "pdf-fetched", "github-api-404", "github-api", "repo-snapshot"}
TIERS_SEEN_OK = OFFICIAL_TIERS | {"secondary"}
REQUIRED_ON_PAGE = ("1-800-GAMBLER", "not betting advice", "does not guarantee", "css/style.css")
MIN_FLAG_ID = 26  # the root dashboard + its NFL pages already publish IR-001..IR-026; this section must not reuse them


def load(name: str):
    return json.loads((DATA / f"{name}.json").read_text(encoding="utf-8"))


class RowParser(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.rows: list[dict] = []
        self.cur = None
        self.in_tbody = 0
        self.cell_cls = None
        self.links: list[str] = []
        self.cell_text = ""

    def handle_starttag(self, tag, attrs):
        d = dict(attrs)
        if d.get("href"):
            self.links.append(d["href"])
        if d.get("src"):
            self.links.append(d["src"])
        if tag == "tbody":
            self.in_tbody += 1
        elif tag == "tr" and self.in_tbody:
            self.cur = {"attrs": d, "blank_cells": 0, "text": ""}
        elif tag == "td" and self.cur is not None:
            self.cell_cls = d.get("class", "")
            self.cell_text = ""

    def handle_data(self, data):
        if self.cur is not None:
            self.cur["text"] += data

    def handle_endtag(self, tag):
        if tag == "tbody":
            self.in_tbody = max(0, self.in_tbody - 1)
        elif tag == "td" and self.cur is not None:
            if self.cell_cls and "blank" in self.cell_cls:
                self.cur["blank_cells"] += 1
            self.cell_cls = None
        elif tag == "tr" and self.cur is not None:
            self.rows.append(self.cur)
            self.cur = None


def check_registry(errors: list[str], warnings: list[str]) -> dict:
    reg = load("sources")
    srcs = reg["sources"]
    ids = [s["id"] for s in srcs]
    if len(ids) != len(set(ids)):
        errors.append("sources.json: duplicate source ids")
    stats = {"sources": len(srcs), "verified_sources": 0, "partial_sources": 0}
    for s in srcs:
        for field in ("id", "title", "org", "tier", "url", "retrieved", "method", "establishes", "status"):
            if not s.get(field):
                errors.append(f"sources.json {s.get('id','?')}: missing field {field}")
        if s.get("tier") not in TIERS_SEEN_OK:
            errors.append(f"sources.json {s['id']}: tier {s.get('tier')!r} is not a recognised publisher tier")
        if s.get("status") == "VERIFIED" and s.get("method") not in FETCH_METHODS:
            errors.append(f"sources.json {s['id']}: claims VERIFIED but method is {s.get('method')!r} (search-snippet may not certify)")
        if s.get("status") not in {"VERIFIED", "PARTIAL", "UNVERIFIED"}:
            errors.append(f"sources.json {s['id']}: unknown status {s.get('status')!r}")
        url = s["url"]
        if url.startswith("http"):
            if not url.startswith("https://"):
                errors.append(f"sources.json {s['id']}: url is not https: {url}")
            host = urlsplit(url).netloc.lower()
            if host not in CITABLE_HOSTS:
                errors.append(f"sources.json {s['id']}: host not on citation allowlist: {host}")
            if host in REFERENCE_ONLY_HOSTS and s["status"] == "VERIFIED":
                errors.append(f"sources.json {s['id']}: reference-only host cannot carry a VERIFIED source")
        elif not (SEC.parent / url).exists() and not (ROOT / url).exists():
            errors.append(f"sources.json {s['id']}: relative source does not exist: {url}")
        stats["verified_sources" if s["status"] == "VERIFIED" else "partial_sources"] += 1
    return {"sources": srcs, "by_id": {s["id"]: s for s in srcs}, **stats}


def check_ids(errors: list[str]) -> None:
    groups = {
        "requirements": ("requirements", "id", "R-"),
        "questions": ("questions", "id", "Q-"),
        "suggestions": ("suggestions", "id", "SG-"),
        "strategies": ("strategies", "id", "ST-"),
        "gates": ("gates", "id", "G-"),
        "flagged": ("items", "id", "IR-"),
        "market": ("facts", "id", "M-"),
        "correlation": ("pairs", "id", "C-"),
    }
    for fname, (key, idfield, prefix) in groups.items():
        doc = load(fname)
        ids = [r[idfield] for r in doc[key]]
        if len(ids) != len(set(ids)):
            errors.append(f"{fname}.json: duplicate ids")
        bad = [i for i in ids if not i.startswith(prefix)]
        if bad:
            errors.append(f"{fname}.json: ids not using prefix {prefix}: {bad}")
    flags = [r["id"] for r in load("flagged")["items"]]
    for fid in flags:
        try:
            num = int(fid.split("-")[1])
        except ValueError:
            errors.append(f"flagged.json: unparsable flag id {fid}")
            continue
        if num < MIN_FLAG_ID:
            errors.append(f"flagged.json: {fid} collides with the root pages' IR-001..IR-026 range")
    # suggestions must not silently become 'done'
    for s in load("suggestions")["suggestions"]:
        if s["status"] not in {"AWAITING-DECISION", "AUTO-DONE", "NOT-RECOMMENDED"}:
            errors.append(f"suggestions.json {s['id']}: unexpected state {s['status']!r}")
        if s["status"] == "AWAITING-DECISION" and not s.get("decide"):
            errors.append(f"suggestions.json {s['id']}: awaiting decision but states no decision to make")
        for o in s["options"]:
            for field in ("label", "effort", "cost", "risk"):
                if not o.get(field):
                    errors.append(f"suggestions.json {s['id']}: option missing {field}")
        if s["recommend"] not in [o["label"].split(" - ")[0][-1] for o in s["options"]]:
            errors.append(f"suggestions.json {s['id']}: recommendation {s['recommend']!r} does not match an offered option")
    # strategies: results must be empty, and every strategy must name its gates
    known_gates = {g["id"] for g in load("gates")["gates"]}
    for st in load("strategies")["strategies"]:
        if st.get("results"):
            errors.append(f"strategies.json {st['id']}: results must be empty until a bet ledger exists")
        for gid in st["gates"]:
            if gid not in known_gates:
                errors.append(f"strategies.json {st['id']}: references unknown gate {gid}")
        if st["status"] not in {"SPEC-NOT-TESTED", "REJECTED-BY-GATE", "TRIAL-CANDIDATE"}:
            errors.append(f"strategies.json {st['id']}: unknown status {st['status']!r}")
    # every question must name the decision it gates and a way to find the answer
    for q in load("questions")["questions"]:
        for field in ("decision", "question", "have", "missing", "how", "blocks"):
            if not q.get(field):
                errors.append(f"questions.json {q['id']}: missing {field}")
    for r in load("requirements")["requirements"]:
        for field in ("req", "accept", "status"):
            if not r.get(field):
                errors.append(f"requirements.json {r['id']}: missing {field}")
        if r["status"] == "MET" and not r.get("gap"):
            warnings.append(f"requirements.json {r['id']}: marked MET with no named remaining gap - re-check")


def check_pages(errors: list[str], warnings: list[str], by_id: dict) -> dict:
    pages = sorted(p for p in SEC.glob("*.html"))
    stats = {"pages": len(pages), "rows": 0, "rows_with_source": 0, "blank_rows": 0, "links": 0, "broken_links": 0}
    nav_names = [p.name for p in pages]
    for p in pages:
        html = p.read_text(encoding="utf-8")
        if "[<<<" in html or ">>>><<<" in html or "<<<<<<<" in html:
            errors.append(f"{p.name}: merge marker left in generated page")
        for token in REQUIRED_ON_PAGE:
            if token not in html:
                errors.append(f"{p.name}: required disclosure/asset missing: {token!r}")
        parser = RowParser()
        parser.feed(html)
        stats["rows"] += len(parser.rows)
        for row in parser.rows:
            a = row["attrs"]
            url = a.get("data-source-url", "")
            sid = a.get("data-src-id", "")
            status = (a.get("data-row-status") or "").strip().lower()
            if not url:
                errors.append(f"{p.name}: row without data-source-url: {row['text'][:60]!r}")
                continue
            stats["rows_with_source"] += 1
            if sid and sid not in by_id:
                errors.append(f"{p.name}: row cites unknown source id {sid!r}")
            if url.startswith("http"):
                host = urlsplit(url).netloc.lower()
                if host not in CITABLE_HOSTS:
                    errors.append(f"{p.name}: row source host not on citation allowlist: {host}")
                if status.startswith("verified"):
                    if host not in ALLOWED_HOSTS:
                        errors.append(f"{p.name}: VERIFIED row cites a reference-only host ({host})")
                    src = by_id.get(sid, {})
                    if src.get("tier") not in OFFICIAL_TIERS:
                        errors.append(f"{p.name}: row claims VERIFIED from tier {src.get('tier')!r} ({sid})")
                    if src.get("method") not in FETCH_METHODS:
                        errors.append(f"{p.name}: row claims VERIFIED from method {src.get('method')!r} ({sid})")
            else:
                target = (SEC / url).resolve()
                if not target.exists():
                    stats["broken_links"] += 1
                    errors.append(f"{p.name}: relative source does not resolve: {url}")
            if row["blank_cells"]:
                stats["blank_rows"] += 1
                if status.startswith("verified") and not a.get("data-blank-ok"):
                    errors.append(
                        f"{p.name}: VERIFIED row contains {row['blank_cells']} blank cell(s) without an "
                        f"as-published-blank assertion: {row['text'][:60]!r}"
                    )
        for href in parser.links:
            if href.startswith(("http://", "https://", "mailto:", "#", "data:")):
                continue
            stats["links"] += 1
            target = (p.parent / href.split("?")[0].split("#")[0])
            if not target.exists():
                stats["broken_links"] += 1
                errors.append(f"{p.name}: broken internal link -> {href}")
        # every page must reach every other page through its nav
        for name in nav_names:
            if name != p.name and f'href="{name}"' not in html:
                errors.append(f"{p.name}: navigation does not link to {name}")
    return stats


def check_meta(errors: list[str], stats: dict, sreg: dict) -> None:
    meta = load("meta")
    counts = meta["counts"]
    expect = {
        "requirements": len(load("requirements")["requirements"]),
        "questions": len(load("questions")["questions"]),
        "suggestions": len(load("suggestions")["suggestions"]),
        "strategies": len(load("strategies")["strategies"]),
        "gates": len(load("gates")["gates"]),
        "correlation_pairs": len(load("correlation")["pairs"]),
        "injury_rows": len(load("injuries")["rows"]),
        "depth_rows": len(load("depth")["rows"]),
        "market_facts": len(load("market")["facts"]),
        "pipeline_steps": len(load("line_model")["steps"]),
        "flags": len(load("flagged")["items"]),
        "sources": sreg["sources"],
    }
    for k, v in expect.items():
        if counts.get(k) != v:
            errors.append(f"meta.json: counts.{k} = {counts.get(k)} but data has {v}")
    for page_name in meta["pages"]:
        if not (SEC / page_name).exists():
            errors.append(f"meta.json: lists page that does not exist: {page_name}")
    if not meta.get("built_utc"):
        errors.append("meta.json: built_utc missing")
    if meta["data_snapshots"].get("market_price_feed") is not None:
        errors.append("meta.json: market_price_feed must stay null until a feed actually exists")


def check_sources_cited(errors: list[str], warnings: list[str], by_id: dict) -> None:
    used = set()
    for p in SEC.glob("*.html"):
        if p.name == "sources.html":  # the registry cites itself; that is not a substantive use
            continue
        used |= set(re.findall(r'data-src-id="([^"]+)"', p.read_text(encoding="utf-8")))
    for sid, s in by_id.items():
        if s.get("use") == "corroboration-only":
            continue  # registered on purpose: its facts are carried by a fetched source
        if sid not in used:
            warnings.append(f"sources.json: {sid} is registered but cited by no substantive row (registry entry only)")


def main() -> int:
    errors: list[str] = []
    warnings: list[str] = []
    if not SEC.exists():
        print("nfl-model/ not found - run scripts/build_nfl_model.py first", file=sys.stderr)
        return 2
    try:
        sreg = check_registry(errors, warnings)
    except Exception as exc:  # registry must load before anything else can be judged
        print(f"FATAL: source registry unusable: {exc}", file=sys.stderr)
        return 2
    try:
        check_ids(errors)
    except Exception as exc:
        print(f"FATAL: data files unusable: {exc}", file=sys.stderr)
        return 2
    stats = check_pages(errors, warnings, sreg["by_id"])
    check_meta(errors, stats, sreg)
    check_sources_cited(errors, warnings, sreg["by_id"])

    report = ROOT / "research" / "nfl-model" / "verification-report.md"
    report.parent.mkdir(parents=True, exist_ok=True)
    report.write_text(
        "# nfl-model verification report\n\n"
        f"- pages checked: {stats['pages']}\n"
        f"- table rows checked: {stats['rows']} (all carrying a source: {stats['rows_with_source']})\n"
        f"- rows containing an explicit blank/unconfirmed cell: {stats['blank_rows']}\n"
        f"- internal links checked: {stats['links']}, broken: {stats['broken_links']}\n"
        f"- sources in registry: {sreg['sources']} ({sreg['verified_sources']} verified by retrieval, {sreg['partial_sources']} partial)\n"
        f"- errors: {len(errors)}\n- warnings: {len(warnings)}\n\n"
        "Rules enforced are listed in the header of scripts/verify_nfl_model.py. A warning is advisory "
        "(for example a registered source that no row cites); an error blocks publication.\n\n"
        + ("## Errors\n" + "\n".join(f"- {e}" for e in errors) if errors else "## Errors\nnone\n")
        + ("\n## Warnings\n" + "\n".join(f"- {w}" for w in warnings) if warnings else "\n## Warnings\nnone\n"),
        encoding="utf-8",
    )
    for e in errors:
        print(f"ERROR: {e}")
    for w in warnings:
        print(f"warn:  {w}")
    print(
        f"\nnfl-model: {stats['pages']} pages, {stats['rows']} rows, {stats['rows_with_source']} source-linked, "
        f"{stats['blank_rows']} rows with declared blanks, {stats['links']} internal links "
        f"({stats['broken_links']} broken), {len(errors)} errors, {len(warnings)} warnings"
    )
    print(f"report: {report.relative_to(ROOT)}")
    if errors:
        return 1
    print("PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
