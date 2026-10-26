#!/usr/bin/env python3
"""2D puppet renderer: flat cartoon characters animated by code.

Characters are drawn once as parts (blank-faced heads, bodies, props). Everything that makes them
act is drawn here, every frame: eyes, pupils, blinks, eyebrows, mouths (lip-synced to the voice
line), glasses, the "It's fine" eye twitch, head bobs/tilts, breathing, squash on loud syllables,
plus camera punch-ins, shakes, flashes, speed lines, sweat drops and a thriller "spiral" background.

usage: puppet.py rig.json scene.json out_dir      -> out_dir/shotNN.mp4 (silent) + timeline.json
"""
from __future__ import annotations

import json
import math
import subprocess
import sys
import wave
from pathlib import Path

import cv2
import numpy as np

sys.path.insert(0, str(Path(__file__).parent))
import face as F  # noqa: E402

W, H, FPS = 1080, 1920, 30
OUTLINE = (40, 22, 18)


# ----------------------------------------------------------------------------- audio analysis
def read_wav(path: Path) -> tuple[np.ndarray, int]:
    with wave.open(str(path)) as f:
        sr, n, ch = f.getframerate(), f.getnframes(), f.getnchannels()
        x = np.frombuffer(f.readframes(n), np.int16).astype(np.float32) / 32768
    if ch > 1:
        x = x.reshape(-1, ch).mean(1)
    return x, sr


# ----------------------------------------------------------------------------- lip sync
# Mouth shapes come from the WORDS (Devanagari syllables), timed by the voice:
#  1. a real character alignment from ElevenLabs (<line>.align.json), or
#  2. the known text spread over the voiced parts of the audio (<line>.txt), or
#  3. the audio alone (fallback).
# Loudness only scales how wide each shape opens; silence always closes the mouth.
_CONS = set(range(0x0915, 0x093A)) | set(range(0x0958, 0x0960))
_LABIAL = set("पफबभम")
_VOWEL_SIGN = {"ा": ("A", 0.95, 1.3), "ि": ("E", 0.5, 1.0), "ी": ("E", 0.55, 1.3), "ु": ("U", 0.35, 1.0),
               "ू": ("U", 0.4, 1.3), "ृ": ("E", 0.4, 1.0), "े": ("E", 0.6, 1.3), "ै": ("E", 0.7, 1.3),
               "ो": ("O", 0.7, 1.3), "ौ": ("O", 0.8, 1.3), "ॉ": ("O", 0.75, 1.3), "ॅ": ("E", 0.6, 1.2)}
_VOWEL_IND = {"अ": ("A", 0.55, 1.0), "आ": ("A", 0.95, 1.3), "इ": ("E", 0.5, 1.0), "ई": ("E", 0.55, 1.3),
              "उ": ("U", 0.35, 1.0), "ऊ": ("U", 0.4, 1.3), "ए": ("E", 0.6, 1.3), "ऐ": ("E", 0.7, 1.3),
              "ओ": ("O", 0.7, 1.3), "औ": ("O", 0.8, 1.3), "ऑ": ("O", 0.75, 1.3), "ऋ": ("E", 0.4, 1.0)}
_LATIN = {"a": ("A", 0.8, 1.0), "e": ("E", 0.55, 1.0), "i": ("E", 0.5, 1.0), "o": ("O", 0.7, 1.0), "u": ("U", 0.4, 1.0)}


def syllables(text: str) -> list[dict]:
    """Split spoken text into syllables: {onset: 'X' (lips closed) | 'U' (v/f) | None, shape, open, weight}."""
    import re
    text = re.sub(r"\[[^\]]*\]", " ", text)
    out, i, n = [], 0, len(text)
    while i < n:
        ch = text[i]
        if ord(ch) in _CONS:
            onset = "X" if ch in _LABIAL else ("U" if ch == "व" else None)
            j, ncons = i + 1, 1
            while j < n and text[j] == "़":
                j += 1
            while j + 1 < n and text[j] == "्" and ord(text[j + 1]) in _CONS:      # conjunct
                j += 2
                ncons += 1
                while j < n and text[j] == "़":
                    j += 1
            if j < n and text[j] in _VOWEL_SIGN:
                shape, op, w = _VOWEL_SIGN[text[j]]
                j += 1
            elif j < n and text[j] == "्":
                shape, op, w = "E", 0.25, 0.5
                j += 1
            else:
                end_of_word = j >= n or not (ord(text[j]) in _CONS or text[j] in _VOWEL_IND)
                shape, op, w = ("E", 0.3, 0.55) if end_of_word else ("A", 0.55, 1.0)   # schwa deletion
            while j < n and text[j] in "ंँः":
                j += 1
            out.append({"onset": onset, "shape": shape, "open": op, "w": w + 0.15 * (ncons - 1), "i0": i, "i1": j})
            i = j
        elif ch in _VOWEL_IND:
            shape, op, w = _VOWEL_IND[ch]
            j = i + 1
            while j < n and text[j] in "ंँः":
                j += 1
            out.append({"onset": None, "shape": shape, "open": op, "w": w, "i0": i, "i1": j})
            i = j
        elif ch.lower() in _LATIN:
            shape, op, w = _LATIN[ch.lower()]
            out.append({"onset": None, "shape": shape, "open": op, "w": w, "i0": i, "i1": i + 1})
            i += 1
        elif ch.isalpha():
            out.append({"onset": "X" if ch.lower() in "mbp" else None, "shape": "E", "open": 0.35, "w": 0.5, "i0": i, "i1": i + 1})
            i += 1
        else:
            i += 1
    return out


def _envelope(path: Path) -> np.ndarray:
    x, sr = read_wav(path)
    hop = sr // FPS
    win = int(sr * 0.04)
    env = np.array([float(np.sqrt((x[max(0, i * hop - win // 2): i * hop + win // 2] ** 2).mean() + 1e-12))
                    for i in range(max(1, len(x) // hop))])
    db = 20 * np.log10(env + 1e-9)
    peak = np.percentile(db, 95) if len(db) else -20
    voiced = db > peak - 26
    level = np.clip((db - (peak - 26)) / 20, 0, 1)
    return voiced, level


def lipsync(path: Path) -> list[tuple[float, str]]:
    """Per video frame: (openness 0..1, mouth shape X closed / A wide / E flat / O round / U small)."""
    import json as _json
    voiced, level = _envelope(path)
    nfr = len(voiced)
    track = [("X", 0.0)] * nfr
    align_p, text_p = path.with_suffix(".align.json"), path.with_suffix(".txt")
    sylls = None
    if align_p.exists():                                    # real timings from the TTS engine
        al = _json.loads(align_p.read_text())
        chars, st, en = al["chars"], al["starts"], al["ends"]
        sylls = syllables("".join(chars))
        for sy in sylls:
            idx = [k for k in range(sy["i0"], min(sy["i1"], len(st)))]
            sy["t0"], sy["t1"] = (st[idx[0]], en[idx[-1]]) if idx else (0, 0)
    elif text_p.exists():                                   # spread syllables over the voiced audio
        sylls = syllables(text_p.read_text())
        vidx = np.nonzero(voiced)[0]
        if len(sylls) and len(vidx):
            tot = sum(s["w"] for s in sylls)
            cum = 0.0
            for sy in sylls:
                a = int(cum / tot * len(vidx))
                cum += sy["w"]
                b = max(a + 1, int(cum / tot * len(vidx)))
                sy["t0"], sy["t1"] = vidx[a] / FPS, (vidx[min(b, len(vidx)) - 1] + 1) / FPS
    if sylls:
        for sy in sylls:
            f0, f1 = int(round(sy["t0"] * FPS)), max(int(round(sy["t0"] * FPS)) + 1, int(round(sy["t1"] * FPS)))
            on = max(1, int(0.3 * (f1 - f0))) if sy["onset"] else (1 if f1 - f0 >= 4 else 0)
            for f in range(max(0, f0), min(nfr, f1)):
                if f - f0 < on:
                    track[f] = (sy["onset"], 0.0 if sy["onset"] == "X" else 0.2) if sy["onset"] else ("E", 0.18)
                else:
                    track[f] = (sy["shape"], sy["open"])
    else:                                                   # audio only
        for f in range(nfr):
            track[f] = ("A", 0.7) if level[f] > 0.6 else (("E", 0.45) if level[f] > 0.25 else ("U", 0.3))
    out, last, hold = [], "X", 9
    for f in range(nfr):
        shape, op = track[f]
        if not voiced[f]:
            shape, op = "X", 0.0
        o = op * (0.45 + 0.55 * float(level[f])) if shape != "X" else 0.0
        if shape != last and hold < 2 and op > 0.25:        # vowel drawings stay at least 2 frames
            shape, o = last, out[-1][0] if out else 0.0
        hold = hold + 1 if shape == last else 0
        last = shape
        out.append((float(o), shape))
    return out


# ----------------------------------------------------------------------------- image helpers
def load_rgba(path: Path) -> np.ndarray:
    im = cv2.imread(str(path), cv2.IMREAD_UNCHANGED)
    if im.shape[2] == 3:
        im = np.dstack([im, np.full(im.shape[:2], 255, np.uint8)])
    return cv2.cvtColor(im, cv2.COLOR_BGRA2RGBA)


def paste(canvas: np.ndarray, rgba: np.ndarray, x: int, y: int, opacity: float = 1.0) -> None:
    """Alpha-composite rgba (uint8) onto canvas (float32 RGB 0..255) with top-left at (x, y)."""
    h, w = rgba.shape[:2]
    x0, y0, x1, y1 = max(0, x), max(0, y), min(canvas.shape[1], x + w), min(canvas.shape[0], y + h)
    if x0 >= x1 or y0 >= y1:
        return
    src = rgba[y0 - y:y1 - y, x0 - x:x1 - x].astype(np.float32)
    a = src[..., 3:4] / 255.0 * opacity
    canvas[y0:y1, x0:x1] = canvas[y0:y1, x0:x1] * (1 - a) + src[..., :3] * a


def affine_layer(rgba: np.ndarray, pivot, angle_deg: float, sx: float, sy: float, dest):
    """Rotate/scale rgba about pivot and return (layer, x, y) so pivot lands at dest."""
    h, w = rgba.shape[:2]
    a = math.radians(angle_deg)
    c, s = math.cos(a), math.sin(a)
    m = np.array([[c * sx, s * sy], [-s * sx, c * sy]], np.float32)
    corners = np.array([[0, 0], [w, 0], [0, h], [w, h]], np.float32) - np.array(pivot, np.float32)
    tc = corners @ m.T
    minx, miny = tc.min(0)
    maxx, maxy = tc.max(0)
    ow, oh = int(math.ceil(maxx - minx)) + 2, int(math.ceil(maxy - miny)) + 2
    off = np.array([-minx + 1, -miny + 1], np.float32)
    M = np.hstack([m, (off - m @ np.array(pivot, np.float32)).reshape(2, 1)])
    out = cv2.warpAffine(rgba, M, (ow, oh), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_CONSTANT, borderValue=(0, 0, 0, 0))
    return out, int(round(dest[0] - off[0])), int(round(dest[1] - off[1]))


def ease(t: float) -> float:
    t = min(1.0, max(0.0, t))
    return t * t * (3 - 2 * t)


# ----------------------------------------------------------------------------- face drawing
EXPR = {  # brow raise (eye radii), brow tilt (+worried / -angry), upper lid, lower lid, smile, pupil scale
    "neutral": (0.0, 0.0, 0.12, 0.0, 0.25, 1.0),
    "proud": (0.35, -0.15, 0.18, 0.25, 0.9, 1.0),
    "happy": (0.3, 0.0, 0.1, 0.3, 1.0, 1.0),
    "nervous": (0.3, 0.65, 0.0, 0.0, 0.0, 0.85),
    "grin": (0.35, 0.7, 0.0, 0.0, 0.0, 0.8),
    "worried": (0.35, 0.85, 0.0, 0.0, -0.45, 0.9),
    "panic": (0.65, 0.9, 0.0, 0.0, -0.7, 0.55),
    "deadpan": (-0.05, 0.0, 0.52, 0.12, 0.0, 1.0),
    "defeated": (-0.1, 0.55, 0.48, 0.0, -0.35, 1.0),
    "angry": (-0.15, -0.8, 0.25, 0.1, -0.6, 0.9),
    "shout": (0.55, -0.55, 0.0, 0.0, -0.2, 0.75),
    "sly": (0.15, -0.25, 0.3, 0.15, 0.7, 1.0),
    "sheepish": (0.25, 0.6, 0.25, 0.2, 0.35, 1.0),
}


def blend_expr(a, b, t):
    return tuple(x + (y - x) * t for x, y in zip(a, b))


class Face:
    def __init__(self, spec: dict, scale: float, skin):
        self.s = scale
        self.eyes = [np.array(e, np.float32) * scale for e in spec["eyes"]]
        self.r = spec["eye_r"] * scale
        self.brow_y = spec.get("brow_gap", 1.9) * self.r
        self.mouth = np.array(spec["mouth"], np.float32) * scale
        self.mw = spec["mouth_w"] * scale
        self.glasses = spec.get("glasses", False)
        self.brow_col = tuple(spec.get("brow_color", (30, 24, 22)))
        self.skin = skin
        self.lash = spec.get("lashes", False)
        self.stache = spec.get("stache")  # (x, y, width) in head px

    def draw(self, img: np.ndarray, st: dict) -> None:
        raise_, tilt, lid, low, smile, pup = st["expr"]
        r = self.r
        thick = max(2, int(r * 0.16))
        for i, c in enumerate(self.eyes):
            side = -1 if i == 0 else 1  # -1 = viewer's left
            cx, cy = float(c[0]), float(c[1])
            ry, rx = r * 1.08, r * 0.86
            lid_i = max(lid, st["blink"])
            if st["twitch"] > 0 and i == 1:
                lid_i = max(lid_i, st["twitch"])
            lid_i = min(1.0, lid_i)
            # eye white
            mask = np.zeros(img.shape[:2], np.uint8)
            cv2.ellipse(mask, (int(cx), int(cy)), (int(rx), int(ry)), 0, 0, 360, 255, -1, cv2.LINE_AA)
            cv2.ellipse(img, (int(cx), int(cy)), (int(rx), int(ry)), 0, 0, 360, (255, 255, 255, 255), -1, cv2.LINE_AA)
            # pupil
            px = cx + st["look"][0] * rx * 0.42
            py = cy + st["look"][1] * ry * 0.35
            pr = r * 0.45 * pup
            pupil = np.zeros_like(mask)
            cv2.circle(pupil, (int(px), int(py)), int(pr), 255, -1, cv2.LINE_AA)
            sel = (pupil > 0) & (mask > 0)
            img[sel] = (25, 20, 20, 255)
            cv2.circle(img, (int(px - pr * 0.35), int(py - pr * 0.35)), max(1, int(pr * 0.28)), (255, 255, 255, 255), -1, cv2.LINE_AA)
            # lids (skin over the eye)
            top = cy - ry
            if lid_i > 0.01:
                ly = top + lid_i * 2 * ry
                lidm = np.zeros_like(mask)
                lidm[: int(ly)] = 255
                sel = (lidm > 0) & (mask > 0)
                img[sel] = (*self.skin, 255)
                if lid_i < 0.98:
                    half = math.sqrt(max(0.0, 1 - ((ly - cy) / ry) ** 2)) * rx
                    cv2.line(img, (int(cx - half), int(ly)), (int(cx + half), int(ly)), (*OUTLINE, 255), thick, cv2.LINE_AA)
            if low > 0.01 and lid_i < 0.95:
                ly = cy + ry - low * ry
                lowm = np.zeros_like(mask)
                lowm[int(ly):] = 255
                sel = (lowm > 0) & (mask > 0)
                img[sel] = (*self.skin, 255)
            cv2.ellipse(img, (int(cx), int(cy)), (int(rx), int(ry)), 0, 0, 360, (*OUTLINE, 255), thick, cv2.LINE_AA)
            if lid_i >= 0.98:
                cv2.ellipse(img, (int(cx), int(cy)), (int(rx), int(ry * 0.25)), 0, 0, 180, (*OUTLINE, 255), thick + 1, cv2.LINE_AA)
            # brow: inner end next to the nose
            by = cy - self.brow_y - raise_ * r
            tw = st["twitch"] * 0.35 * r if i == 1 else 0.0
            inner = (cx - side * rx * 0.95, by - tilt * r * 0.45 + tw)
            outer = (cx + side * rx * 1.15, by + tilt * r * 0.35 + tw)
            mid = ((inner[0] + outer[0]) / 2, min(inner[1], outer[1]) - r * 0.25)
            pts = np.array([inner, mid, outer], np.float32)
            curve = np.array([(1 - t) ** 2 * pts[0] + 2 * (1 - t) * t * pts[1] + t * t * pts[2]
                              for t in np.linspace(0, 1, 12)], np.int32)
            cv2.polylines(img, [curve], False, (*self.brow_col, 255), max(3, int(r * 0.42)), cv2.LINE_AA)
            if self.glasses:
                gr = r * 1.55
                cv2.circle(img, (int(cx), int(cy + r * 0.05)), int(gr), (*OUTLINE, 255), max(3, int(r * 0.3)), cv2.LINE_AA)
                cv2.ellipse(img, (int(cx), int(cy)), (int(gr * 0.7), int(gr * 0.7)), 0, 200, 250, (255, 255, 255, 200), max(2, int(r * 0.1)), cv2.LINE_AA)
        if self.glasses:
            a, b = self.eyes
            gr = r * 1.55
            cv2.line(img, (int(a[0] + gr), int(a[1])), (int(b[0] - gr), int(b[1])), (*OUTLINE, 255), max(3, int(r * 0.26)), cv2.LINE_AA)
        self.draw_mouth(img, st)

    def draw_mouth(self, img: np.ndarray, st: dict) -> None:
        o, shape = st["mouth"]
        smile = st["expr"][4]
        mx, my = float(self.mouth[0]), float(self.mouth[1])
        w = self.mw
        thick = max(3, int(w * 0.07))
        if st.get("grin") and o < 0.12:  # frozen too-wide toothy grin
            hw, hh = w * 0.62, w * 0.16
            pts = np.array([[mx - hw, my - hh * 0.3], [mx + hw, my - hh * 0.3], [mx + hw * 0.85, my + hh], [mx - hw * 0.85, my + hh]], np.int32)
            cv2.fillPoly(img, [pts], (255, 255, 255, 255), cv2.LINE_AA)
            for k in range(1, 6):
                xk = int(mx - hw + k * 2 * hw / 6)
                cv2.line(img, (xk, int(my - hh * 0.3)), (xk, int(my + hh * 0.9)), (*OUTLINE, 160), max(1, thick // 3), cv2.LINE_AA)
            cv2.line(img, (int(mx - hw), int(my + hh * 0.35)), (int(mx + hw), int(my + hh * 0.35)), (*OUTLINE, 200), max(1, thick // 3), cv2.LINE_AA)
            cv2.polylines(img, [pts], True, (*OUTLINE, 255), thick, cv2.LINE_AA)
            return
        if o < 0.12 or shape == "X":
            curve = smile * w * 0.18
            xs = np.linspace(-w * 0.45, w * 0.45, 16)
            ys = my + curve * (1 - (xs / (w * 0.45)) ** 2) - curve
            pts = np.stack([mx + xs, ys], 1).astype(np.int32)
            cv2.polylines(img, [pts], False, (*OUTLINE, 255), thick, cv2.LINE_AA)
            return
        dims = {"A": (0.52, 0.55), "E": (0.58, 0.26), "O": (0.3, 0.42), "U": (0.26, 0.24)}[shape]
        hw = w * dims[0] * (0.75 + 0.25 * o)
        hh = w * dims[1] * (0.35 + 0.65 * o)
        cy = my + hh * 0.35 - smile * w * 0.03
        mask = np.zeros(img.shape[:2], np.uint8)
        top = [(mx + hw * math.cos(t), cy - hh * 0.55 * math.sin(t) - smile * w * 0.05 * math.cos(t) ** 2) for t in np.linspace(0, math.pi, 20)]
        bot = [(mx - hw * math.cos(t), cy + hh * math.sin(t)) for t in np.linspace(0, math.pi, 20)]
        poly = np.array(top + bot, np.int32)
        cv2.fillPoly(mask, [poly], 255, cv2.LINE_AA)
        img[mask > 0] = (95, 25, 35, 255)
        # tongue and teeth, clipped to the mouth
        tm = np.zeros_like(mask)
        cv2.ellipse(tm, (int(mx), int(cy + hh * 0.75)), (int(hw * 0.6), int(hh * 0.5)), 0, 0, 360, 255, -1, cv2.LINE_AA)
        img[(tm > 0) & (mask > 0)] = (225, 105, 115, 255)
        if shape in ("A", "E"):
            tt = np.zeros_like(mask)
            cv2.rectangle(tt, (int(mx - hw), int(cy - hh)), (int(mx + hw), int(cy - hh * 0.55 + hh * (0.5 if shape == "E" else 0.15))), 255, -1)
            img[(tt > 0) & (mask > 0)] = (250, 250, 245, 255)
        cv2.polylines(img, [poly], True, (*OUTLINE, 255), thick, cv2.LINE_AA)


# ----------------------------------------------------------------------------- actors
class Actor:
    def __init__(self, rig: dict, parts_dir: Path, a: dict, shot_dur: float):
        self.spec = a
        self.who = a["who"]
        self.x, self.y = a["x"], a["y"]
        sc = a.get("scale", 1.0)
        body = rig["bodies"].get(a.get("body")) if a.get("body") else None
        head = rig["heads"][a["head"]]
        self.single = head.get("single", False)
        hs = sc * a.get("head_scale", head.get("scale", 1.0))
        self.body = None
        if body:
            im = load_rgba(parts_dir / body["file"])
            for x0, y0, x1, y1 in body.get("erase", []):
                im[y0:y1, x0:x1, 3] = 0
            bs = sc * body.get("scale", 1.0)
            self.body = cv2.resize(im, None, fx=bs, fy=bs, interpolation=cv2.INTER_AREA if bs < 1 else cv2.INTER_CUBIC)
            self.socket = np.array(body["socket"], np.float32) * bs
            self.head_on_top = body.get("head_on_top", False)
        himg = load_rgba(parts_dir / head["file"])
        self.head = cv2.resize(himg, None, fx=hs, fy=hs, interpolation=cv2.INTER_AREA if hs < 1 else cv2.INTER_CUBIC)
        self.neck = np.array(head["neck"], np.float32) * hs
        sk = head.get("skin_at")
        skin = tuple(int(v) for v in himg[sk[1], sk[0], :3]) if sk else (200, 120, 85)
        self.face = Face(head, hs, skin)
        self.stache = None
        if head.get("stache"):
            st = head["stache"]
            simg = load_rgba(parts_dir / st["file"])
            k = st["width"] * hs / simg.shape[1]
            self.stache = (cv2.resize(simg, None, fx=k, fy=k, interpolation=cv2.INTER_AREA), np.array(st["at"], np.float32) * hs)
        self.lines = a.get("lines", [])  # [{"lips": [...], "at": t}]
        self._plan_timing(a, shot_dur)

    # ------------------------------------------------------------------ acting timing (docs/craft/EXPRESSIONS.md)
    def _plan_timing(self, a: dict, shot_dur: float) -> None:
        self.phase = (sum(map(ord, self.who)) % 100) / 17.0
        evs = []
        for e in a.get("events", []):
            if "twitch" in e:                              # retired: one-eye twitch reads as nothing on a phone
                continue
            if e.get("move") == "double_take":             # look -> away -> beat -> snap back + take
                t0 = e["t"]
                base = a.get("look", [0, 0])
                away = [-0.8 if (base[0] if base else 0) >= 0 else 0.8, 0.0]
                evs += [{"t": t0, "look": away}, {"t": t0 + 0.33, "look": list(base) if base else [0, 0]},
                        {"t": t0 + 0.36, "move": "recoil", "dur": 0.5}]
                if not any("expr" in x and abs(x["t"] - t0) < 0.6 for x in a.get("events", [])):
                    evs.append({"t": t0 + 0.36, "expr": "shock"})
                continue
            evs.append(e)
        self.events = sorted(evs, key=lambda e: e["t"])
        rng = np.random.default_rng(sum(map(ord, self.who)) * 7919 + int(a.get("seed", 0)))
        # blinks: on thought changes and head moves, plus a sparse fallback so long holds never look dead
        marks = sorted([e["t"] - 0.04 for e in self.events if ("expr" in e and e["expr"] not in F.BIG) or "look" in e])
        bl, last = [], -9.0
        for m in marks:
            if m - last > 0.6:
                bl.append((m, "n"))
                last = m
        t = rng.uniform(0.6, 1.8)
        while t < shot_dur:
            if all(abs(t - b[0]) > 1.8 for b in bl):
                bl.append((t, "l" if self.spec.get("expr") in ("deadpan", "unimpressed") else "n"))
            t += rng.uniform(3.5, 5.5)
        self.blinks = sorted(bl)
        self.dart_seq = rng.uniform(-1, 1, size=(400, 2))
        self.flashes = []                                   # brow accents on 1-2 stressed words per sentence
        for ln in self.lines:
            lp, last = ln["lips"], -9.0
            for i in range(6, len(lp)):
                if lp[i][0] > 0.6 and max(x[0] for x in lp[i - 6:i]) < 0.15:
                    tt = ln["at"] + i / FPS
                    if tt - last > 1.4 and rng.uniform() < 0.7:
                        self.flashes.append(tt - 0.1)      # brows lead the sound by ~3 frames
                        last = tt

    @staticmethod
    def _take_k(f: float, big: bool) -> tuple[float, float, float]:
        """Blend factor prev->new expression at frame f after the change, plus eye squeeze and head dip.
        Big changes: anticipation (5 fr, slightly the other way) -> accent (3 fr, 125%) -> settle (9 fr)."""
        if not big:
            return ease(f / 6.0), 0.0, 0.0
        if f < 5:
            q = math.sin(f / 5 * math.pi / 2)
            return -0.18 * q, 0.3 * q, 0.02 * q
        if f < 8:
            q = ease((f - 5) / 3)
            return -0.18 + 1.43 * q, 0.3 * (1 - q), 0.02 * (1 - q)
        if f < 17:
            return 1.25 - 0.25 * ease((f - 8) / 9), 0.0, 0.0
        return 1.0, 0.0, 0.0

    def _emo_at(self, t: float) -> tuple[dict, dict]:
        cur = prev = self.spec.get("expr", "neutral")
        tc = -9.0
        for e in self.events:
            if e["t"] > t:
                break
            if "expr" in e:
                prev, cur, tc = cur, e["expr"], e["t"]
        f = (t - tc) * FPS
        k, squeeze, dip = self._take_k(f, cur in F.BIG and tc > -9) if tc > -9 else (1.0, 0.0, 0.0)
        emo = F.blend(F.emotion(prev), F.emotion(cur), k)
        for kk in ("open_l", "open_r", "pupil", "mw"):
            emo[kk] = max(0.05, emo[kk])
        if self.spec.get("emo_mod"):
            emo.update(self.spec["emo_mod"])
        return emo, {"cur": cur, "tc": tc, "squeeze": squeeze, "dip": dip}

    def state(self, t: float) -> dict:
        emo, info = self._emo_at(t)
        emo_brow, _ = self._emo_at(t + 0.1)                 # brows lead the face by ~3 frames
        look = list(self.spec.get("look", [0, 0]))
        look_set = "look" in self.spec
        jump_t, dart = None, self.spec.get("dart", False)
        grin = self.spec.get("grin", False)
        moves, roll, wiggle, shiver = [], None, 0.0, 0.0
        for e in self.events:
            if e["t"] > t:
                break
            if "look" in e:
                look, look_set = list(e["look"]), True
            if "jump" in e:
                jump_t = e["t"]
            if "grin" in e:
                grin = e["grin"]
            if "dart" in e:
                dart = e["dart"]
            d = e.get("dur", 0.6)
            if "move" in e and t < e["t"] + d:
                moves.append((e["move"], (t - e["t"]) / d))
            if "eyeroll" in e and t < e["t"] + d:
                roll = (t - e["t"]) / d
            if "wiggle" in e and t < e["t"] + d:
                wiggle = 1.0
            if "shiver" in e and t < e["t"] + d:
                shiver = 1.0
        if not look_set and info["cur"] in F.GAZE and (look == [0, 0] or look == [0.0, 0.0]):
            look = list(F.GAZE[info["cur"]])
        # nervous eyes dart: a new spot every ~7 frames, 3-frame move
        if dart or emo["darts"] > 0.3:
            fr = t * FPS
            n = int(fr // 7)
            q = min(1.0, (fr - n * 7) / 3)
            p0, p1 = self.dart_seq[n % 400], self.dart_seq[(n + 1) % 400]
            amt = 0.8 if dart else 0.55 * emo["darts"]
            look = [look[0] * 0.4 + amt * (p0[0] + (p1[0] - p0[0]) * q), look[1] * 0.4 + amt * 0.5 * (p0[1] + (p1[1] - p0[1]) * q)]
        # mouth from voice lines: the drawing leads the sound by 2 frames
        o, shape, talk = 0.0, "X", 0.0
        for ln in self.lines:
            i = int((t - ln["at"]) * FPS) + 1
            if 0 <= i < len(ln["lips"]):
                o, shape = ln["lips"][i]
                talk = 1.0
        # blinks: 3 close / 1 hold / 4 open frames (long: 4/2/5); none for angry stares or shock
        blink = 0.0
        if emo["blinks"] >= 0.5:
            for b, kind in self.blinks:
                c, h, op = (4, 2, 5) if kind == "l" else (3, 1, 4)
                f = (t - b) * FPS
                if 0 <= f < c:
                    blink = f / c
                elif c <= f < c + h:
                    blink = 1.0
                elif c + h <= f < c + h + op:
                    blink = 1 - (f - c - h) / op
        blink = max(blink, info["squeeze"])
        flash = 0.0
        for ft in self.flashes:
            f = (t - ft) * FPS
            if 0 <= f < 4:
                flash = 0.32 * ease(f / 4)
            elif 4 <= f < 14:
                flash = 0.32 * (1 - 0.3 * ease((f - 4) / 10)) * (1 - ease((f - 4) / 10))
        st_t = t - info["tc"] if info["tc"] > -9 else t
        sym = min(1.0, max(0.0, (st_t - 0.12) / 0.1)) * (1.0 if st_t < 1.6 else max(0.0, 1 - (st_t - 1.6) / 0.4))
        if info["tc"] <= -9:                                # a starting expression shows its symbol early on
            sym = 1.0 if t < 1.6 else max(0.0, 1 - (t - 1.6) / 0.4)
        return {"expr": emo, "emo": emo, "emo_brow": emo_brow, "mouth": (o, shape), "talk": talk, "blink": blink,
                "twitch": 0.0, "look": look, "jump": jump_t, "grin": grin, "t": t, "moves": moves, "eyeroll": roll,
                "brow_wiggle": wiggle, "shiver": shiver, "brow_flash": flash, "sym": sym, "sym_t": st_t,
                "tilt_sign": (1.0 if look[0] >= 0 else -1.0), "take_dip": info["dip"]}

    def render(self, canvas: np.ndarray, t: float) -> None:
        st = self.state(t)
        o = st["mouth"][0]
        sway = 1.2 * math.sin(2 * math.pi * 0.33 * t + self.phase)
        bob = 3.0 * math.sin(2 * math.pi * 0.5 * t + self.phase)
        rot = sway + st["talk"] * (2.2 * math.sin(2 * math.pi * 1.25 * t + self.phase) + 2.5 * o * math.sin(2 * math.pi * 2.1 * t))
        dy = bob - 12 * o * st["talk"]
        sq = 1 + 0.035 * o * st["talk"]
        if st["twitch"] > 0:
            rot += 1.5 * math.sin(t * 90)
        if st["jump"] is not None and st["jump"] <= t < st["jump"] + 0.35:
            p = (t - st["jump"]) / 0.35
            dy -= 40 * math.sin(p * math.pi) * self.face.s * 2
        rot += self.spec.get("tilt", 0)
        breath = 1 + 0.008 * math.sin(2 * math.pi * 0.28 * t + self.phase)
        head = self.head.copy()
        self.face.draw(head, st)
        if self.stache:
            simg, at = self.stache
            sh, sw = simg.shape[:2]
            lift = -o * sw * 0.04 + math.sin(t * 25) * sw * 0.01 * st["talk"]
            hx, hy = int(at[0] - sw / 2), int(at[1] - sh / 2 + lift)
            tmp = head[..., :3].astype(np.float32)
            paste(tmp, simg, hx, hy)
            head[..., :3] = tmp.astype(np.uint8)
        x, y = self.x, self.y + dy * 0.4
        if self.body is not None:
            bh, bw = self.body.shape[:2]
            body_layer, bx, by = affine_layer(self.body, (self.socket[0], self.socket[1]), 0, 1.0, breath, (x, y + dy * 0.3))
            sock = (x, y + dy * 0.3 - (breath - 1) * self.socket[1])
            hl, hx, hy = affine_layer(head, (self.neck[0], self.neck[1]), rot, 1 / sq ** 0.5, sq, (sock[0], sock[1] + dy * 0.7))
            if self.head_on_top:
                paste(canvas, body_layer, bx, by)
                paste(canvas, hl, hx, hy)
            else:
                paste(canvas, hl, hx, hy)
                paste(canvas, body_layer, bx, by)
        else:
            hl, hx, hy = affine_layer(head, (self.neck[0], self.neck[1]), rot * 0.5, 1 / sq ** 0.5, sq * breath, (x, y + dy))
            paste(canvas, hl, hx, hy)


# ----------------------------------------------------------------------------- whole-figure characters
def analyze_face(rgba: np.ndarray, region_frac: float = 1.0) -> dict:
    """Locate the blank face by skin colour: the face is the biggest skin blob near the top, enclosed by
    its outline, so its lowest row is the chin. Returns top, chin, cx (chin centre), face_w, neck_min."""
    a = rgba[..., 3] > 128
    ys, _ = np.nonzero(a)
    top, bottom = int(ys.min()), int(ys.max())
    lim = top + int((bottom - top) * region_frac)
    hsv = cv2.cvtColor(np.ascontiguousarray(rgba[:lim, :, :3]), cv2.COLOR_RGB2HSV)
    h, sat, v = hsv[..., 0], hsv[..., 1], hsv[..., 2]
    skin = ((h >= 3) & (h <= 17) & (sat >= 60) & (sat <= 215) & (v >= 120) & a[:lim]).astype(np.uint8)
    skin = cv2.morphologyEx(skin, cv2.MORPH_OPEN, np.ones((3, 3), np.uint8))
    n, lab, st, cen = cv2.connectedComponentsWithStats(skin, 8)
    if n <= 1:
        raise ValueError("no face found")
    best = 1 + int(np.argmax(st[1:, 4]))
    x0, y0, w0, h0, area = st[best]
    face = lab == best
    chin = int(y0 + h0 - 1)
    rows = np.nonzero(face[max(y0, chin - 6): chin + 1])[1]
    cx = float(rows.mean()) if len(rows) else float(cen[best][0])
    # top of the head: highest opaque pixel in the face's columns
    cols = a[:, x0:x0 + w0]
    head_top = int(np.nonzero(cols.any(1))[0].min())
    return {"top": head_top, "neck": chin, "neck_min": chin + int(0.06 * w0), "cx": cx, "ear_w": int(w0),
            "face_box": (int(x0), int(y0), int(w0), int(h0))}



def ear_masks(master: np.ndarray, chin: int) -> list:
    """Ear regions of a master head (float masks, master coords): skin blobs beside the face at eye level."""
    a = master[..., 3] > 128
    hsv = cv2.cvtColor(np.ascontiguousarray(master[..., :3]), cv2.COLOR_RGB2HSV)
    h, sat, v = hsv[..., 0], hsv[..., 1], hsv[..., 2]
    skin = ((h >= 3) & (h <= 17) & (sat >= 60) & (sat <= 215) & (v >= 80) & a).astype(np.uint8)
    skin[chin:] = 0
    n, lab, st, cen = cv2.connectedComponentsWithStats(skin, 8)
    if n <= 2:
        return []
    order = np.argsort(-st[1:, 4]) + 1
    face = order[0]
    fx, fy, fw, fh, fa = st[face]
    out = []
    for i in order[1:]:
        x, y, w, hh, area = st[i]
        cx, cy = cen[i]
        if area < 0.01 * fa or area > 0.25 * fa:
            continue
        if not (fy + 0.15 * fh < cy < fy + 0.85 * fh):
            continue
        if fx + 0.2 * fw < cx < fx + 0.8 * fw:
            continue
        m = (lab == i).astype(np.uint8)
        m = cv2.dilate(m, np.ones((5, 5), np.uint8))
        out.append(cv2.GaussianBlur(m.astype(np.float32), (0, 0), 2.0))
    if not out:   # ears drawn joined to the face: take the outer side bands of the face blob at ear height
        fm = (lab == face)
        for x0, x1 in ((fx, fx + int(0.13 * fw)), (fx + int(0.87 * fw), fx + fw)):
            m = np.zeros_like(skin)
            y0, y1 = fy + int(0.22 * fh), fy + int(0.62 * fh)
            m[y0:y1, x0:x1] = fm[y0:y1, x0:x1]
            if m.sum() > 0.005 * fa:
                out.append(cv2.GaussianBlur(m.astype(np.float32), (0, 0), 3.0))
    return out[:2]


_ALIGN_CACHE: dict = {}


def figure_alignment(parts_dir: Path, master_file: str, chin: int, fig_file: str) -> tuple[float, float, float]:
    """master head -> figure mapping (scale, tx, ty), cached on disk next to the parts."""
    cache_path = parts_dir / "align_cache.json"
    if not _ALIGN_CACHE and cache_path.exists():
        _ALIGN_CACHE.update(json.loads(cache_path.read_text()))
    key = f"{master_file}|{chin}|{fig_file}|{(parts_dir / fig_file).stat().st_size}"
    if key not in _ALIGN_CACHE:
        from align import align
        s, tx, ty, score = align(load_rgba(parts_dir / master_file), load_rgba(parts_dir / fig_file), chin)
        _ALIGN_CACHE[key] = [s, tx, ty, score]
        cache_path.write_text(json.dumps(_ALIGN_CACHE, indent=1))
    s, tx, ty, _ = _ALIGN_CACHE[key]
    return s, tx, ty


class FigureActor(Actor):
    """A character drawn as one whole pose drawing. The head is never cut off or replaced.

    - The face (eyes, brows, mouth, moustache) is drawn by code at positions taken from the character's
      master head, mapped onto the drawing, so expressions look identical in every pose and every video.
    - Head motion is a smooth bend: pixels of the head rotate a little about the base of the neck, with
      the effect fading to zero at the collar. No seam is possible.
    - Every pose of a character is scaled so its head is the same size; characters are scaled to their
      real relative heights.
    """

    def __init__(self, rig: dict, parts_dir: Path, a: dict, shot_dur: float):
        self.spec = a
        self.who = a["who"]
        ch = rig["characters"][self.who]
        hspec = rig["heads"][ch["primary_head"]]
        mfile, mchin = hspec["file"], int(ch["chin"])
        master = load_rgba(parts_dir / mfile)
        # one on-screen scale for this character: size = on-screen height (px) of a 1.0-tall character
        sfig = rig["figures"][ch["stand_pose"]]
        stand = load_rgba(parts_dir / sfig["file"])
        ys = np.nonzero(stand[..., 3].max(1) > 128)[0]
        s_stand = figure_alignment(parts_dir, mfile, mchin, sfig.get("align_as_file", sfig["file"]))[0]
        head_k = float(a["size"]) * float(ch.get("height", 1.0)) / (ys.max() - ys.min()) * s_stand  # master px -> screen px
        mmask = (master[..., 3] > 128).astype(np.uint8)
        mmask[mchin:] = 0
        mx0, my0, mw0, mh0 = analyze_face(master)["face_box"]
        self.poses = {}
        for pk in set([a["pose"]] + [e["pose"] for e in a.get("events", []) if "pose" in e]):
            fspec = rig["figures"][pk]
            fig = load_rgba(parts_dir / fspec["file"])
            s, tx, ty = figure_alignment(parts_dir, mfile, mchin, fspec.get("align_as_file", fspec["file"]))
            fk = head_k / s                      # figure px -> screen px
            img = cv2.resize(fig, None, fx=fk, fy=fk, interpolation=cv2.INTER_AREA if fk < 1 else cv2.INTER_CUBIC)
            k = s * fk                           # master px -> screen px
            ox, oy = tx * fk, ty * fk
            # transparent margin above/beside the drawing so a moving head never runs off the image edge
            pad = int(0.45 * mw0 * k) + 8
            img = np.pad(img, ((pad, 0), (pad, pad), (0, 0)))
            ox, oy = ox + pad, oy + pad
            feat = fspec.get("feat", {})
            fdx, fdy, fks = feat.get("dx", 0.0) * k, feat.get("dy", 0.0) * k, feat.get("k", 1.0)
            to = lambda p: [p[0] * k + ox + fdx, p[1] * k + oy + fdy]
            # skin colour sampled from the drawing at the master's skin point
            sx, sy = [int(v) for v in to(hspec["skin_at"])]
            patch = img[max(0, sy - 4):sy + 5, max(0, sx - 4):sx + 5, :3].reshape(-1, 3)
            skin = tuple(int(v) for v in np.median(patch, 0))
            for x, y, rx, ry in fspec.get("paint", []):
                cv2.ellipse(img, (int(x * fk) + pad, int(y * fk) + pad), (int(rx * fk), int(ry * fk)), 0, 0, 360, (*skin, 255), -1, cv2.LINE_AA)
            cx_chin = (mx0 + mw0 / 2) * k + ox
            chin_y = mchin * k + oy
            fw = mw0 * k
            # head weight map: master silhouette mapped onto the figure, extended down the neck, soft edges
            Wm = cv2.warpAffine(mmask * 255, np.float32([[k, 0, ox + fdx * 0], [0, k, oy]]), (img.shape[1], img.shape[0]))
            Wm = np.maximum(Wm, 0)
            neck = np.zeros_like(Wm)
            x0n, x1n = int(cx_chin - 0.42 * fw), int(cx_chin + 0.42 * fw)
            neck[max(0, int(chin_y - fw * 0.3)):int(chin_y + fw * 0.6), max(0, x0n):x1n] = 255
            Wm = np.maximum(Wm, neck)
            # the whole drawn head (hair, crown, ears) must move together: add the figure's own pixels
            # inside the head's band, so nothing above the mapped master silhouette stays behind
            hy, hx = np.nonzero(Wm > 0)
            if len(hy):
                y_top = int(max(0, hy.min() - 0.45 * fw))
                xa, xb = int(max(0, hx.min() - 0.08 * fw)), int(min(img.shape[1], hx.max() + 0.08 * fw))
                band = np.zeros_like(Wm)
                band[y_top:int(chin_y), xa:xb] = (img[y_top:int(chin_y), xa:xb, 3] > 40).astype(np.uint8) * 255
                Wm = np.maximum(Wm, band)
            d = max(3, int(0.16 * fw)) | 1
            Wm = cv2.dilate(Wm, np.ones((d, d), np.uint8))
            Wm = cv2.GaussianBlur(Wm.astype(np.float32) / 255.0, (0, 0), max(1.0, 0.04 * fw))
            yy = np.arange(img.shape[0], dtype=np.float32)[:, None]
            v = np.clip((chin_y + 0.30 * fw - yy) / (0.22 * fw), 0, 1)       # whole face rigid; only the neck bends
            v = v * v * (3 - 2 * v)
            Wm = Wm * v
            nz = np.nonzero(Wm > 0.002)
            mg = int(0.3 * fw) + 4                # room inside the region for the head to move into
            r0, r1 = max(0, nz[0].min() - mg), min(img.shape[0], nz[0].max() + 5)
            c0, c1 = max(0, nz[1].min() - mg), min(img.shape[1], nz[1].max() + mg)
            fs = dict(hspec)
            fs["eyes"] = [[p[0] - c0, p[1] - r0] for p in map(to, hspec["eyes"])]
            fs["eye_r"] = hspec["eye_r"] * k * fks
            m = to(hspec["mouth"])
            fs["mouth"] = [m[0] - c0, m[1] - r0]
            fs["mouth_w"] = hspec["mouth_w"] * k * fks
            if feat.get("eyes"):
                fs["eyes"] = [[(p[0] * k + ox) - c0, (p[1] * k + oy) - r0] for p in feat["eyes"]]
            if feat.get("mouth"):
                fs["mouth"] = [feat["mouth"][0] * k + ox - c0, feat["mouth"][1] * k + oy - r0]
            stache = None
            if hspec.get("stache"):
                st = hspec["stache"]
                simg = load_rgba(parts_dir / st["file"])
                sk = st["width"] * k * fks / simg.shape[1]
                at = to(st["at"])
                stache = (cv2.resize(simg, None, fx=sk, fy=sk, interpolation=cv2.INTER_AREA), np.array([at[0] - c0, at[1] - r0], np.float32))
            fs["ears"] = [{"mask": cv2.warpAffine(em, np.float32([[k, 0, ox], [0, k, oy]]), (img.shape[1], img.shape[0]))[r0:r1, c0:c1]}
                          for em in ear_masks(master, mchin)]
            self.poses[pk] = {"img": img, "roi": (r0, r1, c0, c1), "W": Wm[r0:r1, c0:c1].copy(),
                              "pivot": np.array([cx_chin - c0, chin_y + 0.06 * fw - r0], np.float32),
                              "face": F.Face(fs, 1.0, skin), "stache": stache, "chin": np.array([cx_chin, chin_y], np.float32),
                              "fw": fw}
            self.poses[pk]["grid"] = np.mgrid[0:r1 - r0, 0:c1 - c0].astype(np.float32)
        self.pose = a["pose"]
        self.x = a["x"]
        self.floor = a.get("floor")
        self.neck_y = a.get("neck_y")
        self.lines = a.get("lines", [])
        self._plan_timing(a, shot_dur)

    def geometry(self, pose: str | None = None) -> dict:
        """Where this figure lands on the canvas (no motion): chin point, face width, silhouette box."""
        P = self.poses[pose or self.spec["pose"]]
        bh, bw = P["img"].shape[:2]
        cx, cy = float(P["chin"][0]), float(P["chin"][1])
        if self.floor is not None:
            left, top = self.x - cx, self.floor - bh
        else:
            left, top = self.x - cx, self.neck_y - cy
        a = P["img"][..., 3] > 128
        ys, xs = np.nonzero(a.any(1))[0], np.nonzero(a.any(0))[0]
        return {"chin": (left + cx, top + cy), "fw": float(P["fw"]),
                "box": (left + xs.min(), top + ys.min(), left + xs.max(), top + ys.max())}

    def render(self, canvas: np.ndarray, t: float) -> None:
        st = self.state(t)
        pose, t_pose = self.spec["pose"], -9.0
        for e in self.events:
            if e["t"] > t:
                break
            if "pose" in e:
                pose, t_pose = e["pose"], e["t"]
        P = self.poses[pose]
        o = st["mouth"][0]
        rot = 0.4 * math.sin(2 * math.pi * 0.25 * t + self.phase)       # breathing-level idle, no bobbing
        rot += self.spec.get("tilt", 0)
        nod = -0.018 * P["fw"] * o * st["talk"] + 0.035 * P["fw"] * st["brow_flash"] / 0.32  # small nod on accents
        mv = F.motion(st["emo"], st, t)
        rot += mv["rot"]
        nod += mv["dy"] * P["fw"]
        shx = mv["dx"] * P["fw"]
        # face drawn on the head region, then the head region is bent softly about the neck
        r0, r1, c0, c1 = P["roi"]
        img = P["img"].copy()
        roi = img[r0:r1, c0:c1].copy()
        P["face"].draw(roi, st)
        if P["stache"]:
            simg, at = P["stache"]
            sh, sw = simg.shape[:2]
            lift = -o * sw * 0.04 + math.sin(t * 25) * sw * 0.01 * st["talk"]
            tmp = roi[..., :3].astype(np.float32)
            paste(tmp, simg, int(at[0] - sw / 2), int(at[1] - sh / 2 + lift))
            roi[..., :3] = tmp.astype(np.uint8)
        th = math.radians(rot) * P["W"]
        gy, gx = P["grid"]
        px, py = P["pivot"]
        c, s = np.cos(th), np.sin(th)
        dx, dy = gx - px, gy - py
        mapx = px + c * dx - s * dy - shx * P["W"]
        mapy = py + s * dx + c * dy - nod * P["W"]
        roi = cv2.remap(roi, mapx.astype(np.float32), mapy.astype(np.float32), cv2.INTER_LINEAR,
                        borderMode=cv2.BORDER_CONSTANT, borderValue=(0, 0, 0, 0))
        img[r0:r1, c0:c1] = roi
        breath = 1 + 0.006 * math.sin(2 * math.pi * 0.28 * t + self.phase)
        pop = 1.0
        if 0 <= t - t_pose < 0.14:  # pose change: tiny squash-and-settle
            pop = 1 - 0.015 * math.sin((t - t_pose) / 0.14 * math.pi)
        jump = 0.0
        if st["jump"] is not None and st["jump"] <= t < st["jump"] + 0.35:
            jump = -0.4 * P["fw"] * math.sin((t - st["jump"]) / 0.35 * math.pi)
        bh, bw = img.shape[:2]
        if self.floor is not None:
            foot = (self.x - P["chin"][0] + bw / 2, self.floor)
            pivot = (bw / 2, bh)
        else:
            foot = (self.x, self.neck_y)
            pivot = (P["chin"][0], P["chin"][1])
        sy = breath * pop
        layer, bx, by = affine_layer(img, pivot, 0, 1 / pop ** 0.5, sy, (foot[0], foot[1] + jump))
        paste(canvas, layer, bx, by)


# ----------------------------------------------------------------------------- backgrounds & fx
_SPIRAL = {}


def spiral_bg(t: float) -> np.ndarray:
    if "theta" not in _SPIRAL:
        yy, xx = np.mgrid[0:H // 2, 0:W // 2].astype(np.float32)
        cx, cy = W / 4, H / 4.6
        _SPIRAL["theta"] = np.arctan2(yy - cy, xx - cx)
        _SPIRAL["rad"] = np.sqrt((xx - cx) ** 2 + (yy - cy) ** 2) / (H / 2)
    th, rd = _SPIRAL["theta"], _SPIRAL["rad"]
    stripes = ((th / (2 * math.pi) * 12 + rd * 3.5 - t * 1.6) % 1.0) < 0.5
    pulse = 0.75 + 0.25 * math.sin(t * 2 * math.pi * 2.2)
    red = np.array([150, 20, 35], np.float32) * pulse
    dark = np.array([30, 10, 40], np.float32)
    img = np.where(stripes[..., None], red, dark)
    blue = np.clip(1 - rd * 1.6, 0, 1)[..., None] * np.array([20, 40, 120], np.float32) * (1 - pulse + 0.3)
    img = img + blue
    return cv2.resize(img.astype(np.float32), (W, H), interpolation=cv2.INTER_LINEAR)


def load_bg(path: Path, zoom: float, cx: float, cy: float, blur: float) -> np.ndarray:
    im = cv2.cvtColor(cv2.imread(str(path)), cv2.COLOR_BGR2RGB)
    k = max(W / im.shape[1], H / im.shape[0]) * zoom
    im = cv2.resize(im, None, fx=k, fy=k, interpolation=cv2.INTER_AREA if k < 1 else cv2.INTER_CUBIC)
    x0 = int(min(max(0, cx * im.shape[1] - W / 2), im.shape[1] - W))
    y0 = int(min(max(0, cy * im.shape[0] - H / 2), im.shape[0] - H))
    im = im[y0:y0 + H, x0:x0 + W]
    if blur > 0:
        im = cv2.GaussianBlur(im, (0, 0), blur)
    return im.astype(np.float32)


def speed_lines(canvas: np.ndarray, t: float, strength: float) -> None:
    rng = np.random.default_rng(int(t * FPS))
    cx, cy = W / 2, H * 0.42
    for _ in range(int(60 * strength)):
        a = rng.uniform(0, 2 * math.pi)
        r0 = rng.uniform(0.45, 0.6) * H
        r1 = r0 + rng.uniform(0.15, 0.35) * H
        p0 = (int(cx + math.cos(a) * r0), int(cy + math.sin(a) * r0 * 0.9))
        p1 = (int(cx + math.cos(a) * r1), int(cy + math.sin(a) * r1 * 0.9))
        cv2.line(canvas, p0, p1, (20, 15, 15), int(rng.integers(3, 9)), cv2.LINE_AA)


def sweat(canvas: np.ndarray, x: float, y: float, size: float, p: float) -> None:
    yy = y + p * size * 3
    pts = np.array([[x, yy - size], [x + size * 0.55, yy + size * 0.2], [x, yy + size * 0.65], [x - size * 0.55, yy + size * 0.2]], np.int32)
    cv2.fillPoly(canvas, [pts], (140, 200, 255), cv2.LINE_AA)
    cv2.circle(canvas, (int(x), int(yy + size * 0.15)), int(size * 0.55), (140, 200, 255), -1, cv2.LINE_AA)
    cv2.circle(canvas, (int(x), int(yy + size * 0.15)), int(size * 0.55), (40, 60, 90), max(2, int(size * 0.08)), cv2.LINE_AA)
    cv2.circle(canvas, (int(x - size * 0.15), int(yy)), max(2, int(size * 0.12)), (255, 255, 255), -1, cv2.LINE_AA)


def camera(frame: np.ndarray, zoom: float, cx: float, cy: float, shake=(0.0, 0.0)) -> np.ndarray:
    if abs(zoom - 1) < 1e-3 and shake == (0.0, 0.0):
        return frame
    zoom = max(1.0, zoom)
    cx = min(max(cx, W / (2 * zoom)), W - W / (2 * zoom))
    cy = min(max(cy, H / (2 * zoom)), H - H / (2 * zoom))
    if zoom > 1.0 or shake != (0.0, 0.0):
        zoom = max(zoom, 1.0 + (abs(shake[0]) + abs(shake[1])) / W)  # keep shaken edges inside the frame
    M = np.array([[zoom, 0, W / 2 - zoom * cx + shake[0]], [0, zoom, H / 2 - zoom * cy + shake[1]]], np.float32)
    return cv2.warpAffine(frame, M, (W, H), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_REFLECT)


# ----------------------------------------------------------------------------- shots
def render_shot(rig: dict, parts_dir: Path, shot: dict, lips: dict, out: Path) -> float:
    dur = float(shot["dur"])
    n = int(round(dur * FPS))
    bgname = shot.get("bg", "black")
    bg_static = None
    if bgname not in ("black", "spiral", "white"):
        b = shot.get("bg_view", {})
        bg_static = load_bg(parts_dir / rig["backgrounds"][bgname], b.get("zoom", 1.0), b.get("cx", 0.5), b.get("cy", 0.5), b.get("blur", 0))
    actors = []
    for a in shot.get("actors", []):
        a = dict(a)
        a["lines"] = [{"lips": lips[ln["line"]], "at": ln["at"]} for ln in a.get("lines", [])]
        actors.append((FigureActor if "pose" in a else Actor)(rig, parts_dir, a, dur))
    cam0 = shot.get("cam", {"zoom": 1.0, "cx": W / 2, "cy": H / 2})
    fx = sorted(shot.get("fx", []), key=lambda e: e["t"])
    proc = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}",
                             "-r", str(FPS), "-i", "-", "-c:v", "libx264", "-preset", "veryfast", "-crf", "18",
                             "-pix_fmt", "yuv420p", str(out)], stdin=subprocess.PIPE)
    for f in range(n):
        t = f / FPS
        if bgname == "spiral":
            canvas = spiral_bg(t)
        elif bgname == "black":
            canvas = np.zeros((H, W, 3), np.float32)
        elif bgname == "white":
            canvas = np.full((H, W, 3), 255, np.float32)
        else:
            canvas = bg_static.copy()
        for a in actors:
            a.render(canvas, t)
        zoom, cx, cy = cam0["zoom"], cam0["cx"], cam0["cy"]
        shake = (0.0, 0.0)
        flash, lines_s = 0.0, 0.0
        for e in fx:
            if e["t"] > t:
                continue
            if "cam" in e:
                c = e["cam"]
                k = ease((t - e["t"]) / e.get("over", 0.0)) if e.get("over", 0) > 0 else 1.0
                zoom, cx, cy = zoom + (c["zoom"] - zoom) * k, cx + (c.get("cx", cx) - cx) * k, cy + (c.get("cy", cy) - cy) * k
            if "shake" in e and t < e["t"] + e["shake"]:
                amp = e.get("amp", 18) * (1 - (t - e["t"]) / e["shake"])
                shake = (amp * math.sin(t * 61), amp * math.cos(t * 47))
            if "flash" in e and t < e["t"] + e["flash"]:
                flash = 1 - (t - e["t"]) / e["flash"]
            if "speedlines" in e and t < e["t"] + e["speedlines"]:
                lines_s = 1.0
            if "sweat" in e and t < e["t"] + e.get("dur", 1.2):
                p = (t - e["t"]) / e.get("dur", 1.2)
                sweat(canvas, e["x"], e["y"], e.get("size", 40), p)
        if lines_s:
            speed_lines(canvas, t, lines_s)
        frame = camera(np.clip(canvas, 0, 255), zoom, cx, cy, shake)
        if flash > 0:
            frame = frame * (1 - flash) + 255 * flash
        proc.stdin.write(np.clip(frame, 0, 255).astype(np.uint8).tobytes())
    proc.stdin.close()
    proc.wait()
    return dur


def main() -> int:
    rig_path, scene_path, out_dir = sys.argv[1:4]
    only = set(sys.argv[4].split(",")) if len(sys.argv) > 4 else None
    rig = json.loads(Path(rig_path).read_text())
    scene = json.loads(Path(scene_path).read_text())
    parts_dir = Path(rig_path).parent / rig.get("parts_dir", ".")
    lines_dir = Path(scene_path).parent / scene.get("lines_dir", ".")
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    lips = {name: lipsync(lines_dir / f"{name}.wav") for name in scene["lines"]}
    durs = []
    for i, shot in enumerate(scene["shots"]):
        if only and str(i) not in only:
            durs.append(float(shot["dur"]))
            continue
        d = render_shot(rig, parts_dir, shot, lips, out / f"shot{i:02d}.mp4")
        durs.append(d)
        print(f"shot {i}: {d:.2f}s", flush=True)
    (out / "timeline.json").write_text(json.dumps({"durs": durs}))
    return 0


if __name__ == "__main__":
    sys.exit(main())
