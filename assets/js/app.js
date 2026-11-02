// FREE TIME VACATION - Dashboard + Calendar logic
const TZ = 'America/Los_Angeles';
const isDST = (d) => {
  const jan = new Date(d.getFullYear(),0,1).getTimezoneOffset();
  const jul = new Date(d.getFullYear(),6,1).getTimezoneOffset();
  return d.getTimezoneOffset() < Math.max(jan,jul);
};

function fmtPST(d){
  return d.toLocaleDateString('en-US',{timeZone:TZ, weekday:'short', month:'short', day:'numeric', year:'numeric'});
}
function todayPST(){
  const now = new Date();
  const pstStr = now.toLocaleDateString('en-CA',{timeZone:TZ});
  return new Date(pstStr+"T12:00:00");
}
let current = todayPST();

document.addEventListener('DOMContentLoaded',()=>{
  document.getElementById('today-label').textContent = fmtPST(new Date());
  document.getElementById('tz-label').textContent = new Date().toLocaleTimeString('en-US',{timeZone:TZ, timeZoneName:'short'}).split(' ').pop() + " • PST/PDT auto";
  // preview timeline: Feb 9-22 2026
  renderPreview();
  initCalendar();
  updateNowStatus();
  setInterval(updateNowStatus, 60000);
});

function renderPreview(){
  const el = document.getElementById('timeline-preview');
  if(!el) return;
  const days = [
    {date:'2026-02-08 Sun', label:'Super Bowl LX • last busy day', type:'busy', busy:'NFL/WW1 3:30-8pm PT'},
    {date:'2026-02-09 Mon', label:'FREE — no games', type:'free', free:'All day free'},
    {date:'2026-02-10 Tue', label:'FREE', type:'free'},
    {date:'2026-02-11 Wed', label:'FREE', type:'free'},
    {date:'2026-02-12 Thu', label:'FREE', type:'free'},
    {date:'2026-02-13 Fri', label:'FREE', type:'free'},
    {date:'2026-02-14 Sat', label:'FREE', type:'free'},
    {date:'2026-02-15 Sun', label:'FREE — 7 days straight', type:'free', free:'7-day window ✓'},
    {date:'2026-02-16 Mon', label:'FREE', type:'free'},
    {date:'2026-02-22 Sun', label:'FREE — 14 days straight', type:'free', free:'Best 14-day ✓'},
    {date:'2026-02-24 Tue', label:'Busy again', type:'busy', busy:'MLB spring training starts'},
  ];
  el.innerHTML = days.map(d=>`
    <div class="day ${d.type}">
      <div class="date">${d.date}<small>${d.type==='free' ? 'no radio sports' : d.busy}</small></div>
      <div class="bar">${d.type==='free'? '<i class="free" style="left:0;right:0"></i>' : '<i class="nfl" style="left:30%;right:20%"></i><i class="ww" style="left:55%;right:10%;opacity:.8"></i>'}</div>
      <div class="small ${d.type==='free'?'':'muted'}" style="text-align:right;font-weight:700">${d.free||''}${d.busy||''}</div>
    </div>
  `).join('');
}

// Schedule DB for intraday logic: we use simplified model per day type
// In 2026: Jan 10-Feb 8 = NFL playoffs (busy Thu/Sun/Mon nights); Feb 9-23 = free; Feb24-Mar24 = MLB spring (busy afternoons); Mar25-Sep27 = MLB daily busy; Jul13-16 = MLB All-Star free; Sep10-Jan = NFL+MLB overlap busy; Oct-Nov-Dec = NFL+NCAAF busy.
function getDayInfo(date){
  const iso = date.toISOString().slice(0,10);
  const d = new Date(iso+"T12:00:00");
  const dayName = d.toLocaleDateString('en-US',{timeZone:TZ, weekday:'short'});
  // helper
  const isWeekend = d.getDay()===0 || d.getDay()===6;

  // 2026 logic
  if(iso >= "2026-01-10" && iso <= "2026-02-08"){
    // NFL playoffs - primetime nights
    const dow = d.getDay();
    if(dow===0 || dow===1 || dow===4 || dow===6){ // Sun, Mon, Thu, Sat during playoffs
      return {busy:true, leagues:['NFL','Westwood One'], blocks:[{label:'NFL Playoffs / WW1', start:'1:00 PM', end:'9:30 PM', type:'nfl'}], freeSlices:['Free 6:00 AM – 1:00 PM'], note:'Playoffs — national radio every gameday night.'};
    }
    return {busy:false, freeSlices:['All day free — no games'], leagues:[]};
  }
  if(iso >= "2026-02-09" && iso <= "2026-02-23"){
    return {busy:false, freeSlices:['All day free — best vacation window'], leagues:[], note:'Post-Super Bowl → pre-spring training. Verified free.'};
  }
  if(iso >= "2026-02-24" && iso <= "2026-03-24"){
    return {busy:true, leagues:['MLB (Spring)'], blocks:[{label:'MLB Spring Training (SF/ATH)', start:'12:05 PM', end:'3:30 PM', type:'mlb'}], freeSlices:['Free 6:00 AM – 12:05 PM, 3:30 PM – midnight'], note:'Spring training counts as busy per your rule (preseason). Ignore it to get 5 weeks free.'};
  }
  if(iso >= "2026-03-25" && iso <= "2026-09-27" && !(iso >= "2026-07-13" && iso <= "2026-07-16")){
    // MLB season daily, plus NFL from Sep 10
    let blocks = [{label:'MLB (all 30 clubs)', start:'10:35 AM', end:'10:30 PM', type:'mlb', note:'Many games overlap; Giants & A\'s priority.'}];
    let leagues = ['MLB'];
    if(iso >= "2026-09-10"){
      leagues.push('NFL','Westwood One');
      // add NFL block on specific NFL days
      const nflDays = ["2026-09-10","2026-09-20","2026-09-27","2026-10-04","2026-10-11","2026-10-19","2026-10-25","2026-11-08","2026-11-15","2026-11-22","2026-11-29","2026-12-06","2026-12-13","2026-12-17","2026-12-27","2027-01-03"];
      if(nflDays.includes(iso)){
        blocks.push({label:'NFL 49ers (+ Westwood One)', start: iso==="2026-09-10" ? '5:35 PM' : iso==="2026-10-19" ? '5:15 PM' : '1:00 PM', end:'8:30 PM', type:'nfl'});
      } else if(["2026-09-11","2026-09-14","2026-09-21","2026-09-28"].includes(iso)){
        blocks.push({label:'Westwood One SNF/MNF/TNF', start:'5:15 PM', end:'9:00 PM', type:'ww'});
      }
      leagues.push('NCAAF');
      // NCAAF Sat
      if(d.getDay()===6 && iso >= "2026-09-05" && iso <= "2026-11-28"){
        blocks.push({label:'NCAAF Cal/Stanford', start:'12:00 PM', end:'4:00 PM', type:'ncaaf'});
        leagues.push('NCAAF');
      }
    } else {
      // summer: also NCAAF not yet, but WW not
      if(d.getDay()===6 && iso >= "2026-09-05"){
        blocks.push({label:'NCAAF Cal/Stanford', start:'12:00 PM', end:'4:00 PM', type:'ncaaf'});
        leagues.push('NCAAF');
      }
    }
    return {busy:true, leagues, blocks, freeSlices:['Free ~6:00 AM – 10:35 AM (mornings)','Free late night after 10:30 PM'], note:'MLB daily → no full free days Mar 25–Sep 27 (except All-Star break).'};
  }
  if(iso >= "2026-07-13" && iso <= "2026-07-16"){
    return {busy:false, freeSlices:['All-Star break — 3 free days','No MLB/NFL/NCAAF'], leagues:[], note:'Only gap in MLB season: 3 days. Not enough for a week vacation.'};
  }
  if(iso >= "2026-09-28" && iso <= "2026-11-30"){
    // postseason overlap - busy
    return {busy:true, leagues:['MLB Postseason','NFL','NCAAF','Westwood One'], blocks:[{label:'MLB Postseason + NFL/WW1 + NCAAF', start:'11:00 AM', end:'10:30 PM', type:'mlb'}], freeSlices:['Free 6:00 AM – 11:00 AM only'], note:'World Series Oct 23-31 overlaps NFL midseason + NCAAF.'};
  }
  if(iso >= "2026-12-01" && iso <= "2027-02-08"){
    return {busy:true, leagues:['NFL','NCAAF Bowls','Westwood One'], blocks:[{label:'NFL + Bowls + WW1', start:'10:00 AM', end:'9:00 PM', type:'nfl'}], freeSlices:['Mornings free only'], note:'NFL through Super Bowl + bowl season.'};
  }
  // Generic fallback for 2027-2029: mirror 2026 pattern shifted
  const yr = d.getFullYear();
  if(yr>=2027){
    const m = d.getMonth()+1, dm = iso.slice(5);
    if((m===2 && dm >= "02-05" && dm <= "02-21") || (m===2 && dm < "02-24")){
      if(dm >= "02-09" && dm <= "02-22") return {busy:false, freeSlices:['ESTIMATED free — post-Super Bowl (verify when schedule released)'], leagues:[], est:true};
    }
    if(dm >= "03-25" && dm <= "09-27") return {busy:true, leagues:['MLB (est)','NFL (est)','Westwood One (est)'], blocks:[{label:'ESTIMATED: MLB+ NFL/WW1 (pattern)', start:'11:00 AM', end:'10:30 PM', type:'mlb'}], freeSlices:['Estimated — mornings only'], est:true};
    if(dm >= "07-12" && dm <= "07-15") return {busy:false, freeSlices:['ESTIMATED All-Star 3-day'], leagues:[], est:true};
  }
  // fallback
  if(isWeekend){
    return {busy:true, leagues:['MLB or NFL (seasonal)'], blocks:[{label:'Weekend overlap', start:'10:00 AM', end:'9:00 PM', type:'mlb'}], freeSlices:['Mornings/evenings']};
  }
  return {busy:false, freeSlices:['Likely free — verify on calendar'], leagues:[]};
}

function renderDay(date){
  const info = getDayInfo(date);
  const label = date.toLocaleDateString('en-US',{timeZone:TZ, weekday:'long', year:'numeric', month:'long', day:'numeric'});
  document.getElementById('cal-label').textContent = label + (info.est ? ' • ESTIMATED' : '');
  document.getElementById('pick-date').value = date.toISOString().slice(0,10);

  const container = document.getElementById('day-timeline');
  if(!container) return;

  // update top stat
  const freeHoursEl = document.getElementById('today-free');
  const gamesEl = document.getElementById('today-games');
  const freeNoteEl = document.getElementById('today-free-note');
  if(freeHoursEl){
    if(!info.busy){
      freeHoursEl.textContent = "24 h free";
      freeHoursEl.style.color = "var(--accent)";
      if(gamesEl) gamesEl.textContent = "No games on SF AM/FM today";
      if(freeNoteEl) freeNoteEl.textContent = info.note || "All day free — vacation OK";
    } else {
      // compute free slices roughly: 24h - busy blocks
      const busyStr = info.blocks ? info.blocks.map(b=> b.label).join(" • ") : info.leagues.join(", ");
      freeHoursEl.textContent = info.freeSlices ? info.freeSlices[0].split("–")[0].replace("Free ","") + " free + late night" : "Limited free";
      freeHoursEl.style.color = "var(--warn)";
      if(gamesEl) gamesEl.textContent = busyStr;
      if(freeNoteEl) freeNoteEl.textContent = info.freeSlices ? info.freeSlices.join(" • ") : "";
    }
  }

  let html = "";
  if(!info.busy){
    html += `<div class="day free"><div class="date">${label}<small>NO RADIO SPORTS — ALL DAY FREE</small></div><div class="bar"><i class="free" style="left:0;right:0"></i></div><div style="text-align:right;font-weight:800;color:var(--accent)">24h free ✓</div></div>`;
    html += `<div class="alert good"><b>Vacation-safe:</b> No MLB, NFL, NCAAF, or Westwood One on SF AM/FM. You can leave the radio off all day. ${info.note||''} ${info.est?'<span class="tag est">estimated</span>':''}</div>`;
  } else {
    info.blocks.forEach(b=>{
      html += `<div class="day busy"><div class="date">${b.label}<small>${b.start} – ${b.end} PT • PST</small></div><div class="bar"><i class="${b.type}" style="left:12%;right:8%"></i>${info.blocks.length>1? '<i class="ww" style="left:45%;right:15%;opacity:.6"></i>':''}</div><div style="text-align:right;font-weight:700;color:var(--bad)">BUSY</div></div>`;
    });
    html += `<div style="margin-top:10px"><b>Free slices today (PST):</b><ul class="small">` + info.freeSlices.map(s=>`<li>${s}</li>`).join('') + `</ul>`;
    if(info.leagues) html += `<div class="small muted">Leagues on-air: ${info.leagues.map(l=>`<span class="tag ${l==='Westwood One'?'ww':l.includes('MLB')?'all':l.includes('NFL')?'all':'high'}">${l}</span>`).join(' ')}</div>`;
    html += `</div>`;
    if(info.note) html += `<div class="note" style="margin-top:10px">${info.note} ${info.est?'<span class="tag est">estimated</span>':''}</div>`;
  }
  container.innerHTML = html;

  const note = document.getElementById('free-note');
  if(note){
    if(!info.busy){
      note.innerHTML = `<b style="color:var(--accent)">This whole day is free.</b> No game blocks — radio stays silent. Good for a vacation day. ${info.est?' <span class="tag est">estimated</span> — verify when official schedule drops.':''}`;
    } else {
      note.innerHTML = `Each bar = live AM/FM broadcast window (game + pregame). Gaps between bars = your free time. Example: if games are 12:05-3:30 PM and 5:15-8:30 PM, you&apos;re free 6:00-12:05 PM, 3:30-5:15 PM, and after 8:30 PM (PST). ${info.est?' <span class="tag est">estimated</span>':''}`;
    }
  }
}

function initCalendar(){
  const prev = document.getElementById('btn-prev');
  const next = document.getElementById('btn-next');
  const today = document.getElementById('btn-today');
  const pick = document.getElementById('pick-date');
  if(!prev) return;
  renderDay(current);
  prev.onclick = ()=>{ current = new Date(current.getTime() - 86400000); renderDay(current); };
  next.onclick = ()=>{ current = new Date(current.getTime() + 86400000); renderDay(current); };
  today.onclick = ()=>{ current = todayPST(); renderDay(current); };
  pick.onchange = ()=>{ current = new Date(pick.value+"T12:00:00"); renderDay(current); };
}

function updateNowStatus(){
  const now = new Date();
  const pstHour = parseInt(now.toLocaleString('en-US',{timeZone:TZ, hour:'numeric', hour12:false}));
  const pstMin = parseInt(now.toLocaleString('en-US',{timeZone:TZ, minute:'numeric'}));
  const busy = (()=>{
    const d = todayPST();
    const info = getDayInfo(d);
    if(!info.busy) return false;
    // rough: busy 10am-10:30pm on busy days; overnight free
    const mins = pstHour*60 + pstMin;
    return mins >= 600 && mins <= 1350;
  })();
  const el = document.getElementById('now-status');
  const det = document.getElementById('now-detail');
  if(!el) return;
  if(!busy){
    el.innerHTML = `<span style="color:var(--accent)">● FREE now</span> <span class="small muted" style="font-size:14px">— no game on air</span>`;
    if(det) det.textContent = "No MLB/NFL/NCAAF/WW1 live. Radio is free.";
  } else {
    el.innerHTML = `<span style="color:var(--bad)">● BUSY now</span> <span class="small muted" style="font-size:14px">— live game on air</span>`;
    if(det) det.textContent = "A game is on KNBR/KGO/KNEW/WW1. Not free.";
  }
}
