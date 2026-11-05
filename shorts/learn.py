"""Weekly learning report: statistics computed in code, explained by Claude, never invented.

Rules (so the system improves without drifting):
- Videos are compared at the SAME AGE (7 days after going public); younger videos are excluded.
- Medians, not means; every group reports its n.
- A difference counts as a LESSON only if both groups have n >= MIN_N and the median ratio is
  >= MIN_RATIO (or <= 1/MIN_RATIO). Lessons only steer the writer/idea prompts; anything that would
  change the playbook is a PROPOSAL sent to the owner, not applied.
- Experiments are reported per arm against their own min_videos_per_arm.
"""
from __future__ import annotations

import json
import statistics
import time

from . import experiments as X, notify

MIN_N = 5
MIN_RATIO = 1.3
AGE_H = 7 * 24


def _at_age(state) -> dict[str, dict]:
    """video_id -> metrics snapshot closest to (and not before) 7 days old."""
    best: dict[str, tuple[float, dict]] = {}
    for r in state.db.execute("SELECT video_id, age_hours, data FROM metrics WHERE age_hours >= ?", (AGE_H,)):
        d = abs(r["age_hours"] - AGE_H)
        if r["video_id"] not in best or d < best[r["video_id"]][0]:
            best[r["video_id"]] = (d, json.loads(r["data"]))
    return {k: v[1] for k, v in best.items()}


def stats(state) -> dict:
    snaps = _at_age(state)
    rows = []
    ig7: dict[str, dict] = {}
    try:          # Instagram snapshot closest to 7 days, per job
        for r in state.db.execute("SELECT job_id, age_hours, data FROM ig_metrics WHERE age_hours >= ?", (AGE_H,)):
            d = abs(r["age_hours"] - AGE_H)
            if r["job_id"] not in ig7 or d < ig7[r["job_id"]][0]:
                ig7[r["job_id"]] = (d, json.loads(r["data"]))
    except Exception:  # noqa: BLE001
        pass
    for r in state.db.execute("SELECT u.job_id, u.video_id, t.pillar, t.title, t.notes FROM uploads u JOIN jobs j "
                              "ON j.id=u.job_id JOIN topics t ON t.id=j.topic_id WHERE u.video_id IS NOT NULL"):
        if r["video_id"] not in snaps:
            continue
        try:
            batch = (json.loads(r["notes"] or "{}") or {}).get("batch")
        except Exception:  # noqa: BLE001
            batch = None
        f = state.db.execute("SELECT data FROM features WHERE job_id=?", (r["job_id"],)).fetchone()
        feats = json.loads(f["data"]) if f else {}
        arms = {a["experiment_id"]: a["arm"] for a in state.db.execute(
            "SELECT experiment_id, arm FROM assignments WHERE job_id=?", (r["job_id"],))}
        rows.append({"video": r["video_id"], "title": r["title"], "pillar": r["pillar"], **feats,
                     "batch": batch or "before-5-nov", "arms": arms, "m": snaps[r["video_id"]],
                     "ig": (ig7.get(r["job_id"]) or (0, {}))[1]})
    out: dict = {"videos_at_7d": len(rows), "groups": {}, "lessons": [], "experiments": []}
    if not rows:
        return out
    overall = statistics.median(x["m"].get("views", 0) for x in rows)
    out["median_views_7d"] = overall

    def group(name, key):
        g: dict = {}
        for x in rows:
            k = key(x)
            if k is None:
                continue
            g.setdefault(str(k), []).append(x)
        res = {}
        for k, xs in g.items():
            res[k] = {"n": len(xs),
                      "median_views": statistics.median(x["m"].get("views", 0) for x in xs),
                      "median_pct_viewed": statistics.median(x["m"].get("averageViewPercentage", 0) or 0 for x in xs),
                      "subs_per_1k": round(1000 * sum(x["m"].get("subscribersGained", 0) for x in xs)
                                           / max(1, sum(x["m"].get("views", 0) for x in xs)), 2),
                      # engaged views / views: the API's closest stand-in for Studio's "viewed vs swiped away"
                      "median_kept_pct": statistics.median(round(100 * (x["m"].get("engagedViews") or 0)
                                                                 / max(1, x["m"].get("views") or 0), 1) for x in xs),
                      "shares_per_1k": round(1000 * sum(x["m"].get("shares", 0) or 0 for x in xs)
                                             / max(1, sum(x["m"].get("views", 0) for x in xs)), 2),
                      "ig_median_views": statistics.median((x["ig"].get("views") or 0) for x in xs),
                      "ig_sends_per_1k_reach": round(1000 * sum(x["ig"].get("shares", 0) or 0 for x in xs)
                                                     / max(1, sum(x["ig"].get("reach", 0) or 0 for x in xs)), 2),
                      "ig_median_skip_rate": (statistics.median([x["ig"]["reels_skip_rate"] for x in xs
                                                                 if x["ig"].get("reels_skip_rate") is not None])
                                              if any(x["ig"].get("reels_skip_rate") is not None for x in xs) else None)}
        out["groups"][name] = res
        ok = {k: v for k, v in res.items() if v["n"] >= MIN_N}
        if len(ok) >= 2:
            hi = max(ok, key=lambda k: ok[k]["median_views"])
            lo = min(ok, key=lambda k: ok[k]["median_views"])
            if ok[lo]["median_views"] and ok[hi]["median_views"] / ok[lo]["median_views"] >= MIN_RATIO:
                out["lessons"].append({"dimension": name, "better": hi, "worse": lo,
                                       "ratio": round(ok[hi]["median_views"] / ok[lo]["median_views"], 2),
                                       "n": [ok[hi]["n"], ok[lo]["n"]]})

    group("batch", lambda x: x.get("batch"))          # e.g. the 5 Nov virality batch vs everything before it
    group("pillar", lambda x: x.get("pillar"))
    group("publish_slot_utc", lambda x: x.get("publish_slot_utc"))
    group("hook_formula", lambda x: x.get("hook_formula"))
    group("length", lambda x: None if not x.get("seconds") else ("<30s" if x["seconds"] < 30 else "30-36s" if x["seconds"] < 36 else "36s+"))
    group("wit_lines", lambda x: x.get("wit_lines"))
    group("music", lambda x: x.get("music"))
    for e in X.load_experiments():
        arms = {}
        for a in e.get("arms", {}):
            xs = [x for x in rows if x["arms"].get(e["id"]) == a]
            arms[a] = {"n": len(xs), "median_views": statistics.median(x["m"].get("views", 0) for x in xs) if xs else None}
        ready = all(v["n"] >= e.get("min_videos_per_arm", MIN_N) for v in arms.values())
        out["experiments"].append({"id": e["id"], "status": e.get("status"), "arms": arms, "ready_to_conclude": ready})
    out["costs"] = {"median_cost": statistics.median([x.get("cost_usd") or 0 for x in rows])}
    return out


REPORT = """TASK: learnings
You are the analyst for a YouTube Shorts channel. Write the weekly learning report in plain, simple
English with short bullet points. Use ONLY the numbers in the JSON below; never invent numbers or
causes. Always state n. Say "not enough data yet" whenever a group has n < {min_n}. Remember Shorts
results are noisy and topic-driven: correlation, not proof.
Track growth, not only reach: for each group report subs_per_1k (YouTube), median_kept_pct (engaged views / views,
the swipe-away stand-in), shares_per_1k, and on Instagram ig_sends_per_1k_reach and ig_median_skip_rate when present.
A group with many views but ~0 subs_per_1k is NOT a winner. Compare the "batch" groups first.
Sections (markdown, ## headings): What worked · What didn't · Hooks and openings · Visuals, length,
music, wit · Costs · Experiments (progress per arm; if ready_to_conclude, say which arm leads and by how
much) · Owner feedback themes · Next: repeat / change / stop / test.
Then a final section "## Proposals for the owner" listing at most 3 concrete changes to the production
playbook that the evidence supports (or "None yet").
Also return, after the markdown:
- a line "LESSONS_FOR_WRITER:" followed by at most 5 one-line lessons for the next scripts (hooks, story,
  pacing, visuals, captions, titles). Use the statistical "lessons" list first; then the per-video analyses
  when two or more videos point the same way. Mark each line "(pattern, n=..)" or "(hypothesis)". Never
  contradict docs/PLAYBOOK.md rules (question hook, loop, sourced facts, simple pictures) — refine within them.
- a line "TOPIC_GUIDANCE:" followed by at most 4 lines: which kinds of objects/pillars to double down on,
  keep, or drop, each with its evidence (n, views vs median).
Data: {data}
Per-video analyses (latest first): {analyses}
Owner feedback (latest): {feedback}"""


def weekly(p) -> dict:
    st = stats(p.state)
    fb = [dict(r) for r in p.state.db.execute(
        "SELECT decision, note FROM feedback WHERE note != '' ORDER BY at DESC LIMIT 15")]
    from . import insights
    analyses = insights.recent_lessons(p.state)
    if st["videos_at_7d"] == 0 and not analyses:
        md = ("# Learnings\n\nNo video is old enough to analyse yet. "
              "The first analysis comes 48 hours after the first video goes public.\n")
        p.state.set_setting("learnings_md", md)
        return {"videos": 0}
    r = p._llm(REPORT.format(min_n=MIN_N, data=json.dumps(st)[:12000], feedback=json.dumps(fb)[:3000],
                             analyses=json.dumps(analyses, ensure_ascii=False)[:6000]),
               None, "learnings", est=0.05, model=p.cfg.pipeline["providers"]["llm"]["model_script"],
               max_tokens=3000, json_out=False)
    text = r.text or ""
    md, _, rest = text.partition("LESSONS_FOR_WRITER:")
    lessons, _, topics = rest.partition("TOPIC_GUIDANCE:")
    md = f"# Learnings ({time.strftime('%Y-%m-%d', time.gmtime())})\n\n" + md.strip()
    p.state.set_setting("learnings_md", md)
    if lessons.strip():
        p.state.set_setting("lessons_for_writer", lessons.strip()[:1500])
    if topics.strip():
        p.state.set_setting("topic_guidance", topics.strip()[:1200])
    insights.write_learnings(p)
    head = md.split("## Proposals for the owner")
    tail = head[1].strip()[:700] if len(head) > 1 else ""
    notify.send(p.state, f"📈 Weekly learnings are on the dashboard ({st['videos_at_7d']} videos at 7 days)."
                         + (f"\n\nProposals:\n{tail}" if tail and "None" not in tail[:20] else ""))
    return {"videos": st["videos_at_7d"], "lessons": len(st["lessons"]), "analyses": len(analyses)}
