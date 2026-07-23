# YouTube Shorts Automation Room

Turns a content pillar into a steady stream of published Shorts.

## Pipeline (worker order)

1. **Topic picker** — takes a content pillar/topic from the Research Hub (or
   picks one manually to start). Narrower is better: not "facts" but e.g.
   "60-second true crime cold cases" or "weird science facts explained simply."
2. **Script writer** — generates a short (30-60s) script per video: hook in
   the first 1-2 seconds, body, a closing line that invites a follow/comment.
3. **Voiceover generator** — turns the script into audio via a TTS tool
   (ElevenLabs, or platform-native TTS). Alternative: your own voice, scripted.
4. **Video assembler** — combines voiceover + visuals (stock footage, AI-generated
   b-roll, or simple text/caption-driven templates) + auto-captions into a
   vertical 9:16 video. Tools: CapCut (has automation/templates), or a
   script-driven pipeline (ffmpeg + a captioning tool) for full automation.
5. **Thumbnail/title writer** — Shorts don't need custom thumbnails the way
   long-form does, but the on-screen title text/hook still needs to be written
   per video.
6. **Publisher** — uploads and schedules via the YouTube Data API, or manually
   via YouTube Studio to start.
7. **Performance tracker** — logs views/retention/engagement per video via
   YouTube Analytics, reports back to the Research Hub on what's working.

## Tools/accounts needed

- YouTube channel (monetization needs Partner Program thresholds — treat early
  revenue as ad-revenue-eventually, not immediate).
- TTS tool for voiceover (ElevenLabs or similar) if not using your own voice.
- Video assembly tool (CapCut, or a scripted ffmpeg pipeline for full automation).
- An LLM (Claude/GPT) for scripts.
- YouTube Data API access if automating uploads (OAuth setup required).

## First manual pass checklist

- [ ] Pick 1 content pillar
- [ ] Write 3 scripts
- [ ] Generate voiceover + assemble 3 videos
- [ ] Publish all 3, spaced out (not all same day)
- [ ] Check retention/views after ~1 week before deciding what to automate first

## What to automate first (usually)

Script writing is the cheapest to automate and highest-leverage — automate
that first, keep video assembly manual until you're confident in script
quality and format, then automate assembly.
