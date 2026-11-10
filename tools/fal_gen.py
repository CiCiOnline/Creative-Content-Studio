#!/usr/bin/env python3
"""fal.ai generation runner for the studio (server-side; FAL_KEY stays in studio/.env).

Every command prints a cost estimate and stops. Add --yes to actually submit (billable).
Each submitted job is logged to projects/fal_jobs.jsonl with its request ID; use
`resume` to fetch a result instead of submitting again (a second submit is a new bill).

  voice-clone  --audio sample.wav [--name me]            clone your voice (≥10s clean audio)
  tts          --text "..." | --file script.txt [--voice me] [--speed 1.0]
  avatar       --image headshot.jpg --audio voice.mp3 [--prompt "..."]   talking video
  angles       --video take.mp4 --prompt-file shotlist.md [--res 480p|720p|1080p] [--draft]
  swap         --image look.jpg --video take.mp4 [--orientation video|image] [--prompt "..."]
  resume       --endpoint <id> --request-id <id>
"""
import argparse, json, os, subprocess, sys, time, urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
JOBS = ROOT / "projects" / "fal_jobs.jsonl"
VOICES = ROOT / "assets" / "voice" / "voices.json"
OUT = ROOT / "exports"

EP = {
    "voice-clone": "fal-ai/minimax/voice-clone",
    "tts": "fal-ai/minimax/speech-02-hd",
    "avatar": "bytedance/omnihuman/v2",
    "angles": "bytedance/seedance-2.5/us/reference-to-video",
    "swap": "fal-ai/kling-video/v3/standard/motion-control",
}


def load_env():
    """Load studio/.env into the process without printing anything."""
    f = ROOT / ".env"
    if f.exists():
        for line in f.read_text().splitlines():
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                k, _, v = line.partition("=")
                os.environ.setdefault(k.strip(), v.strip().strip("'\""))
    if not os.environ.get("FAL_KEY"):
        sys.exit("FAL_KEY is absent: run the fal key setup again (see CLAUDE.md).")


def duration(path):
    return float(subprocess.check_output(["ffprobe", "-v", "error", "-show_entries", "format=duration",
                                          "-of", "csv=p=0", str(path)]).decode().strip())


def need(path):
    p = Path(path)
    if not p.exists():
        sys.exit(f"file not found: {path}")
    return p


def upload(fal, path):
    print(f"  uploading {Path(path).name} ...")
    return fal.upload_file(str(path))


def save_url(url, stem, ext):
    OUT.mkdir(exist_ok=True)
    dest = OUT / f"{stem}_{time.strftime('%Y%m%d-%H%M%S')}.{ext}"
    if not url.startswith(("https://fal.media/", "https://v3.fal.media/", "https://v3b.fal.media/",
                           "https://storage.googleapis.com/falserverless/")):
        print(f"  result URL is not on a fal origin, not downloading: {url}")
        return None
    urllib.request.urlretrieve(url, dest)
    print(f"  saved {dest.relative_to(ROOT)}")
    return dest


def log_job(rec):
    JOBS.parent.mkdir(exist_ok=True)
    with JOBS.open("a") as f:
        f.write(json.dumps(rec) + "\n")


def run(fal, endpoint, args_, label):
    """Submit once via the queue, keep the request ID, then wait for the result."""
    h = fal.submit(endpoint, arguments=args_)
    rid = h.request_id
    log_job({"t": time.time(), "endpoint": endpoint, "request_id": rid, "label": label, "state": "submitted"})
    print(f"  submitted {endpoint}  request_id={rid}")
    last = None
    while True:
        st = h.status(with_logs=False)
        name = type(st).__name__
        if name != last:
            print(f"  status: {name}"); last = name
        if name == "Completed":
            break
        time.sleep(4)
    res = h.get()
    log_job({"t": time.time(), "endpoint": endpoint, "request_id": rid, "label": label, "state": "completed"})
    return rid, res


def confirm(est, a):
    print(f"Estimated cost: ~${est:.2f} (fal list price; check fal.ai/pricing for changes)")
    if not a.yes:
        print("Dry run: nothing was submitted. Re-run with --yes to generate.")
        sys.exit(0)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    p = sub.add_parser("voice-clone"); p.add_argument("--audio", required=True); p.add_argument("--name", default="me")
    p.add_argument("--preview", default="Hey, it's me. This is my cloned voice, ready for today's reel.")
    p = sub.add_parser("tts"); g = p.add_mutually_exclusive_group(required=True); g.add_argument("--text"); g.add_argument("--file")
    p.add_argument("--voice", default="me"); p.add_argument("--speed", type=float, default=1.0); p.add_argument("--emotion")
    p = sub.add_parser("avatar"); p.add_argument("--image", required=True); p.add_argument("--audio", required=True); p.add_argument("--prompt")
    p = sub.add_parser("angles"); p.add_argument("--video", required=True); p.add_argument("--prompt-file", required=True)
    p.add_argument("--res", default="720p", choices=["480p", "720p", "1080p"]); p.add_argument("--draft", action="store_true")
    p.add_argument("--no-audio", action="store_true")
    p = sub.add_parser("swap"); p.add_argument("--image", required=True); p.add_argument("--video", required=True)
    p.add_argument("--orientation", default="video", choices=["video", "image"]); p.add_argument("--prompt")
    p.add_argument("--drop-sound", action="store_true")
    p = sub.add_parser("resume"); p.add_argument("--endpoint", required=True); p.add_argument("--request-id", required=True)
    for s in sub.choices.values():
        s.add_argument("--yes", action="store_true", help="actually submit (billable)")
    a = ap.parse_args()

    load_env()
    import fal_client as fal

    if a.cmd == "voice-clone":
        src = need(a.audio)
        d = duration(src)
        if d < 10:
            sys.exit(f"voice sample is {d:.1f}s; fal needs at least 10s of clean speech.")
        confirm(1.5 + len(a.preview) * 0.3 / 1000, a)
        rid, res = run(fal, EP["voice-clone"], {"audio_url": upload(fal, src), "noise_reduction": True,
                       "need_volume_normalization": True, "text": a.preview, "model": "speech-02-hd"}, a.name)
        voices = json.loads(VOICES.read_text()) if VOICES.exists() else {}
        voices[a.name] = {"voice_id": res["custom_voice_id"], "created": time.time(), "request_id": rid}
        VOICES.parent.mkdir(parents=True, exist_ok=True); VOICES.write_text(json.dumps(voices, indent=1))
        print(f"  voice '{a.name}' saved to assets/voice/voices.json")
        print("  NOTE: MiniMax deletes a cloned voice unless it is used for TTS within 7 days.")
        if res.get("audio"): save_url(res["audio"]["url"], f"voice_{a.name}_preview", "mp3")

    elif a.cmd == "tts":
        text = Path(a.file).read_text() if a.file else a.text
        voices = json.loads(VOICES.read_text()) if VOICES.exists() else {}
        vid = voices.get(a.voice, {}).get("voice_id", a.voice)
        confirm(len(text) * 0.1 / 1000, a)
        vs = {"voice_id": vid, "speed": a.speed}
        if a.emotion: vs["emotion"] = a.emotion
        rid, res = run(fal, EP["tts"], {"text": text, "voice_setting": vs, "output_format": "url",
                       "language_boost": "English", "audio_setting": {"sample_rate": 44100, "format": "mp3"}}, a.voice)
        save_url(res["audio"]["url"], f"voice_{a.voice}", "mp3")

    elif a.cmd == "avatar":
        img, aud = need(a.image), need(a.audio)
        d = duration(aud)
        if not 4 <= d <= 300:
            sys.exit(f"audio is {d:.1f}s; OmniHuman needs 4-300s.")
        confirm(d * 0.105, a)
        args_ = {"image_url": upload(fal, img), "audio_url": upload(fal, aud)}
        if a.prompt: args_["prompt"] = a.prompt
        rid, res = run(fal, EP["avatar"], args_, img.stem)
        save_url(res["video"]["url"], f"avatar_{img.stem}", "mp4")

    elif a.cmd == "angles":
        vid = need(a.video)
        d = duration(vid)
        if not 1.8 <= d <= 30.2:
            sys.exit(f"clip is {d:.1f}s; Seedance accepts 1.8-30.2s per reference video. Cut it into segments first.")
        res_ = "480p" if a.draft else a.res
        w, h = {"480p": (480, 854), "720p": (720, 1280), "1080p": (1080, 1920)}[res_]
        rate = 0.0234 if res_ == "1080p" else 0.0214
        tokens = w * h * (d + d) * 24 / 1024          # input + output seconds (editing keeps duration)
        confirm(tokens / 1000 * rate * 0.6, a)        # x0.6 when video inputs are provided
        args_ = {"prompt": Path(a.prompt_file).read_text(), "task": "editing", "video_urls": [upload(fal, vid)],
                 "resolution": res_, "generate_audio": not a.no_audio, "draft": a.draft}
        rid, res = run(fal, EP["angles"], args_, vid.stem)
        save_url(res["video"]["url"], f"angles_{vid.stem}", "mp4")
        if res.get("draft_id"): print(f"  draft_id={res['draft_id']} (finish at 1080p within 7 days)")

    elif a.cmd == "swap":
        img, vid = need(a.image), need(a.video)
        d = duration(vid)
        cap = 30 if a.orientation == "video" else 10
        if d > cap:
            sys.exit(f"clip is {d:.1f}s; max {cap}s with orientation={a.orientation}.")
        confirm(d * 0.126, a)
        args_ = {"image_url": upload(fal, img), "video_url": upload(fal, vid), "character_orientation": a.orientation,
                 "keep_original_sound": not a.drop_sound}
        if a.prompt: args_["prompt"] = a.prompt
        rid, res = run(fal, EP["swap"], args_, vid.stem)
        save_url(res["video"]["url"], f"swap_{vid.stem}", "mp4")

    elif a.cmd == "resume":
        st = fal.status(a.endpoint, a.request_id, with_logs=False)
        print(f"  status: {type(st).__name__}")
        if type(st).__name__ == "Completed":
            res = fal.result(a.endpoint, a.request_id)
            for k in ("video", "audio"):
                if isinstance(res.get(k), dict) and res[k].get("url"):
                    save_url(res[k]["url"], f"resume_{a.request_id[:8]}", "mp4" if k == "video" else "mp3")
            print(json.dumps({k: v for k, v in res.items() if k not in ("video", "audio")}, indent=1))


if __name__ == "__main__":
    try:
        main()
    except Exception as e:  # surface fal billing/lock reasons verbatim, never retry silently
        msg = str(e)
        if "Exhausted balance" in msg or "locked" in msg.lower():
            sys.exit(f"fal refused the request: {msg}\nAdd credits at https://fal.ai/dashboard/usage-billing/credits")
        raise
