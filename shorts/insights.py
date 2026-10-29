"""Per-video post-mortems and the living learnings file (added 28 Oct 2026).

Every published video is analysed twice: at 48 h (early signal) and at 7 days (the comparison age used by
the weekly report). Each analysis combines:
- the video's own numbers (views, engaged views, % viewed, watch time, likes, comments, shares, subscribers);
- the channel's median at the same age (so a video is judged against our own channel, not the internet);
- the retention curve mapped onto the script's beats (where people left, where they rewatched);
- the script, title, hook and production features.
Claude turns that into a short verdict and lessons. Numbers come only from the data; with few videos every
lesson is marked as a hypothesis. Lessons feed the next scripts and topic choices through `learn.weekly`.
Everything is kept in the `video_reviews` table and rendered to data/LEARNINGS.md (state branch) and the
dashboard.
"""
from __future__ import annotations

import json
import statistics
import time

from . import notify

AGES = {"48h": 48, "7d": 168}
PROMPT = """TASK: postmortem
You analyse one YouTube Short from the channel "Secret Smart Stuff" (English explainers about the hidden
design of everyday things). Use ONLY the data below; never invent numbers. Shorts results are noisy and depend
heavily on the topic, so with fewer than 10 videos every lesson is a "hypothesis".
Video ({tag} after going public): {video}
Channel medians at the same age (n={n}): {medians}
Retention: fraction of viewers still watching at each point (1.0 = everyone; above 1 = rewatching), mapped to
the beat that was on screen: {retention}
Script beats (start second, words): {beats}
Production features: {features}
If the features list "learnings_applied" (lessons carried over from earlier videos), say in what_worked or
what_didnt whether applying them seems to have helped, and turn a lesson that worked again into "pattern".
If the video also has "instagram_reel" numbers, compare the two platforms briefly in the summary or lessons
(same video, so a big gap points to the platform/audience, not the content).
Return JSON: {{"verdict": "above"|"at"|"below" (vs the channel median),
 "summary": "one sentence a busy owner can read",
 "what_worked": [str], "what_didnt": [str],
 "drop_points": [{{"beat": str, "second": number, "why": "likely reason, tied to what was on screen"}}],
 "lessons": [{{"area": "topic"|"hook"|"story"|"pacing"|"visuals"|"captions"|"title"|"length"|"loop",
              "lesson": "one actionable line for the next videos", "confidence": "hypothesis"|"pattern"}}],
 "topic_signal": "double_down"|"keep"|"drop"|"unclear"}}"""


def _ensure(state) -> None:
    with state.tx() as db:
        db.execute("CREATE TABLE IF NOT EXISTS video_reviews (video_id TEXT NOT NULL, tag TEXT NOT NULL, "
                   "job_id TEXT, data TEXT NOT NULL, at REAL NOT NULL, PRIMARY KEY (video_id, tag))")


def _snapshot_near(state, vid: str, hours: float) -> dict | None:
    rows = state.db.execute("SELECT age_hours, data FROM metrics WHERE video_id=? AND age_hours >= ? "
                            "ORDER BY age_hours ASC LIMIT 1", (vid, hours)).fetchall()
    return json.loads(rows[0]["data"]) | {"age_hours": round(rows[0]["age_hours"], 1)} if rows else None


def _medians(state, hours: float, exclude: str) -> tuple[dict, int]:
    vids = [r["video_id"] for r in state.db.execute("SELECT video_id FROM uploads WHERE video_id IS NOT NULL")]
    snaps = [s for v in vids if v != exclude and (s := _snapshot_near(state, v, hours))]
    keys = ["views", "engagedViews", "averageViewPercentage", "averageViewDuration", "likes", "comments", "shares",
            "subscribersGained"]
    med = {k: statistics.median([s.get(k) or 0 for s in snaps]) for k in keys} if snaps else {}
    return med, len(snaps)


def _beats(state, job_id: str) -> list[dict]:
    f = state.db.execute("SELECT data FROM features WHERE job_id=?", (job_id,)).fetchone()
    feats = json.loads(f["data"]) if f else {}
    if isinstance(feats.get("beats"), list) and feats["beats"]:   # older rows store only the beat COUNT
        return feats["beats"]
    job = state.get_job(job_id) or {}
    script = ((job.get("artifacts") or {}).get("review") or {}).get("script") or {}
    out, t = [], 0.0
    for sc in script.get("scenes") or []:          # no stored timings (older videos): estimate at 2.6 words/s
        out.append({"id": sc.get("id"), "start": round(t, 1), "words": sc.get("narration", "")})
        t += len(sc.get("narration", "").split()) / 2.6
    return out


def _retention(state, vid: str, beats: list[dict], seconds: float | None) -> list[dict]:
    row = state.db.execute("SELECT data FROM video_detail WHERE video_id=? AND kind='retention'", (vid,)).fetchone()
    if not row:
        return []
    pts = json.loads(row["data"])
    out = []
    for p in pts[::5]:                               # 100 points -> every 5 %
        r = float(p.get("elapsedVideoTimeRatio", 0))
        sec = r * seconds if seconds else None
        beat = None
        if sec is not None:
            for b in beats:
                if b["start"] <= sec:
                    beat = b["id"]
        out.append({"at": round(r, 2), "second": round(sec, 1) if sec is not None else None, "beat": beat,
                    "watching": round(float(p.get("audienceWatchRatio", 0)), 3)})
    return out


def postmortems(p) -> dict:
    """Analyse every public video that has reached 48 h / 7 d and has no analysis for that age yet."""
    state = p.state
    _ensure(state)
    done = []
    rows = state.db.execute("SELECT u.job_id, u.video_id, u.url FROM uploads u WHERE u.status='live'").fetchall()
    for r in rows:
        vid, job = r["video_id"], r["job_id"]
        for tag, hours in AGES.items():
            if state.db.execute("SELECT 1 FROM video_reviews WHERE video_id=? AND tag=?", (vid, tag)).fetchone():
                continue
            snap = _snapshot_near(state, vid, hours)
            if not snap:
                continue
            f = state.db.execute("SELECT data FROM features WHERE job_id=?", (job,)).fetchone()
            feats = json.loads(f["data"]) if f else {}
            beats = _beats(state, job)
            secs = feats.get("seconds") or (beats[-1]["start"] + 3 if beats else None)
            med, n = _medians(state, hours, vid)
            topic = state.db.execute("SELECT t.title, t.pillar FROM jobs j JOIN topics t ON t.id=j.topic_id "
                                     "WHERE j.id=?", (job,)).fetchone()
            video = {"title": (topic["title"] if topic else job), "pillar": topic["pillar"] if topic else None,
                     "url": r["url"], **snap}
            from .publish.instagram import near as ig_near
            igm = ig_near(state, job, hours)
            if igm:
                video["instagram_reel"] = igm     # same video as an Instagram Reel, same age
            res = p._llm(PROMPT.format(tag=tag, video=json.dumps(video), medians=json.dumps(med), n=n,
                                       retention=json.dumps(_retention(state, vid, beats, secs)),
                                       beats=json.dumps(beats)[:4000],
                                       features=json.dumps({k: v for k, v in feats.items() if k != "beats"})[:2000]),
                         job, f"postmortem_{tag}", est=0.03,
                         model=p.cfg.pipeline["providers"]["llm"]["model_script"], max_tokens=2000)
            data = (res.data or {}) | {"metrics": snap, "medians": med, "n_compared": n}
            with state.tx() as db:
                db.execute("INSERT OR REPLACE INTO video_reviews(video_id, tag, job_id, data, at) VALUES (?,?,?,?,?)",
                           (vid, tag, job, json.dumps(data, ensure_ascii=False), time.time()))
            done.append((vid, tag))
            v = snap.get("views", 0)
            les = (data.get("lessons") or [{}])[0].get("lesson", "")
            notify.send(state, f"📊 {tag} check: {notify.esc(video['title'])}\n"
                               f"{v} views (channel median {med.get('views', '-')}, n={n}) · "
                               f"{snap.get('averageViewPercentage', '-')}% viewed · {snap.get('likes', 0)} likes · "
                               f"{snap.get('shares', 0)} shares"
                               + (f"\nInstagram: {igm.get('views', '-')} views · {igm.get('likes', 0)} likes · "
                                  f"{igm.get('shares', 0)} shares · {igm.get('saved', 0)} saves" if igm else "")
                               + f"\n{notify.esc(data.get('summary', ''))}"
                               + (f"\nLesson: {notify.esc(les)}" if les else ""), silent=True)
    write_learnings(p)
    return {"analysed": done}


def write_learnings(p) -> str:
    """Render the living learnings file from the database (state branch: data/LEARNINGS.md)."""
    state = p.state
    _ensure(state)
    lines = ["# Secret Smart Stuff — learnings (auto-updated)", "",
             f"Updated {time.strftime('%Y-%m-%d %H:%M UTC', time.gmtime())}. Built from every published video's 48 h "
             "and 7 day analysis, the weekly report and owner feedback. With fewer than 10 videos, lessons are "
             "hypotheses.", ""]
    rules = state.get_setting("lessons_for_writer")
    guide = state.get_setting("topic_guidance")
    lines += ["## Rules the writer follows now", rules or "- (none yet)", "", "## Topic guidance now", guide or "- (none yet)", ""]
    lines += ["## Per-video analyses", ""]
    for r in state.db.execute("SELECT video_id, tag, job_id, data, at FROM video_reviews ORDER BY at DESC"):
        d = json.loads(r["data"])
        m = d.get("metrics") or {}
        lines.append(f"### {r['job_id']} ({r['tag']}) — {d.get('verdict', '?')} median")
        lines.append(f"- {m.get('views', '?')} views · {m.get('averageViewPercentage', '?')}% viewed · "
                     f"{m.get('likes', 0)} likes · {m.get('shares', 0)} shares · {m.get('subscribersGained', 0)} subs "
                     f"(median views {d.get('medians', {}).get('views', '-')}, n={d.get('n_compared', 0)})")
        lines.append(f"- {d.get('summary', '')}")
        for x in d.get("what_worked") or []:
            lines.append(f"  - ✅ {x}")
        for x in d.get("what_didnt") or []:
            lines.append(f"  - ❌ {x}")
        for x in d.get("drop_points") or []:
            lines.append(f"  - 📉 {x.get('beat')} @ {x.get('second')} s: {x.get('why')}")
        for x in d.get("lessons") or []:
            lines.append(f"  - 💡 [{x.get('area')}, {x.get('confidence')}] {x.get('lesson')}")
        lines.append("")
    md = "\n".join(lines)
    state.set_setting("learnings_live_md", md)
    out = p.cfg.root / "data" / "LEARNINGS.md"
    out.parent.mkdir(exist_ok=True)
    out.write_text(md, encoding="utf-8")
    return md


def recent_lessons(state, limit: int = 12) -> list[dict]:
    _ensure(state)
    out = []
    for r in state.db.execute("SELECT job_id, tag, data FROM video_reviews ORDER BY at DESC LIMIT 20"):
        d = json.loads(r["data"])
        for x in d.get("lessons") or []:
            out.append({"video": r["job_id"], "age": r["tag"], "verdict": d.get("verdict"), **x,
                        "topic_signal": d.get("topic_signal")})
    return out[:limit]
