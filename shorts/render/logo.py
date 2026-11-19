"""The official Grand Theft Auto VI logo for covers and first screens (owner, 20 Nov 2026: "Why are we not using actual
GTA 6 logo instead. I want you to use that only").

assets/brand/gta6_logo.png is cut, unchanged, from Rockstar's own trailer end card (trailer_1, 77 s; the black
background made transparent), never redrawn. It marks the topic of a fan-commentary video; the channel's own name and
look stay ours, and every description says the channel is not affiliated with Rockstar Games.
"""
from __future__ import annotations

from pathlib import Path

from PIL import Image, ImageFilter

ROOT = Path(__file__).resolve().parents[2]
LOGOS = {"GTA 6": ROOT / "assets/brand/gta6_logo.png", "GTA VI": ROOT / "assets/brand/gta6_logo.png"}


def has_logo(badge: str | None) -> bool:
    return bool(badge) and badge.upper() in LOGOS and LOGOS[badge.upper()].exists()


def logo(badge: str, width: int, shadow: bool = True) -> Image.Image:
    """The logo `width` px wide on a transparent canvas, with a soft dark shadow so it reads on any picture."""
    lg = Image.open(LOGOS[badge.upper()]).convert("RGBA")
    lg = lg.resize((width, round(width * lg.height / lg.width)), Image.LANCZOS)
    if not shadow:
        return lg
    pad = width // 8
    canvas = Image.new("RGBA", (lg.width + 2 * pad, lg.height + 2 * pad), (0, 0, 0, 0))
    a = Image.new("L", canvas.size, 0)
    a.paste(lg.getchannel("A"), (pad, pad))
    a = a.filter(ImageFilter.MaxFilter(9)).filter(ImageFilter.GaussianBlur(pad // 3))
    sh = Image.new("RGBA", canvas.size, (8, 0, 16, 0))
    sh.putalpha(a.point(lambda v: min(235, int(v * 1.4))))
    canvas.alpha_composite(sh)
    canvas.alpha_composite(lg, (pad, pad))
    return canvas


def frame_png(badge: str, out: Path, width: int, center: tuple[int, int], size=(1080, 1920)) -> Path:
    """A full-frame transparent PNG with the logo at `center` (for ffmpeg overlay)."""
    f = Image.new("RGBA", size, (0, 0, 0, 0))
    lg = logo(badge, width)
    f.alpha_composite(lg, (center[0] - lg.width // 2, center[1] - lg.height // 2))
    f.save(out)
    return out
