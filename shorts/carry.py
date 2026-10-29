"""Carry-forward: what every new video learns from the ones before it (added 29 Oct 2026, owner's rule).

The owner's standing rule: every new video follows the playbook AND builds on the successes, failures and
insights of the previous ones. This module collects those, every run, from four sources:

1. Audience results (evidence): the weekly learning report's rules (`lessons_for_writer`, `topic_guidance`) and
   the newest per-video post-mortems (48 h / 7 d; hypotheses until they repeat).
2. Our own final review: problems the self-review found on recent videos (blocking ones first) and why topics
   were dropped, so the same mistake is not made twice.
3. The owner: change requests (fix notes), Stop presses and drop reasons.
4. What worked: videos whose post-mortem verdict was "above" the channel median, with what the analysis said
   worked.

`for_script()` returns the text added to the writer's prompt and the list of items applied; the list is saved
with the video's features, so the next post-mortems can judge whether applying them helped (the evaluation
step of the loop). `for_ideas()` is the same for choosing topics.
"""
from __future__ import annotations

import json
import time

MAX_CHARS = 3500


def _ensure(state) -> None:
    with state.tx() as db:
        db.execute("CREATE TABLE IF NOT EXISTS review_notes (job_id TEXT NOT NULL, round INTEGER, kind TEXT NOT NULL, "
                   "beat TEXT, problem TEXT NOT NULL, fix TEXT, at REAL NOT NULL)")


def record_review(state, job_id: str, c: dict) -> None:
    """Called after each self-review round: keep what the review found, for the next videos."""
    _ensure(state)
    rows = [(job_id, c.get("round"), "blocking", b.get("beat"), str(b.get("problem", ""))[:400], str(b.get("fix", ""))[:300])
            for b in c.get("blocking") or []]
    rows += [(job_id, c.get("round"), "improve", b.get("beat"), str(b.get("problem", ""))[:400], str(b.get("fix", ""))[:300])
             for b in (c.get("improvements") or [])[:3]]
    rows += [(job_id, c.get("round"), "image", None, str(f)[:400], None) for f in c.get("hard_flags") or []]
    if not rows:
        return
    with state.tx() as db:
        db.executemany("INSERT INTO review_notes(job_id, round, kind, beat, problem, fix, at) VALUES (?,?,?,?,?,?,?)",
                       [r + (time.time(),) for r in rows])


def _reviews(state, jobs: int = 8, limit: int = 10) -> list[tuple[str, str]]:
    _ensure(state)
    recent = [r["job_id"] for r in state.db.execute(
        "SELECT job_id, MAX(at) AS m FROM review_notes GROUP BY job_id ORDER BY m DESC LIMIT ?", (jobs,))]
    out = []
    for kind in ("blocking", "image", "improve"):
        for r in state.db.execute(
                f"SELECT job_id, problem FROM review_notes WHERE kind=? AND job_id IN ({','.join('?' * len(recent)) or 'NULL'}) "
                "ORDER BY at DESC", (kind, *recent)):
            if len(out) < limit:
                out.append((f"review:{r['job_id']}:{kind}", f"{'[blocking] ' if kind == 'blocking' else ''}{r['problem'][:220]}"))
    return out


def _postmortems(state, limit: int = 8) -> tuple[list[tuple[str, str]], list[tuple[str, str]]]:
    try:
        from .insights import _ensure as ins_ensure
        ins_ensure(state)
    except Exception:  # noqa: BLE001
        return [], []
    lessons, wins = [], []
    for r in state.db.execute("SELECT job_id, tag, data FROM video_reviews ORDER BY at DESC LIMIT 20"):
        d = json.loads(r["data"])
        for i, x in enumerate(d.get("lessons") or []):
            if len(lessons) < limit and x.get("lesson"):
                lessons.append((f"pm:{r['job_id']}:{r['tag']}:{i}",
                                f"[{x.get('area', '?')}, {x.get('confidence', 'hypothesis')}] {x['lesson'][:220]}"))
        if d.get("verdict") == "above" and d.get("what_worked") and len(wins) < 4:
            wins.append((f"win:{r['job_id']}:{r['tag']}", f"{r['job_id']}: " + "; ".join(d["what_worked"][:2])[:240]))
    return lessons, wins


def _owner(state) -> list[tuple[str, str]]:
    out = []
    for decision, label in (("fix", "asked to change"), ("stop", "stopped a video because"), ("drop", "dropped because")):
        for r in state.db.execute("SELECT job_id, note FROM feedback WHERE decision=? AND note != '' ORDER BY at DESC LIMIT 6",
                                  (decision,)):
            out.append((f"owner:{decision}:{r['job_id']}", f"Owner {label}: {r['note'][:220]}"))
    return out


def for_script(state) -> tuple[str, list[str]]:
    parts, applied = [], []

    def block(title: str, items: list[tuple[str, str]]) -> None:
        if items:
            parts.append(f"\n\n{title}\n" + "\n".join(f"- {t}" for _, t in items))
            applied.extend(i for i, _ in items)

    rules = state.get_setting("lessons_for_writer")
    if rules:
        parts.append("\n\nRULES FROM THIS CHANNEL'S OWN ANALYTICS (weekly report; follow them):\n" + rules[:1200])
        applied.append("weekly:lessons_for_writer")
    lessons, wins = _postmortems(state)
    block("WHAT WORKED ON OUR VIDEOS THAT BEAT THE CHANNEL MEDIAN (do more of this):", wins)
    block("LESSONS FROM RECENT VIDEO POST-MORTEMS (newest first; hypotheses until repeated, apply where they fit):", lessons)
    block("PROBLEMS OUR FINAL REVIEW FOUND ON RECENT VIDEOS (do not repeat them; plan pictures and lines so they "
          "cannot happen):", _reviews(state))
    block("THE OWNER'S FEEDBACK ON EARLIER VIDEOS (apply proactively):", _owner(state))
    text = "".join(parts)
    if text:
        text = ("\n\nBUILD ON EARLIER VIDEOS. Everything below comes from this channel's own previous videos. Follow the "
                "playbook rules above first; use these to do better than last time." + text)[:MAX_CHARS]
    return text, applied


def for_ideas(state) -> str:
    """Topic choice: the analytics guidance plus each recent video's topic signal."""
    out = []
    guide = state.get_setting("topic_guidance")
    if guide:
        out.append("What this channel's own analytics say about topics (follow it, keep some variety):\n" + guide[:1200])
    try:
        from .insights import _ensure as ins_ensure
        ins_ensure(state)
        sig = []
        for r in state.db.execute("SELECT v.job_id, v.data, t.title FROM video_reviews v LEFT JOIN jobs j ON j.id=v.job_id "
                                  "LEFT JOIN topics t ON t.id=j.topic_id ORDER BY v.at DESC LIMIT 10"):
            d = json.loads(r["data"])
            if d.get("topic_signal") in ("double_down", "drop"):
                sig.append(f"- {d['topic_signal'].replace('_', ' ')}: {r['title'] or r['job_id']} ({d.get('verdict')} median)")
        if sig:
            out.append("Recent videos' topic signals (more like the double-downs, fewer like the drops):\n" + "\n".join(sig[:6]))
    except Exception:  # noqa: BLE001
        pass
    return ("\n\n" + "\n\n".join(out)) if out else ""
