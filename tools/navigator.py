import json
import os
import random
import time
from playwright.sync_api import sync_playwright
from pathlib import Path

def get_project_root():
    return Path(__file__).parent.parent

def load_config():
    settings_path = get_project_root() / "config" / "settings.json"
    secrets_path = get_project_root() / "secrets.json"
    config = {}
    if secrets_path.exists():
        with open(secrets_path, "r") as f:
            config.update(json.load(f))
    if settings_path.exists():
        with open(settings_path, "r") as f:
            config.update(json.load(f))
    return config

def load_cookies():
    path = get_project_root() / "cookies.json"
    if not path.exists():
        raise FileNotFoundError("cookies.json not found")
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def init_browser(headless=False):
    p = sync_playwright().start()
    browser = p.chromium.launch(
        headless=headless,
        args=[
            "--disable-blink-features=AutomationControlled",
            "--no-sandbox",
            "--disable-infobars"
        ]
    )
    config = load_config()
    user_agent = config.get("user_agent", "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
    context = browser.new_context(
        user_agent=user_agent,
        viewport={"width": 1280, "height": 720},
        locale="en-US"
    )
    try:
        cookies = load_cookies()
        for c in cookies:
            if "sameSite" in c and c["sameSite"] not in ["Strict", "Lax", "None"]:
                del c["sameSite"]
        context.add_cookies(cookies)
        print("   [COOKIE] Injected successfully.")
    except Exception as e:
        print(f"   [WARN] Cookie Injection: {e}")
    page = context.new_page()
    return p, browser, context, page
