#!/usr/bin/env python3
"""Word-level captions with Whisper. Writes JSON for the Remotion engine + an SRT.

Usage: python3 tools/captions.py IN.(mp4|wav|mp3) OUT.json [--model small]
"""
import argparse, json, subprocess, numpy as np
from faster_whisper import WhisperModel

ap = argparse.ArgumentParser()
ap.add_argument("inp"); ap.add_argument("out")
ap.add_argument("--model", default="small")
a = ap.parse_args()

raw = subprocess.check_output(["ffmpeg", "-v", "error", "-i", a.inp, "-ac", "1", "-ar", "16000", "-f", "s16le", "-"])
audio = np.frombuffer(raw, np.int16).astype(np.float32) / 32768
m = WhisperModel(a.model, device="cpu", compute_type="int8")
segs, info = m.transcribe(audio, word_timestamps=True, vad_filter=True)
words = []
for s in segs:
    for w in s.words:
        words.append({"text": w.word.strip(), "start": round(w.start, 3), "end": round(w.end, 3)})
json.dump({"language": info.language, "words": words}, open(a.out, "w"), indent=1)

def ts(t):
    h, r = divmod(t, 3600); mi, s = divmod(r, 60)
    return f"{int(h):02}:{int(mi):02}:{s:06.3f}".replace(".", ",")
with open(a.out.rsplit(".", 1)[0] + ".srt", "w") as f:
    for i in range(0, len(words), 4):
        g = words[i:i + 4]
        f.write(f"{i//4+1}\n{ts(g[0]['start'])} --> {ts(g[-1]['end'])}\n{' '.join(x['text'] for x in g)}\n\n")
print(f"captions: {len(words)} words -> {a.out}")
