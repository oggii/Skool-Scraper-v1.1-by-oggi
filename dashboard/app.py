"""
Skool Scraper Dashboard - FastAPI Backend
"""
from fastapi import FastAPI, Request, WebSocket, WebSocketDisconnect
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, JSONResponse, FileResponse
import json
import os
import asyncio
from pathlib import Path

# Get paths
BASE_DIR = Path(__file__).parent.parent
MAP_FILE = BASE_DIR / "map.json"
STATIC_DIR = Path(__file__).parent / "static"
SETTINGS_FILE = BASE_DIR / "config" / "settings.json"

# Ensure config dir exists
(BASE_DIR / "config").mkdir(exist_ok=True)

app = FastAPI(title="Skool Scraper v1.1 by oggi")

# Serve static files
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

# WebSocket connections for real-time updates
active_connections: list[WebSocket] = []

@app.get("/", response_class=HTMLResponse)
async def home():
    """Serve the main dashboard page"""
    return FileResponse(STATIC_DIR / "index.html")

def get_settings():
    if SETTINGS_FILE.exists():
        with open(SETTINGS_FILE, "r") as f:
            return json.load(f)
    return {"target_url": "", "output_dir": str(BASE_DIR / "downloads")}

def save_settings(settings):
    with open(SETTINGS_FILE, "w") as f:
        json.dump(settings, f, indent=4)

@app.get("/api/settings")
async def api_get_settings():
    return get_settings()

@app.post("/api/settings")
async def api_save_settings(settings: dict):
    current = get_settings()
    current.update(settings)
    save_settings(current)
    return {"success": True}

@app.get("/api/pick-folder")
async def pick_folder():
    """Trigger a native Windows folder picker"""
    import tkinter as tk
    from tkinter import filedialog
    
    root = tk.Tk()
    root.withdraw() # Hide the main window
    root.attributes('-topmost', True) # Bring to front
    
    folder_selected = filedialog.askdirectory()
    root.destroy()
    
    if folder_selected:
        return {"folder": folder_selected}
    return {"folder": None}

@app.get("/api/map")
async def get_map():
    """Return the scraped course map"""
    if not MAP_FILE.exists():
        return JSONResponse({"error": "No map found. Run the mapper first."}, status_code=404)
    
    with open(MAP_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)
    return data

@app.get("/api/stats")
async def get_stats():
    """Return statistics about the scraped content"""
    # Check if we have settings
    settings = get_settings()
    
    if not MAP_FILE.exists():
        return {
            "courses": 0, "modules": 0, "videos": 0, "attachments": 0, 
            "has_settings": bool(settings.get("target_url")),
            "target_url": settings.get("target_url")
        }
    
    with open(MAP_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)
    
    stats = {
        "courses": len(data.get("courses", [])),
        "modules": 0,
        "videos": 0,
        "attachments": 0,
        "sets": 0,
        "has_settings": bool(settings.get("target_url")),
        "target_url": settings.get("target_url")
    }
    
    def count_nodes(nodes):
        for node in nodes:
            if node.get("unitType") == "set":
                stats["sets"] += 1
            else:
                stats["modules"] += 1
            
            meta = node.get("metadata", {})
            # Count Videos
            if meta.get("videoLenMs") or meta.get("videoLink"):
                stats["videos"] += 1
            
            # Count Attachments & Assets
            all_atts = []
            
            # 1. Standard Attachments (JSON)
            atts = meta.get("attachments", [])
            if not atts and "resources" in meta:
                atts = meta.get("resources", [])
            
            if isinstance(atts, str):
                try: atts = json.loads(atts)
                except: atts = []
            all_atts.extend(atts)
            
            # 2. Scraped Assets (DOM)
            res_links = meta.get("resource_links", [])
            for r in res_links:
                # Add if URL is unique
                r_url = r.get('url') or r.get('link')
                if r_url and not any((a.get('link') or a.get('url')) == r_url for a in all_atts):
                    all_atts.append(r)
            
            stats["attachments"] += len(all_atts)
            
            count_nodes(node.get("children", []))
    
    for course in data.get("courses", []):
        stats["courses"] += 1
        hierarchy = course.get("details", {}).get("hierarchy", [])
        count_nodes(hierarchy)
    
    return stats


from fastapi.responses import StreamingResponse

@app.post("/api/scrape")
async def start_scrape():
    """Trigger a new scrape with streaming output"""
    import subprocess
    def generate():
        process = subprocess.Popen(
            ["python", "tools/mapper.py"],
            cwd=BASE_DIR,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            encoding='utf-8',
            bufsize=1
        )
        for line in process.stdout:
            yield line
        process.stdout.close()
        process.wait()
    return StreamingResponse(generate(), media_type="text/plain")

@app.post("/api/download")
async def start_download():
    """Trigger download with streaming output"""
    import subprocess
    def generate():
        process = subprocess.Popen(
            ["python", "tools/downloader.py"],
            cwd=BASE_DIR,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            encoding='utf-8',
            bufsize=1
        )
        for line in process.stdout:
            yield line
        process.stdout.close()
        process.wait()
    return StreamingResponse(generate(), media_type="text/plain")

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket for real-time progress updates"""
    await websocket.accept()
    active_connections.append(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            # Handle incoming messages if needed
    except WebSocketDisconnect:
        active_connections.remove(websocket)

async def broadcast_progress(message: dict):
    """Send progress update to all connected clients"""
    for connection in active_connections:
        try:
            await connection.send_json(message)
        except:
            pass

if __name__ == "__main__":
    import uvicorn
    print("[START] Skool Scraper Dashboard on http://localhost:8000")
    uvicorn.run(app, host="0.0.0.0", port=8000)
