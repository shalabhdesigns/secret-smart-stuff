#!/usr/bin/env python3
"""Build a `fetch` request from ElevenLabs generation ids, finding their newest signed URLs in a log.

The ElevenLabs signed URLs (2 h expiry) appear in the Claude session transcript after a
creative_get_generations / run-status call. This scans the transcript for the latest signed URL of
each generation id and writes commands/request.json for the runner's `fetch` action.

usage: el_fetch_request.py <transcript.jsonl> <release-name> name=GENERATION_ID [name=GENERATION_ID ...]
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def latest_urls(transcript: str, gen_ids: list[str]) -> dict[str, str]:
    text = Path(transcript).read_text(errors="ignore")
    found: dict[str, tuple[str, str]] = {}
    pat = re.compile(r"https://storage\.googleapis\.com/xi-backend/[^\"\\\s]*?/content_generation/[A-Za-z0-9]+/"
                     r"([A-Za-z0-9]+)/content\.(png|mp3|mp4|wav|jpg|webp)\?[^\"\\\s]+")
    for m in pat.finditer(text):
        gid = m.group(1)
        if gid not in gen_ids:
            continue
        url = m.group(0)
        date = re.search(r"X-Goog-Date=(\d{8}T\d{6}Z)", url)
        stamp = date.group(1) if date else ""
        if gid not in found or stamp >= found[gid][0]:
            found[gid] = (stamp, url)
    return {g: u for g, (_, u) in found.items()}


def main() -> int:
    transcript, name, *pairs = sys.argv[1:]
    wanted = dict(p.split("=", 1) for p in pairs)
    urls = latest_urls(transcript, list(wanted.values()))
    missing = [n for n, g in wanted.items() if g not in urls]
    if missing:
        print("missing:", missing)
        return 1
    files = {n: urls[g] for n, g in wanted.items()}
    (ROOT / "commands" / "request.json").write_text(json.dumps({"action": "fetch", "name": name, "files": files}))
    print(f"{len(files)} files -> media-{name}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
