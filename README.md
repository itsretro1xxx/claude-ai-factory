# Claude AI Factory

An AI-worker-driven revenue operation, structured like a small factory floor: one
central research hub coordinating specialized "rooms," each room running its own
pipeline of AI workers toward a specific revenue stream.

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

## The three rooms

| Room | Folder | Job |
|---|---|---|
| Research Hub | [`research-hub/`](research-hub/README.md) | Finds what's worth making, tracks what's working, feeds the other rooms |
| Etsy Print-on-Demand | [`etsy-print-on-demand/`](etsy-print-on-demand/README.md) | Turns a niche into listed, sellable designs with no inventory held |
| YouTube Shorts Automation | [`youtube-shorts-automation/`](youtube-shorts-automation/README.md) | Turns a content pillar into a steady stream of published Shorts |

Each room's README lays out: the worker pipeline (who does what, in order), the
external tools/APIs it needs, and a concrete task checklist to get its first
output live.

## How to use this repo

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

## Worker chat prototype

A minimal room/worker chat UI is available in [`worker-chat/`](worker-chat/).

- Shows room-level worker lists with status, unread indicators, and **Interact** actions
- Supports two-way manager/worker messaging with per-worker thread history
- Persists chat history in browser storage so room and worker conversations can be resumed

Run it locally:

1. `cd worker-chat`
2. `npm install`
3. `npm run dev`
4. `npm run test`
