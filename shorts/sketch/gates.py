"""Deterministic quality gates (no model opinion involved). Each returns a list of problems; empty = pass.

Used by the writers' room (room.py) before any money is spent on voices or art, by the storyboard gate, and by the
final QA on the rendered video. Thresholds live in TARGETS and are documented in docs/TEMPLATE.md §8.
"""
from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
CLICHES = ROOT / "creative" / "cliches.json"

TARGETS = {
    "seconds": (48, 60),          # owner: about 60 s; never cut a line to fit
    "words": (110, 165),          # Roman caption words; Hindi TTS at tempo 1.08 speaks ~2.4-2.9 words/s, plus reactions
    "lines": (12, 24),
    "line_words_max": 14,
    "hook_words_max": 9,
    "cap_line_chars": 42,         # Netflix timed-text max per line (see docs/research)
    "cps_max": 17.0,              # caption reading speed, characters per second (adult programmes)
    "inner_max": 3,
    "first_line_at": 0.30,
}

STAGE_HINDI = ["कृपया", "परंतु", "अत्यंत", "किंतु", "अतः", "हेतु", "प्रतीक्षा"]
LLM_TELLS = [                     # stock phrases that read as machine-written or generic (owner: "not organic")
    "kya baat hai", "ye toh hona hi tha", "sab theek hai na", "life mein", "vibes", "literally",
    "main toh shock", "ekdum mast", "kitne sweet", "takleef kyun",
]


def _caps(plan: dict) -> list[str]:
    return [ln.get("cap", "").replace("\n", " ") for ln in plan.get("lines", [])]


def script(plan: dict, history: list[dict] | None = None) -> list[str]:
    """Hard checks on a written script (before voices)."""
    errs: list[str] = []
    lines = plan.get("lines", [])
    caps = _caps(plan)
    words = sum(len(c.split()) for c in caps)
    lo, hi = TARGETS["words"]
    if not lo <= words <= hi:
        errs.append(f"{words} spoken words; target {lo}-{hi} for a ~55 s episode")
    lo, hi = TARGETS["lines"]
    if not lo <= len(lines) <= hi:
        errs.append(f"{len(lines)} lines; target {lo}-{hi}")
    for ln, c in zip(lines, caps):
        n = len(c.split())
        if n > TARGETS["line_words_max"]:
            errs.append(f"{ln.get('id')}: {n} words (max {TARGETS['line_words_max']}); split it")
        for part in ln.get("cap", "").split("\n"):
            if len(part) > TARGETS["cap_line_chars"]:
                errs.append(f"{ln.get('id')}: caption line over {TARGETS['cap_line_chars']} characters")
        if any(w in ln.get("hi", "") for w in STAGE_HINDI):
            errs.append(f"{ln.get('id')}: stage Hindi word")
        low = c.lower()
        for t in LLM_TELLS:
            if t in low:
                errs.append(f"{ln.get('id')}: stock phrase '{t}' - write what this person would really say")
    if caps and len(caps[0].split()) > TARGETS["hook_words_max"]:
        errs.append(f"hook line has {len(caps[0].split())} words (max {TARGETS['hook_words_max']})")
    inner = sum(1 for ln in lines if "inner" in ln.get("hi", "").lower())
    if inner > TARGETS["inner_max"]:
        errs.append(f"{inner} inner-voice lines (max {TARGETS['inner_max']})")
    for k in ("truth", "game", "loop"):
        if not plan.get(k):
            errs.append(f"missing '{k}' (every episode states its human truth, its game and its loop bridge)")
    if history:
        errs += repetition(plan, history)
    return errs


def _tokens(s: str) -> set[str]:
    return {w for w in re.findall(r"[a-z]{4,}", (s or "").lower())}


def repetition(plan: dict, history: list[dict]) -> list[str]:
    """Premise too close to a recent episode (word overlap of truth/premise)."""
    me = _tokens(f"{plan.get('premise')} {plan.get('truth')} {plan.get('game')}")
    out = []
    for e in history[-30:]:
        other = _tokens(f"{e.get('premise')} {e.get('title')}")
        if me and other:
            j = len(me & other) / len(me | other)
            if j > 0.35:
                out.append(f"premise overlaps Ep {e.get('number')} ({j:.0%} shared words) - find a different situation")
    return out


def cliche(plan: dict) -> list[str]:
    """Situations every desi sketch channel has done; allowed only with a clearly new angle (judge checks)."""
    if not CLICHES.exists():
        return []
    bank = json.loads(CLICHES.read_text())
    text = f"{plan.get('premise', '')} {plan.get('truth', '')}".lower()
    return [c["name"] for c in bank.get("tropes", []) if any(k in text for k in c.get("keys", []))]


def storyboard(plan: dict) -> list[str]:
    """Checks on the staged plan beyond renderability (director.validate covers that)."""
    from . import director as D
    errs = []
    shots = plan.get("shots", [])
    if not shots:
        return ["no shots"]
    lib = D.library()
    voice_only = D.voice_only_ids(plan)
    lines = {ln["id"]: ln for ln in plan.get("lines", [])}
    # a phone voice needs someone on screen holding a phone in that shot
    for i, s in enumerate(shots):
        lid = s.get("line")
        if lid and lines.get(lid, {}).get("who") in voice_only and lines[lid].get("via", "phone") == "phone":
            props = [p for c in s.get("cast", []) for p in (lib["poses"].get(c.get("pose"), {}).get("props") or [])]
            if "phone" not in props and not any("phone" in (c.get("pose") or "") for c in s.get("cast", [])):
                errs.append(f"shot {i}: {lines[lid]['who']} speaks on the phone but nobody on screen holds a phone")
    # every shot belongs to a beat, so retention can later be read per beat
    if any(not s.get("beat") for s in shots):
        errs.append("every shot needs a 'beat' label (hook/setup/escalate1/escalate2/escalate3/turn/punch/button)")
    # loop: the last shot must return to the first shot's framing (same set, type and cast)
    a, b = shots[0], shots[-1]
    if (a.get("set"), a.get("type")) != (b.get("set"), b.get("type")) or \
            sorted(c.get("who") for c in a.get("cast", [])) != sorted(c.get("who") for c in b.get("cast", [])):
        errs.append("loop: the last shot must repeat the first shot's set, shot size and cast so the replay is seamless")
    if plan.get("loop") and not plan["loop"].get("bridge"):
        errs.append("loop: say how the last line leads into the first line ('bridge')")
    return errs


def captions(asm: dict, durs: dict) -> list[str]:
    """Reading speed of every caption against the line's real audio length (after voices exist)."""
    errs = []
    for sh in asm.get("shots", []):
        cap = sh.get("caption")
        if not cap:
            continue
        d = max(0.6, float(sh.get("_line_dur", 0)) or 0.0)
        if not sh.get("_line_dur"):
            continue
        cps = len(cap.replace("\n", "")) / d
        if cps > TARGETS["cps_max"] + 3:            # captions trail the voice; flag only clearly unreadable ones
            errs.append(f"caption '{cap[:30]}…' needs {cps:.0f} chars/s to read (max ~{TARGETS['cps_max']:.0f})")
    return errs
