from .base_worker import BaseWorker


class YouTubeWorker(BaseWorker):
    def __init__(self, config=None):
        super().__init__("YouTube Shorts Worker", config)

    async def run_task(self, task_type, **kwargs):
        if task_type == "script_generation":
            raise NotImplementedError(
                "No script/TTS/video-assembly backend is wired in yet — see "
                "youtube-shorts-automation/README.md pipeline steps 2-4 and Roadmap Phase 0."
            )
        return await super().run_task(task_type, **kwargs)
