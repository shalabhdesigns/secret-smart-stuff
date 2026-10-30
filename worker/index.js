// Secret Smart Stuff studio Worker (Cloudflare, free plan).
//
// 1. /tg      Telegram webhook: the owner's button taps and replies become GitHub runs
//             (workflow_dispatch on command.yml). Nobody else is obeyed.
// 2. /dash    Private dashboard. Login = a 6-digit code sent to the owner's Telegram.
// 3. /oauth/* One-tap YouTube login. The owner gets a one-time link in Telegram; Google sends the
//             code back here; the refresh token is stored ENCRYPTED in KV (key derived from the
//             client secret, which only this Worker and the GitHub runner hold). Only a login for the
//             expected channel (EXPECT_CHANNEL) is kept.
// 4. / and /privacy  Public home page and privacy policy for the Google OAuth app.
// 5. /ig/*    One-tap Instagram login (Business Login for Instagram). Long-lived token stored ENCRYPTED in KV
//             (key from YT_CLIENT_SECRET, label "ig-token-v1:"); only the expected account (EXPECT_IG) is kept.
// 6. /m/<key>.mp4  Serves a video the runner put in KV for a few hours, so Instagram can fetch it.
// 7. scheduled()   Timers that start the daily video and the Instagram posts on time (SCHEDULE binding).
//
// Bindings (set by scripts/deploy_worker.py): KV (namespace), TG_TOKEN, TG_SECRET, OWNER_ID,
// GH_TOKEN, GH_REPO, COOKIE_KEY, SELF_URL, YT_CLIENT_ID, YT_CLIENT_SECRET, EXPECT_CHANNEL,
// IG_APP_ID, IG_APP_SECRET, EXPECT_IG.

const enc = new TextEncoder();

export default {
  async fetch(req, env) {
    const url = new URL(req.url);
    try {
      if (url.pathname === "/tg" && req.method === "POST") return await telegram(req, env);
      if (url.pathname === "/dash/code" && req.method === "POST") return await sendCode(env, url);
      if (url.pathname === "/dash/login" && req.method === "POST") return await login(req, env, url);
      if (url.pathname === "/dash/logout") return logout(url);
      if (url.pathname === "/dash") return await dash(req, env, url);
      if (url.pathname === "/oauth/start") return await oauthStart(env, url);
      if (url.pathname === "/oauth/callback") return await oauthCallback(env, url);
      if (url.pathname === "/ig/start") return await igStart(env, url);
      if (url.pathname === "/ig/callback") return await igCallback(env, url);
      if (url.pathname.startsWith("/m/")) return await media(req, env, url);
      if (url.pathname === "/privacy") return publicPage(PRIVACY);
      if (url.pathname === "/") return publicPage(HOME);
      if (url.pathname === "/health") return new Response("ok");
      return new Response("not found", { status: 404 });
    } catch (e) {
      return new Response("error", { status: 500 });
    }
  },
  // 7. Timers (Cloudflare Cron Triggers): start the daily video and the Instagram posts on time. GitHub's own
  //    schedule can run hours late; it stays as a backup (the runner skips a second daily run the same day).
  async scheduled(event, env, ctx) {
    let plan = {};
    try { plan = JSON.parse(env.SCHEDULE || "{}"); } catch { plan = {}; }
    const request = plan[event.cron];
    if (request) ctx.waitUntil(dispatch(env, { ...request }));
  },
};

// ---------------- Telegram ----------------

async function tg(env, method, body) {
  const r = await fetch(`https://api.telegram.org/bot${env.TG_TOKEN}/${method}`, {
    method: "POST",
    headers: { "content-type": "application/json" },
    body: JSON.stringify(body),
  });
  return r.json();
}

async function dispatch(env, request) {
  request.nonce = `tg-${Date.now()}`;
  const r = await fetch(
    `https://api.github.com/repos/${env.GH_REPO}/actions/workflows/command.yml/dispatches`,
    {
      method: "POST",
      headers: {
        authorization: `Bearer ${env.GH_TOKEN}`,
        accept: "application/vnd.github+json",
        "user-agent": "secretsmartstuff-worker",
        "x-github-api-version": "2022-11-28",
      },
      body: JSON.stringify({ ref: "main", inputs: { request: JSON.stringify(request) } }),
    },
  );
  return r.status === 204 ? null : `GitHub said ${r.status}: ${(await r.text()).slice(0, 150)}`;
}

const JOB = /^[a-z0-9-]{3,60}$/;

async function telegram(req, env) {
  if (req.headers.get("x-telegram-bot-api-secret-token") !== env.TG_SECRET) {
    return new Response("forbidden", { status: 403 });
  }
  const u = await req.json();
  const from = (u.callback_query || u.message || {}).from || {};
  if (String(from.id) !== String(env.OWNER_ID)) return new Response("ok"); // ignore everyone else
  const chat = env.OWNER_ID;

  if (u.callback_query) {
    const cq = u.callback_query;
    const [kind, job] = (cq.data || "").split(":");
    if (!JOB.test(job || "")) return ack(env, cq, "Unknown video");
    const msg = cq.message || {};
    if (kind === "a") {
      // confirm first: publishing is not reversible
      await tg(env, "editMessageReplyMarkup", {
        chat_id: chat, message_id: msg.message_id,
        reply_markup: { inline_keyboard: [[
          { text: "✅ Yes, publish", callback_data: `A:${job}` },
          { text: "↩️ Back", callback_data: `b:${job}` },
        ]] },
      });
      return ack(env, cq, "Tap 'Yes, publish' to confirm");
    }
    if (kind === "b") {
      await tg(env, "editMessageReplyMarkup", { chat_id: chat, message_id: msg.message_id, reply_markup: reviewButtons(job) });
      return ack(env, cq, "OK");
    }
    if (kind === "A") {
      const err = await dispatch(env, { action: "approve", job });
      if (err) return ack(env, cq, "Could not start: " + err, true);
      await tg(env, "editMessageReplyMarkup", {
        chat_id: chat, message_id: msg.message_id,
        reply_markup: { inline_keyboard: [[{ text: "⏳ Approved, uploading…", callback_data: "noop:x" }]] },
      });
      return ack(env, cq, "Approved. I'll message you when it's uploaded.");
    }
    if (kind === "s") {
      // stop an auto-published video: ask once, publishing is the default
      await tg(env, "editMessageReplyMarkup", {
        chat_id: chat, message_id: msg.message_id,
        reply_markup: { inline_keyboard: [[
          { text: "⏸ Yes, keep it private", callback_data: `S:${job}` },
          { text: "↩️ No, publish", callback_data: `k:${job}` },
        ]] },
      });
      return ack(env, cq, "Tap 'Yes' to keep it private");
    }
    if (kind === "k") {
      await tg(env, "editMessageReplyMarkup", { chat_id: chat, message_id: msg.message_id,
        reply_markup: { inline_keyboard: [[{ text: "⏸ Stop it", callback_data: `s:${job}` }]] } });
      return ack(env, cq, "OK, it will publish as planned");
    }
    if (kind === "S") {
      await env.KV.put(`stop:${job}`, "1", { expirationTtl: 7 * 86400 });   // Instagram checks this right before posting
      const err = await dispatch(env, { action: "unpublish", job });
      if (err) return ack(env, cq, "Could not start: " + err, true);
      await tg(env, "editMessageReplyMarkup", { chat_id: chat, message_id: msg.message_id,
        reply_markup: { inline_keyboard: [[{ text: "⏳ Stopping…", callback_data: "noop:x" }]] } });
      return ack(env, cq, "Stopping. I'll confirm in a minute.");
    }
    if (kind === "P") {
      // the owner posted the Reel by hand (Instagram API down): never auto-post this video later
      await env.KV.put(`stop:${job}`, "1", { expirationTtl: 30 * 86400 });
      const err = await dispatch(env, { action: "ig_manual", job });
      if (err) return ack(env, cq, "Could not save: " + err, true);
      await tg(env, "editMessageReplyMarkup", { chat_id: chat, message_id: msg.message_id,
        reply_markup: { inline_keyboard: [[{ text: "✅ Marked as posted by hand", callback_data: "noop:x" }]] } });
      return ack(env, cq, "OK. It won't be posted again.");
    }
    if (kind === "f") {
      await tg(env, "sendMessage", {
        chat_id: chat, parse_mode: "HTML",
        text: `✏️ What should change? Reply to this message in your own words.\n<code>fix job:${job}</code>`,
        reply_markup: { force_reply: true, input_field_placeholder: "e.g. the 3rd picture should show the tabs" },
      });
      return ack(env, cq, "Reply with what to change");
    }
    if (kind === "d") {
      await tg(env, "sendMessage", {
        chat_id: chat, parse_mode: "HTML",
        text: `🗑 Why drop this video? Reply to this message (or reply "skip"). The reason helps me pick better topics.\n<code>drop job:${job}</code>`,
        reply_markup: { force_reply: true },
      });
      return ack(env, cq, "Reply with the reason");
    }
    return ack(env, cq, "");
  }

  const m = u.message;
  if (!m || !m.text) return new Response("ok");
  const text = m.text.trim();
  const replied = (m.reply_to_message && (m.reply_to_message.text || m.reply_to_message.caption)) || "";
  const marker = replied.match(/\b(fix|drop) job:([a-z0-9-]+)/);
  const reviewJob = (replied.match(/job:([a-z0-9-]+)/) || [])[1];

  let request = null, reply = "";
  const isCommand = /^\/[a-z]+\b/i.test(text);   // a /command always wins, even when sent as a reply
  if (!isCommand && marker && JOB.test(marker[2])) {
    const note = /^skip$/i.test(text) ? "" : text.slice(0, 1500);
    if (marker[1] === "fix" && !note) return say(env, chat, "Please say what to change.");
    request = { action: marker[1] === "fix" ? "fix" : "reject", job: marker[2], note };
    reply = marker[1] === "fix"
      ? "👍 Got it. Making the changes; the new version arrives here in about 15 minutes."
      : "👍 Dropped. Your reason is saved; the next video comes with the next daily run (or send /produce).";
  } else if (!isCommand && reviewJob && JOB.test(reviewJob)) {   // any reply to a video = what to change
    request = { action: "fix", job: reviewJob, note: text.replace(/^(fix|change)\s*:?\s*/i, "").slice(0, 1500) };
    reply = "👍 Got it. Making the changes; the new version arrives here in about 15 minutes.";
  } else if (/^\/start\b/.test(text) || /^\/help\b/.test(text)) {
    return say(env, chat,
      "Every new Secret Smart Stuff video is checked by my final review and, if it passes, uploaded and scheduled automatically (until 25 Nov 2026). You get a message for each one.\n\n" +
      "Buttons: ⏸ Stop it (keeps that video private) · ✅ Approve / ✏️ Fix / 🗑 Drop (for videos that need your review)\n\n" +
      "Commands:\n/status – the queue\n/produce – make an extra video now\n" +
      "/dash – dashboard link\n/ytlogin – connect the YouTube channel (one tap)\n/iglogin – connect Instagram (one tap)\n/revenue 2026-11 12.50 – record revenue for a month (USD)");
  } else if (/^\/ytlogin\b/.test(text)) {
    return say(env, chat, "🔑 Tap to connect the Secret Smart Stuff channel (link works once, for 30 minutes):\n" + await loginLink(env) +
      "\n\nSign in as secretsmartstuff@gmail.com, choose the Secret Smart Stuff channel, then Allow.");
  } else if (/^\/iglogin\b/.test(text)) {
    if (!env.IG_APP_ID) return say(env, chat, "Instagram is not set up yet (the app ID is missing).");
    return say(env, chat, "📸 Tap to connect Instagram (link works for 30 minutes):\n" + await loginLink(env, "/ig/start") +
      `\n\nLog in as @${env.EXPECT_IG || "secretsmartstuff"} and tap Allow.`);
  } else if (/^\/status\b/.test(text)) {
    request = { action: "status" }; reply = "⏳ Checking…";
  } else if (/^\/produce\b/.test(text)) {
    request = { action: "produce" }; reply = "🎬 Researching and making a new video. It takes about 15 minutes.";
  } else if (/^\/dash\b/.test(text)) {
    return say(env, chat, `📊 Dashboard: https://${new URL(env.SELF_URL).host}/dash`);
  } else if (/^\/revenue\b/.test(text)) {
    const p = text.split(/\s+/);
    const period = p[1] || "", usd = parseFloat(p[2]);
    if (!/^\d{4}-\d{2}(-\d{2})?$/.test(period) || !isFinite(usd)) {
      return say(env, chat, "Use: /revenue YYYY-MM amount [video_id]\ne.g. /revenue 2026-11 12.50");
    }
    request = { action: "revenue", period, usd, video_id: p[3] || "" };
    reply = `💰 Recording $${usd.toFixed(2)} for ${period}.`;
  } else {
    return say(env, chat, "To change a video, tap ✏️ Fix under it. /help lists commands.");
  }
  const err = await dispatch(env, request);
  return say(env, chat, err ? "⚠️ Could not start that: " + err : reply);
}

function reviewButtons(job) {
  return { inline_keyboard: [
    [{ text: "✅ Approve", callback_data: `a:${job}` }, { text: "✏️ Fix", callback_data: `f:${job}` }],
    [{ text: "🗑 Drop", callback_data: `d:${job}` }],
  ] };
}

async function ack(env, cq, text, alert = false) {
  await tg(env, "answerCallbackQuery", { callback_query_id: cq.id, text: text.slice(0, 190), show_alert: alert });
  return new Response("ok");
}

async function say(env, chat, text) {
  await tg(env, "sendMessage", { chat_id: chat, text, link_preview_options: { is_disabled: true } });
  return new Response("ok");
}

// ---------------- Dashboard ----------------

async function hmac(env, msg) {
  const key = await crypto.subtle.importKey("raw", enc.encode(env.COOKIE_KEY), { name: "HMAC", hash: "SHA-256" }, false, ["sign"]);
  const sig = await crypto.subtle.sign("HMAC", key, enc.encode(msg));
  return [...new Uint8Array(sig)].map((b) => b.toString(16).padStart(2, "0")).join("");
}

async function authed(req, env) {
  const c = (req.headers.get("cookie") || "").match(/(?:^|;\s*)sss=([0-9]+)\.([0-9a-f]{64})/);
  if (!c) return false;
  if (Number(c[1]) < Date.now()) return false;
  return (await hmac(env, c[1])) === c[2];
}

function page(body, status = 200, headers = {}) {
  return new Response(
    `<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">` +
    `<title>Studio login</title><style>body{font:16px system-ui,sans-serif;background:#F4EFE6;color:#14213D;display:grid;place-items:center;min-height:100vh;margin:0}` +
    `main{background:#fff;padding:28px;border-radius:14px;max-width:340px;width:calc(100% - 32px);box-shadow:0 2px 12px #0001}` +
    `button,input{font:inherit;width:100%;padding:12px;border-radius:10px;border:1px solid #ccc;margin-top:10px;box-sizing:border-box}` +
    `button{background:#F26B1D;color:#fff;border:0;font-weight:600}</style></head><body><main>${body}</main></body></html>`,
    { status, headers: { "content-type": "text/html; charset=utf-8", "cache-control": "no-store", ...headers } },
  );
}

async function dash(req, env, url) {
  if (!(await authed(req, env))) {
    const sent = url.searchParams.get("sent");
    const bad = url.searchParams.get("bad");
    return page(
      `<h2>Secret Smart Stuff · Studio</h2>` +
      (sent
        ? `<p>A code was sent to your Telegram.</p><form method="post" action="/dash/login"><input name="code" inputmode="numeric" autocomplete="one-time-code" placeholder="6-digit code" required><button>Open dashboard</button></form>`
        : `<p>Private dashboard. A login code will be sent to the owner's Telegram.</p><form method="post" action="/dash/code"><button>Send me a code</button></form>`) +
      (bad ? `<p style="color:#b00">That code didn't work. Send a new one.</p>` : ""),
    );
  }
  const html = await env.KV.get("dashboard.html");
  return new Response(html || "<p>No dashboard data yet.</p>", {
    headers: { "content-type": "text/html; charset=utf-8", "cache-control": "no-store" },
  });
}

async function sendCode(env, url) {
  const n = Number((await env.KV.get("code_count")) || 0);
  if (n >= 5) return page("<p>Too many codes. Try again in an hour.</p>", 429);
  await env.KV.put("code_count", String(n + 1), { expirationTtl: 3600 });
  const code = String(crypto.getRandomValues(new Uint32Array(1))[0] % 1000000).padStart(6, "0");
  await env.KV.put("login_code", code, { expirationTtl: 600 });
  await tg(env, "sendMessage", { chat_id: env.OWNER_ID, text: `🔐 Dashboard login code: ${code}\n(valid 10 minutes, works once)` });
  return Response.redirect(`${url.origin}/dash?sent=1`, 303);
}

async function login(req, env, url) {
  const form = await req.formData();
  const code = String(form.get("code") || "").trim();
  const want = await env.KV.get("login_code");
  if (!want || code !== want) {
    // 5 wrong tries burn the code, so guessing a 6-digit code is not practical
    const bad = Number((await env.KV.get("bad_tries")) || 0) + 1;
    await env.KV.put("bad_tries", String(bad), { expirationTtl: 600 });
    if (bad >= 5) await env.KV.delete("login_code");
    return Response.redirect(`${url.origin}/dash?bad=1`, 303);
  }
  await env.KV.delete("bad_tries");
  await env.KV.delete("login_code");
  const exp = String(Date.now() + 30 * 86400 * 1000);
  const cookie = `sss=${exp}.${await hmac(env, exp)}; Path=/; Max-Age=${30 * 86400}; HttpOnly; Secure; SameSite=Lax`;
  return new Response(null, { status: 303, headers: { location: `${url.origin}/dash`, "set-cookie": cookie } });
}

function logout(url) {
  return new Response(null, { status: 303, headers: { location: `${url.origin}/dash`, "set-cookie": "sss=; Path=/; Max-Age=0" } });
}

// ---------------- YouTube login (one tap) ----------------

const GOOGLE_AUTH = "https://accounts.google.com/o/oauth2/v2/auth";
const GOOGLE_TOKEN = "https://oauth2.googleapis.com/token";
const SCOPES = [
  "https://www.googleapis.com/auth/youtube.upload",
  "https://www.googleapis.com/auth/youtube.readonly",
  "https://www.googleapis.com/auth/yt-analytics.readonly",
].join(" ");

function randomId(n = 24) {
  return [...crypto.getRandomValues(new Uint8Array(n))].map((b) => b.toString(16).padStart(2, "0")).join("");
}

async function loginLink(env, path = "/oauth/start") {
  const n = randomId();
  await env.KV.put(`oauth_link:${n}`, "1", { expirationTtl: 1800 });
  return `${env.SELF_URL}${path}?n=${n}`;
}

async function oauthStart(env, url) {
  const n = url.searchParams.get("n") || "";
  if (!/^[0-9a-f]{48}$/.test(n) || !(await env.KV.get(`oauth_link:${n}`))) {
    return publicPage(`<h1>Link expired</h1><p>Send /ytlogin to the studio bot for a new one.</p>`, 400);
  }
  // Not deleted here: Telegram's link preview opens the link before the owner taps it. The link stays usable
  // for its 30 minutes; the Google round trip is protected by the single-use `state` below.
  const state = randomId();
  await env.KV.put(`oauth_state:${state}`, "1", { expirationTtl: 1800 });
  const q = new URLSearchParams({
    client_id: env.YT_CLIENT_ID, redirect_uri: `${env.SELF_URL}/oauth/callback`, response_type: "code",
    scope: SCOPES, access_type: "offline", prompt: "consent select_account", include_granted_scopes: "true", state,
  });
  return Response.redirect(`${GOOGLE_AUTH}?${q}`, 302);
}

async function aesKey(env, label = "yt-refresh-v1:") {
  const raw = await crypto.subtle.digest("SHA-256", enc.encode(label + env.YT_CLIENT_SECRET));
  return crypto.subtle.importKey("raw", raw, { name: "AES-GCM" }, false, ["encrypt"]);
}

async function seal(env, text, label = "yt-refresh-v1:") {
  const iv = crypto.getRandomValues(new Uint8Array(12));
  const ct = new Uint8Array(await crypto.subtle.encrypt({ name: "AES-GCM", iv }, await aesKey(env, label), enc.encode(text)));
  const all = new Uint8Array(iv.length + ct.length);
  all.set(iv); all.set(ct, iv.length);
  return btoa(String.fromCharCode(...all));
}

async function oauthCallback(env, url) {
  const state = url.searchParams.get("state") || "";
  if (!/^[0-9a-f]{48}$/.test(state) || !(await env.KV.get(`oauth_state:${state}`))) {
    return publicPage(`<h1>Link expired</h1><p>Send /ytlogin to the studio bot for a new one.</p>`, 400);
  }
  await env.KV.delete(`oauth_state:${state}`);
  if (url.searchParams.get("error")) {
    await say(env, env.OWNER_ID, `⚠️ YouTube login was cancelled (${url.searchParams.get("error")}). Send /ytlogin to try again.`);
    return publicPage(`<h1>Cancelled</h1><p>Nothing was changed.</p>`, 400);
  }
  const r = await fetch(GOOGLE_TOKEN, {
    method: "POST",
    headers: { "content-type": "application/x-www-form-urlencoded" },
    body: new URLSearchParams({
      code: url.searchParams.get("code") || "", client_id: env.YT_CLIENT_ID, client_secret: env.YT_CLIENT_SECRET,
      redirect_uri: `${env.SELF_URL}/oauth/callback`, grant_type: "authorization_code",
    }),
  });
  const tok = await r.json();
  if (!tok.refresh_token || !tok.access_token) {
    await say(env, env.OWNER_ID, `⚠️ YouTube login failed (${tok.error || r.status}). Send /ytlogin to try again.`);
    return publicPage(`<h1>Login failed</h1><p>Nothing was changed. Try again from the bot.</p>`, 400);
  }
  const ch = await (await fetch("https://www.googleapis.com/youtube/v3/channels?part=snippet&mine=true", {
    headers: { authorization: `Bearer ${tok.access_token}` },
  })).json();
  const c = (ch.items || [])[0];
  const title = c ? c.snippet.title : "(no channel)";
  if (!c || (env.EXPECT_CHANNEL && title !== env.EXPECT_CHANNEL)) {
    await say(env, env.OWNER_ID, `⚠️ That login was for "${title}", not "${env.EXPECT_CHANNEL}". Nothing was saved. Send /ytlogin and pick ${env.EXPECT_CHANNEL}.`);
    return publicPage(`<h1>Wrong channel</h1><p>You picked "${esc(title)}". Please try again and choose ${esc(env.EXPECT_CHANNEL)}.</p>`, 400);
  }
  await env.KV.put("yt_refresh.enc", await seal(env, tok.refresh_token));
  await env.KV.put("yt_channel", JSON.stringify({ id: c.id, title, at: new Date().toISOString(), scope: tok.scope || "" }));
  await say(env, env.OWNER_ID, `✅ YouTube connected: ${title}. Approved videos will now upload to this channel.`);
  return publicPage(`<h1>Connected ✅</h1><p>${esc(title)} is connected. You can close this page.</p>`);
}

// ---------------- Instagram login (one tap) + video hand-off ----------------

const IG_SCOPES = "instagram_business_basic,instagram_business_content_publish,instagram_business_manage_insights";

async function igStart(env, url) {
  const n = url.searchParams.get("n") || "";
  if (!/^[0-9a-f]{48}$/.test(n) || !(await env.KV.get(`oauth_link:${n}`))) {
    return publicPage(`<h1>Link expired</h1><p>Send /iglogin to the studio bot for a new one.</p>`, 400);
  }
  const state = randomId();
  await env.KV.put(`ig_state:${state}`, "1", { expirationTtl: 1800 });
  const q = new URLSearchParams({
    enable_fb_login: "0", force_authentication: "1", client_id: env.IG_APP_ID,
    redirect_uri: `${env.SELF_URL}/ig/callback`, response_type: "code", scope: IG_SCOPES, state,
  });
  return Response.redirect(`https://www.instagram.com/oauth/authorize?${q}`, 302);
}

async function igCallback(env, url) {
  const state = url.searchParams.get("state") || "";
  if (!/^[0-9a-f]{48}$/.test(state) || !(await env.KV.get(`ig_state:${state}`))) {
    return publicPage(`<h1>Link expired</h1><p>Send /iglogin to the studio bot for a new one.</p>`, 400);
  }
  await env.KV.delete(`ig_state:${state}`);
  if (url.searchParams.get("error")) {
    await say(env, env.OWNER_ID, `⚠️ Instagram login was cancelled (${url.searchParams.get("error_reason") || url.searchParams.get("error")}). Send /iglogin to try again.`);
    return publicPage(`<h1>Cancelled</h1><p>Nothing was changed.</p>`, 400);
  }
  const code = (url.searchParams.get("code") || "").replace(/#_$/, "");
  const r = await fetch("https://api.instagram.com/oauth/access_token", {
    method: "POST",
    headers: { "content-type": "application/x-www-form-urlencoded" },
    body: new URLSearchParams({
      client_id: env.IG_APP_ID, client_secret: env.IG_APP_SECRET, grant_type: "authorization_code",
      redirect_uri: `${env.SELF_URL}/ig/callback`, code,
    }),
  });
  const j = await r.json();
  const short = (j.data && j.data[0]) || j;
  if (!short.access_token) {
    await say(env, env.OWNER_ID, `⚠️ Instagram login failed (${(j.error && (j.error.message || j.error)) || j.error_message || r.status}). Send /iglogin to try again.`);
    return publicPage(`<h1>Login failed</h1><p>Nothing was changed. Try again from the bot.</p>`, 400);
  }
  const ll = await (await fetch(`https://graph.instagram.com/access_token?${new URLSearchParams({
    grant_type: "ig_exchange_token", client_secret: env.IG_APP_SECRET, access_token: short.access_token })}`)).json();
  if (!ll.access_token) {
    await say(env, env.OWNER_ID, `⚠️ Instagram login step 2 failed (${(ll.error && ll.error.message) || "no token"}). Send /iglogin to try again.`);
    return publicPage(`<h1>Login failed</h1><p>Nothing was changed. Try again from the bot.</p>`, 400);
  }
  const me = await (await fetch(`https://graph.instagram.com/me?fields=user_id,username&access_token=${encodeURIComponent(ll.access_token)}`)).json();
  const want = String(env.EXPECT_IG || "").replace(/^@/, "").toLowerCase();
  if (!me.username || (want && me.username.toLowerCase() !== want)) {
    await say(env, env.OWNER_ID, `⚠️ That login was for @${me.username || "?"}, not @${want}. Nothing was saved. Send /iglogin and log in as @${want}.`);
    return publicPage(`<h1>Wrong account</h1><p>Please try again as @${esc(want)}.</p>`, 400);
  }
  const now = Date.now() / 1000;
  await env.KV.put("ig_token.enc", await seal(env, ll.access_token, "ig-token-v1:"));
  await env.KV.put("ig_account", JSON.stringify({
    user_id: String(me.user_id || short.user_id), username: me.username, at: new Date().toISOString(), at_ts: now,
    expires_at: now + Number(ll.expires_in || 5184000), permissions: short.permissions || "",
  }));
  await say(env, env.OWNER_ID, `✅ Instagram connected: @${me.username}. Each new video will also be posted there as a Reel at its YouTube time.`);
  return publicPage(`<h1>Connected ✅</h1><p>@${esc(me.username)} is connected. You can close this page.</p>`);
}

async function media(req, env, url) {
  const m = url.pathname.match(/^\/m\/([0-9a-f]{32})\.mp4$/);
  if (!m) return new Response("not found", { status: 404 });
  const buf = await env.KV.get(`media:${m[1]}`, { type: "arrayBuffer" });
  if (!buf) return new Response("not found", { status: 404 });
  const size = buf.byteLength;
  const base = { "content-type": "video/mp4", "accept-ranges": "bytes", "cache-control": "no-store" };
  const range = (req.headers.get("range") || "").match(/^bytes=(\d*)-(\d*)$/);
  if (range && (range[1] || range[2])) {
    let start = range[1] ? Number(range[1]) : size - Number(range[2]);
    let end = range[1] && range[2] ? Number(range[2]) : size - 1;
    start = Math.max(0, start); end = Math.min(size - 1, end);
    if (start > end) return new Response(null, { status: 416, headers: { "content-range": `bytes */${size}` } });
    return new Response(req.method === "HEAD" ? null : buf.slice(start, end + 1), { status: 206,
      headers: { ...base, "content-range": `bytes ${start}-${end}/${size}`, "content-length": String(end - start + 1) } });
  }
  return new Response(req.method === "HEAD" ? null : buf, { headers: { ...base, "content-length": String(size) } });
}

// ---------------- Public pages (Google OAuth app home page + privacy policy) ----------------

function esc(s) {
  return String(s).replace(/[&<>"]/g, (ch) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" })[ch]);
}

function publicPage(body, status = 200) {
  return new Response(
    `<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">` +
    `<title>Secret Smart Stuff</title><style>body{margin:0;font:17px/1.6 system-ui,-apple-system,Segoe UI,Roboto,sans-serif;background:#FFFFFF;color:#111}` +
    `main{max-width:680px;margin:0 auto;padding:40px 20px}h1{margin:0 0 8px;color:#1F3BFF}a{color:#1F3BFF}footer{margin-top:40px;font-size:.9rem;color:#555}</style>` +
    `</head><body><main>${body}</main></body></html>`,
    { status, headers: { "content-type": "text/html; charset=utf-8", "cache-control": "no-store" } },
  );
}

const HOME = `<svg role="img" aria-label="Secret Smart Stuff logo" width="72" height="72" viewBox="0 0 200 200" style="border-radius:50%;background:#1F3BFF"><path fill-rule="evenodd" fill="#FFD6E0" d="M100 33 C125 33 140 48 140 72 L140 128 C140 150 124 164 100 164 C76 164 60 150 60 128 L60 72 C60 48 75 33 100 33 Z M100 46 C117 46 126 56 126 71 L126 85 C126 95 119 101 110 101 L90 101 C81 101 74 95 74 85 L74 71 C74 56 83 46 100 46 Z M90 115 L110 115 C115 115 117 118 117 122 L117 129 C117 134 113 137 108 137 L92 137 C87 137 83 134 83 129 L83 122 C83 118 85 115 90 115 Z"/></svg>
<h1>Secret Smart Stuff</h1>
<p><b>The secret smart reasons behind everyday things.</b> Short videos that explain the hidden design of objects you use every day.</p>
<p>Watch on YouTube: <a href="https://www.youtube.com/@secretsmartstuff">youtube.com/@secretsmartstuff</a></p>
<h2>Secret Smart Stuff uploader</h2>
<p>"Secret Smart Stuff uploader" (and its Instagram counterpart "Secret Smart Stuff Publisher") is a private tool used only by the owner of Secret Smart Stuff. It posts the channel's own videos to its own YouTube channel and Instagram account and reads their own statistics. It is not offered to the public, and no other users can sign in to it.</p>
<p>Watch on Instagram: <a href="https://www.instagram.com/secretsmartstuff/">instagram.com/secretsmartstuff</a></p>
<p>Read the <a href="/privacy">Privacy Policy</a>.</p>
<footer>Contact: <a href="mailto:secretsmartstuff@gmail.com">secretsmartstuff@gmail.com</a></footer>`;

const PRIVACY = `<h1>Privacy Policy</h1>
<p>Last updated: 28 October 2026</p>
<p>This policy covers "Secret Smart Stuff uploader" and "Secret Smart Stuff Publisher", private tools used only by the owner of Secret Smart Stuff (YouTube channel and Instagram account).</p>
<h2>What the tool accesses</h2>
<ul><li>Permission to upload videos to the owner's own YouTube channel (youtube.upload).</li>
<li>Read-only access to the owner's own channel and video details (youtube.readonly).</li>
<li>Read-only access to the owner's own channel statistics (yt-analytics.readonly).</li>
<li>Instagram: basic profile of the owner's own professional account, permission to publish its own Reels, and its own insights (instagram_business_basic, instagram_business_content_publish, instagram_business_manage_insights).</li></ul>
<h2>How the data is used</h2>
<p>Only to upload the channel's own videos, schedule them, and measure how they perform. Data is never sold, shared with third parties, or used for advertising.</p>
<h2>Storage and security</h2>
<p>The sign-in token is stored encrypted and is used only by the channel's own automation. No data about viewers or other users is collected.</p>
<h2>Google API Services</h2>
<p>The tool's use of information received from Google APIs follows the <a href="https://developers.google.com/terms/api-services-user-data-policy">Google API Services User Data Policy</a>, including the Limited Use requirements.</p>
<h2>Revoking access</h2>
<p>The owner can revoke access at any time at <a href="https://myaccount.google.com/permissions">myaccount.google.com/permissions</a> (Google) and in Instagram under Settings → Website permissions → Apps and websites.</p>
<h2>Data deletion</h2>
<p>To delete everything the tool stores (sign-in tokens and statistics), email <a href="mailto:secretsmartstuff@gmail.com">secretsmartstuff@gmail.com</a>; it is deleted within 7 days.</p>
<footer>Contact: <a href="mailto:secretsmartstuff@gmail.com">secretsmartstuff@gmail.com</a> · <a href="/">Home</a></footer>`;
