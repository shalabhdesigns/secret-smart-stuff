#!/usr/bin/env python3
"""Contact sheet of every pose with the locked head, for library QA. usage: posecheck.py rig.json out.png who:head:pose ..."""
import sys, json, numpy as np, cv2
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
import puppet as Pp
rig_path, out, *tests = sys.argv[1:]
rig = json.load(open(rig_path)); parts = Path(rig_path).parent / rig.get("parts_dir", ".")
tiles = []
for t in tests:
    who, head, pose = t.split(":")
    canvas = np.full((Pp.H, Pp.W, 3), 235, np.float32)
    Pp.FigureActor(rig, parts, dict(who=who, head=head, pose=pose, size=150, x=540, floor=1880, expr="neutral"), 2.0).render(canvas, 0.0)
    tiles.append(cv2.resize(canvas.astype(np.uint8), (360, 640)))
n = 6
rows = [np.hstack(tiles[i:i + n] + [np.zeros((640, 360, 3), np.uint8)] * (n - len(tiles[i:i + n]))) for i in range(0, len(tiles), n)]
cv2.imwrite(out, cv2.cvtColor(np.vstack(rows), cv2.COLOR_RGB2BGR))
