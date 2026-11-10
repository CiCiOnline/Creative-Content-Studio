---
name: script
description: Write a short-form video script for the creator's AI avatar / voice clone (HeyGen, VEED, ElevenLabs), with on-screen text and effect cues. Use for /script, "write a script", "reel idea", "hook".
---
- Ask nothing if the topic is given. Produce 3 hooks (≤8 words each, pattern-interrupt, curiosity or bold claim), then a full script for the best one.
- Length: 30-45s ≈ 80-120 words. Short sentences. Write for the ear, with contractions. Add ElevenLabs-style pauses with "—" or "...".
- Columns: VOICE | ON-SCREEN TEXT | EFFECT (paper_cut, serif_pop, glass_widgets, angle change, b-roll prompt).
- End with a comment-bait CTA ("Comment X and I'll send you...").
- Save to `projects/<date>-<slug>/script.md` and a clean voice-only `script.txt` for pasting into the avatar app.
- To voice it: `python3 tools/fal_gen.py tts --file projects/<...>/script.txt --voice me` (estimate first, then `--yes`).
  For a talking video: `python3 tools/fal_gen.py avatar --image assets/faces/<best>.jpg --audio exports/<voice>.mp3`.
