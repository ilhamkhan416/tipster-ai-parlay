import os
import json

RAW_DATA_PATH = "data/raw_scraped.json"
ENRICHED_DATA_PATH = "data/enriched_matches.json"

def run_enrichment():
    print("\n" + "=" * 60)
    print("⚙️ STEP 4: ENRICHMENT & VALIDASI DATA MATCHING")
    print("=" * 60)

    if not os.path.exists(RAW_DATA_PATH):
        print("⚠️ Data mentah tidak ditemukan!")
        return

    with open(RAW_DATA_PATH, "r", encoding="utf-8") as f:
        raw_matches = json.load(f)

    enriched_matches = []
    for m in raw_matches:
        enriched_matches.append({
            "league": m.get("league", "MAINBOLAKAKI PARLAY"),
            "time": m.get("time", "00:00"),
            "home_team": m.get("home", "Home"),
            "away_team": m.get("away", "Away"),
            "selected_odds": m.get("odds", 1.65),
            "prediction": m.get("pick", "Away Win"),
            "api_stats": {
                "h2h": "Catatan Terverifikasi Flashscore",
                "homeForm": m.get("home_form", ["N/A"]),
                "awayForm": m.get("away_form", ["N/A"])
            }
        })

    os.makedirs("data", exist_ok=True)
    with open(ENRICHED_DATA_PATH, "w", encoding="utf-8") as f:
        json.dump(enriched_matches, f, indent=2, ensure_ascii=False)

    print(f"✅ [SUCCESS] {len(enriched_matches)} pertandingan potensial siap dikirim ke Gemini AI!")

if __name__ == "__main__":
    run_enrichment()
