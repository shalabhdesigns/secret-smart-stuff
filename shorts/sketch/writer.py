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
    "hi": "Devanagari Hindi as spoken, with 1-3 English audio tags in square brackets where the delivery changes, e.g. [nervous, quiet] [booming, proud, Kanpur accent] [deadpan] [whispering] [laughs]. Use ... for comic pauses. English words written in Devanagari as said (क्लाइंट, ऑफिस).",
    "cap": "the same line in Roman Hinglish for the on-screen caption. Max 2 lines separated by \\n, max ~36 characters per line. Break so the funny word is at the end."}
 ],
 "shots": [
   {"type": "wide|medium|close|inner|black",
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

WRITING RULES (research: docs/craft/COMEDY_WRITING.md, docs/craft/WRITING_AND_EDITING.md)
- STORY FIRST. Pick the cast and the place the story needs. Dev is the usual lead; Meera when the story is at home
  or needs her deadpan; Rocky and the barber shop ONLY when the story is about them. New people and places are
  welcome (see new_characters / new_sets).
- ONE game per sketch. Base reality in 1-2 lines, then THREE escalating beats (change the lever each time:
  specifics, emotion, stakes), a twist or reversal, the punch, then a BUTTON that loops back to the first second.
- Status drives it: whoever is high status falls; the biggest laugh is a status reversal.
- Funny word LAST: Hindi is verb-final, so restructure, or put the reveal in a separate short tag line.
- Rule of three: pattern, pattern, SHORT break. Misdirection at most once.
- Lines 3-10 words (never over 12). Real people interrupt, trail off ("haan wo... matlab..."), answer a question
  with a question. Office/tech words in English, feelings in Hindi. No stage Hindi (kripya, parantu, atyant).
  Light UP flavour. Nobody names the joke or the emotion. Every joke is a real observation an ordinary Indian
  viewer recognises; no generic "vibes" jokes, no punchline that doesn't pay off its setup.
- Dev's inner voice says the truth his outer voice hides; at most 3 times, more panicked each time; never exposition.
- 85-110 spoken words in total, 35-45 s.

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
    from . import world as Wd
    bible = (ROOT / "docs" / "SHOW_BIBLE.md").read_text()
    craft = (ROOT / "docs" / "craft" / "COMEDY_WRITING.md").read_text()
    return ("You are the head writer and director of a hit Hindi cartoon sketch show for YouTube Shorts. "
            "You write sharp, natural, genuinely funny Hindi/Hinglish dialogue with a UP flavour, and you "
            "stage it for a 2D puppet animation system.\n\n" + bible + "\n\n" + craft + "\n\n" + Wd.brief() +
            "\n\nANIMATION LIBRARY (poses, expressions, sounds that exist):\n" + _library_brief() + "\n" + GRAMMAR)


def _history_brief(history: list[dict], feedback: list[dict]) -> str:
    h = "\n".join(f"- {e['number']}: {e.get('title') or ''} | {e.get('premise') or ''}" for e in history[-40:]) or "- (none yet)"
    f = "\n".join(f"- [{x['decision']}] {x['note']}" for x in feedback[-25:] if x.get("note")) or "- (none yet)"
    return f"EPISODES ALREADY MADE (never repeat a situation or joke):\n{h}\n\nOWNER FEEDBACK SO FAR (follow it):\n{f}\n"


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


PANEL = ("Five real Indian Shorts viewers: Ankit (19, college student, Lucknow), Priya (26, IT employee, Noida), "
         "Sunita (36, homemaker, Kanpur), Ramesh (48, shop owner, Kanpur), Zoya (23, works in a call centre, Bhopal). "
         "They scroll fast, they've seen every cliché, they laugh only at things that are TRUE about their lives and "
         "said in a way they couldn't have said themselves. They share only what makes them say 'yeh toh bilkul "
         "mummy/papa/mera dost hai'.")


def _today() -> str:
    import datetime as dt
    return dt.date.today().strftime("%d %B %Y")


def write(llm, history: list[dict], feedback: list[dict], number: int, idea: str = "") -> tuple[dict, float]:
    system = _system()
    cost = [0.0]

    def ask(prompt: str, tokens: int = 8000) -> dict:
        r = llm.ask(prompt, system=system, model=WRITER_MODEL, max_tokens=tokens)
        cost[0] += r.usd
        return r.data

    hist = _history_brief(history, feedback)
    # 1. ideas
    ideas = ask(
        f"TASK: ideate\nToday is {_today()}. Pitch 12 DIFFERENT premises for episode {number}.\n{hist}\n"
        + (f"The owner asked for: {idea}\n" if idea else "") +
        "Rules: start from a real, specific moment almost every Indian has lived (family, relatives, WhatsApp groups, "
        "landlords, exams and results, office and bosses, shaadi season, festivals coming up, trains, cricket, "
        "money, food, neighbours, delivery apps, friends, siblings, parents and technology...). Choose the cast and "
        "place the STORY needs - Rocky and the barber shop only if the story is truly about them. Each premise must "
        "have a twist nobody sees coming and a button that makes people replay it. No premise may repeat an earlier "
        "episode's situation or joke engine.\nReturn JSON {\"ideas\": [{\"id\": 1, \"moment\": \"the real-life "
        "moment\", \"game\": \"the comic engine in one line\", \"beats\": [\"beat 1\", \"beat 2\", \"beat 3\"], "
        "\"twist\": \"...\", \"button\": \"...\", \"cast\": [\"ids\"], \"place\": \"...\", \"share_trigger\": "
        "\"who would forward this to whom, and the caption they'd write\"}]}", 9000)["ideas"]
    # 2. audience panel picks
    pick = ask(
        f"TASK: panel\n{PANEL}\nEach panelist rates every premise 1-10 for: relatable (has this happened to me or my "
        "family?), lol (would I actually laugh out loud?), share (would I forward it?). Be harsh: average ideas get 4-6. "
        "Then pick the TWO premises with the highest combined score and say what would make each funnier.\n"
        "IDEAS:\n" + json.dumps(ideas, ensure_ascii=False) +
        "\nReturn JSON {\"scores\": [{\"id\": 1, \"total\": 0}], \"top\": [{\"id\": 1, \"why\": \"...\", "
        "\"make_it_funnier\": \"...\"}]}", 5000)
    top = pick["top"][:2]
    byid = {x["id"]: x for x in ideas}
    # 3. two full scripts
    scripts = []
    for t in top:
        sc = ask(
            "TASK: screenplay\nWrite the full 35-45 s script for this premise. Comedy first: every line must earn its "
            "place; the funniest version of each joke; real Hinglish people speak. Include expressions and reactions "
            "as directions.\nPREMISE:\n" + json.dumps(byid.get(t["id"], t), ensure_ascii=False) +
            "\nPANEL NOTE: " + t.get("make_it_funnier", "") +
            "\nReturn JSON {\"title_idea\": \"...\", \"premise\": \"...\", \"game\": \"...\", "
            "\"new_characters\": [...], \"new_sets\": [...], \"new_poses\": [...], \"lines\": [{\"who\": \"id\", \"hi\": "
            "\"Devanagari with audio tags\", \"cap\": \"Roman Hinglish caption\", \"direction\": \"what we see / "
            "how faces react\"}]}", 7000)
        scripts.append(sc)
    # 4. table read + 5. punch-up (+ one more round if still not good enough)
    best = None
    for rnd in range(2):
        cands = scripts if best is None else [best]
        tr = ask(
            f"TASK: tableread\n{PANEL}\nThey watch these scripts as if they were finished Shorts. For each: score 1-10 "
            "for relatable, lol, share, rewatch; quote the lines that got a real laugh and the lines that got nothing; "
            "then the head writer lists exact fixes (sharper word choices, a better twist, a tighter button, cuts).\n"
            "SCRIPTS:\n" + json.dumps(cands, ensure_ascii=False) +
            "\nReturn JSON {\"winner\": 0, \"scores\": [{\"relatable\": 0, \"lol\": 0, \"share\": 0, "
            "\"rewatch\": 0}], \"fixes\": [\"...\"]}", 5000)
        win = cands[int(tr.get("winner", 0)) if int(tr.get("winner", 0)) < len(cands) else 0]
        sc_ = (tr.get("scores") or [{}])[int(tr.get("winner", 0)) if int(tr.get("winner", 0)) < len(tr.get("scores") or [1]) else 0]
        best = ask(
            "TASK: punchup\nApply every fix below to the winning script and make it the funniest possible version. "
            "Keep what got laughs. Return the same JSON shape.\nFIXES:\n- " + "\n- ".join(tr.get("fixes") or []) +
            "\nSCRIPT:\n" + json.dumps(win, ensure_ascii=False), 7000)
        if min(sc_.get("lol", 0), sc_.get("relatable", 0)) >= 8:
            break
    # 6. staging
    plan = ask(
        "TASK: stage\nTurn this final script into the full production JSON plan (OUTPUT format in the system prompt). "
        "Keep every line exactly (ids l1, l2, ...). Stage it for maximum comedy: hook shot first, reaction close-ups on "
        "the laughs, the punch and the button marked, faces that match every beat.\nSCRIPT:\n"
        + json.dumps(best, ensure_ascii=False), 12000)
    for k in ("new_characters", "new_sets", "new_poses", "game"):
        if best.get(k) and not plan.get(k):
            plan[k] = best[k]
    plan = _fix_loop(llm, plan, system, cost)
    plan["writers_room"] = {"ideas": len(ideas), "picked": [t.get("why", "") for t in top]}
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
  "Har ... ka ek dost", "Mummy vs ..."), may use one emoji, ends with " | Sab Theek Hai". No clickbait lies,
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
