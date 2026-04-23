# Mega-Cap 200-DMA Screener Guide

This guide explains how to use the stock screening tool found at [screener.py](file:///home/tonyho/workspace/invest/scripts/screener.py).

## Overview

The `screener.py` script is designed to identify high-quality investment opportunities by filtering for companies that meet two primary criteria:
1.  **Big (又大)**: Market Capitalization > $10 Billion.
2.  **Cheap (又便宜)**: Current Stock Price is below its 200-Day Simple Moving Average (200-DMA).

The script automatically fetches the current S&P 500 and NASDAQ-100 constituents and analyzes them in real-time.

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

# Execute the script
./.venv/bin/python3 scripts/screener.py
```

### Script Execution Logic
1.  **Fetch Tickers**: Scrapes the latest S&P 500 and NASDAQ-100 lists from Wikipedia.
2.  **Batch Technical Screen**: Downloads the last year of price data for all ~500 stocks in a single high-speed request.
3.  **Condition Filter**: Filters for stocks where `Current Price < 200-DMA`.
4.  **Fundamental Validation**: For remaining candidates, it fetches current Market Cap to ensure they are > $10B.
5.  **Report Generation**: Generates outputs in terminal, CSV, and HTML formats.

## Outputs

After a successful run, the script produces:

1.  **Terminal Table**: A clean, color-coded summary of matches.
2.  **CSV Export**: [dma_200_screen_results.csv](file:///home/tonyho/workspace/invest/report/dma_200_screen_results.csv) — Raw data for spreadsheet analysis.
3.  **HTML Dashboard**: [dma_200_screen_results.html](file:///home/tonyho/workspace/invest/report/dma_200_screen_results.html) — A premium visual report covering both indices.

## Automated Report Generation

After running the screener, you can generate detailed "Big, Good, and Cheap" financial reports for every matching company using the following script:

```bash
./.venv/bin/python3 scripts/generate_automated_reports.py
```

### What this script does:
- **Financial Data Fetching**: Uses `yfinance` to grab the last 4 years of Revenue, Net Income, EPS, Free Cash Flow, and more.
- **Trend Analysis**: Automatically analyzes year-over-year performance to assign 📈 `Good` or 📉 `Bad` trend indicators.
- **Metric Calculation**: Computes ROE, ROA, and Gross Margins dynamically.
- **File Output**: Creates a dedicated folder for each ticker in the `report/` directory, containing both `.md` and `.html` detailed reports.

> [!WARNING]
> Processing a large number of reports (e.g., 50+) can take significant time (approx. 15-20 seconds per company). The script includes a progress bar to track status.

---
> [!TIP]
> Run this screener weekly to identify stocks that have entered a potential "value" zone or are experiencing long-term trend reversals.
