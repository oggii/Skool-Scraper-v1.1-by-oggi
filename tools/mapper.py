from navigator import init_browser, load_config
import time
import json
import os
import sys
from pathlib import Path

# Windows-safe logging
def flush_print(msg):
    msg = msg.encode('ascii', 'ignore').decode('ascii')
    print(msg)
    sys.stdout.flush()

def mapper():
    flush_print("[MAP] Visual Mapper Starting (Deep Scan v4 - Resource Focus)...")
    try:
        p, browser, context, page = init_browser(headless=True)
        config = load_config()
        
        base_url = config.get("target_url", "").rstrip('/')
        if not base_url:
            flush_print("[ERROR] Target URL not set.")
            return

        classroom_url = base_url if "/classroom" in base_url.lower() else base_url + "/classroom"
        
        flush_print(f"[NAV] Accessing Classroom: {classroom_url}")
        page.goto(classroom_url, wait_until="domcontentloaded", timeout=60000)
        time.sleep(5)
        
        courses_data = page.evaluate("() => window.__NEXT_DATA__?.props?.pageProps?.allCourses || []")
        flush_print(f"[OK] Found {len(courses_data)} total courses.")
        
        full_map = {"courses": []}
        
        for idx, c_meta in enumerate(courses_data):
            title = c_meta['metadata']['title']
            slug = c_meta.get('name')
            
            if not slug or not c_meta['metadata'].get('hasAccess'):
                flush_print(f"\n[SKIP] {title}")
                continue
            
            flush_print(f"\n[COURSE {idx+1}/{len(courses_data)}] Scanning: {title}")
            course_url = f"{classroom_url}/{slug}"
            page.goto(course_url, wait_until="domcontentloaded", timeout=45000)
            time.sleep(5)

            hierarchy = page.evaluate("""() => {
                const props = window.__NEXT_DATA__.props.pageProps;
                function build(node) {
                    const c = node.course || node;
                    return { id: c.id, title: c.metadata?.title || c.name, unitType: c.unitType, children: (node.children || c.children || []).map(build), metadata: {} };
                }
                return props.course?.children?.map(build) || [];
            }""")

            def deep_scan_list(nodes, depth=0):
                indent = "      " + ("  " * depth)
                for node in nodes:
                    if node['unitType'] == 'module':
                        flush_print(f"{indent}[FETCH] Analyzing: {node['title']}...")
                        murl = f"{course_url}?md={node['id']}"
                        
                        try:
                            # Visit module to hydrate both JSON and DOM
                            page.goto(murl, wait_until="domcontentloaded", timeout=30000)
                            time.sleep(4) 
                            
                            # Advanced Extraction: JSON state + Aggressive DOM Scraping
                            extraction = page.evaluate(f"""(mid) => {{
                                const pp = window.__NEXT_DATA__.props.pageProps;
                                let meta = {{}};
                                
                                // 1. Recursive JSON Search
                                function findMeta(obj) {{
                                    if (!obj || typeof obj !== 'object') return null;
                                    if (obj.id === mid && obj.metadata) return obj.metadata;
                                    for (let k in obj) {{
                                        let res = findMeta(obj[k]);
                                        if (res) return res;
                                    }}
                                    return null;
                                }}
                                const jsonMeta = findMeta(pp);
                                if (jsonMeta) meta = {{ ...jsonMeta }};

                                // 2. Aggressive DOM Scraping for Resources/Attachments
                                // Look for anything that looks like a resource link
                                const attachments = [];
                                
                                // Selector for Skool's resource list items + common external hosts
                                const resourceElements = Array.from(document.querySelectorAll('a[href*="/f/"], a[href*="assets.skool.com"], a[href*="notion.site"], a[href*="airtable.com"], a[href*="drive.google.com"], a[href*="dropbox.com"], a[href*="docs.google.com"], a[href*="tally.so"]'));
                                
                                // Also look specifically for text following the "Resources" heading
                                const resHeading = Array.from(document.querySelectorAll('h1, h2, h3, div')).find(el => el.innerText.trim() === 'Resources');
                                if (resHeading) {{
                                    const nextEl = resHeading.nextElementSibling;
                                    if (nextEl) {{
                                        const resLinks = nextEl.querySelectorAll('a');
                                        resLinks.forEach(a => {{
                                            attachments.push({{ name: a.innerText.trim(), url: a.href }});
                                        }});
                                    }}
                                }}

                                resourceElements.forEach(a => {{
                                    const name = a.innerText.trim() || a.href.split('/').pop().split('?')[0];
                                    if (!attachments.find(ex => ex.url === a.href)) {{
                                        attachments.push({{ name: name, url: a.href }});
                                    }}
                                }});

                                if (attachments.length > 0) {{
                                    meta.resource_links = attachments;
                                }}

                                // 3. Ensure Description exists (DOM fallback)
                                if (!meta.desc) {{
                                    const descEl = document.querySelector('.styled-content');
                                    if (descEl) meta.desc = descEl.innerHTML;
                                }}
                                
                                return meta;
                            }}""", node['id'])
                            
                            node['metadata'] = extraction
                            
                            if extraction:
                                has_v = "YES" if extraction.get('videoLink') else "NO"
                                has_a = "YES" if (extraction.get('attachments') or extraction.get('resource_links')) else "NO"
                                flush_print(f"{indent}[OK] Found: Video={has_v}, Assets={has_a}")
                            else:
                                flush_print(f"{indent}[WARN] Empty Module.")
                        except Exception as e:
                            flush_print(f"{indent}[ERR] Fail: {e}")
                    else:
                        flush_print(f"{indent}[FOLDER] {node['title']}...")
                        deep_scan_list(node.get('children', []), depth + 1)

            deep_scan_list(hierarchy)
            full_map["courses"].append({"title": title, "details": {"hierarchy": hierarchy}})

        with open("map.json", "w", encoding="utf-8") as f:
            json.dump(full_map, f, indent=2)
            
        flush_print("\n[FINISH] Deep Map Complete.")
        browser.close()
        p.stop()
    except Exception as e:
        flush_print(f"\n[CRITICAL ERROR] {e}")
        if 'browser' in locals(): browser.close()
        if 'p' in locals(): p.stop()

if __name__ == "__main__":
    mapper()
