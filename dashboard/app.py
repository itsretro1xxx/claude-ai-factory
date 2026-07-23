"""Status dashboard + API for the Claude AI Factory repo.

Reads ROADMAP.md and each room's README.md straight from disk and renders a
single-page overview: roadmap phase progress plus a card per room. Also
exposes a JSON API mirroring the worker pipelines documented in each room's
README (see WORKERS below) — the generate/analyze endpoints are stubs until
an actual image/TTS/LLM backend is wired in per Roadmap Phase 0.
"""
import re
from datetime import datetime, timezone
from pathlib import Path

from flask import Flask, abort, jsonify, render_template, request

ROOT = Path(__file__).resolve().parent.parent

ROOMS = [
    ("Research Hub", "research-hub"),
    ("Etsy Print-on-Demand", "etsy-print-on-demand"),
    ("YouTube Shorts Automation", "youtube-shorts-automation"),
]

# Worker pipelines as documented in each room's README, keyed by worker name.
WORKERS = {
    "niche_picker": "etsy-print-on-demand",
    "design_generator": "etsy-print-on-demand",
    "mockup_builder": "etsy-print-on-demand",
    "listing_copywriter": "etsy-print-on-demand",
    "publisher": "etsy-print-on-demand",
    "performance_tracker": "etsy-print-on-demand",
    "topic_picker": "youtube-shorts-automation",
    "script_writer": "youtube-shorts-automation",
    "voiceover_generator": "youtube-shorts-automation",
    "video_assembler": "youtube-shorts-automation",
    "thumbnail_writer": "youtube-shorts-automation",
    "trend_scout": "research-hub",
    "niche_topic_scorer": "research-hub",
    "performance_analyst": "research-hub",
    "briefing_writer": "research-hub",
}

# In-memory call counters per worker. Resets on restart; this is a status
# dashboard, not a metrics store — swap for a real backend if that's needed.
worker_metrics = {name: {"calls": 0, "last_called": None} for name in WORKERS}

app = Flask(__name__)


@app.errorhandler(404)
def handle_not_found(err):
    if request.path.startswith("/api/"):
        return jsonify({"error": err.description}), 404
    return err


def record_worker_call(name):
    metrics = worker_metrics[name]
    metrics["calls"] += 1
    metrics["last_called"] = datetime.now(timezone.utc).isoformat()


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


@app.route("/api/factory-status")
def api_factory_status():
    phases, rooms = gather_status()
    total_done = sum(p["done"] for p in phases)
    total_tasks = sum(p["total"] for p in phases)
    overall_pct = round(100 * total_done / total_tasks) if total_tasks else 0
    return jsonify(
        {
            "overall": {"done": total_done, "total": total_tasks, "pct": overall_pct},
            "phases": phases,
            "rooms": rooms,
        }
    )


def _not_implemented(worker, note, **extra):
    record_worker_call(worker)
    return (
        jsonify(
            {
                "status": "not_implemented",
                "worker": worker,
                "room": WORKERS[worker],
                "note": note,
                **extra,
            }
        ),
        501,
    )


@app.route("/api/etsy/generate-design", methods=["POST"])
def api_etsy_generate_design():
    body = request.get_json(silent=True) or {}
    niche = body.get("niche")
    if not niche:
        return jsonify({"error": "'niche' is required"}), 400
    count = body.get("count", 3)
    return _not_implemented(
        "design_generator",
        "No image-generation backend is wired in yet — see "
        "etsy-print-on-demand/README.md pipeline step 2 and Roadmap Phase 0.",
        niche=niche,
        count=count,
    )


@app.route("/api/youtube/generate-short", methods=["POST"])
def api_youtube_generate_short():
    body = request.get_json(silent=True) or {}
    topic = body.get("topic")
    if not topic:
        return jsonify({"error": "'topic' is required"}), 400
    count = body.get("count", 1)
    return _not_implemented(
        "script_writer",
        "No script/TTS/video-assembly backend is wired in yet — see "
        "youtube-shorts-automation/README.md pipeline steps 2-4 and Roadmap Phase 0.",
        topic=topic,
        count=count,
    )


@app.route("/api/research/analyze", methods=["POST"])
def api_research_analyze():
    body = request.get_json(silent=True) or {}
    query = body.get("query")
    if not query:
        return jsonify({"error": "'query' is required"}), 400
    return _not_implemented(
        "trend_scout",
        "No trend-data backend is wired in yet — see "
        "research-hub/README.md worker roles and Roadmap Phase 4.",
        query=query,
    )


@app.route("/api/worker/<name>/metrics")
def api_worker_metrics(name):
    if name not in WORKERS:
        abort(404, description=f"Unknown worker '{name}'. Known workers: {sorted(WORKERS)}")
    metrics = worker_metrics[name]
    return jsonify({"worker": name, "room": WORKERS[name], **metrics})


if __name__ == "__main__":
    app.run(debug=True, port=8000)
