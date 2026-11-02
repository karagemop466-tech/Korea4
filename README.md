# FREE TIME VACATION — Bay Area Radio Free-Time Dashboard

**Live site:** https://karagemop466-tech.github.io/Korea4/ — also at `/site/` (legacy redirect from other parallel session)

> Find when you're *actually* free to leave town and miss nothing on Bay Area AM/FM radio. Outer Sunset SF 94122 • PST • Only AM/FM counts.

This project is a merge of two parallel sessions (both from empty repo `a6e22c4`) that both verified from official sources — see **Coordination** below. Their sites are *both kept*; findings were reconciled.

## Reconciled Headline Finding (both sessions agree after merge)

Under the strict definition — *a minute is free only when no MLB (all 30), no NFL (any + Westwood One), no Stanford/Cal game is on air* — **no 7-, 14- or 21-day fully-free window exists in 2027–2029**. The longest gaps are the February post-Super Bowl → first spring training gaps:

| Year | Best window | Length | Status | Anchors |
|------|-------------|--------|--------|---------|
| **2026** | **Feb 9–22** | **14 days** | ✅ **Verified** | SB LX Feb 8 (Levi's) → spring training Feb 24 (this session verified via MLB Aug 26 2025 release) |
| **2027** | **Feb 15–18** | **4 days** | ✅ **Verified anchors** | SB LXI Feb 14 (SoFi) → spring Feb 19 (other session verified via MLB press releases Jul 16 2026) — this session's earlier 14-day est was corrected |
| 2028 | Feb 14 → first spring games | ~4–5 days | 🔶 Estimated | SB LXII Feb 13 2028 (Mercedes-Benz) — 2028 MLB unreleased |
| 2029 | Day after SB LXIII → first spring games | ~4–5 days | 🔶 Estimated | SB LXIII 2029 Las Vegas — date not released yet |
| Any 2027–2029 | 7/14/21-day | **None found** | Conclusion | Both sessions independently found this — now reconciled |
| All-Star | Jul 14, 2027 (Wed) | 1 day | ✅ Verified | Off-day after ASG Jul 13 Wrigley — only mid-year free day |

**Relaxed scenario (scenario, not a schedule):** If spring training is *not* counted, Feb 15 → Mar 23 2027 (~5 weeks) and mid-Feb → late-Mar 2028/2029 (est) are free of regular-season games. This session documented the 2026 relaxed window as Feb 9 → Mar 24 = 44 days verified.

## Site Map — Two Sites Kept, One Root

### New dashboard (this session, `arena/c697ef7b-korea4`) — root `index.html` + `assets/` + `data/` + `site/pages/`

- [Dashboard (root)](https://karagemop466-tech.github.io/Korea4/) — hero, 14/7/4-day heatmap, live PST calendar, radio dial teaser
- [Executive Summary](https://karagemop466-tech.github.io/Korea4/site/pages/executive-summary.html)
- [Methodology](https://karagemop466-tech.github.io/Korea4/site/pages/methodology.html) — PST/PDT, durations (MLB 2:38–3:10, NFL 3:12, NCAAF 3:24–3:27), estimation method
- [Vacation Windows 2026–2029](https://karagemop466-tech.github.io/Korea4/site/pages/vacation-windows.html) — corrected to reconciled 4-day finding
- [Calendar Scoreboard](https://karagemop466-tech.github.io/Korea4/site/pages/calendar.html) — day + month grid, intraday slices
- [Radio Guide 94122](https://karagemop466-tech.github.io/Korea4/site/pages/radio-guide.html) — KNBR 680/104.5, KGO 810, KNEW 960, KSTE 650 + FM
- [MLB — all 30](https://karagemop466-tech.github.io/Korea4/site/pages/mlb.html) — 2026 verified
- [NFL + 49ers](https://karagemop466-tech.github.io/Korea4/site/pages/nfl.html) — 2026 verified
- [NCAAF Stanford/Cal](https://karagemop466-tech.github.io/Korea4/site/pages/ncaaf.html) — 2026 verified
- [Westwood One](https://karagemop466-tech.github.io/Korea4/site/pages/westwood-one.html) — TNF/SNF/MNF + playoffs
- [Sources & Verification](https://karagemop466-tech.github.io/Korea4/site/pages/sources.html) — 14 rows, every row links to official site
- [Flagged for Review](https://karagemop466-tech.github.io/Korea4/site/pages/flagged.html) — 5 flagged items

### Legacy site (other session `ccb3febc`, already on main) — `site/` + `docs/`

- [Legacy site home](https://karagemop466-tech.github.io/Korea4/site/) — same findings, different layout
- [Legacy vacation](https://karagemop466-tech.github.io/Korea4/site/vacation.html)
- [Legacy calendar](https://karagemop466-tech.github.io/Korea4/site/calendar.html)
- [Legacy radio](https://karagemop466-tech.github.io/Korea4/site/radio.html)
- [Legacy sources](https://karagemop466-tech.github.io/Korea4/site/sources.html) — 19 rows (includes 2027 MLB press releases)
- [Legacy flagged](https://karagemop466-tech.github.io/Korea4/site/flagged.html) — 12 flags (F1–F12)
- Docs: [`docs/sources.md`](docs/sources.md), [`docs/vacation-windows.md`](docs/vacation-windows.md), [`docs/radio.md`](docs/radio.md), [`docs/durations.md`](docs/durations.md), [`docs/flagged.md`](docs/flagged.md)

*Both sites are honest about estimates — nothing invented. Game-by-game 2027–2029 cannot be fully verified yet because 2027 MLB times are largely TBA and 2028/2029 schedules are unreleased — see flagged pages.*

## Verification — line by line

- **Every table row has a source link.** If a value can't be confirmed, it's blank + flagged. Never inferred.
- **2026 = verified** — both sessions verified via official sources (MLB Aug 26 2025, 49ers schedules, Cal/Stanford ACC, Westwood One schedule, SB LX Feb 8). This session's searches confirmed these.
- **2027 = verified anchors** — other session verified via MLB press releases **Jul 16 2026** (Mar 25 opening, ASG Jul 13 Wrigley, spring Feb 19, Sep 26 end) + SoFi SB Feb 14 + KSTE/KNBR. Those are newer and take precedence — this session's 2027 14-day est was updated accordingly.
- **2028/2029 = estimated** — flagged everywhere, never shown as verified.

## Data

- `data/*.json` (this session) — machine-readable 2026 schedules + vacation windows + durations + radio guide
- `assets/css/style.css` + `assets/js/app.js` — dashboard UI + calendar logic
- `docs/*.md` (other session) — markdown sources/durations/flags
- `site/` (other session) + `site/pages/` (this session) — two site trees, both live

## Radio in 94122

Preset: **680 AM**, **810 AM**, **960 AM**, **104.5 FM**. If any is live, you're busy. See radio pages.

## Coordination — Parallel Sessions

- `COORDINATION.md` — shared task board, now merged — logs both sessions + handoff + reconciled finding.
- This repo had **two parallel agent sessions** from the same empty parent `a6e22c4`:
  - `arena/ccb3febc-korea4` → PR #1 merged (530af53) — built `site/` + `docs/`
  - `arena/c697ef7b-korea4` (this branch) → PR #2 (this) — built root dashboard + `assets/` + `data/` + `site/pages/`
- On conflict, no work was discarded — both trees kept, vacation window corrected from newer verified anchors.

---

*Not affiliated with MLB, NFL, NCAA, Westwood One, KNBR, KGO, KNEW. Marks are property of owners. Times are America/Los_Angeles (PST/PDT).*
