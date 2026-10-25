#!/usr/bin/env python3
"""Find where a master head sits inside a full-body pose drawing (scale + offset), by matching outlines.

usage: align.py parts_dir master.png figure.png [chin_row]
prints: scale tx ty score   (figure_xy = scale * master_xy + (tx, ty))
"""
from __future__ import annotations

import sys
from pathlib import Path

import cv2
import numpy as np


def outline_map(rgba: np.ndarray) -> np.ndarray:
    a = rgba[..., 3] > 128
    v = cv2.cvtColor(np.ascontiguousarray(rgba[..., :3]), cv2.COLOR_RGB2HSV)[..., 2]
    m = ((v < 95) & a).astype(np.float32)
    edge = cv2.morphologyEx(a.astype(np.uint8), cv2.MORPH_GRADIENT, np.ones((3, 3), np.uint8)).astype(np.float32)
    return np.maximum(m * 0.6, edge)


def align(master: np.ndarray, fig: np.ndarray, chin: int, guess_w: float | None = None) -> tuple[float, float, float, float]:
    from puppet import analyze_face  # noqa
    mi = analyze_face(master)
    fi = analyze_face(fig, 0.35)
    base = fi["ear_w"] / mi["ear_w"]
    mtop = mi["top"]
    mrows = slice(mtop, chin)
    om = outline_map(master)[mrows]
    of = outline_map(fig)
    work = 0.25  # match at quarter resolution, refine at full
    def run(scales, k, region):
        best = (-1, 0, 0, 0)
        ofk = cv2.GaussianBlur(cv2.resize(of, None, fx=k, fy=k, interpolation=cv2.INTER_AREA), (0, 0), 1.2)
        y0, y1, x0, x1 = [int(v * k) for v in region]
        ofk = ofk[y0:y1, x0:x1]
        for s in scales:
            t = cv2.resize(om, None, fx=s * k, fy=s * k, interpolation=cv2.INTER_AREA)
            t = cv2.GaussianBlur(t, (0, 0), 1.2)
            if t.shape[0] >= ofk.shape[0] or t.shape[1] >= ofk.shape[1]:
                continue
            r = cv2.matchTemplate(ofk, t, cv2.TM_CCORR_NORMED)
            _, mv, _, ml = cv2.minMaxLoc(r)
            if mv > best[0]:
                best = (mv, s, (ml[0] / k + x0), (ml[1] / k + y0))
        return best
    H, W = fig.shape[:2]
    fx0, fy0, fw, fh = fi["face_box"]
    region = (0, min(H, fy0 + fh * 3), max(0, fx0 - fw * 2), min(W, fx0 + fw * 3))
    sc, s, x, y = run(np.arange(base * 0.8, base * 1.2, base * 0.01), work, region)
    pad = int(40 / 1)
    region2 = (max(0, y - pad * 3), min(H, y + om.shape[0] * s + pad * 3), max(0, x - pad * 3), min(W, x + om.shape[1] * s + pad * 3))
    sc, s, x, y = run(np.arange(s * 0.97, s * 1.03, s * 0.003), 1.0, region2)
    return s, x, y - mtop * s, sc  # offset so master (0,0) maps correctly


if __name__ == "__main__":
    sys.path.insert(0, str(Path(__file__).parent))
    pd = Path(sys.argv[1])
    from puppet import load_rgba
    m = load_rgba(pd / sys.argv[2]); f = load_rgba(pd / sys.argv[3])
    chin = int(sys.argv[4])
    print(*[round(v, 4) for v in align(m, f, chin)])
