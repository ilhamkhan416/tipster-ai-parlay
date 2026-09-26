// =========================================================
// FIXSCORE PRO - Minimalist Frontend Controller
// Handles 3 Leg, 5 Leg, 10 Leg & History Toggle
// =========================================================

let currentTodayData = null;
let selectedLegKey = 'parlay3'; // Default: Paket 3 Leg

document.addEventListener('DOMContentLoaded', () => {
  setupNavigation();
  loadTodayData();
});

// Setup Switcher Tab Utama (Rekomendasi vs History)
function setupNavigation() {
  const btnToday = document.getElementById('tab-today');
  const btnHistory = document.getElementById('tab-history');

  if (btnToday && btnHistory) {
    btnToday.addEventListener('click', () => {
      setActiveTab(btnToday, btnHistory);
      loadTodayData();
    });

    btnHistory.addEventListener('click', () => {
      setActiveTab(btnHistory, btnToday);
      loadHistoryData();
    });
  }
}

function setActiveTab(activeBtn, inactiveBtn) {
  activeBtn.style.background = 'var(--accent-red)';
  activeBtn.style.color = 'white';
  inactiveBtn.style.background = 'transparent';
  inactiveBtn.style.color = 'var(--text-secondary)';
}

// ---------------------------------------------------------
// 1. REKOMENDASI HARI INI (data/today.json)
// ---------------------------------------------------------
async function loadTodayData() {
  const container = document.getElementById('parlay-container');
  if (!container) return;

  container.innerHTML = `<div style="text-align: center; padding: 24px; color: var(--text-muted); font-size: 13px;">Memuat analisis pertandingan hari ini...</div>`;

  try {
    const response = await fetch('data/today.json');
    if (!response.ok) throw new Error('File today.json belum tersedia');

    currentTodayData = await response.json();

    // Update timestamp di header
    const lastUpdatedElem = document.getElementById('last-updated');
    if (lastUpdatedElem && currentTodayData.updatedAt) {
      lastUpdatedElem.textContent = `Diperbarui: ${currentTodayData.updatedAt}`;
    }

    renderTodayView();
  } catch (error) {
    console.error('Error loading today.json:', error);
    container.innerHTML = `<div style="text-align: center; padding: 24px; color: var(--text-muted); font-size: 13px;">Gagal memuat data hari ini. Silakan coba beberapa saat lagi.</div>`;
  }
}

function renderTodayView() {
  const container = document.getElementById('parlay-container');
  if (!container || !currentTodayData) return;

  container.innerHTML = '';

  // Tombol Selector Paket Leg (3, 5, 10 Leg)
  const selectorWrapper = document.createElement('div');
  selectorWrapper.style.cssText = 'display: flex; gap: 8px; margin-bottom: 20px; justify-content: center; flex-wrap: wrap;';

  const legOptions = [
    { key: 'parlay3', label: '🔥 3 Leg (High Win Rate)' },
    { key: 'parlay5', label: '⚖️ 5 Leg (Balanced)' },
    { key: 'parlay10', label: '🚀 10 Leg (High Return)' }
  ];

  legOptions.forEach(opt => {
    const btn = document.createElement('button');
    btn.textContent = opt.label;
    const isActive = selectedLegKey === opt.key;
    
    btn.style.cssText = `
      padding: 8px 12px;
      font-size: 11px;
      font-weight: 800;
      border-radius: 6px;
      cursor: pointer;
      transition: all 0.2s ease;
      border: 1px solid ${isActive ? 'var(--text-primary)' : 'var(--border-color)'};
      background: ${isActive ? 'var(--text-primary)' : '#FFFFFF'};
      color: ${isActive ? '#FFFFFF' : 'var(--text-secondary)'};
    `;

    btn.onclick = () => {
      selectedLegKey = opt.key;
      renderTodayView();
    };

    selectorWrapper.appendChild(btn);
  });

  container.appendChild(selectorWrapper);

  // Ambil data pertandingan sesuai pilihan leg
  const matches = currentTodayData[selectedLegKey] || [];

  if (matches.length === 0) {
    const emptyMsg = document.createElement('div');
    emptyMsg.style.cssText = 'text-align: center; padding: 20px; color: var(--text-muted); font-size: 13px;';
    emptyMsg.textContent = 'Belum ada pertandingan dalam paket ini.';
    container.appendChild(emptyMsg);
    return;
  }

  // Render Kartu Pertandingan
  matches.forEach((item) => {
    const card = document.createElement('div');
    card.className = 'match-card';

    // Format Form 5 Laga
    const homeFormHtml = (item.analytics?.homeForm || []).map(res => 
      `<span class="form-pill form-${res.toLowerCase()}">${res}</span>`
    ).join(' ');

    const awayFormHtml = (item.analytics?.awayForm || []).map(res => 
      `<span class="form-pill form-${res.toLowerCase()}">${res}</span>`
    ).join(' ');

    const matchTitle = item.match ? item.match.replace(' vs ', ' <span class="vs">VS</span> ') : 'Match';

    card.innerHTML = `
      <div class="card-header">
        <span class="league-tag">⚽ ${item.league || 'ALL LEAGUES'}</span>
        <span class="confidence-badge">Win Rate: ${item.winProb || 80}%</span>
      </div>

      <div class="teams-container">
        ${matchTitle}
      </div>

      <div class="recommendation-box">
        <div>
          <span class="pick-label">REKOMENDASI PASARAN (+EV)</span>
          <span class="pick-value">${item.pick}</span>
        </div>
        <div class="odds-badge">@${item.odds}</div>
      </div>

      <div class="expert-box">
        <div class="expert-title">
          <span class="bullet-red"></span>
          CATATAN PAKAR BOLA
        </div>
        <div style="color: #374151;">${item.expertReason || item.aiReason || 'Evaluasi taktis dan efisiensi performa tim solid.'}</div>

        ${item.analytics ? `
          <div class="analytics-grid">
            <div>Home Form: ${homeFormHtml || '-'}</div>
            <div>Away Form: ${awayFormHtml || '-'}</div>
          </div>
        ` : ''}
      </div>
    `;

    container.appendChild(card);
  });
}

// ---------------------------------------------------------
// 2. HISTORY REKAP (data/history.json)
// ---------------------------------------------------------
async function loadHistoryData() {
  const container = document.getElementById('parlay-container');
  if (!container) return;

  container.innerHTML = `<div style="text-align: center; padding: 24px; color: var(--text-muted); font-size: 13px;">Memuat riwayat rekap pertandingan...</div>`;

  try {
    const response = await fetch('data/history.json');
    if (!response.ok) throw new Error('File history.json belum tersedia');

    const historyList = await response.json();
    container.innerHTML = '';

    if (!Array.isArray(historyList) || historyList.length === 0) {
      container.innerHTML = `<div style="text-align: center; padding: 24px; color: var(--text-muted); font-size: 13px;">Belum ada riwayat rekap tersimpan.</div>`;
      return;
    }

    historyList.forEach((dayGroup) => {
      const dateHeader = document.createElement('div');
      dateHeader.style.cssText = 'font-size: 13px; font-weight: 800; color: var(--text-secondary); margin: 16px 0 10px 0; border-bottom: 1px solid var(--border-color); padding-bottom: 4px;';
      dateHeader.textContent = `📅 Rekap Tanggal: ${dayGroup.date}`;
      container.appendChild(dateHeader);

      (dayGroup.matches || []).forEach((item) => {
        const card = document.createElement('div');
        card.className = 'match-card';
        
        let statusBg = '#E5E7EB';
        let statusColor = '#374151';
        
        if (item.status === 'W' || item.status === 'WH') {
          statusBg = '#DCFCE7';
          statusColor = '#166534';
        } else if (item.status === 'L' || item.status === 'LH') {
          statusBg = '#FEE2E2';
          statusColor = '#991B1B';
        }

        const matchTitle = item.match ? item.match.replace(' vs ', ' <span class="vs">VS</span> ') : 'Match';

        card.innerHTML = `
          <div class="card-header">
            <span class="league-tag">⚽ ${item.league || 'LEAGUE'}</span>
            <span class="confidence-badge" style="background: ${statusBg}; color: ${statusColor}; border: none;">
              STATUS: ${item.status || 'PENDING'}
            </span>
          </div>

          <div class="teams-container">
            ${matchTitle}
          </div>

          <div class="recommendation-box">
            <div>
              <span class="pick-label">PASARAN & SKOR AKHIR</span>
              <span class="pick-value">${item.pick} (Skor: ${item.score || 'N/A'})</span>
            </div>
            <div class="odds-badge">@${item.odds}</div>
          </div>
        `;

        container.appendChild(card);
      });
    });
  } catch (error) {
    console.error('Error loading history.json:', error);
    container.innerHTML = `<div style="text-align: center; padding: 24px; color: var(--text-muted); font-size: 13px;">Belum ada data riwayat rekap tersimpan.</div>`;
  }
}
