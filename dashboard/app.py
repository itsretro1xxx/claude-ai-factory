"""Status dashboard for the Claude AI Factory repo.

Reads ROADMAP.md and each room's README.md straight from disk and renders a
single-page overview: roadmap phase progress plus a card per room. No
third-party dependencies, so `python app.py` works out of the box.
"""
import html
import re
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
HOST = "0.0.0.0"
PORT = 8000

ROOMS = [
    ("Research Hub", "research-hub"),
    ("Etsy Print-on-Demand", "etsy-print-on-demand"),
    ("YouTube Shorts Automation", "youtube-shorts-automation"),
]


def parse_roadmap(text):
    phases = []
    current = None
    for line in text.splitlines():
        heading = re.match(r"^##\s+(.*)", line)
        if heading:
            current = {"title": heading.group(1).strip(), "done": 0, "total": 0}
            phases.append(current)
            continue
        item = re.match(r"^\s*-\s+\[( |x|X)\]\s+(.*)", line)
        if item and current is not None:
            current["total"] += 1
            if item.group(1).lower() == "x":
                current["done"] += 1
    return phases


def parse_room_readme(path):
    if not path.exists():
        return {"title": path.parent.name, "summary": ""}
    text = path.read_text()
    title_match = re.search(r"^#\s+(.*)", text, re.MULTILINE)
    title = title_match.group(1).strip() if title_match else path.parent.name
    paragraphs = re.split(r"\n\s*\n", text[title_match.end():].strip() if title_match else text)
    summary = ""
    for para in paragraphs:
        para = para.strip()
        if para and not para.startswith("#") and not para.startswith("|"):
            summary = re.sub(r"\s+", " ", para)
            break
    return {"title": title, "summary": summary}


def gather_status():
    roadmap_path = ROOT / "ROADMAP.md"
    phases = parse_roadmap(roadmap_path.read_text()) if roadmap_path.exists() else []

    rooms = []
    for label, folder in ROOMS:
        info = parse_room_readme(ROOT / folder / "README.md")
        rooms.append({"label": label, "folder": folder, **info})

    return phases, rooms


def render_page():
    phases, rooms = gather_status()

    total_done = sum(p["done"] for p in phases)
    total_tasks = sum(p["total"] for p in phases)
    overall_pct = round(100 * total_done / total_tasks) if total_tasks else 0

    phase_rows = []
    for p in phases:
        pct = round(100 * p["done"] / p["total"]) if p["total"] else 0
        phase_rows.append(f"""
        <div class="phase">
          <div class="phase-head">
            <span>{html.escape(p['title'])}</span>
            <span class="phase-count">{p['done']}/{p['total']}</span>
          </div>
          <div class="bar"><div class="bar-fill" style="width:{pct}%"></div></div>
        </div>""")

    room_cards = []
    for r in rooms:
        room_cards.append(f"""
        <div class="card">
          <h3>{html.escape(r['label'])}</h3>
          <p>{html.escape(r['summary']) or 'No description yet.'}</p>
          <span class="folder">{html.escape(r['folder'])}/README.md</span>
        </div>""")

    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Claude AI Factory — Dashboard</title>
<style>
  :root {{ color-scheme: light dark; }}
  body {{
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
    max-width: 900px; margin: 0 auto; padding: 2rem 1.5rem 4rem;
    background: #f7f7f8; color: #1a1a1a;
  }}
  @media (prefers-color-scheme: dark) {{
    body {{ background: #16161a; color: #e6e6e6; }}
    .card, .phase {{ background: #212126 !important; border-color: #33333a !important; }}
    .bar {{ background: #33333a !important; }}
    .folder {{ color: #9a9aa5 !important; }}
  }}
  h1 {{ font-size: 1.5rem; margin-bottom: 0.25rem; }}
  .subtitle {{ color: #666; margin-top: 0; }}
  .overall {{ font-size: 0.95rem; margin: 1.5rem 0 0.5rem; font-weight: 600; }}
  .phase, .card {{
    background: #fff; border: 1px solid #e2e2e5; border-radius: 10px;
    padding: 0.9rem 1.1rem; margin-bottom: 0.7rem;
  }}
  .phase-head {{ display: flex; justify-content: space-between; font-size: 0.9rem; margin-bottom: 0.4rem; }}
  .phase-count {{ color: #888; }}
  .bar {{ height: 6px; background: #eee; border-radius: 4px; overflow: hidden; }}
  .bar-fill {{ height: 100%; background: #6c5ce7; }}
  .rooms {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(230px, 1fr)); gap: 0.8rem; margin-top: 0.5rem; }}
  .card h3 {{ margin: 0 0 0.4rem; font-size: 1rem; }}
  .card p {{ margin: 0 0 0.5rem; font-size: 0.88rem; line-height: 1.4; color: #444; }}
  @media (prefers-color-scheme: dark) {{ .card p {{ color: #c2c2c8; }} }}
  .folder {{ font-size: 0.75rem; color: #999; font-family: monospace; }}
  section {{ margin-top: 2rem; }}
  section > h2 {{ font-size: 1.05rem; margin-bottom: 0.6rem; }}
</style>
</head>
<body>
  <h1>Claude AI Factory</h1>
  <p class="subtitle">Live status, read straight from README.md / ROADMAP.md</p>

  <section>
    <h2>Roadmap progress</h2>
    <div class="overall">Overall: {total_done}/{total_tasks} tasks ({overall_pct}%)</div>
    {''.join(phase_rows) or '<p>No ROADMAP.md found.</p>'}
  </section>

  <section>
    <h2>Rooms</h2>
    <div class="rooms">
      {''.join(room_cards)}
    </div>
  </section>
</body>
</html>"""


class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path not in ("/", "/index.html"):
            self.send_response(404)
            self.end_headers()
            return
        body = render_page().encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, fmt, *args):
        pass


def main():
    server = ThreadingHTTPServer((HOST, PORT), Handler)
    print(f"Dashboard running at http://localhost:{PORT}")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()


if __name__ == "__main__":
    main()
