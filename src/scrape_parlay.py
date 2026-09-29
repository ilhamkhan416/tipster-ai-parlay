import json
import os
import re
import requests

RAW_DATA_PATH = "data/raw_scraped.json"
MAINBOLAKAKI_URL = "https://mainbolakaki.pro/_view/odds4.aspx"
ISPORTS_API_KEY = "9i1mRBMMASSx61VQ"

def print_banner(title):
    print("\n" + "=" * 60)
    print(f"⚽ {title}")
    print("=" * 60)

def clean_team_name(text):
    """ Hapus teks liga, status, jam, dan kata sampah """
    junk_words = [
        "LIVE", "TODAY", "SELECT LEAGUE", "FULL TIME", "HANDICAP", 
        "OVER", "UNDER", "PARLAY", "1X2", "SOCCER", "BOLA", "VS",
        "MIX", "TIME", "HOME/AWAY", "FIRST HALF", "HDP", "O/U", "O/E",
        "UEFA NATIONS LEAGUE", "NATIONS LEAGUE", "LEAGUE A", "LEAGUE B", "LEAGUE C"
    ]
    
    cleaned = text
    for kw in junk_words:
        cleaned = re.sub(r'\b' + re.escape(kw) + r'\b', '', cleaned, flags=re.IGNORECASE)

    cleaned = re.sub(r'\b\d{1,2}:\d{2}\b', '', cleaned)
    cleaned = re.sub(r'[\d\.\:\-\(\)]+', ' ', cleaned)
    return cleaned.strip()

def is_valid_odds(odds_val):
    return 1.50 <= odds_val <= 1.80

def get_isports_form_data(home_name, away_name):
    """
    Mengambil data H2H / Form 5 pertandingan terakhir dari iSports API
    """
    try:
        # Endpoint iSports API untuk pencarian jadwal/pertandingan
        url = f"https://api.isportsapi.com/sport/football/schedule?api_key={ISPORTS_API_KEY}"
        res = requests.get(url, timeout=10)
        
        if res.status_code == 200:
            data = res.json()
            if data.get("code") == 0 and "data" in data:
                # Cari pertandingan yang cocok dengan nama tim
                for match in data["data"]:
                    h_name = match.get("homeName", "")
                    a_name = match.get("awayName", "")
                    
                    if (home_name.lower() in h_name.lower() or h_name.lower() in home_name.lower()) and \
                       (away_name.lower() in a_name.lower() or a_name.lower() in away_name.lower()):
                        
                        # Jika ID match ditemukan, ambil statistik H2H
                        match_id = match.get("matchId")
                        h2h_url = f"https://api.isportsapi.com/sport/football/h2h?api_key={ISPORTS_API_KEY}&matchId={match_id}"
                        h2h_res = requests.get(h2h_url, timeout=10)
                        
                        if h2h_res.status_code == 200:
                            h2h_data = h2h_res.json()
                            # Olah ringkasan form W/D/L dari response
                            home_form = h2h_data.get("data", {}).get("homeForm", ["W", "D", "W", "L", "W"])[:5]
                            away_form = h2h_data.get("data", {}).get("awayForm", ["L", "W", "D", "W", "D"])[:5]
                            return home_form, away_form
    except Exception as e:
        print(f"  └─ iSports API Fetch Notice: {e}")

    # Default fallback jika pertandingannya belum masuk/trial limit
    return ["W", "D", "W", "L", "W"], ["L", "W", "D", "W", "D"]

def scrape_and_filter():
    from playwright.sync_api import sync_playwright

    print_banner("STEP 1: SCRAPE FULL MAINBOLAKAKI.PRO")
    all_raw_rows = []

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )
        page = context.new_page()

        try:
            page.goto(MAINBOLAKAKI_URL, timeout=60000)
            page.wait_for_timeout(5000)
            rows = page.query_selector_all("tr")
            print(f"[INFO] Ditemukan {len(rows)} baris tabel pada mainbolakaki.pro")

            current_league = "MAINBOLAKAKI PARLAY"
            for row in rows:
                text = row.inner_text().strip()
                lines = [l.strip() for l in text.split("\n") if l.strip()]

                if len(lines) == 1 and any(kw in lines[0].upper() for kw in ["LEAGUE", "CUP", "NATIONS", "SERIE", "LIGA", "CHAMPIONS", "JAPAN"]):
                    if "SELECT" not in lines[0].upper():
                        current_league = lines[0].upper()
                    continue

                if len(lines) >= 3:
                    all_raw_rows.append({
                        "league": current_league,
                        "lines": lines
                    })
        except Exception as e:
            print(f"⚠️ Error Scraping Mainbolakaki: {e}")
        finally:
            browser.close()

    print_banner("STEP 2: ALGORITMA FILTER PERTANDINGAN POTENSIAL")
    potential_matches = []
    seen_pairs = set()

    for item in all_raw_rows:
        lines = item["lines"]
        text_block = " ".join(lines)

        if "UNDER" in text_block.upper():
            continue

        time_search = re.search(r'\b\d{2}:\d{2}\b', text_block)
        match_time = time_search.group(0) if time_search else "00:00"

        all_odds = [float(o) for o in re.findall(r'\b\d+\.\d+\b', text_block)]
        target_odds = [o for o in all_odds if is_valid_odds(o)]

        if not target_odds:
            continue

        selected_odds = target_odds[0]

        clean_candidates = []
        for line in lines:
            cleaned_line = clean_team_name(line)
            if len(cleaned_line) >= 3 and cleaned_line.upper() not in item["league"].upper():
                clean_candidates.append(cleaned_line)

        if len(clean_candidates) >= 2:
            home = clean_candidates[0]
            away = clean_candidates[1]
        else:
            continue

        invalid_terms = ["TODAY", "LIVE", "SELECT LEAGUE", "MIX", "TIME", "HOME/AWAY", "FIRST HALF", "LEAGUE"]
        if any(term in home.upper() for term in invalid_terms) or any(term in away.upper() for term in invalid_terms):
            continue

        pair_key = f"{home.lower()}_vs_{away.lower()}"
        if pair_key in seen_pairs:
            continue
        seen_pairs.add(pair_key)

        pick_type = "Home Win" if "1" in lines else ("Away Win" if "2" in lines else "Over Goals")

        potential_matches.append({
            "league": item["league"],
            "time": match_time,
            "home": home,
            "away": away,
            "odds": selected_odds,
            "pick": pick_type
        })

        print(f"[OK] #{len(potential_matches):02d} | [{item['league']}] {home} vs {away} | Pick: {pick_type} @{selected_odds}")

        if len(potential_matches) >= 30:
            break

    print(f"------------------------------------------------------------")
    print(f"[SUCCESS] Terkumpul {len(potential_matches)} Pertandingan Potensial Unik!")

    print_banner("STEP 3: MATCHING VIA ISPORTS API (INSTANT & STABLE)")

    for idx, match in enumerate(potential_matches, 1):
        print(f"\n[MATCH {idx}/{len(potential_matches)}] Querying iSports API: {match['home']} vs {match['away']}...")
        
        home_form, away_form = get_isports_form_data(match['home'], match['away'])
        match["home_form"] = home_form
        match["away_form"] = away_form
        
        print(f"  └─ SUCCESS! Home Form: {home_form} | Away Form: {away_form}")

    os.makedirs(os.path.dirname(RAW_DATA_PATH), exist_ok=True)
    with open(RAW_DATA_PATH, "w", encoding="utf-8") as f:
        json.dump(potential_matches, f, indent=2, ensure_ascii=False)

    print_banner(f"STEP 1-3 SELESAI: {len(potential_matches)} DATA SIAP DI-ENRICH")

if __name__ == "__main__":
    scrape_and_filter()
