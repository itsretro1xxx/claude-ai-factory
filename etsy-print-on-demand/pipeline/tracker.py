"""Worker 6: Performance tracker.

Logs sales/views per listing to a local JSONL file so the Research Hub
(currently a manual notes process — see research-hub/README.md) has real
numbers to work from before it's worth automating (ROADMAP.md Phase 4).
"""

from dataclasses import dataclass, asdict
from datetime import datetime, timezone
import json
from pathlib import Path


@dataclass(frozen=True)
class PerformanceRecord:
    listing_id: int
    niche_slug: str
    checked_at: str
    views: int
    favorites: int
    sales: int


class PerformanceTracker:
    def __init__(self, data_dir):
        self.log_path = Path(data_dir) / "performance.jsonl"
        self.log_path.parent.mkdir(parents=True, exist_ok=True)

    def log(self, listing_id: int, niche_slug: str, views: int, favorites: int, sales: int) -> PerformanceRecord:
        record = PerformanceRecord(
            listing_id=listing_id,
            niche_slug=niche_slug,
            checked_at=datetime.now(timezone.utc).isoformat(),
            views=views,
            favorites=favorites,
            sales=sales,
        )
        with self.log_path.open("a") as f:
            f.write(json.dumps(asdict(record)) + "\n")
        return record

    def history_for(self, listing_id: int) -> list:
        if not self.log_path.exists():
            return []
        records = []
        with self.log_path.open() as f:
            for line in f:
                data = json.loads(line)
                if data["listing_id"] == listing_id:
                    records.append(data)
        return records
