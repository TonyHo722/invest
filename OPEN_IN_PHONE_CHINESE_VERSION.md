# 📱 在行動裝置上查看報告
### 🇹🇼 中文版 (Traditional Chinese)

如果您已經將 `report` 資料夾中的 HTML 報告下載到 Android 裝置，您可能會發現直接在 Chrome 中開啟時，報告之間的連結（例如點擊儀表板中的股票代號）無法正常運作。

## 🔒 為什麼連結會被阻擋？
現代行動瀏覽器實施了嚴格的 **「檔案系統沙箱」(File System Sandboxing)** 機制。當您直接開啟本機檔案時，Chrome 會將跨檔案的連結導航視為安全風險並加以阻擋。

**解決方案：** 使用 **Termux** 執行輕量級的本機網頁伺服器。透過 `http://localhost` 提供檔案服務，Chrome 會將您的報告視為一般網站，所有的連結就能完美運作。

---

## 🚀 逐步指南

### 1. 下載儲存庫
將儲存庫資料夾（例如 `invest-master`）儲存到手機的 **Documents (文件)** 資料夾中。

### 2. 安裝 Termux
在 Android 裝置上安裝 [Termux](https://termux.dev/) 應用程式（建議透過 F-Droid 或 Google Play 下載）。

### 3. 授予儲存空間權限
開啟 Termux 並執行以下指令，以允許存取手機儲存空間：
```bash
termux-setup-storage
```

> [!IMPORTANT]
> 手機畫面上會出現權限請求彈出視窗，請務必點選**「允許」**，否則 Termux 無法讀取您的檔案。

### 4. 導航至資料夾
切換到您儲存儲存庫的目錄：
```bash
cd ~/storage/shared/Documents/invest-master
```

### 5. 啟動本機網頁伺服器
我們將使用 Python 來架設伺服器。如果尚未安裝 Python，請執行：
```bash
pkg install python
```

接著啟動伺服器：
```bash
python -m http.server 8080
```

### 6. 在 Chrome 中查看
開啟手機的 Chrome 瀏覽器，前往：
**[http://localhost:8080](http://localhost:8080)**

現在您可以直接瀏覽報告（例如 `report/last/dma_200_screen_result_link_tw.html`），所有的股票連結都將變為可互動式！

---

## ⚠️ 重要注意事項

> [!CAUTION]
> **保持 Termux 執行：** 如果您關閉 Termux，或者 Android 的電池優化功能將其關閉，`localhost` 連結就會失效。查看報告時，請確保 Termux 在背景持續執行。

> [!TIP]
> **使用相對路徑：** 在製作或修改 HTML 檔案時，請務必使用相對路徑（例如 `./data.html`），以確保檔案在 PC 和行動裝置伺服器上都能正常運作。

---

## 💡 方法論致謝
本專案所使用的報表邏輯與計算方法，皆基於 **投資看國際 (KQJ Global Investment)** 所分享的投資架構。欲了解更多投資知識，請造訪他們的 [YouTube 頻道](https://www.youtube.com/@KQJ-stock-analyst)。

