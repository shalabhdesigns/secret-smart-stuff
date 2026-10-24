# Operations Guide

## Daily rhythm (automatic)

| Time (IST) | Workflow | What happens |
|---|---|---|
| 05:47 | `produce` | Refresh competitor signals → top up topic backlog → make one Short → open a review issue |
| when you comment | `review` | `approve` → upload private + schedule · `reject: …` · `fix: …` |
| every 6 h | `analytics` | Pull YouTube Analytics for uploaded Shorts, update pillar insights |
| 21:53 | `summary` | Comment on the "Daily summary" issue: videos, failures, spend |

Times are slightly off the hour on purpose. GitHub delays jobs scheduled exactly on the hour.
Even so, any run can start late.

## Your weekly 3–7 hours

- **Daily, 2–5 minutes:** watch the review video on your phone and reply `approve`, `reject: reason` or `fix: change`.
- **Weekly, about 30 minutes:**
  - Read the summary issue.
  - In YouTube Studio, check "viewed vs swiped away" for the week's Shorts. That number is not in the API.
  - Reply to a few comments.
- **Monthly, about 1 hour:**
  - Check `data/insights.json` (on the `state` branch).
  - Adjust pillar shares or hooks in `config/channel.yaml` if the data is clear.

## How to…

| Task | How |
|---|---|
| **Pause everything** | Repo → Actions → each workflow → "…" → **Disable workflow**. Or set the variable `SHORTS_MODE=dry_run` (no spending, no uploads). |
| **Resume** | Enable the workflows again and set `SHORTS_MODE=live`. |
| **Make a Short on a chosen topic** | Actions → produce → Run workflow → enter the topic ID (from `python -m shorts.cli topics`). |
| **Change budget limits** | Edit `config/pipeline.yaml` → `budget_usd`. When a limit is hit, production pauses and an `alert` issue opens. |
| **Change posting time** | `config/pipeline.yaml` → `schedule.publish_slots_utc` (UTC). 13:30 UTC = 19:00 IST. |
| **Change the voice** | `config/channel.yaml` → `voice.voice_id`. |
| **Swap the image model** | `config/pipeline.yaml` → `providers.images.model` (for example `flux-2-pro`). |
| **Switch to automatic publishing** | After about 30 good Shorts: set `approval.mode: auto` in `config/pipeline.yaml`. Shorts with review score ≥ 8 and no image flags publish on their own. The rest still wait for you. The review issue is opened either way, so you can always see what went out. |
| **An upload says "started but did not confirm"** | Check YouTube Studio. If the video IS there: `python -m shorts.cli upload-resolve JOB --video-id ID`. If not: `python -m shorts.cli upload-resolve JOB`, then comment `approve` again. This guard stops double uploads. |
| **Login expired** (`refresh token expired`) | Re-run `scripts/youtube_auth.py` and update the `YT_REFRESH_TOKEN` secret. Also check the consent screen still says "In production". |
| **Look at everything locally** | `pip install -r requirements.txt`, then `python -m shorts.cli status / topics / summary` (dry-run needs no keys). |

## Troubleshooting

| Symptom | Likely cause | Fix |
|---|---|---|
| No review issue in the morning | Run delayed, failed, or budget pause | Check Actions for a red run, and look for an `alert` issue |
| `alert`: "script has N words" or "review score X" | Script failed quality gates 3 times | Normal. The topic waits for you. Reject it or comment on it. |
| `alert`: "BFL account has no credits left" | Image credit ran out | Top up at dashboard.bfl.ai |
| `alert`: "ElevenLabs 401/quota" | Key revoked or monthly credits used up | Check the ElevenLabs plan or key |
| Signals step says "skipped" | YouTube changed its pages, so yt-dlp broke | Nothing breaks. Discovery runs without fresh signals. Update yt-dlp in `requirements.txt`. |
| Same kind of topic every day | Pillar shares drifted, or the backlog is full of one pillar | Reject a few, or edit the pillar shares |

## Where things are

- **Code:** `shorts/` (pipeline, providers, render, QA, publish, analytics)
- **Settings:** `config/channel.yaml` (identity and content rules), `config/pipeline.yaml` (budgets, schedule, providers)
- **State (database, signals, insights):** the `state` branch, updated after every run
- **Review videos:** repo **Releases** (pre-releases named `review-<job>`)
- **Decisions and research:** `docs/` and `research/`
