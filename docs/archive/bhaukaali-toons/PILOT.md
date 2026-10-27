# Pilot test and continuous improvement

## 1. Pilot (first 6 episodes on template v3)
**Goal:** prove v3 produces better episodes than v2 at the same or lower owner effort.

**Measures per episode** (`creative/performance.json` and the episodes table):
- **Owner effort:**
  - first-pass approval (✅ with no fix): yes or no;
  - fix rounds before approval;
  - drops.
  - v2 baseline: Ep 1 = 2 rounds; Ep 2 = dropped, then 5+ rounds and still open.
- **Gates:**
  - G3 script total and the weakest dimension;
  - punch-up rounds;
  - days with no script good enough.
- **Defects found by G5 before the owner saw them:** transcript, loop seam, captions, visual.
- **Cost per approved episode:** model, voices and art.

**Success criteria** (decided before the pilot):
- First-pass approvals in at least 3 of 6 episodes.
- Median fix rounds of 1 or fewer.
- No repeat of any owner lesson with count 2 or more: first word clipped, people missing, unclear lines, no loop.
- Cost per approved episode of $2.50 or less.

**How it runs:**
- Each pilot episode is produced with `hold=true`.
- Claude checks it (frames, transcript, scorecard), then sends it with `send_review`.
- After the pilot, holding stops and episodes go straight to Telegram.

## 2. After publishing: what we measure (R4)
- **Snapshots:** at 48 h and at 7 d, for every episode.
- **Comparison baseline:** the channel's own median of the last 10–20 episodes. Raw views are never used, because views now count from the first frame.

**Metrics:**
- Engaged views.
- Viewed vs swiped away (YouTube Studio only; the owner can paste it weekly).
- Average % viewed.
- Shares per 1,000 engaged views.
- Subscribers per 1,000.
- Retention per beat (`perf.beat_map`):
  - where viewers left;
  - where they rewatched (a rise in the curve).

**Labels:**
- "Strong" = above the 75th percentile of our own episodes.
- "Weak" = below the 25th percentile.
- Single videos are noisy (Salganik et al.), so act on patterns across ≥5 episodes.

## 3. Experiments (one variable at a time, pre-registered)
**Rules:**
- Write the hypothesis, the metric and the decision rule in `docs/EXPERIMENTS.md` before the first video.
- Run alternating blocks A/B/A/B of at least 5 episodes per arm.
- Compare medians.
- A winner needs to beat the other arm in 4 of 5 matched pairs, or by more than the normal week-to-week spread.
- Otherwise record "no difference".

Queue:

| # | variable | arms | primary metric |
|---|---|---|---|
| E1 | length | ~35 s vs ~55 s | viewed-vs-swiped + shares/1k (APV alone favours short) |
| E2 | pause before punch | 0.3 s vs 0.8 s | retention change across the punch beat |
| E3 | hook type | spoken conflict line vs visual surprise first | viewed-vs-swiped |
| E4 | topical vs evergreen | festival/event tie-in vs everyday | shares/1k |
| E5 | loop bridge | explicit bridge line vs none | average % viewed > 100%? (replays) |

**Instagram:** Trial Reels can pre-test openings with non-followers. This needs at least 1,000 followers.

## 4. Judge calibration (monthly)
- Compare judge script totals with:
  - owner decisions (first-pass approval vs fix);
  - 7-day engaged views and shares (Spearman, from 10 episodes onward; `perf.update`).
- If the correlation with the owner or with viewers is below 0.3, change the anchors or the judge prompt, and add the owner's rejected scripts as low-anchor examples.
- Never let the judge overrule the owner.

## 5. Monthly review (owner + Claude, 15 minutes)
1. **Top and bottom 3 episodes:** read the retention-per-beat notes and add patterns to the writer card as **[H]** rules.
2. **Lessons list:** merge duplicates and retire lessons that never recur.
3. **Cliché bank:** add anything the owner calls "seen it".
4. **Experiments:** close finished ones and record the decision in `docs/EXPERIMENTS.md` and the template change log.
5. **Formats:** keep 70–80% of episodes in the proven format and 20–30% in experiments.

## Change log
- 2026-10-27: Template v3 created (audit `docs/AUDIT_2026-10-27.md`).
