"""Offline tests for the automation layer: experiments, publish times, verification, owner fixes
that reuse media, revenue entry, dashboard build. No network, no GitHub, no Telegram."""
from __future__ import annotations

import datetime as dt
import json
import os
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from shorts import experiments as X  # noqa: E402
from shorts.publish.verify import classify  # noqa: E402
from shorts.state import State  # noqa: E402


def test_publish_time_rotation_and_next_time(tmp_path):
    st = State(tmp_path / "s.db")
    st.upsert_topic("t", "T")
    arms = []
    for i in range(6):
        st.start_job(f"t-v{i}", "t")
        arms.append(X.assign(st, f"t-v{i}")["exp-001-publish-time"])
    assert sorted(arms) == sorted(["a_1900_ist", "b_2230_ist", "c_0730_ist"] * 2)   # balanced
    assert X.assign(st, "t-v0")["exp-001-publish-time"] == arms[0]                    # stable
    now = dt.datetime(2026, 10, 25, 13, 10, tzinfo=dt.timezone.utc)
    assert X.next_publish_time(st, "13:30", 30, now) == "2026-10-26T13:30:00Z"       # too close -> tomorrow
    assert X.next_publish_time(st, "13:30", 15, now) == "2026-10-25T13:30:00Z"
    st.record_upload("t-v0", "h", "uploaded", video_id="x", url="u", publish_at="2026-10-26T13:30:00Z")
    assert X.next_publish_time(st, "13:30", 30, now) == "2026-10-27T13:30:00Z"       # slot taken


def test_verify_classify():
    future = "2099-01-01T00:00:00Z"
    past = "2020-01-01T00:00:00Z"
    now = dt.datetime(2026, 10, 25, tzinfo=dt.timezone.utc).timestamp()
    assert classify({}, None, now)[0] == "problem"
    assert classify({"status": {"uploadStatus": "processed", "privacyStatus": "private", "publishAt": future}}, future, now)[0] == "scheduled"
    assert classify({"status": {"uploadStatus": "processed", "privacyStatus": "public"}}, past, now)[0] == "live"
    s, why = classify({"status": {"uploadStatus": "processed", "privacyStatus": "private"}}, past, now)
    assert s == "problem" and "audit" in why
    assert classify({"status": {"uploadStatus": "rejected", "rejectionReason": "duplicate"}}, past, now)[0] == "problem"


def run_cmd(req: dict, tmp_path: Path) -> int:
    f = tmp_path / "req.json"
    f.write_text(json.dumps(req))
    env = {**os.environ, "SHORTS_MODE": "dry_run", "SHORTS_NO_GITHUB": "1", "TELEGRAM_BOT_TOKEN": ""}
    return subprocess.run([sys.executable, str(ROOT / "scripts" / "run_command.py"), str(f)], cwd=ROOT, env=env,
                          capture_output=True, text=True, timeout=900).returncode


@pytest.mark.slow
def test_produce_fix_reuses_media_then_approve(tmp_path):
    db = ROOT / "state" / "dryrun.db"
    db.unlink(missing_ok=True)
    assert run_cmd({"action": "produce"}, tmp_path) == 0
    st = State(db)
    job = st.jobs("review")[0]["id"]
    assert st.db.execute("SELECT COUNT(*) n FROM features WHERE job_id=?", (job,)).fetchone()["n"] == 1
    assert st.db.execute("SELECT COUNT(*) n FROM assignments WHERE job_id=?", (job,)).fetchone()["n"] == 1
    # a second produce while one waits for review must not make another video
    assert run_cmd({"action": "produce"}, tmp_path) == 0
    assert len(State(db).jobs("review")) == 1
    d = ROOT / "build" / job
    before = {p.name: p.stat().st_mtime for p in d.glob("img*.png")}
    assert run_cmd({"action": "fix", "job": job, "note": "make the music a bit louder"}, tmp_path) == 0
    st = State(db)
    assert st.get_job(job)["status"] == "review"
    # dry-run fake fix returns the same script, so every picture and the voice are reused
    ev = [r["message"] for r in st.db.execute("SELECT message FROM events WHERE job_id=?", (job,))]
    assert any("voice unchanged" in m for m in ev)
    after = {p.name: p.stat().st_mtime for p in d.glob("img*.png")}
    assert before.keys() == after.keys()
    assert st.db.execute("SELECT COUNT(*) n FROM feedback WHERE decision='fix'").fetchone()["n"] == 1
    assert run_cmd({"action": "revenue", "period": "2026-11", "usd": 3.5}, tmp_path) == 0
    assert run_cmd({"action": "approve", "job": job}, tmp_path) == 0          # dry run: approve, no upload
    assert State(db).get_job(job)["status"] == "approved"
    assert run_cmd({"action": "dashboard"}, tmp_path) == 0
    html = (ROOT / "build" / "dashboard.html").read_text()
    assert "Studio" in html and job in html


@pytest.mark.slow
def test_self_review_fixes_then_passes(tmp_path, monkeypatch):
    """The final review rejects round 1 (a malformed picture), the targeted fix regenerates only that
    picture, round 2 passes. Nothing reaches the owner before a pass."""
    monkeypatch.setenv("SHORTS_MODE", "dry_run")
    monkeypatch.setenv("SHORTS_NO_GITHUB", "1")
    monkeypatch.setenv("TELEGRAM_BOT_TOKEN", "")
    db = ROOT / "state" / "dryrun.db"
    db.unlink(missing_ok=True)
    import importlib.util
    spec = importlib.util.spec_from_file_location("rc", ROOT / "scripts" / "run_command.py")
    rc = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(rc)
    from shorts.config import load
    from shorts.pipeline import Pipeline
    p = Pipeline(load())
    tid = p.discover(3)[0] if p.state.topics("shortlisted") == [] else p.state.topics("shortlisted")[0]["id"]
    tid = tid["id"] if isinstance(tid, dict) else tid
    job = p.produce(tid)
    assert p.state.get_job(job)["status"] == "review"
    calls = {"n": 0}
    real_ask = p.llm.ask

    def ask(prompt, **kw):
        if "TASK: critic" in prompt:
            calls["n"] += 1
            if calls["n"] == 1:
                from shorts.providers.llm import LLMResult
                r = real_ask(prompt, **kw)
                r.data = {**r.data, "blocking": [{"beat": "b2", "problem": "malformed object", "fix": "new photo"}],
                          "verdict": "fix"}
                return r
        return real_ask(prompt, **kw)
    p.llm.ask = ask
    d = ROOT / "build" / job
    (d / "critique.json").unlink(missing_ok=True)     # build/ survives between local test runs
    c = rc.self_review(p, job)
    assert c["passed"] and calls["n"] == 2
    hist = json.loads((d / "critique.json").read_text())
    assert [h["passed"] for h in hist] == [False, True]
    assert "### Self-review" in (d / "review.md").read_text()
    assert State(db).db.execute("SELECT COUNT(*) n FROM feedback WHERE decision='selffix'").fetchone()["n"] == 1
    assert State(db).db.execute("SELECT COUNT(*) n FROM feedback WHERE decision='fix'").fetchone()["n"] == 0
    # auto mode: a passing video is approved and published at its experiment slot, with features recorded
    calls2 = {}
    def fake_publish(j, publish_at=None):
        calls2["when"] = publish_at
        p.state.set_job_status(j, "published")
        return {"url": "https://youtube.com/shorts/x"}
    p.publish = fake_publish
    assert rc.auto_publish(p, job) == 0
    assert calls2["when"] and p.state.get_job(job)["status"] == "published"
    feats = json.loads(p.state.db.execute("SELECT data FROM features WHERE job_id=?", (job,)).fetchone()["data"])
    assert feats["beats"] and feats["self_review"]["rounds"] == 2 and feats["publish_at"] == calls2["when"]


def test_postmortem_writes_learnings(tmp_path, monkeypatch):
    """A public video with 48 h metrics + retention gets one analysis, a Telegram note and a LEARNINGS.md entry."""
    monkeypatch.setenv("SHORTS_MODE", "dry_run")
    monkeypatch.setenv("TELEGRAM_BOT_TOKEN", "")
    from shorts.config import load
    from shorts.pipeline import Pipeline
    from shorts import insights
    p = Pipeline(load())
    p.state = State(tmp_path / "s.db")
    st = p.state
    st.upsert_topic("t1", "Why do bus shelters have dots?")
    st.start_job("t1-v1", "t1")
    st.record_upload("t1-v1", "h1", "uploaded", video_id="VID1", url="u", publish_at="2026-10-20T13:30:00Z")
    st.db.execute("UPDATE uploads SET status='live'"); st.db.commit()
    st.set_features("t1-v1", {"seconds": 36, "beats": [{"id": "b1", "start": 0, "words": "Why?"},
                                                        {"id": "b2", "start": 4, "words": "Because."}]})
    st.add_metrics("VID1", {"views": 500, "averageViewPercentage": 80, "likes": 9, "shares": 2}, 50)
    with st.tx() as db:
        db.execute("INSERT INTO video_detail(video_id, kind, data, at) VALUES (?,?,?,?)",
                   ("VID1", "retention", json.dumps([{"elapsedVideoTimeRatio": i / 100, "audienceWatchRatio": 1 - i / 200}
                                                     for i in range(100)]), 0))
    monkeypatch.setattr(p.cfg, "root", tmp_path)
    r = insights.postmortems(p)
    assert r["analysed"] == [("VID1", "48h")]
    assert insights.postmortems(p)["analysed"] == []          # only once per age
    md = (tmp_path / "data" / "LEARNINGS.md").read_text()
    assert "t1-v1 (48h)" in md and "cut repeats" in md
