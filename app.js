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
        <div class="col-span-full text-center py-12 text-organic-muted">
          <p>Belum ada prediksi yang dirilis untuk hari ini.</p>
        </div>
      `;
    });
});

function renderMatches(matches) {
  const container = document.getElementById('match-container');
  container.innerHTML = '';

  if (!matches || matches.length === 0) {
    container.innerHTML = `<p class="col-span-full text-center text-organic-muted py-8">Tidak ada pertandingan terpilih.</p>`;
    return;
  }

  matches.forEach((item, index) => {
    const card = `
      <div class="bg-organic-card rounded-2xl p-5 border border-organic-border shadow-sm hover:shadow-md transition-shadow flex flex-col justify-between">
        <div>
          <!-- Header Liga -->
          <div class="flex justify-between items-center text-xs text-organic-muted pb-3 mb-3 border-b border-organic-border">
            <span class="font-medium text-organic-text">#${index + 1} ${item.league}</span>
            <span class="font-mono">${item.kickoff_time} WIB</span>
          </div>

          <!-- Tim Bertanding -->
          <div class="flex justify-between items-center my-2">
            <div class="w-2/5 text-right font-semibold text-sm text-organic-text">${item.home_team}</div>
            <div class="w-1/5 text-center text-xs text-organic-muted font-serif italic">vs</div>
            <div class="w-2/5 text-left font-semibold text-sm text-organic-text">${item.away_team}</div>
          </div>
        </div>

        <!-- Panel Prediksi -->
        <div class="mt-4 pt-3 bg-organic-accentBg rounded-xl p-3 flex justify-between items-center">
          <div>
            <div class="text-[10px] text-organic-muted uppercase tracking-wider font-semibold">Rekomendasi</div>
            <div class="text-sm font-bold text-organic-accent">
              ${item.prediction} <span class="text-xs text-organic-muted font-normal">(@${item.odds})</span>
            </div>
          </div>
          <div class="text-right">
            <div class="text-[10px] text-organic-muted uppercase tracking-wider font-semibold">Win Rate</div>
            <div class="text-sm font-bold text-organic-accent font-mono">${item.win_rate}%</div>
          </div>
        </div>
      </div>
    `;
    container.innerHTML += card;
  });
}
