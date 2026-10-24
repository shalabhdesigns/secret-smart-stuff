# Decision Log — YouTube Shorts System

Each entry: date, decision, who decided, why. Newest at the bottom.

## 2026-10-24 — Owner answers (batch 1 and 2)

| Topic | Decision | Source |
|---|---|---|
| Language / audience | Not fixed. Research compares English-global vs Hindi/Hinglish-India and recommends one. | Owner delegated |
| Monthly budget | ₹2,000 – ₹8,000 all-in (≈ US$24 – $95) | Owner |
| Approval | Owner approves every video at first; move to automatic only after quality is proven | Owner |
| Science / health / biomedical topics | Excluded. Keep the channel separate from the owner's professional field. | Owner |
| Presentation | Faceless, consistent AI narrator (ElevenLabs) | Owner |
| Hosting | GitHub Actions (scheduled cloud jobs, secrets for API keys) | Owner |
| Owner time | 3 – 7 hours per week | Owner |
| Excluded topics | Politics and news; finance and crypto; religion and astrology; science, health, biomedical | Owner |
| Kids-targeted content | Not excluded by owner, but "made for kids" limits comments and ads; research will weigh it | Owner (not excluded) |

## 2026-10-24 — Environment findings (facts from inspection)

- Cloud workspace shell has no network access to YouTube, Google APIs, ElevenLabs API or OpenArt. MCP connectors (ElevenLabs, OpenArt) and WebSearch/WebFetch do work.
- Installed: ffmpeg 6.1.1, Python 3.13, Node 22, yt-dlp (installed, but cannot reach YouTube from this shell).
- Owner's Mac (Apple Silicon) is linked through the desktop app; no folder connected; not always on.
- No GitHub account is linked to this session yet → needed before GitHub Actions deployment.
- No YouTube connector exists. vidIQ connector exists (research only) — suggested to owner, not connected.
- `youtube-agent-skill` (MIT) cloned to /home/claude/ext. Reusable tools: hookscore.py, title.py, swipe.py, retention.py. It does not publish and targets long-form mostly.

## 2026-10-24 — Platform facts from research (see research/platform_costs.md for sources)

- Partner Program changes on 1 Feb 2027 (new channels): 1,000 subs + 20M Shorts views in 90 days, plus a monthly gate of 10M qualified Shorts views in 90 days to earn from Shorts. → Shorts ad money alone is a weak plan for a new channel; build other revenue (affiliates, sponsors, long-form) into the strategy.
- Shorts revenue estimates: about $0.33 per 1,000 views (US) vs about $0.008 (India) — estimates. Music tracks cut the payout share; original audio or none pays best.
- July 2026 AI policy: template / mass-produced AI content is demonetized at channel level; original characters and stories made with AI are allowed. → Originality and visible creative direction are a hard requirement, not a nice-to-have.
- Upload quota: 100 uploads/day bucket at 1 unit each (since 1 Jun 2026) — not a constraint.
- "Unverified project → private only" rule: Google pages conflict. Must test with one upload early.
- OAuth consent screen must be "In production", or refresh tokens expire after 7 days and break unattended runs.
- OpenArt commercial rights need Plus ($27/mo) or higher; ElevenLabs commercial use needs a paid plan (Starter about $6/mo, Creator about $22/mo — re-check before buying).
- GitHub Actions: 2,000 free min/month (private repo); cron can be delayed. Haiku-class LLM: about $0.10 / $0.50 per M tokens.

## 2026-10-24 — Niche locked (owner decision)

| Topic | Decision | Source |
|---|---|---|
| Niche | Hidden design and origins of everyday things | Owner chose the recommended option |
| Language | English, global audience first; Hindi audio track later | Owner delegated; recommendation accepted with niche |
| Science line | Simple "why the design works" explanations are fine; no science/health/biomedical research topics | Owner |
| Affiliates | Yes, where they fit naturally, always disclosed (after the 500-sub Shopping tier) | Owner |
| Accounts | No YouTube channel or Google Cloud project yet → setup guide needed | Owner |

## 2026-10-24 — Strategy and architecture review (owner)

| Topic | Decision | Source |
|---|---|---|
| Channel name | **Hidden by Design** (handle availability to be checked at creation) | Owner |
| ElevenLabs plan | Creator or higher (commercial use OK) | Owner |
| Voice samples | Approved to spend ElevenLabs credits on 4–5 narrator samples | Owner |
| Claude API + Gemini API costs | Owner wants to discuss cheaper options before committing | Owner |

## 2026-10-24 — Voice and providers (owner)

| Topic | Decision | Source |
|---|---|---|
| Narrator | **Alice** (ElevenLabs premade voice `Xb7hH8MSUJpSbSDYk0k2`, British, clear educator) | Owner |
| Measured voice cost | ≈ 337 credits / ≈ $0.06 per 23-second read (eleven_v4) | Observed |
| Writing + fact checks | Claude API (cheap model for routine steps, stronger model for scripts) | Owner accepted recommendation |
| Images | FLUX.2 (budget "klein" tier) via Black Forest Labs API; Gemini image as fallback | Owner accepted recommendation |
| vidIQ | Skip for now (see reasoning in chat): its connector works only inside Claude, not in GitHub Actions; public data + YouTube API cover the pipeline's needs | Recommendation accepted |

## Implications (recommendations, not yet final)

- Budget of ≈ $24–95/month rules out AI video in every scene of a daily Short. Production style must lean on images + programmatic motion + deterministic editing, with AI video used sparingly.
- Public auto-upload depends on Google's API audit; until then uploads are private and the owner publishes manually or after approval.

## 2026-10-24 — Channel name changed (owner)

| Topic | Decision | Source |
|---|---|---|
| Channel name | **Secret Smart Stuff** (replaces "Hidden by Design"; @hiddenbydesign was taken) | Owner |
| Handle | **@secretsmartstuff** (owner confirmed available) | Owner |
| Tagline | "Why everyday things are designed the way they are." | Recommendation |
| Persona | Alice's voice is "the Professor": calm, curious teacher | Recommendation |

## 2026-10-24 — Final channel name (owner)

| Topic | Decision | Source |
|---|---|---|
| Channel name | **Secret Smart Stuff** (replaces Professor of Things) | Owner |
| Handle | **@secretsmartstuff** (claimed by owner) | Owner |
| Channel Gmail | secretsmartstuff@gmail.com (separate account, as recommended) | Owner |
| Tagline | "The secret smart reasons behind everyday things." | Recommendation |
