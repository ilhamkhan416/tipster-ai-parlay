document.addEventListener('DOMContentLoaded', () => {
  fetch('data/today.json')
    .then(response => {
      if (!response.ok) throw new Error('Gagal mengambil data.');
      return response.json();
    })
    .then(data => {
      document.getElementById('last-update').innerText = data.last_updated || 'Hari Ini';
      renderMatches(data.matches);
    })
    .catch(err => {
      console.error(err);
      document.getElementById('match-container').innerHTML = `
        <div class="col-span-full text-center py-12 text-slate-400">
          <p>Belum ada data prediksi untuk hari ini.</p>
        </div>
      `;
    });
});

function renderMatches(matches) {
  const container = document.getElementById('match-container');
  container.innerHTML = '';

  if (!matches || matches.length === 0) {
    container.innerHTML = `<p class="col-span-full text-center text-slate-400 py-8">Tidak ada pertandingan terpilih.</p>`;
    return;
  }

  matches.forEach((item, index) => {
    const card = `
      <div class="bg-pro-card rounded-lg border border-pro-border hover:border-slate-500 transition overflow-hidden flex flex-col justify-between">
        <!-- Header Liga & Waktu -->
        <div class="bg-pro-header px-4 py-2 border-b border-pro-border flex justify-between items-center text-xs">
          <span class="font-semibold text-pro-accent uppercase tracking-wider">#${index + 1} ${item.league}</span>
          <span class="text-slate-400 font-mono">${item.kickoff_time} WIB</span>
        </div>

        <div class="p-4">
          <!-- Tim Bertanding -->
          <div class="flex justify-between items-center my-2">
            <div class="w-2/5 text-right font-bold text-sm text-white">${item.home_team}</div>
            <div class="w-1/5 text-center text-[11px] font-mono font-semibold text-slate-400 bg-pro-header py-0.5 px-2 rounded border border-pro-border">VS</div>
            <div class="w-2/5 text-left font-bold text-sm text-white">${item.away_team}</div>
          </div>

          <!-- Panel Rekomendasi / Tips -->
          <div class="mt-4 pt-3 border-t border-pro-border/60 flex justify-between items-center">
            <div>
              <div class="text-[10px] text-slate-400 uppercase font-semibold">Rekomendasi Analisis</div>
              <div class="text-sm font-bold text-pro-highlight">
                ${item.prediction} <span class="text-xs text-slate-300 font-normal">(@${item.odds})</span>
              </div>
            </div>
            <div class="text-right">
              <div class="text-[10px] text-slate-400 uppercase font-semibold">Probabilitas</div>
              <div class="text-sm font-bold text-pro-green font-mono">${item.win_rate}%</div>
            </div>
          </div>
        </div>
      </div>
    `;
    container.innerHTML += card;
  });
}
