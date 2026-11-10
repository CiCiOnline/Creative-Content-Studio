---
name: paper_cut
description: Edit a talking-head clip into the "paper cut" collage style (grid paper, ransom-note title, voice-reactive scribbles, cut-out sticker of the speaker, ransom captions). Use when the user says /paper_cut, "paper cut", "collage edit", "ransom note" or "cutout effect".
---
1. Find the clip (argument, or newest file in `inbox/`). Watch it: run `tools/captions.py` first and read the transcript.
2. Pick a 3-part title from the core promise (max 1 word, 1 word, 2-3 words, e.g. VOICE / BUILT / FROM NOTHING). Offer 3 options, then choose the strongest unless the user picks.
3. Pick 3-6 `emphasis` words (the nouns/verbs that carry the idea) for ransom treatment.
4. Run `tools/papercut.sh <clip> "<W1>" "<W2>" "<W3>" <slug>`, then patch `engine/public/<slug>/props.json` emphasis and re-render if needed.
5. QA: extract 3 stills with ffmpeg (0.5s, middle, end), look at them, and fix overlaps (title vs face, captions vs chin).
6. Deliver `exports/<slug>_papercut.mp4` plus one coaching note.
