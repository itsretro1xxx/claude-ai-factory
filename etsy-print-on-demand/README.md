# Etsy Print-on-Demand Room

Turns a niche into listed, sellable designs with no inventory held — the POD
provider prints and ships per order.

## Pipeline (worker order)

1. **Niche picker** — takes a niche from the Research Hub (or picks one manually
   to start): a specific audience + theme, not "t-shirts" but e.g. "gifts for
   plant-obsessed cat owners."
2. **Design generator** — produces design concepts and renders (AI image
   generation, e.g. a diffusion model or Claude-assisted prompt iteration into
   an image tool) for that niche. Start with a small batch (5-10 designs) per niche.
3. **Product/mockup builder** — applies designs to product mockups (shirts,
   mugs, posters, etc.) via the POD provider's mockup generator (Printful/Printify
   both provide this).
4. **Listing copywriter** — generates the Etsy listing: title, 13 tags,
   description, pricing, using an LLM prompted with Etsy SEO conventions
   (front-load keywords in the title, use all 13 tags, avoid keyword stuffing).
5. **Publisher** — pushes the product + listing to Etsy via the POD provider's
   Etsy integration (Printful and Printify both sync directly to a connected
   Etsy shop) or via the Etsy API directly for more control.
6. **Performance tracker** — logs sales/views per listing, reports back to the
   Research Hub on what's converting.

## Tools/accounts needed

- Etsy seller account (shop setup fee applies).
- Printful or Printify account, connected to the Etsy shop (this is the
  standard no-inventory POD integration path).
- An image generation tool for designs (needs a plan for commercial usage
  rights — check the license of whatever model/tool you use).
- An LLM (Claude/GPT) for listing copy.

## First manual pass checklist

- [ ] Pick 1 niche
- [ ] Generate 3-5 designs
- [ ] Build mockups via Printful/Printify
- [ ] Write listing copy (title/tags/description) for each
- [ ] Publish all listings
- [ ] Check back in 1-2 weeks on views/favorites/sales before deciding what to automate first

## What to automate first (usually)

Design generation and listing copywriting are the most repetitive steps once
you're doing more than one niche — automate those before touching
publishing, and keep a manual review step before anything goes live.
