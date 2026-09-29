import os
import json
from datetime import datetime

ENRICHED_DATA_PATH = "data/enriched_matches.json"
ANALYSIS_DATA_PATH = "data/ai_analysis.json"
OUTPUT_HTML_PATH = "index.html"

def load_json(path):
    if not os.path.exists(path):
        return []
    with open(path, "r", encoding="utf-8") as f:
        try:
            return json.load(f)
        except Exception:
            return []

def generate_receipt_html():
    matches = load_json(ENRICHED_DATA_PATH)
    analysis = load_json(ANALYSIS_DATA_PATH)
    
    current_time = datetime.now().strftime("%d/%m/%Y %H:%M:%S")

    cards_html = ""
    for idx, match in enumerate(matches[:10], 1):
        home = match.get("home_team", "Home")
        away = match.get("away_team", "Away")
        league = match.get("league", "PARLAY")
        odds = match.get("selected_odds", 1.60)
        
        stats = match.get("api_stats", {})
        h2h = stats.get("h2h", "Data H2H tidak tersedia")
        home_form = " ".join(stats.get("homeForm", ["-"]))
        away_form = " ".join(stats.get("awayForm", ["-"]))
        
        # Ambil insight dari analisis AI jika ada
        ai_insight = "Analisis taktis mendalam berdasarkan performa terkini, tren H2H Flashscore, dan efisiensi peluang tim."
        if idx <= len(analysis):
            ai_insight = analysis[idx-1].get("reason", ai_insight)

        cards_html += f"""
        <div class="receipt-item">
            <div class="item-header">
                <span class="match-num">#{idx}</span>
                <span class="teams">{home} vs {away}</span>
            </div>
            <div class="meta-row">
                <span>League: {league}</span>
                <span class="pick-odds">PICK: Away Win @{odds:.2f}</span>
            </div>
            
            <button class="toggle-btn" onclick="toggleDetails('details-{idx}')">
                🔍 LIHAT STATS & ANALISIS AI
            </button>
            
            <div id="details-{idx}" class="details-box" style="display: none;">
                <div class="stat-section">
                    <strong>📊 DATA STATISTIK FLASHSCORE:</strong>
                    <ul>
                        <li>H2H: {h2h}</li>
                        <li>Form Home (5 Laga): [{home_form}]</li>
                        <li>Form Away (5 Laga): [{away_form}]</li>
                    </ul>
                </div>
                <div class="ai-section">
                    <strong>🧠 ANALISIS TAKTIS BOLA DARI AI:</strong>
                    <p>{ai_insight}</p>
                </div>
            </div>
        </div>
        """

    html_content = f"""<!DOCTYPE html>
<html lang="id">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Struk Analisis Parlay AI</title>
    <style>
        body {{
            background-color: #121212;
            color: #e0e0e0;
            font-family: 'Courier New', Courier, monospace;
            display: flex;
            justify-content: center;
            padding: 20px;
        }}
        .receipt-container {{
            width: 100%;
            max-width: 600px;
            background-color: #1e1e1e;
            border: 2px dashed #444;
            padding: 20px;
            box-shadow: 0 4px 10px rgba(0,0,0,0.5);
        }}
        .header {{
            text-align: center;
            border-bottom: 2px dashed #444;
            padding-bottom: 10px;
            margin-bottom: 15px;
        }}
        .receipt-item {{
            border-bottom: 1px dashed #333;
            padding: 12px 0;
        }}
        .item-header {{
            display: flex;
            justify-content: space-between;
            font-weight: bold;
            font-size: 1.1em;
        }}
        .meta-row {{
            display: flex;
            justify-content: space-between;
            color: #aaa;
            font-size: 0.9em;
            margin: 5px 0;
        }}
        .pick-odds {{
            color: #00ff66;
            font-weight: bold;
        }}
        .toggle-btn {{
            width: 100%;
            background-color: #2a2a2a;
            color: #fff;
            border: 1px solid #444;
            padding: 6px;
            cursor: pointer;
            margin-top: 5px;
            font-family: inherit;
        }}
        .toggle-btn:hover {{
            background-color: #333;
        }}
        .details-box {{
            background-color: #181818;
            border: 1px solid #333;
            padding: 10px;
            margin-top: 8px;
            font-size: 0.85em;
        }}
        .stat-section ul {{
            margin: 5px 0 10px 15px;
            padding: 0;
        }}
        .ai-section p {{
            margin: 5px 0 0 0;
            color: #ddd;
        }}
    </style>
</head>
<body>
    <div class="receipt-container">
        <div class="header">
            <h2>--- SELECTION LIST (TOP 10) ---</h2>
            <p>Dicetak: {current_time}</p>
        </div>
        
        {cards_html}

    </div>

    <script>
        function toggleDetails(id) {{
            var el = document.getElementById(id);
            if (el.style.display === "none") {{
                el.style.display = "block";
            }} else {{
                el.style.display = "none";
            }}
        }}
    </script>
</body>
</html>
"""

    os.makedirs(os.path.dirname(OUTPUT_HTML_PATH) if os.path.dirname(OUTPUT_HTML_PATH) else ".", exist_ok=True)
    with open(OUTPUT_HTML_PATH, "w", encoding="utf-8") as f:
        f.write(html_content)

    print(f"✅ Struk HTML berhasil dibuat di '{OUTPUT_HTML_PATH}'")

if __name__ == "__main__":
    generate_receipt_html()
