"""The production pipeline: discovery -> scoring -> script -> independent review ->
voice -> visuals -> render -> QA -> packaging -> (owner approval) -> upload.

Every stage records its output in the State DB and on disk, so a crashed or
interrupted run resumes at the first unfinished stage without paying twice.
"""
from __future__ import annotations

import hashlib
import io
import json
import random
import re
import time
from pathlib import Path

from PIL import Image

from . import prompts as P
from .budget import Budget, BudgetExceeded, Limits
from .config import Config
from .qa.media import check_video
from .render import assemble as A
from .render.captions import write_ass
from .render.compose import Callout, Palette, Scene, render_scene
from .state import State
from .ytskill import hook_score, title_lint

STAGES = ["script", "review", "voice", "visuals", "render", "qa", "package"]


class StageFailed(RuntimeError):
    pass


# ---------------- helpers ----------------

def slug(text: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")[:48]


def _grams(text: str, n: int = 4) -> set[str]:
    t = re.sub(r"[^a-z0-9 ]", "", text.lower())
    t = re.sub(r"\b(why|do|does|is|are|the|a|an|have|has|there|of|on|in|so|what)\b", " ", t)
    t = re.sub(r"\s+", " ", t).strip()
    return {t[i:i + n] for i in range(max(0, len(t) - n + 1))}


def similarity(a: str, b: str) -> float:
    ga, gb = _grams(a), _grams(b)
    return len(ga & gb) / len(ga | gb) if ga and gb else 0.0


class Pipeline:
    def __init__(self, cfg: Config):
        self.cfg = cfg
        self.state = State(cfg.path("state_db"))
        b = cfg.pipeline["budget_usd"]
        self.budget = Budget(self.state, Limits(b["daily"], b["monthly"], b["per_video"]))
        self.build = cfg.path("build_dir")
        self.build.mkdir(parents=True, exist_ok=True)
        self.pal = Palette.from_cfg(cfg.channel["style"]["palette"])
        self._providers()

    # ---------- providers ----------
    def _providers(self) -> None:
        pc = self.cfg.pipeline["providers"]
        if self.cfg.live:
            from .providers.images import BFLImages
            from .providers.llm import AnthropicLLM
            from .providers.tts import ElevenLabsTTS
            self.llm = AnthropicLLM(self.cfg.secret("ANTHROPIC_API_KEY"), pc["llm"])
            v = self.cfg.channel["voice"]
            self.tts = ElevenLabsTTS(self.cfg.secret("ELEVENLABS_API_KEY"), v["voice_id"], v["model_id"],
                                     pc["tts"]["usd_per_1k_chars"])
            im = pc["images"]
            self.images = BFLImages(self.cfg.secret("BFL_API_KEY"), im["model"], im["width"], im["height"],
                                    im["usd_each"])
        else:
            from .providers.images import FakeImages
            from .providers.llm import FakeLLM
            from .providers.tts import FakeTTS
            self.llm, self.tts, self.images = FakeLLM(), FakeTTS(), FakeImages()

    def _llm(self, prompt: str, job_id: str | None, what: str, est: float = 0.05, **kw):
        if self.cfg.live:
            self.budget.authorize(est, what, job_id)
        r = self.llm.ask(prompt, **kw)
        if r.usd:
            self.state.add_cost("anthropic", what, 1, r.usd, job_id, estimated=False)
        return r

    # ---------- Stage A+B: discovery and scoring ----------
    def discover(self, n: int = 8, signals: list[dict] | None = None) -> list[str]:
        known = self.state.topics()
        avoid = "\n".join(f"- {t['title']}" for t in known[:200]) or "(none yet)"
        pillars = self.cfg.channel["pillars"]
        ins_path = self.cfg.root / "data" / "insights.json"
        if ins_path.exists():
            from .analytics import adjusted_pillar_shares
            pillars = adjusted_pillar_shares(pillars, json.loads(ins_path.read_text()))
        quotas = ", ".join(f"{p['id']}={max(1, round(p['share'] * n))}" for p in pillars)
        sig_path = self.cfg.root / "data" / "signals.json"
        if signals is None and sig_path.exists():
            signals = json.loads(sig_path.read_text()).get("outliers", [])
        covered_titles = self._competitor_titles()
        covered = "\n".join(f"- {t}" for t in covered_titles[:300]) or "(unknown)"
        sig = json.dumps((signals or [])[:30], ensure_ascii=False) if signals else "(none)"
        r = self._llm(P.IDEAS.format(n=n, quotas=quotas, avoid=avoid, covered=covered, signals=sig), None, "ideas",
                      system=P.SYSTEM_WRITER, model=self.cfg.pipeline["providers"]["llm"]["model_routine"])
        added = []
        for idea in (r.data or {}).get("ideas", []):
            q = idea.get("question", "").strip()
            if not q:
                continue
            dup = max((similarity(q, t["title"]) for t in self.state.topics()), default=0)
            comp = max((similarity(q, t) for t in covered_titles), default=0)
            if dup >= 0.5:
                self.state.log(f"skip duplicate idea ({dup:.2f}): {q}")
                continue
            tid = slug(idea.get("object", q))
            if self.state.get_topic(tid):
                tid = f"{tid}-{hashlib.md5(q.encode()).hexdigest()[:5]}"
            s = self._llm(P.SCORE.format(idea=json.dumps(idea)), None, "score",
                          model=self.cfg.pipeline["providers"]["llm"]["model_routine"], est=0.01)
            sc = s.data or {}
            total = float(sc.get("total", 0))
            if comp >= 0.55:   # a competitor covered it: only worth doing with a clearly better angle
                total -= 15
                sc["competitor_overlap"] = round(comp, 2)
            policy = float((sc.get("scores") or {}).get("policy", 0))
            status = "shortlisted" if total >= 65 and policy >= 8 else "discovered"
            if policy < 6:
                status = "rejected"
            self.state.upsert_topic(
                tid, q, pillar=idea.get("pillar"), status=status, score=total,
                score_detail=sc, evidence=[{"source": "llm-ideas", "signals_used": bool(signals),
                                            "seen_at": time.time(), "confidence": "medium"}],
                notes=json.dumps(idea))
            added.append(tid)
        self.state.log(f"discovery added {len(added)} topics")
        return added

    def _competitor_titles(self) -> list[str]:
        p = self.cfg.root / "data" / "signals.json"
        if not p.exists():
            return []
        return [v["title"] for v in json.loads(p.read_text()).get("all_titles", [])]

    def next_topic(self) -> dict | None:
        for status in ("approved", "shortlisted"):
            ts = self.state.topics(status)
            if ts:
                return ts[0]
        return None

    # ---------- production ----------
    def produce(self, topic_id: str) -> str:
        topic = self.state.get_topic(topic_id)
        if not topic:
            raise KeyError(topic_id)
        job_id = f"{topic_id}-v1"
        job = self.state.start_job(job_id, topic_id)
        if job["status"] in ("review", "approved", "published"):
            return job_id
        self.state.set_topic_status(topic_id, "in_production")
        self.state.set_job_status(job_id, "running")
        d = self.build / job_id
        d.mkdir(parents=True, exist_ok=True)
        done = job["stage"]
        start = STAGES.index(done) + 1 if done in STAGES else 0
        for stage in STAGES[start:]:
            try:
                arts = getattr(self, f"_stage_{stage}")(job_id, topic, d)
                self.state.finish_stage(job_id, stage, arts)
                self.state.log(f"stage {stage} done", job_id=job_id)
            except BudgetExceeded as e:
                self.state.set_job_status(job_id, "paused", str(e))
                self.state.log(f"paused for budget: {e}", "warn", job_id)
                return job_id
            except Exception as e:  # noqa: BLE001 - we record and stop the job, never crash the run
                n = self.state.bump_attempt(job_id)
                status = "failed" if n < self.cfg.pipeline["retries"]["max_attempts"] else "review"
                self.state.set_job_status(job_id, status, f"{stage}: {e}")
                self.state.log(f"stage {stage} failed (attempt {n}): {e}", "error", job_id)
                return job_id
        self.state.set_job_status(job_id, "review")
        return job_id

    def _art(self, job_id: str, stage: str) -> dict:
        return self.state.get_job(job_id)["artifacts"].get(stage, {})  # type: ignore[index]

    # ---- C: script
    def _stage_script(self, job_id: str, topic: dict, d: Path) -> dict:
        idea = json.loads(topic.get("notes") or "{}")
        r_ = self.cfg.channel["rules"]
        lo, hi = r_["target_seconds"]
        wps = r_["words_per_second"]
        prompt = P.SCRIPT.format(object=idea.get("object", topic["title"]), question=topic["title"],
                                 angle=idea.get("angle", ""), pillar=topic.get("pillar"),
                                 seconds_lo=lo, seconds_hi=hi, words_lo=int(lo * wps), words_hi=int(hi * wps),
                                 min_sources=r_["min_sources_main_claim"])
        r = self._llm(prompt, job_id, "script", est=0.25, system=P.SYSTEM_WRITER, web_search=True,
                      model=self.cfg.pipeline["providers"]["llm"]["model_script"], max_tokens=6000)
        script = r.data or {}
        if script.get("viable") is False:
            self.state.set_topic_status(topic["id"], "rejected")
            raise StageFailed(f"idea not viable: {script.get('reason_if_not')}")
        script["cited_sources"] = r.sources
        script["hook_scores"] = [hook_score(h) for h in script.get("hooks", [])]
        if script["hook_scores"]:
            best = max(range(len(script["hook_scores"])), key=lambda i: script["hook_scores"][i]["verdict"])
            script.setdefault("chosen_hook", best)
        self._validate_script(script)
        (d / "script.json").write_text(json.dumps(script, indent=2, ensure_ascii=False))
        return {"file": str(d / "script.json")}

    def _validate_script(self, s: dict) -> None:
        scenes = s.get("scenes") or []
        if not 3 <= len(scenes) <= 8:
            raise StageFailed(f"script has {len(scenes)} scenes (want 4-7)")
        words = sum(len(sc.get("narration", "").split()) for sc in scenes)
        lo, hi = self.cfg.channel["rules"]["target_seconds"]
        wps = self.cfg.channel["rules"]["words_per_second"]
        if words > hi * wps * 1.35 or words < lo * wps * 0.6:
            raise StageFailed(f"script is {words} words, outside target")
        facts = s.get("facts") or []
        if not facts:
            raise StageFailed("no fact list")
        main = [f for f in facts if f.get("main")] or facts[:1]
        need = self.cfg.channel["rules"]["min_sources_main_claim"]
        if any(len(f.get("sources") or []) < need for f in main) and self.cfg.live:
            raise StageFailed("main claim has too few sources")
        if any(not f.get("sources") for f in facts):
            raise StageFailed("a claim has no source")
        banned = self.cfg.channel["rules"]["banned_topics"]
        text = " ".join(sc.get("narration", "") for sc in scenes).lower()
        hits = [b for b in banned if re.search(rf"\b{re.escape(b)}\b", text)]
        if hits:
            raise StageFailed(f"script mentions banned topic words: {hits}")

    # ---- F (part 1): independent review of the script, with one bounded repair
    def _stage_review(self, job_id: str, topic: dict, d: Path) -> dict:
        path = d / "script.json"
        script = json.loads(path.read_text())
        lean = {k: script.get(k) for k in ("title", "hooks", "chosen_hook", "scenes", "facts")}
        rv_model = self.cfg.pipeline["providers"]["llm"]["model_routine"]
        rv = self._llm(P.REVIEW.format(script=json.dumps(lean, ensure_ascii=False)), job_id, "review",
                       est=0.08, web_search=True, model=rv_model).data or {}
        blockers = [p for p in rv.get("problems", []) if p.get("severity") == "blocker"]
        if (blockers or rv.get("verdict") == "fix") and not script.get("_revised"):
            fx = self._llm(P.FIX.format(problems=json.dumps(rv.get("problems", [])),
                                        script=json.dumps(script, ensure_ascii=False)),
                           job_id, "fix", est=0.2, system=P.SYSTEM_WRITER,
                           model=self.cfg.pipeline["providers"]["llm"]["model_script"]).data or {}
            fx["_revised"] = True
            fx["hook_scores"] = [hook_score(h) for h in fx.get("hooks", [])]
            fx["cited_sources"] = script.get("cited_sources", [])
            self._validate_script(fx)
            path.write_text(json.dumps(fx, indent=2, ensure_ascii=False))
            lean = {k: fx.get(k) for k in ("title", "hooks", "chosen_hook", "scenes", "facts")}
            rv = self._llm(P.REVIEW.format(script=json.dumps(lean, ensure_ascii=False)), job_id, "review2",
                           est=0.08, web_search=True, model=rv_model).data or {}
        (d / "review.json").write_text(json.dumps(rv, indent=2))
        if rv.get("verdict") == "reject" or float(rv.get("total", 0)) < self.cfg.channel["rules"]["review_pass_score"]:
            raise StageFailed(f"review score {rv.get('total')} / verdict {rv.get('verdict')}: "
                              f"{[p.get('issue') for p in rv.get('problems', [])]}")
        return {"file": str(d / "review.json"), "score": rv.get("total")}

    # ---- D: voice
    def _stage_voice(self, job_id: str, topic: dict, d: Path) -> dict:
        script = json.loads((d / "script.json").read_text())
        scenes = script["scenes"]
        hooks = script.get("hooks") or []
        idx = script.get("chosen_hook", 0)
        # The chosen hook replaces scene 1's narration so the spoken opening is the scored winner.
        if hooks and 0 <= idx < len(hooks):
            scenes[0]["narration"] = hooks[idx]
        text = " ".join(sc["narration"].strip() for sc in scenes)
        for word, say in (self.cfg.channel["voice"].get("pronunciations") or {}).items():
            text = re.sub(rf"\b{re.escape(word)}\b", say, text)
        if self.cfg.live:
            est = len(text) / 1000 * self.cfg.pipeline["providers"]["tts"]["usd_per_1k_chars"]
            self.budget.authorize(est, "tts", job_id)
        sp = self.tts.speak(text, d / "narration.mp3")
        if sp.usd:
            self.state.add_cost("elevenlabs", "tts_chars", sp.chars, sp.usd, job_id)
        (d / "script.json").write_text(json.dumps(script, indent=2, ensure_ascii=False))
        (d / "words.json").write_text(json.dumps([w.__dict__ for w in sp.words]))
        return {"audio": str(sp.audio), "words": str(d / "words.json"), "duration": sp.duration}

    # ---- E (part 1): images + vision check + callout location
    def _stage_visuals(self, job_id: str, topic: dict, d: Path) -> dict:
        script = json.loads((d / "script.json").read_text())
        style = self.cfg.channel["style"]["image_style"]
        rng = random.Random(job_id)
        out: dict = {"scenes": {}, "flags": []}
        for sc in script["scenes"]:
            if sc["type"] == "blueprint_card":
                continue
            entry: dict = {}
            for key, slot in (("image_prompt", "image"), ("image2_prompt", "image2")):
                if not sc.get(key):
                    continue
                prompt = f"{sc[key]}. {style}. Vertical 9:16 composition, key subject in the middle third."
                path = d / f"{sc['id']}_{slot}.png"
                best = None
                for attempt in range(2):
                    if self.cfg.live:
                        self.budget.authorize(0.03, "image", job_id)
                    img, usd = self.images.generate(prompt, path, seed=rng.randint(1, 10**6))
                    if usd:
                        self.state.add_cost("bfl", "image", 1, usd, job_id)
                    target = (sc.get("callouts") or [{}])[0].get("target", sc[key])
                    chk = self._look(img, target, sc[key], job_id)
                    best = (img, chk)
                    if not (chk.get("has_text_or_logo") or chk.get("artifacts")) and chk.get("matches_prompt", True):
                        break
                img, chk = best  # type: ignore[misc]
                if chk.get("has_text_or_logo") or chk.get("artifacts") or not chk.get("matches_prompt", True):
                    out["flags"].append(f"{sc['id']} {slot}: image check failed twice ({chk})")
                entry[slot] = str(img)
                if slot == "image":
                    entry["callouts"] = []
                    for co in sc.get("callouts") or []:
                        loc = chk if co.get("target") == target else self._look(img, co["target"], sc[key], job_id)
                        if loc.get("found"):
                            entry["callouts"].append({"box": [loc["x"], loc["y"], loc.get("w", 0.2), loc.get("h", 0.2)],
                                                      "label": co.get("label", "")[:24]})
            out["scenes"][sc["id"]] = entry
        (d / "visuals.json").write_text(json.dumps(out, indent=2))
        return {"file": str(d / "visuals.json"), "flags": out["flags"]}

    def _look(self, img: Path, target: str, prompt: str, job_id: str) -> dict:
        im = Image.open(img).convert("RGB")
        im.thumbnail((576, 1024))
        buf = io.BytesIO()
        im.save(buf, "PNG")
        r = self._llm(P.LOCATE.format(target=target, prompt=prompt), job_id, "vision", est=0.01,
                      images=[buf.getvalue()], model=self.cfg.pipeline["providers"]["llm"]["model_routine"],
                      max_tokens=400)
        return r.data or {}

    # ---- E (part 2): render
    def _stage_render(self, job_id: str, topic: dict, d: Path) -> dict:
        script = json.loads((d / "script.json").read_text())
        vis = json.loads((d / "visuals.json").read_text())["scenes"]
        voice = self._art(job_id, "voice")
        words = [A_word(**w) for w in json.loads(Path(voice["words"]).read_text())]
        scenes = script["scenes"]
        counts = [len(sc["narration"].split()) for sc in scenes]
        starts, i = [], 0
        for c in counts:
            starts.append(words[min(i, len(words) - 1)].start if i else 0.0)
            i += c
        end = words[-1].end + 0.6
        motions = list(self.cfg.channel["style"]["variety"]["motions"])
        random.Random(job_id).shuffle(motions)
        clips = []
        for k, sc in enumerate(scenes):
            dur = (starts[k + 1] if k + 1 < len(scenes) else end) - starts[k]
            v = vis.get(sc["id"], {})
            kind = sc["type"] if sc["type"] in ("comparison", "blueprint_card") else "image"
            if kind == "comparison" and not v.get("image2"):
                kind = "image"
            scene = Scene(
                kind=kind, duration=max(dur, 0.8),
                image=Path(v["image"]) if v.get("image") else None,
                image2=Path(v["image2"]) if v.get("image2") else None,
                labels=tuple((sc.get("labels") or ["", ""])[:2]),  # type: ignore[arg-type]
                motion=motions[k % len(motions)],
                callouts=[Callout(tuple(c["box"]), c["label"], 0.35 + 0.9 * j)  # type: ignore[arg-type]
                          for j, c in enumerate(v.get("callouts", []))],
                card_text=sc.get("card_text") or "",
            )
            if scene.kind == "image" and scene.image is None:
                scene.kind, scene.card_text = "blueprint_card", sc.get("card_text") or sc.get("on_screen_text") or ""
            clips.append(render_scene(scene, d / f"clip_{k:02d}.mp4", self.pal))
        video = A.concat(clips, d / "video.mp4")
        music = self.cfg.channel.get("music_file")
        audio = A.mix_audio(A.AudioPlan(Path(voice["audio"]), Path(music) if music else None), end, d / "mix.wav")
        hook_text = (scenes[0].get("on_screen_text") or "").strip()
        # If a callout target sits in the default caption band, drop captions lower so they
        # don't cover the circled detail (still above the phone's bottom title/buttons area).
        boxes = [c["box"] for v in vis.values() for c in v.get("callouts", [])]
        y_cap = 1360 if any(0.50 <= b[1] <= 0.70 for b in boxes) else 1180
        ass = write_ass(words, d / "captions.ass", y_center=y_cap,
                        font=self.cfg.channel["style"]["caption_font"],
                        font_size=self.cfg.channel["style"]["caption_size"],
                        overlays=[(0.0, min(2.2, end), hook_text.upper())] if hook_text else None)
        final = A.finalize(video, audio, ass, d / "final.mp4")
        return {"video": str(final), "duration": end}

    # ---- F (part 2): media QA
    def _stage_qa(self, job_id: str, topic: dict, d: Path) -> dict:
        r = self._art(job_id, "render")
        voice = self._art(job_id, "voice")
        rep = check_video(Path(r["video"]), max_seconds=60.0, min_seconds=8.0,
                          expected_narration_s=voice["duration"])
        flags = self._art(job_id, "visuals").get("flags", [])
        out = rep.as_dict() | {"image_flags": flags}
        (d / "qa.json").write_text(json.dumps(out, indent=2))
        if not rep.passed:
            raise StageFailed("media QA failed: " + "; ".join(c.detail for c in rep.checks if not c.ok and c.hard))
        return {"file": str(d / "qa.json"), "passed": True, "image_flags": flags}

    # ---- G: packaging
    def _stage_package(self, job_id: str, topic: dict, d: Path) -> dict:
        script = json.loads((d / "script.json").read_text())
        ch = self.cfg.channel["channel"]
        title = script.get("title", topic["title"])[:100]
        lint = title_lint(title, script.get("thumb_text"))
        srcs, seen = [], set()
        for f in script.get("facts", []):
            for u in f.get("sources", []):
                if u not in seen:
                    seen.add(u)
                    srcs.append(u)
        tags = list(dict.fromkeys((script.get("hashtags") or []) + ch["default_hashtags"]))[:4]
        desc = (f"{script.get('description', '').strip()}\n\n"
                + ("Sources:\n" + "\n".join(f"- {u}" for u in srcs[:6]) + "\n\n" if srcs else "")
                + "Visuals are AI-generated illustrations; narration is an AI voice. "
                  "Facts are checked against the sources above.\n\n" + " ".join(tags))
        meta = {"title": title, "description": desc[:4900], "tags": [t.lstrip("#") for t in tags],
                "category_id": ch["youtube_category_id"], "language": ch["language"],
                "made_for_kids": ch["made_for_kids"], "contains_synthetic_media": True,
                "title_lint": lint, "thumb_text": script.get("thumb_text"),
                "affiliate_product": script.get("affiliate_product")}
        (d / "metadata.json").write_text(json.dumps(meta, indent=2, ensure_ascii=False))
        (d / "review.md").write_text(self._review_md(job_id, script, meta, d), encoding="utf-8")
        return {"file": str(d / "metadata.json"), "review_md": str(d / "review.md"),
                "cost_usd": round(self.state.job_cost(job_id), 4)}

    def _review_md(self, job_id: str, script: dict, meta: dict, d: Path) -> str:
        rv = json.loads((d / "review.json").read_text()) if (d / "review.json").exists() else {}
        qa = json.loads((d / "qa.json").read_text()) if (d / "qa.json").exists() else {}
        hooks = "\n".join(f"- {h['verdict']:>3} {h['band']:<8} {h['hook']}" for h in script.get("hook_scores", []))
        scenes = "\n".join(f"{i+1}. **{s['type']}** — {s['narration']}" for i, s in enumerate(script["scenes"]))
        facts = "\n".join(f"- {f['claim']} — " + ", ".join(f.get("sources", [])) for f in script.get("facts", []))
        checks = "\n".join(f"- {'✅' if c['ok'] else ('❌' if c['hard'] else '⚠️')} {c['name']}: {c['detail']}"
                           for c in qa.get("checks", []))
        probs = "\n".join(f"- ({p.get('severity')}) {p.get('issue')} → {p.get('fix')}" for p in rv.get("problems", [])) or "- none"
        mode = "DRY RUN — fake providers, not publishable" if not self.cfg.live else "live"
        return f"""## Review: {meta['title']}

`job {job_id}` · mode: **{mode}** · cost so far: **${self.state.job_cost(job_id):.2f}** · review score **{rv.get('total', '?')}/10**

**Reply with one of:** `approve` · `reject: <reason>` · `fix: <what to change>`

### Title check ({meta['title_lint']['score']}/100)
{chr(10).join('- ' + i['kind'] + ': ' + i['detail'] for i in meta['title_lint']['issues']) or '- no issues'}

### Hooks (heuristic score, not a prediction)
{hooks}

### Script
{scenes}

### Facts and sources
{facts}

### Independent review problems
{probs}

### Media checks
{checks}
{('### Image flags' + chr(10) + chr(10).join('- ' + f for f in qa.get('image_flags', []))) if qa.get('image_flags') else ''}

### Description preview
```
{meta['description']}
```
"""

    # ---------- approval + publish ----------
    def decide(self, job_id: str, decision: str, note: str = "") -> None:
        job = self.state.get_job(job_id)
        if not job:
            raise KeyError(job_id)
        if decision == "approve":
            self.state.set_job_status(job_id, "approved")
        elif decision == "reject":
            self.state.set_job_status(job_id, "rejected", note)
            self.state.set_topic_status(job["topic_id"], "rejected")
            self.state.upsert_topic(job["topic_id"], "", notes=json.dumps({"rejected_reason": note}))
        elif decision == "fix":
            # one bounded repair: rewrite from the review stage with the owner's note as a blocker
            d = self.build / job_id
            rv_path = d / "review.json"
            rv = json.loads(rv_path.read_text()) if rv_path.exists() else {}
            rv.setdefault("problems", []).append({"issue": f"owner: {note}", "fix": note, "severity": "blocker"})
            script = json.loads((d / "script.json").read_text())
            script.pop("_revised", None)
            (d / "script.json").write_text(json.dumps(script, indent=2, ensure_ascii=False))
            fx = self._llm(P.FIX.format(problems=json.dumps(rv["problems"]), script=json.dumps(script)),
                           job_id, "owner_fix", est=0.2, system=P.SYSTEM_WRITER,
                           model=self.cfg.pipeline["providers"]["llm"]["model_script"]).data or {}
            fx["_revised"] = True
            fx["hook_scores"] = [hook_score(h) for h in fx.get("hooks", [])]
            (d / "script.json").write_text(json.dumps(fx, indent=2, ensure_ascii=False))
            self.state.finish_stage(job_id, "review")   # resume from voice
            self.state.set_job_status(job_id, "running")
        else:
            raise ValueError(decision)
        self.state.log(f"owner decision: {decision} {note}", job_id=job_id)

    def publish(self, job_id: str, publish_at: str | None = None) -> dict:
        from .publish.youtube import VideoMeta, upload
        job = self.state.get_job(job_id)
        if not job or job["status"] != "approved":
            raise RuntimeError(f"job {job_id} is not approved")
        if not self.cfg.live:
            raise RuntimeError("refusing to upload a dry-run video")
        meta = json.loads(Path(job["artifacts"]["package"]["file"]).read_text())
        vm = VideoMeta(meta["title"], meta["description"], meta["tags"], meta["category_id"],
                       meta["language"], meta["made_for_kids"], meta["contains_synthetic_media"], publish_at)
        rec = upload(self.state, job_id, Path(job["artifacts"]["render"]["video"]), vm)
        self.state.set_job_status(job_id, "published")
        self.state.set_topic_status(job["topic_id"], "published")
        return rec

    # ---------- reporting ----------
    def summary(self) -> str:
        now = time.time()
        jobs = self.state.jobs()
        by = {}
        for j in jobs:
            by.setdefault(j["status"], []).append(j["id"])
        lines = [f"# Daily summary {time.strftime('%Y-%m-%d', time.gmtime(now))}",
                 f"- Spend last 24 h: ${self.state.spend_since(now - 86400):.2f} · this month (approx): "
                 f"${self.state.spend_since(now - 30 * 86400):.2f}",
                 f"- Topics in backlog (shortlisted): {len(self.state.topics('shortlisted'))}"]
        for k, v in sorted(by.items()):
            lines.append(f"- Jobs {k}: {len(v)} ({', '.join(v[-5:])})")
        errs = self.state.db.execute("SELECT at, job_id, message FROM events WHERE level IN ('error','warn') "
                                     "AND at>=? ORDER BY at DESC LIMIT 10", (now - 86400,)).fetchall()
        if errs:
            lines.append("- Problems (24 h):")
            lines += [f"  - {r['job_id'] or '-'}: {r['message'][:160]}" for r in errs]
        return "\n".join(lines)


def A_word(text: str, start: float, end: float):
    from .render.captions import Word
    return Word(text, start, end)
