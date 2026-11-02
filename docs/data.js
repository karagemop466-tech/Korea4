/*
 * data.js — Bay Area sports-radio schedule model (2026-11-02 .. 2029-12-31)
 * -------------------------------------------------------------------------
 * "Free" (Core 4) = no MLB (any club, incl. spring training/postseason),
 * no NFL (incl. 49ers + Westwood One national NFL), no Stanford NCAAF,
 * no California NCAAF on the radio. SF Giants/Athletics/49ers/Stanford/Cal
 * are flagged high priority (hp). Other sports actually receivable on
 * Bay Area AM/FM (Warriors, Sharks, Valkyries, Earthquakes, CFP on ESPN
 * Radio, Westwood One NCAA, LA28 Olympics) are tier "other" — shown when
 * the "All Bay Area radio sports" toggle is on.
 *
 * Status flags:  st:'V' = verified against an official source (see src).
 *                st:'E' = estimate (schedule not yet released, or a
 *                         time/window modeled from verified patterns).
 * Times are minutes after midnight, Pacific Time.
 * Methodology & sources: ../research-notes.md and the site pages.
 */
'use strict';

/* ---------- date utils (UTC-safe) ---------- */
function dstr(y, m, d){ return y+'-'+String(m).padStart(2,'0')+'-'+String(d).padStart(2,'0'); }
function parseD(s){ const [y,m,d]=s.split('-').map(Number); return new Date(Date.UTC(y,m-1,d)); }
function fmt(d){ return dstr(d.getUTCFullYear(), d.getUTCMonth()+1, d.getUTCDate()); }
function addDays(s,n){ const d=parseD(s); d.setUTCDate(d.getUTCDate()+n); return fmt(d); }
function dow(s){ return parseD(s).getUTCDay(); }               // 0=Sun .. 6=Sat
function between(s,a,b){ return s>=a && s<=b; }
function mm(mins){ const h=Math.floor(mins/60), m=mins%60, ap=h<12?'AM':'PM'; let h12=h%12; if(h12===0)h12=12; return h12+':'+String(m).padStart(2,'0')+' '+ap; }
function hm(h,m){ return h*60+m; }

/* ---------- average game durations (minutes) — sources on index/radio pages ---------- */
const DUR = {
  MLB: 158,      // 2:38 — MLB official, 2025 nine-inning average
  MLB_POST: 180, // postseason estimate (longer breaks)
  ASG: 170, DERBY: 165,
  NFL: 190,      // ~3:10 — 3:03 kickoff-to-final-snap (nflverse timing 2024-25) + buffer
  NFL_PLAYOFF: 195,
  SUPERBOWL: 222,// ~3:42 incl. extended halftime
  CFB: 206,      // 3:26 — FBS average 2025 (NCAA statistics compilation)
  WWO: 215       // Westwood One window from its listed (pregame-inclusive) start time
};

/* ---------- explicit events (verified unless st:'E') ---------- */
/* cat: mlb | nfl | wwo | cfb | cfp ; tier: 'core' counts toward "free", 'other' only in All-Radio mode */
const WWO_SRC='Westwood One official NFL schedule (westwoodonesports.com/nfl-schedule, captured 2026-11-02)';
const SF_SRC='49ers 2026 schedule (49ers.com / NFL; cross-checked vs Westwood One listings)';
const CFB_SRC='Official schedules: gostanford.com & calbears.com (ACC)';
const CFP_SRC='College Football Playoff 2026-27 announced dates (collegefootballplayoff.com)';
const NFL_SRC='NFL (nfl.com)';

const EVENTS = [
/* --- Westwood One NFL 2026 broadcasts (start = listed ET time − 3h; pregame-inclusive) --- */
{d:'2026-11-02',s:hm(16,0),dur:DUR.WWO,cat:'wwo',tier:'core',t:'Westwood One MNF: Chicago Bears @ Seattle Seahawks',st:'V',src:WWO_SRC},
{d:'2026-11-05',s:hm(16,30),dur:DUR.WWO,cat:'wwo',tier:'core',t:'Westwood One Thursday Night Football: Jacksonville Jaguars @ Baltimore Ravens',st:'V',src:WWO_SRC},
{d:'2026-11-07',s:hm(12,0),dur:DUR.WWO,cat:'wwo',tier:'other',t:'Westwood One NCAA Football: Oregon @ Ohio State (not Stanford/Cal)',st:'V',src:WWO_SRC},
{d:'2026-11-08',s:hm(6,15),dur:DUR.WWO,cat:'wwo',tier:'core',t:'Westwood One NFL (Madrid): Cincinnati Bengals vs Atlanta Falcons',st:'V',src:WWO_SRC},
{d:'2026-11-08',s:hm(16,30),dur:DUR.WWO,cat:'wwo',tier:'core',t:'Westwood One SNF: Tampa Bay Buccaneers @ Chicago Bears',st:'V',src:WWO_SRC},
{d:'2026-11-09',s:hm(16,0),dur:DUR.WWO,cat:'wwo',tier:'core',t:'Westwood One MNF: Buffalo Bills @ Minnesota Vikings',st:'V',src:WWO_SRC},
{d:'2026-11-12',s:hm(16,30),dur:DUR.WWO,cat:'wwo',tier:'core',t:'Westwood One Thursday Night Football: Washington Commanders @ New York Giants',st:'V',src:WWO_SRC},
{d:'2026-11-15',s:hm(6,15),dur:DUR.WWO,cat:'wwo',tier:'core',t:'Westwood One NFL (Munich): New England Patriots vs Detroit Lions',st:'V',src:WWO_SRC},
{d:'2026-11-15',s:hm(16,30),dur:DUR.WWO,cat:'wwo',tier:'core',t:'Westwood One SNF: Pittsburgh Steelers @ Cincinnati Bengals',st:'V',src:WWO_SRC},
{d:'2026-11-16',s:hm(16,0),dur:DUR.WWO,cat:'wwo',tier:'core',t:'Westwood One MNF: Los Angeles Chargers @ Baltimore Ravens',st:'V',src:WWO_SRC},
{d:'2026-11-19',s:hm(16,30),dur:DUR.WWO,cat:'wwo',tier:'core',t:'Westwood One Thursday Night Football: Indianapolis Colts @ Houston Texans',st:'V',src:WWO_SRC},
{d:'2026-11-22',s:hm(16,30),dur:DUR.WWO,cat:'wwo',tier:'core',hp:1,t:'Westwood One SNF (Mexico City): Minnesota Vikings vs San Francisco 49ers',st:'V',src:WWO_SRC},
{d:'2026-11-23',s:hm(16,0),dur:DUR.WWO,cat:'wwo',tier:'core',t:'Westwood One MNF: Cincinnati Bengals @ Washington Commanders',st:'V',src:WWO_SRC},
{d:'2026-11-25',s:hm(16,30),dur:DUR.WWO,cat:'wwo',tier:'core',t:'Westwood One "Thanksgiving Wednesday": Green Bay Packers @ Los Angeles Rams',st:'V',src:WWO_SRC},
{d:'2026-11-26',s:hm(9,30),dur:DUR.WWO,cat:'wwo',tier:'core',t:'Westwood One Thanksgiving Tripleheader G1: Chicago Bears @ Detroit Lions',st:'V',src:WWO_SRC},
{d:'2026-11-26',s:hm(13,15),dur:DUR.WWO,cat:'wwo',tier:'core',t:'Westwood One Thanksgiving Tripleheader G2: Philadelphia Eagles @ Dallas Cowboys',st:'V',src:WWO_SRC},
{d:'2026-11-26',s:hm(17,0),dur:DUR.WWO,cat:'wwo',tier:'core',t:'Westwood One Thanksgiving Tripleheader G3: Kansas City Chiefs @ Buffalo Bills',st:'V',src:WWO_SRC},
{d:'2026-11-27',s:hm(11,30),dur:DUR.WWO,cat:'wwo',tier:'core',t:'Westwood One Black Friday: Denver Broncos @ Pittsburgh Steelers',st:'V',src:WWO_SRC},
{d:'2026-11-29',s:hm(16,30),dur:DUR.WWO,cat:'wwo',tier:'core',t:'Westwood One SNF: New England Patriots @ Los Angeles Chargers',st:'V',src:WWO_SRC},
{d:'2026-11-30',s:hm(16,0),dur:DUR.WWO,cat:'wwo',tier:'core',t:'Westwood One MNF: Carolina Panthers @ Tampa Bay Buccaneers',st:'V',src:WWO_SRC},
{d:'2026-12-03',s:hm(16,30),dur:DUR.WWO,cat:'wwo',tier:'core',t:'Westwood One Thursday Night Football: Kansas City Chiefs @ Los Angeles Rams',st:'V',src:WWO_SRC},
{d:'2026-12-06',s:hm(16,30),dur:DUR.WWO,cat:'wwo',tier:'core',t:'Westwood One SNF: Houston Texans @ Pittsburgh Steelers',st:'V',src:WWO_SRC},
{d:'2026-12-07',s:hm(16,0),dur:DUR.WWO,cat:'wwo',tier:'core',t:'Westwood One MNF: Dallas Cowboys @ Seattle Seahawks',st:'V',src:WWO_SRC},
{d:'2026-12-10',s:hm(16,30),dur:DUR.WWO,cat:'wwo',tier:'core',t:'Westwood One Thursday Night Football: Minnesota Vikings @ New England Patriots',st:'V',src:WWO_SRC},
{d:'2026-12-13',s:hm(16,30),dur:DUR.WWO,cat:'wwo',tier:'core',t:'Westwood One SNF: Buffalo Bills @ Green Bay Packers',st:'V',src:WWO_SRC},
{d:'2026-12-14',s:hm(16,0),dur:DUR.WWO,cat:'wwo',tier:'core',t:'Westwood One MNF: Pittsburgh Steelers @ Jacksonville Jaguars',st:'V',src:WWO_SRC},
{d:'2026-12-17',s:hm(16,30),dur:DUR.WWO,cat:'wwo',tier:'core',hp:1,t:'Westwood One Thursday Night Football: San Francisco 49ers @ Los Angeles Chargers',st:'V',src:WWO_SRC},
{d:'2026-12-19',s:hm(13,30),dur:DUR.WWO,cat:'wwo',tier:'core',t:'Westwood One Saturday DH G1: Seattle Seahawks @ Philadelphia Eagles',st:'V',src:WWO_SRC},
{d:'2026-12-19',s:hm(17,0),dur:DUR.WWO,cat:'wwo',tier:'core',t:'Westwood One Saturday DH G2: Chicago Bears @ Buffalo Bills',st:'V',src:WWO_SRC},
{d:'2026-12-20',s:hm(16,30),dur:DUR.WWO,cat:'wwo',tier:'core',t:'Westwood One SNF: Detroit Lions @ Minnesota Vikings',st:'V',src:WWO_SRC},
{d:'2026-12-21',s:hm(16,0),dur:DUR.WWO,cat:'wwo',tier:'core',t:'Westwood One MNF: New England Patriots @ Kansas City Chiefs',st:'V',src:WWO_SRC},
{d:'2026-12-24',s:hm(16,30),dur:DUR.WWO,cat:'wwo',tier:'core',t:'Westwood One Thursday Night Football (Christmas Eve): Houston Texans @ Philadelphia Eagles',st:'V',src:WWO_SRC},
{d:'2026-12-25',s:hm(9,30),dur:DUR.WWO,cat:'wwo',tier:'core',t:'Westwood One Christmas Tripleheader G1: Green Bay Packers @ Chicago Bears',st:'V',src:WWO_SRC},
{d:'2026-12-25',s:hm(13,15),dur:DUR.WWO,cat:'wwo',tier:'core',t:'Westwood One Christmas Tripleheader G2: Buffalo Bills @ Denver Broncos',st:'V',src:WWO_SRC},
{d:'2026-12-25',s:hm(17,0),dur:DUR.WWO,cat:'wwo',tier:'core',t:'Westwood One Christmas Tripleheader G3: Los Angeles Rams @ Seattle Seahawks',st:'V',src:WWO_SRC},
{d:'2026-12-26',s:hm(13,0),dur:DUR.WWO,cat:'wwo',tier:'core',t:'Westwood One Week 16 Saturday DH G1 (teams TBA)',st:'V',src:WWO_SRC},
{d:'2026-12-26',s:hm(17,0),dur:DUR.WWO,cat:'wwo',tier:'core',t:'Westwood One Week 16 Saturday DH G2 (teams TBA)',st:'V',src:WWO_SRC},
{d:'2026-12-27',s:hm(16,30),dur:DUR.WWO,cat:'wwo',tier:'core',t:'Westwood One SNF: Jacksonville Jaguars @ Dallas Cowboys (start time truncated in capture — assumed 7:30 PM ET SNF pattern)',st:'E',src:WWO_SRC},
{d:'2026-12-28',s:hm(16,0),dur:DUR.WWO,cat:'wwo',tier:'core',t:'Westwood One MNF: New York Giants @ Detroit Lions',st:'V',src:WWO_SRC},
{d:'2026-12-31',s:hm(16,30),dur:DUR.WWO,cat:'wwo',tier:'core',t:'Westwood One Thursday Night Football (New Year\'s Eve): Baltimore Ravens @ Cincinnati Bengals',st:'V',src:WWO_SRC},
{d:'2027-01-02',s:hm(13,0),dur:DUR.WWO,cat:'wwo',tier:'core',t:'Westwood One Week 17 Saturday DH G1 (teams TBA)',st:'V',src:WWO_SRC},
{d:'2027-01-02',s:hm(17,0),dur:DUR.WWO,cat:'wwo',tier:'core',t:'Westwood One Week 17 Saturday DH G2 (teams TBA)',st:'V',src:WWO_SRC},
{d:'2027-01-03',s:hm(16,30),dur:DUR.WWO,cat:'wwo',tier:'core',hp:1,t:'Westwood One SNF: Philadelphia Eagles @ San Francisco 49ers',st:'V',src:WWO_SRC},
{d:'2027-01-04',s:hm(16,0),dur:DUR.WWO,cat:'wwo',tier:'core',t:'Westwood One MNF: Houston Texans @ Green Bay Packers',st:'V',src:WWO_SRC},
{d:'2027-01-09',s:hm(9,30),dur:DUR.WWO,cat:'wwo',tier:'core',t:'Westwood One Week 18 Saturday Tripleheader G1 (teams TBA)',st:'V',src:WWO_SRC},
{d:'2027-01-09',s:hm(13,15),dur:DUR.WWO,cat:'wwo',tier:'core',t:'Westwood One Week 18 Saturday Tripleheader G2 (teams TBA)',st:'V',src:WWO_SRC},
{d:'2027-01-09',s:hm(17,0),dur:DUR.WWO,cat:'wwo',tier:'core',t:'Westwood One Week 18 Saturday Tripleheader G3 (teams TBA)',st:'V',src:WWO_SRC},
{d:'2027-01-10',s:hm(16,30),dur:DUR.WWO,cat:'wwo',tier:'core',t:'Westwood One Week 18 SNF (teams TBA) — regular season finale',st:'V',src:WWO_SRC},

/* --- San Francisco 49ers, remaining 2026 (kickoff PT) — HIGH PRIORITY --- */
{d:'2026-11-08',s:hm(13,5),dur:DUR.NFL,cat:'nfl',tier:'core',hp:1,t:'49ers vs Las Vegas Raiders (Levi\'s Stadium) — KNBR 680/104.5, 107.7 [kickoff: 1:05 vs 1:25 PM discrepancy — see Flagged page]',st:'V',src:SF_SRC},
{d:'2026-11-15',s:hm(13,25),dur:DUR.NFL,cat:'nfl',tier:'core',hp:1,t:'49ers @ Dallas Cowboys — KNBR',st:'V',src:SF_SRC},
{d:'2026-11-22',s:hm(17,20),dur:DUR.NFL,cat:'nfl',tier:'core',hp:1,t:'49ers vs Minnesota Vikings (Mexico City, SNF) — KNBR + Westwood One',st:'V',src:SF_SRC},
{d:'2026-11-29',s:hm(13,25),dur:DUR.NFL,cat:'nfl',tier:'core',hp:1,t:'49ers vs Seattle Seahawks — KNBR',st:'V',src:SF_SRC},
{d:'2026-12-06',s:hm(10,0),dur:DUR.NFL,cat:'nfl',tier:'core',hp:1,t:'49ers @ New York Giants — KNBR',st:'V',src:SF_SRC},
{d:'2026-12-13',s:hm(13,25),dur:DUR.NFL,cat:'nfl',tier:'core',hp:1,t:'49ers vs Los Angeles Rams — KNBR',st:'V',src:SF_SRC},
{d:'2026-12-17',s:hm(17,15),dur:DUR.NFL,cat:'nfl',tier:'core',hp:1,t:'49ers @ Los Angeles Chargers (Thursday Night Football) — KNBR + Westwood One',st:'V',src:SF_SRC},
{d:'2026-12-27',s:hm(13,25),dur:DUR.NFL,cat:'nfl',tier:'core',hp:1,t:'49ers @ Kansas City Chiefs — KNBR',st:'V',src:SF_SRC},
{d:'2027-01-03',s:hm(17,20),dur:DUR.NFL,cat:'nfl',tier:'core',hp:1,t:'49ers vs Philadelphia Eagles (SNF) — KNBR + Westwood One',st:'V',src:SF_SRC},

/* --- Stanford & California, remaining 2026 — HIGH PRIORITY (dates verified; TBD kickoffs modeled) --- */
{d:'2026-11-14',s:hm(12,30),dur:DUR.CFB,cat:'cfb',tier:'core',hp:1,t:'California @ Virginia — Cal Bears Sports Network, 810 AM (12:30 PM PT kickoff listed by Cal)',st:'V',src:CFB_SRC},
{d:'2026-11-14',s:hm(12,30),dur:DUR.CFB,cat:'cfb',tier:'core',hp:1,t:'Stanford @ Virginia Tech — KTCT 1050 AM (kickoff TBD; modeled 12:30 PM PT)',st:'E',src:CFB_SRC},
{d:'2026-11-21',s:hm(13,0),dur:DUR.CFB,cat:'cfb',tier:'core',hp:1,t:'129th BIG GAME: Stanford @ California (Berkeley) — 810 AM / KTCT 1050 (kickoff TBD; modeled 1:00 PM PT)',st:'E',src:CFB_SRC},
{d:'2026-11-28',s:hm(12,30),dur:DUR.CFB,cat:'cfb',tier:'core',hp:1,t:'SMU @ Stanford (regular-season finale) — KTCT 1050 (kickoff TBD; modeled 12:30 PM PT)',st:'E',src:CFB_SRC},
{d:'2026-11-28',s:hm(12,30),dur:DUR.CFB,cat:'cfb',tier:'core',hp:1,t:'Pittsburgh @ California (regular-season finale) — 810 AM (kickoff TBD; modeled 12:30 PM PT)',st:'E',src:CFB_SRC},

/* --- College Football Playoff 2026-27 (ESPN Radio → KTCT 1050) — tier "other": not Stanford/Cal --- */
{d:'2026-12-18',s:hm(17,0),dur:DUR.CFB,cat:'cfp',tier:'other',t:'CFP First Round (campus game) — ESPN Radio',st:'V',src:CFP_SRC},
{d:'2026-12-19',s:hm(9,0),dur:660,cat:'cfp',tier:'other',t:'CFP First Round — 3 campus games across the day — ESPN Radio (kickoff times est.)',st:'E',src:CFP_SRC},
{d:'2026-12-30',s:hm(16,30),dur:DUR.CFB,cat:'cfp',tier:'other',t:'CFP Quarterfinal: Fiesta Bowl — ESPN Radio (time est.)',st:'E',src:CFP_SRC},
{d:'2027-01-01',s:hm(9,30),dur:660,cat:'cfp',tier:'other',t:'CFP Quarterfinals: Cotton, Rose & Peach Bowls — ESPN Radio (times est.)',st:'E',src:CFP_SRC},
{d:'2027-01-14',s:hm(16,30),dur:DUR.CFB,cat:'cfp',tier:'other',t:'CFP Semifinal: Orange Bowl (7:30 PM ET) — ESPN Radio',st:'V',src:CFP_SRC},
{d:'2027-01-15',s:hm(16,30),dur:DUR.CFB,cat:'cfp',tier:'other',t:'CFP Semifinal: Sugar Bowl (7:30 PM ET) — ESPN Radio',st:'V',src:CFP_SRC},
{d:'2027-01-25',s:hm(16,30),dur:DUR.CFB,cat:'cfp',tier:'other',t:'CFP National Championship, Las Vegas (7:30 PM ET) — ESPN Radio',st:'V',src:CFP_SRC},

/* --- Super Bowls (Westwood One radio) --- */
{d:'2027-02-14',s:hm(15,30),dur:DUR.SUPERBOWL,cat:'nfl',tier:'core',hp:1,t:'Super Bowl LXI, SoFi Stadium, Inglewood (6:30 PM ET) — Westwood One on KNBR',st:'V',src:NFL_SRC+' (host/date announced); Westwood One is NFL national radio partner'},
{d:'2028-02-13',s:hm(15,30),dur:DUR.SUPERBOWL,cat:'nfl',tier:'core',hp:1,t:'Super Bowl LXII, Atlanta — Westwood One (site announced by NFL Oct 2024; exact date expected, not yet officially published)',st:'E',src:NFL_SRC},
{d:'2029-02-11',s:hm(15,30),dur:DUR.SUPERBOWL,cat:'nfl',tier:'core',hp:1,t:'Super Bowl LXIII — Westwood One (Las Vegas reported by secondary sources only; date from 2nd-Sunday-of-Feb pattern) — UNVERIFIED site',st:'E',src:'Pattern estimate — see Flagged page'},

/* --- MLB single-day anchors --- */
{d:'2027-03-24',s:hm(17,0),dur:DUR.MLB,cat:'mlb',tier:'core',t:'MLB Opening Night 2027 — single standalone game (teams/stream TBD; time est.)',st:'E',src:'MLB 2027 schedule release (mlb.com), Jul 16 2026'},
{d:'2027-07-12',s:hm(17,0),dur:DUR.DERBY,cat:'mlb',tier:'core',t:'MLB Home Run Derby, Wrigley Field — exhibition, on ESPN Radio',st:'V',src:'MLB (mlb.com)'},
{d:'2027-07-13',s:hm(17,5),dur:DUR.ASG,cat:'mlb',tier:'core',t:'97th MLB All-Star Game, Wrigley Field — exhibition, on ESPN Radio',st:'V',src:'MLB (mlb.com)'},
{d:'2027-07-15',s:hm(16,0),dur:DUR.MLB,cat:'mlb',tier:'core',t:'MLB standalone second-half opener (single game; time est.)',st:'E',src:'MLB 2027 schedule release coverage'},
{d:'2028-07-10',s:hm(17,0),dur:DUR.DERBY,cat:'mlb',tier:'core',t:'MLB Home Run Derby (est. date), Oracle Park, San Francisco',st:'E',src:'MLB announced SF as 2028 ASG host (date tentative)'},
{d:'2028-07-11',s:hm(17,5),dur:DUR.ASG,cat:'mlb',tier:'core',t:'98th MLB All-Star Game (est. date), Oracle Park, San Francisco',st:'E',src:'MLB announced SF as 2028 ASG host (date tentative)'},
{d:'2029-07-09',s:hm(17,0),dur:DUR.DERBY,cat:'mlb',tier:'core',t:'MLB Home Run Derby (pattern estimate; host not announced)',st:'E',src:'Pattern estimate — see Flagged page'},
{d:'2029-07-10',s:hm(17,5),dur:DUR.ASG,cat:'mlb',tier:'core',t:'99th MLB All-Star Game (pattern estimate; host not announced)',st:'E',src:'Pattern estimate — see Flagged page'}
];

/* NFL playoff windows: pattern estimates (NFL publishes exact dates with each season's schedule / during season) */
const PLAYOFF_ESTS = [
 // [date, starts[], dur, label]
 ['2027-01-16',[hm(13,30),hm(17,0)],DUR.NFL_PLAYOFF,'NFL Wild Card Saturday (2 games, est. times) — Westwood One'],
 ['2027-01-17',[hm(10,0),hm(13,30),hm(17,15)],DUR.NFL_PLAYOFF,'NFL Wild Card Sunday (3 games, est. times) — Westwood One'],
 ['2027-01-18',[hm(17,15)],DUR.NFL_PLAYOFF,'NFL Wild Card Monday (est.) — Westwood One'],
 ['2027-01-23',[hm(13,30),hm(17,15)],DUR.NFL_PLAYOFF,'NFL Divisional Saturday (est.) — Westwood One'],
 ['2027-01-24',[hm(12,0),hm(15,30)],DUR.NFL_PLAYOFF,'NFL Divisional Sunday (est.) — Westwood One'],
 ['2027-01-31',[hm(12,0),hm(15,30)],DUR.NFL_PLAYOFF,'NFL Conference Championships (est.) — Westwood One'],
 ['2027-02-07',[hm(12,0)],180,'NFL Pro Bowl Games (est. weekend — date not announced) — Westwood One'],
 ['2028-01-15',[hm(13,30),hm(17,0)],DUR.NFL_PLAYOFF,'NFL Wild Card Saturday (pattern est.) — Westwood One'],
 ['2028-01-16',[hm(10,0),hm(13,30),hm(17,15)],DUR.NFL_PLAYOFF,'NFL Wild Card Sunday (pattern est.) — Westwood One'],
 ['2028-01-17',[hm(17,15)],DUR.NFL_PLAYOFF,'NFL Wild Card Monday (pattern est.) — Westwood One'],
 ['2028-01-22',[hm(13,30),hm(17,15)],DUR.NFL_PLAYOFF,'NFL Divisional Saturday (pattern est.) — Westwood One'],
 ['2028-01-23',[hm(12,0),hm(15,30)],DUR.NFL_PLAYOFF,'NFL Divisional Sunday (pattern est.) — Westwood One'],
 ['2028-01-30',[hm(12,0),hm(15,30)],DUR.NFL_PLAYOFF,'NFL Conference Championships (pattern est.) — Westwood One'],
 ['2028-02-06',[hm(12,0)],180,'NFL Pro Bowl Games (pattern est.) — Westwood One'],
 ['2029-01-13',[hm(13,30),hm(17,0)],DUR.NFL_PLAYOFF,'NFL Wild Card Saturday (pattern est.) — Westwood One'],
 ['2029-01-14',[hm(10,0),hm(13,30),hm(17,15)],DUR.NFL_PLAYOFF,'NFL Wild Card Sunday (pattern est.) — Westwood One'],
 ['2029-01-15',[hm(17,15)],DUR.NFL_PLAYOFF,'NFL Wild Card Monday (pattern est.) — Westwood One'],
 ['2029-01-20',[hm(13,30),hm(17,15)],DUR.NFL_PLAYOFF,'NFL Divisional Saturday (pattern est.) — Westwood One'],
 ['2029-01-21',[hm(12,0),hm(15,30)],DUR.NFL_PLAYOFF,'NFL Divisional Sunday (pattern est.) — Westwood One'],
 ['2029-01-28',[hm(12,0),hm(15,30)],DUR.NFL_PLAYOFF,'NFL Conference Championships (pattern est.) — Westwood One'],
 ['2029-02-04',[hm(12,0)],180,'NFL Pro Bowl Games (pattern est.) — Westwood One']
];
for (const [dt,starts,dur,label] of PLAYOFF_ESTS)
  for (const s of starts)
    EVENTS.push({d:dt,s:s,dur:dur,cat:'nfl',tier:'core',t:label,st:'E',src:'Pattern estimate — NFL has not published these dates yet'});

/* ---------- season pattern rules ---------- */
/* MLB: st = spring training games; rs = regular season; dark = ASB no-game days; post = postseason ranges */
const MLB_SEASONS = [
 {yr:2027, st:['2027-02-19','2027-03-23'], rs:['2027-03-24','2027-09-26'], dark:['2027-07-12','2027-07-13','2027-07-14'], solo:'2027-07-15',
  post:[['2027-09-28','2027-10-30']], statusST:'V', statusRS:'V',
  note:'2027 schedule officially released Jul 16, 2026 (times mostly TBD). Postseason dates are estimates.'},
 {yr:2028, st:['2028-02-18','2028-03-28'], rs:['2028-03-30','2028-10-01'], dark:['2028-07-10','2028-07-11','2028-07-12'], solo:'2028-07-13',
  post:[['2028-10-03','2028-11-04']], statusST:'E', statusRS:'E',
  note:'2028 schedule NOT released (expected ~Jul 2027) — pattern estimate. If MLB finalizes the extended Olympic break, Jul 10–20 goes dark except the ASG (scenario toggle).'},
 {yr:2029, st:['2029-02-16','2029-03-27'], rs:['2029-03-29','2029-09-30'], dark:['2029-07-09','2029-07-10','2029-07-11'], solo:'2029-07-12',
  post:[['2029-10-02','2029-11-03']], statusST:'E', statusRS:'E',
  note:'2029 schedule NOT released (expected ~Jul 2028) — pattern estimate.'}
];
/* typical union window (all 30 clubs) by weekday — labeled estimate in UI */
const MLB_SLATE = {0:[hm(10,5),hm(19,0)],1:[hm(15,35),hm(22,0)],2:[hm(15,35),hm(22,0)],3:[hm(9,35),hm(22,0)],4:[hm(9,35),hm(22,0)],5:[hm(15,35),hm(22,0)],6:[hm(10,5),hm(22,0)]};
const MLB_ST_WINDOW = [hm(10,0),hm(16,30)];     // spring training typical (FL 1:05 ET & AZ 1:05 MT starts)
const MLB_POST_WINDOW = [hm(13,5),hm(21,0)];    // postseason typical
const OLY28_DARK = ['2028-07-12','2028-07-13','2028-07-14','2028-07-15','2028-07-16','2028-07-17','2028-07-18','2028-07-19','2028-07-20'];

function mlbDay(s, oly28){
  for (const S of MLB_SEASONS){
    if (between(s,S.st[0],S.st[1]))
      return [{s:MLB_ST_WINDOW[0],e:MLB_ST_WINDOW[1],cat:'mlb',tier:'core',st:S.statusST,
               t:'MLB Spring Training games (AZ/FL) — Giants select games on KNBR; window estimated',src:'MLB spring schedule (mlb.com)'}];
    if (between(s,S.rs[0],S.rs[1])){
      if (S.dark.includes(s)) return [];                       // ASB dark (Derby/ASG are EVENTS)
      if (oly28 && S.yr===2028 && OLY28_DARK.includes(s)) return []; // conditional Olympic break scenario
      if (s===S.solo) return [];                               // solo game is an EVENT (or est. single game)
      const w=MLB_SLATE[dow(s)];
      return [{s:w[0],e:w[1],cat:'mlb',tier:'core',st:'E',
               t:'MLB regular-season slate — typical union window, all 30 clubs (first pitch→last out, PT; estimated). Giants on KNBR 680/104.5 ★, A\'s on KNEW 960 ★',
               src:'MLB schedule (mlb.com)'}];
    }
    for (const p of S.post)
      if (between(s,p[0],p[1]))
        return [{s:MLB_POST_WINDOW[0],e:MLB_POST_WINDOW[1],cat:'mlb',tier:'core',st:'E',
                 t:'MLB Postseason window (WC→World Series; games most days — exact dates announced each August; ESPN Radio → KTCT 1050)',
                 src:'MLB postseason (mlb.com)'}];
  }
  return [];
}

/* NFL season pattern: Sundays full days; Thu/Mon nights; special blocks */
const NFL_SEASONS = [
 {label:'2026', st:'V', sundays:['2026-09-13','2027-01-10'], tnf:[], mnf:[], preseason:null},        // Thu/Mon captured as Westwood One EVENTS
 {label:'2027', st:'E', sundays:['2027-09-12','2028-01-09'], tnf:['2027-09-16','2028-01-06'], mnf:['2027-09-13','2028-01-03'], preseason:['2027-08-05','2027-08-29']},
 {label:'2028', st:'E', sundays:['2028-09-10','2029-01-07'], tnf:['2028-09-14','2028-12-28'], mnf:['2028-09-11','2029-01-01'], preseason:['2028-08-03','2028-08-27']},
 {label:'2029', st:'E', sundays:['2029-09-09','2030-01-06'], tnf:['2029-09-13','2029-12-27'], mnf:['2029-09-10','2029-12-31'], preseason:['2029-08-02','2029-08-26']}
];
const NFL_SPECIAL = { // all-day / extra blocks (estimates for 2027+, pattern-based)
 '2027-09-09':[[hm(17,20),hm(20,30)],'NFL Kickoff Game (pattern est.: Thursday after Labor Day) — Westwood One'],
 '2027-11-25':[[hm(9,30),hm(20,35)],'NFL Thanksgiving tripleheader (pattern est.) — Westwood One'],
 '2027-11-26':[[hm(12,0),hm(15,30)],'NFL Black Friday game (pattern est.) — Westwood One'],
 '2027-12-25':[[hm(9,30),hm(20,35)],'NFL Christmas Day games (pattern est.) — Westwood One'],
 '2028-01-08':[[hm(9,30),hm(20,35)],'NFL Week 18 Saturday games (pattern est.) — Westwood One'],
 '2028-09-07':[[hm(17,20),hm(20,30)],'NFL Kickoff Game (pattern est.) — Westwood One'],
 '2028-11-23':[[hm(9,30),hm(20,35)],'NFL Thanksgiving tripleheader (pattern est.) — Westwood One'],
 '2028-11-24':[[hm(12,0),hm(15,30)],'NFL Black Friday game (pattern est.) — Westwood One'],
 '2028-12-25':[[hm(9,30),hm(20,35)],'NFL Christmas Day games (pattern est.) — Westwood One'],
 '2029-01-06':[[hm(9,30),hm(20,35)],'NFL Week 18 Saturday games (pattern est.) — Westwood One'],
 '2029-09-06':[[hm(17,20),hm(20,30)],'NFL Kickoff Game (pattern est.) — Westwood One'],
 '2029-11-22':[[hm(9,30),hm(20,35)],'NFL Thanksgiving tripleheader (pattern est.) — Westwood One'],
 '2029-11-23':[[hm(12,0),hm(15,30)],'NFL Black Friday game (pattern est.) — Westwood One'],
 '2029-12-25':[[hm(9,30),hm(20,35)],'NFL Christmas Day games (pattern est.) — Westwood One']
};
function nflDay(s){
  const out=[], w=dow(s);
  if (NFL_SPECIAL[s]){ const [win,label]=NFL_SPECIAL[s]; out.push({s:win[0],e:win[1],cat:'nfl',tier:'core',st:'E',t:label,src:'NFL pattern estimate'}); }
  for (const S of NFL_SEASONS){
    if (w===0 && between(s,S.sundays[0],S.sundays[1]))
      out.push({s:hm(9,30),e:hm(20,45),cat:'nfl',tier:'core',st:S.st,t:'NFL Sunday (10 AM window → Sunday Night Football). 49ers ★ on KNBR 680/104.5 & 107.7; national SNF on Westwood One',src:'NFL (nfl.com); KNBR also carries Sports USA Radio Sunday games'});
    if (w===4 && S.tnf.length && between(s,S.tnf[0],S.tnf[1]))
      out.push({s:hm(16,30),e:hm(20,45),cat:'wwo',tier:'core',st:S.st,t:'Westwood One Thursday Night Football (pattern est. window)',src:'Westwood One (westwoodonesports.com)'});
    if (w===1 && S.mnf.length && between(s,S.mnf[0],S.mnf[1]))
      out.push({s:hm(16,0),e:hm(20,15),cat:'wwo',tier:'core',st:S.st,t:'Westwood One Monday Night Football (pattern est. window)',src:'Westwood One (westwoodonesports.com)'});
    if (S.preseason && between(s,S.preseason[0],S.preseason[1]) && (w===4||w===5||w===6||w===0))
      out.push({s:hm(13,0),e:hm(20,30),cat:'nfl',tier:'core',st:'E',t:'NFL preseason weekend (pattern est. window) — 49ers ★ preseason on KNBR; select national games on Westwood One',src:'NFL pattern estimate'});
  }
  return out;
}

/* Stanford/Cal pattern seasons (2026 remainder is in EVENTS; 2027+ Saturdays estimated; bye weeks TBD) */
const CFB_SEASONS = [
 {yr:2027, sat:['2027-08-28','2027-11-27'], big:'2027-11-20'},
 {yr:2028, sat:['2028-08-26','2028-11-25'], big:'2028-11-18'},
 {yr:2029, sat:['2029-08-25','2029-11-24'], big:'2029-11-17'}
];
function cfbDay(s){
  for (const S of CFB_SEASONS){
    if (dow(s)===6 && between(s,S.sat[0],S.sat[1])){
      const big = (s===S.big) ? ' incl. BIG GAME (est. date)' : '';
      return [{s:hm(12,0),e:hm(22,30),cat:'cfb',tier:'core',hp:1,st:'E',
               t:'Stanford / California game Saturday'+big+' (ACC schedules release ~Jan; kickoffs TBD → modeled window; ~2 of these Saturdays will be double-bye/dark). Stanford: KTCT 1050 ★ · Cal: 810 AM ★',
               src:CFB_SRC}];
    }
  }
  return [];
}

/* ---------- advisory "other Bay Area radio sports" (season presence, not hard windows) ---------- */
function advisories(s){
  const out=[], m=parseD(s).getUTCMonth()+1, d=parseD(s).getUTCDate(), w=dow(s);
  const yr=parseD(s).getUTCFullYear();
  // Warriors (NBA, 95.7 The Game): late Oct – mid Apr regular season; playoffs through June
  if ((m===10&&d>=20)||m===11||m===12||m<=3||(m===4&&d<=12)) out.push({t:'Golden State Warriors — NBA season (95.7 The Game). Games ~every other day; check the day\'s NBA schedule.',st:'V'});
  else if ((m===4&&d>12)||m===5||(m===6&&d<=20)) out.push({t:'NBA Playoffs window — Warriors possible (95.7 The Game); also national NBA on ESPN Radio.',st:'E'});
  // Sharks (NHL, 98.5 KFOX): early Oct – mid Apr
  if ((m===10&&d>=7)||m===11||m===12||m<=3||(m===4&&d<=16)) out.push({t:'San Jose Sharks — NHL season (98.5 KFOX, San Jose — fair signal in SF).',st:'V'});
  else if ((m===4&&d>16)||m===5||(m===6&&d<=24)) out.push({t:'NHL Stanley Cup Playoffs window (98.5 KFOX).',st:'E'});
  // Valkyries (WNBA, 95.7 home games): mid-May – late Sep (+Oct playoffs)
  if ((m===5&&d>=15)||(m>=6&&m<=8)||(m===9)||(m===10&&d<=15)) out.push({t:'Golden State Valkyries — WNBA season (home games on 95.7 The Game).',st:'V'});
  // Earthquakes (MLS, 810 English / 1370 Spanish): late Feb – Oct, mostly Saturdays
  if (w===6 && ((m===2&&d>=21)||(m>=3&&m<=9)||(m===10&&d<=18))) out.push({t:'San Jose Earthquakes likely Saturday MLS match (810 AM English, 1370 AM Spanish).',st:'E'});
  // Westwood One March Madness (NCAA Basketball): mid-Mar – early Apr evenings/weekends
  if ((m===3&&d>=15)||(m===4&&d<=8)) out.push({t:'NCAA Tournament "March Madness" radio — Westwood One on KNBR/KTCT (evenings & weekends).',st:'E'});
  // LA28 Olympics
  if (between(s,'2028-07-14','2028-07-30')) out.push({t:'LA28 Olympic Games (Jul 14–30, 2028) — daily coverage incl. radio (Westwood One is an Olympics audio partner).',st:'V'});
  // College bowl season overall
  if (between(s,yr+'-12-12',yr+'-12-31')||(m===1&&d<=10)) out.push({t:'NCAA bowl season — a Stanford or Cal bowl game is possible (teams/dates announced early Dec). Bowls on ESPN Radio (KTCT).',st:'E'});
  // ACC Championship weekend note
  if ((s==='2026-12-05'||s==='2027-12-04'||s==='2028-12-02'||s==='2029-12-01')) out.push({t:'ACC Football Championship, Charlotte — busy only if Stanford or Cal qualifies.',st:'E'});
  return out;
}

/* ---------- engine ---------- */
function dayBlocks(s, opts){
  opts = opts||{}; const includeOther = !!opts.other; const oly28 = !!opts.oly28;
  let blocks = EVENTS.filter(e=>e.d===s).map(e=>({s:e.s,e:e.s+e.dur,cat:e.cat,tier:e.tier,hp:!!e.hp,st:e.st,t:e.t,src:e.src}));
  blocks = blocks.concat(mlbDay(s,oly28), nflDay(s), cfbDay(s));
  if (!includeOther) blocks = blocks.filter(b=>b.tier==='core');
  blocks.sort((a,b)=>a.s-b.s);
  return blocks;
}
function mergeBlocks(blocks){
  const ints = blocks.map(b=>[Math.max(0,b.s),Math.min(1440,b.e)]).sort((a,b)=>a[0]-b[0]);
  const out=[];
  for (const [a,b] of ints){
    if (out.length && a<=out[out.length-1][1]) out[out.length-1][1]=Math.max(out[out.length-1][1],b);
    else out.push([a,b]);
  }
  return out;
}
function busyMinutes(s,opts){ return mergeBlocks(dayBlocks(s,opts)).reduce((n,[a,b])=>n+(b-a),0); }
function freeWindows(s,opts){
  const merged=mergeBlocks(dayBlocks(s,opts)); const free=[]; let cur=hm(6,0);
  for (const [a,b] of merged){
    if (a>cur) free.push([Math.max(cur,hm(6,0)),Math.min(a,1440)]);
    cur=Math.max(cur,b);
  }
  if (cur<1440) free.push([Math.max(cur,hm(6,0)),1440]);
  return free.filter(([a,b])=>b-a>0);
}
function classify(s,opts){
  const busy=busyMinutes(s,opts);
  if (busy===0) return 'free';
  if (busy<=210) return 'light';
  return 'busy';
}
function rangeStats(a,b,opts){ // whole-day stats between two date strings inclusive
  let s=a, days=0, free=0, light=0, busyMin=0;
  while (s<=b){ const c=classify(s,opts); if(c==='free')free++; else if(c==='light')light++; busyMin+=busyMinutes(s,opts); days++; s=addDays(s,1); }
  return {days:days,free:free,light:light,busyMin:busyMin};
}
function findStreaks(a,b,minLen,opts){
  let s=a, cur=null; const out=[];
  while (s<=b){
    if (classify(s,opts)==='free'){ if(!cur)cur={start:s,end:s,len:1}; else {cur.end=s;cur.len++;} }
    else { if(cur&&cur.len>=minLen)out.push(cur); cur=null; }
    s=addDays(s,1);
  }
  if (cur&&cur.len>=minLen)out.push(cur);
  return out.sort((x,y)=>y.len-x.len);
}
function bestWindows(a,b,len,opts,topN){ // sliding window with fewest Core-4 busy minutes
  const days=[]; let s=a;
  while (s<=b){ days.push({d:s,m:busyMinutes(s,opts)}); s=addDays(s,1); }
  const res=[];
  for (let i=0;i+len<=days.length;i++){
    let sum=0, freeDays=0, lightDays=0;
    for (let j=i;j<i+len;j++){ sum+=days[j].m; if(days[j].m===0)freeDays++; else if(days[j].m<=210)lightDays++; }
    res.push({start:days[i].d,end:days[i+len-1].d,busyMin:sum,freeDays:freeDays,lightDays:lightDays});
  }
  res.sort((x,y)=>x.busyMin-y.busyMin || x.start.localeCompare(y.start));
  // de-dup overlapping picks: keep top picks at least 'len' days apart
  const picked=[];
  for (const r of res){ if (picked.length>=topN)break; if (picked.every(p=>Math.abs((parseD(p.start)-parseD(r.start))/86400000)>=len)) picked.push(r); }
  return picked;
}

const CAT_LABEL = {mlb:'MLB',nfl:'NFL',wwo:'Westwood One NFL',cfb:'Stanford/Cal',cfp:'College Football Playoff'};
const MODEL_START='2026-11-02', MODEL_END='2029-12-31';
const TODAY = (()=>{ const n=new Date(); return dstr(n.getFullYear(), n.getMonth()+1, n.getDate()); })();
