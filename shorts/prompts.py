"""Prompt templates. Every prompt starts with `TASK: <name>` (the dry-run fake
keys off it) and asks for strict JSON so code, not prose, drives the pipeline."""

SYSTEM_WRITER = """You write scripts for "Hidden by Design", a faceless YouTube Shorts channel that
explains the hidden design reasons behind everyday objects. Voice: calm, curious, warm, precise,
like a friend who just noticed something clever. Short spoken sentences. No hype words
(amazing, insane, crazy), no "did you know", no channel intro, no subscribe pitch.
Never state a fact you cannot support with a source. Never invent numbers, dates or names.
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
Research and write one Short.
Object: {object}
Question: {question}
Angle: {angle}
Pillar: {pillar}
Target length: {seconds_lo}-{seconds_hi} seconds of narration (about {words_lo}-{words_hi} words).

Steps:
1. Use web search to find at least {min_sources} credible sources for the MAIN reason
   (manufacturer/standards bodies, museums, encyclopedias, engineering references, reputable
   publications). If the reason is disputed or only folklore, say so honestly in the script
   ("the most common explanation is...") or answer that the idea is not viable.
2. Write 5 different opening hooks (spoken, 8-18 words, the object + the odd detail + a question
   or a wrong guess). No "did you know".
3. Write the script as 4-7 scenes. Each scene: 1-2 short sentences of narration, a visual.
   Scene types: hero (object, wide), detail (close-up of the key detail), context (object in use /
   in its real setting), comparison (two versions side by side - give image_prompt and
   image2_prompt and two short labels), blueprint_card (paper/grid card with 1-3 short words -
   use for the key takeaway, at most once).
   For image scenes give an image_prompt describing a realistic photo with NO text, NO logos,
   NO people's faces, and the key detail clearly visible. Give 0-2 callouts per image scene:
   {{"target": the exact visible thing to circle, "label": 1-3 words}}.
4. The last line must pay off the hook and loop naturally back to the first line.
5. List every factual claim with the source URLs that support it.

Return JSON:
{{"viable": true|false, "reason_if_not": str,
 "title": "<=60 chars, accurate, a question or clear statement, no all-caps spam",
 "thumb_text": "2-3 words, different words from the title",
 "hooks": [5 strings], "chosen_hook": index,
 "scenes": [{{"id":"s1","type":...,"narration":...,"on_screen_text": (first scene only, 2-4 words,
   different words from the narration),"image_prompt":...,"image2_prompt":..., "labels":[..,..],
   "card_text": ..., "callouts":[...]}}],
 "facts": [{{"claim": str, "sources": [url, ...], "main": true|false}}],
 "description": "2 short sentences for the YouTube description (no sources here)",
 "hashtags": ["#..", "#.."] (3 max, relevant),
 "affiliate_product": "generic product type shown, or null"}}"""

REVIEW = """TASK: review
You are an independent fact-checker and editor. You did NOT write this script. Be strict.
Verify the main claims with web search where needed. Score 0-2 each:
- hook: specific, instant, makes you want the answer
- payoff: the hook's question is actually answered by the end
- visual_match: each scene's visual fits its narration
- accuracy: claims are supported by the listed sources and your own checks (0 if any claim is
  wrong or unsupported)
- originality: not a generic template; has a real insight
Also list concrete problems (wrong facts, forbidden topics, brand/logo as subject, misleading
title, unclear sentence) and the exact fix for each.
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
