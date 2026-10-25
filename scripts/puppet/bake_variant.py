#!/usr/bin/env python3
"""Bake a hair variant (e.g. bowl cut) into a full-body pose drawing, once, as a new library file.

The variant head and the pose's own head share the same face, so they are aligned on the face and
ears only, the variant's hair replaces the pose's hair, and the lower face fades back to the pose's
own drawing. No cut line ever crosses the neck.

usage: bake_variant.py parts_dir primary_head.png primary_chin variant_head.png pose.png out.png
"""
from __future__ import annotations

import sys
from pathlib import Path

import cv2
import numpy as np

sys.path.insert(0, str(Path(__file__).parent))
from align import align, outline_map  # noqa: E402
from puppet import analyze_face, load_rgba  # noqa: E402


def face_align(prim: np.ndarray, var: np.ndarray) -> tuple[float, float, float]:
    """variant -> primary head coords, matched on ears/jaw/nose only (rows below the eyes)."""
    pi, vi = analyze_face(prim), analyze_face(var)
    om_p, om_v = outline_map(prim), outline_map(var)
    def band(info):
        x0, y0, w0, h0 = info["face_box"]
        return y0 + int(h0 * 0.45), y0 + h0 + 4
    py0, py1 = band(pi)
    vy0, vy1 = band(vi)
    tmpl = om_v[vy0:vy1]
    best = (-1, 1, 0, 0)
    for s in np.arange(0.92, 1.08, 0.004):
        t = cv2.GaussianBlur(cv2.resize(tmpl, None, fx=s, fy=s, interpolation=cv2.INTER_AREA), (0, 0), 1.0)
        img = cv2.GaussianBlur(om_p[max(0, py0 - 60):py1 + 60], (0, 0), 1.0)
        if t.shape[0] > img.shape[0] or t.shape[1] > img.shape[1]:
            continue
        r = cv2.matchTemplate(img, t, cv2.TM_CCORR_NORMED)
        _, mv, _, ml = cv2.minMaxLoc(r)
        if mv > best[0]:
            best = (mv, s, ml[0], ml[1] + max(0, py0 - 60) - vy0 * s)
    print(f"  variant->primary score {best[0]:.3f} scale {best[1]:.3f}")
    return best[1], best[2], best[3]


def main() -> int:
    pd = Path(sys.argv[1])
    prim = load_rgba(pd / sys.argv[2]); chin = int(sys.argv[3])
    var = load_rgba(pd / sys.argv[4]); pose = load_rgba(pd / sys.argv[5])
    s1, tx1, ty1 = face_align(prim, var)
    s2, tx2, ty2, sc = align(prim, pose, chin)
    print(f"  primary->pose score {sc:.3f}")
    s, tx, ty = s1 * s2, s2 * tx1 + tx2, s2 * ty1 + ty2   # variant -> pose
    H, W = pose.shape[:2]
    M = np.float32([[s, 0, tx], [0, s, ty]])
    V = cv2.warpAffine(var, M, (W, H), flags=cv2.INTER_CUBIC, borderValue=(0, 0, 0, 0))
    vi = analyze_face(var)
    x0, y0, w0, h0 = vi["face_box"]
    # rows in pose coords: variant fully owns everything above the nose; fades out by the mouth
    fade_a = int(s * (y0 + h0 * 0.42) + ty)
    fade_b = int(s * (y0 + h0 * 0.62) + ty)
    yy = np.arange(H, dtype=np.float32)[:, None]
    wv = np.clip((fade_b - yy) / max(1, fade_b - fade_a), 0, 1)
    wv = np.broadcast_to(wv, (H, W)) * (V[..., 3] / 255.0)
    out = pose.astype(np.float32)
    # 1) remove the pose's own hair where the variant has none (above the fade, head columns only)
    hsv = cv2.cvtColor(np.ascontiguousarray(pose[..., :3]), cv2.COLOR_RGB2HSV)
    pi = analyze_face(prim)
    px0, py0, pw0, ph0 = pi["face_box"]
    hx0, hx1 = int(s2 * (px0 - pw0 * 0.6) + tx2), int(s2 * (px0 + pw0 * 1.6) + tx2)
    head_top = int(s2 * (pi["top"] - 40) + ty2)
    region = np.zeros((H, W), bool)
    region[max(0, head_top):fade_b, max(0, hx0):min(W, hx1)] = True
    vmask = cv2.dilate((V[..., 3] > 30).astype(np.uint8), np.ones((5, 5), np.uint8)) > 0
    hairish = (hsv[..., 2] < 110) | (pose[..., 3] < 250)
    kill = region & ~vmask & hairish & (pose[..., 3] > 0)
    # keep only kill pixels connected to the head (not a raised hand)
    n, lab = cv2.connectedComponents(kill.astype(np.uint8), 8)
    touch = set(np.unique(lab[(cv2.dilate(vmask.astype(np.uint8), np.ones((9, 9), np.uint8)) > 0) & (lab > 0)]))
    kill = np.isin(lab, [k for k in touch if k > 0])
    out[..., 3] = np.where(kill, 0, out[..., 3])
    # 2) composite the variant on top with the vertical fade
    a = wv[..., None]
    vrgb = V[..., :3].astype(np.float32)
    base_a = out[..., 3:4] / 255.0
    new_a = a + base_a * (1 - a)
    rgb = (vrgb * a + out[..., :3] * base_a * (1 - a)) / np.maximum(new_a, 1e-6)
    out = np.dstack([rgb, new_a[..., 0] * 255])
    res = cv2.cvtColor(np.clip(out, 0, 255).astype(np.uint8), cv2.COLOR_RGBA2BGRA)
    cv2.imwrite(str(pd / sys.argv[6]), res)
    print("  wrote", sys.argv[6])
    return 0


if __name__ == "__main__":
    sys.exit(main())
