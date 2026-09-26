// =========================================================
// FIXSCORE PRO - Frontend Controller
// Render Data Rekomendasi & History Rekap
// =========================================================

document.addEventListener('DOMContentLoaded', () => {
  const btnToday = document.getElementById('tab-today');
  const btnHistory = document.getElementById('tab-history');

  if (btnToday && btnHistory) {
    btnToday.addEventListener('click', () => {
      setActiveTab(btnToday, btnHistory);
      loadTodayParlays();
    });

    btnHistory.addEventListener('click', () => {
      setActiveTab(btnHistory, btnToday);
      loadHistoryParlays();
    });
  }

  // Load awal: Rekomendasi Hari Ini
  loadTodayParlays();
});

function setActiveTab(activeBtn, inactiveBtn) {
  activeBtn.style.background = 'var(--accent-red)';
  activeBtn.style.color = 'white';
  inactiveBtn.style.background = 'transparent';
  inactiveBtn.style.color = 'var(--text-secondary)';
}

// 1. RENDER REKOMENDASI HARI INI (data/today.json)
async function loadTodayParlays() {
  const container = document.getElementById('parlay-container');
  if (!container) return;

  container.innerHTML = `<div style="text-align: center; padding: 20px; color: var(--text-muted); font-size: 13px;">Memuat analisis pertandingan hari ini...</div>`;

  try {
    const response = await fetch('data/today.json');
    if (!response.ok) throw new Error('File today.json belum tersedia');

    const data = await response.json();

    // Update waktu pembaruan di header
    const lastUpdatedElem = document.getElementById('last-updated');
    if (lastUpdatedElem && data.updatedAt) {
      lastUpdatedElem.textContent = `Diperbarui: ${data.updatedAt}`;
    }

    container.innerHTML = '';
    const matches = data.parlay3 || data.parlay10 || [];

    if (matches.length === 0) {
      container.innerHTML = `<div style="text-align: center; padding: 20px; color: var(--text-muted); font-size: 13px;">Belum ada rekomendasi untuk hari ini.</div>`;
      return;
    }

    matches.forEach((item) => {
      const matchCard = document.createElement('div');
      matchCard.className = 'match-card';

      // Parse Form Indicators (W, L, D)
      const homeFormHtml = (item.analytics?.homeForm || []).map(res => 
        `<span class="form-pill form-${res.toLowerCase()}">${res}</span>`
      ).join(' ');

      const awayFormHtml = (item.analytics?.awayForm || []).map(res => 
        `<span class="form-pill form-${res.toLowerCase()}">${res}</span>`
      ).join(' ');

      const formattedMatch = item.match ? item.match.replace(' vs ', ' <span class="vs">VS</span> ') : 'Match';

      matchCard.innerHTML = `
        <div class="card-header">
          <span class="league-tag">⚽ ${item.league || 'FOOTBALL LEAGUE'}</span>
          <span class="confidence-badge">Win Rate: ${item.winProb || 80}%</span>
        </div>

        <div class="teams-container">
          ${formattedMatch}
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
          <div>${item.expertReason || item.aiReason || 'Performa tim sangat solid.'}</div>

          ${item.analytics ? `
            <div class="analytics-grid">
              <div>Home Form: ${homeFormHtml || '-'}</div>
              <div>Away Form: ${awayFormHtml || '-'}</div>
            </div>
          ` : ''}
        </div>
      `;

      container.appendChild(matchCard);
    });
  } catch (error) {
    console.error('Error loading today parlays:', error);
    container.innerHTML = `<div style="text-align: center; padding: 20px; color: var(--text-muted); font-size: 13px;">Gagal memuat data hari ini. Silakan coba lagi nanti.</div>`;
  }
}

// 2. RENDER HISTORY REKAP (data/history.json)
async function loadHistoryParlays() {
  const container = document.getElementById('parlay-container');
  if (!container) return;

  container.innerHTML = `<div style="text-align: center; padding: 20px; color: var(--text-muted); font-size: 13px;">Memuat riwayat rekap pertandingan...</div>`;

  try {
    const response = await fetch('data/history.json');
    if (!response.ok) throw new Error('File history.json belum tersedia');

    const historyData = await response.json();
    container.innerHTML = '';

    if (!Array.isArray(historyData) || historyData.length === 0) {
      container.innerHTML = `<div style="text-align: center; padding: 20px; color: var(--text-muted); font-size: 13px;">Belum ada riwayat rekap tersimpan.</div>`;
      return;
    }

    historyData.forEach((dayGroup) => {
      const dateHeader = document.createElement('div');
      dateHeader.style.cssText = 'font-size: 13px; font-weight: 800; color: var(--text-secondary); margin: 16px 0 8px 0; border-bottom: 1px solid var(--border-color); padding-bottom: 4px;';
      dateHeader.textContent = `📅 Rekap Tanggal: ${dayGroup.date}`;
      container.appendChild(dateHeader);

      (dayGroup.matches || []).forEach((item) => {
        const historyCard = document.createElement('div');
        historyCard.className = 'match-card';
        
        // Warna indikator status (W, L, WH, LH, D)
        let statusBg = '#E5E7EB';
        let statusColor = '#374151';
        if (item.status === 'W' || item.status === 'WH') {
          statusBg = '#DCFCE7';
          statusColor = '#166534';
        } else if (item.status === 'L' || item.status === 'LH') {
          statusBg = '#FEE2E2';
          statusColor = '#991B1B';
        }

        const formattedMatch = item.match ? item.match.replace(' vs ', ' <span class="vs">VS</span> ') : 'Match';

        historyCard.innerHTML = `
          <div class="card-header">
            <span class="league-tag">⚽ ${item.league || 'LEAGUE'}</span>
            <span class="confidence-badge" style="background: ${statusBg}; color: ${statusColor}; border: none;">
              STATUS: ${item.status || 'PENDING'}
            </span>
          </div>

          <div class="teams-container">
            ${formattedMatch}
          </div>

          <div class="recommendation-box">
            <div>
              <span class="pick-label">PASARAN & SKOR AKHIR</span>
              <span class="pick-value">${item.pick} (Skor: ${item.score || 'N/A'})</span>
            </div>
            <div class="odds-badge">@${item.odds}</div>
          </div>
        `;

        container.appendChild(historyCard);
      });
    });
  } catch (error) {
    console.error('Error loading history parlays:', error);
    container.innerHTML = `<div style="text-align: center; padding: 20px; color: var(--text-muted); font-size: 13px;">Belum ada data riwayat rekap yang tersimpan.</div>`;
  }
}
