@echo off
echo ===================================================
echo     Skool Scraper - First Time Setup
echo ===================================================
echo.

echo 📦 Installing Python dependencies...
pip install -r requirements.txt

echo 🎭 Installing Playwright browsers...
playwright install chromium

echo.
echo ✅ Setup Complete!
echo You can now run start.bat to launch the dashboard.
pause
