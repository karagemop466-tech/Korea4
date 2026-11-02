// Dev test for docs/data.js — run from repo root:  node tools/test-engine.cjs
const fs=require('fs'), cp=require('child_process'), os=require('os'), path=require('path');
const self=fs.readFileSync(__filename,'utf8');
const marker='// =====TEST BODY BELOW=====';
const body=self.slice(self.lastIndexOf(marker)+marker.length);
const tmp=path.join(os.tmpdir(),'ftv-test.js');
fs.writeFileSync(tmp, fs.readFileSync(path.join(__dirname,'..','docs','data.js'),'utf8') + body);
process.exit(cp.spawnSync(process.execPath,[tmp],{stdio:'inherit'}).status||0);
// =====TEST BODY BELOW=====
let fail=0;
function chk(name,cond){ console.log((cond?'PASS':'FAIL')+' | '+name); if(!cond) fail++; }
const O={};
chk('launch day 2026-11-02 busy (Westwood One MNF)', busyMinutes('2026-11-02',O)>0);
chk('2026-11-07 Stanford+Cal bye -> Core free; busy with other-tier', busyMinutes('2026-11-07',O)===0 && busyMinutes('2026-11-07',{other:true})>0);
chk('SB LXI 2027-02-14 busy', busyMinutes('2027-02-14',O)>0);
chk('2027-02-15..18 free (verified window)', ['2027-02-15','2027-02-16','2027-02-17','2027-02-18'].every(d=>busyMinutes(d,O)===0));
chk('2027-02-19 busy (spring training)', busyMinutes('2027-02-19',O)>0);
chk('2027-07-14 free / 07-13 light', busyMinutes('2027-07-14',O)===0 && classify('2027-07-13',O)==='light');
chk('2028-07-15 free only with Olympic scenario', busyMinutes('2028-07-15',O)>0 && busyMinutes('2028-07-15',{oly28:true})===0);
chk('2027 top streak = 6 days; 2027 has 66 free days', findStreaks('2027-01-01','2027-12-31',1,O)[0].len===6 && rangeStats('2027-01-01','2027-12-31',O).free===66);
let d=MODEL_START, errs=0;
while(d<=MODEL_END){ try{ dayBlocks(d,O); dayBlocks(d,{other:true,oly28:true}); }catch(e){ errs++; } d=addDays(d,1); }
chk('all model days compute', errs===0);
process.exit(fail?1:0);
