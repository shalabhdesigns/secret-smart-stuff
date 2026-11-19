"""Cover / thumbnail for each Short and Reel (owner, 3 Nov 2026: "a proper, well thought-out thumbnail that makes
viewers click").

Two steps:
1. plan()   - the writer model picks the strongest existing picture and 2-4 words of curiosity text. The words must
              be paid off by the video (YouTube removes "egregious clickbait": a title or thumbnail promising something
              the video doesn't deliver, enforced first in India and hardest on news). No new picture is paid for.
2. render() - 1080x1920 JPEG in the brand style: the picture fills the frame; the hook goes in the upper or lower
              part of the frame, whichever hides less of the picture, always inside what the 1:1 / 3:4 grid crops on
              Instagram and the Shorts shelf keep; first line white on ultramarine, second ultramarine on blush.
"""
from __future__ import annotations

import json
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter

from .compose import _font

W, H = 1080, 1920
ULTRA, BLUSH, WHITE = (0x1F, 0x3B, 0xFF), (0xFF, 0xD6, 0xE0), (255, 255, 255)

PLAN = """TASK: cover
You design the cover (thumbnail) of a YouTube Short / Instagram Reel for "Secret Smart Stuff", a channel about the
secret smart reasons behind everyday things. The cover must make a scroller curious enough to tap.

Video title: {title}
The video's beats (what is said, and which picture is on screen):
{beats}
Pictures available: {images}
{news}
Choose:
- "image": the ONE picture id that is most striking and clearly shows the object or the odd detail (usually the
  close, clear shot of the thing the question is about; never a cluttered or text-heavy one).
- "lines": 1 or 2 short lines, 2-5 words in total, ALL CAPS, that create curiosity: a surprising claim, a tension or
  an open loop ("IT'S NOT DECOR", "TOO FAST + TOO SLOW", "WHY THE CURL?"). Plain words a 12-year-old gets.
  It MUST be true and paid off by the video. No lies, no promise the video doesn't keep, no fear-mongering, no
  "SHOCKING"/"YOU WON'T BELIEVE". Different words from the title.
  The words appear ON SCREEN in the first 2 seconds, so they are a claim: they must restate something the narration
  says outright (no new fact, no stronger version of it). A question is safest when unsure.
- "why": one sentence.
Return JSON only: {{"image": "img1", "lines": ["LINE ONE", "LINE TWO"], "why": "..."}}
"""

NEWS_RULE = ("This video is a news tie-in about the Learjet crash in Florida: the cover must not mention deaths, "
             "show or describe a crash, or suggest what caused it. The science is the hook, e.g. 'MAYDAY = ?'.\n")


def plan(llm_ask, script: dict, news: bool = False, news_rule: str | None = None, feedback: dict | None = None) -> dict:
    """llm_ask(prompt) -> dict. Falls back to the hook picture and the script's thumb_text."""
    scenes = script.get("scenes") or []
    imgs = sorted({s.get("image") for s in scenes if s.get("image")})
    beats = "\n".join(f"{s.get('id')}: \"{s.get('narration', '')}\" [picture {s.get('image')}: "
                      f"{(script.get('images') or {}).get(s.get('image'), '')[:160]}]" for s in scenes)
    fallback = {"image": (scenes[0].get("image") if scenes else "img1") or "img1",
                "lines": [str(script.get("thumb_text") or script.get("hook_card") or "").upper()][:1], "why": "fallback"}
    try:
        out = llm_ask(PLAN.format(title=script.get("title", ""), beats=beats, images=", ".join(imgs),
                                  news=((news_rule or NEWS_RULE) + "\n") if news else ((news_rule + "\n") if news_rule else ""))
                     + (f"\nThe review REJECTED the words {feedback.get('rejected')}: {feedback.get('why')}\n"
                        "Choose different words that fix this." if feedback else "")) or {}
        lines = [str(x).strip().upper() for x in (out.get("lines") or []) if str(x).strip()][:2]
        if feedback and [x.upper() for x in feedback.get("rejected") or []] == lines:
            lines = []                                             # the same rejected words again: use the fallback
        if out.get("image") in imgs and lines and sum(len(x.split()) for x in lines) <= 6:
            return {"image": out["image"], "lines": lines, "why": out.get("why", "")}
    except Exception:  # noqa: BLE001
        pass
    return fallback


def _fill(img: Image.Image) -> Image.Image:
    img = img.convert("RGB")
    s = max(W / img.width, H / img.height)
    img = img.resize((round(img.width * s), round(img.height * s)), Image.LANCZOS)
    x, y = (img.width - W) // 2, (img.height - H) // 2
    return img.crop((x, y, x + W, y + H))


def _fit(text: str, max_w: int, start: int = 168) -> tuple:
    size = start
    while size > 70:
        f = _font(size, "Black")
        if f.getbbox(text)[2] <= max_w:
            return f, size
        size -= 6
    return _font(70, "Black"), 70


def _busy(img: Image.Image, y0: int, y1: int) -> float:
    """How much detail a horizontal band holds (edge energy): the words go where they hide the least."""
    band = img.crop((0, y0, W, y1)).convert("L").resize((W // 8, (y1 - y0) // 8)).filter(ImageFilter.FIND_EDGES)
    px = list(band.getdata())
    return sum(px) / max(1, len(px))


# Text zones inside the part every crop keeps (Instagram grid 1:1 keeps y 420-1500, 3:4 keeps 240-1680).
ZONES = {"upper": (430, 820), "lower": (1110, 1500)}


# With a topic badge the group is taller (badge + 2 lines): it uses the 3:4 crop's upper or lower part.
ZONES_BADGE = {"upper": (300, 960), "lower": (980, 1640)}
ZONES_LOGO = {"upper": (250, 1120), "lower": (810, 1680)}
PINK = (0xFF, 0x2E, 0x88)


def _badge(base: Image.Image, text: str, cx: int, cy: int) -> int:
    """The topic badge (owner, 20 Nov 2026: GTA branding on the thumbnail gets instant views): our own big pink slab
    with the game's name, tilted a little, with a soft shadow. Never a copy of Rockstar's logo. -> its height."""
    f, _ = _fit(text, 760, start=250)
    x0, y0, x1, y1 = ImageDraw.Draw(base).textbbox((0, 0), text, font=f)
    tw, th = x1 - x0, y1 - y0
    pw, ph = tw + 2 * 56, th + 2 * 38
    slab = Image.new("RGBA", (pw + 80, ph + 80), (0, 0, 0, 0))
    sd = ImageDraw.Draw(slab)
    sd.rounded_rectangle((40, 40, 40 + pw, 40 + ph), radius=26, fill=PINK + (255,))
    sd.text((40 + 56 - x0 + 6, 40 + 38 - y0 + 8), text, font=f, fill=(90, 0, 40, 255))   # inner drop shadow
    sd.text((40 + 56 - x0, 40 + 38 - y0), text, font=f, fill=WHITE + (255,))
    slab = slab.rotate(4, resample=Image.BICUBIC, expand=True)
    shadow = Image.new("RGBA", slab.size, (0, 0, 0, 0))
    shadow.putalpha(slab.getchannel("A").point(lambda v: int(v * 0.55)))
    shadow = shadow.filter(ImageFilter.GaussianBlur(16))
    px, py = cx - slab.width // 2, cy - slab.height // 2
    base.paste(shadow, (px + 10, py + 18), shadow)
    base.paste(slab, (px, py), slab)
    return ph


def render(picture: Path, lines: list[str], out: Path, zone: str | None = None, badge: str | None = None) -> Path:
    base = _fill(Image.open(picture))
    from . import logo as _logo
    real = _logo.has_logo(badge)
    zones = ZONES_LOGO if real else ZONES_BADGE if badge else ZONES
    zone = zone or min(zones, key=lambda z: _busy(base, *zones[z]))
    z0, z1 = zones[zone]
    if real:     # owner, 20 Nov 2026: the real GTA VI logo, only
        lg = _logo.logo(badge, 600)
        rgba = base.convert("RGBA")
        rgba.alpha_composite(lg, (W // 2 - lg.width // 2, z0 - lg.width // 16))
        base = rgba.convert("RGB")
        z0 += lg.height - lg.width // 8 + 10
    elif badge:
        bh = 200
        _badge(base, badge.upper(), W // 2, z0 + bh // 2 + 20)
        z0 += bh + 70
    d = ImageDraw.Draw(base)
    lines = [x for x in lines if x][:2] or ["?"]
    pad_x, pad_y, gap, radius = 44, 28, 20, 18
    blocks = []
    for i, t in enumerate(lines):
        f, size = _fit(t, W - 2 * 70 - 2 * pad_x, start=128 if real else 150 if badge else 176)
        x0, y0, x1, y1 = d.textbbox((0, 0), t, font=f)
        blocks.append((t, f, x1 - x0, y1 - y0, x0, y0, i))
    total = sum(b[3] + 2 * pad_y for b in blocks) + gap * (len(blocks) - 1)
    y = z0 if real else int((z0 + z1) / 2 - total / 2)
    shadow = Image.new("L", (W, H), 0)
    sd = ImageDraw.Draw(shadow)
    yy = y
    rects = []
    for t, f, tw, th, ox, oy, i in blocks:
        bw, bh = tw + 2 * pad_x, th + 2 * pad_y
        x = (W - bw) // 2
        rects.append((x, yy, bw, bh))
        sd.rounded_rectangle((x + 8, yy + 14, x + bw + 8, yy + bh + 14), radius=radius, fill=110)
        yy += bh + gap
    base = Image.composite(Image.new("RGB", (W, H), (0, 0, 0)), base, shadow.filter(ImageFilter.GaussianBlur(14)))
    d = ImageDraw.Draw(base)
    for (t, f, tw, th, ox, oy, i), (x, yb, bw, bh) in zip(blocks, rects):
        bg, fg = (ULTRA, WHITE) if i == 0 else (BLUSH, ULTRA)
        d.rounded_rectangle((x, yb, x + bw, yb + bh), radius=radius, fill=bg)
        d.text((x + pad_x - ox, yb + pad_y - oy), t, font=f, fill=fg)
    base.save(out, "JPEG", quality=90, optimize=True)
    return out


def make(llm_ask, d: Path, news: bool = False, news_rule: str | None = None, badge: str | None = None) -> dict:
    """Plan + render d/cover.jpg from the job's folder (script.json + its pictures). -> the plan, with "file"."""
    script = json.loads((d / "script.json").read_text())
    early = d / "cover_plan.json"            # made at render time for videos that open with the hook (same words)
    p = json.loads(early.read_text()) if early.exists() else plan(llm_ask, script, news, news_rule)
    pic = d / f"{p['image']}.png"
    fr = p.get("frame")
    if fr and (d / f"{fr.get('image', p['image'])}_clip.mp4").exists():
        # 19 Nov 2026: a shot's middle frame can be dark or empty; Claude picks the exact frame (a face) instead:
        # {"image": "img1", "t": seconds into that clip, "x": 0-1 where the 9:16 window is centred}
        import subprocess
        full = d / "cover_frame_full.png"
        subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-ss", f"{float(fr.get('t', 0)):.2f}", "-i",
                        str(d / f"{fr.get('image', p['image'])}_clip.mp4"), "-frames:v", "1", str(full)], check=True)
        im = Image.open(full).convert("RGB")
        cw = min(im.width, round(im.height * 9 / 16))
        x0 = max(0, min(im.width - cw, round(im.width * float(fr.get("x", 0.5)) - cw / 2)))
        pic = d / "cover_frame.png"
        im.crop((x0, 0, x0 + cw, im.height)).save(pic)
    if not pic.exists():
        cands = sorted(d.glob("img*.png"))
        if not cands:
            raise FileNotFoundError("no pictures for the cover")
        pic = cands[0]
    render(pic, p["lines"], d / "cover.jpg", badge=badge)
    p["file"] = str(d / "cover.jpg")
    (d / "cover.json").write_text(json.dumps(p, ensure_ascii=False, indent=1))
    return p
