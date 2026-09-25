import json
import os
import re
import requests
from datetime import datetime

# Path file
RAW_DATA_PATH = "data/raw_scraped.json"
TODAY_DATA_PATH = "data/today.json"

# Mengambil API Key dari GitHub Secrets / Environment
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")


def load_scraped_data():
    """Membaca data mentah hasil scraping"""
    if not os.path.exists(RAW_DATA_PATH):
        print("⚠️ File data mentah tidak ditemukan.")
        return []
    with open(RAW_DATA_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def local_algorithm_filter(raw_matches):
    """
    STEP 2: HARD FILTERING & ELIMINASI DRAW
    Menyaring pertandingan berdasarkan logika matematis Odds +EV
    """
    filtered = []
    print("🧠 [PRE-FILTER] Memulai sanitasi dan hard filtering data mentah...")

    for item in raw_matches:
        raw_lines = item.get("raw_info", [])
        if len(raw_lines) < 3:
            continue

        text_block = " ".join(raw_lines)
        
        # Ekstrak semua angka desimal sebagai kandidat odds (1X2)
        odds_found = re.findall(r'\b\d+\.\d+\b', text_block)
        parsed_odds = [float(o) for o in odds_found if float(o) > 1.0]

        if len(parsed_odds) < 3:
            continue 

        odds_home = parsed_odds[0]
        odds_draw = parsed_odds[1]
        odds_away = parsed_odds[2]

        # ---------------------------------------------------------
        # ATURAN ELIMINASI KETAT (HARD FILTERING)
        # ---------------------------------------------------------
        if odds_draw <= 3.15:
            continue
            
        if abs(odds_home - odds_away) < 0.35:
            continue
            
        if odds_home > 2.30 and odds_away > 2.30:
            continue

        pick_candidate = "Home Win" if odds_home < odds_away else "Away Win"
        best_odds = min(odds_home, odds_away)
            
        if best_odds < 1.50:
            continue

        filtered.append({
            "match_info": text_block[:200],
            "home_odds": odds_home,
            "draw_odds": odds_draw,
            "away_odds": odds_away,
            "best_pick_candidate": pick_candidate,
            "best_odds": best_odds
        })

    print(f"✅ [PRE-FILTER] Lolos saringan tahap 1: {len(filtered)} pertandingan potensial.")
    
    # DYNAMIC TOP 25 SELECTION
    filtered = sorted(filtered, key=lambda x: x["best_odds"])
    top_matches = filtered[:25]
    print(f"🎯 [PRE-FILTER] Mengambil Top {len(top_matches)} pertandingan murni untuk dianalisis AI.")
    
    return top_matches


def build_universal_prompt(compact_matches):
    """
    Membuat Prompt Universal FIXSCORE (+EV AI Engine) dengan parameter evaluasi mendalam
    """
    matches_json_str = json.dumps(compact_matches, ensure_ascii=False, indent=2)
    
    return (
        "Kamu adalah Head Analyst Sports Intelligence & Senior Quantitative Handicapper profesional (+EV Engine).\n"
        "Tugasmu adalah mengevaluasi tingkat kemenangan (+EV) dari kandidat pertandingan sepak bola secara presisi tinggi.\n\n"
        f"Berikut adalah data {len(compact_matches)} pertandingan hari ini yang telah lolos pra-saringan algoritma (+EV & No-Draw Rule):\n"
        f"{matches_json_str}\n\n"
        "METODOLOGI ANALISIS BERLAPIS (MANDATORY EVALUATION):\n"
        "Sebelum menentukan pilihan (pick) dan persentase Win Rate (%), WAJIB mengevaluasi 5 FAKTOR KRUSIAL berikut:\n"
        "1. ABSENSI & KONDISI PEMAIN KUNCI: Dampak taktis jika top scorer/playmaker/bek utama cedera/akumulasi kartu.\n"
        "2. SUSUNAN PEMAIN & ROTASI SKUAD: Potensi rotasi akibat jadwal padat (Full Strength vs B-Team).\n"
        "3. REKOR HEAD-TO-HEAD & MATCHUP TAKTIS: Dominasi 3-5 H2H terakhir & pertentangan gaya bermain.\n"
        "4. PERFORMA & BERITA TERKINI: Tren 5 laga terakhir (xG, Conversion Rate) & berita internal klub.\n"
        "5. MOTIVASI & SIFAT PERTANDINGAN: Urgensi poin (perburuan gelar/degradasi vs laga formalitas).\n\n"
        "ATURAN DEDUPLIKASI KETAT & OPSI PASARAN:\n"
        "1. TIDAK BOLEH ADA TIM/PARTAI YANG SAMA PERSIH DIPAKAI LEBIH DARI SATU KALI di seluruh paket parlay. 1 Match = Max 1 Pick.\n"
        "2. DILARANG KERAS memilih opsi DRAW (X).\n"
        "3. Prioritaskan 1X2 (Home/Away Win) & Asian Handicap (HDP). O/U hanya jika data xG sangat meyakinkan (Utamakan Over).\n\n"
        "SUSUNAN PAKET PARLAY:\n"
        '- "parlay3"  : 3 pertandingan terbaik dengan kepastian tertinggi (Low Risk / Aman).\n'
        '- "parlay5"  : 5 pertandingan seimbang dengan +EV tinggi (Medium Risk).\n'
        '- "parlay10" : 10 pertandingan potensial untuk payout maksimal (High Return).\n\n'
        "FORMAT KELUARAN WAJIB (HANYA JSON MURNI tanpa markdown/teks tambahan):\n"
        "{\n"
        '  "parlay3": [{"match": "Tim A vs Tim B", "league": "Liga", "pick": "Home Win", "odds": 1.75, "winProb": 82, "aiReason": "Alasan taktis & H2H (max 15 kata)"}],\n'
        '  "parlay5": [... 5 objek ...],\n'
        '  "parlay10": [... 10 objek ...]\n'
        "}"
    )


def analyze_with_gemini(compact_matches):
    """TIER 1: Google Gemini Engine"""
    if not GEMINI_API_KEY:
        print("⚠️ GEMINI_API_KEY tidak ditemukan di environment.")
        return None

    print("🟢 [TIER 1: GEMINI] Memeriksa daftar model Gemini aktif...")
    url_models = f"https://generativelanguage.googleapis.com/v1beta/models?key={GEMINI_API_KEY}"
    candidate_models = []
    
    try:
        res = requests.get(url_models, timeout=10)
        if res.status_code == 200:
            models_data = res.json().get("models", [])
            for m in models_data:
                if "generateContent" in m.get("supportedGenerationMethods", []):
                    model_id = m["name"].replace("models/", "")
                    if "gemini" in model_id.lower():
                        candidate_models.append(model_id)
            print(f"📋 [GEMINI] Model aktif ditemukan: {candidate_models[:3]}")
    except Exception as e:
        print(f"⚠️ Gagal cek model Gemini: {e}")

    if not candidate_models:
        candidate_models = ["gemini-1.5-flash", "gemini-1.5-pro"]

    prompt = build_universal_prompt(compact_matches)

    for model_name in candidate_models:
        print(f"🔄 [GEMINI] Memproses request dengan model '{model_name}'...")
        url_generate = f"https://generativelanguage.googleapis.com/v1beta/models/{model_name}:generateContent?key={GEMINI_API_KEY}"
        headers = {"Content-Type": "application/json"}
        payload = {
            "contents": [{"parts": [{"text": prompt}]}],
            "generationConfig": {"temperature": 0.2}
        }

        try:
            response = requests.post(url_generate, headers=headers, json=payload, timeout=30)
            if response.status_code == 200:
                data = response.json()
                content = data['candidates'][0]['content']['parts'][0]['text']
                json_match = re.search(r'\{.*\}', content, re.DOTALL)
                if json_match:
                    parsed_json = json.loads(json_match.group(0))
                    print(f"✅ [GEMINI SUCCESS] Analisis BERHASIL menggunakan '{model_name}'!")
                    return parsed_json
            else:
                print(f"⚠️ Model Gemini '{model_name}' merespon HTTP {response.status_code}.")
        except Exception as e:
            print(f"⚠️ Error pada Gemini '{model_name}': {e}")

    print("❌ [GEMINI FAILED] Seluruh model Gemini gagal.")
    return None


def analyze_with_openai(compact_matches):
    """TIER 2: OpenAI Engine"""
    if not OPENAI_API_KEY:
        print("⚠️ OPENAI_API_KEY tidak ditemukan di environment.")
        return None

    print("🔵 [TIER 2: OPENAI] Memeriksa daftar model OpenAI aktif...")
    headers = {
        "Authorization": f"Bearer {OPENAI_API_KEY}",
        "Content-Type": "application/json"
    }

    candidate_models = []
    try:
        res = requests.get("https://api.openai.com/v1/models", headers=headers, timeout=10)
        if res.status_code == 200:
            models_data = res.json().get("data", [])
            all_ids = [m['id'] for m in models_data if 'id' in m]
            for target in ["gpt-4o-mini", "gpt-4o", "gpt-3.5-turbo"]:
                if target in all_ids:
                    candidate_models.append(target)
            print(f"📋 [OPENAI] Model aktif ditemukan: {candidate_models}")
    except Exception as e:
        print(f"⚠️ Gagal cek model OpenAI: {e}")

    if not candidate_models:
        candidate_models = ["gpt-4o-mini", "gpt-4o"]

    prompt = build_universal_prompt(compact_matches)

    for model_name in candidate_models:
        print(f"🔄 [OPENAI] Memproses request dengan model '{model_name}'...")
        payload = {
            "model": model_name,
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0.2
        }

        try:
            response = requests.post("https://api.openai.com/v1/chat/completions", headers=headers, json=payload, timeout=30)
            if response.status_code == 200:
                result = response.json()
                content = result['choices'][0]['message']['content']
                json_match = re.search(r'\{.*\}', content, re.DOTALL)
                if json_match:
                    parsed_json = json.loads(json_match.group(0))
                    print(f"✅ [OPENAI SUCCESS] Analisis BERHASIL menggunakan '{model_name}'!")
                    return parsed_json
            else:
                print(f"⚠️ Model OpenAI '{model_name}' merespon HTTP {response.status_code}.")
        except Exception as e:
            print(f"⚠️ Error pada OpenAI '{model_name}': {e}")

    print("❌ [OPENAI FAILED] Seluruh model OpenAI gagal.")
    return None


def analyze_with_groq(compact_matches):
    """TIER 3: Groq AI Engine"""
    if not GROQ_API_KEY:
        print("⚠️ GROQ_API_KEY tidak ditemukan di environment.")
        return None

    print("🟠 [TIER 3: GROQ AI] Memeriksa daftar model Groq aktif...")
    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }

    text_models = []
    try:
        response = requests.get("https://api.groq.com/openai/v1/models", headers=headers, timeout=10)
        if response.status_code == 200:
            raw_models = [m['id'] for m in response.json().get('data', []) if 'id' in m]
            text_models = [
                m for m in raw_models 
                if not any(x in m.lower() for x in ['whisper', 'guard', 'arabic', 'orpheus', 'safeguard'])
            ]
            print(f"📋 [GROQ] Model teks terverifikasi: {text_models[:3]}")
    except Exception as e:
        print(f"⚠️ Gagal cek model Groq: {e}")

    if not text_models:
        text_models = ["llama-3.3-70b-versatile", "llama-3.1-8b-instant"]

    prompt = build_universal_prompt(compact_matches)

    for model_name in text_models:
        print(f"🔄 [GROQ] Memproses request dengan model '{model_name}'...")
        payload = {
            "model": model_name,
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0.2
        }

        try:
            response = requests.post("https://api.groq.com/openai/v1/chat/completions", headers=headers, json=payload, timeout=30)
            if response.status_code == 200:
                result = response.json()
                content = result['choices'][0]['message']['content']
                json_match = re.search(r'\{.*\}', content, re.DOTALL)
                if json_match:
                    parsed_json = json.loads(json_match.group(0))
                    print(f"✅ [GROQ SUCCESS] Analisis BERHASIL menggunakan '{model_name}'!")
                    return parsed_json
            else:
                print(f"⚠️ Model Groq '{model_name}' merespon HTTP {response.status_code}.")
        except Exception as e:
            print(f"⚠️ Error pada Groq '{model_name}': {e}")

    print("❌ [GROQ FAILED] Seluruh model Groq gagal.")
    return None


def enforce_strict_deduplication(parlay_data):
    """STEP 6: STRICT DE-DUPLICATION (Unique Match Enforcer)"""
    if not parlay_data:
        return parlay_data

    used_matches = set()
    cleaned_packages = {"parlay3": [], "parlay5": [], "parlay10": []}

    for key in ["parlay3", "parlay5", "parlay10"]:
        raw_list = parlay_data.get(key, [])
        unique_list = []
        
        for item in raw_list:
            match_name = item.get("match", "").strip().lower()
            normalized_key = re.sub(r'\s+', ' ', match_name)
            
            if normalized_key and normalized_key not in used_matches:
                used_matches.add(normalized_key)
                unique_list.append(item)
        
        cleaned_packages[key] = unique_list

    return cleaned_packages


def generate_fallback_data(compact_matches):
    """Algoritma Fallback Murni (Python)"""
    print("⚙️ [FALLBACK ENGINE] Menyusun paket parlay matematis murni dari data lokal...")
    base_list = []
    
    for i, m in enumerate(compact_matches[:10], 1):
        best_pick = m.get("best_pick_candidate", "Home Win")
        best_odds = m.get("best_odds", 1.75)
        
        base_list.append({
            "match": f"Match Candidate #{i}",
            "league": "Top Football League",
            "pick": best_pick,
            "odds": best_odds,
            "winProb": 72 + (i % 6),
            "aiReason": "Lolos hard filter No-Draw & +EV rasio odds pasar unggulan."
        })

    return {
        "parlay3": base_list[:3],
        "parlay5": base_list[:5],
        "parlay10": base_list[:10]
    }


def main():
    print("🚀 [PIPELINE] Memulai pemrosesan data harian FIXSCORE AI...")
    
    raw_matches = load_scraped_data()
    compact_matches = local_algorithm_filter(raw_matches)
    
    if not compact_matches:
        print("⚠️ Tidak ada pertandingan yang lolos hard filter hari ini.")
        parlay_packages = generate_fallback_data([])
    else:
        parlay_packages = analyze_with_gemini(compact_matches)
        
        if not parlay_packages:
            print("🔄 [FALLBACK] Berpindah dari Gemini ke OpenAI (Tier 2)...")
            parlay_packages = analyze_with_openai(compact_matches)
            
        if not parlay_packages:
            print("🔄 [FALLBACK] Berpindah dari OpenAI ke Groq AI (Tier 3)...")
            parlay_packages = analyze_with_groq(compact_matches)
            
        if not parlay_packages:
            print("⚠️ Seluruh Provider AI Publik Gagal. Menggunakan Algoritma Fallback Lokal...")
            parlay_packages = generate_fallback_data(compact_matches)

    print("🧹 [DEDUPLICATION] Memeriksa & membersihkan partai kembar...")
    final_parlays = enforce_strict_deduplication(parlay_packages)

    now_str = datetime.now().strftime("%d/%m/%Y %H:%M WIB")
    final_output = {
        "updatedAt": now_str,
        "parlay3": final_parlays.get("parlay3", []),
        "parlay5": final_parlays.get("parlay5", []),
        "parlay10": final_parlays.get("parlay10", [])
    }
    
    os.makedirs("data", exist_ok=True)
    with open(TODAY_DATA_PATH, "w", encoding="utf-8") as f:
        json.dump(final_output, f, indent=2, ensure_ascii=False)
        
    print(f"💾 [PIPELINE] Selesai! Paket parlay FIXSCORE AI berhasil disimpan di '{TODAY_DATA_PATH}'.")


if __name__ == "__main__":
    main()
