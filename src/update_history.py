import json
import os
import re
from datetime import datetime
from playwright.sync_api import sync_playwright

TODAY_DATA_PATH = "data/today.json"
HISTORY_DATA_PATH = "data/history.json"


def load_json(filepath):
    if os.path.exists(filepath):
        with open(filepath, "r", encoding="utf-8") as f:
            try:
                return json.load(f)
            except Exception:
                return [] if "history" in filepath else {}
    return [] if "history" in filepath else {}


def save_json(filepath, data):
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def calculate_status(pick, home_score, away_score):
    """
    Hitung W / L / WH / LH / D secara matematis dari skor akhir
    """
    if home_score is None or away_score is None:
        return "PENDING"

    score_diff = home_score - away_score
    total_goals = home_score + away_score
    pick_lower = pick.lower()

    # 1. Pasaran 1X2
    if "home win" in pick_lower:
        return "W" if score_diff > 0 else "L"
    elif "away win" in pick_lower:
        return "W" if score_diff < 0 else "L"

    # 2. Pasaran Handicap (HDP)
    hdp_match = re.search(r'([-+]?\d+\.?\d*)', pick)
    if "hdp" in pick_lower and hdp_match:
        hdp_val = float(hdp_match.group(1))
        effective_diff = score_diff + hdp_val
        
        if effective_diff > 0.25:
            return "W"
        elif effective_diff == 0.25:
            return "WH"
        elif effective_diff == -0.25:
            return "LH"
        elif effective_diff == 0:
            return "D"
        else:
            return "L"

    # 3. Pasaran Over / Under
    ou_match = re.search(r'(\d+\.?\d*)', pick)
    if "over" in pick_lower and ou_match:
        target = float(ou_match.group(1))
        if total_goals > target + 0.25:
            return "W"
        elif total_goals == target + 0.25:
            return "WH"
        elif total_goals == target - 0.25:
            return "LH"
        else:
            return "L"

    return "W"  # Default fallback jika pasaran umum


def scrape_yesterday_results(match_list):
    """
    Scrape skor akhir kemarin dari portal hasil gratisan menggunakan Playwright
    """
    results_map = {}
    print("🔍 [RESULT SCRAPER] Membuka halaman hasil pertandingan kemarin...")

    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()
            
            # Akses halaman hasil publik gratisan
            page.goto("https://www.flashscore.co.id/hasil/", timeout=30000)
            page.wait_for_timeout(3000)

            page_content = page.content().lower()

            for item in match_list:
                match_name = item.get("match", "")
                parts = match_name.split(" vs ")
                if len(parts) < 2:
                    continue

                home_team = parts[0].strip().lower()
                away_team = parts[1].strip().lower()

                # Regex pattern untuk mengekstrak skor akhir "Home X - Y Away"
                pattern = re.compile(
                    re.escape(home_team[:5]) + r'.*?(\d+)\s*[-:]\s*(\d+).*?' + re.escape(away_team[:5]), 
                    re.DOTALL
                )
                match_found = pattern.search(page_content)

                if match_found:
                    h_score = int(match_found.group(1))
                    a_score = int(match_found.group(2))
                    results_map[match_name] = (h_score, a_score)
                    print(f"⚽ Found Result: {match_name} -> {h_score}-{a_score}")
                else:
                    results_map[match_name] = (None, None)

            browser.close()
    except Exception as e:
        print(f"⚠️ Gagal scrape halaman hasil: {e}")

    return results_map


def archive_today_to_history():
    print("📜 [HISTORY] Memulai proses pengarsipan rekomendasi kemarin...")
    
    today_data = load_json(TODAY_DATA_PATH)
    if not today_data or "parlay10" not in today_data:
        print("⚠️ Tidak ada data rekomendasi kemarin di 'today.json'.")
        return

    history_list = load_json(HISTORY_DATA_PATH)
    if not isinstance(history_list, list):
        history_list = []

    yesterday_matches = today_data.get("parlay10", [])
    yesterday_date = today_data.get("updatedAt", datetime.now().strftime("%d/%m/%Y"))

    # Scrape skor pertandingan kemarin
    scores_map = scrape_yesterday_results(yesterday_matches)

    archived_item = {
        "date": yesterday_date,
        "matches": []
    }

    for item in yesterday_matches:
        match_name = item.get("match")
        pick = item.get("pick")
        
        h_score, a_score = scores_map.get(match_name, (None, None))
        status_result = calculate_status(pick, h_score, a_score)

        archived_item["matches"].append({
            "match": match_name,
            "league": item.get("league"),
            "pick": pick,
            "odds": item.get("odds"),
            "score": f"{h_score}-{a_score}" if h_score is not None else "N/A",
            "status": status_result, # STATUS: W, L, WH, LH, D, PENDING
            "expertReason": item.get("expertReason") or item.get("aiReason")
        })

    # Simpan ke history.json
    history_list = [h for h in history_list if h.get("date") != yesterday_date]
    history_list.insert(0, archived_item)

    save_json(HISTORY_DATA_PATH, history_list)
    print(f"✅ [HISTORY] Rekomendasi tanggal {yesterday_date} berhasil disimpan di 'data/history.json'!")


if __name__ == "__main__":
    archive_today_to_history()
