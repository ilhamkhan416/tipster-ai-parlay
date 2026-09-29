import os
import json
import time

ANALYZED_DATA_PATH = "data/analyzed_matches.json"
OUTPUT_HTML_PATH = "index.html"

def generate_html():
    print("\n" + "=" * 60)
    print("🖨️ STEP 6: CETAK STRUK PARLAY HTML")
    print("=" * 60)

    matches = []
    if os.path.exists(ANALYZED_DATA_PATH):
        with open(ANALYZED_DATA_PATH, "r", encoding="utf-8") as f:
            matches = json.load(f)

    match_cards_html = ""
    for idx, m in enumerate(matches, 1):
        home = m.get("home_team", "Home")
        away = m.get("away_team", "Away")
        league = m.get("league", "MAINBOLAKAKI PARLAY")
        match_time = m.get("time", "00:00")
        odds = m.get("selected_odds", 1.65)
        pred = m.get("prediction", "Away Win")
        analysis = m.get("ai_analysis", "Analisis taktis tim.")

        home_form_str = " ".join(m["api_stats"].get("homeForm", ["N/A"]))
        away_form_str = " ".join(m["api_stats"].get("awayForm", ["N/A"]))

        match_cards_html += f"""
        <div class="card">
            <div class="card-header">
                <div>
                    <span class="num">#{idx}</span>
                    <span class="time">{match_time}</span>
                    <span class="teams">{home} vs {away}</span>
                </div>
                <div class="pick">PICK: {pred} @{odds}</div>
            </div>
            <div class="league">League: {league}</div>
            
            <details>
                <summary>🔍 LIHAT STATS & ANALISIS AI</summary>
                <div class="stats">
                    <p>📊 <strong>DATA STATISTIK FLASHSCORE:</strong></p>
                    <ul>
                        <li>Form Home (5 Laga): [{home_form_str}]</li>
                        <li>Form Away (5 Laga): [{away_form_str}]</li>
                    </ul>
                    <p>🧠 <strong>ANALISIS TAKTIS BOLA DARI AI:</strong></p>
                    <p class="analysis-text">{analysis}</p>
                </div>
            </details>
        </div>
        """

    current_time = time.strftime("%d/%m/%Y %H:%M:%S")

    html_content = f"""<!DOCTYPE html>
<html lang="id">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Struk AI Parlay</title>
    <style>
        body {{
            background-color: #121212;
            color: #e0e0e0;
            font-family: 'Courier New', Courier, monospace;
            padding: 20px;
            display: flex;
            justify-content: center;
        }}
        .receipt {{
            background-color: #1e1e1e;
            border: 1px dashed #444;
            padding: 20px;
            max-width: 600px;
            width: 100%;
            border-radius: 8px;
            box-shadow: 0 4px 10px rgba(0,0,0,0.5);
        }}
        .title {{
            text-align: center;
            font-weight: bold;
            font-size: 1.2rem;
            letter-spacing: 2px;
            margin-bottom: 5px;
        }}
        .subtitle {{
            text-align: center;
            font-size: 0.85rem;
            color: #888;
            margin-bottom: 20px;
        }}
        .card {{
            border-bottom: 1px solid #333;
            padding: 15px 0;
        }}
        .card-header {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            font-weight: bold;
        }}
        .num {{ color: #ff9800; margin-right: 8px; }}
        .time {{ color: #aaa; margin-right: 8px; }}
        .teams {{ color: #fff; }}
        .pick {{ color: #4caf50; font-weight: bold; }}
        .league {{ font-size: 0.8rem; color: #777; margin-top: 4px; }}
        details {{ margin-top: 10px; cursor: pointer; }}
        summary {{ font-size: 0.85rem; color: #64b5f6; outline: none; }}
        .stats {{ background: #252525; padding: 10px; border-radius: 5px; margin-top: 8px; font-size: 0.8rem; }}
        .stats ul {{ padding-left: 15px; margin: 5px 0; }}
        .analysis-text {{ color: #bbb; font-style: italic; margin-top: 5px; }}
    </style>
</head>
<body>
    <div class="receipt">
        <div class="title">--- SELECTION LIST (POTENTIAL MATCHES) ---</div>
        <div class="subtitle">Dicetak: {current_time}</div>
        {match_cards_html}
    </div>
</body>
</html>
"""

    with open(OUTPUT_HTML_PATH, "w", encoding="utf-8") as f:
        f.write(html_content)

    print("✅ [SUCCESS] Struk HTML berhasil dicetak!")

if __name__ == "__main__":
    generate_html()
