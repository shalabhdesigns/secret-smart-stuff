"""Cross-promotion (owner, 3 Nov 2026): one quiet line per platform pointing to the other (same handle on both), and
a small translucent on-screen handle that keeps the first/last frames clean so the loop stays seamless."""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from shorts.publish import instagram as ig  # noqa: E402
from shorts.render.captions import Word, write_ass  # noqa: E402


def test_instagram_caption_points_to_youtube_once_and_drops_the_youtube_line():
    meta = {"title": "Why are tiffins stacked?",
            "description": "Each tier keeps food apart.\n\nVisuals are AI-generated illustrations; narration is an AI "
                           "voice.\n\nAlso on Instagram: @secretsmartstuff\n\n#tiffin #design"}
    c = ig.caption(meta)
    assert c.count("Also on YouTube: @secretsmartstuff") == 1 and "Also on Instagram" not in c
    assert "http" not in c.split("Sources")[0]                     # no dead links (captions aren't clickable)


def test_onscreen_handle_fades_and_leaves_the_loop_frames_clean(tmp_path):
    out = write_ass([Word("hi", 0.1, 0.4)], tmp_path / "c.ass", font="Archivo", handle=(3.0, 27.5, "@secretsmartstuff"))
    line = [x for x in out.read_text().splitlines() if x.startswith("Dialogue: 2,")][0]
    assert line.startswith("Dialogue: 2,0:00:03.00,0:00:27.50,Handle") and "{\\fad(500,500)}@secretsmartstuff" in line
    assert "Style: Handle,Archivo,38,&H40FFFFFF" in out.read_text()          # small and translucent
    assert "Handle" not in write_ass([Word("hi", 0.1, 0.4)], tmp_path / "d.ass").read_text().split("[Events]")[1]
