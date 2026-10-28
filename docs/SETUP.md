# Setup — Secret Smart Stuff (restored 28 Oct 2026)

Everything below is set up. Use this page if something has to be redone.

## Accounts

| What | Value |
|---|---|
| YouTube channel | **Secret Smart Stuff** · @secretsmartstuff · English · Education · not made for kids |
| Channel's Google account | secretsmartstuff@gmail.com |
| GitHub repo | `shalabhdesigns/secret-smart-stuff` (private) |
| Studio bot (Telegram) | display name "Secret Smart Stuff Studio" (username @bhaukaalitoonsstudiobot; only BotFather can change the username) |
| Studio Worker (Cloudflare) | `secretsmartstuff-studio` → https://secretsmartstuff-studio.secretsmartstuff.workers.dev (home page, `/privacy`, `/dash`, Telegram webhook, YouTube login) |
| Cloudflare account | login secretsmartstuff@gmail.com (free plan; email changed from the old address on 28 Oct; the account's display name still shows the old address until the owner renames it) |
| Google OAuth app | "Secret Smart Stuff uploader", Google Cloud project `bhaukaali-toons` (Owners: secretsmartstuff@gmail.com and bhaukaalitoons@gmail.com) |

secretsmartstuff@gmail.com became an Owner of the Google Cloud project on 28 Oct (YouTube login re-checked: OK).

## Google Cloud (project `bhaukaali-toons`, sign in as secretsmartstuff@gmail.com)
- **APIs:** YouTube Data API v3, YouTube Analytics API.
- **Google Auth Platform:**
  - **Branding:**
    - App name "Secret Smart Stuff uploader".
    - Home page: https://secretsmartstuff-studio.secretsmartstuff.workers.dev/
    - Privacy policy: https://secretsmartstuff-studio.secretsmartstuff.workers.dev/privacy
    - User support email and developer contact: secretsmartstuff@gmail.com. Authorized domain: secretsmartstuff.workers.dev only.
    - Project display name "Secret Smart Stuff" (the project ID `bhaukaali-toons` can never be renamed).
  - **Audience:** External, **In production**. In "Testing" the login would expire every 7 days.
  - **Data access:** youtube.upload, youtube.readonly, yt-analytics.readonly.
  - **Client "uploader" (Web application).** Redirect URIs:
    - `https://secretsmartstuff-studio.secretsmartstuff.workers.dev/oauth/callback` (the live one);
    - the OAuth Playground;
    - `http://127.0.0.1:8765`.

## GitHub Actions secrets
- `ANTHROPIC_API_KEY`, `ELEVENLABS_API_KEY`, `BFL_API_KEY`
- `YT_CLIENT_ID`, `YT_CLIENT_SECRET`
- `TELEGRAM_BOT_TOKEN`, `CLOUDFLARE_API_TOKEN`, `GH_DISPATCH_TOKEN`
- Variable `SHORTS_MODE=live`.
- `YT_REFRESH_TOKEN` is only a fallback. It still holds the old Bhaukaali login, which the channel guard refuses.
  The real login is the encrypted one in the Worker (below).

## YouTube login (one tap; redo whenever uploads say "send /ytlogin")
1. Send **/ytlogin** to the studio bot. It replies with a one-time link (valid 30 minutes).
2. Tap it, sign in as **secretsmartstuff@gmail.com**, and pick **Secret Smart Stuff**.
3. If Google warns that it "hasn't verified this app", tap **Advanced → Go to … (unsafe)**. Then tick
   everything and tap **Allow**.
4. The bot replies "✅ YouTube connected: Secret Smart Stuff".
   - A login for any other channel is refused and not saved.

How it works:
- The Worker swaps Google's code for a refresh token.
- It encrypts the token with AES-GCM, using a key derived from `YT_CLIENT_SECRET`, and saves it in its KV store.
- The runner reads and decrypts it (`shorts/publish/youtube.py`).
- Before uploading or reading analytics, every run checks that the login's channel is the one in
  `config/channel.yaml`.

## Studio Worker
- Deploy or redeploy: push `{"action":"setup_studio"}` to `commands/request.json`. `scripts/deploy_worker.py`:
  - uploads `worker/index.js`;
  - sets its bindings (including the YouTube client id and secret);
  - re-points the Telegram webhook;
  - renames the bot.
- The dashboard is at `/dash`. The login code is sent to the owner's Telegram.

## Old Bhaukaali accounts (dormant, nothing runs on them)
- YouTube "Bhaukaali Toons" still has Ep 1 public, plus one private test upload.
- Instagram @bhaukaalitoons.
- Vercel project `bhaukaali-toons`: its `site/` pages now point to Secret Smart Stuff. It can be deleted; the
  Google app no longer uses it.
- ElevenLabs voices Dev, Rocky, Meera: unused, cost nothing.
