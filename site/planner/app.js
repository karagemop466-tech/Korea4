import {ZONE, addDays, buildIndex, dayBounds, dayLabel, findCandidates, intervalFor, pacificDay, summarizeDay, timeLabel, zoneLabel} from './core.js';

const root = new URL(document.body.dataset.root || './', location.href);
const path = p => new URL(p, root).href;
const page = document.body.dataset.page || 'overview';
const initialFilter = document.body.dataset.filter || 'all';
const $ = (selector, context = document) => context.querySelector(selector);
const esc = value => String(value ?? '').replace(/[&<>"']/g, c => ({'&':'&amp;', '<':'&lt;', '>':'&gt;', '"':'&quot;', "'":'&#39;'}[c]));
const external = (url, text = 'Official source') => `<a href="${esc(url)}" target="_blank" rel="noopener noreferrer">${esc(text)} <span aria-hidden="true">↗</span></a>`;
const navLink = (label, url, selected) => `<a class="${selected ? 'active' : ''}" href="${path(url)}"${selected ? ' aria-current="page"' : ''}>${label}</a>`;
const arrow = '<span aria-hidden="true">↗</span>';
const icon = (name, size = 20) => {
  const shapes = {
    calendar: '<rect x="3" y="5" width="18" height="16" rx="2"/><path d="M7 3v4m10-4v4M3 10h18"/>',
    spark: '<path d="M12 3l1.8 5.8L20 11l-6.2 2.2L12 19l-1.8-5.8L4 11l6.2-2.2L12 3z"/>',
    radio: '<rect x="3" y="7" width="18" height="13" rx="2"/><path d="M6 7l12-4M7 11h6m-6 3h6"/><circle cx="17" cy="14" r="2"/>',
    shield: '<path d="M12 3l7 3v5c0 4.5-3 7.7-7 10-4-2.3-7-5.5-7-10V6l7-3z"/><path d="M9 12l2 2 4-4"/>',
    clock: '<circle cx="12" cy="12" r="9"/><path d="M12 7v5l3 2"/>',
    left: '<path d="M15 18l-6-6 6-6"/>', right: '<path d="M9 18l6-6-6-6"/>'
  };
  return `<svg width="${size}" height="${size}" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">${shapes[name] || ''}</svg>`;
};
const nav = () => `<header class="topbar"><div class="wrap top-inner">
  <a class="brand" href="${path('index.html')}" aria-label="Free Time home"><span class="brand-mark"><span></span><span></span></span><span><strong>FREE TIME</strong><small>VACATION PLANNER</small></span></a>
  <button class="menu-toggle" id="menu-toggle" aria-expanded="false" aria-controls="main-nav">Menu <span>☰</span></button>
  <nav id="main-nav" aria-label="Main navigation">
    ${navLink('Overview', 'index.html', page === 'overview')}
    ${navLink('Calendar', 'site/planner/calendar.html', page === 'calendar')}
    ${navLink('Vacation windows', 'site/planner/vacation.html', page === 'vacation')}
    ${navLink('Radio guide', 'site/planner/radio.html', page === 'radio')}
    ${navLink('Review', 'site/planner/review.html', page === 'review')}
  </nav><div class="top-zone"><span class="dot"></span> PACIFIC TIME <span class="zone-name">${zoneLabel()}</span></div>
</div></header>`;
const footer = () => `<footer class="footer"><div class="wrap footer-inner"><div><a class="footer-brand" href="${path('index.html')}">FREE TIME <span>✳</span></a><p>A little more room for time away.<br>Made for the Outer Sunset, San Francisco.</p></div><div class="footer-links"><a href="${path('site/planner/methodology.html')}">How it works</a><a href="${path('site/planner/review.html')}">Flagged for review</a><a href="${path('site/planner/radio.html')}">Radio guide</a><a href="https://github.com/karagemop466-tech/Korea4" target="_blank" rel="noopener noreferrer">GitHub ↗</a></div><div class="footer-note">Schedules change. Reception and local carriage are not guaranteed.<br><span>Times use America/Los_Angeles, including daylight saving.</span></div></div></footer>`;

let data, index, selectedDay, filter = initialFilter;
const today = pacificDay(Date.now());
const initialDate = new URLSearchParams(location.search).get('date');
const validDate = value => /^202[6-9]-\d{2}-\d{2}$/.test(value || '') && !Number.isNaN(Date.parse(`${value}T12:00:00Z`)) && addDays(value, 0) === value;
selectedDay = validDate(initialDate) ? initialDate : (today >= '2026-01-01' && today <= '2029-12-31' ? today : '2026-11-02');

function sourceFreshness() {
  const failed = Object.entries(data.sources || {}).filter(([, s]) => !s.ok);
  const hours = (Date.now() - Date.parse(data.generatedAt)) / 3_600_000;
  if (failed.length) return `${failed.length} source${failed.length === 1 ? '' : 's'} need attention`;
  if (hours > 72) return 'Snapshot is more than 3 days old';
  return 'Sources checked';
}
function updatedText() {
  return new Intl.DateTimeFormat('en-US', {timeZone: ZONE, month:'short', day:'numeric', year:'numeric', hour:'numeric', minute:'2-digit', timeZoneName:'short'}).format(new Date(data.generatedAt));
}
function eventMatches(e, selected) {
  if (selected === 'all') return true;
  if (selected === 'local') return e.priority && e.group !== 'restriction';
  if (selected === 'college') return e.sport === 'NCAAF';
  if (selected === 'westwood') return e.group === 'westwood';
  if (selected === 'mlb') return e.sport === 'MLB';
  if (selected === 'nfl') return e.sport === 'NFL';
  if (selected === 'other') return ['NBA', 'WNBA', 'NCAAM', 'MLS'].includes(e.sport);
  return true;
}
function sportLabel(e) {
  return ({MLB:'MLB', NFL:'NFL', NCAAF:'COLLEGE', NCAAM:'COLLEGE HOOPS', RADIO:'WESTWOOD', NBA:'NBA', WNBA:'WNBA', MLS:'SOCCER', REVIEW:'REVIEW'})[e.sport] || esc(e.sport || 'EVENT');
}
const clockWithZone = ms => `${timeLabel(ms)} ${zoneLabel(ms)}`;
function eventDetail(e, day) {
  if (e.group === 'restriction') return e.note || 'The official date or time has not been assigned.';
  if (!e.start) {
    const displaced = e.date && e.date !== day ? `Source date ${dayLabel(e.date, {month:'short', day:'numeric'})}; Pacific date or time TBD` : (e.dateBasis || 'Time TBD');
    return `${displaced} · local radio ${e.radio === 'affiliate-unconfirmed' ? 'affiliate unconfirmed' : 'carriage unconfirmed'}`;
  }
  const t = intervalFor(e);
  const end = t?.end ? clockWithZone(t.end) + (pacificDay(t.end) !== day ? ' next day' : '') : '';
  const endNote = e.group === 'westwood' ? (end ? `network slot to ${end}` : 'network end TBD') : (end ? `estimated end ${end}` : 'end TBD');
  let radio = 'local carriage unconfirmed';
  if (e.radio === 'team-network') radio = 'team radio network; check game';
  if (e.radio === 'announced-station' && e.station) radio = `announced ${e.station}`;
  if (e.radio === 'affiliate-unconfirmed') radio = 'local affiliate unconfirmed';
  return `${e.group === 'westwood' ? 'Network airtime' : 'Start'} · ${endNote} · ${radio}`;
}
function eventRows(events, day, max = Infinity) {
  const sorted = [...events].sort((a,b) => (a.start ? Date.parse(a.start) : -1) - (b.start ? Date.parse(b.start) : -1) || a.title.localeCompare(b.title));
  return sorted.slice(0, max).map(e => `<div class="event-row">
    <div class="event-time">${e.start ? esc(clockWithZone(Date.parse(e.start))) : '<span class="tbd">TIME TBD</span>'}</div>
    <div class="event-main"><div class="event-title">${esc(e.title)} ${e.priority && e.group !== 'restriction' ? '<span class="priority-star" title="Priority team or network">✦</span>' : ''}</div><div class="event-sub">${esc(eventDetail(e, day))}</div></div>
    <div class="event-aside"><span class="sport-chip ${esc((e.sport || '').toLowerCase())}">${sportLabel(e)}</span>${external(e.source, 'Source')}</div>
  </div>`).join('');
}
function dateStrip(day) {
  return `<div class="date-strip" aria-label="Choose a day">${[-3,-2,-1,0,1,2,3].map(offset => {
    const d = addDays(day, offset), active = d === day;
    return `<button class="date-cell ${active ? 'is-selected' : ''}" data-day="${d}" aria-label="${esc(dayLabel(d))}"${active ? ' aria-pressed="true"' : ' aria-pressed="false"'}><span>${esc(dayLabel(d,{weekday:'short'}).toUpperCase())}</span><strong>${Number(d.slice(-2))}</strong><i></i></button>`;
  }).join('')}</div>`;
}
function durationText(ms) {
  const minutes = Math.round(ms/60_000), h = Math.floor(minutes/60), m = minutes%60;
  return `${h ? `${h}h` : ''}${m ? ` ${m}m` : ''}`.trim();
}
function gapsMarkup(summary, day) {
  if (summary.uncertain) return `<div class="uncertain-block"><span class="uncertain-icon">!</span><div><strong>At least one time or date is unconfirmed.</strong><p>We can’t calculate reliable gaps for this day. Date-only events and schedule windows are treated as uncertain for the whole day.</p></div></div>`;
  if (!summary.gaps.length) return `<div class="empty-inline">Tracked events cover this day using the stated estimates. Actual end times can differ.</div>`;
  return `<div class="gap-list">${summary.gaps.map(g => `<div class="gap"><span class="gap-dot"></span><div><strong>${esc(clockWithZone(g.start))} – ${esc(clockWithZone(g.end))}${g.end === summary.end ? ' <small>next day</small>' : ''}</strong><small>Potential gap · ${durationText(g.end-g.start)}</small></div></div>`).join('')}</div>`;
}
function timelineMarkup(summary) {
  if (summary.uncertain) return `<div class="day-timeline is-uncertain"><span>UNCERTAIN TIME</span></div>`;
  const len = summary.end-summary.start;
  return `<div class="day-timeline">${summary.occupied.map(x => `<span style="left:${100*(x.start-summary.start)/len}%;width:${100*(x.end-x.start)/len}%" title="Tracked event interval, estimated unless source supplies an end"></span>`).join('')}</div>`;
}
function calendarPanel(day, compact = false) {
  const summary = summarizeDay(index, day);
  const visible = summary.events.filter(e => eventMatches(e, filter));
  return `<div class="calendar-card card" id="calendar-card">
    <div class="calendar-top"><div><div class="section-kicker">DAY BY DAY <span> / </span> PACIFIC TIME</div><h3>${esc(dayLabel(day))}</h3><p>Browse the schedule and see the space in between.</p></div>
      <div class="calendar-controls"><button class="icon-btn" data-shift="-1" aria-label="Previous day">${icon('left')}</button><button class="today-btn" data-today>Today</button><button class="icon-btn" data-shift="1" aria-label="Next day">${icon('right')}</button><label class="date-picker-label"><span class="sr-only">Choose a date</span><input type="date" id="date-picker" min="2026-01-01" max="2029-12-31" value="${day}"></label></div></div>
    ${dateStrip(day)}
    <div class="day-body"><div class="day-section-title"><div><span class="section-kicker">THE DAILY PICTURE</span><h4>Potential gaps</h4></div><span class="tiny-note">ALL TRACKED CATEGORIES · PT</span></div>
      <div class="timeline-labels">${summary.end - summary.start === 86_400_000 ? "<span>12 AM</span><span>6 AM</span><span>12 PM</span><span>6 PM</span><span>12 AM</span>" : `<span>12 AM</span><span>DST CHANGE · ${(summary.end-summary.start)/3_600_000} HOURS</span><span>12 AM</span>`}</div>${timelineMarkup(summary)}
      ${gapsMarkup(summary, day)}
      <p class="micro-note">Not verified free: these calculations use published records and estimated durations only. Missing schedules, pre/postgame, delays and radio conflicts can change them.</p>
    </div>
    <div class="events-header"><div><span class="section-kicker">ON THE SCHEDULE</span><h4>Tracked events <span class="count-badge">${visible.length}</span></h4></div>${compact ? `<a class="text-link" href="${path(`site/planner/calendar.html?date=${day}`)}">Full calendar ${arrow}</a>` : ''}</div>
    ${!compact ? filterMarkup() : ''}
    <div class="event-list">${visible.length ? eventRows(visible, day, compact ? 5 : 500) : `<div class="empty-state"><span>✳</span><strong>No tracked records in this view.</strong><p>That does not mean the day is free; schedules and local carriage may be incomplete.</p></div>`}</div>
    ${compact && visible.length > 5 ? `<a class="show-more" href="${path(`site/planner/calendar.html?date=${day}`)}">View all ${visible.length} records <span>→</span></a>` : ''}
  </div>`;
}
function filterMarkup() {
  const items = [['all','All records'],['local','Priority teams'],['mlb','MLB'],['nfl','NFL'],['college','Stanford + Cal'],['westwood','Westwood One'],['other','Other radio sports']];
  return `<div class="filter-bar" aria-label="Filter event list">${items.map(([v,l]) => `<button data-filter="${v}" class="filter ${filter === v ? 'selected' : ''}" aria-pressed="${filter === v}">${l}</button>`).join('')}</div><p class="filter-note">Filters change the list, not the gap calculation above.</p>`;
}
function sidePanel() {
  const mlb2027 = data.events.filter(e => e.group === 'mlb' && e.date?.startsWith('2027-')).length;
  return `<aside class="side-stack"><div class="card side-card summary-card"><div class="side-icon">${icon('spark')}</div><span class="section-kicker">THE SHORT ANSWER</span><h3>Don’t book on<br>an empty calendar.</h3><p>The 2027 MLB schedule is out, but many start times are TBD. Other seasons and broadcasts are incomplete, so no vacation is verified conflict-free yet.</p><a class="text-link" href="${path('site/planner/vacation.html')}">Explore planning windows <span>→</span></a></div>
  <div class="card side-card watch-card"><div class="side-heading"><div><span class="section-kicker">KEEP AN EYE ON</span><h3>Your lineup</h3></div>${icon('radio')}</div><p>Following the local teams and networks you care about.</p><div class="team-pills"><a href="${path('site/planner/mlb.html')}"><i class="orange-dot"></i> Giants + A’s</a><a href="${path('site/planner/nfl.html')}"><i class="red-dot"></i> 49ers + NFL</a><a href="${path('site/planner/college.html')}"><i class="gold-dot"></i> Stanford + Cal</a><a href="${path('site/planner/other.html')}"><i class="blue-dot"></i> Warriors + Valkyries + more</a><a href="${path('site/planner/westwood.html')}"><i class="purple-dot"></i> Westwood One</a></div><a class="text-link" href="${path('site/planner/radio.html')}">See the radio guide <span>→</span></a></div>
  <div class="side-note"><span class="dot"></span><div><strong>${mlb2027.toLocaleString()} MLB records for 2027</strong><br><span>Game dates are not proof of local broadcasts.</span></div></div></aside>`;
}
function dashboardStats() {
  const mlb = data.events.filter(e => e.group === 'mlb' && e.date?.startsWith('2027-'));
  const tbd = mlb.filter(e => !e.start).length;
  const summary = summarizeDay(index, selectedDay);
  return `<div class="stats-grid"><a class="stat-card" href="${path('site/planner/mlb.html')}"><span class="stat-icon peach">${icon('calendar')}</span><span class="stat-label">2027 MLB SCHEDULE</span><strong>${mlb.length.toLocaleString()} <small>games listed</small></strong><span class="stat-caption">${tbd.toLocaleString()} with a time TBD <b>↗</b></span></a>
  <a class="stat-card" href="${path('site/planner/vacation.html')}"><span class="stat-icon sage">${icon('spark')}</span><span class="stat-label">VACATION WINDOWS</span><strong>Not verified</strong><span class="stat-caption">1, 2 & 3 week planning <b>↗</b></span></a>
  <a class="stat-card" href="${path(`site/planner/calendar.html?date=${selectedDay}`)}"><span class="stat-icon sand">${icon('clock')}</span><span class="stat-label">SELECTED DAY</span><strong>${summary.events.length} <small>tracked records</small></strong><span class="stat-caption">${summary.uncertain ? 'Some timing is uncertain' : 'Based on known schedules'} <b>↗</b></span></a>
  <a class="stat-card" href="${path('site/planner/review.html')}"><span class="stat-icon lavender">${icon('shield')}</span><span class="stat-label">DATA CONFIDENCE</span><strong>Partial <small>coverage</small></strong><span class="stat-caption">${esc(sourceFreshness())} <b>↗</b></span></a></div>`;
}
function overview() {
  return `<main><div class="wrap"><section class="hero"><div class="hero-content"><div class="hero-kicker"><span>✳</span> THE OUTER SUNSET EDITION <i></i> SAN FRANCISCO, CA</div><h1>Make space for<br><em>time away.</em></h1><p>A thoughtful little planner for finding your time between the games, broadcasts, and everything in between.</p><div class="hero-actions"><a class="button button-dark" href="${path('site/planner/vacation.html')}">Explore vacation windows <span>↗</span></a><a class="hero-link" href="${path('site/planner/methodology.html')}">How it works <span>→</span></a></div></div><div class="hero-caption"><span class="hero-caption-icon">✳</span><span>OUTER SUNSET<br><strong>San Francisco, California</strong></span></div></section>
  <div class="dashboard-heading"><div><div class="section-kicker">YOUR PLANNING DASHBOARD <span> / </span> 2026–2029</div><h2>A little clarity, at a glance.</h2><p>Good plans start with the full picture. Here’s what we know so far.</p></div><a class="updated" href="${path('site/planner/review.html')}"><span class="dot"></span><span>LAST CHECKED<br><strong>${esc(updatedText())}</strong></span></a></div>
  <div id="dashboard-stats">${dashboardStats()}</div>
  <section class="dashboard-grid"><div id="calendar-host">${calendarPanel(selectedDay, true)}</div>${sidePanel()}</section>
  <section class="bottom-callout"><div class="callout-icon">✳</div><div><span class="section-kicker">A NOTE FROM YOUR PLANNER</span><h3>Good to know before you go.</h3><p>A quiet-looking date isn’t necessarily a free date. We keep the unknowns visible so you can make plans with your eyes open.</p></div><a href="${path('site/planner/methodology.html')}" class="button button-outline">Our methodology <span>↗</span></a></section></div></main>`;
}
function headerBlock(kicker, title, copy) {
  return `<div class="page-heading"><div class="section-kicker">${kicker} <span> / </span> 2026–2029</div><h1>${title}</h1><p>${copy}</p></div>`;
}
function calendarPage() {
  return `<main class="wrap page-main">${headerBlock('THE SCOREBOARD', 'Every day, in perspective.', 'Explore official schedules alongside calculated gaps. Dates and times are shown in Pacific time, with daylight saving applied.')}
    <div class="notice"><span>!</span><p><strong>These gaps aren’t verified free.</strong> Published game schedules are broader than confirmed local radio carriage; unreleased games, unknown start times, overtime and pre/postgame remain possible.</p><a href="${path('site/planner/review.html')}">See what’s missing →</a></div>
    <section class="calendar-layout"><div id="calendar-host">${calendarPanel(selectedDay)}</div><aside class="side-stack"><div class="card side-card"><span class="section-kicker">HOW TO READ THIS</span><h3>Start with the knowns.</h3><p>A colored block represents a scheduled start through an estimated end, or a published network slot. Overlaps are combined; halftime is not free time.</p><p>Date-only records conservatively mark the entire possible Pacific day as uncertain.</p><a class="text-link" href="${path('site/planner/methodology.html')}">Read the methodology →</a></div><div class="card side-card"><span class="section-kicker">JUMP TO A LEAGUE</span><div class="quick-links"><a href="${path('site/planner/mlb.html')}">MLB · all 30 clubs <span>↗</span></a><a href="${path('site/planner/nfl.html')}">NFL + 49ers <span>↗</span></a><a href="${path('site/planner/college.html')}">Stanford + Cal <span>↗</span></a><a href="${path('site/planner/westwood.html')}">Westwood One <span>↗</span></a><a href="${path('site/planner/other.html')}">Warriors, Valkyries + more <span>↗</span></a></div></div></aside></section></main>`;
}
function vacationPage() {
  return `<main class="wrap page-main">${headerBlock('TIME AWAY', 'Make room for a longer break.', 'Explore 1-, 2-, and 3-week possibilities against the records currently available. These are planning leads, never verified recommendations.')}
    <div class="notice"><span>!</span><p><strong>No vacation window is verified conflict-free.</strong> NFL, MLB postseason, other sports and local station schedules are not fully published for 2027–2029. Do not book based on a blank calendar.</p><a href="${path('site/planner/review.html')}">Review the unknowns →</a></div>
    <div class="vacation-intro"><div><span class="section-kicker">THE EXECUTIVE SUMMARY</span><h2>Look for room, not guarantees.</h2><p>MLB has published its 2027 schedule, but many game times remain TBD. The 2027 post-Super Bowl period isn’t an empty break: the Warriors play February 15 and 17. For 2028–29, there is not yet enough league coverage to suggest meaningful dates.</p><p>We reserve the entire month of July 2028 as uncertain because MLB has announced an All-Star Game in San Francisco, but not its exact date.</p><p class="source-line">${external('https://www.nba.com/warriors/schedule','Warriors schedule')} &nbsp; ${external('https://www.mlb.com/giants/fans/all-star-game','2028 All-Star announcement')}</p></div><div class="vacation-aside"><div class="aside-emblem">✳</div><span class="section-kicker">THE STANDARD</span><strong>Zero verified<br>free windows</strong><p>Until schedules and station carriage are complete, the honest answer is “not yet.”</p></div></div>
    <section class="card finder-card"><div class="finder-heading"><div><span class="section-kicker">THE WINDOW FINDER</span><h2>Find a planning lead.</h2><p>Intervals below have no records in our snapshot—not necessarily no games or broadcasts.</p></div><div class="finder-controls"><label>YEAR<select id="window-year"><option>2027</option><option>2028</option><option>2029</option></select></label><label>DURATION<select id="window-length"><option value="7">1 week · 7 days</option><option value="14">2 weeks · 14 days</option><option value="21">3 weeks · 21 days</option></select></label></div></div><div id="window-results"></div></section>
    <section class="insight-grid"><div><span class="number">01</span><h3>Dates can move.</h3><p>National games, local stations and newly released schedules can change the picture at any time.</p></div><div><span class="number">02</span><h3>We don’t fill blanks.</h3><p>Time-TBD events and known schedule windows make their possible days uncertain, not free.</p></div><div><span class="number">03</span><h3>A game isn’t its broadcast.</h3><p>Radio start and end times, conflicts, reception and a local affiliate need separate confirmation.</p></div></section></main>`;
}
function renderCandidates() {
  const year = Number($('#window-year').value), length = Number($('#window-length').value);
  const mlbCount = data.events.filter(e => e.group === 'mlb' && e.date?.startsWith(String(year))).length;
  const container = $('#window-results');
  if (mlbCount < 1000) {
    container.innerHTML = `<div class="finder-empty"><span>✳</span><h3>Not enough published coverage for ${year}.</h3><p>No dates are being suggested. MLB’s full ${year} schedule and other leagues or radio schedules are not available in this snapshot.</p>${external('https://www.mlb.com/schedule','Official MLB schedule')}</div>`; return;
  }
  const candidates = findCandidates(index, year, length);
  container.innerHTML = candidates.length ? `<div class="table-wrap"><table><thead><tr><th>PLANNING LEAD</th><th>LENGTH</th><th>STATUS</th><th>SOURCE CHECK</th></tr></thead><tbody>${candidates.slice(0, 12).map(c => `<tr><td><strong>${esc(dayLabel(c.start,{month:'short',day:'numeric'}))} – ${esc(dayLabel(c.end,{month:'short',day:'numeric',year:'numeric'}))}</strong><small>No tracked records on these dates</small></td><td>${length} days</td><td><span class="status-amber">UNVERIFIED</span><small>Missing schedules / local carriage</small></td><td>${external('https://www.mlb.com/schedule','MLB')} · ${external('https://www.nfl.com/schedules/','NFL')}<br><a href="${path('site/planner/methodology.html')}">All coverage →</a> · <a href="${path(`site/planner/calendar.html?date=${c.start}`)}">Open first day →</a></td></tr>`).join('')}</tbody></table></div><p class="micro-note">Showing up to 12 earliest starts, not a ranking. Days with TBD times, source-date ambiguity or a known uncertain schedule window are excluded; unannounced events still may exist.</p>` : `<div class="finder-empty"><span>✳</span><h3>No ${length}-day lead found in the current records.</h3><p>This does not establish that a window is impossible; uncertain days are excluded and future releases can change the result.</p>${external('https://www.mlb.com/schedule','Official MLB schedule')}</div>`;
}
const stations = [
  {team:'San Francisco Giants', frequency:'680 AM · 104.5 FM', name:'KNBR', copy:'English flagship network. Spanish broadcasts: KSFN 1510 AM; individual games and reception still need checking.', source:'https://www.mlb.com/giants/schedule/broadcast-partners', tag:'BASEBALL'},
  {team:'Athletics', frequency:'960 AM', name:'KNEW', copy:'The A’s list KNEW as a Bay Area terrestrial affiliate. A team schedule alone does not verify every game on this station.', source:'https://www.mlb.com/athletics/schedule/affiliates', tag:'BASEBALL'},
  {team:'San Francisco 49ers', frequency:'680 AM · 107.7 FM', name:'KNBR / KSAN', copy:'Team flagship stations. The network list also includes KNBR 104.5 FM and KSFO 810 AM; verify conflicts for the specific game.', source:'https://www.49ers.com/fans/tv-radio', tag:'FOOTBALL'},
  {team:'Stanford football', frequency:'1050 AM', name:'KTCT', copy:'Stanford announced KTCT for its 2026 season. Future-year contracts and individual-game assignments require confirmation.', source:'https://gostanford.com/news/2026/07/30/2026-football-radio-broadcast-team-announced', tag:'COLLEGE'},
  {team:'California football', frequency:'810 AM', name:'KSFO', copy:'The 2026 Cal football information guide lists its Bay Area radio flagship. Confirm the game and station assignment.', source:'https://calbears.com/documents/download/2026/8/7/2026_Cal_Football_Info_Guide.pdf', tag:'COLLEGE'},
  {team:"California men’s basketball", frequency:'810 AM', name:'KSFO', copy:'The 2026–27 schedule lists KSFO for regular-season games. Check current game-specific conflicts.', source:'https://calbears.com/sports/mens-basketball/schedule', tag:'COLLEGE'},
  {team:'San José State men’s basketball', frequency:'860 AM', name:'KTRB', copy:'Selected 2026 game previews list KTRB. The historical entries are incomplete; do not assume future carriage.', source:'https://sjsuspartans.com/news/2026/01/05/spartans-to-host-fresno-state-on-nbc-sports-bay-area', tag:'COLLEGE'},
  {team:'Golden State Warriors', frequency:'95.7 FM', name:'KGMZ · The Game', copy:'The Warriors identify 95.7 The Game as their flagship. The 2026–27 team announcement covers regular-season radio.', source:'https://warriors.com/news/warriors-audacys-95-7-the-game-announce-multi-year-contract-extension-20251023', tag:'BASKETBALL'},
  {team:'Golden State Valkyries', frequency:'95.7 FM', name:'KGMZ · The Game', copy:'Selected 2026 games were announced on terrestrial FM; app-only listings are not treated as FM broadcasts.', source:'https://valkyries.wnba.com/news/golden-state-valkyries-announce-local-television-and-radio-broadcast-schedule-20260425', tag:'BASKETBALL'},
  {team:'San Jose Earthquakes', frequency:'810 AM · 1370 AM', name:'KSFO / KZSF', copy:'The team’s 2026 table lists English and Spanish radio, with some alternatives. Check the individual match and reception.', source:'https://www.sjearthquakes.com/news/news-earthquakes-announce-radio-stations-for-2026-mls-season', tag:'SOCCER'},
  {team:'Westwood One network', frequency:'Local affiliate varies', name:'Check each event', copy:'National network airtime is not proof a Bay Area affiliate carries that event. Blackouts and competing broadcasts can apply.', source:'https://www.westwoodonesports.com/station-finder/', tag:'NETWORK'}
];
function radioPage() {
  return `<main class="wrap page-main">${headerBlock('ON THE DIAL', 'A guide to the local airwaves.', 'A starting point for ordinary AM and FM around the Outer Sunset. These are team or network listings, not a guarantee of a particular broadcast.')}
  <div class="notice"><span>!</span><p><strong>Carriage and reception are separate questions.</strong> Team flagships, station conflicts, power patterns and local blackouts can change what is audible at 94122. Internet-only, satellite and HD subchannels are not counted as ordinary FM.</p><a href="${path('site/planner/review.html')}">What needs review →</a></div>
  <div class="section-heading"><div><span class="section-kicker">YOUR RADIO ROSTER</span><h2>Start with the flagships.</h2></div><p>Linked to the official team or network information.</p></div>
  <div class="station-grid">${stations.map(s => `<article class="card station-card"><div class="station-top"><span class="station-symbol">${icon('radio')}</span><span class="sport-chip">${esc(s.tag)}</span></div><h3>${esc(s.team)}</h3><div class="frequency">${esc(s.frequency)}</div><div class="station-name">${esc(s.name)}</div><p>${esc(s.copy)}</p>${external(s.source,'Official station information')}</article>`).join('')}</div>
  <section class="card radio-note"><span class="section-kicker">A NOTE ON OTHER SPORTS</span><h2>We don’t count a stream as a station.</h2><p>The current Sharks team audio page describes app and web listening; historical KFOX references do not by themselves establish an ordinary-FM broadcast for 2026–27. We keep Sharks carriage in review rather than treating streaming or an old affiliate list as confirmed terrestrial radio.</p>${external('https://www.nhl.com/sharks/team/broadcast','Sharks broadcast information')}</section></main>`;
}
const sourceInfo = {
  mlb:['MLB Stats API','https://www.mlb.com/schedule'], nfl:['NFL schedule','https://www.nfl.com/schedules/'],
  nfl_history:['NFL 2026 historical games','https://www.nfl.com/news/nfl-announces-week-18-schedule-for-2025-season-with-ravens-steelers-on-sunday-night-football'],
  cal:['California football','https://calbears.com/sports/football/schedule'], stanford:['Stanford football','https://gostanford.com/sports/football/schedule'],
  westwood:['Westwood One calendar','https://www.westwoodonesports.com/nfl-schedule/'], warriors:['NBA / Warriors','https://www.nba.com/warriors/schedule'],
  earthquakes:['San Jose Earthquakes','https://www.sjearthquakes.com/news/news-earthquakes-announce-radio-stations-for-2026-mls-season'],
  cal_mbb:['Cal men’s basketball','https://calbears.com/sports/mens-basketball/schedule'],
  valkyries:['Valkyries 2026 radio table','https://valkyries.wnba.com/news/golden-state-valkyries-announce-local-television-and-radio-broadcast-schedule-20260425'],
  historical_radio:['Manually reviewed radio games','https://valkyries.wnba.com/news/gameday-preview-20261031']
};
function reviewPage() {
  const missingTimes = data.events.filter(e => !e.start).length;
  const undated = data.events.filter(e => !e.date).length;
  const sourceRows = Object.entries(sourceInfo).map(([key,[label,url]]) => {
    const s = data.sources[key];
    const stale = !s?.lastSuccess || Date.now() - Date.parse(s.lastSuccess) > 72 * 3_600_000;
    const good = s?.ok && !stale && !['historical_radio', 'nfl_history'].includes(key);
    return `<tr><td><strong>${esc(label)}</strong></td><td><span class="${good ? 'status-sage' : 'status-amber'}">${good ? 'FETCHED' : (['historical_radio', 'nfl_history'].includes(key) ? 'RECHECK' : (s?.ok ? 'STALE' : 'NEEDS REVIEW'))}</span></td><td>${s?.count?.toLocaleString() ?? '—'} records${s?.error ? `<small>${esc(s.error)}</small>` : ''}</td><td>${s?.lastSuccess ? esc(new Intl.DateTimeFormat('en-US',{timeZone:ZONE,month:'short',day:'numeric',year:'numeric',hour:'numeric',minute:'2-digit'}).format(new Date(s.lastSuccess))) : '—'}</td><td>${external(url,'Source')}</td></tr>`;
  }).join('') + `<tr><td><strong>Hand-reviewed announcements</strong></td><td><span class="status-amber">RECHECK</span></td><td>Future dates and opponents<small>Older announcements may change</small></td><td>${esc(data.announcedReviewedAt || '—')}</td><td>${external('https://gostanford.com/news/2026/05/20/two-dates-added-to-notre-dame-rivalry','Example source')}</td></tr>`;
  const flags = [
    ['Incomplete future schedules','2027–29 league, team and broadcast schedules are not complete. An empty date does not establish a free day.','https://www.mlb.com/schedule'],
    ['Unassigned NFL dates','Week 18 and playoff windows have league dates, but individual matchups and kickoffs may be TBD. The published window is reserved as uncertain.','https://www.nfl.com/news/2026-27-national-football-league-important-dates'],
    ['2028 All-Star Game','MLB has named Oracle Park and July 2028, but not a day. July is held uncertain instead of inventing a date.','https://www.mlb.com/giants/fans/all-star-game'],
    ['Stanford time ambiguity','A visible “4 or 4:30 p.m.” or TBA is not a confirmed kickoff, even if a hidden page timestamp looks precise.','https://gostanford.com/sports/football/schedule'],
    ['Superseded 2027 Stanford–TCU game','TCU later announced a different opponent, canceling the earlier Stanford game. The old fixture is excluded.','https://gofrogs.com/news/2026/4/17/football-horned-frogs-to-host-north-texas-in-2027'],
    ['2026 Texans–Steelers kickoff discrepancy','The NFL’s Wild Card schedule lists 8:00 p.m. ET; another NFL article lists 8:15 p.m. The kickoff is blank until reconciled.','https://www.nfl.com/news/nfl-how-to-watch-nfl-playoffs-wild-card-weekend-schedule-and-more'],
    ['2027 Pro Bowl game discontinued','The NFL says it will no longer stage the AFC–NFC Pro Bowl game beginning with the 2026 season. A 2027 celebration is mentioned, but no game or radio airtime should be invented.','https://www.nfl.com/news/nfl-elevates-pro-bowl-selection-game-s-will-cease-being-contested'],
    ['Westwood One local affiliate','Network airtime is not proof that a station in the Outer Sunset will air the event. Affiliate conflicts and blackouts remain possible.','https://www.westwoodonesports.com/station-finder/'],
    ['Game end and broadcast duration','The MLB 2h38m duration is an average, not a guaranteed end. Other durations are explicit planning assumptions; overtime and pre/postgame may extend coverage.','https://www.mlb.com/news/mlb-average-game-time-under-three-hours-third-straight-year'],
    ['Earthquakes 2026 table','The team’s radio schedule was announced in February 2026. Dates, times and station assignments are subject to change; later seasons and playoff broadcasts need checking.','https://www.sjearthquakes.com/news/news-earthquakes-announce-radio-stations-for-2026-mls-season'],
    ['Valkyries 2026 station changes','The April team table listed August 7 as app-only; a later game preview listed 95.7 FM. The later game-specific listing is used. Other app-only games are excluded.','https://valkyries.wnba.com/news/gameday-preview-20260807'],
    ['Historic basketball is incomplete','The current Warriors feed starts with the 2026–27 season. Earlier 2026 Warriors, Cal and San José State basketball schedules are not fully captured; individual verified San José State broadcasts are included.','https://www.nba.com/news/2025-26-nba-regular-season-schedule'],
    ['Sharks terrestrial radio','The current team page describes digital audio; an old KFOX announcement does not verify current ordinary-FM carriage. Sharks games are not assumed on air.','https://www.nhl.com/sharks/team/broadcast'],
    ['Local reception','A station or network listing cannot verify reception at a particular address, radio, or time of day.','https://www.49ers.com/fans/tv-radio'],
    ['Previous four-day claim corrected','February 15–18, 2027 is not verified free: the Warriors schedule includes games on February 15 and 17. The older site’s claim is superseded.','https://www.nba.com/warriors/schedule']
  ];
  return `<main class="wrap page-main">${headerBlock('THE HONEST DETAILS', 'Flagged for review.', 'What we know, what we don’t, and where to check it. Uncertainty is part of the plan—not something to hide.')}
  <div class="review-metrics"><div><span class="section-kicker">TIME OR DATE TBD</span><strong>${missingTimes.toLocaleString()}</strong><p>Source records without an exact start</p></div><div><span class="section-kicker">DATE NOT ASSIGNED</span><strong>${undated.toLocaleString()}</strong><p>Records that cannot be placed on a day</p></div><div><span class="section-kicker">SNAPSHOT CHECKED</span><strong class="metric-date">${esc(updatedText())}</strong><p>Check sources again before planning</p></div></div>
  <section class="review-section"><div class="section-heading"><div><span class="section-kicker">COVERAGE, NOT COMPLETENESS</span><h2>Source health.</h2></div><p>A successful fetch does not mean all future schedules exist.</p></div><div class="card table-wrap"><table><thead><tr><th>SOURCE</th><th>FETCH</th><th>SNAPSHOT</th><th>LAST SUCCESS · PT</th><th>OFFICIAL LINK</th></tr></thead><tbody>${sourceRows}</tbody></table></div></section>
  <section class="review-section"><div class="section-heading"><div><span class="section-kicker">OPEN QUESTIONS</span><h2>Things worth knowing.</h2></div><p>Each note points back to an official source.</p></div><div class="flag-list">${flags.map(([title,copy,url],i) => `<article class="flag-row"><span class="flag-index">${String(i+1).padStart(2,'0')}</span><div><h3>${esc(title)}</h3><p>${esc(copy)}</p></div>${external(url,'Source')}</article>`).join('')}</div></section>
  <section class="review-section"><div class="section-heading"><div><span class="section-kicker">RECORD-LEVEL REVIEW</span><h2>Unconfirmed dates & times.</h2></div><p>Every row has its own official source. Times remain blank until confirmed.</p></div><div class="card review-table-card"><div class="review-search"><label for="review-search">Search records</label><input id="review-search" type="search" placeholder="Team, league, or date"></div><div id="review-table"></div></div></section></main>`;
}
let reviewPageNumber = 0;
function renderReviewTable() {
  const input = $('#review-search');
  if (!input) return;
  const query = input.value.toLowerCase().trim();
  const rows = data.events.filter(e => !e.start && `${e.title} ${e.date || ''} ${e.sport}`.toLowerCase().includes(query));
  const pageSize = 30;
  const maxPage = Math.max(0, Math.ceil(rows.length / pageSize)-1);
  reviewPageNumber = Math.min(reviewPageNumber, maxPage);
  const shown = rows.slice(reviewPageNumber * pageSize, (reviewPageNumber+1) * pageSize);
  $('#review-table').innerHTML = `<div class="table-wrap"><table><thead><tr><th>RECORD</th><th>SOURCE DATE</th><th>START</th><th>NEEDS REVIEW</th><th>OFFICIAL LINK</th></tr></thead><tbody>${shown.map(e => `<tr><td><strong>${esc(e.title)}</strong><small>${sportLabel(e)} · ${esc(e.category || '')}</small></td><td>${esc(e.date || '—')}</td><td>—</td><td>${esc(e.dateBasis || 'Date or time TBD')}</td><td>${external(e.source,'Source')}</td></tr>`).join('') || '<tr><td colspan="5">No matching records.</td></tr>'}</tbody></table></div><div class="pagination"><span>${rows.length ? `${reviewPageNumber*pageSize+1}–${Math.min((reviewPageNumber+1)*pageSize,rows.length)} of ${rows.length.toLocaleString()}` : '0 records'}</span><div><button data-review-page="prev" ${reviewPageNumber === 0 ? 'disabled' : ''}>← Previous</button><button data-review-page="next" ${reviewPageNumber >= maxPage ? 'disabled' : ''}>Next →</button></div></div>`;
}
function methodologyPage() {
  return `<main class="wrap page-main">${headerBlock('BEHIND THE PLANNER', 'A little transparency goes a long way.', 'The calculations are useful only when their limitations are clear. Here’s how each part of the planner works.')}
  <div class="method-grid"><aside class="card method-aside"><span class="section-kicker">ON THIS PAGE</span><a href="#sources">Sources & scope</a><a href="#time">Time & gaps</a><a href="#duration">Duration assumptions</a><a href="#uncertainty">Uncertainty</a><a href="#refresh">Refresh & verification</a></aside><div class="method-copy">
  <section id="sources"><span class="section-kicker">01 / THE INPUTS</span><h2>Official sources, linked per row.</h2><p>We ingest the official MLB schedule for all 30 clubs (spring, regular season, available postseason, exhibitions and All-Star), NFL weekly cards including available preseason and postseason, hand-reviewed 2026 games from the 2025 NFL season, Stanford and Cal team schedules, the NBA Warriors schedule, Cal men’s basketball, the Valkyries’ 2026 FM listings, selected game-specific San José State broadcasts, the team’s 2026 Earthquakes radio table, and Westwood One’s published event calendar. Not all schedules are released; NBA Cup, playoff and future matches may be missing.</p><p>National MLB and NFL games are tracked conservatively because you asked for all games; this is broader than verified Bay Area terrestrial carriage. An official game date is not proof of local AM/FM coverage.</p><p>${external('https://www.mlb.com/schedule','MLB schedule')} · ${external('https://www.nfl.com/schedules/','NFL schedule')} · ${external('https://www.westwoodonesports.com/station-finder/','Westwood affiliates')}</p></section>
  <section id="time"><span class="section-kicker">02 / THE CLOCK</span><h2>Pacific time, all year.</h2><p>Exact starts are stored as UTC and displayed in <code>America/Los_Angeles</code>, switching between PST and PDT automatically. Days can be 23 or 25 hours at daylight-saving transitions. Overlapping event intervals are merged; halftime or breaks are not treated as free. A date without a time is uncertain for the whole possible Pacific day, including adjacent days where the source date’s time zone or an overnight finish could change the Pacific date.</p><p>Westwood One timestamps represent network airtime and, where supplied, a scheduled network end. They are not necessarily kickoff or actual completion; the local affiliate remains unconfirmed.</p></section>
  <section id="duration"><span class="section-kicker">03 / THE ESTIMATES</span><h2>Ends are estimates, not facts.</h2><div class="table-wrap"><table><thead><tr><th>EVENT</th><th>PLANNING DURATION</th><th>BASIS / SOURCE</th></tr></thead><tbody><tr><td>MLB</td><td>2h 38m</td><td>MLB’s 2025 nine-inning average, not a guarantee. ${external('https://www.mlb.com/news/mlb-average-game-time-under-three-hours-third-straight-year','MLB')}</td></tr><tr><td>NFL</td><td>3h 12m</td><td>Planning assumption; overtime and coverage are not included. ${external('https://www.nfl.com/schedules/','NFL')}</td></tr><tr><td>Stanford / Cal football</td><td>3h 30m</td><td>Planning assumption, not a published end time. ${external('https://gostanford.com/sports/football/schedule','Stanford')}</td></tr><tr><td>Warriors</td><td>2h 30m</td><td>Planning assumption, not a published end time. ${external('https://www.nba.com/warriors/schedule','NBA')}</td></tr><tr><td>Valkyries / college basketball</td><td>2h 15m</td><td>Planning assumption; actual end and radio coverage may run longer. ${external('https://calbears.com/sports/mens-basketball/schedule','Cal')}</td></tr><tr><td>Earthquakes</td><td>2h</td><td>Planning assumption; stoppage and extra time may extend play. ${external('https://www.sjearthquakes.com/news/news-earthquakes-announce-radio-stations-for-2026-mls-season','Team')}</td></tr><tr><td>Westwood One</td><td>Published network slot</td><td>Scheduled slot only, if provided; not an actual game end. ${external('https://www.westwoodonesports.com/nfl-schedule/','Westwood One')}</td></tr></tbody></table></div><p>No unverified pregame, postgame or end time is silently added. Allow extra time yourself; delays, extra innings and overtime can extend events.</p></section>
  <section id="uncertainty"><span class="section-kicker">04 / THE CAVEATS</span><h2>No blank means “free.”</h2><p>Candidate windows are intervals with no records in the current snapshot after known uncertain windows are excluded. They are not ranked recommendations and are never verified conflict-free. The planner withholds suggestions for years with too little MLB coverage; other unannounced events can still exist. Local station assignments, signal strength at 94122, coverage conflicts and blackouts require separate confirmation.</p><p>Source dates in a non-Pacific or unknown zone can affect an adjacent Pacific day. Where a whole source window is known but games aren’t assigned to individual dates, we show that window as uncertain rather than inventing fixtures.</p></section>
  <section id="refresh"><span class="section-kicker">05 / KEEPING CURRENT</span><h2>Refresh, then recheck.</h2><p>The published snapshot is refreshed by GitHub Actions. If a feed fails, the last successful records are retained and the failure is surfaced on the review page. Some manually reviewed announcements require periodic re-verification. Always check the linked official game and station before booking.</p><p><a href="${path('site/planner/review.html')}">Open flagged items →</a></p></section></div></div></main>`;
}
function bind() {
  $('#menu-toggle')?.addEventListener('click', event => {
    const button = event.currentTarget, open = button.getAttribute('aria-expanded') !== 'true';
    button.setAttribute('aria-expanded', String(open)); $('#main-nav').classList.toggle('is-open', open);
  });
  document.addEventListener('click', event => {
    const dateButton = event.target.closest('[data-day]');
    const shift = event.target.closest('[data-shift]');
    const todayButton = event.target.closest('[data-today]');
    const filterButton = event.target.closest('[data-filter]');
    const pagination = event.target.closest('[data-review-page]');
    if (dateButton) changeDate(dateButton.dataset.day);
    if (shift) changeDate(addDays(selectedDay, Number(shift.dataset.shift)));
    if (todayButton) changeDate(today >= '2026-01-01' && today <= '2029-12-31' ? today : '2026-11-02');
    if (filterButton) { filter = filterButton.dataset.filter; updateCalendar(); }
    if (pagination) { reviewPageNumber += pagination.dataset.reviewPage === 'next' ? 1 : -1; renderReviewTable(); }
  });
  document.addEventListener('change', event => {
    if (event.target.id === 'date-picker' && event.target.value) changeDate(event.target.value);
    if (['window-year','window-length'].includes(event.target.id)) renderCandidates();
  });
  $('#review-search')?.addEventListener('input', () => {reviewPageNumber = 0; renderReviewTable();});
}
function changeDate(day) {
  if (day < '2026-01-01' || day > '2029-12-31') return;
  selectedDay = day;
  if (page === 'calendar') history.replaceState(null, '', `?date=${day}`);
  updateCalendar();
}
function updateCalendar() {
  const host = $('#calendar-host');
  if (host) host.innerHTML = calendarPanel(selectedDay, page === 'overview');
  const stats = $('#dashboard-stats');
  if (stats) stats.innerHTML = dashboardStats();
}
async function init() {
  document.body.innerHTML = `${nav()}<div id="app"><div class="loading wrap">Checking the schedule…</div></div>${footer()}`;
  try {
    const response = await fetch(path('site/data/events.json'));
    if (!response.ok) throw new Error(`HTTP ${response.status}`);
    data = await response.json();
    index = buildIndex(data);
    const render = {overview, calendar: calendarPage, vacation: vacationPage, radio: radioPage, review: reviewPage, methodology: methodologyPage}[page] || overview;
    $('#app').innerHTML = render();
    bind();
    if (page === 'vacation') renderCandidates();
    if (page === 'review') renderReviewTable();
  } catch (error) {
    $('#app').innerHTML = `<main class="wrap page-main"><div class="notice"><span>!</span><p><strong>The schedule snapshot couldn’t be loaded.</strong> Please try again or check the official sources. Do not treat this as a free calendar.</p>${external('https://www.mlb.com/schedule','Official MLB schedule')}</div><p class="micro-note">${esc(error.message)}</p></main>`;
    bind();
  }
}
init();
