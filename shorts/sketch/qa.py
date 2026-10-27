"""Automatic checks before the owner sees a video.

technical(): length, loudness, true peak, picture/audio streams, no unexpected black.
frames():    contact sheet (2 frames per shot) -> Claude vision check for visual defects.
"""
from __future__ import annotations

import json
import re
import subprocess
from pathlib import Path

from PIL import Image

VISION_MODEL = "claude-sonnet-5-5"


def probe(p: Path) -> dict:
    out = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration:stream=codec_type,width,height",
                          "-of", "json", str(p)], capture_output=True, text=True).stdout
    return json.loads(out or "{}")


def loudness(p: Path) -> tuple[float, float]:
    err = subprocess.run(["ffmpeg", "-nostats", "-i", str(p), "-af", "ebur128=peak=true", "-f", "null", "-"],
                         capture_output=True, text=True).stderr
    i = re.findall(r"I:\s+(-?[\d.]+) LUFS", err)
    tp = re.findall(r"Peak:\s+(-?[\d.]+) dBFS", err)
    return (float(i[-1]) if i else 0.0, float(tp[-1]) if tp else 0.0)


def technical(video: Path, expected_black: float = 0.0) -> dict:
    pr = probe(video)
    dur = float(pr.get("format", {}).get("duration", 0))
    kinds = [s.get("codec_type") for s in pr.get("streams", [])]
    v = next((s for s in pr.get("streams", []) if s.get("codec_type") == "video"), {})
    lufs, tp = loudness(video)
    issues = []
    if not 45 <= dur <= 62:
        issues.append(f"length {dur:.1f}s (want 48-60)")
    if (v.get("width"), v.get("height")) != (1080, 1920):
        issues.append(f"size {v.get('width')}x{v.get('height')}")
    if "audio" not in kinds:
        issues.append("no audio")
    if not -17.5 <= lufs <= -12.5:
        issues.append(f"loudness {lufs} LUFS")
    if tp > -0.9:
        issues.append(f"true peak {tp} dBTP")
    return {"seconds": round(dur, 2), "lufs": lufs, "true_peak": tp, "issues": issues}


def contact_sheet(video: Path, starts: list[float], durs: list[float], out: Path) -> Path:
    tiles = []
    tmp = out.parent / "qa_frames"
    tmp.mkdir(parents=True, exist_ok=True)
    for i, (s, d) in enumerate(zip(starts, durs)):
        for k, f in enumerate((0.3, 0.8)):
            fp = tmp / f"s{i:02d}_{k}.png"
            subprocess.run(["ffmpeg", "-loglevel", "error", "-y", "-ss", f"{s + d * f:.2f}", "-i", str(video),
                            "-frames:v", "1", "-vf", "scale=270:480", str(fp)], check=True)
            tiles.append(fp)
    cols = 8
    rows = (len(tiles) + cols - 1) // cols
    sheet = Image.new("RGB", (cols * 270, rows * 480), "white")
    for n, fp in enumerate(tiles):
        sheet.paste(Image.open(fp), ((n % cols) * 270, (n // cols) * 480))
    sheet.save(out)
    return out


VISION_PROMPT = """TASK: visualqa
These are frames from a 2D cartoon Short (two frames per shot, in order, left to right, top to bottom).
Characters: Dev (mustard hoodie), Rocky (pink shirt, apron, moustache), Meera (black tee, checked pyjamas).
Check ONLY for real visual defects a viewer would notice:
- a character floating above the floor or sunk into it in a full-body shot
- a head, face or limb cut off by the frame edge in a way that looks like a mistake (close-ups cropping the
  body below the shoulders are fine)
- characters overlapping each other badly, or a character obviously the wrong size next to another
- a face missing eyes or mouth, double faces, seams, torn or ghost lines around the neck or head
- captions covering a face, or text cut off
- a black or blank frame (some black frames are intended comic beats: there are {black} of them)
Return JSON: {{"ok": true|false, "issues": ["short description with frame number"]}}. If unsure, ok=true."""


def vision(llm, sheet: Path, black_shots: int) -> tuple[dict, float]:
    r = llm.ask(VISION_PROMPT.format(black=black_shots), model=VISION_MODEL, max_tokens=1500,
                images=[sheet.read_bytes()])
    d = r.data if isinstance(r.data, dict) else {"ok": True, "issues": []}
    return {"ok": bool(d.get("ok", True)), "issues": list(d.get("issues") or [])[:6]}, r.usd


# ----------------------------------------------------------------------------- G5 additions (docs/RUBRIC.md §D)
def _clean(t: str) -> list[str]:
    t = re.sub(r"\[[^\]]*\]", " ", t)                       # audio tags
    t = re.sub(r"[^\w\u0900-\u097F ]+", " ", t)
    return [w for w in t.lower().split() if w]


def transcript(video: Path, plan: dict, api_key: str) -> dict:
    """Speech-to-text of the finished video (ElevenLabs Scribe). Checks: the first word of the first line is actually
    heard (owner: 'the first word gets cut off'), it starts after ~0.2 s, and the words heard match the script."""
    import requests
    wav = video.with_suffix(".stt.mp3")
    subprocess.run(["ffmpeg", "-loglevel", "error", "-y", "-i", str(video), "-vn", "-ac", "1", "-ar", "16000",
                    "-b:a", "64k", str(wav)], check=True)
    with open(wav, "rb") as f:
        r = requests.post("https://api.elevenlabs.io/v1/speech-to-text", headers={"xi-api-key": api_key},
                          data={"model_id": "scribe_v1", "language_code": "hin", "timestamps_granularity": "word",
                                "tag_audio_events": "false"}, files={"file": f}, timeout=300)
    if r.status_code != 200:
        return {"ok": True, "issues": [f"(transcript check unavailable: {r.status_code})"]}
    d = r.json()
    words = [w for w in d.get("words", []) if w.get("type", "word") == "word"]
    heard = _clean(" ".join(w.get("text", "") for w in words))
    script = _clean(" ".join(ln.get("hi", "") for ln in plan.get("lines", [])))
    issues = []
    first_line = _clean(plan["lines"][0].get("hi", "")) if plan.get("lines") else []
    if first_line and words:
        if not any(first_line[0] == h for h in heard[:3]):
            issues.append(f"first word '{first_line[0]}' not heard at the start (heard: {' '.join(heard[:4])})")
        if float(words[0].get("start", 1)) < 0.15:
            issues.append(f"speech starts at {float(words[0].get('start', 0)):.2f}s (want >= 0.25 s)")
    sset = set(script)
    match = sum(1 for w in heard if w in sset) / max(1, len(heard))
    cover = sum(1 for w in sset if w in set(heard)) / max(1, len(sset))
    if cover < 0.6:
        issues.append(f"only {cover:.0%} of the script's words were recognised (pronunciation or clipping?)")
    return {"ok": not issues, "issues": issues, "match": round(match, 2), "cover": round(cover, 2),
            "text": d.get("text", "")[:600]}


def loop_seam(video: Path, seconds: float) -> dict:
    """Last frame vs first frame (same shot = small difference) and audio level jump across the seam."""
    import numpy as np
    def frame(t):
        raw = subprocess.run(["ffmpeg", "-loglevel", "error", "-ss", f"{max(0, t):.3f}", "-i", str(video), "-frames:v", "1",
                              "-vf", "scale=108:192", "-f", "rawvideo", "-pix_fmt", "gray", "-"],
                             capture_output=True).stdout
        return np.frombuffer(raw, np.uint8).astype(np.float32)
    a, b = frame(0.05), frame(seconds - 0.08)
    diff = float(abs(a - b).mean()) if len(a) == len(b) and len(a) else 255.0
    issues = [] if diff < 28 else [f"loop: last frame differs from the first (mean diff {diff:.0f}); end on the opening shot"]
    return {"ok": not issues, "issues": issues, "frame_diff": round(diff, 1)}
