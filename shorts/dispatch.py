"""Start a command run from inside any workflow (workflow_dispatch). Runs share one queue, so it waits its turn."""
from __future__ import annotations

import json
import os
import time

import requests


def dispatch(request: dict) -> bool:
    tok = os.environ.get("GH_DISPATCH_TOKEN") or os.environ.get("GH_TOKEN", "")
    repo = os.environ.get("GITHUB_REPOSITORY", "shalabhdesigns/secret-smart-stuff")
    if not tok or os.environ.get("SHORTS_NO_GITHUB") == "1":
        return False
    for attempt in range(3):
        r = requests.post(f"https://api.github.com/repos/{repo}/actions/workflows/command.yml/dispatches",
                          json={"ref": "main", "inputs": {"request": json.dumps(request, ensure_ascii=False)}},
                          headers={"authorization": f"Bearer {tok}", "accept": "application/vnd.github+json"}, timeout=30)
        if r.status_code == 204:
            return True
        time.sleep(5 * (attempt + 1))
    return False


def resume_paused(state) -> list[str]:
    """Videos paused because a DAY's limit ran out restart by themselves once a new IST day begins (4 Nov 2026:
    a whole series sat paused overnight). Video/month limits still need the owner's tap in Telegram."""
    today = time.strftime("%Y-%m-%d", time.gmtime(time.time() + 5.5 * 3600))
    started = []
    for j in state.jobs("paused"):
        if "day remaining" not in (j.get("error") or ""):
            continue
        paused_day = time.strftime("%Y-%m-%d", time.gmtime((j.get("updated_at") or 0) + 5.5 * 3600))
        key = f"auto_resumed:{j['id']}:{today}"
        if paused_day == today or state.get_setting(key):
            continue
        if dispatch({"action": "finish", "job": j["id"], "rounds": 3, "nonce": f"auto-{j['id'][:20]}-{today}"}):
            state.set_setting(key, "1")
            started.append(j["id"])
    return started


def anthropic_ok() -> bool | None:
    """True if the Anthropic account can pay for a call right now; False if it is out of credit; None if unknown.
    A one-token Haiku call (a tiny fraction of a cent). 17 Nov 2026: a day's 5 videos stopped on an empty balance."""
    key = os.environ.get("ANTHROPIC_API_KEY", "")
    if not key:
        return None
    try:
        r = requests.post("https://api.anthropic.com/v1/messages", timeout=30,
                          headers={"x-api-key": key, "anthropic-version": "2023-06-01", "content-type": "application/json"},
                          json={"model": "claude-haiku-5-5", "max_tokens": 1, "messages": [{"role": "user", "content": "hi"}]})
    except requests.RequestException:
        return None
    if r.status_code == 200:
        return True
    return False if "credit balance" in r.text.lower() else None


def _travel(item: dict) -> dict:
    """A held item that lives in config/daily_queue.json travels as its nonce (dispatch limit 65 KB)."""
    from pathlib import Path
    qf = Path(__file__).resolve().parent.parent / "config" / "daily_queue.json"
    if item.get("queue_nonce"):
        return {"queue_nonce": item["queue_nonce"]}
    if item.get("nonce") and qf.exists() and any(q.get("nonce") == item["nonce"]
                                                 for q in json.loads(qf.read_text()).get("queue") or []):
        return {"queue_nonce": item["nonce"]}
    return {k: v for k, v in item.items() if k != "then"}


def resume_credit_held(state) -> dict:
    """Restart videos held for low credits once the services can pay for them: Anthropic must answer, and the
    picture credits must cover ~$0.80 a video. Runs with every analytics pass and every 15 minutes from
    creditwatch.yml while anything is held, so a top-up restarts them within minutes."""
    held = json.loads(state.get_setting("credit_held") or "[]")
    if not held:
        return {"held": 0}
    if anthropic_ok() is False:
        return {"held": len(held), "waiting": "Anthropic credit"}
    from . import usage
    b = usage.bfl(os.environ.get("BFL_API_KEY", "")) if os.environ.get("BFL_API_KEY") else {}
    if b.get("source") == "measured" and b.get("usd_left", 0) < 0.8 * len(held):
        return {"held": len(held), "waiting": f"BFL ${b.get('usd_left')}"}
    chain = [_travel(h) for h in held]
    head = dict(chain[0])
    head["then"] = chain[1:]
    if dispatch(head):
        state.set_setting("credit_held", "[]")
        state.set_setting("anthropic_dry_told", "")
        try:
            from . import notify
            notify.send(state, f"✅ Credits are back. Restarting {len(held)} held video(s) now.")
        except Exception:  # noqa: BLE001
            pass
        return {"restarted": len(held)}
    return {"held": len(held), "dispatch": "failed"}


# ---------------- owner away: nothing may stay held (20 Nov 2026) ----------------
# Owner, 20 Nov 2026 (away 21-27 Nov): "continue producing videos and publishing them on both Instagram and YouTube
# without requiring any input, intervention, or approval from me". Claude's morning run fixes and approves held
# videos; this is the safety net if that run did not happen or missed one. Every 15 minutes (creditwatch.yml):
# - held BEFORE the voice (text pre-check) and its slot is <= 4 h away: make it anyway without the pre-check
#   (the final check still runs on the finished video);
# - held AFTER the final check and its slot is <= 90 min away: publish it, unless the check found a factual problem
#   (then it stays held; a wrong fact costs more trust than one missed slot).
FACT_WORDS = ("false", "incorrect", "inaccurate", "untrue", "wrong date", "wrong year", "wrong number", "misquot",
              "fabricat", "invented", "contradicts the source", "not what the source")


def _iso(s: str) -> float | None:
    import datetime as dt
    try:
        return dt.datetime.fromisoformat(str(s).replace("Z", "+00:00")).timestamp()
    except (TypeError, ValueError):
        return None


def deadline_publish(state, now: float | None = None) -> dict:
    from pathlib import Path
    now = now or time.time()
    done = set(json.loads(state.get_setting("deadline_done") or "[]"))
    qf = Path(__file__).resolve().parent.parent / "config" / "daily_queue.json"
    queue = json.loads(qf.read_text()).get("queue") or [] if qf.exists() else []
    acted = []
    rows = state.db.execute("SELECT id, topic_id, error FROM jobs WHERE status='review' AND topic_id LIKE 'gta%'").fetchall()
    for r in rows:
        job, topic_id, err = r["id"], r["topic_id"], str(r["error"] or "")
        if job in done:
            continue
        if state.db.execute("SELECT 1 FROM uploads WHERE job_id=? AND video_id IS NOT NULL", (job,)).fetchone():
            continue
        t = state.get_topic(topic_id) or {}
        notes = json.loads(t.get("notes") or "{}")
        slot = _iso(notes.get("publish_at"))
        if not slot:
            continue
        mins = (slot - now) / 60
        if err.startswith("held for Claude before voice"):
            if mins > 240:
                continue
            item = next((q for q in queue if q.get("topic") == topic_id
                         and (q.get("topic_def") or {}).get("notes", {}).get("publish_at") == notes.get("publish_at")), None)
            if not item:
                continue
            req = {k: v for k, v in item.items() if k != "day"}
            req["topic_def"] = json.loads(json.dumps(req["topic_def"]))
            req["topic_def"]["notes"]["precheck"] = False
            if mins < 30:      # too late for its slot: the next 30 minutes
                import datetime as dt
                req["topic_def"]["notes"]["publish_at"] = dt.datetime.fromtimestamp(now + 45 * 60, dt.timezone.utc) \
                    .strftime("%Y-%m-%dT%H:%M:00Z")
            req["nonce"] = f"deadline-{job}"
            req["retire_jobs"] = [job]
            req["fresh"] = True
            if dispatch(req):
                acted.append(f"{job}: remade without the pre-check")
                done.add(job)
                state.log(f"{job}: slot near and still held before voice: remade without the pre-check (owner away)",
                          "warn", job)
            continue
        held = state.db.execute("SELECT 1 FROM events WHERE job_id=? AND message LIKE ?",
                                (job, f"{job} held for Claude: final check%")).fetchone()
        if not held or mins > 90:
            continue
        rnd = state.db.execute("SELECT MAX(round) FROM review_notes WHERE job_id=?", (job,)).fetchone()[0]
        probs = [str(p[0]).lower() for p in state.db.execute(
            "SELECT problem FROM review_notes WHERE job_id=? AND kind='blocking' AND (round IS ? OR round=?)",
            (job, rnd, rnd)).fetchall()]
        if any(w in p for p in probs for w in FACT_WORDS):
            done.add(job)
            state.log(f"{job}: slot near but the final check found a factual problem; stays held", "warn", job)
            continue
        import datetime as dt
        at = slot if mins >= 25 else now + 30 * 60
        pub = dt.datetime.fromtimestamp(at, dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:00Z")
        if dispatch({"action": "approve", "job": job, "publish_at": pub}):
            acted.append(f"{job}: published at {pub} (final-check points were not factual)")
            done.add(job)
            state.log(f"{job}: slot near and still held; approved for {pub} (owner away; no factual problem)",
                      "warn", job)
    if acted:
        state.set_setting("deadline_done", json.dumps(sorted(done)[-200:]))
    return {"deadline": acted}
