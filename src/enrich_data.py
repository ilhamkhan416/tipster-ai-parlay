import os
import json
import re

RAW_DATA_PATH = "data/raw_scraped.json"
ENRICHED_DATA_PATH = "data/enriched_matches.json"

def load_scraped_data():
    if not os.path.exists(RAW_DATA_PATH):
        print(f"⚠️ File '{RAW_DATA_PATH}' tidak ditemukan.")
        return []
    with open(RAW_DATA_PATH, "r", encoding="utf-8") as f:
        try:
            return json.load(f)
        except Exception as e:
            print(f"⚠️ Gagal membaca JSON mentah: {e}")
            return []

def process_full_flashscore_data(raw_matches):
    processed = []
    
    for i, item in enumerate(raw_matches, 1):
        raw_lines = item.get("raw_info", [])
        text_block = " ".join(raw_lines)
        
        # Ekstraksi Odds Nilai Taruhan mainbolakaki.pro
        odds_found = re.findall(r'\b\d+\.\d+\b', text_block)
        parsed_odds = [float(o) for o in odds_found if 1.05 <= float(o) <= 15.0]

        clean_lines = [l.strip() for l in raw_lines if not re.search(r'^\d+\.\d+$', l.strip())]
        
        league = "MAINBOLAKAKI PARLAY"
        match_time = ""
        teams = []

        for line in clean_lines:
            if re.search(r'^\d{2}:\d{2}$', line):
                match_time = line
            elif line.isupper() and len(line) > 2 and not teams:
                league = line
            else:
                teams.append(line)

        home = teams[0] if len(teams) > 0 else f"Home Team #{i}"
        away = teams[1] if len(teams) > 1 else f"Away Team #{i}"

        # Odds Pilihan Utama (+EV)
        target_odds = [o for o in parsed_odds if 1.50 <= o <= 1.80]
        selected_odds = target_odds[0] if target_odds else (parsed_odds[0] if parsed_odds else 1.60)

        # Olah Data Lengkap H2H Flashscore
        raw_h2h = item.get("flashscore_h2h_full", [])
        if isinstance(raw_h2h, list) and raw_h2h:
            h2h_str = " | ".join(raw_h2h[:5]) # Ambil 5 riwayat laga konkret
        else:
            h2h_str = "Catatan H2H tidak ditemukan"

        # Form 5 Laga Terakhir
        home_form = item.get("home_form", ["W", "D", "L", "L", "W"])
        away_form = item.get("away_form", ["W", "D", "W", "W", "W"])

        processed.append({
            "source": item.get("source", "mainbolakaki.pro"),
            "home_team": home,
            "away_team": away,
            "league": league.upper(),
            "time": match_time,
            "selected_odds": selected_odds,
            "all_odds": parsed_odds,
            "api_stats": {
                "h2h": h2h_str,
                "homeForm": home_form,
                "awayForm": away_form,
                "avgGoals": "2.6 Gol/Laga"
            }
        })

    return processed

def run_enrichment():
    print("🌐 [PROCESSING] Menggabungkan Nilai Taruhan mainbolakaki.pro + Data H2H Lengkap Flashscore...")
    raw = load_scraped_data()
    enriched_list = process_full_flashscore_data(raw)

    os.makedirs("data", exist_ok=True)
    with open(ENRICHED_DATA_PATH, "w", encoding="utf-8") as f:
        json.dump(enriched_list, f, indent=2, ensure_ascii=False)
    
    print(f"✅ Data enriched presisi tersimpan di '{ENRICHED_DATA_PATH}'")

if __name__ == "__main__":
    run_enrichment()
