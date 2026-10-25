"""Image-to-video clips via Black Forest Labs FLUX 3 (verified 2026-10-25).

POST https://api.bfl.ai/v1/flux-3-video  {mode: "i2v", keyframes: [base64 png], ...}
Poll polling_url until Ready; result.sample is a signed mp4 (download at once).
Prices (BFL help article): draft from $0.06/s, full render from $0.17/s.
9:16 at hd = 704x1280; the render stage scales it to 1080x1920.
"""
from __future__ import annotations

import base64
import time
from pathlib import Path

import requests

ENDPOINT = "https://api.bfl.ai/v1/flux-3-video"


class VideoError(RuntimeError):
    pass


class BFLVideo:
    def __init__(self, api_key: str, draft: bool = True, usd_per_second: float | None = None):
        self.key, self.draft = api_key, draft
        self.rate = usd_per_second if usd_per_second is not None else (0.06 if draft else 0.17)

    def image_to_video(self, image: Path, prompt: str, out: Path, seconds: int = 5,
                       timeout_s: int = 600) -> tuple[Path, float]:
        b64 = base64.b64encode(image.read_bytes()).decode()
        body = {"mode": "i2v", "prompt": prompt, "keyframes": [f"data:image/png;base64,{b64}"],
                "aspect_ratio": "9:16", "duration": int(seconds), "resolution": "hd",
                "generate_audio": False, "draft": self.draft}
        h = {"x-key": self.key, "accept": "application/json", "content-type": "application/json"}
        r = None
        for attempt in range(4):
            r = requests.post(ENDPOINT, json=body, headers=h, timeout=120)
            if r.status_code != 429:
                break
            time.sleep(5 * (2 ** attempt))
        assert r is not None
        if r.status_code == 402:
            raise VideoError("BFL account has no credits left")
        if r.status_code != 200:
            raise VideoError(f"BFL video submit {r.status_code}: {r.text[:300]}")
        j = r.json()
        poll = j["polling_url"]
        t0 = time.time()
        while time.time() - t0 < timeout_s:
            time.sleep(4)
            try:
                resp = requests.get(poll, headers=h, timeout=30)
            except requests.RequestException:
                continue
            if resp.status_code != 200:
                continue
            s = resp.json()
            st = s.get("status")
            if st == "Ready":
                clip = requests.get(s["result"]["sample"], timeout=300)
                clip.raise_for_status()
                out.write_bytes(clip.content)
                cost = j.get("cost")
                usd = cost / 100 if isinstance(cost, (int, float)) and cost > 5 else seconds * self.rate
                return out, float(usd)
            if st in ("Error", "Failed", "Task not found", "Request Moderated", "Content Moderated"):
                raise VideoError(f"BFL video {st}: {s}")
        raise VideoError("BFL video timed out")


class FakeVideo:
    """Dry run: a slow push-in made with ffmpeg from the still, so the rest of the pipeline is exercised."""

    def image_to_video(self, image: Path, prompt: str, out: Path, seconds: int = 5, **kw) -> tuple[Path, float]:
        import subprocess
        frames = seconds * 30
        subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-loop", "1", "-i", str(image),
                        "-vf", f"scale=1408:2560,zoompan=z='min(1+0.0015*on,1.25)':x='iw/2-(iw/zoom/2)':"
                               f"y='ih/2-(ih/zoom/2)':d={frames}:s=704x1280:fps=30,format=yuv420p",
                        "-frames:v", str(frames), "-c:v", "libx264", "-preset", "veryfast", "-an", str(out)],
                       check=True)
        return out, 0.0
