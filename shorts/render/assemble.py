"""Deterministic video assembly with FFmpeg.

Generative models make the raw pieces (images, short clips, voice, music).
Everything else - timing, motion, cuts, captions, mixing, loudness and the
final encode - is plain FFmpeg, so the result is repeatable and cheap to fix
(a caption typo never means paying to regenerate video).
"""
from __future__ import annotations

import shlex
import subprocess
from dataclasses import dataclass, field
from pathlib import Path

W, H, FPS = 1080, 1920, 30
FONTS_DIR = Path(__file__).resolve().parents[2] / "assets" / "fonts"

# Motion presets for still images ("Ken Burns"). Expressions use `on` = output frame number.
MOTIONS = {
    "zoom_in":   ("min(1+0.0010*on,1.18)", "iw/2-(iw/zoom/2)", "ih/2-(ih/zoom/2)"),
    "zoom_out":  ("max(1.18-0.0010*on,1.0)", "iw/2-(iw/zoom/2)", "ih/2-(ih/zoom/2)"),
    "pan_left":  ("1.12", "(iw-iw/zoom)*(1-on/{N})", "ih/2-(ih/zoom/2)"),
    "pan_right": ("1.12", "(iw-iw/zoom)*(on/{N})", "ih/2-(ih/zoom/2)"),
    "pan_up":    ("1.12", "iw/2-(iw/zoom/2)", "(ih-ih/zoom)*(1-on/{N})"),
    "pan_down":  ("1.12", "iw/2-(iw/zoom/2)", "(ih-ih/zoom)*(on/{N})"),
    "static":    ("1.0", "0", "0"),
}


class RenderError(RuntimeError):
    pass


def run(cmd: list[str], timeout: int = 600) -> str:
    proc = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
    if proc.returncode != 0:
        tail = "\n".join(proc.stderr.strip().splitlines()[-12:])
        raise RenderError(f"ffmpeg failed: {shlex.join(cmd[:6])} ...\n{tail}")
    return proc.stderr


def render_still(image: Path, duration: float, motion: str, out: Path) -> Path:
    """Turn one image into a moving 9:16 clip. The image is first cover-cropped
    to 9:16 and upscaled 2x so zoompan moves smoothly instead of jittering."""
    frames = max(1, round(duration * FPS))
    z, x, y = (s.replace("{N}", str(frames)) for s in MOTIONS.get(motion, MOTIONS["zoom_in"]))
    vf = (
        f"scale={W*2}:{H*2}:force_original_aspect_ratio=increase,crop={W*2}:{H*2},"
        f"zoompan=z='{z}':x='{x}':y='{y}':d={frames}:s={W}x{H}:fps={FPS},"
        f"format=yuv420p,setsar=1"
    )
    run(["ffmpeg", "-y", "-loglevel", "error", "-loop", "1", "-i", str(image),
         "-vf", vf, "-frames:v", str(frames), "-r", str(FPS),
         "-c:v", "libx264", "-preset", "veryfast", "-crf", "18", "-an", str(out)])
    return out


def render_clip(video: Path, duration: float, out: Path, start: float = 0.0) -> Path:
    """Normalize an AI video clip: cover-crop to 9:16, fixed fps, trim, no audio.
    If the clip is shorter than needed, its last frame is held."""
    vf = (f"scale={W}:{H}:force_original_aspect_ratio=increase,crop={W}:{H},"
          f"fps={FPS},tpad=stop_mode=clone:stop_duration={duration:.3f},format=yuv420p,setsar=1")
    run(["ffmpeg", "-y", "-loglevel", "error", "-ss", f"{start:.3f}", "-i", str(video),
         "-vf", vf, "-t", f"{duration:.3f}", "-c:v", "libx264", "-preset", "veryfast",
         "-crf", "18", "-an", str(out)])
    return out


def concat(clips: list[Path], out: Path) -> Path:
    """Hard cuts between scenes (re-encoded once for exact timing)."""
    listfile = out.with_suffix(".txt")
    listfile.write_text("".join(f"file '{c.resolve()}'\n" for c in clips))
    run(["ffmpeg", "-y", "-loglevel", "error", "-f", "concat", "-safe", "0", "-i", str(listfile),
         "-c:v", "libx264", "-preset", "veryfast", "-crf", "18", "-r", str(FPS),
         "-pix_fmt", "yuv420p", str(out)])
    return out


@dataclass
class AudioPlan:
    narration: Path
    music: Path | None = None
    music_gain_db: float = -18.0              # music sits well under the voice
    sfx: list[tuple[Path, float, float]] = field(default_factory=list)  # (file, start_s, gain_db)
    target_lufs: float = -14.0               # common loudness target for mobile
    true_peak: float = -1.5
    loop: bool = False                       # cross-fade the music tail into the start


def _decode(path: Path, sr: int = 48000):
    import numpy as np
    raw = subprocess.run(["ffmpeg", "-loglevel", "error", "-i", str(path), "-f", "f32le", "-ac", "2",
                          "-ar", str(sr), "-"], capture_output=True, check=True, timeout=120).stdout
    return np.frombuffer(raw, np.float32).reshape(-1, 2).copy()


def _fit(x, n: int):
    import numpy as np
    if len(x) >= n:
        return x[:n]
    return np.concatenate([x, np.zeros((n - len(x), 2), np.float32)])


def mix_audio(plan: AudioPlan, duration: float, out: Path) -> Path:
    """Narration + ducked music + sound effects, loudness-normalized, 48 kHz stereo.

    The mix itself is done in numpy (exact lengths, no ffmpeg filter-graph end-of-stream quirks,
    which differ between ffmpeg versions and twice cut or hung the music on the build machine);
    ffmpeg only decodes the inputs and applies the final loudness normalisation."""
    import numpy as np
    sr = 48000
    n = int(round(duration * sr))
    voice = _fit(_decode(plan.narration, sr), n)
    mix = voice.copy()
    if plan.music:
        if plan.loop:
            bed = _decode(_loop_bed(plan.music, duration, out.with_suffix(".bed.wav")), sr)
        else:
            m = _decode(plan.music, sr)
            bed = np.tile(m, (n // max(1, len(m)) + 1, 1))
        bed = _fit(bed, n) * (10 ** (plan.music_gain_db / 20))
        # duck the music a further ~7 dB while the narrator speaks (20 ms attack, 300 ms release)
        level = np.abs(voice).max(axis=1)
        hop = 240                                        # 5 ms blocks
        blocks = level[: n // hop * hop].reshape(-1, hop).max(axis=1)
        env = np.zeros_like(blocks)
        a_att, a_rel = 1 - np.exp(-hop / (0.020 * sr)), 1 - np.exp(-hop / (0.300 * sr))
        e = 0.0
        for i, v in enumerate(blocks):
            e += (v - e) * (a_att if v > e else a_rel)
            env[i] = e
        duck = 1 - 0.55 * np.clip(env / 0.05, 0, 1)
        g = np.repeat(duck, hop)
        g = np.concatenate([g, np.full(n - len(g), g[-1] if len(g) else 1.0)])
        mix += bed * g[:, None]
    for (f, start, gain) in plan.sfx:
        fx = _decode(f, sr) * (10 ** (gain / 20))
        i = int(max(0.0, start) * sr)
        if i >= n:
            continue
        k = min(len(fx), n - i)
        mix[i:i + k] += fx[:k]
    raw = out.with_suffix(".raw.wav")
    import wave
    with wave.open(str(raw), "wb") as f:
        f.setnchannels(2)
        f.setsampwidth(2)
        f.setframerate(sr)
        f.writeframes((np.clip(mix, -1, 1) * 32767).astype("<i2").tobytes())
    run(["ffmpeg", "-y", "-loglevel", "error", "-i", str(raw),
         "-af", f"loudnorm=I={plan.target_lufs}:TP={plan.true_peak}:LRA=11,"
                f"apad=whole_dur={duration:.3f},atrim=start=0:end={duration:.3f}",
         "-ar", "48000", "-c:a", "pcm_s16le", str(out)], timeout=180)
    return out


def finalize(video: Path, audio: Path, ass: Path | None, out: Path) -> Path:
    """Burn captions, mux audio, final H.264/AAC encode for YouTube."""
    vf = "format=yuv420p"
    if ass:
        ass_arg = str(ass).replace(":", r"\:").replace("'", r"\'")
        vf = f"ass='{ass_arg}':fontsdir='{FONTS_DIR}',format=yuv420p"
    run(["ffmpeg", "-y", "-loglevel", "error", "-i", str(video), "-i", str(audio),
         "-vf", vf, "-map", "0:v:0", "-map", "1:a:0",
         "-c:v", "libx264", "-preset", "medium", "-crf", "19", "-profile:v", "high",
         "-r", str(FPS), "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "192k", "-ar", "48000",
         "-movflags", "+faststart", "-shortest", str(out)])
    return out


def _loop_bed(music: Path, duration: float, out: Path, fade: float = 1.0) -> Path:
    """Music bed exactly `duration` long whose end flows into its start: the second of music that
    would follow the last frame is cross-faded (equal power) over the first second, so a looping
    Short never jumps in the music."""
    import numpy as np
    sr = 48000
    raw = subprocess.run(["ffmpeg", "-loglevel", "error", "-i", str(music), "-f", "f32le", "-ac", "2",
                          "-ar", str(sr), "-"], capture_output=True, check=True).stdout
    x = np.frombuffer(raw, np.float32).reshape(-1, 2)
    n, c = int(round(duration * sr)), int(fade * sr)
    reps = (n + c) // len(x) + 1
    m = np.tile(x, (reps, 1))[: n + c].copy()
    head, tail = m[:n].copy(), m[n:n + c]
    t = np.linspace(0, np.pi / 2, c, dtype=np.float32)[:, None]
    head[:c] = head[:c] * np.sin(t) + tail * np.cos(t)
    pcm = (np.clip(head, -1, 1) * 32767).astype("<i2").tobytes()
    import wave
    with wave.open(str(out), "wb") as f:
        f.setnchannels(2)
        f.setsampwidth(2)
        f.setframerate(sr)
        f.writeframes(pcm)
    return out
