# Bhaukaali Toons — production and upload system

Hindi (Hinglish / UP Hindi) cartoon sketch comedy for YouTube Shorts. Home of the sketch show
**Sab Theek Hai**: Dev can never say "no", Rocky the barber never listens, Meera never misses a chance.

- YouTube: [@bhaukaalitoons](https://www.youtube.com/@bhaukaalitoons) · Instagram: @bhaukaalitoons
- Account: bhaukaalitoons@gmail.com · Site (privacy policy for the Google app): https://bhaukaali-toons.vercel.app

## Start here

| Doc | What it covers |
|---|---|
| [CLAUDE.md](CLAUDE.md) | Standing rules for every session |
| [docs/PLAYBOOK.md](docs/PLAYBOOK.md) | How a sketch is written, voiced, animated, checked and delivered |
| [docs/SETUP.md](docs/SETUP.md) | Accounts, keys, Google app, GitHub secrets — and how to redo the YouTube login |
| [docs/STATUS.md](docs/STATUS.md) | What works, what is manual, what is planned |
| [docs/OPERATIONS.md](docs/OPERATIONS.md) | Runner commands and troubleshooting |
| [creative/puppet/README.md](creative/puppet/README.md) | The locked character library (consistency rules) |
| [docs/DECISIONS.md](docs/DECISIONS.md) | Decisions log |

## Layout

```
creative/puppet/   rig.json (characters, poses) · scenes · assembly specs
assets/puppet/     locked character art (poses, heads, hair variants) · voice lines
scripts/puppet/    puppet.py (2D engine) · align.py · bake_variant.py · qa_faces.py · prep_lines.py
scripts/           sketch_assemble.py (captions, sound, music, loudness) · run_command.py (runner actions)
config/            channel.yaml (identity) · pipeline.yaml
shorts/            upload, analytics, state (shared with the retired explainer pipeline)
site/              public home page + privacy policy (Vercel)
docs/archive/      the retired "Secret Smart Stuff" explainer format
```
