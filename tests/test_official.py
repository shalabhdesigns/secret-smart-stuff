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
