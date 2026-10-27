#!/usr/bin/env python3
"""Execute one request (see .github/workflows/command.yml and produce.yml).

The request comes from: the daily schedule, the owner's Telegram (via the Cloudflare Worker),
or Claude (commands/request.json). Every outcome is reported to Telegram when configured, and
to a GitHub issue as a fallback, so nothing fails silently.

Actions
  produce      make (or resume) one Short; topic/angle/question/fresh/reset/skip are optional
  approve      upload as private + schedule (publish time from the active experiment, or publish_at)
  fix          apply the owner's note with minimal edits, reuse unchanged media, send the new version
  reject       drop the topic, keep the reason as feedback
  rerender     rebuild render/qa/package from saved media (no generation cost)
  verify       check uploads went public on time
  status       send a short status message
  revenue      record revenue entered by the owner (period YYYY-MM[-DD], usd, optional video_id)
  dashboard    rebuild the dashboard and upload it to the Worker's storage
  setup_studio deploy the Cloudflare Worker and connect the Telegram bot
  build_audio  one-time: generate the music and sound-effect library
"""
from __future__ import annotations

import json
import os
import re
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from shorts import experiments as X, notify  # noqa: E402
from shorts.config import load                # noqa: E402
from shorts.pipeline import Pipeline          # noqa: E402

JOB_RE = re.compile(r"[a-z0-9-]{3,80}")


def gh(*args: str, check: bool = True) -> str:
    if os.environ.get("SHORTS_NO_GITHUB") == "1":      # offline tests
        return ""
    return subprocess.run(["gh", *args], capture_output=True, text=True, check=check).stdout.strip()


def issue_for(job: str, label: str = "review") -> str | None:
    out = gh("issue", "list", "--label", label, "--state", "open", "--limit", "100",
             "--json", "number,body", "-q",
             f'.[] | select(.body | contains("<!-- job:{job} -->")) | .number', check=False)
    return out.splitlines()[0] if out else None


def alert(p: Pipeline, title: str, body: str) -> None:
    notify.send(p.state, f"⚠️ {title}\n{body[:900]}")
    gh("label", "create", "alert", "--color", "B60205", check=False)
    gh("issue", "create", "--label", "alert", "--title", title[:120], "--body", body[:60000], check=False)


def comment(job: str, text: str, close: bool = False) -> None:
    n = issue_for(job)
    if n:
        gh("issue", "comment", n, "--body", text, check=False)
        if close:
            gh("issue", "close", n, check=False)


def fetch_bundle(job: str, into: Path) -> bool:
    into.mkdir(parents=True, exist_ok=True)
    if os.environ.get("SHORTS_NO_GITHUB") == "1":      # offline tests: use a local copy if present
        local = ROOT / "build" / job / "media.tgz"
        if local.exists() and local.parent != into:
            subprocess.run(["tar", "-xzf", str(local), "-C", str(into)], check=True)
        return local.exists()
    r = subprocess.run(["gh", "release", "download", f"review-{job}", "-D", str(into), "--clobber"],
                       capture_output=True, text=True)
    if (into / "media.tgz").exists():
        subprocess.run(["tar", "-xzf", str(into / "media.tgz"), "-C", str(into)], check=True)
    return r.returncode == 0


def send_for_review(p: Pipeline, job: str) -> None:
    """Publish the review bundle (release + issue) and send the video to the owner's phone."""
    subprocess.run([str(ROOT / "scripts" / "open_review.sh"), job], check=True)
    j = p.state.get_job(job)
    d = ROOT / "build" / job
    meta = json.loads((d / "metadata.json").read_text()) if (d / "metadata.json").exists() else {}
    rv = (j["artifacts"].get("review") or {}).get("content") or {}
    vis = j["artifacts"].get("visuals") or {}
    script = json.loads((d / "script.json").read_text())
    slot = X.slot_for(p.state, job)
    when = X.next_publish_time(p.state, slot, margin_minutes=30)
    topic = p.state.get_topic(j["topic_id"])
    p.state.set_features(job, {**X.features(script, json.loads((d / "visuals.json").read_text())
                                            if (d / "visuals.json").exists() else {},
                                            j["artifacts"].get("render"), topic, p.state.job_cost(job)),
                               "publish_slot_utc": slot})
    notify.review(p.state, job, d / "final.mp4", meta.get("title") or job, rv.get("total", "?"),
                  p.state.job_cost(job), vis.get("flags") or [], f"{when} UTC (≈ {ist(when)} IST)")


def ist(iso: str) -> str:
    import datetime as dt
    t = dt.datetime.fromisoformat(iso.replace("Z", "+00:00")) + dt.timedelta(hours=5, minutes=30)
    return t.strftime("%a %d %b, %H:%M")


def report_failure(p: Pipeline, job: str) -> None:
    j = p.state.get_job(job)
    ev = p.state.db.execute("SELECT message FROM events WHERE job_id=? ORDER BY at DESC LIMIT 6", (job,)).fetchall()
    alert(p, f"Pipeline problem: {job}",
          f"<!-- job:{job} -->\nstatus: {j['status']} · last finished stage: {j['stage']}\n"
          f"error: {j['error']}\n\nrecent events:\n" + "\n".join(f"- {r['message'][:300]}" for r in ev))


# ---------------- actions ----------------

def do_produce(p: Pipeline, req: dict) -> int:
    for skip in req.get("skip") or []:
        for jj in p.state.jobs():
            if jj["topic_id"] == skip:
                p.state.set_job_status(jj["id"], "rejected", "skipped on request")
        if p.state.get_topic(skip):
            p.state.set_topic_status(skip, "rejected")
    for old in req.get("retire_jobs") or []:
        # superseded versions (e.g. made in an old format): close them, keep the topic for a remake
        jj = p.state.get_job(old)
        if jj and jj["status"] in ("review", "failed", "paused", "running"):
            p.state.set_job_status(old, "rejected", "retired: superseded")
            p.state.set_topic_status(jj["topic_id"], "shortlisted")
            comment(old, "Retired: superseded by the current format.", close=True)
    pending = p.state.jobs("review")
    if pending and not req.get("topic") and not req.get("allow_parallel"):
        # one video waits for review at a time: remind instead of making another
        notify.send(p.state, f"⏳ {len(pending)} video(s) still waiting for your review "
                             f"(oldest: {pending[0]['id']}). Approve, fix or drop it to get the next one.")
        return 0
    tid = req.get("topic") or ""
    if not tid:
        if len(p.state.topics("shortlisted")) < 3:
            p.discover(8)
        t = p.next_topic()
        tid = t["id"] if t else ""
    if not tid:
        alert(p, "Pipeline problem: no topic", "Discovery returned no usable topics.")
        return 1
    if req.get("angle") and p.state.get_topic(tid):
        t = p.state.get_topic(tid)
        notes = json.loads(t.get("notes") or "{}")
        notes["angle"] = req["angle"]
        if req.get("question"):
            notes["question"] = req["question"]
        p.state.upsert_topic(tid, "", notes=json.dumps(notes), status="shortlisted")
        if req.get("question"):
            p.state.db.execute("UPDATE topics SET title=? WHERE id=?", (req["question"], tid))
            p.state.db.commit()
    if req.get("reset"):
        mine = [jj for jj in p.state.jobs() if jj["topic_id"] == tid]
        if mine:
            latest = max(mine, key=lambda jj: jj["created_at"])
            for jj in mine:
                if jj["id"] == latest["id"]:
                    p.state.db.execute("UPDATE jobs SET attempts=0, status='failed' WHERE id=?", (jj["id"],))
                elif jj["status"] in ("failed", "paused", "running"):
                    p.state.db.execute("UPDATE jobs SET status='rejected' WHERE id=?", (jj["id"],))
            p.state.db.commit()
    job = p.produce(tid, fresh=bool(req.get("fresh")))
    j = p.state.get_job(job)
    tries = 1
    while j["status"] == "rejected" and tries < 3 and not req.get("topic"):
        t = p.next_topic()          # the quality gate dropped this topic: try the next best one
        if not t:
            break
        job = p.produce(t["id"])
        j = p.state.get_job(job)
        tries += 1
    if j["status"] == "review" and not j["error"]:
        send_for_review(p, job)
        return 0
    if j["status"] == "paused":
        notify.send(p.state, f"⏸ {job} paused: daily budget reached. It finishes automatically on the next run.")
        return 0
    report_failure(p, job)
    return 1


def do_decision(p: Pipeline, req: dict) -> int:
    action, job, note = req["action"], req.get("job", ""), (req.get("note") or "").strip()
    if not JOB_RE.fullmatch(job):
        raise SystemExit("bad job id")
    j = p.state.get_job(job)
    if not j:
        notify.send(p.state, f"I can't find video {job}.")
        return 1
    up = p.state.db.execute("SELECT * FROM uploads WHERE job_id=?", (job,)).fetchone()
    if up and up["video_id"]:
        notify.send(p.state, f"ℹ️ {job} is already uploaded: {up['url']} (nothing changed).")
        return 0
    d = ROOT / "build" / job
    if action == "reject":
        p.decide(job, "reject", note)
        notify.send(p.state, "🗑 Dropped. The next video comes with the next daily run (or send /produce).")
        comment(job, f"❌ Dropped by owner. Reason: {note or 'none given'}", close=True)
        return 0
    if action == "fix":
        if not note:
            notify.send(p.state, "Please say what to change.")
            return 0
        if j["status"] not in ("review", "approved"):
            notify.send(p.state, f"{job} is '{j['status']}', so it can't be fixed now.")
            return 0
        fetch_bundle(job, d / "prior")
        for f in ("script.json", "review.json"):
            if (d / "prior" / f).exists() and not (d / f).exists():
                (d / f).write_text((d / "prior" / f).read_text())
        cost_before = p.state.job_cost(job)
        try:
            p.decide(job, "fix", note)
        except Exception as e:  # noqa: BLE001
            notify.send(p.state, f"⚠️ I couldn't apply that fix: {e}. The video is unchanged; try wording it differently.")
            p.state.set_job_status(job, "review")
            return 1
        p.produce(j["topic_id"])
        j2 = p.state.get_job(job)
        if j2["status"] == "review" and not j2["error"]:
            send_for_review(p, job)
            extra = p.state.job_cost(job) - cost_before
            notify.send(p.state, f"✏️ Fixed version above (fix cost ${extra:.2f}).", silent=True)
            return 0
        report_failure(p, job)
        return 1
    # approve
    if j["status"] not in ("review", "approved"):
        notify.send(p.state, f"{job} is '{j['status']}', so it can't be approved.")
        return 0
    fetch_bundle(job, d)
    p.decide(job, "approve")
    if not p.cfg.live:
        notify.send(p.state, "✅ Approved (dry-run mode: nothing uploaded).")
        return 0
    when = req.get("publish_at") or X.next_publish_time(p.state, X.slot_for(p.state, job))
    try:
        rec = p.publish(job, publish_at=when)
    except Exception as e:  # noqa: BLE001
        p.state.set_job_status(job, "approved", str(e))
        alert(p, f"Upload failed: {job}", f"<!-- job:{job} -->\n{e}\n\nNothing was published. Tap Approve again "
                                          "after the cause is fixed.")
        return 1
    feats = p.state.db.execute("SELECT data FROM features WHERE job_id=?", (job,)).fetchone()
    if feats:
        data = json.loads(feats["data"])
        data["publish_at"] = when
        p.state.set_features(job, data)
    notify.send(p.state, f"⬆️ Uploaded (private until {ist(when)} IST).\n{rec.get('url')}\n"
                         "I'll confirm when it is live.")
    comment(job, f"✅ Uploaded as private, scheduled for {when} UTC. {rec.get('url')}", close=True)
    return 0


def do_rerender(p: Pipeline, req: dict) -> int:
    job = req["job"]
    if not JOB_RE.fullmatch(job):
        raise SystemExit("bad job id")
    j = p.state.get_job(job)
    d = ROOT / "build" / job
    if not j or not fetch_bundle(job, d) or not (d / "visuals.json").exists():
        alert(p, f"Pipeline problem: {job}", f"<!-- job:{job} -->\nNo saved media for {job}; a new version is needed.")
        return 1
    p.state.db.execute("UPDATE jobs SET stage='visuals', status='failed', error=NULL WHERE id=?", (job,))
    p.state.db.commit()
    p.produce(j["topic_id"])
    j = p.state.get_job(job)
    if j["status"] == "review" and not j["error"]:
        send_for_review(p, job)
        return 0
    report_failure(p, job)
    return 1


def do_status(p: Pipeline) -> int:
    now = time.time()
    rev = p.state.jobs("review")
    lines = ["📋 Status"]
    lines.append(f"Waiting for your review: {', '.join(j['id'] for j in rev) or 'none'}")
    ups = p.state.db.execute("SELECT job_id, url, status, publish_at FROM uploads ORDER BY at DESC LIMIT 3").fetchall()
    for u in ups:
        lines.append(f"• {u['status']}: {u['url']} ({u['publish_at'] or ''})")
    lines.append(f"Spend last 24 h: ${p.state.spend_since(now - 86400):.2f} · 30 days: ${p.state.spend_since(now - 30 * 86400):.2f}")
    lines.append(f"Topics in backlog: {len(p.state.topics('shortlisted'))}")
    bad = p.state.db.execute("SELECT message FROM events WHERE level='error' AND at>=? ORDER BY at DESC LIMIT 2",
                             (now - 86400,)).fetchall()
    if bad:
        lines.append("Problems (24 h): " + " | ".join(r["message"][:120] for r in bad))
    url = p.state.get_setting("worker_url")
    if url:
        lines.append(f"Dashboard: {url}/dash")
    notify.send(p.state, "\n".join(lines))
    print("\n".join(lines))
    return 0


def do_revenue(p: Pipeline, req: dict) -> int:
    period, usd, vid = str(req.get("period", "")), float(req.get("usd")), str(req.get("video_id") or "")
    if not re.fullmatch(r"\d{4}-\d{2}(-\d{2})?", period) or not (0 <= usd < 1e6) or (vid and not re.fullmatch(r"[\w-]{6,20}", vid)):
        notify.send(p.state, "That revenue entry looks wrong; nothing saved.")
        return 1
    with p.state.tx() as db:
        db.execute("INSERT INTO revenue(period, video_id, usd, source, at) VALUES (?,?,?,?,?) "
                   "ON CONFLICT(period, video_id, source) DO UPDATE SET usd=excluded.usd, at=excluded.at",
                   (period, vid, usd, "owner", time.time()))
    notify.send(p.state, f"💰 Saved: ${usd:.2f} for {period}{' (' + vid + ')' if vid else ''}. Shown on the dashboard after the next refresh.")
    return 0


def do_verify(p: Pipeline) -> int:
    from shorts.publish.verify import run
    res = run(p.state)
    print(json.dumps(res, indent=1))
    return 0


def do_dashboard(p: Pipeline) -> int:
    from shorts.dashboard import build, upload
    html = build(p.state, p.cfg)
    out = ROOT / "build" / "dashboard.html"
    out.parent.mkdir(exist_ok=True)
    out.write_text(html)
    ok = upload(p.state, html)
    print(json.dumps({"uploaded": ok, "bytes": len(html)}))
    return 0


def main(path: str) -> int:
    req = json.loads(Path(path).read_text())
    action = req.get("action")
    p = Pipeline(load())
    # ---- Bhaukaali Toons / Sab Theek Hai was dropped by the owner on 28 Oct 2026 ----
    if action == "retire_sketch":
        from shorts.sketch import episodes as E
        done = []
        for ep in E.all_eps(p.state, ("writing", "review", "revising", "approved")):
            ep["status"] = "rejected"
            E.log(ep, "retired", "owner dropped the Bhaukaali Toons show (28 Oct 2026)")
            E.save(p.state, ep)
            done.append(ep["id"])
        msg = ("🛑 Bhaukaali Toons is stopped. These episodes are cancelled and will never be uploaded: "
               + (", ".join(done) or "none") + ". Their buttons no longer do anything.")
        notify.send(p.state, msg)
        print(msg)
        return 0
    if str(req.get("job", "")).startswith("ep") or action in ("sketch_daily", "sketch_produce", "grow", "send_review"):
        notify.send(p.state, "That Bhaukaali Toons episode was cancelled (the show is stopped). Nothing was done.")
        return 0
    # ---- Secret Smart Stuff explainers (the live format) ----
    if action in ("produce", "daily"):
        return do_produce(p, req)
    if action in ("approve", "reject", "fix"):
        return do_decision(p, req)
    if action == "rerender":
        return do_rerender(p, req)
    if action == "status":
        return do_status(p)
    if action == "backfill":
        # videos published before features/experiments existed: record what they were made of
        import time as _t
        for up in p.state.db.execute("SELECT job_id, publish_at FROM uploads WHERE video_id IS NOT NULL").fetchall():
            job = up["job_id"]
            if p.state.db.execute("SELECT 1 FROM features WHERE job_id=?", (job,)).fetchone():
                continue
            d = ROOT / "build" / job
            fetch_bundle(job, d)
            if not (d / "script.json").exists():
                continue
            j = p.state.get_job(job)
            slot = (up["publish_at"] or "T13:30")[11:16]
            for e in X.load_experiments():
                if e.get("variable") == "publish_slot_utc":
                    arm = next((a for a, v in e["arms"].items() if v == slot), None)
                    if arm:
                        X.sync(p.state)
                        with p.state.tx() as db:
                            db.execute("INSERT OR IGNORE INTO assignments(experiment_id, job_id, arm, at) VALUES (?,?,?,?)",
                                       (e["id"], job, arm, _t.time()))
            vis = json.loads((d / "visuals.json").read_text()) if (d / "visuals.json").exists() else {}
            words = json.loads((d / "words.json").read_text()) if (d / "words.json").exists() else []
            from shorts.render.sfx import pick_music
            render = {"duration": (words[-1]["end"] + 0.12) if words else 0, "music": str(pick_music(job) or "")}
            p.state.set_features(job, {**X.features(json.loads((d / "script.json").read_text()), vis, render,
                                                    p.state.get_topic(j["topic_id"]), p.state.job_cost(job)),
                                       "publish_slot_utc": slot, "publish_at": up["publish_at"]})
        return do_verify(p)
    if action == "fetch":
        # copy files from signed URLs (e.g. ElevenLabs generations) into a GitHub pre-release
        import requests
        name = re.sub(r"[^a-z0-9-]", "", req["name"])
        d = ROOT / "build" / name
        d.mkdir(parents=True, exist_ok=True)
        files = []
        for fn, url in (req.get("files") or {}).items():
            fn = re.sub(r"[^A-Za-z0-9._-]", "", fn)
            r = requests.get(url, timeout=300)
            r.raise_for_status()
            (d / fn).write_bytes(r.content)
            files.append(str(d / fn))
        tag = f"media-{name}"
        if subprocess.run(["gh", "release", "view", tag], capture_output=True).returncode == 0:
            gh("release", "upload", tag, *files, "--clobber")
        else:
            gh("release", "create", tag, *files, "--prerelease", "--title", tag, "--notes", "working media")
        return 0
    if action == "sketch":
        spec = ROOT / req["spec"]
        r = subprocess.run([sys.executable, str(ROOT / "scripts" / "sketch_assemble.py"), str(spec)],
                           capture_output=True, text=True)
        print(r.stdout, r.stderr[-3000:])
        name = json.loads(spec.read_text())["name"]
        d = ROOT / "build" / name
        tag = f"media-{name}"
        files = [str(p) for p in (d / "final.mp4", d / "timeline.json") if p.exists()]
        if not files:
            (d).mkdir(parents=True, exist_ok=True)
            (d / "error.txt").write_text(r.stderr[-6000:] or "no output")
            files = [str(d / "error.txt")]
        if subprocess.run(["gh", "release", "view", tag], capture_output=True).returncode == 0:
            gh("release", "upload", tag, *files, "--clobber")
        else:
            gh("release", "create", tag, *files, "--prerelease", "--title", tag, "--notes", "sketch render")
        return r.returncode
    if action == "accounts":
        # provider balances (no secrets printed), reported on a GitHub issue
        import requests
        lines = []
        try:
            r = requests.get("https://api.elevenlabs.io/v1/user/subscription",
                             headers={"xi-api-key": os.environ.get("ELEVENLABS_API_KEY", "")}, timeout=30).json()
            lines.append(f"ElevenLabs: tier={r.get('tier')} used={r.get('character_count')} limit={r.get('character_limit')} "
                         f"next_reset={r.get('next_character_count_reset_unix')} status={r.get('status')}")
        except Exception as e:  # noqa: BLE001
            lines.append(f"ElevenLabs: error {e}")
        try:
            r = requests.get("https://api.bfl.ai/v1/credits", headers={"x-key": os.environ.get("BFL_API_KEY", "")}, timeout=30)
            lines.append(f"BFL: {r.status_code} {r.text[:200]}")
        except Exception as e:  # noqa: BLE001
            lines.append(f"BFL: error {e}")
        gh("issue", "create", "--title", "Accounts check", "--label", "audio", "--body", "\n".join(f"- {x}" for x in lines), check=False)
        print(lines)
        return 0
    if action == "upload_sketch":
        # Upload an approved sketch as PRIVATE (owner publishes/schedules it in YouTube Studio).
        from shorts.publish.youtube import VideoMeta, upload
        if req.get("path"):                       # a master file committed in the repo
            src = ROOT / req["path"]
            d, fname = src.parent, src.name
        else:                                     # or a file on a GitHub release
            tag, fname = req["release"], req["file"]
            d = ROOT / "build" / "upload"
            d.mkdir(parents=True, exist_ok=True)
            gh("release", "download", tag, "-p", fname, "-D", str(d), "--clobber")
        ch = (p.cfg.channel or {}).get("channel", {})
        meta = VideoMeta(title=req["title"], description=req["description"], tags=req.get("tags", []),
                         category_id=str(ch.get("youtube_category_id", "23")), language=ch.get("language", "hi"),
                         made_for_kids=False, contains_synthetic_media=bool(req.get("synthetic", False)),
                         publish_at=req.get("publish_at"))
        try:
            res = upload(p.state, req["job"], d / fname, meta)
            msg = f"Uploaded as PRIVATE: {res['url']} (video id {res['video_id']}). Publish or schedule it in YouTube Studio."
        except Exception as e:  # noqa: BLE001
            msg = f"Upload failed: {e}"
        if msg.startswith("Uploaded") and req.get("episode"):     # record it in the episode calendar
            from shorts.sketch import episodes as E
            num = int(req["episode"])
            ep = E.get(p.state, f"ep{num:03d}") or {"id": f"ep{num:03d}", "number": num, "history": []}
            ep.update(status="scheduled" if req.get("publish_at") else "uploaded", slot=req.get("publish_at") or "",
                      title=req["title"], yt_video_id=res.get("video_id"), meta={"title": req["title"],
                      "description": req["description"], "tags": req.get("tags", [])})
            E.log(ep, "scheduled", req.get("publish_at") or "")
            E.save(p.state, ep)
            when = E.fmt_ist(req["publish_at"]) if req.get("publish_at") else "not scheduled"
            notify.send(p.state, f"✅ Ep {num} uploaded (private). Goes public <b>{when}</b>.\n{res.get('url')}")
        gh("issue", "create", "--title", f"Upload: {req['title'][:60]}", "--body", msg, check=False)
        print(msg)
        return 0 if msg.startswith("Uploaded") else 1
    if action == "voice_test":
        import requests as _rq
        from shorts.sketch import world as _W
        key = os.environ["ELEVENLABS_API_KEY"]
        out = Path("build/voice_test"); out.mkdir(parents=True, exist_ok=True)
        rows, files = [], []
        for kind, ids in _W.load()["voice_pool"].items():
            if kind.startswith("_"):
                continue
            for vid in ids:
                info = _rq.get(f"https://api.elevenlabs.io/v1/voices/{vid}", headers={"xi-api-key": key}, timeout=30)
                lab = info.json().get("labels", {}) if info.ok else {}
                name = info.json().get("name", "?") if info.ok else f"info {info.status_code}"
                r = _rq.post(f"https://api.elevenlabs.io/v1/text-to-speech/{vid}", params={"output_format": "mp3_44100_128"},
                             headers={"xi-api-key": key}, json={"text": "अरे बेटा, खाना खाया कि नहीं? सच सच बताना।",
                                                                 "model_id": "eleven_v4"}, timeout=120)
                ok = r.status_code == 200
                if ok:
                    f = out / f"{kind}_{vid}.mp3"; f.write_bytes(r.content); files.append(f)
                rows.append(f"- {kind} {vid}: {name} {lab} tts={'ok' if ok else r.status_code} {'' if ok else r.text[:150]}")
        if files:
            gh("release", "create", "voice-test", "--prerelease", "--title", "voice test", "--notes", "pool voices", check=False)
            gh("release", "upload", "voice-test", *[str(f) for f in files], "--clobber", check=False)
        gh("issue", "create", "--title", "Voice pool test", "--body", "\n".join(rows), check=False)
        print("\n".join(rows))
        return 0
    if action == "judge_calibrate":
        # score known episodes with the script judge (owner-approved vs owner-rejected) to set the gate bar
        from shorts.sketch import episodes as _E, flow as _F, judge as _J, writer as _Wr
        llm = _F._llm(p)
        cost = [0.0]
        rows = []
        for item in req.get("scripts", []):
            for k in range(int(req.get("repeats", 2))):
                r = _J.rubric(llm, item["text"], cost, context=_Wr.lessons_brief())
                rows.append(f"### {item['name']} (owner: {item['owner']}) run {k + 1}: total {r['total']} min {r['min']}\n"
                            f"scores {r['scores']}\nflags {r.get('red_flags')}\n")
        for ep_id in req.get("episodes", []):
            ep = _E.get(p.state, ep_id)
            if ep and ep.get("plan"):
                r = _J.rubric(llm, _J.script_text(ep["plan"]), cost, context=_Wr.lessons_brief())
                rows.append(f"### {ep_id} (status {ep['status']}): total {r['total']} min {r['min']}\nscores {r['scores']}\n"
                            f"flags {r.get('red_flags')}\n")
        p.state.add_cost("anthropic", "judge calibration", 1, cost[0])
        gh("issue", "create", "--title", "Judge calibration", "--body", "\n".join(rows)[:60000] + f"\n\ncost ${cost[0]:.2f}", check=False)
        print("\n".join(rows))
        return 0
    if action == "art_test":
        from shorts.sketch import art as _A
        res = []
        for pid, who, desc in req.get("poses", []):
            res.append(f"pose {pid}: {_A.generate_pose(p, who, pid, desc)}")
        for c in req.get("characters", []):
            res.append(f"character {c['id']}: " + str(_A.generate_character(p, c["id"], c["name"], c["desc"], c["look"],
                                                                         c.get("height", 0.95), c.get("voice", ""), save=c.get("save", False))))
        files = [f for f in Path("build/art").glob("*") if f.suffix in (".png",) and ("sheet" in f.name or f.name.startswith(("pose_", "char_")))]
        gh("release", "create", "art-test", "--prerelease", "--title", "art test", "--notes", "art test outputs", check=False)
        if files:
            gh("release", "upload", "art-test", *[str(f) for f in files], "--clobber", check=False)
        logs = [r["message"] for r in p.state.db.execute("SELECT message FROM events ORDER BY at DESC LIMIT 25").fetchall()]
        gh("issue", "create", "--title", "Art test", "--body", "\n".join(res) + "\n\nLog:\n" + "\n".join(f"- {x}" for x in reversed(logs))[:60000], check=False)
        print(res)
        return 0
    if action == "video_status":
        import requests as _rq
        from shorts.publish.youtube import access_token
        ids = ",".join(req["ids"])
        r = _rq.get("https://www.googleapis.com/youtube/v3/videos",
                    params={"part": "status,snippet,statistics,contentDetails", "id": ids},
                    headers={"Authorization": f"Bearer {access_token()}"}, timeout=60)
        rows = [f"- {v['id']}: {v['snippet']['title']} | channel={v['snippet'].get('channelTitle')} | "
                f"privacy={v['status'].get('privacyStatus')} | publishAt={v['status'].get('publishAt')} | "
                f"published={v['snippet'].get('publishedAt')} | madeForKids={v['status'].get('madeForKids')} | "
                f"lang={v['snippet'].get('defaultAudioLanguage')} | dur={v['contentDetails'].get('duration')} | "
                f"views={v['statistics'].get('viewCount')} likes={v['statistics'].get('likeCount')} "
                f"comments={v['statistics'].get('commentCount')} | tags={v['snippet'].get('tags')}"
                for v in r.json().get("items", [])] or [f"no data: {r.status_code} {r.text[:200]}"]
        ch = _rq.get("https://www.googleapis.com/youtube/v3/channels", params={"part": "snippet,statistics,brandingSettings",
                     "mine": "true"}, headers={"Authorization": f"Bearer {access_token()}"}, timeout=60).json()
        for c in ch.get("items", []):
            rows.append(f"- CHANNEL {c['snippet']['title']} | subs={c['statistics'].get('subscriberCount')} | "
                        f"videos={c['statistics'].get('videoCount')} | views={c['statistics'].get('viewCount')} | "
                        f"country={c['snippet'].get('country')} | lang={c['snippet'].get('defaultLanguage')}")
        lst = _rq.get("https://www.googleapis.com/youtube/v3/search", params={"part": "snippet", "forMine": "true",
                      "type": "video", "maxResults": 25, "order": "date"},
                      headers={"Authorization": f"Bearer {access_token()}"}, timeout=60).json()
        for it in lst.get("items", []):
            rows.append(f"- recent: {it['id'].get('videoId')} {it['snippet']['publishedAt']} {it['snippet']['title']}")
        gh("issue", "create", "--title", "Video status", "--body", "\n".join(rows), check=False)
        print(rows)
        return 0
    if action == "diag":
        # run CLI subcommands and post the tail of their output (no secrets are printed by these)
        out = []
        for sub in req.get("run") or ["analytics", "learn"]:
            r = subprocess.run([sys.executable, "-m", "shorts.cli", sub], capture_output=True, text=True, timeout=600)
            tail = (r.stdout + "\n" + r.stderr).strip().splitlines()[-30:]
            out.append(f"### `{sub}` → exit {r.returncode}\n```\n" + "\n".join(tail) + "\n```")
        gh("issue", "create", "--title", "Diagnostics", "--body", "\n\n".join(out), check=False)
        print("\n".join(out))
        return 0
    if action == "probe":
        # what each service account looks like right now (names, plans, permissions; never secret values)
        import requests
        out = []
        def safe(label, fn):
            try:
                out.append(f"- {label}: {fn()}")
            except Exception as e:  # noqa: BLE001
                out.append(f"- {label}: ERROR {type(e).__name__}: {str(e)[:200]}")
        repo = os.environ.get("GITHUB_REPOSITORY", "")
        ght = os.environ.get("GH_DISPATCH_TOKEN", "")
        H = {"authorization": f"Bearer {ght}", "accept": "application/vnd.github+json"}
        safe("GH token can read secrets key", lambda: requests.get(f"https://api.github.com/repos/{repo}/actions/secrets/public-key", headers=H, timeout=30).status_code)
        safe("GH token repo admin", lambda: requests.get(f"https://api.github.com/repos/{repo}", headers=H, timeout=30).json().get("permissions"))
        safe("GH token type", lambda: "fine-grained" if ght.startswith("github_pat_") else ("classic" if ght.startswith("ghp_") else "other"))
        tg = os.environ.get("TELEGRAM_BOT_TOKEN", "")
        safe("Telegram bot", lambda: {k: v for k, v in requests.get(f"https://api.telegram.org/bot{tg}/getMe", timeout=30).json().get("result", {}).items() if k in ("first_name", "username")})
        safe("Telegram description", lambda: requests.get(f"https://api.telegram.org/bot{tg}/getMyDescription", timeout=30).json().get("result"))
        safe("Telegram short description", lambda: requests.get(f"https://api.telegram.org/bot{tg}/getMyShortDescription", timeout=30).json().get("result"))
        safe("Telegram webhook", lambda: requests.get(f"https://api.telegram.org/bot{tg}/getWebhookInfo", timeout=30).json().get("result", {}).get("url", "")[:80])
        cft, acc = os.environ.get("CLOUDFLARE_API_TOKEN", ""), os.environ.get("CLOUDFLARE_ACCOUNT_ID", "")
        CH = {"authorization": f"Bearer {cft}"}
        safe("Cloudflare subdomain", lambda: requests.get(f"https://api.cloudflare.com/client/v4/accounts/{acc}/workers/subdomain", headers=CH, timeout=30).json().get("result"))
        safe("Cloudflare workers", lambda: [w.get("id") for w in requests.get(f"https://api.cloudflare.com/client/v4/accounts/{acc}/workers/scripts", headers=CH, timeout=30).json().get("result") or []])
        safe("Cloudflare account", lambda: [a.get("name") for a in requests.get("https://api.cloudflare.com/client/v4/accounts", headers=CH, timeout=30).json().get("result") or []])
        el = {"xi-api-key": os.environ.get("ELEVENLABS_API_KEY", "")}
        safe("ElevenLabs plan", lambda: {k: v for k, v in requests.get("https://api.elevenlabs.io/v1/user/subscription", headers=el, timeout=30).json().items() if k in ("tier", "character_count", "character_limit", "next_character_count_reset_unix", "voice_slots_used", "voice_limit", "status")})
        safe("ElevenLabs own voices", lambda: [(v.get("name"), v.get("category")) for v in requests.get("https://api.elevenlabs.io/v1/voices", headers=el, timeout=30).json().get("voices", []) if v.get("category") != "premade"])
        bfl = {"x-key": os.environ.get("BFL_API_KEY", "")}
        safe("BFL credits", lambda: requests.get("https://api.bfl.ai/v1/credits", headers=bfl, timeout=30).json())
        gh("issue", "create", "--title", "Accounts probe", "--body", "\n".join(out), check=False)
        print("\n".join(out))
        return 0
    if action == "whoami":
        # which YouTube channel the stored login uploads to (no secrets printed)
        import requests
        try:
            tok = requests.post("https://oauth2.googleapis.com/token", data={
                "client_id": os.environ.get("YT_CLIENT_ID", ""), "client_secret": os.environ.get("YT_CLIENT_SECRET", ""),
                "refresh_token": os.environ.get("YT_REFRESH_TOKEN", ""), "grant_type": "refresh_token"}, timeout=30)
            if tok.status_code != 200:
                msg = f"Login check FAILED: {tok.status_code} {tok.json().get('error', '')} {tok.json().get('error_description', '')}"
            else:
                body = tok.json()
                r = requests.get("https://www.googleapis.com/youtube/v3/channels", params={"part": "snippet,status", "mine": "true"},
                                 headers={"Authorization": f"Bearer {body['access_token']}"}, timeout=30).json()
                items = r.get("items") or []
                msg = "\n".join(f"- Channel: {c['snippet'].get('title')} | handle: {c['snippet'].get('customUrl')} | id: {c['id']} | "
                                f"madeForKids: {c.get('status', {}).get('madeForKids')}" for c in items) or f"- No channel found: {str(r)[:300]}"
                msg = f"Login OK. Scopes: {body.get('scope', '')}\n{msg}"
        except Exception as e:  # noqa: BLE001
            msg = f"Login check error: {e}"
        gh("issue", "create", "--title", "YouTube login check", "--body", msg, check=False)
        print(msg)
        return 0
    if action == "retire":
        for old in req.get("jobs") or []:
            jj = p.state.get_job(old)
            if jj and jj["status"] in ("review", "failed", "paused", "running"):
                p.state.set_job_status(old, "rejected", "retired: superseded")
                p.state.set_topic_status(jj["topic_id"], "shortlisted")
                comment(old, "Retired: superseded by the current format. The topic stays in the backlog.", close=True)
        return 0
    if action == "revenue":
        return do_revenue(p, req)
    if action == "verify":
        return do_verify(p)
    if action == "dashboard":
        return do_dashboard(p)
    if action == "setup_studio":
        r = subprocess.run([sys.executable, str(ROOT / "scripts" / "deploy_worker.py")], capture_output=True, text=True)
        print(r.stdout, r.stderr[-2000:])
        if r.returncode == 0:
            notify.send(p.state, "🤝 Connected. New Bhaukaali Toons episodes will arrive here for your review.\nSend /help to see what I can do.")
            try:
                do_dashboard(p)
            except Exception as e:  # noqa: BLE001
                print("dashboard skipped:", e)
        else:
            alert(p, "Studio setup problem", r.stdout[-1500:] + "\n" + r.stderr[-1500:])
        return r.returncode
    if action == "build_audio":
        from shorts.providers.music import generate_library, generate_sfx
        key = os.environ.get("ELEVENLABS_API_KEY", "")
        notes = []
        for name, fn, folder in (("music", generate_library, "music"), ("sfx", generate_sfx, "sfx")):
            try:
                notes.append(f"{name}: {len(fn(key, ROOT / 'assets' / folder))} new")
            except Exception as e:  # noqa: BLE001
                notes.append(f"{name} failed: {e}")
        subprocess.run(["git", "config", "user.name", "shorts-bot"], check=True)
        subprocess.run(["git", "config", "user.email", "shorts-bot@users.noreply.github.com"], check=True)
        subprocess.run(["git", "add", "assets/music", "assets/sfx"], check=False)
        if subprocess.run(["git", "diff", "--cached", "--quiet"]).returncode != 0:
            subprocess.run(["git", "commit", "-m", "Add generated audio library"], check=True)
            subprocess.run(["git", "push", "origin", "HEAD:main"], check=True)
        print(notes)
        return 0 if all("failed" not in n for n in notes) else 1
    raise SystemExit(f"unknown action {action!r}")


if __name__ == "__main__":
    sys.exit(main(sys.argv[1]))
