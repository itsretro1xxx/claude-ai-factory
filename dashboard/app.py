"""Status dashboard for the Claude AI Factory repo.

Reads ROADMAP.md and each room's README.md straight from disk and renders a
single-page overview: roadmap phase progress plus a card per room.
"""
import re
from pathlib import Path

from flask import Flask, render_template

ROOT = Path(__file__).resolve().parent.parent

ROOMS = [
    ("Research Hub", "research-hub"),
    ("Etsy Print-on-Demand", "etsy-print-on-demand"),
    ("YouTube Shorts Automation", "youtube-shorts-automation"),
]

app = Flask(__name__)


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
    for phase in phases:
        phase["pct"] = round(100 * phase["done"] / phase["total"]) if phase["total"] else 0
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


@app.route("/")
def index():
    phases, rooms = gather_status()
    total_done = sum(p["done"] for p in phases)
    total_tasks = sum(p["total"] for p in phases)
    overall_pct = round(100 * total_done / total_tasks) if total_tasks else 0
    return render_template(
        "index.html",
        phases=phases,
        rooms=rooms,
        total_done=total_done,
        total_tasks=total_tasks,
        overall_pct=overall_pct,
    )


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)
