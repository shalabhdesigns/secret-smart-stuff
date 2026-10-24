"""Command line entry point.

    python -m shorts.cli discover [--n 8]
    python -m shorts.cli produce [--topic ID]          # next best topic if no ID
    python -m shorts.cli decide JOB approve|reject|fix [--note "..."]
    python -m shorts.cli publish JOB [--at 2026-11-02T13:30:00Z]
    python -m shorts.cli status | summary | topics
    python -m shorts.cli run-daily                     # discover if backlog low, then produce one

Set SHORTS_MODE=live to use real providers (needs API keys); default is dry_run.
"""
from __future__ import annotations

import argparse
import json
import sys

from .config import load
from .pipeline import Pipeline


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(prog="shorts")
    ap.add_argument("--mode", choices=["dry_run", "live"])
    sub = ap.add_subparsers(dest="cmd", required=True)
    s = sub.add_parser("discover"); s.add_argument("--n", type=int, default=8)
    s.add_argument("--signals", help="JSON file of external signals (competitor outliers, questions)")
    s = sub.add_parser("produce"); s.add_argument("--topic")
    s = sub.add_parser("decide"); s.add_argument("job"); s.add_argument("decision", choices=["approve", "reject", "fix"])
    s.add_argument("--note", default="")
    s = sub.add_parser("publish"); s.add_argument("job"); s.add_argument("--at")
    sub.add_parser("status"); sub.add_parser("summary"); sub.add_parser("topics")
    s = sub.add_parser("run-daily"); s.add_argument("--min-backlog", type=int, default=5)
    sub.add_parser("analytics")
    s = sub.add_parser("upload-resolve"); s.add_argument("job")
    s.add_argument("--video-id", help="the video ID if YouTube Studio shows the upload did finish")
    s = sub.add_parser("next-slot")
    a = ap.parse_args(argv)

    p = Pipeline(load(mode=a.mode))
    if a.cmd == "discover":
        sig = json.load(open(a.signals)) if a.signals else None
        print(json.dumps(p.discover(a.n, sig), indent=1))
    elif a.cmd == "produce":
        tid = a.topic or (p.next_topic() or {}).get("id")
        if not tid:
            print("no topic available - run discover first"); return 1
        job = p.produce(tid)
        j = p.state.get_job(job)
        print(json.dumps({"job": job, "status": j["status"], "stage": j["stage"], "error": j["error"]}, indent=1))
        return 0 if j["status"] in ("review", "paused") else 2
    elif a.cmd == "decide":
        p.decide(a.job, a.decision, a.note)
        if a.decision == "fix":
            p.produce(p.state.get_job(a.job)["topic_id"])
    elif a.cmd == "publish":
        print(json.dumps(p.publish(a.job, a.at), indent=1))
    elif a.cmd == "status":
        for j in p.state.jobs():
            print(f"{j['status']:<10} {j['stage']:<8} {j['id']}  {j['error'] or ''}")
    elif a.cmd == "topics":
        for t in p.state.topics():
            print(f"{t['status']:<12} {t['score'] or 0:5.1f}  {t['pillar'] or '-':<13} {t['title']}")
    elif a.cmd == "summary":
        print(p.summary())
    elif a.cmd == "analytics":
        from . import analytics as an
        print(json.dumps(an.snapshot(p.state), indent=1))
        print(json.dumps(an.insights(p.state, p.cfg.root / "data" / "insights.json"), indent=1))
    elif a.cmd == "upload-resolve":
        row = p.state.db.execute("SELECT * FROM uploads WHERE job_id=?", (a.job,)).fetchone()
        if not row:
            print("no upload record for that job"); return 1
        if a.video_id:
            p.state.record_upload(a.job, row["idempotency"], "uploaded", video_id=a.video_id,
                                  url=f"https://youtube.com/shorts/{a.video_id}")
        else:
            p.state.record_upload(a.job, row["idempotency"], "failed")
        p.state.log(f"upload resolved by owner: {a.video_id or 'not on YouTube, retry allowed'}", job_id=a.job)
    elif a.cmd == "next-slot":
        print(next_slot(p))
    elif a.cmd == "run-daily":
        if len(p.state.topics("shortlisted")) < a.min_backlog:
            p.discover()
        t = p.next_topic()
        if t:
            job = p.produce(t["id"])
            print(json.dumps({"job": job, "status": p.state.get_job(job)["status"]}))
    return 0


def next_slot(p: Pipeline) -> str:
    """Next free publish slot (RFC 3339 UTC), at least 2 h from now, one video per slot."""
    import datetime as dt
    slots = p.cfg.pipeline["schedule"]["publish_slots_utc"]
    taken = {r["publish_at"] for r in p.state.db.execute("SELECT publish_at FROM uploads WHERE publish_at IS NOT NULL")}
    now = dt.datetime.now(dt.timezone.utc) + dt.timedelta(hours=2)
    for day in range(0, 60):
        for s in slots:
            h, m = (int(x) for x in s.split(":"))
            cand = (now + dt.timedelta(days=day)).replace(hour=h, minute=m, second=0, microsecond=0)
            iso = cand.strftime("%Y-%m-%dT%H:%M:%SZ")
            if cand > now and iso not in taken:
                return iso
    raise RuntimeError("no free slot in 60 days")


if __name__ == "__main__":
    sys.exit(main())
