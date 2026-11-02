/* app.js — UI logic for Free Time Vacation (Bay Area sports radio) */
'use strict';
const DOWS=['Sunday','Monday','Tuesday','Wednesday','Thursday','Friday','Saturday'];
const MONS=['January','February','March','April','May','June','July','August','September','October','November','December'];
function pretty(s){ const d=parseD(s); return DOWS[d.getUTCDay()]+', '+MONS[d.getUTCMonth()]+' '+d.getUTCDate()+', '+d.getUTCFullYear(); }
function prettyShort(s){ const d=parseD(s); return MONS[d.getUTCMonth()].slice(0,3)+' '+d.getUTCDate()+', '+d.getUTCFullYear(); }
function esc(t){ return String(t).replace(/&/g,'&amp;').replace(/</g,'&lt;'); }
function badge(st){ return st==='V'?'<span class="badge V">VERIFIED</span>':'<span class="badge E">ESTIMATE</span>'; }
function optFromUI(){
  const o={other:false,oly28:false};
  const a=document.getElementById('optOther'), b=document.getElementById('optOly');
  if(a)o.other=a.checked; if(b)o.oly28=b.checked;
  return o;
}

/* ---------------- day view ---------------- */
function renderDay(s){
  const opts=optFromUI();
  if(s<MODEL_START)s=MODEL_START; if(s>MODEL_END)s=MODEL_END;
  const blocks=dayBlocks(s,opts), merged=mergeBlocks(blocks), free=freeWindows(s,opts);
  const busy=busyMinutes(s,opts), cls=classify(s,opts);
  const el=document.getElementById('dayview'); if(!el)return;
  document.getElementById('datepick').value=s;
  const verdictTxt = cls==='free' ? '✅ FULLY FREE — nothing on the radio in your must-hear set today'
    : cls==='light' ? '🟡 LIGHT DAY — only '+(Math.floor(busy/60))+ 'h '+String(busy%60).padStart(2,'0')+'m on air'
    : '🔴 BUSY — '+Math.floor(busy/60)+'h '+String(busy%60).padStart(2,'0')+'m of games on the radio';
  let h='<div class="dayhead"><span class="dow">'+pretty(s)+'</span><span class="verdict '+cls+'">'+verdictTxt+'</span></div>';
  if(s===TODAY)h+='<p class="note">← This is today (in America/Los_Angeles date terms for SF 94122).</p>';
  /* timeline 5:00 AM → midnight */
  const T0=hm(5,0), T1=1440;
  h+='<div class="timeline">';
  for(const [a,b] of free){ const L=Math.max(a,T0); h+='<div class="freeblk" style="left:'+((L-T0)/(T1-T0)*100)+'%;width:'+((b-L)/(T1-T0)*100)+'%"></div>'; }
  for(const b of blocks){ const L=Math.max(b.s,T0), R=Math.min(b.e,T1); if(R>L)h+='<div class="blk'+(b.hp?' hpblk':'')+'" title="'+esc(b.t)+' ('+mm(b.s)+'–'+mm(b.e)+' PT)" style="left:'+((L-T0)/(T1-T0)*100)+'%;width:'+((R-L)/(T1-T0)*100)+'%"></div>'; }
  h+='</div><div class="hourlabels">';
  for(let hr=5;hr<=24;hr+=3){ h+='<span style="left:'+((hr*60-T0)/(T1-T0)*100)+'%">'+mm(hr*60%1440)+'</span>'; }
  h+='</div>';
  h+='<h3>🎧 Free time today (no must-hear game on air)</h3>';
  if(free.length===0) h+='<p>No free window between 6:00 AM and midnight.</p>';
  else { h+='<ul class="freelist">'; for(const [a,b] of free)h+='<li>'+mm(a)+' – '+mm(b===1440?0:b).replace('12:00 AM','Midnight')+' PT &nbsp;<span class="note">('+(Math.floor((b-a)/60))+'h '+String((b-a)%60).padStart(2,'0')+'m free)</span></li>'; h+='</ul>'; }
  h+='<p class="note">Windows use average game lengths (MLB 2:38 · NFL ~3:10 incl. 12-min halftime · NCAAF 3:26 incl. 20-min halftime). Halftime itself is part of the broadcast and is <b>not</b> shown as free time. Radio pregame shows usually begin ~30 min before first pitch/kickoff (Westwood One listed times already include pregame).</p>';
  h+='<h3>📻 On the radio today</h3>';
  if(blocks.length===0)h+='<p>Nothing from your must-hear set is on Bay Area radio today.</p>';
  for(const b of blocks){
    h+='<div class="evt'+(b.hp?' hp':'')+'"><span class="when">'+mm(b.s)+' – '+mm(b.e%1440)+' PT</span> · '+(CAT_LABEL[b.cat]||b.cat)+(b.hp?' <span class="badge hp">★ HIGH PRIORITY</span>':'')+' '+badge(b.st)+'<br>'+esc(b.t)+'<span class="src">Source: '+esc(b.src||'')+'</span></div>';
  }
  const adv=advisories(s);
  if(adv.length && !opts.other){
    h+='<div class="infobox"><b>Also around the dial (not in your must-hear set):</b><ul style="margin:6px 0 2px">';
    for(const a of adv)h+='<li>'+esc(a.t)+' '+badge(a.st)+'</li>';
    h+='</ul></div>';
  }
  h+='<p class="note">Tip: use ◀ Yesterday / Tomorrow ▶ or tap any day in the month grid below.</p>';
  el.innerHTML=h;
  renderMonth(s,opts);
  el.dataset.date=s;
  try{ history.replaceState(null,'','#'+s); }catch(e){}
}

/* ---------------- month grid ---------------- */
function renderMonth(sel,opts){
  const el=document.getElementById('monthview'); if(!el)return;
  const d=parseD(sel), y=d.getUTCFullYear(), mo=d.getUTCMonth();
  const first=dstr(y,mo+1,1);
  let start=first; while(dow(start)!==0)start=addDays(start,-1);
  let h='<div class="controls"><button onclick="monthNav(-1)">◀ Prev month</button><b style="font-size:18px">'+MONS[mo]+' '+y+'</b><button onclick="monthNav(1)">Next month ▶</button></div>';
  h+='<div class="monthcal">';
  for(const n of ['S','M','T','W','T','F','S'])h+='<div class="hd">'+n+'</div>';
  let s=start;
  for(let i=0;i<42;i++){
    const inMonth = parseD(s).getUTCMonth()===mo;
    const inRange = s>=MODEL_START && s<=MODEL_END;
    const c = inRange? classify(s,opts):'dim';
    const busy= inRange? busyMinutes(s,opts):0;
    h+='<div class="cell '+c+(inMonth?'':' dim')+(s===TODAY?' today':'')+(s===sel?' sel':'')+'" '+(inRange?('onclick="renderDay(\''+s+'\')"'):'')+'><div class="n">'+parseD(s).getUTCDate()+'</div>'+(inRange? (c==='free'?'FREE':(Math.round(busy/60*10)/10)+'h on air'):'')+'</div>';
    s=addDays(s,1);
  }
  h+='</div>';
  /* month summary */
  const last=dstr(y,mo+1,new Date(Date.UTC(y,mo+1,0)).getUTCDate());
  const a = first<MODEL_START?MODEL_START:first, b = last>MODEL_END?MODEL_END:last;
  if(a<=b){
    const st=rangeStats(a,b,opts);
    h+='<p class="note"><b>'+MONS[mo]+' '+y+':</b> '+st.free+' fully-free days, '+st.light+' light days (≤3.5 h on air). Longest free streak this month: '+(findStreaks(a,b,1,opts)[0]? findStreaks(a,b,1,opts)[0].len+' day(s)':'none')+'.</p>';
  }
  el.innerHTML=h;
}
function monthNav(dir){
  const cur=document.getElementById('dayview').dataset.date||TODAY;
  const d=parseD(cur); d.setUTCMonth(d.getUTCMonth()+dir);
  let s=fmt(d); if(s<MODEL_START)s=MODEL_START; if(s>MODEL_END)s=MODEL_END;
  renderDay(s);
}
function dayNav(dir){
  const cur=document.getElementById('dayview').dataset.date||TODAY;
  renderDay(addDays(cur,dir));
}
function goToday(){ renderDay(TODAY<MODEL_START?MODEL_START:(TODAY>MODEL_END?MODEL_END:TODAY)); }

/* ---------------- vacation page (computed live from the same model) ---------------- */
function renderVacation(){
  const host=document.getElementById('vac-computed'); if(!host)return;
  const opts=optFromUI();
  let h='';
  for(const yr of [2027,2028,2029]){
    const a=yr+'-01-01', b=yr+'-12-31';
    const streaks=findStreaks(a,b,2,opts);
    h+='<h3>'+yr+' — fully-free streaks (2+ consecutive days, zero must-hear games)</h3>';
    if(streaks.length===0)h+='<p>None found in the model.</p>';
    else{
      h+='<table><thead><tr><th>Window</th><th>Length</th><th>What bounds it</th></tr></thead><tbody>';
      for(const st of streaks.slice(0,6)){
        let note='';
        if(st.start.endsWith('-02-15')||st.start>=yr+'-02-12'&&st.start<=yr+'-02-16')note='Day after Super Bowl → day before first Spring Training games';
        else if(st.start>yr+'-07-08'&&st.start<yr+'-07-22')note='All-Star break dark day(s)' + (yr===2028&&opts.oly28?' + conditional Olympic break (scenario ON)':'');
        h+='<tr><td><b>'+prettyShort(st.start)+' – '+prettyShort(st.end)+'</b></td><td>'+st.len+' days</td><td>'+note+'</td></tr>';
      }
      h+='</tbody></table>';
    }
    for(const L of [7,14,21]){
      const best=bestWindows(a,b,L,opts,3);
      h+='<p><b>Least-conflict '+L+'-day windows in '+yr+'</b> (if you accept some games on air):</p><table><thead><tr><th>Window ('+L+' days)</th><th>Must-hear hours on air during it</th><th>Fully-free days inside</th><th>light days inside</th></tr></thead><tbody>';
      for(const w of best)h+='<tr><td>'+prettyShort(w.start)+' – '+prettyShort(w.end)+'</td><td>'+(Math.round(w.busyMin/60*10)/10)+' h</td><td>'+w.freeDays+'</td><td>'+w.lightDays+'</td></tr>';
      h+='</tbody></table>';
    }
  }
  host.innerHTML=h;
}

/* ---------------- dashboard widgets ---------------- */
function renderDashboard(){
  const t=document.getElementById('dash-today'); if(!t)return;
  const s=TODAY<MODEL_START?MODEL_START:(TODAY>MODEL_END?MODEL_END:TODAY);
  const opts={other:false,oly28:false};
  const busy=busyMinutes(s,opts), free=freeWindows(s,opts), cls=classify(s,opts);
  let h='<p><b>'+pretty(s)+'</b> — <span class="verdict '+cls+'">'+(cls==='free'?'FULLY FREE':cls==='light'?'light DAY':'BUSY')+'</span></p>';
  if(free.length)h+='<p>Free today: '+free.map(([a,b])=>'<b>'+mm(a)+'–'+mm(b%1440)+'</b>').join(', ')+' PT.</p>';
  else h+='<p>No free window today between 6 AM and midnight.</p>';
  /* next fully-free day */
  let s2=s, found=null;
  for(let i=0;i<1200;i++){ if(busyMinutes(s2,opts)===0){found=s2;break;} s2=addDays(s2,1); if(s2>MODEL_END)break; }
  if(found)h+='<p>Next fully-free day: <b>'+pretty(found)+'</b>.</p>';
  const kpis=document.getElementById('dash-kpis');
  if(kpis){
    const y27=rangeStats('2027-01-01','2027-12-31',opts);
    const top27=findStreaks('2027-01-01','2027-12-31',1,opts)[0];
    kpis.innerHTML =
      '<div class="k"><div class="v">'+(top27?top27.len:0)+' days</div><div class="l">Longest STRICT zero-conflict stretch in 2027 (computed; first: '+(top27?prettyShort(top27.start)+'–'+prettyShort(top27.end):'—')+'; playoff-corridor estimates)</div></div>'+
      '<div class="k"><div class="v">Feb 15–18 \'27</div><div class="l">Only window VERIFIED on both sides (Super Bowl LXI → first Spring Training games)</div></div>'+
      '<div class="k"><div class="v">9 days*</div><div class="l">*Conditional best: Jul 12–20, 2028 IF MLB finalizes the extended Olympic break (not final)</div></div>'+
      '<div class="k"><div class="v">'+y27.free+' / 365</div><div class="l">Fully-free days in 2027 under Core-4 rules (plus '+y27.light+' light days ≤3.5 h)</div></div>';
  }
  t.innerHTML=h;
}

/* ---------------- init ---------------- */
document.addEventListener('DOMContentLoaded',function(){
  renderDashboard();
  renderVacation();
  const el=document.getElementById('dayview');
  if(el){
    let s=(location.hash||'').replace('#','');
    if(!/^\d{4}-\d{2}-\d{2}$/.test(s)) s=TODAY;
    renderDay(s);
    document.getElementById('datepick').addEventListener('change',function(){ renderDay(this.value); });
    const dp=document.getElementById('datepick'); dp.min=MODEL_START; dp.max=MODEL_END;
  }
  for(const id of ['optOther','optOly']){
    const c=document.getElementById(id);
    if(c)c.addEventListener('change',function(){
      if(el)renderDay(el.dataset.date||TODAY);
      renderVacation();
    });
  }
});
