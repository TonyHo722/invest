#!/usr/bin/env python3
"""
check_200dma.py
Fetches real 200-day simple moving average vs current price for all tickers in report/.
Prints PASS (below 200 DMA) or FAIL (above 200 DMA) for each.
"""

import os, json
import yfinance as yf

REPORT_DIR = "/home/tonyho/workspace/invest/report"

# Get all ticker directories (skip non-directory files)
tickers = sorted([
    d for d in os.listdir(REPORT_DIR)
    if os.path.isdir(os.path.join(REPORT_DIR, d))
    and not d.startswith(".")
])

print(f"Checking {len(tickers)} tickers against 200-day MA...\n")
print(f"{'TICKER':<8} {'Current':>10} {'200-DMA':>10} {'% vs 200D':>12}  STATUS")
print("-" * 56)

below_200 = []
above_200 = []
errors = []

for ticker in tickers:
    try:
        data = yf.Ticker(ticker)
        hist = data.history(period="1y")
        if hist.empty or len(hist) < 50:
            errors.append(ticker)
            print(f"{ticker:<8} {'N/A':>10} {'N/A':>10} {'N/A':>12}  ⚠️  NO DATA")
            continue

        current = round(hist["Close"].iloc[-1], 2)

        # 200-DMA: use all available data (up to 1 year = ~252 trading days)
        # If we have < 200 days, use what's available
        hist_full = data.history(period="13mo")  # ~280 trading days
        dma200 = round(hist_full["Close"].rolling(200).mean().iloc[-1], 2)

        if current != current or dma200 != dma200:  # NaN check
            errors.append(ticker)
            print(f"{ticker:<8} {str(current):>10} {'N/A':>10} {'N/A':>12}  ⚠️  CALC ERROR")
            continue

        pct = round((current / dma200 - 1) * 100, 1)
        status = "✅ BELOW" if current < dma200 else "❌ ABOVE"

        print(f"{ticker:<8} {current:>10.2f} {dma200:>10.2f} {pct:>+11.1f}%  {status}")

        if current < dma200:
            below_200.append((ticker, current, dma200, pct))
        else:
            above_200.append((ticker, current, dma200, pct))

    except Exception as e:
        errors.append(ticker)
        print(f"{ticker:<8} {'ERROR':>10} {'N/A':>10} {'N/A':>12}  ⚠️  {str(e)[:30]}")

print()
print("=" * 56)
print(f"\n✅ BELOW 200 DMA ({len(below_200)}) — KEEP:")
for t, cur, dma, pct in sorted(below_200, key=lambda x: x[3]):
    print(f"   {t:<8} {cur:>8.2f} vs DMA {dma:>8.2f}  ({pct:+.1f}%)")

print(f"\n❌ ABOVE 200 DMA ({len(above_200)}) — REMOVE:")
for t, cur, dma, pct in sorted(above_200, key=lambda x: x[3], reverse=True):
    print(f"   {t:<8} {cur:>8.2f} vs DMA {dma:>8.2f}  ({pct:+.1f}%)")

if errors:
    print(f"\n⚠️  ERRORS / NO DATA ({len(errors)}):")
    for t in errors:
        print(f"   {t}")

# Save results to JSON for use by cleanup script
results = {
    "below_200": [t for t, *_ in below_200],
    "above_200": [t for t, *_ in above_200],
    "errors": errors,
}
with open("/home/tonyho/workspace/invest/scripts/dma_audit.json", "w") as f:
    json.dump(results, f, indent=2)

print("\n\nResults saved to scripts/dma_audit.json")
