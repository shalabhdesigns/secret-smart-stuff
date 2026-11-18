"""Cost per video for the last N hours (owner, 18 Nov 2026: "Each day you must check how much money we are spending on
each video and find ways to further reduce it ... down to bare minimum").

Usage: git show origin/state:state/live.db > /tmp/live.db && python3 scripts/cost_report.py /tmp/live.db [hours=24]
Prints, per job: total, by provider, by stage, and whether it was published; then the day's total and the waste
(money spent on jobs that were not published).
"""
import sqlite3
import sys
import time
from collections import defaultdict


def main(db: str, hours: float = 24) -> None:
    c = sqlite3.connect(db)
    since = time.time() - hours * 3600
    rows = c.execute("select job_id, provider, item, usd from costs where at >= ?", (since,)).fetchall()
    status = dict(c.execute("select id, status from jobs").fetchall())
    per = defaultdict(lambda: {"total": 0.0, "prov": defaultdict(float), "stage": defaultdict(float)})
    for job, prov, item, usd in rows:
        p = per[job or "(no job)"]
        p["total"] += usd or 0
        p["prov"][prov] += usd or 0
        stage = "review" if str(item).startswith("review") else "fix" if str(item).startswith("fix") else item
        p["stage"][stage] += usd or 0
    day, waste = 0.0, 0.0
    print(f"Cost per video, last {hours:g} h (USD)")
    for job, p in sorted(per.items(), key=lambda kv: -kv[1]["total"]):
        st = status.get(job, "-")
        day += p["total"]
        if st not in ("published", "review", "approved"):
            waste += p["total"]
        prov = ", ".join(f"{k} {v:.3f}" for k, v in sorted(p["prov"].items(), key=lambda kv: -kv[1]))
        top = ", ".join(f"{k} {v:.3f}" for k, v in sorted(p["stage"].items(), key=lambda kv: -kv[1])[:5])
        print(f"- {job} [{st}] {p['total']:.3f} | {prov} | top stages: {top}")
    print(f"TOTAL {day:.2f} | spent on jobs not published: {waste:.2f}")


if __name__ == "__main__":
    main(sys.argv[1], float(sys.argv[2]) if len(sys.argv) > 2 else 24)
