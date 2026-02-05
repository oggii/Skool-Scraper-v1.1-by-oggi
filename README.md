# 🎓 Skool Scraper v1.1 by oggi

A robust, "deep-dive" scraper for Skool.com communities. This tool is designed to map entire course structures, extract all metadata (including hidden assets, internal links, and external resources), and download all content (videos, PDFs, attachments) into a clean, offline-readable format.

[![Buy me a coffee](https://img.shields.io/badge/Buy%20me%20a%20coffee-Donate-yellow.svg)](https://www.paypal.com/paypalme/oggi1337)

**⚠️ DISCLAIMER: Use this tool responsibly. Only scrape communities you have legal access to.**

## 🚀 Key Features

*   **Deep Mapping Engine**: Recursively scans nested folders, sets, and modules to build a complete JSON map of the course.
*   **Smart Resource Detection**: Captures files, internal attachments, and external links (Google Drive, Dropbox, Notion, Airtable, etc.).
*   **Video Downloader (Authenticated)**: Uses `yt-dlp` with your session cookies to download videos (YouTube, Vimeo, Wistia) including restricted content.
*   **Offline HTML Generation**: Converts Skool's TipTap JSON content into clean, formatted HTML pages with embedded resources.
*   **Live Dashboard**: A beautiful, real-time UI/UX to control the scraper, monitor progress, and visualize the course map.
*   **Robust & Resilient**:
    *   **Auto-Retry**: Automatically retries failed downloads.
    *   **Cookie Conversion**: Auto-converts Playwright cookies to Netscape format for `yt-dlp`.
    *   **Resume Capability**: Skips files and videos that are already downloaded.

## 🛠️ Installation

1.  **Install Python 3.10+**: Ensure Python is installed and added to your PATH.
2.  **Install Dependencies**:
    ```bash
    pip install -r requirements.txt
    playwright install chromium
    ```
    *(Note: `yt-dlp` is required for video downloading)*

3.  **Setup Configuration**:
    *   Rename `secrets.example.json` to `secrets.json` and add your target URL.
    *   Rename `cookies.example.json` to `cookies.json` and paste your Skool cookies (see `INSTRUCTIONS.md`).

## 🖥️ Usage

1.  **Start the Dashboard**:
    ```bash
    python dashboard/app.py
    ```
2.  **Open in Browser**: Go to `http://localhost:8000`
3.  **Run Mapper**: Click "Run Mapper" to scan the community structure.
4.  **Start Download**: Click "Start Downloading" to fetch all content.

## 📂 Project Structure

*   `dashboard/`: FastAPI backend and static frontend files.
*   `tools/`: Core logic scripts (`navigator.py`, `mapper.py`, `downloader.py`).
*   `config/`: Configuration settings.
*   `downloads/`: Destination for scraped content (organized by Course Name).
*   `map.json`: The generated structure of the target community.

## 🤝 Contributing
Contributions are welcome! Please feel free to submit a Pull Request.
