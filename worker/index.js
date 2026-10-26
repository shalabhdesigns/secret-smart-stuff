// Bhaukaali Toons studio Worker (Cloudflare, free plan).
//
// 1. /tg   Telegram webhook: the owner's button taps and replies become GitHub runs
//          (workflow_dispatch on command.yml). Nobody else is obeyed.
// 2. /dash Private dashboard. Login = a 6-digit code sent to the owner's Telegram.
//
// Bindings (set by scripts/deploy_worker.py): KV (namespace), TG_TOKEN, TG_SECRET, OWNER_ID,
// GH_TOKEN, GH_REPO, COOKIE_KEY.

const enc = new TextEncoder();

export default {
  async fetch(req, env) {
    const url = new URL(req.url);
    try {
      if (url.pathname === "/tg" && req.method === "POST") return await telegram(req, env);
      if (url.pathname === "/dash/code" && req.method === "POST") return await sendCode(env, url);
      if (url.pathname === "/dash/login" && req.method === "POST") return await login(req, env, url);
      if (url.pathname === "/dash/logout") return logout(url);
      if (url.pathname === "/dash" || url.pathname === "/") return await dash(req, env, url);
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
        "user-agent": "bhaukaalitoons-worker",
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
    if (kind === "f") {
      await tg(env, "sendMessage", {
        chat_id: chat, parse_mode: "HTML",
        text: `✏️ What should change? Reply to this message in your own words.\n<code>fix job:${job}</code>`,
        reply_markup: { force_reply: true, input_field_placeholder: "e.g. Meera's last line should be funnier" },
      });
      return ack(env, cq, "Reply with what to change");
    }
    if (kind === "d") {
      await tg(env, "sendMessage", {
        chat_id: chat, parse_mode: "HTML",
        text: `🗑 Why drop this episode? Reply to this message (or reply "skip"). I'll make a replacement.\n<code>drop job:${job}</code>`,
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
      : "👍 Dropped. Your reason is saved, and a replacement episode is on its way.";
  } else if (reviewJob && JOB.test(reviewJob)) {   // any reply to a video = what to change
    request = { action: "fix", job: reviewJob, note: text.replace(/^(fix|change)\s*:?\s*/i, "").slice(0, 1500) };
    reply = "👍 Got it. Making the changes; the new version arrives here in about 15 minutes.";
  } else if (/^\/start\b/.test(text) || /^\/help\b/.test(text)) {
    return say(env, chat,
      "Every new Sab Theek Hai episode arrives here 3 days before it goes live.\n\n" +
      "Buttons: ✅ Approve (asks to confirm, then uploads it privately, scheduled for its slot) · ✏️ Fix (tell me what to change) · 🗑 Drop\n\n" +
      "Commands:\n/status – the queue\n/produce – make an extra episode now\n" +
      "/dash – dashboard link\n/revenue 2026-11 12.50 – record revenue for a month (USD)");
  } else if (/^\/status\b/.test(text)) {
    request = { action: "status" }; reply = "⏳ Checking…";
  } else if (/^\/produce\b/.test(text)) {
    request = { action: "produce" }; reply = "🎬 Writing and animating a new episode. It takes about 15 minutes.";
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
    [{ text: "🗑 Drop episode", callback_data: `d:${job}` }],
  ] };
}

async function ack(env, cq, text, alert = false) {
  await tg(env, "answerCallbackQuery", { callback_query_id: cq.id, text: text.slice(0, 190), show_alert: alert });
  return new Response("ok");
}

async function say(env, chat, text) {
  await tg(env, "sendMessage", { chat_id: chat, text });
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
      `<h2>Bhaukaali Toons · Studio</h2>` +
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
