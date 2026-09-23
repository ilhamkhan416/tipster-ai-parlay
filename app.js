
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
          <p>Belum ada prediksi yang dirilis untuk hari ini.</p>
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
      <div class="bg-sbobet-card rounded border border-sbobet-border hover:border-sbobet-accent/50 transition overflow-hidden">
        <div class="bg-sbobet-header px-4 py-2 border-b border-sbobet-border flex justify-between items-center text-xs">
          <span class="font-bold text-sbobet-accent uppercase tracking-wider">#${index + 1} ${item.league}</span>
          <span class="text-slate-300 font-mono">${item.kickoff_time} WIB</span>
        </div>
        <div class="p-4">
          <div class="flex justify-between items-center mb-4">
            <div class="w-2/5 text-right font-bold text-sm text-white">${item.home_team}</div>
            <div class="w-1/5 text-center text-xs font-mono font-bold bg-sbobet-header py-1 px-2 rounded text-slate-400 border border-sbobet-border">VS</div>
            <div class="w-2/5 text-left font-bold text-sm text-white">${item.away_team}</div>
          </div>
          <div class="bg-sbobet-header rounded border border-sbobet-border p-2.5 flex justify-between items-center">
            <div>
              <div class="text-[10px] text-slate-400 uppercase font-bold tracking-wider">Tips AI (Pasaran)</div>
              <div class="text-sm font-extrabold text-sbobet-accent">
                ${item.prediction} <span class="text-xs text-white">@${item.odds}</span>
              </div>
            </div>
            <div class="text-right">
              <div class="text-[10px] text-slate-400 uppercase font-bold tracking-wider">Win Rate</div>
              <div class="text-sm font-black text-sbobet-green font-mono">${item.win_rate}%</div>
            </div>
          </div>
        </div>
      </div>
    `;
    container.innerHTML += card;
  });
}
