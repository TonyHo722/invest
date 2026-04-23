# Stock Report Generator User Guide

This guide explains how to use the `gen_report.py` script to generate high-quality financial reports for stock analysis.

---

## 🚀 Getting Started

The `gen_report.py` script is a powerful command-line tool designed to automate the creation of "KQJ Style" financial reports. It fetches live data via `yfinance` and calculates performance trends automatically.

### Prerequisites
The script requires Python 3 and the following libraries (already installed in your `.venv`):
- `yfinance` (Data fetching)
- `pandas` (Data processing)
- `rich` (Terminal output)

---

## 🛠️ Usage

### 1. Simple Generation
Run the script from the root of the workspace using the virtual environment:

```bash
./.venv/bin/python scripts/gen_report.py [TICKER]
```

**Example:**
```bash
./.venv/bin/python scripts/gen_report.py LVMUY
```

### 2. Multi-Stock Generation
You can generate reports for multiple companies in a single command:

```bash
./.venv/bin/python scripts/gen_report.py NKE TSLA AAPL MSFT
```

### 3. Creating a Shortcut (Recommended)
To run the command simply as `gen_report`, you can add an alias to your shell profile (`~/.bashrc`):

```bash
alias gen_report='/home/tonyho/workspace/invest/.venv/bin/python /home/tonyho/workspace/invest/scripts/gen_report.py'
```

---

## 📊 Output Structure

Each time you run the script, it creates or updates a folder in `/report/[TICKER]/` with two files:

| File Type | Filename | Best Use Case |
| :--- | :--- | :--- |
| **Markdown** | `[ticker]_financial_data.md` | General reading and archival. |
| **HTML** | `[ticker]_financial_data.html` | Interactive analysis with live TradingView charts. |

### Dashboard Features
- **Price Charts**: 1-Year (Daily) and 5-Year (Weekly) views.
- **Financial Table**: 4 years of Revenue, Net Income, EPS, FCF, and more.
- **Trend Indicators**: Automatic 📈/📉 detection based on year-over-year performance.
- **Framework Assessment**: Summary of **Big, Good, and Cheap** status.

---

## 🧪 Analysis Logic (KQJ Framework)

The script evaluates stocks based on the **KQJ Global Investment** framework:
1.  **Big (又大)**: Checks if the Market Cap is significant (typically > $10B).
2.  **Good (又好)**: Analyzes if the company is consistently profitable and growing cash flow.
3.  **Cheap (又便宜)**: Looks at valuation multiples (P/E, P/S) relative to recent price action.

---

## ❓ Troubleshooting

- **"No financial data available"**: Some stocks (especially very small ones or non-standard OTC tickers) may not provide full financials through the API.
- **Unterminated String Literal**: If you modify the script, ensure all strings (especially those with Chinese characters) are properly quoted using `f'...'` or `f"..."`.
- **Command Not Found**: Ensure you have executed `chmod +x scripts/gen_report.py` if you try to run it as `./scripts/gen_report.py`.
