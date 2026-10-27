"""Owner feedback -> standing lessons (creative/lessons.json).

Raw notes are specific to one episode ("Gupta aunty is too quiet"); the writer needs the general rule behind them
("a voice-only character must be as loud and clear as the on-screen speaker"). Each fix/drop note is distilled into
0-3 lessons, merged with the existing list (no duplicates), and counted; repeated lessons rise to the top. The writer,
the stager and the judge read the top lessons every episode. Nothing is deleted automatically.
"""
from __future__ import annotations

import json
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
LESSONS = ROOT / "creative" / "lessons.json"
MODEL = "claude-sonnet-5-5"

PROMPT = """TASK: lessons
The owner of a Hindi animated comedy channel reviewed an episode and wrote the note below. Extract 0-3 GENERAL,
reusable lessons for future episodes (not instructions about this one episode). Each lesson: one imperative sentence,
specific and checkable, plus the stage it applies to: one of ideation, writing, dialogue, staging, art, sound,
captions, loop, revision, process. Merge with an existing lesson if it says the same thing (return its id).
EXISTING LESSONS:
@EXISTING
OWNER NOTE (decision: @DECISION):
@NOTE
Return JSON {"lessons": [{"id": "existing id or new", "stage": "...", "text": "..."}]}"""


def load() -> dict:
    if LESSONS.exists():
        return json.loads(LESSONS.read_text())
    return {"_note": "Standing lessons distilled from the owner's feedback. Edit freely.", "lessons": []}


def add(llm, decision: str, note: str) -> float:
    if not note or len(note.strip()) < 8:
        return 0.0
    d = load()
    ex = "\n".join(f"- {x['id']} [{x['stage']}] {x['text']} (x{x['count']})" for x in d["lessons"]) or "- none"
    r = llm.ask(PROMPT.replace("@EXISTING", ex).replace("@DECISION", decision).replace("@NOTE", note[:3000]),
                model=MODEL, max_tokens=1200)
    out = r.data.get("lessons", []) if isinstance(r.data, dict) else []
    byid = {x["id"]: x for x in d["lessons"]}
    for L in out[:3]:
        if L.get("id") in byid:
            byid[L["id"]]["count"] += 1
            byid[L["id"]]["last"] = time.strftime("%Y-%m-%d")
        elif L.get("text"):
            nid = f"L{len(d['lessons']) + 1:03d}"
            item = {"id": nid, "stage": L.get("stage", "writing"), "text": L["text"].strip(), "count": 1,
                    "first": time.strftime("%Y-%m-%d"), "last": time.strftime("%Y-%m-%d")}
            d["lessons"].append(item)
            byid[nid] = item
    LESSONS.write_text(json.dumps(d, ensure_ascii=False, indent=1))
    return r.usd


def brief(stages: tuple[str, ...] | None = None, n: int = 25) -> str:
    d = load()
    items = [x for x in d["lessons"] if not stages or x["stage"] in stages]
    items.sort(key=lambda x: (-x["count"], x["first"]))
    if not items:
        return "OWNER LESSONS: none yet."
    return "OWNER LESSONS (standing rules from the owner's reviews; higher count = repeated complaint, never repeat it):\n" + \
        "\n".join(f"- (x{x['count']}, {x['stage']}) {x['text']}" for x in items[:n])
