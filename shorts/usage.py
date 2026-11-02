"""Resources, balances, limits and subscriptions for the dashboard (owner, 3 Nov 2026).

Rule: never show an assumed number as real. Every item says where its number came from:
- "measured"  : read from the service's own API just now (or from our own run records)
- "manual"    : typed in by the owner on the dashboard, with the date it was typed
- "derived"   : calculated from measured/manual numbers (formula shown), e.g. days left at the current burn rate
- "unavailable": the service has no API for it; the dashboard says why and links to where to look

check(state) runs in every analytics pass (every 4 hours) and stores one snapshot per service in `resources`.
"""
from __future__ import annotations

import datetime as dt
import json
import os
import time

import requests

GITHUB_FREE_MINUTES = 2000      # GitHub Free: 2,000 Actions minutes / month for private repos (owner can override)

LINKS = {
    "elevenlabs": "https://elevenlabs.io/app/subscription",
    "bfl": "https://dashboard.bfl.ai/",
    "anthropic": "https://console.anthropic.com/settings/billing",
    "claude": "https://claude.ai/settings/billing",
    "github": "https://github.com/settings/billing",
    "youtube": "https://console.cloud.google.com/apis/api/youtube.googleapis.com/quotas",
    "instagram": "https://developers.facebook.com/apps/",
    "cloudflare": "https://dash.cloudflare.com/",
}


def _now_iso() -> str:
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())


def _month_start() -> float:
    t = time.gmtime()
    return dt.datetime(t.tm_year, t.tm_mon, 1, tzinfo=dt.timezone.utc).timestamp()


def manual(state) -> dict:
    """Owner-entered values (dashboard form -> Worker KV 'manual.json'); cached in settings for offline builds."""
    raw = None
    try:
        from .publish.youtube import _cf_kv
        raw = _cf_kv("manual.json")
    except Exception:  # noqa: BLE001
        raw = None
    if raw:
        state.set_setting("manual_json", raw)
    try:
        return json.loads(raw or state.get_setting("manual_json") or "{}")
    except ValueError:
        return {}


# ---------------- per service ----------------

def elevenlabs(key: str) -> dict:
    if not key:
        return {"source": "unavailable", "why": "no ElevenLabs key in this run"}
    try:
        r = requests.get("https://api.elevenlabs.io/v1/user/subscription", headers={"xi-api-key": key}, timeout=30)
    except Exception as e:  # noqa: BLE001
        return {"source": "unavailable", "why": f"API error: {e}"[:200]}
    if r.status_code != 200:
        return {"source": "unavailable", "why": f"API {r.status_code} (the key may lack user_read)"}
    j = r.json()
    limit, used = int(j.get("character_limit") or 0), int(j.get("character_count") or 0)
    inv = j.get("next_invoice") or {}
    reset = j.get("next_character_count_reset_unix")
    pay = inv.get("next_payment_attempt_unix")
    return {"source": "measured", "unit": "credits", "limit": limit, "used": used, "left": limit - used,
            "resets": dt.datetime.fromtimestamp(reset, dt.timezone.utc).strftime("%Y-%m-%d") if reset else None,
            "tier": j.get("tier"), "plan_status": j.get("status"), "currency": (j.get("currency") or "usd").upper(),
            "next_invoice": (inv.get("amount_due_cents") or 0) / 100 if inv else None,
            "renews": (dt.datetime.fromtimestamp(pay, dt.timezone.utc).strftime("%Y-%m-%d")
                       if pay and pay > 0 else None),
            "open_invoices": bool(j.get("has_open_invoices")),
            "overage": (j.get("current_overage") or {}).get("amount")}


def bfl(key: str) -> dict:
    if not key:
        return {"source": "unavailable", "why": "no BFL key in this run"}
    try:
        r = requests.get("https://api.bfl.ai/v1/credits", headers={"x-key": key}, timeout=30)
    except Exception as e:  # noqa: BLE001
        return {"source": "unavailable", "why": f"API error: {e}"[:200]}
    if r.status_code != 200:
        return {"source": "unavailable", "why": f"API {r.status_code}"}
    c = float(r.json().get("credits") or 0)
    return {"source": "measured", "unit": "credits", "left": c, "usd_left": round(c / 100, 2),
            "note": "prepaid credits (1 credit = $0.01); no expiry date reported"}


def anthropic(state, man: dict) -> dict:
    """Spend: measured tokens x list price (always). Billed cost: Admin API if an admin key is set (organisations
    only). Balance: Anthropic has no balance API, so it is the owner's last typed balance minus measured spend since."""
    spent_month = state.db.execute("SELECT COALESCE(SUM(usd),0) s FROM costs WHERE provider='anthropic' AND at>=?",
                                   (_month_start(),)).fetchone()["s"]
    out = {"source": "measured", "spent_month_calc": round(spent_month, 2),
           "spent_note": "measured tokens x Anthropic list prices (not an invoice)"}
    admin = os.environ.get("ANTHROPIC_ADMIN_KEY", "").strip()
    if admin:
        try:
            r = requests.get("https://api.anthropic.com/v1/organizations/cost_report",
                             params={"starting_at": time.strftime("%Y-%m-01T00:00:00Z", time.gmtime()),
                                     "ending_at": _now_iso()},
                             headers={"x-api-key": admin, "anthropic-version": "2023-06-01"}, timeout=30)
            if r.status_code == 200:
                cents = 0.0
                for b in r.json().get("data") or []:
                    for x in b.get("results") or []:
                        cents += float(x.get("amount") or 0)
                out["billed_month"] = round(cents / 100, 2)
            else:
                out["billed_why"] = f"Admin API {r.status_code}"
        except Exception as e:  # noqa: BLE001
            out["billed_why"] = str(e)[:150]
    else:
        out["billed_why"] = "set an Admin API key (organisations only) to read billed cost"
    bal = (man.get("balances") or {}).get("anthropic")
    if bal and bal.get("usd") is not None and bal.get("at"):
        at = dt.datetime.fromisoformat(bal["at"].replace("Z", "+00:00")).timestamp()
        since = state.db.execute("SELECT COALESCE(SUM(usd),0) s FROM costs WHERE provider='anthropic' AND at>=?",
                                 (at,)).fetchone()["s"]
        out.update({"left_usd": round(float(bal["usd"]) - since, 2), "left_source": "derived",
                    "left_note": f"your balance ${float(bal['usd']):.2f} on {bal['at'][:10]} minus measured use since"})
    else:
        out["left_source"] = "unavailable"
        out["left_note"] = "Anthropic has no balance API: type your Console balance on the dashboard"
    return out


def github_minutes(state) -> dict:
    """Actions minutes this month, from the repo's run timing API (billable time). Needs GH_TOKEN in the run."""
    tok = os.environ.get("GH_TOKEN") or os.environ.get("GITHUB_TOKEN")
    repo = os.environ.get("GITHUB_REPOSITORY", "shalabhdesigns/secret-smart-stuff")
    if tok:
        h = {"Authorization": f"Bearer {tok}", "Accept": "application/vnd.github+json"}
        since = time.strftime("%Y-%m-01", time.gmtime())
        known = {r["run_id"] for r in state.db.execute("SELECT run_id FROM gh_runs WHERE billable_ms IS NOT NULL")}
        for page in range(1, 11):
            try:
                r = requests.get(f"https://api.github.com/repos/{repo}/actions/runs", headers=h, timeout=30,
                                 params={"per_page": 100, "page": page, "created": f">={since}", "status": "completed"})
                runs = r.json().get("workflow_runs") or []
            except Exception:  # noqa: BLE001
                break
            for run in runs:
                if run["id"] in known:
                    continue
                try:
                    t = requests.get(f"https://api.github.com/repos/{repo}/actions/runs/{run['id']}/timing",
                                     headers=h, timeout=30).json()
                except Exception:  # noqa: BLE001
                    continue
                bill = sum(int(v.get("total_ms") or 0) for v in (t.get("billable") or {}).values())
                with state.tx() as db:
                    db.execute("INSERT OR REPLACE INTO gh_runs(run_id, workflow, created, billable_ms, duration_ms, at) "
                               "VALUES (?,?,?,?,?,?)", (run["id"], run.get("name"), run.get("created_at"), bill,
                                                        int(t.get("run_duration_ms") or 0), time.time()))
            if len(runs) < 100:
                break
    m = time.strftime("%Y-%m", time.gmtime())
    # GitHub's timing API now reports billable time as 0 for many runs; use the run's measured duration then
    rows = state.db.execute("SELECT workflow, SUM(MAX(COALESCE(billable_ms,0), COALESCE(duration_ms,0))) b, "
                            "COUNT(*) n FROM gh_runs WHERE created LIKE ? GROUP BY workflow", (m + "%",)).fetchall()
    if not rows:
        return {"source": "unavailable", "why": "no run timings yet"}
    used = sum((r["b"] or 0) for r in rows) / 60000
    man = manual(state)
    lim = ((man.get("limits") or {}).get("github") or {}).get("github_minutes")
    limit = float(lim or GITHUB_FREE_MINUTES)
    return {"source": "measured", "unit": "minutes", "used": round(used), "limit": int(limit),
            "left": round(limit - used), "resets": _next_month(),
            "by_workflow": {r["workflow"]: round((r["b"] or 0) / 60000) for r in rows},
            "limit_source": "manual" if lim else "GitHub Free plan default",
            "note": "measured run time per workflow run (GitHub bills each job rounded up to a whole minute, so the "
                    "bill can be a little higher)"}


def _next_month() -> str:
    t = time.gmtime()
    y, mo = (t.tm_year + 1, 1) if t.tm_mon == 12 else (t.tm_year, t.tm_mon + 1)
    return f"{y}-{mo:02d}-01"


def instagram() -> dict:
    try:
        from .publish import instagram as ig
        tok, acc = ig.token(refresh=False)
        lim = ig._api("GET", f"{acc['user_id']}/content_publishing_limit", tok, fields="quota_usage,config")
        d = (lim.get("data") or [{}])[0]
        me = ig._api("GET", "me", tok, fields="followers_count,media_count,username")
        return {"source": "measured", "unit": "posts / 24 h", "used": d.get("quota_usage"),
                "limit": (d.get("config") or {}).get("quota_total"),
                "login_expires": time.strftime("%Y-%m-%d", time.gmtime(float(acc.get("expires_at", 0)))),
                "followers": me.get("followers_count"), "media": me.get("media_count")}
    except Exception as e:  # noqa: BLE001
        return {"source": "unavailable", "why": str(e)[:200]}


def youtube() -> dict:
    try:
        from .publish.youtube import access_token
        tok = access_token()
        c = requests.get("https://www.googleapis.com/youtube/v3/channels", params={"part": "statistics", "mine": "true"},
                         headers={"Authorization": f"Bearer {tok}"}, timeout=30).json()
        st = ((c.get("items") or [{}])[0]).get("statistics") or {}
        return {"source": "measured", "login": "ok", "subscribers": int(st.get("subscriberCount") or 0),
                "views": int(st.get("viewCount") or 0), "videos": int(st.get("videoCount") or 0),
                "quota_note": "YouTube doesn't report quota use to the API (10,000 units/day); see Google Cloud console"}
    except Exception as e:  # noqa: BLE001
        return {"source": "unavailable", "why": str(e)[:200]}


# ---------------- status, forecasts, alerts ----------------

def status_of(pct_left: float | None, days_left: float | None, expired: bool = False) -> str:
    if expired:
        return "Expired"
    if (pct_left is not None and pct_left < 10) or (days_left is not None and days_left < 3):
        return "Critical"
    if (pct_left is not None and pct_left < 25) or (days_left is not None and days_left < 7):
        return "Running low"
    return "Healthy"


def _burn(state, service: str, field: str = "left", days: float = 7.0) -> float | None:
    """Units used per day, from the change in the measured balance over the last `days` (ignores top-ups)."""
    rows = [json.loads(r["data"]) | {"_at": r["at"]} for r in state.db.execute(
        "SELECT data, at FROM resources WHERE service=? AND at>=? ORDER BY at", (service, time.time() - days * 86400))]
    rows = [r for r in rows if isinstance(r.get(field), (int, float))]
    if len(rows) < 2:
        return None
    used, span = 0.0, (rows[-1]["_at"] - rows[0]["_at"]) / 86400
    for a, b in zip(rows, rows[1:]):
        if b[field] < a[field]:
            used += a[field] - b[field]
    return used / span if span >= 0.25 else None


def check(state, notify_fn=None) -> dict:
    """Snapshot every service, add status + forecasts, store, and alert (once a day per problem)."""
    man = manual(state)
    snap = {
        "elevenlabs": elevenlabs(os.environ.get("ELEVENLABS_API_KEY", "")),
        "bfl": bfl(os.environ.get("BFL_API_KEY", "")),
        "anthropic": anthropic(state, man),
        "github": github_minutes(state),
        "instagram": instagram(),
        "youtube": youtube(),
    }
    with state.tx() as db:
        for k, v in snap.items():
            if v.get("source") != "unavailable":
                db.execute("INSERT INTO resources(service, data, at) VALUES (?,?,?)", (k, json.dumps(v), time.time()))
        if snap["instagram"].get("followers") is not None:
            db.execute("INSERT OR REPLACE INTO ig_account_daily(day, data, at) VALUES (?,?,?)",
                       (time.strftime("%Y-%m-%d", time.gmtime()), json.dumps(
                           {"followers": snap["instagram"]["followers"], "media": snap["instagram"]["media"]}),
                        time.time()))
    # per-video consumption (for "videos left")
    vids = [r["job_id"] for r in state.db.execute(
        "SELECT job_id FROM uploads WHERE video_id IS NOT NULL AND at>=?", (time.time() - 30 * 86400,))]
    per_video = {}
    if vids:
        q = ",".join("?" * len(vids))
        for prov, col in (("elevenlabs", "quantity"), ("bfl", "usd"), ("anthropic", "usd")):
            tot = state.db.execute(f"SELECT COALESCE(SUM({col}),0) s FROM costs WHERE provider=? AND job_id IN ({q})",
                                   (prov, *vids)).fetchone()["s"]
            per_video[prov] = tot / len(vids)
    out = {}
    plan_per_day = float(((man.get("plan") or {}).get("production") or {}).get("videos_per_day") or 1)
    for k, v in snap.items():
        item = {**v, "link": LINKS.get(k)}
        pct = days = None
        if isinstance(v.get("left"), (int, float)) and isinstance(v.get("limit"), (int, float)) and v["limit"]:
            pct = 100 * v["left"] / v["limit"]
        if k == "elevenlabs" and v.get("source") == "measured":
            pv = per_video.get("elevenlabs")
            if pv:
                item["videos_left"] = int(v["left"] // pv)
                item["per_video"] = round(pv)
                days = item["videos_left"] / plan_per_day
        if k == "bfl" and v.get("source") == "measured":
            pv = per_video.get("bfl")
            if pv:
                item["videos_left"] = int(v["usd_left"] // pv)
                item["per_video_usd"] = round(pv, 2)
                days = item["videos_left"] / plan_per_day
        if k == "anthropic" and isinstance(v.get("left_usd"), (int, float)):
            pv = per_video.get("anthropic")
            if pv:
                item["videos_left"] = int(v["left_usd"] // pv)
                item["per_video_usd"] = round(pv, 2)
                days = item["videos_left"] / plan_per_day
        if k == "github" and v.get("source") == "measured":
            burn = _gh_burn(state)
            if burn:
                item["per_day"] = round(burn)
                days = v["left"] / burn if burn else None
                item["runs_out"] = (dt.date.today() + dt.timedelta(days=max(0, days))).isoformat() if days else None
        b = _burn(state, k) if k in ("elevenlabs", "bfl") else None
        if b:
            item["burn_per_day"] = round(b, 1)
        item["days_left"] = round(days, 1) if days is not None else None
        expired = (k == "elevenlabs" and v.get("plan_status") in ("past_due", "free_disabled")) or v.get("open_invoices")
        item["status"] = "Unknown" if v.get("source") == "unavailable" else status_of(pct, days, bool(expired))
        out[k] = item
    # subscriptions typed in by the owner (Claude, anything else)
    for name, sub in (man.get("subscriptions") or {}).items():
        renew = sub.get("renews")
        d = None
        if renew:
            try:
                d = (dt.date.fromisoformat(renew) - dt.date.today()).days
            except ValueError:
                d = None
        out[f"sub:{name}"] = {"source": "manual", "updated": sub.get("at"), "usd_month": sub.get("usd_month"),
                              "renews": renew, "days_left": d, "share_pct": sub.get("share_pct"),
                              "status": "Expired" if d is not None and d < 0 else ("Running low" if d is not None and d <= 7
                                                                                   else "Healthy"),
                              "link": LINKS.get(name)}
    _alerts(state, out, notify_fn)
    state.set_setting("resources_json", json.dumps({"at": _now_iso(), "items": out}))
    return out


def _gh_burn(state) -> float | None:
    rows = state.db.execute("SELECT SUM(MAX(COALESCE(billable_ms,0), COALESCE(duration_ms,0))) b FROM gh_runs "
                            "WHERE created >= ?",
                            (time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(time.time() - 7 * 86400)),)).fetchone()
    return (rows["b"] or 0) / 60000 / 7 if rows and rows["b"] else None


def _alerts(state, items: dict, notify_fn) -> None:
    if notify_fn is None:
        return
    day = time.strftime("%Y-%m-%d", time.gmtime(time.time() + 5.5 * 3600))
    bad = [(k, v) for k, v in items.items() if v.get("status") in ("Critical", "Expired", "Running low")]
    lines = []
    for k, v in bad:
        key = f"alert:{k}:{v['status']}"
        if state.get_setting(key) == day:
            continue
        state.set_setting(key, day)
        bits = [v["status"]]
        if v.get("left") is not None and v.get("limit"):
            bits.append(f"{v['left']:,} of {v['limit']:,} {v.get('unit', '')} left")
        if v.get("videos_left") is not None:
            bits.append(f"≈{v['videos_left']} videos left")
        if v.get("days_left") is not None:
            bits.append(f"≈{v['days_left']} days")
        if v.get("renews"):
            bits.append(f"renews {v['renews']}")
        lines.append(f"• {k.replace('sub:', '')}: " + ", ".join(bits) + (f" — {v['link']}" if v.get("link") else ""))
    if lines:
        notify_fn("⚠️ Resources that need attention:\n" + "\n".join(lines))


# ---------------- near-real-time per-video counts + Instagram account totals ----------------

def youtube_live(state) -> dict:
    """View/like/comment counts straight from the YouTube Data API (minutes old; 1 quota unit per 50 videos).
    The Analytics API numbers (watch time, retention) lag 1-2 days, so new videos show these first."""
    ids = [r["video_id"] for r in state.db.execute("SELECT video_id FROM uploads WHERE video_id IS NOT NULL")]
    if not ids:
        return {}
    from .publish.youtube import access_token
    tok = access_token()
    out = {}
    for i in range(0, len(ids), 50):
        r = requests.get("https://www.googleapis.com/youtube/v3/videos", headers={"Authorization": f"Bearer {tok}"},
                         params={"part": "statistics", "id": ",".join(ids[i:i + 50])}, timeout=30).json()
        for v in r.get("items") or []:
            s = v.get("statistics") or {}
            out[v["id"]] = {"views": int(s.get("viewCount") or 0), "likes": int(s.get("likeCount") or 0),
                            "comments": int(s.get("commentCount") or 0), "at": _now_iso()}
    state.set_setting("yt_live_json", json.dumps(out))
    return {"videos": len(out)}


def instagram_account_day(state) -> dict:
    """Yesterday's account totals (reach, views, interactions, link taps, accounts engaged)."""
    from .publish import instagram as ig
    tok, acc = ig.token(refresh=False)
    y = dt.datetime.now(dt.timezone.utc).date() - dt.timedelta(days=1)
    since = int(dt.datetime(y.year, y.month, y.day, tzinfo=dt.timezone.utc).timestamp())
    got = {}
    for m in ("reach", "views", "accounts_engaged", "total_interactions", "profile_links_taps"):
        try:
            r = ig._api("GET", f"{acc['user_id']}/insights", tok, metric=m, period="day", metric_type="total_value",
                        since=since, until=since + 86400)
            for x in r.get("data") or []:
                got[m] = (x.get("total_value") or {}).get("value")
        except Exception:  # noqa: BLE001
            got[m] = None
    row = state.db.execute("SELECT data FROM ig_account_daily WHERE day=?", (y.isoformat(),)).fetchone()
    data = {**(json.loads(row["data"]) if row else {}), **{k: v for k, v in got.items() if v is not None}}
    with state.tx() as db:
        db.execute("INSERT OR REPLACE INTO ig_account_daily(day, data, at) VALUES (?,?,?)",
                   (y.isoformat(), json.dumps(data), time.time()))
    return got
