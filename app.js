document.addEventListener("DOMContentLoaded", () => {
  const matchesContainer = document.getElementById("matches-container");
  const filterButtons = document.querySelectorAll(".filter-btn");

  // Fungsi untuk merender daftar pertandingan
  function renderMatches(filter = "all") {
    matchesContainer.innerHTML = "";

    const filteredMatches = matchesData.filter(match => {
      if (filter === "all") return true;
      return match.recommendation.type === filter;
    });

    if (filteredMatches.length === 0) {
      matchesContainer.innerHTML = `
        <div class="bg-white p-8 rounded-xl text-center border border-gray-200">
          <p class="text-gray-500 font-medium">Tidak ada pertandingan untuk kategori pasaran ini.</p>
        </div>
      `;
      return;
    }

    filteredMatches.forEach(match => {
      const matchCard = document.createElement("div");
      matchCard.className = "match-card bg-white rounded-xl p-5 border border-flash-border shadow-sm";

      matchCard.innerHTML = `
        <!-- Header Pertandingan (Liga & Waktu) -->
        <div class="flex justify-between items-center border-b border-gray-100 pb-3 mb-4">
          <div class="flex items-center space-x-2">
            <span class="bg-gray-100 text-gray-700 text-[11px] font-bold px-2.5 py-1 rounded">
              ${match.league}
            </span>
            <span class="text-xs text-gray-400 font-mono">
              <i class="fa-regular fa-clock"></i> ${match.time}
            </span>
          </div>
          <span class="text-[10px] uppercase font-mono font-bold tracking-wider px-2 py-0.5 rounded bg-emerald-50 text-emerald-600 border border-emerald-100">
            +EV Matrix
          </span>
        </div>

        <!-- Tim & Logo -->
        <div class="grid grid-cols-1 md:grid-cols-12 gap-4 items-center">
          <!-- Tim -->
          <div class="md:col-span-5 space-y-3">
            <div class="flex items-center justify-between">
              <div class="flex items-center space-x-3">
                <img src="${match.homeLogo}" alt="${match.homeTeam}" class="w-7 h-7 object-contain" onerror="this.src='https://via.placeholder.com/28'">
                <span class="font-bold text-sm text-gray-900">${match.homeTeam}</span>
              </div>
              <span class="text-xs font-mono font-semibold text-gray-500">xG ${match.xGHome}</span>
            </div>
            <div class="flex items-center justify-between">
              <div class="flex items-center space-x-3">
                <img src="${match.awayLogo}" alt="${match.awayTeam}" class="w-7 h-7 object-contain" onerror="this.src='https://via.placeholder.com/28'">
                <span class="font-bold text-sm text-gray-900">${match.awayTeam}</span>
              </div>
              <span class="text-xs font-mono font-semibold text-gray-500">xG ${match.xGAway}</span>
            </div>
          </div>

          <!-- Probability Bar -->
          <div class="md:col-span-3 bg-gray-50 p-3 rounded-lg border border-gray-100 space-y-2">
            <div class="flex justify-between text-[11px] font-mono">
              <span class="text-gray-600">H: ${match.probHome}</span>
              <span class="text-gray-400">D: ${match.probDraw}</span>
              <span class="text-gray-600">A: ${match.probAway}</span>
            </div>
            <div class="w-full bg-gray-200 h-2 rounded-full overflow-hidden flex">
              <div style="width: ${match.probHome}" class="bg-emerald-500 h-full"></div>
              <div style="width: ${match.probDraw}" class="bg-gray-400 h-full"></div>
              <div style="width: ${match.probAway}" class="bg-sky-500 h-full"></div>
            </div>
            <div class="text-[10px] text-gray-400 text-center font-mono">Model Output Split</div>
          </div>

          <!-- Rekomendasi Algoritma -->
          <div class="md:col-span-4 bg-emerald-50/60 rounded-lg p-3 border border-emerald-100 flex flex-col justify-between">
            <div class="flex justify-between items-start">
              <div>
                <span class="text-[10px] font-bold text-emerald-800 uppercase tracking-wider block">
                  Pilihan Utama (${match.recommendation.market})
                </span>
                <span class="text-sm font-black text-emerald-950 block">
                  ${match.recommendation.pick}
                </span>
              </div>
              <div class="text-right">
                <span class="text-xs font-mono font-bold text-emerald-900 bg-white px-2 py-0.5 rounded border border-emerald-200 block shadow-sm">
                  ${match.recommendation.odds}
                </span>
                <span class="text-[10px] font-mono text-emerald-700 block mt-0.5">
                  Prob: ${match.recommendation.probability}
                </span>
              </div>
            </div>
          </div>
        </div>

        <!-- Analisis Singkat -->
        <div class="mt-3 pt-3 border-t border-gray-100 text-xs text-gray-500 flex items-start space-x-2">
          <i class="fa-solid fa-circle-info text-emerald-600 mt-0.5"></i>
          <span>${match.reasoning}</span>
        </div>
      `;

      matchesContainer.appendChild(matchCard);
    });
  }

  // Handling Filter Click
  filterButtons.forEach(btn => {
    btn.addEventListener("click", () => {
      filterButtons.forEach(b => b.classList.remove("active", "bg-flash-dark", "text-white"));
      filterButtons.forEach(b => b.classList.add("bg-white", "text-gray-700"));

      btn.classList.add("active", "bg-flash-dark", "text-white");
      btn.classList.remove("bg-white", "text-gray-700");

      const filterValue = btn.getAttribute("data-filter");
      renderMatches(filterValue);
    });
  });

  // Render awal saat pertama kali dimuat
  renderMatches("all");
});
