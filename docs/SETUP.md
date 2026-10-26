# Setup — Bhaukaali Toons (done 26 Oct 2026)

Everything below is set up and tested. Use this page if something has to be redone.

## Accounts
| What | Value |
|---|---|
| Google account (owns the channel) | bhaukaalitoons@gmail.com (2-step verification on) |
| YouTube channel | Bhaukaali Toons · @bhaukaalitoons · not made for kids · Comedy · Hindi |
| Instagram | @bhaukaalitoons (Creator account) — Reels posted manually for now |
| GitHub repo | shalabhdesigns/bhaukaali-toons (private) |
| Public site | https://bhaukaali-toons.vercel.app (Vercel project `bhaukaali-toons`, root `site/`) — home page + privacy policy |

## Google Cloud (project `bhaukaali-toons`, signed in as bhaukaalitoons@gmail.com)
- APIs enabled: YouTube Data API v3, YouTube Analytics API.
- Google Auth Platform:
  - Branding: app name "Bhaukaali Toons uploader", support + developer email bhaukaalitoons@gmail.com,
    home page and privacy policy on bhaukaali-toons.vercel.app, authorized domain `bhaukaali-toons.vercel.app`, **no logo**.
  - Audience: External, **In production** (in "Testing" the login would expire every 7 days).
  - Data access: youtube.upload, youtube.readonly, yt-analytics.readonly.
  - Client "uploader" (Web application), redirect URIs: `https://developers.google.com/oauthplayground`, `http://127.0.0.1:8765`.

## GitHub Actions secrets
`YT_CLIENT_ID`, `YT_CLIENT_SECRET`, `YT_REFRESH_TOKEN` (Bhaukaali Toons), `ELEVENLABS_API_KEY`, `BFL_API_KEY`,
`ANTHROPIC_API_KEY`. Variable `SHORTS_MODE=live`.

## Redo the YouTube login (only if it breaks)
1. Open https://developers.google.com/oauthplayground → gear → tick "Use your own OAuth credentials" →
   paste the Client ID and Client secret (Access type: Offline, Force prompt: Consent Screen).
2. Paste the three scopes into "Input your own scopes" → Authorize APIs → sign in with
   bhaukaalitoons@gmail.com → choose Bhaukaali Toons → Advanced → Go to (unsafe) → tick all → Continue.
3. Exchange authorization code for tokens → copy the Refresh token into the `YT_REFRESH_TOKEN` secret.
4. Ask Claude to run `whoami` — it must report "Bhaukaali Toons".

If the client secret is lost: Google Auth Platform → Clients → uploader → Add secret (shown once), then update
`YT_CLIENT_SECRET` and redo the login.
