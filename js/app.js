/* FREE TIME VACATION — static dashboard interactions.
   All schedule data comes from official-source snapshots; browser code only filters,
   merges Pacific-time intervals and computes free windows. */
(function () {
  'use strict';
  const M = window.K4_META || {};
  const DEFAULT_SOURCE = M.default_source_url || 'https://statsapi.mlb.com/api/v1/schedule?sportId=1&season=2027';
  const DURATIONS = Object.assign({ MLB: 158, NFL: 192, NCAAF: 204, MLS: 120 }, M.durations || {});
  const DAY_CACHE = {};
  const CATS = ['MLB', 'NFL', 'NCAAF', 'WWO', 'MLS'];

  function esc(v) {
    return String(v == null ? '' : v).replace(/[&<>"']/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
  }
  function fmtHM(m) {
    m = Math.max(0, Math.min(1440, Math.round(m)));
    return String(Math.floor(m / 60)).padStart(2, '0') + ':' + String(m % 60).padStart(2, '0');
  }
  function todayPacific() { return new Intl.DateTimeFormat('en-CA', {timeZone:'America/Los_Angeles', year:'numeric', month:'2-digit', day:'2-digit'}).format(new Date()); }
  function parseDate(s) { return new Date(String(s) + 'T12:00:00Z'); }
  function dateISO(d) { return d.toISOString().slice(0, 10); }
  function addDays(s, n) { const d = parseDate(s); d.setUTCDate(d.getUTCDate() + n); return dateISO(d); }
  function clampDate(s) {
    const lo = M.data_start || '2026-01-01', hi = (M.date_range || ['2026-11-01','2029-12-31'])[1];
    if (s < lo) return lo; if (s > hi) return hi; return s;
  }
  function sourceUrl(row) { return row && row.source_url ? row.source_url : DEFAULT_SOURCE; }
  function sourceLabel(row) { return (row && row.source_label) || 'Official source'; }
  function externalLink(row, text) {
    return '<a class="source-link" href="' + esc(sourceUrl(row)) + '" target="_blank" rel="noopener">' + esc(text || sourceLabel(row)) + '</a>';
  }
  function statusBadge(status) {
    const s = String(status || '').toUpperCase();
    let cls = 'neutral';
    if (s.includes('VERIFIED') && !s.includes('UNVERIFIED')) cls = 'verified';
    if (s.includes('ESTIMATED') || s.includes('MODEL')) cls = 'estimated';
    if (s.includes('UNVERIFIED') || s.includes('TBD') || s.includes('NOT RELEASED')) cls = 'unverified';
    if (s.includes('CORRECTED')) cls = 'corrected';
    if (s.includes('FLAGGED') || s.includes('REPLACED')) cls = 'flagged';
    if (s.includes('REVIEWED')) cls = 'reviewed';
    return '<span class="badge badge-' + cls + '">' + esc(status || 'UNVERIFIED') + '</span>';
  }
  function mergeIntervals(rows) {
    const sorted = rows.map(r => Object.assign({}, r)).sort((a,b) => a.start-b.start || a.end-b.end);
    const out = [];
    for (const r of sorted) {
      const last = out[out.length-1];
      if (last && r.start <= last.end) {
        last.end = Math.max(last.end, r.end);
        last.labels = (last.labels || []).concat(r.labels || [r.label || r.matchup || 'Busy']);
        last.source_url = last.source_url || r.source_url;
        last.source_label = last.source_label || r.source_label;
        if (!last.categories.includes(r.category)) last.categories.push(r.category);
      } else {
        r.labels = r.labels || [r.label || r.matchup || 'Busy'];
        r.categories = [r.category || 'OTHER'];
        out.push(r);
      }
    }
    return out;
  }
  function freeWindows(busy) {
    const free = []; let cursor = 0;
    for (const b of busy) {
      if (b.start > cursor) free.push({ start: cursor, end: b.start });
      cursor = Math.max(cursor, b.end);
    }
    if (cursor < 1440) free.push({ start: cursor, end: 1440 });
    return free;
  }
  function durationOverride(category) { return Number(DURATIONS[category] || 0); }
  function adjustedIntervals(rows) {
    // Keep pre-split overnight fragments intact. Changing a duration per day
    // cannot correctly recompute cross-midnight events; use the source model.
    return rows.map(r => Object.assign({}, r));
  }

  function selectedIntervals(rows) {
    const showTbd = document.getElementById('show-tbd')?.checked !== false;
    const showModels = document.getElementById('show-models')?.checked !== false;
    const showUnverified = document.getElementById('show-unverified')?.checked !== false;
    const active = new Set(CATS.filter(c => document.querySelector('[data-cat="' + c + '"]')?.checked !== false));
    return adjustedIntervals(rows).filter(r => {
      if (!showTbd && r.status === 'ESTIMATED_TBD_START') return false;
      if (!showModels && r.status === 'ESTIMATED_UNRELEASED_SEASON_MODEL') return false;
      if (!showUnverified && r.status === 'UNVERIFIED_BLOCK') return false;
      if (!active.has(r.category)) return false;
      return true;
    });
  }
  async function loadDays(year) {
    if (DAY_CACHE[year]) return DAY_CACHE[year];
    const res = await fetch('data/official/days-' + year + '.json', { cache: 'force-cache' });
    if (!res.ok) throw new Error('Could not load ' + year + ' day data (' + res.status + ')');
    DAY_CACHE[year] = await res.json();
    return DAY_CACHE[year];
  }
  function intervalClass(r) {
    if (r.status === 'UNVERIFIED_BLOCK') return 'unverified';
    if (r.status === 'ESTIMATED_UNRELEASED_SEASON_MODEL') return 'model';
    return String(r.category || 'other').toLowerCase();
  }
  function renderTimeline(merged, free, holder) {
    const blocks = [];
    merged.slice(0, 18).forEach(b => {
      const label = (b.labels || []).filter(Boolean).slice(0, 2).join(' + ') || b.label || 'Busy';
      blocks.push('<div class="timeline-block ' + intervalClass(b) + '" style="--s:' + b.start + ';--w:' + Math.max(2,b.end-b.start) + '" title="' + esc(label) + '"><a href="' + esc(sourceUrl(b)) + '" target="_blank" rel="noopener" style="color:white">' + esc(fmtHM(b.start) + '–' + fmtHM(b.end) + ' ' + label) + '</a></div>');
    });
    free.slice(0, 10).forEach(f => blocks.push('<div class="timeline-block free" style="--s:' + f.start + ';--w:' + Math.max(2,f.end-f.start) + '">FREE ' + fmtHM(f.start) + '–' + fmtHM(f.end) + '</div>'));
    holder.innerHTML = '<div class="timeline-axis"><span>00:00</span><span>03:00</span><span>06:00</span><span>09:00</span><span>12:00</span><span>15:00</span><span>18:00</span><span>21:00</span></div>' + blocks.join('');
  }
  function dynamicTable(headers, rows) {
    let h = '<div class="scroll"><table><thead><tr>' + headers.map(x => '<th>' + esc(x) + '</th>').join('') + '<th>Official source</th></tr></thead><tbody>';
    rows.forEach(r => {
      const cells = r.cells.map(c => '<td>' + c + '</td>').join('');
      h += '<tr data-source-url="' + esc(sourceUrl(r.sourceRow)) + '">' + cells + '<td>' + externalLink(r.sourceRow, 'Official source') + '</td></tr>';
    });
    return h + '</tbody></table></div>';
  }
  function nearestSource(rows, position) {
    let best = null, dist = Infinity;
    rows.forEach(r => { const d = Math.min(Math.abs(r.start-position), Math.abs(r.end-position)); if (d < dist) { dist=d; best=r; } });
    return best || { source_url: DEFAULT_SOURCE, source_label: 'Official source catalogue' };
  }
  async function renderDay(dateStr) {
    const holder = document.getElementById('day-content');
    if (!holder) return;
    holder.innerHTML = '<div class="callout">Loading official day intervals…</div>';
    try {
      const days = await loadDays(dateStr.slice(0,4));
      const rows = selectedIntervals(days[dateStr] || []);
      const merged = mergeIntervals(rows);
      const free = freeWindows(merged);
      const freeMinutes = free.reduce((a,b) => a + (b.end-b.start), 0);
      const unverified = rows.filter(r => r.status === 'UNVERIFIED_BLOCK').length;
      const models = rows.filter(r => r.status === 'ESTIMATED_UNRELEASED_SEASON_MODEL').length;
      const official = rows.filter(r => r.status === 'OFFICIAL_NETWORK_WINDOW' || r.status === 'OFFICIAL_START_ESTIMATED_DURATION').length;
      const tbd = rows.filter(r => r.status === 'ESTIMATED_TBD_START').length;
      document.getElementById('selected-date').value = dateStr;
      document.getElementById('day-heading').textContent = new Intl.DateTimeFormat('en-US', { timeZone:'America/Los_Angeles', weekday:'long', year:'numeric', month:'long', day:'numeric' }).format(parseDate(dateStr));
      let html = '<div class="status-strip">';
      html += '<span class="pill">Estimated gap ' + Math.floor(freeMinutes/60) + 'h ' + (freeMinutes%60) + 'm PT</span>';
      html += '<span class="pill">' + official + ' official-start windows</span>';
      html += '<span class="pill">' + tbd + ' TBD planning estimates</span>';
      html += '<span class="pill">' + models + ' unreleased-season models</span>';
      html += '<span class="pill">' + unverified + ' unverified blocks</span>';
      html += '</div>';
      if (!rows.length) html += '<div class="callout warn"><strong>UNKNOWN — no captured conflicts.</strong> Empty or filtered data does not confirm a free day. Future schedules and local carriage are incomplete; review the flags page.</div>';
      html += '<div id="day-timeline" class="timeline"></div>';
      html += '<div class="legend"><span><i style="background:#1d63c7"></i>MLB</span><span><i style="background:#b42332"></i>NFL</span><span><i style="background:#6941c6"></i>NCAAF</span><span><i style="background:#a76500"></i>WWO</span><span><i style="background:#087261"></i>MLS</span><span><i style="background:#7a271e"></i>UNVERIFIED</span><span><i style="background:#7c8798"></i>ESTIMATED MODEL</span><span><i style="background:#157a54"></i>FREE</span></div>';
      const freeRows = free.map(f => ({ cells: [fmtHM(f.start), fmtHM(f.end), String(f.end-f.start), statusBadge(f.end-f.start === 1440 ? 'UNVERIFIED ALL-DAY GAP' : 'ESTIMATED PLANNING GAP')], sourceRow: nearestSource(merged, f.start) }));
      html += '<section class="panel"><h2>Estimated intraday planning gaps</h2><p class="intro">Pacific Time (PST/PDT). Links identify nearby schedule evidence, not proof of absence. Coverage may extend beyond estimated end times.</p>' + dynamicTable(['Start PT','End PT','Minutes','Status'], freeRows) + '</section>';
      const eventRows = rows.map(r => ({ cells: [fmtHM(r.start), fmtHM(r.end), esc(r.category || ''), esc(r.label || r.matchup || 'Busy block'), statusBadge(r.verification || r.status), r.focus ? '<span class="badge badge-focus">FOCUS</span>' : '<span class="badge badge-high">HIGH</span>'], sourceRow: r }));
      html += '<section class="panel"><h2>Game / broadcast presence</h2><p class="intro">Every row is a busy-time candidate. Blank official values appear on the main tables as UNVERIFIED.</p>' + dynamicTable(['Start PT','End PT','Category','Event / source basis','Verification','Priority'], eventRows) + '</section>';
      holder.innerHTML = html;
      renderTimeline(merged, free, document.getElementById('day-timeline'));
    } catch (err) {
      holder.innerHTML = '<div class="callout danger"><strong>Data load failed.</strong> ' + esc(err.message) + '</div>';
    }
  }
  function initDaily() {
    const dateInput = document.getElementById('selected-date');
    if (!dateInput) return;
    const params = new URLSearchParams(location.search);
    let dateStr = clampDate(params.get('date') || todayPacific());
    function go(n) { dateStr = addDays(dateStr, n); dateStr = clampDate(dateStr); history.replaceState(null, '', '?date=' + dateStr); renderDay(dateStr); }
    document.querySelectorAll('[data-day-step]').forEach(b => b.addEventListener('click', () => go(Number(b.dataset.dayStep))));
    document.getElementById('today-btn').addEventListener('click', () => { dateStr = clampDate(todayPacific()); history.replaceState(null, '', '?date=' + dateStr); renderDay(dateStr); });
    dateInput.addEventListener('change', () => { dateStr = clampDate(dateInput.value); history.replaceState(null, '', '?date=' + dateStr); renderDay(dateStr); });
    document.querySelectorAll('.filter-toggle, [data-duration]').forEach(el => el.addEventListener('change', () => renderDay(dateStr)));
    renderDay(dateStr);
  }
  async function renderCalendar(year, month) {
    const holder = document.getElementById('calendar-content');
    if (!holder) return;
    holder.innerHTML = '<div class="callout">Loading month…</div>';
    try {
      const days = await loadDays(year);
      const first = new Date(Date.UTC(year, month, 1, 12));
      const daysInMonth = new Date(Date.UTC(year, month + 1, 0, 12)).getUTCDate();
      const startDow = first.getUTCDay();
      let html = '<div class="calendar-grid">';
      ['Sun','Mon','Tue','Wed','Thu','Fri','Sat'].forEach(d => html += '<div class="dow">' + d + '</div>');
      for (let i=0;i<startDow;i++) html += '<div class="calendar-day empty"></div>';
      const monthRows = [];
      for (let dnum=1; dnum<=daysInMonth; dnum++) {
        const key = year + '-' + String(month+1).padStart(2,'0') + '-' + String(dnum).padStart(2,'0');
        const rows = adjustedIntervals(days[key] || []);
        const merged = mergeIntervals(rows);
        const free = freeWindows(merged);
        const freeMinutes = free.reduce((a,b)=>a+(b.end-b.start),0);
        const unverified = rows.filter(r=>r.status==='UNVERIFIED_BLOCK').length;
        const cls = unverified || !merged.length ? 'unverified' : 'busy';
        const sourceRow = merged[0] || { source_url: DEFAULT_SOURCE, source_label: 'Official source catalogue' };
        html += '<div class="calendar-day' + (key === todayPacific() ? ' today' : '') + '"><a href="daily.html?date=' + key + '">' + dnum + '</a><span class="dot ' + cls + '"></span><span class="mini">' + merged.length + ' busy</span><div class="free-minutes">' + Math.floor(freeMinutes/60) + 'h ' + (freeMinutes%60) + 'm gap*</div></div>';
        monthRows.push({ cells: [key, fmtHM(freeMinutes), String(merged.length), String(unverified), statusBadge(unverified ? 'UNVERIFIED BLOCK' : merged.length ? 'GAME DAY' : 'FREE DAY — UNVERIFIED FUTURE')], sourceRow });
      }
      html += '</div>';
      html += '<section class="panel"><h2>Month analysis</h2><p class="intro">Gap minutes are complements of modeled intervals, not confirmed availability. Pacific wall-clock minutes; DST days have 23 or 25 elapsed hours.</p>' + dynamicTable(['Date','Free minutes','Merged busy blocks','Unverified blocks','Status'], monthRows) + '</section>';
      holder.innerHTML = html;
    } catch (err) {
      holder.innerHTML = '<div class="callout danger"><strong>Data load failed.</strong> ' + esc(err.message) + '</div>';
    }
  }
  function initCalendar() {
    const yearSel = document.getElementById('calendar-year'), monthSel = document.getElementById('calendar-month');
    if (!yearSel || !monthSel) return;
    const today = todayPacific();
    yearSel.value = today.slice(0,4); monthSel.value = String(Number(today.slice(5,7))-1);
    function reload() { renderCalendar(Number(yearSel.value), Number(monthSel.value)); }
    yearSel.addEventListener('change', reload); monthSel.addEventListener('change', reload);
    document.getElementById('calendar-prev').addEventListener('click', () => { let y=Number(yearSel.value), m=Number(monthSel.value)-1; if(m<0){m=11;y--;} yearSel.value=y; monthSel.value=m; reload(); });
    document.getElementById('calendar-next').addEventListener('click', () => { let y=Number(yearSel.value), m=Number(monthSel.value)+1; if(m>11){m=0;y++;} yearSel.value=y; monthSel.value=m; reload(); });
    reload();
  }
  function initTables() {
    document.querySelectorAll('.table-wrap[data-table]').forEach(wrap => {
      const rows = Array.from(wrap.querySelectorAll('tbody tr'));
      const search = wrap.querySelector('input[type="search"]');
      const prev = wrap.querySelector('[data-page-prev]');
      const next = wrap.querySelector('[data-page-next]');
      const label = wrap.querySelector('.pager-label');
      const statusButtons = Array.from(wrap.querySelectorAll('[data-status-filter]'));
      const pageSize = Number(wrap.dataset.pageSize || 100);
      let page = 1, query = '', statusFilter = '';
      function visibleRows() {
        return rows.filter(r => {
          const text = (r.dataset.rowText || r.textContent || '').toLowerCase();
          const status = (r.dataset.rowStatus || '').toLowerCase();
          return (!query || text.includes(query)) && (!statusFilter || status.includes(statusFilter));
        });
      }
      function draw() {
        const visible = visibleRows(), pages = Math.max(1, Math.ceil(visible.length / pageSize));
        page = Math.max(1, Math.min(page, pages));
        rows.forEach(r => r.style.display = 'none');
        visible.slice((page-1)*pageSize, page*pageSize).forEach(r => r.style.display = '');
        label.textContent = 'Page ' + page + ' / ' + pages + ' · ' + visible.length + ' rows';
        prev.disabled = page <= 1; next.disabled = page >= pages;
      }
      search?.addEventListener('input', () => { query = search.value.toLowerCase().trim(); page = 1; draw(); });
      prev?.addEventListener('click', () => { page--; draw(); });
      next?.addEventListener('click', () => { page++; draw(); });
      statusButtons.forEach(b => b.addEventListener('click', () => {
        statusFilter = b.dataset.statusFilter === statusFilter ? '' : b.dataset.statusFilter.toLowerCase();
        statusButtons.forEach(x => x.classList.toggle('control-btn', x === b && !!statusFilter));
        page = 1; draw();
      }));
      draw();
    });
  }
  document.addEventListener('DOMContentLoaded', () => { initTables(); initDaily(); initCalendar(); });
})();
