# Format v2 — "Question first, fast cuts, light text"

Date: 25 Oct 2026 · Based on `research/shorts_retention.md` (evidence-graded) · Replaces the v1 scene format.

## Why v1 was changed

The first live Short (onigiri wrapper, 36 s) measured: 6 shots (one cut every 6 s), the question
asked only at 5.5 s, no payoff until 30 s, no music or sound, and a text-card ending that made the
replay obvious. Research says each of those costs retention.

## The evidence that shaped v2

| Rule | Evidence | Grade |
|---|---|---|
| Speech in the first 3 s (ask the question in second one) | Emplifi, 10,110 brand Reels, Mar 2026: +24.7% retention at 10 s vs music/visual-only openings; YouTube and Instagram creator guidance agree | B |
| Question = hook, answer = ending | Highest-performing explainer Short found (Zack D. Films "How Stitches Work", 31 s, ~253M views) opens on the question, ends when answered | C |
| More cuts, simple frames | Wals et al., J. Acad. Marketing Science, Mar 2026 (eye-tracking, 2,520 sessions): cuts raise attention; visual complexity lowers it with a delay | A |
| First payoff by ~12–15 s | OpusClip analysis of 500 TikToks: ~+20% retention vs payoff at the end | C |
| Keep text light | Emplifi: text overlays −6% retention at 10 s and −4.5% at 30 s on speech-led Reels | B |
| Original or no music | YouTube Help: one partner track halves the Short's revenue-pool share; original/third-party music is not deducted | A |
| Seamless loop | Emplifi: +18.7% replays for ≤7 s clips, smaller effect as length grows; YouTube counts replays as views | B |
| Vary the template every upload | YouTube "inauthentic content" rule (Jul 2025) names "slideshows that all have the same narration" | A |
| 28–40 s is fine | Instagram tip (30–60 s), Adobe creator survey Jun 2026 | B/C |

**What the evidence does *not* support:** "show the result first" (no measured gain; question-first is
what's measured), AI video over clean stills (no data), heavy kinetic text (negative data), music-only
openings (negative data).

## The v2 structure (30–36 s)

| Time | Beat | Visual | Sound |
|---|---|---|---|
| 0.0–2.8 s | **The question**, spoken from frame 1, 8–12 words | Punch-in on the hidden detail, circled; 2–3 word hook card for ≤1.5 s | Music bed starts low |
| 2.8–12 s | 3 beats: the odd thing, the wrong guess, **the first "aha"** | New visual state every 2.5–3.5 s (new image, or same image re-framed on a new focus); one callout per beat | Tick on each callout |
| 12–26 s | 4–5 beats: how it works, a date or number, a comparison | Punch-ins, drifts, one draw-on arrow, one keyword pop max | Whoosh on whip cuts, pop on the keyword |
| 26–33 s | 2 beats: the full answer; optional blueprint card | Card or detail | Soft ding on the payoff |
| last 2–3 s | **Closing line that leads back into the question** | Same picture as beat 1, camera settling to the opening frame | Music bed loops |

Rules enforced in code: 11–13 beats; 5–9 words per beat; 6–7 images reused with different focus;
≤2 keyword pops; ≤1 card; ≤1 arrow; last beat reuses the first image; speech trimmed to start at 0.0 s;
captions lighter (72 px) and never stacked on a callout; per-video style seed rotates motion order,
whip cadence and music bed.

## Cost per Short (v2)

Unchanged from v1 (images are reused across beats): about **$0.45–0.70**. The optional AI video clip
(FLUX 3 image-to-video, ~$0.30 for a 5 s draft) stays **off** until an A/B test justifies it.

## Strategic note from the research

Both benchmark channels in this niche are **long-form** (4–6 minute "episodes", ~6 per week), not
Shorts. The stills-plus-voice pipeline suits that format well, and YouTube's Feb 2027 Shorts rule makes
Shorts-only monetisation harder. Plan: keep Shorts for discovery and add a weekly long-form episode built
from the same research (next build item).
