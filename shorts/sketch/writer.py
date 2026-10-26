"""Scripts, revisions and metadata for Sab Theek Hai, written by Claude through the API.

write()    new episode: draft -> comedy-editor pass -> library validation (repaired automatically)
revise()   apply the owner's feedback with the smallest change that does it
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
 "title_idea": "short English working title",
 "premise": "one sentence: the situation and why it is funny",
 "mechanism": "the joke mechanism in a few words (e.g. 'politeness trap + deadpan reveal')",
 "music": one of ["quirky_funk","bright_pop","curious_pluck","clockwork"],
 "lines": [
   {"id": "l1", "who": "dev|rocky|meera",
    "hi": "Devanagari Hindi as spoken, with 1-3 English audio tags in square brackets at the start or where the delivery changes, e.g. [nervous, quiet] or [booming, proud, Kanpur accent] or [deadpan] or [whispering] or [laughs]. Use ... for comic pauses. English words written in Devanagari the way they are said (क्लाइंट, ऑफिस).",
    "cap": "the same line in Roman Hinglish as the on-screen caption. Max 2 lines separated by \\n, max ~38 characters per line."}
 ],
 "shots": [
   {"type": "wide|medium|close|inner|black",
    "set": "a set id (not needed for inner/black)",
    "cast": [{"who": "...", "pose": "a pose id of that character",
              "expr": "starting expression",
              "look": optional "left|right|camera|down|up" (wide shots aim eyes automatically; set it only to override),
              "events": [ {"at": 0.0-1.0, "expr": "..."} | {"at": .., "pose": "another pose of the same character and kind"} |
                          {"at": .., "move": "nod|shake|recoil|lean|double_take"} | {"at": .., "eyeroll": 1} |
                          {"at": .., "wiggle": 1} | {"at": .., "shiver": 1} | {"at": .., "twitch": 1} |
                          {"at": .., "look": "left|right|camera|down|up"} ] }],
    "line": "line id spoken in this shot, or omit for a silent reaction shot",
    "hold": optional seconds to stay on the shot after the line (default 0.35; silent shots default 1.2),
    "camera": optional "punch_in" (fast push-in at 60% for a big reaction),
    "fx": optional [{"at": .., "fx": "shake|flash|speedlines"}],
    "sfx": optional [{"at": .., "name": a sound id}]}
 ]
}
SHOT RULES
- wide: 1-3 characters, whole bodies, same set. medium/close: exactly one character. inner: exactly one
  character (Dev's panic inner voice; the line is that character's inner voice; spiral background; Dev only).
  black: no cast, a comic beat or time cut (0.6-1.5 s), usually with a sound.
- Every line is used in exactly one shot, by a character who is in that shot. Shots follow line order.
- 'at' is a fraction of the shot (0 = start, 1 = end). Put expression changes and gestures exactly where the
  line or the reaction turns: characters must feel alive (eyebrows, eye-rolls, double takes, nods, recoils,
  wiggles, blushes via 'embarrassed', sweating via 'nervous'/'panic'). 2-4 events per character per shot is typical.
- Listeners react too: give the non-speaking characters in a wide shot expressions and events.
- Vary shot types: open on a close or medium on the hook line, use wides to show relationships, cut to a
  silent close reaction for the biggest laughs.
- Use only ids from the LIBRARY. Poses marked solo only in a shot alone. Pose changes only within the same
  character and the same kind (stand<->stand).
- Target 35-45 seconds total: about 9-13 lines plus 2-4 silent reaction/black beats. Spoken Hindi runs at
  about 2.5 words per second.
"""


def _library_brief() -> str:
    lib = D.library()
    poses = {k: {kk: vv for kk, vv in v.items() if kk in ("who", "kind", "desc", "solo", "sets")}
             for k, v in lib["poses"].items()}
    import puppet as PU  # loaded by director
    return json.dumps({"sets": {k: v["desc"] for k, v in lib["sets"].items()},
                       "characters": {k: v["desc"] for k, v in lib["characters"].items()},
                       "poses": poses, "expressions": list(PU.F.EMOTIONS),
                       "sounds": lib["sfx"]}, ensure_ascii=False, indent=1)


def _system() -> str:
    bible = (ROOT / "docs" / "SHOW_BIBLE.md").read_text()
    return ("You are the head writer and director of a hit Hindi cartoon sketch show for YouTube Shorts. "
            "You write sharp, natural, genuinely funny Hindi/Hinglish dialogue with a UP flavour, and you "
            "stage it for a 2D puppet animation system.\n\n" + bible + "\n\nLIBRARY (the only things that exist):\n"
            + _library_brief() + "\n" + GRAMMAR)


def _history_brief(history: list[dict], feedback: list[dict]) -> str:
    h = "\n".join(f"- {e['number']}: {e.get('title') or ''} | {e.get('premise') or ''}" for e in history[-40:]) or "- (none yet)"
    f = "\n".join(f"- [{x['decision']}] {x['note']}" for x in feedback[-25:] if x.get("note")) or "- (none yet)"
    return f"EPISODES ALREADY MADE (never repeat a situation or joke):\n{h}\n\nOWNER FEEDBACK SO FAR (follow it):\n{f}\n"


def _fix_loop(llm, plan: dict, system: str, cost: list[float], tries: int = 3) -> dict:
    for _ in range(tries):
        errs = D.validate(plan)
        if not errs:
            return plan
        r = llm.ask("TASK: repair\nThis plan breaks library rules. Fix ONLY these problems, keep everything else "
                    "identical, return the full JSON.\nPROBLEMS:\n- " + "\n- ".join(errs) + "\n\nPLAN:\n"
                    + json.dumps(plan, ensure_ascii=False), system=system, model=WRITER_MODEL, max_tokens=12000)
        cost[0] += r.usd
        plan = r.data
    errs = D.validate(plan)
    if errs:
        raise D.PlanError("; ".join(errs))
    return plan


def write(llm, history: list[dict], feedback: list[dict], number: int, idea: str = "") -> tuple[dict, float]:
    system = _system()
    cost = [0.0]
    ask = (f"TASK: write\nWrite episode {number} of Sab Theek Hai.\n" + _history_brief(history, feedback) +
           (f"\nThe owner asked for this idea: {idea}\n" if idea else
            "\nFirst think of 5 fresh, very relatable situations that fit the places available, pick the one with "
            "the strongest hook and the best twist, then write it.\n") +
           "Return only the JSON plan.")
    r = llm.ask(ask, system=system, model=WRITER_MODEL, max_tokens=12000)
    cost[0] += r.usd
    draft = r.data
    edit = llm.ask(
        "TASK: punchup\nYou are now the show's toughest comedy editor. Read this draft as a viewer scrolling Shorts in "
        "Kanpur would. Fix: a weak hook, any line that sounds written rather than spoken, any forced catchphrase, "
        "any joke explained twice, a soft ending, a broken loop, dead reaction shots, missing listener reactions, "
        "and anything over 45 seconds. Keep what already works. Return the full improved JSON plan only.\n\nDRAFT:\n"
        + json.dumps(draft, ensure_ascii=False), system=system, model=WRITER_MODEL, max_tokens=12000)
    cost[0] += edit.usd
    plan = _fix_loop(llm, edit.data, system, cost)
    return plan, cost[0]


def revise(llm, plan: dict, note: str, history: list[dict], feedback: list[dict]) -> tuple[dict, str, float]:
    system = _system()
    cost = [0.0]
    r = llm.ask(
        "TASK: revise\nThe owner reviewed this episode and asked for changes. Apply exactly what he asked, with the "
        "smallest change that fully does it (keep line ids of unchanged lines so their voices are reused). If his note "
        "is about timing, expressions or staging, change shots/events; if about words, change lines.\n"
        f"OWNER NOTE: {note}\n\n" + _history_brief(history, feedback) +
        "\nReturn JSON: {\"summary\": \"one short sentence: what you changed\", \"plan\": {...full plan...}}\n\nCURRENT PLAN:\n"
        + json.dumps(plan, ensure_ascii=False), system=system, model=WRITER_MODEL, max_tokens=14000)
    cost[0] += r.usd
    new = _fix_loop(llm, r.data["plan"], system, cost)
    return new, r.data.get("summary", ""), cost[0]


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
  "Har ... ka ek dost", "Rocky vs ..."), may use one emoji, ends with " | Sab Theek Hai". No clickbait lies,
  no brand or real-person names, no ALL CAPS.
- description: 3 short lines. Line 1 hooks with the situation (Hinglish). Line 2: the series line
  "Dev ko 'na' bolna nahi aata, Rocky ko sab aata hai, Meera sab samajhti hai. Roz naya episode."
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
