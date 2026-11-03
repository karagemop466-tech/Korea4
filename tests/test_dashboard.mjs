import assert from 'node:assert/strict';
import fs from 'node:fs';
import vm from 'node:vm';

const code = fs.readFileSync('js/app.js', 'utf8').replace(
  "  document.addEventListener('DOMContentLoaded', () => { initTables(); initDaily(); initCalendar(); });",
  '  globalThis.dashboardTest = { pacificToday, statusBadge, adjustedIntervals, freeWindows, mergeIntervals };'
);
const ctx = { window: {}, document: {}, Intl, Date };
vm.runInNewContext(code, ctx);
const t = ctx.dashboardTest;
assert.equal(t.pacificToday(new Date('2027-01-01T07:59:00Z')), '2026-12-31');
assert.equal(t.pacificToday(new Date('2027-01-01T08:00:00Z')), '2027-01-01');
assert.equal(t.pacificToday(new Date('2027-07-01T06:59:00Z')), '2027-06-30');
assert.match(t.statusBadge('ESTIMATED — NOT A REAL VERIFIED RELEASED SCHEDULE'), /badge-estimated/);
assert.match(t.statusBadge('ESTIMATED / UNVERIFIED'), /badge-unverified/);
assert.match(t.statusBadge('VERIFIED — official kickoff'), /badge-verified/);
const clipped = [{start: 0, end: 40, category: 'MLB', status: 'OFFICIAL_START_ESTIMATED_DURATION'}];
assert.equal(t.adjustedIntervals(clipped)[0].end, 40);
assert.equal(t.freeWindows(t.mergeIntervals([{start: 60, end: 120}, {start: 100, end: 150}]))[1].start, 150);
console.log('Dashboard date, labels, intervals and cross-midnight regression tests passed.');
