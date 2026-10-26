"""Grow the set library automatically: new backgrounds in the exact show style, checked before use.

- One FLUX.2 [pro] image per new set, with an existing approved background as the style reference.
- Claude vision check: same style, empty, eye level, floor visible, no text/people. Fails are discarded.
- Approved sets are committed to the repo (assets/puppet/backgrounds + rig.json + library.json) and the
  owner gets the picture on Telegram. Weekly art budget cap (config: budget_usd.art_weekly, default $5).

New *characters/poses* are not generated here: they need face mapping and identity QA, which is still a
manual step (creative/puppet/README.md).
"""
from __future__ import annotations

import base64
import datetime as dt
import json
import os
import subprocess
import time
from pathlib import Path

import requests
from PIL import Image

from shorts import notify

from . import director as D

ROOT = Path(__file__).resolve().parents[2]
BG_DIR = ROOT / "assets" / "puppet" / "backgrounds"
MODEL = "flux-2-pro"
USD_EACH = 0.06            # flux-2-pro with one reference image, upper estimate
QA_MODEL = "claude-sonnet-5-5"

IDEAS = [
    ("office", "Dev's small IT office: rows of cubicle desks with monitors, a water cooler, motivational poster without words, glass meeting room at the back", "Dev's IT office (cubicles, monitors, water cooler)"),
    ("chai_tapri", "a roadside chai stall corner in Kanpur: tea stall counter with a big kettle and glasses, a wooden bench, a scooter parked, old wall with peeling paint, evening light", "roadside chai stall corner with bench and scooter"),
    ("kitchen", "the small kitchen of Dev and Meera's rented flat: steel utensils on a rack, a gas stove with a pressure cooker, a fridge with magnets, a window with grill", "the flat's small kitchen (stove, pressure cooker, fridge)"),
    ("kirana", "a neighbourhood kirana grocery shop seen from the customer side: wooden counter, shelves of packets and jars without readable labels, a weighing scale", "neighbourhood kirana shop counter"),
    ("gali", "a narrow residential lane (gali) in an Indian city: colourful house fronts, a parked scooter, potted plants, tangled overhead wires, a doorway with steps", "residential lane outside the flat"),
    ("rooftop", "the flat's rooftop terrace (chhat): water tank, clothes drying on a line, neighbouring rooftops, a plastic chair, sunset sky", "rooftop terrace with water tank and drying clothes"),
    ("canteen", "a college canteen: plastic tables and chairs, a serving counter with steel containers, a ceiling fan, notice board without readable text", "college canteen"),
    ("shaadi", "a wedding venue (shaadi hall) at night: decorated stage with marigold garlands, fairy lights, round tables with white cloths, empty", "wedding venue with marigold stage"),
    ("platform", "an Indian railway station platform: yellow edge line, a bench, a pillar, a tea vendor trolley, a train waiting at the side", "railway platform with bench"),
    ("bank", "a small bank branch hall: service counter with glass partitions, a token display without numbers, plastic chairs, a ceiling fan", "small bank branch hall"),
]


def _weekly_art_spend(state) -> float:
    since = time.time() - 7 * 86400
    row = state.db.execute("SELECT COALESCE(SUM(usd),0) s FROM costs WHERE provider='art' AND at>=?", (since,)).fetchone()
    return float(row["s"])


def _flux(key: str, prompt: str, ref: Path, out: Path) -> None:
    ref_small = out.with_suffix(".ref.jpg")
    im = Image.open(ref).convert("RGB")
    im.thumbnail((768, 1376))
    im.save(ref_small, quality=90)
    body = {"prompt": prompt, "width": 1088, "height": 1952, "output_format": "png",
            "input_image": base64.b64encode(ref_small.read_bytes()).decode()}
    h = {"x-key": key, "accept": "application/json", "content-type": "application/json"}
    r = requests.post("https://api.bfl.ai/v1/" + MODEL, json=body, headers=h, timeout=60)
    if r.status_code != 200:
        raise RuntimeError(f"BFL {r.status_code}: {r.text[:200]}")
    poll = r.json()["polling_url"]
    t0 = time.time()
    while time.time() - t0 < 240:
        time.sleep(2)
        s = requests.get(poll, headers=h, timeout=30).json()
        if s.get("status") == "Ready":
            out.write_bytes(requests.get(s["result"]["sample"], timeout=120).content)
            return
        if s.get("status") not in ("Pending", "Processing", None):
            raise RuntimeError(f"BFL {s.get('status')}")
    raise RuntimeError("BFL timed out")


QA = """TASK: setqa
Image 1 is an approved background from our 2D cartoon show. Image 2 is a NEW background for the same show,
meant to show: {desc}.
Characters will be drawn standing on the floor in the lower part of the frame, so check:
1. same flat cartoon illustration style, line weight and colour feel as image 1
2. the place matches the description and looks Indian where relevant
3. empty: no people, no characters, no faces (a small animal at the side is OK)
4. straight-on, eye-level view; floor or ground clearly visible across the bottom ~25% of the image
5. no readable text, letters, numbers, logos or brand names anywhere
6. nothing large in the lower centre that characters would stand inside
Return JSON {{"ok": true|false, "reasons": ["..."]}}. Be strict."""


def grow(p, count: int = 1) -> list[str]:
    """Weekly: add a generally useful place the show doesn't have yet (stories can also ask for one any day)."""
    from . import art as A
    have = set(D.library()["sets"])
    added = []
    for sid, desc, short in [i for i in IDEAS if i[0] not in have][:count]:
        if A.generate_set(p, sid, desc, short):
            added.append(sid)
            notify.send_photo(p.state, BG_DIR / f"{sid}.jpg", f"🎨 New set added to the show: <b>{notify.esc(short)}</b>")
    return added
