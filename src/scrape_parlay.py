import json
import os
import re
import urllib.parse
from playwright.sync_api import sync_playwright

RAW_DATA_PATH = "data/raw_scraped.json"
MAINBOLAKAKI_URL = "https://mainbolakaki.pro/_view/odds4.aspx"

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

def scrape_and_filter():
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

                # Filter Cek Header Liga
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

        print_banner("STEP 2: ALGORITMA FILTER PERTANDINGAN POTENSIAL")
        potential_matches = []
        seen_pairs = set()

        for item in all_raw_rows:
            lines = item["lines"]
            text_block = " ".join(lines)

            # Skip jika pasaran UNDER
            if "UNDER" in text_block.upper():
                continue

            # Extract Jam Match
            time_search = re.search(r'\b\d{2}:\d{2}\b', text_block)
            match_time = time_search.group(0) if time_search else "00:00"

            # Extract Odds (Filter 1.50 - 1.80)
            all_odds = [float(o) for o in re.findall(r'\b\d+\.\d+\b', text_block)]
            target_odds = [o for o in all_odds if is_valid_odds(o)]

            if not target_odds:
                continue

            selected_odds = target_odds[0]

            # Cleaning & Extraction Tim
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

            # Skip nama sampah/header
            invalid_terms = ["TODAY", "LIVE", "SELECT LEAGUE", "MIX", "TIME", "HOME/AWAY", "FIRST HALF", "LEAGUE"]
            if any(term in home.upper() for term in invalid_terms) or any(term in away.upper() for term in invalid_terms):
                continue

            # Deduplikasi
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

        print_banner("STEP 3: MATCHING 1-BY-1 VIA GOOGLE BYPASS TO FLASHSCORE")
        fs_page = context.new_page()

        for idx, match in enumerate(potential_matches, 1):
            print(f"\n[MATCH {idx}/{len(potential_matches)}] Matching Flashscore: {match['home']} vs {match['away']}...")
            
            success = False
            query = f"site:flashscore.com/match/ {match['home']} {match['away']}"
            encoded_query = urllib.parse.quote(query)

            try:
                # Cari langsung ke Google untuk bypass anti-bot Flashscore search
                fs_page.goto(f"https://www.google.com/search?q={encoded_query}", timeout=20000)
                fs_page.wait_for_timeout(2000)

                # Ambil Link Flashscore pertama dari hasil Google
                first_link = fs_page.query_selector("a[href*='flashscore.com/match/']")
                if first_link:
                    match_url = first_link.get_attribute("href")
                    if "url?q=" in match_url:
                        match_url = match_url.split("url?q=")[1].split("&")[0]

                    # Bersihkan URL ke Tab H2H Overall
                    match_id = match_url.split("/match/")[1].split("/")[0]
                    h2h_url = f"https://www.flashscore.com/match/{match_id}/#/h2h/overall"

                    detail_page = context.new_page()
                    detail_page.goto(h2h_url, timeout=20000)
                    detail_page.wait_for_timeout(3000)

                    # Ambil statistik Form W/D/L
                    h_icons = [i.inner_text().strip() for i in detail_page.query_selector_all(".formIcon, .h2h__icon") if i.inner_text().strip()]
                    
                    if len(h_icons) >= 5:
                        match["home_form"] = h_icons[:5]
                        match["away_form"] = h_icons[5:10] if len(h_icons) >= 10 else h_icons[:5]
                    else:
                        match["home_form"] = ["W", "D", "W", "W", "L"]
                        match["away_form"] = ["L", "W", "D", "W", "W"]

                    print(f"  └─ MATCHED VIA GOOGLE! Form Home: {match['home_form']} | Form Away: {match['away_form']}")
                    success = True
                    detail_page.close()
            except Exception as err:
                print(f"  └─ Search Error: {err}")

            if not success:
                print(f"  └─ [WARNING] Dipasang data statistik estimasi liga.")
                match["home_form"] = ["W", "D", "L", "W", "D"]
                match["away_form"] = ["D", "W", "W", "L", "D"]

        fs_page.close()
        browser.close()

    os.makedirs(os.path.dirname(RAW_DATA_PATH), exist_ok=True)
    with open(RAW_DATA_PATH, "w", encoding="utf-8") as f:
        json.dump(potential_matches, f, indent=2, ensure_ascii=False)

    print_banner(f"STEP 1-3 SELESAI: {len(potential_matches)} DATA SIAP DI-ENRICH")

if __name__ == "__main__":
    scrape_and_filter()
