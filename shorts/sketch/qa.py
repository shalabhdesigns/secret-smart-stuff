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
    if not 25 <= dur <= 58:
        issues.append(f"length {dur:.1f}s (want 35-45)")
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
