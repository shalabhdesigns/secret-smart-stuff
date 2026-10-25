// Offline tests for the Worker: fake Telegram, GitHub and KV. Run: node worker/test.mjs
import worker from "./index.js";
import assert from "node:assert/strict";

const calls = [];
globalThis.fetch = async (url, init = {}) => {
  const body = init.body ? JSON.parse(init.body) : null;
  calls.push({ url: String(url), body });
  if (String(url).includes("api.github.com")) return new Response(null, { status: 204 });
  return new Response(JSON.stringify({ ok: true, result: {} }), { headers: { "content-type": "application/json" } });
};
const store = new Map();
const KV = {
  get: async (k) => (store.has(k) ? store.get(k) : null),
  put: async (k, v) => store.set(k, v),
  delete: async (k) => store.delete(k),
};
const env = { KV, TG_TOKEN: "t", TG_SECRET: "s3cret", OWNER_ID: "42", GH_TOKEN: "g", GH_REPO: "o/r",
  COOKIE_KEY: "k".repeat(32), SELF_URL: "https://studio.example.workers.dev" };
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
console.log("worker tests passed");
