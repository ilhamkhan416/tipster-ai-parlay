document.addEventListener('DOMContentLoaded', () => {
  let selectedMarketFilter = 'ALL';
  let userParlaySlip = [];

  // --- INITIAL RENDERING ---
  renderMatchesList();
  renderHistoryTable();
  setupEventListeners();

  // --- EVENT LISTENERS INITIALIZATION ---
  function setupEventListeners() {
    // Navigation Tabs
    document.querySelectorAll('.nav-btn, .footer-nav-link').forEach(btn => {
      btn.addEventListener('click', (e) => {
        e.preventDefault();
        const target = btn.id ? btn.id.replace('nav-', '') : btn.getAttribute('data-target');
        switchTab(target);
      });
    });

    // Mobile Navigation Tabs
    document.getElementById('mnav-dashboard').addEventListener('click', () => { switchTab('dashboard'); toggleMobileMenu(); });
    document.getElementById('mnav-history').addEventListener('click', () => { switchTab('history'); toggleMobileMenu(); });
    document.getElementById('mnav-algorithm').addEventListener('click', () => { switchTab('algorithm'); toggleMobileMenu(); });

    // Filter Buttons
    document.querySelectorAll('.filter-btn').forEach(btn => {
      btn.addEventListener('click', () => {
        const market = btn.id.replace('filter-', '');
        filterMatches(market);
      });
    });

    // Search Bar Input
    document.getElementById('searchInput').addEventListener('keyup', () => {
      renderMatchesList();
    });

    // Mobile Menu Toggle
    document.getElementById('btn-mobile-menu').addEventListener('click', toggleMobileMenu);

    // Telegram Modal Triggers
    document.getElementById('btn-telegram-header').addEventListener('click', openVipModal);
    document.getElementById('btn-close-vip').addEventListener('click', closeVipModal);

    // Analytics Modal Triggers
    document.getElementById('btn-close-analytics').addEventListener('click', closeAnalyticsModal);
    document.getElementById('btn-dismiss-analytics').addEventListener('click', closeAnalyticsModal);

    // Parlay Actions
    document.getElementById('btn-copy-parlay').addEventListener('click', copyParlaySlip);
    document.getElementById('btn-clear-parlay').addEventListener('click', clearParlaySlip);
    
    // Logo Click
    document.getElementById('brand-logo').addEventListener('click', (e) => {
      e.preventDefault();
      switchTab('dashboard');
    });
  }

  // --- TAB SWITCHING ---
  function switchTab(tabName) {
    document.querySelectorAll('.tab-content').forEach(el => el.classList.add('hidden'));

    const inactiveClass = "px-4 py-2.5 rounded-t-lg transition-all text-white hover:bg-black/20 flex items-center gap-2 font-bold nav-btn";
    document.querySelectorAll('.nav-btn').forEach(btn => btn.className = inactiveClass);

    const targetTab = document.getElementById(`tab-${tabName}`);
    if (targetTab) targetTab.classList.remove('hidden');

    const activeNav = document.getElementById(`nav-${tabName}`);
    if (activeNav) {
      activeNav.className = "px-4 py-2.5 rounded-t-lg transition-all text-flash-red bg-white shadow-sm flex items-center gap-2 font-bold nav-btn";
    }

    window.scrollTo({ top: 0, behavior: 'smooth' });
  }

  // --- MATCH RENDERING ---
  function renderMatchesList() {
    const container = document.getElementById('matchesContainer');
    container.innerHTML = '';

    let filtered = MOCK_TODAY_MATCHES.filter(m => {
      if (selectedMarketFilter === 'ALL') return true;
      return m.marketType === selectedMarketFilter;
    });

    const searchTerm = document.getElementById('searchInput').value.toLowerCase();
    if (searchTerm) {
      filtered = filtered.filter(m => 
        m.homeTeam.toLowerCase().includes(searchTerm) || 
        m.awayTeam.toLowerCase().includes(searchTerm) || 
        m.league.toLowerCase().includes(searchTerm)
      );
    }

    if (filtered.length === 0) {
      container.innerHTML = `
        <div class="bg-white p-6 rounded-xl text-center space-y-2 border border-flash-border">
          <i class="fa-solid fa-futbol text-xl text-gray-400"></i>
          <p class="text-xs text-flash-textMuted">Tidak ada partai sepak bola yang cocok dengan kata kunci atau filter yang dipilih.</p>
        </div>
      `;
      return;
    }

    filtered.forEach((m, index) => {
      const isAdded = userParlaySlip.some(p => p.id === m.id);
      const card = document.createElement('div');
      card.className = "bg-white flash-card-hover rounded-xl p-3.5 sm:p-4 border border-flash-border flash-shadow relative space-y-3";

      card.innerHTML = `
        <div class="flex justify-between items-center text-xs font-mono text-flash-textMuted border-b border-flash-border pb-2">
          <div class="flex items-center gap-2">
            <i class="fa-solid fa-futbol text-emerald-600 text-xs"></i>
            <span class="font-extrabold text-flash-textPrimary text-[11px] sm:text-xs font-sans tracking-wide">${m.league}</span>
          </div>
          <span class="bg-gray-100 px-2 py-0.5 rounded border border-flash-border text-flash-textPrimary text-[11px] font-bold">
            <i class="fa-regular fa-clock mr-1 text-flash-red"></i>${m.kickoff}
          </span>
        </div>

        <div class="grid grid-cols-12 items-center gap-2 ${m.isVip ? 'blur-lock' : ''}">
          <div class="col-span-5 space-y-1">
            <div class="font-extrabold text-flash-textPrimary text-sm sm:text-base flex items-center gap-1.5">
              <i class="fa-solid fa-shirt text-xs text-flash-red"></i>
              <span>${m.homeTeam}</span>
            </div>
            <div class="flex items-center gap-1 font-mono text-[9px] font-bold">
              <span class="text-gray-400 font-sans font-normal">Form:</span>
              ${m.homeForm.map(f => `<span class="w-4 h-4 rounded flex items-center justify-center ${f==='W'?'form-badge-w':f==='D'?'form-badge-d':'form-badge-l'}">${f}</span>`).join('')}
            </div>
          </div>

          <div class="col-span-2 text-center">
            <span class="text-[10px] font-mono text-emerald-800 font-bold bg-emerald-50 px-2 py-0.5 rounded border border-emerald-200">VS</span>
          </div>

          <div class="col-span-5 text-right space-y-1">
            <div class="font-extrabold text-flash-textPrimary text-sm sm:text-base flex items-center justify-end gap-1.5">
              <span>${m.awayTeam}</span>
              <i class="fa-solid fa-shirt text-xs text-gray-500"></i>
            </div>
            <div class="flex items-center justify-end gap-1 font-mono text-[9px] font-bold">
              <span class="text-gray-400 font-sans font-normal">Form:</span>
              ${m.awayForm.map(f => `<span class="w-4 h-4 rounded flex items-center justify-center ${f==='W'?'form-badge-w':f==='D'?'form-badge-d':'form-badge-l'}">${f}</span>`).join('')}
            </div>
          </div>
        </div>

        <div class="grid grid-cols-1 sm:grid-cols-2 gap-2 text-[11px] font-mono">
          <div class="px-2.5 py-1 rounded border indicator-pos flex items-center gap-1.5 font-bold">
            <i class="fa-solid fa-circle-check text-emerald-600"></i>
            <span>${m.posEdge}</span>
          </div>
          <div class="px-2.5 py-1 rounded border indicator-neg flex items-center gap-1.5 font-bold">
            <i class="fa-solid fa-triangle-exclamation text-red-600"></i>
            <span>${m.riskFactor}</span>
          </div>
        </div>

        ${m.isVip ? `
          <div class="absolute inset-0 bg-white/95 backdrop-blur-sm rounded-xl flex flex-col items-center justify-center p-4 text-center z-20 space-y-2 border border-flash-border">
            <div class="w-8 h-8 rounded-full bg-flash-redSoft text-flash-red flex items-center justify-center text-xs font-bold border border-red-200">
              <i class="fa-solid fa-lock"></i>
            </div>
            <div class="font-extrabold text-flash-textPrimary text-xs">PARTAI #0${index+1} KHUSUS VIP MEMBER</div>
            <p class="text-[11px] text-flash-textMuted max-w-[220px]">Buka kunci 6 partai VIP harian & racikan statistik.</p>
            <button class="btn-unlock-vip px-3 py-1 bg-flash-red hover:bg-flash-redHover text-white font-bold text-xs rounded transition-all shadow-sm">
              BUKA AKSES VIP
            </button>
          </div>
        ` : ''}

        <div class="bg-gray-50 p-2.5 rounded-lg border border-flash-border flex flex-wrap justify-between items-center gap-2">
          <div>
            <span class="text-[10px] text-flash-textMuted block font-bold">PROYEKSI MODEL KUANTITATIF</span>
            <span class="text-xs sm:text-sm font-extrabold text-flash-red">${m.pick}</span>
          </div>

          <div class="flex items-center gap-3 font-mono text-xs">
            <div class="text-right">
              <span class="text-[10px] text-flash-textMuted block font-sans">VALUE ODDS</span>
              <span class="font-extrabold text-flash-textPrimary bg-amber-100 text-amber-900 px-1.5 py-0.5 rounded border border-amber-300">${m.odds.toFixed(2)}</span>
            </div>
            <div class="text-right">
              <span class="text-[10px] text-emerald-800 font-bold block font-sans">PROBABILITAS</span>
              <span class="font-extrabold text-emerald-700 bg-emerald-100 px-1.5 py-0.5 rounded border border-emerald-300">${m.winProb}%</span>
            </div>
          </div>
        </div>

        <div class="flex items-center justify-between gap-2 pt-0.5 text-xs">
          <button class="btn-analytics text-flash-textMuted hover:text-flash-red flex items-center gap-1.5 transition-colors font-medium" data-id="${m.id}">
            <i class="fa-solid fa-diagram-project text-emerald-600"></i>
            <span class="underline text-[11px]">Matriks Taktis &amp; Stats</span>
          </button>

          <button class="btn-toggle-parlay px-3 py-1 rounded font-bold transition-all text-xs flex items-center gap-1.5 ${isAdded ? 'bg-red-100 text-flash-red border border-red-300' : 'bg-flash-red hover:bg-flash-redHover text-white shadow-sm'}" data-id="${m.id}">
            <i class="fa-solid ${isAdded ? 'fa-minus' : 'fa-plus'}"></i>
            <span>${isAdded ? 'Hapus Slip' : '+ Parlay'}</span>
          </button>
        </div>
      `;

      // Event listeners for dynamic buttons inside card
      const unlockBtn = card.querySelector('.btn-unlock-vip');
      if (unlockBtn) unlockBtn.addEventListener('click', openVipModal);

      const analyticsBtn = card.querySelector('.btn-analytics');
      if (analyticsBtn) analyticsBtn.addEventListener('click', () => openAnalyticsModal(m.id));

      const parlayBtn = card.querySelector('.btn-toggle-parlay');
      if (parlayBtn) parlayBtn.addEventListener('click', () => toggleParlayPick(m.id));

      container.appendChild(card);
    });
  }

  // --- PARLAY CALCULATOR CORE ---
  function toggleParlayPick(id) {
    const match = MOCK_TODAY_MATCHES.find(m => m.id === id);
    if (!match) return;

    const index = userParlaySlip.findIndex(p => p.id === id);
    if (index > -1) {
      userParlaySlip.splice(index, 1);
      showToast(`Dihapus dari racikan: ${match.homeTeam}`);
    } else {
      if (userParlaySlip.length >= 5) {
        showToast("Maksimal racikan 5 partai dalam 1 slip parlay!");
        return;
      }
      userParlaySlip.push(match);
      showToast(`Ditambahkan ke racikan: ${match.homeTeam}`);
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
      pickItem.className = "bg-gray-50 p-2.5 rounded-lg border border-flash-border flex justify-between items-center text-xs";
      pickItem.innerHTML = `
        <div>
          <div class="font-bold text-flash-textPrimary text-[11px]">${m.homeTeam} vs ${m.awayTeam}</div>
          <div class="text-[10px] text-flash-red font-bold">${m.pick}</div>
        </div>
        <div class="flex items-center gap-2 font-mono">
          <span class="text-flash-textPrimary font-extrabold text-xs">@${m.odds.toFixed(2)}</span>
          <button class="btn-remove-pick text-gray-400 hover:text-red-600 p-0.5" data-id="${m.id}">
            <i class="fa-solid fa-xmark"></i>
          </button>
        </div>
      `;

      pickItem.querySelector('.btn-remove-pick').addEventListener('click', () => toggleParlayPick(m.id));
      picksList.appendChild(pickItem);
    });

    document.getElementById('parlayTotalOdds').innerText = totalOdds.toFixed(2);
    document.getElementById('parlayCombinedProb').innerText = (combinedProb * 100).toFixed(1) + '%';
    
    const projectedReturn = Math.round(100000 * totalOdds);
    document.getElementById('parlayProjectedPayout').innerText = `Rp ${projectedReturn.toLocaleString('id-ID')}`;
  }

  function clearParlaySlip() {
    userParlaySlip = [];
    renderMatchesList();
    renderParlaySlip();
    showToast("Racikan slip parlay di-reset.");
  }

  function copyParlaySlip() {
    if (userParlaySlip.length === 0) return;

    let text = `⚽ KALKULASI PARLAY KUANTITATIF - FIXSCORE ⚽\n`;
    text += `📅 Tanggal Rilis: ${new Date().toLocaleDateString('id-ID')}\n\n`;

    let totalOdds = 1.0;
    userParlaySlip.forEach((m, idx) => {
      totalOdds *= m.odds;
      text += `${idx + 1}. ${m.homeTeam} vs ${m.awayTeam}\n   Pilihan Model: ${m.pick} (@${m.odds.toFixed(2)})\n`;
    });

    text += `\n🎯 Multiplier Total Odds: @${totalOdds.toFixed(2)}\n`;
    text += `📈 Data & Metodologi: FIXSCORE Quantitative Pitch Engine\n`;

    const dummy = document.createElement("textarea");
    document.body.appendChild(dummy);
    dummy.value = text;
    dummy.select();
    document.execCommand("copy");
    document.body.removeChild(dummy);

    showToast("Data kalkulasi FIXSCORE berhasil disalin!");
  }

  // --- FILTERS & MODALS ---
  function filterMatches(market) {
    selectedMarketFilter = market;
    document.querySelectorAll('.filter-btn').forEach(btn => {
      const btnMarket = btn.id.replace('filter-', '');
      if (btnMarket === market) {
        btn.className = "filter-btn px-3.5 py-1.5 rounded bg-flash-red text-white transition-all shadow-sm font-bold";
      } else {
        btn.className = "filter-btn px-3.5 py-1.5 rounded bg-gray-100 text-flash-textSecondary hover:bg-gray-200 transition-all font-bold";
      }
    });
    renderMatchesList();
  }

  function openAnalyticsModal(id) {
    const match = MOCK_TODAY_MATCHES.find(m => m.id === id);
    if (!match) return;

    document.getElementById('modalMatchTitle').innerText = `${match.homeTeam} vs ${match.awayTeam}`;
    document.getElementById('modalAiNotes').innerText = match.aiNotes;

    const metricsBody = document.getElementById('modalMetricsBody');
    metricsBody.innerHTML = `
      <div class="space-y-1">
        <div class="flex justify-between text-flash-textMuted font-sans">
          <span>Performa Form 5 Match:</span>
          <span class="text-emerald-700 font-bold font-mono">${match.metrics.form}% (Positif)</span>
        </div>
        <div class="w-full bg-gray-200 rounded-full h-1.5 overflow-hidden">
          <div class="bg-emerald-600 h-1.5 rounded-full" style="width: ${match.metrics.form}%"></div>
        </div>
      </div>

      <div class="space-y-1">
        <div class="flex justify-between text-flash-textMuted font-sans">
          <span>Rating Head-to-Head:</span>
          <span class="text-flash-textPrimary font-bold font-mono">${match.metrics.h2h}%</span>
        </div>
        <div class="w-full bg-gray-200 rounded-full h-1.5 overflow-hidden">
          <div class="bg-gray-600 h-1.5 rounded-full" style="width: ${match.metrics.h2h}%"></div>
        </div>
      </div>

      <div class="space-y-1">
        <div class="flex justify-between text-flash-textMuted font-sans">
          <span>Matriks Expected Goals (xG):</span>
          <span class="text-emerald-700 font-bold font-mono">${match.metrics.xG}% (Unggul)</span>
        </div>
        <div class="w-full bg-gray-200 rounded-full h-1.5 overflow-hidden">
          <div class="bg-emerald-500 h-1.5 rounded-full" style="width: ${match.metrics.xG}%"></div>
        </div>
      </div>

      <div class="space-y-1">
        <div class="flex justify-between text-flash-textMuted font-sans">
          <span>Market Value Edge Index:</span>
          <span class="text-amber-700 font-bold font-mono">${match.metrics.marketVal}%</span>
        </div>
        <div class="w-full bg-gray-200 rounded-full h-1.5 overflow-hidden">
          <div class="bg-amber-500 h-1.5 rounded-full" style="width: ${match.metrics.marketVal}%"></div>
        </div>
      </div>
    `;

    document.getElementById('analyticsModal').classList.remove('hidden');
  }

  function closeAnalyticsModal() {
    document.getElementById('analyticsModal').classList.add('hidden');
  }

  function openVipModal() {
    document.getElementById('vipModal').classList.remove('hidden');
  }

  function closeVipModal() {
    document.getElementById('vipModal').classList.add('hidden');
  }

  function renderHistoryTable() {
    const tbody = document.getElementById('historyTableBody');
    tbody.innerHTML = '';

    MOCK_HISTORY_LOGS.forEach(log => {
      const tr = document.createElement('tr');
      tr.className = "hover:bg-gray-50 transition-colors";
      tr.innerHTML = `
        <td class="p-3 font-mono text-flash-textMuted text-[11px]">
          <div class="font-bold text-flash-textPrimary">${log.date}</div>
          <div class="text-[10px] text-gray-400 font-sans">${log.league}</div>
        </td>
        <td class="p-3 font-bold text-flash-textPrimary text-xs flex items-center gap-1.5">
          <i class="fa-solid fa-futbol text-[10px] text-gray-400"></i>
          <span>${log.match}</span>
        </td>
        <td class="p-3 font-bold text-flash-red text-xs">${log.pick}</td>
        <td class="p-3 font-mono font-extrabold text-flash-textPrimary text-xs">@${log.odds.toFixed(2)}</td>
        <td class="p-3 font-mono font-extrabold text-flash-textPrimary text-xs">${log.score}</td>
        <td class="p-3">
          <span class="px-2 py-0.5 rounded text-[10px] font-bold font-mono flex items-center gap-1 w-fit ${log.status === 'WIN' ? 'bg-emerald-100 text-emerald-800 border border-emerald-300' : 'bg-red-100 text-red-800 border border-red-300'}">
            <i class="fa-solid ${log.status === 'WIN' ? 'fa-check text-emerald-600' : 'fa-xmark text-red-600'}"></i>
            ${log.status}
          </span>
        </td>
      `;
      tbody.appendChild(tr);
    });
  }

  function toggleMobileMenu() {
    document.getElementById('mobileMenu').classList.toggle('hidden');
  }

  function showToast(msg) {
    const toast = document.getElementById('toast');
    document.getElementById('toastMsg').innerText = msg;
    toast.classList.remove('hidden');
    setTimeout(() => {
      toast.classList.add('hidden');
    }, 3000);
  }
});
