import os
from pathlib import Path

ANTHROPIC_MODEL = "claude-opus-4-8"

ROOM_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = ROOM_DIR / "data"

PRINTFUL_API_KEY = os.environ.get("PRINTFUL_API_KEY")
ETSY_API_KEY = os.environ.get("ETSY_API_KEY")
ETSY_ACCESS_TOKEN = os.environ.get("ETSY_ACCESS_TOKEN")
ETSY_SHOP_ID = os.environ.get("ETSY_SHOP_ID")
