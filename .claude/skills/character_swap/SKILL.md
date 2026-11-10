---
name: character_swap
description: Restyle the creator (outfit, hair, makeup, background) or swap characters while keeping their motion, using Kling Motion Control / Runway Aleph. Use for /character_swap, "change my outfit", "change background", "motion control".
---
Preferred: run it through fal with `python3 tools/fal_gen.py swap --image <look> --video <take> [--prompt ...]` (Kling v3 Motion Control; estimate first, then `--yes` after the creator says go). For the reference look image, generate one from the creator's headshot. Fallback, ready-to-paste prompts for apps:
1. **Kling Motion Control** (Aragon AI or Higgsfield; motion video + reference image): "Change the person to the one shown in @image, preserving their identity, facial features and body type exactly. Also change the background to what's shown in @image. Keep all motion, gestures, lip-sync and timing identical." Settings: 1080p, 9:16, audio on.
2. **Runway Aleph** (edit by instruction, one change per pass): e.g. "Replace the frames on the wall with a floating oak shelf and add a tall monstera plant behind me. Keep everything else identical."
For the reference image, suggest generating one with Nano Banana / GPT-image from the creator's headshot. Give that prompt too.
