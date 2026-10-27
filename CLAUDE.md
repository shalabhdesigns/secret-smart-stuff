# Secret Smart Stuff — working notes for Claude

- **Channel:** Secret Smart Stuff (YouTube @secretsmartstuff, account secretsmartstuff@gmail.com). English
  explainer Shorts: "The secret smart reasons behind everyday things."
- **History:** Bhaukaali Toons (a Hindi cartoon sketch show) ran from 26 to 28 Oct 2026. The owner dropped it.
  - Its code is on branch `archive/bhaukaali-toons`.
  - Its docs are in `docs/archive/bhaukaali-toons/`.
  - Never restart it without the owner asking.
- **Read `docs/PLAYBOOK.md` first.** It is the approved production process (baseline: onigiri v9, approved
  25 Oct 2026). Follow it by default. Change it only with evidence (`docs/EXPERIMENTS.md`) or owner approval,
  and log every change in its Change log.
- **Read `docs/LESSONS.md`.** It holds everything learned so far, from both formats.
- **Owner:** Shalabh. He wants:
  - short sentences, simple language, points;
  - finished results, not process updates;
  - to be asked only for real decisions or access.

## Owner rules (standing)
- **He approves every video before it is published.** Nothing goes public without his ✅ in Telegram.
  - On approval the system uploads the video as private, scheduled for its publish slot (the publish-time
    experiment, `config/experiments.yaml`).
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
- **Secrets:** only in GitHub Actions secrets (and the encrypted login in KV). Never in files or chat.
  - The Google OAuth app is "Secret Smart Stuff uploader" in Google Cloud project `bhaukaali-toons` (owned by
    bhaukaalitoons@gmail.com), In production.
  - The Cloudflare account login is secretsmartstuff@gmail.com (since 28 Oct); Worker URL
    https://secretsmartstuff-studio.secretsmartstuff.workers.dev.
  - Keep bhaukaalitoons@gmail.com alive until the Google Cloud project has secretsmartstuff@gmail.com as an owner.
- **Commit trailer:** see the session's attribution instructions.
