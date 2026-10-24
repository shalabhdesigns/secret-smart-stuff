#!/usr/bin/env python3
"""Apply the owner's comment on a review issue (runs inside the review workflow).

Inputs come from environment variables set by the workflow (never inlined into a
shell): COMMENT, ISSUE_BODY, ISSUE. Commands (first line of the comment):
  approve            -> upload as private + schedule for the next free slot
  reject: <reason>   -> topic rejected; reason recorded for future scoring
  fix: <change>      -> one bounded rewrite, re-render, new review posted on the issue
"""
from __future__ import annotations

import os
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from shorts.cli import next_slot  # noqa: E402
from shorts.config import load    # noqa: E402
from shorts.pipeline import Pipeline  # noqa: E402


def gh(*args: str) -> str:
    return subprocess.run(["gh", *args], capture_output=True, text=True, check=True).stdout


def reply(issue: str, text: str) -> None:
    gh("issue", "comment", issue, "--body", text)


def main() -> int:
    comment = (os.environ.get("COMMENT") or "").strip()
    body = os.environ.get("ISSUE_BODY") or ""
    issue = os.environ["ISSUE"]
    m = re.search(r"<!-- job:([a-z0-9-]+) -->", body)
    if not m:
        print("no job marker in issue body; ignoring")
        return 0
    job = m.group(1)
    first = comment.splitlines()[0].strip() if comment else ""
    cmd = re.match(r"^(approve|reject|fix)\b\s*:?\s*(.*)$", first, re.I)
    if not cmd:
        print("comment is not a command; ignoring")
        return 0
    decision, note = cmd.group(1).lower(), cmd.group(2).strip()
    p = Pipeline(load())
    # the MP4 and files live in the review pre-release; fetch them back into build/<job>/
    d = ROOT / "build" / job
    d.mkdir(parents=True, exist_ok=True)
    subprocess.run(["gh", "release", "download", f"review-{job}", "--dir", str(d), "--clobber"], check=False)

    if decision == "reject":
        p.decide(job, "reject", note)
        reply(issue, f"❌ Rejected. Reason saved for future topic scoring: _{note or 'none given'}_")
        gh("issue", "close", issue)
    elif decision == "fix":
        if not note:
            reply(issue, "Please say what to change, e.g. `fix: shorten the second scene`.")
            return 0
        p.decide(job, "fix", note)
        p.produce(p.state.get_job(job)["topic_id"])
        status = p.state.get_job(job)["status"]
        if status == "review":
            subprocess.run([str(ROOT / "scripts" / "open_review.sh"), job], check=True)
        else:
            reply(issue, f"⚠️ The fix did not pass checks ({status}): {p.state.get_job(job)['error']}")
    else:  # approve
        p.decide(job, "approve")
        if not p.cfg.live:
            reply(issue, "✅ Approved (dry-run mode, so nothing was uploaded).")
            return 0
        slot = next_slot(p)
        try:
            rec = p.publish(job, publish_at=slot)
            reply(issue, f"✅ Uploaded as **private**, scheduled to go public at **{slot}** (UTC).\n"
                         f"Link: {rec.get('url')}\n\nIf YouTube locks it as private (unverified API "
                         f"project), see docs/SETUP.md → 'Audit'.")
            gh("issue", "close", issue)
        except Exception as e:  # noqa: BLE001
            reply(issue, f"⚠️ Upload did not complete: {e}\n\nNothing was published. The video stays approved; "
                         f"comment `approve` again after fixing the cause.")
            p.state.set_job_status(job, "approved", str(e))
            return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
