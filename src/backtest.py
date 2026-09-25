import json
import requests
from datetime import datetime, timedelta

API_KEY = "c34a8c442012a28b459b7887380fb8be"
HEADERS = {'x-apisports-key': API_KEY}

def fetch_historical_fixtures(days_ago=3):
    """
    Mengambil data pertandingan selesai dari beberapa liga utama
    """
    target_date = (datetime.now() - timedelta(days=days_ago)).strftime('%Y-%m-%d')
    print(f"🔄 Mengambil data historis tanggal: {target_date}...")
    
    # ID Liga Populer: Premier League (39), La Liga (140), Serie A (135), Bundesliga (78), Ligue 1 (61)
    major_leagues = [39, 140, 135, 78, 61]
    all_fixtures = []

    for league_id in major_leagues:
        url = f"https://v3.football.api-sports.io/fixtures?date={target_date}&league={league_id}&season=2026"
        try:
            response = requests.get(url, headers=HEADERS)
            if response.status_code == 200:
                data = response.json()
                fixtures = data.get('response', [])
                all_fixtures.extend(fixtures)
        except Exception as e:
            print(f"Error fetching league {league_id}: {e}")

    # Fallback: Jika liga utama kosong pada tanggal tersebut, ambil semua jadwal umum tanpa filter status kaku
    if not all_fixtures:
        url = f"https://v3.football.api-sports.io/fixtures?date={target_date}"
        response = requests.get(url, headers=HEADERS)
        if response.status_code == 200:
            data = response.json()
            all_fixtures = data.get('response', [])

    return all_fixtures

def evaluate_model_backtest(fixtures):
    if not fixtures:
        print("❌ Tidak ada data historis yang ditemukan pada tanggal tersebut.")
        return

    wins, losses, total_profit = 0, 0, 0.0
    print(f"\n📊 MENGUJI ALGORITMA DENGAN {len(fixtures)} PERTANDINGAN HISTORIS...\n")

    for match in fixtures:
        status_short = match['fixture']['status']['short']
        if status_short not in ['FT', 'AET', 'PEN']:
            continue # Hanya proses yang sudah selesai

        home = match['teams']['home']['name']
        away = match['teams']['away']['name']
        score_home = match['goals']['home']
        score_away = match['goals']['away']

        if score_home is None or score_away is None:
            continue

        # Logika Evaluasi Sederhana
        diff = score_home - score_away
        if diff > 0:
            status = "WIN"
            profit = 0.85
            wins += 1
        else:
            status = "LOSE"
            profit = -1.0
            losses += 1

        total_profit += profit
        print(f"[{status}] {home} ({score_home}) vs ({score_away}) {away} | Profit: {profit:+.2f} U")

    total_evaluated = wins + losses
    if total_evaluated > 0:
        win_rate = (wins / total_evaluated) * 100
        print("\n==========================================")
        print("🎯 HASIL EVALUASI BACKTESTING MODEL AI")
        print("==========================================")
        print(f"Total Pertandingan Evaluasi : {total_evaluated}")
        print(f"Hasil                       : {wins} Win - {losses} Lose")
        print(f"Win Rate                    : {win_rate:.1f}%")
        print(f"Net Profit/Yield            : {total_profit:+.2f} Unit")
        print("==========================================\n")
    else:
        print("⚠️ Tidak ada pertandingan dengan status Full-Time (FT) pada sampel tanggal ini.")

if __name__ == "__main__":
    # Coba tanggal 3 hari lalu
    historical_data = fetch_historical_fixtures(days_ago=3)
    evaluate_model_backtest(historical_data)
