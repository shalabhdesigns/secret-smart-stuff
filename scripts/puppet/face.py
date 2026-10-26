"""Cartoon faces drawn by code on the locked character art (v2, rebuilt from research — docs/craft/EXPRESSIONS.md).

Principles (Ekman/FACS, Preston Blair, Williams, AnimSchool, School of Motion):
- One clear idea per face. Brows, lids and mouth must agree; no mixed signals.
- Eyes stay symmetric. Only brows (skeptical/confused/thinking) and mouth corners (smirk, annoyed) may be
  asymmetric, and an eye may only differ when its own brow differs (lid follows its brow, max 0.3).
- Genuine smile = mouth corners up AND lower lids pushed up. Forced smile = smiling mouth, worried brows,
  no lower-lid push.
- Phone-sized readability: changes are big (>= 0.3 brow units) or not done at all. No eye twitches,
  no ear redness, no worry lines, at most one symbol (sweat / blush / red face / gloom / vein) per face.

Units: brow heights in "brow units" (about 0.8 x eye radius); eye `open` 0 shut .. 1 neutral .. 1.4 wide;
`lower` 0..1 lower-lid push; mouth corners -1..1.
"""
from __future__ import annotations

import math

import cv2
import numpy as np

OUTLINE = (40, 22, 18)

BASE = dict(
    bi_l=0.0, bo_l=0.0, bi_r=0.0, bo_r=0.0, bc=0.2,          # brows: inner/outer height per side, curve
    open_l=1.0, open_r=1.0, lower=0.1, pupil=1.0, slant=0.0,  # eyes (slant + = angry toward nose, - = sad outer droop)
    eye_style=0, hl=0.0,                                     # 0 normal, 1 closed happy arcs, 2 squeezed shut
    c_l=0.05, c_r=0.05, mstyle=0, mopen=0.0, mw=1.0, mshift=0.0,
    blush=0.0, red=0.0, sweat=0.0, gloom=0.0, vein=0.0, tears=0.0, scrunch=0.0,
    tilt=0.0, bounce=0.0, tremble=0.0, darts=0.0, blinks=1.0,
)
# mstyle: 0 line (talks with normal visemes), 1 closed wide smile, 2 open "D" smile, 3 "O", 4 scream/shout,
#         5 gritted teeth (corners decide: scared/angry/pained vs gritted smile), 6 wavy nervous line,
#         7 open frown, 8 toothy forced grin
DISCRETE = ("eye_style", "mstyle")


def _sym(bi, bo, bc=0.2):
    return dict(bi_l=bi, bo_l=bo, bi_r=bi, bo_r=bo, bc=bc)


def _eyes(o):
    return dict(open_l=o, open_r=o)


def _corners(c):
    return dict(c_l=c, c_r=c)


EMOTIONS: dict[str, dict] = {
    "neutral": {},
    "listening": dict(**_corners(0.12), tilt=3),
    "happy": dict(**_sym(0.2, 0.1, 0.4), **_eyes(0.85), lower=0.45, mstyle=1, **_corners(0.7), mw=1.05),
    "laugh": dict(**_sym(0.3, 0.1, 0.5), eye_style=1, mstyle=2, mopen=0.8, **_corners(1.0), mw=1.15, bounce=1.0, tilt=-5),
    "proud": dict(**_sym(0.2, 0.2, 0.3), **_eyes(0.62), lower=0.3, mstyle=0, c_l=0.6, c_r=0.12, tilt=-4),
    "smug": dict(**_sym(0.15, 0.25, 0.3), **_eyes(0.55), lower=0.3, mstyle=0, c_l=0.65, c_r=0.05, mshift=-0.15, tilt=5),
    "sly": dict(**_sym(-0.35, 0.3, 0.0), **_eyes(0.55), lower=0.4, pupil=0.85, mstyle=1, c_l=0.75, c_r=0.4, mw=1.2, tilt=6),
    "excited": dict(**_sym(0.6, 0.5, 0.6), **_eyes(1.25), pupil=1.15, hl=1.0, mstyle=2, mopen=0.55, **_corners(0.9),
                    mw=1.1, bounce=0.45),
    "nervous": dict(**_sym(0.5, 0.0, 0.1), **_eyes(1.05), pupil=0.85, darts=1.0, mstyle=6, **_corners(-0.1), sweat=1.0),
    "forced_smile": dict(**_sym(0.5, 0.0, 0.1), **_eyes(1.0), lower=0.0, pupil=0.9, mstyle=1, **_corners(0.65), mw=1.25,
                         sweat=1.0),
    "grin": dict(**_sym(0.5, 0.0, 0.1), **_eyes(1.05), lower=0.0, pupil=0.8, mstyle=8, **_corners(0.6), mw=1.3, sweat=1.0),
    "worried": dict(**_sym(0.6, -0.1, 0.0), **_eyes(1.0), mstyle=7, mopen=0.15, **_corners(-0.45), tilt=-3),
    "scared": dict(**_sym(0.8, 0.4, 0.1), **_eyes(1.3), lower=0.2, pupil=0.7, mstyle=5, **_corners(-0.3), mw=1.2,
                   sweat=1.0, darts=0.6),
    "panic": dict(**_sym(1.0, 0.5, 0.0), **_eyes(1.4), lower=0.0, pupil=0.6, mstyle=4, mopen=0.7, **_corners(-0.5),
                  sweat=3.0, darts=1.0, tremble=0.5, blinks=0.0),
    "shock": dict(**_sym(1.0, 0.9, 0.8), **_eyes(1.4), lower=0.0, pupil=0.62, mstyle=3, mopen=0.8, **_corners(-0.1),
                  blinks=0.0),
    "angry": dict(**_sym(-0.8, 0.3, 0.0), **_eyes(0.78), slant=0.6, lower=0.4, pupil=0.8, mstyle=5, **_corners(-0.7),
                  red=0.6, blinks=0.0),
    "furious": dict(**_sym(-0.9, 0.4, 0.0), **_eyes(0.9), slant=0.7, lower=0.3, pupil=0.65, mstyle=4, mopen=0.6,
                    **_corners(-0.8), red=1.0, tremble=0.3, blinks=0.0),
    "shout": dict(**_sym(-0.4, 0.3, 0.0), **_eyes(1.1), slant=0.3, pupil=0.8, mstyle=4, mopen=0.6, **_corners(-0.3), red=0.35),
    "annoyed": dict(**_sym(-0.4, 0.0, 0.0), **_eyes(0.7), lower=0.1, mstyle=0, c_l=-0.3, c_r=-0.3, mshift=0.3, mw=0.85),
    "deadpan": dict(**_sym(-0.05, -0.05, 0.0), **_eyes(0.52), lower=0.15, mstyle=0, **_corners(0.0), mw=0.8, mshift=0.12),
    "unimpressed": dict(**_sym(-0.1, -0.1, 0.0), **_eyes(0.5), lower=0.15, mstyle=0, c_l=-0.15, c_r=-0.15, mw=0.8,
                        mshift=0.15),
    "skeptical": dict(bi_l=0.75, bo_l=0.7, bi_r=-0.3, bo_r=-0.3, bc=0.6, open_l=1.08, open_r=0.8, mstyle=0, c_l=-0.2,
                      c_r=-0.2, mshift=0.3, mw=0.85, tilt=6),
    "disgust": dict(**_sym(-0.4, -0.2, 0.0), **_eyes(0.65), lower=0.6, mstyle=5, **_corners(-0.6), mw=0.95, scrunch=1.0,
                    tilt=-7),
    "sad": dict(**_sym(0.6, -0.3, 0.1), **_eyes(0.75), slant=-0.5, pupil=1.1, mstyle=0, **_corners(-0.6), tilt=-4),
    "defeated": dict(**_sym(0.3, -0.4, 0.0), **_eyes(0.5), slant=-0.3, mstyle=0, **_corners(-0.25), mw=0.9, tilt=-7),
    "embarrassed": dict(**_sym(0.4, 0.0, 0.1), **_eyes(0.85), lower=0.3, mstyle=6, **_corners(0.2), blush=1.0, tilt=-6),
    "sheepish": dict(**_sym(0.4, 0.0, 0.1), **_eyes(0.8), lower=0.4, mstyle=1, c_l=0.55, c_r=0.3, sweat=1.0, tilt=8),
    "confused": dict(bi_l=0.5, bo_l=0.55, bi_r=-0.2, bo_r=0.1, bc=0.6, open_l=1.0, open_r=0.9, pupil=0.9, mstyle=3,
                     mopen=0.15, mw=0.6, mshift=0.3, tilt=12),
    "thinking": dict(bi_l=0.35, bo_l=0.35, bi_r=-0.1, bo_r=-0.1, bc=0.4, open_l=0.9, open_r=0.85, mstyle=0, **_corners(-0.05),
                     mw=0.7, mshift=0.3, tilt=4),
    "love": dict(**_sym(0.4, 0.1, 0.5), **_eyes(0.8), lower=0.4, pupil=1.25, hl=1.0, mstyle=1, **_corners(0.5), mw=0.85,
                 blush=1.0, tilt=-10),
    "pained": dict(**_sym(0.5, -0.2, 0.0), eye_style=2, mstyle=5, **_corners(-0.5), mw=1.15, scrunch=0.6),
}
ALIASES = {"proud ": "proud"}
# changes that get a full "take" (anticipation -> accent -> overshoot -> settle)
BIG = {"shock", "scared", "panic", "excited", "laugh", "angry", "furious", "shout", "happy", "love"}
# the gaze these emotions want unless the scene sets one
GAZE = {"thinking": (0.55, -0.7), "defeated": (0.0, 0.75), "sad": (0.0, 0.6), "embarrassed": (-0.75, 0.35),
        "sheepish": (0.5, 0.45), "worried": (-0.3, 0.45), "sly": (0.75, 0.0)}


def emotion(name: str) -> dict:
    e = dict(BASE)
    e.update(EMOTIONS.get(ALIASES.get(name, name), {}))
    return e


def blend(a: dict, b: dict, k: float) -> dict:
    """k may go below 0 (anticipation) or above 1 (overshoot)."""
    out = {}
    for key in BASE:
        if key in DISCRETE:
            out[key] = b[key] if k >= 0.5 else a[key]
        else:
            out[key] = a[key] + (b[key] - a[key]) * k
    return out


def _blend_color(img: np.ndarray, mask: np.ndarray, color, alpha: float) -> None:
    if alpha <= 0.001:
        return
    a = (mask.astype(np.float32) * alpha * (img[..., 3:4] / 255.0)[..., 0])[..., None]
    img[..., :3] = (img[..., :3].astype(np.float32) * (1 - a) + np.array(color, np.float32) * a).astype(np.uint8)


def _bezier(p0, p1, p2, n=16):
    return np.array([(1 - t) ** 2 * np.array(p0) + 2 * (1 - t) * t * np.array(p1) + t * t * np.array(p2)
                     for t in np.linspace(0, 1, n)], np.int32)


class Face:
    """spec keys: eyes [[x,y],[x,y]], eye_r, mouth [x,y], mouth_w, glasses, brow_gap, brow_color, stache."""

    def __init__(self, spec: dict, scale: float, skin):
        self.s = scale
        self.eyes = [np.array(e, np.float32) * scale for e in spec["eyes"]]
        self.r = spec["eye_r"] * scale
        self.brow_y = spec.get("brow_gap", 1.9) * self.r
        self.mouth = np.array(spec["mouth"], np.float32) * scale
        self.mw = spec["mouth_w"] * scale * 1.2      # mouths read bigger on a phone
        self.glasses = spec.get("glasses", False)
        self.brow_col = tuple(spec.get("brow_color", (30, 24, 22)))
        self.skin = tuple(int(v) for v in skin)
        self.has_stache = bool(spec.get("stache"))

    def _shade(self, k):
        return tuple(int(c * k) for c in self.skin)

    # ------------------------------------------------------------------ draw
    def draw(self, img: np.ndarray, st: dict) -> None:
        e = st["emo"]
        eb = st.get("emo_brow", e)            # brows lead the rest of the face by a few frames
        sym = st.get("sym", 1.0)              # symbols appear on the accent and fade after ~1.5 s
        r = self.r
        t = st.get("t", 0.0)
        a, b = self.eyes
        eye_y = (a[1] + b[1]) / 2
        mid_x = (a[0] + b[0]) / 2
        m_y = float(self.mouth[1])
        H, W = img.shape[:2]
        thick = max(2, int(r * 0.17))
        B = r * 1.15                          # one brow unit

        # ---- face colour (under everything), painted on skin pixels only (never on hair, glasses or outline)
        skin_m = None
        if e["red"] > 0.02 or e["gloom"] > 0.02:
            d = np.abs(img[..., :3].astype(np.int16) - np.array(self.skin, np.int16)).sum(-1)
            skin_m = ((d < 70) & (img[..., 3] > 200)).astype(np.float32)
            skin_m = cv2.GaussianBlur(skin_m, (0, 0), max(1.0, r * 0.08))
            yy = np.arange(H, dtype=np.float32)[:, None]
            xx = np.arange(W, dtype=np.float32)[None, :]
            near = np.clip(1.4 - np.sqrt(((xx - mid_x) / (r * 3.6)) ** 2 + ((yy - (eye_y + m_y) / 2) / (r * 4.6)) ** 2), 0, 1)
            skin_m = skin_m * near
        if e["red"] > 0.02:                                    # anger flush rises from the chin
            rise = np.clip((yy - (eye_y - r * 3.0 + (1 - min(1.0, e["red"])) * r * 3.5)) / (r * 2.5), 0, 1)
            _blend_color(img, skin_m * rise, (205, 45, 40), 0.55 * min(1.0, e["red"]))
        if e["blush"] > 0.02:
            for side, c in ((-1, a), (1, b)):
                cx, cy = c[0] + side * r * 0.45, eye_y + (0.38 if self.has_stache else 0.6) * (m_y - eye_y)
                mask = np.zeros((H, W), np.float32)
                cv2.ellipse(mask, (int(cx), int(cy)), (int(r * 1.0), int(r * 0.55)), 0, 0, 360, 1.0, -1, cv2.LINE_AA)
                mask = cv2.GaussianBlur(mask, (0, 0), max(1.0, r * 0.22))
                _blend_color(img, mask, (238, 92, 105), 0.6 * min(1.0, e["blush"]))
                if e["blush"] > 0.6:
                    for k in range(3):
                        x0 = int(cx - r * 0.5 + k * r * 0.42)
                        cv2.line(img, (x0, int(cy + r * 0.2)), (x0 + int(r * 0.25), int(cy - r * 0.2)), (205, 70, 80, 255),
                                 max(1, int(r * 0.08)), cv2.LINE_AA)
        if e["gloom"] > 0.02:                                  # blue shade sliding down the upper face
            g = 1 - np.clip((yy - (eye_y - r * 4.0)) / (r * 5.0), 0, 1)
            _blend_color(img, skin_m * g, (80, 85, 150), 0.6 * e["gloom"])

        # ---- eyes
        look = st.get("look", (0, 0))
        tr = e["tremble"] + st.get("shiver", 0.0)
        jx = (1 if int(t * 15) % 2 else -1) * r * 0.05 * tr          # 1-px-style tremble every 2 frames
        blink = st.get("blink", 0.0)
        for i, c in enumerate(self.eyes):
            side = -1 if i == 0 else 1
            cx, cy = float(c[0]) + jx, float(c[1])
            op = max(0.0, e["open_l"] if i == 0 else e["open_r"])
            wide = max(1.0, op)
            ry, rx = r * 1.08 * (1 + 0.55 * (wide - 1)), r * 0.86 * (1 + 0.2 * (wide - 1))
            style = int(e["eye_style"])
            if style == 1 and blink < 0.5:                              # happy closed arcs ^ ^
                cv2.ellipse(img, (int(cx), int(cy + ry * 0.3)), (int(rx * 1.05), int(ry * 0.75)), 0, 200, 340,
                            (*OUTLINE, 255), thick + 2, cv2.LINE_AA)
            elif style == 2:                                            # squeezed shut > <
                p = np.array([[cx - side * rx, cy - ry * 0.55], [cx + side * rx * 0.55, cy], [cx - side * rx, cy + ry * 0.55]],
                             np.int32)
                cv2.polylines(img, [p], False, (*OUTLINE, 255), thick + 2, cv2.LINE_AA)
            else:
                mask = np.zeros((H, W), np.uint8)
                cv2.ellipse(mask, (int(cx), int(cy)), (int(rx), int(ry)), 0, 0, 360, 255, -1, cv2.LINE_AA)
                cv2.ellipse(img, (int(cx), int(cy)), (int(rx), int(ry)), 0, 0, 360, (255, 255, 255, 255), -1, cv2.LINE_AA)
                lx, ly = look
                roll = st.get("eyeroll")
                if roll is not None:                                     # both eyes sweep up and across
                    ang = math.pi * (1.0 + roll)
                    lx, ly = math.cos(ang) * 0.85, -0.8 + 0.2 * math.sin(roll * math.pi)
                px, py = cx + lx * rx * 0.42, cy + ly * ry * 0.38
                pr = r * 0.46 * e["pupil"]
                pm = np.zeros_like(mask)
                cv2.circle(pm, (int(px), int(py)), max(2, int(pr)), 255, -1, cv2.LINE_AA)
                img[(pm > 0) & (mask > 0)] = (25, 20, 20, 255)
                hl = max(1, int(pr * 0.32))
                cv2.circle(img, (int(px - pr * 0.35), int(py - pr * 0.35)), hl, (255, 255, 255, 255), -1, cv2.LINE_AA)
                if e["hl"] > 0.5:                                        # extra catch-light (excited / love)
                    cv2.circle(img, (int(px + pr * 0.38), int(py + pr * 0.3)), max(1, int(hl * 0.6)), (255, 255, 255, 255),
                               -1, cv2.LINE_AA)
                # upper lid: closes from the top; slant tilts it (angry: down toward the nose; sad: outer droop)
                lid = max(0.0, min(1.0, 1 - min(op, 1.0)))
                if st.get("eyeroll") is not None:                # "ugh": heavy lids while the eyes roll
                    lid = max(lid, 0.42 * math.sin(min(1.0, st["eyeroll"]) * math.pi) + 0.2)
                lid = max(lid, blink)
                if lid > 0.01:
                    base = cy - ry + lid * 2 * ry * (0.92 if lid < 0.99 else 1.0)
                    sl = e["slant"] * ry * 0.45 * (1 - blink)
                    inner_x, outer_x = cx - side * rx, cx + side * rx
                    y_in, y_out = base + sl, base - sl
                    poly = np.array([[inner_x, cy - ry * 1.6], [outer_x, cy - ry * 1.6], [outer_x, y_out], [inner_x, y_in]], np.int32)
                    lm = np.zeros_like(mask)
                    cv2.fillPoly(lm, [poly], 255)
                    img[(lm > 0) & (mask > 0)] = (*self.skin, 255)
                    if lid < 0.98:
                        cv2.line(img, (int(inner_x), int(y_in)), (int(outer_x), int(y_out)), (*OUTLINE, 255), thick, cv2.LINE_AA)
                lo = e["lower"] * (1 - blink)
                if lo > 0.02 and lid < 0.95:                             # lower lid: cheeks pushing up
                    lyy = cy + ry - lo * ry * 0.95
                    lm = np.zeros_like(mask)
                    lm[int(lyy):] = 255
                    img[(lm > 0) & (mask > 0)] = (*self.skin, 255)
                    cv2.ellipse(img, (int(cx), int(lyy + ry * 0.22)), (int(rx * 0.95), int(ry * 0.28)), 0, 200, 340,
                                (*OUTLINE, 255), max(1, thick - 1), cv2.LINE_AA)
                cv2.ellipse(img, (int(cx), int(cy)), (int(rx), int(ry)), 0, 0, 360, (*OUTLINE, 255), thick, cv2.LINE_AA)
                if lid >= 0.98:
                    cv2.ellipse(img, (int(cx), int(cy + ry * 0.1)), (int(rx), int(ry * 0.22)), 0, 0, 180, (*OUTLINE, 255),
                                thick + 1, cv2.LINE_AA)
            if e["tears"] > 0.05:
                for k in range(1 + int(e["tears"] * 2)):
                    ph = (t * 0.9 + k / 2 + i * 0.37) % 1.0
                    cv2.ellipse(img, (int(cx + side * rx * 0.5), int(cy + ry * 0.8 + ph * r * 3.0)), (int(r * 0.18), int(r * 0.28)),
                                0, 0, 360, (120, 190, 255, 230), -1, cv2.LINE_AA)
            # brows (inner end near the nose); lid follows its brow, brows lead the face
            bi = eb["bi_l"] if i == 0 else eb["bi_r"]
            bo = eb["bo_l"] if i == 0 else eb["bo_r"]
            lift = st.get("brow_flash", 0.0) + st.get("brow_wiggle", 0.0) * 0.35 * math.sin(t * 28 + i * math.pi)
            by = cy - self.brow_y - (max(1.0, op) - 1) * r * 0.5
            inner = (cx - side * rx * 0.95, by - (bi + lift) * B)
            outer = (cx + side * rx * 1.15, by - (bo + lift) * B + r * 0.05)
            midp = ((inner[0] + outer[0]) / 2, min(inner[1], outer[1]) - r * (0.08 + 0.45 * eb["bc"]))
            bw_ = max(4, int(r * 0.58))
            pts = _bezier(inner, midp, outer, 14)
            cv2.polylines(img, [pts], False, (*self.brow_col, 255), bw_, cv2.LINE_AA)
            for pt in (pts[0], pts[-1]):                     # rounded, slightly tapered ends
                cv2.circle(img, (int(pt[0]), int(pt[1])), max(2, bw_ // 2 - 1), (*self.brow_col, 255), -1, cv2.LINE_AA)
            if self.glasses:
                gr = r * 1.55
                cv2.circle(img, (int(c[0]), int(cy + r * 0.05)), int(gr), (*OUTLINE, 255), max(3, int(r * 0.3)), cv2.LINE_AA)
                cv2.ellipse(img, (int(c[0]), int(cy)), (int(gr * 0.7), int(gr * 0.7)), 0, 200, 250, (255, 255, 255, 200),
                            max(2, int(r * 0.1)), cv2.LINE_AA)
        if self.glasses:
            gr = r * 1.55
            cv2.line(img, (int(a[0] + gr), int(a[1])), (int(b[0] - gr), int(b[1])), (*OUTLINE, 255), max(3, int(r * 0.26)), cv2.LINE_AA)

        # ---- one-off symbols (sweat / vein) appear on the accent and fade
        if e["sweat"] > 0.1 and sym > 0.02:
            n = 1 if e["sweat"] < 1.5 else 3
            for k in range(n):
                ph = ((t * 0.35 + k * 0.33) % 1.0) if n > 1 else min(1.0, st.get("sym_t", 0.0) / 1.5)
                sx = b[0] + r * 1.9 if k % 2 == 0 else a[0] - r * 1.9
                sy = eye_y - self.brow_y - r * 0.6 + ph * r * 1.6
                sz = r * 0.42
                pts = np.array([[sx, sy - sz * 1.7], [sx - sz, sy + sz * 0.2], [sx, sy + sz], [sx + sz, sy + sz * 0.2]], np.int32)
                cv2.fillPoly(img, [pts], (150, 205, 245, int(240 * sym)), cv2.LINE_AA)
                cv2.polylines(img, [pts], True, (60, 110, 160, int(255 * sym)), max(1, int(r * 0.07)), cv2.LINE_AA)
        if e["scrunch"] > 0.05:
            ny = eye_y + 0.3 * (m_y - eye_y)
            for k in (-1, 1):
                x0 = mid_x + k * r * 0.25
                for j in range(2):
                    yy = ny - j * r * 0.25
                    cv2.line(img, (int(x0), int(yy)), (int(x0 + k * r * 0.45 * e["scrunch"]), int(yy - r * 0.12)),
                             (*self._shade(0.65), 255), max(2, int(r * 0.08)), cv2.LINE_AA)
        self.draw_mouth(img, st)

    # ------------------------------------------------------------------ mouth
    def draw_mouth(self, img: np.ndarray, st: dict) -> None:
        e = st["emo"]
        o, shape = st["mouth"]
        talk = st.get("talk", 0.0)
        w = self.mw * e["mw"]
        mx = float(self.mouth[0]) + e["mshift"] * self.mw * 0.22
        my = float(self.mouth[1])
        thick = max(4, int(self.mw * 0.09))
        style = int(e["mstyle"])
        cl, cr = e["c_l"], e["c_r"]
        talking = talk > 0 and o > 0.12
        open_ = max(o if talk else 0.0, e["mopen"])
        if st.get("grin") and not talking:
            style = 8

        def corner_pts(hw, y):
            return (mx - hw, y - cl * w * 0.15), (mx + hw, y - cr * w * 0.15)

        if not talking:
            if style == 6:                                     # wavy nervous line
                xs = np.linspace(-w * 0.42, w * 0.42, 24)
                ys = my + np.sin(xs / (w * 0.42) * math.pi * 2.5) * w * 0.035 - (cl + cr) * w * 0.04
                cv2.polylines(img, [np.stack([mx + xs, ys], 1).astype(np.int32)], False, (*OUTLINE, 255), thick, cv2.LINE_AA)
                return
            if style == 8:                                     # toothy forced grin
                hw, hh = w * 0.6, w * 0.17
                l, r_ = corner_pts(hw, my)
                pts = np.array([[l[0], l[1] - hh * 0.3], [r_[0], r_[1] - hh * 0.3], [mx + hw * 0.85, my + hh],
                                [mx - hw * 0.85, my + hh]], np.int32)
                cv2.fillPoly(img, [pts], (255, 255, 255, 255), cv2.LINE_AA)
                for k in range(1, 6):
                    xk = int(mx - hw + k * 2 * hw / 6)
                    cv2.line(img, (xk, int(my - hh * 0.3)), (xk, int(my + hh * 0.9)), (*OUTLINE, 160), max(1, thick // 3), cv2.LINE_AA)
                cv2.line(img, (int(mx - hw), int(my + hh * 0.35)), (int(mx + hw), int(my + hh * 0.35)), (*OUTLINE, 200),
                         max(1, thick // 3), cv2.LINE_AA)
                cv2.polylines(img, [pts], True, (*OUTLINE, 255), thick, cv2.LINE_AA)
                return
            if style == 5 and open_ < 0.35:                    # gritted teeth: corners decide smile vs grimace
                hw, hh = w * 0.5, w * 0.15
                l, r_ = corner_pts(hw, my)
                sag = -(cl + cr) / 2 * w * 0.08
                pts = np.array([[l[0], l[1] - hh * 0.5], [mx, my - hh * 0.5 + sag], [r_[0], r_[1] - hh * 0.5],
                                [r_[0] - hw * 0.08, r_[1] + hh * 0.7], [mx, my + hh + sag], [l[0] + hw * 0.08, l[1] + hh * 0.7]],
                               np.int32)
                cv2.fillPoly(img, [pts], (250, 250, 245, 255), cv2.LINE_AA)
                cv2.line(img, (int(l[0]), int((l[1] + my) / 2 + hh * 0.1)), (int(r_[0]), int((r_[1] + my) / 2 + hh * 0.1)),
                         (*OUTLINE, 210), max(1, thick // 2), cv2.LINE_AA)
                for k in range(1, 5):
                    xk = int(mx - hw + k * 2 * hw / 5)
                    cv2.line(img, (xk, int(my - hh * 0.5)), (xk, int(my + hh * 0.8)), (*OUTLINE, 140), max(1, thick // 3), cv2.LINE_AA)
                cv2.polylines(img, [pts], True, (*OUTLINE, 255), thick, cv2.LINE_AA)
                return
            if style in (0, 1) or open_ < 0.1:                 # closed: line / wide closed smile
                hw = w * (0.45 if style == 0 else 0.55)
                l, r_ = corner_pts(hw, my)
                avg = (cl + cr) / 2
                mid = (mx, my + avg * w * (0.16 if style == 0 else 0.26))
                cv2.polylines(img, [_bezier(l, mid, r_, 18)], False, (*OUTLINE, 255), thick + (1 if style == 1 else 0), cv2.LINE_AA)
                if style == 1 and avg > 0.3:                    # little corner tucks sell a real smile
                    for (x, y), s in ((l, -1), (r_, 1)):
                        cv2.line(img, (int(x), int(y)), (int(x + s * w * 0.06), int(y - w * 0.05)), (*OUTLINE, 255),
                                 max(2, thick - 1), cv2.LINE_AA)
                return

        # ---- open mouth (talking, or an open style)
        dims = {"A": (0.52, 0.55), "E": (0.58, 0.26), "O": (0.3, 0.42), "U": (0.26, 0.24), "X": (0.5, 0.4)}[shape if talking else "X"]
        stress = 1.0 + 0.3 * max(0.0, o - 0.7) / 0.3 if talking else 1.0
        hw = w * dims[0] * (0.75 + 0.25 * open_)
        hh = w * dims[1] * (0.35 + 0.65 * open_) * stress
        if style == 3 and not talking:
            hw, hh = w * 0.3 * (0.8 + 0.4 * open_), w * 0.38 * (0.8 + 0.5 * open_)
        elif style == 4:
            hw, hh = w * 0.5 * (0.9 + 0.3 * open_), w * 0.5 * (0.8 + 0.5 * open_)
        cy = my + hh * 0.3
        avg = (cl + cr) / 2
        mask = np.zeros(img.shape[:2], np.uint8)
        n = 20
        if avg > 0.4 or style == 2:                            # open smile "D": flat top, round bottom
            top = [(mx + hw * math.cos(tt), cy - hh * 0.35 - avg * w * 0.09 * math.cos(tt) ** 2) for tt in np.linspace(0, math.pi, n)]
            bot = [(mx - hw * math.cos(tt), cy + hh * 1.05 * math.sin(tt)) for tt in np.linspace(0, math.pi, n)]
        elif avg < -0.3 or style == 7:                         # open frown: round top, flat bottom
            top = [(mx + hw * math.cos(tt), cy - hh * math.sin(tt)) for tt in np.linspace(0, math.pi, n)]
            bot = [(mx - hw * math.cos(tt), cy + hh * 0.35 + (-avg) * w * 0.06 * math.cos(tt) ** 2) for tt in np.linspace(0, math.pi, n)]
        else:
            top = [(mx + hw * math.cos(tt), cy - hh * 0.55 * math.sin(tt)) for tt in np.linspace(0, math.pi, n)]
            bot = [(mx - hw * math.cos(tt), cy + hh * math.sin(tt)) for tt in np.linspace(0, math.pi, n)]
        poly = np.array(top + bot, np.int32)
        cv2.fillPoly(mask, [poly], 255, cv2.LINE_AA)
        img[mask > 0] = (95, 25, 35, 255)
        tm = np.zeros_like(mask)
        cv2.ellipse(tm, (int(mx), int(cy + hh * 0.75)), (int(hw * 0.6), int(hh * 0.5)), 0, 0, 360, 255, -1, cv2.LINE_AA)
        img[(tm > 0) & (mask > 0)] = (225, 105, 115, 255)
        if (talking and shape in ("A", "E")) or style in (2, 4):
            tt_ = np.zeros_like(mask)
            ys = poly[:, 1].min()
            cv2.rectangle(tt_, (int(mx - hw), int(ys)), (int(mx + hw), int(ys + hh * (0.3 if style == 4 else 0.22))), 255, -1)
            img[(tt_ > 0) & (mask > 0)] = (250, 250, 245, 255)
        cv2.polylines(img, [poly], True, (*OUTLINE, 255), thick, cv2.LINE_AA)


# ----------------------------------------------------------------------------- head motion
def motion(e: dict, st: dict, t: float) -> dict:
    """Head motion from the emotion and from one-off gestures. rot in degrees, dx/dy in face widths."""
    rot = e.get("tilt", 0.0) * st.get("tilt_sign", 1.0)
    dy = st.get("take_dip", 0.0)
    dx = 0.0
    if e["bounce"] > 0.02:                                     # laugh: 2-3 bounces of ~7 frames
        ph = t * 2 * math.pi * 4.3
        dy += -abs(math.sin(ph)) * 0.05 * e["bounce"]
        rot += math.sin(ph) * 2.0 * e["bounce"]
    tr = e["tremble"] + st.get("shiver", 0.0)
    if tr > 0.02:
        dx += (1 if int(t * 15) % 2 else -1) * 0.008 * tr
    for kind, p in st.get("moves", []):
        if kind == "nod":                                      # one clear nod: down, up, settle (~0.4 s)
            dy += math.sin(min(1.0, p * 1.6) * math.pi) * 0.06
            rot += math.sin(min(1.0, p * 1.6) * math.pi) * 1.5
        elif kind == "shake":                                  # three cycles of ~7 frames
            env = 1 - p
            rot += math.sin(p * math.pi * 6) * 8 * env
            dx += math.sin(p * math.pi * 6) * 0.035 * env
        elif kind == "recoil":                                 # snap back 5-10 deg, ease out
            env = math.sin(min(1, p * 3) * math.pi / 2) * (1 - p) ** 0.6
            dy += -0.10 * env
            rot += -7 * env
        elif kind == "lean":
            env = math.sin(p * math.pi)
            dx += 0.06 * env
            rot += 6 * env
    return {"rot": rot, "dx": dx, "dy": dy}
