"""CLI entrypoint for the Etsy Print-on-Demand room.

Runs the two automated steps (design generation, listing copywriting) end
to end for a niche and writes the results under data/niches/<slug>/.
Mockup building and publishing are separate, credential-gated steps — see
pipeline/mockup.py and pipeline/publisher.py.

Usage:
    python run.py --audience "plant-obsessed cat owners" --theme "gifts" --count 5
"""

import argparse

from pipeline.config import DATA_DIR
from pipeline.design import DesignGenerator, save_designs
from pipeline.listing import ListingCopywriter, save_listings
from pipeline.niche import Niche


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate designs and listing copy for a niche.")
    parser.add_argument("--audience", required=True, help="Target audience, e.g. 'plant-obsessed cat owners'")
    parser.add_argument("--theme", required=True, help="Theme/angle, e.g. 'gifts'")
    parser.add_argument("--count", type=int, default=5, help="Number of design concepts to generate (default: 5)")
    args = parser.parse_args()

    niche = Niche(audience=args.audience, theme=args.theme)
    print(f"Niche: {niche.label}")

    print(f"Generating {args.count} design concepts...")
    designs = DesignGenerator().generate(niche, count=args.count)
    designs_path = save_designs(niche, designs, DATA_DIR)
    print(f"Wrote {designs_path}")

    print("Writing Etsy listing copy for each design...")
    copywriter = ListingCopywriter()
    listings = [copywriter.generate(niche, design) for design in designs]
    listings_path = save_listings(niche, listings, DATA_DIR)
    print(f"Wrote {listings_path}")

    print("\nNext steps (manual, per room README):")
    print("  1. Feed each design's image_prompt into an image-generation tool.")
    print("  2. Build mockups: pipeline.mockup.MockupBuilder (needs PRINTFUL_API_KEY).")
    print("  3. Publish drafts: pipeline.publisher.Publisher (needs Etsy API credentials).")
    print("  4. Review drafts in Etsy Shop Manager before publishing live.")


if __name__ == "__main__":
    main()
