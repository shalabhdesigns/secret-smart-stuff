"""Reliability tests: resume after a crash, duplicate prevention, budget stop,
upload idempotency, QA hard gates. All offline (dry-run providers)."""
import shutil
import time
from pathlib import Path

import pytest

from shorts.budget import Budget, BudgetExceeded, Limits
from shorts.config import load
from shorts.pipeline import Pipeline, similarity
from shorts.publish import youtube as yt
from shorts.qa.media import check_video
from shorts.state import State

ROOT = Path(__file__).resolve().parents[1]


@pytest.fixture()
def pipe(tmp_path, monkeypatch):
    cfg = load(mode="dry_run")
    cfg.pipeline["paths"] = {"state_db": str(tmp_path / "s.db"), "build_dir": str(tmp_path / "build")}
    cfg.root = Path("/")  # paths above are absolute
    return Pipeline(cfg)


def test_duplicate_ideas_are_skipped(pipe):
    first = pipe.discover()
    second = pipe.discover()          # the fake returns the same ideas again
    assert len(first) == 2 and second == []
    assert similarity("Why do jeans have a tiny pocket?", "Why do jeans have that tiny pocket") > 0.5
    assert similarity("Why do jeans have a tiny pocket?", "Why are manhole covers round?") < 0.2


def test_resume_after_crash_does_not_repeat_finished_stages(pipe, monkeypatch):
    pipe.discover()
    tid = pipe.next_topic()["id"]
    calls = {"tts": 0}
    real_speak = pipe.tts.speak

    def counting_speak(*a, **k):
        calls["tts"] += 1
        return real_speak(*a, **k)
    monkeypatch.setattr(pipe.tts, "speak", counting_speak)

    def boom(*a, **k):
        raise RuntimeError("simulated crash during visuals")
    monkeypatch.setattr(pipe, "_stage_visuals", boom)
    job = pipe.produce(tid)
    j = pipe.state.get_job(job)
    assert j["status"] == "failed" and j["stage"] == "voice" and "simulated crash" in j["error"]

    monkeypatch.undo()                          # "fix the outage", keep counting TTS calls
    monkeypatch.setattr(pipe.tts, "speak", counting_speak)
    job = pipe.produce(tid)
    j = pipe.state.get_job(job)
    assert j["status"] == "review" and j["stage"] == "package"
    assert calls["tts"] == 1                    # voice was NOT generated (or paid for) twice


def test_job_goes_to_human_review_after_max_attempts(pipe, monkeypatch):
    pipe.discover()
    tid = pipe.next_topic()["id"]
    monkeypatch.setattr(pipe, "_stage_script", lambda *a: (_ for _ in ()).throw(RuntimeError("bad")))
    for _ in range(3):
        job = pipe.produce(tid)
    assert pipe.state.get_job(job)["status"] == "review"


def test_budget_blocks_before_spending(tmp_path):
    st = State(tmp_path / "b.db")
    b = Budget(st, Limits(daily_usd=1.0, monthly_usd=10.0, per_video_usd=0.5))
    st.add_cost("x", "y", 1, 0.45, job_id="j1")
    b.authorize(0.04, "ok", "j1")               # 0.49 <= 0.5
    with pytest.raises(BudgetExceeded):
        b.authorize(0.10, "too much for this video", "j1")
    st.add_cost("x", "y", 1, 0.9, job_id="j2")
    with pytest.raises(BudgetExceeded):
        b.authorize(0.2, "over daily", "j3")


def test_upload_is_idempotent(tmp_path, monkeypatch):
    st = State(tmp_path / "u.db")
    f = tmp_path / "v.mp4"
    f.write_bytes(b"x" * 1000)
    digest = yt.sha256(f)
    meta = yt.VideoMeta("t", "d", [])
    # an earlier run already finished this exact file -> return the record, no network
    st.record_upload("jobA", digest, "uploaded", video_id="abc", url="https://youtube.com/shorts/abc")
    assert yt.upload(st, "jobB", f, meta)["video_id"] == "abc"
    # an earlier run started but never confirmed -> refuse (human must check Studio)
    st2 = State(tmp_path / "u2.db")
    st2.record_upload("jobA", digest, "started")
    with pytest.raises(yt.UploadBlocked):
        yt.upload(st2, "jobA", f, meta)


def test_missing_secrets_fail_clearly(tmp_path, monkeypatch):
    for k in ("YT_CLIENT_ID", "YT_CLIENT_SECRET", "YT_REFRESH_TOKEN"):
        monkeypatch.delenv(k, raising=False)
    with pytest.raises(yt.UploadBlocked, match="missing secrets"):
        yt.access_token()


def test_qa_rejects_wrong_resolution(tmp_path):
    import subprocess
    bad = tmp_path / "bad.mp4"
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-f", "lavfi", "-i", "testsrc=size=1280x720:rate=30",
                    "-f", "lavfi", "-i", "sine=frequency=300", "-t", "10", "-c:v", "libx264", "-c:a", "aac",
                    "-shortest", str(bad)], check=True)
    rep = check_video(bad)
    assert not rep.passed
    assert any(c.name == "resolution" and not c.ok for c in rep.checks)


def test_publish_refuses_dry_run_and_unapproved(pipe):
    pipe.discover()
    job = pipe.produce(pipe.next_topic()["id"])
    with pytest.raises(RuntimeError, match="not approved"):
        pipe.publish(job)
    pipe.decide(job, "approve")
    with pytest.raises(RuntimeError, match="dry-run"):
        pipe.publish(job)


def test_daily_budget_is_per_ist_day():
    """30 Oct 2026: a rolling 24 h counted yesterday's late run against today's video and stopped its fix."""
    from shorts.budget import _ist_day_start
    import calendar
    now = calendar.timegm((2026, 10, 30, 0, 45, 0))            # 06:15 IST on 30 Oct
    assert _ist_day_start(now) == calendar.timegm((2026, 10, 29, 18, 30, 0))   # 00:00 IST on 30 Oct
    late = calendar.timegm((2026, 10, 29, 20, 0, 0))           # 01:30 IST on 30 Oct
    assert _ist_day_start(late) == _ist_day_start(now)


def test_per_video_override_only_for_that_video(tmp_path):
    from shorts.budget import Budget, Limits
    from shorts.state import State
    st = State(tmp_path / "s.db")
    b = Budget(st, Limits(6.0, 50.0, 2.0, {"knife-v1": 3.2}))
    assert abs(b.remaining("knife-v1")["video"] - 3.2) < 1e-9 and abs(b.remaining("other-v1")["video"] - 2.0) < 1e-9


def test_news_videos_publish_asap_at_least_an_hour_apart(tmp_path):
    import importlib.util
    spec = importlib.util.spec_from_file_location("rc", ROOT / "scripts" / "run_command.py")
    rc = importlib.util.module_from_spec(spec); spec.loader.exec_module(rc)
    from shorts.state import State
    import calendar
    st = State(tmp_path / "s.db")
    t0 = calendar.timegm((2026, 11, 2, 16, 0, 0))
    a = rc.news_publish_time(st, now=t0)                       # first: as soon as ready (+20 min margin)
    b = rc.news_publish_time(st, now=t0 + 600)                 # ready 10 min later: waits for the 1-hour gap
    c = rc.news_publish_time(st, now=t0 + 3 * 3600)            # ready much later: goes at once
    assert a == "2026-11-02T16:20:00Z" and b == "2026-11-02T17:20:00Z" and c == "2026-11-02T19:20:00Z"


def test_series_queues_the_next_video_with_the_rest(tmp_path, monkeypatch, capsys):
    import importlib.util
    spec = importlib.util.spec_from_file_location("rc2", ROOT / "scripts" / "run_command.py")
    rc = importlib.util.module_from_spec(spec); spec.loader.exec_module(rc)
    monkeypatch.setenv("SHORTS_NO_GITHUB", "1")
    rc.chain_next(None, {"action": "produce", "topic": "a", "then": [{"topic": "b"}, {"topic": "c"}]})
    out = capsys.readouterr().out
    assert '"topic": "b"' in out and '"then": [{"topic": "c"}]' in out
    rc.chain_next(None, {"action": "produce", "topic": "c", "then": []})       # last one: nothing queued
    assert capsys.readouterr().out == ""


def test_series_resume_keeps_the_rest_of_the_chain(tmp_path, monkeypatch, capsys):
    import importlib.util
    spec = importlib.util.spec_from_file_location("rc3", ROOT / "scripts" / "run_command.py")
    rc = importlib.util.module_from_spec(spec); spec.loader.exec_module(rc)
    monkeypatch.setenv("SHORTS_NO_GITHUB", "1")
    h = {"action": "produce", "topic": "v5", "then": [{"topic": "v6"}, {"topic": "v7"}]}
    rc.chain_next(None, {"then": [{k: v for k, v in h.items() if k != "then"}] + list(h.get("then") or [])})
    out = capsys.readouterr().out
    assert '"topic": "v5"' in out and '"then": [{"topic": "v6"}, {"topic": "v7"}]' in out


def test_owner_raised_limits_from_telegram(tmp_path):
    from shorts.budget import Budget, Limits
    from shorts.state import State
    import time as _t
    st = State(tmp_path / "s.db")
    b = Budget(st, Limits(6.0, 50.0, 2.0, {}))
    st.set_setting("video_extra:v1", "2.0")
    st.set_setting("day_extra:" + _t.strftime("%Y-%m-%d", _t.gmtime(_t.time() + 5.5 * 3600)), "1.5")
    st.set_setting("month_extra:" + _t.strftime("%Y-%m", _t.gmtime()), "3")
    r = b.remaining("v1")
    assert abs(r["video"] - 4.0) < 1e-9 and abs(r["day"] - 7.5) < 1e-9 and abs(r["month"] - 53.0) < 1e-9
    assert abs(b.remaining("v2")["video"] - 2.0) < 1e-9                      # only that video
