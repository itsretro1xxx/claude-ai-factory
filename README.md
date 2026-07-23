# Claude AI Factory 🏭

An AI-powered autonomous factory system with AI workers managing multiple revenue streams.

## 🎯 Vision

Build a scalable AI factory that:
- Conducts AI research and development
- Generates revenue through multiple automated channels
- Manages AI workers autonomously
- Learns and improves over time

## 📦 Project Structure

One central research hub coordinating specialized "rooms," each room running its
own pipeline of AI workers toward a specific revenue stream.

```
                     ┌────────────────────┐
                     │   Research Hub      │
                     │ (trends, niches,    │
                     │  shared knowledge)  │
                     └─────────┬──────────┘
                     signals down │ results up
              ┌────────────────┴─────────────────┐
              ▼                                    ▼
   ┌───────────────────────┐          ┌─────────────────────────┐
   │ Etsy Print-on-Demand   │          │ YouTube Shorts           │
   │ Room                   │          │ Automation Room          │
   └───────────────────────┘          └─────────────────────────┘
```

| Room | Folder | Job |
|---|---|---|
| Research Hub | [`research-hub/`](research-hub/README.md) | Finds what's worth making, tracks what's working, feeds the other rooms |
| Etsy Print-on-Demand | [`etsy-print-on-demand/`](etsy-print-on-demand/README.md) | Turns a niche into listed, sellable designs with no inventory held. Has a working `pipeline/` for design generation + Etsy listing copy — see its README. |
| YouTube Shorts Automation | [`youtube-shorts-automation/`](youtube-shorts-automation/README.md) | Turns a content pillar into a steady stream of published Shorts |

Each room's README lays out: the worker pipeline (who does what, in order), the
external tools/APIs it needs, and a concrete task checklist to get its first
output live.

## 💰 Revenue Streams

### 1. **Etsy Print-on-Demand Store** 🛍️
- AI-generated designs
- Automated product listings
- Order processing and fulfillment coordination
- Analytics and optimization

### 2. **YouTube Shorts Automation** 📹
- AI content generation
- Video creation and editing
- Automated upload and publishing
- Analytics and engagement tracking

### 3. **Additional Revenue Ideas** 🚀
- TikTok automation (similar to YouTube Shorts)
- Blog/content monetization with AI writing
- AI art generation and NFT minting
- Affiliate marketing automation
- Digital product creation
- Email marketing automation

## 🧠 Research & Development

Core research initiatives:
- AI worker optimization and coordination
- Multi-agent collaboration patterns
- Autonomous decision-making systems
- Cost optimization strategies

## 🤖 AI Workers

Each revenue stream is managed by AI workers specialized in:
- Task execution
- Decision making
- Reporting and analytics
- Continuous improvement

## 🚀 Getting Started

### Prerequisites
- Python 3.9+
- Claude API key
- Required API keys for each revenue stream (see each room's README — e.g.
  Etsy POD needs a Printful key and Etsy OAuth credentials)

### Installation

```bash
git clone https://github.com/itsretro1xxx/claude-ai-factory.git
cd claude-ai-factory
pip install -r requirements.txt
```

### Configuration

Copy `.env.example` to `.env` and fill in your keys:

```bash
cp .env.example .env
```

```
CLAUDE_API_KEY=your_key_here
ETSY_API_KEY=your_key_here
YOUTUBE_API_KEY=your_key_here
```

> `CLAUDE_API_KEY` is accepted as an alias for the Claude SDK's standard
> `ANTHROPIC_API_KEY` — the Etsy POD pipeline picks up either. That room also
> needs `PRINTFUL_API_KEY`, `ETSY_ACCESS_TOKEN`, and `ETSY_SHOP_ID` for the
> mockup/publish steps — see `etsy-print-on-demand/.env.example`. YouTube
> Shorts automation isn't built yet, so `YOUTUBE_API_KEY` isn't consumed by
> any code until that room's pipeline exists.

### Next steps

1. Read [`ROADMAP.md`](ROADMAP.md) for the phased build-out (setup → one manual
   pass by hand → automate step by step → scale).
2. Pick **one room** to get to a first live output before automating the other.
   Etsy POD and YouTube Shorts are independent — build whichever matches your
   available accounts/budget first.
3. The Research Hub is only worth automating once at least one room is live and
   generating signal (sales, views) to feed back into it. Start it as a doc/notes
   process, not a pipeline.

## Costs to expect going in

- Etsy: shop setup fee (~$15 one-time in most regions) + per-listing fees + transaction fees.
- Print-on-demand provider (Printful/Printify): free to integrate, they take their cut per item printed.
- YouTube: free to publish; monetization (ad revenue) requires meeting Partner Program thresholds.
- AI generation (images, script, voice): usage-based API costs, small per-asset but scales with volume.
- Optional automation tooling (Make.com/Zapier or custom scripts) if you don't want to run pipelines by hand.
