# Secret Smart Stuff — automated YouTube Shorts system

"The secret smart reasons behind everyday things."

This pipeline:
- researches topics;
- writes sourced scripts;
- voices them (ElevenLabs);
- illustrates them (FLUX);
- renders vertical Shorts with captions, camera moves and original music;
- checks quality;
- sends each video to the owner's Telegram for approval;
- uploads it to YouTube as private and scheduled;
- learns from analytics.

It runs on GitHub Actions, so no computer needs to stay on.

The 26–28 Oct 2026 detour into a Hindi cartoon sketch show (Bhaukaali Toons, now dropped) is on branch
`archive/bhaukaali-toons`.

## Start here

| Doc | What it covers |
|---|---|
| [CLAUDE.md](CLAUDE.md) | Standing rules for every session |
| [docs/PLAYBOOK.md](docs/PLAYBOOK.md) | The approved production process (baseline: onigiri v9) |
| [docs/LESSONS.md](docs/LESSONS.md) | Everything learned so far, from both formats |
| [docs/SETUP.md](docs/SETUP.md) | Accounts, keys, the Google app, the studio Worker; how to redo the YouTube login |
| [docs/STATUS.md](docs/STATUS.md) | What works, what is tested, what is planned |
| [docs/OPERATIONS.md](docs/OPERATIONS.md) | Runner commands, pause/resume, troubleshooting |
| [docs/EXPERIMENTS.md](docs/EXPERIMENTS.md) | Running and queued experiments |
| [docs/COSTS.md](docs/COSTS.md) | Cost per Short and monthly scenarios |
| [docs/DECISIONS.md](docs/DECISIONS.md) | Every decision, with who made it and why |
| [docs/01_NICHE_REPORT.md](docs/01_NICHE_REPORT.md) · [02_CONTENT_STRATEGY](docs/02_CONTENT_STRATEGY.md) · [03_ARCHITECTURE](docs/03_ARCHITECTURE.md) · [04_FORMAT_V2](docs/04_FORMAT_V2.md) | Niche, strategy, architecture, format evidence |

## Try it locally (no keys, no spending)

```bash
pip install -r requirements.txt          # also needs ffmpeg installed
python -m shorts.cli discover            # dry-run ideas
python -m shorts.cli produce             # renders a DRY RUN Short into build/<job>/final.mp4
python -m pytest -q                      # reliability tests
node worker/test.mjs                     # studio Worker tests
```

## Layout

```
config/             channel.yaml (identity, rules) · pipeline.yaml (budgets, schedule, providers) · experiments.yaml
shorts/             pipeline.py · cli.py · state.py · budget.py · analytics.py · learn.py · experiments.py · notify.py · prompts.py
  providers/        llm.py (Claude) · tts.py (ElevenLabs) · images.py (FLUX/BFL) · video.py (clips, off) · music.py
  render/           beats.py (beat renderer) · captions.py · assemble.py · sfx.py
  qa/               media.py (technical gate)
  publish/          youtube.py (one-tap login, channel guard, resumable idempotent upload) · verify.py
scripts/            run_command.py (all runner actions) · deploy_worker.py · state_sync.sh · collect_signals.py
worker/             Cloudflare Worker: Telegram buttons, dashboard, YouTube login, public OAuth pages
reference/approved/ onigiri-v9: the approved baseline (script, prompts, settings, timings)
assets/             music beds, sound effects, fonts
.github/workflows/  produce (daily) · command · review (tests) · analytics · summary (weekly)
vendor/ytskill/     hook scorer, title linter (MIT)
```
