from .base_worker import BaseWorker


class EtsyWorker(BaseWorker):
    def __init__(self, config=None):
        super().__init__("Etsy Print-on-Demand Worker", config)

    async def run_task(self, task_type, **kwargs):
        if task_type == "design_generation":
            raise NotImplementedError(
                "No image-generation backend is wired in yet — see "
                "etsy-print-on-demand/README.md pipeline step 2 and Roadmap Phase 0."
            )
        return await super().run_task(task_type, **kwargs)
