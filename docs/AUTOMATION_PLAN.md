# Automation plan: daily, hands-off production with phone approval

Written 25 Oct 2026, after the owner approved onigiri v9.
Status markers:
- ✅ built and tested on the cloud runner
- 🟡 built, not yet tested live
- ⬜ to build
- 🔑 needs the owner

## 1. What already exists and is verified

| Part | Status | Evidence |
|---|---|---|
| Runs fully in the cloud (GitHub Actions, private repo); laptop not needed | ✅ | every onigiri version was made on GitHub's machines |
| Topic discovery, scoring, backlog | ✅ | `discover`, `SCORE`; 77/100 for onigiri |
| Script with web research, sources, independent review, auto-repair, topic drop | ✅ | v1–v9 runs |
| Images, image checks (text/logo, match-the-words, numbered markers) | ✅ | v7–v9 |
| Voice (Alice), music library, sound effects, numpy mixer | ✅ | v9 re-render: music to the last frame, −14.4 LUFS |
| Renderer (beats, camera moves, captions, pops, markers, pointers, seamless loop) | ✅ | v9 |
| Automatic media QA | ✅ | 13 checks on every video |
| Review bundle (MP4 + notes + saved media for free re-renders) | ✅ | release `review-onigiri-rice-ball-wrapper-v9` |
| Approve → YouTube upload as private + scheduled publish, duplicate guard (SHA-256) | ✅ | `zWJFcVGDdRc` scheduled 25 Oct 13:30 UTC |
| Budget guard (per video, per day, per month) + resume after budget pause | ✅ | v6 pause/resume |
| State tracking (SQLite: topics, jobs, costs, uploads, metrics, events) | ✅ | `state` branch |
| Analytics pull every 6 h (YouTube Analytics API) | 🟡 | code exists; no published video yet to measure |
| Daily summary (GitHub issue) | 🟡 | runs daily; replaced by Telegram (below) |

## 2. What is missing or partial

| Need | Gap |
|---|---|
| Phone notification + approve/fix/reject from phone | Today it's a GitHub issue; no phone push, and playback needs a download |
| Fix with feedback | Exists, but (a) has a bug (the restored old script overwrites the fix) and (b) regenerates *everything*, so liked pictures are lost and it costs about $0.45 |
| Publish verification | Upload is confirmed, but nobody checks that it actually went public at the scheduled time |
| Publish-time experiment | One fixed slot (19:00 IST) |
| Thumbnail, playlist, captions file | Not done (scopes and Shorts limits to check, see §5) |
| Analytics depth | Basic metrics only; no retention curve, traffic sources, intervals, or comparison to similar videos |
| Learning loop + experiment log | Topic-share adjustment only; no recorded experiments, no lessons fed to the writer |
| Dashboard | None |
| Revenue tracking | None (the channel is not monetised yet) |
| Daily run uses a simpler path than Claude's runs (no 3-topic retry, no Telegram) | Unify on one path |

## 3. What gets built

1. **One production path.** The daily schedule and every command run the same code (`scripts/run_command.py`).
2. **Telegram review bot** (owner chose Telegram):
   - The finished video arrives as a Telegram message with title, score, cost and any flags, plus three buttons:
     **✅ Approve**, **✏️ Fix**, **🗑 Drop topic**.
   - **Fix** asks "What should change?". The owner replies in his own words, and a revised version comes back
     to Telegram.
   - **Drop** asks why (optional). Every piece of feedback is saved and fed into the learning loop.
   - Messages from anyone except the owner are ignored. The bot is paired with a one-time code.
   - Alerts (failures, budget pauses), "uploaded", "now live" and a short daily report also go to Telegram.
3. **Cloudflare Worker** (free plan):
   - Receives the Telegram button taps instantly.
   - Starts the matching GitHub run with a token that can only start this repo's workflows.
   - Also serves the dashboard (item 7).
   - Using webhooks avoids GitHub polling, which would use up the free Actions minutes.
4. **Cheaper, more faithful fixes:**
   - Fixes reuse every picture and the voice that didn't change. Only the beats the owner's note touches are
     regenerated.
   - Fixes the overwrite bug.
5. **Publishing package:**
   - Title, description with sources, AI-disclosure line, hashtags (#Shorts + 2–3 topical), tags, category
     (Education), language, made-for-kids = no, `containsSyntheticMedia` = true.
   - A custom thumbnail and playlist are added if the research confirms they work for Shorts through the API
     (§5).
6. **Publish verification:**
   - Checks the video after its scheduled time.
   - Sends Telegram "✅ live: link", or "⚠️ problem: reason" if it stayed private, was rejected or failed
     processing.
7. **Dashboard** (owner chose Cloudflare, login-protected):
   - A private web page from the Worker. To log in, tap "send code", and a 6-digit code arrives in Telegram.
     Only the owner's Telegram can receive codes.
   - Rebuilt from the database after every analytics pull.
   - Sections:
     - **Production:** planned, made, reviewed, approved, dropped, published; failure reasons; time to make;
       cost per video.
     - **Audience:** views, engaged views, watch time, average % viewed, retention, likes, comments, shares,
       subscribers, traffic sources, with period and data freshness shown.
     - **Money:** costs by category, revenue (entered via Telegram `/revenue` until YouTube reports it), net,
       ROI, break-even.
     - **Strategy:** comparisons by pillar, hook type, length, publish time, music, wit; each with sample size.
   - Daily, weekly, monthly and yearly views.
8. **Learning loop:**
   - Per-video features are recorded at production: pillar, hook formula, length, beats, wit lines, pointers,
     music bed, publish slot, cost.
   - Metrics are snapshotted at 1, 3, 7 and 28 days, and compared with videos *of the same age*.
   - Weekly, Claude writes `docs/LEARNINGS.md`: what worked or failed, with sample sizes and confidence.
   - Lessons reach the writer only when the evidence is strong enough. Thresholds are in the experiment rules.
   - Experiments live in `docs/EXPERIMENTS.md`: hypothesis, change, arms, sample needed, result, decision.
9. **First experiment (owner asked): publish time.**
   - Three slots rotate in balanced order:
     - 19:00 IST (morning US East);
     - 22:30 IST (US lunchtime, late evening India);
     - 07:30 IST (US evening, India morning).
   - After about 10 videos per slot, compare views at 7 days and pick the winner.
   - Topic-specific timing comes later, when there is data per audience.

## 4. What the owner needs to do (one time, about 15 minutes)

🔑 These are the only manual steps. The exact click-by-click guide is sent in chat. Results go into GitHub
Settings → Secrets.

1. **Telegram:** create a bot with @BotFather, copy its token, then press Start in the bot.
   → secret `TELEGRAM_BOT_TOKEN`
2. **Cloudflare:** create a free account, then an API token from the "Edit Cloudflare Workers" template.
   → secrets `CLOUDFLARE_API_TOKEN`, `CLOUDFLARE_ACCOUNT_ID`
3. **GitHub:** create a fine-grained token limited to this one repo with "Actions: Read and write" only.
   → secret `GH_DISPATCH_TOKEN`

   It lets the Worker start runs when you tap a button. It cannot read code or change settings.
4. Later and optional: re-run the YouTube sign-in once, if we add playlists, caption files or revenue data
   (extra Google permissions).

## 5. External services, limits and risks

| Service | Cost | Limit / risk |
|---|---|---|
| GitHub Actions (private repo, Free) | $0 | Monthly free minutes. Expected use about 25 min/day, within the quota. Scheduled runs can start late; schedules pause after 60 days without commits (the daily state commits prevent this). |
| Anthropic API | ~$0.30/video | Prepaid credits (≈$97 left); low-credit alert to add |
| Black Forest Labs | ~$0.10–0.15/video | Prepaid credits |
| ElevenLabs | plan | Monthly character quota; voice ~700 chars/video |
| YouTube Data API | free | 10,000 units/day; an upload is about 1,600 units. **Uploads from an unverified Google project may be forced private** — today's 19:00 publish is the test. If it stays private, the Google API audit is needed (form, takes weeks). |
| Telegram Bot API | free | 50 MB per uploaded video (ours are ~13 MB) |
| Cloudflare Workers + KV | free | Daily request limits far above our use |

**Remaining risks:**
- YouTube policy changes (inauthentic content; Partner Program Shorts rule from Feb 2027).
- An expired token stops approvals. Each token's expiry date is recorded, with a reminder 14 days before.
- AI image errors still need the owner's eye.

## 6. How each part is tested

- **Telegram:** send a test video; tap each button; verify only the owner is accepted; a stranger's message is
  ignored.
- **Worker:** unit-test the request handling locally; live-test the dispatch; check that a wrong secret header
  is rejected.
- **Fix flow:** fix a video with a note that touches one beat. Check that the other pictures and the voice are
  reused and the cost stays under $0.15.
- **Publish:** one approve → upload → scheduled → verify "live" (onigiri v9 today).
- **Dashboard:** numbers checked against the database by hand. The login code only works once, for 10 minutes.
- **Daily run:** a full unattended day (05:47 IST run → Telegram → approve from phone → publish → live
  notification).
