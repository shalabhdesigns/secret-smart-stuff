"""Covers (owner, 3 Nov 2026): the best existing picture + 2-5 honest curiosity words, in the brand style, placed
where they hide least of the picture and inside what every platform crop keeps."""
from __future__ import annotations

import json
import sys
from pathlib import Path

from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from shorts.render import cover  # noqa: E402

SCRIPT = {"title": "Why do handrails curl back into the wall?", "thumb_text": "Snag Guard",
          "images": {"img1": "a handrail with a curled end", "img2": "a square open end"},
          "scenes": [{"id": "b1", "narration": "Why does this handrail curl?", "image": "img1"},
                     {"id": "b2", "narration": "A flat end can hook a sleeve.", "image": "img2"}]}


def _job(tmp_path):
    (tmp_path / "script.json").write_text(json.dumps(SCRIPT))
    for name, y in (("img1", 1500), ("img2", 400)):     # img1: detail low in the frame -> words go up
        im = Image.new("RGB", (1088, 1920), (235, 235, 235))
        ImageDraw.Draw(im).rectangle((100, y - 200, 1000, y + 200), fill=(150, 90, 30))
        for x in range(100, 1000, 40):
            ImageDraw.Draw(im).line((x, y - 200, x + 20, y + 200), fill=(40, 40, 40), width=6)
        im.save(tmp_path / f"{name}.png")
    return tmp_path


def test_plan_used_and_cover_rendered(tmp_path):
    d = _job(tmp_path)
    seen = {}

    def ask(prompt):
        seen["p"] = prompt
        return {"image": "img1", "lines": ["why the curl?", "it's not decor"], "why": "clear shot"}
    p = cover.make(ask, d)
    assert p["image"] == "img1" and p["lines"] == ["WHY THE CURL?", "IT'S NOT DECOR"]
    assert "MUST be true and paid off by the video" in seen["p"]          # honest curiosity, never a false promise
    im = Image.open(d / "cover.jpg")
    assert im.size == (1080, 1920) and (d / "cover.jpg").stat().st_size < 2 * 1024 * 1024   # YouTube's 2 MB limit
    # the words went to the upper zone, away from the busy detail low in the frame
    upper = im.crop((0, 430, 1080, 820)).convert("RGB")
    assert any(px == cover.ULTRA or sum(abs(a - b) for a, b in zip(px, cover.ULTRA)) < 30 for px in upper.getdata())


def test_bad_plan_falls_back_to_hook_picture_and_thumb_text(tmp_path):
    d = _job(tmp_path)
    p = cover.make(lambda prompt: {"image": "img9", "lines": ["way too many words in this cover line"]}, d)
    assert p["image"] == "img1" and p["lines"] == ["SNAG GUARD"] and (d / "cover.jpg").exists()


def test_news_cover_rules_reach_the_planner(tmp_path):
    d, seen = _job(tmp_path), {}
    cover.make(lambda prompt: seen.setdefault("p", prompt) and None, d, news=True)
    assert "must not mention deaths" in seen["p"]
