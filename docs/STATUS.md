# Status — 28 Oct 2026 (back to Secret Smart Stuff)

Legend: ✅ works and was tested on the real service · 🟡 built, not yet proven live · 🔜 planned

| Area | Status | Evidence / note |
|---|---|---|
| Daily production (topic → sourced script → review → voice → images → render → QA) | ✅ | onigiri v9 (approved, 1.1k+ views); live runs on GitHub Actions; restored 28 Oct |
| Telegram review (approve / fix / drop) | ✅ | Worked for both formats; fixes are minimal edits that reuse unchanged media |
| Upload private + scheduled after approval | ✅ | onigiri v9 went live on schedule (verify step) |
| Publish-time experiment (3 slots) | 🟡 | Running again from 28 Oct; needs 8 videos per arm |
| Analytics, weekly learning, dashboard | ✅ / 🟡 | Run on schedule; few data points so far |
| One-tap YouTube login (`/ytlogin`) with encrypted token | 🟡 | Worker tests pass; the first live login is pending (fixed a link-preview bug on 28 Oct) |
| Channel guard (no upload or analytics on the wrong channel) | 🟡 | Code in `shorts/publish/youtube.py`; proven once the login is done |
| Hold-for-check before sending (`hold` + `send_review`) | 🟡 | Added 28 Oct for test videos |
| Daily schedule | ✅ on | 05:47 IST; skips while a video waits for review |
| Real-motion AI clips | off | Tested 25 Oct (+$3.18 BFL on one video); experiment only |
| Pronunciation check via speech-to-text | 🔜 | Needs speech-to-text permission on the ElevenLabs key; explainers use the voice service's word timings instead |
| Weekly long-form compilation | 🔜 | Not built |
| Repo renamed back to `secret-smart-stuff` | ✅ | 28 Oct; Worker redeployed |

## Budget
- **Limits:** $2 per video, $6 per day, $45 per month (`config/pipeline.yaml`). The ElevenLabs plan is billed
  separately.
- **October:** about $39 used, mostly by the dropped sketch show. The cap resets on 1 Nov.
- **BFL image credits:** 110.5 (about $1.10) on 28 Oct.
  - That is enough for about 6–8 videos at $0.10–0.20 of images each.
  - **Top-up needed within a week:** at dashboard.bfl.ai (owner).
