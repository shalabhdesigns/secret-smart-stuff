# Production Playbook: Secret Smart Stuff Shorts

**Status:** the single source of truth for how every Short is made.
**Baseline:** the approved video *onigiri v9*. The owner approved it on 25 Oct 2026, and it was uploaded as
YouTube video `zWJFcVGDdRc`, scheduled for 19:00 IST.
**Rule:** every future video follows this playbook by default. Change it only when:
- there is evidence (an experiment in `docs/EXPERIMENTS.md`), or
- the owner approves the change.

Record every change at the bottom of this file under "Change log".

What the code is and where it lives:

| What | Where |
|---|---|
| Exact prompts used for the approved video | `reference/approved/onigiri-v9/prompts_snapshot.py` (copy of `shorts/prompts.py` at approval) |
| Exact settings used | `reference/approved/onigiri-v9/channel.yaml`, `pipeline.yaml` |
| The approved video's script, image prompts, beat plan, word timings, captions, review, QA | `reference/approved/onigiri-v9/` |
| The approved MP4 and full-size media | GitHub release `review-onigiri-rice-ball-wrapper-v9` (`final.mp4`, `media.tgz`) |
| Format research and the evidence behind each rule | `docs/04_FORMAT_V2.md`, `research/shorts_retention.md` |
| Live code | `shorts/` (pipeline, prompts, render), `scripts/`, `.github/workflows/` |

---

## 1. Concept and scripting

**Channel promise:** "The secret smart reasons behind everyday things."
**Audience:** curious English speakers aged 16–40, worldwide (US, UK, CA, AU, IN).

**Where ideas come from** (`IDEAS` prompt, `Pipeline.discover`):
- Each idea = one everyday object + one specific design detail + the question it answers.
- Ideas are spread across five pillars (`config/channel.yaml → pillars`):

  | Pillar | Share |
  |---|---|
  | why_detail | 40% |
  | walk_past | 20% |
  | by_country | 15% |
  | first_version | 15% |
  | india_asia | 10% |

- Ideas avoid objects already used or rejected, and topics competitors already covered (unless the angle is
  clearly different).
- Competitor outliers and search questions are used as inspiration only. Never copy them.

**How ideas are scored** (`SCORE` prompt, Claude Haiku). Each item is out of 10, then weighted to a total out of 100:

| Item | Weight |
|---|---|
| audience | 20 |
| novelty | 25 |
| hook | 20 |
| story | 15 |
| cost | 10 |
| policy | 10 |

The highest-scoring shortlisted topic is made first. Onigiri scored 77/100.

**Steering the angle (optional):** the owner, or Claude, can set an `angle` and a `question` on a topic before
it is made (the `produce` command with an `angle` field). Onigiri needed this: early versions picked the wrong angle.

**Script** (`SCRIPT` prompt, Claude Sonnet 5.5 with web search):
- Up to 6 searches.
- The script must be backed by sources:
  - at least 2 different sources across the script;
  - every fact needs at least one source.
- **Conservative wording:**
  - Never "most", "everyone" or superlatives.
  - Say only what the sources say.
  - If sources disagree, write "one common explanation is…".
- **Forbidden topics:** politics, news, finance, crypto, religion, astrology, health, medicine, scientific
  research.
- **Length:** 26–33 seconds of narration at 2.6 words per second.
  - That is about 68–86 words in 11–13 beats.
  - The finished video runs about 32–36 seconds (onigiri v9 = 36.2 s).
- Code checks the script (`Pipeline._validate_script`):
  - 9–14 beats and 4–9 images;
  - word budget;
  - sources present;
  - no banned words;
  - the last beat uses the first image;
  - the loop lead-in is in place (section 3).

**Independent review** (`REVIEW` prompt, Claude Haiku, separate from the writer):
- **Scores:** hook, payoff, visual match, accuracy, originality (2 points each = 10 total).
- **Pass mark:** 7/10. Below that, up to 2 targeted repairs (`FIX`) within the word budget.
- If it still fails, the topic is dropped (`QualityRejected`) and the next topic is tried (up to 3 per run).
- The review list goes into the owner's review notes.

## 2. Hook and storytelling

Every rule below comes from evidence in `docs/04_FORMAT_V2.md`.

**Beat 1 is the spoken question:**
- 8–12 words, naming the odd detail ("Why does this onigiri hide its seaweed behind plastic?").
- The voice starts at once: leading silence is trimmed in `_stage_voice`, keeping 0.12 s before the first word
  (a tighter cut clipped first words in the sketch period).
- Evidence: speech in the first 3 s gave +24.7% retention at 10 s (Emplifi, 10,110 Reels).
- **No text card over the opening.** It was removed in v8 because it popped in on every replay and broke the
  loop. Text overlays also measured −6% retention (Emplifi).

**First "aha" by beat 4–5.** The core reason is stated plainly. In v9 it was beat 4: "A thin film keeps them apart."

**Then one layer deeper:** how it works, a date or number, a comparison. In v9:
- "Seven-Eleven Japan launched packaged onigiri in 1978."
- The 1-2-3 tabs.

**Second-to-last beat = the answer in one line** (the payoff): "The film keeps wet rice and crisp seaweed apart."

**Wit:**
- 1–2 short, kind, witty lines that state no new fact (`tone: witty`).
  - In v9: "Soggy seaweed makes for a sad lunch."
- They get a playful-but-realistic image (limp seaweed drooping over a plate) and a "shake" camera move.
- At most one comic sound per video (boing or record scratch).

## 3. Story flow, pacing and the loop

**Beats:**
- 11–13 beats. One sentence (5–9 words) and one visual state per beat.
- One beat lasts about 2.5–3.5 s.

**Pictures:**
- 6–7 images per video.
- Beats reuse images with a different `focus`, so 12 visual states come from about 7 pictures.
- **IMAGE = WORDS:** each beat's picture must show what that beat *says*. The owner flagged "peel 2 and 3" being
  shown without tabs 2 and 3 (v2).

**The seamless loop** (the owner explicitly asked for this). All five parts are needed:
1. The last beat reuses image 1 with the `settle_to_start` camera move, ending on the exact opening frame.
   - Code never swaps the first or last image (v6 broke the loop by swapping beat 1's picture).
2. The last line is an **unfinished lead-in** (3–7 words, ending in "...") that the opening question completes.
   - Example: "So next time someone asks you..." → "Why does this onigiri hide its seaweed behind plastic?"
   - Code replaces a question or a long line with this safe lead-in.
3. The video ends 0.12 s after the last word: no silent tail. v7 had 0.5 s of silence.
4. Nothing appears over the first frame (no hook card).
5. The music bed is cross-faded across the loop point, so the replay continues the music
   (`assemble._loop_bed`, 1 s equal-power).

**Transitions:**
- Mostly cuts.
- A whip every 3rd or 4th beat (with a whoosh sound).
- Zoom-cuts on alternate beats.
- A per-video random seed varies the order. Videos must not look like one template: YouTube's
  "inauthentic content" policy names identical slideshows.

## 4. Image generation

- **Model:** Black Forest Labs FLUX.2 `flux-2-pro` at $0.03/image, 1088×1920 PNG (since 28 Oct 2026).
  - `flux-2-klein-4b` ($0.015) is now only the fallback for API errors.
  - Why: klein drew malformed safety pins (wrong coils, a bent wire as the "whole pin"), and the cheap checks
    passed them.
- **Credibility gate on every picture** (`_realism`, Claude Sonnet vision, about $0.01 per picture):
  - The question: would a viewer who owns this object find anything wrong? It checks for wrong or missing parts,
    melted geometry and other AI tells, and whether the asked-for detail is shown.
  - Failed pictures are regenerated with a rewritten prompt, up to 3 tries.
  - If a picture still fails, it is flagged `BLOCKING` and the video cannot pass the final review.
- **Style suffix on every prompt** (`channel.yaml → style.image_style`): "clean editorial product photograph, soft
  natural light, shallow depth of field, realistic materials, uncluttered background, no text, no letters, no
  logos, no watermark", plus "Vertical 9:16 composition, key subject large and centred."
- The writer writes the image prompts. Rules (in `SCRIPT`):
  - realistic photo;
  - no text, logos or faces;
  - the key detail clearly visible;
  - numbered parts shown as **the whole real object front-on** with each part at its real position.
  - **Never ask the image model for numbers or text.** Numbers are drawn by code.
- The approved prompts for v9 are in `reference/approved/onigiri-v9/script.json → images`.
- **Checks after generation** (Claude Haiku vision, in `_stage_visuals`):
  1. **Base check:** any text or logo, or distorted shapes? Regenerate once. If still bad, flag it for the owner.
  2. **LOCATE:** find each beat's `focus` in the picture, for the camera to move toward.
  3. **MATCH:** does this picture show what this beat says?
     - If not, generate a beat-specific replacement (up to 3 per video).
     - Never for the first or last beat.
     - Still not matching? Flag it.
  4. **MARKERS:** one vision call places the numbered badges.
     - Badges are only kept on the object, at high or medium confidence.
- v9 used 9 images (6 planned + 3 replacements), about 120 vision calls and $0.08 of Claude.

## 5. Video generation

- **No AI video clips.** The FLUX 3 image-to-video adapter exists (`shorts/providers/video.py`) but is **off**.
  There is no evidence that AI video beats clean stills for this format, and a 5 s draft costs about $0.30.
  It is a candidate experiment, not the default.
- Motion comes from the renderer's camera moves on stills (`shorts/render/beats.py`):
  - **Moves:** push, pull, punch, drift left/right, hold, shake (witty beats), settle_to_start (last beat).
  - 1080×1920 at 30 fps.

## 6. Editing and stitching

- **Beat timing** comes from the real word timings returned by the voice service:
  - a beat starts when its first word is spoken;
  - the video ends at the last word + 0.12 s.
- **Rendering:** frames are drawn in Python (PIL) and piped to ffmpeg.
- **Final encode** (`assemble.finalize`):
  - video: H.264 high, CRF 19, yuv420p;
  - audio: AAC 192k, 48 kHz;
  - `+faststart`, with captions burned in.
- **Media saved for re-renders:** `media.tgz` (images, voice, timings, plans) goes to the review release. A
  `rerender` command rebuilds the video from it at **no generation cost**. Used for the v9 audio fix.

## 7. On-screen text and annotations

**Captions:**
- Inter, 72 px, white with a black outline, 2–3 words per chunk (max 18 characters).
- The word being spoken is highlighted yellow (`&H0000E5FF`).
- Captions sit at y = 1200 px, or 1360 px when beats focus on the middle of the frame.
- They are never stacked on a label.

**Keyword pops:**
- At most 2 per video: one spoken word, big orange (#F26B1D) with an ink outline.
- Pops at the moment the word is spoken, holds 0.9 s (v9: "SOFT", "APART").

**Numbered markers:**
- Orange badges with white numbers, popping in 0.35 s apart, each with a soft click.
- Used whenever the narration names numbered parts.

**Pointers ("indicators"):**
- At most 3 per video, only on beats that point at a small detail.
- Never on neighbouring beats, the first or last beat, witty beats, or beats with markers, pops or arrows.
- Each one uses a different style: spotlight (dim the rest), corner brackets, short arrow, or circle (at most once).
- **Most beats get no overlay.** The camera move is enough.
- This was owner feedback on v7 ("overuse of circles"). v9 used **zero** pointers.

**Labels:**
- 1–3 words in a paper box.
- Placed only where they clear the captions, pops and markers; otherwise left out.

**Blueprint card:**
- At most 1 per video, 2–4 words.
- Text is wrapped and shrunk to fit (fixed after v4 overflowed).

**Arrows:**
- At most 1. Dropped if shorter than 12% of the frame (v9 drew a stray 2% arrow; fixed after approval).

**Palette:** paper #F4EFE6, ink #14213D, accent #F26B1D.

## 8. Audio and voice

**Voice:**
- ElevenLabs "Alice" (`Xb7hH8MSUJpSbSDYk0k2`, chosen by the owner), model `eleven_v4`.
- Called via the `/with-timestamps` endpoint, mp3 44.1k/128k.
- Small natural pauses between sentences are kept (owner: "small pauses were okay").

**Music:**
- Six original instrumental beds, 45 s each, made once with ElevenLabs Music (`music_v2_5`), in `assets/music/`.
- One bed per video, chosen by job id.
- Played at −17 dB and ducked a further ~7 dB under speech (20 ms attack, 300 ms release).
- **Original music only.** A partner (licensed) track would halve the Short's revenue share.
- The owner asked for music after v1 felt bland.

**Sound effects:**
- Seven curated ElevenLabs effects in `assets/sfx/`: whoosh, click, pop, chime, swipe, boing, record_scratch.
- The owner rejected the earlier synthetic beeps, which are no longer used.
- Played quietly (−17 to −22 dB) and sparingly:

  | Effect | When |
  |---|---|
  | whoosh | on whip cuts |
  | pop | on keyword pops |
  | click | on markers and the first few pointers |
  | swipe | on an arrow |
  | one comic sound | on the first witty beat |
  | chime | only on a card beat |

**Mixing** (`assemble.mix_audio`):
- Done in numpy with exact lengths.
- ffmpeg only decodes and applies loudness normalisation to −14 LUFS, true peak −1.5 dBFS.
- Built this way because ffmpeg filter graphs ended the music early or hung on the build machine (v8, v9).

## 9. Timing and duration

v9, beat by beat (start times measured from `words.json`; beats average ~3 s, the 1978 line is the longest at ~5 s):

| Beat | Line | Approx. start |
|---|---|---|
| b1 | Why does this onigiri hide its seaweed behind plastic? | 0.0 s |
| b2 | Seaweed turns soft when it touches rice. | 4.3 s |
| b3 | Soggy seaweed makes for a sad lunch. (witty) | 7.4 s |
| b4 | A thin film keeps them apart. (first aha) | 10.4 s |
| b5 | Seven-Eleven Japan launched packaged onigiri in 1978. | 13.2 s |
| b6 | Tab one pulls down from the top. (marker 1) | 18.1 s |
| b7 | Tabs two and three are the corners. (markers 2, 3) | 20.7 s |
| b8 | Each pull slides the film out. | 23.3 s |
| b9 | Then the seaweed hugs the rice. | 25.8 s |
| b10 | It can wait on a shelf for hours. | 27.9 s |
| b11 | The film keeps wet rice and crisp seaweed apart. (payoff) | 30.3 s |
| b12 | So next time someone asks you... (loop lead-in) | 34.2 s |
| end | (last word ends 36.08 s, +0.12 s) | 36.2 s |

The exact per-word times are in `reference/approved/onigiri-v9/words.json`.

## 10. Quality assurance

**Automatic checks before the owner sees anything** (`qa/media.py`, `_stage_qa`):
- 1080×1920 at 30 fps, H.264, audio present.
- 8–60 s long.
- Narration fits the video.
- About −14 LUFS, true peak ≤ −0.5 dBFS.
- No silence over 1.2 s, audio starts immediately.
- No black or frozen segments.
- Title check (length and mobile cut-off).
- Hook heuristic.

**Review notes posted with each video:**
- reviewer score and problems;
- facts and sources;
- image flags;
- description preview;
- cost.

**Final self-review** (since 28 Oct 2026, owner: "the video should come to me only after you have
completed your self-review"):
- `Pipeline.critique` runs on the finished MP4. Claude Sonnet sees:
  - a contact sheet with one labelled frame per beat, captions burned in;
  - the first and last frame side by side;
  - the script with timings, facts and sources, the fact-checker's notes, image flags and media checks.
- **It scores 1–5:** hook curiosity, visual credibility, image–word match, payoff, flow and pacing, accuracy,
  loop, rewatch and share. It also lists blocking problems with exact fixes, plus retention risks.
- **Pass (calibrated 28 Oct on the approved onigiri v9, which scores 3.44):**
  - no blocking problem (only glance-obvious ones: wrong or broken object, garbled text, a picture that
    contradicts its words, a false claim, no curiosity hook, a broken loop) and no `BLOCKING` image flag;
  - hook ≥ 4, accuracy ≥ 4, loop ≥ 3, credibility ≥ 2, image match ≥ 2;
  - mean ≥ 3.0.
- **Not passed:** a targeted fix (`selffix`):
  - only the named lines or picture prompts change;
  - flagged pictures are regenerated;
  - everything else is reused;
  - then the video is reviewed again.
- **Limits:**
  - At most 3 reviews (2 fixes) per video.
  - A video that still fails is dropped with the reason, and one other topic is tried.
  - The owner is told only "no video this time" with the reason. He never receives a failing video.
- After an owner fix, one more review (and at most one fix) runs before the new version is sent.
- The scores and summary are in `review.md` and in the Telegram caption.

**Claude's own inspection when Claude is in the session** (this caught most of the problems in v4–v9):
- A contact sheet of about 19 frames.
- The first and last frames compared (the loop).
- Audio level near the end and start (music present across the join).
- The quietest windows checked for dropouts.
- A 3× back-to-back loop preview for the owner.

**Approval criteria:**
- Every automatic check passes.
- Every beat's picture matches its words.
- The loop is seamless.
- No overlapping text.
- Music runs throughout.
- Facts are sourced.
- The owner says "approve".

## 11. Tools, integrations and costs

**Per-video costs:**

| Item | Tool | Per-video cost (v9 actual) |
|---|---|---|
| Ideas, scoring | Claude Haiku 5.5 | ~$0.01 |
| Script + web search | Claude Sonnet 5.5 + `web_search_20250305` | $0.17 |
| Review | Claude Haiku 5.5 | $0.04 |
| Image checks (base, locate, match, markers) | Claude Haiku 5.5 vision | $0.09 |
| Images | BFL FLUX.2 klein 4B | $0.015 each; normally 6–9 = $0.09–0.14 (v9 was made twice, so $0.45) |
| Voice | ElevenLabs eleven_v4 | ~$0.13 per 700 characters, an estimate from plan credits (v9 voiced twice = $0.25) |
| Music and SFX | ElevenLabs (one-time library) | $0 per video |
| Rendering, storage, scheduling | GitHub Actions (private repo) | $0 within the free minutes |
| Upload | YouTube Data API | free (quota) |

- A normal single-pass video costs **about $0.45–0.70**.
- All onigiri attempts together (v1–v9) cost $5.38.
- Budget limits (`pipeline.yaml`): $2 per video, $6 per day, $45 per month.
- Costs are logged per call in the `costs` table.
- ElevenLabs is a monthly plan; its per-video figure is an estimate.

## 12. Mistakes not to repeat (from v1–v9)

| Symptom | Cause | Fix now in code |
|---|---|---|
| Question asked at 5.5 s, no music, 6 slow shots (v1) | v1 format | v2 format: question at 0 s, 11–13 beats |
| Picture did not show "tabs 2 and 3" (v2) | generic image reuse | MATCH check + replacement image, numbered markers |
| Beeps sounded wrong (v2) | synthetic SFX | curated ElevenLabs SFX |
| Card text ran off screen (v4) | no wrapping | wrap + shrink |
| Labels on top of captions, pops, markers (v5) | fixed label position | label placement that avoids them, or no label |
| Opening picture swapped, loop broken (v6) | MATCH replaced beat 1 | first and last beats are never swapped |
| Circles everywhere (v7) | a ring on every beat with a label | ≤3 pointers, varied styles, mostly none |
| End felt like a restart (v7) | 0.5 s silence + question→question + hook card | lead-in ending, 0.12 s tail, no opening card, looped music |
| Music missing (v8) / cut at the end (v9) | ffmpeg filter-graph end-of-stream behaviour | numpy mixer |
| Review bundle lost after a good render (v9) | tar archived its own output | tarball built outside the folder |
| Budget stopped a run mid-way | rolling 24 h limit | paused jobs resume first the next day |

## 13. Known gaps (not captured or not yet solved)

- The **exact per-call LLM inputs and outputs** (the raw searches the writer ran) are not stored, only the
  final script and its cited sources.
- **Image seeds** are random per run and not logged, so an identical image cannot be regenerated.
- **ElevenLabs voice settings** (stability, style) are the voice's defaults and not pinned in code.
- The "film keeps them apart" shot (b4) still does not clearly show the inner film. The image model struggles
  with this; the flag was accepted by the owner.
- **The ElevenLabs cost per video is estimated** from plan credits, not billed per call.

## Change log

- 2026-10-25: Playbook created from the approved onigiri v9. Arrows under 12% of the frame are now dropped.
- 2026-10-28: Restored as the live playbook after the Bhaukaali Toons detour (26–28 Oct). Stills format confirmed
  as default (AI clips off). Voice keeps 0.12 s before the first word (was 0.05 s). Review, fixes and approval
  happen in Telegram; approval uploads private + scheduled for the publish-time experiment slot. Uploads and
  analytics refuse a YouTube login for any other channel. Lessons from both formats: `docs/LESSONS.md`.
- 2026-10-28: Credibility first. FLUX.2 pro is the main image model, every picture passes a strict realism check
  (3 tries), and every finished video passes a final self-review (max 3 rounds, targeted fixes) before the owner
  sees it. Topic scoring now penalises objects whose key detail image models draw badly (springs, coils, gears).
- 2026-10-28: Review bar calibrated to onigiri level (owner). Pictures: at most 6, each one simple whole object;
  parts are shown with focus, markers or labels, never with complex AI scenes. A cheap "can we draw it" probe
  runs before each script. Image model stays FLUX.2 pro (bake-off vs FLUX.2 max and FLUX 3: no clear winner).
