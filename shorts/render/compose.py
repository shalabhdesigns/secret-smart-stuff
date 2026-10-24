"""Frame-by-frame scene renderer (Python + Pillow -> FFmpeg pipe).

This is where the channel's "living blueprint" look comes from:
- smooth Ken Burns motion on the AI image (sub-pixel, no zoompan jitter)
- blueprint callouts (circle + leader line + label) that DRAW ON over ~0.6 s
  and stay locked to the object while the camera moves
- blueprint cards: paper, grid, ink text, accent underline
- comparison scenes: two images stacked with labels

Everything is deterministic: same inputs -> same video.
"""
from __future__ import annotations

import math
import subprocess
from dataclasses import dataclass, field
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

W, H, FPS = 1080, 1920, 30
FONTS = Path(__file__).resolve().parents[2] / "assets" / "fonts"
CAPTION_BAND = (1080, 1290)      # keep labels out of the caption band
SAFE_TOP, SAFE_BOTTOM = 260, 1480  # top bar / bottom title+buttons on phones
SAFE_RIGHT = W - 150


def _font(size: int, weight: str = "ExtraBold") -> ImageFont.FreeTypeFont:
    return ImageFont.truetype(str(FONTS / f"Inter-{weight}.otf"), size)


def _hex(c: str) -> tuple[int, int, int]:
    c = c.lstrip("#")
    return tuple(int(c[i:i + 2], 16) for i in (0, 2, 4))  # type: ignore[return-value]


def ease(t: float) -> float:
    t = max(0.0, min(1.0, t))
    return t * t * (3 - 2 * t)


@dataclass
class Callout:
    box: tuple[float, float, float, float]  # x, y, w, h as fractions of the SOURCE image (center x,y)
    label: str
    at: float = 0.35                        # seconds after scene start when drawing begins


@dataclass
class Scene:
    kind: str                       # hero | detail | context | comparison | blueprint_card
    duration: float
    image: Path | None = None
    image2: Path | None = None      # comparison only
    labels: tuple[str, str] = ("", "")
    motion: str = "zoom_in"
    callouts: list[Callout] = field(default_factory=list)
    card_text: str = ""


@dataclass
class Palette:
    paper: tuple[int, int, int] = (244, 239, 230)
    ink: tuple[int, int, int] = (20, 33, 61)
    accent: tuple[int, int, int] = (242, 107, 29)

    @classmethod
    def from_cfg(cls, d: dict) -> "Palette":
        return cls(_hex(d["paper"]), _hex(d["ink"]), _hex(d["accent"]))


# ---------------- camera ----------------

def _camera(motion: str, p: float) -> tuple[float, float, float]:
    """Return (zoom, cx, cy) - cx/cy are the source-image fraction at frame center."""
    e = ease(p) * 0.85 + p * 0.15
    if motion == "zoom_in":
        return 1.0 + 0.16 * e, 0.5, 0.5
    if motion == "zoom_out":
        return 1.16 - 0.16 * e, 0.5, 0.5
    if motion == "pan_left":
        return 1.14, 0.56 - 0.12 * e, 0.5
    if motion == "pan_right":
        return 1.14, 0.44 + 0.12 * e, 0.5
    if motion == "pan_up":
        return 1.14, 0.5, 0.56 - 0.12 * e
    if motion == "pan_down":
        return 1.14, 0.5, 0.44 + 0.12 * e
    return 1.0, 0.5, 0.5


class _Cam:
    def __init__(self, img: Image.Image, motion: str):
        self.img, self.motion = img, motion
        self.iw, self.ih = img.size
        self.base = max(W / self.iw, H / self.ih)

    def frame(self, p: float, size=(W, H)) -> tuple[Image.Image, callable]:
        z, cx, cy = _camera(self.motion, p)
        s = max(size[0] / self.iw, size[1] / self.ih) * z   # cover-fit, then zoom
        # keep the visible window inside the image
        half_w, half_h = size[0] / 2 / s, size[1] / 2 / s
        cxp = min(max(cx * self.iw, half_w), self.iw - half_w)
        cyp = min(max(cy * self.ih, half_h), self.ih - half_h)
        a, c = 1 / s, cxp - half_w
        e, f = 1 / s, cyp - half_h
        out = self.img.transform(size, Image.AFFINE, (a, 0, c, 0, e, f), resample=Image.BICUBIC)

        def to_out(fx: float, fy: float) -> tuple[float, float]:
            return ((fx * self.iw - c) * s, (fy * self.ih - f) * s)
        return out, to_out


# ---------------- overlays ----------------

def _label_box(d: ImageDraw.ImageDraw, text: str, anchor: tuple[float, float], pal: Palette,
               alpha: float) -> tuple[float, float, float, float]:
    f = _font(46, "ExtraBold")
    tw = d.textlength(text.upper(), font=f)
    pad = 22
    bw, bh = tw + pad * 2, 46 + pad * 2
    x = min(max(anchor[0] - bw / 2, 60), SAFE_RIGHT - bw)
    y = anchor[1] - bh / 2
    a = int(255 * alpha)
    d.rounded_rectangle([x, y, x + bw, y + bh], radius=14, fill=pal.paper + (a,),
                        outline=pal.ink + (a,), width=4)
    d.text((x + pad, y + pad - 4), text.upper(), font=f, fill=pal.ink + (a,))
    return x, y, bw, bh


def _draw_callout(base: Image.Image, co: Callout, to_out, t_local: float, pal: Palette) -> None:
    p = ease((t_local - co.at) / 0.6)
    if p <= 0:
        return
    fx, fy, fw, fh = co.box
    cx, cy = to_out(fx, fy)
    rx_edge, _ = to_out(fx + fw / 2, fy)
    _, ry_edge = to_out(fx, fy + fh / 2)
    rx, ry = max(60, abs(rx_edge - cx) * 1.1), max(60, abs(ry_edge - cy) * 1.1)
    ov = Image.new("RGBA", base.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(ov)
    # ellipse draws on as an arc
    d.arc([cx - rx, cy - ry, cx + rx, cy + ry], start=-90, end=-90 + 360 * p,
          fill=pal.accent + (255,), width=10)
    # label placement: above the target, but outside the caption band and safe areas
    ly = cy - ry - 170
    if ly < SAFE_TOP + 40:
        ly = cy + ry + 170
    if CAPTION_BAND[0] - 60 < ly < CAPTION_BAND[1] + 60:
        ly = CAPTION_BAND[0] - 90 if cy < (CAPTION_BAND[0] + CAPTION_BAND[1]) / 2 else CAPTION_BAND[1] + 90
    ly = min(max(ly, SAFE_TOP + 40), SAFE_BOTTOM - 60)
    lp = ease((t_local - co.at - 0.25) / 0.45)
    if lp > 0:
        start = (cx, cy - ry if ly < cy else cy + ry)
        end = (cx + (0 if abs(cx - W / 2) < 200 else (W / 2 - cx) * 0.3), ly)
        mid = (start[0] + (end[0] - start[0]) * lp, start[1] + (end[1] - start[1]) * lp)
        d.line([start, mid], fill=pal.ink + (255,), width=6)
        if lp > 0.6:
            _label_box(d, co.label, end, pal, ease((lp - 0.6) / 0.4))
    base.alpha_composite(ov)


def _blueprint_card(text: str, p: float, pal: Palette) -> Image.Image:
    img = Image.new("RGBA", (W, H), pal.paper + (255,))
    d = ImageDraw.Draw(img)
    grid = tuple(int(c * 0.9 + i * 0.1) for c, i in zip(pal.paper, pal.ink)) + (255,)
    off = int(p * 40)
    for x in range(-80 + off, W, 80):
        d.line([(x, 0), (x, H)], fill=grid, width=2)
    for y in range(-80 + off, H, 80):
        d.line([(0, y), (W, y)], fill=grid, width=2)
    for (x, y) in [(70, 300), (W - 130, 300), (70, 1560), (W - 130, 1560)]:  # corner registration marks
        d.line([(x, y + 30), (x + 60, y + 30)], fill=pal.ink + (255,), width=4)
        d.line([(x + 30, y), (x + 30, y + 60)], fill=pal.ink + (255,), width=4)
    lines = [ln.strip() for ln in text.replace("·", "\n").split("\n") if ln.strip()]
    f = _font(104 if len(lines) <= 3 else 84, "Black")
    total = len(lines) * 130
    y0 = 760 - total / 2
    for i, ln in enumerate(lines):
        li = ease((p * 1.6) - i * 0.18)
        if li <= 0:
            continue
        tw = d.textlength(ln.upper(), font=f)
        x = (W - tw) / 2
        y = y0 + i * 130 + (1 - li) * 30
        d.text((x, y), ln.upper(), font=f, fill=pal.ink + (int(255 * li),))
        d.line([(x, y + 118), (x + tw * li, y + 118)], fill=pal.accent + (255,), width=8)
    return img


# ---------------- scene -> frames ----------------

def scene_frames(scene: Scene, pal: Palette):
    n = max(1, round(scene.duration * FPS))
    if scene.kind == "blueprint_card":
        for i in range(n):
            yield _blueprint_card(scene.card_text, i / max(n - 1, 1), pal).convert("RGB")
        return
    if scene.kind == "comparison" and scene.image2:
        ca = _Cam(Image.open(scene.image).convert("RGB"), "zoom_in")
        cb = _Cam(Image.open(scene.image2).convert("RGB"), "zoom_out")
        for i in range(n):
            p = i / max(n - 1, 1)
            top, _ = ca.frame(p, (W, H // 2))
            bot, _ = cb.frame(p, (W, H // 2))
            frame = Image.new("RGBA", (W, H))
            frame.paste(top, (0, 0))
            frame.paste(bot, (0, H // 2))
            d = ImageDraw.Draw(frame)
            d.line([(0, H // 2), (W, H // 2)], fill=pal.paper + (255,), width=10)
            for k, (lab, y) in enumerate(((scene.labels[0], H // 2 - 120), (scene.labels[1], H // 2 + 50))):
                if lab:
                    _label_box(d, lab, (W / 2, y + 40), pal, ease(p * 4 - k * 0.5))
            yield frame.convert("RGB")
        return
    cam = _Cam(Image.open(scene.image).convert("RGB"), scene.motion)
    for i in range(n):
        p = i / max(n - 1, 1)
        img, to_out = cam.frame(p)
        img = img.convert("RGBA")
        for co in scene.callouts:
            _draw_callout(img, co, to_out, i / FPS, pal)
        yield img.convert("RGB")


def render_scene(scene: Scene, out: Path, pal: Palette) -> Path:
    proc = subprocess.Popen(
        ["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24",
         "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-", "-c:v", "libx264", "-preset", "veryfast",
         "-crf", "18", "-pix_fmt", "yuv420p", str(out)],
        stdin=subprocess.PIPE, stderr=subprocess.PIPE)
    assert proc.stdin
    try:
        for fr in scene_frames(scene, pal):
            proc.stdin.write(fr.tobytes())
    finally:
        proc.stdin.close()
    if proc.wait() != 0:
        raise RuntimeError(f"scene encode failed: {proc.stderr.read().decode()[-400:]}")  # type: ignore[union-attr]
    return out
