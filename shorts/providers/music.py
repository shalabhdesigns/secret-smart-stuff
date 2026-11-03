"""One-time music library via ElevenLabs Music (verified 2026-10-25).

POST https://api.elevenlabs.io/v1/music  -> raw mp3 bytes.  Creator plan: ~$0.15 per minute.
The key needs the `music_generation` permission. Tracks are generated ONCE, committed to
assets/music, and rotated across videos, so the per-video music cost is zero and the
music is original (no licensed-music revenue penalty on Shorts).
"""
from __future__ import annotations

from pathlib import Path

import requests

ENDPOINT = "https://api.elevenlabs.io/v1/music"

# Short, loop-friendly instrumental beds. Different moods so videos don't all sound alike.
BEDS = {
    "curious_pluck": "Light, curious instrumental: soft pizzicato strings and marimba, gentle ticking percussion, "
                     "100 BPM, playful but calm, steady loopable groove, no melody climax, no vocals",
    "warm_lofi": "Warm lo-fi hip hop instrumental, mellow keys, soft vinyl texture, 88 BPM, relaxed, "
                 "steady loopable groove, no vocals",
    "bright_pop": "Bright minimal electronic pop instrumental, clean synth plucks and light claps, 112 BPM, "
                  "upbeat and tidy, steady loopable groove, no vocals",
    "clockwork": "Minimal clockwork-style instrumental: woodblock ticks, soft kalimba and sub bass, 96 BPM, "
                 "inquisitive and precise, steady loopable groove, no vocals",
    "soft_piano": "Soft piano and light acoustic guitar instrumental, gentle brush percussion, 92 BPM, warm, "
                  "steady loopable groove, no vocals",
    "quirky_funk": "Quirky light funk instrumental, muted guitar, bouncy bass, finger snaps, 104 BPM, fun, "
                   "steady loopable groove, no vocals",
    # series beds (4 Nov 2026, Ramayana film series): used only when a topic asks for them (notes["music"])
    "series_epic_indian": "Original cinematic Indian epic instrumental: low strings, bansuri flute motif, tabla and "
                          "dhol pulse, soft choir pad, 92 BPM, majestic but restrained so a voice sits on top, "
                          "steady loopable groove, no big climax, no vocals",
    "series_epic_tech": "Original cinematic instrumental for a behind-the-scenes film-technology story: pulsing synth "
                        "arpeggio with tabla and low strings, light bansuri accents, 100 BPM, modern and wondrous, "
                        "steady loopable groove, no big climax, no vocals",
}


def generate_library(api_key: str, folder: Path, length_ms: int = 45000) -> list[Path]:
    folder.mkdir(parents=True, exist_ok=True)
    made = []
    for name, prompt in BEDS.items():
        out = folder / f"{name}.mp3"
        if out.exists():
            continue
        r = requests.post(ENDPOINT, params={"output_format": "mp3_44100_128"},
                          headers={"xi-api-key": api_key, "content-type": "application/json"},
                          json={"prompt": prompt, "music_length_ms": length_ms, "model_id": "music_v2_5",
                                "force_instrumental": True}, timeout=600)
        if r.status_code == 401:
            raise PermissionError("ElevenLabs key lacks the music_generation permission")
        if r.status_code != 200:
            raise RuntimeError(f"ElevenLabs music {r.status_code}: {r.text[:300]}")
        out.write_bytes(r.content)
        made.append(out)
    return made


SFX_ENDPOINT = "https://api.elevenlabs.io/v1/sound-generation"

# Small, tasteful set. Used sparingly and quietly by the renderer.
SFX = {
    "whoosh": ("soft quick air whoosh for a fast video transition, clean, subtle, no reverb tail", 0.6),
    "click": ("very soft, short UI click, clean and minimal, like a gentle tap", 0.5),
    "pop": ("soft gentle bubble pop, light and friendly, clean", 0.5),
    "chime": ("soft bright two-note chime for a positive reveal, clean, short", 1.2),
    "swipe": ("short paper slide swipe, clean, subtle", 0.6),
    "boing": ("short light comedic cartoon boing, playful, not loud", 0.7),
    "record_scratch": ("quick short vinyl record scratch for a comedic pause, light", 0.6),
}


def generate_sfx(api_key: str, folder: Path) -> list[Path]:
    folder.mkdir(parents=True, exist_ok=True)
    made = []
    for name, (prompt, secs) in SFX.items():
        out = folder / f"{name}.mp3"
        if out.exists():
            continue
        r = requests.post(SFX_ENDPOINT, params={"output_format": "mp3_44100_128"},
                          headers={"xi-api-key": api_key, "content-type": "application/json"},
                          json={"text": prompt, "duration_seconds": secs, "prompt_influence": 0.6}, timeout=300)
        if r.status_code == 401:
            raise PermissionError("ElevenLabs key lacks the sound_generation permission")
        if r.status_code != 200:
            raise RuntimeError(f"ElevenLabs SFX {r.status_code}: {r.text[:300]}")
        out.write_bytes(r.content)
        made.append(out)
    return made
