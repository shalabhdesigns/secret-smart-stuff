"""Find where a code-drawn face goes on a blank-faced drawing (eyes, mouth, brows), from the drawn nose.

Every character in the show is drawn with a blank face that has only a nose. The nose is the dark line work
inside the skin of the face; the face width at nose height gives the scale. Proportions are calibrated on the
hand-made masters (Dev, Meera, Rocky).
"""
from __future__ import annotations

import cv2
import numpy as np


def skin_mask(rgba: np.ndarray) -> np.ndarray:
    a = rgba[..., 3] > 128
    hsv = cv2.cvtColor(np.ascontiguousarray(rgba[..., :3]), cv2.COLOR_RGB2HSV)
    h, s, v = hsv[..., 0], hsv[..., 1], hsv[..., 2]
    return ((h >= 3) & (h <= 17) & (s >= 60) & (s <= 215) & (v >= 120) & a).astype(np.uint8)


def nose_and_face(rgba: np.ndarray, region: float = 0.4) -> dict:
    """Face blob (largest skin blob in the top 40% of the figure), the nose inside it, face width at nose level."""
    a = rgba[..., 3] > 128
    ys = np.nonzero(a.any(1))[0]
    lim = ys.min() + int(region * (ys.max() - ys.min())) + 1
    sk = skin_mask(rgba)
    sk[lim:] = 0
    sk = cv2.morphologyEx(sk, cv2.MORPH_OPEN, np.ones((3, 3), np.uint8))
    n, lab, st, _ = cv2.connectedComponentsWithStats(sk, 8)
    if n <= 1:
        raise ValueError("no face")
    best = 1 + int(np.argmax(st[1:, 4]))
    x0, y0, w0, h0, _ = st[best]
    face = (lab == best).astype(np.uint8)
    filled = face.copy()
    cnts, _ = cv2.findContours(face, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
    cv2.drawContours(filled, cnts, -1, 1, -1)
    holes = (filled > 0) & (face == 0)
    v = cv2.cvtColor(np.ascontiguousarray(rgba[..., :3]), cv2.COLOR_RGB2HSV)[..., 2]
    dark = holes & (v < 150)
    # the nose: dark line work in the middle band of the face, not at its edges
    band = np.zeros_like(dark)
    band[y0 + int(0.2 * h0): y0 + int(0.68 * h0), x0 + int(0.3 * w0): x0 + int(0.7 * w0)] = True
    dark &= band
    nn, nl, ns, _ = cv2.connectedComponentsWithStats(dark.astype(np.uint8), 8)
    if nn <= 1:
        raise ValueError("no nose found")
    idx = 1 + int(np.argmax(ns[1:, 4]))
    nx, ny, nw, nh, _ = ns[idx]
    keep = [i for i in range(1, nn) if ns[i, 4] > 0.15 * ns[idx, 4]
            and abs((ns[i, 0] + ns[i, 2] / 2) - (nx + nw / 2)) < 0.15 * w0 and abs(ns[i, 1] - ny) < 0.25 * h0]
    xs0 = min(ns[i, 0] for i in keep); ys0 = min(ns[i, 1] for i in keep)
    xs1 = max(ns[i, 0] + ns[i, 2] for i in keep); ys1 = max(ns[i, 1] + ns[i, 3] for i in keep)
    row = int((ys0 + ys1) / 2)
    cols = np.nonzero(filled[row])[0]
    # face width at nose level, without the ears: the run of face pixels around the nose
    mid = int((xs0 + xs1) / 2)
    runs = np.split(cols, np.nonzero(np.diff(cols) > 1)[0] + 1)
    run = next((r for r in runs if r[0] <= mid <= r[-1]), cols)
    # chin: the face outline below the nose (the first dark row under the nose in the nose column, past the mouth area)
    col = filled[:, mid] > 0
    below = np.nonzero(~col[ys1 + 5:])[0]
    chin = int(ys1 + 5 + below[0]) if len(below) else int(np.nonzero(col)[0].max())
    return {"nose": (int(xs0), int(ys0), int(xs1), int(ys1)), "face_l": int(run[0]), "face_r": int(run[-1]),
            "chin": chin, "face_box": (int(x0), int(y0), int(w0), int(h0))}


# calibrated on the hand-placed masters (Dev, Meera, Rocky). Units: face width at nose level (fw).
# eyes: above the bottom of the nose; mouth: 42% of the way from the nose bottom to the chin.
PROP = {"eye_dx": 0.235, "eye_up": 0.31, "eye_r": 0.095, "mouth_k": 0.42, "mouth_w": 0.28}


def anchors(rgba: np.ndarray, prop: dict | None = None, region: float = 0.4) -> dict:
    p = {**PROP, **(prop or {})}
    f = nose_and_face(rgba, region)
    x0, y0, x1, y1 = f["nose"]
    cx = (x0 + x1) / 2
    fw = f["face_r"] - f["face_l"]
    eye_y = y1 - p["eye_up"] * fw
    mouth_y = y1 + p["mouth_k"] * (f["chin"] - y1)
    return {"eyes": [[round(cx - p["eye_dx"] * fw), round(eye_y)], [round(cx + p["eye_dx"] * fw), round(eye_y)]],
            "eye_r": round(p["eye_r"] * fw), "mouth": [round(cx), round(mouth_y)], "mouth_w": round(p["mouth_w"] * fw),
            "chin": f["chin"], "chin_x": round(cx), "skin_at": [round(cx - 0.3 * fw), round(y1 + 0.05 * fw)],
            "neck": [round(cx), f["chin"] + round(0.3 * fw)], "brow_gap": 1.8, "face_w": fw}
