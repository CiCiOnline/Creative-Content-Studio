# Creative-Content-Studio

An AI video studio run by Claude: talking-head edits with paper-cut collage effects, cutouts,
word-by-word captions, and pay-as-you-go AI generation through fal.ai (voice clone, talking avatar
from a photo, multi-angle and drone shots, outfit and scene swaps).

## Start a session
```bash
./setup.sh
```
Then add the fal key: Claude runs the browser-approval flow from https://fal.ai/get-started.md,
and the key goes into `.env`, which is git-ignored and never committed.

## Layout
- `CLAUDE.md`: Claude's creative-director rules, toolkit and fal price table
- `.claude/skills/`: slash commands `/direct`, `/paper_cut`, `/angles`, `/script`, `/character_swap`
- `tools/`: `cutout.py`, `captions.py`, `levels.py`, `papercut.sh`, `fal_gen.py`
- `engine/`: Remotion motion-graphics engine (React → MP4)
- `inbox/` raw material · `assets/` faces, voice, brand · `projects/` per-video work · `exports/` renders
- `studio-playbook.html`: setup guide
