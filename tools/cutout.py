#!/usr/bin/env python3
"""Paper-cut sticker cutout: removes the background from a talking-head video
and adds a torn white sticker border, like the 'paper cut' reels.

Usage:
  python3 tools/cutout.py IN.mp4 OUT.webm [--border 14] [--bg none|#f3efe6]
Output: VP9 WebM with alpha (drop it on any background / into Remotion),
or an MP4 on a solid colour if --bg is a colour.
"""
import argparse, subprocess, sys, os
import numpy as np, cv2
import mediapipe as mp
from mediapipe.tasks import python as mpt
from mediapipe.tasks.python import vision

HERE = os.path.dirname(os.path.abspath(__file__))
MODEL = os.path.join(HERE, "..", "models", "selfie_multiclass.tflite")


def probe(path):
    out = subprocess.check_output(["ffprobe", "-v", "error", "-select_streams", "v:0",
        "-show_entries", "stream=width,height,r_frame_rate", "-of", "csv=p=0", path]).decode().strip()
    w, h, r = out.split(",")
    n, d = r.split("/")
    return int(w), int(h), float(n) / float(d)


def torn_edge(mask, border, rng):
    """Dilate the matte into a slightly jagged, hand-cut sticker border."""
    k = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (border * 2 + 1, border * 2 + 1))
    outer = cv2.dilate(mask, k)
    # jaggedness: low-frequency noise pushed through the edge
    h, w = mask.shape
    noise = cv2.resize(rng.random((h // 12 + 1, w // 12 + 1)).astype(np.float32), (w, h))
    jag = cv2.dilate(mask, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (border + 1, border + 1)))
    outer = np.where(noise > 0.5, outer, jag)
    return cv2.GaussianBlur(outer, (3, 3), 0)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("inp"); ap.add_argument("out")
    ap.add_argument("--border", type=int, default=0, help="sticker border px (0 = auto)")
    ap.add_argument("--bg", default="none")
    ap.add_argument("--shadow", action="store_true", default=True)
    a = ap.parse_args()

    w, h, fps = probe(a.inp)
    border = a.border or max(6, w // 45)
    seg = vision.ImageSegmenter.create_from_options(vision.ImageSegmenterOptions(
        base_options=mpt.BaseOptions(model_asset_path=MODEL),
        running_mode=vision.RunningMode.VIDEO, output_confidence_masks=True))

    dec = subprocess.Popen(["ffmpeg", "-v", "error", "-i", a.inp, "-f", "rawvideo", "-pix_fmt", "rgb24", "-"],
                           stdout=subprocess.PIPE)
    solid = a.bg != "none"
    enc_args = ["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgba", "-s", f"{w}x{h}",
                "-r", str(fps), "-i", "-", "-i", a.inp]
    if solid:
        c = a.bg.lstrip("#")
        enc_args += ["-filter_complex", f"color=0x{c}:s={w}x{h}:r={fps}[b];[b][0:v]overlay=shortest=1,format=yuv420p[v]",
                     "-map", "[v]", "-map", "1:a?", "-shortest", "-c:v", "libx264", "-crf", "18", "-c:a", "aac", a.out]
    else:
        enc_args += ["-map", "0:v", "-map", "1:a?", "-shortest",
                     "-c:v", "libvpx-vp9", "-pix_fmt", "yuva420p", "-b:v", "4M", "-c:a", "libopus", a.out]
    enc = subprocess.Popen(enc_args, stdin=subprocess.PIPE)

    rng = np.random.default_rng(7)
    prev = None
    i = 0
    while True:
        buf = dec.stdout.read(w * h * 3)
        if len(buf) < w * h * 3:
            break
        rgb = np.frombuffer(buf, np.uint8).reshape(h, w, 3)
        res = seg.segment_for_video(mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb), int(i * 1000 / fps))
        bgconf = res.confidence_masks[0].numpy_view()  # class 0 = background
        m = 1.0 - bgconf
        prev = m if prev is None else 0.6 * m + 0.4 * prev  # temporal smoothing kills flicker
        mask = (np.clip((prev - 0.35) / 0.3, 0, 1) * 255).astype(np.uint8)
        mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, np.ones((5, 5), np.uint8))
        if i % 6 == 0:  # re-roll the torn edge a few times a second = hand-animated 'boil'
            rng = np.random.default_rng(i)
        outer = torn_edge(mask, border, rng)

        out = np.zeros((h, w, 4), np.uint8)
        if a.shadow:
            sh = np.roll(np.roll(outer, border // 2, 0), border // 2, 1)
            sh = cv2.GaussianBlur(sh, (0, 0), border / 2)
            out[..., 3] = (sh * 0.35).astype(np.uint8)
        white = outer > 0
        out[white, :3] = 255
        out[..., 3] = np.maximum(out[..., 3], outer)
        alpha = mask.astype(np.float32)[..., None] / 255
        out[..., :3] = (rgb * alpha + out[..., :3] * (1 - alpha)).astype(np.uint8)
        enc.stdin.write(out.tobytes())
        i += 1
    enc.stdin.close(); enc.wait(); dec.wait()
    print(f"cutout: {i} frames -> {a.out}")


if __name__ == "__main__":
    main()
