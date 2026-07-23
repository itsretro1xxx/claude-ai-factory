import os
from pathlib import Path

ANTHROPIC_MODEL = "claude-opus-4-8"

ROOM_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = ROOM_DIR / "data"

# The Claude SDK reads ANTHROPIC_API_KEY by default. The root .env.example
# uses the friendlier CLAUDE_API_KEY name — accept it as an alias so a
# single root-level .env works without also setting a room-specific one.
if not os.environ.get("ANTHROPIC_API_KEY") and os.environ.get("CLAUDE_API_KEY"):
    os.environ["ANTHROPIC_API_KEY"] = os.environ["CLAUDE_API_KEY"]

PRINTFUL_API_KEY = os.environ.get("PRINTFUL_API_KEY")
ETSY_API_KEY = os.environ.get("ETSY_API_KEY")
ETSY_ACCESS_TOKEN = os.environ.get("ETSY_ACCESS_TOKEN")
ETSY_SHOP_ID = os.environ.get("ETSY_SHOP_ID")
