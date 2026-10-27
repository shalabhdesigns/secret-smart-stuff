# Scoring rubric and gate thresholds

One rubric, used by the independent judge (`shorts/sketch/judge.py`), the deterministic checks (`gates.py`, `qa.py`)
and the owner. Scores are 1–5 with written anchors; the judge must quote the evidence before scoring (reduces judge
bias, docs/research/R2). LLM scores are a coarse filter; the owner's decision and real audience data are the final word.

## A. Premise (G1 screen, before any script)
| dimension (weight) | 1 | 3 | 5 |
|---|---|---|---|
| truth (×2) | generic | familiar, stated plainly | specific truth viewers have lived but never heard said |
| laughs (×2) | no laugh in sight | one clear laugh | a turn that should get a real laugh plus smaller ones |
| fresh (×1.5) | a meme every page has posted | familiar + new detail | a take nobody has done |
| clarity (×1) | needs explaining | clear after setup | who/where/what obvious in 5 s |
| showable (×1) | can't be shown with our puppets | mostly talk | funniest moments are visible |
| share (×1.5) | nobody forwards it | some would | viewers tag a specific person |
| simple (×2) | many moving parts | needs one setup line | one sentence, one place, ≤3 people, airtight logic |
Each logic hole the judge lists costs 0.4. Gate G1: top 3 by weighted score → blind pairwise (both orders) → 2 finalists. Hard drops: repeats a recent episode;
cliché without a fresh angle; needs a person on screen we can't draw (decided before scripting).

## B. Script (G2/G3, before voices)
| dimension | 1 | 3 | 5 |
|---|---|---|---|
| truth | no real observation | familiar, plain | specific, slightly embarrassing truth |
| clarity | first-timer lost | clear after a few seconds | relations, place, want obvious by 5 s without exposition |
| funny | no line gets a laugh | smiles, one real laugh | several real laughs that build, biggest near the end |
| surprise | all predictable | one genuine surprise | the turn reframes everything and feels inevitable |
| escalation | flat/repetitive | rises, beats alike | each beat bigger, different lever |
| dialogue | stiff/stock/incomplete/confusing | natural but plain | every line a real person, distinct voices, complete, clear |
| character | mouthpieces | clear wants | every line from a want and a flaw, consistent with bible |
| shareability | nobody forwards | some would | viewers tag a specific person, quote the last line |
| loop | dead stop | fine but jarring replay | last moment flows into the first; replay reveals more |
**Pass (calibrated 27 Oct 2026):** average ≥ 3.2, no dimension < 2.5, funny ≥ 3.0, clarity ≥ 3.0, no BLOCKING problem,
all hard checks pass.
- **Calibration:** this judge scored the owner-approved pilot Ep 1 at 2.94 / 3.33 / 3.22 over three runs (mean 3.16).
  It scored the two scripts the owner rejected at 2.72 and 2.33. The order matched the owner's, but the judge is harsh
  and noisy (±0.3).
- **What the bar means:** at least as good as what the owner approved.
- **Raising the bar:** recalibrate it upwards as approved episodes accumulate (PILOT §4).
- **Blocking vs notes:** the judge always finds some nitpicks, so only BLOCKING problems stop a script. A problem is blocking when most first-time viewers would be confused or offended, or when it is wrong Hindi. Notes still guide the punch-up.
**Red flags (any one fails):** a line a first-time viewer would misunderstand · Hindi a native speaker wouldn't say
(natural short replies like "Toh?" are fine) · identity-based target (caste, religion, region, body, disability, gender) ·
real person/brand mocked · plot hole a viewer notices on first watch · same joke as a recent episode. Re-checks after a
fix only keep unresolved flags and new flags in changed lines (prevents a moving target).
**Hard checks (gates.script):** 110–165 words · 12–24 lines · line ≤14 words · hook ≤9 words · caption line ≤42 chars ·
no stage Hindi or stock phrases · inner voice ≤3 · truth, game and loop bridge stated.
Fail → punch-up with the judge's notes (≤2 rounds) → second finalist → still below 3.3 or red flag: no episode today
(the owner is told; nothing weak reaches him).

## C. Storyboard (G4, before render)
Pass = renderable (director.validate) + every shot has a beat + phone voices have a phone on screen + last shot mirrors
the first + loop bridge stated + continuity check finds no prop/presence/hearing/continuity problem. ≤2 repair rounds.

## D. Finished video (G5, before the owner sees it)
| check | pass |
|---|---|
| length | 48–60 s (hard max 62) |
| first line | starts ≥ 0.25 s; first word present in the transcript |
| every line | transcript matches the script ≥ 80% of words (pronunciation, nothing clipped) |
| loudness | −17.5 to −12.5 LUFS integrated; true peak ≤ −0.9 dBTP |
| captions | ≤42 chars/line, ≤2 lines, reading speed ≤20 cps |
| loop seam | last frame vs first frame visually close (same shot); no audio jump at the seam |
| visual QA | no floating/cut-off/overlapping characters, no face defects, captions clear of faces |
Defects found → automatic rerender/fix where possible; otherwise the owner is told exactly what failed.

## E. Owner review (Telegram)
Owner sees the video + the scorecard (script total, weakest dimension, what was fixed). His decision is the label:
✅ approve (no fixes) is the main quality signal. Track **first-pass approval rate** and **fix rounds per episode**.

## F. After publishing (perf.py, docs/PILOT.md)
At 48 h and 7 d vs the channel's own median of the last 10–20 episodes: engaged views, viewed-vs-swiped (Studio),
average % viewed, shares per 1,000 engaged views, subscribers per 1,000; retention per beat (where people left/rewatched).
