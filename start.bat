@echo off
echo ===================================================
echo     Skool Scraper Dashboard - Startup Script
echo ===================================================
echo.
echo 🚀 Checking environment...

if not exist venv (
    echo ⚠️ Virtual environment not found. 
    echo Please run setup first (or install dependencies manually).
)

echo 🚀 Starting Dashboard Server...
echo 🌐 Open http://localhost:8000 in your browser
echo.

python dashboard/app.py

pause
