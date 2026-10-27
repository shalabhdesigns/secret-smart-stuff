# Publishing time and metadata (research, 26 Oct 2026)

The automatic pipeline follows this page (`shorts/sketch/writer.py` META_RULES, `shorts/sketch/episodes.py` slot).

## When we publish
- **Default: 7:30 PM IST every day.**
  - This is just after work and college, about 1.5–2 hours before the 9–11 PM mobile peak.
  - That leaves time for the Shorts feed's first "seed" test audience.
- **Posting time matters little for Shorts.**
  - In May 2025, YouTube said posting time is not a ranking signal.
  - The time only changes how fast the first viewers arrive.
- **The IST time data is weak:** it comes from vendor blogs (SocialPilot, WsCube), with no public study of Hindi Shorts.
- **Later A/B test:** rotate 1:00 PM and 9:30 PM IST weekly for 4–6 weeks. Compare engaged views at 48 h and "stayed to watch".
- **After a few thousand views:** read Studio → Audience → "When your viewers are on YouTube" and publish 1–2 hours before the peak.

## Metadata
- **Title:**
  - 40–60 characters, Roman Hinglish.
  - A relatable situation ("Jab…", "POV:", "Har … ka ek dost"), plus ` | Sab Theek Hai`.
  - Titles show in the Shorts feed.
- **Description:**
  - Line 1: the hook.
  - Line 2: the series line.
  - Line 3: a comment prompt.
  - Then the hashtags.
- **Hashtags:** 3–5 in total, always `#SabTheekHai`. More than 60 means YouTube ignores all of them. `#shorts` is optional.
- **Tags:** 6–10. They play only a "minimal role" (YouTube).
- **API fields:**
  - category 23 (Comedy);
  - `defaultLanguage` and `defaultAudioLanguage` = `hi`;
  - private + `publishAt`;
  - `selfDeclaredMadeForKids` = false. Animation alone is not "made for kids", and kids mode would turn off comments.
  - `containsSyntheticMedia` = false. Fully animated, non-realistic content does not need the AI label. Never imitate a real person's voice.
- **Not automated, and why:**
  - **Caption tracks and pinned comments** need the extra `youtube.force-ssl` permission. Captions are already burned into the video. The pinned-comment text is sent to the owner on Telegram.
  - **The "related video" link** can only be set in Studio.

## Policy safety (inauthentic / repetitious content, July 2025)
- One unique script and situation every day, with varied sets and shots. Never the same episode twice.
- Never delete and re-upload a weak Short. YouTube can treat that as spam.
- At most one upload a day.

## Sources
- https://support.google.com/youtube/answer/1311392 (YPP policies)
- https://support.google.com/youtube/answer/14328491 (AI disclosure)
- https://support.google.com/youtube/answer/9528076 (made for kids)
- https://developers.google.com/youtube/v3/docs/videos
- https://support.google.com/youtube/answer/6390658 (hashtags)
- https://support.google.com/youtube/answer/146402 (tags)
- https://www.netinfluencer.com/youtube-debunks-common-myths-about-shorts-as-format-gains-traction/
- https://www.socialpilot.co/blog/best-time-to-post-on-youtube (weak)
- https://www.wscubetech.com/blog/best-time-to-post-on-youtube/ (weak)
