# Professor of Things — automated YouTube Shorts system

"Every everyday object has a reason. We show you the reason in under a minute."

A small, reliable pipeline that researches topics, writes sourced scripts, voices
them (ElevenLabs), illustrates them (FLUX), renders vertical Shorts with
blueprint-style callouts and captions (FFmpeg), checks quality, asks the owner to
approve, uploads to YouTube as private + scheduled, and learns from analytics.
It runs on GitHub Actions, so no computer needs to stay on.

## Start here

| Doc | What it covers |
|---|---|
| [docs/SETUP.md](docs/SETUP.md) | One-time setup: accounts, keys, first runs |
| [docs/OPERATIONS.md](docs/OPERATIONS.md) | Daily rhythm, pause/resume, troubleshooting |
| [docs/STATUS.md](docs/STATUS.md) | What is built, tested, untested, planned |
| [docs/01_NICHE_REPORT.md](docs/01_NICHE_REPORT.md) | Why this niche |
| [docs/02_CONTENT_STRATEGY.md](docs/02_CONTENT_STRATEGY.md) | Pillars, hooks, quality bar, pilot plan |
| [docs/03_ARCHITECTURE.md](docs/03_ARCHITECTURE.md) | Stages, limits, failure handling |
| [docs/COSTS.md](docs/COSTS.md) | Cost per Short and monthly scenarios |
| [docs/RISKS.md](docs/RISKS.md) | Risks, hard limits, what cannot be verified |
| [docs/DECISIONS.md](docs/DECISIONS.md) | Every decision with who made it and why |

## Try it locally (no keys, no spending)

```bash
pip install -r requirements.txt          # also needs ffmpeg installed
python -m shorts.cli discover            # dry-run ideas
python -m shorts.cli produce             # renders a DRY RUN Short into build/<job>/final.mp4
python -m shorts.cli status
python -m pytest -q                      # reliability tests
```

## Layout

```
config/            channel.yaml (identity, rules) · pipeline.yaml (budgets, schedule, providers)
shorts/            pipeline.py · cli.py · state.py · budget.py · analytics.py · prompts.py
  providers/       llm.py (Claude) · tts.py (ElevenLabs) · images.py (FLUX/BFL) - each with a dry-run fake
  render/          compose.py (scenes) · captions.py · assemble.py (FFmpeg)
  qa/              media.py (technical gate)
  publish/         youtube.py (resumable, idempotent upload)
scripts/           youtube_auth.py · collect_signals.py · open_review.sh · handle_review.py · state_sync.sh
.github/workflows  produce · review · analytics · summary
vendor/ytskill/    hook scorer, title linter (MIT, from youtube-agent-skill)
```
