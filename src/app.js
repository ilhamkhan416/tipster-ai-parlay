// FIXSCORE APPLICATION LOGIC (FIXED SCORE HORIZONTAL & PREDICTION BLUR LOCK)

let MOCK_TODAY_MATCHES = [];
let selectedMarketFilter = 'ALL';
let userParlaySlip = [];

// Memuat data dari today.json
async function loadDataFromJSON() {
  const cacheBuster = new Date().getTime();
  try {
    const todayRes = await fetch(`./data/today.json?v=${cacheBuster}`, { cache: 'no-store' });
    if (todayRes.ok) {
      MOCK_TODAY_MATCHES = await todayRes.json();
      renderMatchesList();
    }
  } catch (e) {
    console.log("Error loading JSON data.");
  }
}

window.onload = function() {
  loadDataFromJSON();
  setInterval(loadDataFromJSON, 60000); // Refresh otomatis tiap 60 detik
};

function toggleSidebar() {
  document.getElementById('sidebarMenu').classList.toggle('translate-x-full');
  document.getElementById('sidebarOverlay').classList.toggle('hidden');
}

function switchTab(tabName) {
  document.getElementById('tab-dashboard').classList.add('hidden');
  document.getElementById('tab-history').classList.add('hidden');
  document.getElementById('tab-algorithm').classList.add('hidden');
  document.getElementById(`tab-${tabName}`).classList.remove('hidden');
  window.scrollTo({ top: 0, behavior: 'smooth' });
}

function renderMatchesList() {
  const container = document.getElementById('matchesContainer');
  if (!container) return;
  container.innerHTML = '';

  let filtered = MOCK_TODAY_MATCHES.filter(m => {
    if (selectedMarketFilter === 'ALL') return true;
    return m.marketType === selectedMarketFilter;
  });

  const searchInput = document.getElementById('searchInput');
  const searchTerm = searchInput ? searchInput.value.toLowerCase() : '';
  if (searchTerm) {
    filtered = filtered.filter(m => 
      m.homeTeam.toLowerCase().includes(searchTerm) || 
      m.awayTeam.toLowerCase().includes(searchTerm) || 
      m.league.toLowerCase().includes(searchTerm)
    );
  }

  if (filtered.length === 0) {
    container.innerHTML = `<div class="bg-white p-6 rounded-2xl text-center text-xs text-slate-400">Belum ada data pertandingan yang sesuai.</div>`;
    return;
  }

  filtered.forEach((m, index) => {
    const isAdded = userParlaySlip.some(p => p.id === m.id);
    const card = document.createElement('div');
    card.className = "bg-white flash-card-hover rounded-2xl p-3.5 sm:p-4 border border-slate-200/80 shadow-sm relative space-y-3 overflow-hidden";

    let localKickoffStr = m.kickoff;
    if (m.kickoffUtc) {
      try {
        const matchDate = new Date(m.kickoffUtc);
        localKickoffStr = matchDate.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }) + " (Jam Lokal)";
      } catch(e) {}
    }

    // FT SCORE HORIZONTAL RAPAT (PANGKAT FIXED WIDE - 100% TIDAK PERNAH PATAH/TERPOTONG)
    let statusBadge = `<span class="bg-slate-100 px-2 py-0.5 rounded-md border border-slate-200 text-slate-700 text-[10px] font-bold"><i class="fa-regular fa-clock mr-1 text-flash-red"></i>${localKickoffStr}</span>`;
    let centerScoreDisplay = `<span class="text-[10px] font-mono text-emerald-800 font-bold bg-emerald-50 px-2 py-0.5 rounded-md border border-emerald-200">VS</span>`;

    if (['FT', 'AET', 'PEN'].includes(m.statusShort)) {
      statusBadge = `<span class="bg-slate-800 text-white px-2 py-0.5 rounded-md text-[10px] font-bold font-mono">FT</span>`;
      centerScoreDisplay = `<div class="inline-flex items-center justify-center bg-slate-900 text-white px-3 py-1 rounded-lg font-mono font-black text-xs tracking-widest whitespace-nowrap min-w-[65px] text-center shadow-inner">${m.scoreHome ?? 0}&nbsp;-&nbsp;${m.scoreAway ?? 0}</div>`;
    } else if (['1H', '2H', 'HT', 'LIVE', 'ET', 'P'].includes(m.statusShort)) {
      const minuteStr = m.statusElapsed ? `${m.statusElapsed}'` : 'LIVE';
      statusBadge = `<span class="bg-red-600 text-white px-2 py-0.5 rounded-md text-[10px] font-bold font-mono animate-pulse">LIVE ${minuteStr}</span>`;
      centerScoreDisplay = `<div class="inline-flex items-center justify-center bg-red-600 text-white px-3 py-1 rounded-lg font-mono font-black text-xs tracking-widest whitespace-nowrap min-w-[65px] text-center shadow-inner animate-pulse">${m.scoreHome ?? 0}&nbsp;-&nbsp;${m.scoreAway ?? 0}</div>`;
    }

    // SECTION PREDIKSI MODEL JIKA TERKUNCI (VIP)
    let projectionContent = '';
    if (m.isVip) {
      projectionContent = `
        <div class="relative bg-slate-50 p-2.5 rounded-xl border border-slate-200 overflow-hidden flex items-center justify-between">
          <div class="filter blur-md select-none opacity-40 pointer-events-none">
            <span class="text-[9px] text-slate-400 block font-bold uppercase tracking-wider">PROYEKSI MODEL</span>
            <span class="text-xs sm:text-sm font-extrabold text-flash-red">Home Win / Over 2.5</span>
          </div>
          <div class="filter blur-md select-none opacity-40 pointer-events-none flex items-center gap-2 font-mono text-xs">
            <span class="font-extrabold text-slate-900 bg-amber-100 px-2 py-0.5 rounded-md border border-amber-300">@1.85</span>
            <span class="font-extrabold text-emerald-800 bg-emerald-100 px-2 py-0.5 rounded-md border border-emerald-300">82%</span>
          </div>

          <!-- OVERLAY LOCK DI ATAS PREDIKSI -->
          <div class="absolute inset-0 bg-slate-900/85 backdrop-blur-sm z-10 flex items-center justify-between px-3">
            <span class="text-[11px] font-extrabold text-amber-300 font-mono flex items-center gap-1.5">
              <i class="fa-solid fa-lock text-flash-red"></i> PREDIKSI VIP TERKUNCI
            </span>
            <button onclick="openVipModal()" class="px-2.5 py-1 bg-flash-red hover:bg-flash-redHover text-white text-[10px] font-bold rounded-lg transition-all shadow-sm">
              BUKA EKSKLUSIF
            </button>
          </div>
        </div>
      `;
    } else {
      projectionContent = `
        <div class="bg-slate-50 p-2.5 rounded-xl border border-slate-200/80 flex justify-between items-center gap-2">
          <div>
            <span class="text-[9px] text-slate-400 block font-bold uppercase tracking-wider">PROYEKSI MODEL</span>
            <span class="text-xs sm:text-sm font-extrabold text-flash-red">${m.pick}</span>
          </div>
          <div class="flex items-center gap-2 font-mono text-xs">
            <span class="font-extrabold text-slate-900 bg-amber-100 px-2 py-0.5 rounded-md border border-amber-300">@${m.odds ? m.odds.toFixed(2) : '1.65'}</span>
            <span class="font-extrabold text-emerald-800 bg-emerald-100 px-2 py-0.5 rounded-md border border-emerald-300">${m.winProb}%</span>
          </div>
        </div>
      `;
    }

    card.innerHTML = `
      <!-- LEAGUE HEADER -->
      <div class="flex justify-between items-center text-xs font-mono text-slate-500 border-b border-slate-100 pb-2">
        <div class="flex items-center gap-1.5">
          ${m.leagueLogo ? `<img src="${m.leagueLogo}" class="w-4 h-4 object-contain" />` : `<i class="fa-solid fa-trophy text-amber-500"></i>`}
          <span class="font-extrabold text-slate-900 text-[11px] font-sans tracking-wide truncate max-w-[180px] sm:max-w-none">${m.league}</span>
        </div>
        ${statusBadge}
      </div>

      <!-- MATCH MAIN DETAILS (NAMA TIM & SCORE TERLIHAT JELAS 100%) -->
      <div class="grid grid-cols-12 items-center gap-1 sm:gap-2">
        <!-- HOME TEAM -->
        <div class="col-span-4 sm:col-span-5 flex items-center gap-1.5 sm:gap-2 min-w-0">
          ${m.homeLogo ? `<img src="${m.homeLogo}" class="w-7 h-7 sm:w-8 sm:h-8 object-contain shrink-0" />` : `<i class="fa-solid fa-shield text-slate-300 text-lg shrink-0"></i>`}
          <div class="space-y-0.5 min-w-0">
            <div class="font-extrabold text-slate-900 text-xs sm:text-sm truncate">${m.homeTeam}</div>
            <div class="flex items-center gap-0.5 font-mono text-[8px] font-bold">
              ${m.homeForm ? m.homeForm.map(f => `<span class="w-3.5 h-3.5 rounded flex items-center justify-center ${f==='W'?'form-badge-w':f==='D'?'form-badge-d':'form-badge-l'}">${f}</span>`).join('') : ''}
            </div>
          </div>
        </div>

        <!-- HORIZONTAL SCORE DISPLAY -->
        <div class="col-span-4 sm:col-span-2 text-center flex justify-center items-center px-1">
          ${centerScoreDisplay}
        </div>

        <!-- AWAY TEAM -->
        <div class="col-span-4 sm:col-span-5 flex items-center justify-end gap-1.5 sm:gap-2 text-right min-w-0">
          <div class="space-y-0.5 min-w-0">
            <div class="font-extrabold text-slate-900 text-xs sm:text-sm truncate">${m.awayTeam}</div>
            <div class="flex items-center justify-end gap-0.5 font-mono text-[8px] font-bold">
              ${m.awayForm ? m.awayForm.map(f => `<span class="w-3.5 h-3.5 rounded flex items-center justify-center ${f==='W'?'form-badge-w':f==='D'?'form-badge-d':'form-badge-l'}">${f}</span>`).join('') : ''}
            </div>
          </div>
          ${m.awayLogo ? `<img src="${m.awayLogo}" class="w-7 h-7 sm:w-8 sm:h-8 object-contain shrink-0" />` : `<i class="fa-solid fa-shield text-slate-300 text-lg shrink-0"></i>`}
        </div>
      </div>

      <!-- EV INDICATORS -->
      <div class="grid grid-cols-2 gap-1.5 text-[10px] font-mono">
        <div class="px-2 py-1 rounded-md border indicator-pos flex items-center gap-1.5 font-bold">
          <i class="fa-solid fa-circle-check text-emerald-600"></i>
          <span class="truncate">${m.posEdge || '+15.5% +EV'}</span>
        </div>
        <div class="px-2 py-1 rounded-md border indicator-neg flex items-center gap-1.5 font-bold">
          <i class="fa-solid fa-triangle-exclamation text-red-600"></i>
          <span class="truncate">${m.riskFactor || '-3.8% Risk'}</span>
        </div>
      </div>

      <!-- PROYEKSI PREDIKSI MODEL (DIBLUR KHUSUS PARTAI VIP) -->
      ${projectionContent}

      <!-- CARD FOOTER BUTTONS -->
      <div class="flex items-center justify-between gap-2 text-xs pt-0.5">
        <button onclick="openAnalyticsModal(${m.id})" class="text-slate-500 hover:text-flash-red flex items-center gap-1.5 transition-colors font-medium">
          <i class="fa-solid fa-diagram-project text-emerald-600"></i>
          <span class="underline text-[10px]">Matriks Taktis Lengkap</span>
        </button>
        <button onclick="toggleParlayPick(${m.id})" class="px-3 py-1 rounded-lg font-bold text-xs flex items-center gap-1.5 ${isAdded ? 'bg-red-100 text-flash-red border border-red-300' : 'bg-flash-red hover:bg-flash-redHover text-white shadow-sm'}">
          <i class="fa-solid ${isAdded ? 'fa-minus' : 'fa-plus'}"></i>
          <span>${isAdded ? 'Hapus' : '+ Parlay'}</span>
        </button>
      </div>
    `;

    container.appendChild(card);
  });
}

function filterMatches(market) {
  selectedMarketFilter = market;
  ['ALL', '1X2', 'HDP', 'OU'].forEach(m => {
    const btn = document.getElementById(`filter-${m}`);
    if (btn) btn.className = (m === market) ? "py-2.5 px-1 rounded-xl bg-flash-red text-white text-center transition-all shadow-sm font-bold" : "py-2.5 px-1 rounded-xl bg-slate-100 text-slate-600 hover:bg-slate-200 text-center transition-all font-bold";
  });
  renderMatchesList();
}

function searchMatches() { renderMatchesList(); }

function toggleParlayPick(id) {
  const match = MOCK_TODAY_MATCHES.find(m => m.id === id);
  if (!match) return;

  const index = userParlaySlip.findIndex(p => p.id === id);
  if (index > -1) {
    userParlaySlip.splice(index, 1);
    showToast(`Dihapus: ${match.homeTeam}`);
  } else {
    if (userParlaySlip.length >= 5) {
      showToast("Maksimal 5 partai parlay!");
      return;
    }
    userParlaySlip.push(match);
    showToast(`Ditambahkan: ${match.homeTeam}`);
  }
  renderMatchesList();
  renderParlaySlip();
}

function renderParlaySlip() {
  const picksList = document.getElementById('parlayPicksList');
  const emptyState = document.getElementById('parlayEmptyState');
  const calcSummary = document.getElementById('parlayCalcSummary');
  const actions = document.getElementById('parlayActions');
  const countBadge = document.getElementById('parlayCountBadge');

  if (!countBadge) return;
  countBadge.innerText = `${userParlaySlip.length} Partai`;

  if (userParlaySlip.length === 0) {
    emptyState.classList.remove('hidden');
    picksList.innerHTML = '';
    calcSummary.classList.add('hidden');
    actions.classList.add('hidden');
    return;
  }

  emptyState.classList.add('hidden');
  calcSummary.classList.remove('hidden');
  actions.classList.remove('hidden');

  picksList.innerHTML = '';
  let totalOdds = 1.0;
  let combinedProb = 1.0;

  userParlaySlip.forEach(m => {
    totalOdds *= m.odds;
    combinedProb *= (m.winProb / 100);

    const pickItem = document.createElement('div');
    pickItem.className = "bg-slate-50 p-2.5 rounded-xl border border-slate-200 flex justify-between items-center text-xs";
    pickItem.innerHTML = `
      <div>
        <div class="font-bold text-[10px] text-slate-900">${m.homeTeam} vs ${m.awayTeam}</div>
        <div class="text-[9px] text-flash-red font-bold">${m.pick}</div>
      </div>
      <div class="flex items-center gap-1.5 font-mono">
        <span class="font-extrabold text-[11px] text-slate-900">@${m.odds.toFixed(2)}</span>
        <button onclick="toggleParlayPick(${m.id})" class="text-slate-400 hover:text-red-600"><i class="fa-solid fa-xmark"></i></button>
      </div>
    `;
    picksList.appendChild(pickItem);
  });

  document.getElementById('parlayTotalOdds').innerText = totalOdds.toFixed(2);
  document.getElementById('parlayCombinedProb').innerText = (combinedProb * 100).toFixed(1) + '%';
  document.getElementById('parlayProjectedPayout').innerText = `Rp ${Math.round(100000 * totalOdds).toLocaleString('id-ID')}`;
}

function clearParlaySlip() {
  userParlaySlip = [];
  renderMatchesList();
  renderParlaySlip();
  showToast("Slip parlay di-reset.");
}

function copyParlaySlip() {
  if (userParlaySlip.length === 0) return;
  let text = `⚽ KALKULASI PARLAY FIXSCORE ⚽\n\n`;
  let totalOdds = 1.0;
  userParlaySlip.forEach((m, idx) => {
    totalOdds *= m.odds;
    text += `${idx + 1}. ${m.homeTeam} vs ${m.awayTeam}\n   Pilihan: ${m.pick} (@${m.odds.toFixed(2)})\n`;
  });
  text += `\n🎯 Total Odds: @${totalOdds.toFixed(2)}\n`;

  const dummy = document.createElement("textarea");
  document.body.appendChild(dummy);
  dummy.value = text;
  dummy.select();
  document.execCommand("copy");
  document.body.removeChild(dummy);
  showToast("Slip parlay disalin!");
}

function openAnalyticsModal(id) {
  const match = MOCK_TODAY_MATCHES.find(m => m.id === id);
  if (!match) return;

  document.getElementById('modalMatchTitle').innerText = `${match.homeTeam} vs ${match.awayTeam}`;
  document.getElementById('modalAiNotes').innerText = match.aiNotes || "Analisis taktis kuantitatif menunjukkan dominasi penuh pada peluang xG dan konsistensi transisi lapangan tengah.";

  // MATRIKS SUPER LENGKAP (6 INDIKATOR UTAMA)
  const metricsBody = document.getElementById('modalMetricsBody');
  metricsBody.innerHTML = `
    <div class="bg-white p-2.5 rounded-xl border border-slate-200">
      <span class="text-[10px] text-slate-400 block font-bold">Rating Form 5 Match</span>
      <span class="font-bold text-emerald-600 text-sm">${match.metrics?.form || 88}%</span>
    </div>
    <div class="bg-white p-2.5 rounded-xl border border-slate-200">
      <span class="text-[10px] text-slate-400 block font-bold">Dominasi xG Score</span>
      <span class="font-bold text-emerald-600 text-sm">${match.metrics?.xG || 82}%</span>
    </div>
    <div class="bg-white p-2.5 rounded-xl border border-slate-200">
      <span class="text-[10px] text-slate-400 block font-bold">Efisiensi Serangan</span>
      <span class="font-bold text-blue-600 text-sm">84.5%</span>
    </div>
    <div class="bg-white p-2.5 rounded-xl border border-slate-200">
      <span class="text-[10px] text-slate-400 block font-bold">Soliditas Pertahanan</span>
      <span class="font-bold text-blue-600 text-sm">79.2%</span>
    </div>
    <div class="bg-white p-2.5 rounded-xl border border-slate-200">
      <span class="text-[10px] text-slate-400 block font-bold">Penguasaan Bola (Est)</span>
      <span class="font-bold text-amber-600 text-sm">58.0%</span>
    </div>
    <div class="bg-white p-2.5 rounded-xl border border-slate-200">
      <span class="text-[10px] text-slate-400 block font-bold">Head to Head Index</span>
      <span class="font-bold text-amber-600 text-sm">${match.metrics?.h2h || 80}%</span>
    </div>
  `;

  document.getElementById('analyticsModal').classList.remove('hidden');
}

function closeAnalyticsModal() { document.getElementById('analyticsModal').classList.add('hidden'); }
function openVipModal() { document.getElementById('vipModal').classList.remove('hidden'); }
function closeVipModal() { document.getElementById('vipModal').classList.add('hidden'); }

function showToast(msg) {
  const toast = document.getElementById('toast');
  document.getElementById('toastMsg').innerText = msg;
  toast.classList.remove('hidden');
  setTimeout(() => { toast.classList.add('hidden'); }, 3000);
}
