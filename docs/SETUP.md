# Setup Guide (one time, about 60–90 minutes)

You do these steps once. After that the system runs by itself, and you only approve videos.
Steps are in order. Each step says **why** it is needed.

> Keep every key secret. Never paste a key into a chat, an issue or a file in the repo.
> Keys go only into **GitHub → Settings → Secrets**.

---

## Step 1 — GitHub (where the system lives and runs)

1. Create a free account at **github.com** (skip if you have one).
2. Create a **private** repository named `hidden-by-design`.
   - Private matters: it keeps your files hidden and gives 2,000 free automation minutes a month.
3. Let Claude put the code there. Choose one:
   - **Easiest:** in Claude, open *Settings → Connectors* and connect **GitHub**. Then tell me "push the code". I'll do the rest.
   - **Or manually:** download the project zip I send you, then upload it on the repo page (*Add file → Upload files*).

## Step 2 — YouTube channel

1. Sign in to YouTube with the Google account you want to own the channel.
2. Profile picture → **Create a channel** → name: **Hidden by Design**.
   - Handle: try `@hiddenbydesign`. If it's taken, try `@hiddenbydesignshorts` or `@hidden.by.design`.
3. In **YouTube Studio → Settings → Channel → Advanced**, set **"No, set this channel as not made for kids"**.
4. Verify your phone number at **youtube.com/verify**. This unlocks longer uploads and custom thumbnails.

## Step 3 — Google Cloud (permission for the system to upload)

1. Open **console.cloud.google.com** and sign in with the **same** Google account.
2. Create a project named `hidden-by-design`.
3. Go to **APIs & Services → Library** and enable:
   - **YouTube Data API v3**
   - **YouTube Analytics API**
4. Go to **APIs & Services → OAuth consent screen** (may be called "Google Auth Platform"):
   - User type: **External**. App name: `Hidden by Design uploader`. Use your email for support and developer contact.
   - Add these scopes: `youtube.upload`, `youtube.readonly`, `yt-analytics.readonly`.
   - **Publishing status: click "Publish app" so it says "In production".**
     - ⚠️ This matters. In "Testing", Google cancels the login every 7 days and the automation stops.
     - Google may show "unverified app" warnings. That's normal for an app only you use.
5. Go to **APIs & Services → Credentials → Create credentials → OAuth client ID**:
   - Application type: **Desktop app**. Name: `uploader`.
   - Copy the **Client ID** and **Client secret**. You'll need them in Steps 4 and 6.

## Step 4 — Log in once to get the "refresh token"

This lets the system upload without your password. Do it on your Mac.

1. Open **Terminal** and run:
   ```bash
   pip3 install requests
   python3 scripts/youtube_auth.py --client-id "PASTE_CLIENT_ID" --client-secret "PASTE_CLIENT_SECRET"
   ```
   Run it from the downloaded project folder.
2. A browser opens. Sign in with the **channel's** Google account and allow access.
   - If you see "Google hasn't verified this app", click **Advanced → Go to … (unsafe)**. It's your own app.
3. The Terminal prints a long **refresh token**. Copy it for Step 6.

## Step 5 — API keys for the AI services

| Service | Where | What to set | Starting credit |
|---|---|---|---|
| **Anthropic (Claude API)** — writing and fact checks | console.anthropic.com → API keys | Create a key named `shorts` | Add **$10** prepaid; set a monthly limit of **$15** |
| **ElevenLabs** — Alice's voice | elevenlabs.io → Developers → API keys | Create a key with **Text to Speech** permission only | Uses your Creator plan credits |
| **Black Forest Labs (FLUX)** — images | dashboard.bfl.ai → API keys | Create a key | Add **$10** |

## Step 6 — Put the keys into GitHub

In your repo: **Settings → Secrets and variables → Actions**.

**Secrets** (New repository secret, one each):

| Name | Value |
|---|---|
| `ANTHROPIC_API_KEY` | from Step 5 |
| `ELEVENLABS_API_KEY` | from Step 5 |
| `BFL_API_KEY` | from Step 5 |
| `YT_CLIENT_ID` | from Step 3 |
| `YT_CLIENT_SECRET` | from Step 3 |
| `YT_REFRESH_TOKEN` | from Step 4 |

**Variables** tab → New variable: `SHORTS_MODE` = `dry_run`. Switch it to `live` in Step 8.

## Step 7 — First test run (free, nothing uploaded)

1. Repo → **Actions** → enable workflows if asked.
2. Choose **produce** → **Run workflow**.
3. After about 5 minutes, a new **Issue** appears called "Review: [DRY RUN] …" with a test video.
   This proves GitHub, ffmpeg, the review flow and state saving all work.
4. Comment `approve` on it. You should get a reply saying "dry-run mode, nothing uploaded".

## Step 8 — First real Short

1. Change the variable `SHORTS_MODE` to `live`.
2. Run **produce** again. This costs about $0.40–$0.70.
3. Watch the video in the issue. If it's good, comment `approve`.
4. The system uploads it as **private** and schedules it for the next slot (19:00 IST).
5. Open YouTube Studio and check:
   - The video is there, scheduled, with the description and sources.
   - **If it says the video is locked as private** (Google's rule for unverified API projects), see "Audit" below.

From then on, **produce** runs every morning automatically.

---

## Audit (only if uploads get locked to private)

Google's documentation disagrees with itself on whether new API projects can make videos public. If your scheduled video stays locked as private:

1. Fill in the **YouTube API Services – Audit and Quota Extension Form** (search that exact name).
   - Use case: "Uploading my own channel's videos from my own automation. Single user."
2. While waiting (Google gives no timeline), use the fallback:
   - The system still uploads as private.
   - You change it to **Public** or **Scheduled** in YouTube Studio. That takes 10 seconds per video.

## Affiliates and Shopping (later)

When the channel reaches **500 subscribers** and the expanded Partner Program tier, apply in **YouTube Studio → Earn**. Then link products. The system already notes the generic product type in each video's metadata (`affiliate_product`).
