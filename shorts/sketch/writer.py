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
 "game": "the one unusual thing that drives the sketch, in one sentence",
 "structure": "which structure you used (A Haan Ki Seedhi / B Galti Nahi Style Hai / C Status Ka Jhoola / D Ulta Pada / other)",
 "title_idea": "short English working title",
 "premise": "one sentence: the situation and why it is funny",
 "music": one of ["quirky_funk","bright_pop","curious_pluck","clockwork"],
 "lines": [
   {"id": "l1", "who": "dev|rocky|meera",
    "hi": "Devanagari Hindi as spoken, with 1-3 English audio tags in square brackets where the delivery changes, e.g. [nervous, quiet] [booming, proud, Kanpur accent] [deadpan] [whispering] [laughs]. Use ... for comic pauses. English words written in Devanagari as said (क्लाइंट, ऑफिस).",
    "cap": "the same line in Roman Hinglish for the on-screen caption. Max 2 lines separated by \\n, max ~36 characters per line. Break so the funny word is at the end."}
 ],
 "shots": [
   {"type": "wide|medium|close|inner|black",
    "set": "a set id (not needed for inner/black)",
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

WRITING RULES (research: docs/craft/WRITING_AND_EDITING.md)
- ONE game per sketch. Base reality in 1-2 lines, then THREE escalating beats (change the lever each time:
  specifics, emotion, stakes), one false victory or reversal, the punch, then a BUTTON that loops back to the
  first second (callback to a word or prop from the first 5 seconds).
- Status drives it: Dev low status (accepts every offer), Rocky high status (never concedes, turns every
  mistake into genius), Meera relaxed high status (still, fewest words, lowers others with one line). The
  biggest laugh is a status reversal.
- Funny word LAST: Hindi is verb-final, so restructure, or put the reveal in a separate short tag line.
- Rule of three: pattern, pattern, SHORT break. Misdirection at most once.
- Lines 3-10 words (never over 12). Real people interrupt, trail off ("haan wo... matlab..."), answer a question
  with a question. Office/tech words in English, feelings in Hindi. No stage Hindi (kripya, parantu, atyant).
  At most one UP marker (kaahe, bhaukaal, chaukas, guru) every 2-3 lines. Nobody names the joke or the emotion.
  "Sab theek hai" at most once, only as an ironic button. Every joke must be a real observation a person in
  Kanpur would recognise; no generic "vibes" jokes, no punchline that doesn't pay off its setup.
- Dev's inner voice says the truth his outer voice hides; at most 3 times, more panicked each time; never exposition.
- Meera: at most 3 lines, each lands.
- 85-110 spoken words in total, 35-45 s.
STRUCTURES that fit: A "Haan Ki Seedhi" (Dev says yes to bigger and bigger asks; outer voice calmer, inner voice
louder; button: he finally says "nahi"... to Meera's trivial ask). B "Galti Nahi, Style Hai" (Rocky's mistake gets
grander justifications; the client starts believing; Meera's one fact collapses it). C "Status Ka Jhoola" (the high
one humiliates the low one; a small reveal flips it; the former high one begs). D "Ulta Pada" (staging points to an
obvious outcome; the final reveal reframes it; Meera treats it as normal). Invent others when they fit better.

STAGING / EDITING RULES
- Shot 1 has a line (the hook) spoken at 0 s, 8 words or fewer, showing the conflict. No greetings.
- A wide shot of the set early (by shot 2-3) so geography reads. Wides for physical/spatial gags, close-ups for
  reactions and punch lines. Never three shots of the same size in a row; when cutting to the same character,
  change shot size. Dialogue shots ~1.5-4 s; long lines are split automatically.
- Silent reaction close-ups (0.6-1.2 s) are where many laughs live; give the punch reaction 1-2 s.
- inner: Dev only, at most 3. black: at most one 0.4-0.8 s beat, never first or last.
- SOUND: at most 3 sound effects in the whole video, each only for a visible action (scissors on screen, a photo
  being taken). No decorative sounds.
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
        "Kanpur would, then check every item: one game stated and served by every beat; first line <= 8 words and "
        "shows the conflict; three escalating beats on different levers; every punch ends on its funny word and is "
        "never explained; a status shift or reversal; a button that loops to the first second; Meera <= 3 lines, "
        "inner voice <= 3; no stage Hindi, no line over 12 words, no forced catchphrase; reaction shots on the big "
        "laughs; each face shows one clear idea that matches the line; 85-110 words. Rewrite whatever fails, keep "
        "what works. Return the full improved JSON plan only.\n\nDRAFT:\n"
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
