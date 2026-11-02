"""Owner dashboard: one self-contained HTML page built from the state DB (rebuilt 3 Nov 2026).

Served privately by the Cloudflare Worker at /dash (login code via Telegram); free to host. Rebuilt by every
analytics pass (every 6 h) and on demand (the page's "Refresh now" button starts one).

No invented numbers. Every figure carries one of these labels:
- measured   : reported by the service's API, or counted by our own runs (tokens, characters, minutes, views)
- calculated : measured usage x the provider's list price (e.g. Anthropic tokens x price) - not an invoice
- allocated  : a shared cost split by a stated rule (subscriptions, overheads, dropped attempts)
- estimated  : list price per item where the provider reports nothing (e.g. an image when BFL gave no cost)
- manual     : typed in by the owner, with the date
- unavailable: the platform has no API for it (the page says why)
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
FORMAT_START = "2026-10-20"           # Secret Smart Stuff explainers; earlier costs belong to the archived format
ARCHIVED_PROVIDERS = ("sketch", "art")


def _iso(ts: float | None) -> str | None:
    return dt.datetime.fromtimestamp(ts, dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ") if ts else None


def _month(ts: float) -> str:
    return dt.datetime.fromtimestamp(ts, dt.timezone.utc).strftime("%Y-%m")


def _j(s, default=None):
    try:
        return json.loads(s) if s else default
    except (TypeError, ValueError):
        return default


def collect(state, cfg) -> dict:
    db = state.db
    now = time.time()
    from .usage import manual
    man = manual(state)
    topics = {r["id"]: dict(r) for r in db.execute("SELECT id, title, pillar, status, notes FROM topics")}
    jobs = {r["id"]: dict(r) for r in db.execute("SELECT id, topic_id, stage, status, error, created_at, updated_at "
                                                  "FROM jobs")}
    uploads = {r["job_id"]: dict(r) for r in db.execute("SELECT * FROM uploads WHERE video_id IS NOT NULL")}
    costs = [dict(r) for r in db.execute("SELECT job_id, provider, item, quantity, usd, estimated, at, meta FROM costs")]
    costs = [c for c in costs if c["provider"] not in ARCHIVED_PROVIDERS]
    archived_usd = db.execute("SELECT COALESCE(SUM(usd),0) s FROM costs WHERE provider IN ('sketch','art')").fetchone()["s"]
    feats = {r["job_id"]: _j(r["data"], {}) for r in db.execute("SELECT job_id, data FROM features")}
    arms = {}
    for r in db.execute("SELECT experiment_id, job_id, arm FROM assignments"):
        arms.setdefault(r["job_id"], {})[r["experiment_id"]] = r["arm"]
    snaps: dict[str, list] = {}
    for r in db.execute("SELECT video_id, fetched_at, age_hours, data FROM metrics ORDER BY fetched_at"):
        snaps.setdefault(r["video_id"], []).append({"age_h": round(r["age_hours"] or 0, 1), "at": _iso(r["fetched_at"]),
                                                   **_j(r["data"], {})})
    detail = {}
    for r in db.execute("SELECT video_id, kind, data FROM video_detail"):
        detail.setdefault(r["video_id"], {})[r["kind"]] = _j(r["data"])
    live = _j(state.get_setting("yt_live_json"), {}) or {}
    try:
        igp = {r["job_id"]: dict(r) for r in db.execute(
            "SELECT job_id, status, permalink, media_id, publish_at FROM ig_posts")}
    except Exception:  # noqa: BLE001 - created on first Instagram post
        igp = {}
    igm: dict[str, list] = {}
    try:
        for r in db.execute("SELECT job_id, age_hours, data, at FROM ig_metrics ORDER BY at"):
            igm.setdefault(r["job_id"], []).append({"age_h": round(r["age_hours"], 1), "at": _iso(r["at"]),
                                                   **_j(r["data"], {})})
    except Exception:  # noqa: BLE001
        pass
    reviews: dict[str, dict] = {}
    try:
        for r in db.execute("SELECT job_id, tag, data, at FROM video_reviews ORDER BY at"):
            reviews.setdefault(r["job_id"], {})[r["tag"]] = {**_j(r["data"], {}), "at": _iso(r["at"])}
    except Exception:  # noqa: BLE001
        pass
    run_jobs: dict[int, list] = {}
    gh_min: dict[int, float] = {}
    try:
        for r in db.execute("SELECT run_id, job_id FROM run_jobs"):
            run_jobs.setdefault(r["run_id"], []).append(r["job_id"])
        for r in db.execute("SELECT run_id, billable_ms, duration_ms FROM gh_runs"):
            gh_min[r["run_id"]] = max(r["billable_ms"] or 0, r["duration_ms"] or 0) / 60000
    except Exception:  # noqa: BLE001
        pass
    minutes_by_job: dict[str, float] = {}
    for rid, js in run_jobs.items():
        for jb in js:
            minutes_by_job[jb] = minutes_by_job.get(jb, 0) + gh_min.get(rid, 0) / len(js)

    # ---------- costs: direct per job, by provider, with labels ----------
    res = (_j(state.get_setting("resources_json"), {}) or {}).get("items", {})
    el = res.get("elevenlabs") or {}
    el_plan_usd = None
    el_plan_src = None
    sub_el = (man.get("subscriptions") or {}).get("elevenlabs") or {}
    if sub_el.get("usd_month"):
        el_plan_usd, el_plan_src = float(sub_el["usd_month"]), "manual"
    elif el.get("next_invoice"):
        el_plan_usd, el_plan_src = float(el["next_invoice"]), "measured (next invoice)"
    el_limit = el.get("limit")
    per_char = (el_plan_usd / el_limit) if (el_plan_usd and el_limit) else None

    direct: dict[str, dict] = {}
    for c in costs:
        jid = c["job_id"] or "-"
        d = direct.setdefault(jid, {})
        p = c["provider"]
        e = d.setdefault(p, {"usd": 0.0, "qty": 0.0, "n": 0, "labels": set(), "tokens": 0})
        meta = _j(c["meta"], {}) or {}
        if p == "anthropic":
            e["usd"] += c["usd"]
            e["labels"].add("calculated")
            e["tokens"] += int(c["quantity"] or 0) if meta else 0
        elif p == "elevenlabs":
            e["qty"] += c["quantity"] or 0
            if per_char:
                e["usd"] += (c["quantity"] or 0) * per_char
                e["labels"].add("allocated")
            else:
                e["usd"] += c["usd"]
                e["labels"].add("estimated")
        elif p == "bfl":
            e["usd"] += c["usd"]
            e["labels"].add("measured" if meta.get("source") == "api" else "estimated")
        else:
            e["usd"] += c["usd"]
            e["labels"].add("estimated" if c["estimated"] else "calculated")
        e["n"] += 1
    for d in direct.values():
        for e in d.values():
            e["labels"] = sorted(e["labels"])
            e["usd"] = round(e["usd"], 3)

    def job_direct(jid: str) -> float:
        return sum(e["usd"] for e in (direct.get(jid) or {}).values())

    # ---------- monthly overheads -> allocated per published video ----------
    months: dict[str, dict] = {}
    for c in costs:
        m = _month(c["at"])
        mm = months.setdefault(m, {"by_provider": {}, "overhead": 0.0, "dropped": 0.0, "published": 0, "direct": 0.0})
        mm["by_provider"][c["provider"]] = mm["by_provider"].get(c["provider"], 0) + c["usd"]
    for jid, up in uploads.items():
        m = (up.get("publish_at") or "")[:7] or _month(up["at"])
        months.setdefault(m, {"by_provider": {}, "overhead": 0.0, "dropped": 0.0, "published": 0, "direct": 0.0})
        months[m]["published"] += 1
    for c in costs:          # each dollar counts in the month it was spent
        jid = c["job_id"] or "-"
        mm = months[_month(c["at"])]
        usd = c["usd"]
        if c["provider"] == "elevenlabs" and per_char:
            usd = (c["quantity"] or 0) * per_char
        j = jobs.get(jid)
        if jid == "-":
            mm["overhead"] += usd
        elif jid not in uploads and (not j or j["status"] in ("rejected", "failed")):
            mm["dropped"] += usd
        else:
            mm["direct"] += usd
    subs = man.get("subscriptions") or {}
    for m, mm in months.items():
        alloc = []
        for name, s in subs.items():
            if name == "elevenlabs" or not s.get("usd_month"):
                continue         # ElevenLabs is already spread per character above
            share = float(s.get("share_pct") or 100) / 100
            alloc.append({"name": name, "usd": round(float(s["usd_month"]) * share, 2),
                          "rule": f"${float(s['usd_month']):.2f}/month x {share * 100:.0f}% used for this channel",
                          "label": "allocated", "typed": s.get("at")})
        mm["subscriptions"] = alloc
        n = max(1, mm["published"])
        mm["per_video_overhead"] = round((mm["overhead"] + mm["dropped"] + sum(a["usd"] for a in alloc)) / n, 3)
        mm["by_provider"] = {k: round(v, 2) for k, v in mm["by_provider"].items()}
        for k in ("overhead", "dropped", "direct"):
            mm[k] = round(mm[k], 2)

    # ---------- revenue (manual + YouTube API if ever monetised) ----------
    rev_rows = [dict(r) for r in db.execute("SELECT period, video_id, usd, source FROM revenue")]
    for r in man.get("revenue") or []:
        rev_rows.append({"period": r.get("period"), "video_id": r.get("video_id") or "", "job": r.get("job") or "",
                         "platform": r.get("platform") or "", "usd": float(r.get("usd") or 0), "source": "manual",
                         "note": r.get("note"), "at": r.get("at")})

    # ---------- videos ----------
    videos = []
    for jid, up in sorted(uploads.items(), key=lambda kv: kv[1].get("publish_at") or ""):
        j = jobs.get(jid) or {}
        t = topics.get(j.get("topic_id"), {})
        notes = _j(t.get("notes"), {}) or {}
        s = snaps.get(up["video_id"]) or []
        yt_latest = s[-1] if s else {}
        lv = live.get(up["video_id"]) or {}
        ig = igm.get(jid) or []
        ig_latest = ig[-1] if ig else {}
        f = feats.get(jid, {})
        pub_m = (up.get("publish_at") or "")[:7]
        overhead = (months.get(pub_m) or {}).get("per_video_overhead", 0)
        dcost = job_direct(jid)
        revs = [r for r in rev_rows if r.get("video_id") == up["video_id"] or r.get("job") == jid]
        revenue = round(sum(r["usd"] for r in revs), 2) if revs else None
        yt_views = lv.get("views") if lv else yt_latest.get("views")
        ig_views = ig_latest.get("views")
        full = round(dcost + overhead, 2)
        videos.append({
            "job": jid, "title": t.get("title") or jid, "pillar": t.get("pillar"), "news": bool(notes.get("news")),
            "published": up.get("publish_at"), "yt_url": up.get("url"), "yt_id": up["video_id"],
            "ig_url": (igp.get(jid) or {}).get("permalink"), "ig_status": (igp.get(jid) or {}).get("status"),
            "yt_live": lv or None,
            "yt": {k: yt_latest.get(k) for k in ("views", "engagedViews", "estimatedMinutesWatched", "averageViewDuration",
                                                  "averageViewPercentage", "likes", "comments", "shares",
                                                  "subscribersGained", "subscribersLost")} | {"age_h": yt_latest.get("age_h"),
                                                                                              "at": yt_latest.get("at")},
            "yt_series": [{"age_h": x["age_h"], "views": x.get("views")} for x in s],
            "ig": ({k: ig_latest.get(k) for k in ("views", "reach", "likes", "comments", "shares", "saved",
                                                  "total_interactions", "ig_reels_avg_watch_time",
                                                  "ig_reels_video_view_total_time", "reels_skip_rate")}
                   | {"age_h": ig_latest.get("age_h"), "at": ig_latest.get("at")}) if ig_latest else None,
            "ig_series": [{"age_h": x["age_h"], "views": x.get("views")} for x in ig],
            "retention": (detail.get(up["video_id"]) or {}).get("retention"),
            "traffic": (detail.get(up["video_id"]) or {}).get("traffic"),
            "views_total": (yt_views or 0) + (ig_views or 0),
            "cost": {"direct": round(dcost, 2), "by_provider": direct.get(jid, {}), "overhead_share": overhead,
                     "full": full, "gh_minutes": round(minutes_by_job.get(jid, 0), 1)},
            "revenue": revenue, "revenue_rows": revs,
            "profit": round(revenue - full, 2) if revenue is not None else None,
            "roi_pct": round(100 * (revenue - full) / full, 1) if revenue is not None and full else None,
            "features": {k: f.get(k) for k in ("hook_text", "hook_formula", "seconds", "beats", "words", "images",
                                               "wit_lines", "pops", "music", "publish_slot_utc", "self_review")},
            "learnings_applied": len(f.get("learnings_applied") or []),
            "arms": arms.get(jid, {}), "reviews": reviews.get(jid, {}),
        })

    # ---------- channel level ----------
    daily = [{"day": r["day"], **_j(r["data"], {})} for r in db.execute("SELECT day, data FROM channel_daily ORDER BY day")]
    try:
        ig_daily = [{"day": r["day"], **_j(r["data"], {})} for r in db.execute(
            "SELECT day, data FROM ig_account_daily ORDER BY day")]
    except Exception:  # noqa: BLE001
        ig_daily = []
    attempts = [{"job": jid, "title": topics.get(j["topic_id"], {}).get("title"), "status": j["status"],
                 "error": (j["error"] or "")[:200], "created": _iso(j["created_at"]), "cost": round(job_direct(jid), 2),
                 "published": jid in uploads}
                for jid, j in jobs.items() if j["created_at"] >= dt.datetime.fromisoformat(FORMAT_START).replace(
                    tzinfo=dt.timezone.utc).timestamp()]
    events = [{"at": _iso(r["at"]), "level": r["level"], "job": r["job_id"], "msg": r["message"][:300]} for r in db.execute(
        "SELECT at, level, job_id, message FROM events WHERE level IN ('error','warn') ORDER BY at DESC LIMIT 40")]
    exps = [_j(r["data"], {}) for r in db.execute("SELECT data FROM experiments")]
    return {
        "generated_at": _iso(now),
        "metrics_at": _iso(db.execute("SELECT MAX(fetched_at) m FROM metrics").fetchone()["m"]),
        "refresh": {"every_hours": 6, "note": "YouTube Analytics (watch time, retention) lags 1-2 days; Instagram "
                    "insights up to 48 h; live YouTube counts come from the Data API at every refresh."},
        "videos": videos, "attempts": attempts, "months": months,
        "archived_usd": round(archived_usd, 2), "manual": man,
        "elevenlabs_rate": {"usd_per_char": per_char, "plan_usd": el_plan_usd, "plan_source": el_plan_src,
                            "plan_chars": el_limit},
        "resources": res, "resources_at": (_j(state.get_setting("resources_json"), {}) or {}).get("at"),
        "daily": daily, "ig_daily": ig_daily, "events": events, "experiments": exps,
        "learnings_md": (state.get_setting("learnings_md") or "")[:9000],
        "writer_rules": (state.get_setting("lessons_for_writer") or "")[:3000],
        "topic_guidance": (state.get_setting("topic_guidance") or "")[:2000],
        "costs_raw": [{"day": _iso(c["at"])[:10], "job": c["job_id"], "provider": c["provider"], "item": c["item"],
                       "qty": c["quantity"], "usd": round(c["usd"], 4), "label": (
                           "calculated" if c["provider"] == "anthropic" else
                           ("measured" if (_j(c["meta"], {}) or {}).get("source") == "api" else "estimated"))}
                      for c in costs if c["at"] >= now - 62 * 86400],
    }


def build(state, cfg) -> str:
    data = collect(state, cfg)
    tpl = (ROOT / "shorts" / "dashboard_template.html").read_text()
    return tpl.replace("/*__DATA__*/null", json.dumps(data, default=str).replace("</", "<\\/"))


def upload(state, html: str) -> bool:
    """Put the page into the Worker's KV store (Cloudflare API). False if not configured."""
    token = os.environ.get("CLOUDFLARE_API_TOKEN", "").strip()
    acc = os.environ.get("CLOUDFLARE_ACCOUNT_ID", "").strip()
    if not acc:                       # the account id is not secret; it lives in config/pipeline.yaml
        from .config import load
        acc = str(load().pipeline.get("cloudflare_account_id", "")).strip()
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
