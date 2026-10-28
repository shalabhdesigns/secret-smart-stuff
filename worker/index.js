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
//
// Bindings (set by scripts/deploy_worker.py): KV (namespace), TG_TOKEN, TG_SECRET, OWNER_ID,
// GH_TOKEN, GH_REPO, COOKIE_KEY, SELF_URL, YT_CLIENT_ID, YT_CLIENT_SECRET, EXPECT_CHANNEL.

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
      if (url.pathname === "/privacy") return publicPage(PRIVACY);
      if (url.pathname === "/") return publicPage(HOME);
      if (url.pathname === "/health") return new Response("ok");
      return new Response("not found", { status: 404 });
    } catch (e) {
      return new Response("error", { status: 500 });
    }
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
      const err = await dispatch(env, { action: "unpublish", job });
      if (err) return ack(env, cq, "Could not start: " + err, true);
      await tg(env, "editMessageReplyMarkup", { chat_id: chat, message_id: msg.message_id,
        reply_markup: { inline_keyboard: [[{ text: "⏳ Stopping…", callback_data: "noop:x" }]] } });
      return ack(env, cq, "Stopping. I'll confirm in a minute.");
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
  if (marker && JOB.test(marker[2])) {
    const note = /^skip$/i.test(text) ? "" : text.slice(0, 1500);
    if (marker[1] === "fix" && !note) return say(env, chat, "Please say what to change.");
    request = { action: marker[1] === "fix" ? "fix" : "reject", job: marker[2], note };
    reply = marker[1] === "fix"
      ? "👍 Got it. Making the changes; the new version arrives here in about 15 minutes."
      : "👍 Dropped. Your reason is saved; the next video comes with the next daily run (or send /produce).";
  } else if (reviewJob && JOB.test(reviewJob)) {   // any reply to a video = what to change
    request = { action: "fix", job: reviewJob, note: text.replace(/^(fix|change)\s*:?\s*/i, "").slice(0, 1500) };
    reply = "👍 Got it. Making the changes; the new version arrives here in about 15 minutes.";
  } else if (/^\/start\b/.test(text) || /^\/help\b/.test(text)) {
    return say(env, chat,
      "Every new Secret Smart Stuff video is checked by my final review and, if it passes, uploaded and scheduled automatically (until 25 Nov 2026). You get a message for each one.\n\n" +
      "Buttons: ⏸ Stop it (keeps that video private) · ✅ Approve / ✏️ Fix / 🗑 Drop (for videos that need your review)\n\n" +
      "Commands:\n/status – the queue\n/produce – make an extra video now\n" +
      "/dash – dashboard link\n/ytlogin – connect the YouTube channel (one tap)\n/revenue 2026-11 12.50 – record revenue for a month (USD)");
  } else if (/^\/ytlogin\b/.test(text)) {
    return say(env, chat, "🔑 Tap to connect the Secret Smart Stuff channel (link works once, for 30 minutes):\n" + await loginLink(env) +
      "\n\nSign in as secretsmartstuff@gmail.com, choose the Secret Smart Stuff channel, then Allow.");
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

async function loginLink(env) {
  const n = randomId();
  await env.KV.put(`oauth_link:${n}`, "1", { expirationTtl: 1800 });
  return `${env.SELF_URL}/oauth/start?n=${n}`;
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

async function aesKey(env) {
  const raw = await crypto.subtle.digest("SHA-256", enc.encode("yt-refresh-v1:" + env.YT_CLIENT_SECRET));
  return crypto.subtle.importKey("raw", raw, { name: "AES-GCM" }, false, ["encrypt"]);
}

async function seal(env, text) {
  const iv = crypto.getRandomValues(new Uint8Array(12));
  const ct = new Uint8Array(await crypto.subtle.encrypt({ name: "AES-GCM", iv }, await aesKey(env), enc.encode(text)));
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

// ---------------- Public pages (Google OAuth app home page + privacy policy) ----------------

function esc(s) {
  return String(s).replace(/[&<>"]/g, (ch) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" })[ch]);
}

function publicPage(body, status = 200) {
  return new Response(
    `<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">` +
    `<title>Secret Smart Stuff</title><style>body{margin:0;font:17px/1.6 system-ui,-apple-system,Segoe UI,Roboto,sans-serif;background:#F4EFE6;color:#14213D}` +
    `main{max-width:680px;margin:0 auto;padding:40px 20px}h1{margin:0 0 8px}a{color:#C4551A}footer{margin-top:40px;font-size:.9rem;color:#555}</style>` +
    `</head><body><main>${body}</main></body></html>`,
    { status, headers: { "content-type": "text/html; charset=utf-8", "cache-control": "no-store" } },
  );
}

const HOME = `<h1>Secret Smart Stuff</h1>
<p><b>The secret smart reasons behind everyday things.</b> Short videos that explain the hidden design of objects you use every day.</p>
<p>Watch on YouTube: <a href="https://www.youtube.com/@secretsmartstuff">youtube.com/@secretsmartstuff</a></p>
<h2>Secret Smart Stuff uploader</h2>
<p>"Secret Smart Stuff uploader" is a private tool used only by the owner of the Secret Smart Stuff channel. It uploads the channel's own videos to YouTube and reads the channel's own statistics. It is not offered to the public, and no other users can sign in to it.</p>
<p>Read the <a href="/privacy">Privacy Policy</a>.</p>
<footer>Contact: <a href="mailto:secretsmartstuff@gmail.com">secretsmartstuff@gmail.com</a></footer>`;

const PRIVACY = `<h1>Privacy Policy</h1>
<p>Last updated: 28 October 2026</p>
<p>This policy covers "Secret Smart Stuff uploader", a private tool used only by the owner of the Secret Smart Stuff YouTube channel.</p>
<h2>What the tool accesses</h2>
<ul><li>Permission to upload videos to the owner's own YouTube channel (youtube.upload).</li>
<li>Read-only access to the owner's own channel and video details (youtube.readonly).</li>
<li>Read-only access to the owner's own channel statistics (yt-analytics.readonly).</li></ul>
<h2>How the data is used</h2>
<p>Only to upload the channel's own videos, schedule them, and measure how they perform. Data is never sold, shared with third parties, or used for advertising.</p>
<h2>Storage and security</h2>
<p>The sign-in token is stored encrypted and is used only by the channel's own automation. No data about viewers or other users is collected.</p>
<h2>Google API Services</h2>
<p>The tool's use of information received from Google APIs follows the <a href="https://developers.google.com/terms/api-services-user-data-policy">Google API Services User Data Policy</a>, including the Limited Use requirements.</p>
<h2>Revoking access</h2>
<p>The owner can revoke access at any time at <a href="https://myaccount.google.com/permissions">myaccount.google.com/permissions</a>.</p>
<footer>Contact: <a href="mailto:secretsmartstuff@gmail.com">secretsmartstuff@gmail.com</a> · <a href="/">Home</a></footer>`;
