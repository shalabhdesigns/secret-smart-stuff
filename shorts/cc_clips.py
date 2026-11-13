"""Daily scan for GTA videos we may legally reuse (owner, 14 Nov 2026).

YouTube's own Creative Commons filter (videoLicense=creativeCommon). A CC BY label only licenses the UPLOADER's own
work: their gameplay capture, voice and edit. It never clears Rockstar's trailers or anyone else's clips inside it, so:
- "gameplay"  = the uploader's own gameplay capture (usable with credit; Rockstar's fan-video policy still applies);
- "trailer-based" = built from Rockstar trailers/official clips -> treat as an official excerpt (a few seconds,
  with our commentary), better taken from Rockstar's own media page;
- "never" = leaks, early copies/unboxings before launch, cheats/exploits.
New finds go to Telegram once a day. Every use needs the CC BY credit line in the description.
"""
from __future__ import annotations

import json
import re
import time

import requests

QUERIES = ["GTA 6 gameplay", "GTA 6", "GTA VI", "Grand Theft Auto VI gameplay", "GTA 6 Vice City", "GTA 6 physics",
           "GTA 6 funny moments", "GTA 6 map"]
NEVER = ("leak", "vazou", "vaz", "early unboxing", "early copy", "unboxing", "mod menu", "cheat", "glitch", "teleport")
TRAILER = ("trailer", "extended look", "tráiler", "detalles", "details", "explained", "breakdown", "everything we know")


def _dur(d: str) -> int:
    m = re.match(r"PT(?:(\d+)H)?(?:(\d+)M)?(?:(\d+)S)?", d or "")
    return (int(m.group(1) or 0) * 3600 + int(m.group(2) or 0) * 60 + int(m.group(3) or 0)) if m else 0


def classify(title: str, published: str, launch: str = "2026-11-19") -> str:
    t = title.lower()
    if any(k in t for k in NEVER) and published < launch:
        return "never"
    if any(k in t for k in ("cheat", "mod menu", "glitch", "teleport", "leak")):
        return "never"
    if published < launch and ("gta 6" in t or "gta vi" in t or "gta6" in t):
        return "trailer-based"          # before launch, GTA 6 footage can only be Rockstar's (or leaked)
    if any(k in t for k in TRAILER):
        return "trailer-based"
    return "gameplay"


def scan(token: str, after: str = "2026-11-01T00:00:00Z") -> list[dict]:
    H = {"Authorization": f"Bearer {token}"}
    ids = set()
    for q in QUERIES:
        r = requests.get("https://www.googleapis.com/youtube/v3/search", headers=H, timeout=30, params={
            "part": "snippet", "q": q, "type": "video", "videoLicense": "creativeCommon", "maxResults": 50,
            "order": "viewCount", "publishedAfter": after})
        if r.status_code == 200:
            ids |= {it["id"]["videoId"] for it in r.json().get("items", [])}
    rows = []
    idl = sorted(ids)
    for i in range(0, len(idl), 50):
        r = requests.get("https://www.googleapis.com/youtube/v3/videos", headers=H, timeout=30, params={
            "part": "snippet,status,contentDetails,statistics", "id": ",".join(idl[i:i + 50])})
        for v in r.json().get("items", []) if r.status_code == 200 else []:
            sn, st = v["snippet"], v["status"]
            if st.get("license") != "creativeCommon":
                continue
            pub = sn.get("publishedAt", "")[:10]
            rows.append({"id": v["id"], "url": f"https://www.youtube.com/watch?v={v['id']}", "title": sn["title"],
                         "channel": sn.get("channelTitle"), "published": pub, "seconds": _dur(v["contentDetails"].get("duration")),
                         "views": int(v.get("statistics", {}).get("viewCount", 0) or 0),
                         "class": classify(sn["title"], pub),
                         "credit": f"Clip: \"{sn['title']}\" by {sn.get('channelTitle')} "
                                   f"(https://www.youtube.com/watch?v={v['id']}), CC BY 3.0, edited"})
    rows.sort(key=lambda r: -r["views"])
    return rows


def daily(state) -> dict:
    """Once per IST day: refresh the library; tell the owner about new usable finds."""
    from .publish.youtube import access_token
    from . import notify
    today = time.strftime("%Y-%m-%d", time.gmtime(time.time() + 5.5 * 3600))
    if state.get_setting("cc_scan_day") == today:
        return {"skipped": "already today"}
    rows = scan(access_token())
    old = json.loads(state.get_setting("cc_library_json") or "{}").get("rows", [])
    seen = {r["id"] for r in old}
    new = [r for r in rows if r["id"] not in seen and r["class"] == "gameplay"]
    keep = {r["id"]: r for r in old + rows}
    state.set_setting("cc_library_json", json.dumps({"at": time.time(), "rows": list(keep.values())}))
    state.set_setting("cc_scan_day", today)
    if new:
        notify.send(state, "🎬 New Creative Commons GTA clips (creator's own gameplay; check before use):\n" + "\n".join(
            f"• {notify.esc(r['title'][:70])} ({r['views']:,} views) {r['url']}" for r in new[:6]), silent=True)
    return {"found": len(rows), "new_gameplay": len(new)}
