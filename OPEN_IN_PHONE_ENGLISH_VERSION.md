# 📱 Viewing Reports on Mobile
### 🇬🇧 English Version

If you have downloaded the HTML reports from the `report` folder to your Android device, you might notice that links between files (e.g., clicking a ticker in the dashboard) do not work when opened directly in Chrome.

## 🔒 Why are links blocked?
Modern mobile browsers enforce strict **File System Sandboxing**. When you open local files directly, Chrome treats cross-linking as a security risk and blocks the navigation.

**The Solution:** Use **Termux** to run a lightweight local web server. By serving files over `http://localhost`, Chrome treats your reports like a standard website, allowing all links to work perfectly.

---

## 🚀 Step-by-Step Guide

### 1. Download the Repository
Save the repository folder (e.g., `invest-master`) to your phone's **Documents** folder.

### 2. Install Termux
Install the [Termux](https://termux.dev/) app on your Android device (available via F-Droid or Play Store).

### 3. Grant Storage Permissions
Open Termux and run the following command to allow access to your phone's storage:
```bash
termux-setup-storage
```

> [!IMPORTANT]
> A popup will appear on your phone. **Grant the permission** to allow Termux to see your files.

### 4. Navigate to the Folder
Change your directory to where you saved the repository:
```bash
cd ~/storage/shared/Documents/invest-master
```

### 5. Start the Local Web Server
We will use Python to serve the files. If you haven't installed it yet, run:
```bash
pkg install python
```

Then, start the server:
```bash
python -m http.server 8080
```

### 6. View in Chrome
Open Chrome on your phone and navigate to:
**[http://localhost:8080](http://localhost:8080)**

You can now navigate to your reports (e.g., `report/last/dma_200_screen_result_link_tw.html`) and all ticker links will be fully interactive!

---

## ⚠️ Important Notes

> [!CAUTION]
> **Keep Termux Running:** If you close Termux or if Android's battery optimizer kills it, the `localhost` link will stop working. Keep Termux active in the background while viewing.

> [!TIP]
> **Use Relative Paths:** Always use relative paths (e.g., `./ticker_data.html`) in your HTML to ensure they work correctly across both PC and Mobile servers.

---

## 💡 Methodology Credits
The reporting methodology used in this project is based on the frameworks developed by **KQJ Global Investment**. For more investment insights, visit their [YouTube Channel](https://www.youtube.com/@KQJ-stock-analyst).

