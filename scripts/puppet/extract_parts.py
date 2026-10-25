#!/usr/bin/env python3
"""Cut puppet parts out of a flat-green parts sheet.

usage: extract_parts.py sheet.png out_dir name1 name2 ...   (names in left-to-right order of the parts)

Keys out the green background (soft alpha + green-spill removal), groups nearby pixels into parts,
sorts the parts left to right (top to bottom for parts in the same column) and writes RGBA PNGs.
"""
from __future__ import annotations

import sys
from pathlib import Path

import cv2
import numpy as np
from PIL import Image


def key_green(rgb: np.ndarray) -> np.ndarray:
    f = rgb.astype(np.float32)
    r, g, b = f[..., 0], f[..., 1], f[..., 2]
    green = g - np.maximum(r, b)
    alpha = np.clip(1.0 - (green - 30.0) / 110.0, 0.0, 1.0)
    out = f.copy()
    spill = green > 0
    out[..., 1] = np.where(spill, np.maximum(r, b) + np.clip(green, 0, 10), g)  # remove green fringe
    rgba = np.dstack([np.clip(out, 0, 255), alpha * 255]).astype(np.uint8)
    return rgba


def split(rgba: np.ndarray, min_area: int = 4000, gap: int = 18):
    mask = (rgba[..., 3] > 128).astype(np.uint8)
    grown = cv2.dilate(mask, np.ones((gap, gap), np.uint8))
    n, labels, stats, _ = cv2.connectedComponentsWithStats(grown, 8)
    parts = []
    for i in range(1, n):
        x, y, w, h, area = stats[i]
        if area < min_area:
            continue
        sel = (labels == i)
        part = rgba.copy()
        part[..., 3] = np.where(sel, part[..., 3], 0)
        pad = 6
        y0, y1 = max(0, y - pad), min(rgba.shape[0], y + h + pad)
        x0, x1 = max(0, x - pad), min(rgba.shape[1], x + w + pad)
        parts.append(((x + w / 2), (y + h / 2), part[y0:y1, x0:x1]))
    parts.sort(key=lambda p: (round(p[0] / 300), p[1]))
    return parts


def main() -> int:
    sheet, out_dir, *names = sys.argv[1:]
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    rgba = key_green(np.array(Image.open(sheet).convert("RGB")))
    parts = split(rgba)
    print(f"{len(parts)} parts found")
    for i, (cx, cy, img) in enumerate(parts):
        name = names[i] if i < len(names) else f"extra{i}"
        Image.fromarray(img).save(out / f"{name}.png")
        print(f"  {name}: {img.shape[1]}x{img.shape[0]} at ({cx:.0f},{cy:.0f})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
