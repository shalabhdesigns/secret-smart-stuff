# Pipeline Architecture

Date: 24 Oct 2026 · Status: **design accepted for build; deployment details pending owner accounts**

## 1. The big picture

```
 GitHub Actions (always on, free tier)                      Owner (phone)
 ┌──────────────────────────────────────────────────────┐
 │ daily 06:00 IST   discover → score → backlog          │
 │ daily 07:00 IST   produce next approved topic:        │
 │                   script → fact sheet → voice →       │
 │                   images → (optional clip) → render → │
 │                   QA gate → package metadata          │──► GitHub Issue "Review: <title>"
 │                                                       │      preview MP4 + script + sources
 │ on "approve" comment  upload as private + schedule    │◄── comment: approve / reject / fix: …
 │ every 6 h         analytics snapshot                  │
 │ daily 22:00 IST   daily summary report                │──► Issue/email summary
 └──────────────────────────────────────────────────────┘
        state: SQLite file (state/shorts.db) committed to a `state` branch after every run
        media: build artifacts kept 14 days; final MP4s attached to the review issue
```

**Why this shape**
- **GitHub Actions** is free for our volume (~10–20 min per Short; 2,000 free min/month on a private repo), always on, and keeps API keys as encrypted secrets. Its network is open, unlike this Claude workspace.
- **One SQLite file** holds all state. There's no database server to pay for or maintain. Committing it after each run gives history and crash recovery.
- **GitHub Issues as the approval desk.** The owner gets a phone notification, watches the preview, and replies `approve`. Free, logged and simple. Email or Telegram can be added later.
- **Plain Python + FFmpeg.** No agent framework, no long multi-agent chats. AI is called only where judgement is needed (ideas, scripts, fact review), with structured JSON outputs.

## 2. Providers (swappable adapters)

Each provider sits behind a small interface (`shorts/providers/`). Changing a model is a config change, not a rebuild.

| Job | Default | Fallback | Est. cost per Short |
|---|---|---|---|
| Ideas, scripts, review | Claude API: Sonnet-class for scripts, Haiku-class for scoring and checks | Any OpenAI-compatible LLM | $0.05 – $0.20 |
| Fact sourcing | Claude API web search tool | Manual sources in the review issue | ~$0.05 (≈5 searches) |
| Voice + word timings | ElevenLabs TTS "with timestamps" | ElevenLabs Flash model (half the credits) | ~500–1,000 credits (inside the plan) |
| Images | Google Gemini image ("Nano Banana 2.x") via Gemini API | FLUX.2 via Black Forest Labs / fal | $0.30 – $0.80 (8–12 images) |
| Short video clip (optional, off in pilot) | fal-hosted video model | None (stills + motion) | $0.30 – $1.00 per 3–5 s |
| Diagrams, captions, motion, mix | Our own code + FFmpeg (free) | — | $0 |
| Upload, analytics | YouTube Data API v3 + Analytics API | Manual upload from the review issue | $0 |

Prices are third-party or list estimates checked on 24 Oct 2026. Every call records its real cost when the provider reports one.

## 3. Stages, limits and failure handling

| Stage | What it does | Known limits / dependencies | Likely failures | Mitigation |
|---|---|---|---|---|
| **A. Discovery** | Pulls candidate objects from the inventory, search suggestions, Reddit "why is…" questions, and competitor outliers (public channel lists via yt-dlp, using `swipe.py`'s multiple-over-median method) | Public data only; YouTube Data API search costs 100 units per call; yt-dlp can break when YouTube changes its pages | Source blocked or empty | Each source is optional; the backlog never depends on one. Every item stores source URL, time and confidence. |
| **B. Topic scoring** | Scores each idea 0–100: audience relevance, novelty versus our past videos, momentum, hook strength, story potential, production cost, policy risk | LLM scores are noisy | Inflated scores; repeats | Fixed rubric with JSON output; deterministic duplicate check (normalized title + object name + embedding-free shingle similarity); keep the top N only |
| **C. Script** | 3 angles → pick 1 → 5 hooks scored by `hookscore.py` → script with scene list, word count, on-screen text, visual prompts, fact sheet with sources | LLMs invent facts | Unsupported claim; too long | Every claim must cite a source URL from the search step; second-model review; word budget at about 2.6 words per second; bounded rewrite (max 2) |
| **D. Voice** | ElevenLabs TTS with character timestamps → word timings → captions | Plan credit limits; pronunciation of brand or foreign words | Mispronunciation; credit exhaustion | Pronunciation dictionary in config; budget guard checks credits first; one retry, then review queue |
| **E. Visuals + render** | Images per scene → code-drawn blueprint callouts → motion → captions → audio mix (narration, quiet original bed, SFX) → final encode | Image models can draw wrong details and garbled text | Malformed object; text in image | Prompts forbid text and logos; per-image vision check (cheap model) for text and artifacts; regenerate only the failed image (max 2) |
| **F. QA gate** | Media checks (resolution, fps, loudness, silence, black and frozen frames) + script checks + independent AI review score ≥ 7/10 + duplicate check | AI review is not proof of accuracy | False pass | Hard gates are code, not AI; the owner approves every video during the pilot |
| **G. Packaging** | Title (linted by `title.py`), description with sources and AI disclosure, 3–5 relevant hashtags, category, language | Tags barely affect reach | Clickbait drift | Title must match the script's main claim; no all-caps spam; length checks |
| **H. Publish** | Resumable upload as **private**, optional `publishAt`, record video ID, poll processing | Unverified API project may lock videos to private (Google docs conflict); OAuth must be "In production"; 100 uploads/day | Expired token; partial upload; lock | SHA-256 idempotency record before upload; "started but unconfirmed" blocks re-upload until a human checks; clear error messages in the issue |
| **I. Analytics** | Every 6 h for 7 days, then daily for 28 days: views, engaged views, avg % viewed, likes, comments, shares, subs gained | Data lags 48–72 h; "viewed vs swiped away" appears to be Studio-only | Missing metrics | Store raw API JSON; compare videos at equal age; weekly owner note for Studio-only metrics |
| **Ops** | Budget guard, retries with backoff, job state, daily summary | Actions cron can run late; scheduled workflows in public repos pause after 60 days of inactivity | Missed run; silent stop | Private repo; every run commits state (activity); daily summary issue makes silence visible |

## 4. Approval flow (pilot phase)

1. A finished Short opens a GitHub Issue with the MP4, the script, the sources and the QA report.
2. The owner comments:
   - `approve` → uploaded as private and scheduled for the next publishing slot.
   - `reject: reason` → the topic is marked rejected, and the reason feeds scoring.
   - `fix: what to change` → one bounded repair, then a new review issue.
3. After 30 approved Shorts with few fixes, the owner can switch to **auto mode**. In auto mode, Shorts with a review score ≥ 8 publish automatically and the rest still come for review.

## 5. What cannot be fully automated (hard limits)

- **Creating accounts and consent:** the YouTube channel, Google Cloud project, OAuth consent and API keys must be done by the owner once.
- **Google's possible upload audit:** if the project is locked to private, a human must file the audit form.
- **"Viewed vs swiped away"** and some Shorts metrics are visible in YouTube Studio only.
- **Monetization applications and affiliate or Shopping setup** are done by the owner in YouTube Studio.
- **Final accountability for facts:** automation reduces errors but cannot guarantee zero errors.
