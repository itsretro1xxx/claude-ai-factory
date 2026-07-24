"""Shared worker behavior: status tracking, task history, metrics, and a
Claude helper (`call_claude`) that subclasses use for actual generation.

Subclasses either implement `run_task(task_type, **kwargs)` and let the
default `execute_task` wrapper handle history/status, or override
`execute_task` directly (calling `log_task` themselves) when they need more
control, as ResearchWorker does.
"""
import os
from datetime import datetime, timezone

try:
    from anthropic import AsyncAnthropic
except ImportError:
    AsyncAnthropic = None

DEFAULT_MODEL = "claude-sonnet-5"


class BaseWorker:
    def __init__(self, name, config=None):
        self.name = name
        self.config = config or {}
        self.status = "idle"
        self.task_history = []
        self.factory = None
        self.metrics = {"tasks_completed": 0, "tasks_failed": 0, "last_run": None}
        self._client = None

    def _get_client(self):
        if self._client is None:
            if AsyncAnthropic is None:
                raise RuntimeError(
                    "The 'anthropic' package is not installed — "
                    "run `pip install -r requirements.txt`."
                )
            api_key = os.getenv("ANTHROPIC_API_KEY")
            if not api_key:
                raise RuntimeError(
                    "ANTHROPIC_API_KEY is not set — add it to dashboard/.env to enable "
                    f"{self.name} generation tasks."
                )
            self._client = AsyncAnthropic(api_key=api_key)
        return self._client

    async def call_claude(self, prompt, system=None, model=None, max_tokens=2048):
        client = self._get_client()
        response = await client.messages.create(
            model=model or self.config.get("model", DEFAULT_MODEL),
            max_tokens=max_tokens,
            system=system or "",
            messages=[{"role": "user", "content": prompt}],
        )
        return "".join(block.text for block in response.content if block.type == "text")

    def log_task(self, task_type, result):
        status = result.get("status", "success") if isinstance(result, dict) else "success"
        self.task_history.append(
            {
                "task_type": task_type,
                "finished_at": datetime.now(timezone.utc).isoformat(),
                "status": status,
                "result": result,
            }
        )
        self.status = "idle"

    async def execute_task(self, task_type, **kwargs):
        self.status = "running"
        try:
            result = await self.run_task(task_type, **kwargs)
            self.log_task(task_type, result)
            return result
        except Exception as e:
            self.log_task(task_type, {"status": "error", "error": str(e)})
            raise

    async def run_task(self, task_type, **kwargs):
        raise NotImplementedError(f"{self.name} has no handler for task '{task_type}'")

    async def get_metrics(self):
        completed = sum(1 for t in self.task_history if t["status"] == "success")
        failed = sum(1 for t in self.task_history if t["status"] == "error")
        self.metrics.update(
            tasks_completed=completed,
            tasks_failed=failed,
            last_run=self.task_history[-1]["finished_at"] if self.task_history else None,
        )
        return {"status": self.status, **self.metrics}
