import assert from 'node:assert/strict';
import {readFileSync,existsSync} from 'node:fs';
import vm from 'node:vm';
const ctx=vm.createContext({Intl,Date,console,window:{},document:{querySelector:()=>null},fetch});
vm.runInContext(readFileSync('assets/data.js','utf8'),ctx);
ctx.EVENTS=ctx.window.EVENTS;
vm.runInContext(readFileSync('assets/app.js','utf8'),ctx);
const evalIn=s=>vm.runInContext(s,ctx);
assert.equal(evalIn("new Date(midnight('2027-03-14')).toISOString()"),'2027-03-14T08:00:00.000Z');
assert.equal(evalIn("new Date(midnight('2027-03-15')).toISOString()"),'2027-03-15T07:00:00.000Z');
assert.equal(evalIn("(midnight('2027-11-08')-midnight('2027-11-07'))/3600000"),25);
assert.equal(evalIn("shiftDay('2028-02-28', 1)"),'2028-02-29');
assert.equal(evalIn("shiftDay('2028-12-31', 1)"),'2029-01-01');
ctx.sample={dates:[{games:[{gamePk:123,gameDate:'2027-03-25T07:33:00Z',officialDate:'2027-03-25',publicFacing:true,status:{startTimeTBD:true},teams:{away:{team:{id:133,name:'Athletics'}},home:{team:{id:134,name:'Pittsburgh Pirates'}}}}]}]};
assert.equal(evalIn('parseMLB(sample)[0].start'),undefined);
assert.equal(evalIn('parseMLB(sample)[0].date'),'2027-03-25');
assert.equal(evalIn('parseMLB(sample)[0].priority'),true);
assert.equal(evalIn("current='2026-11-08'; intervals([{start:'2026-11-08T13:00:00-08:00',length:180},{start:'2026-11-08T15:00:00-08:00',length:180}]).length"),2);
assert.equal(evalIn("current='2026-11-09'; listForDay().some(e=>e.title.includes('Buffalo Bills at Minnesota Vikings'))"),true);
assert.equal(evalIn("current='2026-11-21'; listForDay().some(e=>e.title==='Stanford at California' && e.date==='2026-11-21')"),true);
assert.equal(evalIn("EVENTS.every(e=>e.source && (e.start || e.date) && (!e.start || e.length > 0))"),true);
for(const page of ['index.html','vacation.html','sources.html','review.html']){
 const html=readFileSync(page,'utf8'); assert.match(html,/<html lang="en">/);
 for(const [,link] of html.matchAll(/(?:href|src)="([^"]+)"/g)) if(!/^(https?:|#|mailto:)/.test(link)) assert.ok(existsSync(link),`${page}: broken local link ${link}`);
 assert.ok(html.includes('Flagged for review'));
}
console.log('All schedule, DST, TBD, source and local-link checks passed.');
