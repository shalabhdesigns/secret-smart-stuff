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
METRICS = ["views", "engagedViews", "averageViewDuration", "averageViewPercentage",
           "likes", "comments", "shares", "subscribersGained"]


def _query(token: str, video_ids: list[str], start: str, end: str, metrics: list[str]) -> dict:
    r = requests.get(REPORTS, headers={"Authorization": f"Bearer {token}"}, timeout=60, params={
        "ids": "channel==MINE", "startDate": start, "endDate": end, "metrics": ",".join(metrics),
        "dimensions": "video", "filters": "video==" + ",".join(video_ids), "maxResults": 200})
    return {"status": r.status_code, "body": r.json() if r.content else {}}


def snapshot(state: State, start_date: str = "2026-01-01") -> dict:
    rows = state.db.execute("SELECT job_id, video_id, at FROM uploads WHERE video_id IS NOT NULL").fetchall()
    if not rows:
        return {"videos": 0}
    token = access_token()
    end = time.strftime("%Y-%m-%d", time.gmtime())
    ids = [r["video_id"] for r in rows]
    metrics, missing = list(METRICS), []
    res = _query(token, ids, start_date, end, metrics)
    while res["status"] == 400 and len(metrics) > 1:
        dropped = metrics.pop(1)                 # drop optional metrics one by one
        missing.append(dropped)
        res = _query(token, ids, start_date, end, metrics)
    if res["status"] != 200:
        raise RuntimeError(f"analytics error {res['status']}: {str(res['body'])[:300]}")
    cols = [h["name"] for h in res["body"].get("columnHeaders", [])]
    uploaded_at = {r["video_id"]: r["at"] for r in rows}
    for row in res["body"].get("rows", []):
        rec = dict(zip(cols, row))
        vid = rec.get("video")
        age = (time.time() - uploaded_at.get(vid, time.time())) / 3600
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
