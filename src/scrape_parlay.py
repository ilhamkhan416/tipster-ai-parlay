import json
import os
import time
from playwright.sync_api import sync_playwright

RAW_DATA_PATH = "data/raw_scraped.json"


def scrape_parlay_matches():
    print("🌐 [SCRAPER] Membuka browser Playwright untuk scraping data pasaran...")
    matches_data = []

    try:
        with sync_playwright() as p:
            # Jalankan headless Chromium
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()

            # Mengakses portal pasaran taruhan publik
            # Silakan ganti URL sesuai dengan target portal pasaran pilihan Anda
            target_url = "https://www.flashscore.co.id/"
            page.goto(target_url, timeout=45000)
            page.wait_for_timeout(5000)

            # Scroll otomatis untuk memicu lazy-loading data pertandingan
            page.evaluate("window.scrollTo(0, document.body.scrollHeight/2);")
            time.sleep(2)

            # Ekstrak elemen-elemen pertandingan dari DOM
            # Mengambil blok-blok teks yang berisi info Tim, Liga, dan Odds 1X2
            match_elements = page.query_selector_all(".event__match")

            print(f"📊 [SCRAPER] Berhasil mengidentifikasi {len(match_elements)} elemen pertandingan.")

            for elem in match_elements:
                try:
                    text_content = elem.inner_text()
                    lines = [line.strip() for line in text_content.split("\n") if line.strip()]
                    
                    if len(lines) >= 3:
                        matches_data.append({
                            "raw_info": lines,
                            "scraped_at": time.strftime("%Y-%m-%d %H:%M:%S")
                        })
                except Exception as ex:
                    continue

            browser.close()
            print(f"✅ [SCRAPER] Ekstraksi selesai. Mendapatkan {len(matches_data)} data mentah.")

    except Exception as e:
        print(f"⚠️ Error saat scraping: {e}")

    # Fallback dummy data jika scraping gagal atau tidak ada pertandingan terdeteksi
    if not matches_data:
        print("⚠️ Scraping tidak menghasilkan data. Menggunakan data simulasi cadangan...")
        matches_data = [
            {
                "raw_info": ["BOLIVIA PRIMERA", "Nacional Potosi", "Club Always Ready", "1.55", "3.80", "5.50"],
                "scraped_at": time.strftime("%Y-%m-%d %H:%M:%S")
            },
            {
                "raw_info": ["ENGLISH PREMIER LEAGUE", "Arsenal", "Everton", "1.40", "4.50", "7.00"],
                "scraped_at": time.strftime("%Y-%m-%d %H:%M:%S")
            },
            {
                "raw_info": ["LA LIGA", "Real Madrid", "Getafe", "1.35", "5.00", "8.50"],
                "scraped_at": time.strftime("%Y-%m-%d %H:%M:%S")
            }
        ]

    # Simpan hasil scraping ke data/raw_scraped.json
    os.makedirs(os.path.dirname(RAW_DATA_PATH), exist_ok=True)
    with open(RAW_DATA_PATH, "w", encoding="utf-8") as f:
        json.dump(matches_data, f, indent=2, ensure_ascii=False)

    print(f"💾 [SCRAPER] Data mentah berhasil disimpan di '{RAW_DATA_PATH}'.")


if __name__ == "__main__":
    scrape_parlay_matches()
