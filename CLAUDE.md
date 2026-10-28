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
  orange/navy/cream or other "AI default" palettes. See `assets/brand/README.md`.
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
- **Instagram (since 28 Oct 2026):** @secretsmartstuff. Each published video is posted as a Reel at its YouTube
  slot (`shorts/publish/instagram.py`, `instagram.yml`). Login: `/iglogin` (Meta app "Secret Smart Stuff Publisher",
  dev mode; see `docs/SETUP.md`). Stop cancels a pending post; a posted Reel can only be deleted in the app.
- **Secrets:** only in GitHub Actions secrets (and the encrypted login in KV). Never in files or chat.
  - The Google OAuth app is "Secret Smart Stuff uploader" in Google Cloud project `bhaukaali-toons` (Owners: secretsmartstuff@gmail.com since 28 Oct, and
    bhaukaalitoons@gmail.com), In production.
  - The Cloudflare account login is secretsmartstuff@gmail.com (since 28 Oct); Worker URL
    https://secretsmartstuff-studio.secretsmartstuff.workers.dev.
  - secretsmartstuff@gmail.com is an Owner of the Google Cloud project (28 Oct); the old account is a second Owner.
- **Commit trailer:** see the session's attribution instructions.
