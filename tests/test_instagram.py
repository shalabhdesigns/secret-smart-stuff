"""Offline tests for Instagram posting: caption rules, queue/stop, timing, crash-safe posting, insights.
Instagram, Cloudflare and GitHub are faked; nothing leaves the machine."""
from __future__ import annotations

import json
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from shorts.publish import instagram as ig  # noqa: E402
from shorts.state import State  # noqa: E402

META = {"title": "Why do bus shelters have tiny dots on the glass?",
        "description": ("Some bus shelter glass has small printed dots. They help birds see the glass.\n\n"
                        "Sources:\n- https://www.fws.gov/story/x\n- https://abcbirds.org/a.pdf\n- https://www.fws.gov/y\n\n"
                        "Visuals are AI-generated illustrations; narration is an AI voice. Facts are checked.\n\n"
                        "#designfacts #busstop #everydayobjects #design #birds #glass")}


def test_caption_rules():
    c = ig.caption(META)
    assert c.startswith("Why do bus shelters")
    assert "Sources: fws.gov, abcbirds.org" in c                 # domains, no duplicates, no long URLs
    assert "AI-generated" in c                                    # disclosure kept
    tags = [w for w in c.split() if w.startswith("#")]
    assert len(tags) == 5 and "#secretsmartstuff" in tags         # Instagram's 5-hashtag limit
    assert len(c) <= 2200


class FakeIG:
    """Fake graph.instagram.com: containers finish after one poll; counts publishes."""
    def __init__(self):
        self.published, self.containers, self.polls = 0, {}, 0

    def __call__(self, method, path, tok, **kw):
        if path.endswith("/media") and method == "POST":
            assert kw["media_type"] == "REELS" and kw["video_url"].startswith("https://w.example/m/")
            cid = f"C{len(self.containers) + 1}"
            self.containers[cid] = "IN_PROGRESS"
            return {"id": cid}
        if path in self.containers and method == "GET":
            self.polls += 1
            st = self.containers[path]
            if st == "IN_PROGRESS":
                self.containers[path] = "FINISHED"
            return {"status_code": st}
        if path.endswith("/media_publish"):
            self.published += 1
            self.containers[kw["creation_id"]] = "PUBLISHED"
            return {"id": f"M{self.published}"}
        if path.endswith("/insights"):
            if "ig_reels_video_view_total_time" in kw["metric"]:
                raise RuntimeError("Instagram insights: metric ig_reels_video_view_total_time is not supported")
            return {"data": [{"name": "views", "values": [{"value": 321}]}, {"name": "likes", "values": [{"value": 12}]}]}
        if path.startswith("M"):
            return {"permalink": f"https://www.instagram.com/reel/{path}/", "timestamp": "2026-10-01T17:01:00+0000"}
        raise AssertionError((method, path))


def _setup(tmp_path, monkeypatch):
    st = State(tmp_path / "s.db")
    st.set_setting("worker_url", "https://w.example")
    st.upsert_topic("t", "T")
    for j in ("t-v1", "t-v2", "t-v3"):
        st.start_job(j, "t")
        st.record_upload(j, "h" + j, "scheduled", video_id="Y" + j, url="u", publish_at="2026-10-28T17:00:00Z")
    fake = FakeIG()
    puts = []
    monkeypatch.setattr(ig, "enabled", lambda: True)
    monkeypatch.setattr(ig, "token", lambda refresh=True: ("TOK", {"user_id": "1789", "username": "secretsmartstuff"}))
    monkeypatch.setattr(ig, "_api", fake)
    monkeypatch.setattr(ig, "_kv_put", lambda k, d, ttl=None: puts.append((k, len(d), ttl)))
    mp4 = tmp_path / "final.mp4"
    mp4.write_bytes(b"\0" * 1000)
    monkeypatch.setattr(ig, "_fetch", lambda job, into: (mp4, META))
    monkeypatch.setattr(ig.time, "sleep", lambda s: None)
    monkeypatch.setattr(ig.notify, "send", lambda *a, **k: None)
    return st, fake, puts


def test_queue_waits_for_slot_then_posts_once(tmp_path, monkeypatch):
    st, fake, puts = _setup(tmp_path, monkeypatch)
    future = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(time.time() + 3600))
    ig.queue(st, "t-v1", future)
    assert ig.publish_due(st)["posted"] == []                       # not yet
    with st.tx() as db:
        db.execute("UPDATE ig_posts SET publish_at='2020-01-01T00:00:00Z'")
    res = ig.publish_due(st)["posted"]
    assert res[0]["permalink"] == "https://www.instagram.com/reel/M1/"
    assert puts and puts[0][0].startswith("media:") and puts[0][2] == 6 * 3600   # temporary, expires
    assert ig.publish_due(st)["posted"] == [] and fake.published == 1            # never twice


def test_stop_cancels_pending_and_reports_posted(tmp_path, monkeypatch):
    st, fake, _ = _setup(tmp_path, monkeypatch)
    ig.queue(st, "t-v1", "2020-01-01T00:00:00Z")
    ig.queue(st, "t-v2", "2020-01-01T00:00:00Z")
    assert ig.hold(st, "t-v1") == "held"
    with st.tx() as db:                                            # owner stopped t-v2 on YouTube only
        db.execute("UPDATE uploads SET status='held' WHERE job_id='t-v2'")
    assert ig.publish_due(st)["posted"] == [] and fake.published == 0
    assert st.db.execute("SELECT status FROM ig_posts WHERE job_id='t-v2'").fetchone()["status"] == "held"
    ig.queue(st, "t-v3", "2020-01-01T00:00:00Z")
    ig.publish_due(st)
    assert ig.hold(st, "t-v3") == "posted"                         # too late: owner is told to delete in the app
    assert ig.hold(st, "nope") == "none"


def test_crash_after_publish_is_not_repeated(tmp_path, monkeypatch):
    st, fake, _ = _setup(tmp_path, monkeypatch)
    ig.queue(st, "t-v1", "2020-01-01T00:00:00Z")
    real = fake.__call__

    def dies_after_publish(method, path, tok, **kw):
        out = real(method, path, tok, **kw)
        if path.endswith("/media_publish"):
            raise RuntimeError("runner died")
        return out
    monkeypatch.setattr(ig, "_api", dies_after_publish)
    assert ig.publish_due(st)["problems"]
    monkeypatch.setattr(ig, "_api", lambda m, p, t, **kw: ({"data": [{"id": "M1"}]} if p.endswith("1789/media") and m == "GET"
                                                           else real(m, p, t, **kw)))
    res = ig.publish_due(st)["posted"]
    assert fake.published == 1 and res[0]["media_id"] == "M1"


def test_insights_drop_unsupported_metric(tmp_path, monkeypatch):
    st, fake, _ = _setup(tmp_path, monkeypatch)
    ig.queue(st, "t-v1", "2020-01-01T00:00:00Z")
    ig.publish_due(st)
    assert ig.snapshot(st) == {"reels": 1}
    d = json.loads(st.db.execute("SELECT data FROM ig_metrics").fetchone()["data"])
    assert d["views"] == 321 and "error" not in d
    assert ig.near(st, "t-v1", 0)["likes"] == 12
