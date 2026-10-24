# Risks and Limitations

Likelihood is given in words, because there is no reliable data for precise percentages.

## 1. Market risk

| Risk | Likelihood | Impact | Warning sign | Mitigation | Residual |
|---|---|---|---|---|---|
| Niche saturates (leaders plus a copycat wave) | Medium | High | Our median views fall while leaders' growth also stalls | Distinct design-diagram angle; India/Asia lane; skip topics competitors covered unless the angle is better | Medium |
| Views don't turn into subscribers | Medium–high (common for fact channels) | Medium | Under 1 subscriber per 1,000 views | Series framing, weekly compilations, consistent look and voice | Medium |
| Virality simply doesn't come | Medium | High | First 30 Shorts under ~1,000 median views | Kill/pivot rule in the niche report; alternative niche ready | Real and unavoidable |

## 2. Platform risk

| Risk | Likelihood | Impact | Warning sign | Mitigation | Residual |
|---|---|---|---|---|---|
| **AI "inauthentic / mass-produced" demonetization** | Medium | Very high (whole channel) | Monetization review rejection; "reused content" notice | Varied visuals, owner approval, sourced facts, 1/day not 4/day, real insight in each video | Medium. Policy wording is broad. |
| Partner Program rule change on 1 Feb 2027 (20M Shorts views to join) | Certain (announced) | High for ad income | — | Plan income from Shopping/affiliates (500-sub tier), sponsors, long-form | Ad revenue may stay small for a long time |
| API project locked to private uploads | Unclear (Google docs conflict) | Medium | Uploaded videos say "locked private" | Audit form; manual publish in Studio meanwhile | Low (10 s per video by hand) |
| Algorithm or policy changes | Ongoing | Medium–high | Sudden drop in views across all videos | Diversify formats; keep the evergreen core | Medium |
| Account enforcement (strike) | Low with this niche | Very high | Any policy email | No brands as subject, no real faces, no forbidden topics, AI disclosure | Low |

## 3. Content risk

| Risk | Likelihood | Impact | Mitigation | Residual |
|---|---|---|---|---|
| Factual errors | Medium (LLMs make mistakes) | High (trust, misinformation) | Sources required per claim; independent reviewer with web search; owner approval | Low–medium. No system is error-free. |
| Repetitive, samey output | Medium over time | Medium | Variety rules, pillar rotation, review "originality" score | Medium |
| AI image errors (wrong object details, stray text) | Medium | Medium | Vision check, one retry, flags shown in the review | Medium. Some errors pass to your review. |

## 4. Legal and rights risk

| Risk | Note | Mitigation |
|---|---|---|
| Copyright | We generate our own images and narration; no third-party footage or music | Keep the music off, or use original/licensed music only |
| Trademarks | Brands as the subject or logos in images | Prompts forbid logos; vision check flags text and logos; titles avoid brand names |
| Voice | Alice is an ElevenLabs premade voice, used on a paid (commercial) plan | Keep a paid plan while publishing |
| Disclosure | Realistic AI imagery → set the "altered or synthetic content" flag | Set automatically (`containsSyntheticMedia: true`) plus a note in the description |
| Affiliates | Must be disclosed | Add a disclosure line when product links are added (manual step) |
| Image rights (FLUX via BFL API) | BFL's terms allow commercial use of outputs on its paid API | Re-check BFL's terms before monetizing |

## 5. Technical risk

| Risk | Mitigation |
|---|---|
| Provider outage or API changes (Anthropic, ElevenLabs, BFL, YouTube) | Retries with backoff; job resumes later; `alert` issue; providers swappable in config |
| yt-dlp breaks when YouTube changes pages | Signals are optional; discovery continues without them |
| GitHub cron delays or skipped runs | Daily summary makes gaps visible; manual "Run workflow" |
| **Live integrations are untested** (no network from the build environment) | Step 7–8 of SETUP is the first real test. Expect 1–3 small fixes on the first live run. |

## 6. Financial risk

- Budget guard stops spending before limits (per video, day, month).
- Failed jobs never retry endlessly (3 attempts, then human review).
- Revenue is uncertain and may be close to zero for months. Treat the first 3 months as a paid experiment of roughly ₹2,500–3,500 per month.

## 7. Operational risk

| Risk | Mitigation |
|---|---|
| Refresh token expiry | Consent screen "In production"; clear error message; re-run the auth script |
| Keys leak | Keys only in GitHub secrets; never in code or logs; ElevenLabs key limited to TTS |
| You're unavailable (travel, busy weeks) | Videos simply wait in review; nothing publishes without approval in manual mode |
| Two workflows writing state at once | A concurrency group serializes them; state push retries |

## 8. Analytics risk

- Data arrives 48–72 hours late.
- "Viewed vs swiped away" seems to be visible in Studio only.
- Small samples mislead: don't judge a video under ~1,000 views or before 7 days.
- Pillar weights only change once 10+ videos with 1,000+ views exist, and then only by 0.5–1.5×.

---

## What cannot be fully automated (hard limits)

- Creating accounts and giving consent (YouTube, Google Cloud, API keys): you, once.
- Google's possible upload audit: you file it if needed.
- Monetization, Shopping and affiliate sign-ups: you, in YouTube Studio.
- Final responsibility for facts and policy: you. That's why approval is on by default.

## What may stay unreliable

- AI image accuracy on fine object details.
- Fact-checking of obscure claims (the reviewer may miss errors).
- Hook scoring. It's a heuristic, not a prediction.

## What I could not verify

- That the live API calls work end to end. This environment has no network route to those services.
- The current "locked private" rule for new API projects.
- Exact token use per script.
- Whether any niche competitor data is exactly right. It comes from third-party stats sites.
