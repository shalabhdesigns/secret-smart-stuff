"""The show's world memory (creative/world.json): characters (drawn or voice-only), places, continuity, running gags.

- brief(): what the writer reads every episode.
- cast_voice(): voice id for any character, assigning a pooled voice to a new character on first use.
- learn(): after an episode is approved, record new characters, places and facts so later episodes stay consistent.
"""
from __future__ import annotations

import json
from pathlib import Path

from . import director as D

ROOT = Path(__file__).resolve().parents[2]
WORLD = ROOT / "creative" / "world.json"


def load() -> dict:
    return json.loads(WORLD.read_text())


def save(w: dict) -> None:
    WORLD.write_text(json.dumps(w, ensure_ascii=False, indent=1))


def brief(w: dict | None = None) -> str:
    w = w or load()
    lib = D.library()
    chars = []
    for cid, c in w["characters"].items():
        if c.get("pending"):
            continue                                    # introduced by an episode that isn't approved yet
        how = "DRAWN (can appear on screen)" if cid in lib["characters"] else "VOICE ONLY so far (phone/video call or off-screen)"
        chars.append(f"- {cid} ({c.get('name', cid)}), {how}: {c['desc']}"
                     + (f" Relations: {json.dumps(c.get('relations'), ensure_ascii=False)}" if c.get("relations") else ""))
    places = [f"- {k}: {v}" + (" [drawn set available]" if k in lib["sets"] else " [no set yet: will be drawn automatically if used]")
              for k, v in w["places"].items()]
    sets = [f"- {k}: {v['desc']}" for k, v in lib["sets"].items()]
    return ("WORLD MEMORY (keep continuity with this):\nCHARACTERS:\n" + "\n".join(chars) +
            "\nPLACES MENTIONED SO FAR:\n" + "\n".join(places) +
            "\nDRAWN SETS THAT EXIST:\n" + "\n".join(sets) +
            "\nCONTINUITY SO FAR:\n" + "\n".join(f"- {x}" for x in w.get("continuity", [])[-40:]) +
            "\nRUNNING GAGS:\n" + "\n".join(f"- {x}" for x in w.get("running_gags", [])))


def cast_voice(who: str, kind_hint: str = "", w: dict | None = None) -> str | None:
    """Voice id for a character. New voice-only characters get a pooled voice that is then fixed forever."""
    lib = D.library()
    if who in lib["characters"]:
        return lib["characters"][who]["voice"]
    w = w or load()
    c = w["characters"].get(who)
    if c and c.get("voice"):
        return c["voice"]
    pool = w["voice_pool"].get(kind_hint or (c or {}).get("voice_type", ""), []) or w["voice_pool"]["young_man"]
    used = {x.get("voice") for x in w["characters"].values()}
    voice = next((v for v in pool if v not in used), pool[0])
    return voice


def register_new(plan: dict, w: dict | None = None, ep_id: str = "") -> dict:
    """Make sure every speaker in the plan has a character record and a fixed voice."""
    w = w or load()
    lib = D.library()
    newc = {c["id"]: c for c in plan.get("new_characters", []) if c.get("id")}
    for ln in plan.get("lines", []):
        who = ln["who"]
        if who in lib["characters"] or who in w["characters"]:
            continue
        spec = newc.get(who, {})
        voice = cast_voice(who, spec.get("voice_type", ""), w)
        w["characters"][who] = {"name": spec.get("name", who.title()), "drawn": False, "role": "supporting",
                                "voice_type": spec.get("voice_type", ""), "voice": voice,
                                "desc": spec.get("desc", ""), "relations": spec.get("relations", {}),
                                **({"pending": ep_id} if ep_id else {})}
    return w


def forget_pending(ep_id: str) -> None:
    """An episode was dropped: characters it introduced (and nothing else used) disappear again."""
    w = load()
    gone = [k for k, c in w["characters"].items() if c.get("pending") == ep_id]
    for k in gone:
        del w["characters"][k]
    if gone:
        save(w)


def voices_for(plan: dict) -> dict:
    lib = D.library()
    w = load()
    out = {k: v["voice"] for k, v in lib["characters"].items()}
    w = register_new(plan, w)
    for k, c in w["characters"].items():
        if c.get("voice"):
            out[k] = c["voice"]
    return out


LEARN = """TASK: learn
An episode of our show was approved. Update the world memory so future episodes stay consistent.
Return JSON: {"continuity": ["one short fact per new thing established (who, what happened, any new detail about a
character's life, family, job, home, habits)"], "running_gags": ["only genuinely new recurring bits, usually none"],
"places": {"place_id": "short description"} (only new places), "characters": {"id": {"name": "...", "desc": "...",
"relations": {...}}} (only NEW characters or important new details about existing ones)}
EPISODE @NUM: @PREMISE
SCRIPT:
@SCRIPT
CURRENT WORLD:
@WORLD"""


def learn(llm, plan: dict, number: int, ep_id: str = "") -> float:
    w = register_new(plan)
    for c in w["characters"].values():
        if ep_id and c.get("pending") == ep_id:
            c.pop("pending")
    script = "\n".join(f"{ln['who']}: {ln['cap']}".replace("\n", " ") for ln in plan["lines"])
    prompt = (LEARN.replace("@NUM", str(number)).replace("@PREMISE", plan.get("premise", ""))
              .replace("@SCRIPT", script)
              .replace("@WORLD", json.dumps({k: w[k] for k in ("characters", "places", "continuity")}, ensure_ascii=False)[:12000]))
    r = llm.ask(prompt, model="claude-sonnet-5-5", max_tokens=2500)
    d = r.data if isinstance(r.data, dict) else {}
    for f in d.get("continuity") or []:
        w.setdefault("continuity", []).append(f"Ep {number}: {f}")
    for g in d.get("running_gags") or []:
        if g not in w.get("running_gags", []):
            w.setdefault("running_gags", []).append(g)
    for k, v in (d.get("places") or {}).items():
        w["places"].setdefault(k, v)
    for k, v in (d.get("characters") or {}).items():
        if k in w["characters"]:
            w["characters"][k]["desc"] = v.get("desc") or w["characters"][k]["desc"]
            w["characters"][k].setdefault("relations", {}).update(v.get("relations") or {})
        elif k not in D.library()["characters"]:
            w["characters"][k] = {"name": v.get("name", k), "drawn": False, "role": "supporting",
                                  "voice": cast_voice(k, v.get("voice_type", ""), w), "desc": v.get("desc", ""),
                                  "relations": v.get("relations", {})}
    for k, c in w["characters"].items():
        c.setdefault("episodes", [])
        if any(ln["who"] == k for ln in plan["lines"]) and number not in c["episodes"]:
            c["episodes"].append(number)
    save(w)
    return r.usd


def commit(msg: str, paths: list[Path] | None = None) -> None:
    """Runner only: commit world/library changes to main so every later run sees them."""
    import subprocess
    paths = paths or [WORLD]
    subprocess.run(["git", "config", "user.name", "shorts-bot"], check=False)
    subprocess.run(["git", "config", "user.email", "shorts-bot@users.noreply.github.com"], check=False)
    subprocess.run(["git", "add", *[str(x) for x in paths]], check=True)
    if subprocess.run(["git", "diff", "--cached", "--quiet"]).returncode == 0:
        return
    subprocess.run(["git", "commit", "-m", msg], check=True)
    for _ in range(3):
        subprocess.run(["git", "pull", "--rebase", "--autostash", "origin", "main"], check=False)
        if subprocess.run(["git", "push", "origin", "HEAD:main"]).returncode == 0:
            return
