"""New art on demand, in the exact show style, checked before use: sets, poses and new on-screen characters.

- Images: FLUX.2 [pro] with approved show art as the style/identity reference.
- Characters and poses are drawn with a BLANK face (only a nose) on flat green; the face is drawn by code,
  exactly like Dev, Meera and Rocky, so expressions and lip sync work the same for everyone.
- Every new image passes automatic checks (green key, face found, head matches) and a Claude vision check
  of the rendered result (with the code-drawn face). Failures are thrown away and retried once.
- Spending counts against the weekly art cap (config budget_usd.art_weekly). Nothing is committed if a check fails.
"""
from __future__ import annotations

import base64
import datetime as dt
import json
import os
import sys
import time
from pathlib import Path

import cv2
import numpy as np
import requests
from PIL import Image

from . import director as D
from . import facefind as FF

ROOT = Path(__file__).resolve().parents[2]
BG_DIR = ROOT / "assets" / "puppet" / "backgrounds"
PARTS = ROOT / "assets" / "puppet" / "parts"
WORK = ROOT / "build" / "art"
MODEL = "flux-2-pro"
USD_EACH = 0.07            # one FLUX.2 [pro] image with references, upper estimate
QA_MODEL = "claude-sonnet-5-5"
GREEN = (0, 177, 64)

sys.path.insert(0, str(ROOT / "scripts" / "puppet"))


class ArtError(RuntimeError):
    pass


# ----------------------------------------------------------------------------- helpers
def weekly_spend(state) -> float:
    since = time.time() - 7 * 86400
    row = state.db.execute("SELECT COALESCE(SUM(usd),0) s FROM costs WHERE provider='art' AND at>=?", (since,)).fetchone()
    return float(row["s"])


def _cap(p) -> float:
    return float(p.cfg.pipeline.get("budget_usd", {}).get("art_weekly", 5.0))


def can_spend(p, n: int = 1) -> bool:
    return weekly_spend(p.state) + n * USD_EACH <= _cap(p)


def _b64_small(path: Path, box=(768, 1376)) -> str:
    im = Image.open(path)
    if im.mode == "RGBA":                       # figures go on flat green, like the drawings the show was made from
        bg = Image.new("RGB", im.size, GREEN)
        bg.paste(im, (0, 0), im)
        im = bg
    im = im.convert("RGB")
    im.thumbnail(box)
    tmp = WORK / f"ref_{path.stem}.jpg"
    tmp.parent.mkdir(parents=True, exist_ok=True)
    im.save(tmp, quality=90)
    return base64.b64encode(tmp.read_bytes()).decode()


def flux(p, what: str, prompt: str, refs: list[Path], out: Path, w: int = 1088, h: int = 1952,
         model: str = MODEL) -> None:
    if not can_spend(p):
        raise ArtError(f"weekly art budget (${_cap(p):.0f}) reached")
    key = os.environ.get("BFL_API_KEY", "")
    if model.startswith("flux-kontext"):          # image editing model: keeps the reference, changes what's asked
        body = {"prompt": prompt, "aspect_ratio": "9:16", "output_format": "png", "safety_tolerance": 2,
                "input_image": _b64_small(refs[0], (1024, 1820))}
    else:
        body = {"prompt": prompt, "width": w, "height": h, "output_format": "png"}
        for i, r in enumerate(refs[:4]):
            body["input_image" if i == 0 else f"input_image_{i + 1}"] = _b64_small(r)
    hd = {"x-key": key, "accept": "application/json", "content-type": "application/json"}
    r = requests.post("https://api.bfl.ai/v1/" + model, json=body, headers=hd, timeout=60)
    if r.status_code != 200:
        raise ArtError(f"BFL {r.status_code}: {r.text[:200]}")
    p.state.add_cost("art", what, 1, USD_EACH)
    poll = r.json()["polling_url"]
    t0 = time.time()
    while time.time() - t0 < 300:
        time.sleep(2)
        s = requests.get(poll, headers=hd, timeout=30).json()
        if s.get("status") == "Ready":
            out.parent.mkdir(parents=True, exist_ok=True)
            out.write_bytes(requests.get(s["result"]["sample"], timeout=120).content)
            return
        if s.get("status") not in ("Pending", "Processing", None):
            raise ArtError(f"BFL {s.get('status')}")
    raise ArtError("BFL timed out")


def _llm(p):
    from shorts.providers.llm import AnthropicLLM
    cfg = dict(p.cfg.pipeline["providers"]["llm"])
    cfg.setdefault("prices", {}).setdefault(QA_MODEL, [2.0, 10.0])
    return AnthropicLLM(os.environ["ANTHROPIC_API_KEY"], cfg)


def _vision(p, prompt: str, images: list[Path]) -> dict:
    llm = _llm(p)
    r = llm.ask(prompt, model=QA_MODEL, max_tokens=1200, images=[i.read_bytes() for i in images])
    p.state.add_cost("anthropic", "art qa", 1, r.usd)
    return r.data if isinstance(r.data, dict) else {"ok": False, "reasons": ["no verdict"]}


def _small(path: Path, out: Path, h: int = 1100) -> Path:
    im = Image.open(path)
    if im.mode == "RGBA":
        bg = Image.new("RGB", im.size, (235, 235, 235))
        bg.paste(im, (0, 0), im)
        im = bg
    im = im.convert("RGB")
    im = im.resize((max(1, int(im.size[0] * h / im.size[1])), h))
    im.save(out)
    return out


def key_out(png: Path, out: Path) -> np.ndarray:
    """Flat green -> transparent with no green/teal fringe; keep the biggest drawing; crop with a small margin.
    Edge pixels are un-mixed from the measured background colour, then the edge is pulled in by 1 px."""
    rgb = np.array(Image.open(png).convert("RGB")).astype(np.float32)
    H, W = rgb.shape[:2]
    border = np.concatenate([rgb[:8].reshape(-1, 3), rgb[-8:].reshape(-1, 3), rgb[:, :8].reshape(-1, 3), rgb[:, -8:].reshape(-1, 3)])
    bg = np.median(border, 0)
    r, g, b = rgb[..., 0], rgb[..., 1], rgb[..., 2]
    green = g - np.maximum(r, b)
    gbg = bg[1] - max(bg[0], bg[2])
    alpha = np.clip(1.0 - (green - 0.12 * gbg) / (0.75 * gbg), 0.0, 1.0)
    # biggest drawing only
    solid = (alpha > 0.5).astype(np.uint8)
    n, lab, st, _ = cv2.connectedComponentsWithStats(cv2.dilate(solid, np.ones((15, 15), np.uint8)), 8)
    if n <= 1:
        raise ArtError("nothing drawn")
    best = 1 + int(np.argmax(st[1:, 4]))
    alpha *= (lab == best)
    x, y, w, h, _ = st[best]
    if y <= 2 or y + h >= H - 2:
        raise ArtError("figure is cut by the image edge (head or feet missing)")
    # un-mix: C = a*F + (1-a)*BG  ->  F = (C - (1-a)*BG) / a
    a3 = np.maximum(alpha, 1e-3)[..., None]
    fg = np.clip((rgb - (1 - a3) * bg) / a3, 0, 255)
    fg[..., 1] = np.minimum(fg[..., 1], np.maximum(fg[..., 0], fg[..., 2]) + 25)   # any leftover spill
    a8 = (alpha * 255).astype(np.uint8)
    a8 = cv2.erode(a8, np.ones((3, 3), np.uint8))                                   # pull the edge in 1 px
    a8[a8 < 20] = 0
    rgba = np.dstack([fg.astype(np.uint8), a8])
    m = 12
    rgba = rgba[max(0, y - m):y + h + m, max(0, x - m):x + w + m]
    if rgba.shape[0] < 2200:                       # match the resolution of the hand-made library (~2700 px tall)
        k = 2600 / rgba.shape[0]
        up = cv2.resize(rgba, None, fx=k, fy=k, interpolation=cv2.INTER_CUBIC)
        col = up[..., :3].astype(np.float32)
        blur = cv2.GaussianBlur(col, (0, 0), 1.6)
        up[..., :3] = np.clip(col + 0.6 * (col - blur), 0, 255).astype(np.uint8)   # keep outlines crisp
        rgba = up
    Image.fromarray(rgba).save(out)
    return rgba


def _commit(paths: list[Path], msg: str) -> None:
    from . import world as Wd
    Wd.commit(msg, paths)


def _save_json(path: Path, data: dict) -> None:
    path.write_text(json.dumps(data, indent=1, ensure_ascii=False))


# ----------------------------------------------------------------------------- sets
SET_QA = """TASK: setqa
Image 1 is an approved background from our 2D cartoon show. Image 2 is a NEW background for the same show,
meant to show: @DESC
Characters will be drawn standing on the floor in the lower part of the frame, so check:
1. same flat cartoon illustration style, line weight and colour feel as image 1
2. the place matches the description and looks Indian where relevant
3. empty: no people, no characters, no faces (a small animal at the side is OK)
4. straight-on, eye-level view; floor or ground clearly visible across the bottom ~25% of the image
5. no readable text, letters, numbers, logos or brand names anywhere
6. nothing large in the lower centre that characters would stand inside
Return JSON {"ok": true|false, "reasons": ["..."]}. Be strict."""


def generate_set(p, sid: str, desc: str, short: str = "") -> bool:
    lib = D.library()
    if sid in lib["sets"]:
        return True
    ref = BG_DIR / "flat.jpg"
    for attempt in range(2):
        out = WORK / f"set_{sid}_{attempt}.png"
        prompt = ("Using exactly the same flat 2D cartoon illustration style, outline thickness, soft shading and warm "
                  f"colour palette as the reference image, draw a different empty location: {desc}. Vertical 9:16 "
                  "background for an animated show, straight-on eye-level view, the floor/ground clearly visible "
                  "across the bottom quarter, open empty space in the lower centre, no people, no characters, "
                  "no text, no letters, no logos.")
        try:
            flux(p, f"set {sid}", prompt, [ref], out)
        except ArtError as e:
            p.state.log(f"set {sid}: {e}", "warn")
            if "budget" in str(e):
                return False
            continue
        v = _vision(p, SET_QA.replace("@DESC", desc), [_small(ref, WORK / "cmp_ref.png", 976),
                                                        _small(out, WORK / "cmp_new.png", 976)])
        if not v.get("ok"):
            p.state.log(f"set {sid} rejected: {v.get('reasons')}", "info")
            continue
        dst = BG_DIR / f"{sid}.jpg"
        Image.open(out).convert("RGB").save(dst, quality=93)
        rg = D.rig()
        rg["backgrounds"][sid] = f"../backgrounds/{sid}.jpg"
        _save_json(D.RIG, rg)
        lib = D.library()
        lib["sets"][sid] = {"bg": sid, "floor": 1850, "desc": short or desc, "added": dt.date.today().isoformat()}
        _save_json(D.LIB, lib)
        _commit([dst, D.RIG, D.LIB], f"Library: new set {sid}")
        return True
    return False


# ----------------------------------------------------------------------------- poses and characters
BLANK = ("The face is deliberately BLANK: plain skin with ONLY a nose drawn - no eyes, no eyebrows, no mouth, no "
         "glasses, no facial expression (eyes and mouth are added later by animation software). ")
FIGURE = ("Full body from the top of the head to the shoes, standing on nothing, the head upright and facing the "
          "viewer straight on (not tilted, not turned), both ears visible. Solid flat pure green background "
          "(#00B140) filling the whole image, no shadow on the ground, no text, nothing else in the image.")


LEG_WORDS = ("leg", "feet", "foot", "walk", "run", "sit", "kneel", "jump", "kick", "squat", "dance", "lying", "bend",
             "crouch", "step", "tiptoe", "shoe")


def graft_legs(rg: dict, who: str, new_file: str, cut: float = 0.88, band: int = 30) -> None:
    """Image editors keep the body but like to change shoes. When a pose doesn't involve the legs, take the lower
    legs and feet from the character's approved standing drawing (placed by matching the head), blended in."""
    import puppet as pp
    from align import align
    ch = rg["characters"][who]
    h = rg["heads"][ch["primary_head"]]
    master = pp.load_rgba(PARTS / h["file"])
    stand = pp.load_rgba(PARTS / rg["figures"][ch["stand_pose"]]["file"])
    new = pp.load_rgba(PARTS / new_file)
    s1, tx1, ty1, _ = align(master, stand, int(ch["chin"]))
    s2, tx2, ty2, _ = align(master, new, int(ch["chin"]))
    k = s2 / s1                                         # stand px -> new px
    M = np.float32([[k, 0, tx2 - tx1 * k], [0, k, ty2 - ty1 * k]])
    ys = np.nonzero(stand[..., 3].max(1) > 128)[0]
    cut_y = (ys.min() + cut * (ys.max() - ys.min())) * k + ty2 - ty1 * k
    foot_y = ys.max() * k + ty2 - ty1 * k
    Hn = int(max(new.shape[0], foot_y + 20))
    canvas = np.zeros((Hn, new.shape[1], 4), np.uint8)
    canvas[:new.shape[0]] = new
    warped = cv2.warpAffine(stand, M, (new.shape[1], Hn), flags=cv2.INTER_CUBIC, borderValue=(0, 0, 0, 0))
    # fine-align the legs themselves: best shift/scale so both drawings' legs overlap just above the cut
    y0, y1 = int(cut_y - 3 * band), int(cut_y - band / 2)
    a_new = (canvas[y0:y1, :, 3] > 128).astype(np.float32)
    best = (-1.0, 0, 0, 1.0)
    for sc in (0.98, 1.0, 1.02):
        cx = new.shape[1] / 2
        Ms = np.float32([[sc, 0, cx * (1 - sc)], [0, sc, cut_y * (1 - sc)]])
        ws = cv2.warpAffine(warped[..., 3], Ms, (new.shape[1], Hn))
        for dy in range(-40, 41, 4):
            for dx in range(-60, 61, 3):
                ys0, ys1 = y0 - dy, y1 - dy
                if ys0 < 0 or ys1 > Hn:
                    continue
                b = (np.roll(ws[ys0:ys1], dx, axis=1) > 128).astype(np.float32)
                inter = (a_new * b).sum()
                iou = inter / max(1.0, a_new.sum() + b.sum() - inter)
                if iou > best[0]:
                    best = (iou, dx, dy, sc)
    _, dx, dy, sc = best
    Ms = np.float32([[sc, 0, new.shape[1] / 2 * (1 - sc) + dx], [0, sc, cut_y * (1 - sc) + dy]])
    warped = cv2.warpAffine(warped, Ms, (new.shape[1], Hn), flags=cv2.INTER_CUBIC, borderValue=(0, 0, 0, 0))
    # the seam goes at the lowest row (not below the ankles) where both drawings still show the same thing
    yA, yB = int(cut_y - 0.25 * (foot_y - cut_y) - 3 * band), int(cut_y)
    if yB - yA > 10:
        both = (canvas[yA:yB, :, 3] > 200) & (warped[yA:yB, :, 3] > 200)
        diff = np.abs(canvas[yA:yB, :, :3].astype(np.float32) - warped[yA:yB, :, :3].astype(np.float32)).mean(2)
        rowd = np.where(both.sum(1) > 20, (diff * both).sum(1) / np.maximum(1, both.sum(1)), 999)
        rowd = np.convolve(rowd, np.ones(9) / 9, mode="same")
        ok = np.nonzero(rowd < 45)[0]
        if len(ok):
            cut_y = yA + int(ok.max()) - band / 2
    # only the legs: below the cut, keep the parts connected to the feet (drops hanging fingertips etc.)
    low = (warped[..., 3] > 0).astype(np.uint8)
    low[:max(0, int(cut_y - band))] = 0
    n, lab, st, _ = cv2.connectedComponentsWithStats(low, 8)
    if n > 1:
        bottom = st[1:, 1] + st[1:, 3]
        keep = [i + 1 for i, b in enumerate(bottom) if b >= bottom.max() - 25]
        warped[..., 3] = (warped[..., 3] * np.isin(lab, keep)).astype(np.uint8)
    w = np.clip((np.arange(Hn) - (cut_y - band / 2)) / band, 0, 1).astype(np.float32)[:, None]
    an, aw = canvas[..., 3].astype(np.float32) / 255, warped[..., 3].astype(np.float32) / 255
    wn, ww = an * (1 - w), aw * w
    started = w > 0                                    # from the seam down, the approved legs define the outline
    wn = np.where(started & (aw < 0.5), 0.0, wn)
    ww = np.where(started & (an < 0.5), aw, ww)
    col = (canvas[..., :3] * wn[..., None] + warped[..., :3] * ww[..., None]) / np.maximum(wn + ww, 1e-4)[..., None]
    alpha = wn + ww
    out = np.dstack([np.clip(col, 0, 255), np.clip(alpha * 255, 0, 255)]).astype(np.uint8)
    ys2 = np.nonzero(out[..., 3].max(1) > 0)[0]
    out = out[:ys2.max() + 12]
    Image.fromarray(out).save(PARTS / new_file)


def _render_sheet(rg: dict, who: str, poses: list[str], out: Path, exprs=("neutral", "happy", "shock")) -> Path:
    import puppet as pp
    tiles = []
    for pk in poses:
        for ex in exprs:
            lips = [(0.8, "A")] * 200 if ex == "happy" else [(0.0, "X")] * 200
            a = {"who": who, "pose": pk, "x": 540, "floor": 1880, "size": 1500, "expr": ex, "lines": [{"lips": lips, "at": 0}]}
            act = pp.FigureActor(rg, PARTS, a, 3.0)
            canvas = np.full((pp.H, pp.W, 3), (225, 225, 225), np.float32)
            act.render(canvas, 1.0)
            tiles.append(canvas.astype(np.uint8)[60:1900:2, ::2])
    per = len(exprs)
    rows = [np.hstack(tiles[i:i + per]) for i in range(0, len(tiles), per)]
    Image.fromarray(np.vstack(rows)).save(out)
    return out


POSE_QA = """TASK: poseqa
Image 1: our approved cartoon character in their standard pose. Image 2: the SAME character in a NEW pose.
Both are rendered by our animation software, which draws the eyes, brows, mouth (and glasses, for characters who
wear them) by code, in 3 expressions each. Left/right mirroring of the pose is fine.
The new pose should be: @DESC
Check strictly:
1. same character: identical head shape, hair, skin tone, clothes, colours, proportions and outline style
2. the pose matches the description, reads clearly, hands and fingers are complete and correct (no extra limbs)
3. the code-drawn face sits naturally on the face (eyes level and inside the face, mouth below the nose, nothing
   floating on hair or outside the head) and there is no second drawn face, mouth or eyes from the drawing itself
4. full body visible, nothing cut off, no green fringes or leftover background
Return JSON {"ok": true|false, "reasons": ["..."]}."""


def _alignment_score(rg: dict, who: str, fig_file: str) -> float:
    from align import align
    import puppet as pp
    ch = rg["characters"][who]
    h = rg["heads"][ch["primary_head"]]
    s, tx, ty, score = align(pp.load_rgba(PARTS / h["file"]), pp.load_rgba(PARTS / fig_file), int(ch["chin"]))
    return float(score)


def generate_pose(p, who: str, pose_id: str, desc: str, kind: str = "stand") -> bool:
    lib, rg = D.library(), D.rig()
    if pose_id in rg["figures"]:
        return True
    if who not in rg["characters"]:
        return False
    stand = rg["figures"][rg["characters"][who]["stand_pose"]]["file"]
    look = lib["characters"].get(who, {}).get("desc", "")
    edit = (f"Change only the pose of this cartoon character: {desc}. Keep everything else pixel-identical: the same "
            "head and hair (do not restyle or smooth the hair), the same blank face with only a nose (do not add eyes, "
            "eyebrows, mouth or glasses), the same skin colour, the same clothes and the SAME FOOTWEAR in the same colour, "
            "the same outline style and the same flat green background with no shadow on the ground. Full body visible "
            "from head to feet with empty green space above and below. No text.")
    prompts = [
        ("Draw the cartoon character from the reference image again, in the same flat 2D cartoon show style as the reference "
         f"image (same outline thickness, cel shading and colours). Character: {look} Keep the head, hair, skin tone, "
         f"clothes and proportions identical to the reference. New pose: {desc}. " + BLANK + FIGURE),
        (f"A flat 2D cartoon character illustration, same character design and style as the reference image: {look} "
         f"Pose: {desc}. Simple cartoon face with only a nose drawn (eyes and mouth are added later in animation). "
         "Full body, upright head facing the viewer, plain flat green background."),
    ]
    margin = (" Leave clear empty green space above the head and below the feet; the whole figure fits inside the "
              "middle 85% of the image height. Do not add any text or print on clothes.")
    plan = [("flux-kontext-pro", edit), ("flux-kontext-pro", edit), (MODEL, prompts[0] + margin), (MODEL, prompts[1] + margin)]
    for attempt, (model, prompt) in enumerate(plan):
        raw = WORK / f"pose_{pose_id}_{attempt}.png"
        try:
            flux(p, f"pose {pose_id}", prompt, [PARTS / stand], raw, 1088, 1952, model=model)
            fname = f"{pose_id}.png"
            key_out(raw, PARTS / fname)
            if kind == "stand" and not any(w_ in desc.lower() for w_ in LEG_WORDS):
                graft_legs(rg, who, fname)
            score = _alignment_score(rg, who, fname)
            if score < 0.72:
                raise ArtError(f"head doesn't match the character (score {score:.2f})")
        except (ArtError, ValueError) as e:
            p.state.log(f"pose {pose_id}: {e}", "warn")
            if "budget" in str(e):
                return False
            continue
        rg2 = json.loads(json.dumps(rg))
        rg2["figures"][pose_id] = {"file": fname}
        sheet = _render_sheet(rg2, who, [pose_id], WORK / f"pose_{pose_id}_sheet.png")
        ref_sheet = _render_sheet(rg2, who, [rg["characters"][who]["stand_pose"]], WORK / f"pose_{who}_ref_sheet.png")
        v = _vision(p, POSE_QA.replace("@DESC", desc), [_small(ref_sheet, WORK / "pose_ref.png", 900),
                                                         _small(sheet, WORK / "pose_new.png", 900)])
        p.state.log(f"pose {pose_id} qa: {json.dumps(v)[:400]}", "info")
        if not v.get("ok"):
            continue
        _save_json(D.RIG, rg2)
        lib["poses"][pose_id] = {"who": who, "kind": kind, "desc": desc, "added": dt.date.today().isoformat()}
        _save_json(D.LIB, lib)
        _commit([PARTS / fname, D.RIG, D.LIB], f"Library: new pose {pose_id}")
        return True
    (PARTS / f"{pose_id}.png").unlink(missing_ok=True)
    return False


CHAR_QA = """TASK: charqa
Image 1: two approved characters of our 2D cartoon show (style reference). Image 2: a NEW character for the
show, rendered by our animation software with code-drawn eyes, brows and mouth, in 3 expressions.
The character should be: @DESC
Check strictly:
1. same flat cartoon style, outline weight and colour feel as image 1; clearly an Indian person as described
2. the code-drawn face looks natural: both eyes level and well inside the face, the right size for the head,
   brows above the eyes, mouth centred below the nose; nothing on the hair, ears or outside the face
3. there is no second face, eyes or mouth from the drawing itself; hands complete; full body visible
4. decent, non-offensive, not a caricature of any real person
If ONLY the face placement is off, say how: "eyes_up" (positive = move eyes up, as a fraction of face width,
e.g. 0.04), "eyes_apart" (positive = further apart), "mouth_down" (positive = lower), "size" (multiply eyes/mouth).
Return JSON {"ok": true|false, "face_only": true|false, "adjust": {"eyes_up": 0, "eyes_apart": 0,
"mouth_down": 0, "size": 1.0}, "reasons": ["..."]}."""


def generate_character(p, cid: str, name: str, desc: str, look: str, height: float, voice: str, save: bool = True) -> bool:
    """A new on-screen character: one standing figure (blank face) + automatic face anchors + checks."""
    lib, rg = D.library(), D.rig()
    if cid in rg["characters"]:
        return True
    style = [PARTS / "dev_stand.png", PARTS / "meera_arms.png"]
    for attempt in range(2):
        raw = WORK / f"char_{cid}_{attempt}.png"
        prompt = ("Draw ONE new character for the same flat 2D cartoon show as the reference images - exactly the "
                  "same drawing style, outline thickness, soft cel shading, skin rendering and colour feel, but a "
                  f"DIFFERENT person: {look}. Standing relaxed, arms down by the sides. " + BLANK + FIGURE +
                  " Leave clear empty green space above the head and below the feet. No text on clothes.")
        fname = f"{cid}_stand.png"
        try:
            flux(p, f"character {cid}", prompt, style, raw, 1088, 1952)
            rgba = key_out(raw, PARTS / fname)
            anc = FF.anchors(rgba, region=0.4)
        except (ArtError, ValueError) as e:
            p.state.log(f"character {cid}: {e}", "warn")
            if "budget" in str(e):
                return False
            continue
        prop = dict(FF.PROP)
        for fix in range(3):
            anc = FF.anchors(rgba, prop, region=0.4)
            rg2 = json.loads(json.dumps(rg))
            rg2["heads"][cid] = {"file": fname, "eyes": anc["eyes"], "eye_r": anc["eye_r"], "mouth": anc["mouth"],
                                 "mouth_w": anc["mouth_w"], "neck": anc["neck"], "brow_gap": anc["brow_gap"],
                                 "skin_at": anc["skin_at"], "chin": anc["chin"], "chin_x": anc["chin_x"]}
            rg2["characters"][cid] = {"primary_head": cid, "chin": anc["chin"], "stand_pose": f"{cid}_stand",
                                      "height": round(float(height), 2)}
            rg2["figures"][f"{cid}_stand"] = {"file": fname}
            try:
                sheet = _render_sheet(rg2, cid, [f"{cid}_stand"], WORK / f"char_{cid}_sheet.png")
            except Exception as e:  # noqa: BLE001
                p.state.log(f"character {cid} render: {e}", "warn")
                break
            ref = WORK / "char_ref.png"
            a, b = Image.open(_small(PARTS / "dev_stand.png", WORK / "r1.png", 900)), Image.open(_small(PARTS / "meera_arms.png", WORK / "r2.png", 900))
            both = Image.new("RGB", (a.size[0] + b.size[0] + 20, 900), (235, 235, 235))
            both.paste(a, (0, 0)); both.paste(b, (a.size[0] + 20, 0)); both.save(ref)
            v = _vision(p, CHAR_QA.replace("@DESC", f"{name}: {desc}. Looks: {look}"), [ref, _small(sheet, WORK / "char_new.png", 900)])
            p.state.log(f"character {cid} qa: {json.dumps(v)[:400]}", "info")
            if v.get("ok") and not save:
                return True
            if v.get("ok"):
                _save_json(D.RIG, rg2)
                lib["characters"][cid] = {"voice": voice, "height": round(float(height), 2), "caption_colour": "white",
                                          "desc": f"{name}: {desc}. {look}", "added": dt.date.today().isoformat()}
                lib["poses"][f"{cid}_stand"] = {"who": cid, "kind": "stand", "desc": "standing, arms down"}
                _save_json(D.LIB, lib)
                _commit([PARTS / fname, D.RIG, D.LIB], f"Library: new character {cid}")
                return True
            if not v.get("face_only"):
                p.state.log(f"character {cid} rejected: {v.get('reasons')}", "info")
                break
            adj = v.get("adjust") or {}
            prop["eye_up"] += float(adj.get("eyes_up", 0))
            prop["eye_dx"] += float(adj.get("eyes_apart", 0)) / 2
            prop["mouth_k"] += float(adj.get("mouth_down", 0)) * 2
            k = float(adj.get("size", 1.0) or 1.0)
            prop["eye_r"] *= k
            prop["mouth_w"] *= k
    (PARTS / f"{cid}_stand.png").unlink(missing_ok=True)
    return False
