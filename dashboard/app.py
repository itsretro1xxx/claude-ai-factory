"""
Dashboard - Web UI for Claude AI Factory
Main entry point for the factory dashboard
"""

from flask import Flask, render_template, jsonify, request, send_file
import asyncio
import os
from datetime import datetime, timedelta
from dotenv import load_dotenv
import json
import logging

from factory.factory import AIFactory
from workers.etsy_worker import EtsyWorker
from workers.youtube_worker import YouTubeWorker
from workers.research_worker import ResearchWorker

load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__)
app.config['JSON_SORT_KEYS'] = False

# Global factory instance
factory = None
factory_start_time = None

def init_factory():
    """Initialize the AI factory"""
    global factory, factory_start_time

    if factory is None:
        factory_start_time = datetime.now()

        config = {
            "name": "Claude AI Factory 🏭",
            "env": os.getenv("FACTORY_ENV", "development"),
            "start_time": factory_start_time.isoformat()
        }

        factory = AIFactory(config)

        # Register workers
        etsy_config = {
            "max_listings_per_run": 5,
            "design_style": "modern,minimalist,trending"
        }
        etsy_worker = EtsyWorker(etsy_config)
        factory.register_worker(etsy_worker)

        youtube_config = {
            "content_types": ["trending", "tutorial", "entertainment"],
            "shorts_per_batch": 2
        }
        youtube_worker = YouTubeWorker(youtube_config)
        factory.register_worker(youtube_worker)

        research_config = {
            "analysis_depth": "deep"
        }
        research_worker = ResearchWorker(research_config)
        factory.register_worker(research_worker)

        logger.info("Factory initialized with 3 workers")

    return factory

@app.route('/')
def dashboard():
    """Serve the main dashboard"""
    init_factory()
    return render_template('dashboard.html')

@app.route('/api/factory-status')
def get_factory_status():
    """Get current factory status"""
    init_factory()

    days_running = (datetime.now() - factory_start_time).days

    status = {
        "factory_name": factory.name,
        "days_running": days_running,
        "workers_count": len(factory.workers),
        "workers": [
            {
                "name": worker.name,
                "status": worker.status,
                "tasks_completed": len(worker.task_history),
                "metrics": worker.metrics
            }
            for worker in factory.workers
        ],
        "metrics": factory.metrics
    }

    return jsonify(status)

@app.route('/api/etsy/generate-design')
async def generate_etsy_design():
    """Generate Etsy design using Claude"""
    init_factory()

    try:
        etsy_worker = factory.workers[0]
        result = await etsy_worker.execute_task("design_generation")

        return jsonify({
            "status": "success",
            "data": result
        })
    except Exception as e:
        logger.error(f"Error generating design: {e}")
        return jsonify({
            "status": "error",
            "error": str(e)
        }), 500

@app.route('/api/youtube/generate-short')
async def generate_youtube_short():
    """Generate YouTube short script and ideas"""
    init_factory()

    try:
        youtube_worker = factory.workers[1]
        result = await youtube_worker.execute_task("script_generation")

        return jsonify({
            "status": "success",
            "data": result
        })
    except Exception as e:
        logger.error(f"Error generating short: {e}")
        return jsonify({
            "status": "error",
            "error": str(e)
        }), 500

@app.route('/api/research/analyze')
async def research_analyze():
    """Get research insights and trending ideas"""
    init_factory()

    try:
        research_worker = factory.workers[2]
        result = await research_worker.execute_task("market_research")

        return jsonify({
            "status": "success",
            "data": result
        })
    except Exception as e:
        logger.error(f"Error analyzing research: {e}")
        return jsonify({
            "status": "error",
            "error": str(e)
        }), 500

@app.route('/api/worker/<worker_name>/metrics')
def get_worker_metrics(worker_name):
    """Get specific worker metrics"""
    init_factory()

    for worker in factory.workers:
        if worker_name.lower() in worker.name.lower():
            return jsonify({
                "worker": worker.name,
                "metrics": worker.get_metrics()
            })

    return jsonify({"error": "Worker not found"}), 404

if __name__ == '__main__':
    app.run(debug=True, port=5000)
