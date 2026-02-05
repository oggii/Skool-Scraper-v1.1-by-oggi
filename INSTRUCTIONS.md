# 📖 Setup & Usage Instructions

Follow this guide to get the Skool Scraper up and running completely from scratch.

## 1. Get Your Cookies 🍪
The scraper needs your "Session Cookies" to log in as you. **It cannot log in with username/password.**

1.  Open Chrome/Edge and log in to [Skool.com](https://www.skool.com).
2.  Install the [EditThisCookie](https://chrome.google.com/webstore/detail/editthiscookie/fngmhnnpilhplaeedfedHEZmremgdi) extension.
3.  Click the extension icon while on Skool.com.
4.  Click the "Export" button (door icon with an arrow). This copies the cookies to your clipboard.
5.  Open `cookies.json` in this folder (rename `cookies.example.json` if needed).
6.  Paste the content and save.

**Important**: If you log out of Skool manually in your browser, these cookies will die. If the scraper stops working, just repeat this step.

## 2. Configure Target URL 🎯
Tell the scraper which community you want to tackle.

1.  Open `config/settings.json` (or rename `secrets.example.json` to `secrets.json` in the root).
2.  Set `target_url` to the "Classroom" link of your community.
    *   Example: `https://www.skool.com/my-community-name/classroom`
    *   *Note: You can also set this directly in the Dashboard Settings tab.*

## 3. Launching 🚀

1.  Open a terminal in this folder.
2.  Run the dashboard:
    ```bash
    python dashboard/app.py
    ```
3.  Open your browser to: `http://localhost:8000`

## 4. The Workflow 🔄

1.  **Run Mapper**:
    *   Click the "Run Mapper" button in the dashboard.
    *   A hidden browser will open, visit every module, and build a map.
    *   *Wait for it to say "[FINISH] Deep Map Complete."*

2.  **Verify Map**:
    *   Go to the "Course Map" tab to see everything it found.
    *   Check if "Assets=YES" for modules you know have files.

3.  **Download**:
    *   Go to the "Download" tab.
    *   Click "Start Downloading Everything".
    *   Videos, PDFs, and HTML files will appear in your `downloads/` folder.

## ⚠️ Troubleshooting

**"WinError 32: The process cannot access the file..."**
*   This happens when `yt-dlp` tries to rename a video while Windows is still scanning it.
*   **Fix**: The scraper has auto-retry logic built-in. Just let it run; it will wait 10 seconds and try again automatically.

**"Cookies file must be Netscape formatted"**
*   **Fix**: The scraper now handles this automatically! It converts your `cookies.json` to `cookies_netscape.txt` every time you start a download. You don't need to do anything.

**"Downloads failing? (403 Forbidden)"**
*   Your cookies might be expired.
*   **Fix**: Go back to Step 1, export fresh cookies from Chrome, and paste them into `cookies.json`.
