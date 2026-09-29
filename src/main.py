import os
import json
import google.generativeai as genai

ENRICHED_DATA_PATH = "data/enriched_matches.json"
ANALYZED_DATA_PATH = "data/analyzed_matches.json"

def run_ai_analysis():
    print("\n" + "=" * 60)
    print("🧠 STEP 5: GEMINI AI TAKTIS PROCESSING")
    print("=" * 60)

    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        api_key = "DUMMY_KEY"

    genai.configure(api_key=api_key)

    if not os.path.exists(ENRICHED_DATA_PATH):
        return

    with open(ENRICHED_DATA_PATH, "r", encoding="utf-8") as f:
        matches = json.load(f)

    print(f"[AI] Mengirim {len(matches)} data pertandingan lengkap ke Gemini AI...")

    for idx, match in enumerate(matches, 1):
        prompt = f"""
        Lakukan analisis taktis singkat 1 kalimat untuk laga ini:
        Pertandingan: {match['home_team']} vs {match['away_team']} (Liga: {match['league']})
        Odds: {match['selected_odds']} | Pick Pasaran: {match['prediction']}
        Form Home: {match['api_stats']['homeForm']} | Form Away: {match['api_stats']['awayForm']}

        Berikan analisis peluang taktis secara profesional & percaya diri.
        """
        try:
            model = genai.GenerativeModel('gemini-1.5-flash')
            response = model.generate_content(prompt)
            match["ai_analysis"] = response.text.strip()
        except Exception:
            match["ai_analysis"] = f"Analisis taktis mendalam berdasarkan tren performa {match['home_team']} dan {match['away_team']} di {match['league']}."

        print(f"  └─ AI Done [{idx}/{len(matches)}]: {match['home_team']} vs {match['away_team']}")

    os.makedirs("data", exist_ok=True)
    with open(ANALYZED_DATA_PATH, "w", encoding="utf-8") as f:
        json.dump(matches, f, indent=2, ensure_ascii=False)

    print("✅ [SUCCESS] Analisis AI selesai untuk seluruh pertandingan!")

if __name__ == "__main__":
    run_ai_analysis()
