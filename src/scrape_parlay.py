import json
import os
import time
from playwright.sync_api import sync_playwright

RAW_DATA_PATH = "data/raw_scraped.json"
MAINBOLAKAKI_URL = "https://mainbolakaki.pro/_view/odds4.aspx"

IGNORE_KEYWORDS = [
    "SOCCER", "MIX PARLAY", "SELECT LEAGUE", "FULL TIME", 
    "FIRST HALF", "TODAY", "TIME", "HOME/AWAY", "HANDICAP", 
    "OVER/UNDER", "1X2", "ODDS", "LIVE", "UPDATE"
]

def is_clean_text(text):
    text_upper = text.upper()
    for kw in IGNORE_KEYWORDS:
        if kw in text_upper:
            return False
    return True

def scrape_mainbolakaki_and_flashscore():
    print("🌐 [SCRAPER] Membuka mainbolakaki.pro & Flashscore...")
    raw_matches = []

    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            context = browser.new_context(
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
            )
            page = context.new_page()

            # 1. Scraping data mainbolakaki.pro
            try:
                page.goto(MAINBOLAKAKI_URL, timeout=45000)
                page.wait_for_timeout(4000)
                rows = page.query_selector_all("tr")

                for row in rows:
                    text_content = row.inner_text()
                    lines = [line.strip() for line in text_content.split("\n") if line.strip() and is_clean_text(line)]

                    if len(lines) >= 3:
                        raw_matches.append({
                            "source": "mainbolakaki.pro",
                            "raw_info": lines,
                            "scraped_at": time.strftime("%Y-%m-%d %H:%M:%S")
                        })
            except Exception as e:
                print(f"⚠️ Gagal akses mainbolakaki.pro: {e}")

            # 2. Deep Scrape Flashscore untuk Form & H2H
            fs_page = context.new_page()
            try:
                fs_page.goto("https://www.flashscore.co.id/", timeout=35000)
                fs_page.wait_for_timeout(3000)
                
                match_elements = fs_page.query_selector_all(".event__match")

                for item in raw_matches[:15]:
                    raw_lines = item.get("raw_info", [])
                    home_candidate = raw_lines[1] if len(raw_lines) > 1 else ""

                    matched_id = None
                    if home_candidate:
                        for elem in match_elements:
                            if home_candidate.lower() in elem.inner_text().lower():
                                match_id_attr = elem.get_attribute("id")
                                matched_id = match_id_attr.split("_")[-1] if match_id_attr else None
                                break

                    if matched_id:
                        detail_page = context.new_page()
                        try:
                            detail_page.goto(f"https://www.flashscore.co.id/pertandingan/{matched_id}/#/h2h/overall", timeout=15000)
                            detail_page.wait_for_timeout(2500)

                            # H2H Rows
                            h2h_rows = detail_page.query_selector_all(".h2h__row")
                            h2h_list = [r.inner_text().replace("\n", " ") for r in h2h_rows[:5]]
                            item["flashscore_h2h_full"] = h2h_list

                            # Form W/D/L
                            form_sections = detail_page.query_selector_all(".h2h__section")
                            if len(form_sections) >= 2:
                                home_icons = form_sections[0].query_selector_all(".formIcon")
                                away_icons = form_sections[1].query_selector_all(".formIcon")

                                item["home_form"] = [icon.inner_text().strip() for icon in home_icons[:5] if icon.inner_text().strip()]
                                item["away_form"] = [icon.inner_text().strip() for icon in away_icons[:5] if icon.inner_text().strip()]

                        except Exception as err:
                            print(f"⚠️ Skip detail match ID {matched_id}: {err}")
                        finally:
                            detail_page.close()

            except Exception as e:
                print(f"⚠️ Flashscore Scrape Error: {e}")
            finally:
                fs_page.close()

            browser.close()
    except Exception as e:
        print(f"⚠️ Error Scraper Engine: {e}")

    os.makedirs(os.path.dirname(RAW_DATA_PATH), exist_ok=True)
    with open(RAW_DATA_PATH, "w", encoding="utf-8") as f:
        json.dump(raw_matches, f, indent=2, ensure_ascii=False)

    print(f"💾 [SCRAPER] Simpan {len(raw_matches)} baris data mentah.")

if __name__ == "__main__":
    scrape_mainbolakaki_and_flashscore()
