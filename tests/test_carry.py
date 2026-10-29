"""The learning loop: every new video gets what earlier videos taught (audience results, our own final review,
the owner's feedback), and records which lessons it applied so later post-mortems can judge them."""
from __future__ import annotations

import json
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from shorts import carry  # noqa: E402
from shorts.state import State  # noqa: E402


def test_empty_channel_adds_nothing(tmp_path):
    st = State(tmp_path / "s.db")
    text, applied = carry.for_script(st)
    assert text == "" and applied == []
    assert carry.for_ideas(st) == ""


def test_all_sources_reach_the_next_script(tmp_path):
    st = State(tmp_path / "s.db")
    st.upsert_topic("t", "Why do bus shelters have dots?")
    st.start_job("t-v1", "t")
    # our own final review found problems on an earlier video
    carry.record_review(st, "t-v1", {"round": 1, "blocking": [{"beat": "b4", "problem": "hands with six fingers", "fix": "no hands"}],
                                     "improvements": [{"beat": "b7", "problem": "dots too faint", "fix": "bigger dots"}],
                                     "hard_flags": ["BLOCKING img3: warped bench"]})
    # the audience: a post-mortem with a lesson and a win
    from shorts import insights
    insights._ensure(st)
    with st.tx() as db:
        db.execute("INSERT INTO video_reviews(video_id, tag, job_id, data, at) VALUES (?,?,?,?,?)",
                   ("V1", "48h", "t-v1", json.dumps({"verdict": "above", "what_worked": ["bird reveal at 7 s"],
                                                      "lessons": [{"area": "hook", "lesson": "name the object in the first line",
                                                                   "confidence": "hypothesis"}],
                                                      "topic_signal": "double_down"}), time.time()))
    # the owner
    st.add_feedback("t-v1", "fix", "the third picture should show the tabs")
    st.set_setting("lessons_for_writer", "- keep it under 36 s")
    text, applied = carry.for_script(st)
    for needle in ("keep it under 36 s", "bird reveal at 7 s", "name the object in the first line",
                   "hands with six fingers", "warped bench", "dots too faint", "third picture should show the tabs"):
        assert needle in text, needle
    assert text.index("[blocking] hands") < text.index("dots too faint")          # blocking problems first
    assert "weekly:lessons_for_writer" in applied and any(a.startswith("pm:t-v1:48h") for a in applied)
    assert any(a.startswith("review:t-v1") for a in applied) and any(a.startswith("owner:fix") for a in applied)
    assert len(text) <= carry.MAX_CHARS
    ideas = carry.for_ideas(st)
    assert "double down: Why do bus shelters have dots?" in ideas
