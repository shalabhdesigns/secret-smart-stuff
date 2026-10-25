# Secret Smart Stuff — working notes for Claude

- **Read `docs/PLAYBOOK.md` first.** It is the approved production process (baseline: onigiri v9, approved
  25 Oct 2026). Follow it by default. Change it only with evidence (`docs/EXPERIMENTS.md`) or owner approval,
  and log every change in its Change log.
- Owner: Shalabh. He wants:
  - short sentences, simple language, points;
  - finished results, not process updates.
- Owner decisions so far:
  - **Approves every video before it is published.** Nothing goes public without approval.
  - Review happens on his phone (Telegram).
  - One video a day; publish times are an experiment.
- Owner feedback that is now standing rule:
  - each picture must show what is being said;
  - original music always;
  - only tasteful sound effects;
  - 1–2 light witty lines;
  - a seamless loop (end flows into start);
  - few pointers, varied styles, none unless needed.
- Before sending a video to the owner, inspect it:
  - a frame contact sheet;
  - first frame vs last frame;
  - music level at the end and start;
  - no dropouts;
  - send a 3× loop preview with it.
- Nothing runs on the owner's laptop. Everything runs in GitHub Actions (private repo
  `shalabhdesigns/secret-smart-stuff`).
  - State lives in SQLite on the `state` branch.
  - Claude drives runs by pushing `commands/request.json` (see `scripts/run_command.py`).
- Secrets live only in GitHub Actions secrets, never in files.
- Commit trailer: see the session's attribution instructions.
