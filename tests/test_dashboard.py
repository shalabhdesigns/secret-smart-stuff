"""Dashboard (3 Nov 2026): every dollar lands in exactly one bucket, labels say where numbers come from, and
resource statuses follow the stated thresholds."""
from __future__ import annotations

import json
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from shorts import dashboard, usage  # noqa: E402
from shorts.state import State  # noqa: E402


class Cfg:
    pipeline = {}
    channel = {}


def _state(tmp_path):
    st = State(tmp_path / "s.db")
    st.set_setting("manual_json", json.dumps({"subscriptions": {"claude": {"usd_month": 100, "share_pct": 20}}}))
    for t in ("a", "b", "c"):
        st.upsert_topic(t, f"Why {t}?")
        st.start_job(f"{t}-v1", t)
    st.record_upload("a-v1", "h1", "uploaded", video_id="YA", url="https://youtube.com/shorts/YA",
                     publish_at=time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()))
    st.set_job_status("b-v1", "rejected", "final review")
    st.add_cost("anthropic", "script", 1000, 0.40, "a-v1", estimated=False, meta={"input_tokens": 900, "output_tokens": 100})
    st.add_cost("bfl", "image", 1, 0.03, "a-v1")
    st.add_cost("bfl", "image", 1, 0.05, "a-v1", meta={"source": "api", "credits": 5})
    st.add_cost("elevenlabs", "tts_chars", 500, 0.09, "a-v1")
    st.add_cost("anthropic", "script", 1, 0.50, "b-v1", estimated=False)       # dropped attempt
    st.add_cost("anthropic", "ideas", 1, 0.10, None, estimated=False)          # shared work
    return st


def test_costs_reconcile_and_are_labelled(tmp_path, monkeypatch):
    monkeypatch.setattr(usage, "manual", lambda state: json.loads(state.get_setting("manual_json")))
    d = dashboard.collect(_state(tmp_path), Cfg())
    m = next(iter(d["months"].values()))
    assert round(m["direct"] + m["overhead"] + m["dropped"], 2) == 1.17            # every dollar once
    assert m["subscriptions"][0]["usd"] == 20.0                                   # $100 x 20% for this channel
    v = d["videos"][0]
    bp = v["cost"]["by_provider"]
    assert bp["anthropic"]["labels"] == ["calculated"] and bp["anthropic"]["tokens"] == 1000
    assert bp["bfl"]["labels"] == ["estimated", "measured"]                       # one list price, one reported
    assert bp["elevenlabs"]["labels"] == ["estimated"]                            # no plan price known yet
    assert v["cost"]["overhead_share"] == round(0.10 + 0.50 + 20.0, 3)           # 1 published video takes it all
    assert v["revenue"] is None and v["roi_pct"] is None                          # never invented


def test_status_thresholds():
    assert usage.status_of(50, 30) == "Healthy"
    assert usage.status_of(20, None) == "Running low" and usage.status_of(None, 5) == "Running low"
    assert usage.status_of(8, None) == "Critical" and usage.status_of(None, 2) == "Critical"
    assert usage.status_of(80, 80, expired=True) == "Expired"


def test_template_has_data_slot_and_labels():
    tpl = (ROOT / "shorts" / "dashboard_template.html").read_text()
    assert "/*__DATA__*/null" in tpl
    for lbl in ("measured", "calculated", "allocated", "estimated", "manual", "unavailable"):
        assert f"{lbl}:" in tpl
