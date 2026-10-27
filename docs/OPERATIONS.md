# Operations Guide

## Daily rhythm (automatic)

| Time (IST) | Workflow | What happens |
|---|---|---|
| 05:47 | `produce` | Refreshes competitor signals, tops up the topic backlog, makes one Short and sends it to your Telegram. It skips the day while a video is still waiting for you. |
| when you tap | `command` | ✅ Approve → upload as private, scheduled for its slot · ✏️ Fix → minimal edit and a new version · 🗑 Drop → reason saved |
| every 4 h + after each slot | `analytics` | YouTube Analytics for this channel's Shorts; checks uploads went live |
| Monday 09:03 | `summary` | Weekly learning report (what worked, by pillar and publish time) |

Times are slightly off the hour on purpose. GitHub delays jobs scheduled exactly on the hour, and any run can
start late.

## Your time

- **Daily, 2–5 minutes:** watch the video in Telegram, then tap ✅, ✏️ (say what to change) or 🗑.
- **Weekly, about 15 minutes:**
  - In YouTube Studio, check "viewed vs swiped away" for the week's Shorts. That number is not in the API.
  - Reply to a few comments.
- **Monthly:** the dashboard (`/dash` in the bot) shows cost, views and what is working.

## Bot commands

| Command | What it does |
|---|---|
| /status | What is waiting, recent uploads, spend |
| /produce | Make an extra video now |
| /ytlogin | Connect or refresh the YouTube login (one tap) |
| /dash | Dashboard link (login code sent to Telegram) |
| /revenue 2026-11 12.50 | Record revenue for a month |

## How to…

| Task | How |
|---|---|
| **Pause everything** | Set the repo variable `SHORTS_MODE=dry_run` (no spending, no uploads), or disable the `produce` workflow. |
| **Resume** | Set `SHORTS_MODE=live` and enable the workflows again. |
| **Make a Short on a chosen topic** | Claude pushes `{"action":"produce","topic":"<id>"}` to `commands/request.json`. Optionally add `angle` / `question`. |
| **Change budget limits** | `config/pipeline.yaml` → `budget_usd`. When a limit is hit, production pauses and resumes on the next run. |
| **Change posting times** | `config/experiments.yaml` (the publish-time experiment chooses the slot). |
| **Change the voice** | `config/channel.yaml` → `voice.voice_id`. |
| **"YouTube login expired" / "login is for another channel"** | Send /ytlogin to the bot and pick Secret Smart Stuff (`docs/SETUP.md`). |
| **An upload says "started but did not confirm"** | Check YouTube Studio. If the video IS there: `python -m shorts.cli upload-resolve JOB --video-id ID`. If not: `python -m shorts.cli upload-resolve JOB`, then approve again. This guard stops double uploads. |
| **Redeploy the studio Worker** | Push `{"action":"setup_studio"}`. |

## Troubleshooting

| Symptom | Likely cause | Fix |
|---|---|---|
| No video in the morning | A video is still waiting for review, the run was delayed or failed, or the budget paused it | /status; check Actions for a red run and look for an `alert` |
| "BFL account has no credits left" | Image credit ran out | Top up at dashboard.bfl.ai |
| "ElevenLabs 401/quota" | Key revoked or monthly credits used up | Check the ElevenLabs plan or key |
| Signals step says "skipped" | yt-dlp broke on a YouTube change | Nothing breaks. Update yt-dlp in `requirements.txt`. |
| Same kind of topic every day | Pillar shares drifted | Drop a few with a reason, or edit the pillar shares |

## Where things are

- **Code:** `shorts/` (pipeline, providers, render, QA, publish, analytics), `worker/` (studio), `scripts/`.
- **Settings:** `config/channel.yaml`, `config/pipeline.yaml`, `config/experiments.yaml`.
- **State (database, signals, insights):** the `state` branch, updated after every run.
- **Review videos:** repo Releases (pre-releases named `review-<job>`).
- **Decisions, lessons and research:** `docs/` and `research/`.
