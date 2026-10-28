"""Instagram Reels: post each published video at its YouTube slot, and read its numbers (added 28 Oct 2026).

How it works
- Login: the owner sends /iglogin to the studio bot (Instagram Business Login, no Facebook Page needed). The
  Worker stores the long-lived token ENCRYPTED in KV ("ig_token.enc"; same scheme as the YouTube login, key
  derived from YT_CLIENT_SECRET with the label "ig-token-v1:") plus "ig_account" (user id, username, expiry).
  Tokens last 60 days; `token()` refreshes them automatically when fewer than 20 days are left.
- Guard: nothing is posted unless the login is for the account in config/channel.yaml (`instagram.handle`).
- Posting: Instagram's API cannot schedule. When a video is uploaded to YouTube it is queued here with the same
  publish time; `publish_due` (run by the instagram workflow at each slot, and by every analytics run) posts it
  once that time has come, unless the owner pressed Stop.
- The video must be at a public URL for Instagram to fetch: the MP4 is put in the Worker's KV store for 6 hours
  under a random 32-hex key and served at <worker>/m/<key>.mp4. The repo stays private.
- Idempotent: the container id is saved before publishing; a run that died half-way is finished, never repeated.
"""
from __future__ import annotations

import base64
import hashlib
import json
import os
import secrets
import subprocess
import tempfile
import time
from pathlib import Path
from urllib.parse import urlparse

import requests

from .. import notify
from .youtube import _cf_kv

GRAPH = "https://graph.instagram.com"
VERSION = "v25.0"          # Graph API version (v25.0 announced 2026); bump when Meta retires it
REFRESH_DAYS = 20
METRICS = ["views", "reach", "likes", "comments", "shares", "saved", "total_interactions",
           "ig_reels_avg_watch_time", "ig_reels_video_view_total_time"]


class NotReady(RuntimeError):
    """Instagram is not connected (or connected to the wrong account)."""


# ---------------- config / KV ----------------

def _cfg() -> dict:
    from ..config import load
    return load().channel.get("instagram") or {}


def enabled() -> bool:
    return bool(_cfg().get("enabled"))


def _kv_target() -> tuple[str, str, str] | None:
    tok = os.environ.get("CLOUDFLARE_API_TOKEN", "").strip()
    from ..config import load
    from ..state import State
    cfg = load()
    acc = (os.environ.get("CLOUDFLARE_ACCOUNT_ID") or str(cfg.pipeline.get("cloudflare_account_id", ""))).strip()
    ns = State(cfg.path("state_db")).get_setting("cf_kv_namespace")
    return (tok, acc, ns) if tok and acc and ns else None


def _kv_put(key: str, data: bytes | str, ttl: int | None = None) -> None:
    t = _kv_target()
    if not t:
        raise NotReady("the studio Worker's store is not configured")
    tok, acc, ns = t
    params = {"expiration_ttl": ttl} if ttl else None
    r = requests.put(f"https://api.cloudflare.com/client/v4/accounts/{acc}/storage/kv/namespaces/{ns}/values/{key}",
                     headers={"Authorization": f"Bearer {tok}"}, params=params,
                     data=data if isinstance(data, bytes) else data.encode(), timeout=120)
    if r.status_code != 200:
        raise RuntimeError(f"KV write {key}: {r.status_code} {r.text[:200]}")


def _key() -> bytes:
    return hashlib.sha256(("ig-token-v1:" + os.environ["YT_CLIENT_SECRET"]).encode()).digest()


def _open(sealed: str) -> str:
    from cryptography.hazmat.primitives.ciphers.aead import AESGCM
    raw = base64.b64decode(sealed)
    return AESGCM(_key()).decrypt(raw[:12], raw[12:], None).decode()


def _seal(text: str) -> str:
    from cryptography.hazmat.primitives.ciphers.aead import AESGCM
    iv = os.urandom(12)
    return base64.b64encode(iv + AESGCM(_key()).encrypt(iv, text.encode(), None)).decode()


# ---------------- login ----------------

_CACHE: dict = {}


def token(refresh: bool = True) -> tuple[str, dict]:
    """-> (access token, account info). Refreshes the 60-day token when fewer than 20 days remain."""
    if "tok" in _CACHE:
        return _CACHE["tok"], _CACHE["acc"]
    sealed, acc = _cf_kv("ig_token.enc"), _cf_kv("ig_account")
    if not sealed or not acc:
        raise NotReady("Instagram is not connected yet: send /iglogin to the studio bot")
    tok, acc = _open(sealed), json.loads(acc)
    want = str(_cfg().get("handle", "")).lstrip("@").lower()
    if want and str(acc.get("username", "")).lower() != want:
        raise NotReady(f"the Instagram login is for @{acc.get('username')}, not @{want}: send /iglogin")
    left = float(acc.get("expires_at", 0)) - time.time()
    if left <= 0:
        raise NotReady("the Instagram login expired: send /iglogin to the studio bot")
    if refresh and left < REFRESH_DAYS * 86400 and time.time() - float(acc.get("at_ts", 0)) > 86400:
        r = requests.get(f"{GRAPH}/refresh_access_token", timeout=30,
                         params={"grant_type": "ig_refresh_token", "access_token": tok})
        if r.status_code == 200 and r.json().get("access_token"):
            tok = r.json()["access_token"]
            acc = {**acc, "expires_at": time.time() + int(r.json().get("expires_in", 5184000)), "at_ts": time.time(),
                   "refreshed": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())}
            _kv_put("ig_token.enc", _seal(tok))
            _kv_put("ig_account", json.dumps(acc))
    _CACHE.update(tok=tok, acc=acc)
    return tok, acc


def _api(method: str, path: str, tok: str, **params) -> dict:
    r = requests.request(method, f"{GRAPH}/{VERSION}/{path}", timeout=60,
                         **({"data": {**params, "access_token": tok}} if method == "POST"
                            else {"params": {**params, "access_token": tok}}))
    body = r.json() if r.content else {}
    if r.status_code != 200 or "error" in body:
        err = body.get("error") or {}
        raise RuntimeError(f"Instagram {path.split('/')[-1]}: {err.get('message') or r.text[:200]} "
                           f"(code {err.get('code')}/{err.get('error_subcode')})")
    return body


def whoami() -> dict:
    tok, acc = token()
    me = _api("GET", "me", tok, fields="user_id,username,account_type,media_count")
    lim = {}
    try:
        lim = _api("GET", f"{acc['user_id']}/content_publishing_limit", tok, fields="quota_usage,config")
    except RuntimeError as e:
        lim = {"error": str(e)}
    return {"account": me, "expires": time.strftime("%Y-%m-%d", time.gmtime(float(acc["expires_at"]))), "limit": lim}


# ---------------- queue ----------------

def _ensure(state) -> None:
    with state.tx() as db:
        db.execute("CREATE TABLE IF NOT EXISTS ig_posts (job_id TEXT PRIMARY KEY, status TEXT NOT NULL, "
                   "publish_at TEXT, container_id TEXT, media_id TEXT, permalink TEXT, error TEXT, at REAL NOT NULL)")
        db.execute("CREATE TABLE IF NOT EXISTS ig_metrics (media_id TEXT NOT NULL, job_id TEXT, age_hours REAL "
                   "NOT NULL, data TEXT NOT NULL, at REAL NOT NULL)")


def queue(state, job_id: str, publish_at: str | None) -> None:
    """Called after the YouTube upload. Posts later, at publish_at (UTC ISO), via publish_due."""
    if not enabled():
        return
    _ensure(state)
    with state.tx() as db:
        db.execute("INSERT OR IGNORE INTO ig_posts(job_id, status, publish_at, at) VALUES (?,?,?,?)",
                   (job_id, "pending", publish_at or time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()), time.time()))


def hold(state, job_id: str) -> str:
    """Owner pressed Stop. -> 'held' | 'posted' (already public on Instagram) | 'none'."""
    _ensure(state)
    row = state.db.execute("SELECT status FROM ig_posts WHERE job_id=?", (job_id,)).fetchone()
    if not row:
        return "none"
    if row["status"] in ("posted", "publishing"):
        return "posted"
    with state.tx() as db:
        db.execute("UPDATE ig_posts SET status='held' WHERE job_id=?", (job_id,))
    return "held"


def caption(meta: dict, extra_tag: str = "#secretsmartstuff") -> str:
    """Instagram caption from the YouTube metadata: title, the explanation, sources (domains), AI note,
    and at most 5 hashtags (Instagram's limit)."""
    desc = str(meta.get("description", ""))
    paras = [p.strip() for p in desc.split("\n\n") if p.strip()]
    body = paras[0] if paras else ""
    urls = [w.strip("-• ") for w in desc.split() if w.strip("-• ").startswith("http")]
    hosts: list[str] = []
    for u in urls:
        h = urlparse(u).netloc.replace("www.", "")
        if h and h not in hosts:
            hosts.append(h)
    ai = next((p for p in paras if p.lower().startswith("visuals are ai")), "Visuals are AI-generated illustrations; "
              "narration is an AI voice.")
    tags = [w for w in dict.fromkeys(w for w in desc.split() if w.startswith("#")) if w != extra_tag]
    tags = tags[:4] + [extra_tag]
    out = [str(meta.get("title", "")).strip(), body]
    if hosts:
        out.append("Sources: " + ", ".join(hosts[:6]))
    out += [ai, " ".join(tags)]
    return "\n\n".join(x for x in out if x)[:2200]


def _fetch(job_id: str, into: Path) -> tuple[Path, dict]:
    """The final MP4 and metadata from the job's review release (works on any runner)."""
    into.mkdir(parents=True, exist_ok=True)
    local = Path("build") / job_id
    if (local / "final.mp4").exists() and (local / "metadata.json").exists():
        return local / "final.mp4", json.loads((local / "metadata.json").read_text())
    subprocess.run(["gh", "release", "download", f"review-{job_id}", "-p", "final.mp4", "-p", "metadata.json",
                    "-D", str(into), "--clobber"], check=True, capture_output=True)
    return into / "final.mp4", json.loads((into / "metadata.json").read_text())


def _worker_url(state) -> str:
    u = state.get_setting("worker_url")
    if not u:
        raise NotReady("studio Worker URL unknown (run setup_studio)")
    return u.rstrip("/")


def post(state, job_id: str) -> dict:
    """Post one queued video now. Safe to call again after a crash."""
    _ensure(state)
    tok, acc = token()
    uid = acc["user_id"]
    row = state.db.execute("SELECT * FROM ig_posts WHERE job_id=?", (job_id,)).fetchone()
    if row and row["status"] == "posted":
        return {"job": job_id, "permalink": row["permalink"], "already": True}
    cont = row["container_id"] if row else None
    if cont:      # a previous run got this far: finish it, never post twice
        st = _api("GET", cont, tok, fields="status_code,status")
        if st.get("status_code") == "PUBLISHED":
            return _record_published(state, job_id, tok, uid, None, cont)
        if st.get("status_code") in ("ERROR", "EXPIRED"):
            cont = None
    if not cont:
        with tempfile.TemporaryDirectory() as tmp:
            mp4, meta = _fetch(job_id, Path(tmp))
            key = secrets.token_hex(16)
            _kv_put(f"media:{key}", mp4.read_bytes(), ttl=6 * 3600)
            url = f"{_worker_url(state)}/m/{key}.mp4"
            cont = _api("POST", f"{uid}/media", tok, media_type="REELS", video_url=url, caption=caption(meta),
                        share_to_feed="true")["id"]
        with state.tx() as db:
            db.execute("INSERT INTO ig_posts(job_id, status, container_id, at) VALUES (?,?,?,?) ON CONFLICT(job_id) "
                       "DO UPDATE SET status='publishing', container_id=excluded.container_id, error=NULL",
                       (job_id, "publishing", cont, time.time()))
    for _ in range(60):                   # Instagram processes the video: usually 30 s - 3 min
        st = _api("GET", cont, tok, fields="status_code,status")
        code = st.get("status_code")
        if code == "FINISHED":
            break
        if code == "PUBLISHED":
            return _record_published(state, job_id, tok, uid, None, cont)
        if code in ("ERROR", "EXPIRED"):
            with state.tx() as db:
                db.execute("UPDATE ig_posts SET status='failed', container_id=NULL, error=? WHERE job_id=?",
                           (str(st.get("status"))[:500], job_id))
            raise RuntimeError(f"Instagram could not process the video: {st.get('status')}")
        time.sleep(10)
    else:
        raise RuntimeError("Instagram is still processing the video after 10 minutes; will retry next run")
    media = _api("POST", f"{uid}/media_publish", tok, creation_id=cont)["id"]
    return _record_published(state, job_id, tok, uid, media, cont)


def _record_published(state, job_id, tok, uid, media_id, cont) -> dict:
    if not media_id:   # published by an earlier run that died before saving the id: find it
        recent = _api("GET", f"{uid}/media", tok, fields="id,timestamp", limit=5).get("data") or []
        media_id = recent[0]["id"] if recent else None
    info = _api("GET", media_id, tok, fields="permalink,timestamp,media_product_type") if media_id else {}
    with state.tx() as db:
        db.execute("UPDATE ig_posts SET status='posted', media_id=?, permalink=?, error=NULL, at=? WHERE job_id=?",
                   (media_id, info.get("permalink"), time.time(), job_id))
    return {"job": job_id, "media_id": media_id, "permalink": info.get("permalink")}


def publish_due(state, grace_min: int = 5) -> dict:
    """Post every queued video whose time has come (skips videos the owner stopped on YouTube)."""
    if not enabled():
        return {"skipped": "instagram disabled"}
    _ensure(state)
    now = time.time()
    done, problems = [], []
    rows = state.db.execute("SELECT p.job_id, p.publish_at, p.status, u.status AS yt FROM ig_posts p "
                            "LEFT JOIN uploads u ON u.job_id=p.job_id WHERE p.status IN ('pending','publishing')"
                            ).fetchall()
    import datetime as dt
    for r in rows:
        if r["yt"] == "held":
            hold(state, r["job_id"])
            continue
        due = dt.datetime.fromisoformat((r["publish_at"] or "1970-01-01T00:00:00Z").replace("Z", "+00:00")).timestamp()
        if r["status"] == "pending" and now < due - grace_min * 60:
            continue
        try:
            res = post(state, r["job_id"])
            done.append(res)
            if not res.get("already"):
                notify.send(state, f"📸 On Instagram now: {res.get('permalink') or '(link pending)'}", silent=True)
        except NotReady as e:
            problems.append(str(e))
            notify.send(state, f"⚠️ Instagram post waiting: {notify.esc(str(e))}")
            break
        except Exception as e:  # noqa: BLE001
            problems.append(f"{r['job_id']}: {e}")
            with state.tx() as db:
                db.execute("UPDATE ig_posts SET error=? WHERE job_id=?", (str(e)[:500], r["job_id"]))
            tries = state.db.execute("SELECT COUNT(*) AS n FROM events WHERE job_id=? AND message LIKE 'instagram:%'",
                                     (r["job_id"],)).fetchone()["n"]
            state.log(f"instagram: {e}", "warn", r["job_id"])
            if tries in (0, 3):     # tell the owner on the first failure and if it keeps failing
                notify.send(state, f"⚠️ Instagram post failed for {r['job_id']}: {notify.esc(str(e)[:300])}. "
                                   "I'll retry on the next run.")
    return {"posted": done, "problems": problems}


# ---------------- numbers ----------------

def snapshot(state) -> dict:
    """Insights for every posted Reel, stored with its age (hours since posting)."""
    if not enabled():
        return {"skipped": "instagram disabled"}
    _ensure(state)
    rows = state.db.execute("SELECT job_id, media_id FROM ig_posts WHERE status='posted' AND media_id IS NOT NULL"
                            ).fetchall()
    if not rows:
        return {"reels": 0}
    tok, _ = token()
    import datetime as dt
    out = 0
    for r in rows:
        info = _api("GET", r["media_id"], tok, fields="timestamp")
        posted = dt.datetime.strptime(info["timestamp"], "%Y-%m-%dT%H:%M:%S%z").timestamp()
        metrics, data = list(METRICS), {}
        for _ in range(len(METRICS)):
            try:
                body = _api("GET", f"{r['media_id']}/insights", tok, metric=",".join(metrics))
                for m in body.get("data") or []:
                    v = (m.get("values") or [{}])[0].get("value", m.get("total_value", {}).get("value"))
                    data[m["name"]] = v
                break
            except RuntimeError as e:     # a metric Instagram does not offer for this media: drop it, retry
                bad = next((m for m in metrics if m in str(e)), None)
                if not bad:
                    data["error"] = str(e)[:300]
                    break
                metrics.remove(bad)
        with state.tx() as db:
            db.execute("INSERT INTO ig_metrics(media_id, job_id, age_hours, data, at) VALUES (?,?,?,?,?)",
                       (r["media_id"], r["job_id"], (time.time() - posted) / 3600, json.dumps(data), time.time()))
        out += 1
    return {"reels": out}


def near(state, job_id: str, hours: float) -> dict | None:
    """Instagram numbers for a job at (about) the given age, for the post-mortems."""
    try:
        _ensure(state)
        row = state.db.execute("SELECT age_hours, data FROM ig_metrics WHERE job_id=? AND age_hours >= ? "
                               "ORDER BY age_hours ASC LIMIT 1", (job_id, hours)).fetchone()
    except Exception:  # noqa: BLE001
        return None
    return json.loads(row["data"]) | {"age_hours": round(row["age_hours"], 1)} if row else None
