"""Core AIFactory: a registry of workers plus aggregate metrics."""


class AIFactory:
    def __init__(self, config):
        self.name = config["name"]
        self.env = config.get("env", "development")
        self.start_time = config.get("start_time")
        self.workers = []

    def register_worker(self, worker):
        worker.factory = self
        self.workers.append(worker)

    @property
    def metrics(self):
        return {
            "workers_registered": len(self.workers),
            "tasks_completed": sum(w.metrics.get("tasks_completed", 0) for w in self.workers),
            "tasks_failed": sum(w.metrics.get("tasks_failed", 0) for w in self.workers),
        }
