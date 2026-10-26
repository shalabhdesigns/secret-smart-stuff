"""Expressive cartoon faces, drawn by code on top of the locked character art.

Every feature is a continuous parameter, so emotions blend smoothly and can be mixed:
  brows   raise (each side), tilt (angry <-> worried), arch, furrow lines
  eyes    openness, upper-lid droop, lower-lid squint, asymmetry, pupil size, style
          (normal / happy arcs ^^ / squeezed > < / shocked dots), sparkle, eye-roll, tremble
  mouth   smile curve, width, base opening, style (line, open smile, grin, smirk, wavy,
          frown-open, O, scream, gritted teeth, pout) — blended with the lip-sync visemes
  cheeks  blush, puff, smile lines
  nose    scrunch lines
  ears    flush red (ear masks come from the master head)
  extras  sweat drops, anger vein, worry lines, gloom shade, tears
Head motion (nod, shake, tremble, laugh bounce, recoil) is returned by `motion()` for the actor.
"""
from __future__ import annotations

import math

import cv2
import numpy as np

OUTLINE = (40, 22, 18)

# ----------------------------------------------------------------------------- parameters
BASE = dict(
    brow_l=0.0, brow_r=0.0, brow_tilt=0.0, brow_arch=0.25, furrow=0.0,
    eye_open=1.0, lid=0.12, squint=0.0, lid_asym=0.0, pupil=1.0, eye_style=0, sparkle=0.0,
    smile=0.25, mouth_w=1.0, mouth_open=0.0, mouth_style=0, smirk=0.0,
    blush=0.0, puff=0.0, smile_lines=0.0, scrunch=0.0, ear_red=0.0,
    sweat=0.0, vein=0.0, worry_lines=0.0, gloom=0.0, tears=0.0,
    tremble=0.0, bounce=0.0, head_tilt=0.0,
)
# eye_style: 0 normal, 1 happy arcs, 2 squeezed shut > <, 3 shocked (tiny pupils, wide)
# mouth_style: 0 line/viseme, 1 open smile (D), 2 toothy grin, 3 wavy nervous, 4 O, 5 scream,
#              6 gritted teeth, 7 pout, 8 frown-open
DISCRETE = ("eye_style", "mouth_style")

EMOTIONS: dict[str, dict] = {
    "neutral": {},
    "happy": dict(brow_l=0.3, brow_r=0.3, lid=0.05, squint=0.3, smile=0.9, smile_lines=0.4, mouth_style=1, mouth_open=0.15),
    "laugh": dict(brow_l=0.45, brow_r=0.45, eye_style=1, smile=1.0, mouth_style=1, mouth_open=0.7, mouth_w=1.2,
                  smile_lines=0.8, blush=0.3, bounce=1.0, head_tilt=-4),
    "proud": dict(brow_l=0.45, brow_r=0.45, brow_tilt=-0.1, lid=0.25, squint=0.25, smile=0.9, smirk=0.2,
                  smile_lines=0.5, head_tilt=-3),
    "smug": dict(brow_l=0.55, brow_r=0.05, lid=0.38, lid_asym=0.12, smile=0.6, smirk=0.8, head_tilt=4),
    "sly": dict(brow_l=-0.1, brow_r=0.45, brow_tilt=-0.35, lid=0.32, squint=0.3, lid_asym=-0.15, smile=0.6, smirk=0.7),
    "excited": dict(brow_l=0.7, brow_r=0.7, eye_open=1.25, pupil=1.2, sparkle=1.0, smile=1.0, mouth_style=1,
                    mouth_open=0.55, mouth_w=1.15, blush=0.35, bounce=0.6),
    "nervous": dict(brow_l=0.35, brow_r=0.25, brow_tilt=0.75, eye_open=1.05, pupil=0.75, smile=0.0, mouth_style=3,
                    sweat=0.6, tremble=0.25),
    "forced_smile": dict(brow_l=0.4, brow_r=0.3, brow_tilt=0.8, eye_open=1.12, pupil=0.7, smile=0.6, mouth_style=2,
                         mouth_w=1.25, sweat=0.5, tremble=0.15),
    "worried": dict(brow_l=0.4, brow_r=0.4, brow_tilt=0.9, brow_arch=0.1, worry_lines=0.6, eye_open=1.05, pupil=0.9,
                    smile=-0.5, mouth_style=3),
    "scared": dict(brow_l=0.7, brow_r=0.7, brow_tilt=0.9, eye_open=1.3, pupil=0.55, smile=-0.6, mouth_style=8,
                   mouth_open=0.35, worry_lines=0.7, sweat=1.0, tremble=0.6, gloom=0.3),
    "panic": dict(brow_l=0.8, brow_r=0.75, brow_tilt=1.0, eye_open=1.35, pupil=0.45, eye_style=3, smile=-0.7,
                  mouth_style=5, mouth_open=0.6, worry_lines=0.8, sweat=1.0, tremble=1.0, gloom=0.4),
    "shock": dict(brow_l=0.95, brow_r=0.95, brow_arch=0.5, eye_open=1.4, eye_style=3, pupil=0.4, smile=-0.2,
                  mouth_style=4, mouth_open=0.8, ear_red=0.0),
    "angry": dict(brow_l=-0.25, brow_r=-0.25, brow_tilt=-1.0, furrow=0.8, lid=0.25, squint=0.25, pupil=0.85,
                  smile=-0.7, mouth_style=6, mouth_w=1.05, scrunch=0.5, vein=0.7, ear_red=0.6, puff=0.2),
    "furious": dict(brow_l=-0.35, brow_r=-0.35, brow_tilt=-1.2, furrow=1.0, eye_open=1.15, pupil=0.5, smile=-0.9,
                    mouth_style=5, mouth_open=0.7, scrunch=0.8, vein=1.0, ear_red=1.0, tremble=0.5),
    "annoyed": dict(brow_l=-0.1, brow_r=0.1, brow_tilt=-0.5, furrow=0.4, lid=0.4, squint=0.15, smile=-0.4, smirk=-0.3,
                    puff=0.3),
    "deadpan": dict(brow_l=-0.05, brow_r=-0.05, lid=0.52, squint=0.12, smile=0.0),
    "unimpressed": dict(brow_l=0.35, brow_r=-0.1, lid=0.5, lid_asym=0.1, smile=-0.25, smirk=-0.4),
    "skeptical": dict(brow_l=-0.2, brow_r=0.75, brow_tilt=-0.2, lid=0.3, lid_asym=0.2, squint=0.2, smile=-0.15, smirk=0.4,
                      head_tilt=5),
    "disgust": dict(brow_l=-0.1, brow_r=-0.25, brow_tilt=-0.4, furrow=0.5, lid=0.35, squint=0.5, scrunch=1.0, smile=-0.8,
                    mouth_style=6, smirk=-0.5, head_tilt=-4),
    "sad": dict(brow_l=0.3, brow_r=0.3, brow_tilt=1.0, lid=0.35, pupil=1.15, smile=-0.9, mouth_style=3, tears=0.5,
                gloom=0.2),
    "defeated": dict(brow_l=-0.1, brow_r=-0.1, brow_tilt=0.6, lid=0.55, squint=0.1, smile=-0.4, gloom=0.6, head_tilt=-6),
    "embarrassed": dict(brow_l=0.3, brow_r=0.3, brow_tilt=0.7, lid=0.3, eye_style=0, smile=0.35, mouth_style=3, blush=1.0,
                        ear_red=0.8, sweat=0.4, head_tilt=-5),
    "sheepish": dict(brow_l=0.3, brow_r=0.2, brow_tilt=0.65, lid=0.28, squint=0.25, smile=0.45, smirk=0.25, blush=0.6,
                     ear_red=0.3, sweat=0.3, head_tilt=-4),
    "confused": dict(brow_l=0.7, brow_r=-0.2, brow_tilt=0.3, lid_asym=0.25, eye_open=1.1, pupil=0.9, smile=-0.2, smirk=-0.5,
                     mouth_style=3, head_tilt=8),
    "thinking": dict(brow_l=0.1, brow_r=0.5, lid=0.3, lid_asym=-0.15, smile=0.0, smirk=0.35, head_tilt=4),
    "love": dict(brow_l=0.5, brow_r=0.5, brow_tilt=0.3, eye_style=1, smile=0.9, blush=1.0, sparkle=0.6, head_tilt=-6),
    "pained": dict(brow_l=0.2, brow_r=0.2, brow_tilt=1.0, eye_style=2, smile=-0.6, mouth_style=6, mouth_w=1.15, scrunch=0.6,
                   sweat=0.5, tremble=0.4),
    "grin": dict(brow_l=0.35, brow_r=0.35, brow_tilt=0.7, eye_open=1.12, pupil=0.75, smile=0.5, mouth_style=2, mouth_w=1.3,
                 sweat=0.4),
    "shout": dict(brow_l=0.55, brow_r=0.55, brow_tilt=-0.55, eye_open=1.2, pupil=0.75, smile=-0.2, mouth_style=5,
                  mouth_open=0.5, ear_red=0.5, vein=0.4),
}
ALIASES = {"proud ": "proud"}


def emotion(name: str) -> dict:
    e = dict(BASE)
    e.update(EMOTIONS.get(ALIASES.get(name, name), {}))
    return e


def blend(a: dict, b: dict, k: float) -> dict:
    out = {}
    for key in BASE:
        if key in DISCRETE:
            out[key] = b[key] if k >= 0.5 else a[key]
        else:
            out[key] = a[key] + (b[key] - a[key]) * k
    return out


def _blend_color(img: np.ndarray, mask: np.ndarray, color, alpha: float) -> None:
    """Paint `color` into img (RGBA uint8) where mask>0 (float mask 0..1), only on opaque pixels."""
    if alpha <= 0.001:
        return
    a = (mask.astype(np.float32) * alpha * (img[..., 3:4] / 255.0)[..., 0])[..., None]
    img[..., :3] = (img[..., :3].astype(np.float32) * (1 - a) + np.array(color, np.float32) * a).astype(np.uint8)


def _bezier(p0, p1, p2, n=16):
    return np.array([(1 - t) ** 2 * np.array(p0) + 2 * (1 - t) * t * np.array(p1) + t * t * np.array(p2)
                     for t in np.linspace(0, 1, n)], np.int32)


# ----------------------------------------------------------------------------- the face
class Face:
    """spec keys: eyes [[x,y],[x,y]], eye_r, mouth [x,y], mouth_w, glasses, brow_gap, brow_color, stache,
    ears [ {mask: HxW float32 in ROI coords} ] (optional). Coordinates are in the image passed to draw()."""

    def __init__(self, spec: dict, scale: float, skin):
        self.s = scale
        self.eyes = [np.array(e, np.float32) * scale for e in spec["eyes"]]
        self.r = spec["eye_r"] * scale
        self.brow_y = spec.get("brow_gap", 1.9) * self.r
        self.mouth = np.array(spec["mouth"], np.float32) * scale
        self.mw = spec["mouth_w"] * scale
        self.glasses = spec.get("glasses", False)
        self.brow_col = tuple(spec.get("brow_color", (30, 24, 22)))
        self.skin = tuple(int(v) for v in skin)
        self.ears = spec.get("ears", [])
        self.has_stache = bool(spec.get("stache"))
        self.rng = np.random.default_rng(7)

    # -- helpers
    def _shade(self, k):
        return tuple(int(c * k) for c in self.skin)

    def draw(self, img: np.ndarray, st: dict) -> None:
        e = st["emo"]
        r = self.r
        t = st.get("t", 0.0)
        a, b = self.eyes
        eye_y = (a[1] + b[1]) / 2
        mid_x = (a[0] + b[0]) / 2
        m_y = float(self.mouth[1])
        H, W = img.shape[:2]
        thick = max(2, int(r * 0.16))

        # ---- cheeks: blush, puff, smile lines (under everything)
        for side, c in ((-1, a), (1, b)):
            cx, cy = c[0] + side * r * 0.55, eye_y + 0.58 * (m_y - eye_y)
            if e["blush"] > 0.02:
                mask = np.zeros((H, W), np.float32)
                cv2.ellipse(mask, (int(cx), int(cy)), (int(r * 1.05), int(r * 0.55)), 0, 0, 360, 1.0, -1, cv2.LINE_AA)
                mask = cv2.GaussianBlur(mask, (0, 0), max(1.0, r * 0.25))
                _blend_color(img, mask, (235, 95, 105), 0.55 * min(1.0, e["blush"]))
                if e["blush"] > 0.6:     # anime blush hatch marks
                    for k in range(3):
                        x0 = int(cx - r * 0.5 + k * r * 0.42)
                        cv2.line(img, (x0, int(cy + r * 0.2)), (x0 + int(r * 0.25), int(cy - r * 0.2)), (205, 70, 80, 255),
                                 max(1, int(r * 0.08)), cv2.LINE_AA)
            if e["puff"] > 0.05:
                rr = int(r * (0.7 + 0.5 * e["puff"]))
                cv2.ellipse(img, (int(cx + side * r * 0.25), int(cy + r * 0.3)), (rr, int(rr * 0.85)), 0,
                            -60 if side > 0 else 120, 60 if side > 0 else 240, (*self._shade(0.82), 255),
                            max(2, int(r * 0.1)), cv2.LINE_AA)
            if e["smile_lines"] > 0.1 and not self.has_stache:
                mx = float(self.mouth[0]) + side * self.mw * (0.62 + 0.1 * e["mouth_w"])
                p0 = (mx, m_y - self.mw * 0.35)
                p1 = (mx + side * self.mw * 0.12, m_y)
                p2 = (mx, m_y + self.mw * 0.22)
                cv2.polylines(img, [_bezier(p0, p1, p2)], False, (*self._shade(0.72), int(255 * min(1, e["smile_lines"]))),
                              max(2, int(r * 0.09)), cv2.LINE_AA)

        # ---- ears flush red
        if e["ear_red"] > 0.02:
            for ear in self.ears:
                _blend_color(img, ear["mask"], (225, 60, 55), 0.6 * min(1.0, e["ear_red"]))

        # ---- gloom (blue shade over the upper face)
        if e["gloom"] > 0.02:
            mask = np.zeros((H, W), np.float32)
            top = int(eye_y - r * 4.5)
            g = np.clip((np.arange(H, dtype=np.float32) - top) / (eye_y + r * 1.5 - top), 0, 1)
            g = 1 - g
            band = np.zeros((H, W), np.float32)
            x0, x1 = int(a[0] - r * 2.4), int(b[0] + r * 2.4)
            band[max(0, top):, max(0, x0):min(W, x1)] = 1
            mask = band * g[:, None]
            mask = cv2.GaussianBlur(mask, (0, 0), r * 0.5)
            _blend_color(img, mask, (70, 70, 140), 0.45 * e["gloom"])
            for k in range(4):   # vertical gloom lines
                x = int(a[0] - r * 0.6 + k * (b[0] - a[0] + r * 1.2) / 3)
                cv2.line(img, (x, int(eye_y - r * 3.4)), (x, int(eye_y - r * (2.6 - 0.2 * (k % 2)))), (60, 60, 110, 200),
                         max(1, int(r * 0.1)), cv2.LINE_AA)

        # ---- eyes
        look = st.get("look", (0, 0))
        tremble = e["tremble"] + st.get("shiver", 0.0)
        jx = math.sin(t * 61) * r * 0.06 * tremble
        jy = math.cos(t * 53) * r * 0.05 * tremble
        for i, c in enumerate(self.eyes):
            side = -1 if i == 0 else 1
            cx, cy = float(c[0]) + jx, float(c[1]) + jy
            openk = max(0.2, e["eye_open"])
            ry, rx = r * 1.08 * openk, r * 0.86 * (0.85 + 0.15 * openk)
            lid = e["lid"] + side * e["lid_asym"]
            lid = max(lid, st.get("blink", 0.0))
            if st.get("twitch", 0) > 0 and i == 1:
                lid = max(lid, st["twitch"])
            lid = min(1.0, max(0.0, lid))
            style = int(e["eye_style"])
            if style == 1 and st.get("blink", 0) < 0.5:          # happy arcs ^ ^
                cv2.ellipse(img, (int(cx), int(cy + ry * 0.25)), (int(rx * 1.05), int(ry * 0.75)), 0, 200, 340,
                            (*OUTLINE, 255), thick + 2, cv2.LINE_AA)
            elif style == 2:                                       # squeezed shut > <
                d = side
                p = np.array([[cx - d * rx, cy - ry * 0.6], [cx + d * rx * 0.6, cy], [cx - d * rx, cy + ry * 0.6]], np.int32)
                cv2.polylines(img, [p], False, (*OUTLINE, 255), thick + 2, cv2.LINE_AA)
            else:
                mask = np.zeros((H, W), np.uint8)
                cv2.ellipse(mask, (int(cx), int(cy)), (int(rx), int(ry)), 0, 0, 360, 255, -1, cv2.LINE_AA)
                cv2.ellipse(img, (int(cx), int(cy)), (int(rx), int(ry)), 0, 0, 360, (255, 255, 255, 255), -1, cv2.LINE_AA)
                pup = e["pupil"] * (0.55 if style == 3 else 1.0)
                lx, ly = look
                roll = st.get("eyeroll")
                if roll is not None:                               # pupils sweep up and around
                    ang = math.pi * (1.0 + roll)
                    lx, ly = math.cos(ang) * 0.9, -0.85 + 0.25 * math.sin(roll * math.pi)
                px = cx + lx * rx * 0.42 + math.sin(t * 47 + i) * rx * 0.05 * tremble
                py = cy + ly * ry * 0.38
                pr = r * 0.45 * pup
                pm = np.zeros_like(mask)
                cv2.circle(pm, (int(px), int(py)), max(2, int(pr)), 255, -1, cv2.LINE_AA)
                img[(pm > 0) & (mask > 0)] = (25, 20, 20, 255)
                hl = max(1, int(pr * 0.3))
                cv2.circle(img, (int(px - pr * 0.35), int(py - pr * 0.35)), hl, (255, 255, 255, 255), -1, cv2.LINE_AA)
                if e["sparkle"] > 0.3:
                    cv2.circle(img, (int(px + pr * 0.35), int(py + pr * 0.3)), max(1, int(hl * 0.6)), (255, 255, 255, 255),
                               -1, cv2.LINE_AA)
                    s = r * 0.35 * e["sparkle"]
                    sx, sy = cx + side * rx * 1.3, cy - ry * 1.2
                    for ang in (0, math.pi / 2):
                        dx, dy = math.cos(ang) * s, math.sin(ang) * s
                        cv2.line(img, (int(sx - dx), int(sy - dy)), (int(sx + dx), int(sy + dy)), (255, 245, 180, 255),
                                 max(1, int(r * 0.08)), cv2.LINE_AA)
                top = cy - ry
                if lid > 0.01:                                       # upper lid
                    lyy = top + lid * 2 * ry
                    lm = np.zeros_like(mask)
                    lm[: max(0, int(lyy))] = 255
                    img[(lm > 0) & (mask > 0)] = (*self.skin, 255)
                    if lid < 0.98:
                        half = math.sqrt(max(0.0, 1 - ((lyy - cy) / ry) ** 2)) * rx
                        cv2.line(img, (int(cx - half), int(lyy)), (int(cx + half), int(lyy)), (*OUTLINE, 255), thick, cv2.LINE_AA)
                sq = e["squint"]
                if sq > 0.01 and lid < 0.95:                         # lower lid (cheeks pushing up)
                    lyy = cy + ry - sq * ry * 1.1
                    lm = np.zeros_like(mask)
                    lm[int(lyy):] = 255
                    img[(lm > 0) & (mask > 0)] = (*self.skin, 255)
                    cv2.ellipse(img, (int(cx), int(lyy + ry * 0.25)), (int(rx * 0.95), int(ry * 0.3)), 0, 200, 340,
                                (*OUTLINE, 255), max(1, thick - 1), cv2.LINE_AA)
                cv2.ellipse(img, (int(cx), int(cy)), (int(rx), int(ry)), 0, 0, 360, (*OUTLINE, 255), thick, cv2.LINE_AA)
                if lid >= 0.98:
                    cv2.ellipse(img, (int(cx), int(cy)), (int(rx), int(ry * 0.25)), 0, 0, 180, (*OUTLINE, 255), thick + 1, cv2.LINE_AA)
            # tears
            if e["tears"] > 0.05:
                n = 1 + int(e["tears"] * 2)
                for k in range(n):
                    ph = (t * 0.9 + k / n + i * 0.37) % 1.0
                    tx = cx + side * rx * 0.5
                    ty = cy + ry * 0.8 + ph * r * 3.0
                    cv2.ellipse(img, (int(tx), int(ty)), (int(r * 0.18), int(r * 0.28)), 0, 0, 360, (120, 190, 255, 230), -1,
                                cv2.LINE_AA)
            # brows: inner end next to the nose
            raise_ = e["brow_l"] if i == 0 else e["brow_r"]
            raise_ += st.get("brow_flash", 0.0)
            tilt = e["brow_tilt"]
            by = cy - self.brow_y - raise_ * r - (openk - 1) * r * 0.6
            tw = st.get("twitch", 0) * 0.35 * r if i == 1 else 0.0
            wig = st.get("brow_wiggle", 0.0) * r * 0.35 * math.sin(t * 28 + i * math.pi)
            inner = (cx - side * rx * 0.95, by - tilt * r * 0.5 + tw + wig)
            outer = (cx + side * rx * 1.15, by + tilt * r * 0.4 + tw + wig)
            midp = ((inner[0] + outer[0]) / 2, min(inner[1], outer[1]) - r * (0.1 + 0.4 * e["brow_arch"]))
            cv2.polylines(img, [_bezier(inner, midp, outer, 12)], False, (*self.brow_col, 255), max(3, int(r * 0.42)),
                          cv2.LINE_AA)
            if self.glasses:
                gr = r * 1.55
                cv2.circle(img, (int(cx - jx), int(cy - jy + r * 0.05)), int(gr), (*OUTLINE, 255), max(3, int(r * 0.3)), cv2.LINE_AA)
                cv2.ellipse(img, (int(cx - jx), int(cy - jy)), (int(gr * 0.7), int(gr * 0.7)), 0, 200, 250,
                            (255, 255, 255, 200), max(2, int(r * 0.1)), cv2.LINE_AA)
        if self.glasses:
            gr = r * 1.55
            cv2.line(img, (int(a[0] + gr), int(a[1])), (int(b[0] - gr), int(b[1])), (*OUTLINE, 255), max(3, int(r * 0.26)), cv2.LINE_AA)

        # ---- furrow + worry lines + vein + sweat
        bridge_y = eye_y - self.brow_y * 0.7
        if e["furrow"] > 0.05:
            for k in (-1, 1):
                x = mid_x + k * r * 0.22
                cv2.line(img, (int(x), int(bridge_y - r * 0.55 * e["furrow"])), (int(x - k * r * 0.08), int(bridge_y + r * 0.3)),
                         (*self._shade(0.65), 255), max(2, int(r * 0.09)), cv2.LINE_AA)
        if e["worry_lines"] > 0.05:
            fy = eye_y - self.brow_y - r * 1.4
            for k in range(3):
                y = fy - k * r * 0.38
                xs = np.linspace(mid_x - r * 1.3, mid_x + r * 1.3, 14)
                ys = y + np.sin(xs / r * 3.0) * r * 0.08
                cv2.polylines(img, [np.stack([xs, ys], 1).astype(np.int32)], False,
                              (*self._shade(0.7), int(255 * min(1, e["worry_lines"]))), max(1, int(r * 0.08)), cv2.LINE_AA)
        if e["vein"] > 0.05:
            vx, vy = b[0] + r * 1.4, eye_y - self.brow_y - r * 1.6
            s = r * (0.45 + 0.25 * abs(math.sin(t * 9))) * min(1, e["vein"])
            for ang in (0.25, 1.82, 3.39, 4.96):
                p0 = (vx + math.cos(ang) * s * 0.25, vy + math.sin(ang) * s * 0.25)
                p2 = (vx + math.cos(ang + 0.6) * s, vy + math.sin(ang + 0.6) * s)
                p1 = (vx + math.cos(ang) * s * 0.9, vy + math.sin(ang) * s * 0.9)
                cv2.polylines(img, [_bezier(p0, p1, p2, 8)], False, (210, 40, 50, 255), max(2, int(r * 0.13)), cv2.LINE_AA)
        if e["sweat"] > 0.1:
            n = 1 + int(e["sweat"] * 1.5)
            for k in range(n):
                ph = (t * 0.6 + k * 0.45) % 1.0
                sx = (a[0] - r * 1.8) if k % 2 == 0 else (b[0] + r * 1.8)
                sy = eye_y - self.brow_y - r * 1.2 + ph * r * 2.5
                sz = r * 0.32
                pts = np.array([[sx, sy - sz * 1.6], [sx - sz, sy + sz * 0.2], [sx, sy + sz], [sx + sz, sy + sz * 0.2]], np.int32)
                cv2.fillPoly(img, [pts], (150, 205, 245, 235), cv2.LINE_AA)
                cv2.polylines(img, [pts], True, (60, 110, 160, 255), max(1, int(r * 0.06)), cv2.LINE_AA)

        # ---- nose scrunch
        if e["scrunch"] > 0.05:
            ny = eye_y + 0.3 * (m_y - eye_y)
            for k in (-1, 1):
                x0 = mid_x + k * r * 0.25
                for j in range(2):
                    yy = ny - j * r * 0.25
                    cv2.line(img, (int(x0), int(yy)), (int(x0 + k * r * 0.45 * e["scrunch"]), int(yy - r * 0.12)),
                             (*self._shade(0.65), 255), max(2, int(r * 0.08)), cv2.LINE_AA)

        self.draw_mouth(img, st)

    # ----------------------------------------------------------------------------- mouth
    def draw_mouth(self, img: np.ndarray, st: dict) -> None:
        e = st["emo"]
        o, shape = st["mouth"]
        talk = st.get("talk", 0.0)
        smile = e["smile"]
        mx, my = float(self.mouth[0]), float(self.mouth[1])
        w = self.mw * e["mouth_w"]
        thick = max(3, int(self.mw * 0.07))
        style = int(e["mouth_style"])
        smirk = e["smirk"]
        open_ = max(o * (1.0 if talk else 0.0), e["mouth_open"])
        if st.get("grin") and o < 0.12:
            style = 2

        def corners(hw, base_y):
            # corner heights: smile lifts both, smirk lifts one side and drops the other
            lift = smile * w * 0.12
            return (mx - hw, base_y - lift + smirk * w * 0.08), (mx + hw, base_y - lift - smirk * w * 0.12)

        if style == 3 and open_ < 0.15:                     # wavy nervous line
            xs = np.linspace(-w * 0.45, w * 0.45, 24)
            ys = my + np.sin(xs / (w * 0.45) * math.pi * 2.5 + st.get("t", 0) * 6) * w * 0.035 - smile * w * 0.05
            cv2.polylines(img, [np.stack([mx + xs, ys], 1).astype(np.int32)], False, (*OUTLINE, 255), thick, cv2.LINE_AA)
            return
        if style == 7 and open_ < 0.15:                     # pout
            cv2.ellipse(img, (int(mx), int(my)), (int(w * 0.18), int(w * 0.13)), 0, 0, 360, (150, 60, 70, 255), -1, cv2.LINE_AA)
            cv2.ellipse(img, (int(mx), int(my)), (int(w * 0.18), int(w * 0.13)), 0, 0, 360, (*OUTLINE, 255), thick, cv2.LINE_AA)
            return
        if style == 2 and open_ < 0.2:                      # toothy grin (forced)
            hw, hh = w * 0.6, w * 0.17
            l, r_ = corners(hw, my)
            pts = np.array([[l[0], l[1] - hh * 0.3], [r_[0], r_[1] - hh * 0.3], [mx + hw * 0.85, my + hh], [mx - hw * 0.85, my + hh]],
                           np.int32)
            cv2.fillPoly(img, [pts], (255, 255, 255, 255), cv2.LINE_AA)
            for k in range(1, 6):
                xk = int(mx - hw + k * 2 * hw / 6)
                cv2.line(img, (xk, int(my - hh * 0.3)), (xk, int(my + hh * 0.9)), (*OUTLINE, 160), max(1, thick // 3), cv2.LINE_AA)
            cv2.line(img, (int(mx - hw), int(my + hh * 0.35)), (int(mx + hw), int(my + hh * 0.35)), (*OUTLINE, 200),
                     max(1, thick // 3), cv2.LINE_AA)
            cv2.polylines(img, [pts], True, (*OUTLINE, 255), thick, cv2.LINE_AA)
            return
        if style == 6 and open_ < 0.35:                     # gritted teeth (angry / pained)
            hw, hh = w * 0.5, w * 0.16 * (1 + open_)
            cy = my + smile * w * 0.04
            pts = np.array([[mx - hw, cy - hh * (0.6 - 0.4 * min(0, smile))], [mx + hw, cy - hh * (0.6 - 0.4 * min(0, smile))],
                            [mx + hw * 0.9, cy + hh], [mx - hw * 0.9, cy + hh]], np.int32)
            cv2.fillPoly(img, [pts], (250, 250, 245, 255), cv2.LINE_AA)
            cv2.line(img, (int(mx - hw), int(cy + hh * 0.2)), (int(mx + hw), int(cy + hh * 0.2)), (*OUTLINE, 220),
                     max(1, thick // 2), cv2.LINE_AA)
            for k in range(1, 5):
                xk = int(mx - hw + k * 2 * hw / 5)
                cv2.line(img, (xk, int(cy - hh * 0.6)), (xk, int(cy + hh)), (*OUTLINE, 150), max(1, thick // 3), cv2.LINE_AA)
            cv2.polylines(img, [pts], True, (*OUTLINE, 255), thick, cv2.LINE_AA)
            return
        if open_ < 0.12 or (shape == "X" and style in (0,) and e["mouth_open"] < 0.12):
            # closed: curve with smile + smirk
            l, r_ = corners(w * 0.45, my)
            mid = (mx, my + smile * w * 0.16 - (l[1] + r_[1] - 2 * my) * 0.1)
            cv2.polylines(img, [_bezier(l, mid, r_, 18)], False, (*OUTLINE, 255), thick, cv2.LINE_AA)
            return

        # ---- open mouth: viseme proportions shaped by the emotion style
        dims = {"A": (0.52, 0.55), "E": (0.58, 0.26), "O": (0.3, 0.42), "U": (0.26, 0.24), "X": (0.5, 0.4)}[shape if talk else "X"]
        hw = w * dims[0] * (0.75 + 0.25 * open_)
        hh = w * dims[1] * (0.35 + 0.65 * open_)
        if style == 4:                                       # O shock
            hw, hh = w * 0.24 * (0.8 + 0.4 * open_), w * 0.3 * (0.8 + 0.5 * open_)
        elif style == 5:                                     # scream
            hw, hh = w * 0.5 * (0.9 + 0.3 * open_), w * 0.55 * (0.8 + 0.5 * open_)
        cy = my + hh * 0.3
        lift = smile * w * 0.08
        mask = np.zeros(img.shape[:2], np.uint8)
        if style == 1 or (smile > 0.5 and style in (0,)):    # open smile "D": flat top, round bottom
            top = [(mx + hw * math.cos(tt), cy - hh * 0.35 - lift * math.cos(tt) ** 2 - smirk * w * 0.06 * math.cos(tt))
                   for tt in np.linspace(0, math.pi, 20)]
            bot = [(mx - hw * math.cos(tt), cy + hh * 1.05 * math.sin(tt)) for tt in np.linspace(0, math.pi, 20)]
        elif style == 8 or smile < -0.3:                     # frown-open: round top, flatter bottom
            top = [(mx + hw * math.cos(tt), cy - hh * math.sin(tt)) for tt in np.linspace(0, math.pi, 20)]
            bot = [(mx - hw * math.cos(tt), cy + hh * 0.35 + (-smile) * w * 0.06 * math.cos(tt) ** 2)
                   for tt in np.linspace(0, math.pi, 20)]
        else:
            top = [(mx + hw * math.cos(tt), cy - hh * 0.55 * math.sin(tt) - lift * math.cos(tt) ** 2) for tt in np.linspace(0, math.pi, 20)]
            bot = [(mx - hw * math.cos(tt), cy + hh * math.sin(tt)) for tt in np.linspace(0, math.pi, 20)]
        poly = np.array(top + bot, np.int32)
        cv2.fillPoly(mask, [poly], 255, cv2.LINE_AA)
        img[mask > 0] = (95, 25, 35, 255)
        tm = np.zeros_like(mask)
        cv2.ellipse(tm, (int(mx), int(cy + hh * 0.75)), (int(hw * 0.6), int(hh * 0.5)), 0, 0, 360, 255, -1, cv2.LINE_AA)
        img[(tm > 0) & (mask > 0)] = (225, 105, 115, 255)
        if shape in ("A", "E") or style in (1, 5):
            tt_ = np.zeros_like(mask)
            ys = poly[:, 1].min()
            cv2.rectangle(tt_, (int(mx - hw), int(ys)), (int(mx + hw), int(ys + hh * (0.3 if style == 5 else 0.22))), 255, -1)
            img[(tt_ > 0) & (mask > 0)] = (250, 250, 245, 255)
        cv2.polylines(img, [poly], True, (*OUTLINE, 255), thick, cv2.LINE_AA)


# ----------------------------------------------------------------------------- head motion
def motion(e: dict, st: dict, t: float) -> dict:
    """Extra head motion from the emotion and from one-off events. Returns rot (deg), dx, dy (px factors of face w)."""
    rot = e.get("head_tilt", 0.0)
    dy = 0.0
    dx = 0.0
    if e["bounce"] > 0.02:                                   # laughing bounce
        dy += -abs(math.sin(t * 2 * math.pi * 3.2)) * 0.06 * e["bounce"]
        rot += math.sin(t * 2 * math.pi * 3.2) * 2.5 * e["bounce"]
    tr = e["tremble"] + st.get("shiver", 0.0)
    if tr > 0.02:
        dx += math.sin(t * 71) * 0.012 * tr
        dy += math.cos(t * 67) * 0.008 * tr
    for kind, p in st.get("moves", []):                      # one-off gestures, p in 0..1
        if kind == "nod":
            dy += math.sin(p * math.pi * 4) * 0.05 * (1 - p)
            rot += math.sin(p * math.pi * 4) * 3 * (1 - p)
        elif kind == "shake":
            rot += math.sin(p * math.pi * 6) * 7 * (1 - p)
            dx += math.sin(p * math.pi * 6) * 0.03 * (1 - p)
        elif kind == "recoil":
            env = math.sin(min(1, p * 2.5) * math.pi / 2) * (1 - p) ** 0.5
            dy += -0.10 * env
            rot += -6 * env
        elif kind == "lean":
            env = math.sin(p * math.pi)
            dx += 0.05 * env
            rot += 5 * env
        elif kind == "double_take":
            env = math.sin(min(1, p * 4) * math.pi) * (1 - p)
            rot += 10 * env
            dy += -0.05 * abs(env)
    return {"rot": rot, "dx": dx, "dy": dy}
