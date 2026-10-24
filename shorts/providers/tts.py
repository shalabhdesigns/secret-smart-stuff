"""Text to speech with word timings.

Live: ElevenLabs `/v1/text-to-speech/{voice}/with-timestamps`, which returns the
audio plus character-level timing. We convert that to word timings so captions
follow the real voice exactly.
Dry-run: a tone track with synthetic timings (clearly not speech).
"""
from __future__ import annotations

import base64
import time
import wave
from dataclasses import dataclass
from pathlib import Path

import numpy as np
import requests

from ..render.captions import Word, words_from_char_alignment

API = "https://api.elevenlabs.io/v1/text-to-speech/{voice}/with-timestamps"


@dataclass
class Speech:
    audio: Path
    words: list[Word]
    duration: float
    usd: float
    chars: int


class TTSError(RuntimeError):
    pass


class ElevenLabsTTS:
    def __init__(self, api_key: str, voice_id: str, model_id: str, usd_per_1k_chars: float):
        self.key, self.voice, self.model, self.rate = api_key, voice_id, model_id, usd_per_1k_chars

    def speak(self, text: str, out: Path, retries: int = 3) -> Speech:
        body = {"text": text, "model_id": self.model, "output_format": "mp3_44100_128"}
        headers = {"xi-api-key": self.key, "content-type": "application/json"}
        for attempt in range(retries):
            r = requests.post(API.format(voice=self.voice), json=body, headers=headers, timeout=180)
            if r.status_code in (429, 500, 502, 503):
                time.sleep(5 * (2 ** attempt))
                continue
            if r.status_code != 200:
                raise TTSError(f"ElevenLabs {r.status_code}: {r.text[:300]}")
            j = r.json()
            out.write_bytes(base64.b64decode(j["audio_base64"]))
            al = j.get("alignment") or j.get("normalized_alignment")
            if not al:
                raise TTSError("ElevenLabs returned no alignment data")
            words = words_from_char_alignment(al["characters"], al["character_start_times_seconds"],
                                              al["character_end_times_seconds"])
            dur = words[-1].end if words else 0.0
            return Speech(out, words, dur, len(text) / 1000 * self.rate, len(text))
        raise TTSError("ElevenLabs kept failing")


class FakeTTS:
    SR = 48000

    def speak(self, text: str, out: Path) -> Speech:
        words, t = [], 0.12
        for w in text.split():
            d = 0.16 + 0.045 * len(w)
            words.append(Word(w, t, t + d))
            t += d + 0.06 + (0.22 if w[-1:] in ".?!," else 0)
        total = t + 0.2
        a = np.zeros(int(total * self.SR))
        for w in words:
            s, e = int(w.start * self.SR), int(w.end * self.SR)
            n = e - s
            env = np.sin(np.pi * np.arange(n) / max(n, 1))
            a[s:e] += 0.3 * env * np.sin(2 * np.pi * (170 + 15 * len(w.text)) * np.arange(n) / self.SR)
        out = out.with_suffix(".wav")
        with wave.open(str(out), "wb") as f:
            f.setnchannels(1)
            f.setsampwidth(2)
            f.setframerate(self.SR)
            f.writeframes((np.clip(a, -1, 1) * 32767).astype("<i2").tobytes())
        return Speech(out, words, words[-1].end, 0.0, len(text))
