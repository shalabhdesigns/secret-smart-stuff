# Bhaukaali Toons — working notes for Claude

- Channel: **Bhaukaali Toons** (YouTube @bhaukaalitoons, Instagram @bhaukaalitoons, account
  bhaukaalitoons@gmail.com). Show: **Sab Theek Hai** — Hindi/Hinglish (UP flavour) 2D cartoon sketches.
  The earlier "Secret Smart Stuff" explainer format is retired; it lives only in `docs/archive/`.
- **Read `docs/PLAYBOOK.md` first** and follow it. Change it only with evidence or owner approval.
- Owner: Shalabh. He wants short sentences, simple language, points; finished results, not process updates.

## Owner rules (standing)
- **Approves every video before it is published** (Telegram ✅). On approval the system uploads it as private with
  a scheduled publish time (7:30 PM IST slot). Never publish anything he has not approved.
- Characters must stay **identical forever**: use only the locked library (`creative/puppet/README.md`).
  Never cut/replace heads at render time; new poses pass `qa_faces.py` before use.
- No floating characters, no limbs cut by the frame except deliberate camera framing; correct relative heights.
- Dialogue: natural, witty, intelligent; catchphrases must never feel forced. Roman Hinglish captions.
- Every sketch loops: the last beat leads back into the first.
- Length: aim 35–45 s, never over 60 s.
- Original music only; tasteful sound effects only.
- Flag cost and policy risks before spending. Don't claim something works until it has been tested.

## Before sending any video
- Check 4+ frames of every shot at full size (seams, proportions, framing, captions).
- Contact sheet of the full video; loudness about −15 LUFS, true peak below −1 dBTP.
- Check Hindi pronunciation (transcribe) and say plainly what could not be checked.
- Send a 3× loop preview with it.

## The automatic daily loop (shorts/sketch/)
- `produce.yml` (daily) -> `run_command.py daily` -> `shorts/sketch/flow.py`: chase pending reviews, maybe add a new
  set (grow.py, weekly, $5/week art cap), then write -> voice -> animate -> check -> send to Telegram, made 3 days
  ahead of its slot. Max 4 episodes waiting at once.
- Writer: `writer.py` (Claude API, rules from docs/SHOW_BIBLE.md + docs/craft/). Director: `director.py` turns the
  plan into exact shots (layout, framing, timing, continuity, long-shot splitting). Voices: `voices.py` (ElevenLabs
  eleven_v4, unchanged lines reused). QA: `qa.py` (tech checks + Claude vision check). Calendar: `episodes.py`.
- Owner's Telegram buttons -> Cloudflare Worker `bhaukaalitoons-studio` -> GitHub `command.yml` with
  approve / fix (his note -> revise) / reject (makes a replacement). `rerender` re-renders the same plan for free.
- Renders live in GitHub releases `episodes`, `episodes-2`, ... (auto rollover before 1000 files).
- Faces/acting: `scripts/puppet/face.py` + `Actor.state` follow docs/craft/EXPRESSIONS.md. Lip sync comes from the
  Devanagari syllables of each line (`<line>.txt`, or TTS alignment `<line>.align.json`).

## Systems
- Code: private repo `shalabhdesigns/bhaukaali-toons`. Runs on GitHub Actions; nothing runs on the owner's laptop.
- Claude drives the runner by pushing `commands/request.json` (actions in `scripts/run_command.py`, e.g.
  `whoami`, `accounts`, `diag`, `sketch`).
- Secrets live only in GitHub Actions secrets: `YT_CLIENT_ID`, `YT_CLIENT_SECRET`, `YT_REFRESH_TOKEN`
  (Google Cloud project `bhaukaali-toons`, app "Bhaukaali Toons uploader", In production),
  `ELEVENLABS_API_KEY`, `BFL_API_KEY`, `ANTHROPIC_API_KEY`, `TELEGRAM_BOT_TOKEN`, `CLOUDFLARE_API_TOKEN`,
  `GH_DISPATCH_TOKEN`. Never put secrets in files or chat.
- Voices: ElevenLabs flow F9Yu1qHGas1nIdxPh2yp, model eleven_v4, Devanagari text with audio tags.
  Dev `ZjaFChlI14QPkGSR18mK`, Rocky `m9qrUtG4N193K879RHOm`, Meera `hHyd5z9VxRT4YKoDwPRl`.
- Commit trailer: see the session's attribution instructions.
