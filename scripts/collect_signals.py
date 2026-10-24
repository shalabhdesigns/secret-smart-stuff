#!/usr/bin/env python3
"""Stage A helper: collect public competitor Shorts listings and rank outliers.

Runs on GitHub Actions (open network). Uses yt-dlp to read PUBLIC channel
listings only - no login, no cookies, no private data. Ranks each Short by its
multiple over that channel's own median views (the youtube-agent-skill
`/yt-viral` method), so the signal is about the idea, not the channel's size.

Output: data/signals.json = {"collected_at", "all_titles": [...], "outliers": [...]}
If yt-dlp fails (YouTube changes pages often), the previous signals file is kept
and the pipeline continues without fresh signals.
"""
from __future__ import annotations

import json
import statistics
import subprocess
import sys
import time
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "data" / "signals.json"


def listing(handle: str, limit: int = 300) -> list[dict]:
    url = f"https://www.youtube.com/{handle}/shorts"
    p = subprocess.run(["yt-dlp", "--flat-playlist", "-J", "--playlist-end", str(limit), url],
                       capture_output=True, text=True, timeout=300)
    if p.returncode != 0:
        raise RuntimeError(p.stderr.strip()[-300:])
    entries = json.loads(p.stdout).get("entries") or []
    return [{"channel": handle, "title": e.get("title"), "views": e.get("view_count"),
             "url": e.get("url") or f"https://youtube.com/shorts/{e.get('id')}"}
            for e in entries if e.get("title")]


def main() -> int:
    comps = yaml.safe_load((ROOT / "config" / "channel.yaml").read_text()).get("competitors", [])
    all_rows, errors = [], []
    for c in comps:
        try:
            all_rows += listing(c["handle"])
        except Exception as e:  # noqa: BLE001
            errors.append(f"{c['handle']}: {e}")
    if not all_rows:
        print("no signals collected; keeping previous file", errors, file=sys.stderr)
        return 0
    outliers = []
    for ch in {r["channel"] for r in all_rows}:
        rows = [r for r in all_rows if r["channel"] == ch and isinstance(r["views"], int)]
        if len(rows) < 4:
            continue
        med = statistics.median(r["views"] for r in rows) or 1
        for r in rows:
            mult = r["views"] / med
            if mult >= 2.0:
                outliers.append(r | {"multiple": round(mult, 1)})
    outliers.sort(key=lambda r: -r["multiple"])
    OUT.parent.mkdir(exist_ok=True)
    OUT.write_text(json.dumps({"collected_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
                               "errors": errors, "all_titles": [{"channel": r["channel"], "title": r["title"]}
                                                                for r in all_rows],
                               "outliers": outliers[:60]}, indent=1, ensure_ascii=False))
    print(f"signals: {len(all_rows)} titles, {len(outliers)} outliers, errors: {errors}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
