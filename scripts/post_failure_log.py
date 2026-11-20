#!/usr/bin/env python3
"""On a crashed run, post the last lines of its output as a GitHub issue (secrets masked) so Claude can debug
without access to the Actions log viewer."""
import os
import subprocess
import sys
from pathlib import Path

log = Path(sys.argv[1])
title = sys.argv[2] if len(sys.argv) > 2 else "Run failed"
text = log.read_text(errors="replace") if log.exists() else "(no output captured)"
for k, v in os.environ.items():
    if v and len(v) >= 8 and any(s in k for s in ("KEY", "TOKEN", "SECRET")):
        text = text.replace(v, "***")
tail = "\n".join(text.splitlines()[-80:])
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from shorts.notify import quiet_now  # noqa: E402
if quiet_now():   # owner away: no issue (GitHub would email him); Claude's daily runs read failed runs' logs instead
    print(tail[-4000:])
    sys.exit(0)
subprocess.run(["gh", "label", "create", "alert", "--color", "B60205"], capture_output=True)
subprocess.run(["gh", "issue", "create", "--label", "alert", "--title", title[:120],
                "--body", f"```\n{tail[-60000:]}\n```"], check=False)
