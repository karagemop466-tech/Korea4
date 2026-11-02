# Executive Summary — Free Time Vacation (Bay Area Sports Radio)
Date: 2026-11-02 · Session: arena-97161ae7 · Site: https://karagemop466-tech.github.io/Korea4/

## The question
Find 1-, 2- and 3-week windows in 2027–2029 with **zero** must-hear live sports on Bay Area AM/FM radio,
where "must-hear" = all 30 MLB clubs (Giants/A's ★), all NFL incl. the 49ers ★, Stanford ★ and Cal ★
football, and Westwood One's national NFL broadcasts — verified line-by-line against official schedules,
with anything unreleased clearly labeled an estimate.

## The answer
1. **No strict 7-, 14- or 21-day zero-conflict window exists in 2027, 2028 or 2029.** Baseball hands off
   to football, football hands off to spring training. The longest the dial is ever fully dark is
   **6 consecutive days**, and only in the late-January→mid-February NFL-playoff corridor, in the weekday
   seams between playoff Sundays (Divisional → Conference Championships → Pro Bowl Games → Super Bowl).
2. **2027 windows (computed from official calendars):** Jan 25–30, Feb 1–6, Feb 8–13 (6 days each;
   boundaries estimated except the Super Bowl), plus **Feb 15–18, 2027 (4 days) — the only window verified
   on both sides**: Super Bowl LXI is Sun Feb 14, 2027 (NFL, announced), and MLB's officially released
   2027 schedule starts spring-training games Fri Feb 19, 2027.
3. **2028:** same corridor (~Jan 24–29, ~Jan 31–Feb 5, ~Feb 7–12, ~Feb 14–17 — estimates), **plus a
   conditional 9-day standout, Jul 12–20, 2028**, if MLB finalizes its publicly-envisioned extended
   Olympic break during LA28 (All-Star Game at Oracle Park ~Jul 11; season resuming Jul 21). Not agreed
   with the players' association yet — flagged, scenario-toggled on the site, do not book on it.
4. **2029:** same corridor (~Jan 22–27, ~Jan 29–Feb 3, ~Feb 5–10, ~Feb 12–15 — all estimates; no 2029
   schedules exist yet).
5. **Practical longer trips:** the "Super Bowl sandwich" (2027: Feb 1–13, miss only the Pro Bowl Games
   exhibition, home for the Super Bowl), or Super-Bowl-to-Opening-Day (2027: Feb 15–Mar 24, ~5½ weeks
   with only spring-training exhibitions on air). Engine-ranked least-conflict 7/14/21-day windows for all
   three years are computed live on the Vacation page.

## What was verified (official sources, linked in every site table)
- **MLB 2027 schedule officially released Jul 16, 2026**: ST games Feb 19–Mar 23; Opening Day Mar 25;
  All-Star break dark days Jul 12–14 (ASG Jul 13, Wrigley Field); season ends Sep 26. 2026 anchors also
  verified (Opening Night Mar 25 Yankees @ Giants; season ended Sep 27; WS from Oct 23). **2028 ASG host
  (Oracle Park, SF)** announced Aug 2026. MLB average game **2:38** (2025, MLB official).
- **NFL:** 2026 regular season ends Jan 10, 2027 (per Westwood One's official listings, captured in full —
  ~50 broadcasts Nov 2026–Jan 2027, all on the site in PT). **Super Bowl LXI Sun Feb 14, 2027** (SoFi;
  Westwood One). SB LXII site announced (Atlanta; date expected Feb 13, 2028). NFL avg game ~3:03–3:12.
- **49ers** remaining 2026 dates/kickoffs cross-checked (one 20-min discrepancy flagged).
  **Stanford/Cal** remaining 2026 from official athletics sites (Big Game Nov 21; kickoff TBDs flagged).
  **CFP 2026-27** bracket dates announced (championship Jan 25, 2027, Las Vegas). NCAAF avg game **3:26**.
- **Bay Area radio map (94122):** Giants & 49ers & Westwood One on KNBR 680/104.5 (+49ers on 107.7/810;
  Westwood One overflow KTCT 1050); A's on KNEW 960 (flagship KSTE 650 Sacramento — weak in SF); Stanford
  KTCT 1050; Cal 810 AM; Warriors/Valkyries 95.7; Sharks 98.5; Earthquakes 810/1370; ESPN Radio via KTCT.

## Risks & open items (published on the Flagged for Review page, F-1…F-15)
- The three earlier project sites/repos (ScheduleFreeTime, VacationSchedule, RADIOSF) are **dead (404)**;
  this project was rebuilt from scratch — no prior data survived.
- **MLB CBA expires Dec 1, 2026** — a lockout could shift 2027 spring dates.
- Playoff-round dates, Pro Bowl Games date/carriage, SB LXII/LXIII exact dates, all 2028/29 schedules,
  and 2027 MLB first-pitch/postseason times are unreleased → labeled estimates; the site's engine
  recomputes the moment officials publish.

## Deliverables
GitHub Pages site in `docs/` (Dashboard · day/month Free-Time Scoreboard through Dec 2029 with exact free
windows daily · Vacation rankings incl. scenario toggles · MLB/NFL-Stanford-Cal/Westwood One/Radio
reference tables with source links · Flagged-for-Review page), `research-notes.md` (method & sources),
and `COORDINATION.md` (multi-session task board). Engine validated with an automated Node test run
(all day computations + key anchors asserted).
