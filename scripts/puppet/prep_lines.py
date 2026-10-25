#!/usr/bin/env python3
"""Turn voice-line mp3s into tight 48 kHz mono wavs: trim the ends, shorten long pauses.

usage: prep_lines.py in_dir out_dir [max_pause_s=0.28] name1 name2 ...
"""
from __future__ import annotations

import subprocess
import sys
import wave
from pathlib import Path

import numpy as np

SR = 48000


def decode(p: Path, tempo: float = float(__import__("os").environ.get("TEMPO", "1.08"))) -> np.ndarray:
    raw = subprocess.run(["ffmpeg", "-loglevel", "error", "-i", str(p), "-af", f"atempo={tempo}", "-f", "f32le", "-ac", "1", "-ar", str(SR), "-"],
                         capture_output=True, check=True).stdout
    return np.frombuffer(raw, np.float32).copy()


def tighten(x: np.ndarray, max_pause: float) -> np.ndarray:
    hop = SR // 100
    env = np.array([np.sqrt((x[i:i + hop] ** 2).mean() + 1e-12) for i in range(0, len(x), hop)])
    db = 20 * np.log10(env + 1e-9)
    thr = np.percentile(db, 95) - 35
    loud = db > thr
    if not loud.any():
        return x
    first, last = np.argmax(loud), len(loud) - np.argmax(loud[::-1])
    keep = []
    i = first
    run = 0
    for i in range(max(0, first - 4), min(len(loud), last + 6)):
        if loud[i]:
            run = 0
            keep.append(i)
        else:
            run += 1
            if run * hop / SR <= max_pause:
                keep.append(i)
    out = np.concatenate([x[k * hop:(k + 1) * hop] for k in keep])
    fade = int(0.004 * SR)  # tiny crossfades are unnecessary at hop joins in silence; fade the ends only
    out[:fade] *= np.linspace(0, 1, fade)
    out[-fade:] *= np.linspace(1, 0, fade)
    return out


def main() -> int:
    src, dst, max_pause, *names = sys.argv[1:]
    out = Path(dst)
    out.mkdir(parents=True, exist_ok=True)
    for n in names:
        x = tighten(decode(Path(src) / f"{n}.mp3"), float(max_pause))
        with wave.open(str(out / f"{n}.wav"), "wb") as f:
            f.setnchannels(1)
            f.setsampwidth(2)
            f.setframerate(SR)
            f.writeframes((np.clip(x, -1, 1) * 32767).astype("<i2").tobytes())
        print(f"{n}: {len(x) / SR:.2f}s")
    return 0


if __name__ == "__main__":
    sys.exit(main())
