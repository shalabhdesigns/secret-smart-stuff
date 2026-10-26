#!/usr/bin/env python3
"""QA sheet: every emotion on one character pose. usage: emo_sheet.py rig.json pose out.jpg [emotion ...]"""
import json, sys
from pathlib import Path
import cv2, numpy as np
sys.path.insert(0, str(Path(__file__).parent))
import puppet as pp
import face as F
rig_path, pose, out = sys.argv[1:4]
emos = sys.argv[4:] or list(F.EMOTIONS)
rig = json.loads(Path(rig_path).read_text()); pd = Path(rig_path).parent / rig.get("parts_dir", ".")
who = pose.split("_")[0]
tiles = []
for em in emos:
    a = {"who": who, "pose": pose, "x": 540, "neck_y": 1050, "size": 2400 if who != "rocky" else 2000, "expr": em}
    act = pp.FigureActor(rig, pd, a, 3.0)
    act.blinks = []
    canvas = np.full((pp.H, pp.W, 3), (205, 225, 205), np.float32)
    act.render(canvas, 0.7)
    crop = canvas[180:1200, 140:940].astype(np.uint8).copy()
    cv2.putText(crop, em, (12, 50), 0, 1.6, (0, 0, 0), 4)
    tiles.append(cv2.cvtColor(crop, cv2.COLOR_RGB2BGR))
cols = 6
while len(tiles) % cols:
    tiles.append(np.full_like(tiles[0], 255))
rows = [np.hstack(tiles[i:i + cols]) for i in range(0, len(tiles), cols)]
sheet = np.vstack(rows)
cv2.imwrite(out, cv2.resize(sheet, None, fx=float(__import__("os").environ.get("SC","0.36")), fy=float(__import__("os").environ.get("SC","0.36")), interpolation=cv2.INTER_AREA), [cv2.IMWRITE_JPEG_QUALITY, 88])
print(len(emos), sheet.shape)
