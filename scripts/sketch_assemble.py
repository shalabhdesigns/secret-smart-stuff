#!/usr/bin/env python3
"""Assemble an animated sketch from generated shots (runs on the GitHub runner).

Input: a JSON spec (see creative/pilot_haircut.json). Shots are downloaded from their (signed)
URLs, normalised to 1080x1920 @ 30 fps with stereo 48 kHz audio, cut together, then sound
effects / extra voice lines / music are mixed in numpy (exact timing), loudness-normalised to
-14 LUFS, captions burned in, and the result is published to a GitHub pre-release.

Shot fields:
  url | image (still) | black: true           source
  dur                                          seconds (stills/black; video: optional trim length)
  trim_start                                   seconds into the video
  keep_audio (default true)                    keep the clip's own audio (lip-synced speech)
  zoom: "in"|"out"|"shake"                     simple camera move (stills or video)
  flash_end: true                              white flash on the last 3 frames (camera flash)
  caption: "text", speaker: "dev"|...          one caption for the shot
  sounds: [{url|file, at, gain_db, reverb}]    extra audio relative to the shot start
"""
from __future__ import annotations

import json
import math
import subprocess
import sys
import tempfile
import wave
from pathlib import Path

import numpy as np
import requests

ROOT = Path(__file__).resolve().parents[1]
W, H, FPS, SR = 1080, 1920, 30, 48000
SPEAKER_COLOURS = {"dev": "&H0050D0FF", "rocky": "&H00B48CFF", "meera": "&H00D2D24B", "": "&H00FFFFFF"}


def run(cmd: list[str]) -> None:
    p = subprocess.run(cmd, capture_output=True, text=True)
    if p.returncode != 0:
        raise RuntimeError(" ".join(cmd[:4]) + "\n" + p.stderr[-1500:])


def fetch(src: str, out: Path) -> Path:
    if src.startswith("release:"):                      # release:<tag>/<file> (kept media, no expiry)
        tag, fn = src[len("release:"):].split("/", 1)
        out = out.with_name(out.stem + "_" + Path(fn).name)
        run(["gh", "release", "download", tag, "-p", fn, "-O", str(out), "--clobber"])
        return out
    if src.startswith("http"):
        r = requests.get(src, timeout=300)
        r.raise_for_status()
        out.write_bytes(r.content)
        return out
    return ROOT / src


def duration(p: Path) -> float:
    out = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(p)],
                         capture_output=True, text=True).stdout.strip()
    return float(out or 0)


def has_audio(p: Path) -> bool:
    out = subprocess.run(["ffprobe", "-v", "error", "-select_streams", "a", "-show_entries", "stream=index",
                          "-of", "csv=p=0", str(p)], capture_output=True, text=True).stdout.strip()
    return bool(out)


def decode(p: Path) -> np.ndarray:
    raw = subprocess.run(["ffmpeg", "-loglevel", "error", "-i", str(p), "-f", "f32le", "-ac", "2", "-ar", str(SR), "-"],
                         capture_output=True, check=True).stdout
    return np.frombuffer(raw, np.float32).reshape(-1, 2).copy()


def reverb(x: np.ndarray) -> np.ndarray:
    out = x.copy()
    for delay, g in ((0.031, 0.45), (0.067, 0.32), (0.113, 0.22), (0.171, 0.14)):
        d = int(delay * SR)
        out[d:] += x[:-d] * g
    return out * 0.8


def segment(i: int, shot: dict, tmp: Path) -> tuple[Path, float]:
    out = tmp / f"seg{i:02d}.mp4"
    vf_scale = f"scale={W}:{H}:force_original_aspect_ratio=increase:flags=lanczos,crop={W}:{H},setsar=1"
    zoom = shot.get("zoom")
    if shot.get("black"):
        d = float(shot.get("dur", 0.5))
        run(["ffmpeg", "-y", "-loglevel", "error", "-f", "lavfi", "-i", f"color=c=black:s={W}x{H}:r={FPS}:d={d}",
             "-f", "lavfi", "-i", f"anullsrc=r={SR}:cl=stereo", "-t", f"{d}", "-c:v", "libx264", "-pix_fmt", "yuv420p",
             "-c:a", "aac", "-shortest", str(out)])
        return out, d
    if shot.get("image"):
        src = fetch(shot["image"], tmp / f"img{i}.png")
        d = float(shot.get("dur", 2.0))
        frames = int(round(d * FPS))
        z = {"in": "min(1+0.0018*on,1.25)", "out": "max(1.2-0.0018*on,1.0)"}.get(zoom, "1.0")
        vf = (f"scale={W*2}:{H*2}:force_original_aspect_ratio=increase,crop={W*2}:{H*2},"
              f"zoompan=z='{z}':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':d={frames}:s={W}x{H}:fps={FPS},setsar=1")
        run(["ffmpeg", "-y", "-loglevel", "error", "-loop", "1", "-i", str(src), "-f", "lavfi", "-i",
             f"anullsrc=r={SR}:cl=stereo", "-vf", vf, "-t", f"{d}", "-c:v", "libx264", "-pix_fmt", "yuv420p",
             "-c:a", "aac", "-shortest", str(out)])
        return out, d
    src = fetch(shot["url"], tmp / f"clip{i}.mp4")
    ss = float(shot.get("trim_start", 0))
    full = duration(src)
    d = float(shot.get("dur") or (full - ss))
    vf = vf_scale
    if zoom == "in":
        vf += f",zoompan=z='min(1+0.0015*on,1.15)':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':d=1:s={W}x{H}:fps={FPS}"
    elif zoom == "shake":
        vf += ",crop=iw-40:ih-70:20+14*sin(t*55):35+12*cos(t*47),scale=1080:1920"
    if shot.get("flash_end"):
        vf += f",fade=t=out:st={max(0, d - 0.12):.2f}:d=0.12:color=white"
    a_in = ["-i", str(src)] if (shot.get("keep_audio", True) and has_audio(src)) else []
    cmd = ["ffmpeg", "-y", "-loglevel", "error", "-ss", f"{ss}", "-t", f"{d}", "-i", str(src)]
    if a_in:
        cmd += ["-vf", f"{vf},fps={FPS}", "-map", "0:v:0", "-map", "0:a:0", "-af", f"aresample={SR},apad",
                "-ac", "2"]
    else:
        cmd += ["-f", "lavfi", "-i", f"anullsrc=r={SR}:cl=stereo", "-vf", f"{vf},fps={FPS}", "-map", "0:v:0",
                "-map", "1:a:0"]
    cmd += ["-t", f"{d}", "-c:v", "libx264", "-preset", "medium", "-crf", "18", "-pix_fmt", "yuv420p",
            "-c:a", "aac", "-ar", str(SR), str(out)]
    run(cmd)
    return out, d


def ass_time(t: float) -> str:
    h, rem = divmod(t, 3600)
    m, s = divmod(rem, 60)
    return f"{int(h)}:{int(m):02d}:{s:05.2f}"


def captions(spec: dict, starts: list[float], durs: list[float], out: Path) -> Path:
    lines = ["[Script Info]", "ScriptType: v4.00+", f"PlayResX: {W}", f"PlayResY: {H}", "WrapStyle: 0", "",
             "[V4+ Styles]",
             "Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, "
             "Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, "
             "MarginL, MarginR, MarginV, Encoding",
             "Style: Cap,Inter,64,&H00FFFFFF,&H00FFFFFF,&H00000000,&H64000000,-1,0,0,0,100,100,0,0,1,7,3,2,80,80,420,1",
             "", "[Events]", "Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text"]
    for s, st, d in zip(spec["shots"], starts, durs):
        if not s.get("caption"):
            continue
        a = st + float(s.get("caption_at", 0.05))
        b = st + d - 0.05
        col = SPEAKER_COLOURS.get(s.get("speaker", ""), "&H00FFFFFF")
        txt = s["caption"].replace("\n", "\\N")
        ital = "\\i1" if s.get("inner") else ""
        lines.append(f"Dialogue: 0,{ass_time(a)},{ass_time(b)},Cap,,0,0,0,,{{\\c{col}{ital}\\fad(60,60)}}{txt}")
    out.write_text("\n".join(lines) + "\n")
    return out


def main(spec_path: str) -> int:
    spec = json.loads(Path(spec_path).read_text())
    name = spec["name"]
    tmp = Path(tempfile.mkdtemp(prefix="sketch_"))
    segs, durs = [], []
    for i, shot in enumerate(spec["shots"]):
        p, d = segment(i, shot, tmp)
        segs.append(p)
        durs.append(d)
    starts = [sum(durs[:i]) for i in range(len(durs))]
    total = sum(durs)
    (tmp / "list.txt").write_text("".join(f"file '{p}'\n" for p in segs))
    joined = tmp / "joined.mp4"
    run(["ffmpeg", "-y", "-loglevel", "error", "-f", "concat", "-safe", "0", "-i", str(tmp / "list.txt"),
         "-c", "copy", str(joined)])
    # audio: clip audio + overlays + music, mixed in numpy
    n = int(round(total * SR))
    base = decode(joined)
    mix = np.zeros((n, 2), np.float32)
    k = min(n, len(base))
    mix[:k] = base[:k]
    for i, shot in enumerate(spec["shots"]):
        for snd in shot.get("sounds") or []:
            src = fetch(snd.get("url") or snd["file"], tmp / f"snd{i}_{abs(hash(str(snd))) % 10**6}.audio")
            x = decode(src) * (10 ** (float(snd.get("gain_db", 0)) / 20))
            if snd.get("reverb"):
                x = reverb(x)
            at = float(snd.get("at", 0)) + (durs[i] if snd.get("from_end") else 0.0)
            a = max(0, int((starts[i] + at) * SR))
            if a >= n:
                continue
            m = min(len(x), n - a)
            mix[a:a + m] += x[:m]
    mu = spec.get("music")
    if mu:
        bed = decode(fetch(mu["file"], tmp / "music.audio"))
        bed = np.tile(bed, (n // max(1, len(bed)) + 1, 1))[:n] * (10 ** (float(mu.get("gain_db", -20)) / 20))
        env = np.ones(n, np.float32)
        for lo, hi in mu.get("mute_shots", []):            # e.g. the thriller spiral
            a, b = int(starts[lo] * SR), int((starts[hi] + durs[hi]) * SR)
            env[a:b] = 0.0
        fade = int(0.08 * SR)
        env = np.convolve(env, np.ones(fade) / fade, mode="same").astype(np.float32)
        mix += bed * env[:, None]
    raw = tmp / "mix.wav"
    with wave.open(str(raw), "wb") as f:
        f.setnchannels(2)
        f.setsampwidth(2)
        f.setframerate(SR)
        f.writeframes((np.clip(mix, -1, 1) * 32767).astype("<i2").tobytes())
    norm = tmp / "mix_norm.wav"
    run(["ffmpeg", "-y", "-loglevel", "error", "-i", str(raw), "-af",
         f"loudnorm=I=-14:TP=-1.5:LRA=11,apad=whole_dur={total:.3f},atrim=0:{total:.3f}", "-ar", str(SR), str(norm)])
    ass = captions(spec, starts, durs, tmp / "caps.ass")
    outdir = ROOT / "build" / name
    outdir.mkdir(parents=True, exist_ok=True)
    final = outdir / "final.mp4"
    fonts = ROOT / "assets" / "fonts"
    run(["ffmpeg", "-y", "-loglevel", "error", "-i", str(joined), "-i", str(norm), "-map", "0:v:0", "-map", "1:a:0",
         "-vf", f"ass='{ass}':fontsdir='{fonts}',format=yuv420p", "-c:v", "libx264", "-preset", "medium",
         "-crf", "19", "-profile:v", "high", "-r", str(FPS), "-c:a", "aac", "-b:a", "192k", "-movflags", "+faststart",
         "-shortest", str(final)])
    (outdir / "timeline.json").write_text(json.dumps({"starts": starts, "durs": durs, "total": total}, indent=1))
    print(json.dumps({"final": str(final), "seconds": round(total, 2)}))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1]))
