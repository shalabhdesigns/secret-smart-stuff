"""The writers' room v3 (docs/TEMPLATE.md stages 1-5). Every stage has a deliverable and a gate; weak material is
stopped before voices, art or render are paid for.

  1 OBSERVE   24 specific, recognisable behaviours (writer model, high temperature, rotated life areas)
  2 PREMISE   8 premise cards: truth, game, wants, 3 beats, turn, button, loop, visuals, art needed, share trigger
  G1          deterministic (cliché, repetition) + blind pairwise tournament by an independent judge -> top 2
  ART         the chosen premise's new people/places are drawn NOW, so the script is written for what can be shown
  3 SCRIPT    two full scripts (one per finalist) with beat labels and a joke map
  G2          blind pairwise script choice + anchored rubric (independent judge)
  4 PUNCH-UP  judge fixes + alternatives for the weakest lines; story kept
  G3          rubric bar (avg >= 3.8, nothing < 3, funny >= 3.8, clarity >= 4, no red flags) + hard script checks
  5 STAGE     storyboard plan (shots, beats, props, continuity, loop) for the animation engine
  G4          renderability + storyboard checks + judge "does the picture match the words" -> repair
"""
from __future__ import annotations

import datetime as dt
import json
from pathlib import Path

from . import director as D
from . import gates as G
from . import judge as J

ROOT = Path(__file__).resolve().parents[2]
AREAS = ["parents & phone calls", "siblings & cousins", "relatives & family functions", "neighbours & the building",
         "flatmates & shared chores", "office, bosses & WhatsApp groups", "money, salary day & EMIs",
         "food, delivery apps & the kitchen", "festivals & rituals", "weddings & shagun", "travel, trains & autos",
         "shopping, bargaining & online returns", "health, gym & home remedies", "technology & parents",
         "landlords, rent & maintenance", "friends & plans that never happen", "school/college memories & exams",
         "weather & seasons", "cricket & TV", "government offices, queues & paperwork"]


def _ctx(number: int, slot: str | None) -> str:
    today = dt.date.today()
    when = dt.date.fromisoformat(slot[:10]) if slot else today + dt.timedelta(days=3)
    cal = json.loads((ROOT / "creative" / "calendar.json").read_text())
    near = [f"{e['name']} ({e['date']})" for e in cal["events"]
            if -2 <= (dt.date.fromisoformat(e["date"]) - when).days <= 10]
    seasons = [s["name"] for s in cal["seasons"] if when.month in s["months"]]
    return (f"Today is {today:%d %B %Y}. This episode goes public on {when:%A %d %B %Y}, 7:30 PM IST.\n"
            f"Timely events around then: {', '.join(near) or 'none'}.\nSeason: {'; '.join(seasons)}.\n"
            "Mix: a timely episode only when it gives a fresher angle than an evergreen one; roughly half evergreen.")


def _areas(history: list[dict], k: int = 7) -> list[str]:
    import random
    used = " ".join(f"{e.get('premise', '')} {e.get('title', '')}".lower() for e in history[-6:])
    fresh = [a for a in AREAS if not any(w in used for w in a.split(" & ")[0].split()[:1])]
    random.Random(len(history)).shuffle(fresh)
    return (fresh + AREAS)[:k]


def _apply_patch(sc: dict, patch: dict) -> dict:
    sc = json.loads(json.dumps(sc))
    lines = sc.get("lines", [])
    rep = patch.get("replace") or {}
    for ln in lines:
        if ln.get("id") in rep and isinstance(rep[ln["id"]], dict):
            ln.update({k: v for k, v in rep[ln["id"]].items() if v not in (None, "")})
    dele = set(patch.get("delete") or [])
    lines = [ln for ln in lines if ln.get("id") not in dele]
    ins = patch.get("insert_after") or {}
    out = []
    for ln in lines:
        out.append(ln)
        for new in ins.get(ln.get("id"), []) or []:
            if isinstance(new, dict) and new.get("cap"):
                out.append(new)
    used = set()
    for i, ln in enumerate(out):                      # keep ids unique
        if not ln.get("id") or ln["id"] in used:
            ln["id"] = f"l{i + 1}x"
        used.add(ln["id"])
    sc["lines"] = out
    for k, v in (patch.get("set") or {}).items():
        if v:
            sc[k] = v
    return sc


class NotGoodEnough(RuntimeError):
    def __init__(self, msg: str, cost: float = 0.0):
        super().__init__(msg)
        self.cost = cost


def write(llm, history: list[dict], feedback: list[dict], number: int, idea: str = "", slot: str | None = None,
          art_cb=None, log=print) -> tuple[dict, float]:
    from . import writer as Wr
    system = Wr._system()
    cost = [0.0]
    gate_log: list[str] = []

    def ask(prompt: str, tokens: int = 8000, temperature: float | None = None) -> dict:
        r = llm.ask(prompt, system=system, model=Wr.WRITER_MODEL, max_tokens=tokens, temperature=temperature,
                    cache_system=True)
        cost[0] += r.usd
        return r.data

    hist = Wr._history_brief(history, feedback)
    ctx = _ctx(number, slot)

    # ---- 1. OBSERVE
    obs = ask(
        f"TASK: observe\n{ctx}\n{hist}\n" + (f"The owner asked for: {idea}\n" if idea else "") +
        f"Life areas to mine today: {', '.join(_areas(history))}.\n"
        "List 16 SPECIFIC behaviours that ordinary Indian people really do but rarely say out loud (WRITER CARD §1). "
        "Each must name a concrete object, phrase, number or ritual. Skip anything in the CLICHÉ list unless you have a "
        "genuinely new angle on it. No jokes yet - just true observations.\n"
        'Return JSON {"observations": [{"id": 1, "area": "...", "behaviour": "...", "unspoken_rule": "the rule '
        'everyone follows but never states", "detail": "the specific object/phrase/number", "who_does_this": "...", '
        '"timely": "event name or empty"}]}', 7000, temperature=1.0)["observations"]

    # ---- 2. PREMISE
    cards = ask(
        f"TASK: premise\n{ctx}\nOBSERVATIONS:\n{json.dumps(obs, ensure_ascii=False)}\n"
        "Pick the 6 observations with the most comic tension and turn each into a premise card (WRITER CARD §2). "
        "Cast and place come from the story. Plan how every moment will be SHOWN with the animation library; list any "
        "new person/place you need (max 1 new on-screen person, 1 new place). A person who is physically present "
        "must be on screen.\n"
        'Return JSON {"cards": [{"id": "P1", "obs": 1, "truth": "the human truth in one sentence", "game": "the '
        'pattern that repeats and heightens", "timely": "", "cast": [{"who": "id or new id", "on_screen": true, '
        '"want": "...", "flaw": "..."}], "relations_cue": "how a first-time viewer learns who they are to each other '
        'in the first 5 s, naturally", "place": "set id or new place", "beats": ["escalation 1", "2", "3"], "turn": '
        '"the reversal/reframe", "punch": "...", "button": "...", "loop_bridge": "how the last moment leads into the '
        'first line", "visual_gags": ["..."], "props": ["object: how it is seen"], "new_people": [{"id": "", '
        '"name": "", "desc": "", "look": "", "voice_type": "", "relations": {}, "height": 0.95}], "new_place": '
        '{"id": "", "desc": ""}, "share_trigger": "who forwards it to whom", "fresh_angle": "why no meme page has '
        'done this exact take"}]}', 9000, temperature=0.9)["cards"]

    # ---- G1: deterministic checks + independent blind tournament
    keep = []
    for c in cards:
        tmp = {"premise": c.get("truth"), "truth": c.get("truth"), "game": c.get("game")}
        rep = G.repetition(tmp, history)
        if rep:
            gate_log.append(f"G1 drop {c.get('id')}: {rep[0]}")
            continue
        c["_cliche"] = G.cliche(tmp)
        keep.append(c)
    if len(keep) < 2:
        keep = cards[:4]

    def card_text(c: dict) -> str:
        return (f"Truth: {c.get('truth')}\nGame: {c.get('game')}\nBeats: {' / '.join(c.get('beats', []))}\n"
                f"Turn: {c.get('turn')}\nPunch: {c.get('punch')}\nButton: {c.get('button')}\n"
                f"Fresh angle: {c.get('fresh_angle')}" + (f"\n(Overused situation: {', '.join(c['_cliche'])})"
                                                           if c.get("_cliche") else ""))
    screen = J.premise_scores(llm, keep, card_text, cost)              # anchored absolute screen of all cards
    top3 = sorted(range(len(keep)), key=lambda i: -screen[i])[:3]
    pw = J.pairwise(llm, [keep[i] for i in top3], card_text,
                    "Which premise would make more ordinary Indian viewers laugh out loud AND forward it to a "
                    "specific person? Prefer a specific, fresh truth over a familiar meme situation, and a turn "
                    "that surprises. Penalise overused situations unless the angle is truly new.", cost,
                    keep=2, max_pairs=3)                               # pairwise only between finalists
    ranked = [(top3[i], screen[top3[i]] + s) for i, s in pw]
    finalists = [keep[i] for i, _ in ranked]
    gate_log.append("G1 finalists: " + ", ".join(f"{keep[i].get('id')} ({s:.1f})" for i, s in ranked))
    log(gate_log[-1])

    # ---- ART for the leading premise (so the script is written for what can actually be shown)
    art_note = ""
    if art_cb:
        res = art_cb(finalists[0])
        if res.get("failed"):
            art_note = ("ART THAT COULD NOT BE MADE (write around it: off-screen at the door, on a call, or someone "
                        "else): " + "; ".join(res["failed"]))
        if res.get("made"):
            art_note += ("\nNEW ART READY: " + ", ".join(res["made"]))
        gate_log.append(f"ART: made {res.get('made')}, failed {res.get('failed')}")
        system = Wr._system()                        # library changed -> refresh what the writer sees

    # ---- 3. SCRIPT (one per finalist)
    def draft(card: dict) -> dict:
        return ask(
            f"TASK: script\n{ctx}\n{art_note}\nPREMISE CARD:\n{json.dumps({k: v for k, v in card.items() if not k.startswith('_')}, ensure_ascii=False)}\n"
            "Write the full ~55-second script (WRITER CARD §3-5): 14-22 lines, 110-160 spoken words. Every line a "
            "complete, natural sentence a real person would say. Label each line with its beat. Mark the joke map. "
            'Return JSON {"title_idea": "", "premise": "", "truth": "", "game": "", "structure": "", "relations_cue": "", '
            '"loop": {"bridge": "", "last_line_leads_to_first": true}, "new_characters": [], "new_sets": [], '
            '"props": [], "lines": [{"id": "l1", "who": "", "via": "", "beat": "hook|setup|escalate1|escalate2|'
            'escalate3|turn|punch|button", "hi": "Devanagari with audio tags", "cap": "Roman Hinglish caption", '
            '"direction": "what we see / faces"}], "jokes": [{"line": "l5", "type": "reveal|reversal|callback|'
            'rule-of-three|status-drop|visual", "assumption": "what the audience believed", "reveal_word": ""}]}',
            9000, temperature=0.8)

    scripts = [draft(c) for c in finalists]
    for s, c in zip(scripts, finalists):
        s.setdefault("truth", c.get("truth"))
        s.setdefault("game", c.get("game"))
        s.setdefault("relations_cue", c.get("relations_cue"))
        if not s.get("loop"):
            s["loop"] = {"bridge": c.get("loop_bridge", "")}

    # ---- G2: choose the stronger script (blind, both orders), then score it against anchors
    if len(scripts) > 1:
        best = J.pairwise(llm, scripts, J.script_text,
                          "Which finished script would get more real laughs from Indian viewers and more shares? "
                          "Judge the lines themselves: are they natural, complete, clear to a first-time viewer, and "
                          "funny?", cost, keep=1, max_pairs=1)[0][0]
    else:
        best = 0
    order = [best] + [i for i in range(len(scripts)) if i != best]
    attempts = []
    for idx in order:
        sc = scripts[idx]
        prev, changed = None, None
        for rnd in range(4):
            hard = G.script(sc, history)
            r = J.rubric(llm, J.script_text(sc), cost, context=Wr.lessons_brief(), previous=prev, changed=changed)
            attempts.append((r.get("total", 0), sc, r, hard))
            gate_log.append(f"G3 script {idx} round {rnd}: total {r.get('total')} min {r.get('min')} "
                            f"flags {str(r.get('red_flags'))[:300]} hard {hard[:3]}")
            log(gate_log[-1])
            if (J.passes(r) and not hard) or rnd == 3:
                break
            # ---- 4. PUNCH-UP as a PATCH: only the flagged/weak lines change, so fixes converge instead of
            # rewriting the whole script and creating new problems.
            patch = ask(
                "TASK: punchup\nFix this script with the SMALLEST change (WRITER CARD §6). Do not change the story, "
                "premise, cast or any line that isn't a problem. For each line you change, think of 3 alternatives and "
                "keep the funniest complete, natural, logical one. Every red flag and hard-check problem must be "
                "resolved; also improve the weakest dimension.\n"
                f"JUDGE SCORES: {json.dumps(r.get('scores'))}\nRED FLAGS: {r.get('red_flags')}\n"
                f"WEAKEST LINES: {r.get('weakest_lines')}\nFIXES: {r.get('fixes')}\nHARD CHECK PROBLEMS: {hard}\n"
                f"SCRIPT:\n{json.dumps(sc, ensure_ascii=False)}\n"
                'Return JSON {"replace": {"l7": {"who": "", "via": "", "beat": "", "hi": "", "cap": "", "direction": ""}}, '
                '"delete": ["l9"], "insert_after": {"l3": [{"id": "l3b", "who": "", "beat": "", "hi": "", "cap": ""}]}, '
                '"set": {"loop": {"bridge": ""}, "relations_cue": "", "truth": "", "game": ""}, "why": "one line"}', 5000)
            before = {ln["id"]: ln.get("cap") for ln in sc.get("lines", [])}
            sc = _apply_patch(sc, patch)
            changed = [ln["id"] for ln in sc.get("lines", []) if before.get(ln["id"]) != ln.get("cap")]
            prev = r
        if J.passes(r) and not hard:
            break
    total, script, rub, hard = max(attempts, key=lambda a: (J.passes(a[2]) and not a[3], a[0]))
    if total < 3.3 or rub.get("red_flags"):
        raise NotGoodEnough(f"no script reached the bar today (best {total}, flags {rub.get('red_flags')}); "
                            + " | ".join(gate_log[-4:]), cost[0])

    # ---- 5. STAGE + G4
    plan = ask(
        "TASK: stage\nTurn this approved script into the full production plan (OUTPUT format; STAGING CARD). Keep every "
        "line exactly (ids, text). Every shot gets a beat label. Show what the words talk about; props in the right "
        "hands; anyone physically present is on screen. The last shot repeats the first shot's set, size and cast so "
        "the loop is seamless.\nSCRIPT:\n" + json.dumps(script, ensure_ascii=False), 14000)
    for k in ("truth", "game", "loop", "relations_cue", "new_characters", "new_sets", "props", "jokes", "structure",
              "title_idea", "premise"):
        if script.get(k) and not plan.get(k):
            plan[k] = script[k]
    plan = Wr._fix_loop(llm, plan, system, cost)
    for rnd in range(2):
        probs = G.storyboard(plan)
        v = J.storyboard_check(llm, plan, cost)
        probs += v.get("problems", [])
        gate_log.append(f"G4 storyboard round {rnd}: {probs[:4]}")
        log(gate_log[-1])
        if not probs:
            break
        plan2 = ask("TASK: repair\nFix ONLY these storyboard problems; keep the lines identical. Return the full JSON.\n"
                    "PROBLEMS:\n- " + "\n- ".join(probs) + "\n\nPLAN:\n" + json.dumps(plan, ensure_ascii=False), 14000)
        for k in ("truth", "game", "loop", "relations_cue", "jokes", "premise", "title_idea", "structure"):
            plan2.setdefault(k, plan.get(k))
        plan = Wr._fix_loop(llm, plan2, system, cost)
    plan["scorecard"] = {"total": rub.get("total"), "scores": rub.get("scores"), "red_flags": rub.get("red_flags"),
                         "fixes_left": rub.get("fixes", [])[:3], "premise_finalists": [c.get("truth") for c in finalists],
                         "gates": gate_log[-12:]}
    return plan, cost[0]
