// STATE GLOBAL APLIKASI
let CURRENT_PARLAY_DATA = {
  parlay3: [],
  parlay5: [],
  parlay10: []
};
let ACTIVE_CATEGORY = 3; // Default 3 Partai

// INITIALIZATION
document.addEventListener('DOMContentLoaded', () => {
  loadDataFromJSON();
});

// MEMUAT DATA HARI INI & HISTORY
async function loadDataFromJSON() {
  const cacheBuster = new Date().getTime();
  try {
    // 1. Memuat rekomendasi harian
    const todayRes = await fetch(`./data/today.json?v=${cacheBuster}`, { cache: 'no-store' });
    if (todayRes.ok) {
      const data = await todayRes.json();
      CURRENT_PARLAY_DATA.parlay3 = data.parlay3 || [];
      CURRENT_PARLAY_DATA.parlay5 = data.parlay5 || [];
      CURRENT_PARLAY_DATA.parlay10 = data.parlay10 || [];

      // Tampilkan timestamp update jika elemen tersedia
      const timeElem = document.getElementById('last-updated-time');
      if (timeElem && data.updatedAt) {
        timeElem.innerText = `Diperbarui: ${data.updatedAt}`;
      }

      renderMatchesList();
    }

    // 2. Memuat data rekap history
    const historyRes = await fetch(`./data/history.json?v=${cacheBuster}`, { cache: 'no-store' });
    if (historyRes.ok) {
      const historyData = await historyRes.json();
      renderHistoryTable(historyData);
    }
  } catch (e) {
    console.log("Memuat data JSON default/fallback.");
  }
}

// FUNGSI GANTI KATEGORI PARLAY (3, 5, 10 PARTAI)
function switchParlayCategory(numLegs) {
  ACTIVE_CATEGORY = numLegs;

  // Update styling tombol aktif
  [3, 5, 10].forEach(num => {
    const btn = document.getElementById(`btn-parlay-${num}`);
    if (btn) {
      if (num === numLegs) {
        btn.className = "px-4 py-2 rounded-xl text-xs font-bold transition-all bg-flash-red text-white shadow-md shadow-red-500/20";
      } else {
        btn.className = "px-4 py-2 rounded-xl text-xs font-bold transition-all bg-slate-100 text-slate-600 hover:bg-slate-200";
      }
    }
  });

  renderMatchesList();
}

// RENDER LIST PERTANDINGAN BERDASARKAN KATEGORI AKTIF
function renderMatchesList() {
  const container = document.getElementById('matches-container');
  if (!container) return;

  const currentList = CURRENT_PARLAY_DATA[`parlay${ACTIVE_CATEGORY}`] || [];

  if (currentList.length === 0) {
    container.innerHTML = `
      <div class="bg-white rounded-2xl p-8 text-center border border-slate-100 shadow-sm">
        <p class="text-slate-400 text-xs font-bold">Belum ada data pertandingan untuk kategori ${ACTIVE_CATEGORY} Partai hari ini.</p>
      </div>
    `;
    updateParlaySummary(0, 0);
    return;
  }

  let html = '';
  let totalCombinedOdds = 1.0;

  currentList.forEach((m, idx) => {
    const odds = m.odds ? parseFloat(m.odds) : 1.85;
    totalCombinedOdds *= odds;

    html += `
      <div class="bg-white rounded-2xl p-4 border border-slate-100 shadow-sm hover:border-slate-200 transition-all">
        <!-- HEADER MATCH: LIGA & PROBABILITAS -->
        <div class="flex justify-between items-center mb-2 pb-2 border-b border-slate-50">
          <span class="text-[10px] font-bold uppercase tracking-wider text-slate-400">${m.league || 'Premier League'}</span>
          <span class="text-[11px] font-extrabold text-emerald-600 bg-emerald-50 px-2.5 py-0.5 rounded-full border border-emerald-100">
            Win Rate: ${m.winProb || 70}%
          </span>
        </div>

        <!-- TIM PERTANDINGAN -->
        <div class="my-2">
          <h3 class="text-sm font-extrabold text-slate-800">${m.match || 'Team A vs Team B'}</h3>
        </div>

        <!-- PROYEKSI AI (+EV) -->
        <div class="bg-slate-50 p-3 rounded-xl border border-slate-100 flex justify-between items-center gap-2 my-2">
          <div>
            <span class="text-[9px] text-slate-400 block font-bold uppercase tracking-wider">REKOMENDASI PICK (+EV)</span>
            <span class="text-xs sm:text-sm font-black text-flash-red">${m.pick || 'Home Win'}</span>
          </div>
          <div class="text-right">
            <span class="text-[9px] text-slate-400 block font-bold uppercase tracking-wider">ODDS</span>
            <span class="font-mono text-xs font-black text-slate-900 bg-amber-100 px-2 py-0.5 rounded-md border border-amber-200">
              @${odds.toFixed(2)}
            </span>
          </div>
        </div>

        <!-- ANALISIS ANALITIK GEMINI AI -->
        ${m.aiReason ? `
          <div class="mt-2 text-[11px] text-slate-500 leading-relaxed bg-blue-50/50 p-2.5 rounded-lg border border-blue-100/50">
            <span class="font-bold text-blue-700">💡 Analisis AI:</span> ${m.aiReason}
          </div>
        ` : ''}
      </div>
    `;
  });

  container.innerHTML = html;
  updateParlaySummary(currentList.length, totalCombinedOdds);
}

// UPDATE RINGKASAN PARLAY & KALKULATOR EST
function updateParlaySummary(matchCount, totalOdds) {
  const countElem = document.getElementById('summary-count');
  const oddsElem = document.getElementById('summary-total-odds');
  const estWinElem = document.getElementById('summary-est-win');
  const stakeInput = document.getElementById('stake-input');

  if (countElem) countElem.innerText = `${matchCount} Leg`;
  if (oddsElem) oddsElem.innerText = `@${totalOdds.toFixed(2)}`;

  const calculatePayout = () => {
    const stake = stakeInput ? parseFloat(stakeInput.value) || 0 : 100;
    const estPayout = stake * totalOdds;
    if (estWinElem) {
      estWinElem.innerText = `Rp ${Math.round(estPayout * 1000).toLocaleString('id-ID')}`;
    }
  };

  if (stakeInput) {
    stakeInput.oninput = calculatePayout;
  }
  calculatePayout();
}

// RENDER TABEL HISTORY REKAP
function renderHistoryTable(historyData) {
  const tbody = document.querySelector('#tab-history tbody');
  if (!tbody || !historyData) return;

  tbody.innerHTML = '';
  historyData.forEach(item => {
    let badgeClass = "bg-emerald-100 text-emerald-800";
    if (item.status === "LOSE") badgeClass = "bg-red-100 text-red-800";
    if (item.status === "DRAW" || item.status === "PUSH") badgeClass = "bg-slate-100 text-slate-800";
    if (item.status === "WIN_HALF") badgeClass = "bg-teal-100 text-teal-800";
    if (item.status === "LOSE_HALF") badgeClass = "bg-amber-100 text-amber-800";

    const tr = document.createElement('tr');
    tr.className = "bg-white hover:bg-slate-50/50 border-b border-slate-100";
    tr.innerHTML = `
      <td class="p-3 font-bold">${item.date || '-'}</td>
      <td class="p-3 font-sans">${item.summary || 'Rekap Evaluasi Algoritma'}</td>
      <td class="p-3 font-bold">${item.totalMatches || '10'} Leg</td>
      <td class="p-3"><span class="${badgeClass} px-2 py-0.5 rounded-md font-bold text-[10px]">${item.status}</span></td>
      <td class="p-3 font-bold ${item.units && item.units.includes('+') ? 'text-emerald-600' : 'text-red-600'}">${item.units || '0.00 Unit'}</td>
    `;
    tbody.appendChild(tr);
  });
}

// NAVIGATION TAB (REKOMENDASI VS HISTORY)
function switchMainTab(tabName) {
  const tabToday = document.getElementById('tab-content-today');
  const tabHistory = document.getElementById('tab-content-history');
  const btnToday = document.getElementById('nav-btn-today');
  const btnHistory = document.getElementById('nav-btn-history');

  if (tabName === 'today') {
    if (tabToday) tabToday.classList.remove('hidden');
    if (tabHistory) tabHistory.classList.add('hidden');
    if (btnToday) btnToday.className = "px-4 py-2 text-xs font-extrabold text-flash-red border-b-2 border-flash-red";
    if (btnHistory) btnHistory.className = "px-4 py-2 text-xs font-bold text-slate-400 hover:text-slate-600";
  } else {
    if (tabToday) tabToday.classList.add('hidden');
    if (tabHistory) tabHistory.classList.remove('hidden');
    if (btnToday) btnToday.className = "px-4 py-2 text-xs font-bold text-slate-400 hover:text-slate-600";
    if (btnHistory) btnHistory.className = "px-4 py-2 text-xs font-extrabold text-flash-red border-b-2 border-flash-red";
  }
}
