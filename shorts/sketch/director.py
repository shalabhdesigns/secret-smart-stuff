"""Turn a written episode plan into an exact puppet scene + assembly spec.

The writer (an LLM) only chooses *what* happens: set, shot type, who is in it, poses, expressions,
gestures, which line is spoken, sound effects. Everything about *where* things go — positions, sizes,
floor lines, camera framing, timing — is computed here from tested rules and the real figure
geometry, so the model can never float a character, crop a head or break relative heights.

Shot types
  wide    1-3 characters on the floor of the set, full bodies, slight camera push.
  medium  one character, waist up (re-rendered larger, not upscaled), background softened.
  close   one character, head and shoulders, background blurred.
  inner   the panic spiral: one character's face, thriller background, line with reverb.
  black   a beat of black (comic pause / time cut), optional sound effect.
Event times in the plan are fractions (0..1) of the shot; real times come from the voice lengths.
"""
from __future__ import annotations

import json
import random
import sys
import wave
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts" / "puppet"))

import puppet as PU  # noqa: E402

W, H = PU.W, PU.H
RIG = ROOT / "creative" / "puppet" / "rig.json"
LIB = ROOT / "creative" / "puppet" / "library.json"
MUSIC = ["quirky_funk", "bright_pop", "curious_pluck", "clockwork"]
WIDE_SIZE = 1210          # on-screen height of a 1.0-tall standing character in a wide shot
SEATED = {"size": 960, "floor_shift": -105}   # the barber chair sits further back
LINE_AT = 0.08          # speech starts this long into a shot (first shot: 0.03)
PUNCH_PAUSE = 0.50     # stillness + silence before the main punch (docs/craft/STAGING_CARD.md; tune with retention)
HOLD = 0.2              # default gap after a line (the enemy of comedy is the unnecessary pause)
MAX_SHOT = 4.8          # longer dialogue shots are split on a pause, cutting to the next shot size
SFX_MAX = 3
OVERLAP = 70          # px two neighbours may overlap in a crowded wide shot
MIN_SHOT = 1.0
FIRST_LINE_AT = 0.30   # phones/players swallow the first ~0.1-0.2 s of audio on autoplay and loop; never start a word at 0


class PlanError(ValueError):
    pass


def library() -> dict:
    return json.loads(LIB.read_text())


def rig() -> dict:
    return json.loads(RIG.read_text())


def wav_seconds(p: Path) -> float:
    with wave.open(str(p)) as f:
        return f.getnframes() / f.getframerate()


# ----------------------------------------------------------------------------- validation
WORLD = ROOT / "creative" / "world.json"


def voice_only_ids(plan: dict | None = None) -> set[str]:
    """Characters that are heard but not drawn (phone calls, voices from another room)."""
    w = json.loads(WORLD.read_text()) if WORLD.exists() else {"characters": {}}
    lib = library()
    out = {k for k, c in w["characters"].items() if k not in lib["characters"]}
    for c in (plan or {}).get("new_characters", []):
        cid = c.get("id")
        if cid and cid not in lib["characters"]:
            if c.get("on_screen"):
                out.discard(cid)
            else:
                out.add(cid)
    return out


def validate(plan: dict, lib: dict | None = None, extra: dict | None = None) -> list[str]:
    """Problems that would make the plan unrenderable. Empty list = OK.
    extra: {"sets": [set ids that will be drawn before render], "poses": {pose id: who}} (writing time only)."""
    lib = lib or library()
    extra = extra or {}
    errs: list[str] = []
    rg = rig()
    sets_ok = set(lib["sets"]) | set(extra.get("sets", []))
    new_poses = extra.get("poses", {})
    new_chars = set(extra.get("chars", []))
    voice_only = voice_only_ids(plan)
    lines = {ln.get("id"): ln for ln in plan.get("lines", [])}
    if not lines:
        errs.append("no lines")
    for ln in lines.values():
        if ln.get("who") not in lib["characters"] and ln.get("who") not in voice_only and ln.get("who") not in new_chars:
            errs.append(f"line {ln.get('id')}: unknown speaker {ln.get('who')} (new people must be in new_characters)")
        if not ln.get("hi") or not ln.get("cap"):
            errs.append(f"line {ln.get('id')}: needs 'hi' (Devanagari) and 'cap' (Roman caption)")
    used = []
    emotions = set(PU.F.EMOTIONS)
    for i, s in enumerate(plan.get("shots", [])):
        typ = s.get("type")
        if typ not in ("wide", "medium", "close", "inner", "black"):
            errs.append(f"shot {i}: bad type {typ}")
            continue
        if typ != "black" and s.get("set") not in sets_ok and typ != "inner":
            errs.append(f"shot {i}: unknown set {s.get('set')}")
        cast = s.get("cast", [])
        if typ == "black":
            if cast:
                errs.append(f"shot {i}: black shot has no cast")
        elif not cast:
            errs.append(f"shot {i}: no cast")
        if typ in ("medium", "close", "inner") and len(cast) != 1:
            errs.append(f"shot {i}: {typ} shot needs exactly one character")
        if typ == "wide" and len(cast) > 3:
            errs.append(f"shot {i}: at most 3 characters")
        whos = [c.get("who") for c in cast]
        if len(set(whos)) != len(whos):
            errs.append(f"shot {i}: a character appears twice")
        for c in cast:
            pose = c.get("pose")
            if c.get("who") in voice_only:
                errs.append(f"shot {i}: {c.get('who')} is voice-only and can't be in a shot's cast")
                continue
            if pose in new_poses:
                if new_poses[pose] != c.get("who"):
                    errs.append(f"shot {i}: new pose {pose} is not {c.get('who')}'s")
                for e in c.get("events", []):
                    if "pose" in e:
                        errs.append(f"shot {i}: no pose changes from a new pose")
                continue
            if pose not in rg["figures"]:
                errs.append(f"shot {i}: unknown pose {pose}")
                continue
            base = pose.replace("_bowl", "").replace("_tuft", "")
            meta = lib["poses"].get(base)
            if not meta or meta["who"] != c.get("who"):
                errs.append(f"shot {i}: pose {pose} is not {c.get('who')}'s")
                continue
            if meta.get("sets") and typ != "inner" and s.get("set") not in meta["sets"]:
                errs.append(f"shot {i}: pose {pose} only works in {meta['sets']}")
            if meta.get("solo") and len(cast) > 1:
                errs.append(f"shot {i}: pose {pose} only in a shot alone")
            if c.get("expr", "neutral") not in emotions:
                errs.append(f"shot {i}: unknown expression {c.get('expr')}")
            for e in c.get("events", []):
                if "expr" in e and e["expr"] not in emotions:
                    errs.append(f"shot {i}: unknown expression {e['expr']}")
                if "pose" in e:
                    pb = e["pose"].replace("_bowl", "").replace("_tuft", "")
                    pm = lib["poses"].get(pb)
                    if e["pose"] not in rg["figures"] or not pm or pm["who"] != c.get("who") or pm["kind"] != meta["kind"]:
                        errs.append(f"shot {i}: bad pose change {e['pose']}")
                    elif pm.get("solo") and len(cast) > 1:
                        errs.append(f"shot {i}: pose {e['pose']} only in a shot alone")
                if "move" in e and e["move"] not in ("nod", "shake", "recoil", "lean", "double_take"):
                    errs.append(f"shot {i}: unknown move {e['move']}")
                if not 0 <= float(e.get("at", 0)) <= 1:
                    errs.append(f"shot {i}: event 'at' must be 0..1")
        ln = s.get("line")
        if ln:
            if ln not in lines:
                errs.append(f"shot {i}: unknown line {ln}")
            elif lines[ln]["who"] in voice_only:
                if typ in ("black", "inner"):
                    errs.append(f"shot {i}: a voice-only line needs a shot of someone listening")
            elif lines[ln]["who"] not in whos and not (typ == "black"):
                errs.append(f"shot {i}: speaker {lines[ln]['who']} is not in the shot")
            used.append(ln)
        for fx in s.get("sfx", []):
            if fx.get("name") not in lib["sfx"]:
                errs.append(f"shot {i}: unknown sound {fx.get('name')}")
    shots = plan.get("shots", [])
    kinds = [s.get("type") for s in shots]
    if kinds.count("black") > 1:
        errs.append("at most one black beat")
    if kinds and (kinds[0] == "black" or kinds[-1] == "black"):
        errs.append("a black beat can't be the first or the last shot (it kills the hook / the loop)")
    if kinds.count("inner") > 3:
        errs.append("at most 3 inner-voice shots")
    if sum(len(s.get("sfx", [])) for s in shots) > SFX_MAX:
        errs.append(f"at most {SFX_MAX} sound effects in the whole video")
    if shots and not shots[0].get("line"):
        errs.append("the first shot must start with a line (hook at 0 s)")
    run = 1
    for k in range(1, len(kinds)):
        same = kinds[k] == kinds[k - 1] and kinds[k] in ("wide", "medium", "close")
        run = run + 1 if same else 1
        if run > 2:
            errs.append(f"shots {k - 2}-{k}: three {kinds[k]} shots in a row; vary the shot size")
            break
    if sum(1 for s in shots if s.get("punch")) > 2:
        errs.append("mark at most 2 shots as punch (the main punch and the button)")
    missing = set(lines) - set(used)
    if missing:
        errs.append(f"lines never used: {sorted(missing)}")
    dup = {x for x in used if used.count(x) > 1}
    if dup:
        errs.append(f"lines used twice: {sorted(dup)}")
    return errs


# ----------------------------------------------------------------------------- layout
def _geom(rg: dict, parts: Path, who: str, pose: str, x: float, floor: float, size: float) -> dict:
    a = PU.FigureActor(rg, parts, {"who": who, "pose": pose, "x": x, "floor": floor, "size": size}, 1.0)
    return a.geometry()


def _pose_set(c: dict) -> list[str]:
    return [c["pose"]] + [e["pose"] for e in c.get("events", []) if "pose" in e]


def _union_geom(rg, parts, c, x, floor, size) -> dict:
    gs = [_geom(rg, parts, c["who"], p, x, floor, size) for p in _pose_set(c)]
    box = (min(g["box"][0] for g in gs), min(g["box"][1] for g in gs), max(g["box"][2] for g in gs), max(g["box"][3] for g in gs))
    return {"chin": gs[0]["chin"], "fw": gs[0]["fw"], "box": box}


def layout_wide(rg: dict, parts: Path, lib: dict, set_name: str, cast: list[dict]) -> list[dict]:
    """x / floor / size for each character so that nobody overlaps and nobody leaves the frame."""
    floor0 = lib["sets"][set_name]["floor"]
    size = WIDE_SIZE * (0.92 if len(cast) == 3 else 1.0)
    for _ in range(12):
        placed, widths = [], []
        for c in cast:
            seated = lib["poses"][c["pose"].replace("_bowl", "").replace("_tuft", "")]["kind"] == "seated"
            sz = size * SEATED["size"] / WIDE_SIZE if seated else size
            fl = floor0 + (SEATED["floor_shift"] if seated else 0)
            g = _union_geom(rg, parts, c, 0.0, fl, sz)
            widths.append(g["box"][2] - g["box"][0])
            placed.append({"size": sz, "floor": fl, "left_off": g["box"][0], "chin_y": g["chin"][1], "top": g["box"][1]})
        n = len(cast)
        gap = (W - 40 - sum(widths)) / (n + 1)
        if gap >= 14 or size < 900:
            break
        if n > 1 and (W - 40 - sum(widths) + OVERLAP * (n - 1)) >= 0 and size < 1080:
            break                                        # small overlap (one stands just behind the other)
        size *= 0.95
    if gap >= 0:
        xs, cur, step = [], 20 + gap, gap
    else:                                                # overlap evenly, never past the frame edges
        step = (W - 40 - sum(widths)) / max(1, len(cast) - 1)
        xs, cur = [], 20.0
    for p, w in zip(placed, widths):
        xs.append(cur - p["left_off"])                 # chin x so the box starts at cur
        cur += w + step
    return [{"x": round(float(x), 1), "floor": p["floor"], "size": round(p["size"], 1), "chin_y": p["chin_y"], "top": p["top"]}
            for x, p in zip(xs, placed)]


def frame_single(rg: dict, parts: Path, lib: dict, set_name: str, c: dict, typ: str) -> dict:
    """Re-render one character larger instead of zooming the camera (keeps lines crisp)."""
    floor0 = lib["sets"][set_name]["floor"]
    seated = lib["poses"][c["pose"].replace("_bowl", "").replace("_tuft", "")]["kind"] == "seated"
    size = SEATED["size"] if seated else WIDE_SIZE * 0.95
    fl = floor0 + (SEATED["floor_shift"] if seated else 0)
    g = _union_geom(rg, parts, c, W / 2, fl, size)
    fw = g["fw"]
    Z = {"medium": 1.45, "close": 2.1}[typ] * (WIDE_SIZE * 0.95 / size)
    bw = g["box"][2] - g["box"][0]
    Z = max(1.0, min(Z, (W - 40) / bw if typ == "medium" else Z))   # wide poses: keep both arms in frame
    chin_target = {"medium": 0.40, "close": 0.47}[typ] * H
    # canvas point (cx, cy) maps to the screen centre; chin must land at chin_target
    cx = g["chin"][0]
    cy = g["chin"][1] - (chin_target - H / 2) / Z
    cx = min(max(cx, W / (2 * Z)), W - W / (2 * Z))
    cy = min(max(cy, H / (2 * Z)), H - H / (2 * Z))
    x2 = W / 2 + (W / 2 - cx) * Z          # character drawn at canvas centre before scaling
    floor2 = H / 2 + (fl - cy) * Z
    blur = {"medium": 4, "close": 7}[typ]
    return {"x": round(x2, 1), "floor": round(floor2, 1), "size": round(size * Z, 1),
            "bg_view": {"zoom": round(Z, 3), "cx": round(cx / W, 4), "cy": round(cy / H, 4), "blur": blur},
            "head_y": round(H / 2 + (g["chin"][1] - 0.55 * fw - cy) * Z, 1)}


def frame_inner(rg: dict, parts: Path, c: dict) -> dict:
    a = PU.FigureActor(rg, parts, {"who": c["who"], "pose": c["pose"], "x": W / 2, "neck_y": 1000, "size": 1000}, 1.0)
    fw = a.geometry()["fw"]
    size = 1000 * 470.0 / fw
    return {"x": W / 2, "neck_y": 1080, "size": round(size, 1)}


def _look_at(src_x: float, dst_x: float, dy: float) -> list[float]:
    d = 0.7 if dst_x > src_x else -0.7
    return [d, 0.3 if dy > 60 else (-0.3 if dy < -60 else 0.0)]


# ----------------------------------------------------------------------------- continuity
def keep_continuity(plan: dict) -> dict:
    """An inner-voice close-up shows the character exactly as they are in the scene around it
    (same pose, e.g. still sitting in the barber chair), never a different outfit or posture."""
    shots = [dict(s) for s in plan["shots"]]
    for i, s in enumerate(shots):
        if s["type"] != "inner" or not s.get("cast"):
            continue
        who = s["cast"][0]["who"]
        near = None
        for j in list(range(i - 1, -1, -1)) + list(range(i + 1, len(shots))):
            o = shots[j]
            if o["type"] in ("inner", "black"):
                continue
            c = next((c for c in o.get("cast", []) if c["who"] == who), None)
            if c:
                poses = [c["pose"]] + [e["pose"] for e in c.get("events", []) if "pose" in e]
                near = poses[-1] if j < i else poses[0]
                break
        if near:
            s["cast"] = [{**s["cast"][0], "pose": near, "events": [e for e in s["cast"][0].get("events", []) if "pose" not in e]}]
    return {**plan, "shots": shots}


# ----------------------------------------------------------------------------- long-shot splitting
NEXT_SIZE = {"wide": "close", "medium": "close", "close": "medium"}


def _pauses(wav: Path) -> list[float]:
    """Mid-points of silent gaps (>= 0.12 s) inside a voice line."""
    import numpy as np
    with wave.open(str(wav)) as f:
        x = np.frombuffer(f.readframes(f.getnframes()), np.int16).astype(np.float32) / 32768
        sr = f.getframerate()
    hop = sr // 100
    env = np.array([np.sqrt((x[i:i + hop] ** 2).mean() + 1e-12) for i in range(0, len(x) - hop, hop)])
    if not len(env):
        return []
    quiet = 20 * np.log10(env + 1e-9) < (20 * np.log10(np.percentile(env, 95) + 1e-9) - 30)
    out, start = [], None
    for i, q in enumerate(quiet):
        if q and start is None:
            start = i
        if not q and start is not None:
            if i - start >= 12:
                out.append((start + i) / 2 / 100)
            start = None
    return out


def split_long(plan: dict, durs: dict, lines_dir: Path) -> dict:
    """Cut dialogue shots longer than MAX_SHOT at a natural pause, the second part one shot size closer."""
    out = []
    caps = {ln["id"]: ln["cap"] for ln in plan["lines"]}
    for s in plan["shots"]:
        lid, typ = s.get("line"), s["type"]
        if not lid or typ not in NEXT_SIZE:
            out.append(s)
            continue
        d = durs[lid]
        total = LINE_AT + d + float(s.get("hold", HOLD))
        if total <= MAX_SHOT:
            out.append(s)
            continue
        cands = [p for p in _pauses(lines_dir / f"{lid}.wav") if 0.3 * d <= p <= 0.72 * d]
        if not cands:
            out.append(s)
            continue
        sp = min(cands, key=lambda p: abs(p - d / 2))
        cut = LINE_AT + sp
        speaker = next((c for c in s["cast"] if c["who"] == next(ln["who"] for ln in plan["lines"] if ln["id"] == lid)), s["cast"][0])
        a = {**s, "line_end": sp, "hold": 0.0}
        b = {**s, "type": NEXT_SIZE[typ], "line_offset": sp, "punch": False, "punch_tail": bool(s.get("punch")),
             "sfx": [], "fx": [], "camera": None,
             "cast": [dict(speaker)]}
        b.pop("camera", None)
        parts = caps[lid].split("\n")
        if len(parts) >= 2:
            a["cap"], b["cap"] = parts[0], "\n".join(parts[1:])
        # events go to the part they fall in
        def side(c, first):
            evs = []
            for e in c.get("events", []):
                t = float(e.get("at", 0)) * total
                if (t < cut) == first:
                    evs.append({**e, "at": round(t / cut if first else (t - cut) / max(0.1, total - cut), 3)})
            return evs
        a["cast"] = [{**c, "events": side(c, True)} for c in s["cast"]]
        b["cast"] = [{**speaker, "events": side(speaker, False)}]
        # the second part starts from the expression the speaker ended the first part with
        last = [e["expr"] for e in speaker.get("events", []) if "expr" in e and float(e.get("at", 0)) * total < cut]
        if last:
            b["cast"][0]["expr"] = last[-1]
        out += [a, b]
    return {**plan, "shots": out}


# ----------------------------------------------------------------------------- build
def build(plan: dict, lines_dir: Path, shots_dir: Path, name: str, seed: int = 0) -> tuple[dict, dict]:
    """Return (scene, assemble_spec). Lines must already be in lines_dir as <id>.wav."""
    lib, rg = library(), rig()
    errs = validate(plan, lib)
    if errs:
        raise PlanError("; ".join(errs))
    parts = RIG.parent / rg.get("parts_dir", ".")
    rng = random.Random(seed)
    lines = {ln["id"]: ln for ln in plan["lines"]}
    durs = {lid: wav_seconds(lines_dir / f"{lid}.wav") for lid in lines}
    voice_only = voice_only_ids(plan)
    wnames = json.loads(WORLD.read_text())["characters"] if WORLD.exists() else {}
    names = {c["id"]: c.get("name", c["id"]) for c in plan.get("new_characters", []) if c.get("id")}
    names.update({k: v.get("name", k) for k, v in wnames.items()})
    plan = keep_continuity(plan)
    plan = split_long(plan, durs, lines_dir)
    scene = {"lines_dir": str(lines_dir), "lines": list(lines), "shots": []}
    asm = {"name": name, "music": {"file": f"assets/music/{plan.get('music') or rng.choice(MUSIC)}.mp3",
                                   "gain_db": -22, "duck_db": 4, "mute_shots": [], "mute_ranges": []}, "shots": []}
    clock = 0.0
    for i, s in enumerate(plan["shots"]):
        typ = s["type"]
        lid = s.get("line")
        off = float(s.get("line_offset", 0.0))
        end = float(s.get("line_end", durs[lid])) if lid else 0.0
        talk = (end - off) if lid else 0.0
        lead = 0.0 if off else (FIRST_LINE_AT if i == 0 else (PUNCH_PAUSE if s.get("punch") else LINE_AT))
        line_at = lead - off                                  # where the line starts relative to this shot
        if typ == "black":
            hold = min(0.8, max(0.4, float(s.get("hold", 0.6))))
        else:
            hold = float(s.get("hold", HOLD if lid else 1.0))
            if (s.get("punch") and "line_end" not in s) or s.get("punch_tail"):
                hold = max(hold, 0.9)                         # let the punch land before the cut
        dur = round(max(MIN_SHOT if typ != "black" else 0.4, (lead + talk + hold) if lid else hold), 2)
        if s.get("punch") and lid and not off:                # drop the music just before the punch
            asm["music"]["mute_ranges"].append([round(clock + lead - 0.4, 2), round(clock + dur, 2)])
        speaker = lines[lid]["who"] if lid else ""
        shot: dict = {"dur": dur}
        actors = []
        if typ == "black":
            shot["bg"] = "black"
            asm["music"]["mute_shots"].append([i, i])
        elif typ == "inner":
            shot["bg"] = "spiral"
            c = s["cast"][0]
            f = frame_inner(rg, parts, c)
            actors.append({"who": c["who"], "pose": c["pose"], **f, "expr": c.get("expr", "panic"), "dart": True, "c": c})
            shot["fx"] = [{"t": 0, "cam": {"zoom": 1.12, "cx": 540, "cy": 760}, "over": dur - 0.1},
                          {"t": 0, "shake": 0.5, "amp": 14},
                          {"t": round(dur * 0.15, 2), "sweat": 1, "x": 880, "y": 420, "size": 46, "dur": 2.0}]
            asm["music"]["mute_shots"].append([i, i])
        elif typ == "wide":
            shot["bg"] = lib["sets"][s["set"]]["bg"]
            pos = layout_wide(rg, parts, lib, s["set"], s["cast"])
            for c, p in zip(s["cast"], pos):
                actors.append({"who": c["who"], "pose": c["pose"], "x": p["x"], "floor": p["floor"], "size": p["size"],
                               "expr": c.get("expr", "neutral"), "c": c, "_chin_y": p["chin_y"]})
            # look at whoever is speaking (speaker looks at the nearest other person)
            for a in actors:
                if "look" in a["c"]:
                    continue
                others = [o for o in actors if o is not a]
                if not others:
                    a["look"] = [0, 0]
                    continue
                tgt = next((o for o in others if o["who"] == speaker), None) or min(others, key=lambda o: abs(o["x"] - a["x"]))
                a["look"] = _look_at(a["x"], tgt["x"], tgt["_chin_y"] - a["_chin_y"])
            top = min(a["_chin_y"] for a in actors)
            shot["fx"] = [{"t": 0, "cam": {"zoom": 1.03, "cx": 540, "cy": 1000}},
                          {"t": 0, "cam": {"zoom": 1.07, "cx": 540, "cy": max(900, min(1100, top + 300))}, "over": dur}]
        else:
            shot["bg"] = lib["sets"][s["set"]]["bg"]
            c = s["cast"][0]
            f = frame_single(rg, parts, lib, s["set"], c, typ)
            shot["bg_view"] = f.pop("bg_view")
            f.pop("head_y")
            actors.append({"who": c["who"], "pose": c["pose"], **f, "expr": c.get("expr", "neutral"), "c": c})
        cam = s.get("camera")
        if cam == "punch_in" and typ in ("medium", "close", "wide"):
            at = round(dur * float(s.get("camera_at", 0.6)), 2)
            shot.setdefault("fx", []).append({"t": at, "cam": {"zoom": 1.25, "cx": 540, "cy": 760}, "over": 0.25})
        for fx in s.get("fx", []):
            t = round(dur * float(fx.get("at", 0)), 2)
            if fx.get("fx") == "shake":
                shot.setdefault("fx", []).append({"t": t, "shake": 0.45, "amp": 16})
            elif fx.get("fx") == "flash":
                shot.setdefault("fx", []).append({"t": t, "flash": 0.25})
            elif fx.get("fx") == "speedlines":
                shot.setdefault("fx", []).append({"t": t, "speedlines": 0.6})
        out_actors = []
        for a in actors:
            c = a.pop("c")
            a.pop("_chin_y", None)
            if "look" in c:
                lk = c["look"]
                a["look"] = {"left": [-0.8, 0], "right": [0.8, 0], "camera": [0, 0], "down": [0, 0.7], "up": [0, -0.6]}.get(lk, lk) \
                    if isinstance(lk, str) else lk
            a.setdefault("look", [0, 0])
            if c["who"] == speaker and lid:
                a["lines"] = [{"line": lid, "at": round(line_at, 3)}]
            evs, last_expr = [], -9.0
            for e in sorted(c.get("events", []), key=lambda e: float(e.get("at", 0))):
                if "twitch" in e:
                    continue
                if "expr" in e:                                # an expression must hold >= ~0.45 s to read
                    if dur * float(e.get("at", 0)) - last_expr < 0.45:
                        continue
                    last_expr = dur * float(e.get("at", 0))
                t = round(dur * float(e.get("at", 0)), 2)
                ee = {k: v for k, v in e.items() if k != "at"}
                if "move" in ee:
                    ee.setdefault("dur", 0.6)
                for key in ("eyeroll", "wiggle", "shiver"):
                    if key in ee:
                        ee[key] = 1
                        ee.setdefault("dur", {"eyeroll": 0.75, "wiggle": 0.7, "shiver": 0.7}[key])
                if "look" in ee and isinstance(ee["look"], str):
                    ee["look"] = {"left": [-0.8, 0], "right": [0.8, 0], "camera": [0, 0], "down": [0, 0.7], "up": [0, -0.6]}.get(ee["look"], [0, 0])
                evs.append({"t": t, **ee})
            a["events"] = evs
            a["seed"] = i
            out_actors.append(a)
        if out_actors:
            shot["actors"] = out_actors
        scene["shots"].append(shot)
        sounds = []
        if lid and not off:                                   # a split line's audio plays once, across the cut
            via = lines[lid].get("via", "phone") if speaker in voice_only else ""
            sounds.append({"url": str(lines_dir / f"{lid}.wav"), "at": round(lead, 3), "voice": True,
                           "gain_db": 3 if typ == "inner" else 0, **({"reverb": True} if typ == "inner" else {}),
                           **({"phone": True} if via == "phone" else {}), **({"offscreen": True} if via == "offscreen" else {})})
        if typ == "inner":
            sounds.append({"url": "assets/sfx/spiral.mp3", "at": 0, "gain_db": -11})
        for fx in s.get("sfx", []):
            sounds.append({"url": f"assets/sfx/{fx['name']}.mp3", "at": round(dur * float(fx.get("at", 0)), 2),
                           "gain_db": float(fx.get("gain_db", -4))})
        ash = {"url": str(shots_dir / f"shot{i:02d}.mp4"), "speaker": speaker, "keep_audio": False, "sounds": sounds,
               "beat": s.get("beat", ""), "_line_dur": round(talk, 3) if lid and not off else 0.0}
        if lid:
            from .gates import wrap
            ash["caption"] = wrap(s.get("cap") or lines[lid]["cap"])
            if speaker in voice_only and not off:
                ash["caption"] = f"{names.get(speaker, speaker.title())}: " + ash["caption"]
            ash["caption_at"] = max(0.0, round(lead - 0.05, 2))
            if typ == "inner":
                ash["inner"] = True
        asm["shots"].append(ash)
        clock += dur
    return scene, asm


def total_seconds(scene: dict) -> float:
    return round(sum(s["dur"] for s in scene["shots"]), 2)
