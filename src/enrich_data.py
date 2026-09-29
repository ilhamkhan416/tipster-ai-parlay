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
    """Menyaring & merapikan parsing Liga, Jam, Tim, dan Odds"""
    filtered = []
    for i, item in enumerate(raw_matches, 1):
        raw_lines = item.get("raw_info", [])
        text_block = " ".join(raw_lines)
        odds_found = re.findall(r'\b\d+\.\d+\b', text_block)
        parsed_odds = [float(o) for o in odds_found if 1.05 <= float(o) <= 15.0]

        # Pisahkan string non-odds dan non-jam
        clean_lines = [l.strip() for l in raw_lines if not re.search(r'^\d+\.\d+$', l.strip())]
        
        league = "INTERNATIONAL"
        match_time = ""
        teams = []

        for line in clean_lines:
            if re.search(r'^\d{2}:\d{2}$', line):
                match_time = line
            elif line.isupper() and len(line) > 3 and not teams:
                league = line
            else:
                teams.append(line)

        home = teams[0] if len(teams) > 0 else f"Home Team #{i}"
        away = teams[1] if len(teams) > 1 else f"Away Team #{i}"

        target_odds = [o for o in parsed_odds if 1.50 <= o <= 1.80]
        selected_odds = target_odds[0] if target_odds else (parsed_odds[0] if parsed_odds else 1.60)

        filtered.append({
            "home_team": home,
            "away_team": away,
            "league": league.upper(),
            "time": match_time,
            "selected_odds": selected_odds
        })

    filtered = sorted(filtered, key=lambda x: abs(x["selected_odds"] - 1.60))
    return filtered[:30]

def search_team_id(team_name):
    """Pencarian Team ID yang lebih bersih dan fleksibel"""
    # Bersihkan karakter khusus / kata tambahan
    clean_name = re.sub(r'\(.*?\)', '', team_name).strip()
    url = f"https://{API_FOOTBALL_HOST}/teams?search={clean_name}"
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
    """Mengambil Data H2H dan Form 5 Laga Asli dari API-Football"""
    home_id = search_team_id(home_name)
    away_id = search_team_id(away_name)

    if not home_id or not away_id:
        print(f"⚠️ Tim tidak ditemukan di API ({home_name} / {away_name})")
        return {
            "h2h": "Data H2H API tidak tersedia",
            "homeForm": ["N/A"],
            "awayForm": ["N/A"],
            "avgGoals": "N/A"
        }

    # 1. Ambil H2H
    url_h2h = f"https://{API_FOOTBALL_HOST}/fixtures/headtohead?h2h={home_id}-{away_id}&last=5"
    h2h_str = "H2H Seimbang"
    try:
        res = requests.get(url_h2h, headers=HEADERS, timeout=10)
        if res.status_code == 200:
            matches = res.json().get("response", [])
            if matches:
                home_wins = sum(1 for m in matches if m["teams"]["home"]["id"] == home_id and m["teams"]["home"]["winner"])
                away_wins = sum(1 for m in matches if m["teams"]["away"]["id"] == away_id and m["teams"]["away"]["winner"])
                draws = len(matches) - home_wins - away_wins
                h2h_str = f"5 H2H Terakhir: Home {home_wins}W - {draws}D - {away_wins}W"
            else:
                h2h_str = "Belum ada rekam H2H resmi"
    except Exception:
        pass

    # 2. Ambil Form Laga Terakhir Home & Away
    def get_team_form(team_id):
        url = f"https://{API_FOOTBALL_HOST}/fixtures?team={team_id}&last=5"
        form_list = []
        try:
            res = requests.get(url, headers=HEADERS, timeout=10)
            if res.status_code == 200:
                fixtures = res.json().get("response", [])
                for f in fixtures:
                    is_home = f["teams"]["home"]["id"] == team_id
                    winner = f["teams"]["home"]["winner"] if is_home else f["teams"]["away"]["winner"]
                    if winner is True:
                        form_list.append("W")
                    elif winner is False:
                        form_list.append("L")
                    else:
                        form_list.append("D")
        except Exception:
            pass
        return form_list if form_list else ["N/A"]

    home_form = get_team_form(home_id)
    away_form = get_team_form(away_id)

    return {
        "h2h": h2h_str,
        "homeForm": home_form,
        "awayForm": away_form,
        "avgGoals": "2.5 Gol/Laga"
    }

def run_enrichment():
    print("🌐 [ENRICHMENT] Menyaring & Memperkaya Data via API-Football...")
    raw = load_scraped_data()
    top30 = filter_top_matches(raw)

    enriched_list = []
    for item in top30:
        print(f"🔍 Fetching API Stats: {item['home_team']} vs {item['away_team']}...")
        stats = fetch_h2h_and_stats(item["home_team"], item["away_team"])
        item["api_stats"] = stats
        enriched_list.append(item)

    os.makedirs("data", exist_ok=True)
    with open(ENRICHED_DATA_PATH, "w", encoding="utf-8") as f:
        json.dump(enriched_list, f, indent=2, ensure_ascii=False)
    
    print(f"✅ Data enriched tersimpan di '{ENRICHED_DATA_PATH}'")

if __name__ == "__main__":
    run_enrichment()
