"""Offline test of the writers' room v3 gates with a scripted fake model (no API calls)."""
import json
import re

from shorts.sketch import gates as G
from shorts.sketch import judge as J
from shorts.sketch import room


class R:
    def __init__(self, d):
        self.data, self.usd = d, 0.001


LINES = [("dev", "Meera, Mummy ka video call aa raha hai!"), ("meera", "Toh utha lo, Dev. Main chips kha rahi hoon."),
         ("dev", "Kamra dekha hai? Mummy ko lagega hum yahan rehte hain."), ("meera", "Hum yahan rehte hi hain."),
         ("dev", "Jaldi, ye kapde almari mein daalo!"), ("meera", "Almari mein jagah nahi hai, Dev."),
         ("dev", "Toh bed ke neeche daal do, jaldi karo!"), ("meera", "Bed ke neeche pichhli Diwali ke kapde hain."),
         ("dev", "Achha, camera sirf deewar pe rakhunga."), ("meera", "Deewar pe tumhara poster hai, Dev."),
         ("dev", "Kaun sa poster? Wo toh maine utaar diya tha."), ("meera", "Haan, aur Mummy ki photo laga di."),
         ("dev", "Mummy ki photo? Haan, wo toh sanskaar hai."), ("meera", "Usi photo ke peeche poster hai."),
         ("dev", "Hello Mummy! Sab theek hai, ghar ekdum saaf hai!"), ("meera", "Aunty, wo jhooth bol raha hai.")]


def plan_fixture():
    lines = [{"id": f"l{i + 1}", "who": w, "beat": "setup", "hi": "[calm] अरे " + c, "cap": c} for i, (w, c) in enumerate(LINES)]
    shots = []
    for i, ln in enumerate(lines):
        typ = ["wide", "close", "medium", "close"][i % 4]
        who = ln["who"]
        cast = ([{"who": "dev", "pose": "dev_stand"}, {"who": "meera", "pose": "meera_chips"}] if typ == "wide"
                else [{"who": who, "pose": "dev_stand" if who == "dev" else "meera_chips"}])
        shots.append({"type": typ, "set": "flat", "cast": cast, "line": ln["id"], "beat": "setup"})
    shots.append({"type": "wide", "set": "flat", "beat": "button",
                  "cast": [{"who": "dev", "pose": "dev_stand"}, {"who": "meera", "pose": "meera_chips"}]})
    return {"title_idea": "Video call", "premise": "Mummy's surprise video call", "truth": "we clean only the part the camera sees",
            "game": "every hiding place is already full", "loop": {"bridge": "Mummy calls again"}, "music": "bright_pop",
            "lines": lines, "shots": shots}


class Fake:
    def __init__(self):
        self.tasks = []

    def ask(self, prompt, **kw):
        t = re.search(r"TASK: (\w+)", prompt).group(1)
        self.tasks.append(t)
        if t == "observe":
            return R({"observations": [{"id": i, "behaviour": f"b{i}"} for i in range(24)]})
        if t == "premise":
            return R({"cards": [{"id": f"P{i}", "truth": f"truth {i} unique{i}", "game": f"game {i}", "beats": ["a", "b", "c"]}
                                for i in range(8)]})
        if t == "premise_screen":
            return R({"cards": [{"card": i + 1, "scores": {k: 3 + (i % 3) for k in J.PREMISE_ANCHORS}} for i in range(8)]})
        if t == "compare":
            return R({"winner": "X"})
        if t in ("script", "punchup"):
            p = plan_fixture()
            return R({k: v for k, v in p.items() if k != "shots"})
        if t == "rubric":
            return R({"scores": {k: 4.2 for k in J.RUBRIC}, "red_flags": [], "fixes": []})
        if t in ("stage", "repair"):
            return R(plan_fixture())
        if t == "storyboard_check":
            return R({"problems": []})
        raise AssertionError(t)


def test_room_happy_path():
    f = Fake()
    plan, cost = room.write(f, [], [], 3, art_cb=lambda c: {"made": [], "failed": []}, log=lambda m: None)
    assert plan["scorecard"]["total"] >= 3.8
    assert f.tasks[:2] == ["observe", "premise"] and "stage" in f.tasks
    assert G.storyboard(plan) == []


def test_room_rejects_weak_script():
    class Weak(Fake):
        def ask(self, prompt, **kw):
            if "TASK: rubric" in prompt:
                return R({"scores": {k: 2.5 for k in J.RUBRIC}, "red_flags": ["confusing or meaningless line"], "fixes": ["x"]})
            return super().ask(prompt, **kw)
    try:
        room.write(Weak(), [], [], 3, log=lambda m: None)
    except room.NotGoodEnough:
        return
    raise AssertionError("a weak script must not reach production")


def test_hard_checks_catch_stock_phrases_and_missing_loop():
    p = plan_fixture()
    p["lines"][0]["cap"] = "Arey kitne sweet ho aap, kya baat hai"
    p.pop("loop")
    errs = G.script(p)
    assert any("stock phrase" in e for e in errs) and any("loop" in e for e in errs)


def test_storyboard_loop_mirror():
    p = plan_fixture()
    p["shots"][-1]["type"] = "close"
    p["shots"][-1]["cast"] = [{"who": "dev", "pose": "dev_stand"}]
    assert any("loop" in e for e in G.storyboard(p))
