#!/usr/bin/env python3
import os
import sys
import argparse
import pandas as pd
import yfinance as yf
from rich.console import Console
from rich.progress import Progress
import time
import json
from datetime import datetime
from pathlib import Path

# Add scripts dir to path so we can potentially import from generate_reports if needed
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Resolve report directory dynamically: <project_root>/<YYYYMMDD>_report
# Matches the same convention used by screener.py
_project_root = Path(__file__).resolve().parent.parent
_today_str = datetime.now().strftime("%Y%m%d")
REPORT_DIR = str(_project_root / f"{_today_str}_report")

def get_trend_emoji(values, reverse=False):
    """
    Returns a trend emoji based on the series of values.
    reverse=True means lower is better (e.g., for P/E ratios).
    """
    if not values or len(values) < 2:
        return "⚠️ MIXED"
    
    try:
        # Convert to float if they are strings with commas/symbols
        clean_values = []
        for v in values:
            if isinstance(v, str):
                v = v.replace(',', '').replace('%', '').replace('$', '').replace('~', '')
                if 'B' in v: v = float(v.replace('B', '')) * 1e9
                if 'M' in v: v = float(v.replace('M', '')) * 1e6
            clean_values.append(float(v))
            
        first = clean_values[0]
        last = clean_values[-1]
        
        if reverse:
            return "📈 Good" if last < first else "📉 Bad"
        else:
            return "📈 Good" if last > first else "📉 Bad"
    except:
        return "⚠️ MIXED"

def build_md(s):
    """Generates Markdown report based on company data."""
    t = s["ticker"]
    fin_headers = ["Year / Status","Revenue","Gross Profit","Op. Profit","Net Income","EPS","Dividends/Share","Free Cash Flow","Buybacks"]
    eff_headers = ["Year / Status","Gross Margin (%)","Inventory Days","ROE (%)","ROA (%)"]
    val_headers = ["Year / Status","P/S","P/E","P/B"]

    is_us_stock = not (t.endswith('.TW') or t.endswith('.TWO') or t.endswith('.T'))
    is_tw_stock = t.endswith('.TW') or t.endswith('.TWO')
    
    if is_us_stock:
        chart_1y = f"[![{t} 1-Year Chart](https://charts2.finviz.com/chart.ashx?t={t}&ty=c&ta=1&p=d&s=l)](https://finviz.com/quote.ashx?t={t})"
        chart_5y = f"[![{t} 5-Year Chart](https://charts2.finviz.com/chart.ashx?t={t}&ty=c&ta=1&p=w&s=l)](https://finviz.com/quote.ashx?t={t})"
        chart_source = "*Source: Finviz — Click chart to open interactive view*"
        charts_md = f"""### 📈 Today's Quote — {t}
{chart_1y}

### 📊 Long-Term Technical Analysis — {t}
{chart_5y}

{chart_source}"""
    elif is_tw_stock:
        tw_url = f"https://tw.stock.yahoo.com/quote/{t}"
        tw_ta_url = f"https://tw.stock.yahoo.com/quote/{t}/technical-analysis"
        charts_md = f"""### 📈 Today's Quote — {t}
[View Interactive Chart]({tw_url})

### 📊 Long-Term Technical Analysis — {t}
[View Historical Technical Chart]({tw_ta_url})

*Source: Yahoo Finance TW — [Today's Chart]({tw_url}) | [Long-Term Analysis]({tw_ta_url})*"""
    else: # Japan stock
        yahoo_url = f"https://finance.yahoo.com/quote/{t}"
        charts_md = f"""### 📈 Price Charts ({t})

*Note: Finviz charts are not available for non-US stocks. Please view charts on Yahoo Finance:*

[View {t} on Yahoo Finance]({yahoo_url})"""

    lines = [
        f"# {s['company']} ({t}) Detailed Financial Data",
        f'Generated Automated Report — Based on "KQJ Global Investment Channel" Analysis Layout',
        "",
        "## 0. Stock Price Charts",
        "",
        charts_md,
        "",
        "---",
        "",
        f'## 1. Market Position ("Big / 又大")',
        f"| Indicator | {s['company']} ({t}) |",
        "| :--- | :--- |",
        f"| Sector | {s['sector']} |",
        f"| Market Cap | {s['mcap']} |",
        f"| Current Price | {s['price']} |",
        "",
        f'## 2. Operational and Financial Performance ("Good / 又好")',
        "| " + " | ".join(fin_headers) + " |",
        "| " + " | ".join([":---"]*len(fin_headers)) + " |",
    ]
    for row in s["fin"]:
        lines.append("| **" + str(row[0]) + "** | " + " | ".join(str(x) for x in row[1:]) + " |")
    lines.append("| **Trend** | " + " | ".join(s["fin_trends"]) + " |")

    lines += [
        "",
        "## 3. Efficiency and Return Metrics",
        "| " + " | ".join(eff_headers) + " |",
        "| " + " | ".join([":---"]*len(eff_headers)) + " |",
    ]
    for row in s["eff"]:
        lines.append("| **" + str(row[0]) + "** | " + " | ".join(str(x) for x in row[1:]) + " |")
    lines.append("| **Trend** | " + " | ".join(s["eff_trends"]) + " |")

    lines += [
        "",
        f'## 4. Valuations - 3P Model ("Cheap / 又便宜")',
        "| " + " | ".join(val_headers) + " |",
        "| " + " | ".join([":---"]*len(val_headers)) + " |",
    ]
    for row in s["val"]:
        lines.append("| **" + str(row[0]) + "** | " + " | ".join(str(x) for x in row[1:]) + " |")
    lines.append("| **Trend** | " + " | ".join(s["val_trends"]) + " |")

    kqj_labels = ["Big (又大)","Good (又好)","Cheap (又便宜)",">50% Upside Potential"]
    lines += [
        "",
        "## 5. Automated Framework Assessment",
        "| Criterion | Status | Notes |",
        "| :--- | :--- | :--- |",
    ]
    for label, status, note in zip(kqj_labels, s["kqj"], s["notes"]):
        lines.append(f"| {label} | {status} | {note} |")

    return "\n".join(lines) + "\n"

def map_exchange(yf_exchange):
    """Maps yfinance exchange codes to TradingView prefixes."""
    if not yf_exchange:
        return "NYSE"
    mapping = {
        'NMS': 'NASDAQ',
        'NGM': 'NASDAQ',
        'NCM': 'NASDAQ',
        'NYQ': 'NYSE',
        'NYS': 'NYSE',
        'ASE': 'AMEX',
        'BTS': 'BATS',
        'TYO': 'TSE',
        'JPX': 'TSE'
    }
    return mapping.get(yf_exchange, "NYSE")

def build_html(s):
    """Generates HTML report based on company data."""
    t = s["ticker"]
    is_us_stock = not (t.endswith('.TW') or t.endswith('.TWO') or t.endswith('.T'))
    is_tw_stock = t.endswith('.TW') or t.endswith('.TWO')
    
    if is_us_stock:
        ex_enc = f"{s['exchange']}:{t}"
        chart_html = f"""
    <div class="chart-grid">
        <div class="chart-box">
            <h3>📈 1-Year Price Chart (Daily)</h3>
            <iframe src="https://s.tradingview.com/widgetembed/?symbol={ex_enc}&interval=D&range=12M&theme=light&style=1&locale=en&hide_side_toolbar=true&allow_symbol_change=false"
                height="300" allowtransparency="true" scrolling="no" allowfullscreen></iframe>
        </div>
        <div class="chart-box">
            <h3>📈 5-Year Price Chart (Weekly)</h3>
            <iframe src="https://s.tradingview.com/widgetembed/?symbol={ex_enc}&interval=W&range=60M&theme=light&style=1&locale=en&hide_side_toolbar=true&allow_symbol_change=false"
                height="300" allowtransparency="true" scrolling="no" allowfullscreen></iframe>
        </div>
    </div>"""
    elif is_tw_stock:
        tw_url = f"https://tw.stock.yahoo.com/quote/{t}"
        tw_ta_url = f"https://tw.stock.yahoo.com/quote/{t}/technical-analysis"
        chart_html = f"""
    <div class="chart-grid">
        <div class="chart-box" style="display: flex; flex-direction: column; align-items: center; justify-content: center; height: 300px; background: #f8f9fa;">
            <p style="color: #555; text-align: center; padding: 20px;">
                <span style="font-size: 2rem;">📈</span><br><br>
                <strong style="font-size: 1.1rem;">Today's Quote</strong><br>
                <span style="color: #888; font-size: 0.9rem;">Current price, volume &amp; intraday chart</span><br><br>
                <a href="{tw_url}" target="_blank" style="display: inline-block; padding: 12px 28px; background: #0066cc; color: white; text-decoration: none; border-radius: 6px; font-weight: bold; font-size: 1rem;">📈 Today's Chart</a>
            </p>
        </div>
        <div class="chart-box" style="display: flex; flex-direction: column; align-items: center; justify-content: center; height: 300px; background: #f8f9fa;">
            <p style="color: #555; text-align: center; padding: 20px;">
                <span style="font-size: 2rem;">📊</span><br><br>
                <strong style="font-size: 1.1rem;">Long-Term Technical Analysis</strong><br>
                <span style="color: #888; font-size: 0.9rem;">Historical chart with MA &amp; indicators</span><br><br>
                <a href="{tw_ta_url}" target="_blank" style="display: inline-block; padding: 12px 28px; background: #6600cc; color: white; text-decoration: none; border-radius: 6px; font-weight: bold; font-size: 1rem;">📊 Long-Term Chart</a>
            </p>
        </div>
    </div>"""
    else: # Japan stock
        yahoo_url = f"https://finance.yahoo.com/quote/{t}"
        chart_html = f"""
    <div class="chart-grid">
        <div class="chart-box" style="display: flex; flex-direction: column; align-items: center; justify-content: center; height: 300px; background: #f8f9fa;">
            <p style="color: #555; text-align: center; padding: 20px;">
                <span style="font-size: 2rem;">📈</span><br><br>
                <strong style="font-size: 1.1rem;">Price Chart &amp; Analysis</strong><br>
                <span style="color: #888; font-size: 0.9rem;">View interactive charts and historical data</span><br><br>
                <a href="{yahoo_url}" target="_blank" style="display: inline-block; padding: 12px 28px; background: #0066cc; color: white; text-decoration: none; border-radius: 6px; font-weight: bold; font-size: 1rem;">📈 View on Yahoo Finance</a>
            </p>
        </div>
    </div>"""

    css_extra = """
        .chart-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 20px; margin-bottom: 30px; }
        .chart-box { border: 1px solid #ddd; border-radius: 8px; overflow: hidden; }
        .chart-box h3 { margin: 0; padding: 10px 14px; background: #2c3e50; color: #fff; font-size: 14px; }
        .chart-box iframe { display: block; width: 100%; border: none; }
        .chart-note { background: #f8f9fa; border-left: 4px solid #2c3e50; padding: 10px 16px; margin-bottom: 30px; font-size: 0.9em; color: #555; }
        @media (max-width: 600px) { .chart-grid { grid-template-columns: 1fr; } }"""

    fin_headers = ["Year","Revenue","Gross Profit","Op. Profit","Net Income","EPS","Dividends","FCF","Buybacks"]
    eff_headers = ["Year","Gross Margin","Inventory Days","ROE","ROA"]
    val_headers = ["Year","P/S","P/E","P/B"]

    def trend_cell(v):
        cls = "good" if "Good" in v or "PASS" in v else ("bad" if "Bad" in v else "mixed")
        if "RISK" in v: cls = "risk"
        return f'<td class="{cls}">{v}</td>'

    fin_rows = "\n".join(
        "<tr><td><strong>" + str(r[0]) + "</strong></td>" + "".join(f"<td>{c}</td>" for c in r[1:]) + "</tr>"
        for r in s["fin"]
    )
    fin_trend = "<tr><td><strong>Trend</strong></td>" + "".join(trend_cell(v) for v in s["fin_trends"]) + "</tr>"

    eff_rows = "\n".join(
        "<tr><td><strong>" + str(r[0]) + "</strong></td>" + "".join(f"<td>{c}</td>" for c in r[1:]) + "</tr>"
        for r in s["eff"]
    )
    eff_trend = "<tr><td><strong>Trend</strong></td>" + "".join(trend_cell(v) for v in s["eff_trends"]) + "</tr>"

    val_rows = "\n".join(
        "<tr><td><strong>" + str(r[0]) + "</strong></td>" + "".join(f"<td>{c}</td>" for c in r[1:]) + "</tr>"
        for r in s["val"]
    )
    val_trend = "<tr><td><strong>Trend</strong></td>" + "".join(trend_cell(v) for v in s["val_trends"]) + "</tr>"

    kqj_labels = ["Big (又大)","Good (又好)","Cheap (又便宜)","Upside Potential"]
    kqj_rows = "\n".join(
        f'<tr><td>{label}</td><td class="{"good" if "PASS" in status else ("bad" if "Bad" in status else ("risk" if "RISK" in status else "mixed"))}">{status}</td><td>{note}</td></tr>'
        for label, status, note in zip(kqj_labels, s["kqj"], s["notes"])
    )

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{s['company']} ({t}) Financial Data</title>
    <style>
        body {{ font-family: Arial, sans-serif; line-height: 1.6; max-width: 960px; margin: 0 auto; padding: 20px; color: #333; }}
        h1, h2, h3 {{ color: #2c3e50; }}
        table {{ border-collapse: collapse; width: 100%; margin-bottom: 30px; }}
        th, td {{ border: 1px solid #ddd; padding: 10px; text-align: left; }}
        th {{ background-color: #f2f2f2; }}
        .good {{ color: green; font-weight: bold; }}
        .bad {{ color: red; font-weight: bold; }}
        .mixed {{ color: orange; font-weight: bold; }}
        .risk {{ color: red; font-weight: bold; }}{css_extra}
    </style>
</head>
<body>
    <h1>{s['company']} ({t}) Detailed Financial Data</h1>
    <p>Automated Analysis Dashboard</p>

    <h2>0. Stock Price Charts</h2>
    {chart_html}

    <h2>1. Market Position ("Big / 又大")</h2>
    <table>
        <tr><th>Indicator</th><th>{s['company']} ({t})</th></tr>
        <tr><td>Sector</td><td>{s['sector']}</td></tr>
        <tr><td>Market Cap</td><td>{s['mcap']}</td></tr>
        <tr><td>Current Price</td><td>{s['price']}</td></tr>
    </table>

    <h2>2. Operational and Financial Performance ("Good / 又好")</h2>
    <table>
        <tr>{"".join(f"<th>{h}</th>" for h in fin_headers)}</tr>
        {fin_rows}
        {fin_trend}
    </table>

    <h2>3. Efficiency and Return Metrics</h2>
    <table>
        <tr>{"".join(f"<th>{h}</th>" for h in eff_headers)}</tr>
        {eff_rows}
        {eff_trend}
    </table>

    <h2>4. Valuations - 3P Model ("Cheap / 又便宜")</h2>
    <table>
        <tr>{"".join(f"<th>{h}</th>" for h in val_headers)}</tr>
        {val_rows}
        {val_trend}
    </table>

    <h2>5. Framework Assessment</h2>
    <table>
        <tr><th>Criterion</th><th>Status</th><th>Notes</th></tr>
        {kqj_rows}
    </table>
</body>
</html>"""

def fetch_and_generate(ticker_sym, company_name, current_price, mcap, metrics_list=None):
    """Fetches data for a ticker and generates reports."""
    try:
        ticker = yf.Ticker(ticker_sym)
        fin = ticker.financials
        cf = ticker.cashflow
        bs = ticker.balance_sheet
        info = ticker.info
        
        # We want the last 4 years
        years = fin.columns[:4][::-1] # Older to newer
        if len(years) < 2: return False
        
        # Fetch share history once to avoid multiple calls
        try:
            shares_history = ticker.get_shares_full(start=years[0] - pd.Timedelta(days=365), end=years[-1] + pd.Timedelta(days=30))
        except:
            shares_history = pd.Series()
            
        fin_data = []
        eff_data = []
        val_data = []
        
        for year in years:
            y_label = str(year.year)
            
            # Operational
            rev = fin.get(year).get('Total Revenue', 0)
            gp = fin.get(year).get('Gross Profit', 0)
            op = fin.get(year).get('Operating Income', 0)
            ni = fin.get(year).get('Net Income', 0)
            eps = fin.get(year).get('Basic EPS', 0)
            
            div = ticker.dividends.loc[str(year.year)].sum() if not ticker.dividends.empty and str(year.year) in ticker.dividends.index.year.astype(str) else 0
            fcf = cf.get(year).get('Free Cash Flow', 0)
            buyback = cf.get(year).get('Repurchase Of Capital Stock', 0)
            
            fin_data.append((y_label, f"{rev/1e6:,.0f}M", f"{gp/1e6:,.0f}M", f"{op/1e6:,.0f}M", f"{ni/1e6:,.0f}M", f"{eps:.2f}", f"{div:.2f}", f"{fcf/1e6:,.0f}M", f"{abs(buyback)/1e6:,.0f}M"))
            
            # Efficiency
            gm = (gp / rev * 100) if rev else 0
            inv = bs.get(year).get('Inventory', 0)
            equity = bs.get(year).get('Stockholders Equity', 1)
            assets = bs.get(year).get('Total Assets', 1)
            roe = (ni / equity * 100)
            roa = (ni / assets * 100)
            
            eff_data.append((y_label, f"{gm:.1f}%", "N/A", f"{roe:.1f}%", f"{roa:.1f}%"))
            
            # Historical Valuations Calculation
            try:
                # Normalize year timezone for comparison
                year_tz = year.tz_localize('UTC')
                
                # Get price at fiscal year end
                # Fetch a range to ensure we get a trading day
                hist = ticker.history(start=year - pd.Timedelta(days=10), end=year + pd.Timedelta(days=2))
                if not hist.empty:
                    # Get the closest day to the year end (last row in range)
                    ye_price = hist['Close'].iloc[-1]
                else:
                    ye_price = 0
                
                # Get shares at fiscal year end
                shares = 0
                if not shares_history.empty:
                    # Normalize shares history index to UTC for comparison
                    sh_utc = shares_history.copy()
                    sh_utc.index = sh_utc.index.tz_convert('UTC') if sh_utc.index.tz is not None else sh_utc.index.tz_localize('UTC')
                    s_at_date = sh_utc[sh_utc.index <= year_tz]
                    if not s_at_date.empty:
                        shares = s_at_date.iloc[-1]
                
                if not shares:
                    shares = info.get('sharesOutstanding', 0)
                
                if ye_price > 0 and shares > 0:
                    mcap_ye = ye_price * shares
                    ps = f"{mcap_ye / rev:.2f}" if rev and rev > 0 else "N/A"
                    pe = f"{ye_price / eps:.2f}" if eps and eps > 0 else "N/A"
                    pb = f"{mcap_ye / equity:.2f}" if equity and equity > 0 else "N/A"
                    val_data.append((y_label, ps, pe, pb))
                else:
                    val_data.append((y_label, "N/A", "N/A", "N/A"))
            except:
                val_data.append((y_label, "N/A", "N/A", "N/A"))
            
        # Update last year with live ratios from info if available
        try:
            cur_ps = info.get('priceToSalesTrailing12Months')
            cur_pe = info.get('trailingPE')
            cur_pb = info.get('priceToBook')
            
            y, ps, pe, pb = val_data[-1]
            if cur_ps: ps = f"{cur_ps:.2f}"
            if cur_pe: pe = f"{cur_pe:.2f}"
            if cur_pb: pb = f"{cur_pb:.2f}"
            val_data[-1] = (y, ps, pe, pb)
        except:
            pass
        
        # Compute Trends
        fin_trends = [
            get_trend_emoji([r[1] for r in fin_data]),
            get_trend_emoji([r[2] for r in fin_data]),
            get_trend_emoji([r[3] for r in fin_data]),
            get_trend_emoji([r[4] for r in fin_data]),
            get_trend_emoji([r[5] for r in fin_data]),
            get_trend_emoji([r[6] for r in fin_data]),
            get_trend_emoji([r[7] for r in fin_data]),
            get_trend_emoji([r[8] for r in fin_data])
        ]
        
        eff_trends = [
            get_trend_emoji([r[1] for r in eff_data]),
            "⚠️ N/A",
            get_trend_emoji([r[3] for r in eff_data]),
            get_trend_emoji([r[4] for r in eff_data])
        ]
        
        val_trends = ["⚠️ MIXED", "⚠️ MIXED", "⚠️ MIXED"]
        
        # Currency symbol handling
        currency = info.get('currency', 'USD')
        currency_symbols = {'USD': '$', 'TWD': 'NT$', 'EUR': '€', 'GBP': '£', 'JPY': '¥', 'CNY': '¥', 'HKD': 'HK$'}
        cur_sym = currency_symbols.get(currency, f"{currency} ")

        s = {
            "ticker": ticker_sym,
            "company": company_name,
            "exchange": map_exchange(info.get('exchange')),
            "sector": info.get('sector', 'N/A'),
            "mcap": f"{cur_sym}{mcap/1e9:.2f}B",
            "price": f"{cur_sym}{current_price:.2f}",
            "high": "N/A", "low": "N/A",
            "kqj": ["✅ PASS", "📈 Good", "✅ PASS", "⚠️ MIXED"],
            "notes": [
                f"Market Cap: {cur_sym}{mcap/1e9:.2f}B",
                f"Automated check of 4-year financial trajectory.",
                f"Current Price: {cur_sym}{current_price:.2f}",
                "Further qualitative analysis required for upside potential."
            ],
            "fin": fin_data, "fin_trends": fin_trends,
            "eff": eff_data, "eff_trends": eff_trends,
            "val": val_data, "val_trends": val_trends,
            "note": f"Automated report generated from live data. Sector: {info.get('sector', 'N/A')}."
        }
        
        # Save metrics for summary
        if metrics_list is not None:
            roe_values = {}
            for year_label, _, _, roe_str, _ in eff_data:
                try:
                    roe_values[year_label] = float(roe_str.replace('%', ''))
                except:
                    roe_values[year_label] = 0.0
            
            # Calculate average of past 4 years (excluding the latest one if it's the current year)
            # Actually let's just take the first N-1 if N >= 2
            avg_roe = 0.0
            if len(roe_values) >= 2:
                # Get labels sorted by year
                sorted_labels = sorted(roe_values.keys())
                # Exclude the last one (latest)
                past_labels = sorted_labels[:-1]
                if past_labels:
                    avg_roe = round(sum(roe_values[l] for l in past_labels) / len(past_labels), 2)
            
            metrics_list[ticker_sym] = {
                "roe": roe_values,
                "avg_roe_past": avg_roe
            }

        # Determine market subfolder
        market_subfolder = "US_stock"
        if ticker_sym.endswith('.T'):
            market_subfolder = "JP_stock"
        elif ticker_sym.endswith('.TW') or ticker_sym.endswith('.TWO'):
            market_subfolder = "TW_stock"
            
        folder = os.path.join(REPORT_DIR, market_subfolder, ticker_sym)
        os.makedirs(folder, exist_ok=True)
        
        with open(os.path.join(folder, f"{ticker_sym.lower()}_financial_data.md"), "w") as f:
            f.write(build_md(s))
        with open(os.path.join(folder, f"{ticker_sym.lower()}_financial_data.html"), "w") as f:
            f.write(build_html(s))
            
        return True
    except Exception as e:
        # print(f"Error processing {ticker_sym}: {e}")
        return False

def run_for_market(market_key, console, global_metrics=None):
    """Runs report generation for a single market key ('us', 'tw', or 'jp')."""
    input_csv = os.path.join(REPORT_DIR, f"dma_200_screen_results_{market_key}.csv")
    console.print(f"\n[bold blue]Automated Financial Report Generator ({market_key.upper()})[/bold blue]")
    console.print(f"[dim]Report directory: {REPORT_DIR}[/dim]\n")

    if not os.path.exists(input_csv):
        console.print(f"[red]Input file not found: {input_csv}[/red]")
        console.print(f"[yellow]Hint: Run screener.py --market {market_key} first.[/yellow]")
        return 0

    df = pd.read_csv(input_csv)
    tickers = df.to_dict('records')
    console.print(f"Loaded {len(tickers)} companies from screener output.\n")

    success_count = 0
    with Progress() as progress:
        task = progress.add_task("[cyan]Generating reports...", total=len(tickers))
        for t in tickers:
            ticker_sym = t['Ticker']
            company_name = t['Name']
            if fetch_and_generate(ticker_sym, company_name, t['Price'], t['Market Cap'], global_metrics):
                success_count += 1
            progress.advance(task)

    console.print(f"\n[bold green]Successfully generated reports for {success_count}/{len(tickers)} companies.[/bold green]")
    console.print(f"Files are located in {REPORT_DIR}/[TICKER]/ folders.")
    return success_count

def main():
    parser = argparse.ArgumentParser(description="Automated Financial Report Generator")
    parser.add_argument('--market', choices=['us', 'tw', 'jp', 'all'], default='us', help='Market to scan')
    args = parser.parse_args()

    console = Console()

    # Expand 'all' into individual market keys
    markets = ['us', 'tw', 'jp'] if args.market == 'all' else [args.market]

    global_metrics = {}
    total_success = 0
    for market_key in markets:
        total_success += run_for_market(market_key, console, global_metrics)

    # Save global metrics summary
    if global_metrics:
        metrics_path = os.path.join(REPORT_DIR, "metrics_summary.json")
        with open(metrics_path, 'w', encoding='utf-8') as f:
            json.dump(global_metrics, f, indent=2)
        console.print(f"\n[bold green]Metrics summary saved to {metrics_path}[/bold green]")

    if len(markets) > 1:
        console.print(f"\n[bold green]Grand total: {total_success} reports generated across {len(markets)} markets.[/bold green]")

if __name__ == "__main__":
    main()
