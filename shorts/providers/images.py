"""Image generation.

Live: Black Forest Labs API (FLUX.2). Submit -> poll `polling_url` -> download
`result.sample` (signed URL valid ~10 minutes, so we download immediately).
Dry-run: a procedural placeholder image labelled DRY RUN.
"""
from __future__ import annotations

import hashlib
import time
from pathlib import Path

import requests
from PIL import Image, ImageDraw, ImageFont

BASE = "https://api.bfl.ai/v1/"
FONT = Path(__file__).resolve().parents[2] / "assets" / "fonts" / "Inter-Black.otf"


class ImageError(RuntimeError):
    pass


class BFLImages:
    def __init__(self, api_key: str, model: str, width: int, height: int, usd_each: dict):
        self.key, self.model, self.w, self.h, self.prices = api_key, model, width, height, usd_each

    def generate(self, prompt: str, out: Path, seed: int | None = None, model: str | None = None,
                 timeout_s: int = 180) -> tuple[Path, float]:
        model = model or self.model
        body = {"prompt": prompt, "width": self.w, "height": self.h, "output_format": "png"}
        if seed is not None:
            body["seed"] = seed
        h = {"x-key": self.key, "accept": "application/json", "content-type": "application/json"}
        for attempt in range(6):
            r = requests.post(BASE + model, json=body, headers=h, timeout=60)
            if r.status_code == 422 and "extra_forbidden" in r.text:
                # newer models (e.g. flux-3-image) take fewer fields: drop the refused ones and retry
                bad = [d.get("loc", [None, None])[-1] for d in (r.json().get("detail") or [])
                       if d.get("type") == "extra_forbidden"]
                if "width" in bad or "height" in bad:
                    body["aspect_ratio"] = "9:16"
                for k in bad:
                    body.pop(k, None)
                continue
            if r.status_code != 429:
                break
            time.sleep(5 * (2 ** min(attempt, 3)))   # too many active tasks: wait and retry
        if r.status_code == 402:
            raise ImageError("BFL account has no credits left")
        if r.status_code != 200:
            raise ImageError(f"BFL submit {r.status_code}: {r.text[:300]}")
        poll = r.json()["polling_url"]
        t0 = time.time()
        while time.time() - t0 < timeout_s:
            time.sleep(1.0)
            try:
                resp = requests.get(poll, headers=h, timeout=30)
            except requests.RequestException:
                continue
            if resp.status_code != 200:
                continue
            s = resp.json()
            status = s.get("status")
            if status == "Ready":
                img = requests.get(s["result"]["sample"], timeout=120)
                img.raise_for_status()
                out.write_bytes(img.content)
                return out, float(self.prices.get(model, 0.03))
            if status in ("Error", "Failed", "Task not found", "No Card Generated",
                          "Request Moderated", "Content Moderated"):
                raise ImageError(f"BFL generation {status}: {s}")
        raise ImageError("BFL generation timed out")


class FakeImages:
    def generate(self, prompt: str, out: Path, seed: int | None = None, **kw) -> tuple[Path, float]:
        hsh = hashlib.md5(prompt.encode()).digest()
        base = (40 + hsh[0] % 80, 50 + hsh[1] % 80, 70 + hsh[2] % 90)
        img = Image.new("RGB", (1088, 1920), base)
        d = ImageDraw.Draw(img)
        for i in range(0, 1920, 96):
            d.line([(0, i), (1088, i + 300)], fill=tuple(min(255, c + 25) for c in base), width=6)
        d.ellipse([294, 760, 794, 1260], outline=(240, 240, 240), width=14)
        f = ImageFont.truetype(str(FONT), 64)
        d.text((80, 300), "DRY RUN IMAGE", font=f, fill=(255, 255, 255))
        f2 = ImageFont.truetype(str(FONT), 40)
        words, line, y = prompt.split(), "", 1400
        for w in words:
            if len(line) + len(w) > 34:
                d.text((80, y), line, font=f2, fill=(230, 230, 230)); y += 52; line = ""
            line += w + " "
        d.text((80, y), line, font=f2, fill=(230, 230, 230))
        img.save(out)
        return out, 0.0
