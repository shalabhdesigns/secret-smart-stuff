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


def mix_audio(plan: AudioPlan, duration: float, out: Path) -> Path:
    """Narration + ducked music + sound effects, loudness-normalized, 48 kHz stereo."""
    inputs = ["-i", str(plan.narration)]
    filters = ["[0:a]aformat=sample_rates=48000:channel_layouts=stereo,asplit=2[voice][key]"]
    mix_in = ["[voice]"]
    idx = 1
    if plan.music:
        inputs += ["-stream_loop", "-1", "-i", str(plan.music)]
        filters.append(
            f"[{idx}:a]aformat=sample_rates=48000:channel_layouts=stereo,"
            f"volume={plan.music_gain_db}dB,atrim=0:{duration:.3f}[mraw]"
        )
        # duck the music further whenever the narrator speaks
        filters.append("[mraw][key]sidechaincompress=threshold=0.03:ratio=8:attack=20:release=300[music]")
        mix_in.append("[music]")
        idx += 1
    else:
        filters.append("[key]anullsink")
    for (f, start, gain) in plan.sfx:
        inputs += ["-i", str(f)]
        ms = int(start * 1000)
        filters.append(
            f"[{idx}:a]aformat=sample_rates=48000:channel_layouts=stereo,volume={gain}dB,"
            f"adelay={ms}|{ms}[s{idx}]"
        )
        mix_in.append(f"[s{idx}]")
        idx += 1
    filters.append(
        f"{''.join(mix_in)}amix=inputs={len(mix_in)}:duration=first:normalize=0,"
        f"apad,atrim=0:{duration:.3f},"
        f"loudnorm=I={plan.target_lufs}:TP={plan.true_peak}:LRA=11[out]"
    )
    run(["ffmpeg", "-y", "-loglevel", "error", *inputs, "-filter_complex", ";".join(filters),
         "-map", "[out]", "-ar", "48000", "-c:a", "pcm_s16le", str(out)])
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
