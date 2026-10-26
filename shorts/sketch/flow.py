"""The daily sketch loop: write -> voice -> animate -> check -> owner review (Telegram) -> fix -> approve ->
private upload scheduled at the episode's slot.

Nothing is ever published without the owner's approval. Uploads go up private with a publishAt time;
YouTube makes them public at that time.
"""
from __future__ import annotations

import datetime as dt
import json
import os
import shutil
import subprocess
import sys
import zipfile
from pathlib import Path

from shorts import notify
from shorts.providers.llm import AnthropicLLM

from . import director as D
from . import episodes as E
from . import qa as Q
from . import voices as V
from . import world as Wd
from . import writer as Wr

ROOT = Path(__file__).resolve().parents[2]
RELEASE = "episodes"                      # GitHub release that keeps every rendered version
MAX_LIVE = E.LEAD_DAYS + 1                # never more than this many episodes waiting at once
TEMPO_FAST = 1.12


def gh(*args: str, check: bool = True) -> str:
    return subprocess.run(["gh", *args], capture_output=True, text=True, check=check).stdout.strip()


def _llm(p):
    cfg = dict(p.cfg.pipeline["providers"]["llm"])
    cfg.setdefault("prices", {})
    cfg["prices"].setdefault("claude-opus-5-5", [4.0, 20.0])
    cfg["prices"].setdefault("claude-sonnet-5-5", [2.0, 10.0])
    return AnthropicLLM(os.environ["ANTHROPIC_API_KEY"], cfg)


def _voices(plan: dict | None = None) -> dict:
    return Wd.voices_for(plan or {})


def prepare_art(p, ep: dict, plan: dict, llm) -> dict:
    """Draw whatever new art the story asked for (set, poses, one on-screen person) and fix every new person's
    voice. Anything that can't be drawn is taken out and the episode is restaged without it."""
    from . import art as A
    lib = D.library()
    w = Wd.register_new(plan, ep_id=ep["id"])
    failed, made = [], []
    for c in plan.get("new_characters", []):
        cid = c.get("id")
        if not cid or cid in lib["characters"] or not c.get("on_screen"):
            continue
        rec = w["characters"].setdefault(cid, {"name": c.get("name", cid), "pending": ep["id"]})
        rec.update(name=c.get("name", cid), desc=c.get("desc", ""), relations=c.get("relations", {}),
                   voice_type=c.get("voice_type", ""), look=c.get("look", ""))
        rec["voice"] = rec.get("voice") or Wd.cast_voice(cid, c.get("voice_type", ""), w)
        ok = False
        try:
            ok = A.generate_character(p, cid, c.get("name", cid), c.get("desc", ""), c.get("look", ""),
                                      float(c.get("height") or 0.95), rec["voice"])
        except Exception as e:  # noqa: BLE001
            p.state.log(f"character {cid}: {e}", "warn")
        if ok:
            rec["drawn"] = True
            made.append(f"new character {c.get('name', cid)}")
        else:
            c["on_screen"] = False
            failed.append(f"{c.get('name', cid)} could not be drawn, so {cid} is VOICE-ONLY now (phone call or a voice "
                          "from another room; not in any shot's cast)")
    Wd.save(w)
    Wd.commit(f"World: characters for {ep['id']}")
    for x in plan.get("new_sets", [])[:1]:
        if x.get("id") in D.library()["sets"]:
            continue
        ok = False
        try:
            ok = A.generate_set(p, x["id"], x.get("desc", ""), x.get("desc", "")[:120])
        except Exception as e:  # noqa: BLE001
            p.state.log(f"set {x.get('id')}: {e}", "warn")
        if ok:
            made.append(f"new place {x['id']}")
        else:
            failed.append(f"the place {x['id']} could not be drawn; use an existing set")
            plan["new_sets"] = [y for y in plan["new_sets"] if y is not x]
    for x in list(plan.get("new_poses", []))[:2]:
        if x.get("id") in D.rig()["figures"]:
            continue
        ok = False
        try:
            ok = A.generate_pose(p, x.get("who", ""), x["id"], x.get("desc", ""))
        except Exception as e:  # noqa: BLE001
            p.state.log(f"pose {x.get('id')}: {e}", "warn")
        if ok:
            made.append(f"new pose {x['id']}")
        else:
            failed.append(f"the pose {x['id']} could not be drawn; use existing poses")
            plan["new_poses"] = [y for y in plan["new_poses"] if y is not x]
    if made:
        E.log(ep, "art", ", ".join(made))
    if failed:
        note = ("Some new art could not be made: " + "; ".join(failed) + ". Restage the episode without it. Keep "
                "the story, the lines and the jokes exactly where possible.")
        E.log(ep, "art_failed", note)
        plan, _s, c = Wr.revise(llm, _only_existing(plan), note, _history(p, ep["id"]), _feedback(p))
        cost = [c]
        plan = Wr._fix_loop(llm, _only_existing(plan), Wr._system(), cost)
        _cost(p, ep, "restage", cost[0])
    return plan


def _only_existing(plan: dict) -> dict:
    """Keep only new-art requests that now exist in the library (so nothing missing reaches the renderer)."""
    lib, rg = D.library(), D.rig()
    plan = dict(plan)
    plan["new_sets"] = [x for x in plan.get("new_sets", []) if x.get("id") in lib["sets"]]
    plan["new_poses"] = [x for x in plan.get("new_poses", []) if x.get("id") in rg["figures"]]
    plan["new_characters"] = [{**c, "on_screen": bool(c.get("on_screen")) and c.get("id") in lib["characters"]}
                              for c in plan.get("new_characters", [])]
    return plan


def _feedback(p) -> list[dict]:
    rows = p.state.db.execute("SELECT decision, note FROM feedback WHERE job_id LIKE 'ep%' ORDER BY id").fetchall()
    return [dict(r) for r in rows]


def _history(p, exclude: str = "") -> list[dict]:
    pilot = [{"number": 1, "title": "The Haircut", "premise": "Dev can't tell Rocky his haircut is a disaster; "
              "asks for 'thoda kam', gets worse; tells Meera he'll get it fixed tomorrow - by Rocky."}]
    return pilot + [e for e in E.all_eps(p.state) if e["id"] != exclude and e["status"] != "failed"]


MAX_ASSETS = 950          # GitHub allows 1000 files per release (no total-size limit); roll over before that


def _release_tags() -> list[str]:
    out = gh("release", "list", "--limit", "200", "--json", "tagName", "-q", ".[].tagName", check=False)
    tags = [t for t in out.splitlines() if t == RELEASE or t.startswith(RELEASE + "-")]
    return sorted(tags, key=lambda t: int(t.split("-")[-1]) if t != RELEASE else 1)


def _current_release(extra: int) -> str:
    tags = _release_tags()
    tag = tags[-1] if tags else RELEASE
    if tags:
        n = int(gh("release", "view", tag, "--json", "assets", "-q", ".assets | length", check=False) or 0)
        if n + extra > MAX_ASSETS:
            tag = f"{RELEASE}-{len(tags) + 1}"
            tags = []
    if not tags or tag not in tags:
        if subprocess.run(["gh", "release", "view", tag], capture_output=True).returncode != 0:
            gh("release", "create", tag, "--prerelease", "--title", f"Episode renders ({tag})",
               "--notes", "Every rendered version of every episode (kept for revisions and uploads).")
    return tag


def _put(files: list[Path]) -> str:
    tag = _current_release(len(files))
    gh("release", "upload", tag, *[str(f) for f in files], "--clobber")
    return tag


def _get(name: str, into: Path) -> Path | None:
    """name may be 'tag/file' or a bare file name (searched in every episodes release, newest first)."""
    into.mkdir(parents=True, exist_ok=True)
    tags = [name.split("/", 1)[0]] if "/" in name else list(reversed(_release_tags()))
    fname = name.split("/", 1)[-1]
    for tag in tags:
        r = subprocess.run(["gh", "release", "download", tag, "-p", fname, "-D", str(into), "--clobber"],
                           capture_output=True, text=True)
        if r.returncode == 0:
            return into / fname
    return None


def _spent_month(p) -> float:
    start = dt.datetime.now(dt.timezone.utc).replace(day=1, hour=0, minute=0, second=0, microsecond=0).timestamp()
    return p.state.spend_since(start)


def _budget_ok(p) -> tuple[bool, str]:
    b = p.cfg.pipeline.get("budget_usd", {})
    spent = _spent_month(p)
    cap = float(b.get("monthly", 45))
    return (spent + 1.0 <= cap, f"${spent:.2f} of ${cap:.2f} this month")


# ----------------------------------------------------------------------------- rendering
def render(p, ep: dict, plan: dict, work: Path) -> dict:
    """Voices + animation + mix + checks for `plan`. Returns info for the review message."""
    lines_dir, shots_dir, cache = work / "lines", work / "shots", work / "voice_cache"
    for d in (lines_dir, shots_dir):
        shutil.rmtree(d, ignore_errors=True)
    cache.mkdir(parents=True, exist_ok=True)
    # reuse earlier takes of unchanged lines
    z = _get(f"{ep['id']}-voices.zip", work / "dl")
    if z:
        with zipfile.ZipFile(z) as f:
            f.extractall(cache)
    fake = p.cfg.pipeline.get("mode") != "live"
    key = os.environ.get("ELEVENLABS_API_KEY", "")
    cost = 0.0
    llm = _llm(p) if not fake else None
    tempo = 1.08
    for attempt in range(3):
        vr = V.make(plan["lines"], _voices(plan), cache, lines_dir, key, tempo=tempo, fake=fake)
        cost += vr["usd"]
        scene, asm = D.build(plan, lines_dir, shots_dir, ep["id"], seed=ep["number"])
        total = D.total_seconds(scene)
        if total <= 46.5:
            break
        if total <= 50 and tempo < TEMPO_FAST:
            tempo = TEMPO_FAST                       # a touch faster is invisible; try that first
            continue
        if attempt == 2 or llm is None:
            break
        plan, c = Wr.shorten(llm, plan, total, vr["seconds"])
        cost += c
        tempo = 1.08
    (work / "scene.json").write_text(json.dumps(scene, ensure_ascii=False, indent=1))
    (work / "assemble.json").write_text(json.dumps(asm, ensure_ascii=False, indent=1))
    subprocess.run([sys.executable, str(ROOT / "scripts" / "puppet" / "puppet.py"), str(D.RIG),
                    str(work / "scene.json"), str(shots_dir)], check=True)
    r = subprocess.run([sys.executable, str(ROOT / "scripts" / "sketch_assemble.py"), str(work / "assemble.json")],
                       capture_output=True, text=True)
    if r.returncode != 0:
        raise RuntimeError("assembly failed: " + r.stderr[-800:])
    built = ROOT / "build" / ep["id"] / "final.mp4"
    ver = int(ep.get("version") or 0) + 1
    final = work / f"{ep['id']}-v{ver}.mp4"
    subprocess.run(["ffmpeg", "-loglevel", "error", "-y", "-i", str(built), "-c:v", "copy", "-af",
                    "aresample=192000,alimiter=limit=0.70:level=false:attack=1:release=50,aresample=48000",
                    "-c:a", "aac", "-b:a", "192k", "-movflags", "+faststart", str(final)], check=True)
    tl = json.loads((ROOT / "build" / ep["id"] / "timeline.json").read_text())
    tech = Q.technical(final)
    sheet = Q.contact_sheet(final, tl["starts"], tl["durs"], work / f"{ep['id']}-v{ver}-sheet.png")
    vis = {"ok": True, "issues": []}
    if llm is not None:
        try:
            vis, c = Q.vision(llm, sheet, sum(1 for s in plan["shots"] if s["type"] == "black"))
            cost += c
        except Exception as e:  # noqa: BLE001
            vis = {"ok": True, "issues": [f"(visual check unavailable: {str(e)[:80]})"]}
    # keep voices for later revisions
    zp = work / f"{ep['id']}-voices.zip"
    with zipfile.ZipFile(zp, "w") as f:
        for m in cache.glob("*.mp3"):
            f.write(m, m.name)
    tag = _put([final, zp, sheet])
    return {"plan": plan, "version": ver, "video": final, "asset": f"{tag}/{final.name}", "seconds": tech["seconds"],
            "qa": {"tech": tech, "visual": vis}, "cost": cost}


# ----------------------------------------------------------------------------- owner messages
def _review_text(ep: dict, info: dict, summary: str = "") -> str:
    m = ep.get("meta") or {}
    issues = info["qa"]["tech"]["issues"] + info["qa"]["visual"]["issues"]
    out = [f"🎬 <b>Ep {ep['number']} · v{info['version']}</b>: {notify.esc(m.get('title') or ep.get('title') or '')}",
           f"Goes live <b>{E.fmt_ist(ep['slot'])}</b> if approved.",
           f"{info['seconds']:.0f}s · cost so far ${float(ep.get('cost') or 0):.2f}"]
    if summary:
        out.append(f"Changed: {notify.esc(summary)}")
    out.append("Auto-check: " + ("✅ no problems found" if not issues else "⚠️ " + notify.esc("; ".join(issues)[:300])))
    out.append(f"<code>job:{ep['id']}</code>")
    return "\n".join(out)


def _send_review(p, ep: dict, info: dict, summary: str = "") -> None:
    text = _review_text(ep, info, summary)
    if ep.get("hold"):                     # checked by Claude first; sent later with the send_review action
        msg = None
        E.log(ep, "held", "waiting for a check before it goes to the owner")
    else:
        msg = notify.send_video(p.state, info["video"], text, notify.review_buttons(ep["id"]))
    m = ep.get("meta") or {}
    body = (text.replace("<b>", "**").replace("</b>", "**").replace("<code>", "`").replace("</code>", "`")
            + f"\n\nVideo file (GitHub release): `{info["asset"]}`\n\n**Title:** {m.get('title')}\n\n"
            f"**Description:**\n{m.get('description')}\n\n**Tags:** {', '.join(m.get('tags') or [])}\n\n"
            "**Script:**\n" + "\n".join(f"- {ln['who']}: {ln['cap']}".replace("\n", " ") for ln in info["plan"]["lines"])
            + f"\n\n<!-- job:{ep['id']} -->")
    gh("label", "create", "review", "--color", "0E8A16", check=False)
    existing = gh("issue", "list", "--label", "review", "--state", "open", "--search", f"job:{ep['id']} in:body",
                  "--json", "number", "-q", ".[0].number", check=False)
    if existing:
        gh("issue", "comment", existing, "--body", body, check=False)
    else:
        gh("issue", "create", "--label", "review", "--title", f"Review Ep {ep['number']}: {m.get('title', '')}"[:120],
           "--body", body, check=False)
    if not msg and not ep.get("hold"):
        p.state.log(f"{ep['id']}: Telegram not configured, review posted as a GitHub issue", "warn")


def send_review(p, req: dict) -> int:
    """Send a held episode to the owner's Telegram (after it was checked)."""
    ep = E.get(p.state, req["job"])
    if not ep or not ep.get("video_asset"):
        return 1
    video = _get(ep["video_asset"], ROOT / "build" / "send")
    if not video:
        return 1
    ep.pop("hold", None)
    E.save(p.state, ep)
    qa = ep.get("qa") or {"tech": {"issues": []}, "visual": {"issues": []}}
    info = {"video": video, "version": ep["version"], "seconds": float((qa.get("tech") or {}).get("seconds") or 0),
            "qa": qa, "asset": ep["video_asset"], "plan": ep["plan"]}
    text = _review_text(ep, info, req.get("note", ""))
    notify.send_video(p.state, video, text, notify.review_buttons(ep["id"]))
    return 0


def _fail(p, ep: dict, stage: str, err: Exception) -> None:
    ep["status"] = "failed" if stage == "write" else ep.get("status", "review")
    E.log(ep, "error", f"{stage}: {err}")
    E.save(p.state, ep)
    text = f"⚠️ Ep {ep['number']} ({stage}) failed: {str(err)[:300]}\nI'll retry on the next daily run."
    notify.send(p.state, text)
    gh("issue", "create", "--label", "alert", "--title", f"Episode {ep['id']} {stage} failed", "--body", text[:3000], check=False)


# ----------------------------------------------------------------------------- actions
def _clear_stale(p) -> None:
    """Episodes left half-made by a crashed or cancelled run are marked failed so they don't block the queue."""
    import time as _t
    for ep in E.all_eps(p.state, ("writing", "revising")):
        if _t.time() - float(ep.get("updated") or 0) > 3 * 3600:
            ep["status"] = "failed" if ep["status"] == "writing" else "review"
            E.log(ep, "stale", "run did not finish")
            E.save(p.state, ep)


def produce(p, req: dict) -> int:
    E.init(p.state)
    _clear_stale(p)
    live = E.pipeline_days_covered(p.state)
    if live >= MAX_LIVE and not req.get("force"):
        print(f"{live} episodes already waiting; nothing to make today")
        return 0
    ok, why = _budget_ok(p)
    if not ok:
        notify.send(p.state, f"⏸ Budget reached ({why}). No new episode today.")
        return 0
    number = E.next_number(p.state)
    ep = {"id": f"ep{number:03d}", "number": number, "status": "writing", **({"hold": True} if req.get("hold") else {}),
          "slot": E.next_free_slot(p.state).isoformat().replace("+00:00", "Z"), "version": 0, "cost": 0.0}
    E.log(ep, "start", req.get("idea", ""))
    E.save(p.state, ep)
    work = ROOT / "build" / "work" / ep["id"]
    work.mkdir(parents=True, exist_ok=True)
    try:
        llm = _llm(p)
        plan, c = Wr.write(llm, _history(p, ep["id"]), _feedback(p), number, req.get("idea", ""))
        _cost(p, ep, "script", c)
        ep.update(plan=plan, title=plan.get("title_idea"), premise=plan.get("premise"))
        E.save(p.state, ep)
        plan = prepare_art(p, ep, plan, llm)
        ep["plan"] = plan
        E.save(p.state, ep)
    except Exception as e:  # noqa: BLE001
        _fail(p, ep, "write", e)
        return 1
    return _finish_version(p, ep, plan, work)


def _has_job_arg(p) -> bool:
    import inspect
    return "job_id" in inspect.signature(p.state.add_cost).parameters


def _cost(p, ep: dict, what: str, usd: float) -> None:
    if usd <= 0:
        return
    if _has_job_arg(p):
        p.state.add_cost("sketch", f"{ep['id']} {what}", 1, usd, job_id=ep["id"])
    else:
        p.state.add_cost("sketch", f"{ep['id']} {what}", 1, usd)
    ep["cost"] = float(ep.get("cost") or 0) + usd


def _finish_version(p, ep: dict, plan: dict, work: Path, summary: str = "") -> int:
    try:
        info = render(p, ep, plan, work)
    except Exception as e:  # noqa: BLE001
        _fail(p, ep, "render", e)
        return 1
    _cost(p, ep, f"v{info['version']} voices+checks", info["cost"])
    if not ep.get("meta") or (summary and [l["cap"] for l in info["plan"]["lines"]] != [l["cap"] for l in (ep.get("plan") or {}).get("lines", [])]):
        try:
            meta, c = Wr.metadata(_llm(p), info["plan"], ep["number"])
            _cost(p, ep, "metadata", c)
            ep["meta"] = meta
        except Exception as e:  # noqa: BLE001
            ep.setdefault("meta", {"title": f"{plan.get('title_idea', 'Sab Theek Hai')} | Sab Theek Hai",
                                   "description": plan.get("premise", ""), "hashtags": ["#SabTheekHai"], "tags": []})
            E.log(ep, "warn", f"metadata: {e}")
    ep.update(plan=info["plan"], version=info["version"], video_asset=info["asset"], qa=info["qa"], status="review",
              title=(ep.get("meta") or {}).get("title") or ep.get("title"))
    E.log(ep, "review", f"v{info['version']} {summary}")
    E.save(p.state, ep)
    _send_review(p, ep, info, summary)
    return 0


def fix(p, req: dict) -> int:
    ep = E.get(p.state, req["job"])
    note = (req.get("note") or "").strip()
    if not ep or not note:
        notify.send(p.state, "I couldn't find that episode or the note was empty.")
        return 1
    if ep["status"] in ("scheduled", "published"):
        notify.send(p.state, f"Ep {ep['number']} is already uploaded. Changes now would need a re-upload; tell me if you want that.")
        return 0
    p.state.add_feedback(ep["id"], "fix", note)
    ep["status"] = "revising"
    E.log(ep, "fix", note)
    E.save(p.state, ep)
    work = ROOT / "build" / "work" / ep["id"]
    work.mkdir(parents=True, exist_ok=True)
    try:
        llm = _llm(p)
        plan, summary, c = Wr.revise(llm, ep["plan"], note, _history(p, ep["id"]), _feedback(p))
        _cost(p, ep, "revision script", c)
        plan = prepare_art(p, ep, plan, llm)
    except Exception as e:  # noqa: BLE001
        ep["status"] = "review"
        _fail(p, ep, "revise", e)
        return 1
    return _finish_version(p, ep, plan, work, summary or "as requested")


def rerender(p, req: dict) -> int:
    """Re-render an episode's current plan with the latest animation engine (voices reused, no AI cost)."""
    ep = E.get(p.state, req["job"])
    if not ep or not ep.get("plan"):
        return 1
    work = ROOT / "build" / "work" / ep["id"]
    work.mkdir(parents=True, exist_ok=True)
    return _finish_version(p, ep, ep["plan"], work, req.get("note") or "animation improved, same script")


def reject(p, req: dict) -> int:
    ep = E.get(p.state, req["job"])
    if not ep:
        return 1
    p.state.add_feedback(ep["id"], "reject", req.get("note", ""))
    ep["status"] = "rejected"
    E.log(ep, "rejected", req.get("note", ""))
    E.save(p.state, ep)
    try:
        Wd.forget_pending(ep["id"])
        Wd.commit(f"World: forget characters from dropped {ep['id']}")
    except Exception as e:  # noqa: BLE001
        p.state.log(f"world forget: {e}", "warn")
    notify.send(p.state, f"🗑 Ep {ep['number']} dropped. Making a replacement now; it will arrive here.")
    return produce(p, {"force": True, "hold": req.get("hold", False)})


def approve(p, req: dict) -> int:
    from shorts.publish.youtube import VideoMeta, upload
    ep = E.get(p.state, req["job"])
    if not ep:
        return 1
    if ep["status"] in ("scheduled", "published") and ep.get("yt_video_id"):
        notify.send(p.state, f"ℹ️ Ep {ep['number']} is already uploaded: https://youtube.com/shorts/{ep['yt_video_id']}")
        return 0
    slot = dt.datetime.fromisoformat(ep["slot"].replace("Z", "+00:00"))
    if slot < dt.datetime.now(dt.timezone.utc) + dt.timedelta(minutes=45):
        slot = E.next_free_slot(p.state, earliest=dt.datetime.now(dt.timezone.utc))
        ep["slot"] = slot.isoformat().replace("+00:00", "Z")
    video = _get(ep["video_asset"], ROOT / "build" / "upload")
    if not video:
        notify.send(p.state, f"⚠️ I couldn't find the video file for Ep {ep['number']}.")
        return 1
    m = ep.get("meta") or {}
    ch = (p.cfg.channel or {}).get("channel", {})
    meta = VideoMeta(title=m.get("title", ""), description=m.get("description", ""), tags=m.get("tags", []),
                     category_id=str(ch.get("youtube_category_id", "23")), language="hi", made_for_kids=False,
                     contains_synthetic_media=False, publish_at=ep["slot"])
    try:
        res = upload(p.state, ep["id"], video, meta)
    except Exception as e:  # noqa: BLE001
        notify.send(p.state, f"⚠️ Upload of Ep {ep['number']} failed: {str(e)[:300]}")
        E.log(ep, "upload_error", str(e))
        E.save(p.state, ep)
        return 1
    ep.update(status="scheduled", yt_video_id=res.get("video_id"))
    E.log(ep, "scheduled", ep["slot"])
    E.save(p.state, ep)
    p.state.add_feedback(ep["id"], "approve", "")
    try:                                            # remember what this episode established, for continuity
        c = Wd.learn(_llm(p), ep["plan"], ep["number"], ep["id"])
        _cost(p, ep, "world memory", c)
        E.save(p.state, ep)
        Wd.commit(f"World: learn from {ep['id']}")
    except Exception as e:  # noqa: BLE001
        p.state.log(f"world learn: {e}", "warn")
    pin = m.get("pinned_comment")
    notify.send(p.state, f"✅ Ep {ep['number']} uploaded (private). It goes public <b>{E.fmt_ist(ep['slot'])}</b>.\n"
                f"{res.get('url')}" + (f"\n\nOptional pinned comment:\n{notify.esc(pin)}" if pin else ""))
    return 0


def daily(p, req: dict) -> int:
    """Morning run: chase reviews that are getting close to their slot, then make the next episode."""
    E.init(p.state)
    now = dt.datetime.now(dt.timezone.utc)
    for ep in E.all_eps(p.state, ("review",)):
        slot = dt.datetime.fromisoformat(ep["slot"].replace("Z", "+00:00"))
        left = (slot - now).total_seconds() / 3600
        if left < 2:
            new = E.next_free_slot(p.state, earliest=now + dt.timedelta(hours=3))
            ep["slot"] = new.isoformat().replace("+00:00", "Z")
            E.log(ep, "moved", "not approved in time")
            E.save(p.state, ep)
            notify.send(p.state, f"⏰ Ep {ep['number']} wasn't approved in time, so it did NOT go out. "
                        f"New slot: {E.fmt_ist(ep['slot'])}. It's still waiting above for your review.")
        elif left < 30:
            notify.send(p.state, f"⏰ Reminder: Ep {ep['number']} goes live {E.fmt_ist(ep['slot'])} only if you approve it. "
                        "Scroll up to the video and tap ✅ or ✏️.")
    for ep in E.all_eps(p.state, ("scheduled",)):
        slot = dt.datetime.fromisoformat(ep["slot"].replace("Z", "+00:00"))
        if slot < now:
            ep["status"] = "published"
            E.save(p.state, ep)
    # grow the set library: weekly, or faster while the show has few places
    try:
        from . import grow as G
        from . import art as A
        if dt.datetime.now(E.IST).weekday() == 0 and A.weekly_spend(p.state) < 2.0:
            G.grow(p, 1)                             # stories ask for their own places; this is a small extra
    except Exception as e:  # noqa: BLE001
        p.state.log(f"library growth skipped: {e}", "warn")
    return produce(p, req)


def status(p) -> str:
    E.init(p.state)
    rows = []
    for ep in E.all_eps(p.state, ("writing", "review", "revising", "approved", "scheduled")):
        rows.append(f"Ep {ep['number']} · {ep['status']} · {E.fmt_ist(ep['slot'])} · {(ep.get('title') or '')[:40]}")
    ok, why = _budget_ok(p)
    return "\n".join(rows or ["Nothing in the queue."]) + f"\nSpend: {why}"
