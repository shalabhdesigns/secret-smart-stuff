"""Thin wrapper around the vendored youtube-agent-skill tools (MIT, reviewed
2026-10-24: pure-Python text heuristics, no network, no file writes)."""
from __future__ import annotations

import importlib.util
from functools import lru_cache
from pathlib import Path

VENDOR = Path(__file__).resolve().parents[1] / "vendor" / "ytskill"


@lru_cache(maxsize=None)
def _load(name: str):
    spec = importlib.util.spec_from_file_location(f"ytskill_{name}", VENDOR / f"{name}.py")
    mod = importlib.util.module_from_spec(spec)  # type: ignore[arg-type]
    spec.loader.exec_module(mod)  # type: ignore[union-attr]
    return mod


def hook_score(text: str) -> dict:
    """5-property hook panel (heuristic warning light, not a predictor)."""
    m = _load("hookscore")
    parts, verdict, formula, _ = m.score(text)
    return {"hook": text, "verdict": verdict, "band": m.band(verdict), "properties": parts, "formula": formula}


def title_lint(title: str, thumb: str | None = None) -> dict:
    m = _load("title")
    r = m.check(title, thumb)
    r["issues"] = [{"kind": k, "detail": d} for k, d in r["issues"]]
    return r
