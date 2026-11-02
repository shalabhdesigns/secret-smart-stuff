// Offline tests for the Worker: fake Telegram, GitHub and KV. Run: node worker/test.mjs
import worker from "./index.js";
import assert from "node:assert/strict";

const calls = [];
let channelTitle = "Secret Smart Stuff";
let igUser = "secretsmartstuff";
globalThis.fetch = async (url, init = {}) => {
  let body = null;
  try { body = init.body ? JSON.parse(init.body) : null; } catch { body = String(init.body); }
  calls.push({ url: String(url), body });
  if (String(url).includes("api.github.com")) return new Response(null, { status: 204 });
  if (String(url).includes("oauth2.googleapis.com/token"))
    return new Response(JSON.stringify({ refresh_token: "RT-123", access_token: "AT", scope: "x" }), { headers: { "content-type": "application/json" } });
  if (String(url).includes("youtube/v3/channels"))
    return new Response(JSON.stringify({ items: [{ id: "UCx", snippet: { title: channelTitle } }] }), { headers: { "content-type": "application/json" } });
  if (String(url).includes("api.instagram.com/oauth/access_token"))
    return new Response(JSON.stringify({ data: [{ access_token: "IGS-short", user_id: "1789", permissions: "instagram_business_basic" }] }));
  if (String(url).includes("graph.instagram.com/access_token"))
    return new Response(JSON.stringify({ access_token: "IGL-long", token_type: "bearer", expires_in: 5184000 }));
  if (String(url).includes("graph.instagram.com/me"))
    return new Response(JSON.stringify({ user_id: "1789", username: igUser, id: "app-scoped" }));
  return new Response(JSON.stringify({ ok: true, result: {} }), { headers: { "content-type": "application/json" } });
};
const store = new Map();
const KV = {
  get: async (k) => (store.has(k) ? store.get(k) : null),
  put: async (k, v) => store.set(k, v),
  delete: async (k) => store.delete(k),
  list: async ({ prefix = "" } = {}) => ({ keys: [...store.keys()].filter((k) => k.startsWith(prefix)).map((name) => ({ name })),
                                         list_complete: true }),
};
const env = { KV, TG_TOKEN: "t", TG_SECRET: "s3cret", OWNER_ID: "42", GH_TOKEN: "g", GH_REPO: "o/r",
  COOKIE_KEY: "k".repeat(32), SELF_URL: "https://studio.example.workers.dev",
  YT_CLIENT_ID: "cid", YT_CLIENT_SECRET: "csecret", EXPECT_CHANNEL: "Secret Smart Stuff",
  IG_APP_ID: "igapp", IG_APP_SECRET: "igsecret", EXPECT_IG: "secretsmartstuff" };
const H = { "content-type": "application/json", "x-telegram-bot-api-secret-token": "s3cret" };
const tgPost = (u, headers = H) => worker.fetch(new Request("https://x/tg", { method: "POST", headers, body: JSON.stringify(u) }), env);
const gh = () => calls.filter((c) => c.url.includes("api.github.com"));
const lastReq = () => JSON.parse(gh().at(-1).body.inputs.request);

// wrong secret -> 403, nothing dispatched
assert.equal((await tgPost({ message: { from: { id: 42 }, text: "/produce" } }, { "content-type": "application/json" })).status, 403);
assert.equal(gh().length, 0);
// stranger -> ignored
await tgPost({ message: { from: { id: 7 }, text: "/produce" } });
assert.equal(gh().length, 0);
// approve needs confirmation
await tgPost({ callback_query: { id: "1", from: { id: 42 }, data: "a:onigiri-v9", message: { message_id: 5 } } });
assert.equal(gh().length, 0);
await tgPost({ callback_query: { id: "2", from: { id: 42 }, data: "A:onigiri-v9", message: { message_id: 5 } } });
assert.deepEqual({ ...lastReq(), nonce: undefined }, { action: "approve", job: "onigiri-v9", nonce: undefined });
// stop an auto-published video: confirm first, then dispatch
let nstop = gh().length;
await tgPost({ callback_query: { id: "9", from: { id: 42 }, data: "s:bus-v1", message: { message_id: 7 } } });
assert.equal(gh().length, nstop);
await tgPost({ callback_query: { id: "10", from: { id: 42 }, data: "S:bus-v1", message: { message_id: 7 } } });
assert.equal(lastReq().action, "unpublish"); assert.equal(lastReq().job, "bus-v1");
// bad job id rejected
const before = gh().length;
await tgPost({ callback_query: { id: "3", from: { id: 42 }, data: "A:../../x", message: { message_id: 5 } } });
assert.equal(gh().length, before);
// fix: reply to the prompt
await tgPost({ message: { from: { id: 42 }, text: "make the 3rd picture show the tabs",
  reply_to_message: { text: "✏️ What should change?\nfix job:onigiri-v9" } } });
assert.equal(lastReq().action, "fix"); assert.equal(lastReq().note, "make the 3rd picture show the tabs");
// drop with skip
await tgPost({ message: { from: { id: 42 }, text: "skip", reply_to_message: { text: "drop job:onigiri-v9" } } });
assert.equal(lastReq().action, "reject"); assert.equal(lastReq().note, "");
// fix by replying to the video caption
await tgPost({ message: { from: { id: 42 }, text: "fix: louder music", reply_to_message: { caption: "🎬 x\njob:abc-v2" } } });
assert.equal(lastReq().job, "abc-v2"); assert.equal(lastReq().note, "louder music");
// revenue
await tgPost({ message: { from: { id: 42 }, text: "/revenue 2026-11 12.5" } });
assert.equal(lastReq().action, "revenue"); assert.equal(lastReq().usd, 12.5);
const n = gh().length;
await tgPost({ message: { from: { id: 42 }, text: "/revenue nov twelve" } });
assert.equal(gh().length, n);

// dashboard: no cookie -> login page, no data leak
store.set("dashboard.html", "<p>SECRET NUMBERS</p>");
let r = await worker.fetch(new Request("https://x/dash"), env);
assert.ok(!(await r.text()).includes("SECRET"));
// code sent to owner only
await worker.fetch(new Request("https://x/dash/code", { method: "POST" }), env);
const code = store.get("login_code");
assert.match(code, /^\d{6}$/);
assert.equal(calls.at(-1).body.chat_id, "42");
// wrong code 5 times burns it
const form = (c) => { const f = new FormData(); f.set("code", c); return f; };
for (let i = 0; i < 5; i++) await worker.fetch(new Request("https://x/dash/login", { method: "POST", body: form("000000") }), env);
assert.equal(store.get("login_code"), undefined);
// new code, correct login -> cookie -> data visible
store.delete("bad_tries");
await worker.fetch(new Request("https://x/dash/code", { method: "POST" }), env);
r = await worker.fetch(new Request("https://x/dash/login", { method: "POST", body: form(store.get("login_code")) }), env);
const cookie = r.headers.get("set-cookie").split(";")[0];
r = await worker.fetch(new Request("https://x/dash", { headers: { cookie } }), env);
assert.ok((await r.text()).includes("SECRET"));
// forged cookie rejected
r = await worker.fetch(new Request("https://x/dash", { headers: { cookie: "sss=99999999999999.0000000000000000000000000000000000000000000000000000000000000000" } }), env);
assert.ok(!(await r.text()).includes("SECRET"));
// code works once
r = await worker.fetch(new Request("https://x/dash/login", { method: "POST", body: form(code) }), env);
assert.ok(r.headers.get("location").includes("bad=1"));

// public pages
r = await worker.fetch(new Request("https://x/"), env);
assert.ok((await r.text()).includes("Secret Smart Stuff uploader"));
r = await worker.fetch(new Request("https://x/privacy"), env);
assert.ok((await r.text()).includes("Limited Use"));

// one-tap YouTube login
const login = async () => {
  await tgPost({ message: { from: { id: 42 }, text: "/ytlogin" } });
  const link = [...store.keys()].find((k) => k.startsWith("oauth_link:")).slice(11);
  let rr = await worker.fetch(new Request(`https://x/oauth/start?n=${link}`), env);
  assert.equal(rr.status, 302);
  const loc = new URL(rr.headers.get("location"));
  assert.equal(loc.searchParams.get("redirect_uri"), "https://studio.example.workers.dev/oauth/callback");
  assert.equal(loc.searchParams.get("access_type"), "offline");
  // a link preview (or a second tap) must not use the link up
  assert.equal((await worker.fetch(new Request(`https://x/oauth/start?n=${link}`), env)).status, 302);
  store.delete(`oauth_link:${link}`);
  return loc.searchParams.get("state");
};
// the bot's login message has no link preview
await tgPost({ message: { from: { id: 42 }, text: "/ytlogin" } });
assert.equal(calls.filter((c) => c.url.includes("sendMessage")).at(-1).body.link_preview_options.is_disabled, true);
for (const k of [...store.keys()]) if (k.startsWith("oauth_link:")) store.delete(k);
// forged state -> refused, nothing stored
r = await worker.fetch(new Request("https://x/oauth/callback?state=" + "a".repeat(48) + "&code=c"), env);
assert.equal(r.status, 400); assert.equal(store.get("yt_refresh.enc"), undefined);
// wrong channel -> not stored
channelTitle = "Some Other Channel";
r = await worker.fetch(new Request(`https://x/oauth/callback?state=${await login()}&code=c`), env);
assert.equal(r.status, 400); assert.equal(store.get("yt_refresh.enc"), undefined);
// right channel -> stored encrypted (never in clear)
channelTitle = "Secret Smart Stuff";
r = await worker.fetch(new Request(`https://x/oauth/callback?state=${await login()}&code=c`), env);
assert.equal(r.status, 200);
const sealed = store.get("yt_refresh.enc");
assert.ok(sealed && !sealed.includes("RT-123"));
assert.equal(JSON.parse(store.get("yt_channel")).title, "Secret Smart Stuff");
// decrypt like the runner does
const raw = Uint8Array.from(atob(sealed), (ch) => ch.charCodeAt(0));
const kraw = await crypto.subtle.digest("SHA-256", new TextEncoder().encode("yt-refresh-v1:csecret"));
const key = await crypto.subtle.importKey("raw", kraw, { name: "AES-GCM" }, false, ["decrypt"]);
const plain = new TextDecoder().decode(await crypto.subtle.decrypt({ name: "AES-GCM", iv: raw.slice(0, 12) }, key, raw.slice(12)));
assert.equal(plain, "RT-123");

// a command sent as a reply to a video message is still a command (bug seen 28 Oct: /iglogin became a "fix")
let nfix = gh().length;
await tgPost({ message: { from: { id: 42 }, text: "/iglogin", reply_to_message: { text: "Review…\njob:ep002b" } } });
assert.equal(gh().length, nfix);
assert.ok(calls.filter((c) => c.url.includes("sendMessage")).at(-1).body.text.includes("/ig/start?n="));

// one-tap Instagram login
const igLogin = async () => {
  for (const k of [...store.keys()]) if (k.startsWith("oauth_link:")) store.delete(k);
  await tgPost({ message: { from: { id: 42 }, text: "/iglogin" } });
  assert.ok(calls.filter((c) => c.url.includes("sendMessage")).at(-1).body.text.includes("/ig/start?n="));
  const link = [...store.keys()].find((k) => k.startsWith("oauth_link:")).slice(11);
  const rr = await worker.fetch(new Request(`https://x/ig/start?n=${link}`), env);
  assert.equal(rr.status, 302);
  const loc = new URL(rr.headers.get("location"));
  assert.equal(loc.host, "www.instagram.com");
  assert.equal(loc.searchParams.get("client_id"), "igapp");
  assert.equal(loc.searchParams.get("redirect_uri"), "https://studio.example.workers.dev/ig/callback");
  assert.ok(loc.searchParams.get("scope").includes("instagram_business_content_publish"));
  return loc.searchParams.get("state");
};
r = await worker.fetch(new Request("https://x/ig/callback?state=" + "b".repeat(48) + "&code=c"), env);
assert.equal(r.status, 400); assert.equal(store.get("ig_token.enc"), undefined);
igUser = "someone_else";
r = await worker.fetch(new Request(`https://x/ig/callback?state=${await igLogin()}&code=c#_`), env);
assert.equal(r.status, 400); assert.equal(store.get("ig_token.enc"), undefined);
igUser = "secretsmartstuff";
r = await worker.fetch(new Request(`https://x/ig/callback?state=${await igLogin()}&code=c`), env);
assert.equal(r.status, 200);
const igSealed = store.get("ig_token.enc");
assert.ok(igSealed && !igSealed.includes("IGL-long"));
const acct = JSON.parse(store.get("ig_account"));
assert.equal(acct.user_id, "1789"); assert.equal(acct.username, "secretsmartstuff");
assert.ok(acct.expires_at > Date.now() / 1000 + 50 * 86400);
const igRaw = Uint8Array.from(atob(igSealed), (ch) => ch.charCodeAt(0));
const igK = await crypto.subtle.importKey("raw", await crypto.subtle.digest("SHA-256", new TextEncoder().encode("ig-token-v1:csecret")),
  { name: "AES-GCM" }, false, ["decrypt"]);
assert.equal(new TextDecoder().decode(await crypto.subtle.decrypt({ name: "AES-GCM", iv: igRaw.slice(0, 12) }, igK, igRaw.slice(12))), "IGL-long");
// video hand-off: only the exact random key, whole file and byte ranges
store.set("media:" + "c".repeat(32), new Uint8Array([1, 2, 3, 4, 5]).buffer);
r = await worker.fetch(new Request("https://x/m/" + "c".repeat(32) + ".mp4"), env);
assert.equal(r.status, 200); assert.equal(r.headers.get("content-type"), "video/mp4");
assert.equal((await r.arrayBuffer()).byteLength, 5);
r = await worker.fetch(new Request("https://x/m/" + "c".repeat(32) + ".mp4", { headers: { range: "bytes=1-2" } }), env);
assert.equal(r.status, 206); assert.equal(r.headers.get("content-range"), "bytes 1-2/5");
assert.deepEqual([...new Uint8Array(await r.arrayBuffer())], [2, 3]);
assert.equal((await worker.fetch(new Request("https://x/m/" + "d".repeat(32) + ".mp4"), env)).status, 404);
assert.equal((await worker.fetch(new Request("https://x/m/../ig_token.enc"), env)).status, 404);
// covers (3 Nov 2026): same store, served as JPEG; other extensions are refused
r = await worker.fetch(new Request("https://x/m/" + "c".repeat(32) + ".jpg"), env);
assert.equal(r.status, 200); assert.equal(r.headers.get("content-type"), "image/jpeg");
assert.equal((await worker.fetch(new Request("https://x/m/" + "c".repeat(32) + ".png"), env)).status, 404);
// timers: a cron that is in SCHEDULE dispatches its request; any other does nothing
const waits = [];
const sEnv = { ...env, SCHEDULE: JSON.stringify({ "17 0 * * *": { action: "daily" }, "48 16 * * *": { action: "ig_due" } }) };
let ngh = gh().length;
await worker.scheduled({ cron: "17 0 * * *" }, sEnv, { waitUntil: (p) => waits.push(p) });
await Promise.all(waits);
assert.equal(gh().length, ngh + 1); assert.equal(lastReq().action, "daily");
await worker.scheduled({ cron: "1 1 * * *" }, sEnv, { waitUntil: (p) => waits.push(p) });
await Promise.all(waits);
assert.equal(gh().length, ngh + 1);
// Instagram watcher (3 Nov 2026): starts igpost.yml once for a Reel due within ~15 min; never for later, stopped or
// already-started ones
const t0 = Date.parse("2026-11-03T19:52:00Z");
store.set("igdue:job-soon", "2026-11-03T20:00:00Z");
store.set("igdue:job-later", "2026-11-03T21:00:00Z");
store.set("igdue:job-stopped", "2026-11-03T20:00:00Z"); store.set("stop:job-stopped", "1");
ngh = gh().length;
const { igWatch } = await import("./index.js");
assert.deepEqual(await igWatch({ ...env }, t0), ["job-soon"]);
const ig = calls[calls.length - 1];
assert.ok(ig.url.endsWith("/actions/workflows/igpost.yml/dispatches")); assert.deepEqual(ig.body.inputs, { job: "job-soon" });
assert.deepEqual(await igWatch({ ...env }, t0 + 60e3), []);                 // already started: not twice
const wEnv = { ...env, SCHEDULE: JSON.stringify({ "*/5 * * * *": { action: "igwatch" } }) };
store.delete("igdisp:job-soon");
await worker.scheduled({ cron: "*/5 * * * *" }, wEnv, { waitUntil: (p) => waits.push(p) });
await Promise.all(waits);
// owner-entered values: login required; set / add revenue / delete; junk refused
const post = (path, body, c) => worker.fetch(new Request("https://x" + path, { method: "POST", body: JSON.stringify(body),
  headers: c ? { cookie: c } : {} }), env);
assert.equal((await post("/dash/manual", { op: "set", section: "balances", name: "anthropic", value: { usd: 20 } })).status, 401);
assert.equal((await worker.fetch(new Request("https://x/dash/manual.json"), env)).status, 401);
r = await post("/dash/manual", { op: "set", section: "subscriptions", name: "claude",
  value: { plan: "Max", usd_month: 100, renews: "2026-11-20", share_pct: 30, evil: { x: 1 } } }, cookie);
assert.equal(r.status, 200);
let man = JSON.parse(store.get("manual.json"));
assert.equal(man.subscriptions.claude.usd_month, 100); assert.ok(man.subscriptions.claude.at); assert.equal(man.subscriptions.claude.evil, undefined);
await post("/dash/manual", { op: "revenue_add", rows: [{ period: "2026-11", platform: "youtube", usd: 1.5 }] }, cookie);
man = JSON.parse(store.get("manual.json")); assert.equal(man.revenue.length, 1); assert.equal(man.revenue[0].usd, 1.5);
await post("/dash/manual", { op: "revenue_del", index: 0 }, cookie);
assert.equal(JSON.parse(store.get("manual.json")).revenue.length, 0);
assert.equal((await post("/dash/manual", { op: "set", section: "secrets", name: "x", value: {} }, cookie)).status, 400);
r = await worker.fetch(new Request("https://x/dash/manual.json", { headers: { cookie } }), env);
assert.equal(r.status, 200);
// refresh button: starts analytics once per 15 minutes
assert.equal((await worker.fetch(new Request("https://x/dash/refresh", { method: "POST", headers: { cookie } }), env)).status, 200);
assert.ok(calls[calls.length - 1].url.endsWith("/actions/workflows/analytics.yml/dispatches"));
assert.equal((await worker.fetch(new Request("https://x/dash/refresh", { method: "POST", headers: { cookie } }), env)).status, 429);
console.log("worker tests passed");
