"""GTA 6 performance analysis: learn only from GTA videos, with numbers (owner, 20 Nov 2026).

Owner: "Every video should contribute to a better understanding of what works, what doesn't, and why. Analyse the
actual performance, identify specific opportunities, and translate those findings into concrete changes in
subsequent videos." and "Stop incorporating learnings from our earlier product-focused videos."

Usage: git show origin/state:state/live.db > /tmp/live.db && python3 scripts/gta_learn.py /tmp/live.db
Writes the numbers part of docs/GTA_LEARNINGS.md (between the AUTO markers) and data/gta_perf.json.
No API calls, no cost. Claude's daily run reads it, evaluates the running experiments, decides the next ones and
applies them to tomorrow's scripts (the experiments log in the same file is written by Claude).
"""
from __future__ import annotations

import json
import re
import sqlite3
import statistics as st
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DOC = ROOT / "docs" / "GTA_LEARNINGS.md"
START, END = "<!-- AUTO:START -->", "<!-- AUTO:END -->"
LOGO_FROM = "2026-11-19T20:00:00Z"      # first video whose cover/first screen had the real GTA VI logo
STORY_FROM = 1795392000                  # ~18 Nov 2026: story format + Mark voice

CATS = [("money", r"price|cost|cheap|rupee|₹|\$|dollar|worth|edition|buy"),
        ("records", r"record|views|biggest|million|fastest|sales|sold"),
        ("characters", r"lucia|jason|character|cast|cal |boobie|brian"),
        ("real world", r"florida|miami|real|map|keys|everglades|tokyo|city"),
        ("drama", r"leak|court|hack|delay|lawsuit|war"),
        ("tech", r"pc|disc|ps5|xbox|storage|gb|download|unlock|frame|fps|console"),
        ("reviews", r"review|score|metacritic")]


def category(text: str) -> str:
    t = text.lower()
    for name, rx in CATS:
        if re.search(rx, t):
            return name
    return "other"


def near(rows: list[tuple[float, dict]], hours: float, lo: float, hi: float) -> dict | None:
    c = [(abs(a - hours), d) for a, d in rows if lo <= a <= hi]
    return min(c, key=lambda x: x[0])[1] if c else None


def med(xs):
    xs = [x for x in xs if isinstance(x, (int, float))]
    return round(st.median(xs), 1) if xs else None


def collect(db: str) -> list[dict]:
    c = sqlite3.connect(db)
    c.row_factory = sqlite3.Row
    scripts = json.loads((ROOT / "config" / "gta_scripts.json").read_text()) if (ROOT / "config" / "gta_scripts.json").exists() else {}
    shots = json.loads((ROOT / "assets" / "official" / "shots.json").read_text())
    shots = shots.get("shots", shots)
    out = []
    for u in c.execute("SELECT u.job_id, u.video_id, u.publish_at, u.status, j.topic_id, j.created_at, t.title "
                       "FROM uploads u JOIN jobs j ON j.id=u.job_id LEFT JOIN topics t ON t.id=j.topic_id "
                       "WHERE u.job_id LIKE 'gta%' AND u.video_id IS NOT NULL AND u.status IN ('live','scheduled','published')"):
        job, vid = u["job_id"], u["video_id"]
        yt = [(r["age_hours"], json.loads(r["data"])) for r in c.execute(
            "SELECT age_hours, data FROM metrics WHERE video_id=? ORDER BY age_hours", (vid,))]
        ig = [(r["age_hours"], json.loads(r["data"])) for r in c.execute(
            "SELECT age_hours, data FROM ig_metrics WHERE job_id=? ORDER BY age_hours", (job,))]
        f = c.execute("SELECT data FROM features WHERE job_id=?", (job,)).fetchone()
        feats = json.loads(f["data"]) if f else {}
        sc = scripts.get(u["topic_id"]) or {}
        first_shot = ""
        if sc:
            ref = (sc.get("images") or {}).get((sc.get("scenes") or [{}])[0].get("image"), "")
            first_shot = (shots.get(ref.split(":", 1)[-1]) or {}).get("shows", ref)
        title = sc.get("title") or u["title"] or job
        # YouTube: the Data API's live counts (minutes old) beat the Analytics API (1-2 days late) for views
        import datetime as _dt
        pub = _dt.datetime.fromisoformat((u["publish_at"] or "1970-01-01T00:00:00Z").replace("Z", "+00:00")).timestamp()
        try:
            live = [((r["at"] - pub) / 3600, {"views": r["views"]}) for r in c.execute(
                "SELECT at, views FROM yt_live WHERE video_id=? ORDER BY at", (vid,))]
        except sqlite3.OperationalError:
            live = []
        now_live = json.loads((c.execute("SELECT value FROM settings WHERE key='yt_live_json'").fetchone() or ["{}"])[0]).get(vid, {})
        y24 = near(live, 24, 16, 40) or near(yt, 24, 16, 40)
        yl = (yt[-1][1] if yt else {}) | ({"views": now_live["views"]} if now_live.get("views") is not None else {})
        i24, il = near(ig, 24, 16, 40), (ig[-1][1] if ig else None)
        out.append({
            "job": job, "video": vid, "title": title, "publish_at": u["publish_at"],
            "slot_utc": (u["publish_at"] or "")[11:16], "category": category(title + " " + (feats.get("hook_text") or "")),
            "logo": (u["publish_at"] or "") >= LOGO_FROM, "story": float(u["created_at"] or 0) >= STORY_FROM,
            "seconds": feats.get("seconds"), "hook": feats.get("hook_text") or "",
            "cover_lines": (sc.get("cover") or {}).get("lines"), "first_shot": first_shot[:80],
            "character_first": bool(re.search(r"lucia|jason|man|woman", first_shot, re.I)),
            "experiment": sc.get("experiment"),
            "yt_age_h": round(yt[-1][0], 1) if yt else None,
            "yt_views_24h": (y24 or {}).get("views"), "yt_views": (yl or {}).get("views"),
            "yt_pct_viewed": (yl or {}).get("averageViewPercentage"), "yt_subs": (yl or {}).get("subscribersGained"),
            "ig_age_h": round(ig[-1][0], 1) if ig else None,
            "ig_views_24h": (i24 or {}).get("views"), "ig_views": (il or {}).get("views"),
            "ig_watch_s": round(((il or {}).get("ig_reels_avg_watch_time") or 0) / 1000, 1) or None,
            "ig_skip": (il or {}).get("reels_skip_rate"), "ig_shares": (il or {}).get("shares"),
            "ig_saves": (il or {}).get("saved"), "ig_reach": (il or {}).get("reach"),
        })
    acct = {}
    for svc in ("youtube", "instagram"):
        rows = c.execute("SELECT data, at FROM resources WHERE service=? ORDER BY at", (svc,)).fetchall()
        if rows:
            first, last = json.loads(rows[0]["data"]), json.loads(rows[-1]["data"])
            k = "subscribers" if svc == "youtube" else "followers"
            acct[svc] = {"now": last.get(k), "first_seen": first.get(k),
                         "views_total": last.get("views"), "at": time.strftime("%d %b %H:%M", time.gmtime(rows[-1]["at"]))}
    return out, acct


def groups(vs: list[dict], key, label: str) -> list[str]:
    g: dict = {}
    for v in vs:
        g.setdefault(key(v), []).append(v)
    lines = [f"**{label}** (median per video: IG views 24h / YT views 24h / IG avg watch s / n)"]
    for k, items in sorted(g.items(), key=lambda kv: -(med([x["ig_views_24h"] for x in kv[1]]) or 0)):
        lines.append(f"- {k}: {med([x['ig_views_24h'] for x in items])} / {med([x['yt_views_24h'] for x in items])} / "
                     f"{med([x['ig_watch_s'] for x in items])} / n={len(items)}")
    return lines


def render(vs: list[dict], acct: dict) -> str:
    now = time.strftime("%Y-%m-%d %H:%M UTC", time.gmtime())
    vs = sorted(vs, key=lambda v: (v["publish_at"] or ""))
    L = [START, f"_Numbers updated {now} by scripts/gta_learn.py (GTA videos only; no API cost)._", ""]
    if acct:
        L.append("**Accounts:** " + "; ".join(f"{k} {v['now']} (first seen {v['first_seen']})" for k, v in acct.items()))
        L.append("")
    L += ["| published (UTC) | video | cat | logo | s | IG 24h | IG now | IG watch s | IG skip % | IG shares | YT 24h | YT now | YT % viewed | exp |",
          "|---|---|---|---|---|---|---|---|---|---|---|---|---|---|"]
    for v in vs:
        L.append(f"| {(v['publish_at'] or '')[5:16]} | {v['title'][:48]} | {v['category']} | {'Y' if v['logo'] else '-'} | "
                 f"{v['seconds'] or '-'} | {v['ig_views_24h'] or '-'} | {v['ig_views'] or '-'} | {v['ig_watch_s'] or '-'} | "
                 f"{v['ig_skip'] or '-'} | {v['ig_shares'] or '-'} | {v['yt_views_24h'] or '-'} | {v['yt_views'] or '-'} | "
                 f"{v['yt_pct_viewed'] or '-'} | {v['experiment'] or ''} |")
    done = [v for v in vs if v["ig_views_24h"] is not None or v["yt_views_24h"] is not None]
    L += ["", f"Videos with 24 h numbers: {len(done)} of {len(vs)}.", ""]
    if done:
        L += groups(done, lambda v: v["category"], "By topic type") + [""]
        L += groups(done, lambda v: "logo" if v["logo"] else "no logo", "Logo on cover/first screen") + [""]
        L += groups(done, lambda v: v["slot_utc"], "By slot (UTC)") + [""]
        L += groups(done, lambda v: ("<45 s" if (v["seconds"] or 0) < 45 else "45-55 s" if (v["seconds"] or 0) <= 55 else ">55 s"),
                    "By length") + [""]
        L += groups(done, lambda v: "story format" if v["story"] else "old format", "Format") + [""]
        top = sorted(done, key=lambda v: -(v["ig_views_24h"] or 0))
        L.append("**Top 3 (IG 24h):** " + " | ".join(f"{v['title'][:40]} ({v['ig_views_24h']}; hook: \"{v['hook'][:70]}\")" for v in top[:3]))
        L.append("")
        L.append("**Bottom 3 (IG 24h):** " + " | ".join(f"{v['title'][:40]} ({v['ig_views_24h']}; hook: \"{v['hook'][:70]}\")" for v in top[-3:]))
    L.append(END)
    return "\n".join(L)


def main(db: str) -> None:
    vs, acct = collect(db)
    (ROOT / "data").mkdir(exist_ok=True)
    (ROOT / "data" / "gta_perf.json").write_text(json.dumps({"videos": vs, "accounts": acct}, indent=1, ensure_ascii=False))
    block = render(vs, acct)
    doc = DOC.read_text() if DOC.exists() else ""
    if START in doc and END in doc:
        doc = doc[:doc.index(START)] + block + doc[doc.index(END) + len(END):]
    else:
        doc = doc + "\n\n## Numbers\n\n" + block + "\n"
    DOC.write_text(doc)
    print(block)


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "/tmp/live.db")
