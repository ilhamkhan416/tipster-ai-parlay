// =========================================================
// FIXSCORE PRO - Complete Flashscore Layout Controller
// Position: /src/app.js
// =========================================================

let currentData = null;
let activeLeg = 'parlay3'; // Default ke Paket 3 Leg

document.addEventListener('DOMContentLoaded', () => {
  setupTabs();
  loadTodayData();
});

// ---------------------------------------------------------
// NAVIGASI UTAMA (TAB REKOMENDASI VS HISTORY)
// ---------------------------------------------------------
function setupTabs() {
  const btnToday = document.getElementById('tab-today');
  const btnHistory = document.getElementById('tab-history');

  if (btnToday && btnHistory) {
    btnToday.addEventListener('click', () => {
      btnToday.classList.add('active');
      btnHistory.classList.remove('active');
      loadTodayData();
    });

    btnHistory.addEventListener('click', () => {
      btnHistory.classList.add('active');
      btnToday.classList.remove('active');
      loadHistoryData();
    });
  }
}

// ---------------------------------------------------------
// 1. RENDER DATA REKOMENDASI HARI INI (data/today.json)
// ---------------------------------------------------------
async function loadTodayData() {
  const container = document.getElementById('parlay-container');
  if (!container) return;

  container.innerHTML = `<div class="loading-state">Memuat data pertandingan & analisis pasaran...</div>`;

  try {
    const res = await fetch('data/today.json');
    if (!res.ok) throw new Error('File data/today.json tidak ditemukan');
    currentData = await res.json();

    const timeElem = document.getElementById('last-updated');
    if (timeElem && currentData.updatedAt) {
      timeElem.textContent = `UPDATED: ${currentData.updatedAt}`;
    }

    renderTodayContent();
  } catch (e) {
    console.error('Error loading today.json:', e);
    container.innerHTML = `<div class="loading-state">Data rekomendasi hari ini belum tersedia.</div>`;
  }
}

function renderTodayContent() {
  const container = document.getElementById('parlay-container');
  if (!container || !currentData) return;

  container.innerHTML = '';

  // Selector Tombol Piramida (3, 5, 10 Leg)
  const legNav = document.createElement('div');
  legNav.className = 'leg-selector';
  
  const options = [
    { key: 'parlay3', label: '3 LEG (HIGH WIN RATE)' },
    { key: 'parlay5', label: '5 LEG (BALANCED)' },
    { key: 'parlay10', label: '10 LEG (HIGH RETURN)' }
  ];

  options.forEach(opt => {
    const btn = document.createElement('button');
    btn.className = `leg-btn ${activeLeg === opt.key ? 'active' : ''}`;
    btn.textContent = opt.label;
    btn.onclick = () => {
      activeLeg = opt.key;
      renderTodayContent();
    };
    legNav.appendChild(btn);
  });

  container.appendChild(legNav);

  // Ambil data pertandingan sesuai paket leg
  const matches = currentData[activeLeg] || [];
  if (matches.length === 0) {
    container.innerHTML += `<div class="loading-state">Tidak ada pertandingan pada paket ini.</div>`;
    return;
  }

  // Render Baris Pertandingan Tipe Flashscore
  matches.forEach(item => {
    const rawMatch = item.match || 'Home Team vs Away Team';
    const teams = rawMatch.split(' vs ');
    const homeTeam = teams[0] ? teams[0].trim() : 'Home';
    const awayTeam = teams[1] ? teams[1].trim() : 'Away';

    // Parse Form W/L/D
    const homeForm = (item.analytics?.homeForm || []).map(r => 
      `<span class="f-pill f-${r.toLowerCase()}">${r}</span>`
    ).join('');

    const awayForm = (item.analytics?.awayForm || []).map(r => 
      `<span class="f-pill f-${r.toLowerCase()}">${r}</span>`
    ).join('');

    const wrapper = document.createElement('div');
    wrapper.innerHTML = `
      <div class="league-header">
        <span>⚽ ${item.league || 'ALL LEAGUES'}</span>
        <span class="win-rate-badge">WIN RATE: ${item.winProb || 80}%</span>
      </div>

      <div class="match-box">
        <div class="teams-row">
          <span class="team-name team-home">${homeTeam}</span>
          <span class="vs-badge">VS</span>
          <span class="team-name team-away">${awayTeam}</span>
        </div>

        <div class="pick-bar">
          <div>
            <span class="pick-title">Rekomendasi Pasaran (+EV)</span>
            <span class="pick-value">${item.pick}</span>
          </div>
          <div class="odds-value">@${item.odds}</div>
        </div>

        <div class="expert-reason">
          <div class="expert-label">Catatan Analis</div>
          <div>${item.expertReason || item.aiReason || 'Evaluasi taktis dan statistik tim terverifikasi.'}</div>

          ${item.analytics ? `
            <div class="form-grid">
              <div>HOME: ${homeForm || '-'}</div>
              <div>AWAY: ${awayForm || '-'}</div>
            </div>
          ` : ''}
        </div>
      </div>
    `;

    container.appendChild(wrapper);
  });
}

// ---------------------------------------------------------
// 2. RENDER HISTORY REKAP (data/history.json)
// ---------------------------------------------------------
async function loadHistoryData() {
  const container = document.getElementById('parlay-container');
  if (!container) return;

  container.innerHTML = `<div class="loading-state">Memuat riwayat rekap pertandingan...</div>`;

  try {
    const res = await fetch('data/history.json');
    if (!res.ok) throw new Error('File data/history.json tidak ditemukan');
    const historyList = await res.json();

    container.innerHTML = '';
    if (!Array.isArray(historyList) || historyList.length === 0) {
      container.innerHTML = `<div class="loading-state">Belum ada riwayat rekap tersimpan.</div>`;
      return;
    }

    historyList.forEach(group => {
      const dateBar = document.createElement('div');
      dateBar.style.cssText = 'background: #11161B; color: #FFFFFF; padding: 6px 10px; font-size: 11px; font-weight: 700; margin-top: 10px; text-transform: uppercase; border-left: 3px solid var(--accent-red);';
      dateBar.textContent = `📅 REKAP TANGGAL: ${group.date}`;
      container.appendChild(dateBar);

      (group.matches || []).forEach(item => {
        const rawMatch = item.match || 'Home vs Away';
        const teams = rawMatch.split(' vs ');
        const homeTeam = teams[0] ? teams[0].trim() : 'Home';
        const awayTeam = teams[1] ? teams[1].trim() : 'Away';
        
        let statusBg = '#777777';
        if (item.status === 'W' || item.status === 'WH') statusBg = 'var(--green-win)';
        if (item.status === 'L' || item.status === 'LH') statusBg = 'var(--red-loss)';

        const card = document.createElement('div');
        card.className = 'match-box';
        card.style.borderTop = '1px solid var(--border-color)';
        
        card.innerHTML = `
          <div class="league-header" style="background: transparent; border: none; padding: 2px 0 6px 0;">
            <span>⚽ ${item.league || 'LEAGUE'}</span>
          </div>

          <div class="teams-row">
            <span class="team-name team-home">${homeTeam}</span>
            <span class="vs-badge">VS</span>
            <span class="team-name team-away">${awayTeam}</span>
          </div>

          <div class="pick-bar">
            <div>
              <span class="pick-title">Pasaran & Skor Akhir</span>
              <span class="pick-value">${item.pick} (Skor: ${item.score || 'N/A'})</span>
            </div>
            <div style="background: ${statusBg}; color: #FFFFFF; font-size: 10px; font-weight: 900; padding: 3px 6px; border-radius: 2px;">
              ${item.status || 'PENDING'}
            </div>
          </div>
        `;

        container.appendChild(card);
      });
    });
  } catch (e) {
    console.error('Error loading history.json:', e);
    container.innerHTML = `<div class="loading-state">Belum ada data riwayat tersimpan.</div>`;
  }
}
