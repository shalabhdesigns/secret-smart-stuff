# Sab Theek Hai — production template v3 (27 Oct 2026)

This is the canonical workflow. It replaces the v2 writers' room and the old playbook sections on script, animation, sound
and QA. Rules live in three cards that the models read: `docs/SHOW_BIBLE.md`, `docs/craft/WRITER_CARD.md`,
`docs/craft/STAGING_CARD.md` (+ `docs/craft/EXPRESSIONS.md`). Scores and thresholds: `docs/RUBRIC.md`. Why each decision
was made: `docs/AUDIT_2026-10-27.md` and `docs/research/`.

**Principle:** cheap stages filter hard; expensive stages only see material that already passed. The owner only sees
an episode that passed every gate, with its scorecard. The owner and real viewers — not a model — are the final judges,
and the model judges are checked against them.

## Stages, deliverables, gates

| # | stage | deliverable | gate (pass criteria) | code |
|---|---|---|---|---|
| 0 | Context | date, publish slot, timely events (`creative/calendar.json`), world memory, owner lessons, audience data | — | `room._ctx`, `world.brief`, `lessons.brief`, `perf.brief` |
| 1 | Observe | 24 specific behaviours (object/phrase/number + unspoken rule), rotated life areas | — | `room.write` (writer, temp 1.0) |
| 2 | Premise | 8 premise cards: truth, violation+benign, game, wants/flaws, 3 beats, turn, punch, button, loop bridge, who-is-who cue, visual gags, props, art needed, share trigger, fresh angle | **G1**: drop repeats; flag clichés; anchored screen (RUBRIC A) → top 3 → blind pairwise both orders → 2 finalists | `gates.repetition/cliche`, `judge.premise_scores`, `judge.pairwise` |
| 2b | Art first | new person / place for the leading premise drawn and checked NOW | art QA (identity, face placement, no cut-offs); failure → written around before scripting | `flow.art_for_premise`, `art.py` |
| 3 | Script | 2 full scripts (one per finalist), beat-labelled lines, joke map (A/B meaning, reveal word) | **G2**: blind pairwise picks the stronger | `room.write`, `judge.pairwise` |
| 4 | Punch-up | same story, weak lines replaced by the best of 3 alts, dead lines cut | **G3**: RUBRIC B pass + hard checks; ≤2 punch-ups, then 2nd finalist; best < 3.3 or red flag → **no episode today** | `judge.rubric/passes`, `gates.script` |
| 5 | Storyboard | full plan: shots with beats, poses/props, expressions/events, holds, loop mirror | **G4**: renderable + storyboard checks + continuity check (props, presence, hearing, continuity, loop); ≤2 repairs | `director.validate`, `gates.storyboard`, `judge.storyboard_check` |
| 6 | Voices | one fixed voice per character; lines prepared without trimming into words | first word present (G5) | `voices.py`, `prep_lines.py` |
| 7 | Animate + edit + sound | render, captions, mix, loop seam | — | `director.build`, `puppet.py`, `sketch_assemble.py` |
| 8 | Final QA | technical + transcript + captions + loop seam + visual QA | **G5**: RUBRIC D; failures fixed or reported | `qa.py` |
| 9 | Owner review | Telegram video + scorecard; ✅ / ✏️ fix / 🗑 drop | owner decision | `flow.py`, worker |
| 10 | Learn | lessons from every note; perf at 48 h/7 d mapped to beats; judge calibration | monthly review (docs/PILOT.md) | `lessons.py`, `perf.py`, `analytics.py` |

## Revision protocol (owner ✏️)
1. The note becomes a lesson (`lessons.add`) if it generalises.
2. The fix keeps the same story. Only what the note asks changes; line ids of unchanged lines stay (voices reused).
3. The revised script passes G3's hard checks and red flags; the plan passes G4.
4. Art the fix needs is drawn first; the message to the owner lists what really changed and what could not be done.
5. 🗑 Drop = a new episode from stage 1, with the owner's note as feedback.

## Targets that are decisions, not research (tune with data)
- Length ~55 s (48–60): owner's request; research on optimal Shorts length conflicts (docs/research/R4) → planned test.
- Laugh every ~8–10 s; 0.5 s stillness before the punch; first line at 0.30 s; loop on every episode.

## Cost (typical, per new episode)
Writers' room ≈ $0.9–1.4 (writer Opus with prompt caching, judge Sonnet), voices ≈ $0.3, QA ≈ $0.05, art only when needed
(weekly cap). A failed G3 day costs ≈ $1 and protects the owner's time.

## What the owner does
Approve, fix with a note, or drop — on Telegram, once a day. Everything else is automatic.
