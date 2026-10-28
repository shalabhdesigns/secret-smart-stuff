"""After upload: confirm YouTube processed the video and that it actually went public on time.

Status flow in the uploads table: uploaded -> scheduled -> live, or -> problem (with a reason).
Each change is announced once on Telegram (and logged), so nothing fails silently.
"""
from __future__ import annotations

import datetime as dt
import time

from .. import notify
from .youtube import processing_status


def _ts(iso: str | None) -> float | None:
    if not iso:
        return None
    return dt.datetime.fromisoformat(iso.replace("Z", "+00:00")).timestamp()


def classify(item: dict, publish_at: str | None, now: float) -> tuple[str, str]:
    """-> (status, human reason). Pure function (tested offline)."""
    if not item:
        return "problem", "YouTube no longer returns this video (deleted or not visible to this account)"
    st = item.get("status") or {}
    up, priv = st.get("uploadStatus"), st.get("privacyStatus")
    if up in ("failed", "rejected", "deleted"):
        why = st.get("failureReason") or st.get("rejectionReason") or up
        return "problem", f"YouTube {up} the upload ({why})"
    due = _ts(st.get("publishAt") or publish_at)
    if priv == "public":
        return "live", "public"
    if due and now < due:
        return ("scheduled", "processing" if up == "uploaded" else "scheduled") if up in ("uploaded", "processed") else ("uploaded", up or "")
    if due and now >= due + 20 * 60:
        return "problem", ("still private 20+ min after its publish time. Most likely cause: uploads from an "
                           "unverified Google API project are locked to private until the project passes "
                           "YouTube's API audit")
    return "uploaded", "waiting for publish time"


def run(state) -> list[dict]:
    out = []
    now = time.time()
    rows = state.db.execute("SELECT * FROM uploads WHERE video_id IS NOT NULL AND status NOT IN ('live','failed','held')").fetchall()
    for r in rows:
        try:
            item = processing_status(r["video_id"])
        except Exception as e:  # noqa: BLE001
            state.log(f"verify {r['video_id']}: {e}", "warn", r["job_id"])
            continue
        status, why = classify(item, r["publish_at"], now)
        prev = r["status"]
        if status != prev:
            with state.tx() as db:
                db.execute("UPDATE uploads SET status=?, privacy=? WHERE job_id=?",
                           (status, (item.get("status") or {}).get("privacyStatus"), r["job_id"]))
            state.log(f"upload {r['video_id']}: {prev} -> {status} ({why})",
                      "error" if status == "problem" else "info", r["job_id"])
            if status == "live":
                notify.send(state, f"🎉 Live now: {r['url']}")
            elif status == "scheduled" and prev in ("uploaded", "started"):
                notify.send(state, f"✅ Uploaded and scheduled for {r['publish_at']} UTC.\n{r['url']}", silent=True)
            elif status == "problem":
                notify.send(state, f"⚠️ Publishing problem for {r['url']}:\n{why}")
        out.append({"job": r["job_id"], "video": r["video_id"], "status": status, "why": why})
    return out
