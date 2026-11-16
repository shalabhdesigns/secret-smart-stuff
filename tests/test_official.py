from pathlib import Path

from PIL import Image

from shorts import official
from shorts.pipeline import Pipeline


def test_official_ref():
    assert Pipeline._official_ref("OFFICIAL:vi_Vice_City_13") == ("vi_Vice_City_13", None)
    assert Pipeline._official_ref("official: vi_Jason_Duval_01@0.3 extra") == ("vi_Jason_Duval_01", 0.3)
    assert Pipeline._official_ref("a photo of a shelf") is None


def test_vertical_crop(tmp_path, monkeypatch):
    monkeypatch.setattr(official, "IMG", tmp_path)
    Image.new("RGB", (3840, 2160), (200, 30, 30)).save(tmp_path / "vi_X_01.jpg")
    out = official.vertical("vi_X_01", tmp_path / "o.png", 0.9)
    assert Image.open(out).size == (1080, 1920)


def test_visuals_line_credits_rockstar(tmp_path):
    (tmp_path / "visuals.json").write_text('{"images": {"img1": {"official": "vi_X_01"}}}')
    assert "Rockstar Games" in Pipeline._visuals_line(tmp_path)
    (tmp_path / "visuals.json").write_text('{"images": {"img1": {}}}')
    assert "AI-generated" in Pipeline._visuals_line(Path(tmp_path))


def test_clip_segment_and_still(tmp_path, monkeypatch):
    import json
    import subprocess
    from shorts import official_clips as oc
    monkeypatch.setattr(oc, "CLIPS", tmp_path)
    monkeypatch.setattr(oc, "BASE", tmp_path)
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-f", "lavfi", "-i", "testsrc=size=1920x1080:rate=30",
                    "-t", "6", "-pix_fmt", "yuv420p", str(tmp_path / "trailer_x.mp4")], check=True)
    (tmp_path / "shots.json").write_text(json.dumps({"shots": {
        "trailer_x_00010": {"clip": "trailer_x", "start": 1.0, "end": 3.0, "shows": "a car on a beach road"},
        "trailer_x_00030": {"clip": "trailer_x", "start": 3.0, "end": 6.0, "shows": "a gun fight", "avoid": "violence"}}}))
    seg = oc.segment("trailer_x_00010", tmp_path / "s.mp4", 2.5)
    assert 2.5 <= oc._dur(seg) <= 3.2
    from PIL import Image
    assert Image.open(oc.still("trailer_x_00010", tmp_path / "f.png")).size == (1080, 1920)
    assert oc.best_match("car driving by the beach") == "trailer_x_00010"
    assert "violence" not in oc.shots_text()
