"""Stage I: performance snapshots and the feedback loop.

- Pulls per-video metrics from the YouTube Analytics API (official), stores raw
  JSON with the video's age, so later comparisons are like-for-like.
- Compares each video with the channel's own median at the same age.
- Updates pillar weights for discovery only when there is enough data.

Known limits (documented, not hidden):
- Data typically lags 48-72 h.
- "Viewed vs swiped away" appears to be YouTube Studio only; the owner can paste
  it weekly into data/studio_notes.csv if wanted.
- Some metrics (e.g. engagedViews) may be unavailable for an account or period;
  we retry without them and record which were missing.
"""
from __future__ import annotations

import json
import statistics
import time
from pathlib import Path

import requests

from .publish.youtube import access_token
from .state import State

REPORTS = "https://youtubeanalytics.googleapis.com/v2/reports"
METRICS = ["views", "engagedViews", "estimatedMinutesWatched", "averageViewDuration", "averageViewPercentage",
           "likes", "comments", "shares", "subscribersGained", "subscribersLost"]
DAILY = ["views", "engagedViews", "estimatedMinutesWatched", "subscribersGained", "subscribersLost",
         "likes", "comments", "shares"]


def _query(token: str, video_ids: list[str], start: str, end: str, metrics: list[str]) -> dict:
    r = requests.get(REPORTS, headers={"Authorization": f"Bearer {token}"}, timeout=60, params={
        "ids": "channel==MINE", "startDate": start, "endDate": end, "metrics": ",".join(metrics),
        "dimensions": "video", "filters": "video==" + ",".join(video_ids), "maxResults": 200,
        "sort": "-views"})
    return {"status": r.status_code, "body": r.json() if r.content else {}}


def snapshot(state: State, start_date: str = "2026-01-01") -> dict:
    rows = state.db.execute("SELECT job_id, video_id, at, publish_at FROM uploads "
                            "WHERE video_id IS NOT NULL").fetchall()
    if not rows:
        return {"videos": 0}
    token = access_token()
    end = time.strftime("%Y-%m-%d", time.gmtime())
    import datetime as dt
    ids = [r["video_id"] for r in rows]
    live_at = {}
    for r in rows:   # age counts from going public (publish_at), not from the private upload
        ts = r["at"]
        if r["publish_at"]:
            ts = dt.datetime.strptime(r["publish_at"], "%Y-%m-%dT%H:%M:%SZ").replace(
                tzinfo=dt.timezone.utc).timestamp()
        live_at[r["video_id"]] = ts
    metrics, missing = list(METRICS), []
    for i in range(0, len(ids), 200):
        batch = ids[i:i + 200]
        res = _query(token, batch, start_date, end, metrics)
        for optional in ("engagedViews", "averageViewPercentage", "estimatedMinutesWatched", "subscribersLost"):
            if res["status"] == 400 and optional in str(res["body"]) and optional in metrics:
                metrics.remove(optional)
                missing.append(optional)
                res = _query(token, batch, start_date, end, metrics)
        if res["status"] != 200:
            raise RuntimeError(f"analytics error {res['status']}: {str(res['body'])[:300]}")
        cols = [h["name"] for h in res["body"].get("columnHeaders", [])]
        for row in res["body"].get("rows", []):
            rec = dict(zip(cols, row))
            vid = rec.get("video")
            age = (time.time() - live_at.get(vid, time.time())) / 3600
            if age < 0:
                continue          # not public yet
            state.add_metrics(vid, rec | {"missing_metrics": missing}, age)
    return {"videos": len(ids), "missing_metrics": missing}


def insights(state: State, out: Path, min_videos: int = 10, min_views: int = 1000, age_days: int = 7) -> dict:
    """Pillar performance at a fixed age; only acted on with enough data."""
    q = """SELECT u.video_id, t.pillar, m.data, m.age_hours FROM uploads u
           JOIN jobs j ON j.id=u.job_id JOIN topics t ON t.id=j.topic_id
           JOIN metrics m ON m.video_id=u.video_id WHERE m.age_hours >= ?"""
    latest: dict[str, tuple] = {}
    for r in state.db.execute(q, (age_days * 24,)):
        # keep the snapshot closest to the target age
        prev = latest.get(r["video_id"])
        if prev is None or abs(r["age_hours"] - age_days * 24) < abs(prev[2] - age_days * 24):
            latest[r["video_id"]] = (r["pillar"], json.loads(r["data"]), r["age_hours"])
    vids = [(p, d) for p, d, _ in latest.values() if d.get("views", 0) >= min_views]
    result: dict = {"videos_considered": len(vids), "enough_data": len(vids) >= min_videos, "pillars": {}}
    if vids:
        med = statistics.median(d["views"] for _, d in vids)
        by: dict[str, list] = {}
        for p, d in vids:
            by.setdefault(p or "unknown", []).append(d)
        for p, ds in by.items():
            result["pillars"][p] = {
                "n": len(ds),
                "median_views_vs_channel": round(statistics.median(x["views"] for x in ds) / med, 2) if med else None,
                "avg_view_pct": round(statistics.mean(x.get("averageViewPercentage", 0) for x in ds), 1),
                "subs_per_1k_views": round(1000 * sum(x.get("subscribersGained", 0) for x in ds)
                                           / max(1, sum(x["views"] for x in ds)), 2),
            }
    out.write_text(json.dumps(result, indent=2))
    return result


def adjusted_pillar_shares(base: list[dict], insight: dict) -> list[dict]:
    """Shift pillar shares toward winners, bounded to 0.5x-1.5x of the base share,
    and only when there is enough data. Keeps exploring: no pillar drops to zero."""
    if not insight.get("enough_data"):
        return base
    out = []
    for p in base:
        perf = insight["pillars"].get(p["id"], {}).get("median_views_vs_channel") or 1.0
        out.append(p | {"share": p["share"] * max(0.5, min(1.5, perf))})
    total = sum(p["share"] for p in out)
    return [p | {"share": p["share"] / total} for p in out]


def _get(token: str, params: dict) -> tuple[int, dict]:
    r = requests.get(REPORTS, headers={"Authorization": f"Bearer {token}"}, timeout=60,
                     params={"ids": "channel==MINE", **params})
    return r.status_code, (r.json() if r.content else {})


def _rows(body: dict) -> list[dict]:
    cols = [h["name"] for h in body.get("columnHeaders", [])]
    return [dict(zip(cols, row)) for row in body.get("rows", []) or []]


def channel_daily(state: State, days: int = 400) -> dict:
    """Channel totals per day (for trends and period views on the dashboard)."""
    import datetime as dt
    first = state.db.execute("SELECT MIN(publish_at) p FROM uploads WHERE publish_at IS NOT NULL").fetchone()["p"]
    if not first:
        return {"days": 0}
    start = max(dt.date.fromisoformat(first[:10]) - dt.timedelta(days=1),
                dt.date.today() - dt.timedelta(days=days)).isoformat()
    end = time.strftime("%Y-%m-%d", time.gmtime())
    token = access_token()
    metrics = list(DAILY)
    code, body = _get(token, {"startDate": start, "endDate": end, "metrics": ",".join(metrics), "dimensions": "day", "sort": "day"})
    if code == 400 and "engagedViews" in str(body):
        metrics.remove("engagedViews")
        code, body = _get(token, {"startDate": start, "endDate": end, "metrics": ",".join(metrics), "dimensions": "day", "sort": "day"})
    if code != 200:
        state.log(f"channel daily analytics {code}: {str(body)[:200]}", "warn")
        return {"error": code}
    rows = _rows(body)
    with state.tx() as db:
        for r in rows:
            db.execute("INSERT INTO channel_daily(day, data, at) VALUES (?,?,?) ON CONFLICT(day) DO UPDATE SET "
                       "data=excluded.data, at=excluded.at", (r.pop("day"), json.dumps(r), time.time()))
    return {"days": len(rows)}


def video_details(state: State) -> dict:
    """Retention curve and traffic sources per public video (one call each, small channel)."""
    token = access_token()
    end = time.strftime("%Y-%m-%d", time.gmtime())
    done, errors = 0, []
    for r in state.db.execute("SELECT video_id, publish_at FROM uploads WHERE status='live'").fetchall():
        vid, start = r["video_id"], (r["publish_at"] or "2026-01-01")[:10]
        queries = {
            "retention": {"metrics": "audienceWatchRatio,relativeRetentionPerformance",
                          "dimensions": "elapsedVideoTimeRatio", "filters": f"video=={vid}"},
            "traffic": {"metrics": "views,estimatedMinutesWatched", "dimensions": "insightTrafficSourceType",
                        "filters": f"video=={vid}", "sort": "-views"},
        }
        for kind, q in queries.items():
            code, body = _get(token, {"startDate": start, "endDate": end, **q})
            if code == 400 and kind == "retention" and "relativeRetentionPerformance" in str(body):
                q["metrics"] = "audienceWatchRatio"
                code, body = _get(token, {"startDate": start, "endDate": end, **q})
            if code != 200:
                errors.append(f"{vid} {kind}: {code}")
                continue
            with state.tx() as db:
                db.execute("INSERT INTO video_detail(video_id, kind, data, at) VALUES (?,?,?,?) ON CONFLICT(video_id, kind) "
                           "DO UPDATE SET data=excluded.data, at=excluded.at", (vid, kind, json.dumps(_rows(body)), time.time()))
            done += 1
    if errors:
        state.log("video detail analytics: " + "; ".join(errors[:5]), "warn")
    return {"details": done, "errors": errors[:5]}


def revenue_from_api(state: State) -> dict:
    """Estimated revenue per video per month, if the channel is monetised AND the monetary scope was
    granted. Otherwise returns why not; revenue then comes from the owner's /revenue entries."""
    token = access_token()
    end = time.strftime("%Y-%m-%d", time.gmtime())
    code, body = _get(token, {"startDate": "2026-10-01", "endDate": end, "metrics": "estimatedRevenue",
                              "dimensions": "video", "sort": "-estimatedRevenue", "maxResults": 200})
    if code != 200:
        return {"available": False, "why": f"{code}: {str(body.get('error', {}).get('message', body))[:160]}"}
    with state.tx() as db:
        for r in _rows(body):
            db.execute("INSERT INTO revenue(period, video_id, usd, source, at) VALUES (?,?,?,?,?) ON CONFLICT(period, "
                       "video_id, source) DO UPDATE SET usd=excluded.usd, at=excluded.at",
                       ("lifetime", r["video"], float(r["estimatedRevenue"]), "youtube_api_estimate", time.time()))
    # channel revenue per day, merged into channel_daily for period views
    code, body = _get(token, {"startDate": "2026-10-01", "endDate": end, "metrics": "estimatedRevenue",
                              "dimensions": "day", "sort": "day"})
    if code == 200:
        with state.tx() as db:
            for r in _rows(body):
                row = db.execute("SELECT data FROM channel_daily WHERE day=?", (r["day"],)).fetchone()
                data = json.loads(row["data"]) if row else {}
                data["estimatedRevenue"] = r["estimatedRevenue"]
                db.execute("INSERT INTO channel_daily(day, data, at) VALUES (?,?,?) ON CONFLICT(day) DO UPDATE SET "
                           "data=excluded.data, at=excluded.at", (r["day"], json.dumps(data), time.time()))
    return {"available": True}
