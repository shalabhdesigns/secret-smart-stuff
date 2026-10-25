"""Experiments, arm assignment, publish times and per-video features (for learning)."""
from __future__ import annotations

import datetime as dt
import json
import time
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]


def load_experiments() -> list[dict]:
    path = ROOT / "config" / "experiments.yaml"
    if not path.exists():
        return []
    return (yaml.safe_load(path.read_text()) or {}).get("experiments") or []


def sync(state) -> list[dict]:
    exps = load_experiments()
    with state.tx() as db:
        for e in exps:
            db.execute("INSERT INTO experiments(id, data, at) VALUES (?,?,?) "
                       "ON CONFLICT(id) DO UPDATE SET data=excluded.data, at=excluded.at",
                       (e["id"], json.dumps(e), time.time()))
    return exps


def assign(state, job_id: str) -> dict[str, str]:
    """Give this job one arm of every active experiment (balanced rotation, stable once given)."""
    out = {}
    for e in sync(state):
        if e.get("status") != "active":
            continue
        row = state.db.execute("SELECT arm FROM assignments WHERE experiment_id=? AND job_id=?",
                               (e["id"], job_id)).fetchone()
        if row:
            out[e["id"]] = row["arm"]
            continue
        counts = {a: 0 for a in e["arms"]}
        for r in state.db.execute(
                "SELECT a.arm, COUNT(*) n FROM assignments a JOIN jobs j ON j.id=a.job_id "
                "WHERE a.experiment_id=? AND j.status NOT IN ('rejected') GROUP BY a.arm", (e["id"],)):
            if r["arm"] in counts:
                counts[r["arm"]] = r["n"]
        arm = min(counts, key=lambda a: (counts[a], list(e["arms"]).index(a)))
        with state.tx() as db:
            db.execute("INSERT INTO assignments(experiment_id, job_id, arm, at) VALUES (?,?,?,?)",
                       (e["id"], job_id, arm, time.time()))
        out[e["id"]] = arm
    return out


def slot_for(state, job_id: str, default: str = "13:30") -> str:
    for e in load_experiments():
        if e.get("variable") == "publish_slot_utc" and e.get("status") == "active":
            arm = assign(state, job_id).get(e["id"])
            if arm:
                return e["arms"][arm]
    return default


def next_publish_time(state, slot: str, margin_minutes: int = 30, now: dt.datetime | None = None) -> str:
    """Next time at `slot` (HH:MM UTC) at least `margin_minutes` ahead, not already used by another upload."""
    now = now or dt.datetime.now(dt.timezone.utc)
    earliest = now + dt.timedelta(minutes=margin_minutes)
    taken = {r["publish_at"] for r in state.db.execute(
        "SELECT publish_at FROM uploads WHERE publish_at IS NOT NULL AND status != 'failed'")}
    h, m = (int(x) for x in slot.split(":"))
    for day in range(0, 30):
        cand = (earliest + dt.timedelta(days=day)).replace(hour=h, minute=m, second=0, microsecond=0)
        if cand < earliest:
            continue
        iso = cand.strftime("%Y-%m-%dT%H:%M:%SZ")
        if iso not in taken:
            return iso
    raise RuntimeError("no free publish time in 30 days")


def features(script: dict, visuals: dict | None, render: dict | None, topic: dict | None, cost: float) -> dict:
    """What a video was made of. Recorded once per video; the learning report groups by these."""
    scenes = script.get("scenes") or []
    words = sum(len(sc.get("narration", "").split()) for sc in scenes)
    hs = script.get("hook_scores") or []
    ch = script.get("chosen_hook") or 0
    hook = hs[ch] if isinstance(ch, int) and ch < len(hs) else (hs[0] if hs else {})
    notes = json.loads((topic or {}).get("notes") or "{}") if topic else {}
    beats = (visuals or {}).get("beats") or {}
    return {
        "pillar": (topic or {}).get("pillar") or notes.get("pillar"),
        "topic_score": (topic or {}).get("score"),
        "hook_text": scenes[0].get("narration") if scenes else "",
        "hook_formula": hook.get("formula"),
        "hook_heuristic": hook.get("verdict"),
        "seconds": round(float((render or {}).get("duration") or 0), 1),
        "beats": len(scenes),
        "words": words,
        "images": len(script.get("images") or {}),
        "replacement_images": sum(1 for b in beats.values() if (b or {}).get("image")),
        "wit_lines": sum(1 for sc in scenes if sc.get("tone") == "witty"),
        "pops": sum(1 for sc in scenes if sc.get("pop")),
        "markers": sum(1 for sc in scenes if sc.get("markers")),
        "cards": sum(1 for sc in scenes if sc.get("card_text") and not sc.get("image")),
        "music": Path((render or {}).get("music") or "").stem or None,
        "loop_leadin": (scenes[-1].get("narration", "").endswith("...") if scenes else False),
        "playbook": "v9-baseline",
        "cost_usd": round(cost, 3),
    }
