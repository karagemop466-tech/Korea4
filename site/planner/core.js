/** Source-aware date arithmetic and interval union, always in Pacific time. */
export const ZONE = 'America/Los_Angeles';
const partFormatter = new Intl.DateTimeFormat('en-US', {
  timeZone: ZONE, year: 'numeric', month: '2-digit', day: '2-digit',
  hour: '2-digit', minute: '2-digit', second: '2-digit', hourCycle: 'h23'
});
const partValues = ms => Object.fromEntries(partFormatter.formatToParts(new Date(ms)).filter(p => p.type !== 'literal').map(p => [p.type, Number(p.value)]));
const pad = n => String(n).padStart(2, '0');
export function pacificDay(ms) {
  const p = partValues(ms);
  return `${p.year}-${pad(p.month)}-${pad(p.day)}`;
}
export function addDays(day, amount) {
  const [y, m, d] = day.split('-').map(Number);
  return new Date(Date.UTC(y, m - 1, d + amount, 12)).toISOString().slice(0, 10);
}
export function localMidnight(day) {
  const [year, month, date] = day.split('-').map(Number);
  const desired = Date.UTC(year, month - 1, date);
  let guess = desired;
  for (let i = 0; i < 5; i++) {
    const p = partValues(guess);
    const represented = Date.UTC(p.year, p.month - 1, p.day, p.hour, p.minute, p.second);
    const next = guess + desired - represented;
    if (next === guess) break;
    guess = next;
  }
  return guess;
}
export function dayBounds(day) { return [localMidnight(day), localMidnight(addDays(day, 1))]; }
export function dayLabel(day, opts = {weekday: 'long', month: 'long', day: 'numeric', year: 'numeric'}) {
  // Noon UTC is safely on the same civil date in this zone.
  return new Intl.DateTimeFormat('en-US', {...opts, timeZone: ZONE}).format(new Date(`${day}T20:00:00Z`));
}
export function timeLabel(ms) {
  return new Intl.DateTimeFormat('en-US', {hour: 'numeric', minute: '2-digit', timeZone: ZONE}).format(new Date(ms));
}
export function zoneLabel(ms = Date.now()) {
  return new Intl.DateTimeFormat('en-US', {timeZone: ZONE, timeZoneName: 'short'}).formatToParts(new Date(ms)).find(p => p.type === 'timeZoneName')?.value || 'PT';
}
export function intervalFor(event) {
  if (!event.start) return null;
  const start = Date.parse(event.start);
  const end = event.end ? Date.parse(event.end) : start + (Number(event.durationMinutes) || 0) * 60_000;
  if (!Number.isFinite(start)) return null;
  // An unknown end is not replaced with a fictitious duration.
  return {start, end: Number.isFinite(end) && end > start ? end : null};
}
export function buildIndex(data) {
  const index = new Map();
  const put = (day, e) => {
    if (!day || day < '2026-01-01' || day > '2029-12-31') return;
    if (!index.has(day)) index.set(day, []);
    if (!index.get(day).some(x => x.id === e.id)) index.get(day).push(e);
  };
  for (const event of data.events || []) {
    const interval = intervalFor(event);
    if (interval) {
      const first = pacificDay(interval.start);
      const last = interval.end ? pacificDay(interval.end - 1) : first;
      let day = first;
      for (let i = 0; i < 3 && day <= last; i++, day = addDays(day, 1)) put(day, event);
    } else if (event.date) {
      for (const offset of event.possibleOffsetDays || [0]) put(addDays(event.date, offset), event);
    }
  }
  for (const restriction of data.restrictions || []) {
    let day = restriction.startDate;
    for (let i = 0; i < 370 && day < restriction.endDate; i++, day = addDays(day, 1)) {
      put(day, {...restriction, sport: 'REVIEW', group: 'restriction', category: 'Schedule window', start: null, date: restriction.startDate, priority: true});
    }
  }
  return index;
}
export function union(intervals) {
  const sorted = intervals.filter(x => x.end > x.start).sort((a, b) => a.start - b.start || a.end - b.end);
  const merged = [];
  for (const item of sorted) {
    const last = merged.at(-1);
    if (last && item.start <= last.end) last.end = Math.max(last.end, item.end);
    else merged.push({...item});
  }
  return merged;
}
export function summarizeDay(index, day) {
  const events = index.get(day) || [];
  const [start, end] = dayBounds(day);
  const uncertain = events.some(e => !e.start || !intervalFor(e)?.end);
  const occupied = union(events.map(intervalFor).filter(x => x && x.end).map(x => ({start: Math.max(start, x.start), end: Math.min(end, x.end)})));
  const gaps = [];
  if (!uncertain) {
    let cursor = start;
    for (const item of occupied) {
      if (cursor < item.start) gaps.push({start: cursor, end: item.start});
      cursor = Math.max(cursor, item.end);
    }
    if (cursor < end) gaps.push({start: cursor, end});
  }
  return {events, uncertain, occupied, gaps, start, end};
}
export function findCandidates(index, year, length) {
  const result = [];
  let first = null, run = 0;
  for (let day = `${year}-01-01`; day < `${year + 1}-01-01`; day = addDays(day, 1)) {
    if (!(index.get(day) || []).length) {
      if (!first) first = day;
      run++;
    } else {
      if (run >= length) result.push({start: first, end: addDays(first, length - 1), run});
      first = null; run = 0;
    }
  }
  if (run >= length) result.push({start: first, end: addDays(first, length - 1), run});
  return result;
}
