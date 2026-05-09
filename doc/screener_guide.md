# Mega-Cap 200-DMA Screener Guide

This guide explains how to use the stock screening tool found at [screener.py](file:///home/tonyho/workspace/invest/scripts/screener.py).

## Overview

The `screener.py` script is designed to identify high-quality investment opportunities by filtering for companies that meet two primary criteria:
1.  **Big (又大)**: Market Capitalization > 10 Billion (USD for US stocks, TWD for Taiwan stocks).
2.  **Cheap (又便宜)**: Current Stock Price is below its 200-Day Simple Moving Average (200-DMA).

The script can automatically fetch constituents from the S&P 500, NASDAQ-100, and Taiwan Stock Exchange (TWSE/TPEx) and analyze them in real-time.

## Prerequisites

The script requires Python 3.x and several libraries already installed in the local virtual environment (`.venv`):
- `yfinance`: For fetching stock prices and market capitalization data.
- `pandas`: For data manipulation and CSV export.
- `requests` & `beautifulsoup4`: For scraping the S&P 500 ticker list.
- `rich`: For beautiful terminal output and progress bars.

## How to Run

To run the screener, use the terminal and execute the script using the project's virtual environment:

```bash
# Navigate to project root
cd /home/tonyho/workspace/invest

# Execute the script (Defaults to US market)
./.venv/bin/python3 scripts/screener.py

# Alternatively, scan specific markets:
./.venv/bin/python3 scripts/screener.py --market us  # S&P 500 & NASDAQ-100
./.venv/bin/python3 scripts/screener.py --market tw  # Taiwan TWSE & TPEx
./.venv/bin/python3 scripts/screener.py --market jp  # Japan Nikkei 225
./.venv/bin/python3 scripts/screener.py --market all # US, TW, and JP markets
```

### Script Execution Logic
1.  **Fetch Tickers**: Scrapes the latest constituent lists depending on the chosen market (Wikipedia for US, official ISIN for TW, iShares for JP).
2.  **Batch Technical Screen**: Downloads the last year of price data for all selected stocks in a single high-speed request.
3.  **Condition Filter**: Filters for stocks where `Current Price < 200-DMA`.
4.  **Fundamental Validation**: For remaining candidates, it fetches current Market Cap and Currency to ensure they are > 10B (USD or TWD).
5.  **Report Generation**: Generates outputs in terminal, CSV, and HTML formats.

## Outputs

After a successful run, the script produces:

1.  **Terminal Table**: A clean, color-coded summary of matches.
2.  **CSV Export**: Raw data for spreadsheet analysis (e.g., `dma_200_screen_results_us.csv` or `dma_200_screen_results_tw.csv`).
3.  **HTML Dashboard**: A premium visual report (e.g., `dma_200_screen_results_us.html` or `dma_200_screen_results_tw.html`).

## Automated Report Generation

After running the screener, you can generate detailed "Big, Good, and Cheap" financial reports for every matching company using the following script:

```bash
# Navigate to project root
cd /home/tonyho/workspace/invest

# Generate reports for the US market (default)
./.venv/bin/python3 scripts/generate_automated_reports.py --market us

# Or generate for the TW market
./.venv/bin/python3 scripts/generate_automated_reports.py --market tw

# Or generate for the JP market
./.venv/bin/python3 scripts/generate_automated_reports.py --market jp
```

### What this script does:
- **Financial Data Fetching**: Uses `yfinance` to grab the last 4 years of Revenue, Net Income, EPS, Free Cash Flow, and more.
- **Trend Analysis**: Automatically analyzes year-over-year performance to assign 📈 `Good` or 📉 `Bad` trend indicators.
- **Metric Calculation**: Computes ROE, ROA, and Gross Margins dynamically.
- **File Output**: Creates a dedicated folder for each ticker in the `report/` directory, containing both `.md` and `.html` detailed reports.

> [!WARNING]
> Processing a large number of reports (e.g., 50+) can take significant time (approx. 15-20 seconds per company). The script includes a progress bar to track status.

## Link Individual Reports to the Main Dashboard

Once individual financial reports are generated, you can create a fully interconnected interactive dashboard by linking them to the main screener results HTML:

```bash
# Navigate to project root
cd /home/tonyho/workspace/invest

# Link reports for the US market (default)
./.venv/bin/python3 scripts/add_report_links.py --market us

# Or link for the TW market
./.venv/bin/python3 scripts/add_report_links.py --market tw

# Or link for the JP market
./.venv/bin/python3 scripts/add_report_links.py --market jp
```

### What this script does:
- **Parses the HTML Dashboard**: It reads the generated `dma_200_screen_results_{market}.html`.
- **Injects Hyperlinks**: It wraps every stock ticker badge in a clickable link pointing to that stock's dedicated HTML report (e.g., `AAPL/aapl_financial_data.html`).
- **Interactive Output**: It generates a new interactive dashboard (e.g., `dma_200_screen_result_link_us.html`). Clicking on any ticker in this new report will instantly open its full financial breakdown.

---
> [!TIP]
> Run this screener weekly to identify stocks that have entered a potential "value" zone or are experiencing long-term trend reversals.
