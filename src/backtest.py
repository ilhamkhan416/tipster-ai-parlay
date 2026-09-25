import json
import requests
from datetime import datetime, timedelta

# API Key milikmu
API_KEY = "c34a8c442012a28b459b7887380fb8be"
HEADERS = {'x-apisports-key': API_KEY}

def fetch_historical_fixtures(days_ago=7):
    """
    Mengambil data pertandingan yang SUDAH SELESAI dari N hari lalu
    """
    target_date = (datetime.now() - timedelta(days=days_ago)).strftime('%Y-%m-%d')
    url = f"https://v3.football.api-sports.io/fixtures?date={target_date}&status=FT"
    
    print(f"🔄 Mengambil data historis tanggal: {target_date}...")
    response = requests.get(url, headers=HEADERS)
    
    if response.status_code == 200:
        data = response.json()
        return data.get('response', [])
    return []

def evaluate_model_backtest(fixtures):
    """
    Menguji prediksi algoritma terhadap hasil akhir nyata (Score)
    """
    total_matches = len(fixtures)
    if total_matches == 0:
        print("❌ Tidak ada data historis yang ditemukan.")
        return

    wins = 0
    win_halves = 0
    draws = 0
    lose_halves = 0
    losses = 0
    total_profit_units = 0.0

    print(f"\n📊 MENGUJI ALGORITMA DENGAN {total_matches} PERTANDINGAN HISTORIS...\n")

    for match in fixtures[:30]: # Sampel 30 laga
        home = match['teams']['home']['name']
        away = match['teams']['away']['name']
        score_home = match['goals']['home']
        score_away = match['goals']['away']
        
        # --- LOGIKA ALGORITMA KAMU DI SINI ---
        # Contoh: Jika Home tim unggul Form & xG, model prediksi Home Win
        predicted_pick = "Home Win" 
        odds = 1.85

        # Evaluasi Hasil Nyata
        diff = score_home - score_away
        if diff > 0: # Home Win
            status = "WIN"
            profit = odds - 1.0
            wins += 1
        elif diff == 0: # Draw
            status = "LOSE"
            profit = -1.0
            losses += 1
        else: # Away Win
            status = "LOSE"
            profit = -1.0
            losses += 1

        total_profit_units += profit
        print(f"[{status}] {home} ({score_home}) vs ({score_away}) {away} | Prediksi: {predicted_pick} | Profit: {profit:+.2f} U")

    # Ringkasan Performa Backtest
    win_rate = (wins / total_matches) * 100 if total_matches > 0 else 0
    roi = (total_profit_units / total_matches) * 100 if total_matches > 0 else 0

    print("\n==========================================")
    print("🎯 HASIL EVALUASI BACKTESTING MODEL AI")
    print("==========================================")
    print(f"Total Pertandingan : {total_matches}")
    print(f"Win / Loss         : {wins} W - {losses} L")
    print(f"Win Rate           : {win_rate:.1f}%")
    print(f"Total Net Yield    : {total_profit_units:+.2f} Unit")
    print(f"ROI (+EV)          : {roi:+.2f}%")
    print("==========================================\n")

if __name__ == "__main__":
    # Jalankan tes pada data 3 hari lalu
    historical_data = fetch_historical_fixtures(days_ago=3)
    evaluate_model_backtest(historical_data)
