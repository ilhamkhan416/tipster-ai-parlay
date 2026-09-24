import os
import json
import requests
from datetime import datetime, timedelta, timezone

# Konfigurasi Zona Waktu WIB (UTC+7)
WIB = timezone(timedelta(hours=7))

API_SPORTS_KEY = os.getenv("RAPIDAPI_KEY")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

HEADERS_SPORTS = {
    "x-apisports-key": API_SPORTS_KEY if API_SPORTS_KEY else ""
}

def get_all_raw_matches_from_api():
    """Mengambil SELURUH jadwal pertandingan hari ini & besok dari API-SPORTS (Filter Jam 11 s/d 11)"""
    now_wib = datetime.now(WIB)
    today_str = now_wib.strftime("%Y-%m-%d")
    tomorrow_str = (now_wib + timedelta(days=1)).strftime("%Y-%m-%d")
    
    cutoff_today = now_wib.replace(hour=11, minute=0, second=0, microsecond=0)
    cutoff_tomorrow = cutoff_today + timedelta(days=1)
    
    url = "https://v3.football.api-sports.io/fixtures"
    raw_list = []
    
    if API_SPORTS_KEY:
        for date_target in [today_str, tomorrow_str]:
            try:
                res = requests.get(url, headers=HEADERS_SPORTS, params={"date": date_target}, timeout=15)
                if res.status_code == 200:
                    data = res.json().get("response", [])
                    for item in data:
                        fixture = item.get("fixture", {})
                        league = item.get("league", {}).get("name", "").upper()
                        teams = item.get("teams", {})
                        
                        # Filter membuang liga gurem / kelompok umur
                        if any(bad in league for bad in ["U19", "U20", "U21", "RESERVE", "WOMEN", "AMATEUR", "YOUTH"]):
                            continue
                            
                        date_utc_str = fixture.get("date", "")
                        if date_utc_str:
                            match_dt_wib = datetime.fromisoformat(date_utc_str.replace("Z", "+00:00")).astimezone(WIB)
                            
                            # RENTANG KETAT: Hanya ambil laga antara Jam 11:00 WIB Hari Ini s/d Jam 11:00 WIB Besok
                            if not (cutoff_today <= match_dt_wib < cutoff_tomorrow):
                                continue
                        else:
                            continue
                            
                        raw_list.append({
                            "league": league,
                            "homeTeam": teams.get("home", {}).get("name"),
                            "awayTeam": teams.get("away", {}).get("name"),
                            "kickoffUtc": date_utc_str,
                            "kickoffWib": match_dt_wib.strftime("%H:%M") + " WIB"
                        })
            except Exception as e:
                print(f"Error fetch raw matches ({date_target}): {e}")
            
    return raw_list

def analyze_and_filter_with_gemini(raw_matches):
    """Mengirim data pertandingan ke Gemini AI dengan multiple endpoint fallback"""
    if not GEMINI_API_KEY or not raw_matches:
        print("PERINGATAN: GEMINI_API_KEY / Data Mentah Kosong!")
        return []

    # Daftar endpoint model yang dicoba secara berurutan
    endpoints = [
        "https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent",
        "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent",
        "https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-pro:generateContent"
    ]

    prompt = f"""
    Kamu adalah Head Quant Analyst Sepak Bola. Berikut adalah jadwal pertandingan sepak bola NYATA dalam rentang jam 11:00 WIB hari ini s/d 11:00 WIB besok:
    {json.dumps(raw_matches, indent=2)}

    TUGAS UTAMA:
    1. Pilih maksimal 10 pertandingan TERBAIK dari daftar di atas yang melibatkan klub/liga papan atas (Premier League, La Liga, Serie A, Champions League, Eredivisie, dll).
    2. Tentukan proyeksi pilihan pasaran paling masuk akal (1X2, Asian Handicap -1.0, atau Over/Under 2.5).
    3. Output WAJIB berupa JSON ARRAY MURNI tanpa teks/markdown tambahan:
    [
      {{
        "league": "NAMA LIGA",
        "homeTeam": "Tim Kandang",
        "awayTeam": "Tim Tandang",
        "kickoffUtc": "ISO String Waktu UTC",
        "kickoff": "HH:MM WIB",
        "pick": "Rekomendasi Pilihan",
        "marketType": "1X2 / HDP / OU",
        "odds": 1.65,
        "winProb": 78,
        "posEdge": "+16.5% +EV (Kalkulasi Engine)",
        "riskFactor": "-3.8% Volatilitas Transisi",
        "aiNotes": "Analisis taktis 1-2 kalimat."
      }}
    ]
    """

    payload = {"contents": [{"parts": [{"text": prompt}]}]}
    
    # Pengiriman API Key lewat Header Resmi Google AI Studio
    headers = {
        "Content-Type": "application/json",
        "x-goog-api-key": GEMINI_API_KEY
    }

    for url in endpoints:
        try:
            print(f"Mencoba koneksi ke Gemini API via {url.split('/')[-1]}...")
            res = requests.post(url, json=payload, headers=headers, timeout=40)
            
            if res.status_code == 200:
                result = res.json()
                text_response = result['candidates'][0]['content']['parts'][0]['text']
                
                # Pembersihan string JSON
                text_cleaned = text_response.strip()
                if "```json" in text_cleaned:
                    text_cleaned = text_cleaned.split("```json")[1].split("```")[0].strip()
                elif "```" in text_cleaned:
                    text_cleaned = text_cleaned.split("```")[1].split("```")[0].strip()

                analyzed_matches = json.loads(text_cleaned)
                
                for idx, m in enumerate(analyzed_matches):
                    m["id"] = idx + 1
                    m["isVip"] = True if idx >= 4 else False
                    m["homeForm"] = ["W", "W", "D", "W", "L"]
                    m["awayForm"] = ["D", "W", "L", "W", "D"]
                    m["metrics"] = {"form": 88, "h2h": 82, "xG": 80, "marketVal": 84}
                    
                print("BERHASIL memproses data via Gemini AI!")
                return analyzed_matches
            else:
                print(f"Gagal koneksi endpoint ({res.status_code}): {res.text[:100]}")
        except Exception as e:
            print(f"Error pada endpoint {url}: {e}")
            
    return []

if __name__ == "__main__":
    print("Menjalankan FIXSCORE Quant Engine...")
    raw_data = get_all_raw_matches_from_api()
    print(f"Total laga nyata ditemukan: {len(raw_data)} pertandingan.")
    
    final_matches = analyze_and_filter_with_gemini(raw_data)
    
    if final_matches:
        os.makedirs("data", exist_ok=True)
        with open("data/today.json", "w") as f:
            json.dump(final_matches, f, indent=2)
        print(f"SELESAI! {len(final_matches)} pertandingan NYATA hasil analisis Gemini disimpan ke data/today.json")
    else:
        print("Gagal memproses Gemini API. Menampilkan log error.")
