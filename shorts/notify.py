"""Phone notifications through the owner's Telegram bot.

The runner SENDS (videos for review, alerts, "uploaded", "live", daily report).
Button taps and replies are RECEIVED by the Cloudflare Worker (worker/index.js), which starts a
GitHub run; the runner never polls Telegram (that would burn Actions minutes).

Everything here is best-effort: if Telegram is not configured or fails, the GitHub issue that the
pipeline already writes is the fallback, and the failure is logged, never raised.
"""
from __future__ import annotations

import json
import os
from pathlib import Path

import requests

API = "https://api.telegram.org/bot{token}/{method}"


def _token() -> str:
    return os.environ.get("TELEGRAM_BOT_TOKEN", "").strip()


def chat_id(state) -> str | None:
    return state.get_setting("telegram_chat_id") if state else None


def enabled(state) -> bool:
    return bool(_token() and chat_id(state))


def call(method: str, data: dict | None = None, files: dict | None = None, timeout: int = 120) -> dict:
    r = requests.post(API.format(token=_token(), method=method), data=data, files=files, timeout=timeout)
    try:
        body = r.json()
    except ValueError:
        body = {"ok": False, "description": r.text[:200]}
    if not body.get("ok"):
        raise RuntimeError(f"telegram {method}: {body.get('description')}")
    return body["result"]


def keyboard(rows: list[list[tuple[str, str]]]) -> str:
    return json.dumps({"inline_keyboard": [[{"text": t, "callback_data": d} for t, d in row] for row in rows]})


def send(state, text: str, buttons: list[list[tuple[str, str]]] | None = None, silent: bool = False) -> dict | None:
    if not enabled(state):
        return None
    data = {"chat_id": chat_id(state), "text": text[:4000], "parse_mode": "HTML",
            "disable_web_page_preview": "true", "disable_notification": "true" if silent else "false"}
    if buttons:
        data["reply_markup"] = keyboard(buttons)
    try:
        return call("sendMessage", data)
    except Exception as e:  # noqa: BLE001
        state.log(f"telegram send failed: {e}", "warn")
        return None


def send_video(state, path: Path, caption: str, buttons=None) -> dict | None:
    if not enabled(state):
        return None
    data = {"chat_id": chat_id(state), "caption": caption[:1000], "parse_mode": "HTML",
            "supports_streaming": "true", "width": 1080, "height": 1920}
    if buttons:
        data["reply_markup"] = keyboard(buttons)
    try:
        with open(path, "rb") as f:
            return call("sendVideo", data, files={"video": (path.name, f, "video/mp4")}, timeout=300)
    except Exception as e:  # noqa: BLE001
        state.log(f"telegram video failed: {e}", "warn")
        return send(state, caption + "\n\n(video could not be attached: " + str(e)[:120] + ")", buttons)


def esc(s: str) -> str:
    return (s or "").replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def review_buttons(job: str) -> list[list[tuple[str, str]]]:
    # callback_data max 64 bytes: "a:" + job id (job ids are short slugs)
    return [[("✅ Approve", f"a:{job}"[:64]), ("✏️ Fix", f"f:{job}"[:64])], [("🗑 Drop", f"d:{job}"[:64])]]


def review(state, job: str, video: Path, title: str, score, cost: float, flags: list[str], slot: str | None,
           extra: str = "") -> None:
    lines = [f"🎬 <b>{esc(title)}</b>", f"Fact-check {score}/10 · cost ${cost:.2f}"]
    if extra:
        lines.append(esc(extra))
    if slot:
        lines.append(f"If approved: goes public {esc(slot)}")
    if flags:
        lines.append("Notes: " + esc("; ".join(f[:90] for f in flags[:3])))
    lines.append(f"<code>job:{esc(job)}</code>")
    msg = send_video(state, video, "\n".join(lines), review_buttons(job))
    if msg:
        state.set_setting(f"telegram_review_msg:{job}", str(msg.get("message_id")))


def setup_from_updates(state) -> str | None:
    """Pairing: the first chat that sent /start to the bot becomes the owner chat.
    Only used once, before the webhook is set (getUpdates does not work while a webhook is set)."""
    if not _token():
        return None
    if chat_id(state):
        return chat_id(state)
    for u in reversed(call("getUpdates", {"timeout": 0})):
        m = u.get("message") or {}
        if m.get("chat", {}).get("type") == "private" and (m.get("text") or "").startswith("/start"):
            cid = str(m["chat"]["id"])
            state.set_setting("telegram_chat_id", cid)
            state.set_setting("telegram_owner_user_id", str(m.get("from", {}).get("id", cid)))
            return cid
    return None


def send_photo(state, path: Path, caption: str) -> dict | None:
    if not enabled(state):
        return None
    try:
        with open(path, "rb") as f:
            return call("sendPhoto", {"chat_id": chat_id(state), "caption": caption[:1000], "parse_mode": "HTML"},
                        files={"photo": (path.name, f, "image/jpeg")})
    except Exception as e:  # noqa: BLE001
        state.log(f"telegram photo failed: {e}", "warn")
        return send(state, caption)
