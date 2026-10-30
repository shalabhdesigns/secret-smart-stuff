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
import tempfile
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
    import re as _re
    clean = _re.sub(r"<!--.*?-->", "", body).strip()
    notify.send(p.state, f"⚠️ {notify.esc(title)}\n{notify.esc(clean[:900])}")
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


def preserve_media(p: Pipeline) -> None:
    """After a crash: save every finished-but-unpublished video's media to its review release, so the next run can
    resume it instead of paying for new pictures and voice (30 Oct 2026: a crash lost the knife video's media)."""
    for jj in p.state.jobs("review") + p.state.jobs("paused"):
        d = ROOT / "build" / jj["id"]
        if (d / "final.mp4").exists() and (d / "metadata.json").exists():
            subprocess.run([str(ROOT / "scripts" / "open_review.sh"), jj["id"]], check=False)


def record_features(p: Pipeline, job: str) -> tuple[str, str]:
    """What the video is made of (for the learning loop) + its publish slot. Returns (slot, publish time)."""
    j = p.state.get_job(job)
    d = ROOT / "build" / job
    script = json.loads((d / "script.json").read_text())
    slot = X.slot_for(p.state, job)
    when = X.next_publish_time(p.state, slot, margin_minutes=30)
    topic = p.state.get_topic(j["topic_id"])
    feats = X.features(script, json.loads((d / "visuals.json").read_text()) if (d / "visuals.json").exists() else {},
                       j["artifacts"].get("render"), topic, p.state.job_cost(job))
    try:
        beats, end = p._beat_frames(d)
        feats["beats"] = [{"id": b["id"], "start": b["start"], "words": b["words"]} for b in beats]
        feats.setdefault("seconds", round(end, 1))
    except Exception as e:  # noqa: BLE001
        p.state.log(f"beat timings not recorded: {e}", "warn", job)
    crit = json.loads((d / "critique.json").read_text()) if (d / "critique.json").exists() else []
    if crit:
        feats["self_review"] = {"rounds": len(crit), "mean": crit[-1].get("mean"), "scores": crit[-1].get("scores")}
    lj = d / "learnings.json"
    if lj.exists():                                     # which earlier lessons this video applied (for evaluation)
        feats["learnings_applied"] = json.loads(lj.read_text()).get("applied", [])
    p.state.set_features(job, {**feats, "publish_slot_utc": slot})
    return slot, when


def auto_mode(p: Pipeline) -> bool:
    """Owner (28 Oct 2026): publish without his approval for 28 days when the video passes the final review."""
    a = p.cfg.pipeline.get("approval") or {}
    until = str(a.get("auto_until") or "")
    on = a.get("mode") == "auto" and p.cfg.live and (not until or time.strftime("%Y-%m-%d", time.gmtime()) <= until)
    if a.get("mode") == "auto" and not on and until and not p.state.get_setting(f"auto_ended:{until}"):
        p.state.set_setting(f"auto_ended:{until}", "1")
        notify.send(p.state, f"🔔 The automatic publishing period ended ({until}). New videos now wait for your ✅ "
                             "again. Tell me if you want to extend it.")
    return on


def auto_publish(p: Pipeline, job: str) -> int:
    subprocess.run([str(ROOT / "scripts" / "open_review.sh"), job], check=True)     # record: release + issue
    d = ROOT / "build" / job
    slot, when = record_features(p, job)
    crit = json.loads((d / "critique.json").read_text()) if (d / "critique.json").exists() else [{}]
    c = crit[-1]
    p.decide(job, "approve", f"auto: passed the final review (mean {c.get('mean')})")
    try:
        rec = p.publish(job, publish_at=when)
    except Exception as e:  # noqa: BLE001
        p.state.set_job_status(job, "approved", str(e))
        alert(p, f"Upload failed: {job}", f"{e}\n\nNothing was published. It will be retried on the next run.")
        return 1
    feats = p.state.db.execute("SELECT data FROM features WHERE job_id=?", (job,)).fetchone()
    if feats:
        p.state.set_features(job, {**json.loads(feats["data"]), "publish_at": when})
    meta = json.loads((d / "metadata.json").read_text())
    sc = c.get("scores") or {}
    cap = (f"✅ <b>{notify.esc(meta.get('title', job))}</b>\nUploaded. Goes public {ist(when)} IST.\n"
           f"{rec.get('url')}\nMy review: {c.get('mean')}/5 · hook {sc.get('hook_curiosity', '?')} · "
           f"credibility {sc.get('visual_credibility', '?')} · share {sc.get('share', '?')} · cost ${p.state.job_cost(job):.2f}\n"
           f"{notify.esc(c.get('summary', ''))}\n<code>job:{job}</code>")
    notify.send_video(p.state, d / "final.mp4", cap, [[("⏸ Stop it", f"s:{job}"[:64])]])
    comment(job, f"✅ Auto-published (private until {when} UTC). {rec.get('url')}", close=True)
    return 0


def send_for_review(p: Pipeline, job: str) -> None:
    """Publish the review bundle (release + issue) and send the video to the owner's phone."""
    subprocess.run([str(ROOT / "scripts" / "open_review.sh"), job], check=True)
    j = p.state.get_job(job)
    d = ROOT / "build" / job
    meta = json.loads((d / "metadata.json").read_text()) if (d / "metadata.json").exists() else {}
    rv = (j["artifacts"].get("review") or {}).get("content") or {}
    vis = j["artifacts"].get("visuals") or {}
    slot, when = record_features(p, job)
    crit = json.loads((d / "critique.json").read_text()) if (d / "critique.json").exists() else []
    extra = ""
    if crit:
        c = crit[-1]
        sc = c.get("scores") or {}
        extra = (f"My review: {'passed' if c.get('passed') else 'NOT passed'} after {len(crit)} round(s) · "
                 f"hook {sc.get('hook_curiosity', '?')}/5 · credibility {sc.get('visual_credibility', '?')}/5 · "
                 f"rewatch {sc.get('rewatch', '?')}/5 · share {sc.get('share', '?')}/5\n{c.get('summary', '')}")
    notify.review(p.state, job, d / "final.mp4", meta.get("title") or job, rv.get("total", "?"),
                  p.state.job_cost(job), [f for f in (vis.get("flags") or []) if not f.startswith("BLOCKING")],
                  f"{when} UTC (≈ {ist(when)} IST)", extra)


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

def keep_rejected(job: str) -> None:
    """Save a video that failed the final review (video, contact sheet, review notes) for inspection."""
    d = ROOT / "build" / job
    files = [str(d / f) for f in ("final.mp4", "contact_sheet.jpg", "critique.json", "review.md", "script.json")
             if (d / f).exists()]
    if files and os.environ.get("SHORTS_NO_GITHUB") != "1":
        gh("release", "create", f"rejected-{job}", *files, "--prerelease", "--title", f"Rejected by self-review: {job}",
           "--notes", "Not sent to the owner. Kept to learn from.", check=False)


def self_review(p: Pipeline, job: str, rounds: int = 3) -> dict:
    """Claude's final review of the finished video, with up to `rounds` reviews (so at most rounds-1 targeted
    fixes). Only a video that passes reaches the owner. See Pipeline.critique for the bar."""
    d = ROOT / "build" / job
    if not (d / "final.mp4").exists():
        fetch_bundle(job, d)
    topic = p.state.get_job(job)["topic_id"]
    c, prev = {}, None
    from shorts.budget import BudgetExceeded
    for r in range(1, rounds + 1):
        try:
            c = p.critique(job, r, prev)
        except BudgetExceeded as e:
            return {**(prev or {}), "passed": False, "budget_stop": True,
                    "summary": f"stopped: budget limit reached before review round {r} ({e})"}
        if c.get("passed") or c.get("verdict") == "drop" or c.get("unshowable") or r == rounds:
            return c
        p.prepare_prior(job, c)
        try:
            p.decide(job, "selffix", p.fix_note(c, job))
            p.produce(topic)
        except BudgetExceeded as e:   # a spending limit is not a quality verdict: pause, never drop or crash
            return {**c, "passed": False, "budget_stop": True, "summary": f"fix paused: budget limit ({e})"}
        j = p.state.get_job(job)
        if j["status"] != "review" or j["error"]:
            c = {**c, "passed": False, "summary": f"fix round stopped: {j['status']} {j['error'] or ''}"}
            return c
        prev = c
    return c


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
    if req.get("action") == "daily":
        # one video a day: two triggers (GitHub's schedule and the Worker's timer) may both fire
        today = time.strftime("%Y-%m-%d", time.gmtime(time.time() + 5.5 * 3600))     # IST day
        if p.state.get_setting("last_daily_ist") == today:
            print(f"daily run already done for {today}; skipping")
            return 0
        p.state.set_setting("last_daily_ist", today)
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
    topics_left = 2           # a topic that fails the final review is dropped; one more topic is tried
    while j["status"] == "review" and not j["error"] and not req.get("skip_self_review"):
        c = self_review(p, job)
        if c.get("passed"):
            break
        if c.get("budget_stop"):
            # not a failed video: keep it, tell the owner, finish it when money allows (never publish it unreviewed)
            p.state.set_job_status(job, "paused", c["summary"][:300])
            notify.send(p.state, f"⏸ {job} is paused: a spending limit stopped its fix ({notify.esc(c['summary'][:200])}). "
                                 "Nothing was published. Raise the limit or tell me to drop it.")
            return 0
        reason = f"self-review: {c.get('summary', '')}"[:400]
        keep_rejected(job)
        p.decide(job, "reject", reason)
        p.state.log(f"{job} dropped by self-review: {reason}", "warn", job)
        topics_left -= 1
        t = p.next_topic() if topics_left > 0 and not req.get("topic") else None
        if not t:
            notify.send(p.state, f"🔍 No video this time: it failed my final check ({c.get('summary', '')[:300]}). "
                                 "I'll try a new topic on the next run.")
            return 0
        job = p.produce(t["id"])
        j = p.state.get_job(job)
    if j["status"] == "review" and not j["error"]:
        if auto_mode(p) and not req.get("hold"):
            return auto_publish(p, job)
        if req.get("hold"):
            # Claude checks it frame by frame first, then sends it with {"action":"send_review","job":...}
            subprocess.run([str(ROOT / "scripts" / "open_review.sh"), job], check=True)
            print(f"held for checking: {job}")
            return 0
        send_for_review(p, job)
        return 0
    if j["status"] == "paused":
        notify.send(p.state, f"⏸ {job} paused: a budget limit was reached. It finishes automatically on the next run.")
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
            self_review(p, job, rounds=2)
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


def _login_link(p: Pipeline) -> str:
    """A one-time link to the Worker's YouTube login (same as sending /ytlogin to the bot)."""
    import secrets as _s
    import requests
    acc = (os.environ.get("CLOUDFLARE_ACCOUNT_ID") or str(p.cfg.pipeline.get("cloudflare_account_id", ""))).strip()
    ns, url = p.state.get_setting("cf_kv_namespace"), p.state.get_setting("worker_url")
    n = _s.token_hex(24)
    r = requests.put(f"https://api.cloudflare.com/client/v4/accounts/{acc}/storage/kv/namespaces/{ns}/values/oauth_link:{n}",
                     params={"expiration_ttl": 1800}, data="1",
                     headers={"Authorization": f"Bearer {os.environ['CLOUDFLARE_API_TOKEN']}"}, timeout=30)
    if r.status_code != 200:
        return "(could not make the link; send /ytlogin to this bot instead)"
    return f"{url}/oauth/start?n={n}"


def main(path: str) -> int:
    req = json.loads(Path(path).read_text())
    action = req.get("action")
    p = Pipeline(load())
    if req.get("owner_ok_extra_daily_usd"):
        # one-off, owner-approved extra room on the rolling 24 h limit (the monthly cap still applies)
        extra = min(float(req["owner_ok_extra_daily_usd"]), 5.0)
        spent_24h = p.state.spend_since(time.time() - 86400)
        p.budget.limits.daily_usd = max(p.budget.limits.daily_usd, spent_24h + extra)
        p.state.log(f"owner allowed +${extra:.2f} on today's daily limit for this run")
    # ---- Secret Smart Stuff explainers (the live format) ----
    if action in ("produce", "daily"):
        try:
            return do_produce(p, req)
        except Exception:
            preserve_media(p)       # a crash must not throw away paid-for pictures and voice
            raise
    if action in ("approve", "reject", "fix"):
        return do_decision(p, req)
    if action == "rename_repo":
        # owner asked (28 Oct 2026): repo back to its Secret Smart Stuff name; then redeploy the Worker so its
        # Telegram buttons dispatch to the new name (GitHub redirects git, but not workflow dispatch POSTs)
        import requests
        old, new = os.environ.get("GITHUB_REPOSITORY", ""), f"{os.environ.get('GITHUB_REPOSITORY_OWNER', 'shalabhdesigns')}/{req['name']}"
        if old.lower() != new.lower():
            r = requests.patch(f"https://api.github.com/repos/{old}", json={"name": req["name"]},
                               headers={"authorization": f"Bearer {os.environ['GH_DISPATCH_TOKEN']}",
                                        "accept": "application/vnd.github+json"}, timeout=30)
            print("rename:", r.status_code, r.json().get("full_name") if r.ok else r.text[:300])
            if not r.ok:
                alert(p, "Repo rename failed", f"{r.status_code} {r.text[:500]}")
                return 1
        env = {**os.environ, "GITHUB_REPOSITORY": new}
        d = subprocess.run([sys.executable, str(ROOT / "scripts" / "deploy_worker.py")], capture_output=True, text=True, env=env)
        print(d.stdout, d.stderr[-2000:])
        if d.returncode != 0:
            alert(p, "Studio redeploy after rename failed", d.stdout[-1500:] + "\n" + d.stderr[-1500:])
            return d.returncode
        notify.send(p.state, f"🔧 Repo is now {new}; studio address: {p.state.get_setting('worker_url') or '?'}. "
                             "Buttons and /ytlogin keep working; your YouTube login is unchanged.")
        return 0
    if action == "archive_old_show_data":
        # one-off (28 Oct 2026): move the dropped sketch show's rows out of the live database into a JSON file on
        # the archive branch, then remove those tables, so nothing of it is left in the live system
        tables = [r[0] for r in p.state.db.execute("SELECT name FROM sqlite_master WHERE type='table' AND "
                                                   "(name LIKE '%_bhaukaali' OR name='episodes')")]
        dump = {t: [dict(r) for r in p.state.db.execute(f"SELECT * FROM {t}")] for t in tables}
        wt = ROOT / ".archive-wt"
        subprocess.run(["git", "config", "user.name", "shorts-bot"], check=True)
        subprocess.run(["git", "config", "user.email", "shorts-bot@users.noreply.github.com"], check=True)
        subprocess.run(["git", "fetch", "-q", "origin", "archive/bhaukaali-toons"], check=True)
        subprocess.run(["git", "worktree", "add", "-q", str(wt), "FETCH_HEAD"], check=True)
        (wt / "data").mkdir(exist_ok=True)
        (wt / "data" / "state_export_28oct2026.json").write_text(json.dumps(dump, indent=1, default=str, ensure_ascii=False))
        subprocess.run(["git", "-C", str(wt), "add", "data"], check=True)
        subprocess.run(["git", "-C", str(wt), "commit", "-qm", "Archive: live-database rows of the dropped show"], check=True)
        subprocess.run(["git", "-C", str(wt), "push", "-q", "origin", "HEAD:refs/heads/archive/bhaukaali-toons"], check=True)
        subprocess.run(["git", "worktree", "remove", "--force", str(wt)], check=True)
        with p.state.tx() as db:
            for t in tables:
                db.execute(f"DROP TABLE {t}")
            db.execute("DELETE FROM settings WHERE key LIKE 'publish_slot_ist%' OR key LIKE 'art_%' OR key LIKE 'sketch%'")
        print({t: len(v) for t, v in dump.items()})
        return 0
    if action == "drop_topics":
        for tid in req.get("topics") or []:
            for jj in p.state.jobs():
                if jj["topic_id"] == tid and jj["status"] not in ("published", "approved"):
                    p.state.set_job_status(jj["id"], "rejected", req.get("reason", "dropped"))
            if p.state.get_topic(tid):
                p.state.set_topic_status(tid, "rejected")
        return 0
    if action == "image_bakeoff":
        # same hard prompts on several BFL models; images + credibility checks go to a release and an issue
        from shorts.providers.images import BFLImages
        ic = p.cfg.pipeline["providers"]["images"]
        prices = {**ic["usd_each"], **(req.get("prices") or {})}
        gen = BFLImages(p.cfg.secret("BFL_API_KEY"), ic["model"], ic["width"], ic["height"], prices)
        d = ROOT / "build" / "bakeoff"
        d.mkdir(parents=True, exist_ok=True)
        style = p.cfg.channel["style"]["image_style"]
        rows, files = [], []
        for i, pr in enumerate(req["prompts"]):
            for m in req["models"]:
                out = d / f"p{i + 1}_{m}.png"
                try:
                    if p.cfg.live:
                        p.budget.authorize(float(prices.get(m, 0.08)), "bakeoff", None)
                    img, usd = gen.generate(f"{pr}. {style}. Vertical 9:16 composition.", out, seed=1234 + i, model=m)
                    p.state.add_cost("bfl", "image", 1, usd, "bakeoff")
                    real = p._realism(img, pr, "image model comparison", "bakeoff")
                    rows.append(f"- p{i + 1} {m}: ok={real.get('ok')} blocking={real.get('blocking')}")
                    from PIL import Image as _I
                    im = _I.open(img).convert("RGB")
                    im.thumbnail((720, 1280))
                    jp = out.with_suffix(".jpg")
                    im.save(jp, quality=88)
                    files.append(str(jp))
                except Exception as e:  # noqa: BLE001
                    rows.append(f"- p{i + 1} {m}: ERROR {str(e)[:200]}")
        if files:
            tag = req.get("tag", "bakeoff-1")
            if subprocess.run(["gh", "release", "view", tag], capture_output=True).returncode == 0:
                gh("release", "upload", tag, *files, "--clobber", check=False)
            else:
                gh("release", "create", tag, *files, "--prerelease", "--title", "Image model bake-off",
                   "--notes", "same prompts, several models", check=False)
        gh("issue", "create", "--title", "Image model bake-off", "--body", "\n".join(rows), check=False)
        print("\n".join(rows))
        return 0
    if action == "claude_fix":
        # Claude's own frame check found something: targeted fix, re-review once, keep it held for Claude
        job, note = req.get("job", ""), (req.get("note") or "").strip()
        j = p.state.get_job(job) if JOB_RE.fullmatch(job) else None
        if not j or not note or j["status"] != "review":
            return 1
        d = ROOT / "build" / job
        fetch_bundle(job, d)
        fetch_bundle(job, d / "prior")
        p.decide(job, "selffix", note)
        p.produce(j["topic_id"])
        c = p.critique(job, 9)
        subprocess.run([str(ROOT / "scripts" / "open_review.sh"), job], check=True)
        print(json.dumps({k: c.get(k) for k in ("passed", "mean", "scores", "summary", "blocking")}, indent=1))
        return 0
    if action == "critic_only":
        # calibration: score an existing video with the final review, no fixes, nothing sent
        job = req.get("job", "")
        if not JOB_RE.fullmatch(job) or not p.state.get_job(job):
            return 1
        d = ROOT / "build" / job
        fetch_bundle(job, d)
        c = p.critique(job, 1)
        body = json.dumps({k: c.get(k) for k in ("passed", "mean", "scores", "summary", "blocking", "improvements",
                                                  "retention_risks")}, indent=1, ensure_ascii=False)
        gh("issue", "create", "--title", f"Calibration: final review of {job}", "--body", body[:60000], check=False)
        print(body)
        return 0
    if action == "finish":
        # resume a video whose final review/fix was stopped (e.g. by a budget limit): review, fix, then the normal
        # path - publish in auto mode if it passes, drop it if it fails, pause again if a limit stops it
        job = req.get("job", "")
        j = p.state.get_job(job) if JOB_RE.fullmatch(job) else None
        if not j or j["status"] not in ("review", "paused"):
            notify.send(p.state, f"I can't finish {job}: it is {j['status'] if j else 'unknown'}.")
            return 1
        if j["status"] == "paused":
            p.state.set_job_status(job, "review", "")
        d = ROOT / "build" / job
        if not fetch_bundle(job, d) or not (d / "final.mp4").exists():
            # the media is gone (the run that made it crashed): rebuild from the saved, already-reviewed script
            p.state.log("finish: media not saved; rebuilding pictures and voice from the saved script", "warn", job)
            p.state.set_job_status(job, "paused", "")     # produce() skips a job in 'review'; 'paused' resumes it
            p.produce(j["topic_id"])
            j = p.state.get_job(job)
            if j["status"] != "review" or j["error"]:
                if j["status"] == "paused":
                    notify.send(p.state, f"⏸ {job} is paused by a spending limit while rebuilding.")
                    return 0
                report_failure(p, job)
                return 1
        try:
            c = self_review(p, job, int(req.get("rounds", 2)))
        except Exception:
            preserve_media(p)
            raise
        if c.get("passed"):
            if auto_mode(p):
                return auto_publish(p, job)
            send_for_review(p, job)
            return 0
        if c.get("budget_stop"):
            p.state.set_job_status(job, "paused", c["summary"][:300])
            notify.send(p.state, f"⏸ {job} is still paused by a spending limit ({notify.esc(c['summary'][:200])}).")
            return 0
        reason = f"self-review: {c.get('summary', '')}"[:400]
        keep_rejected(job)
        p.decide(job, "reject", reason)
        notify.send(p.state, f"🔍 {job} failed my final check after the fix, so it was dropped: "
                             f"{notify.esc(c.get('summary', '')[:300])}")
        return 0
    if action == "self_review":
        job = req.get("job", "")
        if not JOB_RE.fullmatch(job) or not p.state.get_job(job):
            return 1
        c = self_review(p, job, int(req.get("rounds", 3)))
        subprocess.run([str(ROOT / "scripts" / "open_review.sh"), job], check=True)
        print(json.dumps({k: c.get(k) for k in ("passed", "mean", "scores", "summary", "blocking")}, indent=1))
        if not c.get("passed") and req.get("drop_if_failed"):
            p.decide(job, "reject", f"self-review: {c.get('summary', '')}"[:400])
        return 0
    if action == "unpublish":
        # owner tapped "Stop it": keep the video private and cancel its scheduled publish
        from shorts.publish.youtube import unschedule
        up = p.state.db.execute("SELECT * FROM uploads WHERE job_id=?", (req.get("job", ""),)).fetchone()
        if not up or not up["video_id"]:
            notify.send(p.state, "I can't find that upload.")
            return 1
        try:
            unschedule(up["video_id"])
        except Exception as e:  # noqa: BLE001
            alert(p, "Could not stop the video", f"{up['url']}: {e}")
            return 1
        with p.state.tx() as db:
            db.execute("UPDATE uploads SET status='held', privacy='private' WHERE job_id=?", (up["job_id"],))
        p.state.add_feedback(up["job_id"], "stop", req.get("note", ""))
        from shorts.publish import instagram as ig
        igs = ig.hold(p.state, up["job_id"])
        ig_note = {"held": " The Instagram post is cancelled too.",
                   "posted": " ⚠️ It is already on Instagram: delete it in the Instagram app (the API can't hide it)."}
        notify.send(p.state, f"⏸ Stopped. {up['url']} stays private (not scheduled).{ig_note.get(igs, '')} Reply to "
                             "this message with what was wrong if you want; I'll learn from it.")
        return 0
    if action == "ig_whoami":
        # which Instagram account the stored login posts to, its token expiry and posting quota (no secrets printed)
        from shorts.publish import instagram as ig
        try:
            msg = "Instagram login OK.\n" + json.dumps(ig.whoami(), indent=1)
        except Exception as e:  # noqa: BLE001
            msg = f"Instagram login check: {e}"
            try:      # which login keys the Worker's store holds (names only, never values)
                msg += "\nStore keys: " + ", ".join(k for k in ig.kv_keys() if not k.startswith(("media:", "oauth_", "ig_state:", "dash")))
            except Exception as e2:  # noqa: BLE001
                msg += f"\nStore keys: unavailable ({e2})"
        gh("issue", "create", "--title", "Instagram login check", "--body", msg, check=False)
        print(msg)
        return 0
    if action == "backfill_reviews":
        # one-off: load the final-review findings of earlier videos into the learning loop (shorts/carry.py)
        from shorts import carry
        import tarfile
        carry._ensure(p.state)
        done = []
        for jj in p.state.jobs()[-12:]:
            if p.state.db.execute("SELECT 1 FROM review_notes WHERE job_id=?", (jj["id"],)).fetchone():
                continue
            with tempfile.TemporaryDirectory() as tmp:
                hist = None
                for tag in (f"rejected-{jj['id']}", f"review-{jj['id']}"):
                    subprocess.run(["gh", "release", "download", tag, "-p", "critique.json", "-p", "media.tgz",
                                    "-D", tmp, "--clobber"], capture_output=True)
                    cj, tgz = Path(tmp) / "critique.json", Path(tmp) / "media.tgz"
                    if cj.exists():
                        hist = json.loads(cj.read_text())
                    elif tgz.exists():
                        with tarfile.open(tgz) as tf:
                            m = next((x for x in tf.getmembers() if x.name.endswith("critique.json")), None)
                            hist = json.loads(tf.extractfile(m).read()) if m else None
                    if hist:
                        break
                for c in hist or []:
                    carry.record_review(p.state, jj["id"], c)
                if hist:
                    done.append(jj["id"])
        print(json.dumps({"backfilled": done}))
        return 0
    if action == "ig_due":
        # same as the instagram workflow: post what is due, preparing early and publishing at the exact minute
        from shorts.publish import instagram as ig
        print(json.dumps(ig.publish_due(p.state), default=str))
        return 0
    if action == "ig_manual":
        # the owner posted this Reel by hand (Telegram "I posted it" button): never auto-post it later
        from shorts.publish import instagram as ig
        ig.manual(p.state, req.get("job", ""), req.get("permalink") or None)
        notify.send(p.state, f"✅ Noted: {req.get('job')} was posted on Instagram by hand. It won't be posted again.",
                    silent=True)
        return 0
    if action == "ig_hand":
        # Instagram API is down: send the owner the Reel + caption to post by hand now
        from shorts.publish import instagram as ig
        ig.send_for_hand_posting(p.state, req.get("job", ""), req.get("why") or "Instagram API unavailable")
        return 0
    if action == "ig_queue":
        # queue an already-uploaded YouTube video for Instagram at a given time (default: its YouTube publish time)
        from shorts.publish import instagram as ig
        job = req.get("job", "")
        up = p.state.db.execute("SELECT status, publish_at FROM uploads WHERE job_id=?", (job,)).fetchone()
        if not up or up["status"] == "held":
            notify.send(p.state, f"I can't queue {job} for Instagram: it is not a published YouTube video.")
            return 1
        ig.queue(p.state, job, req.get("at") or up["publish_at"])
        print(json.dumps(dict(p.state.db.execute("SELECT * FROM ig_posts WHERE job_id=?", (job,)).fetchone())))
        return 0
    if action == "ig_post":
        # post one already-published YouTube video to Instagram NOW (owner-approved test or catch-up)
        from shorts.publish import instagram as ig
        job = req.get("job", "")
        up = p.state.db.execute("SELECT status FROM uploads WHERE job_id=?", (job,)).fetchone()
        if not up or up["status"] == "held":
            notify.send(p.state, f"I can't post {job} to Instagram: it is not a published YouTube video.")
            return 1
        ig._ensure(p.state)
        with p.state.tx() as db:
            db.execute("INSERT OR IGNORE INTO ig_posts(job_id, status, publish_at, at) VALUES (?,?,?,?)",
                       (job, "pending", time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()), time.time()))
        try:
            res = ig.post(p.state, job)
        except Exception as e:  # noqa: BLE001
            alert(p, "Instagram test post failed", f"{job}: {e}")
            return 1
        notify.send(p.state, f"📸 Posted to Instagram: {res.get('permalink')}")
        gh("issue", "create", "--title", "Instagram post", "--body", json.dumps(res), check=False)
        return 0
    if action == "send_review":
        job = req.get("job", "")
        if not JOB_RE.fullmatch(job) or not p.state.get_job(job) or p.state.get_job(job)["status"] != "review":
            notify.send(p.state, f"I can't send {job}: it is not waiting for review.")
            return 1
        d = ROOT / "build" / job
        fetch_bundle(job, d)
        send_for_review(p, job)
        if req.get("note"):
            notify.send(p.state, req["note"], silent=True)
        return 0
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
    if action == "yt_login":
        notify.send(p.state, "🔑 Connect the Secret Smart Stuff channel (link works once, 30 minutes):\n" + _login_link(p))
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
        from shorts.publish.youtube import access_token
        try:
            tok = access_token(check_channel=False)
            r = requests.get("https://www.googleapis.com/youtube/v3/channels", params={"part": "snippet,status", "mine": "true"},
                             headers={"Authorization": f"Bearer {tok}"}, timeout=30).json()
            items = r.get("items") or []
            msg = "\n".join(f"- Channel: {c['snippet'].get('title')} | handle: {c['snippet'].get('customUrl')} | id: {c['id']} | "
                            f"madeForKids: {c.get('status', {}).get('madeForKids')}" for c in items) or f"- No channel found: {str(r)[:300]}"
            msg = "Login OK.\n" + msg
        except Exception as e:  # noqa: BLE001
            msg = f"Login check: {e}"
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
            notify.send(p.state, "🤝 Connected. New Secret Smart Stuff videos will arrive here for your review.\nSend /help to see what I can do.")
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
