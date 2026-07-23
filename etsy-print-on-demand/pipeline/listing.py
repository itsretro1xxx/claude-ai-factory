"""Worker 4: Listing copywriter.

Turns a design concept into Etsy listing copy: title, 13 tags, description,
and a suggested price, following Etsy SEO conventions (front-load keywords
in the title, use all 13 tags, avoid keyword stuffing).

Automating this step is the other highest-leverage first automation per the
room README, alongside design generation.
"""

from dataclasses import dataclass, asdict
import json

import anthropic

from .config import ANTHROPIC_MODEL
from .design import DesignConcept
from .niche import Niche

LISTING_SCHEMA = {
    "type": "object",
    "properties": {
        "title": {
            "type": "string",
            "description": "Etsy listing title, <=140 chars, keywords front-loaded, no keyword stuffing",
        },
        "tags": {
            "type": "array",
            "items": {"type": "string"},
            "description": "Exactly 13 Etsy tags, each <=20 chars, no duplicates, mix of broad and long-tail",
        },
        "description": {
            "type": "string",
            "description": (
                "Etsy listing description: opens with the hook/who it's for, "
                "describes the design, lists product options, sizing note, "
                "and a call to action. Plain text, no markdown."
            ),
        },
        "price_usd": {
            "type": "number",
            "description": "Suggested retail price in USD for a standard product (e.g. t-shirt)",
        },
    },
    "required": ["title", "tags", "description", "price_usd"],
    "additionalProperties": False,
}


@dataclass(frozen=True)
class ListingCopy:
    title: str
    tags: list
    description: str
    price_usd: float


class ListingCopywriter:
    def __init__(self, client: anthropic.Anthropic | None = None):
        self.client = client or anthropic.Anthropic()

    def generate(self, niche: Niche, design: DesignConcept) -> ListingCopy:
        response = self.client.messages.create(
            model=ANTHROPIC_MODEL,
            max_tokens=2048,
            output_config={"format": {"type": "json_schema", "schema": LISTING_SCHEMA}},
            messages=[
                {
                    "role": "user",
                    "content": (
                        f"Write Etsy listing copy for a print-on-demand product.\n\n"
                        f"Niche: {niche.label}\n"
                        f"Design name: {design.name}\n"
                        f"Design concept: {design.concept}\n"
                        f"Product types: {', '.join(design.product_types)}\n\n"
                        "Follow Etsy SEO best practice: front-load the most important "
                        "keywords in the title, use all 13 tag slots with a mix of broad "
                        "and specific/long-tail phrases, and write a description that "
                        "converts browsers into buyers without stuffing keywords."
                    ),
                }
            ],
        )
        text = next(b.text for b in response.content if b.type == "text")
        data = json.loads(text)
        return ListingCopy(**data)


def save_listings(niche: Niche, listings: list[ListingCopy], data_dir) -> "Path":
    from pathlib import Path

    out_dir = Path(data_dir) / "niches" / niche.slug
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / "listings.json"
    out_path.write_text(json.dumps([asdict(listing) for listing in listings], indent=2))
    return out_path
