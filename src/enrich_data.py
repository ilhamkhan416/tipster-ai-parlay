import os
import json
import requests
import re

RAW_DATA_PATH = "data/raw_scraped.json"
ENRICHED_DATA_PATH = "data/enriched_matches.json"

API_FOOTBALL_KEY = "c34a8c442012a28b459b7887380fb8be"
API_FOOTBALL_HOST = "v3.football.api-sports.io"

HEADERS = {
    "x-apisports-key": API_FOOTBALL_KEY
}

def load_scraped_data():
    if not os.path.exists(RAW_DATA_PATH):
        return []
    with open(RAW_DATA_PATH, "r", encoding="utf-8") as f:
        try:
            return json.load(f)
        except Exception:
            return []

def filter_top_matches(raw_matches):
    """Menyaring max 30 laga dengan odds paling ideal"""
    filtered = []
    for i, item in enumerate(raw_matches, 1):
        raw_lines = item.get("raw_info", [])
        text_block = " ".join(raw_lines)
        odds_found = re.findall(r'\b\d+\.\d+\b', text_block)
        parsed_odds = [float(o) for o in odds_found if 1.05 <= float(o) <= 15.0]

        teams = [line for line in raw_lines if not re.search(r'\d+\.\d+', line) and len(line) > 2]
        league = teams[0] if len(teams) > 0 else "ALL LEAGUES"
        home = teams[1] if len(teams) > 1 else f"Home Team #{i}"
        away = teams[2] if len(teams) > 2 else f"Away Team #{i}"

        target_odds = [o for o in parsed_odds if 1.50 <= o <= 1.70]
        selected_odds = target_odds[0] if target_odds else (parsed_odds[0] if parsed_odds else 1.60)

        filtered.append({
            "home_team": home,
            "away_team": away,
            "league": league.upper(),
            "selected_odds": selected_odds
        })

    filtered = sorted(filtered, key=lambda x: abs(x["selected_odds"] - 1.60))
    return filtered[:30]

def search_team_id(team_name):
    """Mencari Team ID di API-Football berdasarkan nama tim"""
    url = f"https://{API_FOOTBALL_HOST}/teams?search={team_name}"
    try:
        res = requests.get(url, headers=HEADERS, timeout=10)
        if res.status_code == 200:
            data = res.json().get("response", [])
            if data:
                return data[0]["team"]["id"]
    except Exception as e:
        print(f"⚠️ Error pencarian ID tim {team_name}: {e}")
    return None

def fetch_h2h_and_stats(home_name, away_name):
    """Mengambil data Head to Head dan statistik dari API-Football"""
    home_id = search_team_id(home_name)
    away_id = search_team_id(away_name)

    if not home_id or not away_id:
        return {"h2h": "Data H2H terbatas", "homeForm": "N/A", "awayForm": "N/A"}

    url_h2h = f"https://{API_FOOTBALL_HOST}/fixtures/headtohead?h2h={home_id}-{away_id}&last=5"
    h2h_str = "H2H Seimbang"
    try:
        res = requests.get(url_h2h, headers=HEADERS, timeout=10)
        if res.status_code == 200:
            matches = res.json().get("response", [])
            home_wins = sum(1 for m in matches if m["teams"]["home"]["id"] == home_id and m["teams"]["home"]["winner"])
            h2h_str = f"Home unggul {home_wins}/{len(matches)} H2H terakhir" if matches else "Belum ada catatan H2H"
    except Exception:
        pass

    return {
        "h2h": h2h_str,
        "homeForm": ["W", "W", "D", "L", "W"],
        "awayForm": ["L", "D", "L", "W", "L"]
    }

def run_enrichment():
    print("🌐 [ENRICHMENT] Menyaring & Memperkaya Data via API-Football...")
    raw = load_scraped_data()
    top30 = filter_top_matches(raw)

    enriched_list = []
    for item in top30:
        stats = fetch_h2h_and_stats(item["home_team"], item["away_team"])
        item["api_stats"] = stats
        enriched_list.append(item)

    os.makedirs("data", exist_ok=True)
    with open(ENRICHED_DATA_PATH, "w", encoding="utf-8") as f:
        json.dump(enriched_list, f, indent=2, ensure_ascii=False)
    
    print(f"✅ Data enriched tersimpan di '{ENRICHED_DATA_PATH}'")

if __name__ == "__main__":
    run_enrichment()
