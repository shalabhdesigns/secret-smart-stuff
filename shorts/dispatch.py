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
