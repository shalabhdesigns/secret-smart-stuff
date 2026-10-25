#!/usr/bin/env python3
"""QA sheet: every pose with the code-drawn face, at full size. usage: qa_faces.py rig.json out.jpg [pose ...]"""
import json, sys
from pathlib import Path
import cv2, numpy as np
sys.path.insert(0, str(Path(__file__).parent))
import puppet as pp
rig_path, out = sys.argv[1:3]
rig = json.loads(Path(rig_path).read_text())
pd = Path(rig_path).parent / rig.get("parts_dir", ".")
poses = sys.argv[3:] or list(rig["figures"])
tiles = []
for pk in poses:
    who = pk.split("_")[0]
    for mode in ("talk", "rest"):
        lips = [(0.9, "A")] * 200 if mode == "talk" else [(0.0, "X")] * 200
        a = {"who": who, "pose": pk, "x": 540, "neck_y": 1100, "size": 1700, "expr": "happy" if mode == "talk" else "neutral",
             "lines": [{"lips": lips, "at": 0}]}
        act = pp.FigureActor(rig, pd, a, 3.0)
        canvas = np.full((pp.H, pp.W, 3), (150, 200, 150), np.float32)
        act.render(canvas, 1.0 if mode == "talk" else 0.05)
        crop = canvas[350:1500, 90:990].astype(np.uint8)
        cv2.putText(crop, f"{pk} {mode}", (10, 40), 0, 1.1, (0, 0, 0), 3)
        tiles.append(cv2.cvtColor(crop, cv2.COLOR_RGB2BGR))
rows = [np.hstack(tiles[i:i + 4] + [np.zeros_like(tiles[0])] * (4 - len(tiles[i:i + 4]))) for i in range(0, len(tiles), 4)]
sheet = np.vstack(rows)
cv2.imwrite(out, cv2.resize(sheet, None, fx=0.5, fy=0.5, interpolation=cv2.INTER_AREA), [cv2.IMWRITE_JPEG_QUALITY, 88])
