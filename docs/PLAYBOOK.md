# Production Playbook: Sab Theek Hai (Bhaukaali Toons)

Baseline: the pilot "The Haircut", 46-second cut (approved 26 Oct 2026). Change this playbook only with
evidence (`docs/EXPERIMENTS.md`) or owner approval, and log changes at the bottom.

## 1. Format
- 2D cartoon sketch, vertical 1080×1920, 30 fps, 35–45 s (never over 60 s).
- Cast: **Dev** (polite, can't say no), **Rocky** (barber, overconfident, Kanpur flavour), **Meera** (flatmate, deadpan).
- Hindi/Hinglish with UP flavour; burned-in **Roman Hinglish** captions, colour per speaker.
- Loop: the last beat leads straight back into the first shot.

## 2. Script
- One relatable desi situation; the joke comes from character, not from a repeated catchphrase.
- 10–13 short lines. A callback (e.g. "achha hai" said again in a worse moment) and a final twist
  that sets up the loop.
- Owner approves the script before voices are made.

## 3. Voices (ElevenLabs, ~$0.15–0.35 per sketch)
- eleven_v4, Devanagari text with audio tags ([deadpan], [whispering]...), two takes per line, pick one.
- Voice IDs are in `CLAUDE.md`. Transcribe the chosen takes to check pronunciation.
- `scripts/puppet/prep_lines.py`: tempo 1.08–1.12, trim pauses (keep comic pauses ~0.3 s).

## 4. Animation (free, ~5 min render)
- Locked character library only (`creative/puppet/README.md`). Scene JSON: shots, actors (pose, floor/neck_y,
  size, expression, events), camera moves, fx.
- `size` = on-screen height of a 1.0-tall standing character. Wide shots ~1130–1210; seated in the chair
  is staged further back (~960).
- People stand on the floor (`floor`) in wide/medium shots; close-ups via camera zoom.
- Render: `python scripts/puppet/puppet.py rig.json scene.json out_dir`.

## 5. Sound and assembly
- `scripts/sketch_assemble.py spec.json`: captions, voices, SFX (twitch, spiral, snips, shutter), music
  bed (quirky_funk at −24 dB, muted on inner-voice and black shots), loudness −15 LUFS.
- Final limiter: true peak below −1 dBTP.

## 6. QA (before the owner sees it)
- 4+ frames per shot at full size: no seams, correct heights, nobody floating, no accidental crops,
  captions readable and inside the safe area.
- Full contact sheet, loudness, first vs last frame (loop), 3× loop preview.

## 7. Delivery
- Owner reviews → approves → upload as **private** with title, description, hashtags → owner publishes or schedules.

## Change log
- 2026-10-26: Created from the approved pilot (2D puppet format replaces the archived explainer playbook).
