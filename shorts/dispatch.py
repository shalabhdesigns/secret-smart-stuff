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


def resume_credit_held(state) -> dict:
    """Restart videos held for low credits once the picture and voice credits can pay for them (~$0.80 of pictures
    each). Runs with every analytics pass, so a top-up restarts them within 6 hours."""
    held = json.loads(state.get_setting("credit_held") or "[]")
    if not held:
        return {"held": 0}
    import os
    from . import usage
    b = usage.bfl(os.environ.get("BFL_API_KEY", "")) if os.environ.get("BFL_API_KEY") else {}
    if b.get("source") == "measured" and b.get("usd_left", 0) < 0.8 * len(held):
        return {"held": len(held), "waiting": f"BFL ${b.get('usd_left')}"}
    # skip ones whose publish time has passed (they'd go out at the next free slot instead)
    head = dict(held[0])
    head["then"] = held[1:]
    if dispatch(head):
        state.set_setting("credit_held", "[]")
        return {"restarted": len(held)}
    return {"held": len(held), "dispatch": "failed"}
