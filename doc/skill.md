# Investment Analysis Table Formatting Rules

This document outlines the standard table format used for summarizing stock analyses (specifically based on the KQJ Global Investment Channel method).

## 0. Stock Screening Rule (Updated)

The **primary screening criterion** for "Cheap / 又便宜" candidates is:

> **Current Price must be BELOW the 200-Day Simple Moving Average (200-DMA)**

### Formula
```
200-DMA = Average of the last 200 daily closing prices
Qualifies if: Current Price < 200-DMA
```

### Why 200-DMA (not 52-week midpoint)?
| | 52-Week Midpoint | 200-DMA |
| :--- | :--- | :--- |
| **Method** | (High + Low) / 2 | Rolling 200-day average of closes |
| **Industry Standard** | Basic range center | ✅ Yes — widely used by institutions |
| **Sensitivity** | Distorted by single spike/crash | Smoothed by actual trading price history |
| **Meaning** | Price relative to range | Price relative to long-term trend |

### Data Source
Use **yfinance** to fetch live 200-DMA:
```python
import yfinance as yf
hist = yf.Ticker("NKE").history(period="13mo")
dma200 = hist["Close"].rolling(200).mean().iloc[-1]
qualifies = hist["Close"].iloc[-1] < dma200
```

---

## 1. General Table Structure
All tables should use standard Markdown formatting with aligned columns.

- **Header Row:** Use descriptive titles (e.g., `Year / Status`, `Revenue`, `EPS`).
- **Alignment:** 
  - Left-align strings and textual descriptions (`:---`).
  - (Optional) Right-align numerical data for better readability if desired.
- **Borders/Formatting:** Use `|` characters to demarcate columns and rows.

## 2. Status & Trend Indicators
When summarizing the overall trend or providing a rating for a specific row/metric, use the following standardized emojis to quickly convey the status:

- **Good/Positive:** 📈 `Good` or ✅ `PASS`
- **Bad/Negative:** 📉 `Bad`
- **Mixed/Neutral:** ⚠️ `MIXED`
- **High Risk:** ⚠️ `HIGH RISK`

## 3. Categories of Analysis
Group data into the following standardized sections:

### A. Market Position (Big / 又大)
Focuses on the company's size and industry standing.
- **Required fields:** Global Rank, Market Cap.

### B. Operational and Financial Performance (Good / 又好)
Focuses on raw profitability and cash generation over a multi-year period.
- **Required fields:** Year, Revenue, Gross Profit, Operating Profit, Net Income, EPS, Dividends, Free Cash Flow, Stock Repurchases.
- **Final Row:** Must always be a "Trend" row evaluating the trajectory of each metric.

### C. Efficiency and Return Metrics
Focuses on management efficiency.
- **Required fields:** Year, Gross Margin (%), Inventory Turnover Days, ROE (%), ROA (%).
- **Final Row:** Must always be a "Trend" row.

### D. Valuations (Cheap / 又便宜)
Focuses on whether the stock is trading at a discount.
- **Required fields:** Year, P/S, P/E, P/B ratios.
- **Final Row:** Must always be a "Trend" row evaluating if the current ratios represent a discount.

## 4. Markdown Example

```markdown
| Year / Status | Revenue (M USD) | EPS (USD) | Dividends per Share (USD) |
| :--- | :--- | :--- | :--- |
| **2022** | 46,710 | 3.8 | 1.2 |
| **Current** | 46,440 | 2.0 | 1.6 |
| **Trend** | 📉 Bad | 📉 Bad | 📈 Good |
```

## 5. HTML Output Styling
When creating the `.html` equivalent of these tables, ensure the following CSS rules are applied for consistency:

```css
table { border-collapse: collapse; width: 100%; margin-bottom: 30px; }
th, td { border: 1px solid #ddd; padding: 10px; text-align: left; }
th { background-color: #f2f2f2; }
.good { color: green; font-weight: bold; }
.bad { color: red; font-weight: bold; }
.mixed { color: orange; font-weight: bold; }
.risk { color: red; font-weight: bold; }
```
Apply the corresponding classes (`class="good"`, `class="bad"`) to the trend summary cells.

## 6. Stock Price Charts (Section 0)

All reports should include a **Section 0** with a 1-year and 5-year stock price chart, placed **before** the Market Position section.

### A. Markdown (.md) — Finviz embedded image links

Use Finviz chart image URLs with a clickable link to the full quote page. Replace `TICKER` with the stock symbol.

```markdown
## 0. Stock Price Charts

### 📈 1-Year Price Chart (TICKER)
[![TICKER 1-Year Chart](https://charts2.finviz.com/chart.ashx?t=TICKER&ty=c&ta=1&p=d&s=l)](https://finviz.com/quote.ashx?t=TICKER)

*Source: Finviz — Click chart to open interactive view*

### 📈 5-Year Price Chart (TICKER)
[![TICKER 5-Year Chart](https://charts2.finviz.com/chart.ashx?t=TICKER&ty=c&ta=1&p=w&s=l)](https://finviz.com/quote.ashx?t=TICKER)

*Source: Finviz — Click chart to open interactive view*

> **Chart Notes:**
> - The **1-Year chart** (daily candles) shows short-term momentum and recent support/resistance levels.
> - The **5-Year chart** (weekly candles) shows the long-term price trend and major drawdown magnitude.

---
```

**URL Parameters:**
- `p=d` → Daily candles (1-Year view)
- `p=w` → Weekly candles (5-Year view)
- `ta=1` → Include technical analysis overlays

### B. HTML (.html) — TradingView iframe widgets

Use two side-by-side TradingView iframes in a responsive CSS grid. Replace `EXCHANGE%3ATICKER` (e.g. `NYSE%3ANKE`) and `TICKER` with the stock's exchange and symbol.

```html
<!-- Add to <style> block -->
.chart-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 20px; margin-bottom: 30px; }
.chart-box { border: 1px solid #ddd; border-radius: 8px; overflow: hidden; }
.chart-box h3 { margin: 0; padding: 10px 14px; background: #2c3e50; color: #fff; font-size: 14px; }
.chart-box iframe { display: block; width: 100%; border: none; }
.chart-note { background: #f8f9fa; border-left: 4px solid #2c3e50; padding: 10px 16px; margin-bottom: 30px; font-size: 0.9em; }
@media (max-width: 600px) { .chart-grid { grid-template-columns: 1fr; } }

<!-- Section 0 HTML block -->
<h2>0. Stock Price Charts</h2>
<div class="chart-grid">
    <div class="chart-box">
        <h3>📈 1-Year Price Chart (Daily)</h3>
        <iframe
            src="https://s.tradingview.com/widgetembed/?symbol=EXCHANGE%3ATICKER&interval=D&range=12M&theme=light&style=1&locale=en&hide_side_toolbar=true&allow_symbol_change=false"
            height="300" allowtransparency="true" scrolling="no" allowfullscreen>
        </iframe>
    </div>
    <div class="chart-box">
        <h3>📈 5-Year Price Chart (Weekly)</h3>
        <iframe
            src="https://s.tradingview.com/widgetembed/?symbol=EXCHANGE%3ATICKER&interval=W&range=60M&theme=light&style=1&locale=en&hide_side_toolbar=true&allow_symbol_change=false"
            height="300" allowtransparency="true" scrolling="no" allowfullscreen>
        </iframe>
    </div>
</div>
```

**TradingView URL Parameters:**
- `interval=D` + `range=12M` → 1-Year daily chart
- `interval=W` + `range=60M` → 5-Year weekly chart
- `theme=light` → Light theme (use `dark` for dark mode)
- Charts require an active internet connection to render.

---

## 7. Model Execution Rules: Prioritizing Specific Tools

When executing tasks or modifying files in this workspace, the AI assistant MUST strictly prioritize specific APIs and tools over generic commands to ensure performance, security, and cleanliness.

### Core Guidelines:
- **No `cat` for File Creation/Appends:** Never run `cat << 'EOF' > file` or `echo "text" >> file` in a bash command to create, overwrite, or append content to files. 
- **Use Dedicated APIs:** Use the direct file tools like `write_to_file` or `replace_file_content` (or native python file methods) to perform atomic file operations. Spawning a terminal process for simple file modifications is inefficient and error-prone.
- **Specific CLI Tools:** Avoid using generic, nested shell pipelines (e.g., `grep | sed | awk`) inside terminal runs if specific tools or standard language scripts can do it cleaner.
- **Verification:** Always check the status of running commands immediately and verify syntax changes using structured verification rather than generic shell scripts.
