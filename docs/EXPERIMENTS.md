# Experiments log

How experiments work:
- One variable per experiment. Everything else follows `docs/PLAYBOOK.md`.
- The arms and how they are assigned are defined in `config/experiments.yaml`. The pipeline assigns arms in
  balanced rotation when a video is made.
- Results are compared at the same video age (7 days), using medians, with n shown.
- An experiment concludes only when every arm reaches its minimum sample. The decision is recorded here
  and, if it changes the playbook, in the playbook's change log.

## exp-001: publish time (active, started 25 Oct 2026)

- **Why:** the owner asked to vary publish times and then double down on what works.
- **Hypothesis:** the publish time changes early distribution for an English, worldwide audience.
- **Arms** (UTC → IST / US Eastern):

  | Arm | UTC | IST | US Eastern |
  |---|---|---|---|
  | a | 13:30 | 19:00 | morning |
  | b | 17:00 | 22:30 | 13:00 |
  | c | 02:00 | 07:30 | 22:00, previous day |

- **Prior evidence:**
  - Buffer, 2026: Shorts do best in the local evening, 6–11 pm.
  - Adobe, 2025: 8–10 am underperformed.

  These are averages across many channels.
- **Metric:**
  - Primary: views at 7 days.
  - Secondary: engaged views, average % viewed, subscribers gained, all at 7 days.
- **Sample:** 8 videos per arm, about 24 days at 1 video a day.
- **Confounders to watch:**
  - Topic strength (the biggest factor).
  - Day of week.
  - The channel's growing audience over time. Arms rotate daily, which spreads this out.
- **Result:** pending.
- **Decision:** pending.

## Candidates (not started; one at a time)

| Experiment | Hypothesis | Notes |
|---|---|---|
| Hook style: question vs. bold statement | A spoken question in second one holds viewers better | Our baseline is the question; evidence grade B |
| Length: ~28 s vs. ~36 s | Shorter keeps more of the audience to the end | Needs many videos; topic noise is high |
| One AI video clip (FLUX 3) vs. stills only | Real motion lifts retention | Costs about $0.30 more per video; test only after timing is settled |
| Wit lines: 1 vs. 2 | More humour keeps viewers without hurting trust | Owner wants a lighter tone; measure % viewed |
