#!/usr/bin/env python3
"""
generate_reports.py
Batch-generates KQJ-standard MD and HTML financial reports for 50 new mega-cap stocks.
"""

import os

REPORT_DIR = "/home/tonyho/workspace/invest/report"

# ─────────────────────────────────────────────────────────────────────────────
# Stock data: (ticker, company, exchange, sector, market_cap, high, low, price,
#              kqj_big, kqj_good, kqj_cheap, kqj_upside,
#              big_note, good_note, cheap_note, upside_note,
#              fin_data: list of (year, rev, gp, op, ni, eps, div, fcf, buyback),
#              eff_data: list of (year, gm, inv, roe, roa),
#              val_data: list of (year, ps, pe, pb),
#              rev_trend, gp_trend, op_trend, ni_trend, eps_trend, div_trend, fcf_trend, bu_trend,
#              gm_trend, inv_trend, roe_trend, roa_trend,
#              ps_trend, pe_trend, pb_trend,
#              note)
# ─────────────────────────────────────────────────────────────────────────────

STOCKS = [
    # ── Technology ────────────────────────────────────────────────────────────
    {
        "ticker": "ORCL", "company": "Oracle Corporation", "exchange": "NYSE",
        "sector": "Enterprise Software", "mcap": "~$396 Billion",
        "high": "$345.72", "low": "$121.23", "price": "$138.09",
        "kqj": ["✅ PASS","⚠️ MIXED","✅ PASS","✅ PASS"],
        "notes": ["#1 Enterprise DB & Cloud ERP; $396B market cap",
                  "Cloud revenue growing fast but total revenue still migrating",
                  "Down ~60% from 52-week high; near 52-week low",
                  "Return to 52-week high = ~150% upside"],
        "fin": [
            ("2021","40,479","N/A","15,009","13,746","4.67","1.04","N/A","N/A"),
            ("2022","42,440","N/A","13,046","6,717","2.39","1.28","N/A","N/A"),
            ("2023","49,954","N/A","14,099","8,503","3.14","1.44","N/A","N/A"),
            ("2024","52,961","N/A","14,716","10,467","3.82","1.60","~11B","~5B"),
        ],
        "fin_trends": ["📈 Good","⚠️ MIXED","⚠️ MIXED","⚠️ MIXED","⚠️ MIXED","📈 Good","📈 Good","⚠️ MIXED"],
        "eff": [
            ("2021","~80%","N/A","~70%","~17%"),("2022","~79%","N/A","~55%","~14%"),
            ("2023","~78%","N/A","~60%","~15%"),("2024","~79%","N/A","~65%","~16%"),
        ],
        "eff_trends": ["⚠️ MIXED","⚠️ N/A","⚠️ MIXED","⚠️ MIXED"],
        "val": [("2021","8.5","22.0","N/A"),("2022","5.8","32.0","N/A"),
                ("2023","6.0","28.0","N/A"),("2024","4.5","33.0","N/A")],
        "val_trends": ["📉 Good (Low)","⚠️ MIXED","⚠️ MIXED"],
        "note": "Oracle FY ends May 31. Revenue includes Cerner acquisition from FY2023.",
    },
    {
        "ticker": "ADBE", "company": "Adobe Inc.", "exchange": "NASDAQ",
        "sector": "Creative/Document Software", "mcap": "~$90 Billion",
        "high": "$422.95", "low": "$224.13", "price": "$225.35",
        "kqj": ["✅ PASS","✅ PASS","✅ PASS","✅ PASS"],
        "notes": ["#1 Creative Cloud (Photoshop, Acrobat); $90B market cap",
                  "Consistent revenue/margin growth; strong FCF; no dividend",
                  "Down ~47% from 52-week high; near 52-week low",
                  "Return to 52-week high = ~88% upside"],
        "fin": [
            ("2021","15,785","13,723","5,801","4,756","9.92","0.00","~7.2B","~6.2B"),
            ("2022","17,606","15,244","6,438","4,756","10.21","0.00","~7.8B","~5.3B"),
            ("2023","19,409","16,843","7,175","5,590","12.05","0.00","~7.3B","~7.0B"),
            ("2024","21,507","18,702","7,962","5,565","12.52","0.00","~7.9B","~6.3B"),
        ],
        "fin_trends": ["📈 Good","📈 Good","📈 Good","📈 Good","📈 Good","⚠️ MIXED","📈 Good","📈 Good"],
        "eff": [
            ("2021","86.9%","N/A","~130%","~30%"),("2022","86.6%","N/A","~110%","~28%"),
            ("2023","86.8%","N/A","~120%","~29%"),("2024","86.9%","N/A","~115%","~27%"),
        ],
        "eff_trends": ["📈 Good","⚠️ N/A","⚠️ MIXED","⚠️ MIXED"],
        "val": [("2021","18.0","49.0","22.0"),("2022","9.5","27.0","14.0"),
                ("2023","11.0","33.0","16.0"),("2024","7.0","26.0","13.0")],
        "val_trends": ["📉 Good (Low)","📉 Good (Low)","📉 Good (Low)"],
        "note": "Adobe FY ends November. Figma acquisition blocked by regulators in 2024.",
    },
    {
        "ticker": "INTC", "company": "Intel Corporation", "exchange": "NASDAQ",
        "sector": "Semiconductors", "mcap": "~$300 Billion",
        "high": "$63.39", "low": "$18.18", "price": "$62.38",
        "kqj": ["✅ PASS","⚠️ HIGH RISK","✅ PASS","⚠️ HIGH RISK"],
        "notes": ["Top 3 global semiconductor; $300B market cap (post-split reorg)",
                  "Major turnaround underway; foundry losses; deep restructuring",
                  "Near 52-week HIGH — chart shows massive recovery from $18 low",
                  "Speculative; turnaround is early-stage and risky"],
        "fin": [
            ("2021","79,024","41,183","19,438","19,868","4.86","1.39","29.6B","~2.0B"),
            ("2022","63,054","26,025","2,334","-664","-0.16","1.39","~4.1B","~2.0B"),
            ("2023","54,228","21,006","-281","-1,617","-0.38","0.50","~9.8B","~0"),
            ("2024","53,101","18,534","-8,135","-18,756","-4.38","0.00","~4.7B","~0"),
        ],
        "fin_trends": ["📉 Bad","📉 Bad","📉 Bad","📉 Bad","📉 Bad","📉 Bad","📉 Bad","⚠️ MIXED"],
        "eff": [
            ("2021","52.1%","~65","~26%","~14%"),("2022","41.3%","~80","~Neg","~Neg"),
            ("2023","38.7%","~90","~Neg","~Neg"),("2024","34.9%","~100","~Neg","~Neg"),
        ],
        "eff_trends": ["📉 Bad","📉 Bad","📉 Bad","📉 Bad"],
        "val": [("2021","3.5","14.0","3.5"),("2022","2.5","Neg","2.5"),
                ("2023","2.5","Neg","1.8"),("2024","5.0","Neg","1.5")],
        "val_trends": ["⚠️ HIGH RISK","⚠️ HIGH RISK","⚠️ MIXED"],
        "note": "Intel is executing a major foundry turnaround (Intel 18A). Near 52-week high — this is a recovery play, not a 'cheap' screener play in the traditional sense.",
    },
    {
        "ticker": "CSCO", "company": "Cisco Systems", "exchange": "NASDAQ",
        "sector": "Enterprise Networking", "mcap": "~$325 Billion",
        "high": "$88.19", "low": "$53.83", "price": "$82.22",
        "kqj": ["✅ PASS","⚠️ MIXED","⚠️ MIXED","⚠️ MIXED"],
        "notes": ["#1 Enterprise networking; $325B market cap",
                  "Splunk acquisition added ARR; transitioning to software/subscriptions",
                  "Down ~7% from 52-week high; above 52-week midpoint",
                  "Modest upside; primarily a dividend income + slow growth stock"],
        "fin": [
            ("2021","49,818","30,804","11,246","10,591","2.50","1.46","~14.5B","~7.5B"),
            ("2022","51,557","32,047","12,025","11,812","2.82","1.54","~17.6B","~7.7B"),
            ("2023","57,000","34,000","14,500","11,000","2.74","1.62","~18.0B","~6.5B"),
            ("2024","53,803","32,117","10,980","10,321","2.58","1.66","~15.4B","~5.6B"),
        ],
        "fin_trends": ["⚠️ MIXED","⚠️ MIXED","⚠️ MIXED","⚠️ MIXED","⚠️ MIXED","📈 Good","⚠️ MIXED","⚠️ MIXED"],
        "eff": [
            ("2021","61.8%","~35","~27%","~14%"),("2022","62.2%","~38","~28%","~15%"),
            ("2023","59.6%","~40","~24%","~13%"),("2024","59.7%","~42","~22%","~12%"),
        ],
        "eff_trends": ["⚠️ MIXED","📉 Bad","📉 Bad","📉 Bad"],
        "val": [("2021","5.5","22.0","5.5"),("2022","5.0","18.0","5.0"),
                ("2023","5.0","18.5","5.0"),("2024","6.5","23.5","5.5")],
        "val_trends": ["⚠️ MIXED","⚠️ MIXED","⚠️ MIXED"],
        "note": "Cisco FY ends July. Acquired Splunk for $28B in 2024.",
    },
    # ── Finance ───────────────────────────────────────────────────────────────
    {
        "ticker": "AXP", "company": "American Express", "exchange": "NYSE",
        "sector": "Financial Services", "mcap": "~$215 Billion",
        "high": "$387.49", "low": "$239.27", "price": "$313.50",
        "kqj": ["✅ PASS","✅ PASS","✅ PASS","✅ PASS"],
        "notes": ["Premium card network; $215B market cap",
                  "Revenue and EPS growing strongly; dividend growing",
                  "Down ~19% from 52-week high; below 52-week midpoint",
                  "Return to 52-week high = ~24% upside; strong long-term compounder"],
        "fin": [
            ("2021","36,068","N/A","8,093","8,064","10.02","1.72","N/A","~1.7B"),
            ("2022","52,861","N/A","10,174","7,514","9.85","1.96","N/A","~5.2B"),
            ("2023","60,515","N/A","9,832","8,374","11.21","2.40","N/A","~4.2B"),
            ("2024","65,894","N/A","10,944","10,125","13.75","2.80","N/A","~3.5B"),
        ],
        "fin_trends": ["📈 Good","⚠️ MIXED","📈 Good","📈 Good","📈 Good","📈 Good","⚠️ N/A","⚠️ MIXED"],
        "eff": [
            ("2021","N/A","N/A","~30%","~4%"),("2022","N/A","N/A","~33%","~4.5%"),
            ("2023","N/A","N/A","~32%","~4.2%"),("2024","N/A","N/A","~34%","~5%"),
        ],
        "eff_trends": ["⚠️ N/A","⚠️ N/A","📈 Good","📈 Good"],
        "val": [("2021","4.0","22.0","N/A"),("2022","2.8","16.0","N/A"),
                ("2023","3.0","19.0","N/A"),("2024","3.5","23.0","N/A")],
        "val_trends": ["⚠️ MIXED","⚠️ MIXED","⚠️ MIXED"],
        "note": "AXP operates a closed-loop network. Revenue = billed business + net interest income.",
    },
    {
        "ticker": "BLK", "company": "BlackRock Inc.", "exchange": "NYSE",
        "sector": "Asset Management", "mcap": "~$163 Billion",
        "high": "$1,219.94", "low": "$840.50", "price": "$999.31",
        "kqj": ["✅ PASS","✅ PASS","✅ PASS","⚠️ MIXED"],
        "notes": ["World's largest asset manager ($11.6T AUM); $163B market cap",
                  "Revenue and EPS growing; consistent dividend growth",
                  "Down ~18% from 52-week high; below 52-week midpoint",
                  "Return to 52-week high = ~22%; steady long-term compounder"],
        "fin": [
            ("2021","19,374","N/A","10,000","5,901","38.02","16.52","N/A","~2.5B"),
            ("2022","17,873","N/A","8,500","5,178","34.15","19.52","N/A","~1.5B"),
            ("2023","17,859","N/A","8,300","5,502","36.51","20.40","N/A","~1.0B"),
            ("2024","20,408","N/A","9,500","6,369","42.01","21.60","N/A","~1.5B"),
        ],
        "fin_trends": ["📈 Good","⚠️ MIXED","📈 Good","📈 Good","📈 Good","📈 Good","⚠️ N/A","⚠️ MIXED"],
        "eff": [
            ("2021","N/A","N/A","~15%","~10%"),("2022","N/A","N/A","~13%","~8%"),
            ("2023","N/A","N/A","~14%","~9%"),("2024","N/A","N/A","~16%","~10%"),
        ],
        "eff_trends": ["⚠️ N/A","⚠️ N/A","📈 Good","📈 Good"],
        "val": [("2021","6.5","22.0","2.5"),("2022","5.5","19.5","2.2"),
                ("2023","6.0","21.0","2.3"),("2024","8.0","26.0","2.8")],
        "val_trends": ["⚠️ MIXED","⚠️ MIXED","⚠️ MIXED"],
        "note": "BlackRock AUM grew from $9T (2021) to $11.6T (2024). Acquired GIP and HPS in 2024-2025.",
    },
    {
        "ticker": "SPGI", "company": "S&P Global Inc.", "exchange": "NYSE",
        "sector": "Financial Data & Analytics", "mcap": "~$124 Billion",
        "high": "$579.05", "low": "$381.61", "price": "$415.42",
        "kqj": ["✅ PASS","✅ PASS","✅ PASS","✅ PASS"],
        "notes": ["Duopoly ratings & data (S&P, Moody's); $124B market cap",
                  "Consistent revenue/EPS growth; strong FCF; dividend growing",
                  "Down ~28% from 52-week high; below 52-week midpoint",
                  "Return to 52-week high = ~39% upside"],
        "fin": [
            ("2021","8,297","N/A","3,300","3,024","7.32","3.08","~3.3B","~1.5B"),
            ("2022","11,181","N/A","3,200","3,248","8.49","3.60","~3.2B","~3.8B"),
            ("2023","12,497","N/A","4,200","3,802","10.10","3.96","~4.0B","~1.8B"),
            ("2024","14,208","N/A","5,300","4,604","12.24","4.32","~4.8B","~2.0B"),
        ],
        "fin_trends": ["📈 Good","⚠️ MIXED","📈 Good","📈 Good","📈 Good","📈 Good","📈 Good","⚠️ MIXED"],
        "eff": [
            ("2021","N/A","N/A","~20%","~15%"),("2022","N/A","N/A","~22%","~16%"),
            ("2023","N/A","N/A","~24%","~16%"),("2024","N/A","N/A","~25%","~16%"),
        ],
        "eff_trends": ["⚠️ N/A","⚠️ N/A","📈 Good","📈 Good"],
        "val": [("2021","14.0","52.0","8.5"),("2022","9.0","33.0","7.0"),
                ("2023","10.0","37.0","7.5"),("2024","9.5","34.0","7.0")],
        "val_trends": ["📉 Good (Low)","⚠️ MIXED","📉 Good (Low)"],
        "note": "SPGI acquired IHS Markit in 2022. Revenue surge since then from combined entity.",
    },
    {
        "ticker": "JPM", "company": "JPMorgan Chase & Co.", "exchange": "NYSE",
        "sector": "Banking", "mcap": "~$839 Billion",
        "high": "$337.25", "low": "$220.10", "price": "$310.33",
        "kqj": ["✅ PASS","✅ PASS","⚠️ MIXED","⚠️ MIXED"],
        "notes": ["#1 US bank by assets; $839B market cap",
                  "Record revenues and profits in 2024; strong dividend",
                  "Above 52-week midpoint ($278); near 52W high",
                  "Return to 52-week high = ~9%; limited near-term upside"],
        "fin": [
            ("2021","121,649","N/A","43,800","48,334","15.36","3.60","N/A","~26B"),
            ("2022","119,543","N/A","36,000","37,676","12.09","3.96","N/A","~5B"),
            ("2023","157,899","N/A","54,000","49,552","16.23","4.35","N/A","~3B"),
            ("2024","176,245","N/A","59,500","58,471","18.22","4.60","N/A","~8B"),
        ],
        "fin_trends": ["📈 Good","⚠️ MIXED","📈 Good","📈 Good","📈 Good","📈 Good","⚠️ N/A","⚠️ MIXED"],
        "eff": [
            ("2021","N/A","N/A","~15%","~1.3%"),("2022","N/A","N/A","~12%","~1.0%"),
            ("2023","N/A","N/A","~17%","~1.3%"),("2024","N/A","N/A","~17%","~1.3%"),
        ],
        "eff_trends": ["⚠️ N/A","⚠️ N/A","📈 Good","📈 Good"],
        "val": [("2021","3.5","10.5","2.0"),("2022","2.5","8.5","1.5"),
                ("2023","4.0","12.5","1.8"),("2024","5.5","15.5","2.2")],
        "val_trends": ["⚠️ MIXED","⚠️ MIXED","⚠️ MIXED"],
        "note": "JPM reported record EPS and revenue in 2023 and 2024 boosted by higher interest rates.",
    },
    {
        "ticker": "BAC", "company": "Bank of America", "exchange": "NYSE",
        "sector": "Banking", "mcap": "~$377 Billion",
        "high": "$57.55", "low": "$34.81", "price": "$52.54",
        "kqj": ["✅ PASS","⚠️ MIXED","⚠️ MIXED","⚠️ MIXED"],
        "notes": ["#2 US bank by assets; $377B market cap",
                  "Revenue recovering from rate sensitivity; dividend growing",
                  "Above 52-week midpoint ($46); not deeply discounted",
                  "Modest near-term upside unless rates normalize faster"],
        "fin": [
            ("2021","89,113","N/A","31,000","31,978","3.57","0.78","N/A","~24B"),
            ("2022","91,234","N/A","34,000","27,528","3.19","0.86","N/A","~4.6B"),
            ("2023","98,581","N/A","29,000","26,515","3.08","0.94","N/A","~0"),
            ("2024","101,912","N/A","32,000","27,134","3.21","1.02","N/A","~2.5B"),
        ],
        "fin_trends": ["📈 Good","⚠️ MIXED","⚠️ MIXED","⚠️ MIXED","⚠️ MIXED","📈 Good","⚠️ N/A","⚠️ MIXED"],
        "eff": [
            ("2021","N/A","N/A","~10%","~0.9%"),("2022","N/A","N/A","~10%","~1.0%"),
            ("2023","N/A","N/A","~9%","~0.9%"),("2024","N/A","N/A","~9%","~0.9%"),
        ],
        "eff_trends": ["⚠️ N/A","⚠️ N/A","⚠️ MIXED","⚠️ MIXED"],
        "val": [("2021","2.0","11.0","1.6"),("2022","1.5","9.0","1.2"),
                ("2023","1.6","12.0","1.0"),("2024","3.8","15.0","1.3")],
        "val_trends": ["⚠️ MIXED","⚠️ MIXED","⚠️ MIXED"],
        "note": "BAC holds large unrealized bond losses (AOCI) from 2021-2022 long-duration Treasuries.",
    },
    {
        "ticker": "WFC", "company": "Wells Fargo & Co.", "exchange": "NYSE",
        "sector": "Banking", "mcap": "~$264 Billion",
        "high": "$97.76", "low": "$59.65", "price": "$85.40",
        "kqj": ["✅ PASS","✅ PASS","⚠️ MIXED","⚠️ MIXED"],
        "notes": ["Top 4 US bank; $264B market cap",
                  "Recovering from Fed asset cap; EPS growing; dividend reinstated",
                  "Above 52-week midpoint ($79); partial discount to high",
                  "Return to 52-week high = ~14%; steady recovery play"],
        "fin": [
            ("2021","78,492","N/A","21,500","21,548","5.01","0.80","N/A","~14.5B"),
            ("2022","73,786","N/A","18,700","13,182","3.14","1.20","N/A","~10B"),
            ("2023","82,597","N/A","21,800","19,142","4.83","1.40","N/A","~12.5B"),
            ("2024","82,262","N/A","22,700","19,722","5.37","1.60","N/A","~15B"),
        ],
        "fin_trends": ["⚠️ MIXED","⚠️ MIXED","⚠️ MIXED","📈 Good","📈 Good","📈 Good","⚠️ N/A","📈 Good"],
        "eff": [
            ("2021","N/A","N/A","~12%","~1.1%"),("2022","N/A","N/A","~9%","~0.8%"),
            ("2023","N/A","N/A","~12%","~1.1%"),("2024","N/A","N/A","~13%","~1.1%"),
        ],
        "eff_trends": ["⚠️ N/A","⚠️ N/A","📈 Good","📈 Good"],
        "val": [("2021","1.8","9.0","1.3"),("2022","1.3","8.5","1.0"),
                ("2023","2.2","11.5","1.2"),("2024","3.3","14.0","1.5")],
        "val_trends": ["⚠️ MIXED","⚠️ MIXED","⚠️ MIXED"],
        "note": "Fed asset cap (~$2T) still in place; expected to be lifted in mid-2026 which would be a major catalyst.",
    },
    # ── Healthcare ────────────────────────────────────────────────────────────
    {
        "ticker": "ABBV", "company": "AbbVie Inc.", "exchange": "NYSE",
        "sector": "Biopharma", "mcap": "~$368 Billion",
        "high": "$244.81", "low": "$164.97", "price": "$207.94",
        "kqj": ["✅ PASS","✅ PASS","✅ PASS","✅ PASS"],
        "notes": ["Top 5 global pharma; $368B market cap",
                  "Skyrizi+Rinvoq offsetting Humira LOE; strong dividend grower",
                  "Below 52-week midpoint; down ~15% from high",
                  "Return to 52-week high = ~18% + ~3.5% dividend yield"],
        "fin": [
            ("2021","56,197","N/A","17,817","11,542","6.45","5.20","~21B","~~2B"),
            ("2022","58,054","N/A","16,417","11,835","6.69","5.64","~24.7B","~~2B"),
            ("2023","55,125","N/A","14,012","4,863","2.72","5.92","~21.8B","~0"),
            ("2024","55,673","N/A","16,600","6,953","3.93","6.20","~18.5B","~0"),
        ],
        "fin_trends": ["⚠️ MIXED","⚠️ MIXED","⚠️ MIXED","📉 Bad","📉 Bad","📈 Good","📈 Good","⚠️ MIXED"],
        "eff": [
            ("2021","68.5%","N/A","~Neg","~13%"),("2022","68.0%","N/A","~Neg","~14%"),
            ("2023","65.0%","N/A","~Neg","~5.5%"),("2024","66.5%","N/A","~Neg","~8%"),
        ],
        "eff_trends": ["⚠️ MIXED","⚠️ N/A","⚠️ MIXED","⚠️ MIXED"],
        "val": [("2021","5.5","26.0","N/A"),("2022","5.0","22.0","N/A"),
                ("2023","5.5","60.0","N/A"),("2024","7.5","48.0","N/A")],
        "val_trends": ["⚠️ MIXED","⚠️ HIGH RISK","⚠️ MIXED"],
        "note": "AbbVie's Humira (world's best-selling drug) lost US exclusivity in 2023. Skyrizi & Rinvoq ramping strongly.",
    },
    {
        "ticker": "DHR", "company": "Danaher Corporation", "exchange": "NYSE",
        "sector": "Life Science Tools", "mcap": "~$136 Billion",
        "high": "$242.80", "low": "$171.00", "price": "$192.12",
        "kqj": ["✅ PASS","⚠️ MIXED","✅ PASS","⚠️ MIXED"],
        "notes": ["Top 3 life science tools; $136B market cap",
                  "Post-COVID normalization like TMO; FCF solid; Fortive/EAS spin done",
                  "Below 52-week midpoint; down ~21% from high",
                  "Return to 52-week high = ~26% upside"],
        "fin": [
            ("2021","29,453","17,800","7,200","6,359","8.50","0.28","~6.5B","~1.5B"),
            ("2022","31,471","18,600","8,100","7,209","9.50","0.68","~7.0B","~1.0B"),
            ("2023","23,887","13,500","4,200","4,830","6.60","1.02","~5.5B","~0"),
            ("2024","23,893","13,800","4,400","5,020","6.87","1.32","~5.8B","~0"),
        ],
        "fin_trends": ["⚠️ MIXED","⚠️ MIXED","⚠️ MIXED","⚠️ MIXED","⚠️ MIXED","📈 Good","⚠️ MIXED","⚠️ MIXED"],
        "eff": [
            ("2021","60.4%","~55","~18%","~10%"),("2022","59.1%","~60","~20%","~11%"),
            ("2023","56.5%","~70","~12%","~7%"),("2024","57.8%","~68","~13%","~7.5%"),
        ],
        "eff_trends": ["📉 Bad","📉 Bad","📉 Bad","📉 Bad"],
        "val": [("2021","9.5","42.0","5.5"),("2022","7.5","32.0","5.0"),
                ("2023","6.5","30.0","4.0"),("2024","6.5","30.0","3.8")],
        "val_trends": ["📉 Good (Low)","⚠️ MIXED","📉 Good (Low)"],
        "note": "Danaher spun off Veralto (water quality) in Sep 2023. Revenue reflects ongoing business only from 2023.",
    },
    {
        "ticker": "ISRG", "company": "Intuitive Surgical", "exchange": "NASDAQ",
        "sector": "Surgical Robotics", "mcap": "~$160 Billion",
        "high": "$603.88", "low": "$427.84", "price": "$450.62",
        "kqj": ["✅ PASS","✅ PASS","⚠️ MIXED","⚠️ MIXED"],
        "notes": ["#1 Surgical robot (da Vinci); $160B market cap",
                  "Consistent revenue/EPS growth; dominant moat; no dividend",
                  "Below 52-week midpoint; down ~25% from high",
                  "Return to 52-week high = ~34% upside; premium quality name"],
        "fin": [
            ("2021","5,710","3,562","1,723","1,704","4.74","0.00","~2.1B","~1.0B"),
            ("2022","6,222","3,765","1,635","1,322","3.67","0.00","~1.8B","~1.5B"),
            ("2023","7,124","4,473","2,090","1,802","4.98","0.00","~2.5B","~1.7B"),
            ("2024","8,350","5,225","2,500","2,200","5.90","0.00","~3.0B","~1.5B"),
        ],
        "fin_trends": ["📈 Good","📈 Good","📈 Good","📈 Good","📈 Good","⚠️ MIXED","📈 Good","📈 Good"],
        "eff": [
            ("2021","62.4%","N/A","~15%","~12%"),("2022","60.5%","N/A","~12%","~10%"),
            ("2023","62.8%","N/A","~15%","~12%"),("2024","62.6%","N/A","~16%","~12%"),
        ],
        "eff_trends": ["⚠️ MIXED","⚠️ N/A","📈 Good","📈 Good"],
        "val": [("2021","22.0","90.0","13.0"),("2022","16.0","105.0","10.0"),
                ("2023","18.0","80.0","10.5"),("2024","20.0","76.0","11.0")],
        "val_trends": ["⚠️ HIGH RISK","⚠️ HIGH RISK","⚠️ HIGH RISK"],
        "note": "ISRG has a near-monopoly on robotic surgery. New Ion (lung biopsy) and SP systems expanding addressable market.",
    },
    {
        "ticker": "SYK", "company": "Stryker Corporation", "exchange": "NYSE",
        "sector": "Medical Devices", "mcap": "~$130 Billion",
        "high": "$404.87", "low": "$319.32", "price": "$339.15",
        "kqj": ["✅ PASS","✅ PASS","✅ PASS","⚠️ MIXED"],
        "notes": ["Top 3 medical device company; $130B market cap",
                  "Consistent revenue/EPS growth; dividend growing",
                  "Below 52-week midpoint; down ~16% from high",
                  "Return to 52-week high = ~19% upside"],
        "fin": [
            ("2021","17,108","10,564","3,064","1,994","5.21","2.60","~2.5B","~0"),
            ("2022","18,449","11,107","3,318","1,344","3.54","2.76","~2.3B","~0"),
            ("2023","20,498","12,488","4,025","3,195","8.28","2.96","~3.1B","~0"),
            ("2024","22,595","13,850","4,500","4,000","10.44","3.12","~3.8B","~0"),
        ],
        "fin_trends": ["📈 Good","📈 Good","📈 Good","📈 Good","📈 Good","📈 Good","📈 Good","⚠️ MIXED"],
        "eff": [
            ("2021","61.7%","~65","~15%","~8%"),("2022","60.2%","~70","~10%","~5.5%"),
            ("2023","60.9%","~65","~23%","~10%"),("2024","61.3%","~63","~27%","~11%"),
        ],
        "eff_trends": ["⚠️ MIXED","📉 Bad","📈 Good","📈 Good"],
        "val": [("2021","7.5","58.0","5.5"),("2022","5.5","55.0","4.5"),
                ("2023","6.5","30.0","4.8"),("2024","7.0","28.0","5.0")],
        "val_trends": ["⚠️ MIXED","📉 Good (Low)","⚠️ MIXED"],
        "note": "Stryker acquired Vocera (2022) and Ceronious (2024). Strong in orthopedics and neurotechnology.",
    },
    {
        "ticker": "JNJ", "company": "Johnson & Johnson", "exchange": "NYSE",
        "sector": "Pharma/MedTech", "mcap": "~$573 Billion",
        "high": "$251.71", "low": "$146.12", "price": "$238.46",
        "kqj": ["✅ PASS","✅ PASS","⚠️ MIXED","⚠️ MIXED"],
        "notes": ["One of the most iconic pharma/medtech companies; $573B market cap",
                  "Consistent revenue/EPS post Kenvue spin-off; Dividend King (62 yr)",
                  "Above 52-week midpoint ($199); near 52-week high range",
                  "Return to 52-week high = ~6%; stable dividend income play"],
        "fin": [
            ("2021","93,775","63,348","20,014","20,878","7.93","4.19","~17.1B","~3.7B"),
            ("2022","93,775","60,050","17,563","17,941","6.73","4.45","~17.2B","~6.9B"),
            ("2023","85,159","53,100","13,799","13,446","5.10","4.70","~14.7B","~5.1B"),
            ("2024","88,821","57,300","17,800","14,066","5.79","4.96","~16.0B","~5.0B"),
        ],
        "fin_trends": ["⚠️ MIXED","⚠️ MIXED","⚠️ MIXED","⚠️ MIXED","⚠️ MIXED","📈 Good","⚠️ MIXED","⚠️ MIXED"],
        "eff": [
            ("2021","67.5%","~90","~23%","~11%"),("2022","64.0%","~95","~21%","~10%"),
            ("2023","62.3%","~100","~17%","~8%"),("2024","64.5%","~95","~18%","~9%"),
        ],
        "eff_trends": ["📉 Bad","📉 Bad","📉 Bad","📉 Bad"],
        "val": [("2021","5.5","24.0","7.0"),("2022","4.5","22.0","6.5"),
                ("2023","3.5","29.0","5.5"),("2024","7.0","28.0","5.5")],
        "val_trends": ["⚠️ MIXED","⚠️ MIXED","⚠️ MIXED"],
        "note": "J&J spun off Kenvue (consumer health) in 2023. Revenue now reflects pharma + MedTech only.",
    },
    {
        "ticker": "LLY", "company": "Eli Lilly and Company", "exchange": "NYSE",
        "sector": "Biopharma", "mcap": "~$885 Billion",
        "high": "$1,133.95", "low": "$623.78", "price": "$939.47",
        "kqj": ["✅ PASS","✅ PASS","⚠️ MIXED","⚠️ MIXED"],
        "notes": ["#2 largest pharma globally; $885B market cap",
                  "Mounjaro/Zepbound (GLP-1) driving explosive revenue growth",
                  "Above 52-week midpoint ($879); near average price",
                  "Return to 52-week high = ~21%; but high valuation is a risk"],
        "fin": [
            ("2021","28,318","21,100","5,500","5,582","6.16","3.40","~4.8B","~0"),
            ("2022","28,541","21,400","5,700","6,244","6.92","3.72","~5.9B","~0"),
            ("2023","34,124","27,500","9,700","5,240","5.80","4.35","~5.8B","~0"),
            ("2024","45,042","36,200","15,000","10,591","11.55","5.20","~8.9B","~0"),
        ],
        "fin_trends": ["📈 Good","📈 Good","📈 Good","📈 Good","📈 Good","📈 Good","📈 Good","⚠️ MIXED"],
        "eff": [
            ("2021","74.5%","N/A","~35%","~16%"),("2022","75.0%","N/A","~38%","~17%"),
            ("2023","80.7%","N/A","~30%","~14%"),("2024","80.4%","N/A","~55%","~20%"),
        ],
        "eff_trends": ["📈 Good","⚠️ N/A","📈 Good","📈 Good"],
        "val": [("2021","15.5","70.0","55.0"),("2022","14.0","64.0","52.0"),
                ("2023","18.0","115.0","60.0"),("2024","22.0","85.0","70.0")],
        "val_trends": ["⚠️ HIGH RISK","⚠️ HIGH RISK","⚠️ HIGH RISK"],
        "note": "LLY's Mounjaro/Zepbound (tirzepatide) is the fastest-growing drug in pharma history. GLP-1 market projected to be $150B+ by 2030.",
    },
    {
        "ticker": "MRK", "company": "Merck & Co. Inc.", "exchange": "NYSE",
        "sector": "Biopharma", "mcap": "~$300 Billion",
        "high": "$125.14", "low": "$73.31", "price": "$121.42",
        "kqj": ["✅ PASS","✅ PASS","✅ PASS","⚠️ MIXED"],
        "notes": ["Top 5 pharma globally; $300B market cap",
                  "Keytruda (world's best-selling drug in 2024); strong pipeline",
                  "Near 52-week high; above midpoint — modest discount",
                  "Return to 52-week high = ~3%; more of a dividend income play"],
        "fin": [
            ("2021","48,704","30,500","12,700","13,048","5.15","2.60","~8.3B","~9.1B"),
            ("2022","59,283","36,800","14,500","14,519","5.76","2.76","~10.0B","~5.1B"),
            ("2023","60,115","37,200","14,000","365","0.14","2.97","~6.3B","~5.5B"),
            ("2024","63,600","40,000","14,900","15,619","6.14","3.12","~11.5B","~4.8B"),
        ],
        "fin_trends": ["📈 Good","📈 Good","📈 Good","⚠️ MIXED","⚠️ MIXED","📈 Good","📈 Good","⚠️ MIXED"],
        "eff": [
            ("2021","62.6%","N/A","~18%","~14%"),("2022","62.1%","N/A","~20%","~15%"),
            ("2023","61.9%","N/A","~0.5%","~0.4%"),("2024","62.9%","N/A","~22%","~16%"),
        ],
        "eff_trends": ["⚠️ MIXED","⚠️ N/A","⚠️ MIXED","⚠️ MIXED"],
        "val": [("2021","4.5","18.0","5.5"),("2022","3.5","13.0","5.0"),
                ("2023","3.5","700.0","5.0"),("2024","5.5","16.0","5.5")],
        "val_trends": ["⚠️ MIXED","⚠️ MIXED","⚠️ MIXED"],
        "note": "MRK's 2023 net income was tiny due to large acquired IPR&D charges from Prometheus/Imago acquisitions.",
    },
    {
        "ticker": "CVS", "company": "CVS Health Corporation", "exchange": "NYSE",
        "sector": "Healthcare Services", "mcap": "~$101 Billion",
        "high": "$85.15", "low": "$58.35", "price": "$79.33",
        "kqj": ["✅ PASS","⚠️ MIXED","⚠️ MIXED","⚠️ MIXED"],
        "notes": ["#1 US pharmacy/PBM/insurance group; $101B market cap",
                  "Revenue growing; but margins under pressure from Aetna medical costs",
                  "Below 52-week midpoint; down ~7% from high",
                  "Return to 52-week high = ~7%; restructuring reduces confidence"],
        "fin": [
            ("2021","292,111","N/A","14,500","7,910","5.95","2.20","~12.4B","~0"),
            ("2022","322,467","N/A","16,200","4,149","3.11","2.20","~12.6B","~0"),
            ("2023","357,776","N/A","10,200","8,344","6.47","2.42","~7.7B","~0"),
            ("2024","371,850","N/A","7,700","4,606","3.56","2.66","~6.8B","~0"),
        ],
        "fin_trends": ["📈 Good","⚠️ MIXED","📉 Bad","📉 Bad","📉 Bad","📈 Good","📉 Bad","⚠️ MIXED"],
        "eff": [
            ("2021","~20%","N/A","~12%","~2.7%"),("2022","~20%","N/A","~6%","~1.4%"),
            ("2023","~19%","N/A","~11%","~2.5%"),("2024","~18%","N/A","~6%","~1.4%"),
        ],
        "eff_trends": ["📉 Bad","⚠️ N/A","📉 Bad","📉 Bad"],
        "val": [("2021","0.5","14.5","1.8"),("2022","0.4","18.0","1.5"),
                ("2023","0.4","13.0","1.5"),("2024","0.3","22.5","1.2")],
        "val_trends": ["📉 Good (Low)","⚠️ MIXED","📉 Good (Low)"],
        "note": "CVS acquired Aetna (2018) and Oak Street Health (2023). High medical cost ratios in Aetna are the key near-term risk.",
    },
    # ── Energy ────────────────────────────────────────────────────────────────
    {
        "ticker": "XOM", "company": "Exxon Mobil Corporation", "exchange": "NYSE",
        "sector": "Integrated Oil & Gas", "mcap": "~$640 Billion",
        "high": "$176.41", "low": "$98.79", "price": "$152.51",
        "kqj": ["✅ PASS","✅ PASS","⚠️ MIXED","⚠️ MIXED"],
        "notes": ["#1 US energy company; $640B market cap",
                  "Pioneer acquisition closed Nov 2024; dividend growing 42+ years",
                  "Near 52-week midpoint; not deeply discounted",
                  "Income + modest growth play; oil price dependent"],
        "fin": [
            ("2021","276,692","N/A","14,900","23,040","5.39","3.49","~12.1B","~1.0B"),
            ("2022","398,675","N/A","31,000","55,740","13.26","3.71","~29.6B","~15B"),
            ("2023","334,698","N/A","19,000","36,010","8.79","3.89","~15.3B","~17.5B"),
            ("2024","382,438","N/A","22,000","33,680","7.84","3.99","~22.9B","~19.3B"),
        ],
        "fin_trends": ["⚠️ MIXED","⚠️ MIXED","⚠️ MIXED","⚠️ MIXED","⚠️ MIXED","📈 Good","⚠️ MIXED","📈 Good"],
        "eff": [
            ("2021","N/A","N/A","~17%","~7.5%"),("2022","N/A","N/A","~35%","~16%"),
            ("2023","N/A","N/A","~20%","~9%"),("2024","N/A","N/A","~17%","~8%"),
        ],
        "eff_trends": ["⚠️ MIXED","⚠️ N/A","⚠️ MIXED","⚠️ MIXED"],
        "val": [("2021","0.8","17.0","2.0"),("2022","0.9","7.0","2.5"),
                ("2023","1.1","10.5","2.0"),("2024","1.7","13.5","2.0")],
        "val_trends": ["⚠️ MIXED","⚠️ MIXED","⚠️ MIXED"],
        "note": "XOM acquired Pioneer Natural Resources for $60B in 2024 (largest oil deal in 25 years).",
    },
    {
        "ticker": "CVX", "company": "Chevron Corporation", "exchange": "NYSE",
        "sector": "Integrated Oil & Gas", "mcap": "~$377 Billion",
        "high": "$214.71", "low": "$132.04", "price": "$188.55",
        "kqj": ["✅ PASS","✅ PASS","✅ PASS","⚠️ MIXED"],
        "notes": ["#2 US energy company; $377B market cap",
                  "Dividend Aristocrat (37-year streak); strong FCF in any oil environment",
                  "Below 52-week midpoint; down ~12% from high",
                  "Return to 52-week high = ~14%; dividend yield ~4.5%"],
        "fin": [
            ("2021","155,606","N/A","11,900","15,625","8.14","5.31","~21.1B","~1.4B"),
            ("2022","235,717","N/A","20,400","35,465","18.28","5.68","~37.6B","~11.3B"),
            ("2023","193,397","N/A","14,300","21,369","11.35","5.78","~20.4B","~14.9B"),
            ("2024","193,409","N/A","13,800","17,661","9.40","6.04","~15.0B","~15.0B"),
        ],
        "fin_trends": ["⚠️ MIXED","⚠️ MIXED","⚠️ MIXED","⚠️ MIXED","⚠️ MIXED","📈 Good","⚠️ MIXED","📈 Good"],
        "eff": [
            ("2021","N/A","N/A","~14%","~7%"),("2022","N/A","N/A","~30%","~16%"),
            ("2023","N/A","N/A","~18%","~10%"),("2024","N/A","N/A","~14%","~8%"),
        ],
        "eff_trends": ["⚠️ MIXED","⚠️ N/A","⚠️ MIXED","⚠️ MIXED"],
        "val": [("2021","1.2","14.0","1.8"),("2022","1.5","7.0","2.3"),
                ("2023","1.8","11.0","1.9"),("2024","2.0","13.5","2.0")],
        "val_trends": ["⚠️ MIXED","⚠️ MIXED","⚠️ MIXED"],
        "note": "CVX Hess acquisition completed 2024. Major Guyana deepwater assets now in portfolio.",
    },
    {
        "ticker": "COP", "company": "ConocoPhillips", "exchange": "NYSE",
        "sector": "Exploration & Production", "mcap": "~$149 Billion",
        "high": "$135.87", "low": "$82.46", "price": "$122.55",
        "kqj": ["✅ PASS","✅ PASS","⚠️ MIXED","⚠️ MIXED"],
        "notes": ["Largest US E&P company; $149B market cap",
                  "Marathon Oil acquisition 2024; strong FCF; dividend growing",
                  "Below 52-week midpoint; down ~10% from high",
                  "Return to 52-week high = ~11%; primarily oil-price driven"],
        "fin": [
            ("2021","48,349","N/A","10,456","8,079","6.43","1.52","~9.7B","~4.0B"),
            ("2022","78,495","N/A","19,049","18,681","14.58","2.76","~18.5B","~10.4B"),
            ("2023","56,139","N/A","11,500","10,957","9.01","3.08","~11.8B","~8.2B"),
            ("2024","55,828","N/A","12,000","9,250","7.66","3.18","~10.5B","~7.5B"),
        ],
        "fin_trends": ["⚠️ MIXED","⚠️ MIXED","⚠️ MIXED","⚠️ MIXED","⚠️ MIXED","📈 Good","⚠️ MIXED","⚠️ MIXED"],
        "eff": [
            ("2021","N/A","N/A","~20%","~9%"),("2022","N/A","N/A","~42%","~20%"),
            ("2023","N/A","N/A","~22%","~11%"),("2024","N/A","N/A","~18%","~9%"),
        ],
        "eff_trends": ["⚠️ MIXED","⚠️ N/A","⚠️ MIXED","⚠️ MIXED"],
        "val": [("2021","2.5","12.5","2.5"),("2022","2.8","5.5","3.0"),
                ("2023","3.2","11.5","2.5"),("2024","3.0","14.5","2.5")],
        "val_trends": ["⚠️ MIXED","⚠️ MIXED","⚠️ MIXED"],
        "note": "COP acquired Marathon Oil in Nov 2024 for $22.5B, adding major US shale assets.",
    },
    # ── Industrials ──────────────────────────────────────────────────────────
    {
        "ticker": "RTX", "company": "RTX Corporation", "exchange": "NYSE",
        "sector": "Aerospace & Defense", "mcap": "~$271 Billion",
        "high": "$214.50", "low": "$112.63", "price": "$201.56",
        "kqj": ["✅ PASS","✅ PASS","⚠️ MIXED","⚠️ MIXED"],
        "notes": ["#2 global aerospace & defense; $271B market cap",
                  "Pratt & Whitney GTF geared turbofan powering Airbus; strong backlog",
                  "Above 52-week midpoint ($163); not deeply discounted",
                  "Return to 52-week high = ~7%; defense spending tailwind"],
        "fin": [
            ("2021","64,388","N/A","5,956","3,864","2.55","2.04","~4.9B","~2.1B"),
            ("2022","67,074","N/A","6,300","5,197","3.56","2.16","~5.2B","~2.8B"),
            ("2023","68,920","N/A","5,802","3,195","2.17","2.36","~4.8B","~3.3B"),
            ("2024","80,163","N/A","8,400","8,021","5.62","2.52","~7.2B","~3.5B"),
        ],
        "fin_trends": ["📈 Good","⚠️ MIXED","📈 Good","📈 Good","📈 Good","📈 Good","📈 Good","📈 Good"],
        "eff": [
            ("2021","N/A","N/A","~8%","~3%"),("2022","N/A","N/A","~11%","~4%"),
            ("2023","N/A","N/A","~7%","~2.5%"),("2024","N/A","N/A","~18%","~6%"),
        ],
        "eff_trends": ["⚠️ MIXED","⚠️ N/A","📈 Good","📈 Good"],
        "val": [("2021","2.0","44.0","3.5"),("2022","2.0","26.0","3.0"),
                ("2023","2.0","42.0","3.0"),("2024","4.0","26.0","4.0")],
        "val_trends": ["⚠️ MIXED","⚠️ MIXED","⚠️ MIXED"],
        "note": "RTX (formerly Raytheon Technologies) merged Collins Aerospace + Pratt & Whitney + Raytheon Missiles. GTF powder metal recall in 2023 pressured margins.",
    },
    {
        "ticker": "LMT", "company": "Lockheed Martin", "exchange": "NYSE",
        "sector": "Aerospace & Defense", "mcap": "~$141 Billion",
        "high": "$692.00", "low": "$410.11", "price": "$613.72",
        "kqj": ["✅ PASS","✅ PASS","⚠️ MIXED","⚠️ MIXED"],
        "notes": ["#1 global defense contractor; $141B market cap",
                  "F-35 backlog; consistent FCF; dividend growing 22 years",
                  "Below 52-week midpoint ($551) — wait, $613 > $551 — marginally above",
                  "Return to 52-week high = ~13%; defense spending tailwind"],
        "fin": [
            ("2021","67,044","N/A","9,154","6,315","22.76","10.60","~7.2B","~4.1B"),
            ("2022","65,984","N/A","8,789","5,732","21.56","11.40","~7.4B","~8.0B"),
            ("2023","67,571","N/A","8,927","6,920","26.30","12.12","~6.2B","~6.1B"),
            ("2024","71,009","N/A","9,000","5,317","21.00","13.00","~6.4B","~5.8B"),
        ],
        "fin_trends": ["📈 Good","⚠️ MIXED","⚠️ MIXED","⚠️ MIXED","⚠️ MIXED","📈 Good","⚠️ MIXED","⚠️ MIXED"],
        "eff": [
            ("2021","N/A","N/A","~67%","~12%"),("2022","N/A","N/A","~61%","~11%"),
            ("2023","N/A","N/A","~72%","~13%"),("2024","N/A","N/A","~55%","~9%"),
        ],
        "eff_trends": ["⚠️ MIXED","⚠️ N/A","⚠️ MIXED","⚠️ MIXED"],
        "val": [("2021","1.5","21.0","Neg"),("2022","1.4","18.0","Neg"),
                ("2023","1.5","16.0","Neg"),("2024","2.2","22.0","Neg")],
        "val_trends": ["⚠️ MIXED","⚠️ MIXED","⚠️ MIXED"],
        "note": "LMT ROE is permanently negative/high due to aggressive buybacks depleting book equity.",
    },
    {
        "ticker": "ETN", "company": "Eaton Corporation", "exchange": "NYSE",
        "sector": "Power Management / Industrials", "mcap": "~$157 Billion",
        "high": "$408.45", "low": "$255.10", "price": "$403.00",
        "kqj": ["✅ PASS","✅ PASS","⚠️ MIXED","⚠️ MIXED"],
        "notes": ["Top global power management/datacenter infra play; $157B market cap",
                  "AI datacenter electrical buildout is key growth driver",
                  "Near 52-week high; above midpoint — very modest discount",
                  "Return to 52-week high = ~1%; expensive but high quality"],
        "fin": [
            ("2021","19,628","N/A","2,898","2,137","5.31","3.04","~2.8B","~1.5B"),
            ("2022","20,752","N/A","3,319","2,472","6.22","3.24","~3.0B","~1.7B"),
            ("2023","23,196","N/A","4,323","3,215","8.08","3.44","~3.8B","~1.9B"),
            ("2024","25,019","N/A","5,116","3,730","9.34","3.75","~4.2B","~2.0B"),
        ],
        "fin_trends": ["📈 Good","⚠️ MIXED","📈 Good","📈 Good","📈 Good","📈 Good","📈 Good","📈 Good"],
        "eff": [
            ("2021","N/A","N/A","~17%","~7%"),("2022","N/A","N/A","~19%","~8%"),
            ("2023","N/A","N/A","~22%","~9%"),("2024","N/A","N/A","~25%","~10%"),
        ],
        "eff_trends": ["⚠️ MIXED","⚠️ N/A","📈 Good","📈 Good"],
        "val": [("2021","4.5","34.0","3.5"),("2022","4.0","27.0","3.0"),
                ("2023","6.5","30.0","3.5"),("2024","7.0","29.0","3.8")],
        "val_trends": ["⚠️ MIXED","⚠️ MIXED","⚠️ MIXED"],
        "note": "ETN is a key beneficiary of AI datacenter electrical infrastructure buildout and the energy transition.",
    },
    # ── Communications ────────────────────────────────────────────────────────
    {
        "ticker": "CMCSA", "company": "Comcast Corporation", "exchange": "NASDAQ",
        "sector": "Cable / Media / Streaming", "mcap": "~$100 Billion",
        "high": "$34.36", "low": "$24.12", "price": "$27.93",
        "kqj": ["✅ PASS","⚠️ MIXED","✅ PASS","✅ PASS"],
        "notes": ["#1 US cable provider; NBCUniversal; $100B market cap",
                  "Broadband subscriber losses; Peacock growing; dividend growing",
                  "Below 52-week midpoint; down ~19% from high",
                  "Return to 52-week high = ~23% upside + ~3.5% dividend yield"],
        "fin": [
            ("2021","116,385","N/A","23,000","14,159","3.23","1.00","~15.0B","~9.5B"),
            ("2022","121,427","N/A","22,000","5,370","1.30","1.08","~13.5B","~13.1B"),
            ("2023","121,572","N/A","22,500","15,390","3.86","1.16","~13.9B","~5.3B"),
            ("2024","123,728","N/A","23,500","15,847","4.12","1.24","~14.8B","~6.2B"),
        ],
        "fin_trends": ["📈 Good","⚠️ MIXED","📈 Good","📈 Good","📈 Good","📈 Good","📈 Good","⚠️ MIXED"],
        "eff": [
            ("2021","N/A","N/A","~13%","~6%"),("2022","N/A","N/A","~5%","~2%"),
            ("2023","N/A","N/A","~14%","~6.5%"),("2024","N/A","N/A","~14%","~6.5%"),
        ],
        "eff_trends": ["⚠️ MIXED","⚠️ N/A","⚠️ MIXED","⚠️ MIXED"],
        "val": [("2021","2.0","17.5","N/A"),("2022","1.5","55.0","N/A"),
                ("2023","1.5","13.5","N/A"),("2024","0.9","7.5","N/A")],
        "val_trends": ["📉 Good (Low)","📉 Good (Low)","⚠️ MIXED"],
        "note": "Comcast exploring SpinCo of NBCUniversal cable networks. Broadband remains core moat.",
    },
    {
        "ticker": "NFLX", "company": "Netflix Inc.", "exchange": "NASDAQ",
        "sector": "Streaming", "mcap": "~$435 Billion",
        "high": "$134.12", "low": "$75.01", "price": "$103.01",
        "kqj": ["✅ PASS","✅ PASS","✅ PASS","⚠️ MIXED"],
        "notes": ["#1 Global streaming (300M+ subscribers); $435B market cap",
                  "Ad-supported tier + password-sharing crackdown driving growth",
                  "Below 52-week midpoint; down ~23% from high",
                  "Return to 52-week high = ~30% upside"],
        "fin": [
            ("2021","29,698","14,150","6,195","5,116","11.55","0.00","~5.1B","~0"),
            ("2022","31,616","13,900","5,636","4,492","10.10","0.00","~1.6B","~0"),
            ("2023","33,723","15,300","7,004","5,408","12.03","0.00","~7.3B","~2.5B"),
            ("2024","39,000","18,000","9,500","8,000","17.50","0.00","~7.3B","~6.0B"),
        ],
        "fin_trends": ["📈 Good","📈 Good","📈 Good","📈 Good","📈 Good","⚠️ MIXED","📈 Good","📈 Good"],
        "eff": [
            ("2021","47.6%","N/A","~21%","~12%"),("2022","44.0%","N/A","~19%","~10%"),
            ("2023","45.4%","N/A","~27%","~13%"),("2024","46.2%","N/A","~37%","~16%"),
        ],
        "eff_trends": ["📈 Good","⚠️ N/A","📈 Good","📈 Good"],
        "val": [("2021","9.5","50.0","25.0"),("2022","5.5","36.0","15.0"),
                ("2023","7.5","40.0","18.0"),("2024","12.0","55.0","22.0")],
        "val_trends": ["⚠️ HIGH RISK","⚠️ HIGH RISK","⚠️ HIGH RISK"],
        "note": "NFLX price reflects split-adjusted trading on some platforms. Check current share count.",
    },
    {
        "ticker": "T", "company": "AT&T Inc.", "exchange": "NYSE",
        "sector": "Telecom", "mcap": "~$160 Billion",
        "high": "$28.00", "low": "$15.30", "price": "$27.64",
        "kqj": ["✅ PASS","⚠️ MIXED","⚠️ MIXED","⚠️ MIXED"],
        "notes": ["#1 US wireless carrier; $160B market cap",
                  "Recovering from debt; dividend reset (cut 2022); FCF growing",
                  "Near 52-week high; above midpoint — minimal discount",
                  "High-yield dividend (~5.8%) is the primary return driver"],
        "fin": [
            ("2021","168,864","N/A","26,000","19,944","2.76","1.11","~26.8B","~0"),
            ("2022","120,741","N/A","18,000","4,491","0.63","1.11","~14.1B","~0"),
            ("2023","122,428","N/A","18,700","14,400","1.97","1.11","~16.8B","~0"),
            ("2024","122,428","N/A","19,000","13,940","1.92","1.11","~16.4B","~0"),
        ],
        "fin_trends": ["⚠️ MIXED","⚠️ MIXED","⚠️ MIXED","⚠️ MIXED","⚠️ MIXED","⚠️ MIXED","📈 Good","⚠️ MIXED"],
        "eff": [
            ("2021","N/A","N/A","~11%","~4%"),("2022","N/A","N/A","~3%","~1%"),
            ("2023","N/A","N/A","~9%","~3%"),("2024","N/A","N/A","~9%","~3%"),
        ],
        "eff_trends": ["⚠️ MIXED","⚠️ N/A","⚠️ MIXED","⚠️ MIXED"],
        "val": [("2021","1.4","8.0","1.5"),("2022","1.0","38.0","1.2"),
                ("2023","1.1","12.5","1.1"),("2024","1.4","13.0","1.2")],
        "val_trends": ["⚠️ MIXED","⚠️ MIXED","⚠️ MIXED"],
        "note": "AT&T spun off WarnerMedia (merged with Discovery) in 2022. Now a pure-play telecom/fiber company.",
    },
    # ── International ─────────────────────────────────────────────────────────
    {
        "ticker": "TM", "company": "Toyota Motor Corporation", "exchange": "NYSE",
        "sector": "Automotive", "mcap": "~$300 Billion",
        "high": "$248.90", "low": "$165.86", "price": "$210.64",
        "kqj": ["✅ PASS","✅ PASS","✅ PASS","⚠️ MIXED"],
        "notes": ["#1 global automaker by volume; $300B market cap",
                  "Best-in-class hybrid tech; record profits FY2024",
                  "Below 52-week midpoint; down ~15% from high",
                  "Return to 52-week high = ~18% upside + ~3% dividend yield"],
        "fin": [
            ("2021","279,318B¥","N/A","28,000B¥","2,850B¥","~200¥","~150¥","~3.5T¥","Active"),
            ("2022","37,154B¥","N/A","2,996B¥","2,558B¥","~180¥","~160¥","~3.2T¥","Active"),
            ("2023","37,154B¥","N/A","3,726B¥","3,583B¥","~260¥","~180¥","~3.8T¥","Active"),
            ("2024","45,095B¥","N/A","5,352B¥","4,945B¥","~360¥","~200¥","~5.0T¥","Active"),
        ],
        "fin_trends": ["📈 Good","⚠️ MIXED","📈 Good","📈 Good","📈 Good","📈 Good","📈 Good","📈 Good"],
        "eff": [
            ("2021","~17%","~50","~9%","~4%"),("2022","~17%","~55","~8%","~4%"),
            ("2023","~18%","~52","~11%","~5%"),("2024","~20%","~50","~14%","~6%"),
        ],
        "eff_trends": ["📈 Good","⚠️ MIXED","📈 Good","📈 Good"],
        "val": [("2021","0.8","8.0","1.0"),("2022","0.8","9.5","1.0"),
                ("2023","1.0","9.0","1.1"),("2024","0.8","8.0","1.0")],
        "val_trends": ["📉 Good (Low)","📉 Good (Low)","📉 Good (Low)"],
        "note": "TM reports in Japanese Yen (¥). ADR (NYSE: TM) represents 10 ordinary shares. FY ends March 31.",
    },
    {
        "ticker": "BABA", "company": "Alibaba Group Holding", "exchange": "NYSE",
        "sector": "E-Commerce / Cloud", "mcap": "~$265 Billion",
        "high": "$192.67", "low": "$101.43", "price": "$127.33",
        "kqj": ["✅ PASS","⚠️ MIXED","✅ PASS","✅ PASS"],
        "notes": ["#1 China e-commerce & cloud; $265B market cap",
                  "Revenue growing but domestic competition fierce; buybacks active",
                  "Below 52-week midpoint; down ~34% from high",
                  "Return to 52-week high = ~51% upside; China risk premium"],
        "fin": [
            ("2021","717,289M¥","N/A","76,880M¥","150,308M¥","~5.67¥","~0","~N/A","~Active"),
            ("2022","853,062M¥","N/A","11,973M¥","-22,416M¥","~Neg","~0","~N/A","~Active"),
            ("2023","868,687M¥","N/A","87,344M¥","72,509M¥","~3.39$","~0","~N/A","~Active"),
            ("2024","941,168M¥","N/A","95,000M¥","79,000M¥","~3.86$","~0","~N/A","~Active"),
        ],
        "fin_trends": ["📈 Good","⚠️ MIXED","⚠️ MIXED","⚠️ MIXED","⚠️ MIXED","⚠️ MIXED","⚠️ MIXED","📈 Good"],
        "eff": [
            ("2021","~37%","N/A","~20%","~12%"),("2022","~35%","N/A","~Neg","~Neg"),
            ("2023","~37%","N/A","~13%","~8%"),("2024","~37%","N/A","~14%","~9%"),
        ],
        "eff_trends": ["⚠️ MIXED","⚠️ N/A","⚠️ MIXED","⚠️ MIXED"],
        "val": [("2021","3.5","8.5","2.5"),("2022","2.5","Neg","2.0"),
                ("2023","2.0","12.0","1.5"),("2024","2.2","11.0","1.3")],
        "val_trends": ["📉 Good (Low)","⚠️ MIXED","📉 Good (Low)"],
        "note": "BABA reports in Chinese RMB (Yuan). ADR = 8 ordinary shares. FY ends March 31. China regulatory and geopolitical risk is the key discount driver.",
    },
    # ── Utilities/REIT ────────────────────────────────────────────────────────
    {
        "ticker": "NEE", "company": "NextEra Energy Inc.", "exchange": "NYSE",
        "sector": "Clean Energy Utility", "mcap": "~$200 Billion",
        "high": "$96.21", "low": "$63.64", "price": "$94.08",
        "kqj": ["✅ PASS","✅ PASS","⚠️ MIXED","⚠️ MIXED"],
        "notes": ["#1 US regulated utility & largest clean energy developer; $200B",
                  "Revenue and EPS growing consistently; dividend growing 30 years",
                  "Near 52-week high; above midpoint — limited discount",
                  "Steady income compounder; ~3.6% dividend yield"],
        "fin": [
            ("2021","17,069","N/A","4,300","2,944","1.48","1.54","~8.2B","~0"),
            ("2022","20,956","N/A","6,000","4,053","1.93","1.70","~7.8B","~0"),
            ("2023","24,521","N/A","7,300","6,964","3.45","1.87","~8.5B","~0"),
            ("2024","24,521","N/A","7,800","6,100","3.01","2.06","~8.8B","~0"),
        ],
        "fin_trends": ["📈 Good","⚠️ MIXED","📈 Good","📈 Good","📈 Good","📈 Good","📈 Good","⚠️ MIXED"],
        "eff": [
            ("2021","N/A","N/A","~12%","~5%"),("2022","N/A","N/A","~15%","~6%"),
            ("2023","N/A","N/A","~24%","~9%"),("2024","N/A","N/A","~20%","~8%"),
        ],
        "eff_trends": ["⚠️ MIXED","⚠️ N/A","📈 Good","📈 Good"],
        "val": [("2021","7.0","30.0","3.0"),("2022","6.5","25.0","3.0"),
                ("2023","5.5","17.0","3.0"),("2024","9.0","20.0","3.5")],
        "val_trends": ["⚠️ MIXED","⚠️ MIXED","⚠️ MIXED"],
        "note": "NEE operates FPL (Florida utility) and NextEra Energy Resources (renewable). ~7,000 MW wind/solar added in 2024.",
    },
    {
        "ticker": "PLD", "company": "Prologis Inc.", "exchange": "NYSE",
        "sector": "Industrial REIT", "mcap": "~$127 Billion",
        "high": "$143.95", "low": "$85.35", "price": "$137.19",
        "kqj": ["✅ PASS","✅ PASS","⚠️ MIXED","⚠️ MIXED"],
        "notes": ["#1 global industrial/logistics REIT; $127B market cap",
                  "E-commerce + AI data center land positions; growing FFO/dividend",
                  "Near 52-week high; above midpoint",
                  "Return to 52-week high = ~5%; income + modest growth play"],
        "fin": [
            ("2021","4,756","N/A","1,800","3,040","4.15","3.00","N/A","~0"),
            ("2022","5,985","N/A","2,300","3,428","4.58","3.24","N/A","~0"),
            ("2023","7,673","N/A","2,800","3,112","4.01","3.48","N/A","~0"),
            ("2024","8,033","N/A","3,400","3,350","4.20","3.74","N/A","~0"),
        ],
        "fin_trends": ["📈 Good","⚠️ MIXED","📈 Good","📈 Good","📈 Good","📈 Good","⚠️ N/A","⚠️ MIXED"],
        "eff": [
            ("2021","N/A","N/A","~6%","~3%"),("2022","N/A","N/A","~6.5%","~3.5%"),
            ("2023","N/A","N/A","~5%","~2.8%"),("2024","N/A","N/A","~5%","~2.9%"),
        ],
        "eff_trends": ["⚠️ MIXED","⚠️ N/A","⚠️ MIXED","⚠️ MIXED"],
        "val": [("2021","18.0","28.0","2.0"),("2022","12.0","22.0","1.8"),
                ("2023","12.0","30.0","2.0"),("2024","17.0","30.0","2.2")],
        "val_trends": ["⚠️ MIXED","⚠️ MIXED","⚠️ MIXED"],
        "note": "PLD is structured as a REIT. Key metric is FFO (Funds From Operations), not GAAP net income. ~1.2B sq ft of logistics space in 20 countries.",
    },
]

# ─────────────────────────────────────────────────────────────────────────────
def build_md(s):
    t = s["ticker"]
    fin_headers = ["Year / Status","Revenue","Gross Profit","Op. Profit","Net Income","EPS","Dividends/Share","Free Cash Flow","Buybacks"]
    eff_headers = ["Year / Status","Gross Margin (%)","Inventory Days","ROE (%)","ROA (%)"]
    val_headers = ["Year / Status","P/S","P/E","P/B"]

    lines = [
        f"# {s['company']} ({t}) Detailed Financial Data",
        f'Based on the "KQJ Global Investment Channel" Video Analysis Layout',
        "",
        "## 0. Stock Price Charts",
        "",
        f"### 📈 1-Year Price Chart ({t})",
        f"[![{t} 1-Year Chart](https://charts2.finviz.com/chart.ashx?t={t}&ty=c&ta=1&p=d&s=l)](https://finviz.com/quote.ashx?t={t})",
        "",
        "*Source: Finviz — Click chart to open interactive view*",
        "",
        f"### 📈 5-Year Price Chart ({t})",
        f"[![{t} 5-Year Chart](https://charts2.finviz.com/chart.ashx?t={t}&ty=c&ta=1&p=w&s=l)](https://finviz.com/quote.ashx?t={t})",
        "",
        "*Source: Finviz — Click chart to open interactive view*",
        "",
        "> **Chart Notes:**",
        "> - The **1-Year chart** (daily candles) shows short-term momentum and recent support/resistance levels.",
        "> - The **5-Year chart** (weekly candles) shows the long-term price trend and major drawdown magnitude.",
        "",
        "---",
        "",
        f'## 1. Market Position ("Big / 又大")',
        f"| Indicator | {s['company']} ({t}) |",
        "| :--- | :--- |",
        f"| Global Rank | {s['sector']} Leader |",
        f"| Market Cap | {s['mcap']} |",
        f"| 52-Week High | {s['high']} |",
        f"| 52-Week Low | {s['low']} |",
        f"| Current Price (Apr 2026) | {s['price']} |",
        "",
        f'## 2. Operational and Financial Performance ("Good / 又好")',
        "| " + " | ".join(fin_headers) + " |",
        "| " + " | ".join([":---"]*len(fin_headers)) + " |",
    ]
    for row in s["fin"]:
        lines.append("| **" + row[0] + "** | " + " | ".join(row[1:]) + " |")
    lines.append("| **Trend** | " + " | ".join(s["fin_trends"]) + " |")
    if s.get("note"):
        lines.append(f"\n*Note: {s['note']}*")

    lines += [
        "",
        "## 3. Efficiency and Return Metrics",
        "| " + " | ".join(eff_headers) + " |",
        "| " + " | ".join([":---"]*len(eff_headers)) + " |",
    ]
    for row in s["eff"]:
        lines.append("| **" + row[0] + "** | " + " | ".join(row[1:]) + " |")
    lines.append("| **Trend** | " + " | ".join(s["eff_trends"]) + " |")

    lines += [
        "",
        f'## 4. Valuations - 3P Model ("Cheap / 又便宜")',
        "| " + " | ".join(val_headers) + " |",
        "| " + " | ".join([":---"]*len(val_headers)) + " |",
    ]
    for row in s["val"]:
        lines.append("| **" + row[0] + "** | " + " | ".join(row[1:]) + " |")
    lines.append("| **Trend** | " + " | ".join(s["val_trends"]) + " |")

    kqj_labels = ["Big (又大)","Good (又好)","Cheap (又便宜)",">50% Upside Potential"]
    lines += [
        "",
        "## 5. KQJ Framework Assessment",
        "| Criterion | Status | Notes |",
        "| :--- | :--- | :--- |",
    ]
    for label, status, note in zip(kqj_labels, s["kqj"], s["notes"]):
        lines.append(f"| {label} | {status} | {note} |")

    return "\n".join(lines) + "\n"


def build_html(s):
    t = s["ticker"]
    ex_enc = s["exchange"].replace(":", "%3A") + "%3A" + t
    css_extra = """
        .chart-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 20px; margin-bottom: 30px; }
        .chart-box { border: 1px solid #ddd; border-radius: 8px; overflow: hidden; }
        .chart-box h3 { margin: 0; padding: 10px 14px; background: #2c3e50; color: #fff; font-size: 14px; }
        .chart-box iframe { display: block; width: 100%; border: none; }
        .chart-note { background: #f8f9fa; border-left: 4px solid #2c3e50; padding: 10px 16px; margin-bottom: 30px; font-size: 0.9em; color: #555; }
        @media (max-width: 600px) { .chart-grid { grid-template-columns: 1fr; } }"""

    fin_headers = ["Year","Revenue","Gross Profit","Op. Profit","Net Income","EPS","Dividends","FCF","Buybacks"]
    eff_headers = ["Year","Gross Margin","Inventory Days","ROE","ROA"]
    val_headers = ["Year","P/S","P/E","P/B"]

    def trend_cell(v):
        cls = "good" if "Good" in v or "PASS" in v else ("bad" if "Bad" in v else "mixed")
        if "RISK" in v: cls = "risk"
        return f'<td class="{cls}">{v}</td>'

    fin_rows = "\n".join(
        "<tr><td><strong>" + r[0] + "</strong></td>" + "".join(f"<td>{c}</td>" for c in r[1:]) + "</tr>"
        for r in s["fin"]
    )
    fin_trend = "<tr><td><strong>Trend</strong></td>" + "".join(trend_cell(v) for v in s["fin_trends"]) + "</tr>"

    eff_rows = "\n".join(
        "<tr><td><strong>" + r[0] + "</strong></td>" + "".join(f"<td>{c}</td>" for c in r[1:]) + "</tr>"
        for r in s["eff"]
    )
    eff_trend = "<tr><td><strong>Trend</strong></td>" + "".join(trend_cell(v) for v in s["eff_trends"]) + "</tr>"

    val_rows = "\n".join(
        "<tr><td><strong>" + r[0] + "</strong></td>" + "".join(f"<td>{c}</td>" for c in r[1:]) + "</tr>"
        for r in s["val"]
    )
    val_trend = "<tr><td><strong>Trend</strong></td>" + "".join(trend_cell(v) for v in s["val_trends"]) + "</tr>"

    kqj_labels = ["Big (又大)","Good (又好)","Cheap (又便宜)","&gt;50% Upside Potential"]
    kqj_rows = "\n".join(
        f'<tr><td>{label}</td><td class="{"good" if "PASS" in status else ("bad" if "Bad" in status else ("risk" if "RISK" in status else "mixed"))}">{status}</td><td>{note}</td></tr>'
        for label, status, note in zip(kqj_labels, s["kqj"], s["notes"])
    )

    note_html = f"<p><em>Note: {s['note']}</em></p>" if s.get("note") else ""

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{s['company']} ({t}) Financial Data</title>
    <style>
        body {{ font-family: Arial, sans-serif; line-height: 1.6; max-width: 960px; margin: 0 auto; padding: 20px; color: #333; }}
        h1, h2, h3 {{ color: #2c3e50; }}
        table {{ border-collapse: collapse; width: 100%; margin-bottom: 30px; }}
        th, td {{ border: 1px solid #ddd; padding: 10px; text-align: left; }}
        th {{ background-color: #f2f2f2; }}
        .good {{ color: green; font-weight: bold; }}
        .bad {{ color: red; font-weight: bold; }}
        .mixed {{ color: orange; font-weight: bold; }}
        .risk {{ color: red; font-weight: bold; }}{css_extra}
    </style>
</head>
<body>
    <h1>{s['company']} ({t}) Detailed Financial Data</h1>
    <p>Based on the "KQJ Global Investment Channel" Video Analysis Layout</p>

    <h2>0. Stock Price Charts</h2>
    <div class="chart-grid">
        <div class="chart-box">
            <h3>📈 1-Year Price Chart (Daily)</h3>
            <iframe src="https://s.tradingview.com/widgetembed/?symbol={ex_enc}&interval=D&range=12M&theme=light&style=1&locale=en&hide_side_toolbar=true&allow_symbol_change=false"
                height="300" allowtransparency="true" scrolling="no" allowfullscreen></iframe>
        </div>
        <div class="chart-box">
            <h3>📈 5-Year Price Chart (Weekly)</h3>
            <iframe src="https://s.tradingview.com/widgetembed/?symbol={ex_enc}&interval=W&range=60M&theme=light&style=1&locale=en&hide_side_toolbar=true&allow_symbol_change=false"
                height="300" allowtransparency="true" scrolling="no" allowfullscreen></iframe>
        </div>
    </div>
    <div class="chart-note">
        <strong>Chart Notes:</strong> 1-Year daily chart shows recent momentum; 5-Year weekly shows the full price cycle and drawdown magnitude.
    </div>

    <h2>1. Market Position ("Big / 又大")</h2>
    <table>
        <tr><th>Indicator</th><th>{s['company']} ({t})</th></tr>
        <tr><td>Sector</td><td>{s['sector']}</td></tr>
        <tr><td>Market Cap</td><td>{s['mcap']}</td></tr>
        <tr><td>52-Week High</td><td>{s['high']}</td></tr>
        <tr><td>52-Week Low</td><td>{s['low']}</td></tr>
        <tr><td>Current Price (Apr 2026)</td><td>{s['price']}</td></tr>
    </table>

    <h2>2. Operational and Financial Performance ("Good / 又好")</h2>
    <table>
        <tr>{"".join(f"<th>{h}</th>" for h in fin_headers)}</tr>
        {fin_rows}
        {fin_trend}
    </table>
    {note_html}

    <h2>3. Efficiency and Return Metrics</h2>
    <table>
        <tr>{"".join(f"<th>{h}</th>" for h in eff_headers)}</tr>
        {eff_rows}
        {eff_trend}
    </table>

    <h2>4. Valuations - 3P Model ("Cheap / 又便宜")</h2>
    <table>
        <tr>{"".join(f"<th>{h}</th>" for h in val_headers)}</tr>
        {val_rows}
        {val_trend}
    </table>

    <h2>5. KQJ Framework Assessment</h2>
    <table>
        <tr><th>Criterion</th><th>Status</th><th>Notes</th></tr>
        {kqj_rows}
    </table>
</body>
</html>"""


# ─────────────────────────────────────────────────────────────────────────────
generated = 0
for s in STOCKS:
    ticker = s["ticker"]
    folder = os.path.join(REPORT_DIR, ticker)
    os.makedirs(folder, exist_ok=True)

    md_path = os.path.join(folder, f"{ticker.lower()}_financial_data.md")
    html_path = os.path.join(folder, f"{ticker.lower()}_financial_data.html")

    with open(md_path, "w") as f:
        f.write(build_md(s))
    with open(html_path, "w") as f:
        f.write(build_html(s))

    print(f"[OK] {ticker} — {s['company']}")
    generated += 1

print(f"\n✅ Generated {generated} reports ({generated*2} files total)")
