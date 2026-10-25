#!/usr/bin/env python3
"""Last-resort alert when a workflow step crashes (so failures never go unnoticed)."""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
try:
    from shorts import notify
    from shorts.config import load
    from shorts.state import State
    cfg = load()
    st = State(cfg.path("state_db"))
    notify.send(st, f"⚠️ {' '.join(sys.argv[1:])}. Claude can look at it; nothing was published.")
except Exception as e:  # noqa: BLE001
    print("notify failed:", e)
