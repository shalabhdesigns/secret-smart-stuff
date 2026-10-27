"""Stage 9: learn from real viewers.

Reads what the analytics job already stores (per-video metric snapshots by age, and the retention curve
`audienceWatchRatio` by `elapsedVideoTimeRatio`), maps the retention curve onto each episode's beats
(hook / base / escalation / turn / punch / button), and writes `creative/performance.json`:

- per episode: premise, structure, judge scores, metrics at ~48 h and ~7 d, where viewers left, where they rewatched;
- channel medians, and how well the script judge's score predicted real results (only once n >= 10).

The writer reads a short summary of this file every episode (writer._history_brief), so real audience behaviour,
not only model opinion, steers future scripts. Nothing here claims causation: one channel, small samples.
"""
from __future__ import annotations

import json
import statistics
from pathlib import Path

from . import episodes as E

ROOT = Path(__file__).resolve().parents[2]
PERF = ROOT / "creative" / "performance.json"


def _metric_at(state, video_id: str, hours: float) -> dict | None:
    rows = state.db.execute("SELECT age_hours, data FROM metrics WHERE video_id=? ORDER BY age_hours",
                            (video_id,)).fetchall()
    best = None
    for r in rows:
        if r["age_hours"] >= hours:
            best = json.loads(r["data"])
            best["_age_h"] = round(r["age_hours"], 1)
            break
    return best


def _retention(state, video_id: str) -> list[dict]:
    try:
        r = state.db.execute("SELECT data FROM video_detail WHERE video_id=? AND kind='retention'", (video_id,)).fetchone()
    except Exception:  # noqa: BLE001  (table appears after the first analytics run)
        return []
    return json.loads(r["data"]) if r else []


def beat_map(curve: list[dict], timeline: dict) -> dict:
    """Retention by beat. curve: [{elapsedVideoTimeRatio, audienceWatchRatio}], timeline: {starts, durs, beats}."""
    if not curve or not timeline or not timeline.get("starts"):
        return {}
    total = sum(timeline["durs"]) or 1.0
    pts = sorted((float(c["elapsedVideoTimeRatio"]), float(c["audienceWatchRatio"])) for c in curve)

    def at(t: float) -> float:
        x = t / total
        prev = pts[0]
        for p in pts:
            if p[0] >= x:
                if p[0] == prev[0]:
                    return p[1]
                k = (x - prev[0]) / (p[0] - prev[0])
                return prev[1] + k * (p[1] - prev[1])
            prev = p
        return pts[-1][1]

    out = []
    for i, (s, d) in enumerate(zip(timeline["starts"], timeline["durs"])):
        a, b = at(s), at(s + d)
        out.append({"shot": i, "beat": (timeline.get("beats") or [""] * len(timeline["starts"]))[i],
                    "start": round(s, 2), "in": round(a, 3), "out": round(b, 3), "change": round(b - a, 3)})
    drops = sorted(out, key=lambda r: r["change"])[:2]
    rises = [r for r in out if r["change"] > 0.01]          # >0: people rewatched this part (or looped back)
    return {"shots": out, "worst": drops, "rewatched": rises,
            "start": round(at(0.0), 3), "end": round(at(total - 0.05), 3)}


def update(p) -> dict:
    """Refresh creative/performance.json from stored analytics. Safe to run any time."""
    st = p.state
    E.init(st)
    rows = st.db.execute("SELECT job_id, video_id FROM uploads WHERE video_id IS NOT NULL").fetchall()
    vid_of = {r["job_id"]: r["video_id"] for r in rows}
    eps = []
    for ep in E.all_eps(st, ("scheduled", "published")):
        vid = ep.get("yt_video_id") or vid_of.get(ep["id"])
        if not vid:
            continue
        qa = ep.get("qa") or {}
        rec = {"id": ep["id"], "number": ep["number"], "title": ep.get("title"), "premise": ep.get("premise"),
               "structure": (ep.get("plan") or {}).get("structure"), "game": (ep.get("plan") or {}).get("game"),
               "scores": (ep.get("plan") or {}).get("scorecard"), "m48": _metric_at(st, vid, 48),
               "m7d": _metric_at(st, vid, 7 * 24), "retention": beat_map(_retention(st, vid), qa.get("timeline") or {})}
        eps.append(rec)

    def med(key: str, when: str = "m7d"):
        vals = [float(e[when][key]) for e in eps if e.get(when) and e[when].get(key) is not None]
        return round(statistics.median(vals), 2) if vals else None

    summary = {"episodes_measured": sum(1 for e in eps if e.get("m7d")),
               "median_7d": {k: med(k) for k in ("views", "engagedViews", "averageViewPercentage", "shares", "likes")}}
    # does the judge predict reality? (Spearman rank correlation, only with enough data)
    pairs = [((e.get("scores") or {}).get("total"), (e.get("m7d") or {}).get("engagedViews") or (e.get("m7d") or {}).get("views"))
             for e in eps]
    pairs = [(a, b) for a, b in pairs if a is not None and b is not None]
    if len(pairs) >= 10:
        def ranks(v):
            order = sorted(range(len(v)), key=lambda i: v[i])
            r = [0.0] * len(v)
            for k, i in enumerate(order):
                r[i] = float(k)
            return r
        ra, rb = ranks([a for a, _ in pairs]), ranks([b for _, b in pairs])
        n = len(pairs)
        d2 = sum((x - y) ** 2 for x, y in zip(ra, rb))
        summary["judge_vs_reality_spearman"] = round(1 - 6 * d2 / (n * (n * n - 1)), 2)
        summary["judge_vs_reality_n"] = n
    else:
        summary["judge_vs_reality_spearman"] = None
        summary["note"] = f"need 10 measured episodes to check the judge (have {len(pairs)})"
    data = {"summary": summary, "episodes": eps}
    PERF.write_text(json.dumps(data, ensure_ascii=False, indent=1))
    return summary


def brief(max_eps: int = 8) -> str:
    """What the writer is told about real audience behaviour (short, factual, no over-claiming)."""
    if not PERF.exists():
        return "AUDIENCE DATA: none yet (no episode has been public for 7 days)."
    d = json.loads(PERF.read_text())
    eps = [e for e in d.get("episodes", []) if e.get("m7d")]
    if not eps:
        return "AUDIENCE DATA: none yet (no episode has been public for 7 days)."
    key = "engagedViews" if any((e["m7d"] or {}).get("engagedViews") for e in eps) else "views"
    eps.sort(key=lambda e: -float(e["m7d"].get(key) or 0))
    lines = [f"AUDIENCE DATA (7-day {key}; one channel, small numbers - treat as hints, not laws):"]
    for e in eps[:max_eps]:
        r = e.get("retention") or {}
        worst = ", ".join(f"{w['beat'] or 'shot ' + str(w['shot'])} ({w['change']:+.0%})" for w in r.get("worst", []))
        lines.append(f"- Ep {e['number']} '{e.get('title')}': {key} {e['m7d'].get(key)}, avg viewed "
                     f"{e['m7d'].get('averageViewPercentage')}%, shares {e['m7d'].get('shares')}; "
                     f"structure {e.get('structure')}; viewers left most at: {worst or 'n/a'}")
    s = d.get("summary", {})
    if s.get("judge_vs_reality_spearman") is not None:
        lines.append(f"Judge score vs real results: Spearman {s['judge_vs_reality_spearman']} (n={s['judge_vs_reality_n']}).")
    return "\n".join(lines)
