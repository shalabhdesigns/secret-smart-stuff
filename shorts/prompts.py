"""Prompt templates. Every prompt starts with `TASK: <name>` (the dry-run fake
keys off it) and asks for strict JSON so code, not prose, drives the pipeline."""

SYSTEM_WRITER = """You write scripts for "Secret Smart Stuff", a faceless YouTube Shorts channel that
explains the hidden design reasons behind everyday objects. Voice: calm, curious, warm, precise,
like a friend who just noticed something clever. Short spoken sentences. No hype words
(amazing, insane, crazy), no "did you know", no channel intro, no subscribe pitch.
Never state a fact you cannot support with a source. Never invent numbers, dates or names.
Be conservative: say only what your sources actually say. No generalisations you cannot check
("most", "many people", "everyone"), no superlatives, no "the only reason". If sources differ,
say "one common explanation is...". Prefer ONE clear, well-sourced reason over several shaky ones.
Image prompts must match the facts exactly (shape, size, material, country) - check them.
Never copy a source's sentence structure; write in your own words.
Forbidden topics: politics, news, finance, crypto, religion, astrology, health, medicine,
scientific research. Do not make a brand, logo or real person the subject."""

IDEAS = """TASK: ideas
Propose {n} NEW Short ideas for the channel. Pillar quotas for this batch: {quotas}.
Each idea = one everyday object + one specific design detail + the question it answers.
Prefer objects people touch or pass daily, worldwide; include objects common in India and Asia
when the pillar is india_asia or by_country. Avoid anything in this list of already-used or
rejected objects/questions:
{avoid}

Topics competitors ALREADY covered (do not repeat these objects/questions unless your angle
is clearly different - then say what is different in "angle"):
{covered}

Optional external signals (competitor outliers, search questions) - use only as inspiration
about what people care about, never copy a title:
{signals}

Return JSON: {{"ideas": [{{"object": str, "pillar": pillar_id, "question": str,
"angle": str (the twist or wrong guess), "why_interesting": str}}]}}"""

SCORE = """TASK: score
Score this Short idea for the channel (0-10 each):
- audience: will a broad 16-40 global audience care?
- novelty: is the reason genuinely surprising to most people?
- hook: can the first 2 seconds be a sharp, specific question?
- story: is there a wrong guess -> real reason -> payoff arc?
- cost: can realistic AI photos show the object AND its key detail correctly (10 = common, simple shapes;
  low = tiny mechanisms or exact geometry image models often get wrong, e.g. springs, coils, gears, clasps)?
- policy: 10 = zero risk (no forbidden topic, no brand as subject, no real people, no danger).
Idea: {idea}
Return JSON: {{"scores": {{"audience":n,"novelty":n,"hook":n,"story":n,"cost":n,"policy":n}},
"total": 0-100 weighted (audience 20, novelty 25, hook 20, story 15, cost 10, policy 10),
"reason": one sentence}}"""

SCRIPT = """TASK: script
Research and write one Short in the channel's v2 format (question-first, fast-cut, light text).
Object: {object}
Question: {question}
Angle: {angle}
Pillar: {pillar}
Target: {seconds_lo}-{seconds_hi} seconds of narration ({words_lo}-{words_hi} words total).

Format rules (these come from retention research, follow them exactly):
- BEAT 1 is the spoken question, 8-12 words, specific, names the odd detail. The voice starts at
  second zero. No "did you know", no intro.
- 11-13 beats total. Each beat = ONE short sentence (5-9 words) and ONE visual state.
- Keep the TOTAL inside the word budget above; short beats, no filler.
- First "aha" (the core reason, stated plainly) must land by beat 4 or 5. Then go one layer deeper
  (how it works, a date, a number, a comparison), then the full answer.
- SECOND-TO-LAST beat: the answer in one plain line (the payoff).
- LAST beat (the loop): the video replays straight into beat 1 with no pause, so the last beat is an
  UNFINISHED lead-in, 3-7 words, that beat 1's question grammatically completes. Read them together:
  "So next time someone asks you..." + "Why does this onigiri hide its seaweed behind plastic?"
  It must NOT be a question or a full sentence, must end with "...", and it reuses image img1.
- 6-7 images total, in "images": each a realistic photo prompt, NO text, NO logos, NO people's faces,
  the key detail clearly visible. Beats reuse images with a different "focus" (a different visible
  part to frame) - that is how we get 12 visual states from 7 pictures.
- "focus": the exact visible thing in that image for the camera to move toward (e.g. "the thin plastic
  film between the seaweed and rice"). Required on every image beat.
- "callout": 1-3 word label, ONLY when the beat points at a small detail a viewer could miss; at most
  3 beats, never neighbouring beats, never beat 1 or the last beat. Leave it null otherwise - the
  camera move alone is usually enough. "pop": ONE emphatic word spoken in that
  beat, on at most 2 beats total. "card_text": 2-4 words for a paper blueprint card, at most 1 beat
  (no image on that beat). "arrow": at most 1 beat, {{"from": visible thing, "to": visible thing}}.
- "hook_card": 2-3 words (used for the thumbnail only; nothing is shown over the opening frame).
- Use web search first: at least {min_sources} credible sources for the main reason. If the reason is
  disputed or folklore, say "the most common explanation is..." or mark the idea not viable.
- Be conservative: no "most", "many people", "everyone", no superlatives, no "the only reason".
- WIT: include 1-2 short, light, witty lines that fit the story (dry humour, playful personification
  of the object, a relatable everyday moment, a funny understatement). Mark them "tone": "witty".
  They must not state new facts, must be kind (no jokes about people, cultures or groups) and
  should get their own playful-but-realistic image (e.g. "a single limp, soggy sheet of seaweed
  drooping sadly over the edge of a plate").
{video_rule}- PICTURES AN AI MODEL CAN DRAW: at most 6 pictures. Each is ONE whole, common object or simple everyday scene
  from a clear angle on a plain background, described plainly (shape, material, colour). Never ask for
  actions, before/after states, wet/dripping/steaming effects, motion, hands doing things, or close-ups of
  small parts: show the whole object and let the camera focus, a marker, a label or a pop point at the part. Avoid prompts that need transparent internals, liquids inside tubes, tiny holes, exact
  part counts or precise mechanisms; show those through a simpler shot plus the narration, a marker or a pop.
- IMAGE = WORDS: every beat's image must visibly show what that beat SAYS. If a beat names steps or
  numbered parts ("pull tab 1, then 2 and 3"), the image must show the WHOLE real object front-on
  (e.g. the full triangular wrapper, not a flat packet), with each of those physical parts clearly
  separate at its real position (e.g. the top pull strip and both bottom corner flaps), and
  you must add "markers": [{{"label": "1", "target": the exact visible part}}, ...] - numbers are
  drawn on by code, so NEVER ask the image model for numbers or text.

Return JSON:
{{"viable": true|false, "reason_if_not": str,
 "title": "<=60 chars, accurate, a question or clear statement",
 "thumb_text": "2-3 words, different words from the title",
 "hook_card": "2-3 words",
 "hooks": [5 alternative spoken opening questions, 8-12 words each], "chosen_hook": index,
 "images": {{"img1": "prompt", "img2": "prompt", ...}},
{motions_field} "scenes": [{{"id": "b1", "narration": str, "image": "img1"|null, "focus": str|null,
   "motion": "punch"|"push"|"pull"|"drift"|"hold", "transition": "cut"|"whip"|"zoom_cut",
   "callout": str|null, "pop": str|null, "arrow": {{"from": str, "to": str}}|null,
   "card_text": str|null, "tone": "normal"|"witty",
   "markers": [{{"label": str, "target": str}}] | null}}],
 "facts": [{{"claim": str, "sources": [url, ...], "main": true|false}}],
 "description": "2 short sentences for the YouTube description (no sources here)",
 "hashtags": ["#..", "#.."] (3 max, relevant),
 "affiliate_product": "generic product type shown, or null"}}"""

REVIEW = """TASK: review
You are an independent fact-checker and editor for a 30-45 second YouTube Short. You did NOT
write this script. Check the main claims with web search where needed. Judge the script AS
WRITTEN: "opening_line" is what the viewer hears first. Score 0-2 each, using these anchors:
- hook: 2 = the opening line names a specific odd detail and makes you want the answer;
  1 = clear but generic; 0 = vague or misleading.
- payoff: 2 = the question is clearly answered by the end; 1 = answered but weakly; 0 = not answered.
  The LAST beat is by design an unfinished lead-in that flows into beat 1 when the Short loops
  (e.g. "So next time someone asks you..."); judge the payoff on the beat before it, and do not
  ask for the last beat to restate the answer.
- visual_match: 2 = every image prompt fits its narration and is factually right; 1 = minor
  mismatch; 0 = a visual that would mislead.
- accuracy: 2 = every claim supported by a listed source or your check; 1 = only small wording
  issues, nothing false; 0 = any claim false or unsupported.
- originality: 2 = a fresh angle or detail most viewers won't know; 1 = a clear, well-made
  explanation of a known fact (acceptable for a Short); 0 = generic filler.
Lines marked "tone": "witty" are intentional light humour: judge them only for taste and fit
(kind, relevant, not misleading), not as factual claims.
List concrete problems with the exact fix. Mark severity "blocker" only for false or unsupported
claims, forbidden topics, brand/logo as subject or a misleading title; everything else is "minor".
SCRIPT JSON:
{script}
Return JSON: {{"scores": {{"hook":n,"payoff":n,"visual_match":n,"accuracy":n,"originality":n}},
"total": sum, "problems": [{{"issue": str, "fix": str, "severity": "blocker"|"minor"}}],
"verdict": "pass"|"fix"|"reject"}}"""

FIX = """TASK: script
Revise this script to fix ONLY these problems. Keep everything else. Same JSON schema.
Problems: {problems}
Script: {script}"""

OWNER_FIX = """TASK: script
The channel owner reviewed this Short and asked for a change. Apply EXACTLY what they asked and
nothing else. Every beat, line, image prompt, focus, pop, marker and field that the request does
not touch must stay CHARACTER-FOR-CHARACTER identical (unchanged pictures and voice are reused, so
needless edits cost money and lose what the owner liked). Keep the format rules: question first,
the second-to-last line is the answer, the last line is the "..." lead-in into beat 1, the last beat
uses img1. If the request needs a new picture, change only that image's prompt (or add a new image
key and point the beat at it). Facts must stay sourced; never invent facts to satisfy a request.
Owner's request: "{note}"
Other rule: {length_rule}
Script: {script}
Return the full revised script JSON (same schema) with one extra field
"change_summary": one short sentence saying what you changed."""

LOCATE = """TASK: locate
Look at this image (a generated photo for a YouTube Short). Answer as JSON:
{{"found": bool (is "{target}" clearly visible?),
 "x": center x as fraction 0-1, "y": center y as fraction 0-1, "w": width fraction, "h": height fraction,
 "has_text_or_logo": bool (any letters, numbers, brand marks or watermarks visible?),
 "artifacts": bool (warped/melted shapes, extra parts, impossible geometry?),
 "matches_prompt": bool (does it show: {prompt}?)}}"""


MATCH = """TASK: match
This picture is shown while the narrator says: "{narration}"
It was generated from: "{prompt}". The camera frames: "{focus}".
Would a viewer clearly SEE what the sentence describes? Be strict about specific things the
sentence names (numbered parts, actions, objects, before/after states). A generic shot of the
object is NOT a match when the sentence names a specific part or action.
Return JSON: {{"matches": bool, "missing": str,
 "better_prompt": str (a realistic photo prompt that would show exactly what the sentence describes,
   the key part large and clear; never ask for text, numbers or letters in the image)}}"""


MARKERS = """TASK: markers
The narrator says: "{narration}". We will draw numbered badges on this picture.
For each item, give the point (fractions 0-1 of width/height) where the badge should sit: on the
physical part it refers to, or the most sensible spot if that part is implied (e.g. "corner 2" =
a corner of the wrapper). A badge must sit ON the object, never on empty background; if the part
is not visibly on the object, use confidence "low". Items: {markers}
Return JSON: {{"markers": [{{"label": str, "x": float, "y": float,
 "confidence": "high"|"medium"|"low"}}]}}"""


CLIPCHECK = """TASK: clipcheck
These are 3 frames (left to right: 25%, 50%, 75% through) of a short AI-generated video clip for a
YouTube Short. It was asked to show: "{prompt}". The narrator says over it: "{narration}".
Be strict. Answer JSON:
{{"ok": bool (true only if nothing below is wrong),
 "morphing": bool (objects melt, change shape, extra/missing parts, impossible physics),
 "text_or_logo": bool (letters, numbers or brand marks appear),
 "faces": bool (a human face is visible),
 "shows_action": bool (the requested action/change is visible),
 "problems": "one short sentence"}}"""


# Only used when providers.video_clips.enabled is true (real-motion clips experiment).
VIDEO_RULE = """- VIDEO: every image becomes a short real-motion video clip (image-to-video), so this is footage,
  not a slideshow. For each image write a "motions" line: ONE clear physical action or change that
  matches what the narration says over that image (e.g. "a hand pulls the centre strip down and the
  clear film slides out from between the rice and the seaweed"; "the escalator steps glide up and
  slip between the comb teeth"), plus a gentle camera move. Real-world physics only, slow and
  smooth, nothing morphs, appears from nowhere or changes shape; hands are fine, no faces, no text.
  Images for numbered-part beats (markers) stay still, so give them a camera-only motion.
"""
MOTIONS_FIELD = """ "motions": {"img1": "what MOVES in this image's video clip", "img2": "...", ...},
"""


# ---- credibility gate for every generated picture (added 28 Oct 2026 after the safety-pin test showed
# malformed, obviously-AI objects passing the cheap checks)
REALISM = """TASK: realism
This AI-generated photo will appear for ~3 seconds in an educational YouTube Short about: {topic}.
It was asked to show: "{prompt}".
Question: would an ordinary viewer, glancing at it on a phone, think "that's wrong" or "that's fake AI"?
BLOCKING (only these): the main object is malformed, unrecognisable or built wrong in a way people notice
(e.g. a safety pin drawn as a bent wire, a spring as a flat spiral, extra or fused parts, melted shapes);
garbled text or letters; physically impossible scenes; obviously plastic/CG look.
NOT blocking: small deviations from the prompt's details, slightly simplified parts, lighting or style choices,
things only an engineer would notice. Do not nitpick. Most decent product photos should pass.
Keep every string under 20 words; at most 3 items per list.
Return JSON: {{"ok": bool (false only if something BLOCKING is visible), "blocking": [str], "minor": [str],
 "shows_detail": bool, "retry_prompt": str (only if not ok: a SIMPLER photo prompt for a common, whole,
   real version of the object from a clear angle on a plain background; no text, no numbers)}}"""

CRITIC = """TASK: critic
You are the final quality reviewer for a YouTube Short on "Secret Smart Stuff" (English, faceless explainer:
"the secret smart reasons behind everyday things"). You did not make it. The owner will only see videos you
pass, and he does not want to catch basic problems himself. Be strict and specific.

IMAGE 1 is a contact sheet: one frame from the middle of every beat, in order, labelled with the beat id
(captions are burned in, as the viewer sees them). IMAGE 2 is the FIRST frame (left) next to the LAST frame
(right): they must match for a seamless loop.

What a strong Short on this channel does (evidence: docs/04_FORMAT_V2, research/shorts_retention.md):
1. Beat 1 is a spoken curiosity question about a specific odd detail, and frame 1 SHOWS that detail.
2. The first "aha" (the core reason, stated plainly) lands by ~10 s; then one deeper layer (a date, number,
   comparison or how-it-works detail); the second-to-last beat answers the opening question in one line.
3. Every beat adds new information or a light, kind laugh; nothing is said twice; no filler.
4. The last line is an unfinished lead-in ("So next time someone asks you...") that the opening question
   completes, and the last frame equals the first frame, so the replay feels continuous.
5. Every picture is a credible real-world photo of exactly what the words say. One malformed or obviously
   AI-generated object destroys trust in the whole channel: that is ALWAYS blocking.
6. Captions readable, never covering the key detail; overlays sparse (pointers only where they help).
7. ~28-38 s. 1-2 witty lines max, kind and relevant.

The script (beat id, start second, words, what the picture was meant to show):
{beats}
Title: {title}
Facts and sources: {facts}
Fact-checker notes: {review}
Automatic flags: {flags}
Automatic media checks: {qa}
{previous}
Score 1-5 (5 = excellent, 3 = acceptable but forgettable):
 hook_curiosity, visual_credibility, image_word_match, payoff, flow_pacing, accuracy, loop,
 rewatch (would people watch it twice?), share (would someone send it to a friend?).
Calibration: the owner approved, and viewers liked (1.1k views), a video whose AI photos were imperfect (a
slightly odd wrapper shape, simplified parts). That level is acceptable. Score honestly, but only call
something BLOCKING when most viewers would notice it at a glance and it would hurt trust or understanding:
- the object is unrecognisable, clearly the wrong object, or visibly broken/melted (e.g. a safety pin drawn
  as a bent wire);
- garbled text or fake labels on screen;
- a picture that clearly contradicts its words (shows the opposite, or a different object);
- a false or unsupported claim; a hook that is not a curiosity question; a broken loop; unreadable or
  overlapping text.
Imperfect-but-recognisable AI photos, repetition, slow beats and missed opportunities go in "improvements"
(only ones that would clearly raise retention or shares).
For each problem give an exact fix the writer can apply: which beat, the new line (same length or shorter),
or the new photo prompt for that beat's image (describe the real object's exact shape; plain background).
If the object itself cannot be photographed credibly by an AI image model even with better prompts, say so.
Return JSON: {{"scores": {{"hook_curiosity":n,"visual_credibility":n,"image_word_match":n,"payoff":n,
 "flow_pacing":n,"accuracy":n,"loop":n,"rewatch":n,"share":n}},
 "blocking": [{{"beat": str, "problem": str, "fix": str}}],
 "improvements": [{{"beat": str, "problem": str, "fix": str}}],
 "retention_risks": [str], "unshowable": bool,
 "verdict": "send"|"fix"|"drop", "summary": "one sentence a busy owner can read"}}"""

SELF_FIX = """TASK: script
The final quality review of this Short found problems. Apply the fixes below and nothing else.
Every beat, line, image prompt, focus, pop, marker and field the fixes do not touch must stay
CHARACTER-FOR-CHARACTER identical (unchanged pictures and voice are reused). Keep the format rules:
question first, the second-to-last line is the answer, the last line is the "..." lead-in into beat 1,
the last beat uses img1. To replace a picture, change that image's prompt (describe the real object's exact
shape and parts plainly; never ask for text or numbers). Facts must stay sourced; never invent facts.
Fixes: {note}
Other rule: {length_rule}
Script: {script}
Return the full revised script JSON (same schema) with one extra field
"change_summary": one short sentence saying what you changed."""
