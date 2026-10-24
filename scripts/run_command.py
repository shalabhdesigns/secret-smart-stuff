#!/usr/bin/env python3
"""Execute one request from commands/request.json (see .github/workflows/command.yml).

produce  -> make (or resume) one Short; open a review issue, or an alert issue with the error
approve / reject / fix -> same behaviour as the owner commenting on the review issue
Every outcome is reported on a GitHub issue so it can be read back without Actions access.
"""
from __future__ import annotations

import json
import os
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from shorts.config import load      # noqa: E402
from shorts.pipeline import Pipeline  # noqa: E402


def gh(*args: str, check: bool = True) -> str:
    return subprocess.run(["gh", *args], capture_output=True, text=True, check=check).stdout.strip()


def review_issue(job: str) -> str | None:
    out = gh("issue", "list", "--label", "review", "--state", "open", "--limit", "100",
             "--json", "number,body", "-q",
             f'.[] | select(.body | contains("<!-- job:{job} -->")) | .number', check=False)
    return out.splitlines()[0] if out else None


def alert(title: str, body: str) -> None:
    gh("label", "create", "alert", "--color", "B60205", check=False)
    gh("issue", "create", "--label", "alert", "--title", title, "--body", body)


def main(path: str) -> int:
    req = json.loads(Path(path).read_text())
    action = req.get("action")
    p = Pipeline(load())
    if action == "produce":
        tid = req.get("topic") or ""
        if not tid:
            if len(p.state.topics("shortlisted")) < 3:
                p.discover(8)
            t = p.next_topic()
            tid = t["id"] if t else ""
        if not tid:
            alert("Pipeline problem: no topic", "Discovery returned no usable topics.")
            return 1
        job = p.produce(tid)
        j = p.state.get_job(job)
        if j["status"] == "review":
            subprocess.run([str(ROOT / "scripts" / "open_review.sh"), job], check=True)
        else:
            ev = p.state.db.execute("SELECT message FROM events WHERE job_id=? ORDER BY at DESC LIMIT 8",
                                    (job,)).fetchall()
            alert(f"Pipeline problem: {job}",
                  f"<!-- job:{job} -->\nstatus: **{j['status']}** · last finished stage: `{j['stage']}`\n\n"
                  f"error: `{j['error']}`\n\nrecent events:\n" + "\n".join(f"- {r['message']}" for r in ev))
        return 0
    if action in ("approve", "reject", "fix"):
        job = req["job"]
        if not re.fullmatch(r"[a-z0-9-]+", job):
            raise SystemExit("bad job id")
        issue = review_issue(job)
        if not issue:
            alert(f"Pipeline problem: {job}", f"No open review issue found for job `{job}`.")
            return 1
        os.environ["COMMENT"] = f"{action}: {req.get('note', '')}".strip().rstrip(":")
        os.environ["ISSUE_BODY"] = f"<!-- job:{job} -->"
        os.environ["ISSUE"] = issue
        sys.path.insert(0, str(ROOT / "scripts"))
        import handle_review  # noqa: E402
        return handle_review.main()
    raise SystemExit(f"unknown action {action!r}")


if __name__ == "__main__":
    sys.exit(main(sys.argv[1]))
