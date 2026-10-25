"""Procedural sound effects (zero cost, always available) + music bed selection.

Whooshes, ticks, pops and a soft "ding" are synthesized with numpy, so the
pipeline never depends on an external service for sound design. Music beds are
original tracks generated once (ElevenLabs Music) and stored in assets/music;
they rotate per video. If none exist, the video simply has no bed.
"""
from __future__ import annotations

import hashlib
import wave
from pathlib import Path

import numpy as np

SR = 48000
ASSETS = Path(__file__).resolve().parents[2] / "assets"


def _write(path: Path, a: np.ndarray) -> Path:
    a = np.clip(a, -1, 1)
    with wave.open(str(path), "wb") as f:
        f.setnchannels(1)
        f.setsampwidth(2)
        f.setframerate(SR)
        f.writeframes((a * 32767).astype("<i2").tobytes())
    return path


def _env(n: int, attack: float, decay: float) -> np.ndarray:
    t = np.arange(n) / SR
    return np.minimum(t / max(attack, 1e-4), 1.0) * np.exp(-np.maximum(t - attack, 0) / max(decay, 1e-4))


def whoosh(path: Path, dur: float = 0.32) -> Path:
    n = int(dur * SR)
    rng = np.random.default_rng(7)
    noise = rng.standard_normal(n)
    # band-pass by simple moving averages (cheap) + sweep via envelope shaping
    k = 24
    low = np.convolve(noise, np.ones(k) / k, mode="same")
    band = noise - low
    env = _env(n, 0.09, 0.09)
    return _write(path, 0.5 * band * env)


def tick(path: Path) -> Path:
    n = int(0.06 * SR)
    t = np.arange(n) / SR
    return _write(path, 0.6 * np.sin(2 * np.pi * 1900 * t) * _env(n, 0.002, 0.012))


def pop(path: Path) -> Path:
    n = int(0.14 * SR)
    t = np.arange(n) / SR
    f = 520 * np.exp(-t * 18) + 140
    return _write(path, 0.7 * np.sin(2 * np.pi * np.cumsum(f) / SR) * _env(n, 0.003, 0.05))


def ding(path: Path) -> Path:
    n = int(0.9 * SR)
    t = np.arange(n) / SR
    tone = (np.sin(2 * np.pi * 1046 * t) + 0.5 * np.sin(2 * np.pi * 2093 * t) + 0.25 * np.sin(2 * np.pi * 3136 * t))
    return _write(path, 0.35 * tone * _env(n, 0.004, 0.28))


def riser(path: Path, dur: float = 0.8) -> Path:
    n = int(dur * SR)
    t = np.arange(n) / SR
    rng = np.random.default_rng(3)
    noise = rng.standard_normal(n)
    k = 60
    hp = noise - np.convolve(noise, np.ones(k) / k, mode="same")
    env = (t / dur) ** 2.2
    return _write(path, 0.35 * hp * env)


def build_library(folder: Path) -> dict[str, Path]:
    folder.mkdir(parents=True, exist_ok=True)
    lib = {"whoosh": whoosh(folder / "whoosh.wav"), "tick": tick(folder / "tick.wav"),
           "pop": pop(folder / "pop.wav"), "ding": ding(folder / "ding.wav"),
           "riser": riser(folder / "riser.wav")}
    return lib


def pick_music(job_id: str) -> Path | None:
    folder = ASSETS / "music"
    tracks = sorted(folder.glob("*.mp3")) + sorted(folder.glob("*.wav")) if folder.exists() else []
    if not tracks:
        return None
    i = int(hashlib.md5(job_id.encode()).hexdigest(), 16) % len(tracks)
    return tracks[i]
