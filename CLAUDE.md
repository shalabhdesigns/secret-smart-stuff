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
- **Flag cost and policy risks before spending.** Never claim something works until it has been tested.

## Before sending any video
- A frame contact sheet, plus full-size frames of anything doubtful.
- First frame vs last frame (the loop).
- Music level at the end and start; no dropouts; the first word complete.
- Send a 3× loop preview with it.

## Systems
- **Code:** private repo `shalabhdesigns/secret-smart-stuff` (named `bhaukaali-toons` 26–28 Oct; GitHub redirects
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
