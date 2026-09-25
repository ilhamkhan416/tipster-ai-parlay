import json
import asyncio
import os
from playwright.async_api import async_playwright

TARGET_URL = "https://mainbolakaki.pro/_view/odds4.aspx"
RAW_DATA_PATH = "data/raw_scraped.json"

async def scrape_parlay_odds():
    print(f"🔄 [SCRAPER] Membuka situs parlay: {TARGET_URL}...")
    
    # Memastikan folder data ada
    os.makedirs("data", exist_ok=True)

    async with async_playwright() as p:
        # Menjalankan Chromium headless dengan User-Agent browser asli
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            viewport={"width": 1280, "height": 800}
        )
        page = await context.new_page()

        try:
            # Buka halaman web parlay
            await page.goto(TARGET_URL, wait_until="networkidle", timeout=60000)
            await page.wait_for_timeout(5000)  # Waktu tunggu ekstra untuk render JavaScript

            scraped_matches = []

            # Mengambil seluruh baris tabel pasaran
            rows = await page.query_selector_all("tr")
            print(f"📊 [SCRAPER] Ditemukan {len(rows)} baris pada elemen tabel.")

            for index, row in enumerate(rows):
                text_content = await row.inner_text()
                if not text_content:
                    continue

                lines = [line.strip() for line in text_content.split("\n") if line.strip()]
                
                # Memfilter baris yang memuat struktur nama tim & odds pasaran
                if len(lines) >= 3:
                    scraped_matches.append({
                        "id": index + 1,
                        "raw_info": lines
                    })

            print(f"✅ [SCRAPER] Berhasil mengekstraksi {len(scraped_matches)} data pasaran mentah.")

            # Simpan data mentah ke file temporary
            with open(RAW_DATA_PATH, "w", encoding="utf-8") as f:
                json.dump(scraped_matches, f, indent=2, ensure_ascii=False)
                
            print(f"💾 [SCRAPER] Data tersimpan sementara di '{RAW_DATA_PATH}'.")

        except Exception as e:
            print(f"❌ [SCRAPER ERROR] Gagal melakukan scraping: {e}")
            # Jika scraping error, buat file kosong agar pipeline tidak crash total
            with open(RAW_DATA_PATH, "w", encoding="utf-8") as f:
                json.dump([], f)
        finally:
            await browser.close()

if __name__ == "__main__":
    asyncio.run(scrape_parlay_odds())
