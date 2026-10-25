#!/usr/bin/env python3
"""Render one still per shot (at a chosen fraction of the shot) into a contact sheet, for layout checks."""
import json, sys
from pathlib import Path
import numpy as np, cv2
sys.path.insert(0, str(Path(__file__).parent))
import puppet as P

rig_path, scene_path, out_png = sys.argv[1:4]
frac = float(sys.argv[4]) if len(sys.argv) > 4 else 0.5
rig = json.loads(Path(rig_path).read_text()); scene = json.loads(Path(scene_path).read_text())
parts = Path(rig_path).parent / rig.get("parts_dir", ".")
lines_dir = Path(scene_path).parent / scene.get("lines_dir", ".")
lips = {n: P.lipsync(lines_dir / f"{n}.wav") for n in scene["lines"]}
tiles = []
for shot in scene["shots"]:
    t = shot["dur"] * frac
    bg = shot.get("bg", "black")
    if bg == "spiral": canvas = P.spiral_bg(t)
    elif bg == "black": canvas = np.zeros((P.H, P.W, 3), np.float32)
    else:
        b = shot.get("bg_view", {})
        canvas = P.load_bg(parts / rig["backgrounds"][bg], b.get("zoom", 1), b.get("cx", .5), b.get("cy", .5), b.get("blur", 0))
    for a in shot.get("actors", []):
        a = dict(a); a["lines"] = [{"lips": lips[l["line"]], "at": l["at"]} for l in a.get("lines", [])]
        (P.FigureActor if "pose" in a else P.Actor)(rig, parts, a, shot["dur"]).render(canvas, t)
    c = shot.get("cam", {"zoom": 1, "cx": 540, "cy": 960})
    z, cx, cy = c["zoom"], c["cx"], c["cy"]
    for e in shot.get("fx", []):
        if "cam" in e and e["t"] <= t:
            k = P.ease((t - e["t"]) / e["over"]) if e.get("over") else 1
            z, cx, cy = z + (e["cam"]["zoom"] - z) * k, cx + (e["cam"].get("cx", cx) - cx) * k, cy + (e["cam"].get("cy", cy) - cy) * k
    fr = P.camera(np.clip(canvas, 0, 255), z, cx, cy)
    tiles.append(cv2.resize(fr.astype(np.uint8), (270, 480)))
rows = [np.hstack(tiles[i:i + 6] + [np.zeros((480, 270, 3), np.uint8)] * (6 - len(tiles[i:i + 6]))) for i in range(0, len(tiles), 6)]
cv2.imwrite(out_png, cv2.cvtColor(np.vstack(rows), cv2.COLOR_RGB2BGR))
