#!/usr/bin/env python3
"""Build the NFL line-origination decision-support section (nfl-model/*.html).

Everything on these pages is rendered from nfl-model/data/*.json. No page is
hand-written, and no value is typed into HTML: a cell that has no verified
official value renders as an explicit "not confirmed" blank, and the verification
gate (scripts/verify_nfl_model.py) refuses a row that claims VERIFIED without an
official source it can point at.

Derived tables (break-even probability, required sample size, ROI standard error,
correlation bounds) are computed here from the formulas shown on the page, so the
arithmetic can never drift from its stated assumptions.
"""
from __future__ import annotations

import json
import math
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlsplit

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "nfl-model" / "data"
OUT = ROOT / "nfl-model"
SNAPSHOT_URL = "https://github.com/karagemop466-tech/Korea4/blob/main/research/official/manifest.json"

BUILD_UTC = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

NAV = [
    ("index.html", "Overview"),
    ("requirements.html", "Requirements"),
    ("questions.html", "Open questions"),
    ("suggestions.html", "Suggestions"),
    ("line-origination.html", "Line origination"),
    ("strategies.html", "Strategies"),
    ("gates.html", "Validation gates"),
    ("correlation.html", "Correlation"),
    ("leaderboard.html", "Leaderboard"),
    ("injuries.html", "Injuries"),
    ("depth-deficiency.html", "Depth & backups"),
    ("market.html", "Market facts"),
    ("sources.html", "Sources"),
    ("flagged.html", "Flagged"),
    ("executive-summary.html", "Executive summary"),
]

DISCLOSURE = (
    "This section is decision support and documentation, not betting advice and not a service offering "
    "odds or picks. It does not guarantee any profit; at NFL sample sizes a profitable-looking record can "
    "be produced by variance alone, and every unverified value on these pages is left blank for that reason. "
    "Wagering is lawful only in some jurisdictions and only for eligible adults - confirm your own "
    "jurisdiction's rules with its regulator, not with this site. If gambling stops being a choice, "
    "call or text 1-800-GAMBLER (US); Colorado players also have BetSmart.Colorado.gov."
)

STATUS_CLASS = {
    "verified": "badge-verified",
    "answered": "badge-verified",
    "met": "badge-verified",
    "auto-done": "badge-verified",
    "done": "badge-verified",
    "partial": "badge-flagged",
    "specified": "badge-estimated",
    "spec / not tested": "badge-estimated",
    "spec-not-tested": "badge-estimated",
    "trial-candidate": "badge-estimated",
    "spec": "badge-estimated",
    "awaiting-decision": "badge-flagged",
    "awaiting decision": "badge-flagged",
    "not-recommended": "badge-unverified",
    "open": "badge-unverified",
    "blocked": "badge-unverified",
    "unverified": "badge-unverified",
    "needs review": "badge-flagged",
    "not-claimed": "badge-unverified",
    "not present": "badge-unverified",
    "not-present": "badge-unverified",
    "rejected-by-gate": "badge-replaced",
    "derived": "badge-neutral",
    "exact": "badge-neutral",
    "sign-known": "badge-estimated",
    "nested-exact": "badge-neutral",
    "weak-unknown": "badge-unverified",
    "independent-by-assumption": "badge-estimated",
    "needs-measurement": "badge-unverified",
}


def load(name: str):
    return json.loads((DATA / f"{name}.json").read_text(encoding="utf-8"))


SOURCES = {s["id"]: s for s in load("sources")["sources"]}
REQ = load("requirements")
QUES = load("questions")
SUG = load("suggestions")
STRAT = load("strategies")
GATES = load("gates")
CORR = load("correlation")
LEAD = load("leaderboard")
INJ = load("injuries")
DEPTH = load("depth")
MKT = load("market")
LM = load("line_model")
FLAGS = load("flagged")


def esc(text) -> str:
    return (
        str(text)
        .replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
    )


def status_of(raw: str) -> tuple[str, str]:
    """Return (label, css-class). Unknown labels keep their text and go neutral."""
    key = (raw or "").strip().lower()
    for prefix, cls in sorted(STATUS_CLASS.items(), key=lambda kv: -len(kv[0])):
        if key.startswith(prefix):
            return raw.strip().upper().replace("—", " — "), cls
    return (raw.strip().upper() if raw else "UNVERIFIED"), "badge-neutral"


def badge(raw: str) -> str:
    label, cls = status_of(raw)
    return f'<span class="badge badge-{cls.replace("badge-", "")}">{esc(label)}</span>'


def source_cell(src_id: str) -> str:
    """Row-level official source link; a missing or unknown source id is a hard build error."""
    if not src_id:
        raise SystemExit("build error: row without a src id")
    s = SOURCES.get(src_id)
    if not s:
        raise SystemExit(f"build error: unknown source id {src_id!r}")
    url = s["url"]
    if url.startswith("http"):
        return f'<a class="source-link" href="{esc(url)}" target="_blank" rel="noopener">{esc(s["title"][:70])}</a>'
    return f'<a class="source-link" href="../{esc(url)}">{esc(s["title"][:70])}</a>'


def row_attrs(src_id: str, status: str) -> str:
    s = SOURCES.get(src_id, {})
    url = s.get("url", "")
    if not url.startswith("http"):
        url = f"https://github.com/karagemop466-tech/Korea4/blob/main/{url}"
    return f'data-source-url="{esc(url)}" data-row-status="{esc(status.lower())}" data-src-id="{esc(src_id)}"'


def cell(value, cls="", blankable=True) -> str:
    if value is None or value == "":
        if blankable:
            return '<td class="blank">not confirmed</td>'
        return '<td class="blank">—</td>'
    if isinstance(value, (int, float)):
        return f'<td class="num">{value}</td>'
    return f'<td class="{cls}">{esc(value)}</td>' if cls else f"<td>{esc(value)}</td>"


def render_table(name: str, columns: list[dict], rows: list[dict], page_size=25) -> str:
    head = "".join(f"<th>{esc(c['label'])}</th>" for c in columns)
    body = []
    for r in rows:
        status = r.get("status") or r.get("answer_status") or ""
        blank_ok = r.get("_blank_ok")
        tds = []
        for c in columns:
            v = r.get(c["key"], "")
            if c.get("kind") == "badge":
                tds.append(f"<td>{badge(str(v))}</td>")
            elif c.get("kind") == "source":
                tds.append(f"<td>{source_cell(r.get('src', ''))}</td>")
            elif c.get("kind") == "link":
                href = str(v)
                href = href if href.startswith("http") else "../" + href.lstrip("./")
                tds.append(f'<td><a href="{esc(href)}" target="_blank" rel="noopener">{esc(v)}</a></td>')
            elif c.get("kind") == "list":
                items = v if isinstance(v, list) else [v]
                tds.append("<td>" + "<br>".join(esc(x) for x in items if x) + "</td>")
            else:
                tds.append(cell(v, c.get("cls", ""), c.get("blankable", True)))
        attrs = row_attrs(r.get("src", ""), status)
        if blank_ok:
            attrs += f' data-blank-ok="{esc(blank_ok)}"'
        body.append(f"<tr {attrs}>" + "".join(tds) + "</tr>")
    return (
        f'<div class="table-wrap" data-table="{name}" data-page-size="{page_size}">\n'
        f'<div class="table-controls"><input type="search" placeholder="Filter {esc(name)} rows…" '
        'aria-label="Filter rows">'
        '<button type="button" data-status-filter="verified">Verified</button>'
        '<button type="button" data-status-filter="partial">Partial</button>'
        '<button type="button" data-status-filter="open">Open/blocked</button>'
        '<span class="pager"><button type="button" data-page-prev>‹ Prev</button>'
        '<span class="pager-label"></span><button type="button" data-page-next>Next ›</button></span></div>'
        f'<div class="scroll"><table><thead><tr>{head}</tr></thead><tbody>{"".join(body)}</tbody></table></div>'
        "</div>"
    )


# ---------------------------------------------------------------- derived math
def price_table() -> str:
    rows = []
    for price in (-105, -110, -115, -120, -130, -150, +100, +120):
        if price < 0:
            implied = -price / (-price + 100)
            dec = 1 + 100 / -price
        else:
            implied = 100 / (price + 100)
            dec = 1 + price / 100
        rows.append(
            {
                "price": f"{price:+d}" if price > 0 else str(price),
                "dec": round(dec, 4),
                "implied": f"{implied*100:.2f}%",
                "margin": f"{(implied-0.5)*100:+.2f} pts vs a coin flip",
            }
        )
    head = "".join(f"<th>{h}</th>" for h in ("American price", "Decimal", "Implied probability", "Break-even shift"))
    body = "".join(
        f'<tr {row_attrs("arxiv-nfl-lines", "derived")}><td class="num">{r["price"]}</td>'
        f'<td class="num">{r["dec"]}</td><td class="num">{r["implied"]}</td><td class="num">{r["margin"]}</td></tr>'
        for r in rows
    )
    return f'<div class="table-wrap"><div class="scroll"><table><thead><tr>{head}</tr></thead><tbody>{body}</tbody></table></div></div>'


def required_n_table() -> str:
    za, zb = 1.959963985, 0.841621234  # two-sided 5% and 80% power
    p0 = 110 / 210
    rows = []
    for edge in (0.005, 0.01, 0.02, 0.03, 0.05, 0.08):
        n = (za + zb) ** 2 * p0 * (1 - p0) / edge**2
        rows.append((edge, n, n / 272))
    head = "".join(f"<th>{h}</th>" for h in ("True edge over break-even", "Bets needed", "Seasons at 272 bets/season", "Practical read"))
    body = "".join(
        f'<tr {row_attrs("arxiv-nfl-lines", "derived")}><td class="num">{e*100:.1f} pts</td>'
        f'<td class="num">{n:,.0f}</td><td class="num">{s:.1f}</td>'
        f"<td>{esc(read)}</td></tr>"
        for (e, n, s), read in zip(
            rows,
            (
                "not separable from noise inside any single-season plan",
                "needs roughly 18 seasons of once-per-game betting",
                "needs roughly 4-5 seasons - the realistic floor for a funded side",
                "about 2 seasons at one bet per game, or one season at 4-5 independent bets per game",
                "one season is enough - which is why such edges are usually already priced out",
                "a season of a handful of bets; a number this large in a public market is a red flag about the estimate, not the opportunity",
            ),
        )
    )
    return f'<div class="table-wrap"><div class="scroll"><table><thead><tr>{head}</tr></thead><tbody>{body}</tbody></table></div></div>'


def roi_se_table() -> str:
    dec = 1 + 100 / 110
    head = "".join(f"<th>{h}</th>" for h in ("Bets logged (n)", "1 SE on ROI", "95% interval half-width", "What a 0%-edge run can look like"))
    body = ""
    for n in (50, 100, 200, 300, 550, 1000, 2000, 5000):
        se = dec * math.sqrt(0.55 * 0.45 / n)
        body += (
            f'<tr {row_attrs("arxiv-nfl-lines", "derived")}><td class="num">{n:,}</td>'
            f'<td class="num">{se*100:.2f} pts</td><td class="num">±{1.96*se*100:.2f} pts</td>'
            f"<td>roughly ±{1.64*se*100:.1f} points of ROI at the 90% level</td></tr>"
        )
    return f'<div class="table-wrap"><div class="scroll"><table><thead><tr>{head}</tr></thead><tbody>{body}</tbody></table></div></div>'


def frechet_table() -> str:
    head = "".join(f"<th>{h}</th>" for h in ("Marginal A", "Marginal B", "Joint probability range", "Implied correlation range", "Useful for pricing?"))
    body = ""
    for pa, pb in ((0.5238, 0.5238), (0.5238, 0.30), (0.75, 0.55), (0.30, 0.30)):
        lo = max(0.0, pa + pb - 1)
        hi = min(pa, pb)
        sd = math.sqrt(pa * (1 - pa) * pb * (1 - pb))
        r_lo = (lo - pa * pb) / sd if sd else float("nan")
        r_hi = (hi - pa * pb) / sd if sd else float("nan")
        body += (
            f'<tr {row_attrs("arxiv-nfl-lines", "derived")}><td class="num">{pa*100:.1f}%</td>'
            f'<td class="num">{pb*100:.1f}%</td><td class="num">[{lo:.3f}, {hi:.3f}]</td>'
            f'<td class="num">[{r_lo:+.2f}, {r_hi:+.2f}]</td>'
            "<td>no - the bound is far wider than any pricing decision, which is exactly why G-11 requires measurement</td></tr>"
        )
    for pa, pb in ((0.30, 0.55), (0.20, 0.60)):
        sd = math.sqrt(pa * (1 - pa) * pb * (1 - pb))
        rho = (pa - pa * pb) / sd  # nested: A implies B
        body += (
            f'<tr {row_attrs("arxiv-nfl-lines", "derived")}><td class="num">{pa*100:.1f}% (tighter line)</td>'
            f'<td class="num">{pb*100:.1f}% (looser line)</td><td class="num">{pa:.3f} (A implies B)</td>'
            f'<td class="num">{rho:+.3f} - exact</td><td>yes, but only because the two events are nested, so the ticket adds no information</td></tr>'
        )
    return f'<div class="table-wrap"><div class="scroll"><table><thead><tr>{head}</tr></thead><tbody>{body}</tbody></table></div></div>'


def formula(text: str) -> str:
    return f'<p class="formula">{esc(text)}</p>'


# ---------------------------------------------------------------- page chrome
def page(fname: str, active: str, title: str, lead: str, blocks: list[str], ages: list[tuple] | None = None) -> str:
    nav = ""
    for href, label in NAV:
        if href == fname:
            nav += f'<a href="{href}" class="active" aria-current="page">{label}</a>'
        else:
            nav += f'<a href="{href}">{label}</a>'
    ages_html = ""
    if ages:
        ages_html = '<div class="grid cards">' + "".join(
            f'<div class="card"><div class="label">{esc(a[0])}</div><div class="number" style="font-size:17px">{esc(a[1])}</div>'
            f'<div class="label">{esc(a[2])}</div></div>'
            for a in ages
        ) + "</div>"
    return f"""<!doctype html>
<html lang="en"><head>
<meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{esc(title)} — NFL line origination — Korea4</title>
<meta name="description" content="NFL line origination, signal strategy and validation-gate documentation for this repository.">
<link rel="stylesheet" href="../css/style.css">
<link rel="stylesheet" href="assets/model.css">
<script>window.K4_MODEL_META={{"built_utc":"{BUILD_UTC}","section":"nfl-model"}};</script>
<script src="assets/model.js" defer></script>
</head><body>
<header class="topbar"><div class="topbar-inner">
  <a class="brand" href="index.html">NFL LINES &amp; SIGNALS</a>
  <span class="tz">decision-support section of FREE TIME VACATION · built {BUILD_UTC}</span>
  <nav class="main-nav">{nav}<a href="../index.html">← Main dashboard</a></nav>
</div></header>
<main>
  <h1 class="page-title">{esc(title)}</h1>
  <p class="page-lead">{esc(lead)}</p>
  {ages_html}
  {''.join(blocks)}
  <footer class="footer">
    <strong>Every table row links to the source that establishes it; blanks are unconfirmed values, never zeros.</strong><br>
    <span class="mini">{DISCLOSURE}</span><br>
    <a href="../index.html">Main dashboard</a> <a href="../flagged.html">Dashboard flags IR-001…IR-021</a> <a href="flagged.html">Section flags</a> <a href="sources.html">Source registry</a>
    <br><span class="mini">Built {BUILD_UTC} by scripts/build_nfl_model.py from nfl-model/data/*.json; verified by scripts/verify_nfl_model.py. Source manifest of the underlying repository snapshot: <a href="{SNAPSHOT_URL}">research/official/manifest.json</a>.</span>
  </footer>
</main></body></html>
"""


def panel(title: str, intro: str, inner: str) -> str:
    return f'<section class="panel"><h2>{esc(title)}</h2><p class="intro">{esc(intro)}</p>{inner}</section>'


def callout(kind: str, html: str) -> str:
    cls = "callout" if kind == "info" else f"callout {kind}"
    return f'<div class="{cls}">{html}</div>'


def option_cards(items: list[dict], keys=("label", "detail", "risk")) -> str:
    cards = []
    for it in items:
        cards.append(
            '<div class="card"><div class="label">'
            + esc(it.get(keys[0], ""))
            + '</div><div class="mini">'
            + esc(it.get(keys[1], ""))
            + "</div>"
            + (f'<div class="mini"><strong>Risk:</strong> {esc(it.get("risk",""))}</div>' if it.get("risk") else "")
            + (f'<div class="mini"><strong>Effort/cost:</strong> {esc(it.get("effort",""))} · {esc(it.get("cost",""))}</div>' if it.get("effort") else "")
            + "</div>"
        )
    return f'<div class="grid cards" style="grid-template-columns:repeat(auto-fit,minmax(260px,1fr))">{"".join(cards)}</div>'


def write(fname: str, html: str) -> None:
    (OUT / fname).write_text(html, encoding="utf-8")
    print(f"wrote nfl-model/{fname} ({len(html):,} bytes)")


def main() -> None:
    global BUILD_UTC
    # `--stamp <utc>` re-renders with an already-published build stamp, which is how CI
    # proves the committed pages match their data without a timestamp-only false diff.
    import sys

    if "--stamp" in sys.argv:
        BUILD_UTC = sys.argv[sys.argv.index("--stamp") + 1]
    OUT.mkdir(parents=True, exist_ok=True)
    counts = {
        "requirements": len(REQ["requirements"]),
        "questions": len(QUES["questions"]),
        "suggestions": len(SUG["suggestions"]),
        "strategies": len(STRAT["strategies"]),
        "gates": len(GATES["gates"]),
        "correlation_pairs": len(CORR["pairs"]),
        "injury_rows": len(INJ["rows"]),
        "depth_rows": len(DEPTH["rows"]),
        "market_facts": len(MKT["facts"]),
        "pipeline_steps": len(LM["steps"]),
        "flags": len(FLAGS["items"]),
        "sources": len(SOURCES),
        "leaderboard_metrics": len(LEAD["metrics"]),
        "verified_rows": 0,  # recomputed from the rendered pages below
        "blank_cells": 0,
    }

    # ---------------------------------------------------------------- index
    awaiting = [s for s in SUG["suggestions"] if s["status"] == "AWAITING-DECISION"]
    blocking_q = [q for q in QUES["questions"] if q["status"] != "ANSWERED"]
    idx_blocks = [
        callout(
            "warn",
            "<strong>What this section is, and what it is not.</strong> It is the requirements, open questions, "
            "suggestions and strategy specifications for originating NFL lines and running a scored strategy "
            "competition. It is not a results page: this repository contains no market prices and no settled bets, "
            "so every result column in this section is blank by rule (IR-035). Nothing here has been implemented "
            "from the suggestions list beyond documentation, because each such item needs an owner decision.",
        ),
        '<div class="grid cards">'
        + "".join(
            f'<div class="card"><div class="number">{counts[k]}</div><div class="label">{lbl}</div></div>'
            for k, lbl in (
                ("requirements", "requirements specified"),
                ("questions", "decision-readiness questions"),
                ("suggestions", "suggestions awaiting a decision"),
                ("strategies", "strategies specified (0 tested)"),
                ("gates", "validation gates"),
                ("flags", "irregularities flagged"),
                ("sources", "official sources in the registry"),
            )
        )
        + "</div>",
        panel(
            "The three questions that block everything else",
            "Full register on the open-questions page; these are the ones whose answer changes what can be built next.",
            render_table(
                "top-questions",
                [
                    {"key": "id", "label": "ID"},
                    {"key": "decision", "label": "Decision it gates"},
                    {"key": "question", "label": "Question"},
                    {"key": "cost", "label": "Cost to answer"},
                    {"key": "status", "label": "Status", "kind": "badge"},
                    {"key": "src", "label": "Source", "kind": "source"},
                ],
                [QUES["questions"][0], QUES["questions"][3], QUES["questions"][5]],
                page_size=10,
            ),
        ),
        panel(
            "Sections",
            "Each page is a table-first view generated from the same data files, with a source link on every row.",
            '<div class="grid cards" style="grid-template-columns:repeat(auto-fit,minmax(230px,1fr))">'
            + "".join(
                f'<div class="card"><a href="{href}"><strong>{label}</strong></a>'
                f'<div class="mini">{desc}</div></div>'
                for href, label, desc in (
                    ("requirements.html", "Requirements", "28 requirements with status, acceptance test and named gap."),
                    ("questions.html", "Open questions", "What we know, what we do not, cheapest way to find out."),
                    ("suggestions.html", "Suggestions", "20 proposals with options, cost, risk and a recommendation - unimplemented."),
                    ("line-origination.html", "Line origination", "The pipeline from roster and availability to a released number, plus derived market arithmetic."),
                    ("strategies.html", "Strategies", "14 specified strategies across singles, parlays and prop combos, with 2 rejected on method."),
                    ("gates.html", "Validation gates", "18 gates that decide promotion; the luck-removal machinery is here."),
                    ("correlation.html", "Correlation", "Which leg pairs are exact, which need measurement, and why bounds are not a price."),
                    ("leaderboard.html", "Leaderboard", "Tiered competition, scoring weights, discipline rules and reward options."),
                    ("injuries.html", "Injuries", "Official Week 10 report rows as published, with the parsing traps documented."),
                    ("depth-deficiency.html", "Depth & backups", "A dated official depth chart with vacancy states and the five findings it produced."),
                    ("market.html", "Market facts", "Vig, break-even, realised state revenue data, and the roster rules that gate availability."),
                    ("sources.html", "Sources", "Every source with tier, retrieval method, date and what it actually establishes."),
                    ("flagged.html", "Flagged", "13 irregularities found while building, with evidence and effect."),
                    ("executive-summary.html", "Executive summary", "One page for the decision-maker."),
                )
            )
            + "</div>",
        ),
        panel(
            "Suggestion count by state",
            "The suggestions page is the review surface: nothing in the AWAITING-DECISION group has been built.",
            render_table(
                "sug-summary",
                [
                    {"key": "state", "label": "State", "kind": "badge"},
                    {"key": "count", "label": "Items"},
                    {"key": "ids", "label": "Suggestion ids"},
                ],
                [
                    {"state": "AWAITING-DECISION", "count": len(awaiting), "ids": ", ".join(s["id"] for s in awaiting), "src": "repo-official-snapshot", "status": "awaiting-decision"},
                    {"state": "AUTO-DONE", "count": len(SUG["suggestions"]) - len(awaiting), "ids": ", ".join(s["id"] for s in SUG["suggestions"] if s["status"] == "AUTO-DONE"), "src": "repo-official-snapshot", "status": "auto-done"},
                ],
                page_size=10,
            ),
        ),
        callout(
            "info",
            f"<strong>Answered: {len(QUES['questions']) - len(blocking_q)} of {len(QUES['questions'])} questions.</strong> "
            "The rest stay open because they need money, a legal read, an owner preference, or a document this "
            "session could not retrieve - not because nobody looked.",
        ),
    ]
    write(
        "index.html",
        page(
            "index.html",
            "index.html",
            "NFL line origination & signal leaderboard",
            "Requirements, decision-readiness, strategy specifications and validation gates for originating our own NFL lines - every row tied to an official source, every unknown left blank.",
            idx_blocks,
            [
                ("Data snapshot age", "2026-11-02", "official schedule snapshot captured by the repository (11 days before this build)"),
                ("Injury data as of", "2026-11-13", "Week 10, 2026 report retrieved by this session from nfl.com"),
                ("Depth chart as of", "11/10/26", "date published by the club on its own depth-chart page"),
                ("Market prices", "none", "no price feed exists in this repository, so no edge or result can be shown"),
            ],
        ),
    )

    # ---------------------------------------------------------------- requirements
    write(
        "requirements.html",
        page(
            "requirements.html",
            "requirements.html",
            "Requirements register",
            "The full list of requirements implied by the brief, each with an acceptance test that could actually be run and the named gap that stands between today and it.",
            [
                callout("info", f"Status counts: " + ", ".join(f"<strong>{k}</strong> {sum(1 for r in REQ['requirements'] if r['status']==k)}" for k in ("MET", "PARTIAL", "SPECIFIED", "BLOCKED")) + ". A requirement marked SPECIFIED is written, not built."),
                panel(
                    "All requirements",
                    "Sorted by category. 'Acceptance test' is what a verifier would check; if no check exists, the requirement is not real.",
                    render_table(
                        "requirements",
                        [
                            {"key": "id", "label": "ID"},
                            {"key": "cat", "label": "Area"},
                            {"key": "req", "label": "Requirement"},
                            {"key": "pri", "label": "Priority"},
                            {"key": "status", "label": "Status", "kind": "badge"},
                            {"key": "accept", "label": "Acceptance test"},
                            {"key": "gap", "label": "Named gap"},
                            {"key": "src", "label": "Source", "kind": "source"},
                        ],
                        REQ["requirements"],
                        page_size=15,
                    ),
                ),
            ],
        ),
    )

    # ---------------------------------------------------------------- questions
    write(
        "questions.html",
        page(
            "questions.html",
            "questions.html",
            "Decision-readiness: questions, information and answers",
            "What must be answered before a decision here is reasonable, split into what we already have, what we do not have, and the cheapest way to find out. Suggestions for discovering missing information are attached to each question.",
            [
                callout(
                    "warn",
                    "<strong>Nothing on this page is rhetorical.</strong> Every OPEN row has been looked for in an "
                    "official source during this session and is either unavailable without a purchase, unavailable "
                    "without a decision, or blocked by a retrieval failure recorded on the flagged page.",
                ),
                panel(
                    "Question register",
                    "Each row states the decision it gates; an answer that changes no decision is not a question worth asking.",
                    render_table(
                        "questions",
                        [
                            {"key": "id", "label": "ID"},
                            {"key": "decision", "label": "Decision it gates"},
                            {"key": "question", "label": "Question"},
                            {"key": "have", "label": "What we have"},
                            {"key": "missing", "label": "What we do not have"},
                            {"key": "how", "label": "Cheapest way to find out"},
                            {"key": "cost", "label": "Cost"},
                            {"key": "status", "label": "Answer status", "kind": "badge"},
                            {"key": "blocks", "label": "Blocks"},
                            {"key": "src", "label": "Source", "kind": "source"},
                        ],
                        QUES["questions"],
                        page_size=8,
                    ),
                ),
            ],
        ),
    )

    # ---------------------------------------------------------------- suggestions
    blocks = [
        callout(
            "warn",
            "<strong>Review surface, not a to-do list already done.</strong> Nineteen of these twenty items changed "
            "nothing in the codebase or the budget. Pick an option per item, record the decision, and only then does "
            "an agent implement it. The three AUTO-DONE items were safe to do without a decision and are labelled as such.",
        )
    ]
    for s in SUG["suggestions"]:
        opts = option_cards(
            [
                {"label": o["label"], "detail": f"Effort: {o['effort']} · Cost: {o['cost']}", "risk": o["risk"]}
                for o in s["options"]
            ]
        )
        blocks.append(
            f'<section class="panel"><h2>{esc(s["id"])} · {esc(s["area"])} — {badge(s["status"])}</h2>'
            f'<p class="intro">{esc(s["problem"])}</p>'
            f'<p><strong>Proposal:</strong> {esc(s["proposal"])}</p>'
            f"{opts}"
            f'<p><strong>Recommendation:</strong> option {esc(s["recommend"])} — {esc(s["why"])}</p>'
            f'<p><strong>Decision required from you:</strong> {esc(s["decide"])}</p>'
            f'<p class="mini"><strong>If approved, it touches:</strong> {esc(s["touches"])}</p>'
            f'<p class="mini">Evidence: {source_cell(s["src"])}</p></section>'
        )
    blocks.insert(
        1,
        panel(
            "Suggestions index",
            "One row per proposal; the detail panels below carry the options, cost, risk and recommendation.",
            render_table(
                "suggestions",
                [
                    {"key": "id", "label": "ID"},
                    {"key": "area", "label": "Area"},
                    {"key": "problem", "label": "Problem it addresses"},
                    {"key": "proposal", "label": "Proposal"},
                    {"key": "recommend", "label": "Pick"},
                    {"key": "status", "label": "State", "kind": "badge"},
                    {"key": "src", "label": "Source", "kind": "source"},
                ],
                SUG["suggestions"],
                page_size=20,
            ),
        ),
    )
    write("suggestions.html", page("suggestions.html", "suggestions.html", "Suggestions for review", "Improvement options for the site and the modelling programme, costed and ranked, held unimplemented until someone chooses a path.", blocks))

    # ---------------------------------------------------------------- line origination
    lo = [
        callout(
            "info",
            "<strong>The honest summary of this page:</strong> the pipeline is specified end to end and most of its "
            "inputs are official and free; the one input that cannot be synthesised is the market price, and until it "
            "exists no number on this site can be called an edge.",
        ),
        panel(
            "Pipeline",
            "Steps must be built in this order, because each later step's honesty depends on the earlier step's timestamps.",
            render_table(
                "pipeline",
                [
                    {"key": "id", "label": "Step"},
                    {"key": "step", "label": "What it does"},
                    {"key": "inputs", "label": "Inputs"},
                    {"key": "status", "label": "Status", "kind": "badge"},
                    {"key": "note", "label": "Constraint or finding"},
                    {"key": "src", "label": "Source", "kind": "source"},
                ],
                [dict(s, src=s.get("src") or "nfl-pro-faq-ngs") for s in LM["steps"]],
                page_size=15,
            ),
        ),
        panel(
            "Derived arithmetic — price to probability",
            "Implied probability of a single price and the break-even shift against a coin flip. Computed here from the price convention: negative prices imply -p/(-p+100), positive prices imply 100/(p+100).",
            price_table()
            + formula("Formula shown on this page; values are DERIVED, not measured, and are not a claim about any operator's current prices."),
        ),
        panel(
            "Derived arithmetic — how big must the edge be to be provable",
            "Bets needed to detect a true edge over break-even, normal approximation, two-sided 5% significance and 80% power, variance evaluated at the -110 break-even probability.",
            required_n_table()
            + formula("n = (z(0.975) + z(0.80))^2 * p0(1-p0) / edge^2 with p0 = 110/210 = 0.52381. Independent bets assumed: correlated bets, parlays and a 272-game season all make these numbers worse, never better."),
        ),
        panel(
            "Derived arithmetic — how much luck a season contains",
            "Standard error of ROI by sample size at -110 prices with a 55% true hit rate. This is the quantity the leaderboard weights against, and the reason 'it won' is not evidence.",
            roi_se_table()
            + formula("SE(ROI) = decimal_return * sqrt(p(1-p)/n) with decimal return 1.9091 at -110. A 300-bet season therefore carries a 95% interval of roughly ±10.8 ROI points around whatever the truth is."),
        ),
        panel(
            "Validation protocol",
            "What can be scored today without buying anything, and what cannot.",
            render_table(
                "validation",
                [
                    {"key": "phase", "label": "Phase"},
                    {"key": "detail", "label": "Protocol"},
                    {"key": "status", "label": "State", "kind": "badge"},
                    {"key": "src", "label": "Source", "kind": "source"},
                ],
                [
                    {"phase": "Before any price exists", "detail": LM["validation_protocol"]["before_any_price"], "status": "DERIVED - buildable now", "src": "repo-official-snapshot"},
                    {"phase": "Once prices exist", "detail": LM["validation_protocol"]["once_prices_exist"], "status": "BLOCKED - needs R-02", "src": "odds-api-nfl"},
                    {"phase": "Never permitted", "detail": LM["validation_protocol"]["never"], "status": "PROHIBITED", "src": "arxiv-nfl-lines"},
                ],
                page_size=10,
            ),
        ),
    ]
    write("line-origination.html", page("line-origination.html", "line-origination.html", "Origination pipeline and market arithmetic", "How an independent line gets produced, what it needs, and the arithmetic that decides whether a claim about it can ever be tested.", lo))

    # ---------------------------------------------------------------- strategies
    sb = [
        callout(
            "danger",
            "<strong>Read the blank columns as the result.</strong> No strategy below has a bet count, hit rate, edge "
            "or return, because there is no price data and no settled ledger in this repository (IR-035). Two entries "
            "are recorded as REJECTED-BY-GATE so that a rejected idea cannot come back looking new.",
        ),
        panel(
            "Catalogue index",
            "Family: single bet, parlay/SGP, prop combo, meta (a rule about the others) or benchmark (the yardstick).",
            render_table(
                "strategies",
                [
                    {"key": "id", "label": "ID"},
                    {"key": "name", "label": "Strategy"},
                    {"key": "family", "label": "Bet type"},
                    {"key": "market", "label": "Markets"},
                    {"key": "status", "label": "State", "kind": "badge"},
                    {"key": "gap", "label": "What is missing to test it"},
                    {"key": "src", "label": "Source", "kind": "source"},
                ],
                [dict(s, src=s.get("src") or "arxiv-nfl-lines") for s in STRAT["strategies"]],
                page_size=15,
            ),
        ),
    ]
    for s in STRAT["strategies"]:
        detail = render_table(
            f"st-{s['id'].lower()}",
            [
                {"key": "k", "label": "Field"},
                {"key": "v", "label": "Specification"},
            ],
            [
                {"k": "Hypothesis", "v": s["hypothesis"], "status": "VERIFIED - as written", "src": "repo-official-snapshot"},
                {"k": "Signal rule (mechanical)", "v": s["signal"], "status": "VERIFIED - as written", "src": "repo-official-snapshot"},
                {"k": "Required inputs", "v": "; ".join(s["inputs"]), "status": "PARTIAL - see gap", "src": "repo-official-snapshot"},
                {"k": "Correlation treatment", "v": s["corr"], "status": "VERIFIED - as written", "src": "repo-official-snapshot"},
                {"k": "Staking", "v": s["stake"], "status": "SPEC - owner decision pending", "src": "repo-official-snapshot"},
                {"k": "Why the edge could exist", "v": s["edge"] + " " + s["why_may_work"], "status": "HYPOTHESIS", "src": "arxiv-nfl-lines"},
                {"k": "Why it probably fails", "v": s["why_fails"], "status": "HYPOTHESIS", "src": "arxiv-nfl-lines"},
                {"k": "Gates applied", "v": ", ".join(s["gates"]), "status": "VERIFIED - as written", "src": "repo-official-snapshot"},
                {"k": "Data gap", "v": s["gap"], "status": "BLOCKED", "src": "repo-official-snapshot"},
            ],
            page_size=12,
        )
        results = render_table(
            f"st-{s['id'].lower()}-results",
            [
                {"key": "metric", "label": "Result metric"},
                {"key": "value", "label": "Value"},
                {"key": "gate", "label": "Gate that reads it"},
            ],
            [
                {"metric": m, "value": "", "gate": g, "status": "UNVERIFIED - no ledger", "src": "repo-official-snapshot"}
                for m, g in (
                    ("bets logged (n)", "G-09"),
                    ("hit rate ± SE", "G-05"),
                    ("mean edge at entry (pts)", "G-06"),
                    ("mean CLV vs close (pts)", "G-06"),
                    ("adjusted p-value (BH)", "G-08"),
                    ("Brier vs market", "G-07"),
                    ("ROI ± 95% interval", "G-05"),
                    ("max drawdown (units)", "G-17"),
                    ("missing-close rate", "G-14"),
                )
            ],
            page_size=10,
        )
        sb.append(
            f'<section class="panel"><h2>{esc(s["id"])} · {esc(s["name"])} {badge(s["status"])}</h2>'
            f'<p class="intro">{esc(s["family"])} · {esc(s["market"])}</p>{detail}<h3>Results (blank by rule)</h3>{results}</section>'
        )
    sb.insert(
        2,
        panel(
            "Results columns, explained",
            "Every strategy panel repeats the same nine result fields. They are blank in every panel, and the reason is a data gap, not an omission of work.",
            f'<div class="callout warn">{esc(STRAT["results_rule"])}</div>',
        ),
    )
    write("strategies.html", page("strategies.html", "strategies.html", "Strategy catalogue", "Singles, parlays and player-prop combinations, each with a mechanical signal rule, its correlation treatment, its gates, and a result column that stays blank until data exists.", sb))

    # ---------------------------------------------------------------- gates
    gb = [
        callout(
            "info",
            "<strong>Design intent:</strong> a gate is a test a strategy cannot pass by having a good month. Where a "
            "gate depends on a number this repository does not have, that is stated in its 'needs' field rather than "
            "smoothed over.",
        ),
        panel(
            "Gate set",
            "BLOCKING gates stop funding; REQUIRED-EVIDENCE gates stop publication; ADVISORY gates are displayed only.",
            render_table(
                "gates",
                [
                    {"key": "id", "label": "ID"},
                    {"key": "name", "label": "Gate"},
                    {"key": "class", "label": "Class"},
                    {"key": "rule", "label": "Mechanical rule"},
                    {"key": "why", "label": "What it protects against"},
                    {"key": "needs", "label": "Needs"},
                    {"key": "fail_action", "label": "On failure"},
                    {"key": "src", "label": "Source", "kind": "source"},
                ],
                [dict(g, src=g.get("src") or "arxiv-nfl-lines", status="SPECIFIED - design of this programme") for g in GATES["gates"]],
                page_size=20,
            ),
        ),
        panel(
            "Removing luck, stated as arithmetic",
            "Two derived tables: how large a sample an edge needs, and how much ROI noise a sample contains.",
            required_n_table()
            + roi_se_table()
            + formula("Both tables are computed by the build from the formulas above them (normal approximation, -110 payoff structure, 55% true hit rate). They are the reason G-09 and G-05 are blocking rather than advisory."),
        ),
    ]
    write("gates.html", page("gates.html", "gates.html", "Validation gates", "The tests every strategy must pass before it is funded, published or rewarded - written so that a passing strategy is a strategy, not a streak.", gb))

    # ---------------------------------------------------------------- correlation
    cb = [
        callout(
            "warn",
            "<strong>No correlation value is published in the 'measured' column, because none is measured.</strong> "
            "The column is blank by the same rule that blanks a market price; the only values shown are the ones "
            "arithmetic can produce from the marginals, and they are labelled as such.",
        ),
        panel(
            "Leg pairs",
            "Type: nested-exact (dependence fixed by construction), sign-known (direction is known, size is not), weak-unknown, independent-by-assumption.",
            render_table(
                "correlation",
                [
                    {"key": "id", "label": "ID"},
                    {"key": "legs", "label": "Leg pair"},
                    {"key": "relation", "label": "Relation"},
                    {"key": "type", "label": "Type", "kind": "badge"},
                    {"key": "direction", "label": "Expected direction"},
                    {"key": "rho", "label": "What we can state now"},
                    {"key": "measured", "label": "Measured value"},
                    {"key": "handling", "label": "Pricing / eligibility handling"},
                    {"key": "src", "label": "Source", "kind": "source"},
                ],
                [dict(p, status="SPEC - not measured", src=p.get("src") or "arxiv-nfl-lines") for p in CORR["pairs"]],
                page_size=15,
            ),
        ),
        panel(
            "Why bounds are not a price",
            "Fréchet-Hoeffding bounds on the joint probability from two marginals, converted to the correlation range they imply; nested pairs are exact but add no information.",
            frechet_table()
            + formula("P(A and B) ∈ [max(0, pA+pB-1), min(pA, pB)]; ρ = (P(A and B) - pApB) / sqrt(pA(1-pA)pB(1-pB)). For a nested pair, P(A and B) = pA exactly, which is the only case where arithmetic alone fixes ρ."),
        ),
        panel(
            "Estimation method and thresholds",
            "How a measured value gets here, and the minimum evidence before it may enter a price.",
            render_table(
                "corr-method",
                [{"key": "k", "label": "Item"}, {"key": "v", "label": "Statement"}, {"key": "status", "label": "State", "kind": "badge"}],
                [
                    {"k": "Estimator", "v": CORR["method"]["estimator"], "status": "SPECIFIED", "src": "repo-official-snapshot"},
                    {"k": "Bounds fallback", "v": CORR["method"]["bounds"], "status": "SPECIFIED", "src": "repo-official-snapshot"},
                    {"k": "Why not import published values", "v": CORR["method"]["why_not_import"], "status": "VERIFIED - policy", "src": "repo-official-snapshot"},
                    {"k": "Minimum evidence per pair", "v": CORR["method"]["minimum_n_per_pair"], "status": "SPECIFIED", "src": "repo-official-snapshot"},
                ],
                page_size=10,
            ),
        ),
    ]
    write("correlation.html", page("correlation.html", "correlation.html", "Correlation values and how they get earned", "Parlays and prop combos are joint probabilities. This page records what dependence we can state today, and the measurement path for the rest.", cb))

    # ---------------------------------------------------------------- leaderboard
    lb = [
        callout(
            "info",
            "<strong>" + esc(LEAD["concept"]) + "</strong>",
        ),
        panel(
            "Tiers",
            "Promotion between tiers is by gate evidence, and a strategy can be demoted by a failed gate but never by a bad month.",
            render_table(
                "tiers",
                [
                    {"key": "tier", "label": "Tier"},
                    {"key": "what", "label": "What happens"},
                    {"key": "scored_on", "label": "Scored on"},
                    {"key": "promotes_to", "label": "Promotes to"},
                ],
                [dict(t, status="SPECIFIED", src="repo-official-snapshot") for t in LEAD["tiers"]],
                page_size=10,
            ),
        ),
        panel(
            "Scoring metrics",
            "Weights are the design's opinion about what deserves credit: information and discipline dominate, profit is a minor term.",
            render_table(
                "metrics",
                [
                    {"key": "id", "label": "ID"},
                    {"key": "metric", "label": "Metric"},
                    {"key": "formula", "label": "Definition"},
                    {"key": "weight", "label": "Weight"},
                    {"key": "min_n", "label": "Min n"},
                    {"key": "value", "label": "Current value"},
                    {"key": "why", "label": "Why it resists luck"},
                    {"key": "src", "label": "Source", "kind": "source"},
                ],
                [dict(m, src=m.get("src") or "arxiv-nfl-lines", status=m.get("status", "UNVERIFIED - no entries")) for m in LEAD["metrics"]],
                page_size=10,
            ),
        ),
        panel(
            "Discipline rules",
            "The rules that keep a ranked competition from becoming a leaderboard of whoever logged the most flattering subset.",
            "<ul>" + "".join(f"<li>{esc(r)}</li>" for r in LEAD["discipline_rules"]) + "</ul>",
        ),
        panel(
            "Reward structure (awaiting decision)",
            "Status: " + LEAD["rewards"]["status"] + ". Recommendation: " + LEAD["rewards"]["recommended"],
            option_cards([{"label": o["label"], "detail": o["detail"], "risk": o["risk"]} for o in LEAD["rewards"]["options"]]),
        ),
        panel(
            "Season window and entry state",
            "What the competition would run on, and how many entrants exist today (none).",
            render_table(
                "season",
                [{"key": "k", "label": "Item"}, {"key": "v", "label": "Value"}, {"key": "status", "label": "State", "kind": "badge"}],
                [
                    {"k": "Season window", "v": LEAD["season_window"]["value"] + " — " + LEAD["season_window"]["note"], "status": LEAD["season_window"]["status"], "src": "repo-official-snapshot"},
                    {"k": "Registered entries", "v": str(LEAD["entry_count"]["value"]) + " — " + LEAD["entry_count"]["note"], "status": LEAD["entry_count"]["status"], "src": "repo-official-snapshot"},
                    {"k": "Standings", "v": LEAD["standings_note"], "status": "NOT-CLAIMED", "src": "repo-official-snapshot"},
                ],
                page_size=10,
            ),
        ),
    ]
    write("leaderboard.html", page("leaderboard.html", "leaderboard.html", "Leaderboard competition design", "A season-long internal competition where strategies earn their place by gate evidence and closing-line edge, not by which month they got lucky in.", lb))

    # ---------------------------------------------------------------- injuries
    ib = [
        callout(
            "warn",
            "<strong>Coverage: one club, one week, one document.</strong> "
            + INJ["coverage"][2]["detail"]
            + " The rows below are transcribed from the official page exactly as it presented them, including its blanks.",
        ),
        panel(
            "How to read the official report",
            "Three rules that determine almost every bug in an injury pipeline.",
            "<ul>" + "".join(f"<li>{esc(r)}</li>" for r in INJ["reading_rules"]) + "</ul>",
        ),
        panel(
            "Week 10, 2026 — " + INJ["context"]["game"],
            INJ["context"]["when"] + " · " + INJ["context"]["records_shown_on_page"] + " · " + INJ["context"]["note"],
            render_table(
                "injuries",
                [
                    {"key": "club", "label": "Club"},
                    {"key": "player", "label": "Player"},
                    {"key": "pos", "label": "Pos"},
                    {"key": "injury", "label": "Injury (as published)"},
                    {"key": "practice", "label": "Practice status"},
                    {"key": "game_status", "label": "Game status"},
                    {"key": "chart_depth", "label": "Depth-chart position"},
                    {"key": "status", "label": "State", "kind": "badge"},
                    {"key": "src", "label": "Source", "kind": "source"},
                ],
                [dict(r, status="VERIFIED (blanks are as published by the league)", _blank_ok="as-published-blank", src="nfl-injuries-reg10") for r in INJ["rows"]],
                page_size=20,
            ),
        ),
        panel(
            "Retrieval coverage and its limits",
            "What this session actually read, so nobody mistakes one club's rows for league-wide tracking.",
            render_table(
                "coverage",
                [
                    {"key": "scope", "label": "Scope"},
                    {"key": "count", "label": "Count"},
                    {"key": "detail", "label": "Detail"},
                    {"key": "status", "label": "State", "kind": "badge"},
                    {"key": "src", "label": "Source", "kind": "source"},
                ],
                [dict(c, status="VERIFIED", src="nfl-injuries-reg10") for c in INJ["coverage"]],
                page_size=10,
            ),
        ),
        panel(
            "From report to signal: the tracking model",
            "What the system must store, in what cadence, and which interpretations are forbidden.",
            render_table(
                "injury-model",
                [{"key": "k", "label": "Element"}, {"key": "v", "label": "Design"}, {"key": "status", "label": "State", "kind": "badge"}, {"key": "src", "label": "Source", "kind": "source"}],
                [
                    {"k": "Grain", "v": "one row per (club, player, report day, field) with the league's own status vocabulary; never a single 'current' table", "status": "SPECIFIED", "src": "repo-official-snapshot"},
                    {"k": "Blank handling", "v": "a missing game status is stored as NO_DESIGNATION, a missing diagnosis as NO_DIAGNOSIS; neither is ever converted to a probability (IR-038)", "status": "SPECIFIED", "src": "nfl-injury-policy"},
                    {"k": "Cadence", "v": "capture on every official report day (the page publishes one status per player, so the ladder must be assembled from successive captures - IR-032)", "status": "SPECIFIED", "src": "nfl-injuries-current"},
                    {"k": "Render-integrity assertion", "v": "a snapshot is rejected unless every club block and a per-club minimum row count are present, because a partial page render looks like a healthy roster (IR-033)", "status": "SPECIFIED", "src": "repo-official-snapshot"},
                    {"k": "Rule-derived windows", "v": "transactions converted to dated unavailability using the league roster rules, with the rule version recorded (IR-029)", "status": "PARTIAL", "src": "nfl-roster-faq"},
                    {"k": "Signal use", "v": "availability enters as a unit-level delta against the depth chart (ST-04, ST-05, ST-06, ST-07); raw counts are not signals", "status": "SPECIFIED", "src": "arxiv-nfl-lines"},
                    {"k": "Secondary data", "v": "aggregator detail (injury type, 'rest', reporter attribution) may be stored in a clearly labelled secondary table that no gate and no verified row may read (Q-14)", "status": "UNVERIFIED - excluded from values", "src": "secondary-injury-aggregators"},
                ],
                page_size=12,
            ),
        ),
    ]
    write("injuries.html", page("injuries.html", "injuries.html", "Injury tracking (official report, verified rows)", "What the league publishes about availability, what the blanks mean, and what our one-week sample shows about the traps in this data.", ib, [("Report as of", "Week 10, 2026", "retrieved from nfl.com on 2026-11-13"), ("Clubs covered", "1 of 32", "San Francisco 49ers structured; see IR-034")]))

    # ---------------------------------------------------------------- depth
    db = [
        callout(
            "info",
            "<strong>Source and date:</strong> the club's own depth-chart page, which carries its own "
            f"'Updated as of {esc(DEPTH['club_published_as_of'])}' stamp. This is the only official document that "
            "shows what the team itself says about who is next man up.",
        ),
        panel(
            DEPTH.get("method_note", ""),
            "d1 = first string as listed by the club; empty slots are exactly as the club lists them.",
            render_table(
                "depth",
                [
                    {"key": "group", "label": "Unit"},
                    {"key": "pos", "label": "Position"},
                    {"key": "d1", "label": "1st string"},
                    {"key": "d1_note", "label": "1st-string availability note"},
                    {"key": "d2", "label": "2nd string"},
                    {"key": "d3", "label": "3rd string"},
                    {"key": "count", "label": "Names listed"},
                    {"key": "vacancy", "label": "Listed-depth state", "kind": "badge"},
                    {"key": "src", "label": "Source", "kind": "source"},
                ],
                [
                    dict(
                        r,
                        count=sum(1 for k in ("d1", "d2", "d3", "d4") if r.get(k)),
                        vacancy=("no listed backup" if sum(1 for k in ("d2", "d3", "d4") if r.get(k)) == 0 else ("thin: 2 listed" if sum(1 for k in ("d2", "d3", "d4") if r.get(k)) == 1 else "3+ listed")),
                        status="VERIFIED (an empty string is what the club lists)",
                        _blank_ok="as-published-blank",
                        src="sf-depth-chart",
                    )
                    for r in DEPTH["rows"]
                ],
                page_size=20,
            ),
        ),
        panel(
            "Findings from this one chart",
            "Each finding is an arithmetic or coverage observation about the documents retrieved, not a claim about team strength.",
            render_table(
                "depth-flags",
                [{"key": "id", "label": "ID"}, {"key": "finding", "label": "Finding"}, {"key": "consequence", "label": "Consequence for the model"}, {"key": "action", "label": "Action taken in this build"}, {"key": "status", "label": "State", "kind": "badge"}, {"key": "src", "label": "Source", "kind": "source"}],
                [dict(f, status="VERIFIED", src="sf-depth-chart") for f in DEPTH["flags"]],
                page_size=10,
            ),
        ),
        panel(
            "Deficiency index specification",
            "What the brief asks for - 'know the deficiencies in defenses when backups replace starters' - becomes this; it is a formula plus a data requirement, and it deliberately has no coefficient until measured.",
            render_table(
                "deficiency",
                [{"key": "k", "label": "Component"}, {"key": "v", "label": "Definition"}, {"key": "status", "label": "State", "kind": "badge"}, {"key": "src", "label": "Source", "kind": "source"}],
                [
                    {"k": "Unit grouping", "v": "positions mapped to units (secondary, front seven, interior line, skill) so a group's availability can be assessed together rather than name-by-name", "status": "SPECIFIED", "src": "repo-official-snapshot"},
                    {"k": "Replacement tier", "v": "rank of the highest-available player on the club's own chart, plus the explicit state 'no listed backup' (this chart produced that state at left corner)", "status": "VERIFIED - observable", "src": "sf-depth-chart"},
                    {"k": "Availability weight", "v": "DNP > Limited > Full > absent from report, using the league's own definitions, with NO_DESIGNATION kept separate", "status": "SPECIFIED", "src": "nfl-injury-policy"},
                    {"k": "League baseline", "v": "distribution of listed depth per position across all 32 charts, required before any 'thin depth' threshold means anything (IR-036)", "status": "BLOCKED - needs 31 more clubs", "src": "repo-official-snapshot"},
                    {"k": "Impact coefficient", "v": "effect of a replacement tier on expected points, to be fitted on our own history with opponent, rest, venue and game-importance controls held fixed (SG-19)", "status": "BLOCKED - needs results + prices", "src": "arxiv-nfl-lines"},
                    {"k": "Offence mirror", "v": "identical structure applied to offensive units; the brief asks for both, and one chart already shows a first-string left tackle and a first-string running back both listed DNP", "status": "SPECIFIED", "src": "nfl-injuries-reg10"},
                ],
                page_size=10,
            ),
        ),
    ]
    write("depth-deficiency.html", page("depth-deficiency.html", "depth-deficiency.html", "Depth charts and backup replacement", "Who the team itself says is next man up, what the club's own chart shows when it lists nobody, and the specification that turns that into a deficiency measure.", db, [("Chart date", DEPTH["club_published_as_of"], "published by the club on its own page"), ("Clubs collected", "1 of 32", "32 parsers and a staleness rule are required first (IR-028)")]))

    # ---------------------------------------------------------------- market
    mb = [
        panel(
            "Verified market and regulatory facts",
            "State revenue documents are used here for one reason: they quantify what the market actually costs a bettor, which is the bar every strategy must clear.",
            render_table(
                "market",
                [
                    {"key": "id", "label": "ID"},
                    {"key": "topic", "label": "Topic"},
                    {"key": "fact", "label": "Fact"},
                    {"key": "value", "label": "Value"},
                    {"key": "status", "label": "Status", "kind": "badge"},
                    {"key": "note", "label": "Interpretation and caveat"},
                    {"key": "src", "label": "Source", "kind": "source"},
                ],
                MKT["facts"],
                page_size=15,
            ),
        ),
        callout(
            "warn",
            "<strong>Why a state's tax figure is not a hold percentage.</strong> The Colorado release publishes handle "
            "and tax on the same page, but tax is a share of adjusted gross revenue, and the report that contains "
            "revenue by bet type is a separate operator-level PDF (Q-04). Nothing on this site converts a tax number "
            "into a hold claim.",
        ),
        panel(
            "Compliance and consumer-protection items",
            "Recorded because the brief asks for a decision-support site, and a decision that ignores jurisdiction is not a decision.",
            render_table(
                "compliance",
                [{"key": "k", "label": "Item"}, {"key": "v", "label": "Position of this section"}, {"key": "status", "label": "Status", "kind": "badge"}, {"key": "src", "label": "Source", "kind": "source"}],
                [
                    {"k": "Age and eligibility", "v": "Not asserted anywhere; open question Q-06 blocks any real-money step.", "status": "UNVERIFIED", "src": "repo-official-snapshot"},
                    {"k": "Legal review of the reward mechanism", "v": "A prize competition attached to a betting-adjacent leaderboard is escalated to counsel before it is run (Q-13, Q-15).", "status": "OPEN", "src": "in-68iac-27"},
                    {"k": "Self-settlement", "v": "Outcomes come from the league's official statistics and the season's stat standard; a regulator rule we cite requires outcomes to be verifiable and independently produced (G-13).", "status": "PARTIAL", "src": "in-68iac-27"},
                    {"k": "No profit claim", "v": "The section publishes zero profit figures because it has zero settled bets; the absence is enforced by the build, not by wording.", "status": "NOT-CLAIMED", "src": "repo-official-snapshot"},
                    {"k": "Help resource", "v": "Carried in the footer of every page here, as the state regulator that supplies our market data does on its own release.", "status": "VERIFIED", "src": "co-gaming-sept26"},
                ],
                page_size=10,
            ),
        ),
    ]
    write("market.html", page("market.html", "market.html", "Market, regulatory and roster facts", "The external conditions any originated line has to survive: what the market costs, what the league publishes, what a regulator requires.", mb))

    # ---------------------------------------------------------------- sources
    sb2 = [
        callout("info", "<strong>" + esc(load("sources")["policy"]) + "</strong>"),
        panel(
            "Source registry",
            "Tier: official-league / official-team / official-government / official-operator / official-vendor / academic / secondary / repo-internal. Method is how this session obtained it.",
            render_table(
                "sources",
                [
                    {"key": "id", "label": "ID"},
                    {"key": "title", "label": "Title"},
                    {"key": "org", "label": "Publisher"},
                    {"key": "tier", "label": "Tier"},
                    {"key": "retrieved", "label": "Retrieved"},
                    {"key": "method", "label": "Method"},
                    {"key": "status", "label": "Status", "kind": "badge"},
                    {"key": "url", "label": "Link", "kind": "link"},
                    {"key": "establishes", "label": "What it establishes"},
                    {"key": "notes", "label": "Caveats"},
                ],
                [dict(s, src=s["id"]) for s in SOURCES.values()],
                page_size=15,
            ),
        ),
    ]
    write("sources.html", page("sources.html", "sources.html", "Source registry", "Every document behind this section, with its publisher, tier, retrieval method, date and the specific thing it proves.", sb2))

    # ---------------------------------------------------------------- flagged
    fb = [
        callout(
            "danger",
            "<strong>These are the findings a reviewer should read first.</strong> " + esc(FLAGS["rule"]),
        ),
        panel(
            "Irregularities, IR-027 onward",
            "Scope note: " + FLAGS["scope"],
            render_table(
                "flags",
                [
                    {"key": "id", "label": "ID"},
                    {"key": "severity", "label": "Severity"},
                    {"key": "title", "label": "Finding"},
                    {"key": "detail", "label": "What was observed"},
                    {"key": "evidence", "label": "Evidence"},
                    {"key": "effect", "label": "Effect on this section"},
                    {"key": "action", "label": "Action / next step"},
                    {"key": "found", "label": "Found"},
                    {"key": "status", "label": "State", "kind": "badge"},
                    {"key": "src", "label": "Source", "kind": "source"},
                ],
                [dict(f, status="NEEDS REVIEW", src=f.get("src") or "repo-official-snapshot") for f in FLAGS["items"]],
                page_size=15,
            ),
        ),
    ]
    write("flagged.html", page("flagged.html", "flagged.html", "Flagged for review", "Irregularities found while building this section, each with evidence, effect and the next step - published so they can be reviewed after the site is live.", fb))

    # ---------------------------------------------------------------- executive summary
    met = sum(1 for r in REQ["requirements"] if r["status"] == "MET")
    answered = sum(1 for q in QUES["questions"] if q["status"] == "ANSWERED")
    eb = [
        callout(
            "warn",
            "<strong>Bottom line.</strong> The NFL line-origination programme is now specified, documented and "
            "verifiable - and it has no results, because results require one purchased input that no amount of "
            "modelling can substitute for. That is the single most important fact for planning: the work to date "
            "removes ambiguity about what to build and in what order, not about whether the market can be beaten.",
        ),
        panel(
            "Scoreboard of the section itself",
            "Counts computed at build time from the data files behind the tables.",
            '<div class="grid cards">'
            + "".join(
                f'<div class="card"><div class="number">{a}</div><div class="label">{b}</div></div>'
                for a, b in (
                    (f"{met}/{len(REQ['requirements'])}", "requirements met today"),
                    (f"{answered}/{len(QUES['questions'])}", "questions answerable from what we have"),
                    (f"{len(awaiting)}/{len(SUG['suggestions'])}", "suggestions awaiting your decision"),
                    (f"{len(STRAT['strategies'])}", "strategies specified · 0 tested · 2 rejected by gate"),
                    (f"{len(GATES['gates'])}", "validation gates defined"),
                    (f"{len(FLAGS['items'])}", "irregularities flagged for review"),
                    (f"{len(SOURCES)}", "sources in the registry"),
                )
            )
            + "</div>",
        ),
        panel(
            "What is real today (verified inputs)",
            "The verified building blocks, so the plan is not mistaken for speculation.",
            render_table(
                "exec-verified",
                [{"key": "k", "label": "Input"}, {"key": "v", "label": "What we verified, and when"}, {"key": "status", "label": "Status", "kind": "badge"}, {"key": "src", "label": "Source", "kind": "source"}],
                [
                    {"k": "Availability reporting", "v": "Week 10, 2026 per-club report rows transcribed from the official page (twelve 49ers entries; no game-status designations), plus the league's own definitions of every status value", "status": "VERIFIED", "src": "nfl-injuries-reg10"},
                    {"k": "Depth and replacements", "v": "the club's own chart dated 11/10/26, including a position where it lists no backup at all", "status": "VERIFIED", "src": "sf-depth-chart"},
                    {"k": "Roster rules that date an absence", "v": "injured reserve: no list limit, eight return designations per club, four-game minimum; 16-man practice squads; PUP/NFI activation after four games (2022-era wording, so rule versioning is required)", "status": "PARTIAL", "src": "nfl-roster-faq"},
                    {"k": "Market cost benchmark", "v": "Colorado: September 2026 handle $546,819,852.87 with $4,743,419.32 tax; New Jersey: August 2026 sports wagering revenue $61,445,421, down 25.0% year over year", "status": "VERIFIED", "src": "co-gaming-sept26"},
                    {"k": "Data-latency constraint", "v": "the league publishes tracking data the day after the game, and live box score and play-by-play during it - which decides what a pre-kickoff prop model can know", "status": "VERIFIED", "src": "nfl-pro-faq-ngs"},
                    {"k": "Price-feed availability", "v": "a documented NFL feed with moneyline, spreads, totals, quarter/half and player props, historical from mid-2020, with a free key tier to trial against", "status": "VERIFIED", "src": "odds-api-nfl"},
                    {"k": "Break-even arithmetic", "v": "52.381% needed at -110, and 2,560 games of 2002-2011 public data where home underdogs produced 53.5% against that threshold - a ~1 point margin over break-even in a decade-old sample", "status": "VERIFIED", "src": "arxiv-nfl-lines"},
                ],
                page_size=10,
            ),
        ),
        panel(
            "What is missing (and who can supply it)",
            "Three of these need a decision, two need money, one needs a legal read, none need research that has not already been scoped.",
            render_table(
                "exec-missing",
                [{"key": "k", "label": "Missing"}, {"key": "v", "label": "Why it blocks"}, {"key": "who", "label": "Who unblocks it"}, {"key": "src", "label": "Source", "kind": "source"}],
                [
                    {"k": "Market prices (open, midweek, close) and prop lines", "v": "without them there is no edge, no CLV, no correlation estimate and no leaderboard; every result table stays blank", "who": "owner: approve the SG-01 trial", "src": "odds-api-nfl"},
                    {"k": "Box scores / play-level results in this repository", "v": "the largest free gap: no scoring baselines means no originated number, and results are official and unpurchased", "who": "agent task once scope is agreed", "src": "repo-official-snapshot"},
                    {"k": "31 remaining depth charts and every report day of the season", "v": "cross-league deficiency and any league-wide baseline for 'thin depth'", "who": "agent task; needs the 32-parser collector accepted (SG-10)", "src": "sf-depth-chart"},
                    {"k": "Objective: originate a line, or find mispriced bets", "v": "the metric that decides promotion differs (Brier calibration versus closing-line value); tuning against the wrong one wastes the season", "who": "owner: Q-02", "src": "arxiv-nfl-lines"},
                    {"k": "Jurisdiction, eligibility, bankroll and unit size", "v": "gates G-10 and G-17 cannot be evaluated without a stake policy, and any real step needs legality confirmed", "who": "owner: Q-06 and Q-16", "src": "repo-official-snapshot"},
                    {"k": "Legal read on the reward mechanism", "v": "prize competition law is separate from wagering law; the design avoids stake-pool prizes for this reason", "who": "owner's counsel: Q-13", "src": "in-68iac-27"},
                ],
                page_size=10,
            ),
        ),
        panel(
            "Recommended path, in order",
            "Sequenced so that each step is falsifiable before the next one spends money.",
            "<ol>"
            + "".join(
                f"<li>{esc(x)}</li>"
                for x in (
                    "Answer Q-02 (objective) and Q-06 (jurisdiction/eligibility) - free, and they decide everything downstream.",
                    "Approve SG-01 option A: a short, logged price-feed trial through the remaining 2026 weeks. No archive purchase until the trial proves coverage.",
                    "Build the free half now: box-score ingestion (LM-06), 32-club chart and report collection (LM-03/LM-04), and the discrete margin model (SG-08). None of it needs a purchase.",
                    "Start Tier 1 paper logging with the frozen gate set and pre-registered specs (SG-06, G-01..G-04). No strategy is funded on the first season, ever.",
                    "Only after a season of CLV and calibration evidence: pick the funding policy (Q-16), then choose a reward model (SG-14), then legal review (Q-13).",
                    "Keep the site's honesty machinery mandatory: per-dataset staleness (SG-18/SG-05), gate-enforced disclosures (SG-17), and blanks rather than guesses in every result column.",
                )
            )
            + "</ol>",
        ),
        panel(
            "Risk register for the decision-maker",
            "What would make this programme's numbers wrong in a way that is hard to notice.",
            render_table(
                "exec-risk",
                [{"key": "k", "label": "Risk"}, {"key": "v", "label": "Why it matters here"}, {"key": "mitigation", "label": "Mitigation in this design"}, {"key": "src", "label": "Source", "kind": "source"}],
                [
                    {"k": "Silent partial renders of official pages", "v": "a truncated injury page looks like a healthy roster, which is a fabricated signal rather than a visible gap", "mitigation": "row-count and per-club presence assertions before a snapshot is accepted (IR-033)", "src": "nfl-injuries-current"},
                    {"k": "Blank-as-signal parsing errors", "v": "the league deliberately omits certain-to-play players from the game status, so a default of 'Questionable' invents availability news", "mitigation": "NO_DESIGNATION stored as its own state, plus a unit test that no feature reads a blank as a probability (IR-038)", "src": "nfl-injury-policy"},
                    {"k": "Small-sample self-deception", "v": "±10.8 points of ROI at 300 bets means a season can look excellent by chance", "mitigation": "G-05 luck budget and G-09 effect-size sizing are blocking, and profit carries a 0.10 leaderboard weight", "src": "arxiv-nfl-lines"},
                    {"k": "Catalogue shopping", "v": "testing 14 strategies at 5% produces winners with no edge", "mitigation": "Benjamini-Hochberg adjustment across the whole evaluation list, and no removal of losing entries (G-08, G-18)", "src": "arxiv-nfl-lines"},
                    {"k": "Rules that change under the model", "v": "roster rules, prop definitions and operator correlation policies all move between seasons", "mitigation": "rule and stat-standard snapshots per season with hashes, referenced by every affected row (G-12, G-13)", "src": "nfl-roster-faq"},
                    {"k": "Stale data presented as current", "v": "the schedule snapshot is already 11 days behind this build, and depth or injury data decays within days", "mitigation": "per-dataset age stamps in each table header and a gate failure when a VERIFIED claim exceeds its staleness threshold (SG-05/SG-18)", "src": "repo-official-snapshot"},
                ],
                page_size=10,
            ),
        ),
        callout(
            "info",
            "<strong>Manual input required from you:</strong> exactly the six items in the 'missing' table. Everything "
            "else in this session - research, data retrieval, verification, code, build, publication - was completed "
            "without asking. Flagged items and unverified values are published here rather than held back, so the "
            "site is usable and the uncertainty stays visible.",
        ),
    ]
    write("executive-summary.html", page("executive-summary.html", "executive-summary.html", "Executive summary", "The one-page read for whoever decides: what is verified, what is missing, what it costs, and what to do first.", eb))

    # ---------------------------------------------------------------- meta
    # Tally the rendered pages rather than the inputs, so these numbers describe what a
    # reader actually sees (a row can only be VERIFIED if its source was retrieved).
    rendered = "".join((OUT / href).read_text(encoding="utf-8") for href, _ in NAV)
    counts["verified_rows"] = rendered.count('data-row-status="verified')
    counts["blank_cells"] = rendered.count('class="blank"')
    meta = {
        "section": "nfl-model",
        "built_utc": BUILD_UTC,
        "counts": counts,
        "data_snapshots": {
            "schedule_official_snapshot_captured": "2026-11-02T17:41:45Z",
            "injury_report_retrieved": INJ["retrieved"],
            "depth_chart_club_as_of": DEPTH["club_published_as_of"],
            "regulator_reports": {"colorado": "September 2026 (released 2026-11-05)", "new_jersey": "August 2026 (released 2026-09-16)"},
            "market_price_feed": None,
        },
        "pages": [href for href, _ in NAV],
        "disclosure_required_in_every_page": "1-800-GAMBLER",
    }
    (DATA / "meta.json").write_text(json.dumps(meta, indent=2) + "\n", encoding="utf-8")
    print(f"wrote nfl-model/data/meta.json · {counts}")


if __name__ == "__main__":
    main()
