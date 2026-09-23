document.addEventListener('DOMContentLoaded', () => {
  fetch('data/history.json')
    .then(response => {
      if (!response.ok) throw new Error('Gagal mengambil riwayat.');
      return response.json();
    })
    .then(data => {
      renderHistory(data.history);
    })
    .catch(err => {
      console.error(err);
      document.getElementById('history-container').innerHTML = `
        <div class="text-center py-12 text-slate-400">
          <p>Belum ada riwayat hasil prediksi sebelumnya.</p>
        </div>
      `;
    });
});

function renderHistory(history) {
  const container = document.getElementById('history-container');
  container.innerHTML = '';

  if (!history || history.length === 0) {
    container.innerHTML = `<p class="text-center text-slate-400 py-8">Belum ada data riwayat.</p>`;
    return;
  }

  history.forEach(item => {
    const isWin = item.status.toUpperCase() === 'WIN';
    const statusColor = isWin ? 'bg-sbobet-green/20 text-sbobet-green border-sbobet-green/30' : 'bg-sbobet-red/20 text-sbobet-red border-sbobet-red/30';
    
    const card = `
      <div class="bg-sbobet-card rounded border border-sbobet-border p-4 flex flex-col md:flex-row justify-between items-center gap-3">
        <div class="flex-1 text-center md:text-left">
          <div class="text-xs text-slate-400 font-mono">${item.date} | ${item.league}</div>
          <div class="font-bold text-white text-sm mt-0.5">${item.home_team} vs ${item.away_team}</div>
          <div class="text-xs text-sbobet-accent mt-1">Tips: ${item.prediction} (@${item.odds})</div>
        </div>
        <div class="text-center md:text-right">
          <div class="text-xs text-slate-300 font-mono">Skor Akhir: <span class="font-bold text-white">${item.score}</span></div>
          <span class="inline-block mt-1 px-3 py-0.5 text-xs font-bold rounded border uppercase ${statusColor}">
            ${item.status}
          </span>
        </div>
      </div>
    `;
    container.innerHTML += card;
  });
}
