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
| **Free Cash Flow (FCF)** | Cash Flow: `Free Cash Flow` | Cash from operations minus capital expenditures. |
| **Buybacks** | Cash Flow: `Repurchase Of Capital Stock` | Cash spent by the company to buy back its own shares (shown as absolute value). |

## 2. Efficiency and Return Metrics
These ratios measure how effectively the company uses its capital.

| Metric | Formula | Goal |
| :--- | :--- | :--- |
| **Gross Margin** | `(Gross Profit / Revenue) * 100` | Higher is better (pricing power). |
| **Inventory Days** | `(Inventory / Cost of Revenue) * 365` | Lower is better (efficient inventory turnover). |
| **ROE (%)** | `(Net Income / Stockholders Equity) * 100` | Return on Equity. Measures profitability relative to shareholder capital. |
| **ROA (%)** | `(Net Income / Total Assets) * 100` | Return on Assets. Measures efficiency of total asset base. |

## 3. Valuations - 3P Model ("Cheap")
We use two tables to assess if a stock is "Cheap" relative to its history and recent performance.

### 4.1 Historical Annual Valuations
Calculated using the stock price and share count at the **Fiscal Year-End (FYE) Date**.

*   **Logic**: The script identifies the exact date of the financial statement (e.g., Dec 31st for most US stocks, May 31st for Oracle Japan) and fetches the **Closing Price** from that specific trading day.
*   **P/S (Price to Sales)**: `(FYE Price * FYE Shares) / Annual Revenue`
*   **P/E (Price to Earnings)**: `FYE Price / Annual EPS`
*   **P/B (Price to Book)**: `(FYE Price * FYE Shares) / Stockholders Equity`

### 4.2 Recent Quarterly Valuations (Past 4Q)
Calculated using the price at the **Quarter-End Date**.

*   **Logic**: Similar to the annual table, the script fetches the Closing Price on the date the quarter ended (e.g., March 31, June 30, etc.).
*   **TTM Sum**: For any given quarter, we sum the values of that quarter plus the three quarters preceding it.
*   **P/E (TTM)**: `Quarter-End Price / (Sum of last 4 Quarters EPS)`
*   **P/S (TTM)**: `(Quarter-End Price * Historical Shares) / (Sum of last 4 Quarters Revenue)`
*   **Annualized (A)**: If fewer than 4 quarters of data are available in the API, the script falls back to `Quarterly Value * 4`. These are marked with **(A)**.
*   **Market Cap**: Calculated using the **Historical Share Count** at that specific quarter's end date (not just current shares).

## 4. Framework Assessment (Big/Good/Cheap)
*   **Big (又大)**: Check if Market Cap is above threshold (default ~¥100B or $1B).
*   **Good (又好)**: Automated check for upward trajectory in Revenue, Net Income, and FCF over 4 years.
*   **Cheap (又便宜)**: Qualitative check against historical P/E and P/S averages.

---

## 5. Worked Example: Pool Corporation (POOL) 2025
This example shows how the script derived the numbers for POOL's 2025 Annual report.

### A. Raw Data (Extracted from yfinance)
*   **Data Date**: December 31, 2025a (Fiscal Year End)
*   **Price (at FYE)**: $173.68
*   **Total Revenue**: $5,289M
*   **Net Income**: $406M
*   **Basic EPS**: $10.89
*   **Total Assets**: $3,625M (Approx.)
*   **Stockholders Equity**: $1,183.6M (Approx.)
*   **Shares Outstanding**: 36.4M

### B. Formula Execution
1.  **Market Cap Calculation**:
    *   `Formula`: Price * Shares
    *   `Execution`: $173.68 * 36.4M = **$6,321.9M (~$6.32B)**
2.  **P/S (Price to Sales)**:
    *   `Formula`: Market Cap / Revenue
    *   `Execution`: $6,321.9M / $5,289M = **1.19**
3.  **P/E (Price to Earnings)**:
    *   `Formula`: Price / EPS
    *   `Execution`: $173.68 / $10.89 = **15.95**
4.  **P/B (Price to Book)**:
    *   `Formula`: Market Cap / Stockholders Equity
    *   `Execution`: $6,321.9M / $1,183.6M = **5.34**
5.  **ROE (Return on Equity)**:
    *   `Formula`: (Net Income / Equity) * 100
    *   `Execution`: ($406M / $1,183.6M) * 100 = **34.3%**

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
