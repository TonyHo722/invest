#!/usr/bin/env python3
import requests
import pandas as pd
import yfinance as yf
from bs4 import BeautifulSoup
from rich.console import Console
from rich.table import Table
from rich.progress import Progress
import time
import argparse
import urllib.request
import ssl
import re
import os
from datetime import datetime
from pathlib import Path

def get_sp500_tickers():
    """Fetches S&P 500 tickers from Wikipedia."""
    url = "https://en.wikipedia.org/wiki/List_of_S%26P_500_companies"
    return fetch_wikipedia_tickers(url, "constituents")

def get_nasdaq100_tickers():
    """Fetches NASDAQ-100 tickers from Wikipedia."""
    url = "https://en.wikipedia.org/wiki/Nasdaq-100"
    return fetch_wikipedia_tickers(url, "constituents")

def get_all_jp_tickers():
    """Fetches large-cap Japanese tickers from the iShares MSCI Japan ETF (EWJ) holdings.
    Returns tickers with the Yahoo Finance .T suffix.
    """
    url = "https://www.ishares.com/us/products/239665/ishares-msci-japan-etf/1467271812596.ajax?fileType=csv&fileName=EWJ_holdings&dataType=fund"
    try:
        headers = {'User-Agent': 'Mozilla/5.0'}
        response = requests.get(url, headers=headers, timeout=10)
        tickers = []
        for line in response.text.splitlines():
            parts = line.split(',')
            if parts:
                first_col = parts[0].replace('"', '').strip()
                if re.fullmatch(r"\d{4}", first_col):
                    tickers.append(first_col + '.T')
        return list(set(tickers))
    except Exception as e:
        print(f"Error fetching JP tickers from EWJ: {e}")
        return []

def get_tw_tickers(market_type='all'):
    """Fetches TWSE and TPEx tickers and their Chinese names from TWSE ISIN."""
    tickers = {}
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE
    
    modes = []
    if market_type in ['twse', 'all']:
        modes.append(('2', '.TW'))
    if market_type in ['tpex', 'all']:
        modes.append(('4', '.TWO'))
        
    for mode, suffix in modes:
        url = f'https://isin.twse.com.tw/isin/C_public.jsp?strMode={mode}'
        try:
            req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
            html = urllib.request.urlopen(req, context=ctx).read().decode('cp950', errors='ignore')
            soup = BeautifulSoup(html, 'html.parser')
            for row in soup.find_all('tr'):
                cells = row.find_all('td')
                if len(cells) > 0:
                    text = cells[0].text.strip()
                    match = re.match(r'^(\d{4})\s+(.+)', text)
                    if match:
                        ticker = match.group(1) + suffix
                        name = match.group(2).strip()
                        tickers[ticker] = name
        except Exception as e:
            print(f"Error fetching TW tickers for mode {mode}: {e}")
    return tickers

def fetch_wikipedia_tickers(url, table_id):
    """Generic helper to fetch tickers from a Wikipedia table."""
    try:
        headers = {'User-Agent': 'Mozilla/5.0'}
        response = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(response.text, 'html.parser')
        table = soup.find('table', {'id': table_id})
        tickers = []
        for row in table.find_all('tr')[1:]:
            cells = row.find_all('td')
            if not cells:
                continue
            ticker = cells[0].text.strip()
            # Handle stocks like BRK.B or GOOGL (duplicates/classes)
            ticker = ticker.replace('.', '-')
            # Sometimes tickers have extra info or whitespace
            ticker = ticker.split()[0] 
            tickers.append(ticker)
        return list(set(tickers)) # Unique tickers only
    except Exception as e:
        print(f"Error fetching tickers from {url}: {e}")
        return []

def screen_stocks(tickers, names_map=None, min_mcap_usd_billion=10, min_mcap_twd_billion=10, min_mcap_jpy_billion=100):
    """
    Screens tickers for Price < 200-DMA and Market Cap > min_mcap_billion.
    Optimized by fetching technicals in batch before checking fundamentals.
    """
    results = []
    console = Console()
    
    console.print(f"[cyan]Downloading historical data for {len(tickers)} tickers in chunks...[/cyan]")
    data_frames = []
    chunk_size = 20
    
    with Progress() as progress:
        task = progress.add_task("[yellow]Downloading data...", total=len(tickers))
        for i in range(0, len(tickers), chunk_size):
            chunk = tickers[i:i+chunk_size]
            try:
                df_chunk = yf.download(chunk, period="1y", interval="1d", group_by='ticker', progress=False, threads=True)
                if not df_chunk.empty:
                    data_frames.append(df_chunk)
            except Exception:
                pass
            progress.advance(task, advance=len(chunk))
            time.sleep(1) # Be nice to Yahoo Finance API

    if not data_frames:
        console.print("[red]Error: Could not download any data. You may be rate-limited by Yahoo Finance.[/red]")
        return []

    data = pd.concat(data_frames, axis=1)

    # Filter candidates based on 200-DMA first (Fast)
    candidates = []
    for ticker_sym in tickers:
        try:
            if ticker_sym not in data.columns.levels[0]:
                continue
                
            ticker_hist = data[ticker_sym].dropna()
            if len(ticker_hist) < 200:
                continue
            
            dma200 = ticker_hist['Close'].rolling(window=200).mean().iloc[-1]
            current_price = ticker_hist['Close'].iloc[-1]
            
            if current_price < dma200:
                candidates.append({
                    'symbol': ticker_sym,
                    'price': current_price,
                    'dma200': dma200
                })
        except Exception:
            continue

    console.print(f"[green]Found {len(candidates)} candidates below 200-DMA. Checking Market Caps...[/green]")

    # Check Market Cap for candidates (Slow but only for a small set)
    with Progress() as progress:
        task = progress.add_task("[yellow]Querying Market Caps...", total=len(candidates))
        
        for c in candidates:
            try:
                t = yf.Ticker(c['symbol'])
                info = t.info
                mcap = info.get('marketCap', 0)
                currency = info.get('currency', 'USD')
                
                if currency == 'TWD':
                    threshold = min_mcap_twd_billion * 1e9
                elif currency == 'JPY':
                    threshold = min_mcap_jpy_billion * 1e9
                else:
                    threshold = min_mcap_usd_billion * 1e9
                
                if mcap >= threshold:
                    pct_diff = ((c['price'] / c['dma200']) - 1) * 100
                    company_name = info.get('shortName', c['symbol'])
                    if names_map and c['symbol'] in names_map:
                        company_name = f"{company_name} ({names_map[c['symbol']]})"
                    results.append({
                        'Ticker': c['symbol'],
                        'Name': company_name,
                        'Market Cap': mcap,
                        'Currency': currency,
                        'Price': c['price'],
                        '200-DMA': c['dma200'],
                        '% Diff': pct_diff
                    })
            except Exception:
                pass
            progress.advance(task)
            
    return results

def main():
    parser = argparse.ArgumentParser(description="Mega-Cap 200-DMA Screener")
    parser.add_argument('--market', choices=['us', 'tw', 'jp', 'all'], default='us', help='Market to scan')
    parser.add_argument('--min-mcap-jpy', type=float, default=100, help='Minimum market cap in billions of JPY (default 100)')
    args = parser.parse_args()

    console = Console()
    console.print(f"[bold blue]Mega-Cap 200-DMA Screener ({args.market.upper()})[/bold blue]\n")
    
    start_time = time.time()
    
    tickers = []
    if args.market in ['us', 'all']:
        sp500_tickers = get_sp500_tickers()
        nasdaq_tickers = get_nasdaq100_tickers()
        tickers.extend(sp500_tickers)
        tickers.extend(nasdaq_tickers)
        console.print(f"Fetched {len(sp500_tickers)} S&P 500 and {len(nasdaq_tickers)} NASDAQ-100 tickers.")
        
    tw_names_map = {}
    if args.market in ['tw', 'all']:
        tw_tickers_dict = get_tw_tickers()
        tw_names_map = tw_tickers_dict
        tickers.extend(tw_tickers_dict.keys())
        console.print(f"Fetched {len(tw_tickers_dict)} TWSE/TPEx tickers.")

    if args.market in ['jp', 'all']:
        jp_tickers = get_all_jp_tickers()
        tickers.extend(jp_tickers)
        console.print(f"Fetched {len(jp_tickers)} JP tickers.")
    
    # Merge and remove duplicates
    tickers = list(set(tickers))
    
    if not tickers:
        console.print("[red]Could not fetch tickers from any source. Exiting.[/red]")
        return
        
    console.print(f"Unique tickers to scan: [bold cyan]{len(tickers)}[/bold cyan]\n")
    
    matches = screen_stocks(tickers, tw_names_map, min_mcap_jpy_billion=args.min_mcap_jpy)
    
    if not matches:
        console.print("[yellow]No companies match the criteria.[/yellow]")
    else:
        table = Table(title="Screening Results")
        table.add_column("Ticker", style="cyan")
        table.add_column("Name", style="white")
        table.add_column("Market Cap", justify="right")
        table.add_column("Price", justify="right")
        table.add_column("200-DMA", justify="right")
        table.add_column("% Diff", justify="right")

        for m in sorted(matches, key=lambda x: x['% Diff']):
            divisor = 1e9
            table.add_row(
                m['Ticker'],
                m['Name'],
                f"{m['Market Cap']/divisor:.2f}B {m['Currency']}",
                f"{m['Price']:.2f} {m['Currency']}",
                f"{m['200-DMA']:.2f} {m['Currency']}",
                f"[red]{m['% Diff']:.2f}%[/red]"
            )

        console.print(table)
        
        # Resolve output directory
        project_root = Path(__file__).resolve().parent.parent
        today_str = datetime.now().strftime("%Y%m%d")
        report_dir = project_root / f"{today_str}_report"
        report_dir.mkdir(parents=True, exist_ok=True)
        console.print(f"[dim]Output directory: {report_dir}[/dim]")

        # Save results to a CSV
        try:
            df = pd.DataFrame(matches)
            csv_path = report_dir / f"dma_200_screen_results_{args.market}.csv"
            df.to_csv(csv_path, index=False)
            console.print(f"\n[bold green]Results saved to {csv_path}[/bold green]")
        except Exception as e:
            console.print(f"\n[red]Could not save CSV: {e}[/red]")
            
        # Generate Premium HTML Report
        try:
            html_path = report_dir / f"dma_200_screen_results_{args.market}.html"
            html_template = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Screener: Mega-Cap Value ({args.market.upper()})</title>
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;600;700&family=Plus+Jakarta+Sans:wght@300;400;600;700&display=swap" rel="stylesheet">
    <style>
        :root {{
            --bg: #0f172a;
            --card-bg: rgba(30, 41, 59, 0.7);
            --primary: #38bdf8;
            --accent: #818cf8;
            --text-main: #f1f5f9;
            --text-dim: #94a3b8;
            --success: #4ade80;
            --danger: #f87171;
            --border: rgba(255, 255, 255, 0.1);
        }}
        
        * {{ box-sizing: border-box; }}
        body {{
            background-color: var(--bg);
            background-image: 
                radial-gradient(at 0% 0%, rgba(56, 189, 248, 0.15) 0px, transparent 50%),
                radial-gradient(at 100% 100%, rgba(129, 140, 248, 0.15) 0px, transparent 50%);
            color: var(--text-main);
            font-family: 'Plus Jakarta Sans', sans-serif;
            margin: 0;
            padding: 40px 20px;
            min-height: 100vh;
        }}
        
        .container {{
            max-width: 1200px;
            margin: 0 auto;
        }}
        
        header {{
            text-align: center;
            margin-bottom: 60px;
        }}
        
        h1 {{
            font-family: 'Outfit', sans-serif;
            font-size: 3rem;
            font-weight: 700;
            margin-bottom: 10px;
            background: linear-gradient(to right, var(--primary), var(--accent));
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }}
        
        .subtitle {{
            color: var(--text-dim);
            font-size: 1.1rem;
            letter-spacing: 0.05em;
        }}

        .stats-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin-bottom: 40px;
        }}
        
        .stat-card {{
            background: var(--card-bg);
            backdrop-filter: blur(12px);
            border: 1px solid var(--border);
            padding: 24px;
            border-radius: 16px;
            text-align: center;
        }}
        
        .stat-value {{ font-size: 2rem; font-weight: 700; color: var(--primary); }}
        .stat-label {{ color: var(--text-dim); font-size: 0.9rem; margin-top: 4px; }}

        .table-container {{
            background: var(--card-bg);
            backdrop-filter: blur(12px);
            border: 1px solid var(--border);
            border-radius: 20px;
            overflow: hidden;
            box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.5);
        }}
        
        table {{
            width: 100%;
            border-collapse: collapse;
            font-size: 0.95rem;
        }}
        
        th {{
            background: rgba(255, 255, 255, 0.05);
            padding: 18px 24px;
            text-align: left;
            font-weight: 600;
            color: var(--text-dim);
            text-transform: uppercase;
            font-size: 0.75rem;
            letter-spacing: 0.1em;
            border-bottom: 1px solid var(--border);
        }}
        
        td {{
            padding: 16px 24px;
            border-bottom: 1px solid var(--border);
        }}
        
        tr:last-child td {{ border-bottom: none; }}
        
        tr:hover {{
            background: rgba(255, 255, 255, 0.03);
            transition: background 0.2s ease;
        }}
        
        .ticker-badge {{
            background: linear-gradient(45deg, var(--primary), var(--accent));
            color: #000;
            font-weight: 800;
            padding: 4px 10px;
            border-radius: 6px;
            font-size: 0.85rem;
            display: inline-block;
        }}
        
        .price {{ font-family: 'Outfit', sans-serif; font-weight: 600; }}
        .mcap {{ color: var(--text-dim); }}
        .pct-neg {{ color: var(--success); font-weight: 700; }}
        
        .footer {{
            text-align: center;
            margin-top: 60px;
            color: var(--text-dim);
            font-size: 0.85rem;
        }}

        @media (max-width: 768px) {{
            h1 {{ font-size: 2rem; }}
            .mcap, .dma-col {{ display: none; }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>Market Value Screener</h1>
            <p class="subtitle">Mega-Cap ({args.market.upper()}) Below 200-DMA</p>
        </header>
        
        <div class="stats-grid">
            <div class="stat-card">
                <div class="stat-value">{len(matches)}</div>
                <div class="stat-label">Companies Found</div>
            </div>
            <div class="stat-card">
                <div class="stat-value">> $10B</div>
                <div class="stat-label">Market Cap Filter</div>
            </div>
            <div class="stat-card">
                <div class="stat-value">200-DMA</div>
                <div class="stat-label">Technical Level</div>
            </div>
        </div>

        <div class="table-container">
            <table>
                <thead>
                    <tr>
                        <th>Ticker</th>
                        <th>Company Name</th>
                        <th class="mcap" style="text-align: right">Market Cap</th>
                        <th style="text-align: right">Price</th>
                        <th class="dma-col" style="text-align: right">200-DMA</th>
                        <th style="text-align: right">% Discount</th>
                    </tr>
                </thead>
                <tbody>
                    {"".join([f'''
                    <tr>
                        <td><span class="ticker-badge">{m['Ticker']}</span></td>
                        <td>{m['Name']}</td>
                        <td class="mcap" style="text-align: right">{m['Market Cap']/1e9:.2f}B {m['Currency']}</td>
                        <td class="price" style="text-align: right">{m['Price']:.2f} {m['Currency']}</td>
                        <td class="dma-col price" style="text-align: right; color: #94a3b8">{m['200-DMA']:.2f} {m['Currency']}</td>
                        <td class="pct-neg" style="text-align: right">{m['% Diff']:.2f}%</td>
                    </tr>''' for m in sorted(matches, key=lambda x: x['% Diff'])])}
                </tbody>
            </table>
        </div>
        
        <footer class="footer">
            <p>Data provided by Yahoo Finance & Wikipedia Analysts. Generated on {time.strftime('%Y-%m-%d %H:%M:%S')}</p>
        </footer>
    </div>
</body>
</html>"""
            with open(html_path, "w") as f:
                f.write(html_template)
            console.print(f"[bold green]Premium HTML report generated: {html_path}[/bold green]")
        except Exception as e:
            console.print(f"\n[red]Could not generate HTML: {e}[/red]")

    end_time = time.time()
    console.print(f"\n[dim]Screening completed in {end_time - start_time:.1f} seconds.[/dim]")

if __name__ == "__main__":
    main()
