"""Voice lines: ElevenLabs (eleven_v4, Devanagari + audio tags) -> tight 48 kHz mono wavs.

Unchanged lines are reused across revisions (cache key = voice + text), so a fix only pays for the
lines that actually changed.
"""
from __future__ import annotations

import hashlib
import shutil
import subprocess
import sys
import time
import wave
from pathlib import Path

import numpy as np
import requests

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts" / "puppet"))

import prep_lines as PL  # noqa: E402

API = "https://api.elevenlabs.io/v1/text-to-speech/{voice}"
MODEL = "eleven_v4"
USD_PER_1K_CHARS = 0.18          # measured 2026-10-24 (config/pipeline.yaml providers.tts)


class VoiceError(RuntimeError):
    pass


def key(voice: str, text: str) -> str:
    return hashlib.sha1(f"{MODEL}|{voice}|{text}".encode()).hexdigest()[:16]


def tts(api_key: str, voice: str, text: str, out: Path, retries: int = 3) -> None:
    for attempt in range(retries):
        r = requests.post(API.format(voice=voice), params={"output_format": "mp3_44100_128"},
                          headers={"xi-api-key": api_key, "content-type": "application/json"},
                          json={"text": text, "model_id": MODEL}, timeout=180)
        if r.status_code in (429, 500, 502, 503):
            time.sleep(5 * (2 ** attempt))
            continue
        if r.status_code != 200:
            raise VoiceError(f"ElevenLabs {r.status_code}: {r.text[:300]}")
        out.write_bytes(r.content)
        return
    raise VoiceError("ElevenLabs kept failing")


def spoken_chars(text: str) -> int:
    import re
    return len(re.sub(r"\[[^\]]*\]", "", text).strip())


def seconds(p: Path) -> float:
    with wave.open(str(p)) as f:
        return f.getnframes() / f.getframerate()


def to_wav(mp3: Path, wav: Path, tempo: float, max_pause: float = 0.28) -> float:
    x = PL.tighten(PL.decode(mp3, tempo), max_pause)
    with wave.open(str(wav), "wb") as f:
        f.setnchannels(1)
        f.setsampwidth(2)
        f.setframerate(PL.SR)
        f.writeframes((np.clip(x, -1, 1) * 32767).astype("<i2").tobytes())
    return len(x) / PL.SR


def make(lines: list[dict], voices: dict[str, str], cache: Path, out: Path, api_key: str,
         tempo: float = 1.08, fake: bool = False) -> dict:
    """Write out/<line id>.wav for every line. Returns {"usd": spent, "seconds": {id: s}, "new": [ids]}."""
    cache.mkdir(parents=True, exist_ok=True)
    out.mkdir(parents=True, exist_ok=True)
    usd, secs, new = 0.0, {}, []
    for ln in lines:
        v = voices[ln["who"]]
        k = key(v, ln["hi"])
        mp3 = cache / f"{k}.mp3"
        if not mp3.exists():
            if fake:
                n = max(1.0, spoken_chars(ln["hi"]) / 14)
                subprocess.run(["ffmpeg", "-loglevel", "error", "-y", "-f", "lavfi", "-i",
                                f"sine=frequency=220:duration={n}", "-af", "volume=0.3,tremolo=f=6:d=0.9",
                                str(mp3)], check=True)
            else:
                tts(api_key, v, ln["hi"], mp3)
                usd += len(ln["hi"]) / 1000 * USD_PER_1K_CHARS
                # one retry if the take is implausibly long/short for the text (hallucinated or clipped)
                d = PL.decode(mp3, 1.0).size / PL.SR
                c = max(1, spoken_chars(ln["hi"]))
                if d > 0.35 * c + 4 or d < 0.025 * c:
                    tts(api_key, v, ln["hi"], mp3)
                    usd += len(ln["hi"]) / 1000 * USD_PER_1K_CHARS
            new.append(ln["id"])
        secs[ln["id"]] = round(to_wav(mp3, out / f"{ln['id']}.wav", tempo), 3)
        (out / f"{ln['id']}.txt").write_text(ln["hi"])          # words drive the mouth shapes (lip sync)
        shutil.copy(mp3, out / f"{ln['id']}.mp3")
    return {"usd": round(usd, 4), "seconds": secs, "new": new}
