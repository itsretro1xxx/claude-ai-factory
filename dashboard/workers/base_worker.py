"""Shared worker behavior: status tracking, task history, metrics.

Subclasses implement `run_task(task_type, **kwargs)` — everything else
(status transitions, history, timing) is handled here.
"""
from datetime import datetime, timezone


class BaseWorker:
    def __init__(self, name, config=None):
        self.name = name
        self.config = config or {}
        self.status = "idle"
        self.task_history = []
        self.factory = None

    async def execute_task(self, task_type, **kwargs):
        self.status = "running"
        started_at = datetime.now(timezone.utc).isoformat()
        entry = {"task_type": task_type, "started_at": started_at}
        try:
            result = await self.run_task(task_type, **kwargs)
            entry.update(finished_at=datetime.now(timezone.utc).isoformat(), status="success", result=result)
            return result
        except Exception as e:
            entry.update(finished_at=datetime.now(timezone.utc).isoformat(), status="error", error=str(e))
            raise
        finally:
            self.task_history.append(entry)
            self.status = "idle"

    async def run_task(self, task_type, **kwargs):
        raise NotImplementedError(f"{self.name} has no handler for task '{task_type}'")

    @property
    def metrics(self):
        completed = sum(1 for t in self.task_history if t["status"] == "success")
        failed = sum(1 for t in self.task_history if t["status"] == "error")
        return {
            "tasks_completed": completed,
            "tasks_failed": failed,
            "last_run": self.task_history[-1]["finished_at"] if self.task_history else None,
        }

    def get_metrics(self):
        return {"status": self.status, **self.metrics}
