# 📈 Global Stock Screener & Reporter (KQJ Methodology)

An automated tool for screening and generating detailed financial reports for global stocks (US, Taiwan, Japan). This tool strictly adheres to the **KQJ Global Investment** methodology for calculating true business performance.

## 💡 Methodology Credits
The calculation logic, efficiency metrics, and valuation frameworks used in this tool are based on the methodology shared by **KQJ Global Investment**.
- **YouTube Channel:** [KQJ Global Investment / 投資看國際](https://www.youtube.com/@KQJ-stock-analyst)

## 🚀 Key Features
- **Global Coverage**: Supports S&P 500, NASDAQ-100, Nikkei 225, and TWSE/TPEx markets.
- **KQJ Metrics**: Implementation of Average-based ROE/ROA, DSO (Days Sales Outstanding), and custom Free Cash Flow (OCF - WC - CapEx).
- **Historical Snapshots**: Annual valuation tables (P/S, P/E, P/B) based on exact Fiscal Year-End closing prices.
- **Interactive Dashboards**: Premium HTML dashboards with automated ticker-to-report linking.

## 📊 Latest Reports
The `report/last/` folder always contains the most recently generated screening results.
Click the links below to open the interactive dashboards directly on GitHub:

| Market | Interactive Dashboard |
| :--- | :--- |
| 🇺🇸 US (S&P 500 / NASDAQ) | [dma_200_screen_result_link_us.html](report/last/dma_200_screen_result_link_us.html) |
| 🇹🇼 Taiwan (TWSE / TPEx) | [dma_200_screen_result_link_tw.html](report/last/dma_200_screen_result_link_tw.html) |
| 🇯🇵 Japan (Nikkei 225) | [dma_200_screen_result_link_jp.html](report/last/dma_200_screen_result_link_jp.html) |

> [!NOTE]
> GitHub renders HTML files as raw code. To view the interactive dashboard, download the file and open it in a browser, or use the [Mobile Viewing Guide](#-mobile-viewing-guides) to serve it via a local server.

## 📱 Mobile Viewing Guides
If you want to view the generated HTML reports on your Android/iOS device with working links, please follow the guides below:
- 🇺🇸 [English Mobile Guide](OPEN_IN_PHONE_ENGLISH_VERSION.md)
- 🇹🇼 [中文行動裝置查看指南](OPEN_IN_PHONE_CHINESE_VERSION.md)

---

## 🛠️ Getting Started

### 📦 How to Download (ZIP)
If you are not using Git, you can download the entire repository as a ZIP file:
1. Click the green **Code** button at the top of this GitHub page.
2. Select **Download ZIP**.
3. Extract the `invest-master` folder to your computer or phone.

### ⚙️ Installation (for Developers)
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### Usage
Use the provided `Makefile` to run the pipeline:
- `make all`: Run full pipeline for all markets.
- `make pipeline-us`: Run US market only.
- `make pipeline-tw`: Run Taiwan market only.
- `make pipeline-jp`: Run Japan market only.

For detailed calculation logic, see [doc/report_logic_guide.md](doc/report_logic_guide.md).
