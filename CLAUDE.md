# Secret Smart Stuff — working notes for Claude

- **Channel:** Secret Smart Stuff (YouTube @secretsmartstuff, account secretsmartstuff@gmail.com). English
  explainer Shorts: "The secret smart reasons behind everyday things."
- **History:** a Hindi cartoon sketch format was tried 26–28 Oct 2026 and dropped. Everything from it (code, docs,
  data) is on branch `archive/bhaukaali-toons` only; nothing of it runs. Never restart it unless the owner asks.
- **Read `docs/PLAYBOOK.md` first.** It is the approved production process (baseline: onigiri v9, approved
  25 Oct 2026). Follow it by default. Change it only with evidence (`docs/EXPERIMENTS.md`) or owner approval,
  and log every change in its Change log.
- **Read `docs/LESSONS.md`.** It holds everything learned so far, from both formats.
- **Owner:** Shalabh. He wants:
  - short sentences, simple language, points;
  - finished results, not process updates;
  - to be asked only for real decisions or access.

## Owner rules (standing)
- **Auto-publishing until 25 Nov 2026** (owner, 28 Oct): a video that passes the final review is uploaded
  private + scheduled for its slot without waiting for him; he gets each video in Telegram with a "⏸ Stop it"
  button. A video that fails is never published: it is fixed (≤3 review rounds) or dropped and he is told.
  After `approval.auto_until` the system returns to manual ✅ by itself.
- **One video a day.** Daily production starts automatically; one video waits for review at a time.
- **Format:** stills with camera moves (onigiri v9), 30–36 s.
  - Real-motion AI clips are off. They cost about $2.50–3.50 more per video; test them only as an experiment.
- **Feedback that is now a standing rule:**
  - each picture shows exactly what is being said;
  - original music always;
  - only tasteful sound effects;
  - 1–2 light witty lines;
  - a seamless loop;
  - few pointers (varied styles, none unless needed);
  - never clip the first word.
- **Brand (29 Oct 2026):** Pull Tab logo; ultramarine #1F3BFF + blush #FFD6E0 + white; Archivo. Never return to
  orange/navy/cream or other "AI default" palettes. See the brand design system (https://claude.ai/artifact/TUm2uFFjQQvvaYaQoLRqLB; read its
  `project/README.md`) and `assets/brand/README.md`.
- **Lean format.** Images, captions, annotations and simple purposeful treatments; minimal AI video.
- **Visual credibility above all.** Nothing that looks malformed, implausible or obviously AI. Animation only when
  it helps understanding.
- **Self-review every video before the owner sees it** (owner, 28 Oct 2026):
  - check visuals, facts, flow, pacing, audio and captions;
  - judge its potential (curiosity, retention, rewatch, share) using evidence;
  - fix the real issues;
  - at most 3 rounds.
  - The code does this automatically (`Pipeline.critique`). When Claude is in the session, Claude also checks the
    frames. The owner is the final approver, not the person who catches basic mistakes.
- **Every video builds on the previous ones** (owner, 29 Oct 2026): learn → apply → evaluate → improve, every upload
  (`shorts/carry.py`, PLAYBOOK §14). Never let a new video ignore what earlier videos, the review and the owner taught.
- **When something fails, fix it at once** (owner, 30 Oct 2026): find the cause, fix it, try again, then tell him the
  result. If only he can fix it (a login, a Meta block), say exactly what to do and give him a way to finish by hand.
- **Covers** (owner, 3 Nov 2026): every video gets a designed, curiosity-driven cover that the video pays off (PLAYBOOK §15).
  Never misleading: YouTube removes clickbait, and is strictest on news.
- **News tie-ins** (owner, 2 Nov 2026): a series can be queued with `"then"` (each run queues the next). Rules: no
  pictures of the event or its victims, never suggest a cause, and say the cause is unknown (`P.NEWS`).
- **Videos about a game show the game** (owner, 16 Nov 2026: "Do not do this ever again"): every GTA video uses official Rockstar images (`shorts/official.py`, `assets/official/catalogue.json`, scenes `OFFICIAL:<id>`), GTA 6 from the first frame and GTA 5 whenever it is compared. Never a video about a game with only stock or AI pictures. Images are used unchanged (crop + camera move), credited to Rockstar in the description.
- **Footage first, images last** (owner, 16 Nov 2026): growth over ad money. Every video prefers real video
  footage that tells the story: official/free-to-use footage (Rockstar's own trailer downloads via
  `shorts/official_clips.py`, scenes `CLIP:<shot>`; creators' own CC-licensed footage only with permission). Official
  or free stills only when no footage fits; Black Forest Labs images only as a last resort when genuinely needed.
  Story first: hook in the first second, escalating reveals, a "wow" payoff, a comment question, a seamless loop.
- **Story format + natural voice** (owner, 18 Nov 2026): the old scripts were "unnatural, badly built, confusing".
  GTA videos use `notes.style: "story"` (`shorts/prompts.py` STORY_*): a real person telling a friend a story, natural
  complete sentences clear on one listen, hook -> escalating reveals -> wow payoff -> comment question, 45-70 s
  (110-170 words), no loop lead-in, real Rockstar/Take-Two quotes word for word. Voice: "Mark - Natural
  Conversations" (ElevenLabs Voice Library, eleven_v4) with up to 5 delivery tags per video.
- **Scripts are written by Claude in session, not by the API** (owner, 18 Nov 2026: "$20 every 3-4 days is way too
  much ... create a video on the first try"). Claude researches, writes and fact-checks each day's scripts and picks
  every shot from `assets/official/shots.json` in `scripts/gta_scripts.py` -> `config/gta_scripts.json` ->
  `notes.script`. The pipeline then skips the paid script/review/repair/storyboard stages; one Haiku final check;
  a failing video is held for Claude, never dropped. API cost per video: a few cents.
- **GTA branding on every first screen** (owner, 20 Nov 2026: "GTA 5 or GTA 6 branding in the thumbnail or first
  screen gains instant views"; his best Reels showed Lucia's face or GTA V cover art). Owner, 20 Nov 2026: "use the
  actual GTA 6 logo ... only". Every GTA video: the real GTA VI logo (`assets/brand/gta6_logo.png`, cut unchanged
  from Rockstar's trailer end card; `shorts/render/logo.py`) above 2 short cover lines on the cover, big on the first
  1.8 s and small in the corner after (`finalize(overlays=)`); the first beat's shot is a strong character shot;
  scripts set `cover_lines` (true, said in the video) and may set `cover_frame`. Owner, 21 Nov 2026: the cover words
  were too short to know what the video is about -> `cover_lines` = 3 lines, 6-12 words, each <= 22 characters, that
  say clearly what the video is about AND leave a question (e.g. "19 MILLION SOLD / ON DAY ONE? / HERE'S THE CATCH");
  never a line starting with "GTA 6"; no cover picture repeated from a recent video (`cover_frame`). The checker
  enforces this; the opening card shows them for 2.6 s. Owner, 21 Nov 2026: cover pictures must grab attention
  ("our goal is attention"): use the boldest official moments (masked robberies, police/prison, chases, stunts, beach
  and party shots) from `assets/official/attention_shots.json` (the `faces` list FIRST: 21 Nov numbers show a clear Lucia/Jason face on the cover wins, faceless covers flop; rules R2-R5 in docs/GTA_LEARNINGS.md) via `cover_frame {"shot", "f", "x"}` (any official shot,
  not only ones in the video); preview with the `shotframes` workflow; rotate them. Not nudity, gore or a picture
  the video contradicts: YouTube and Instagram stop recommending those, which costs the reach we want. Never make the channel itself look
  like Rockstar's; descriptions keep "fan commentary, not affiliated".
- **Daily cost check** (owner, 18 Nov 2026: "each day check how much we are spending on each video and find ways to
  further reduce it ... bring it down to bare minimum"). Every day run `scripts/cost_report.py` on the state db, report
  cost per video and the waste (spend on videos not published), find the biggest remaining cost and cut it.
- **GTA 6 launch week: 5 videos a day** (owner, 16 Nov 2026). Slots in `config/pipeline.yaml` `gta_slots`: from 22 Nov
  12:00, 14:00, 17:00, 20:00, 02:00 UTC (the 23:00 slot was weak on YouTube; experiment E3). Review the numbers after 7 days: 8 a day if views per video hold, back to 3 if they fall.
- **Flag cost and policy risks before spending.** Never claim something works until it has been tested.

## Owner away 21-27 Nov 2026 (owner, 20 Nov: "I DO NOT WANT ANY INTERRUPTIONS WHATSOEVER ... without requiring any
input, intervention, or approval from me")
- One scheduled Claude run a day (cloud, not his laptop), **"Daily GTA scripts + cost check", 12:41 IST**: learning
  loop (`scripts/gta_learn.py`, `docs/GTA_LEARNINGS.md`), cost check, tomorrow's 5 scripts, and a safety pass on
  today's videos (made at 05:47 IST; first slot 19:30 IST): held/failed -> fix real problems in `scripts/gta_scripts.py`,
  remake (queue item + new `nonce` + `retire_jobs`), look at the frames, approve with its slot. It appends results to
  `docs/AWAY_LOG.md` and never messages or asks the owner.
- Approvals: auto-publish until 30 Nov (`approval.auto_until`). Claude may approve a held video after fixing it and
  checking its frames. Safety net (`shorts/dispatch.deadline_publish`, every 15 min): a video still held 90 min before
  its slot is published unless the final check found a factual problem; one held before the voice is remade without
  the pre-check 4 h before its slot.
- Quiet mode (`quiet_from`/`quiet_until` in `config/pipeline.yaml`): no Telegram messages, no GitHub issues or
  comments (they e-mail him). Errors go to the state `events` table; failed runs are read with
  `gh api repos/shalabhdesigns/secret-smart-stuff/actions/runs?status=failure` and the job logs API.
- Limits: YouTube upload quota ~6 uploads a day (5 videos + 1 remake upload at most; a remake before upload costs no
  quota). November budget $155 ($121 used by 20 Nov). Instagram login valid to 27 Dec.
- **Learning** (owner, 20 Nov 2026): learn only from GTA videos (`scripts/gta_learn.py`, `docs/GTA_LEARNINGS.md`);
  every finding has numbers and changes the next scripts; experiments have a test and a control; nothing generic or
  repeated. The old generic per-video post-mortems are off for GTA videos.
- **Ambition** (owner, 20 Nov 2026): don't let caution about monetisation or copyright rule ideas out by default;
  explore. Still never: re-upload other creators' videos without permission, publish false claims, or present the
  channel as Rockstar's (any of these can get the channel removed, which ends growth).

## Before sending any video
- A frame contact sheet, plus full-size frames of anything doubtful.
- First frame vs last frame (the loop).
- Music level at the end and start; no dropouts; the first word complete.
- Send a 3× loop preview with it.

## Systems
- **Code:** public repo (since Nov 2026; unlimited Actions minutes) `shalabhdesigns/secret-smart-stuff` (named `bhaukaali-toons` 26–28 Oct; GitHub redirects
  the old name).
  - Everything runs on GitHub Actions; nothing runs on the owner's laptop.
  - State lives in SQLite on the `state` branch.
  - Claude drives runs by pushing `commands/request.json` (actions in `scripts/run_command.py`). Use the REST
    API only, because GraphQL is blocked.
- **Daily loop:** `produce.yml` → `run_command.py daily` → `shorts/pipeline.py`:
  1. topic;
  2. sourced script;
  3. independent review;
  4. voice (ElevenLabs Alice);
  5. images (FLUX.2);
  6. render;
  7. QA;
  8. Telegram review.
- **Owner's Telegram buttons:**
  - Worker `secretsmartstuff-studio` (Cloudflare) → `command.yml`.
  - Buttons: approve / fix (minimal edit, reuses unchanged media) / reject.
- **YouTube login:**
  - One tap: the owner sends `/ytlogin` to the studio bot.
  - The refresh token is stored encrypted in the Worker's KV store.
  - Uploads and analytics refuse any login that is not for the channel named in `config/channel.yaml`.
- **Instagram (since 28 Oct 2026):** @secretsmartstuff. Each published video is posted as a Reel at the same
  minute it goes public on YouTube. The Worker watches `igdue:<job>` every 5 minutes and starts `igpost.yml` about 10
  minutes early. That run doesn't save state; it records `igdone:<job>` in KV. `instagram.yml` and the analytics run
  are backups that only post Reels more than 20 minutes overdue (`shorts/publish/instagram.py`). Login: `/iglogin` (Meta app "Secret Smart Stuff Publisher",
  dev mode; see `docs/SETUP.md`). Stop cancels a pending post; a posted Reel can only be deleted in the app.
- **Dashboard** (rebuilt 3 Nov 2026): `/dash` on the Worker (Telegram login code). `shorts/dashboard.py` +
  `dashboard_template.html`, data from `shorts/usage.py` (resources, balances, alerts). Every number is labelled
  measured / calculated / allocated / estimated / manual / unavailable. Never show an assumed number as real.
  Owner-entered values live in KV `manual.json`. It refreshes every 6 h or on "Refresh now".
- **GitHub Actions minutes:** GitHub Free gives 2,000 a month for private repos. Watch the dashboard's
  "Credits & limits". Avoid long waits inside runs.
- **Secrets:** only in GitHub Actions secrets (and the encrypted login in KV). Never in files or chat.
  - The Google OAuth app is "Secret Smart Stuff uploader" in Google Cloud project `bhaukaali-toons` (Owners: secretsmartstuff@gmail.com since 28 Oct, and
    bhaukaalitoons@gmail.com), In production.
  - The Cloudflare account login is secretsmartstuff@gmail.com (since 28 Oct); Worker URL
    https://secretsmartstuff-studio.secretsmartstuff.workers.dev.
  - secretsmartstuff@gmail.com is an Owner of the Google Cloud project (28 Oct); the old account is a second Owner.
- **Commit trailer:** see the session's attribution instructions.
