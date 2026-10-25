"""Beat renderer (v2): one continuous frame stream for the whole Short.

A Short is a list of Beats (1.5–3.5 s each). Rendering everything in one pass
lets effects cross shot boundaries: whip transitions, kinetic word "pops" timed
to the spoken word, draw-on diagram arrows, split reveals, and a last frame
that lands exactly on the first frame so the replay loops seamlessly.

All motion is deterministic code; the only generated assets are the images.
"""
from __future__ import annotations

import math
import subprocess
from dataclasses import dataclass, field
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter, ImageFont

from .compose import (CAPTION_BAND, FONTS, FPS, H, SAFE_BOTTOM, SAFE_RIGHT, SAFE_TOP, W, Palette,
                      _blueprint_card, _font, _label_box, ease)


@dataclass
class Pop:
    text: str
    at: float                 # absolute seconds (usually the spoken word's start)
    hold: float = 0.9
    accent: bool = True


@dataclass
class Arrow:
    a: tuple[float, float]    # image fractions
    b: tuple[float, float]
    at: float                 # absolute seconds when it starts drawing


@dataclass
class Marker:
    label: str                # e.g. "1", "2"
    pos: tuple[float, float]  # image fractions
    at: float                 # absolute seconds when it pops in


@dataclass
class Beat:
    start: float
    end: float
    image: Path | None = None
    image2: Path | None = None          # split reveal / comparison
    focus: tuple[float, float, float, float] | None = None   # x, y, w, h fractions to frame
    motion: str = "push"                # push | pull | punch | drift_l | drift_r | hold | settle_to_start
    transition: str = "cut"             # cut | whip | zoom_cut | reveal
    callout_label: str | None = None    # circles `focus` with this label
    callout_at: float | None = None
    pops: list[Pop] = field(default_factory=list)
    arrow: Arrow | None = None
    card_text: str = ""                 # blueprint card instead of an image
    hook_text: str = ""                 # big headline shown over this beat (opening only)
    split_at: float | None = None       # diagonal reveal of image2 starting at this time
    labels: tuple[str, str] = ("", "")  # split labels
    markers: list[Marker] = field(default_factory=list)   # numbered badges drawn on the image


# ---------------- camera ----------------

def _cam_params(beat: Beat, p: float, first_zoom: float | None = None) -> tuple[float, float, float]:
    """zoom, cx, cy for progress p in [0,1]."""
    fx, fy = (0.5, 0.5)
    if beat.focus:
        fx, fy = beat.focus[0], beat.focus[1]
    e = ease(p)
    m = beat.motion
    if m == "shake":                      # comic beat: quick jolt, then still
        j = max(0.0, 1 - p * 4)
        return 1.12, fx + 0.012 * math.sin(p * 90) * j, fy + 0.008 * math.cos(p * 70) * j
    if m == "push":
        return 1.0 + 0.14 * e, 0.5 + (fx - 0.5) * 0.5 * e, 0.5 + (fy - 0.5) * 0.5 * e
    if m == "pull":
        return 1.16 - 0.16 * e, fx + (0.5 - fx) * e, fy + (0.5 - fy) * e
    if m == "punch":                      # snap in on the focus, then settle
        z = 1.30 - 0.18 * ease(min(1.0, p * 3.2))
        return z, fx, fy
    if m == "drift_l":
        return 1.12, 0.56 - 0.12 * e, fy
    if m == "drift_r":
        return 1.12, 0.44 + 0.12 * e, fy
    if m == "settle_to_start":            # for the loop: end exactly where beat 1 begins
        z0 = 1.14
        return z0 + ((first_zoom or 1.0) - z0) * e, 0.5, 0.5
    return 1.06, fx, fy                   # hold


def _render_cam(img: Image.Image, zoom: float, cx: float, cy: float, size=(W, H)):
    iw, ih = img.size
    s = max(size[0] / iw, size[1] / ih) * zoom
    half_w, half_h = size[0] / 2 / s, size[1] / 2 / s
    cxp = min(max(cx * iw, half_w), iw - half_w)
    cyp = min(max(cy * ih, half_h), ih - half_h)
    c, f = cxp - half_w, cyp - half_h
    out = img.transform(size, Image.AFFINE, (1 / s, 0, c, 0, 1 / s, f), resample=Image.BILINEAR)

    def to_out(fx: float, fy: float) -> tuple[float, float]:
        return ((fx * iw - c) * s, (fy * ih - f) * s)
    return out, to_out


# ---------------- overlays ----------------

def _pop(frame: Image.Image, pop: Pop, t: float, pal: Palette) -> None:
    dt = t - pop.at
    if dt < 0 or dt > pop.hold + 0.25:
        return
    sc = 0.55 + 0.55 * ease(dt / 0.18) if dt < 0.18 else (1.1 - 0.1 * ease((dt - 0.18) / 0.12) if dt < 0.3 else 1.0)
    alpha = 1.0 if dt < pop.hold else 1.0 - (dt - pop.hold) / 0.25
    size = int(150 * sc)
    f = _font(max(10, size), "Black")
    text = pop.text.upper()
    d = ImageDraw.Draw(frame, "RGBA")
    tw = d.textlength(text, font=f)
    if tw > W - 120:
        f = _font(max(10, int(size * (W - 120) / tw)), "Black")
        tw = d.textlength(text, font=f)
    x, y = (W - tw) / 2, 560 - size / 2
    a = int(255 * max(0.0, min(1.0, alpha)))
    col = (pal.accent if pop.accent else pal.paper) + (a,)
    outline = pal.ink + (a,)
    for ox, oy in ((-6, 0), (6, 0), (0, -6), (0, 6), (-4, -4), (4, 4), (-4, 4), (4, -4)):
        d.text((x + ox, y + oy), text, font=f, fill=outline)
    d.text((x, y), text, font=f, fill=col)


def _marker(frame: Image.Image, mk: Marker, to_out, t: float, pal: Palette) -> None:
    """Numbered badge that pops onto a specific spot (e.g. pull-tab 1, 2, 3)."""
    dt = t - mk.at
    if dt < 0:
        return
    sc = min(1.0, 0.4 + 0.6 * ease(dt / 0.16)) if dt < 0.16 else (1.12 - 0.12 * ease((dt - 0.16) / 0.12) if dt < 0.28 else 1.0)
    x, y = to_out(*mk.pos)
    x = min(max(x, 90), W - 90)
    y = min(max(y, SAFE_TOP + 60), SAFE_BOTTOM - 60)
    r = 58 * sc
    d = ImageDraw.Draw(frame, "RGBA")
    d.ellipse([x - r - 6, y - r - 6, x + r + 6, y + r + 6], fill=pal.paper + (255,))
    d.ellipse([x - r, y - r, x + r, y + r], fill=pal.accent + (255,))
    f = _font(max(10, int(72 * sc)), "Black")
    tw = d.textlength(mk.label, font=f)
    d.text((x - tw / 2, y - 44 * sc), mk.label, font=f, fill=pal.paper + (255,))


def _hook(frame: Image.Image, text: str, t: float, pal: Palette) -> None:
    """Opening headline: two lines, slams in, holds, slides up and out."""
    if t > 1.7:
        return
    p_in = ease(t / 0.22)
    p_out = ease((t - 1.3) / 0.4) if t > 1.3 else 0.0
    lines = [ln.strip() for ln in text.split("\n") if ln.strip()][:2]
    f = _font(112, "Black")
    d = ImageDraw.Draw(frame, "RGBA")
    y0 = 430 - (len(lines) - 1) * 70 - int(p_out * 400)
    a = int(255 * (1 - p_out))
    for i, ln in enumerate(lines):
        ln = ln.upper()
        tw = d.textlength(ln, font=f)
        if tw > W - 100:
            f2 = _font(int(112 * (W - 100) / tw), "Black")
            tw = d.textlength(ln, font=f2)
        else:
            f2 = f
        x = (W - tw) / 2 + (1 - p_in) * (-W if i % 2 == 0 else W)
        y = y0 + i * 140
        pad = 18
        d.rounded_rectangle([x - pad, y - 6, x + tw + pad, y + 124], radius=18,
                            fill=(pal.ink if i == 0 else pal.accent) + (int(a * 0.92),))
        d.text((x, y), ln, font=f2, fill=pal.paper + (a,))


def _arrow(frame: Image.Image, ar: Arrow, to_out, t: float, pal: Palette) -> None:
    p = ease((t - ar.at) / 0.45)
    if p <= 0:
        return
    ax, ay = to_out(*ar.a)
    bx, by = to_out(*ar.b)
    ex, ey = ax + (bx - ax) * p, ay + (by - ay) * p
    d = ImageDraw.Draw(frame, "RGBA")
    d.line([(ax, ay), (ex, ey)], fill=pal.accent + (255,), width=12)
    if p > 0.6:
        ang = math.atan2(by - ay, bx - ax)
        for s in (-1, 1):
            d.line([(ex, ey), (ex - 40 * math.cos(ang + s * 0.5), ey - 40 * math.sin(ang + s * 0.5))],
                   fill=pal.accent + (255,), width=12)


def _callout(frame: Image.Image, beat: Beat, to_out, t: float, pal: Palette) -> None:
    at = beat.callout_at if beat.callout_at is not None else beat.start + 0.25
    p = ease((t - at) / 0.5)
    if p <= 0 or not beat.focus:
        return
    fx, fy, fw, fh = beat.focus
    cx, cy = to_out(fx, fy)
    rx_e, _ = to_out(fx + fw / 2, fy)
    _, ry_e = to_out(fx, fy + fh / 2)
    rx = min(max(70, abs(rx_e - cx) * 1.1), W * 0.42)
    ry = min(max(70, abs(ry_e - cy) * 1.1), H * 0.22)
    cx = min(max(cx, rx + 20), W - rx - 20)      # keep the ring on screen
    cy = min(max(cy, SAFE_TOP + ry), SAFE_BOTTOM - ry)
    d = ImageDraw.Draw(frame, "RGBA")
    d.arc([cx - rx, cy - ry, cx + rx, cy + ry], start=-90, end=-90 + 360 * p, fill=pal.accent + (255,), width=10)
    if beat.callout_label and p > 0.5:
        ly = _label_y(beat, to_out, cx, cy, ry, t)
        if ly is None:          # nowhere clean to put it: the ring alone says enough
            return
        d.line([(cx, cy - ry if ly < cy else cy + ry), (cx, ly)], fill=pal.ink + (255,), width=6)
        _label_box(d, beat.callout_label, (cx, ly), pal, ease((p - 0.5) / 0.5))


CAPTION_Y = 1200    # set by render(); captions sit in a ~170 px band around this


def _label_y(beat: Beat, to_out, cx: float, cy: float, ry: float, t: float) -> float | None:
    """Pick a label row that clears the captions, keyword pops and numbered markers."""
    blocked = [(CAPTION_Y - 130, CAPTION_Y + 130)]
    if any(pp.at - 0.1 <= t <= pp.at + pp.hold + 0.3 for pp in beat.pops):
        blocked.append((440, 690))                       # pop text band
    if beat.hook_text and t - beat.start < 1.8:
        blocked.append((280, 620))
    mk_xy = [to_out(*mk.pos) for mk in beat.markers]
    for ly in (cy - ry - 120, cy + ry + 120):
        if not (SAFE_TOP + 40 <= ly <= SAFE_BOTTOM - 60):
            continue
        if any(lo - 50 < ly < hi + 50 for lo, hi in blocked):
            continue
        if any(abs(my - ly) < 130 and abs(mx - cx) < 330 for mx, my in mk_xy):
            continue
        return ly
    return None


def _split(base: Image.Image, other: Image.Image, p: float, labels: tuple[str, str], pal: Palette) -> Image.Image:
    """Diagonal wipe revealing `other` over `base` (0 -> 1)."""
    if p <= 0:
        return base
    mask = Image.new("L", (W, H), 0)
    d = ImageDraw.Draw(mask)
    x = -W * 0.6 + (W * 2.2) * ease(p)
    d.polygon([(x, 0), (x + W * 0.35, 0), (x - W * 0.25, H), (x - W * 0.6, H)], fill=255)
    d.polygon([(x - W * 0.6, 0), (x, 0), (x - W * 0.6, H), (x - W * 1.2, H)], fill=255)
    out = Image.composite(other, base, mask)
    dd = ImageDraw.Draw(out, "RGBA")
    dd.line([(x, 0), (x - W * 0.6, H)], fill=pal.paper + (255,), width=10)
    if labels[0] and p < 0.9:
        _label_box(dd, labels[0], (W * 0.25, 300), pal, 1.0)
    if labels[1] and p > 0.3:
        _label_box(dd, labels[1], (W * 0.75, 300), pal, 1.0)
    return out


# ---------------- main render ----------------

def render(beats: list[Beat], total: float, out: Path, pal: Palette, caption_y: int = 1200) -> Path:
    global CAPTION_Y
    CAPTION_Y = caption_y
    beats = sorted(beats, key=lambda b: b.start)
    cache: dict[Path, Image.Image] = {}

    def load(p: Path) -> Image.Image:
        if p not in cache:
            im = Image.open(p).convert("RGB")
            if im.width < W * 1.3:
                im = im.resize((int(im.width * W * 1.3 / im.width), int(im.height * W * 1.3 / im.width)), Image.LANCZOS)
            cache[p] = im
        return cache[p]

    first_zoom = 1.0
    n = round(total * FPS)
    proc = subprocess.Popen(
        ["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}",
         "-r", str(FPS), "-i", "-", "-c:v", "libx264", "-preset", "veryfast", "-crf", "18",
         "-pix_fmt", "yuv420p", str(out)], stdin=subprocess.PIPE, stderr=subprocess.PIPE)
    assert proc.stdin

    def beat_frame(b: Beat, t: float):
        p = 0.0 if b.end <= b.start else min(1.0, max(0.0, (t - b.start) / (b.end - b.start)))
        if b.card_text and not b.image:
            fr = _blueprint_card(b.card_text, p, pal).convert("RGB")
            return fr, (lambda fx, fy: (fx * W, fy * H))
        z, cx, cy = _cam_params(b, p, first_zoom)
        fr, to_out = _render_cam(load(b.image), z, cx, cy)  # type: ignore[arg-type]
        if b.image2 and b.split_at is not None and t >= b.split_at:
            other, _ = _render_cam(load(b.image2), z, cx, cy)
            fr = _split(fr, other, (t - b.split_at) / 0.55, b.labels, pal)
        return fr, to_out

    try:
        idx = 0
        for i in range(n):
            t = i / FPS
            while idx + 1 < len(beats) and t >= beats[idx + 1].start:
                idx += 1
            b = beats[idx]
            frame, to_out = beat_frame(b, t)
            # transition into this beat
            dt = t - b.start
            if idx > 0 and b.transition == "whip" and dt < 0.2:
                q = ease(dt / 0.2)
                prev, _ = beat_frame(beats[idx - 1], b.start - 1 / FPS)
                canvas = Image.new("RGB", (W, H))
                canvas.paste(prev.filter(ImageFilter.GaussianBlur(14 * (1 - q))), (int(-W * q), 0))
                canvas.paste(frame.filter(ImageFilter.GaussianBlur(14 * (1 - q))), (int(W * (1 - q)), 0))
                frame = canvas
            elif idx > 0 and b.transition == "zoom_cut" and dt < 0.3:
                q = 1 + 0.22 * (1 - ease(dt / 0.3))
                frame = frame.resize((int(W * q), int(H * q)), Image.BILINEAR).crop(
                    ((int(W * q) - W) // 2, (int(H * q) - H) // 2, (int(W * q) - W) // 2 + W, (int(H * q) - H) // 2 + H))
            frame = frame.convert("RGBA")
            if b.focus and b.callout_label is not None:
                _callout(frame, b, to_out, t, pal)
            if b.arrow:
                _arrow(frame, b.arrow, to_out, t, pal)
            for mk in b.markers:
                _marker(frame, mk, to_out, t, pal)
            for pop in b.pops:
                _pop(frame, pop, t, pal)
            if b.hook_text:
                _hook(frame, b.hook_text, t - b.start, pal)
            proc.stdin.write(frame.convert("RGB").tobytes())
    finally:
        proc.stdin.close()
    if proc.wait() != 0:
        raise RuntimeError(f"beat render failed: {proc.stderr.read().decode()[-400:]}")  # type: ignore[union-attr]
    return out
