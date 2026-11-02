import assert from 'node:assert/strict';
import {addDays, buildIndex, dayBounds, findCandidates, pacificDay, summarizeDay, union} from '../site/planner/core.js';

assert.equal((dayBounds('2027-03-14')[1] - dayBounds('2027-03-14')[0])/36e5, 23, 'spring DST day');
assert.equal((dayBounds('2027-11-07')[1] - dayBounds('2027-11-07')[0])/36e5, 25, 'fall DST day');
assert.equal(pacificDay(Date.parse('2027-02-16T03:00:00Z')), '2027-02-15');
assert.equal(addDays('2028-02-28', 1), '2028-02-29');
assert.deepEqual(union([{start: 1, end: 5}, {start: 3, end: 8}, {start: 8, end: 9}]), [{start: 1, end: 9}]);
const idx = buildIndex({events: [
  {id: 'a', date: '2027-02-15', start: '2027-02-16T03:00:00Z', durationMinutes: 150},
  {id: 'b', date: '2027-02-17', start: '2027-02-18T03:00:00Z', durationMinutes: 150},
  {id: 'unknown', date: '2027-03-02', start: null, possibleOffsetDays: [-1, 0, 1]},
  {id: 'noend', date: '2027-03-05', start: '2027-03-05T20:00:00Z'}
], restrictions: [{id: 'allstar', startDate:'2028-07-01', endDate:'2028-08-01'}]});
assert.equal(summarizeDay(idx, '2027-03-01').uncertain, true);
assert.equal(summarizeDay(idx, '2027-03-03').gaps.length, 0);
assert.equal(summarizeDay(idx, '2027-03-05').uncertain, true, 'unknown end is not invented');
assert.equal(summarizeDay(idx, '2028-07-31').uncertain, true);
assert.equal(summarizeDay(idx, '2028-08-01').uncertain, false);
assert(!findCandidates(idx, 2027, 7).some(c => c.start <= '2027-02-15' && c.end >= '2027-02-15'));
console.log('Pacific time, interval union, TBD and candidate tests passed.');
