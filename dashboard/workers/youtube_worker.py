"""
YouTube Worker - Generates trending YouTube Shorts content ideas and scripts
"""

import logging
from typing import Dict, Any
import json
from .base_worker import BaseWorker

logger = logging.getLogger(__name__)


class YouTubeWorker(BaseWorker):
    """
    AI Worker specialized in generating trending YouTube Shorts content
    """

    def __init__(self, config: Dict[str, Any]):
        """Initialize YouTube worker"""
        super().__init__("YouTube Shorts Generator 🎬", config)
        self.shorts_created = 0

    async def execute_task(self, task: str) -> Dict[str, Any]:
        """
        Execute YouTube task

        Args:
            task: Task type (script_generation, trend_analysis, etc.)

        Returns:
            Task result with video scripts and ideas
        """
        logger.info(f"Executing YouTube task: {task}")

        try:
            if task == "script_generation":
                result = await self._generate_scripts()
            elif task == "trend_check":
                result = await self._check_trends()
            else:
                result = {"status": "unknown_task", "task": task}

            self.log_task(task, result)
            return result

        except Exception as e:
            logger.error(f"Error executing task {task}: {e}")
            return {"status": "error", "error": str(e)}

    async def _generate_scripts(self) -> Dict[str, Any]:
        """Generate trending YouTube Shorts scripts based on current viral trends"""
        system_prompt = """You are a professional YouTube Shorts strategist and scriptwriter.
Create HIGH-PERFORMING short-form video scripts that:
- Use proven viral hooks
- Include trending sounds/audio
- Have high watch completion rates
- Include clear CTAs
- Follow current YouTube algorithm trends (2024-2025)
- Are optimized for maximum engagement"""

        prompt = """Generate 5 VIRAL YouTube Shorts Scripts RIGHT NOW:

For EACH script, provide:

1. VIDEO TITLE: Catchy title that generates clicks
2. CONTENT CATEGORY: Type of content (education, entertainment, motivation, etc)
3. TARGET AUDIENCE: Who this video attracts
4. HOOK (FIRST 2 SECONDS): The critical opening that stops scrollers
   - Text on screen
   - Visual element
   - Sound/music
5. MAIN BODY (5-30 seconds): The core content
   - Script dialogue (if needed)
   - Visual description
   - Pacing notes
6. TRENDING SOUNDS: Top 3 sounds to use (must mention current trending sounds)
7. TRENDING HASHTAGS: Relevant hashtags for reach
8. CALL-TO-ACTION: How to end the video
9. UPLOAD STRATEGY: Best time/day to upload
10. THUMBNAIL TEXT: What to use as cover
11. CHANNEL NICHE: What type of channel can do this
12. VIRAL POTENTIAL: Estimated reach (1-100k views realistic range)
13. SIMILAR VIDEOS: Popular videos in this style (reference)
14. MUSIC/AUDIO RECOMMENDATIONS: Specific songs that work
15. ENGAGEMENT TACTICS: How to boost comments/shares

TRENDING VIDEO TYPES (Pick from 2024-2025):
- Quick productivity hacks (2-3 minute tasks)
- Money-making/side hustle tutorials
- AI tools demonstrations (automation, content creation)
- Motivational/inspirational stories
- Educational/learning content
- Fitness/health quick tips
- Cooking/recipe content
- Comedy/entertainment
- Reaction videos
- Trending sound challenges
- Before & after transformations
- Day in the life vlogs
- Problem & solution videos
- Trend-jacking videos

CURRENT VIRAL TRENDS TO FOCUS ON:
- AI productivity automation
- ChatGPT/AI tools for money
- Work from home lifestyle
- Passive income strategies
- Personal development
- Funny/relatable humor
- Life hacks that save time/money
- Educational content that's entertaining

Return as JSON with "scripts" array. Each script should be IMMEDIATELY USABLE."""

        response = await self.call_claude(prompt, system=system_prompt)

        try:
            result = json.loads(response)
            scripts = result.get("scripts", [])
        except Exception:
            scripts = [{"raw_script": response}]

        self.shorts_created += len(scripts)

        return {
            "status": "success",
            "type": "script_generation",
            "scripts_count": len(scripts),
            "scripts": scripts,
            "metadata": {
                "trend_focus": "viral_2024_2025",
                "quality": "production_ready",
                "total_shorts_created": self.shorts_created,
                "content_types": ["education", "entertainment", "motivation", "automation"]
            }
        }

    async def _check_trends(self) -> Dict[str, Any]:
        """Check what's currently trending on YouTube Shorts"""
        system_prompt = """You are a YouTube Shorts trend analyst.
Provide real data on what's ACTUALLY going viral right now."""

        prompt = """What YouTube Shorts TRENDS are EXPLODING RIGHT NOW in 2024-2025?

Provide for EACH trending category:
1. Trend name/category
2. Current viral status (1-10)
3. Why it's trending
4. Typical video length
5. Best hook approach
6. Trending sounds for this
7. Estimated view potential (realistic)
8. Growth trajectory
9. Saturation level (how many similar videos)
10. Unique angle opportunities
11. Best upload frequency
12. Monetization potential
13. Channel growth potential
14. Evergreen vs trendy (will it last)
15. Similar successful channels

FOCUS ON PROVEN VIRAL CATEGORIES:
- What's actually getting millions of views
- What smaller creators can replicate
- What has low competition but high interest
- What trends have longevity
- What's emerging vs what's fading

Include specific examples of videos/channels doing well.
Format as comprehensive, actionable JSON."""

        response = await self.call_claude(prompt, system=system_prompt)

        try:
            trends = json.loads(response)
        except Exception:
            trends = {"raw_trends": response}

        return {
            "status": "success",
            "type": "trend_check",
            "trends": trends
        }

    async def get_metrics(self) -> Dict[str, Any]:
        """Get worker metrics"""
        self.metrics = {
            "shorts_created": self.shorts_created,
            "tasks_completed": len(self.task_history)
        }
        return self.metrics
