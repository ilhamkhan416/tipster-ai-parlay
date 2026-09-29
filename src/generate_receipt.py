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
            max-width: 420px;
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
        .footer {{
            text-align: center;
            font-size: 10px;
            margin-top: 15px;
            text-transform: uppercase;
        }}
        @media print {{
            body {{ background: #fff; padding: 0; }}
            .receipt {{ border: none; box-shadow: none; width: 100%; }}
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
</body>
</html>
"""

    with open(OUTPUT_HTML_PATH, "w", encoding="utf-8") as f:
        f.write(html_content)

    print(f"📄 Halaman struk parlay berhasil digenerasi ke '{OUTPUT_HTML_PATH}'.")

if __name__ == "__main__":
    generate_receipt_html()
