import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import vm from 'node:vm';
const els=new Map();
function el(key){if(!els.has(key))els.set(key,{textContent:'',innerHTML:'',value:'',className:'',classList:{toggle(){}},querySelectorAll:()=>[]});return els.get(key)}
const ctx=vm.createContext({Intl,Date,console,window:{},document:{querySelector:el,querySelectorAll:()=>[]},fetch:async()=>({ok:true,json:async()=>({dates:[]})})});
vm.runInContext(readFileSync('assets/data.js','utf8'),ctx);ctx.EVENTS=ctx.window.EVENTS;
vm.runInContext(readFileSync('assets/app.js','utf8'),ctx);
await new Promise(resolve=>setTimeout(resolve,0));
assert.equal(el('#feed-status').textContent,'MLB feed connected');
assert.match(el('#coverage').textContent,/incomplete/);
await vm.runInContext("current='2026-11-21'; load()",ctx);
assert.match(el('#game-rows').innerHTML,/Stanford at California/);
assert.match(el('#windows').innerHTML,/cannot be calculated/);
ctx.fetch=async()=>{throw Error('offline')};
await vm.runInContext("current='2027-03-25'; load()",ctx);
assert.equal(el('#feed-status').textContent,'MLB feed unavailable');
assert.match(el('#windows').innerHTML,/cannot be calculated/);
console.log('UI states, TBD and failed-feed handling passed.');
