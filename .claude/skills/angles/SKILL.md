---
name: angles
description: Turn one single-camera take into a multi-angle edit (close-ups, low angle, top-down, drone, orbit) by writing the Seedance 2.5 / Kling video-edit prompt. Use for /angles, "multiple angles", "camera angles", "drone view".
---
1. Get the clip, run `tools/captions.py`, and choose cut points on sentence or phrase boundaries (every 2.5-4s; faster during the hook).
2. Assign an angle per cut and vary scale AND height: Medium → Close-up → Low angle → Side profile → Top-down → Extreme close-up → Over-the-shoulder → Wide → (drone pull-back / orbit for the finale).
3. Output `projects/<slug>/angles_prompt.md` in this exact form:
```
Edit @Video1. Keep the same scene, dialogue, actions and timing.
00:00 — Medium shot
00:03 — Close-up
...
End at 00:22.5.
Keep the location, dialogue, lip-sync and actions identical. Do not add or remove people or props.
```
4. Also write per-segment mini-prompts (one angle each, ≤5s) because the model rarely nails a whole clip at once. The creator generates segment by segment.
5. Tell the creator: Higgsfield → Video → Edit → model "Seedance 2.5" → upload the original → paste → 1080p 9:16. When the clips come back, put them in `inbox/` and Claude will conform them (match audio to the original, colour-match, add whoosh transitions).
