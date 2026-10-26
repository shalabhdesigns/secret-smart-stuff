# Bhaukaali Toons — working notes for Claude

- Channel: **Bhaukaali Toons** (YouTube @bhaukaalitoons, Instagram @bhaukaalitoons, account
  bhaukaalitoons@gmail.com). Show: **Sab Theek Hai** — Hindi/Hinglish (UP flavour) 2D cartoon sketches.
  The earlier "Secret Smart Stuff" explainer format is retired; it lives only in `docs/archive/`.
- **Read `docs/PLAYBOOK.md` first** and follow it. Change it only with evidence or owner approval.
- Owner: Shalabh. He wants short sentences, simple language, points; finished results, not process updates.

## Owner rules (standing)
- **Approves every video before it is published.** Uploads go up as private; he makes them public/scheduled.
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

## Systems
- Code: private repo `shalabhdesigns/bhaukaali-toons`. Runs on GitHub Actions; nothing runs on the owner's laptop.
- Claude drives the runner by pushing `commands/request.json` (actions in `scripts/run_command.py`, e.g.
  `whoami`, `accounts`, `diag`, `sketch`).
- Secrets live only in GitHub Actions secrets: `YT_CLIENT_ID`, `YT_CLIENT_SECRET`, `YT_REFRESH_TOKEN`
  (Google Cloud project `bhaukaali-toons`, app "Bhaukaali Toons uploader", In production),
  `ELEVENLABS_API_KEY`, `BFL_API_KEY`, `ANTHROPIC_API_KEY`. Never put secrets in files or chat.
- Voices: ElevenLabs flow F9Yu1qHGas1nIdxPh2yp, model eleven_v4, Devanagari text with audio tags.
  Dev `ZjaFChlI14QPkGSR18mK`, Rocky `m9qrUtG4N193K879RHOm`, Meera `hHyd5z9VxRT4YKoDwPRl`.
- Commit trailer: see the session's attribution instructions.
