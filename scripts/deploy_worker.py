#!/usr/bin/env python3
"""Deploy the studio Worker to Cloudflare and point the Telegram bot at it. Idempotent.

Needs env: CLOUDFLARE_API_TOKEN, CLOUDFLARE_ACCOUNT_ID, TELEGRAM_BOT_TOKEN, GH_DISPATCH_TOKEN,
GITHUB_REPOSITORY. Pairing: the owner must have pressed Start in the bot before the FIRST deploy
(the chat id is read once with getUpdates, then the webhook takes over).
Prints a JSON status line; writes worker_url / telegram_chat_id into the state DB.
"""
from __future__ import annotations

import json
import os
import secrets
import sys
from pathlib import Path

import requests

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from shorts import notify          # noqa: E402
from shorts.config import load     # noqa: E402
from shorts.state import State     # noqa: E402

CF = "https://api.cloudflare.com/client/v4"
NAME = "bhaukaalitoons-studio"
KV_TITLE = "bhaukaalitoons-studio"


def cf(method: str, path: str, **kw) -> dict:
    h = {"Authorization": f"Bearer {os.environ['CLOUDFLARE_API_TOKEN']}"}
    r = requests.request(method, CF + path, headers=h, timeout=60, **kw)
    body = r.json() if r.headers.get("content-type", "").startswith("application/json") else {}
    if not body.get("success", False):
        raise RuntimeError(f"Cloudflare {method} {path}: {r.status_code} {json.dumps(body.get('errors'))[:300]}")
    return body.get("result") or {}


def kv_namespace(acc: str) -> str:
    page = cf("GET", f"/accounts/{acc}/storage/kv/namespaces", params={"per_page": 100})
    for ns in page:
        if ns["title"] == KV_TITLE:
            return ns["id"]
    return cf("POST", f"/accounts/{acc}/storage/kv/namespaces", json={"title": KV_TITLE})["id"]


def subdomain(acc: str) -> str:
    try:
        sub = cf("GET", f"/accounts/{acc}/workers/subdomain").get("subdomain")
        if sub:
            return sub
    except RuntimeError:
        pass
    for cand in ("bhaukaalitoons", f"bhaukaalitoons-{secrets.token_hex(2)}"):
        try:
            return cf("PUT", f"/accounts/{acc}/workers/subdomain", json={"subdomain": cand})["subdomain"]
        except RuntimeError:
            continue
    raise RuntimeError("could not register a workers.dev subdomain; open Workers & Pages once in the dashboard")


def main() -> int:
    acc = os.environ["CLOUDFLARE_ACCOUNT_ID"].strip()
    cfg = load()
    state = State(cfg.path("state_db"))
    owner = notify.setup_from_updates(state)
    if not owner:
        print(json.dumps({"ok": False, "why": "press Start in the Telegram bot first"}))
        return 2
    owner_user = state.get_setting("telegram_owner_user_id") or owner
    ns = kv_namespace(acc)
    sub = subdomain(acc)
    url = f"https://{NAME}.{sub}.workers.dev"
    tg_secret = secrets.token_urlsafe(32)
    meta = {
        "main_module": "index.js",
        "compatibility_date": "2026-09-01",
        "bindings": [
            {"type": "kv_namespace", "name": "KV", "namespace_id": ns},
            {"type": "secret_text", "name": "TG_TOKEN", "text": os.environ["TELEGRAM_BOT_TOKEN"].strip()},
            {"type": "secret_text", "name": "TG_SECRET", "text": tg_secret},
            {"type": "secret_text", "name": "GH_TOKEN", "text": os.environ["GH_DISPATCH_TOKEN"].strip()},
            {"type": "secret_text", "name": "COOKIE_KEY", "text": secrets.token_urlsafe(48)},
            {"type": "plain_text", "name": "OWNER_ID", "text": owner_user},
            {"type": "plain_text", "name": "GH_REPO", "text": os.environ["GITHUB_REPOSITORY"]},
            {"type": "plain_text", "name": "SELF_URL", "text": url},
        ],
    }
    code = (ROOT / "worker" / "index.js").read_bytes()
    cf("PUT", f"/accounts/{acc}/workers/scripts/{NAME}", files={
        "metadata": (None, json.dumps(meta), "application/json"),
        "index.js": ("index.js", code, "application/javascript+module"),
    })
    cf("POST", f"/accounts/{acc}/workers/scripts/{NAME}/subdomain", json={"enabled": True})
    hook = notify.call("setWebhook", {"url": f"{url}/tg", "secret_token": tg_secret,
                                     "allowed_updates": json.dumps(["message", "callback_query"]),
                                     "drop_pending_updates": "true"})
    notify.call("setMyCommands", {"commands": json.dumps([
        {"command": "status", "description": "What's happening now"},
        {"command": "produce", "description": "Make a video now"},
        {"command": "dash", "description": "Dashboard link"},
        {"command": "revenue", "description": "Record revenue: /revenue 2026-11 12.50"},
        {"command": "help", "description": "How this works"},
    ])})
    state.set_setting("worker_url", url)
    state.set_setting("cf_kv_namespace", ns)
    print(json.dumps({"ok": True, "url": url, "webhook": hook, "owner_chat": owner}))
    return 0


if __name__ == "__main__":
    sys.exit(main())
