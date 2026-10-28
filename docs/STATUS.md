# Status — 28 Oct 2026 (back to Secret Smart Stuff)

Legend: ✅ works and was tested on the real service · 🟡 built, not yet proven live · 🔜 planned

| Area | Status | Evidence / note |
|---|---|---|
| Daily production (topic → sourced script → review → voice → images → render → QA) | ✅ | onigiri v9 (approved, 1.1k+ views); live runs on GitHub Actions; restored 28 Oct |
| Telegram review (approve / fix / drop) | ✅ | Worked for both formats; fixes are minimal edits that reuse unchanged media |
| Upload private + scheduled after approval | ✅ | onigiri v9 went live on schedule (verify step) |
| Publish-time experiment (3 slots) | 🟡 | Running again from 28 Oct; needs 8 videos per arm |
| Analytics, weekly learning, dashboard | ✅ / 🟡 | Run on schedule; few data points so far |
| One-tap YouTube login (`/ytlogin`) with encrypted token | ✅ | Owner connected Secret Smart Stuff on 28 Oct; survived the Worker move |
| Channel guard (no upload or analytics on the wrong channel) | ✅ | Login check reports Secret Smart Stuff |
| Final self-review (max 3 rounds) + can-we-draw-it probe | 🟡 | Live: first 2 topics correctly rejected; fixes added 28 Oct; next video is the proof |
| Hold-for-check before sending (`hold` + `send_review`) | 🟡 | Added 28 Oct for test videos |
| Auto-publish until 25 Nov (passes review → private + scheduled, Telegram note with ⏸ Stop it) | 🟡 | Tested with a fake upload (tests pass); first real one is the next daily video |
| Per-video post-mortems (48 h, 7 d) + living `data/LEARNINGS.md` | 🟡 | Tested offline; first real one when the bus-shelter video is 48 h old (30–31 Oct) |
| Old show data | ✅ | Exported to `archive/bhaukaali-toons`, removed from the live database (28 Oct) |
| Daily schedule | ✅ on | 05:47 IST; skips while a video waits for review |
| Real-motion AI clips | off | Tested 25 Oct (+$3.18 BFL on one video); experiment only |
| Pronunciation check via speech-to-text | 🔜 | Needs speech-to-text permission on the ElevenLabs key; explainers use the voice service's word timings instead |
| Weekly long-form compilation | 🔜 | Not built |
| Repo renamed back to `secret-smart-stuff` | ✅ | 28 Oct; Worker redeployed |

## Budget
- **Limits:** $2 per video, $6 per day, $45 per month (`config/pipeline.yaml`). Owner overrides (28 Oct): October $56, November $60
  (one video a day in auto mode). The ElevenLabs plan is billed separately.
- **October:** $49.0 of $50 used by 28 Oct (the sketch show, then the Secret Smart Stuff tests). Resets on 1 Nov.
- **BFL image credits:** topped up by the owner on 28 Oct.
