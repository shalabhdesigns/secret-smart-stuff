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


def lipsync(path: Path) -> list[tuple[float, str]]:
    """Per video frame: (openness 0..1, mouth shape). Shapes: X closed, A wide, E teeth, O round, U small."""
    x, sr = read_wav(path)
    hop = sr // FPS
    win = int(sr * 0.045)
    frames = []
    for i in range(0, max(1, len(x) // hop)):
        seg = x[max(0, i * hop - win // 2): i * hop + win // 2]
        if len(seg) < 32:
            frames.append((0.0, 0.0, 0.0))
            continue
        rms = float(np.sqrt((seg ** 2).mean()) + 1e-9)
        spec = np.abs(np.fft.rfft(seg * np.hanning(len(seg))))
        freqs = np.fft.rfftfreq(len(seg), 1 / sr)
        cen = float((spec * freqs).sum() / (spec.sum() + 1e-9))
        zcr = float(np.mean(np.abs(np.diff(np.sign(seg)))) / 2)
        frames.append((rms, cen, zcr))
    rms = np.array([f[0] for f in frames])
    db = 20 * np.log10(rms + 1e-9)
    peak = np.percentile(db, 97) if len(db) else -20
    open_ = np.clip((db - (peak - 28)) / 22, 0, 1)
    # attack fast, release a little slower -> natural chatter
    sm = np.zeros_like(open_)
    for i, v in enumerate(open_):
        prev = sm[i - 1] if i else 0
        sm[i] = prev + (v - prev) * (0.85 if v > prev else 0.55)
    out = []
    last, hold = "X", 0
    for i, (o, (r, cen, zcr)) in enumerate(zip(sm, frames)):
        if o < 0.12:
            shape = "X"
        elif zcr > 0.18 and o < 0.55:
            shape = "E"
        elif cen < 900 and o > 0.25:
            shape = "O"
        elif o < 0.3:
            shape = "U"
        else:
            shape = "A"
        if shape != last and hold < 2 and shape != "X":
            shape = last
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
        self.phase = (sum(map(ord, self.who)) % 100) / 17.0
        self.events = sorted(a.get("events", []), key=lambda e: e["t"])
        rng = np.random.default_rng(sum(map(ord, self.who)) * 7919 + int(a.get("seed", 0)))
        self.blinks = []
        t = rng.uniform(0.4, 1.6)
        while t < shot_dur:
            self.blinks.append(t)
            t += rng.uniform(1.8, 3.8)
        self.darts = rng.uniform(-1, 1, size=(400, 2))

    def state(self, t: float) -> dict:
        expr_name, prev_name, t_change = self.spec.get("expr", "neutral"), self.spec.get("expr", "neutral"), -9.0
        look = list(self.spec.get("look", [0, 0]))
        twitch_t, twitch_d, jump_t, dart = None, 0.0, None, self.spec.get("dart", False)
        grin = self.spec.get("grin", False)
        for e in self.events:
            if e["t"] > t:
                break
            if "expr" in e:
                prev_name, expr_name, t_change = expr_name, e["expr"], e["t"]
            if "look" in e:
                look = e["look"]
            if "twitch" in e:
                twitch_t, twitch_d = e["t"], e.get("dur", 0.7)
            if "jump" in e:
                jump_t = e["t"]
            if "grin" in e:
                grin = e["grin"]
            if "dart" in e:
                dart = e["dart"]
        k = ease((t - t_change) / 0.18)
        expr = blend_expr(EXPR[prev_name], EXPR[expr_name], k)
        # mouth from voice lines
        o, shape, talk = 0.0, "X", 0.0
        for ln in self.lines:
            i = int((t - ln["at"]) * FPS)
            if 0 <= i < len(ln["lips"]):
                o, shape = ln["lips"][i]
                talk = 1.0
        blink = 0.0
        for b in self.blinks:
            if b <= t < b + 0.14:
                blink = math.sin((t - b) / 0.14 * math.pi)
        twitch = 0.0
        if twitch_t is not None and twitch_t <= t < twitch_t + twitch_d:
            twitch = 0.55 + 0.45 * abs(math.sin((t - twitch_t) * 2 * math.pi * 7))
        if dart:
            d = self.darts[int(t * 4) % len(self.darts)]
            look = [float(d[0]), float(d[1]) * 0.5]
        return {"expr": expr, "mouth": (o, shape), "talk": talk, "blink": blink, "twitch": twitch,
                "look": look, "jump": jump_t, "grin": grin}

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


# ----------------------------------------------------------------------------- locked heads on full-body poses
def central_widths(alpha: np.ndarray, cx: int) -> np.ndarray:
    """Width of the opaque run through column cx, per row (0 where cx is transparent)."""
    a = alpha > 128
    w = np.zeros(a.shape[0], np.int32)
    for y in range(a.shape[0]):
        row = a[y]
        if not row[cx]:
            continue
        l = cx
        while l > 0 and row[l - 1]:
            l -= 1
        r = cx
        while r < len(row) - 1 and row[r + 1]:
            r += 1
        w[y] = r - l + 1
    return w


def analyze_head(rgba: np.ndarray, search_frac: float = 0.5) -> dict:
    """Find the head in an image: top, neck_top (just under the chin), centre x and ear-level width."""
    a = rgba[..., 3] > 128
    ys, xs = np.nonzero(a)
    top = int(ys.min())
    band = a[top: top + max(8, int((ys.max() - top) * 0.12))].astype(np.uint8)
    nb, lb, sb, cb = cv2.connectedComponentsWithStats(band, 8)
    big = 1 + int(np.argmax(sb[1:, 4]))  # the head is the biggest blob at the top (not a raised hand)
    cx = int(cb[big][0])
    top = top + int(sb[big][1])
    w = central_widths(rgba[..., 3], cx)
    lim = top + int((ys.max() - top) * search_frac)
    ymax = top + int(np.argmax(w[top:lim]))
    maxw = int(w[ymax])
    bottom = int(ys.max())
    win_end = min(bottom - int((bottom - top) * 0.04), ymax + int((ymax - top) * 1.3) + 2)  # skip the neck's end cap
    seg = w[ymax:win_end].astype(np.float32)
    seg[seg == 0] = 1e9
    mn = float(seg.min())
    near = np.nonzero(seg <= mn * 1.08 + 2)[0]
    neck = ymax + int(near[0])  # first row that reaches the neck's width = just under the chin
    neck_min = ymax + int(np.argmin(seg))
    span = neck - top
    lo, hi = top + int(span * 0.45), top + int(span * 0.95)
    ear_w = int(w[lo:hi].max()) if hi > lo else maxw
    row = a[neck]
    l = cx
    while l > 0 and row[l - 1]:
        l -= 1
    r = cx
    while r < len(row) - 1 and row[r + 1]:
        r += 1
    return {"top": top, "neck": neck, "neck_min": max(neck, neck_min), "cx": (l + r) / 2, "ear_w": ear_w}


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


def erase_head(rgba: np.ndarray, info: dict) -> np.ndarray:
    """Remove the drawn head: only skin / hair / outline-coloured pixels above the chin that are connected
    to the face. Clothing (collars, hoods, capes, shirts) and the chair are never touched."""
    out = rgba.copy()
    cut = info["neck"] + 3
    reg = out[:cut]
    hsv = cv2.cvtColor(np.ascontiguousarray(reg[..., :3]), cv2.COLOR_RGB2HSV)
    h, sat, v = hsv[..., 0].astype(int), hsv[..., 1].astype(int), hsv[..., 2].astype(int)
    alpha = reg[..., 3] > 20
    skin = (h >= 3) & (h <= 17) & (sat >= 60) & (sat <= 215) & (v >= 120)
    dark = v < 95                                     # black hair and the outline
    grey = (sat < 45) & (v >= 95) & (v <= 205)        # grey temples
    teal = (h >= 78) & (h <= 100) & (sat > 70)        # Meera's streak
    cand = alpha & (skin | dark | grey | teal)
    cols = np.abs(np.arange(out.shape[1]) - info["cx"]) <= 0.8 * info["ear_w"]
    cand &= cols[None, :]
    n, lab = cv2.connectedComponents(cand.astype(np.uint8), 8)
    x0, y0, w0, h0 = info["face_box"]
    fy, fx = y0 + h0 // 2, x0 + w0 // 2
    keep = set()
    if lab[fy, fx] > 0:
        keep.add(lab[fy, fx])
    top_rows = lab[info["top"]: info["top"] + max(3, (cut - info["top"]) // 6)]
    keep.update(int(k) for k in np.unique(top_rows) if k > 0)
    m = np.isin(lab, list(keep))
    m = cv2.dilate(m.astype(np.uint8), np.ones((3, 3), np.uint8)).astype(bool) & cand  # tidy anti-aliased edges
    reg[..., 3] = np.where(m, 0, reg[..., 3])
    # halo: faint anti-aliased leftovers of the drawn head's outline just around what was removed
    ring = cv2.dilate(m.astype(np.uint8), np.ones((9, 9), np.uint8)).astype(bool) & ~m
    faint = ring & (reg[..., 3] < 250) & (cand | (reg[..., 3] < 160))
    reg[..., 3] = np.where(faint, 0, reg[..., 3])
    return out


class FigureActor(Actor):
    """A full-body pose drawing with the character's locked head placed on it.

    Proportions come from the pose drawing; the face/hair are always the same head file, so the
    character can never drift. Poses can be swapped mid-shot (pose events) for gestures.
    """

    def __init__(self, rig: dict, parts_dir: Path, a: dict, shot_dur: float):
        self.spec = a
        self.who = a["who"]
        ch = rig["characters"][self.who]
        head_key = a.get("head", ch["primary_head"])
        size = float(a["size"]) * ch.get("face_scale", 1.0)  # on-screen face width, px (Dev-equivalent)
        prim_spec = rig["heads"][ch["primary_head"]]
        prim = load_rgba(parts_dir / prim_spec["file"])
        pinfo = analyze_face(prim)
        hk = size / pinfo["ear_w"]
        head = rig["heads"][head_key]
        himg = load_rgba(parts_dir / head["file"])
        hinfo = analyze_face(himg)
        head_h = (pinfo["neck"] - pinfo["top"]) * hk  # on-screen head height, top of hair to chin
        fig_infos = {}
        for pk in set([a["pose"]] + [e["pose"] for e in a.get("events", []) if "pose" in e]):
            fig = load_rgba(parts_dir / rig["figures"][pk]["file"])
            fi = analyze_face(fig, 0.35)
            fi.update({k: v for k, v in rig["figures"][pk].items() if k in ("neck", "neck_min", "cx", "ear_w", "top")})
            fig_infos[pk] = (fig, fi)
        gap = max(((fi["neck_min"] - fi["neck"]) / (fi["neck"] - fi["top"]) * (pinfo["neck"] - pinfo["top"]) / pinfo["ear_w"])
                  for _, fi in fig_infos.values())
        cut = min(himg.shape[0], hinfo["neck"] + int(0.025 * hinfo["ear_w"]) + 3)  # keep the chin outline only
        himg = himg[:cut].copy()
        self.head = cv2.resize(himg, None, fx=hk, fy=hk, interpolation=cv2.INTER_AREA if hk < 1 else cv2.INTER_CUBIC)
        self.neck = np.array([hinfo["cx"], hinfo["neck"]], np.float32) * hk
        sk = head.get("skin_at")
        skin = tuple(int(v) for v in load_rgba(parts_dir / head["file"])[sk[1], sk[0], :3]) if sk else (200, 120, 85)
        self.face = Face(head, hk, skin)
        self.stache = None
        if head.get("stache"):
            st = head["stache"]
            simg = load_rgba(parts_dir / st["file"])
            k = st["width"] * hk / simg.shape[1]
            self.stache = (cv2.resize(simg, None, fx=k, fy=k, interpolation=cv2.INTER_AREA), np.array(st["at"], np.float32) * hk)
        # poses
        self.poses = {}
        for pk, (fig, finfo) in fig_infos.items():
            body = erase_head(fig, finfo)
            fk = hk * pinfo["ear_w"] / finfo["ear_w"]  # pose scaled so its face matches the master face width
            body = cv2.resize(body, None, fx=fk, fy=fk, interpolation=cv2.INTER_AREA if fk < 1 else cv2.INTER_CUBIC)
            self.poses[pk] = {"img": body, "neck": np.array([finfo["cx"], finfo["neck"]], np.float32) * fk}
        self.pose = a["pose"]
        self.x = a["x"]
        self.floor = a.get("floor")
        self.neck_y = a.get("neck_y")
        self.lines = a.get("lines", [])
        self.phase = (sum(map(ord, self.who)) % 100) / 17.0
        self.events = sorted(a.get("events", []), key=lambda e: e["t"])
        rng = np.random.default_rng(sum(map(ord, self.who)) * 7919 + int(a.get("seed", 0)))
        self.blinks = []
        t = rng.uniform(0.4, 1.6)
        while t < shot_dur:
            self.blinks.append(t)
            t += rng.uniform(1.8, 3.8)
        self.darts = rng.uniform(-1, 1, size=(400, 2))

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
        sway = 1.0 * math.sin(2 * math.pi * 0.33 * t + self.phase)
        rot = sway + st["talk"] * (2.0 * math.sin(2 * math.pi * 1.25 * t + self.phase) + 2.2 * o * math.sin(2 * math.pi * 2.1 * t))
        hdy = -0.02 * self.head.shape[0] * o * st["talk"]
        if st["twitch"] > 0:
            rot += 1.5 * math.sin(t * 90)
        rot += self.spec.get("tilt", 0)
        breath = 1 + 0.006 * math.sin(2 * math.pi * 0.28 * t + self.phase)
        pop = 1.0
        if 0 <= t - t_pose < 0.14:  # pose change: tiny squash-and-settle
            pop = 1 - 0.05 * math.sin((t - t_pose) / 0.14 * math.pi)
        jump = 0.0
        if st["jump"] is not None and st["jump"] <= t < st["jump"] + 0.35:
            jump = -0.25 * self.head.shape[1] * math.sin((t - st["jump"]) / 0.35 * math.pi)
        img = P["img"]
        bh, bw = img.shape[:2]
        if self.floor is not None:
            foot = (self.x - P["neck"][0] + bw / 2, self.floor)  # bottom-centre of the drawing on the floor
            pivot = (bw / 2, bh)
        else:
            foot = (self.x, self.neck_y)
            pivot = (P["neck"][0], P["neck"][1])
        sy = breath * pop
        body_layer, bx, by = affine_layer(img, pivot, 0, 1 / pop ** 0.5, sy, (foot[0], foot[1] + jump))
        # where the neck ended up after the body transform
        nx = foot[0] + (P["neck"][0] - pivot[0]) / pop ** 0.5
        ny = foot[1] + jump + (P["neck"][1] - pivot[1]) * sy
        head = self.head.copy()
        self.face.draw(head, st)
        if self.stache:
            simg, at = self.stache
            sh, sw = simg.shape[:2]
            lift = -o * sw * 0.04 + math.sin(t * 25) * sw * 0.01 * st["talk"]
            tmp = head[..., :3].astype(np.float32)
            paste(tmp, simg, int(at[0] - sw / 2), int(at[1] - sh / 2 + lift))
            head[..., :3] = tmp.astype(np.uint8)
        sq = 1 + 0.03 * o * st["talk"]
        hl, hx, hy = affine_layer(head, (self.neck[0], self.neck[1]), rot, 1 / sq ** 0.5, sq, (nx, ny + hdy))
        paste(canvas, body_layer, bx, by)
        paste(canvas, hl, hx, hy)  # locked head on top, cut at the chin; the pose keeps its own neck and collar


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
