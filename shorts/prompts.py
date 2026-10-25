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
- cost: can it be shown with object photos + simple diagrams (10 = easy)?
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
- LAST beat: a closing line that leads naturally back into beat 1 (the video loops), and it reuses
  image img1 (same picture as beat 1).
- 6-7 images total, in "images": each a realistic photo prompt, NO text, NO logos, NO people's faces,
  the key detail clearly visible. Beats reuse images with a different "focus" (a different visible
  part to frame) - that is how we get 12 visual states from 7 pictures.
- "focus": the exact visible thing in that image to frame/circle (e.g. "the thin plastic film between
  the seaweed and rice"). Required on every image beat.
- "callout": 1-3 word label for the focus, on at most 6 beats. "pop": ONE emphatic word spoken in that
  beat, on at most 2 beats total. "card_text": 2-4 words for a paper blueprint card, at most 1 beat
  (no image on that beat). "arrow": at most 1 beat, {{"from": visible thing, "to": visible thing}}.
- "hook_card": 2-3 words shown on screen for the first 1.5 s, DIFFERENT words from the spoken question.
- Use web search first: at least {min_sources} credible sources for the main reason. If the reason is
  disputed or folklore, say "the most common explanation is..." or mark the idea not viable.
- Be conservative: no "most", "many people", "everyone", no superlatives, no "the only reason".
- WIT: include 1-2 short, light, witty lines that fit the story (dry humour, playful personification
  of the object, a relatable everyday moment, a funny understatement). Mark them "tone": "witty".
  They must not state new facts, must be kind (no jokes about people, cultures or groups) and
  should get their own playful-but-realistic image (e.g. "a single limp, soggy sheet of seaweed
  drooping sadly over the edge of a plate").
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
 "scenes": [{{"id": "b1", "narration": str, "image": "img1"|null, "focus": str|null,
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
