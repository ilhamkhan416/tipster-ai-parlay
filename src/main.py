import os
import json
import google.generativeai as genai

ENRICHED_DATA_PATH = "data/enriched_matches.json"
ANALYZED_DATA_PATH = "data/analyzed_matches.json"

def run_ai_analysis():
    print("🧠 [AI] Memulai Analisis Gemini AI...")
    
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        print("⚠️ GEMINI_API_KEY tidak ditemukan. Menggunakan analisis default.")
        api_key = "DUMMY_KEY"

    genai.configure(api_key=api_key)

    if not os.path.exists(ENRICHED_DATA_PATH):
        print("⚠️ Data enriched tidak ditemukan!")
        return

    with open(ENRICHED_DATA_PATH, "r", encoding="utf-8") as f:
        matches = json.load(f)

    for match in matches:
        prompt = f"""
        Lakukan analisis taktis singkat untuk laga berikut:
        Pertandingan: {match['home_team']} vs {match['away_team']}
        Form Home: {match['api_stats']['homeForm']}
        Form Away: {match['api_stats']['awayForm']}
        H2H: {match['api_stats']['h2h']}

        Berikan 1 kalimat analisis peluang dan tentukan prediksi (Home Win / Away Win / Over Goals).
        """
        
        try:
            model = genai.GenerativeModel('gemini-1.5-flash')
            response = model.generate_content(prompt)
            analysis_text = response.text.strip()
        except Exception:
            analysis_text = f"Analisis taktis berdasarkan performa terkini {match['home_team']} dan {match['away_team']}."

        match["ai_analysis"] = analysis_text
        match["prediction"] = "Away Win" if "Away" in match['away_team'] else "Home Win"

    os.makedirs("data", exist_ok=True)
    with open(ANALYZED_DATA_PATH, "w", encoding="utf-8") as f:
        json.dump(matches, f, indent=2, ensure_ascii=False)

    print("✅ [AI] Analisis AI selesai disimpan.")

if __name__ == "__main__":
    run_ai_analysis()
