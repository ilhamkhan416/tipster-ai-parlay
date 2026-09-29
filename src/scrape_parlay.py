import json
import os
import re
from playwright.sync_api import sync_playwright

RAW_DATA_PATH = "data/raw_scraped.json"
MAINBOLAKAKI_URL = "https://mainbolakaki.pro/_view/odds4.aspx"

def print_banner(title):
    print("\n" + "=" * 60)
    print(f"⚽ {title}")
    print("=" * 60)

def clean_text_junk(text):
    """ Membersihkan status LIVE, Jam, Header, dan Kata Sampah """
    # Hapus kata status/header umum
    junk_words = [
        "LIVE", "TODAY", "SELECT LEAGUE", "FULL TIME", "HANDICAP", 
        "OVER", "UNDER", "PARLAY", "1X2", "SOCCER", "BOLA", "VS"
    ]
    
    cleaned = text
    for kw in junk_words:
        cleaned = re.sub(r'\b' + re.escape(kw) + r'\b', '', cleaned, flags=re.IGNORECASE)

    # Hapus format jam (contoh: 02:45, 18:00) dan angka murni
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

                # Filter Cek League Header
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

            # 1. Skip jika mengandung kata UNDER
            if "UNDER" in text_block.upper():
                continue

            # 2. Extract Jam Match (HH:MM)
            time_search = re.search(r'\b\d{2}:\d{2}\b', text_block)
            match_time = time_search.group(0) if time_search else "00:00"

            # 3. Extract Odds (Filter 1.50 - 1.80)
            all_odds = [float(o) for o in re.findall(r'\b\d+\.\d+\b', text_block)]
            target_odds = [o for o in all_odds if is_valid_odds(o)]

            if not target_odds:
                continue

            selected_odds = target_odds[0]

            # 4. Extract & Clean Nama Tim Home / Away
            clean_candidates = []
            for line in lines:
                cleaned_line = clean_text_junk(line)
                if len(cleaned_line) >= 3:
                    clean_candidates.append(cleaned_line)

            # Minimal butuh 2 kata valid untuk nama Tim Home & Away
            if len(clean_candidates) >= 2:
                home = clean_candidates[0]
                away = clean_candidates[1]
            else:
                continue

            # Skip header palsu seperti 'TODAY' vs 'SELECT LEAGUE'
            if home.upper() in ["TODAY", "LIVE"] or away.upper() in ["SELECT LEAGUE", "TODAY"]:
                continue

            # Deduplikasi Pertandingan
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

        print_banner("STEP 3: MATCHING 1-BY-1 FLASHSCORE (RETRY LOOP)")
        fs_page = context.new_page()

        for idx, match in enumerate(potential_matches, 1):
            print(f"\n[MATCH {idx}/{len(potential_matches)}] Matching Flashscore: {match['home']} vs {match['away']}...")
            
            success = False
            attempts = 0
            # Pencarian berlapis ke Flashscore: [Home Away], [Home], [Away]
            keywords = [f"{match['home']} {match['away']}", match['home'], match['away']]

            while not success and attempts < len(keywords):
                search_kw = keywords[attempts]
                attempts += 1
                print(f"  └─ Attempt {attempts}: Searching keyword '{search_kw}'...")

                try:
                    fs_page.goto(f"https://www.flashscore.co.id/cari/?q={search_kw}", timeout=15000)
                    fs_page.wait_for_timeout(2000)

                    match_elem = fs_page.query_selector(".searchResult .event__match, .event__match")
                    if match_elem:
                        match_id_attr = match_elem.get_attribute("id")
                        if match_id_attr:
                            match_id = match_id_attr.split("_")[-1]
                            
                            detail_page = context.new_page()
                            detail_page.goto(f"https://www.flashscore.co.id/pertandingan/{match_id}/#/h2h/overall", timeout=15000)
                            detail_page.wait_for_timeout(2000)

                            form_sections = detail_page.query_selector_all(".h2h__section")
                            if len(form_sections) >= 2:
                                h_icons = [i.inner_text().strip() for i in form_sections[0].query_selector_all(".formIcon") if i.inner_text().strip()]
                                a_icons = [i.inner_text().strip() for i in form_sections[1].query_selector_all(".formIcon") if i.inner_text().strip()]

                                match["home_form"] = h_icons[:5]
                                match["away_form"] = a_icons[:5]
                                print(f"  └─ MATCHED! Form Home: {h_icons[:5]} | Form Away: {a_icons[:5]}")
                                success = True

                            detail_page.close()
                except Exception as err:
                    print(f"  └─ Retry Error: {err}")

            if not success:
                print(f"  └─ [WARNING] Flashscore sync failed, dipasang status N/A.")
                match["home_form"] = ["N/A"]
                match["away_form"] = ["N/A"]

        fs_page.close()
        browser.close()

    os.makedirs(os.path.dirname(RAW_DATA_PATH), exist_ok=True)
    with open(RAW_DATA_PATH, "w", encoding="utf-8") as f:
        json.dump(potential_matches, f, indent=2, ensure_ascii=False)

    print_banner(f"STEP 1-3 SELESAI: {len(potential_matches)} DATA SIAP DI-ENRICH")

if __name__ == "__main__":
    scrape_and_filter()
