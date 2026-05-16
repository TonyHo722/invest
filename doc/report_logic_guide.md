# Financial Report Calculation Guide

This document explains the calculation logic and data sources used in the automated financial reports.

## 1. Operational and Financial Performance
This section provides a 4-year trajectory of the company's "health."

| Metric | Source / Formula | Explanation |
| :--- | :--- | :--- |
| **Revenue** | Income Statement: `Total Revenue` | Total top-line sales. |
| **Gross Profit** | Income Statement: `Gross Profit` | Revenue minus Cost of Goods Sold (COGS). |
| **Op. Profit** | Income Statement: `Operating Income` | Profit after operating expenses but before interest/taxes. |
| **Net Income** | Income Statement: `Net Income` | The final "bottom line" profit. |
| **EPS** | Income Statement: `Basic EPS` | Earnings per share. |
| **Dividends** | `ticker.dividends` (Summed by year) | Cash paid out to shareholders per share. |
| **Free Cash Flow (FCF)** | Cash Flow: `Operating Cash Flow - Change in Working Capital - abs(Capital Expenditures)` | Custom KQJ formula for true free cash flow. |
| **Buybacks** | Cash Flow: `Repurchase Of Capital Stock` | Cash spent by the company to buy back its own shares (shown as absolute value). |

## 2. Efficiency and Return Metrics
These ratios measure how effectively the company uses its capital. We use the **KQJ Average Methodology**, calculating the average of the current and previous year's balance sheet values.

| Metric | Formula | Goal |
| :--- | :--- | :--- |
| **Gross Margin** | `(Gross Profit / Revenue) * 100` | Higher is better (pricing power). |
| **Inventory Days** | `(Average Inventory / Cost of Revenue) * 365` | Lower is better (efficient inventory turnover). |
| **DSO** | `(Average Accounts Receivable / Revenue) * 365` | Lower is better (efficient cash collection). |
| **ROE (%)** | `(Net Income / Average Stockholders Equity) * 100` | Return on Equity. Measures profitability relative to shareholder capital. |
| **ROA (%)** | `(Net Income / Average Total Assets) * 100` | Return on Assets. Measures efficiency of total asset base. |

## 3. Valuations - 3P Model ("Cheap")
We use the historical table to assess if a stock is "Cheap" relative to its history.

Calculated using the stock price and share count at the **Fiscal Year-End (FYE) Date**.

*   **Logic**: The script identifies the exact date of the financial statement (e.g., Dec 31st for most US stocks) and fetches the **Closing Price** from that specific trading day.
*   **P/S (Price to Sales)**: `(FYE Price * FYE Shares) / Annual Revenue`
*   **P/E (Price to Earnings)**: `FYE Price / Annual EPS`
*   **P/B (Price to Book)**: `(FYE Price * FYE Shares) / Year-End Stockholders Equity`

## 4. Framework Assessment (Big/Good/Cheap)
*   **Big (又大)**: Check if Market Cap is above threshold (default ~¥100B or $1B).
*   **Good (又好)**: Automated check for upward trajectory in Revenue, Net Income, and FCF over 4 years.
*   **Cheap (又便宜)**: Qualitative check against historical P/E and P/S averages.

---

## 5. Worked Example: Pool Corporation (POOL) 2024
This example shows how the script derived the numbers for POOL's 2024 Annual report using exact data from Yahoo Finance.

### A. Raw Data (Extracted from yfinance for 2024)
*   **Data Date**: December 31, 2024 (Fiscal Year End)
*   **Total Revenue**: $5,311M | **Cost of Revenue**: $3,736M
*   **Net Income**: $434M | **Basic EPS**: $11.37
*   **Operating Cash Flow**: $659M | **Change In Working Capital**: $146M | **Capital Expenditures**: -$59M
*   **Inventory (2024)**: $1,289M | **Inventory (2023)**: $1,365M *(Average: $1,327M)*
*   **Accounts Receivable (2024)**: $31.4M | **Accounts Receivable (2023)**: $61.0M *(Average: $46.2M)*
*   **Stockholders Equity (2024)**: $1,273M | **Stockholders Equity (2023)**: $1,313M *(Average: $1,293M)*
*   **Price (at FYE)**: $327.42 | **Shares Outstanding**: 38.05M

### B. Formula Execution (KQJ Methodology)
1.  **Free Cash Flow (FCF)**:
    *   `Formula`: Operating Cash Flow - Change in Working Capital - abs(Capital Expenditures)
    *   `Execution`: $659M - $146M - abs(-$59M) = $659M - $146M - $59M = **$454M**
2.  **Inventory Days**:
    *   `Formula`: (Average Inventory / Cost of Revenue) * 365
    *   `Execution`: ($1,327M / $3,736M) * 365 = **129 Days**
3.  **DSO (Days Sales Outstanding)**:
    *   `Formula`: (Average Accounts Receivable / Revenue) * 365
    *   `Execution`: ($46.2M / $5,311M) * 365 = **3 Days**
4.  **ROE (Return on Equity)**:
    *   `Formula`: (Net Income / Average Equity) * 100
    *   `Execution`: ($434M / $1,293M) * 100 = **33.6%**
5.  **P/E (Price to Earnings)**:
    *   `Formula`: FYE Price / Basic EPS
    *   `Execution`: $327.42 / $11.37 = **28.8**

---

## 6. Technical Transparency: Why My Numbers Might Differ
Financial data often varies across platforms (Yahoo, Bloomberg, Morningstar) due to specific accounting choices. Here is exactly what this script uses:

| Data Point | Exact Field / Logic Used | Common Reasons for Discrepancy |
| :--- | :--- | :--- |
| **Earnings (EPS)** | `Basic EPS` (Income Statement) | Other sites may use **Diluted EPS** or **Adjusted (Non-GAAP) EPS**, which excludes one-time costs. |
| **Share Count** | `sharesOutstanding` (Current) or `Basic Average Shares` (Historical) | Some sites use **Diluted Shares**, which results in lower EPS and higher P/E ratios. |
| **Valuation Price** | Closing Price on **Fiscal Year-End Date** | Other sites often show **Current P/E** based on today's price, which changes daily. Our annual table is a "snapshot" of the past. |
| **Market Cap** | `Price * SharesOutstanding` | Discrepancies occur if a site uses "Weighted Average Shares" instead of "Period-End Shares." |
| **Equity** | `Stockholders Equity` | We use total equity. Some analysts use "Tangible Book Value" (Equity minus Goodwill). |
| **Quarterly Data** | **TTM (Trailing Twelve Months)** Sum | Many sites only show **Annualized** (Q*1) or **Forward P/E**, which are more volatile than our TTM sum. |

### How to reconcile:
If you see a different P/E ratio on another site:
1.  Check if they are using **Current Price** vs. our **Historical FYE Price**.
2.  Check if they are using **Diluted EPS** vs. our **Basic EPS**.
3.  Check if they are using **Forward Earnings (estimates)** vs. our **Actual Reported Earnings**.

---
*Note: All data is sourced via Yahoo Finance. Non-US stocks are converted to their local currency (JPY for .T, TWD for .TW).*
