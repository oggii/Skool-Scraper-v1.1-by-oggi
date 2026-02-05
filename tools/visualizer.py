import json
import os

def generate_html_map():
    with open("map.json", "r", encoding="utf-8") as f:
        data = json.load(f)
        
    courses = data.get("courses", [])
    
    html = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Community Map - Skool Scraper</title>
        <style>
            body { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif; background: #f8f9fa; color: #333; margin: 0; padding: 20px; }
            h1 { text-align: center; }
            .container { max-width: 800px; margin: 0 auto; }
            .course-card { background: white; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); margin-bottom: 20px; overflow: hidden; }
            .course-header { padding: 15px 20px; background: #fff; border-bottom: 1px solid #eee; display: flex; justify-content: space-between; align-items: center; cursor: pointer; }
            .course-header:hover { background: #f1f3f5; }
            .course-title { font-weight: 600; font-size: 1.1em; }
            .locked-badge { background: #e9ecef; color: #868e96; padding: 4px 8px; border-radius: 4px; font-size: 0.8em; }
            .course-content { padding: 0 20px; display: none; }
            .set-group { margin: 15px 0; border-left: 2px solid #eee; padding-left: 10px; }
            .set-header { display: flex; align-items: center; cursor: pointer; padding: 5px 0; }
            .set-title { font-weight: 600; color: #555; }
            .module-list { list-style: none; padding: 0; }
            .module-item { padding: 8px 0; border-bottom: 1px solid #f1f1f1; display: flex; align-items: center; flex-wrap: wrap; }
            .module-item:last-child { border-bottom: none; }
            .module-icon { margin-right: 10px; color: #228be6; }
            .badge { padding: 2px 6px; border-radius: 4px; font-size: 0.7em; margin-left: 8px; display: inline-flex; align-items: center; }
            .video-badge { background: #e7f5ff; color: #228be6; }
            .attachment-badge { background: #fff3bf; color: #f08c00; }
            .details-open { display: block; padding-bottom: 20px; }
            .toggle-icon { margin-right: 5px; font-size: 0.8em; color: #999; }
        </style>
        <script>
            function toggleCourse(id) {
                const content = document.getElementById('content-' + id);
                if (content.style.display === 'block') {
                    content.style.display = 'none';
                } else {
                    content.style.display = 'block';
                }
            }
             function toggleSet(id) {
                const content = document.getElementById('set-content-' + id);
                const icon = document.getElementById('set-icon-' + id);
                if (content.style.display === 'none') {
                    content.style.display = 'block';
                    icon.innerText = '▼';
                } else {
                    content.style.display = 'none';
                    icon.innerText = '▶';
                }
            }
        </script>
    </head>
    <body>
        <div class="container">
            <h1>Community Map</h1>
            <p style="text-align:center; color:#777">Scanned at: """ + data.get('scanned_at', 'Unknown') + """</p>
    """
    
    for c in courses:
        locked = c.get('locked', False)
        details = c.get('details', {})
        hierarchy = details.get('hierarchy', [])
        
        # Fallback
        if not hierarchy:
            sets = details.get('sets', [])
            modules = details.get('modules', [])
            if sets or modules:
                 hierarchy = modules + sets

        has_content = len(hierarchy) > 0
        
        # Recursive renderer
        def render_node(node):
            title = node.get('title') or "Untitled"
            unit_type = node.get('unitType', 'module')
            children = node.get('children', [])
            nid = node.get('id')
            
            html_out = ""
            
            if unit_type == 'set':
                # Render as a collapsible group
                child_html = "".join([render_node(child) for child in children])
                html_out += f"""
                <div class="set-group">
                    <div class="set-header" onclick="toggleSet('{nid}')">
                        <span id="set-icon-{nid}" class="toggle-icon">▼</span>
                        <div class="set-title">📁 {title}</div>
                    </div>
                    <div id="set-content-{nid}" class="set-content" style="padding-left: 10px; display: block;">
                        {child_html}
                    </div>
                </div>
                """
            else:
                # Render as module
                meta = node.get('metadata', {})
                video_ms = meta.get('videoLenMs')
                attachments = meta.get('attachments', [])
                
                badges = ""
                if video_ms:
                    mins = round(video_ms / 1000 / 60)
                    badges += f'<span class="badge video-badge">🎥 {mins}m</span>'
                
                if attachments:
                    badges += f'<span class="badge attachment-badge">📎 {len(attachments)} Files</span>'
                
                html_out += f'<div class="module-item"><span class="module-icon">📄</span>{title}{badges}</div>'
                
            return html_out

        content_html = ""
        if has_content:
             content_html += '<div class="course-structure">'
             for item in hierarchy:
                 content_html += render_node(item)
             content_html += '</div>'
        
        onClick = f"onclick=\"toggleCourse('{c['id']}')\"" if has_content else ""
        cursor = "cursor: pointer;" if has_content else "cursor: default;"
        
        html += f"""
            <div class="course-card">
                <div class="course-header" {onClick} style="{cursor}">
                    <span class="course-title">{c['title']}</span>
                    <div>
                        {'<span class="locked-badge">🔒 Locked</span>' if locked else ''}
                        {'<span>🔽</span>' if has_content else ''}
                    </div>
                </div>
                <div id="content-{c['id']}" class="course-content">
                    {content_html if has_content else '<p style="padding:10px; color:#999">No visible modules.</p>'}
                </div>
            </div>
        """
        
    html += """
        </div>
    </body>
    </html>
    """
    
    with open("map.html", "w", encoding="utf-8") as f:
        f.write(html)
        
    print("✅ Created map.html")

if __name__ == "__main__":
    generate_html_map()
