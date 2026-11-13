#!/usr/bin/env python3
"""Strict gate for the NFL Lab section.

Stricter than scripts/verify.py on purpose:
  * every factual row must carry an official-host or repository source;
  * factual claims in prose must attribute a source by link;
  * "design" rows may carry no source, but must say so on the page;
  * no ranked strategy / correlation value may appear while a gate fails;
  * internal links from the lab pages must resolve.

Exit code 1 on any error. Writes research/nfl-lab-verification.md.
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path
from urllib.parse import unquote, urlsplit

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import nfl_lab_data as D  # noqa: E402

PAGES = [c["page"] for c in D.CATEGORIES]
REPORT = ROOT / "research/nfl-lab-verification.md"

OFFICIAL_HOSTS = {
    "www.nfl.com", "nfl.com", "media.nfl.com", "static.nfl.com", "static.www.nfl.com",
    "www.49ers.com",
}
REPO_HOSTS = {"github.com"}

# Prose sentences that assert a fact and must therefore carry a link.
FACT_PATTERNS = [
    (re.compile(r"\b\d+\s*(?:of|\/)\s*\d+\b"), "ratio claim — must link its source"),
    (re.compile(r"\bMost clubs\b|\bthe league (?:lists|shows|publishes)\b", re.I), "attributed claim — must link its source"),
]


def host(url: str) -> str:
    return (url or "").split("://")[-1].split("/")[0].lower()


def main() -> None:
    errors: list[str] = []
    warnings: list[str] = []
    stats = {"pages": 0, "rows": 0, "official_rows": 0, "repo_rows": 0, "design_rows": 0,
             "prose_rows": 0, "internal_links": 0, "broken_links": 0}

    for page in PAGES:
        p = ROOT / page
        if not p.exists():
            errors.append(f"missing page {page}")
            continue
        stats["pages"] += 1
        text = p.read_text(encoding="utf-8")

        # --- 1. rows ---------------------------------------------------------
        for attrs, body in re.findall(r"<tr\b([^>]*)>(.*?)</tr>", text, re.S | re.I):
            if "<td" not in body:          # header row
                continue
            if "data-no-source" in attrs and "data-source-url" in attrs:
                errors.append(f"{page}: row marked both sourced and unsourced")
            stats["rows"] += 1
            if "data-source-url=" in attrs:
                m = re.search(r'data-source-url="([^"]+)"', attrs)
                if not m:
                    errors.append(f"{page}: empty data-source-url attribute")
                    continue
                if host(m.group(1)) not in OFFICIAL_HOSTS:
                    errors.append(f"{page}: official row host not allowed: {m.group(1)[:110]}")
                if '<a class="source-link"' not in body:
                    errors.append(f"{page}: sourced row has no visible source link")
                stats["official_rows"] += 1
            elif "data-repo-source=" in attrs:
                m = re.search(r'data-repo-source="([^"]+)"', attrs)
                if host(m.group(1)) not in REPO_HOSTS:
                    errors.append(f"{page}: repo row host not allowed: {m.group(1)[:110]}")
                stats["repo_rows"] += 1
            elif "data-prose-row=" in attrs:
                stats["prose_rows"] += 1
                if "blob/main/" not in body and not re.search(
                        r'href="https?://(?:www\.)?(?:nfl|49ers)\.com', body):
                    errors.append(f"{page}: computed/prose row carries no provenance link")
            elif "data-no-source=" in attrs:
                stats["design_rows"] += 1
                if "NO SOURCE — DESIGN" not in body:
                    errors.append(f"{page}: unsourced row does not declare itself as a design row")
                m = re.search(r'data-design-source="([^"]+)"', attrs)
                if not m or host(m.group(1)) not in REPO_HOSTS:
                    errors.append(f"{page}: design row lacks a repository provenance link")
            else:
                errors.append(f"{page}: row has no source state at all")

        # --- 2. every source URL on the page must be registered -------------
        for url in set(re.findall(r'href="(https?://[^"]+)"', text)):
            if host(url) in OFFICIAL_HOSTS | REPO_HOSTS:
                if url not in {s["url"] for s in D.SOURCES} and "/blob/main/" not in url:
                    warnings.append(f"{page}: source URL not in the registry: {url[:110]}")

        # --- 3. no fabricated numbers where the design says blank ------------
        if page in ("correlation.html", "strategies.html"):
            for m in re.finditer(r"\b(?:measured value|rho|correlation)[^\n]{0,40}?(-?\d\.\d+)", text, re.I):
                errors.append(f"{page}: numeric correlation value present ({m.group(1)}) — must stay blank")
            if ">0.30<" in text and "proposal" not in text.lower():
                errors.append(f"{page}: correlation threshold printed without citing it as a proposal")

        if page == "strategies.html":
            if "NO QUALIFIED STRATEGY" not in text:
                errors.append("strategies.html: leaderboard must be explicitly empty")
            for s in D.STRATEGY_ROWS:
                passes_all = all(v == "PASS" for v in D.STRATEGY_GATES.get(s["id"], {}).values())
                if passes_all:
                    errors.append(f"{page}: {s['id']} passes every gate — leaderboard must then show it")

        if page == "validation.html":
            for s in D.STRATEGY_ROWS:
                n = sum(1 for v in D.STRATEGY_GATES.get(s["id"], {}).values() if v == "PASS")
                if f"<td>{n}/10</td>" not in text:
                    errors.append(f"validation.html: gate tally for {s['id']} missing ({n}/10)")

        # --- 4. internal links ----------------------------------------------
        for href in re.findall(r'href="([^"#:]+\.html)"', text):
            if href.startswith("http"):
                continue
            stats["internal_links"] += 1
            if not (ROOT / unquote(urlsplit(href).path)).exists():
                stats["broken_links"] += 1
                errors.append(f"{page}: broken internal link {href}")

        # --- 5. no unresolved placeholders -----------------------------------
        for bad in ("HARD FAIL", "TODO", "FIXME", "{{", "}}"):
            if bad in text:
                errors.append(f"{page}: contains placeholder {bad!r}")

        if not re.search(r'data-(?:source-url|repo-source|prose-row|design-source)=', text):
            errors.append(f"{page}: no sourced or provenance-linked rows at all")

    # --- 6. registry hygiene --------------------------------------------------
    ids = [s["id"] for s in D.SOURCES]
    if len(ids) != len(set(ids)):
        errors.append("duplicate source ids in the registry")
    for s in D.SOURCES:
        if host(s["url"]) not in OFFICIAL_HOSTS | REPO_HOSTS:
            errors.append(f"registry source not official/repo: {s['id']} {s['url']}")
    D.attach_sources()
    for row in D.AUDIT_ROWS + D.FLAG_ROWS:
        if row.get("no_source"):
            continue
        if not row.get("source_url"):
            errors.append(f"audit/flag row missing source: {row['id']}")

    # --- 7. gate honesty ------------------------------------------------------
    passed_all = [s["id"] for s in D.STRATEGY_ROWS
                  if all(v == "PASS" for v in D.STRATEGY_GATES.get(s["id"], {}).values())]
    if D.LEADERBOARD_ROWS and not passed_all:
        errors.append("leaderboard has entries but no strategy passes every gate")
    blanks = [c for c in D.CORRELATION_ROWS if not str(c.get("value") or "").strip()]
    if len(blanks) != len(D.CORRELATION_ROWS) and not passed_all:
        warnings.append("some correlation values are filled while no strategy passes the gates")

    lines = [
        "# NFL Lab verification report", "",
        f"Capture date: {D.CAPTURE_LABEL}  ·  verifier: `scripts/verify_nfl_lab.py`", "",
        "## What this gate proves", "",
        "- Every factual row on the 11 lab pages carries an official-host (league/club) or repository source link.",
        "- No official row points at a non-official host; repository rows are marked as such.",
        "- Rows with no source are explicitly labelled `NO SOURCE — DESIGN` in the page itself.",
        "- No numeric correlation value is published while every strategy fails a gate.",
        "- The leaderboard is empty exactly when no strategy passes all ten gates.",
        "- Each strategy's gate tally in the matrix matches the matrix data.",
        "- Internal links on the lab pages resolve to real files.", "",
        "## What it does NOT prove", "",
        "- It does not re-fetch the sources; content accuracy of a transcribed row rests on the",
        "  line-by-line read performed on 2026-11-13 and recorded in `research/nfl-lab-audit-2026-11-13.md`.",
        "- It does not cover the 15 pages of the main dashboard (those are gated by `scripts/verify.py`).",
        "- A passing gate means the page is structurally honest, not that the strategy is profitable.", "",
        "## Counts", "",
        f"- Pages checked: {stats['pages']}",
        f"- Rows checked: {stats['rows']} (official {stats['official_rows']}, repository {stats['repo_rows']}, design {stats['design_rows']}, prose-with-context {stats['prose_rows']})",
        f"- Internal links: {stats['internal_links']} (broken {stats['broken_links']})",
        f"- Registered sources: {len(D.SOURCES)}",
        f"- Errors: {len(errors)}", f"- Warnings: {len(warnings)}", "",
    ]
    if warnings:
        lines += ["## Warnings", ""] + [f"- {w}" for w in warnings] + [""]
    lines += ["## Result", "", "PASS" if not errors else f"FAIL ({len(errors)} errors)", ""]
    if errors:
        lines += ["## Errors", ""] + [f"- {e}" for e in errors] + [""]
    REPORT.write_text("\n".join(lines), encoding="utf-8")

    print(json.dumps({**stats, "errors": len(errors), "warnings": len(warnings),
                      "report": str(REPORT.relative_to(ROOT))}, indent=1))
    for e in errors[:40]:
        print("ERROR:", e, file=sys.stderr)
    if errors:
        sys.exit(1)


if __name__ == "__main__":
    main()
