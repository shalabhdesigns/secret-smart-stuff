"""Independent judging for the writers' room.

Why a separate judge (docs/TEMPLATE.md §2, docs/research/R2): language models favour their own writing and are swayed by
answer order and length, and absolute 1-10 humour scores are noisy. So:
- the judge is a different model from the writer (writer: Opus; judge: Sonnet);
- candidates are anonymised and shown in BOTH orders; a win counts only if it survives the swap;
- comparisons are pairwise ("which would more viewers laugh at and send to someone?"), not absolute scores;
- the rubric uses anchored 1-5 levels with a written reason per score, and hard red flags that fail on their own;
- every verdict is stored, so later it can be checked against the owner's decisions and real audience data (perf.py).
"""
from __future__ import annotations

import itertools
import json
import random

JUDGE_MODEL = "claude-sonnet-5-5"

AUDIENCE = ("You judge for ordinary Indian viewers of Hindi comedy Shorts: students, office workers, homemakers, "
            "shop owners, small towns and big cities. They have seen every meme. They laugh at things that are TRUE "
            "about their own lives, said in a sharper way than they could say it. They share a video only when it "
            "reminds them of a specific person. Be blunt; most material is average.")


def _ask(llm, prompt: str, cost: list[float], tokens: int = 2500) -> dict:
    r = llm.ask(prompt, system=AUDIENCE, model=JUDGE_MODEL, max_tokens=tokens, temperature=0.0)
    cost[0] += r.usd
    return r.data if isinstance(r.data, dict) else {}


def pairwise(llm, items: list[dict], render, question: str, cost: list[float], keep: int = 2,
             max_pairs: int = 15) -> list[tuple[int, float]]:
    """Round-robin (capped) of blind pairwise comparisons, each shown in both orders.
    Returns [(index, score)] best first. render(item) -> text shown to the judge."""
    n = len(items)
    pairs = list(itertools.combinations(range(n), 2))
    random.Random(n).shuffle(pairs)
    pairs = pairs[:max_pairs]
    score = [0.0] * n
    for a, b in pairs:
        votes = []
        for x, y in ((a, b), (b, a)):
            d = _ask(llm, f"TASK: compare\n{question}\n\nOPTION X:\n{render(items[x])}\n\nOPTION Y:\n{render(items[y])}\n\n"
                          "Think about which one a real viewer would actually laugh at and forward. Length is not quality. "
                          'Return JSON {"winner": "X"|"Y"|"tie", "why": "one sentence"}', cost, 400)
            w = d.get("winner")
            votes.append(x if w == "X" else (y if w == "Y" else None))
        if votes[0] is not None and votes[0] == votes[1]:
            score[votes[0]] += 1.0                       # consistent in both orders
        else:
            score[a] += 0.5
            score[b] += 0.5                              # order-dependent or tie -> no real preference
    ranked = sorted(range(n), key=lambda i: -score[i])
    return [(i, score[i]) for i in ranked[:keep]]


RUBRIC = {
    "truth": "1 = no real-life observation, generic; 3 = familiar situation, stated plainly; 5 = a specific, slightly "
             "embarrassing truth most viewers have lived but never heard said out loud",
    "clarity": "1 = a first-time viewer can't tell who these people are or what is going on; 3 = clear after a few "
               "seconds; 5 = relationships, place and want are obvious by 5 s without any exposition",
    "funny": "1 = no line would get a laugh; 3 = smiles, one real laugh; 5 = several real laughs that build, the "
             "biggest near the end",
    "surprise": "1 = every punchline predictable; 3 = one genuine surprise; 5 = the turn reframes everything before "
                "it and still feels inevitable",
    "escalation": "1 = flat or repetitive; 3 = rises but beats feel alike; 5 = each beat clearly bigger and changes "
                  "a different lever (stakes, specifics, emotion)",
    "dialogue": "1 = stiff, stock or machine-sounding Hindi, incomplete or confusing sentences; 3 = natural but "
                "plain; 5 = every line sounds like a real person from UP/Delhi speaking, distinct voices, complete "
                "and clear, nobody explains the joke",
    "character": "1 = characters are mouthpieces; 3 = clear wants; 5 = every line comes from a want and a flaw, "
                 "consistent with the show bible and earlier episodes",
    "shareability": "1 = nobody would forward it; 3 = some would; 5 = viewers will tag a specific person "
                    "(\"this is literally my mother\") and quote the last line",
    "loop": "1 = ending is a dead stop; 3 = ending is fine but replay is jarring; 5 = the last moment flows "
            "straight into the first and the replay reveals something new",
}
RED_FLAGS = ["confusing or meaningless line", "incomplete or ungrammatical Hindi sentence", "joke depends on caste, "
             "religion, region, body, disability or gender as the target", "a real named person or brand mocked",
             "plot hole / physically impossible staging", "the same joke as a recent episode",
             "a premise that every desi meme page has already done with no new angle"]


def rubric(llm, script_text: str, cost: list[float], context: str = "") -> dict:
    keys = list(RUBRIC)
    d = _ask(llm, "TASK: rubric\nScore this 60-second animated sketch script on each dimension using ONLY the "
                  "anchored levels (1-5, halves allowed). Quote the line that justifies each score. Then list any red "
                  "flags from this list that apply: " + "; ".join(RED_FLAGS) + ". Then give the 3 most valuable fixes."
                  + (f"\nCONTEXT:\n{context}" if context else "") + "\nANCHORS:\n" +
                  "\n".join(f"- {k}: {v}" for k, v in RUBRIC.items()) + "\nSCRIPT:\n" + script_text +
                  '\nReturn JSON {"scores": {' + ", ".join(f'"{k}": 0' for k in keys) +
                  '}, "evidence": {"<dimension>": "quoted line"}, "red_flags": ["..."], "weakest_lines": ["id: why"], '
                  '"fixes": ["..."]}', cost, 3000)
    sc = {k: float((d.get("scores") or {}).get(k, 0) or 0) for k in keys}
    d["scores"] = sc
    d["total"] = round(sum(sc.values()) / len(keys), 2)
    d["min"] = min(sc.values()) if sc else 0
    return d


def passes(r: dict, bar: float = 3.8, floor: float = 3.0) -> bool:
    """Script gate G3: no red flags, average >= bar, nothing below floor, and the comedy itself >= bar."""
    return (not r.get("red_flags") and r.get("total", 0) >= bar and r.get("min", 0) >= floor
            and r["scores"].get("funny", 0) >= bar and r["scores"].get("clarity", 0) >= 4)


def script_text(plan: dict) -> str:
    names = {"dev": "Dev", "meera": "Meera", "rocky": "Rocky"}
    names.update({c.get("id"): c.get("name") for c in plan.get("new_characters", []) if c.get("id")})
    out = [f"PREMISE: {plan.get('premise', '')}", f"HUMAN TRUTH: {plan.get('truth', '')}"]
    for ln in plan.get("lines", []):
        via = f" ({ln['via']})" if ln.get("via") else ""
        d = f"   [{ln['direction']}]" if ln.get("direction") else ""
        out.append(f"{ln.get('id', '')} {names.get(ln['who'], ln['who'])}{via}: {ln['cap'].replace(chr(10), ' ')}{d}")
    return "\n".join(out)


PREMISE_ANCHORS = {
    "truth": "1 generic / 3 familiar but plain / 5 specific truth viewers have lived but never heard said",
    "laughs": "1 no laugh in sight / 3 one clear laugh / 5 a turn that should get a real laugh plus smaller ones on the way",
    "fresh": "1 a meme every desi page has posted / 3 familiar situation, new detail / 5 a take nobody has done",
    "clarity": "1 needs explaining / 3 clear after setup / 5 a first-time viewer gets who/where/what in 5 s",
    "showable": "1 can't be shown with our 2D puppets / 3 mostly talk / 5 the funniest moments are visible on screen",
    "share": "1 nobody forwards it / 3 some would / 5 viewers will tag a specific person",
}


def premise_scores(llm, cards: list[dict], render, cost: list[float]) -> list[float]:
    """Anchored absolute screening (more robust to surface distractors than pairwise; Tripathi et al. 2025).
    Cards are scored in a shuffled order, each with evidence before the score."""
    order = list(range(len(cards)))
    random.Random(len(cards) * 7).shuffle(order)
    text = "\n\n".join(f"CARD {k + 1}:\n{render(cards[i])}" for k, i in enumerate(order))
    d = _ask(llm, "TASK: premise_screen\nScore every premise card on each dimension using ONLY these anchors (1-5). "
                  "For each card first write one sentence of evidence, then the scores. Length and polish are not "
                  "quality.\nANCHORS:\n" + "\n".join(f"- {k}: {v}" for k, v in PREMISE_ANCHORS.items()) +
                  f"\n\n{text}\n\n" + 'Return JSON {"cards": [{"card": 1, "evidence": "...", "scores": {' +
                  ", ".join(f'"{k}": 0' for k in PREMISE_ANCHORS) + "}}]}", cost, 4000)
    out = [0.0] * len(cards)
    for row in d.get("cards") or []:
        try:
            i = order[int(row["card"]) - 1]
        except (KeyError, ValueError, IndexError):
            continue
        s = row.get("scores") or {}
        # laughs and truth weigh double: they are what the owner asks for first
        w = {"truth": 2, "laughs": 2, "fresh": 1.5, "clarity": 1, "showable": 1, "share": 1.5}
        out[i] = sum(float(s.get(k, 0) or 0) * w[k] for k in w) / sum(w.values())
    return out


def storyboard_check(llm, plan: dict, cost: list[float]) -> dict:
    """Does what we SEE match what we HEAR? Props, presence, continuity, logic (who knows what, who can hear whom)."""
    from . import director as D
    lib = D.library()
    poses = {k: {"who": v["who"], "desc": v.get("desc", ""), "props": v.get("props", [])} for k, v in lib["poses"].items()}
    lines = {ln["id"]: f"{ln['who']}{' (' + ln['via'] + ')' if ln.get('via') else ''}: {ln['cap']}" for ln in plan.get("lines", [])}
    shots = [{"i": i, "beat": s.get("beat"), "type": s.get("type"), "set": s.get("set"),
              "cast": [f"{c.get('who')}:{c.get('pose')}" for c in s.get("cast", [])], "line": lines.get(s.get("line"), "")}
             for i, s in enumerate(plan.get("shots", []))]
    d = _ask(llm, "TASK: storyboard_check\nYou are the continuity supervisor of a 2D animated sketch. For each shot you "
                  "see who is on screen in which pose (pose descriptions list the props they hold) and the line heard. "
                  "Find ONLY real problems a viewer would notice: a prop that is talked about but shown wrong or missing "
                  "from the hands it should be in; a person who is physically present (in the room, at the door) but "
                  "not on screen; someone hearing or answering a line they could not hear (e.g. a phone held to "
                  "another person's ear); a line spoken by someone who isn't there; continuity jumps (pose/prop "
                  "teleports between consecutive shots of the same moment); the last shot not matching the first shot "
                  "for the loop. Ignore style.\nPOSES:\n" + json.dumps(poses, ensure_ascii=False) + "\nSHOTS:\n" +
                  json.dumps(shots, ensure_ascii=False) + '\nReturn JSON {"problems": ["shot N: ..."]}', cost, 2000)
    return {"problems": [p for p in (d.get("problems") or []) if isinstance(p, str)][:8]}
