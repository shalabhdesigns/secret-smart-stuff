# Operations Guide

## Daily rhythm (automatic)

| Time (IST) | Workflow | What happens |
|---|---|---|
| 05:47 | `produce` | Makes one Short. If it passes the final review it is uploaded private + scheduled for its slot (auto mode until 25 Nov 2026) and you get it in Telegram with a ⏸ Stop it button. If it fails, it is fixed or dropped and you are told. |
| 19:00 / 22:30 / 07:30 (the video's slot) | `instagram` | Posts the day's video as an Instagram Reel at the same time it goes public on YouTube. A Stop before then cancels it. |
| when you tap | `command` | ⏸ Stop it → keeps that video private · (manual mode) ✅ Approve / ✏️ Fix / 🗑 Drop |
| every 4 h + after each slot | `analytics` | YouTube Analytics for every video; confirms uploads went live; post-mortems at 48 h and 7 days (short Telegram note each) |
| Monday and Thursday 09:03 | `summary` | Learnings update: rules for the writer, topic guidance, proposals for you; `data/LEARNINGS.md` |

Times are slightly off the hour on purpose. GitHub delays jobs scheduled exactly on the hour, and any run can
start late.

## Your time

- **Daily, optional:** watch the new video in Telegram; tap ⏸ Stop it only if something is wrong.
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
| /iglogin | Connect or refresh the Instagram login (one tap; send it as a new message, not a reply) |
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
| **Instagram post failed / "send /iglogin"** | Send /iglogin. To post a published video now: `{"action":"ig_post","job":"<job>"}`. Check the login: `{"action":"ig_whoami"}`. |
| **"API access blocked" (code 200) / Meta blocked the app** | Retrying can't fix it. The system warns at queue time, and at the slot it sends the Reel + caption to Telegram to post by hand, with an "I posted it" button (`ig_manual`), so it is never posted twice. Fix: the owner logs in to facebook.com, developers.facebook.com and instagram.com, clears any Meta warning, then /iglogin. Resend the Reel: `{"action":"ig_hand","job":"<job>"}`. |
| **Dashboard numbers look wrong or old** | Press "Refresh now" on the dashboard (~3 min), or run the analytics workflow. Check "About the data" for what each number is based on. |
| **Enter a subscription, balance or revenue** | Dashboard → Costs & revenue / Credits & limits forms (saved to KV `manual.json`). |
| **Give published videos covers** | `{"action":"covers_backfill"}` (optional `"jobs":[...]`). YouTube is set by API. For Instagram, each cover comes to Telegram to set in the app (Reel → ⋯ → Edit → Edit cover). |
| **Post one Reel now / at its minute** | Run the `igpost` workflow with `job=<job>`. It waits for the publish time, posts, and records it in KV. |
| **A series of videos** | `{"action":"produce","topic":...,"topic_def":{...},"then":[next requests]}`. Each run queues the next. |
| **Stop a video already on Instagram** | The API can't hide it: delete it in the Instagram app. |
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
