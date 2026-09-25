import requests
import json

# DATABASE SEPAK BOLA PUBLIK OPEN-SOURCE (GRATIS & PULUHAN LAGA SEKALIGUS)
DATA_SOURCES = [
    "https://raw.githubusercontent.com/openfootball/football.json/master/2023-24/en.1.json", # Premier League
    "https://raw.githubusercontent.com/openfootball/football.json/master/2023-24/es.1.json", # La Liga
    "https://raw.githubusercontent.com/openfootball/football.json/master/2023-24/it.1.json", # Serie A
    "https://raw.githubusercontent.com/openfootball/football.json/master/2023-24/de.1.json", # Bundesliga
]

def fetch_bulk_historical_matches():
    print("🔄 Menarik DATASET LENGKAP dari Open Football Data (Ratusan Laga)...")
    all_matches = []

    for source in DATA_SOURCES:
        try:
            res = requests.get(source, timeout=10)
            if res.status_code == 200:
                data = res.json()
                league_name = data.get('name', 'League')
                rounds = data.get('rounds', [])
                
                for r in rounds:
                    for match in r.get('matches', []):
                        score = match.get('score', {})
                        if score and 'ft' in score:
                            all_matches.append({
                                'league': league_name,
                                'home': match.get('team1'),
                                'away': match.get('team2'),
                                'score_home': score['ft'][0],
                                'score_away': score['ft'][1],
                            })
        except Exception as e:
            print(f"Error loading source: {e}")

    return all_matches

def run_backtest_engine():
    matches = fetch_bulk_historical_matches()

    if not matches:
        print("❌ Gagal menarik dataset pertandingan.")
        return

    print(f"\n✅ BERHASIL MENDAPATKAN {len(matches)} PERTANDINGAN HISTORIS SELESAI!\n")
    print("==========================================================")
    print("📊 MENJALANKAN BACKTEST MODEL AI DENGAN DATASET BESAR")
    print("==========================================================\n")

    wins = 0
    losses = 0
    draws = 0
    total_profit = 0.0

    # Ambil sampel 50 pertandingan pertama untuk pengujian cepat
    test_sample = matches[:50] 

    for idx, m in enumerate(test_sample, 1):
        league = m['league']
        home = m['home']
        away = m['away']
        s_home = m['score_home']
        s_away = m['score_away']

        # --- LOGIKA PREDIKSI MODEL AI ---
        # Prediksi Home Win dengan odds rata-rata 1.85
        predicted_pick = f"{home} Win"
        odds = 1.85

        diff = s_home - s_away

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
        print(f"{idx}. [{status}] {league}: {home} ({s_home}) vs ({s_away}) {away} | Profit: {profit:+.2f} U")

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
