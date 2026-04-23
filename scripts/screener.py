#!/usr/bin/env python3
import requests
import pandas as pd
import yfinance as yf
from bs4 import BeautifulSoup
from rich.console import Console
from rich.table import Table
from rich.progress import Progress
import time

def get_sp500_tickers():
    """Fetches S&P 500 tickers from Wikipedia."""
    url = "https://en.wikipedia.org/wiki/List_of_S%26P_500_companies"
    return fetch_wikipedia_tickers(url, "constituents")

def get_nasdaq100_tickers():
    """Fetches NASDAQ-100 tickers from Wikipedia."""
    url = "https://en.wikipedia.org/wiki/Nasdaq-100"
    return fetch_wikipedia_tickers(url, "constituents")

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

def screen_stocks(tickers, min_mcap_billion=10):
    """
    Screens tickers for Price < 200-DMA and Market Cap > min_mcap_billion.
    Optimized by fetching technicals in batch before checking fundamentals.
    """
    results = []
    console = Console()
    
    console.print(f"[cyan]Downloading historical data for {len(tickers)} tickers...[/cyan]")
    # Use yf.download for batch fetching of historical data
    try:
        data = yf.download(tickers, period="1y", interval="1d", group_by='ticker', progress=True)
    except Exception as e:
        console.print(f"[red]Error downloading data: {e}[/red]")
        return []

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
                
                if mcap >= min_mcap_billion * 1e9:
                    pct_diff = ((c['price'] / c['dma200']) - 1) * 100
                    results.append({
                        'Ticker': c['symbol'],
                        'Name': info.get('shortName', c['symbol']),
                        'Market Cap': mcap,
                        'Price': c['price'],
                        '200-DMA': c['dma200'],
                        '% Diff': pct_diff
                    })
            except Exception:
                pass
            progress.advance(task)
            
    return results

def main():
    console = Console()
    console.print("[bold blue]Mega-Cap 200-DMA Screener[/bold blue]\n")
    
    start_time = time.time()
    
    sp500_tickers = get_sp500_tickers()
    nasdaq_tickers = get_nasdaq100_tickers()
    
    # Merge and remove duplicates
    tickers = list(set(sp500_tickers + nasdaq_tickers))
    
    if not tickers:
        console.print("[red]Could not fetch tickers from any source. Exiting.[/red]")
        return
        
    console.print(f"Fetched {len(sp500_tickers)} S&P 500 and {len(nasdaq_tickers)} NASDAQ-100 tickers.")
    console.print(f"Unique tickers to scan: [bold cyan]{len(tickers)}[/bold cyan]\n")
    
    matches = screen_stocks(tickers)
    
    if not matches:
        console.print("[yellow]No companies match the criteria (Market Cap > $10B and Price < 200-DMA).[/yellow]")
    else:
        table = Table(title="Screening Results")
        table.add_column("Ticker", style="cyan")
        table.add_column("Name", style="white")
        table.add_column("Market Cap", justify="right")
        table.add_column("Price", justify="right")
        table.add_column("200-DMA", justify="right")
        table.add_column("% Diff", justify="right")

        for m in sorted(matches, key=lambda x: x['% Diff']):
            table.add_row(
                m['Ticker'],
                m['Name'],
                f"${m['Market Cap']/1e9:.2f}B",
                f"${m['Price']:.2f}",
                f"${m['200-DMA']:.2f}",
                f"[red]{m['% Diff']:.2f}%[/red]"
            )

        console.print(table)
        
        # Save results to a CSV
        try:
            df = pd.DataFrame(matches)
            csv_path = "/home/tonyho/workspace/invest/report/dma_200_screen_results.csv"
            df.to_csv(csv_path, index=False)
            console.print(f"\n[bold green]Results saved to {csv_path}[/bold green]")
        except Exception as e:
            console.print(f"\n[red]Could not save CSV: {e}[/red]")
            
        # Generate Premium HTML Report
        try:
            html_path = "/home/tonyho/workspace/invest/report/dma_200_screen_results.html"
            html_template = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Screener: Mega-Cap Value (S&P 500 & NASDAQ-100)</title>
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
            <p class="subtitle">Mega-Cap (S&P 500 & NASDAQ-100) Below 200-DMA</p>
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
                        <td class="mcap" style="text-align: right">${m['Market Cap']/1e9:.2f}B</td>
                        <td class="price" style="text-align: right">${m['Price']:.2f}</td>
                        <td class="dma-col price" style="text-align: right; color: #94a3b8">${m['200-DMA']:.2f}</td>
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
