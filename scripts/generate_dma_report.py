import os
import yfinance as yf
from datetime import datetime

REPORT_DIR = "/home/tonyho/workspace/invest/report"
OUTPUT_MD = os.path.join(REPORT_DIR, "dma_200_screen_results.md")
OUTPUT_HTML = os.path.join(REPORT_DIR, "dma_200_screen_results.html")

# Tickers already identified as curated in the report folder
tickers = sorted([
    d for d in os.listdir(REPORT_DIR)
    if os.path.isdir(os.path.join(REPORT_DIR, d))
    and not d.startswith(".")
])

below_200 = []
above_200 = []

print(f"Generating 200-DMA report for {len(tickers)} tickers...")

for ticker in tickers:
    try:
        data = yf.Ticker(ticker)
        hist = data.history(period="13mo")
        if hist.empty or len(hist) < 200:
            continue
            
        current = hist["Close"].iloc[-1]
        dma200 = hist["Close"].rolling(200).mean().iloc[-1]
        
        diff_pct = ((current / dma200) - 1) * 100
        
        info = {
            "ticker": ticker,
            "current": round(current, 2),
            "dma200": round(dma200, 2),
            "diff_pct": round(diff_pct, 1)
        }
        
        if current < dma200:
            below_200.append(info)
        else:
            above_200.append(info)
    except Exception as e:
        print(f"Error processing {ticker}: {e}")

# Sort by difference percentage
below_200.sort(key=lambda x: x["diff_pct"])
above_200.sort(key=lambda x: x["diff_pct"], reverse=True)

# Generate Markdown
md_content = f"""# Results — 200-DMA Screen
*Generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*

This report summarizes which mega-cap stocks in the portfolio are currently trading above or below their **200-Day Simple Moving Average (200-DMA)**.

## 🟢 Stocks Below 200-DMA (Value Candidates)
These stocks meet the "Cheap" screening criteria and are kept in the active report list.

| Ticker | Current Price | 200-DMA | % vs 200D |
| :--- | :--- | :--- | :--- |
"""
for item in below_200:
    md_content += f"| **{item['ticker']}** | ${item['current']:.2f} | ${item['dma200']:.2f} | {item['diff_pct']:+.1f}% |\n"

md_content += f"""
## 🔴 Stocks Above 200-DMA (Removed from Screen)
These stocks currently exceed the screening threshold and have been removed from the active analysis folder.

| Ticker | Current Price | 200-DMA | % vs 200D |
| :--- | :--- | :--- | :--- |
"""
for item in above_200:
    md_content += f"| **{item['ticker']}** | ${item['current']:.2f} | ${item['dma200']:.2f} | {item['diff_pct']:+.1f}% |\n"

with open(OUTPUT_MD, "w") as f:
    f.write(md_content)

# Generate HTML
html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>200-DMA Screen Results</title>
    <style>
        :root {{
            --primary: #2c3e50;
            --secondary: #34495e;
            --success: #27ae60;
            --danger: #c0392b;
            --light: #f8f9fa;
        }}
        body {{ font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; line-height: 1.6; max-width: 1000px; margin: 0 auto; padding: 40px; color: #333; background: #fff; }}
        h1 {{ border-bottom: 2px solid var(--primary); padding-bottom: 10px; color: var(--primary); }}
        h2 {{ margin-top: 40px; padding: 10px; border-radius: 4px; }}
        .header-below {{ background: #e8f5e9; color: var(--success); border-left: 5px solid var(--success); }}
        .header-above {{ background: #ffebee; color: var(--danger); border-left: 5px solid var(--danger); }}
        table {{ border-collapse: collapse; width: 100%; margin: 20px 0; box-shadow: 0 2px 15px rgba(0,0,0,0.1); border-radius: 8px; overflow: hidden; }}
        th, td {{ padding: 12px 15px; text-align: left; border-bottom: 1px solid #ddd; }}
        th {{ background-color: var(--secondary); color: white; text-transform: uppercase; font-size: 0.9em; }}
        tr:nth-child(even) {{ background-color: #f2f2f2; }}
        tr:hover {{ background-color: #e9ecef; }}
        .pct-neg {{ color: var(--success); font-weight: bold; }}
        .pct-pos {{ color: var(--danger); font-weight: bold; }}
        .footer {{ margin-top: 50px; font-size: 0.8em; color: #777; font-style: italic; }}
    </style>
</head>
<body>
    <h1>Results — 200-DMA Screen</h1>
    <p>Last Analysis: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>

    <h2 class="header-below">🟢 Stocks Below 200-DMA</h2>
    <table>
        <thead>
            <tr>
                <th>Ticker</th>
                <th>Current Price</th>
                <th>200-DMA</th>
                <th>% vs 200D</th>
            </tr>
        </thead>
        <tbody>
"""
for item in below_200:
    html_content += f"""
            <tr>
                <td><strong>{item['ticker']}</strong></td>
                <td>${item['current']:.2f}</td>
                <td>${item['dma200']:.2f}</td>
                <td class="pct-neg">{item['diff_pct']:+.1f}%</td>
            </tr>"""

html_content += """
        </tbody>
    </table>

    <h2 class="header-above">🔴 Stocks Above 200-DMA</h2>
    <table>
        <thead>
            <tr>
                <th>Ticker</th>
                <th>Current Price</th>
                <th>200-DMA</th>
                <th>% vs 200D</th>
            </tr>
        </thead>
        <tbody>
"""
for item in above_200:
    html_content += f"""
            <tr>
                <td><strong>{item['ticker']}</strong></td>
                <td>${item['current']:.2f}</td>
                <td>${item['dma200']:.2f}</td>
                <td class="pct-pos">{item['diff_pct']:+.1f}%</td>
            </tr>"""

html_content += f"""
        </tbody>
    </table>
    <p class="footer">Generated by Investment Analysis automated screening system. Rule: Current Price &lt; 200-Day SMA.</p>
</body>
</html>"""

with open(OUTPUT_HTML, "w") as f:
    f.write(html_content)

print("Report generation complete.")
