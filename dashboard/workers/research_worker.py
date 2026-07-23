from .base_worker import BaseWorker


class ResearchWorker(BaseWorker):
    def __init__(self, config=None):
        super().__init__("Research Hub Worker", config)

    async def run_task(self, task_type, **kwargs):
        if task_type == "market_research":
            raise NotImplementedError(
                "No trend-data backend is wired in yet — see "
                "research-hub/README.md worker roles and Roadmap Phase 4."
            )
        return await super().run_task(task_type, **kwargs)
