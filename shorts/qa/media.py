"""Technical checks on the rendered file - run before any human or AI review.

These are hard gates: a video that fails one never reaches the publish queue.
"""
from __future__ import annotations

import json
import re
import subprocess
from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class Check:
    name: str
    ok: bool
    detail: str
    hard: bool = True  # hard = blocks publishing; soft = warning for the reviewer


@dataclass
class MediaReport:
    path: str
    checks: list[Check] = field(default_factory=list)

    @property
    def passed(self) -> bool:
        return all(c.ok for c in self.checks if c.hard)

    def as_dict(self) -> dict:
        return {"path": self.path, "passed": self.passed,
                "checks": [c.__dict__ for c in self.checks]}


def _probe(path: Path) -> dict:
    out = subprocess.run(
        ["ffprobe", "-v", "error", "-print_format", "json", "-show_format", "-show_streams", str(path)],
        capture_output=True, text=True,
    )
    if out.returncode != 0:
        raise RuntimeError(out.stderr.strip())
    return json.loads(out.stdout)


def _ffmpeg_filter_log(path: Path, args: list[str]) -> str:
    out = subprocess.run(["ffmpeg", "-hide_banner", "-nostats", "-i", str(path), *args, "-f", "null", "-"],
                         capture_output=True, text=True)
    return out.stderr


def check_video(path: Path, max_seconds: float = 60.0, min_seconds: float = 8.0,
                expected_narration_s: float | None = None) -> MediaReport:
    rep = MediaReport(str(path))
    if not path.exists() or path.stat().st_size < 50_000:
        rep.checks.append(Check("file_exists", False, "missing or suspiciously small file"))
        return rep
    try:
        info = _probe(path)
    except RuntimeError as e:
        rep.checks.append(Check("decodable", False, f"ffprobe failed: {e}"))
        return rep

    v = next((s for s in info["streams"] if s["codec_type"] == "video"), None)
    a = next((s for s in info["streams"] if s["codec_type"] == "audio"), None)
    dur = float(info["format"].get("duration", 0))

    rep.checks.append(Check("has_video", v is not None, "video stream present" if v else "no video stream"))
    rep.checks.append(Check("has_audio", a is not None, "audio stream present" if a else "no audio stream"))
    if v:
        w, h = int(v["width"]), int(v["height"])
        rep.checks.append(Check("resolution", (w, h) == (1080, 1920), f"{w}x{h} (want 1080x1920)"))
        num, den = (int(x) for x in v.get("avg_frame_rate", "0/1").split("/"))
        fps = num / den if den else 0
        rep.checks.append(Check("frame_rate", 23.9 <= fps <= 60.1, f"{fps:.2f} fps"))
        rep.checks.append(Check("codec", v.get("codec_name") == "h264", v.get("codec_name", "?")))
    rep.checks.append(Check("duration", min_seconds <= dur <= max_seconds,
                            f"{dur:.2f}s (allowed {min_seconds}-{max_seconds}s)"))
    if expected_narration_s:
        rep.checks.append(Check("narration_fits", dur + 0.05 >= expected_narration_s,
                                f"video {dur:.2f}s vs narration {expected_narration_s:.2f}s"))

    if a:
        log = _ffmpeg_filter_log(path, ["-map", "0:a", "-af", "ebur128=peak=true"])
        m_i = re.findall(r"I:\s+(-?[\d.]+) LUFS", log)
        m_tp = re.findall(r"Peak:\s+(-?[\d.]+) dBFS", log)
        lufs = float(m_i[-1]) if m_i else None
        peak = float(m_tp[-1]) if m_tp else None
        rep.checks.append(Check("loudness", lufs is not None and -17.5 <= lufs <= -11.0,
                                f"integrated {lufs} LUFS (want about -14)"))
        rep.checks.append(Check("no_clipping", peak is not None and peak <= -0.5,
                                f"true peak {peak} dBFS (want <= -0.5)"))
        sil = _ffmpeg_filter_log(path, ["-map", "0:a", "-af", "silencedetect=noise=-45dB:d=1.2"])
        gaps = [float(x) for x in re.findall(r"silence_duration: ([\d.]+)", sil)]
        rep.checks.append(Check("no_long_silence", not gaps,
                                f"silent gaps: {gaps}" if gaps else "no silence over 1.2s"))
        lead = re.search(r"silence_start: (-?[\d.]+)", sil)
        rep.checks.append(Check("instant_start", not (lead and float(lead.group(1)) < 0.05 and gaps and gaps[0] > 0.6),
                                "audio starts immediately" if not lead else f"leading silence at {lead.group(1)}s",
                                hard=False))

    blk = _ffmpeg_filter_log(path, ["-map", "0:v", "-vf", "blackdetect=d=0.4:pix_th=0.08"])
    blacks = re.findall(r"black_start:([\d.]+) black_end:([\d.]+)", blk)
    rep.checks.append(Check("no_black_frames", not blacks,
                            f"black segments {blacks}" if blacks else "no black segments"))
    frz = _ffmpeg_filter_log(path, ["-map", "0:v", "-vf", "freezedetect=n=0.002:d=3"])
    freezes = re.findall(r"freeze_duration: ([\d.]+)", frz)
    rep.checks.append(Check("no_frozen_video", not freezes,
                            f"frozen segments {freezes}s" if freezes else "no frozen segments over 3s",
                            hard=False))
    return rep
