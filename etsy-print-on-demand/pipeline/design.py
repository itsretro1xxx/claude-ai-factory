"""Worker 2: Design generator.

Turns a niche into a batch of design concepts: a name, a one-line concept,
and a detailed prompt for an image-generation tool. This module only does
the concept/prompt-writing step (text) — actually rendering the art still
needs a diffusion model or image tool fed with `image_prompt` below (see
the room README: "needs a plan for commercial usage rights").

Automating this step is the highest-leverage first automation per the room
README ("Design generation ... [is] the most repetitive steps once you're
doing more than one niche").
"""

from dataclasses import dataclass, asdict
import json

import anthropic

from .config import ANTHROPIC_MODEL
from .niche import Niche

DESIGN_SCHEMA = {
    "type": "object",
    "properties": {
        "designs": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "name": {
                        "type": "string",
                        "description": "Short internal name for the design, e.g. 'Cat on a Monstera Leaf'",
                    },
                    "concept": {
                        "type": "string",
                        "description": "One-sentence description of the design's visual idea",
                    },
                    "image_prompt": {
                        "type": "string",
                        "description": (
                            "A detailed prompt for an image-generation model to render this "
                            "design as flat, print-ready art: subject, style, composition, "
                            "color palette, and background (transparent/white for POD printing)"
                        ),
                    },
                    "product_types": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Suggested POD products this design suits, e.g. ['t-shirt', 'mug', 'poster']",
                    },
                },
                "required": ["name", "concept", "image_prompt", "product_types"],
                "additionalProperties": False,
            },
        }
    },
    "required": ["designs"],
    "additionalProperties": False,
}


@dataclass(frozen=True)
class DesignConcept:
    name: str
    concept: str
    image_prompt: str
    product_types: list


class DesignGenerator:
    def __init__(self, client: anthropic.Anthropic | None = None):
        self.client = client or anthropic.Anthropic()

    def generate(self, niche: Niche, count: int = 5) -> list[DesignConcept]:
        response = self.client.messages.create(
            model=ANTHROPIC_MODEL,
            max_tokens=4096,
            output_config={"format": {"type": "json_schema", "schema": DESIGN_SCHEMA}},
            messages=[
                {
                    "role": "user",
                    "content": (
                        f"Generate {count} distinct print-on-demand design concepts for the "
                        f"niche '{niche.label}'. Each design should be a self-contained visual "
                        "idea that would sell well on Etsy to this audience — avoid generic "
                        "clip-art tropes, favor a specific angle or joke or aesthetic. Vary the "
                        "style across the set (e.g. don't make all 5 line-art)."
                    ),
                }
            ],
        )
        text = next(b.text for b in response.content if b.type == "text")
        data = json.loads(text)
        return [DesignConcept(**d) for d in data["designs"]]


def save_designs(niche: Niche, designs: list[DesignConcept], data_dir) -> "Path":
    from pathlib import Path

    out_dir = Path(data_dir) / "niches" / niche.slug
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / "designs.json"
    out_path.write_text(
        json.dumps(
            {"niche": asdict(niche), "designs": [asdict(d) for d in designs]},
            indent=2,
        )
    )
    return out_path
