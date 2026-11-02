// FREE TIME VACATION PLANNER - Application Logic
let allGames = [];
let vacationWindows = [];
let currentDate = new Date('2026-11-02'); // Today's date

document.addEventListener('DOMContentLoaded', () => {
  allGames = buildGameDatabase();
  vacationWindows = findVacationWindows(allGames, 7);
  initDashboard();
});

function initDashboard() {
  updateTodayView();
  updateStats();
  updateUpcoming();
  updateVacationWindows();
}

function switchTab(tabName) {
  document.querySelectorAll('.tab-content').forEach(t => t.classList.remove('active'));
  document.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
  document.getElementById('tab-' + tabName).classList.add('active');
  event.target.classList.add('active');
}

function changeDay(offset) {
  currentDate.setDate(currentDate.getDate() + offset);
  updateTodayView();
}

function goToToday() {
  currentDate = new Date('2026-11-02');
  updateTodayView();
}

function goToDate(dateStr) {
  currentDate = new Date(dateStr + 'T12:00:00');
  updateTodayView();
}

function updateStats() {
  const dateStr = currentDate.toISOString().split('T')[0];
  const daySched = getDaySchedule(allGames, dateStr);
  
  const statusEl = document.getElementById('todayStatus');
  const gamesEl = document.getElementById('gamesToday');
  const freeEl = document.getElementById('freeHours');
  const bestEl = document.getElementById('bestWindow');
  
  if (daySched.games.length === 0) {
    statusEl.textContent = 'FREE';
    statusEl.className = 'value free';
  } else if (daySched.hasHighPriority) {
    statusEl.textContent = 'BUSY';
    statusEl.className = 'value busy';
  } else {
    statusEl.textContent = 'GAMES ON';
    statusEl.className = 'value warn';
  }
  
  gamesEl.textContent = daySched.games.length;
  freeEl.textContent = (daySched.totalFreeMinutes / 60).toFixed(1) + 'h';
  
  if (vacationWindows.length > 0) {
    const best = vacationWindows[0];
    bestEl.textContent = best.days + ' days';
  }
}

function updateTodayView() {
  const dateStr = currentDate.toISOString().split('T')[0];
  const daySched = getDaySchedule(allGames, dateStr);
  
  // Update date display
  const opts = { weekday: 'long', year: 'numeric', month: 'long', day: 'numeric' };
  document.getElementById('currentDate').textContent = currentDate.toLocaleDateString('en-US', opts);
  document.getElementById('datePicker').value = dateStr;
  
  // Update timeline
  renderTimeline(daySched);
  
  // Update games list
  renderGamesList(daySched);
  
  // Update free blocks
  renderFreeBlocks(daySched);
  
  // Update stats
  updateStats();
}

function renderTimeline(daySched) {
  const bar = document.getElementById('timelineBar');
  bar.innerHTML = '';
  
  const totalMins = 1440; // 24 hours
  
  // Render free blocks
  daySched.freePeriods.forEach(period => {
    const block = document.createElement('div');
    block.className = 'timeline-block free';
    const leftPct = (period.start / totalMins) * 100;
    const widthPct = ((period.end - period.start) / totalMins) * 100;
    block.style.left = leftPct + '%';
    block.style.width = widthPct + '%';
    if (widthPct > 5) {
      block.textContent = 'FREE';
    }
    bar.appendChild(block);
  });
  
  // Render busy blocks
  daySched.busyPeriods.forEach(period => {
    const block = document.createElement('div');
    const isHigh = period.game && period.game.highPriority;
    block.className = 'timeline-block busy' + (isHigh ? ' high-priority' : '');
    const leftPct = (period.start / totalMins) * 100;
    const widthPct = ((period.end - period.start) / totalMins) * 100;
    block.style.left = leftPct + '%';
    block.style.width = widthPct + '%';
    if (widthPct > 4) {
      const sport = period.game ? period.game.sport : '';
      block.textContent = sport;
    }
    block.title = period.game ? 
      `${period.game.sport}: ${period.game.away || ''} ${period.game.home || ''} ${period.game.matchup || ''}` : 'Game';
    bar.appendChild(block);
  });
}

function renderGamesList(daySched) {
  const container = document.getElementById('todayGames');
  
  if (daySched.games.length === 0) {
    container.innerHTML = '<p style="color:var(--free);font-weight:600;">🎉 No games today! Full day free!</p>';
    return;
  }
  
  let html = '';
  daySched.games.forEach(game => {
    const sportBadge = game.sport === 'MLB' ? 'badge-mlb' : 
                       game.sport === 'NFL' ? 'badge-nfl' : 'badge-ncaaf';
    const priorityBadge = game.highPriority ? '<span class="badge badge-high">⭐ HIGH</span>' : '';
    const matchup = game.matchup || `${game.away || ''} vs ${game.home || ''}`;
    const verifiedBadge = game.verified ? '<span class="badge badge-verified">✓</span>' : '<span class="badge badge-estimated">~Est</span>';
    
    html += `<div class="game-item">
      <span class="game-time">${game.time || 'TBA'}</span>
      <div class="game-details">
        <div>${matchup} ${priorityBadge}</div>
        <div class="game-sport">
          <span class="badge ${sportBadge}">${game.sport}</span> 
          ${game.type || ''} ${verifiedBadge}
          ${game.note ? '<br><small style="color:var(--warning)">' + game.note + '</small>' : ''}
        </div>
      </div>
    </div>`;
  });
  
  container.innerHTML = html;
}

function renderFreeBlocks(daySched) {
  const container = document.getElementById('freeBlocks');
  
  if (daySched.freePeriods.length === 0) {
    container.innerHTML = '<p style="color:var(--busy);">No free time today - games all day!</p>';
    return;
  }
  
  let html = '';
  daySched.freePeriods.forEach(period => {
    const duration = period.end - period.start;
    const hours = Math.floor(duration / 60);
    const mins = duration % 60;
    html += `<div class="game-item">
      <span class="game-time" style="color:var(--free);">${minutesToTime(period.start)}</span>
      <div class="game-details">
        <div style="color:var(--free);">Free until ${minutesToTime(period.end)}</div>
        <div class="game-sport">${hours}h ${mins}m available</div>
      </div>
    </div>`;
  });
  
  container.innerHTML = html;
}

function updateUpcoming() {
  const today = '2026-11-02';
  const highPriorityUpcoming = allGames
    .filter(g => g.highPriority && g.date >= today)
    .sort((a, b) => a.date.localeCompare(b.date) || (a.time || '').localeCompare(b.time || ''))
    .slice(0, 30);
  
  const tbody = document.getElementById('upcomingBody');
  let html = '';
  
  highPriorityUpcoming.forEach(game => {
    const sportBadge = game.sport === 'MLB' ? 'badge-mlb' : 
                       game.sport === 'NFL' ? 'badge-nfl' : 'badge-ncaaf';
    const verifiedBadge = game.verified ? '<span class="badge badge-verified">✓ Verified</span>' : '<span class="badge badge-estimated">~ Estimated</span>';
    const matchup = game.matchup || `${game.away || ''} vs ${game.home || ''}`;
    const sourceLink = game.source ? `<a href="${game.source}" target="_blank" rel="noopener">View</a>` : '-';
    
    html += `<tr>
      <td>${game.date}</td>
      <td>${game.time || 'TBA'}</td>
      <td>${matchup}</td>
      <td><span class="badge ${sportBadge}">${game.sport}</span></td>
      <td><span class="badge badge-high">⭐ HIGH</span> ${verifiedBadge}</td>
      <td>${sourceLink}</td>
    </tr>`;
  });
  
  tbody.innerHTML = html;
}

function updateVacationWindows(filterYear) {
  const container = document.getElementById('vacationList');
  let windows = vacationWindows;
  
  if (filterYear) {
    windows = windows.filter(w => w.year === filterYear);
  }
  
  // Show only 7+ day windows
  windows = windows.filter(w => w.days >= 7).slice(0, 20);
  
  if (windows.length === 0) {
    container.innerHTML = '<p style="color:var(--warning);">No vacation windows of 7+ days found for this year.</p>';
    return;
  }
  
  let html = '';
  windows.forEach(w => {
    const weeks = Math.floor(w.days / 7);
    const extraDays = w.days % 7;
    const durationStr = weeks > 0 ? `${weeks} week${weeks > 1 ? 's' : ''}${extraDays > 0 ? ' + ' + extraDays + ' days' : ''}` : `${w.days} days`;
    
    html += `<div class="vacation-card">
      <div>
        <div class="dates">${w.start} → ${w.end}</div>
        <div style="color:var(--text-dim);font-size:0.8rem;">Year: ${w.year}</div>
      </div>
      <div class="duration">${w.days} days (${durationStr})</div>
    </div>`;
  });
  
  container.innerHTML = html;
}

function filterYear(year, btn) {
  document.querySelectorAll('.year-btn').forEach(b => b.classList.remove('active'));
  btn.classList.add('active');
  updateVacationWindows(year || null);
}
