import requests
import json
from datetime import datetime, timedelta

# API Publik Gratis (Tanpa Limit Harian Ketat & Tanpa API Key Terbatas)
FREE_API_URL = "https://www.thesportsdb.com/api/v1/json/3/eventsday.php?d={date}&s=Soccer"

def fetch_all_real_matches_free(days_ago=1):
    """
    Menarik SELURUH pertandingan nyata yang sudah selesai dari API Publik Gratis
    """
    target_date = (datetime.now() - timedelta(days=days_ago)).strftime('%Y-%m-%d')
    print(f"🔄 Menarik SELURUH data pertandingan nyata tanggal: {target_date} (Via Free Premium API)...")

    url = FREE_API_URL.format(date=target_date)
    
    try:
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            data = response.json()
            events = data.get('events', [])
            
            if not events:
                print("⚠️ Data tanggal ini kosong, mencoba hari sebelumnya...")
                return []

            # Filter hanya pertandingan yang punya skor akhir nyata
            finished_matches = []
            for ev in events:
                if ev.get('intHomeScore') is not None and ev.get('intAwayScore') is not None:
                    finished_matches.append({
                        'league': ev.get('strLeague', 'Soccer League'),
                        'home': ev.get('strHomeTeam'),
                        'away': ev.get('strAwayTeam'),
                        'score_home': int(ev.get('intHomeScore')),
                        'score_away': int(ev.get('intAwayScore')),
                    })
            return finished_matches
        else:
            print(f"❌ HTTP Error: {response.status_code}")
    except Exception as e:
        print(f"❌ Error Request API: {e}")
        
    return []

def run_backtest_engine():
    # Coba ambil data kemarin (1 hari lalu)
    matches = fetch_all_real_matches_free(days_ago=1)

    # Jika kemarin tidak ada data (misal jeda internasional), ambil 2 hari lalu
    if not matches:
        matches = fetch_all_real_matches_free(days_ago=2)

    if not matches:
        print("❌ Gagal mendapatkan data dari API Gratis. Silakan jalankan ulang nanti.")
        return

    print(f"\n✅ BERHASIL MENDAPATKAN {len(matches)} PERTANDINGAN NYATA KEMARIN!\n")
    print("==========================================================")
    print("📊 MENJALANKAN BACKTEST MODEL AI DENGAN DATA NYATA")
    print("==========================================================\n")

    wins = 0
    losses = 0
    draws = 0
    total_profit = 0.0

    for idx, m in enumerate(matches, 1):
        league = m['league']
        home = m['home']
        away = m['away']
        s_home = m['score_home']
        s_away = m['score_away']

        # --- LOGIKA PREDIKSI MODEL AI KAMU ---
        # Contoh: Model memprediksi Tuan Rumah (Home) Win dengan Odds 1.85
        predicted_pick = f"{home} Win"
        odds = 1.85

        diff = s_home - s_away

        # Evaluasi Hasil Nyata
        if diff > 0:
            status = "WIN"
            profit = odds - 1.0
            wins += 1
        elif diff == 0:
            status = "DRAW"
            profit = 0.0
            draws += 1
        else:
            status = "LOSE"
            profit = -1.0
            losses += 1

        total_profit += profit
        print(f"{idx}. [{status}] {league}: {home} ({s_home}) vs ({s_away}) {away} | Pick: {predicted_pick} | Profit: {profit:+.2f} U")

    total_evaluated = wins + losses + draws
    win_rate = (wins / total_evaluated * 100) if total_evaluated > 0 else 0
    roi = (total_profit / total_evaluated * 100) if total_evaluated > 0 else 0

    print("\n==========================================")
    print("🎯 RINGKASAN HASIL PERFORMA BACKTEST MODEL AI")
    print("==========================================")
    print(f"Total Pertandingan Evaluasi : {total_evaluated}")
    print(f"Hasil Akhir                 : {wins} Win - {draws} Draw - {losses} Lose")
    print(f"Win Rate                    : {win_rate:.1f}%")
    print(f"Total Net Yield             : {total_profit:+.2f} Unit")
    print(f"ROI (+EV)                   : {roi:+.1f}%")
    print("==========================================\n")

if __name__ == "__main__":
    run_backtest_engine()
