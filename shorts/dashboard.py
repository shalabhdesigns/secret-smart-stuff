"""Owner dashboard: one self-contained HTML page built from the state DB.

Served privately by the Cloudflare Worker (login code via Telegram). Rebuilt after every
analytics pull and after production/publish events. No numbers are invented: anything the
APIs have not provided is shown as "no data yet", with the reporting period and freshness.
"""
from __future__ import annotations

import datetime as dt
import json
import os
import statistics
import time
from pathlib import Path

import requests

ROOT = Path(__file__).resolve().parents[1]


def _iso(ts: float | None) -> str | None:
    return dt.datetime.fromtimestamp(ts, dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ") if ts else None


def collect(state, cfg) -> dict:
    db = state.db
    now = time.time()
    jobs = [dict(r) for r in db.execute("SELECT id, topic_id, stage, status, error, created_at, updated_at FROM jobs")]
    topics = {r["id"]: dict(r) for r in db.execute("SELECT id, title, pillar, status, score FROM topics")}
    costs = [dict(r) for r in db.execute("SELECT job_id, provider, item, usd, estimated, at FROM costs")]
    uploads = {r["job_id"]: dict(r) for r in db.execute("SELECT * FROM uploads")}
    feats = {r["job_id"]: json.loads(r["data"]) for r in db.execute("SELECT job_id, data FROM features")}
    arms = {}
    for r in db.execute("SELECT experiment_id, job_id, arm FROM assignments"):
        arms.setdefault(r["job_id"], {})[r["experiment_id"]] = r["arm"]
    fb = [dict(r) for r in db.execute("SELECT at, job_id, decision, note FROM feedback ORDER BY at DESC LIMIT 50")]
    revenue = [dict(r) for r in db.execute("SELECT period, video_id, usd, source FROM revenue")]
    daily = [{"day": r["day"], **json.loads(r["data"])} for r in db.execute("SELECT day, data FROM channel_daily ORDER BY day")]
    events = [dict(r) for r in db.execute(
        "SELECT at, level, job_id, message FROM events WHERE level IN ('error','warn') ORDER BY at DESC LIMIT 40")]
    # latest snapshot per video + snapshots by age (for like-for-like comparisons)
    snaps: dict[str, list] = {}
    for r in db.execute("SELECT video_id, fetched_at, age_hours, data FROM metrics ORDER BY fetched_at"):
        snaps.setdefault(r["video_id"], []).append({"age_h": round(r["age_hours"] or 0, 1), "at": r["fetched_at"],
                                                   **json.loads(r["data"])})
    detail = {}
    for r in db.execute("SELECT video_id, kind, data, at FROM video_detail"):
        detail.setdefault(r["video_id"], {})[r["kind"]] = json.loads(r["data"])
    last_metrics = db.execute("SELECT MAX(fetched_at) m FROM metrics").fetchone()["m"]

    cost_by_job: dict[str, float] = {}
    for c in costs:
        cost_by_job[c["job_id"] or "-"] = cost_by_job.get(c["job_id"] or "-", 0) + c["usd"]
    first_review: dict[str, float] = {}
    for r in db.execute("SELECT job_id, MIN(at) t FROM events WHERE message LIKE 'stage package done%' GROUP BY job_id"):
        first_review[r["job_id"]] = r["t"]

    videos = []
    for jid, up in uploads.items():
        j = next((x for x in jobs if x["id"] == jid), {})
        t = topics.get(j.get("topic_id"), {})
        s = snaps.get(up["video_id"]) or []
        latest = s[-1] if s else {}

        def at_age(days: int):
            cands = [x for x in s if x["age_h"] >= days * 24]
            return min(cands, key=lambda x: x["age_h"]) if cands else None

        api = [r["usd"] for r in revenue if r["video_id"] == up["video_id"] and r["source"] == "youtube_api_estimate"]
        rev = sum(api) if api else sum(r["usd"] for r in revenue if r["video_id"] == up["video_id"] and r["source"] == "owner")
        videos.append({
            "job": jid, "video_id": up["video_id"], "url": up["url"], "title": t.get("title") or jid,
            "pillar": t.get("pillar"), "publish_at": up["publish_at"], "status": up["status"],
            "cost": round(cost_by_job.get(jid, 0), 3),
            "revenue": round(rev, 2) if rev else None,
            "latest": latest, "d1": at_age(1), "d3": at_age(3), "d7": at_age(7), "d28": at_age(28),
            "snapshots": [{"age_h": x["age_h"], "views": x.get("views")} for x in s],
            "features": feats.get(jid, {}), "arms": arms.get(jid, {}),
            "retention": (detail.get(up["video_id"]) or {}).get("retention"),
            "traffic": (detail.get(up["video_id"]) or {}).get("traffic"),
        })

    status_counts: dict[str, int] = {}
    for j in jobs:
        status_counts[j["status"]] = status_counts.get(j["status"], 0) + 1
    # production time = job created -> first review-ready (one per topic version)
    make_minutes = [round((first_review[j["id"]] - j["created_at"]) / 60, 1) for j in jobs if j["id"] in first_review]
    fixed = (cfg.pipeline.get("fixed_costs_usd_month") or {})
    first_cost = min((c["at"] for c in costs), default=now)
    months_active = max(1.0, (now - first_cost) / (30.44 * 86400))
    api_cash = sum(c["usd"] for c in costs if c["provider"] != "elevenlabs")
    exps = [json.loads(r["data"]) for r in db.execute("SELECT data FROM experiments")]
    return {
        "generated_at": _iso(now),
        "metrics_fetched_at": _iso(last_metrics),
        "channel": cfg.channel.get("name") if hasattr(cfg, "channel") else "Secret Smart Stuff",
        "jobs": [{**j, "title": topics.get(j["topic_id"], {}).get("title"), "cost": round(cost_by_job.get(j["id"], 0), 3),
                  "reached_review": j["id"] in first_review,
                  "created": _iso(j["created_at"]), "updated": _iso(j["updated_at"])} for j in jobs],
        "status_counts": status_counts,
        "make_minutes": make_minutes,
        "costs": [{"day": _iso(c["at"])[:10], "provider": c["provider"], "item": c["item"], "usd": c["usd"],
                   "estimated": bool(c["estimated"]), "job": c["job_id"]} for c in costs],
        "fixed_monthly": fixed, "months_active": round(months_active, 2), "api_cash": round(api_cash, 2),
        "revenue": revenue, "videos": videos, "daily": daily, "events": [
            {**e, "at": _iso(e["at"])} for e in events],
        "feedback": [{**f, "at": _iso(f["at"])} for f in fb],
        "experiments": exps,
        "learnings": (state.get_setting("learnings_md") or "")[:8000],
        "topics_backlog": sum(1 for t in topics.values() if t["status"] == "shortlisted"),
    }


def build(state, cfg) -> str:
    data = collect(state, cfg)
    tpl = (ROOT / "shorts" / "dashboard_template.html").read_text()
    return tpl.replace("/*__DATA__*/null", json.dumps(data, default=str).replace("</", "<\\/"))


def upload(state, html: str) -> bool:
    """Put the page into the Worker's KV store (Cloudflare API). False if not configured."""
    acc, token = os.environ.get("CLOUDFLARE_ACCOUNT_ID", "").strip(), os.environ.get("CLOUDFLARE_API_TOKEN", "").strip()
    ns = state.get_setting("cf_kv_namespace")
    if not (acc and token and ns):
        return False
    r = requests.put(f"https://api.cloudflare.com/client/v4/accounts/{acc}/storage/kv/namespaces/{ns}/values/dashboard.html",
                     headers={"Authorization": f"Bearer {token}", "Content-Type": "text/html"},
                     data=html.encode("utf-8"), timeout=60)
    ok = r.status_code == 200 and r.json().get("success")
    if not ok:
        state.log(f"dashboard upload failed: {r.status_code} {r.text[:200]}", "warn")
    return bool(ok)


def median(xs):
    xs = [x for x in xs if x is not None]
    return statistics.median(xs) if xs else None
