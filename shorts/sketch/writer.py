"""Scripts, revisions and metadata for Sab Theek Hai (docs/TEMPLATE.md).

write()    new episode: the writers' room v3 with gates (room.py)
revise()   owner's fix note -> the same story, smallest change, re-checked
metadata() title / description / hashtags / tags / pinned comment from the research playbook
"""
from __future__ import annotations

import json
from pathlib import Path

from . import director as D

ROOT = Path(__file__).resolve().parents[2]
WRITER_MODEL = "claude-opus-5-5"
META_MODEL = "claude-sonnet-5-5"

GRAMMAR = """
OUTPUT: one JSON object, no prose around it:
{
 "truth": "the human truth in one sentence (what viewers have lived)",
 "game": "the one unusual pattern that drives the sketch and heightens, in one sentence",
 "structure": "e.g. yes-ladder, doubling-down, status see-saw, misdirect-and-reveal, or name your own",
 "relations_cue": "how a first-time viewer learns who these people are to each other in the first 5 s",
 "loop": {"bridge": "how the last moment leads straight into the first line"},
 "props": ["object: how/where it is seen"],
 "title_idea": "short English working title",
 "premise": "one sentence: the situation and why it is funny",
 "music": one of ["quirky_funk","bright_pop","curious_pluck","clockwork"],
 "new_characters": [optional, only people NOT in world memory: {"id": "short_id", "name": "Mummy", "desc": "who
    they are and their comic trait", "voice_type": "older_woman|older_man|young_woman|young_man|service_voice",
    "relations": {"dev": "mother"}, "on_screen": false, "look": "only if on_screen: age, build, hair, clothes,
    colours (drawn automatically in the show style)", "height": 0.85-1.05 (only if on_screen; Dev is 1.0)}],
    At most ONE new on-screen person per episode; the rest are voice-only (phone/video call, voice from another
    room). A new on-screen person can only use the pose "<id>_stand" (standing, arms down) in this episode.
 "new_poses": [optional, at most 2 poses an EXISTING drawn character needs for this story: {"id": "dev_phone",
    "who": "dev", "desc": "standing, holding a phone to his right ear with his right hand, left arm down"}]
    (standing poses only; drawn automatically). Prefer existing poses; ask for a new one only when the story needs it.
 "new_sets": [optional, at most ONE place that has no drawn set yet: {"id": "short_id", "desc": "what the place looks
    like (it will be drawn automatically in the show style, empty, eye level)"}],
 "lines": [
   {"id": "l1", "who": "a character id (drawn or voice-only)", "via": "phone|offscreen (voice-only speakers only)",
    "beat": "hook|setup|escalate1|escalate2|escalate3|turn|punch|button",
    "hi": "Devanagari Hindi as spoken, with 1-3 English audio tags in square brackets where the delivery changes, e.g. [nervous, quiet] [booming, proud, Kanpur accent] [deadpan] [whispering] [laughs]. Use ... for comic pauses. English words written in Devanagari as said (क्लाइंट, ऑफिस).",
    "cap": "the same line in Roman Hinglish for the on-screen caption. Max 2 lines separated by \\n, max 42 characters per line. Break so the reveal word ends the caption.",
    "direction": "optional: what we see / how faces react"}
 ],
 "shots": [
   {"type": "wide|medium|close|inner|black", "beat": "the beat this shot belongs to (same labels as lines)",
    "set": "a drawn set id or your new_sets id (not needed for inner/black)",
    "cast": [{"who": "...", "pose": "a pose id of that character", "expr": "starting expression",
              "look": optional "left|right|camera|down|up" (wide shots aim eyes automatically),
              "events": [ {"at": 0.0-1.0, "expr": "..."} | {"at": .., "pose": "another pose of the same character and kind"} |
                          {"at": .., "move": "nod|shake|recoil|lean|double_take"} | {"at": .., "eyeroll": 1} |
                          {"at": .., "wiggle": 1} | {"at": .., "shiver": 1} | {"at": .., "look": "left|right|camera|down|up"} ] }],
    "line": "line id spoken in this shot, or omit for a silent reaction shot",
    "punch": true only on the main punch line and the button (adds the comic beat before it and drops the music),
    "hold": optional seconds to stay after the line (default 0.2; reaction shots 0.6-1.2; the punch reaction 1.0-2.0),
    "camera": optional "punch_in" (fast push-in at 60% for the single biggest reaction),
    "fx": optional [{"at": .., "fx": "shake|flash"}],
    "sfx": optional [{"at": .., "name": a sound id}]}
 ]
}

RULES: follow the WRITER CARD and the STAGING CARD above; the OWNER LESSONS override everything else.
Staging essentials: the first shot speaks the hook (starts automatically at 0.30 s); a wide early so geography reads;
reaction close-ups on the laughs; never 3 same-size shots in a row; inner voice Dev only, <=3; black beat <=1, never
first or last; <=3 sound effects, each for a visible action; the LAST shot repeats the FIRST shot's set, shot size and cast.
ACTING RULES (research: docs/craft/EXPRESSIONS.md)
- Change a character's expression once per change of THOUGHT (about every 2-4 s), never more often than every
  0.5 s. Each face shows ONE clear idea. Speakers change more than listeners; listeners mostly react with one
  clear expression change at the right moment, e.g. a slow burn annoyed -> angry, or neutral -> shock.
- Use: listening (neutral, attentive), forced_smile (Dev's polite agony), deadpan/unimpressed/skeptical (Meera),
  proud/smug/sly/excited (Rocky), shock with a recoil for big takes, double_take for a delayed realisation,
  embarrassed/sheepish after getting caught, defeated for the end of a loss, laugh for real joy.
- Gestures: nod on agreement, shake on refusal, recoil on shock, lean when pushing, eyeroll only for Meera,
  wiggle (eyebrow wiggle) only for Rocky being sly. At most one gesture per character per shot.
- Use ONLY ids from the LIBRARY. Poses marked solo only in a shot alone. Pose changes only within the same character
  and kind (stand<->stand). Every line is used in exactly one shot, by a character who is in that shot, in order.
"""


def _library_brief() -> str:
    lib = D.library()
    poses = {k: {kk: vv for kk, vv in v.items() if kk in ("who", "kind", "desc", "solo", "sets", "props")}
             for k, v in lib["poses"].items()}
    import puppet as PU  # loaded by director
    return json.dumps({"sets": {k: v["desc"] for k, v in lib["sets"].items()},
                       "characters": {k: v["desc"] for k, v in lib["characters"].items()},
                       "poses": poses, "expressions": list(PU.F.EMOTIONS),
                       "sounds": lib["sfx"]}, ensure_ascii=False, indent=1)


def lessons_brief() -> str:
    from . import lessons as L
    return L.brief()


def _system() -> str:
    from . import perf as P
    from . import world as Wd
    bible = (ROOT / "docs" / "SHOW_BIBLE.md").read_text()
    card = (ROOT / "docs" / "craft" / "WRITER_CARD.md").read_text()
    stage = (ROOT / "docs" / "craft" / "STAGING_CARD.md").read_text()
    cl = json.loads((ROOT / "creative" / "cliches.json").read_text())
    cliches = "CLICHÉ LIST (done to death; only with a clearly new angle): " + "; ".join(c["name"] for c in cl["tropes"])
    return ("You are the head writer and director of a hit Hindi cartoon sketch show for YouTube Shorts. You write "
            "sharp, natural, genuinely funny Hindi/Hinglish with a light UP flavour, and you stage it for a 2D puppet "
            "animation system.\n\n" + bible + "\n\n" + card + "\n\n" + stage + "\n\n" + lessons_brief() + "\n\n" +
            cliches + "\n\n" + P.brief() + "\n\n" + Wd.brief() +
            "\n\nANIMATION LIBRARY (sets, poses with the props they show, expressions, sounds that exist):\n" +
            _library_brief() + "\n" + GRAMMAR)


def _history_brief(history: list[dict], feedback: list[dict]) -> str:
    h = "\n".join(f"- {e['number']}: {e.get('title') or ''} | {e.get('premise') or ''}" for e in history[-40:]) or "- (none yet)"
    f = "\n".join(f"- [{x['decision']}] {x['note'][:400]}" for x in feedback[-5:] if x.get("note")) or "- (none yet)"
    return (f"EPISODES ALREADY MADE (never repeat a situation or joke engine):\n{h}\n\n"
            f"OWNER'S MOST RECENT NOTES (the general lessons are in OWNER LESSONS):\n{f}\n")


def _fix_loop(llm, plan: dict, system: str, cost: list[float], tries: int = 3) -> dict:
    for _ in range(tries):
        errs = D.validate(plan, extra=_extra(plan))
        if not errs:
            return plan
        r = llm.ask("TASK: repair\nThis plan breaks library rules. Fix ONLY these problems, keep everything else "
                    "identical, return the full JSON.\nPROBLEMS:\n- " + "\n- ".join(errs) + "\n\nPLAN:\n"
                    + json.dumps(plan, ensure_ascii=False), system=system, model=WRITER_MODEL, max_tokens=12000)
        cost[0] += r.usd
        plan = r.data
    errs = D.validate(plan, extra=_extra(plan))
    if errs:
        raise D.PlanError("; ".join(errs))
    return plan


def _extra(plan: dict) -> dict:
    """Art the plan asks for that will be drawn before render: new sets, new poses, one new on-screen person."""
    lib = D.library()
    poses = {x["id"]: x.get("who") for x in plan.get("new_poses", [])[:2] if x.get("id") and x.get("who") in lib["characters"]}
    chars = [c["id"] for c in plan.get("new_characters", []) if c.get("id") and c.get("on_screen")][:1]
    for cid in chars:
        poses[f"{cid}_stand"] = cid
    return {"sets": [x["id"] for x in plan.get("new_sets", []) if x.get("id")][:1], "poses": poses, "chars": chars}


def write(llm, history: list[dict], feedback: list[dict], number: int, idea: str = "", slot: str | None = None,
          art_cb=None, log=print) -> tuple[dict, float]:
    from . import room
    return room.write(llm, history, feedback, number, idea, slot=slot, art_cb=art_cb, log=log)


def revise(llm, plan: dict, note: str, history: list[dict], feedback: list[dict]) -> tuple[dict, str, float]:
    """Owner's fix note -> the SAME story with the smallest change that fully does it (docs/TEMPLATE.md, revision
    protocol). The result passes the hard script checks and the red-flag check before it is staged."""
    from . import gates as G
    from . import judge as J
    system = _system()
    cost = [0.0]

    def ask(prompt: str, tokens: int = 14000) -> dict:
        r = llm.ask(prompt, system=system, model=WRITER_MODEL, max_tokens=tokens, cache_system=True)
        cost[0] += r.usd
        return r.data

    d = ask("TASK: revise\nThe owner reviewed this episode and wrote the note below. Keep the SAME story, premise, "
            "characters and jokes that he didn't criticise. Change only what the note asks, but change it fully and well "
            "(if he says a line makes no sense, write a clear, funny, complete replacement; if he says someone should be "
            "on screen, stage them on screen; if he says something isn't visible, make it visible). Keep the ids of "
            "unchanged lines so their voices are reused. Never write a different story unless he explicitly asks.\n"
            f"OWNER NOTE: {note}\n\n" + _history_brief(history, feedback) +
            '\nReturn JSON: {"summary": "one short sentence: what you changed", "plan": {...full plan...}}\n\nCURRENT PLAN:\n'
            + json.dumps(plan, ensure_ascii=False))
    new = d["plan"]
    for k in ("truth", "game", "loop", "relations_cue", "props", "jokes", "premise", "title_idea", "structure"):
        if plan.get(k) and not new.get(k):
            new[k] = plan[k]
    hard = [e for e in G.script(new) if "words" not in e and "lines;" not in e]
    r = J.rubric(llm, J.script_text(new), cost, context=lessons_brief())
    if hard or r.get("red_flags"):
        d2 = ask("TASK: revise\nYour revision still has these problems. Fix them with the smallest change, keep the "
                 "story. Return the same JSON shape.\nPROBLEMS:\n- " + "\n- ".join(hard + list(r.get("red_flags") or []))
                 + "\n\nPLAN:\n" + json.dumps(new, ensure_ascii=False))
        new = d2.get("plan", new)
    new = _fix_loop(llm, new, system, cost)
    if plan.get("scorecard"):
        new["scorecard"] = {**plan["scorecard"], "revision_rubric": r.get("total"), "revision_flags": r.get("red_flags")}
    return new, d.get("summary", ""), cost[0]


def shorten(llm, plan: dict, seconds: float, durs: dict) -> tuple[dict, float]:
    system = _system()
    cost = [0.0]
    r = llm.ask(
        f"TASK: shorten\nThis episode runs {seconds:.1f} s; it must be at most 45 s. Measured line lengths (s): "
        + json.dumps(durs) + "\nCut or tighten lines and silent beats without losing the hook, the best laughs or the "
        "loop. Keep ids of unchanged lines. Return the full JSON plan only.\n\nPLAN:\n" + json.dumps(plan, ensure_ascii=False),
        system=system, model=WRITER_MODEL, max_tokens=12000)
    cost[0] += r.usd
    return _fix_loop(llm, r.data, system, cost), cost[0]


META_RULES = """
Write YouTube Shorts metadata for this episode. Research-based rules (docs/METADATA.md):
- title: 40-60 characters, Roman Hinglish, a relatable situation people recognise ("Jab ...", "POV: ...",
  "Har ... ka ek dost", "Mummy vs ..."), may use one emoji, ends with " | Sab Theek Hai". No clickbait lies,
  no brand or real-person names, no ALL CAPS.
- description: 3 short lines. Line 1 hooks with the situation (Hinglish). Line 2: the series line
  "Dev ko 'na' bolna nahi aata, Meera ko sab samajh aata hai. Roz naya episode."
  Line 3: a comment prompt that people can answer in one word or a number. Then a blank line, then the hashtags.
- hashtags: 3-5 total, always #SabTheekHai, plus 2-4 that fit the topic (e.g. #HindiComedy #DesiComedy
  #Kanpur, or a festival/exam/season tag only when the episode is about it). Never more than 5.
- tags: 6-10 search phrases (character names, "sab theek hai", "hindi cartoon comedy", topic words), total under 400 characters.
- pinned_comment: a fun question or 1-vs-2 vote in Hinglish that invites replies.
Return JSON: {"title": "...", "description": "...", "hashtags": ["#..."], "tags": ["..."], "pinned_comment": "..."}
"""


def metadata(llm, plan: dict, number: int) -> tuple[dict, float]:
    script = "\n".join(f"{ln['who']}: {ln['cap']}" for ln in plan["lines"])
    r = llm.ask("TASK: metadata\n" + META_RULES + f"\nEPISODE {number}: {plan.get('premise', '')}\nSCRIPT:\n{script}",
                model=META_MODEL, max_tokens=2000)
    m = r.data
    tags = [t for t in (m.get("hashtags") or []) if t.startswith("#")][:5]
    if "#SabTheekHai" not in tags:
        tags = ["#SabTheekHai"] + tags[:4]
    m["hashtags"] = tags
    title = (m.get("title") or plan.get("title_idea", "Sab Theek Hai")).strip()
    m["title"] = title[:95]
    desc = (m.get("description") or "").strip()
    if not any(h in desc for h in tags):
        desc += "\n\n" + " ".join(tags)
    m["description"] = desc[:4800]
    tl, total = [], 0
    for t in m.get("tags") or []:
        if total + len(t) + 1 > 400:
            break
        tl.append(t)
        total += len(t) + 1
    m["tags"] = tl
    return m, r.usd
