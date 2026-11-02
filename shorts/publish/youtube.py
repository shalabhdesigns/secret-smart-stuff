"""YouTube upload through the official Data API v3 (resumable upload).

Status: written against the documented API, NOT yet tested against a real
channel (this workspace has no network route to Google). It runs on GitHub
Actions, where the network is open.

Safety rules built in
- Idempotency: the SHA-256 of the final MP4 is recorded BEFORE upload starts.
  If a run dies mid-upload, the next run sees the record and refuses to start
  a second upload; a human checks YouTube Studio and resolves it.
- Uploads go up as `private` (optionally with `publishAt` for scheduling).
  Nothing is made public by this module directly.
- Credentials come only from environment variables (GitHub secrets).
"""
from __future__ import annotations

import hashlib
import json
import os
import time
from dataclasses import dataclass
from pathlib import Path

import requests

from ..state import State

TOKEN_URL = "https://oauth2.googleapis.com/token"
UPLOAD_URL = "https://www.googleapis.com/upload/youtube/v3/videos"
VIDEOS_URL = "https://www.googleapis.com/youtube/v3/videos"
SCOPES = ["https://www.googleapis.com/auth/youtube.upload",
          "https://www.googleapis.com/auth/youtube.readonly",
          "https://www.googleapis.com/auth/yt-analytics.readonly"]
CHUNK = 8 * 1024 * 1024


class UploadBlocked(RuntimeError):
    """Raised when uploading could create a duplicate or break a rule."""


@dataclass
class VideoMeta:
    title: str
    description: str
    tags: list[str]
    category_id: str = "27"            # 27 = Education; set per channel in config
    language: str = "en"
    made_for_kids: bool = False
    contains_synthetic_media: bool = True
    publish_at: str | None = None      # RFC 3339 UTC, e.g. 2026-11-02T13:30:00Z


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda: f.read(1 << 20), b""):
            h.update(block)
    return h.hexdigest()


_CACHE: dict = {}


def _cf_kv(key: str) -> str | None:
    """Read one value from the studio Worker's KV store (None if not configured or missing)."""
    tok = os.environ.get("CLOUDFLARE_API_TOKEN", "").strip()
    if not tok:
        return None
    try:
        from ..config import load
        cfg = load()
        acc = (os.environ.get("CLOUDFLARE_ACCOUNT_ID") or str(cfg.pipeline.get("cloudflare_account_id", ""))).strip()
        ns = State(cfg.path("state_db")).get_setting("cf_kv_namespace")
    except Exception:  # noqa: BLE001
        return None
    if not (acc and ns):
        return None
    r = requests.get(f"https://api.cloudflare.com/client/v4/accounts/{acc}/storage/kv/namespaces/{ns}/values/{key}",
                     headers={"Authorization": f"Bearer {tok}"}, timeout=30)
    return r.text if r.status_code == 200 else None


def _stored_refresh_token() -> str | None:
    """The refresh token saved by the Worker's one-tap login (/ytlogin), encrypted with a key derived
    from YT_CLIENT_SECRET (AES-GCM, iv || ciphertext+tag, base64). See worker/index.js `seal`."""
    sealed = _cf_kv("yt_refresh.enc")
    if not sealed:
        return None
    import base64

    from cryptography.hazmat.primitives.ciphers.aead import AESGCM
    raw = base64.b64decode(sealed)
    key = hashlib.sha256(("yt-refresh-v1:" + os.environ["YT_CLIENT_SECRET"]).encode()).digest()
    return AESGCM(key).decrypt(raw[:12], raw[12:], None).decode()


def expected_channel() -> str:
    try:
        from ..config import load
        return str(load().channel["channel"]["name"])
    except Exception:  # noqa: BLE001
        return ""


def access_token(check_channel: bool = True) -> str:
    """Exchange the stored refresh token for a short-lived access token.

    The token comes from the Worker's one-tap login when present, else from the GitHub secret
    YT_REFRESH_TOKEN. With check_channel (the default) the token must belong to the channel named in
    config/channel.yaml, so nothing is ever uploaded to, or measured from, the wrong channel."""
    if "token" in _CACHE and _CACHE["exp"] > time.time() + 60:
        return _CACHE["token"]
    need = ["YT_CLIENT_ID", "YT_CLIENT_SECRET"]
    missing = [k for k in need if not os.environ.get(k)]
    if missing:
        raise UploadBlocked(f"missing secrets: {', '.join(missing)}")
    try:
        refresh = _stored_refresh_token()
    except Exception as e:  # noqa: BLE001
        raise UploadBlocked(f"the saved YouTube login could not be read ({e}); send /ytlogin in Telegram") from e
    refresh = refresh or os.environ.get("YT_REFRESH_TOKEN", "")
    if not refresh:
        raise UploadBlocked("no YouTube login yet: send /ytlogin to the studio bot")
    r = requests.post(TOKEN_URL, data={
        "client_id": os.environ["YT_CLIENT_ID"],
        "client_secret": os.environ["YT_CLIENT_SECRET"],
        "refresh_token": refresh,
        "grant_type": "refresh_token",
    }, timeout=30)
    if r.status_code == 400 and "invalid_grant" in r.text:
        raise UploadBlocked("YouTube login expired or revoked: send /ytlogin to the studio bot")
    r.raise_for_status()
    token = r.json()["access_token"]
    want = expected_channel()
    if check_channel and want:
        ch = requests.get("https://www.googleapis.com/youtube/v3/channels", params={"part": "snippet", "mine": "true"},
                          headers={"Authorization": f"Bearer {token}"}, timeout=30).json()
        titles = [c["snippet"]["title"] for c in ch.get("items", [])]
        if want not in titles:
            raise UploadBlocked(f"the YouTube login is for {titles or 'no channel'}, not '{want}': "
                                "send /ytlogin to the studio bot and pick the right channel")
    _CACHE.update(token=token, exp=time.time() + int(r.json().get("expires_in", 3600)))
    return token


def _clean(text: str, max_bytes: int) -> str:
    """YouTube rejects < and > in titles/descriptions and caps length in bytes."""
    t = text.replace("<", "‹").replace(">", "›")
    b = t.encode("utf-8")[:max_bytes]
    return b.decode("utf-8", errors="ignore")


def _body(meta: VideoMeta) -> dict:
    status = {
        "privacyStatus": "private",
        "selfDeclaredMadeForKids": meta.made_for_kids,
        "containsSyntheticMedia": meta.contains_synthetic_media,
        "embeddable": True,
    }
    if meta.publish_at:
        status["publishAt"] = meta.publish_at
    return {
        "snippet": {
            "title": _clean(meta.title, 100)[:100],
            "description": _clean(meta.description, 5000),
            "tags": meta.tags[:15],
            "categoryId": meta.category_id,
            "defaultLanguage": meta.language,
            "defaultAudioLanguage": meta.language,
        },
        "status": status,
    }


def upload(state: State, job_id: str, video: Path, meta: VideoMeta,
           max_retries: int = 5) -> dict:
    digest = sha256(video)
    prior = state.upload_for_hash(digest)
    if prior and prior["status"] in ("uploaded", "processed"):
        return prior                      # already done - never upload twice
    if prior and prior["status"] == "started":
        raise UploadBlocked(f"an earlier upload of this file started but did not confirm "
                            f"(job {prior['job_id']}). Check YouTube Studio, then mark it "
                            f"resolved with `shorts upload-resolve {prior['job_id']}`.")
    token = access_token()
    size = video.stat().st_size
    init = requests.post(
        UPLOAD_URL, params={"uploadType": "resumable", "part": "snippet,status"},
        headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json",
                 "X-Upload-Content-Type": "video/mp4", "X-Upload-Content-Length": str(size)},
        data=json.dumps(_body(meta)), timeout=60,
    )
    if init.status_code == 403 and "quota" in init.text.lower():
        raise UploadBlocked("upload quota exhausted for today")
    if init.status_code >= 400:
        raise UploadBlocked(f"upload could not start ({init.status_code}): {init.text[:300]}")
    session = init.headers["Location"]
    # Only now can a video start to exist on YouTube, so only now block re-uploads.
    state.record_upload(job_id, digest, "started", privacy="private", publish_at=meta.publish_at)

    sent, attempt = 0, 0
    with video.open("rb") as f:
        while sent < size:
            f.seek(sent)
            chunk = f.read(CHUNK)
            end = sent + len(chunk) - 1
            try:
                r = requests.put(session, data=chunk, timeout=300, headers={
                    "Authorization": f"Bearer {token}",
                    "Content-Range": f"bytes {sent}-{end}/{size}"})
            except requests.RequestException:
                r = None
            if r is not None and r.status_code in (200, 201):
                vid = r.json()["id"]
                url = f"https://youtube.com/shorts/{vid}"
                state.record_upload(job_id, digest, "uploaded", video_id=vid, url=url)
                return state.upload_for_hash(digest)  # type: ignore[return-value]
            if r is not None and r.status_code == 308:      # chunk accepted, keep going
                rng = r.headers.get("Range")
                sent = int(rng.split("-")[1]) + 1 if rng else 0
                attempt = 0
                continue
            if r is not None and r.status_code < 500 and r.status_code != 429:
                state.record_upload(job_id, digest, "failed")
                raise UploadBlocked(f"upload rejected {r.status_code}: {r.text[:300]}")
            attempt += 1                                     # 5xx / 429 / network: back off
            if attempt > max_retries:
                raise UploadBlocked("upload kept failing; left as 'started' for a human to check")
            time.sleep(min(2 ** attempt, 60))
            try:
                q = requests.put(session, timeout=60, headers={
                    "Authorization": f"Bearer {token}", "Content-Range": f"bytes */{size}"})
            except requests.RequestException:
                continue
            if q.status_code in (200, 201):
                vid = q.json()["id"]
                state.record_upload(job_id, digest, "uploaded", video_id=vid, url=f"https://youtube.com/shorts/{vid}")
                return state.upload_for_hash(digest)  # type: ignore[return-value]
            if q.status_code == 308:
                rng = q.headers.get("Range")
                sent = int(rng.split("-")[1]) + 1 if rng else 0
    raise UploadBlocked("upload ended without confirmation")


def processing_status(video_id: str) -> dict:
    token = access_token()
    r = requests.get(VIDEOS_URL, params={"part": "status,processingDetails", "id": video_id},
                     headers={"Authorization": f"Bearer {token}"}, timeout=30)
    r.raise_for_status()
    items = r.json().get("items", [])
    return items[0] if items else {}


def unschedule(video_id: str) -> dict:
    """Keep a video private and remove its scheduled publish time (owner's "Stop it" button)."""
    token = access_token()
    body = {"id": video_id, "status": {"privacyStatus": "private", "selfDeclaredMadeForKids": False,
                                       "embeddable": True, "containsSyntheticMedia": True}}
    r = requests.put(VIDEOS_URL, params={"part": "status"}, json=body,
                     headers={"Authorization": f"Bearer {token}"}, timeout=30)
    if r.status_code >= 400:
        raise UploadBlocked(f"could not stop {video_id}: {r.status_code} {r.text[:200]}")
    return r.json()


THUMB_URL = "https://www.googleapis.com/upload/youtube/v3/thumbnails/set"


def set_thumbnail(video_id: str, image: Path) -> dict:
    """Custom thumbnail (cover) for a video or Short. YouTube needs a phone-verified channel (and, for Shorts in
    the feed, the Partner Program); a refusal is returned, never raised, so publishing never depends on it."""
    data = image.read_bytes()
    if len(data) > 2 * 1024 * 1024:
        return {"ok": False, "error": "cover larger than YouTube's 2 MB limit"}
    try:
        r = requests.post(THUMB_URL, params={"videoId": video_id}, data=data, timeout=120,
                          headers={"Authorization": f"Bearer {access_token()}", "Content-Type": "image/jpeg"})
    except Exception as e:  # noqa: BLE001
        return {"ok": False, "error": str(e)[:300]}
    if r.status_code == 200:
        return {"ok": True}
    return {"ok": False, "error": f"{r.status_code}: {r.text[:300]}"}
