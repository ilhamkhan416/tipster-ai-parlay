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

        # Butuh minimal 3 odds (Home, Draw, Away) untuk dianalisa
        if len(parsed_odds) < 3:
            continue 

        # Asumsi standar urutan 1X2: [Home, Draw, Away]
        odds_home = parsed_odds[0]
        odds_draw = parsed_odds[1]
        odds_away = parsed_odds[2]

        # ---------------------------------------------------------
        # ATURAN ELIMINASI KETAT (HARD FILTERING)
        # ---------------------------------------------------------
        
        # Aturan 1: Jika odds Draw terlalu rendah (Bookmaker memprediksi seri)
        if odds_draw <= 3.15:
            continue
            
        # Aturan 2: Kekuatan kedua tim terlalu seimbang (Selisih odds tipis)
        if abs(odds_home - odds_away) < 0.35:
            continue
            
        # Aturan 3: Tidak ada tim favorit yang jelas (Keduanya lemah)
        if odds_home > 2.30 and odds_away > 2.30:
            continue

        # Tentukan siapa tim Favorit (Home atau Away)
        pick_candidate = "Home Win" if odds_home < odds_away else "Away Win"
        best_odds = min(odds_home, odds_away)
            
        # Aturan 4: Batas Minimal Odds untuk tim favorit tidak boleh di bawah 1.50
        if best_odds < 1.50:
            continue

        # Jika lolos semua saringan, masukkan ke daftar potensial
        filtered.append({
            "match_info": text_block[:200], # Potong ringkasan agar hemat token AI
            "home_odds": odds_home,
            "draw_odds": odds_draw,
            "away_odds": odds_away,
            "best_pick_candidate": pick_candidate,
            "best_odds": best_odds
        })

    print(f"✅ [PRE-FILTER] Lolos saringan tahap 1: {len(filtered)} pertandingan potensial.")
    
    # ---------------------------------------------------------
    # DYNAMIC TOP 25 SELECTION
    # ---------------------------------------------------------
    # Urutkan berdasarkan odds terbaik (tingkat kepastian tertinggi)
    filtered = sorted(filtered, key=lambda x: x["best_odds"])
    
    # Ambil maksimal Top 25 pertandingan untuk meringankan kerja AI
    top_matches = filtered[:25]
    print(f"🎯 [PRE-FILTER] Mengambil Top {len(top_matches)} pertandingan murni untuk dianalisis AI.")
    
    return top_matches
