#!/usr/bin/env python3
"""Audio loudness per video frame (0..1) -> JSON, so waveforms/scribbles react to the voice.
Usage: python3 tools/levels.py IN OUT.json [--fps 30]"""
import argparse, json, subprocess, numpy as np
ap = argparse.ArgumentParser(); ap.add_argument("inp"); ap.add_argument("out"); ap.add_argument("--fps", type=int, default=30)
a = ap.parse_args()
raw = subprocess.check_output(["ffmpeg", "-v", "error", "-i", a.inp, "-ac", "1", "-ar", "48000", "-f", "s16le", "-"])
x = np.frombuffer(raw, np.int16).astype(np.float32) / 32768
step = 48000 // a.fps
rms = np.array([np.sqrt(np.mean(x[i:i + step] ** 2)) for i in range(0, len(x) - step, step)])
lv = np.clip(rms / (np.percentile(rms, 95) + 1e-6), 0, 1)
json.dump([round(float(v), 3) for v in lv], open(a.out, "w"))
print(f"levels: {len(lv)} frames -> {a.out}")
