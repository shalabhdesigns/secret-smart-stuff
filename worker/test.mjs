// Offline tests for the Worker: fake Telegram, GitHub and KV. Run: node worker/test.mjs
import worker from "./index.js";
import assert from "node:assert/strict";

const calls = [];
let channelTitle = "Secret Smart Stuff";
globalThis.fetch = async (url, init = {}) => {
  let body = null;
  try { body = init.body ? JSON.parse(init.body) : null; } catch { body = String(init.body); }
  calls.push({ url: String(url), body });
  if (String(url).includes("api.github.com")) return new Response(null, { status: 204 });
  if (String(url).includes("oauth2.googleapis.com/token"))
    return new Response(JSON.stringify({ refresh_token: "RT-123", access_token: "AT", scope: "x" }), { headers: { "content-type": "application/json" } });
  if (String(url).includes("youtube/v3/channels"))
    return new Response(JSON.stringify({ items: [{ id: "UCx", snippet: { title: channelTitle } }] }), { headers: { "content-type": "application/json" } });
  return new Response(JSON.stringify({ ok: true, result: {} }), { headers: { "content-type": "application/json" } });
};
const store = new Map();
const KV = {
  get: async (k) => (store.has(k) ? store.get(k) : null),
  put: async (k, v) => store.set(k, v),
  delete: async (k) => store.delete(k),
};
const env = { KV, TG_TOKEN: "t", TG_SECRET: "s3cret", OWNER_ID: "42", GH_TOKEN: "g", GH_REPO: "o/r",
  COOKIE_KEY: "k".repeat(32), SELF_URL: "https://studio.example.workers.dev",
  YT_CLIENT_ID: "cid", YT_CLIENT_SECRET: "csecret", EXPECT_CHANNEL: "Secret Smart Stuff" };
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
channelTitle = "Bhaukaali Toons";
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
console.log("worker tests passed");
