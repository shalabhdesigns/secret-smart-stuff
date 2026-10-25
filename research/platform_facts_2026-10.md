# Platform facts checked 25 Oct 2026

Checked with official documentation where possible. Re-check anything older than 3 months before
relying on it. Confidence: H = high, M = medium, L = low.

## YouTube Data API

**Custom thumbnails (`thumbnails.set`)**
- Works with the `youtube.upload` scope and costs 50 units. Since Sep 2026 the file limit is 50 MB. (H)
  https://developers.google.com/youtube/v3/docs/thumbnails/set
- YouTube Help: "Custom thumbnails for Shorts are currently only available to add in YouTube Studio on a
  computer." This needs a verified account (an Intermediate feature, unlocked by phone verification). (H)
  - https://support.google.com/youtube/answer/72431
  - https://support.google.com/youtube/answer/9890437
- Shorts thumbnails appear on the homepage and channel pages, not in the Shorts feed. They started rolling
  out on 25 Jul 2026. (M, secondary source)

**Captions, playlists, video status**
- `captions.insert`: needs the `youtube.force-ssl` scope, 400 units. (H)
- `playlistItems.insert`: needs the `youtube` or `youtube.force-ssl` scope, 50 units. (H)
- `videos.list` status fields: (H) https://developers.google.com/youtube/v3/docs/videos
  - uploadStatus: deleted, failed, processed, rejected, uploaded;
  - failureReason;
  - rejectionReason;
  - publishAt;
  - containsSyntheticMedia.

**Unverified Google projects (conflicting sources)**
- The current docs (updated 2026-10-15) say videos from unverified projects are **not** restricted to
  private.
- The revision history still holds the 2020 rule that restricted them, with no entry reversing it.
- No API field shows the lock. So our own upload is the test. (L–M)
  https://developers.google.com/youtube/v3/docs/videos/insert

**Quota**
- Since 1 Jun 2026, `videos.insert` has its own bucket: 100 calls a day at 1 unit each.
- Other methods share 10,000 units a day. Quota resets at midnight Pacific. (H)
  https://developers.google.com/youtube/v3/determine_quota_cost

## YouTube Analytics API (v2)

- **Available metrics:** views, engagedViews, estimatedMinutesWatched, averageViewDuration,
  averageViewPercentage, likes, comments, shares, subscribersGained/Lost, audienceWatchRatio. (H)
  https://developers.google.com/youtube/analytics/metrics
- **No impressions or click-through rate.** These exist only in Reporting API bulk "reach" reports
  (since Jan 2026). (H)
- **Revenue metrics** need the `yt-analytics-monetary.readonly` scope and a channel in the Partner Program;
  otherwise the API returns 403. (H)
- **How views are counted:**
  - Shorts views count every start or replay (Mar 2025).
  - engagedViews keeps the old counting method.
  - Revenue uses engaged views. (H)
- **Data latency:** 48–72 hours. (H)
- **Useful dimensions:** creatorContentType=SHORTS; insightTrafficSourceType (includes SHORTS, HASHTAGS);
  elapsedVideoTimeRatio (100 points); ageGroup; gender. (H)

## Best time to post (evidence)

- **Buffer** (about 1.8M videos, Jul 2026): Shorts do best in the local evening, 6–11 pm. Monday and
  Tuesday are weakest. Shorts keep being resurfaced for days, so timing matters less. (M)
  https://buffer.com/resources/best-time-to-post-on-youtube/
- **Adobe** (24k Shorts, 280 creators, 2025): 8–10 am underperformed. (M, secondary source)
- **YouTube** only advises posting consistently. The "when your viewers are on YouTube" report is meant
  for Premieres and live streams. https://support.google.com/youtube/answer/9314416

## Titles, hashtags, tags

- Up to 3 hashtags show by the title. More than 60 are all ignored.
  https://support.google.com/youtube/answer/6390658
- There is no official requirement for a #Shorts hashtag. A Short is classified by its shape and length
  (up to 3 min).
- Tags play a "minimal role". Titles max 100 characters, descriptions max 5,000.

## Telegram Bot API

- Bots can upload videos up to 50 MB (multipart), or send files up to 20 MB by URL. (H)
- The webhook `secret_token` arrives in the `X-Telegram-Bot-Api-Secret-Token` header. (H)
- Rate limit: about 1 message per second per chat. (H)
  https://core.telegram.org/bots/api, https://core.telegram.org/bots/faq

## Cloudflare (free plan)

- **Workers:** 100k requests a day, 10 ms CPU per request. (H)
- **KV:** 100k reads and 1k writes a day, 1 GB. (H)
- **Zero Trust:** free up to 50 users. (H)

## GitHub Actions (private repo, Free plan)

- **Included:** 2,000 minutes a month. Each job is rounded up to the next minute. (H)
- **Schedules:** shortest interval is 5 minutes, and runs can be delayed at busy times, especially on the
  hour. (M–H)
- **Auto-disable after 60 days of inactivity:** documented for public repos only. (H)
- **`workflow_dispatch` with a fine-grained token:** needs the "Actions: write" permission. (H)

## YouTube policies

- **AI disclosure** (`containsSyntheticMedia`): required for realistic altered or synthetic content.
  Disclosing does not limit reach or monetisation. (H) https://support.google.com/youtube/answer/14328491
- **Inauthentic content** (renamed Jul 2025, clarified Jul 2026): not monetised:
  - "AI-generated content made with generic or unoriginal templates";
  - "image slideshows… with minimal narrative". (H)

  https://support.google.com/youtube/answer/1311392
- **Partner Program from 1 Feb 2027:**
  - New applicants need 8,000 watch hours in 365 days **or 20M Shorts views in 90 days**.
  - Shorts ad revenue sharing needs **10M Shorts views in 90 days**. (H)

  https://blog.youtube/news-and-events/youtube-partner-program-updates-2027-new-opportunities-earn/
