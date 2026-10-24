# Build Status — 24 Oct 2026

Legend: ✅ completed and tested · 🟡 written but not tested against the real service · 🔜 planned

| Area | Status | Evidence / note |
|---|---|---|
| Niche research and selection | ✅ | `docs/01_NICHE_REPORT.md`, `research/*.md` |
| Content strategy | ✅ (draft, owner-reviewed name and voice) | `docs/02_CONTENT_STRATEGY.md` |
| Architecture | ✅ | `docs/03_ARCHITECTURE.md` |
| State DB, resume after crash, retry limits | ✅ | `tests/test_reliability.py` (8 tests pass) |
| Budget guard | ✅ | Unit test |
| Duplicate topic detection (own + competitor titles) | ✅ | Unit test |
| Scene renderer (motion, blueprint callouts, cards, comparisons) | ✅ | Rendered and inspected frames |
| Captions from word timings, safe-area layout | ✅ | Rendered and inspected |
| Audio mix + loudness normalization | ✅ | QA reports −14 LUFS |
| Media QA gate | ✅ | Passes good file; rejects wrong resolution |
| End-to-end dry run (discover → package → review bundle) | ✅ | ~100 s per Short with fake providers |
| Voice (ElevenLabs Alice) | ✅ voice chosen / 🟡 API adapter | Samples made via the ElevenLabs connector; the timestamp API adapter is untested here |
| Script + research + review (Claude API) | 🟡 | Written to current docs (model IDs, web search tool); needs a live run |
| Images (FLUX.2 via BFL) | 🟡 | Written to current docs; needs a live run |
| Vision check + callout locating | 🟡 | Needs a live run |
| YouTube upload (resumable, idempotent, private + schedule) | 🟡 | Idempotency logic tested offline; the real upload is untested |
| YouTube Analytics snapshot + insights | 🟡 | Needs a live channel |
| GitHub Actions workflows + state branch | 🟡 | YAML validated; state sync tested against a local git remote; not yet run on GitHub |
| Review via GitHub issues (approve / reject / fix) | 🟡 | Script written; needs GitHub |
| Auto-publish mode | 🟡 | Off by default |
| Competitor signals (yt-dlp outliers) | 🟡 | Can't reach YouTube from here; best-effort by design |
| Weekly long-form compilation | 🔜 | Strategy item; not built |
| Pruning old review releases | 🔜 | Small script |
| Hindi audio track | 🔜 | After the channel grows |
| Optional AI video clips | 🔜 | Adapter not written; off in the pilot |

## Independent check (24 Oct 2026)

A separate reviewer compared every live adapter and workflow with the current official docs.
- No blockers were found.
- Six likely bugs and four minor issues were found, and **all are fixed**:
  - Approvals could be dropped while another run was queued.
  - A failed upload start could block retries.
  - Web searches were over-counted.
  - Long server-tool turns (`pause_turn`) weren't handled.
  - Analytics queries were missing a sort and batching.
  - The review issue lookup could open duplicates.
  - Also fixed: the TTS output format parameter, image polling robustness, YouTube text limits, and PKCE login.
- Re-tested offline: 8/8 tests pass.

## Next actions

1. **Owner:** complete `docs/SETUP.md` Steps 1–6.
2. **Claude:** push the code to the repo (if GitHub is connected) and watch the first dry run.
3. **First live Short:** fix anything the real APIs reveal, then a pilot of 30 Shorts at 1 per day.
