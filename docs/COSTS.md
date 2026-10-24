# Cost Estimate

Date: 24 Oct 2026 · Exchange rate used: **₹85 = $1** (approximate).
Prices are list prices checked on 24 Oct 2026, unless marked "measured". They change. Re-check before topping up.

## Cost per Short (30–40 seconds, no AI video)

| Item | Basis | Low | High |
|---|---|---|---|
| Script + research (Sonnet 5.5, $2 / $10 per M tokens, plus about 6 web searches at $0.01) | ~25–40k input, ~3–5k output tokens | $0.12 | $0.20 |
| Independent review (Haiku 5.5, plus about 4 searches) | | $0.04 | $0.06 |
| Owner-requested or automatic fix pass (about 1 in 3 videos) | averaged | $0.02 | $0.07 |
| Topic ideas + scoring (shared across a batch) | Haiku | $0.01 | $0.02 |
| Image checks + callout locating (vision, about 8 calls) | Haiku | $0.01 | $0.02 |
| Images: 6–9 FLUX.2 klein at about $0.015, plus about 25% retries | | $0.11 | $0.17 |
| Voice (Alice): **measured** about 337 credits ≈ $0.061 per 23 s read; 30–40 s ≈ 450–600 credits | uses plan credits | $0.08 | $0.11 |
| GitHub Actions: about 8–15 min per Short | free tier | $0 | $0 |
| YouTube API | free | $0 | $0 |
| **Total per Short (marginal)** | | **≈ $0.39 (₹33)** | **≈ $0.65 (₹55)** |

The voice line is paid for by your ElevenLabs Creator plan (fixed cost below). It isn't extra unless you run out of plan credits.

## Monthly scenarios

Fixed costs: **ElevenLabs Creator ≈ $22/month (≈ ₹1,870)**. GitHub, YouTube API and Google Cloud are $0 at this scale.

| Volume | Variable AI cost | + ElevenLabs | **Total / month** | GitHub minutes (2,000 free) | Fits ₹2–8k? |
|---|---|---|---|---|---|
| 15 Shorts (pilot start) | $4 – $8 | $22 | **$26 – $30 (₹2,200 – 2,550)** | ~200 | ✅ |
| 30 Shorts (1/day) | $9 – $17 | $22 | **$31 – $39 (₹2,650 – 3,300)** | ~400 | ✅ |
| 60 Shorts (2/day) | $18 – $33 | $22 | **$40 – $55 (₹3,400 – 4,700)** | ~800 | ✅ |
| 90 Shorts (3/day) | $27 – $50 | $22* | **$49 – $72 (₹4,150 – 6,100)** | ~1,200 | ✅ (*voice credits get tight; may need a higher plan) |

The pipeline's own limit (`config/pipeline.yaml`) is **$45/month for variable AI spend**. It pauses before crossing that.

## Hidden and indirect costs

| Cost | Size | Note |
|---|---|---|
| Failed generations | +10–25% on images | Already included in the image line as retries |
| Rejected topics (you reject after full production) | ~$0.50 each | Rejecting early (at script stage) is cheaper; review issues show the script first |
| AI video clips (off in the pilot) | $0.30–$1.00 per 3–5 s | Turn on only if the data shows motion matters |
| Weekly long-form compilation | ~$0 extra (reuses Shorts) | Builder not implemented yet |
| GitHub storage for review videos | ~20–40 MB per Short in Releases | Free, but prune old review releases (planned) |
| Your time | 3–7 h/week | The largest real cost |
| Price changes | unknown | Keep the budget limits on |

## What is uncertain

- **Token counts per script** are estimates. Web-search results can make input tokens larger. The first 10 live runs will show the real number; it's recorded per job in the state database.
- **ElevenLabs credits per Short** depend on script length and retakes. The measured figure comes from one 331-character read.
- **FLUX prices** come from Black Forest Labs' list via a third-party page (Sep 2026). Confirm on the BFL dashboard.
