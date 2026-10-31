"""31 Oct 2026: ElevenLabs credits ran out mid-video. The owner is warned early, and a video is not started
when credits can't cover it."""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from shorts.providers import tts  # noqa: E402
from shorts.state import State  # noqa: E402


class R:
    def __init__(self, used, limit=131000, code=200):
        self.status_code, self._j = code, {"character_count": used, "character_limit": limit,
                                           "next_character_count_reset_unix": 1795000000}

    def json(self):
        return self._j


def test_low_credits_warn_once_a_day_and_block_below_minimum(tmp_path, monkeypatch):
    st, sent = State(tmp_path / "s.db"), []
    monkeypatch.setattr("shorts.notify.send", lambda state, text, *a, **k: sent.append(text))
    monkeypatch.setattr(tts.requests, "get", lambda *a, **k: R(used=131000 - 132))
    c = tts.credit_check(st, "k")
    assert c["left"] == 132 and not c["ok"] and "on hold" in sent[0]
    tts.credit_check(st, "k")
    assert len(sent) == 1                                          # once a day
    monkeypatch.setattr(tts.requests, "get", lambda *a, **k: R(used=10000))
    assert tts.credit_check(st, "k")["ok"]                          # plenty left: no block
    monkeypatch.setattr(tts.requests, "get", lambda *a, **k: R(used=0, code=401))
    assert tts.credit_check(st, "k") == {"ok": True, "unknown": True}   # key can't read it: never block
