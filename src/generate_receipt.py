import json
import os

TODAY_DATA_PATH = "data/today.json"
OUTPUT_HTML_PATH = "index.html"

def generate_receipt_html():
    if not os.path.exists(TODAY_DATA_PATH):
        print("⚠️ File today.json tidak ditemukan.")
        return

    with open(TODAY_DATA_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)

    updated_at = data.get("updatedAt", "-")
    parlay10 = data.get("parlay10", [])

    items_html = ""
    for idx, item in enumerate(parlay10, 1):
        stats = item.get("apiStatsUsed", {})
        home_form = " ".join(stats.get("homeForm", [])) if isinstance(stats.get("homeForm"), list) else "-"
        away_form = " ".join(stats.get("awayForm", [])) if isinstance(stats.get("awayForm"), list) else "-"
        
        items_html += f"""
        <div class="item">
            <div class="row">
                <span class="num">#{idx}</span>
                <span class="match">{item.get('match')}</span>
            </div>
            <div class="sub-info">
                <span>League: {item.get('league')}</span>
            </div>
            <div class="row pick-row">
                <span class="pick">PICK: <strong>{item.get('pick')}</strong></span>
                <span class="odds">@{item.get('odds')}</span>
            </div>
            <div class="notes">
                Prob: {item.get('winProb')}% | {item.get('expertReason')}
            </div>
            
            <!-- Tombol Toggle Detail AI & Stats -->
            <button class="btn-detail" onclick="toggleDetail('detail-{idx}')">🔍 Lihat Stats & Analisis AI</button>
            
            <!-- Panel Detail Tersembunyi -->
            <div id="detail-{idx}" class="detail-box" style="display: none;">
                <div class="detail-header">📊 DATA STATISTIK API-FOOTBALL:</div>
                <div class="detail-item">• H2H: {stats.get('h2hSummary', item.get('analytics', {}).get('h2hSummary', '-'))}</div>
                <div class="detail-item">• Rerata Gol: {stats.get('avgGoals', item.get('analytics', {}).get('avgGoals', '-'))}</div>
                <div class="detail-item">• Form Home (5 Laga): [{home_form}]</div>
                <div class="detail-item">• Form Away (5 Laga): [{away_form}]</div>
                
                <div class="detail-header" style="margin-top:6px;">🧠 ANALISIS TAKTIS BOLA DARI AI:</div>
                <div class="detail-item ai-text">{item.get('aiAnalysisDetail', item.get('expertReason'))}</div>
            </div>
        </div>
        <div class="dash-line"></div>
        """

    html_content = f"""<!DOCTYPE html>
<html lang="id">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>FIXSCORE PARLAY RECEIPT</title>
    <style>
        * {{
            box-sizing: border-box;
            margin: 0;
            padding: 0;
            font-family: 'Courier New', Courier, monospace;
        }}
        body {{
            background-color: #f4f4f4;
            color: #000;
            display: flex;
            justify-content: center;
            padding: 20px 10px;
        }}
        .receipt {{
            background: #fff;
            width: 100%;
            max-width: 440px;
            padding: 20px 15px;
            border: 1px solid #ccc;
            box-shadow: 0 4px 10px rgba(0,0,0,0.05);
        }}
        .header {{
            text-align: center;
            margin-bottom: 15px;
        }}
        .header h1 {{
            font-size: 20px;
            font-weight: bold;
            letter-spacing: 2px;
            text-transform: uppercase;
        }}
        .header p {{
            font-size: 11px;
            color: #333;
        }}
        .dash-line {{
            border-bottom: 1px dashed #000;
            margin: 10px 0;
        }}
        .summary {{
            font-size: 12px;
            margin-bottom: 10px;
        }}
        .summary div {{
            display: flex;
            justify-content: space-between;
            margin-bottom: 3px;
        }}
        .item {{
            margin-bottom: 8px;
            font-size: 12px;
        }}
        .row {{
            display: flex;
            justify-content: space-between;
            font-weight: bold;
        }}
        .match {{
            text-align: right;
            max-width: 85%;
        }}
        .sub-info {{
            font-size: 10px;
            color: #444;
            margin-top: 2px;
        }}
        .pick-row {{
            margin-top: 4px;
            font-size: 12px;
            background: #eee;
            padding: 2px 4px;
        }}
        .notes {{
            font-size: 10px;
            color: #222;
            margin-top: 3px;
            font-style: italic;
        }}
        .btn-detail {{
            margin-top: 6px;
            width: 100%;
            background: #000;
            color: #fff;
            border: none;
            padding: 4px 0;
            font-size: 10px;
            font-family: inherit;
            cursor: pointer;
            text-transform: uppercase;
        }}
        .btn-detail:hover {{
            background: #333;
        }}
        .detail-box {{
            margin-top: 6px;
            padding: 6px;
            border: 1px solid #000;
            background: #fafafa;
            font-size: 10px;
        }}
        .detail-header {{
            font-weight: bold;
            text-decoration: underline;
            margin-bottom: 3px;
        }}
        .detail-item {{
            margin-bottom: 2px;
            word-wrap: break-word;
        }}
        .ai-text {{
            line-height: 1.3;
            color: #111;
        }}
        .footer {{
            text-align: center;
            font-size: 10px;
            margin-top: 15px;
            text-transform: uppercase;
        }}
    </style>
</head>
<body>
    <div class="receipt">
        <div class="header">
            <h1>FIXSCORE PARLAY</h1>
            <p>SENIOR HANDICAPPER ANALYSIS</p>
            <p>DATE: {updated_at}</p>
        </div>

        <div class="dash-line"></div>

        <div class="summary">
            <div><span>PARLAY 3 TOTAL ODDS:</span> <strong>@{data.get('parlay3_total_odds', '-')}</strong></div>
            <div><span>PARLAY 5 TOTAL ODDS:</span> <strong>@{data.get('parlay5_total_odds', '-')}</strong></div>
            <div><span>PARLAY 10 TOTAL ODDS:</span> <strong>@{data.get('parlay10_total_odds', '-')}</strong></div>
        </div>

        <div class="dash-line"></div>
        <div style="text-align:center; font-size:11px; font-weight:bold; margin-bottom:8px;">--- SELECTION LIST (TOP 10) ---</div>

        {items_html}

        <div class="footer">
            <p>*** USE RESPONSIBLY ***</p>
            <p>PERSONAL ANALYTICS SYSTEM</p>
        </div>
    </div>

    <script>
        function toggleDetail(id) {{
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

    with open(OUTPUT_HTML_PATH, "w", encoding="utf-8") as f:
        f.write(html_content)

    print(f"📄 Struk parlay interaktif berhasil digenerasi ke '{OUTPUT_HTML_PATH}'.")

if __name__ == "__main__":
    generate_receipt_html()
