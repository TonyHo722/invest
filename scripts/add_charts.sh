#!/usr/bin/env bash
# add_charts.sh — Injects Section 0 stock price charts into all report MD and HTML files
# Based on skill.md Section 6 standard

REPORT_DIR="/home/tonyho/workspace/invest/report"

# Exchange map overrides (default: NASDAQ)
declare -A EXCHANGE
EXCHANGE[NKE]="NYSE"
EXCHANGE[HD]="NYSE"
EXCHANGE[META]="NASDAQ"
EXCHANGE[TSLA]="NASDAQ"
EXCHANGE[UNH]="NYSE"
EXCHANGE[NVO]="NYSE"
EXCHANGE[PG]="NYSE"
EXCHANGE[MCD]="NYSE"
EXCHANGE[TMO]="NYSE"
EXCHANGE[DIS]="NYSE"
EXCHANGE[ABT]="NYSE"
EXCHANGE[CRM]="NYSE"
EXCHANGE[MSFT]="NASDAQ"
EXCHANGE[ACN]="NYSE"
EXCHANGE[IBM]="NYSE"
EXCHANGE[SAP]="NYSE"
EXCHANGE[QCOM]="NASDAQ"
EXCHANGE[MDT]="NYSE"
EXCHANGE[BX]="NYSE"
EXCHANGE[PM]="NYSE"
EXCHANGE[SBUX]="NASDAQ"
EXCHANGE[VZ]="NYSE"
EXCHANGE[PFE]="NYSE"
EXCHANGE[BMY]="NYSE"
EXCHANGE[AMGN]="NASDAQ"
EXCHANGE[GILD]="NASDAQ"
EXCHANGE[MO]="NYSE"
EXCHANGE[PEP]="NASDAQ"
EXCHANGE[KO]="NYSE"
EXCHANGE[GE]="NYSE"
EXCHANGE[HON]="NASDAQ"
EXCHANGE[WMT]="NYSE"

for TICKER_DIR in "$REPORT_DIR"/*/; do
  TICKER=$(basename "$TICKER_DIR")
  EX="${EXCHANGE[$TICKER]:-NASDAQ}"

  # Find the MD and HTML files
  MD_FILE="$TICKER_DIR/${TICKER,,}_financial_data.md"
  HTML_FILE="$TICKER_DIR/${TICKER,,}_financial_data.html"

  # ── Patch MD file ──────────────────────────────────────────────────────────
  if [[ -f "$MD_FILE" ]]; then
    # Skip if already patched
    if grep -q "## 0. Stock Price Charts" "$MD_FILE"; then
      echo "[SKIP MD] $TICKER — already has Section 0"
    else
      # Build the chart block
      CHART_BLOCK="## 0. Stock Price Charts

### 📈 1-Year Price Chart ($TICKER)
[![$TICKER 1-Year Chart](https://charts2.finviz.com/chart.ashx?t=${TICKER}&ty=c&ta=1&p=d&s=l)](https://finviz.com/quote.ashx?t=${TICKER})

*Source: Finviz — Click chart to open interactive view*

### 📈 5-Year Price Chart ($TICKER)
[![$TICKER 5-Year Chart](https://charts2.finviz.com/chart.ashx?t=${TICKER}&ty=c&ta=1&p=w&s=l)](https://finviz.com/quote.ashx?t=${TICKER})

*Source: Finviz — Click chart to open interactive view*

> **Chart Notes:**
> - The **1-Year chart** (daily candles) shows short-term momentum and recent support/resistance levels.
> - The **5-Year chart** (weekly candles) shows the long-term price trend and major drawdown magnitude.

---

"
      # Prepend after the first two header lines
      HEADER=$(head -2 "$MD_FILE")
      REST=$(tail -n +3 "$MD_FILE")
      printf '%s\n\n%s\n%s' "$HEADER" "$CHART_BLOCK" "$REST" > "$MD_FILE"
      echo "[OK  MD] $TICKER"
    fi
  fi

  # ── Patch HTML file ────────────────────────────────────────────────────────
  if [[ -f "$HTML_FILE" ]]; then
    if grep -q "chart-grid" "$HTML_FILE"; then
      echo "[SKIP HTML] $TICKER — already has chart-grid"
    else
      ENC_TICKER=$(python3 -c "import urllib.parse; print(urllib.parse.quote('$EX:$TICKER'))")

      # CSS to inject inside existing <style> block (before closing </style>)
      CSS_INSERT='        .chart-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 20px; margin-bottom: 30px; }
        .chart-box { border: 1px solid #ddd; border-radius: 8px; overflow: hidden; }
        .chart-box h3 { margin: 0; padding: 10px 14px; background: #2c3e50; color: #fff; font-size: 14px; }
        .chart-box iframe { display: block; width: 100%; border: none; }
        .chart-note { background: #f8f9fa; border-left: 4px solid #2c3e50; padding: 10px 16px; margin-bottom: 30px; font-size: 0.9em; color: #555; border-radius: 0 6px 6px 0; }
        .chart-note ul { margin: 6px 0; padding-left: 18px; }
        @media (max-width: 600px) { .chart-grid { grid-template-columns: 1fr; } }'

      # HTML block to inject after <body> opening <h1>...</h1><p>...</p>
      CHART_HTML="
    <h2>0. Stock Price Charts</h2>
    <div class=\"chart-grid\">
        <div class=\"chart-box\">
            <h3>📈 1-Year Price Chart (Daily)</h3>
            <iframe
                src=\"https://s.tradingview.com/widgetembed/?symbol=${ENC_TICKER}&interval=D&range=12M&theme=light&style=1&locale=en&hide_side_toolbar=true&allow_symbol_change=false\"
                height=\"300\" allowtransparency=\"true\" scrolling=\"no\" allowfullscreen>
            </iframe>
        </div>
        <div class=\"chart-box\">
            <h3>📈 5-Year Price Chart (Weekly)</h3>
            <iframe
                src=\"https://s.tradingview.com/widgetembed/?symbol=${ENC_TICKER}&interval=W&range=60M&theme=light&style=1&locale=en&hide_side_toolbar=true&allow_symbol_change=false\"
                height=\"300\" allowtransparency=\"true\" scrolling=\"no\" allowfullscreen>
            </iframe>
        </div>
    </div>
    <div class=\"chart-note\">
        <strong>Chart Notes:</strong>
        <ul>
            <li>The <strong>1-Year chart</strong> (daily candles) shows short-term momentum and recent support/resistance levels.</li>
            <li>The <strong>5-Year chart</strong> (weekly candles) shows the long-term price trend and major drawdown magnitude.</li>
        </ul>
    </div>"

      python3 - "$HTML_FILE" "$CSS_INSERT" "$CHART_HTML" << 'PYEOF'
import sys, re

html_file = sys.argv[1]
css_insert = sys.argv[2]
chart_html = sys.argv[3]

with open(html_file, 'r') as f:
    content = f.read()

# 1. Inject CSS before </style>
content = content.replace('</style>', css_insert + '\n    </style>', 1)

# 2. Inject chart block after first <p>...</p> that follows <h1>
# Strategy: insert after the first </p> that appears in <body>
body_start = content.find('<body')
first_p_end = content.find('</p>', body_start)
if first_p_end != -1:
    insert_pos = first_p_end + len('</p>')
    content = content[:insert_pos] + '\n' + chart_html + '\n' + content[insert_pos:]

with open(html_file, 'w') as f:
    f.write(content)

print('done')
PYEOF
      echo "[OK  HTML] $TICKER"
    fi
  fi
done

echo ""
echo "All done!"
