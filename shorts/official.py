"""Official game images (owner, 16 Nov 2026: "GTA videos must show GTA 6 / GTA 5 images").

Source: Rockstar Games' own media pages. Images are used unchanged (crop + camera move only), with our own
narration and captions on top, and credited "Images: Rockstar Games" in the description.
Never AI-edited, never mixed into AI art, never used to fake gameplay.

Files are NOT committed (the repo is public): `sync()` downloads them on a GitHub runner into
assets/official/img/, which the workflows keep in the Actions cache (private to the repo).
`assets/official/catalogue.json` (committed) says what each picture shows, so the writer can pick one per beat.
"""
from __future__ import annotations

import json
import re
import sys
import time
import urllib.request
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "assets" / "official"
IMG = BASE / "img"
UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
      "Chrome/130.0 Safari/537.36")
VI_PAGE = "https://www.rockstargames.com/VI/media/screenshots"
CREDIT = "Images: Rockstar Games (official Grand Theft Auto screenshots), used for commentary."


def _get(url: str, tries: int = 3) -> bytes:
    last = None
    for k in range(tries):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept": "*/*",
                                                       "Referer": "https://www.rockstargames.com/"})
            with urllib.request.urlopen(req, timeout=60) as r:
                return r.read()
        except Exception as e:  # noqa: BLE001
            last = e
            time.sleep(2 + 3 * k)
    raise RuntimeError(f"download failed: {url} ({last})")


def sources() -> dict[str, dict]:
    """id -> {game, url, page}. GTA VI: every screenshot on Rockstar's media page (ids are Rockstar's own
    file names, e.g. vi_Vice_City_13). GTA V: the fixed list in sources.json."""
    out: dict[str, dict] = {}
    fixed = json.loads((BASE / "sources.json").read_text())
    for it in fixed.get("images", []):
        out[it["id"]] = it
    try:
        html = _get(VI_PAGE).decode("utf-8", "replace")
        for path in dict.fromkeys(re.findall(r"/VI/_next/static/media/[A-Za-z0-9_]+?_\d+\.[A-Za-z0-9_.~-]+?\.jpg", html)):
            name = path.rsplit("/", 1)[1].split(".")[0]
            out["vi_" + name] = {"id": "vi_" + name, "game": "GTA VI", "page": VI_PAGE,
                                 "url": "https://www.rockstargames.com" + path + "?imwidth=3840"}
    except Exception as e:  # noqa: BLE001
        print(f"GTA VI media page not read: {e}")
    return out


def path_for(img_id: str) -> Path:
    return IMG / f"{img_id}.jpg"


def sync(sheets: Path | None = None) -> dict:
    IMG.mkdir(parents=True, exist_ok=True)
    src = sources()
    got, failed = 0, []
    for img_id, it in src.items():
        p = path_for(img_id)
        if p.exists() and p.stat().st_size > 20_000:
            continue
        try:
            data = _get(it["url"])
            tmp = p.with_suffix(".part")
            tmp.write_bytes(data)
            im = Image.open(tmp).convert("RGB")
            im.save(p, "JPEG", quality=92)
            tmp.unlink()
            got += 1
        except Exception as e:  # noqa: BLE001
            failed.append(f"{img_id}: {e}")
    index = {}
    for img_id, it in src.items():
        p = path_for(img_id)
        if p.exists():
            w, h = Image.open(p).size
            index[img_id] = {**it, "w": w, "h": h}
    (IMG / "index.json").write_text(json.dumps(index, indent=1))
    if sheets:
        contact_sheets(sorted(index), sheets)
    print(f"official images: {len(index)} on disk ({got} new), {len(failed)} failed")
    for f in failed[:20]:
        print("  ", f)
    return {"count": len(index), "new": got, "failed": failed}


def contact_sheets(ids: list[str], out: Path, per: int = 12) -> None:
    from PIL import ImageDraw
    out.mkdir(parents=True, exist_ok=True)
    tw, th = 480, 270
    for n in range(0, len(ids), per):
        chunk = ids[n:n + per]
        sheet = Image.new("RGB", (tw * 3, (th + 28) * ((len(chunk) + 2) // 3)), "white")
        d = ImageDraw.Draw(sheet)
        for i, img_id in enumerate(chunk):
            im = Image.open(path_for(img_id)).convert("RGB")
            im.thumbnail((tw, th))
            x, y = (i % 3) * tw, (i // 3) * (th + 28)
            sheet.paste(im, (x, y))
            d.text((x + 4, y + th + 6), img_id, fill="black")
        sheet.save(out / f"sheet_{n // per:02d}.jpg", quality=80)


def catalogue() -> dict[str, dict]:
    f = BASE / "catalogue.json"
    return json.loads(f.read_text()).get("images", {}) if f.exists() else {}


def catalogue_text(games: tuple[str, ...] = ("GTA VI", "GTA V")) -> str:
    """One line per usable image, for the writer: `id | game | what it shows`."""
    lines = []
    for img_id, it in catalogue().items():
        if it.get("game") in games and not it.get("avoid"):
            lines.append(f"{img_id} | {it['game']} | {it['shows']}")
    return "\n".join(lines)


SOLO = ("vi_Jason_Duval_", "vi_Lucia_Caminos_", "vi_Boobie_Ike_", "vi_Brian_Heder_", "vi_Cal_Hampton_",
        "vi_DreQuan_Priest_", "vi_Raul_Bautista_", "vi_Real_Dimez_")


def frame_mode(img_id: str) -> str:
    """crop = full-height 9:16 cut (one person); wide = most of the picture over a blurred fill (two people, places);
    fit = the whole picture over a blurred fill (signs, maps, aerials)."""
    it = catalogue().get(img_id) or {}
    if it.get("frame"):
        return it["frame"]
    return "crop" if img_id.startswith(SOLO) else "wide"


def vertical(img_id: str, out: Path, focus_x: float | None = None) -> Path:
    """A 1080x1920 frame from an official image, unchanged apart from crop/scale (never AI-edited)."""
    from PIL import ImageEnhance, ImageFilter
    p = path_for(img_id)
    if not p.exists():
        raise FileNotFoundError(f"official image {img_id} is not on this runner (run the official sync)")
    im = Image.open(p).convert("RGB")
    w, h = im.size
    fx = float((catalogue().get(img_id) or {}).get("focus_x", 0.5)) if focus_x is None else focus_x
    mode = frame_mode(img_id)
    if mode == "crop":
        cw = min(w, round(h * 9 / 16))
        left = int(min(max(fx * w - cw / 2, 0), w - cw))
        im.crop((left, 0, left + cw, h)).resize((1080, 1920), Image.LANCZOS).save(out, "PNG")
        return out
    # blurred, darkened fill from the same picture, then the picture itself in the middle
    sc = max(1080 / w, 1920 / h)
    bg = im.resize((round(w * sc), round(h * sc)), Image.LANCZOS)
    bl, bt = (bg.width - 1080) // 2, (bg.height - 1920) // 2
    bg = bg.crop((bl, bt, bl + 1080, bt + 1920)).filter(ImageFilter.GaussianBlur(40))
    bg = ImageEnhance.Brightness(bg).enhance(0.55)
    fh = 1150 if mode == "wide" else round(1080 * h / w)
    fw = round(w * fh / h)
    fg = im.resize((fw, fh), Image.LANCZOS)
    if fw > 1080:
        left = int(min(max(fx * fw - 540, 0), fw - 1080))
        fg = fg.crop((left, 0, left + 1080, fh))
    bg.paste(fg, ((1080 - fg.width) // 2, (1920 - fg.height) // 2))
    bg.save(out, "PNG")
    return out


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "sync":
        r = sync(Path(sys.argv[2]) if len(sys.argv) > 2 else None)
        sys.exit(0 if r["count"] else 1)
