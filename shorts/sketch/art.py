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


def flux(p, what: str, prompt: str, refs: list[Path], out: Path, w: int = 1088, h: int = 1952) -> None:
    if not can_spend(p):
        raise ArtError(f"weekly art budget (${_cap(p):.0f}) reached")
    key = os.environ.get("BFL_API_KEY", "")
    body = {"prompt": prompt, "width": w, "height": h, "output_format": "png"}
    for i, r in enumerate(refs[:4]):
        body["input_image" if i == 0 else f"input_image_{i + 1}"] = _b64_small(r)
    hd = {"x-key": key, "accept": "application/json", "content-type": "application/json"}
    r = requests.post("https://api.bfl.ai/v1/" + MODEL, json=body, headers=hd, timeout=60)
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
    """Flat green -> transparent; keep the biggest drawing; crop with a small margin."""
    from extract_parts import key_green
    rgb = np.array(Image.open(png).convert("RGB"))
    rgba = key_green(rgb)
    a = (rgba[..., 3] > 128).astype(np.uint8)
    n, lab, st, _ = cv2.connectedComponentsWithStats(cv2.dilate(a, np.ones((15, 15), np.uint8)), 8)
    if n <= 1:
        raise ArtError("nothing drawn")
    best = 1 + int(np.argmax(st[1:, 4]))
    keep = (lab == best)
    rgba[..., 3] = (rgba[..., 3] * keep).astype(np.uint8)
    x, y, w, h, _ = st[best]
    H, W = a.shape
    if y <= 2 or y + h >= H - 2:
        raise ArtError("figure is cut by the image edge (head or feet missing)")
    m = 12
    rgba = rgba[max(0, y - m):y + h + m, max(0, x - m):x + w + m]
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
    rows = [np.hstack(tiles[i:i + 3]) for i in range(0, len(tiles), 3)]
    Image.fromarray(np.vstack(rows)).save(out)
    return out


POSE_QA = """TASK: poseqa
Image 1: our approved cartoon character in their standard pose. Image 2: the SAME character in a NEW pose,
rendered by our animation software with code-drawn eyes, brows and mouth (3 expressions per pose).
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
    for attempt in range(2):
        raw = WORK / f"pose_{pose_id}_{attempt}.png"
        prompt = ("Redraw EXACTLY the same cartoon character as in the reference image - same head, hair, skin tone, "
                  "clothes, colours, body proportions, line weight and flat 2D cartoon style - in a new pose: "
                  f"{desc}. " + BLANK + FIGURE)
        try:
            flux(p, f"pose {pose_id}", prompt, [PARTS / stand], raw, 1088, 1952)
            fname = f"{pose_id}.png"
            key_out(raw, PARTS / fname)
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
        v = _vision(p, POSE_QA.replace("@DESC", desc), [_small(PARTS / stand, WORK / "pose_ref.png"),
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
                  f"DIFFERENT person: {look}. Standing relaxed, arms down by the sides. " + BLANK + FIGURE)
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
