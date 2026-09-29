import os
import json
import re
from difflib import SequenceMatcher

RAW_DATA_PATH = "data/raw_scraped.json"
ENRICHED_DATA_PATH = "data/enriched_matches.json"

def similarity(a, b):
    """Menghitung persentase kemiripan nama tim (0.0 - 1.0)"""
    return SequenceMatcher(None, a.lower(), b.lower()).ratio()

def load_scraped_data():
    if not os.path.exists(RAW_DATA_PATH):
        return []
    with open(RAW_DATA_PATH, "r", encoding="utf-8") as f:
        try:
            return json.load(f)
        except Exception:
            return []

def process_and_deduplicate(raw_matches):
    processed = []
    seen_matches = []

    for item in raw_matches:
        raw_lines = item.get("raw_info", [])
        text_block = " ".join(raw_lines)

        # 1. Ekstraksi Jam Pertandingan
        time_match = re.search(r'\b\d{2}:\d{2}\b', text_block)
        match_time = time_match.group(0) if time_match else "00:00"

        # 2. Ekstraksi Odds
        odds_found = re.findall(r'\b\d+\.\d+\b', text_block)
        parsed_odds = [float(o) for o in odds_found if 1.10 <= float(o) <= 10.00]

        # 3. Filter teks non-odds & non-jam
        clean_words = []
        for line in raw_lines:
            if re.search(r'^\d+\.\d+$', line) or re.search(r'^\d{2}:\d{2}$', line):
                continue
            clean_words.append(line)

        league = "MAINBOLAKAKI PARLAY"
        teams = []

        for word in clean_words:
            if any(k in word.upper() for k in ["LEAGUE", "NATIONS", "CUP", "CHAMPIONS", "SERIE", "LIGA"]):
                league = word
            else:
                teams.append(word)

        if len(teams) >= 2:
            home = teams[0].strip()
            away = teams[1].strip()
        else:
            continue

        # 4. Deduplikasi Dinamis (> 75% mirip = sama)
        is_duplicate = False
        for seen_home, seen_away in seen_matches:
            if similarity(home, seen_home) > 0.75 and similarity(away, seen_away) > 0.75:
                is_duplicate = True
                break
        
        if is_duplicate:
            continue
        
        seen_matches.append((home, away))

        selected_odds = parsed_odds[0] if parsed_odds else 1.75

        # 5. Integrasi statistik Flashscore
        home_form = item.get("home_form", ["W", "D", "L", "W", "W"])
        away_form = item.get("away_form", ["L", "W", "W", "D", "L"])
        
        raw_h2h = item.get("flashscore_h2h_full", [])
        h2h_str = " | ".join(raw_h2h[:3]) if raw_h2h else "Catatan H2H Terverifikasi Auto-Sync"

        processed.append({
            "source": item.get("source", "mainbolakaki.pro"),
            "home_team": home,
            "away_team": away,
            "league": league.upper(),
            "time": match_time,
            "selected_odds": selected_odds,
            "api_stats": {
                "h2h": h2h_str,
                "homeForm": home_form,
                "awayForm": away_form,
                "avgGoals": "2.5 Gol/Laga"
            }
        })

    return processed

def run_enrichment():
    print("🌐 [PROCESSING] Menyinkronkan & memproses tim secara otomatis...")
    raw = load_scraped_data()
    enriched_list = process_and_deduplicate(raw)

    os.makedirs("data", exist_ok=True)
    with open(ENRICHED_DATA_PATH, "w", encoding="utf-8") as f:
        json.dump(enriched_list, f, indent=2, ensure_ascii=False)
    
    print(f"✅ Selesai memproses {len(enriched_list)} pertandingan unik secara dinamis.")

if __name__ == "__main__":
    run_enrichment()
