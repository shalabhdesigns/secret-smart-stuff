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


def access_token() -> str:
    """Exchange the stored refresh token for a short-lived access token."""
    need = ["YT_CLIENT_ID", "YT_CLIENT_SECRET", "YT_REFRESH_TOKEN"]
    missing = [k for k in need if not os.environ.get(k)]
    if missing:
        raise UploadBlocked(f"missing secrets: {', '.join(missing)}")
    r = requests.post(TOKEN_URL, data={
        "client_id": os.environ["YT_CLIENT_ID"],
        "client_secret": os.environ["YT_CLIENT_SECRET"],
        "refresh_token": os.environ["YT_REFRESH_TOKEN"],
        "grant_type": "refresh_token",
    }, timeout=30)
    if r.status_code == 400 and "invalid_grant" in r.text:
        raise UploadBlocked("refresh token expired or revoked - re-run scripts/youtube_auth.py "
                            "(and make sure the OAuth consent screen is 'In production')")
    r.raise_for_status()
    return r.json()["access_token"]


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
