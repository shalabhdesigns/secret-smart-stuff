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


class QualityRejected(StageFailed):
    """The script could not reach the quality bar; drop the topic instead of retrying it."""


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
        vc = pc.get("video_clips") or {}
        self.clips_on = bool(vc.get("enabled"))
        if self.clips_on and self.cfg.live:
            from .providers.video import BFLVideo
            rate = (vc.get("usd_per_second") or {}).get("draft" if vc.get("draft", True) else "full")
            self.video = BFLVideo(self.cfg.secret("BFL_API_KEY"), draft=vc.get("draft", True), usd_per_second=rate)
        else:
            from .providers.video import FakeVideo
            self.video = FakeVideo()

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
        drops = [r["note"] for r in self.state.db.execute(
            "SELECT note FROM feedback WHERE decision='drop' AND note != '' ORDER BY at DESC LIMIT 8")]
        extra = ("\n\nThe owner dropped earlier topics for these reasons - avoid ideas with the same problem:\n"
                 + "\n".join(f"- {x[:200]}" for x in drops)) if drops else ""
        r = self._llm(P.IDEAS.format(n=n, quotas=quotas, avoid=avoid, covered=covered, signals=sig) + extra, None, "ideas",
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
        # Finish what was started first: a failed job resumes from its last good stage.
        # A job paused by the daily budget is finished the next day before anything new starts.
        for j in self.state.jobs("failed") + self.state.jobs("paused"):
            t = self.state.get_topic(j["topic_id"])
            if t:
                return t
        for status in ("approved", "shortlisted"):
            ts = self.state.topics(status)
            if ts:
                return ts[0]
        return None

    # ---------- production ----------
    def produce(self, topic_id: str, fresh: bool = False) -> str:
        topic = self.state.get_topic(topic_id)
        if not topic:
            raise KeyError(topic_id)
        existing = [j for j in self.state.jobs() if j["topic_id"] == topic_id]
        job_id = f"{topic_id}-v1"
        if existing:
            latest = max(existing, key=lambda j: j["created_at"])
            if fresh:
                for j in existing:
                    if j["status"] in ("review", "failed", "paused"):
                        self.state.set_job_status(j["id"], "rejected", "superseded by a new version")
                job_id = f"{topic_id}-v{len(existing) + 1}"
            else:
                job_id = latest["id"]
        job = self.state.start_job(job_id, topic_id)
        if job["status"] in ("review", "approved", "published"):
            return job_id
        self.state.set_topic_status(topic_id, "in_production")
        self.state.set_job_status(job_id, "running")
        d = self.build / job_id
        d.mkdir(parents=True, exist_ok=True)
        done = self._restore(job, d)
        start = STAGES.index(done) + 1 if done in STAGES else 0
        for stage in STAGES[start:]:
            try:
                arts = getattr(self, f"_stage_{stage}")(job_id, topic, d)
                self.state.finish_stage(job_id, stage, arts)
                self.state.log(f"stage {stage} done", job_id=job_id)
            except QualityRejected as e:
                self.state.set_job_status(job_id, "rejected", f"{stage}: {e}")
                self.state.set_topic_status(topic_id, "rejected")
                self.state.log(f"topic dropped at quality gate: {e}", "warn", job_id)
                return job_id
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

    def _restore(self, job: dict, d: Path) -> str:
        """Each run starts on a fresh machine. Text outputs (script, review) are kept in the
        state database and written back here; media outputs are not kept, so if they are
        missing the job steps back to the last stage whose outputs still exist."""
        arts = job["artifacts"]
        if arts.get("review", {}).get("script"):
            (d / "script.json").write_text(json.dumps(arts["review"]["script"], indent=2, ensure_ascii=False))
            (d / "review.json").write_text(json.dumps(arts["review"].get("content", {}), indent=2))
        elif arts.get("script", {}).get("content") and not (d / "script.json").exists():
            (d / "script.json").write_text(json.dumps(arts["script"]["content"], indent=2, ensure_ascii=False))
        needs = {
            "script": [d / "script.json"],
            "review": [d / "script.json", d / "review.json"],
            "voice": [Path(arts.get("voice", {}).get("audio", d / "_none")),
                      Path(arts.get("voice", {}).get("words", d / "_none"))],
            "visuals": [d / "visuals.json"],
            "render": [Path(arts.get("render", {}).get("video", d / "_none"))],
            "qa": [d / "qa.json"],
            "package": [d / "metadata.json", d / "review.md"],
        }
        done = job["stage"]
        last_ok = "created"
        for st in STAGES:
            if done not in STAGES or STAGES.index(st) > STAGES.index(done):
                break
            if not all(f.exists() for f in needs[st]):
                break
            last_ok = st
        if last_ok != done:
            self.state.log(f"resuming from after '{last_ok}' (outputs of later stages not on this machine)",
                           job_id=job["id"])
        return last_ok

    def _art(self, job_id: str, stage: str) -> dict:
        return self.state.get_job(job_id)["artifacts"].get(stage, {})  # type: ignore[index]

    # ---- C: script
    def _owner_context(self) -> str:
        """The owner's past change requests (so the writer gets it right first time) and lessons that
        passed the evidence bar in the weekly learning report. Both are short; empty when none."""
        out = []
        notes = [r["note"] for r in self.state.db.execute(
            "SELECT note FROM feedback WHERE decision='fix' AND note != '' ORDER BY at DESC LIMIT 8")]
        if notes:
            out.append("\n\nThe channel owner asked for these changes on earlier videos. Apply them proactively "
                       "where relevant:\n" + "\n".join(f"- {n[:240]}" for n in notes))
        lessons = self.state.get_setting("lessons_for_writer")
        if lessons:
            out.append("\n\nLessons from this channel's own analytics (evidence-backed):\n" + lessons[:1500])
        return "".join(out)

    def _stage_script(self, job_id: str, topic: dict, d: Path) -> dict:
        idea = json.loads(topic.get("notes") or "{}")
        r_ = self.cfg.channel["rules"]
        lo, hi = r_["target_seconds"]
        wps = r_["words_per_second"]
        prompt = P.SCRIPT.format(video_rule=P.VIDEO_RULE if self.clips_on else "",
                                 motions_field=P.MOTIONS_FIELD if self.clips_on else "",
                                 object=idea.get("object", topic["title"]), question=topic["title"],
                                 angle=idea.get("angle", ""), pillar=topic.get("pillar"),
                                 seconds_lo=lo, seconds_hi=hi, words_lo=int(lo * wps), words_hi=int(hi * wps),
                                 min_sources=r_["min_sources_main_claim"])
        prompt += self._owner_context()
        r = self._llm(prompt, job_id, "script", est=0.25, system=P.SYSTEM_WRITER, web_search=True,
                      model=self.cfg.pipeline["providers"]["llm"]["model_script"], max_tokens=12000)
        script = r.data or {}
        if script.get("viable") is False:
            self.state.set_topic_status(topic["id"], "rejected")
            raise StageFailed(f"idea not viable: {script.get('reason_if_not')}")
        script["cited_sources"] = r.sources
        self._sync_hook(script)
        self._attach_citations(script)
        script["hook_scores"] = [hook_score(h) for h in script.get("hooks", [])]
        if script["hook_scores"]:
            best = max(range(len(script["hook_scores"])), key=lambda i: script["hook_scores"][i]["verdict"])
            script.setdefault("chosen_hook", best)
        try:
            self._validate_script(script)
        except StageFailed as e:
            # One bounded repair with web search: ask for the missing sources / fixes.
            self.state.log(f"script failed check ({e}); one repair attempt", "warn", job_id)
            fx = self._llm(P.FIX.format(problems=json.dumps([self._length_rule(), {"issue": str(e),
                    "fix": "Search the web and add at least two independent, credible source URLs "
                           "for the main claim (and one for every other claim). Keep everything else."}]),
                    script=json.dumps(script, ensure_ascii=False)),
                job_id, "script_repair", est=0.2, system=P.SYSTEM_WRITER, web_search=True,
                model=self.cfg.pipeline["providers"]["llm"]["model_script"], max_tokens=12000)
            fixed = fx.data or {}
            fixed["cited_sources"] = (script.get("cited_sources") or []) + fx.sources
            fixed["hook_scores"] = [hook_score(h) for h in fixed.get("hooks", [])]
            self._attach_citations(fixed)
            self._validate_script(fixed)
            script = fixed
        (d / "script.json").write_text(json.dumps(script, indent=2, ensure_ascii=False))
        return {"file": str(d / "script.json"), "content": script}

    def _length_rule(self) -> dict:
        lo, hi = self.cfg.channel["rules"]["target_seconds"]
        wps = self.cfg.channel["rules"]["words_per_second"]
        return {"issue": "length", "severity": "blocker",
                "fix": f"Keep the TOTAL narration between {int(lo * wps)} and {int(hi * wps)} words across "
                       f"11-13 beats (5-9 words each). If you add words anywhere, cut the same number elsewhere."}

    @staticmethod
    def _sync_hook(s: dict) -> None:
        """The spoken first line must be the chosen hook, so reviewer and viewer see the same thing."""
        hooks, scenes = s.get("hooks") or [], s.get("scenes") or []
        if not hooks or not scenes:
            return
        scores = s.get("hook_scores") or []
        idx = s.get("chosen_hook")
        if not isinstance(idx, int) or not 0 <= idx < len(hooks):
            idx = max(range(len(scores)), key=lambda i: scores[i]["verdict"]) if scores else 0
        s["chosen_hook"] = idx
        scenes[0]["narration"] = hooks[idx]

    @staticmethod
    def _attach_citations(s: dict) -> None:
        """Pages the model actually cited during web search are real sources. If the main
        claim lists fewer than two, top it up from those citations (never invented URLs)."""
        cited = list(dict.fromkeys(c["url"] for c in s.get("cited_sources") or [] if c.get("url")))
        facts = s.get("facts") or []
        main = [f for f in facts if f.get("main")] or facts[:1]
        for f in main:
            srcs = list(dict.fromkeys(f.get("sources") or []))
            for u in cited:
                if len(srcs) >= 2:
                    break
                if u not in srcs:
                    srcs.append(u)
            f["sources"] = srcs

    def _validate_script(self, s: dict) -> None:
        scenes = s.get("scenes") or []
        if not 9 <= len(scenes) <= 14:
            raise StageFailed(f"script has {len(scenes)} beats (want 11-13)")
        words = sum(len(sc.get("narration", "").split()) for sc in scenes)
        lo, hi = self.cfg.channel["rules"]["target_seconds"]
        wps = self.cfg.channel["rules"]["words_per_second"]
        if words > hi * wps * 1.08 or words < lo * wps * 0.75:
            raise StageFailed(f"script is {words} words; target {int(lo*wps)}-{int(hi*wps)}")
        images = s.get("images") or {}
        if not 4 <= len(images) <= 9:
            raise StageFailed(f"script has {len(images)} images (want 6-7)")
        for sc in scenes:
            if sc.get("image") and sc["image"] not in images:
                raise StageFailed(f"beat {sc.get('id')} uses unknown image {sc['image']}")
            if not sc.get("image") and not sc.get("card_text"):
                raise StageFailed(f"beat {sc.get('id')} has neither image nor card")
        if sum(1 for sc in scenes if sc.get("pop")) > 2:
            for sc in scenes[::-1]:
                if sc.get("pop") and sum(1 for x in scenes if x.get("pop")) > 2:
                    sc["pop"] = None
        if sum(1 for sc in scenes if sc.get("card_text") and not sc.get("image")) > 1:
            raise StageFailed("more than one card beat")
        if scenes[-1].get("image") != scenes[0].get("image") and scenes[0].get("image"):
            scenes[-1]["image"] = scenes[0]["image"]          # loop: end on the opening picture
            scenes[-1]["card_text"] = None
        # loop lead-in: never a question or a closed sentence, so the voice carries into beat 1
        last = scenes[-1].get("narration", "").strip()
        if last.endswith("?") or len(last.split()) > 8:
            last = "So next time someone asks you"          # safe lead-in for a question opening
        scenes[-1]["narration"] = re.sub(r"[.!,;:…\s]+$", "", last) + "..."
        for sc in (scenes[0], scenes[-1]):
            sc["callout"] = None
            sc["pop"] = None
        facts = s.get("facts") or []
        if not facts:
            raise StageFailed("no fact list")
        main = [f for f in facts if f.get("main")] or facts[:1]
        need = self.cfg.channel["rules"]["min_sources_main_claim"]
        if any(not f.get("sources") for f in facts):
            raise StageFailed("a claim has no source")
        distinct = {u for f in facts for u in (f.get("sources") or [])}
        if self.cfg.live and (any(not f.get("sources") for f in main) or len(distinct) < need):
            raise StageFailed("main claim has too few sources")
        banned = self.cfg.channel["rules"]["banned_topics"]
        text = " ".join(sc.get("narration", "") for sc in scenes).lower()
        hits = [b for b in banned if re.search(rf"\b{re.escape(b)}\b", text)]
        if hits:
            raise StageFailed(f"script mentions banned topic words: {hits}")

    def _stage_review(self, job_id: str, topic: dict, d: Path) -> dict:
        """Independent review, then up to 2 targeted repairs. If it still scores below the bar,
        the topic is dropped (QualityRejected) so the run can move on to a better topic."""
        path = d / "script.json"
        script = json.loads(path.read_text())
        rv_model = self.cfg.pipeline["providers"]["llm"]["model_routine"]
        bar = self.cfg.channel["rules"]["review_pass_score"]

        def review(sc: dict, tag: str) -> dict:
            # The reviewer sees only what the viewer will get (no hook list or index to confuse it).
            lean = {"title": sc.get("title"),
                    "opening_line": (sc.get("scenes") or [{}])[0].get("narration", ""),
                    "scenes": sc.get("scenes"), "facts": sc.get("facts")}
            return self._llm(P.REVIEW.format(script=json.dumps(lean, ensure_ascii=False)), job_id, tag,
                             est=0.08, web_search=True, model=rv_model, max_tokens=8000).data or {}

        rv = review(script, "review")
        for round_ in range(2):
            if float(rv.get("total", 0)) >= bar and rv.get("verdict") != "reject":
                break
            if rv.get("verdict") == "reject":
                break
            problems = rv.get("problems", []) + [self._length_rule(), {"issue": "general", "severity": "blocker", "fix":
                "Fix every problem above. Remove or soften any claim you cannot support with a source "
                "you can open. Keep the hook, the first scene's narration and chosen_hook consistent."}]
            fx = self._llm(P.FIX.format(problems=json.dumps(problems), script=json.dumps(script, ensure_ascii=False)),
                           job_id, f"fix{round_ + 1}", est=0.25, system=P.SYSTEM_WRITER, web_search=True,
                           model=self.cfg.pipeline["providers"]["llm"]["model_script"], max_tokens=12000)
            fixed = fx.data or {}
            fixed["cited_sources"] = (script.get("cited_sources") or []) + fx.sources
            fixed["hook_scores"] = [hook_score(h) for h in fixed.get("hooks", [])]
            self._sync_hook(fixed)
            self._attach_citations(fixed)
            try:
                self._validate_script(fixed)
            except StageFailed as e:
                self.state.log(f"repair {round_ + 1} broke the script ({e}); keeping previous", "warn", job_id)
                continue
            script = fixed
            path.write_text(json.dumps(script, indent=2, ensure_ascii=False))
            rv = review(script, f"review{round_ + 2}")
        (d / "review.json").write_text(json.dumps(rv, indent=2))
        if rv.get("verdict") == "reject" or float(rv.get("total", 0)) < bar:
            raise QualityRejected(f"review score {rv.get('total')} / verdict {rv.get('verdict')}: "
                                  f"{[p.get('issue') for p in rv.get('problems', [])][:4]}")
        return {"file": str(d / "review.json"), "score": rv.get("total"), "content": rv,
                "script": json.loads(path.read_text())}

    # ---- D: voice
    def _stage_voice(self, job_id: str, topic: dict, d: Path) -> dict:
        script = json.loads((d / "script.json").read_text())
        self._sync_hook(script)
        scenes = script["scenes"]
        text = " ".join(sc["narration"].strip() for sc in scenes)
        for word, say in (self.cfg.channel["voice"].get("pronunciations") or {}).items():
            text = re.sub(rf"\b{re.escape(word)}\b", say, text)
        reused = self._reuse_voice(d, text)
        if reused:
            self.state.log("voice unchanged: reused the previous narration", job_id=job_id)
            (d / "script.json").write_text(json.dumps(script, indent=2, ensure_ascii=False))
            return reused
        if self.cfg.live:
            est = len(text) / 1000 * self.cfg.pipeline["providers"]["tts"]["usd_per_1k_chars"]
            self.budget.authorize(est, "tts", job_id)
        sp = self.tts.speak(text, d / "narration.mp3")
        if sp.usd:
            self.state.add_cost("elevenlabs", "tts_chars", sp.chars, sp.usd, job_id)
        # Speech must start at second zero: trim leading silence and shift the word timings.
        # Keep 0.12 s before the aligned first word: alignment can mark a word's start after its first
        # consonant, and a tighter cut clipped first words (owner flagged it 3 times, Oct 2026).
        lead = max(0.0, (sp.words[0].start if sp.words else 0.0) - 0.12)
        audio = sp.audio
        if lead > 0.02:
            trimmed = d / ("narration_trim" + sp.audio.suffix)
            A.run(["ffmpeg", "-y", "-loglevel", "error", "-ss", f"{lead:.3f}", "-i", str(sp.audio),
                   "-c", "copy" if sp.audio.suffix == ".wav" else "libmp3lame", str(trimmed)])
            audio = trimmed
            for w in sp.words:
                w.start, w.end = max(0.0, w.start - lead), max(0.0, w.end - lead)
        (d / "script.json").write_text(json.dumps(script, indent=2, ensure_ascii=False))
        (d / "words.json").write_text(json.dumps([w.__dict__ for w in sp.words]))
        (d / "voice_text.txt").write_text(text)
        return {"audio": str(audio), "words": str(d / "words.json"), "duration": sp.words[-1].end if sp.words else 0}

    # ---- reuse of a previous version's media (owner fixes) ----
    def _prior(self, d: Path) -> Path | None:
        pr = d / "prior"
        return pr if (pr / "script.json").exists() else None

    def _reuse_voice(self, d: Path, text: str) -> dict | None:
        pr = self._prior(d)
        if not pr:
            return None
        old = (pr / "voice_text.txt").read_text() if (pr / "voice_text.txt").exists() else None
        if old is None:   # older bundles: rebuild the text from the old script
            try:
                old_script = json.loads((pr / "script.json").read_text())
                old = " ".join(sc["narration"].strip() for sc in old_script["scenes"])
                for word, say in (self.cfg.channel["voice"].get("pronunciations") or {}).items():
                    old = re.sub(rf"\b{re.escape(word)}\b", say, old)
            except Exception:  # noqa: BLE001
                return None
        audio = next((pr / n for n in ("narration_trim.mp3", "narration_trim.wav", "narration.mp3")
                      if (pr / n).exists()), None)
        if old != text or not audio or not (pr / "words.json").exists():
            return None
        import shutil
        shutil.copy(audio, d / audio.name)
        shutil.copy(pr / "words.json", d / "words.json")
        (d / "voice_text.txt").write_text(text)
        words = json.loads((d / "words.json").read_text())
        return {"audio": str(d / audio.name), "words": str(d / "words.json"),
                "duration": words[-1]["end"] if words else 0, "reused": True}

    # ---- E (part 1): images + vision check + focus boxes
    def _stage_visuals(self, job_id: str, topic: dict, d: Path) -> dict:
        script = json.loads((d / "script.json").read_text())
        style = self.cfg.channel["style"]["image_style"]
        rng = random.Random(job_id)
        out: dict = {"images": {}, "beats": {}, "flags": []}
        images: dict = dict(script.get("images") or {})
        self._match_budget = 3          # at most 3 replacement images per video
        first_focus = {}
        for sc in script["scenes"]:
            if sc.get("image") and sc.get("focus") and sc["image"] not in first_focus:
                first_focus[sc["image"]] = sc["focus"]
        pr = self._prior(d)
        old_script = json.loads((pr / "script.json").read_text()) if pr else {}
        old_vis = json.loads((pr / "visuals.json").read_text()) if pr and (pr / "visuals.json").exists() else {}
        old_images = old_script.get("images") or {}
        old_scenes = {sc["id"]: sc for sc in old_script.get("scenes") or []}
        reused_keys: set[str] = set()
        for key, prompt_text in images.items():
            prompt = f"{prompt_text}. {style}. Vertical 9:16 composition, key subject large and centred."
            path = d / f"{key}.png"
            if pr and old_images.get(key) == prompt_text and (pr / f"{key}.png").exists() \
                    and key in (old_vis.get("images") or {}):
                import shutil
                shutil.copy(pr / f"{key}.png", path)
                info = dict(old_vis["images"][key])
                info["path"] = str(path)
                info["focus_cache"] = {}
                out["images"][key] = info
                reused_keys.add(key)
                continue
            best = None
            for attempt in range(2):
                if self.cfg.live:
                    self.budget.authorize(0.03, "image", job_id)
                try:
                    img, usd = self.images.generate(prompt, path, seed=rng.randint(1, 10**6))
                except Exception as e:  # noqa: BLE001
                    fb = self.cfg.pipeline["providers"]["images"].get("fallback_model")
                    if not fb:
                        raise
                    self.state.log(f"image model failed ({e}); trying {fb}", "warn", job_id)
                    img, usd = self.images.generate(prompt, path, seed=rng.randint(1, 10**6), model=fb)
                if usd:
                    self.state.add_cost("bfl", "image", 1, usd, job_id)
                chk = self._look(img, first_focus.get(key, prompt_text), prompt_text, job_id)
                best = (img, chk)
                if not (chk.get("has_text_or_logo") or chk.get("artifacts")):
                    break
            img, chk = best  # type: ignore[misc]
            if chk.get("has_text_or_logo") or chk.get("artifacts"):
                what = ", ".join(x for x, v in (("visible text/logo", chk.get("has_text_or_logo")),
                                                ("distorted shapes", chk.get("artifacts"))) if v)
                out["flags"].append(f"{key}: {what} (after 2 tries)")
            out["images"][key] = {"path": str(img), "check": chk, "focus_cache": {first_focus.get(key, ""): chk}}
        for sc in script["scenes"]:
            entry: dict = {}
            old_sc = old_scenes.get(sc["id"])
            old_entry = (old_vis.get("beats") or {}).get(sc["id"])
            if (old_sc is not None and old_entry is not None and sc.get("image") in reused_keys
                    and all(old_sc.get(k) == sc.get(k) for k in ("narration", "image", "focus", "markers", "arrow"))):
                # same words, same picture: keep the old framing, markers and any replacement image
                entry = dict(old_entry)
                fix_key = entry.get("image")
                if fix_key and fix_key not in out["images"]:
                    src = pr / f"{fix_key}.png"
                    if src.exists() and fix_key in (old_vis.get("images") or {}):
                        import shutil
                        shutil.copy(src, d / f"{fix_key}.png")
                        info = dict(old_vis["images"][fix_key])
                        info["path"] = str(d / f"{fix_key}.png")
                        info["focus_cache"] = {}
                        out["images"][fix_key] = info
                    else:
                        entry.pop("image", None)
                out["beats"][sc["id"]] = entry
                continue
            if sc.get("image") and sc.get("focus"):
                info = out["images"][sc["image"]]
                loc = info["focus_cache"].get(sc["focus"])
                if loc is None:
                    loc = self._look(Path(info["path"]), sc["focus"], images[sc["image"]], job_id)
                    info["focus_cache"][sc["focus"]] = loc
                if loc.get("found"):
                    entry["focus"] = [loc["x"], loc["y"], loc.get("w", 0.25), loc.get("h", 0.25)]
            # Does this picture show what this beat SAYS? If not, give the beat its own image.
            # The first and last beats share one picture (that is the loop), so neither is swapped.
            loop_end = sc is script["scenes"][-1] or sc is script["scenes"][0]
            if sc.get("image") and self._match_budget > 0 and not loop_end:
                key = sc["image"]
                info = out["images"][key]
                m = self._match(Path(info["path"]), sc, images.get(key, ""), job_id)
                if not m.get("matches", True) and m.get("better_prompt"):
                    self._match_budget -= 1
                    new_key = f"{sc['id']}_fix"
                    new_prompt = m["better_prompt"]
                    path = d / f"{new_key}.png"
                    if self.cfg.live:
                        self.budget.authorize(0.03, "image", job_id)
                    img, usd = self.images.generate(f"{new_prompt}. {style}. Vertical 9:16 composition, "
                                                    f"key subject large and centred.", path,
                                                    seed=rng.randint(1, 10**6))
                    if usd:
                        self.state.add_cost("bfl", "image", 1, usd, job_id)
                    images[new_key] = new_prompt
                    out["images"][new_key] = {"path": str(img), "check": {}, "focus_cache": {}}
                    m2 = self._match(img, sc, new_prompt, job_id)
                    if not m2.get("matches", True):
                        out["flags"].append(f"{sc['id']}: image may not match the words ({m2.get('missing', '')})")
                    entry["image"] = new_key
                    loc = self._look(img, sc.get("focus") or new_prompt, new_prompt, job_id)
                    entry["focus"] = [loc["x"], loc["y"], loc.get("w", 0.25), loc.get("h", 0.25)] if loc.get("found") else None
                elif not m.get("matches", True):
                    out["flags"].append(f"{sc['id']}: image may not match the words ({m.get('missing', '')})")
            if sc.get("markers") and sc.get("image"):
                key = entry.get("image") or sc["image"]
                info = out["images"][key]
                marks = []
                im = Image.open(info["path"]).convert("RGB")
                im.thumbnail((576, 1024))
                buf = io.BytesIO()
                im.save(buf, "PNG")
                spec = [{"label": str(m.get("label", ""))[:3], "target": m.get("target", "")} for m in sc["markers"][:4]]
                r = self._llm(P.MARKERS.format(narration=sc.get("narration", ""), markers=json.dumps(spec)),
                              job_id, "markers", est=0.01, images=[buf.getvalue()],
                              model=self.cfg.pipeline["providers"]["llm"]["model_routine"], max_tokens=500)
                for m in (r.data or {}).get("markers", []):
                    if m.get("confidence") in ("high", "medium") and m.get("x") is not None:
                        marks.append({"label": str(m.get("label", ""))[:3], "pos": [m["x"], m["y"]]})
                if marks:
                    entry["markers"] = marks
                elif sc["markers"]:
                    out["flags"].append(f"{sc['id']}: numbered parts not visible in the image")
            if sc.get("arrow") and sc.get("image"):
                info = out["images"][sc["image"]]
                a = self._look(Path(info["path"]), sc["arrow"].get("from", ""), images[sc["image"]], job_id)
                b = self._look(Path(info["path"]), sc["arrow"].get("to", ""), images[sc["image"]], job_id)
                # an arrow shorter than ~12% of the frame reads as a stray mark, so drop it
                if a.get("found") and b.get("found") and ((a["x"] - b["x"]) ** 2 + (a["y"] - b["y"]) ** 2) ** 0.5 >= 0.12:
                    entry["arrow"] = [[a["x"], a["y"]], [b["x"], b["y"]]]
            out["beats"][sc["id"]] = entry
        for info in out["images"].values():
            info.pop("focus_cache", None)
        if self.clips_on:
            self._make_clips(job_id, script, out, d, old_vis if pr else {}, old_script if pr else {}, pr)
        (d / "visuals.json").write_text(json.dumps(out, indent=2))
        return {"file": str(d / "visuals.json"), "flags": out["flags"]}

    # ---- E (part 2): real-motion clips (image-to-video) from the checked stills
    def _beat_durations(self, script: dict) -> list[float]:
        words = json.loads(Path(self._art_path("voice", "words")).read_text()) if self._art_path("voice", "words") else []
        counts = [len(sc["narration"].split()) for sc in script["scenes"]]
        starts, wi = [], 0
        for c in counts:
            starts.append(words[min(wi, len(words) - 1)]["start"] if (wi and words) else 0.0)
            wi += c
        end = (words[-1]["end"] + 0.12) if words else sum(counts) / 2.6
        return [(starts[i + 1] if i + 1 < len(starts) else end) - starts[i] for i in range(len(starts))]

    def _art_path(self, stage: str, key: str) -> str | None:
        job = getattr(self, "_current_job", None)
        if not job:
            return None
        return (self.state.get_job(job)["artifacts"].get(stage) or {}).get(key)

    def _make_clips(self, job_id: str, script: dict, out: dict, d: Path, old_vis: dict, old_script: dict,
                    pr: Path | None) -> None:
        import shutil
        vc = self.cfg.pipeline["providers"]["video_clips"]
        rate = (vc.get("usd_per_second") or {}).get("draft" if vc.get("draft", True) else "full", 0.06)
        self._current_job = job_id
        durs = self._beat_durations(script)
        scenes = script["scenes"]
        need: dict[str, float] = {}
        said: dict[str, list[str]] = {}
        for k, sc in enumerate(scenes):
            if k == len(scenes) - 1:
                continue                      # the last beat replays the opening clip backwards (loop)
            key = (out["beats"].get(sc["id"]) or {}).get("image") or sc.get("image")
            if not key or sc.get("markers"):
                continue                      # numbered markers need a still picture to stay on target
            need[key] = need.get(key, 0) + durs[k]
            said.setdefault(key, []).append(sc["narration"])
        out["clips"] = {}
        total, regen_left = 0, int(vc.get("max_regenerations", 2))
        motions = script.get("motions") or {}
        for key in sorted(need, key=lambda k: (k != scenes[0].get("image"), -need[k])):   # opening clip first
            secs = 5 if need[key] <= 5.5 else 10
            if len(out["clips"]) >= vc.get("max_clips", 8) or total + secs > vc.get("max_seconds", 55):
                out["flags"].append(f"{key}: no clip (per-video clip limit); shown as a still")
                continue
            motion = motions.get(key) or (f"Show this happening: {' '.join(x.rstrip('.') for x in said[key])}. "
                                          "Slow, realistic motion with a gentle camera push-in.")
            motion = motion.strip().rstrip(".")
            prompt = (f"{motion}. Photorealistic, smooth and slow, real-world physics, the object keeps its exact "
                      f"shape, nothing morphs or appears from nowhere, no text, no faces.")
            path = d / f"clip_{key}.mp4"
            old = (old_vis.get("clips") or {}).get(key) if old_vis else None
            if pr and old and old.get("prompt") == prompt and (pr / path.name).exists() \
                    and (old_script.get("images") or {}).get(key) == (script.get("images") or {}).get(key):
                shutil.copy(pr / path.name, path)
                out["clips"][key] = {**old, "path": str(path), "reused": True}
                total += old.get("seconds", secs)
                continue
            still = Path(out["images"][key]["path"])
            chk: dict = {}
            for attempt in range(2):
                if self.cfg.live:
                    self.budget.authorize(secs * rate, "video", job_id)
                clip, usd = self.video.image_to_video(still, prompt if attempt == 0 else
                                                      prompt + " Keep every object exactly as in the first frame.",
                                                      path, seconds=secs)
                if usd:
                    self.state.add_cost("bfl", "video_seconds", secs, usd, job_id)
                chk = self._check_clip(clip, prompt, " ".join(said[key]), job_id)
                if chk.get("ok", True) or regen_left <= 0:
                    break
                regen_left -= 1
                self.state.log(f"clip {key} failed check ({chk.get('problems')}); regenerating", "warn", job_id)
            if not chk.get("ok", True):
                out["flags"].append(f"clip {key}: {chk.get('problems', 'quality issue')}")
            out["clips"][key] = {"path": str(path), "seconds": secs, "prompt": prompt, "check": chk}
            total += secs

    def _check_clip(self, clip: Path, prompt: str, narration: str, job_id: str) -> dict:
        import subprocess
        import tempfile
        try:
            dur = float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0",
                                        str(clip)], capture_output=True, text=True).stdout.strip() or 5)
            frames = []
            with tempfile.TemporaryDirectory() as td:
                for i, f in enumerate((0.25, 0.5, 0.75)):
                    fp = Path(td) / f"{i}.png"
                    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-ss", f"{dur * f:.2f}", "-i", str(clip),
                                    "-frames:v", "1", "-vf", "scale=288:512", str(fp)], check=True)
                    frames.append(Image.open(fp).convert("RGB"))
            sheet = Image.new("RGB", (288 * 3, 512))
            for i, im in enumerate(frames):
                sheet.paste(im, (288 * i, 0))
            buf = io.BytesIO()
            sheet.save(buf, "PNG")
            r = self._llm(P.CLIPCHECK.format(prompt=prompt, narration=narration), job_id, "clipcheck", est=0.01,
                          images=[buf.getvalue()], model=self.cfg.pipeline["providers"]["llm"]["model_routine"],
                          max_tokens=400)
            return r.data or {"ok": True}
        except Exception as e:  # noqa: BLE001
            self.state.log(f"clip check skipped: {e}", "warn", job_id)
            return {"ok": True, "problems": f"not checked ({e})"}

    def _match(self, img: Path, sc: dict, prompt: str, job_id: str) -> dict:
        im = Image.open(img).convert("RGB")
        im.thumbnail((576, 1024))
        buf = io.BytesIO()
        im.save(buf, "PNG")
        r = self._llm(P.MATCH.format(narration=sc.get("narration", ""), prompt=prompt, focus=sc.get("focus") or ""),
                      job_id, "match", est=0.01, images=[buf.getvalue()],
                      model=self.cfg.pipeline["providers"]["llm"]["model_routine"], max_tokens=500)
        return r.data or {}

    def _look(self, img: Path, target: str, prompt: str, job_id: str) -> dict:
        im = Image.open(img).convert("RGB")
        im.thumbnail((576, 1024))
        buf = io.BytesIO()
        im.save(buf, "PNG")
        r = self._llm(P.LOCATE.format(target=target, prompt=prompt), job_id, "vision", est=0.01,
                      images=[buf.getvalue()], model=self.cfg.pipeline["providers"]["llm"]["model_routine"],
                      max_tokens=400)
        return r.data or {}

    # ---- E (part 2): render (v2 beat engine)
    def _stage_render(self, job_id: str, topic: dict, d: Path) -> dict:
        from .render.beats import Arrow, Beat, Marker, Pop, render as render_beats
        from .render.sfx import build_library, pick_music
        script = json.loads((d / "script.json").read_text())
        vis = json.loads((d / "visuals.json").read_text())
        voice = self._art(job_id, "voice")
        words = [A_word(**w) for w in json.loads(Path(voice["words"]).read_text())]
        scenes = script["scenes"]
        rng = random.Random(job_id + "style")
        # beat timing from the real word timings
        counts = [len(sc["narration"].split()) for sc in scenes]
        starts, wi = [], 0
        beat_words = []
        for c in counts:
            starts.append(words[min(wi, len(words) - 1)].start if wi else 0.0)
            beat_words.append(words[wi:wi + c])
            wi += c
        # Loop: stop ~a word-gap after the last word so the replay's first word follows naturally.
        end = words[-1].end + 0.12
        beats: list[Beat] = []
        sfx_events: list[tuple[str, float, float]] = []
        callouts_with_sound, comic_used, chime_used = 0, False, False
        whip_every = rng.choice([3, 4])
        motions_cycle = ["punch", "push", "drift_l", "pull", "drift_r"]
        rng.shuffle(motions_cycle)
        clips = vis.get("clips") or {}
        clip_cursor: dict[str, float] = {}
        # Indicators: only where a beat points at a specific detail, at most 3 per video, never on
        # neighbouring beats, never on the loop beats, and a different style each time.
        indicator_at: dict[int, str] = {}
        styles = ["spotlight", "brackets", "pointer", "ring"]
        rng.shuffle(styles)
        last_k = -9
        for k, sc in enumerate(scenes):
            v = vis["beats"].get(sc["id"], {})
            if (0 < k < len(scenes) - 1 and sc.get("callout") and v.get("focus") and not v.get("markers")
                    and not sc.get("pop") and not v.get("arrow") and sc.get("tone") != "witty"
                    and k - last_k > 1 and len(indicator_at) < 3):
                indicator_at[k] = styles[len(indicator_at)]
                last_k = k
        for k, sc in enumerate(scenes):
            b_start = starts[k]
            b_end = starts[k + 1] if k + 1 < len(scenes) else end
            v = vis["beats"].get(sc["id"], {})
            img_key = v.get("image") or sc.get("image")
            img = Path(vis["images"][img_key]["path"]) if img_key else None
            witty = sc.get("tone") == "witty"
            motion = {"punch": "punch", "push": "push", "pull": "pull", "hold": "hold",
                      "drift": motions_cycle[k % len(motions_cycle)]}.get(sc.get("motion") or "", motions_cycle[k % len(motions_cycle)])
            if witty:
                motion = "shake"
            if k == 0:
                motion = "push"                                    # starts at zoom 1.0 (loop anchor)
            if k == len(scenes) - 1:
                motion = "settle_to_start"                         # lands on the opening frame
            trans = sc.get("transition") or ("whip" if (k % whip_every == whip_every - 1) else ("zoom_cut" if k % 2 else "cut"))
            if k == 0:
                trans = "cut"
            focus = tuple(v["focus"]) if v.get("focus") else None
            markers = [Marker(m["label"], tuple(m["pos"]), b_start + 0.3 + 0.35 * j)
                       for j, m in enumerate(v.get("markers") or [])]
            if motion == "punch" and not focus:
                motion = "push"
            pops = []
            if sc.get("pop"):
                at = b_start + 0.3
                for w in beat_words[k]:
                    if re.sub(r"[^a-z0-9]", "", w.text.lower()) == re.sub(r"[^a-z0-9]", "", sc["pop"].lower()):
                        at = w.start
                        break
                pops.append(Pop(sc["pop"], at))
                sfx_events.append(("pop", at, -20.0))
            arrow = None
            if v.get("arrow"):
                (ax, ay), (bx, by) = v["arrow"]
                arrow = Arrow((ax, ay), (bx, by), b_start + 0.4)
                sfx_events.append(("swipe", b_start + 0.35, -22.0))
            if k in indicator_at and focus and callouts_with_sound < 3:
                callouts_with_sound += 1
                sfx_events.append(("click", b_start + 0.25, -22.0))
            for mk in markers:
                sfx_events.append(("click", mk.at, -22.0))
            if trans == "whip":
                sfx_events.append(("whoosh", b_start - 0.15, -19.0))
            if witty and not comic_used:
                comic_used = True
                sfx_events.append((rng.choice(["boing", "record_scratch"]), b_start + 0.05, -17.0))
            if sc.get("card_text") and not img and not chime_used:
                chime_used = True
                sfx_events.append(("chime", b_start + 0.1, -18.0))
            clip, clip_from, clip_dir = None, 0.0, 1
            ck = clips.get(img_key) if img_key else None
            if k == len(scenes) - 1 and scenes[0].get("image") and clips.get((vis["beats"].get(scenes[0]["id"]) or {}).get("image") or scenes[0]["image"]):
                # loop: play the opening clip backwards so the last frame IS the first frame
                first_key = (vis["beats"].get(scenes[0]["id"]) or {}).get("image") or scenes[0]["image"]
                clip, clip_from, clip_dir = Path(clips[first_key]["path"]), b_end - b_start, -1
            elif ck and not markers and img:
                clip, clip_from = Path(ck["path"]), clip_cursor.get(img_key, 0.0)
                clip_cursor[img_key] = clip_from + (b_end - b_start)
            if clip and arrow:
                arrow = None                          # still-based overlays would drift off target
                sfx_events = [e for e in sfx_events if not (e[0] == "swipe" and abs(e[1] - (b_start + 0.35)) < 1e-6)]
            beats.append(Beat(start=b_start, end=b_end, image=img, focus=focus, motion=motion, transition=trans,
                              clip=clip, clip_from=clip_from, clip_dir=clip_dir,
                              callout_label=(sc.get("callout") or "") if (focus and k in indicator_at and not clip) else None,
                              indicator=indicator_at.get(k, "ring"),
                              callout_at=b_start + 0.25, pops=pops, arrow=arrow,
                              card_text=(sc.get("card_text") or "") if not img else "", markers=markers,
                              # no opening text card: it would pop in on every replay and break the loop
                              hook_text=""))
        boxes = [b.focus for b in beats if b.focus]
        y_cap = 1360 if any(0.50 <= f[1] <= 0.70 for f in boxes) else 1200
        video = render_beats(beats, end, d / "video.mp4", self.pal, caption_y=y_cap)
        lib = build_library()
        sfx = [(lib[name], max(0.0, t), gain) for name, t, gain in sfx_events if name in lib]
        music = pick_music(job_id)
        audio = A.mix_audio(A.AudioPlan(Path(voice["audio"]), music, music_gain_db=-17.0, sfx=sfx,
                                        loop=True), end, d / "mix.wav")
        ass = write_ass(words, d / "captions.ass", y_center=y_cap,
                        font=self.cfg.channel["style"]["caption_font"],
                        font_size=self.cfg.channel["style"]["caption_size"])
        final = A.finalize(video, audio, ass, d / "final.mp4")
        return {"video": str(final), "duration": end, "beats": len(beats), "music": str(music) if music else None}

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
        scenes = "\n".join(f"{i+1}. {s['narration']}" + (f"  _(pop: {s['pop']})_" if s.get('pop') else "") for i, s in enumerate(script["scenes"]))
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
            self.state.add_feedback(job_id, "approve", note)
        elif decision == "reject":
            self.state.set_job_status(job_id, "rejected", note)
            self.state.set_topic_status(job["topic_id"], "rejected")
            t = self.state.get_topic(job["topic_id"]) or {}
            notes = json.loads(t.get("notes") or "{}")
            notes["rejected_reason"] = note
            self.state.upsert_topic(job["topic_id"], "", notes=json.dumps(notes))
            self.state.add_feedback(job_id, "drop", note)
        elif decision == "fix":
            # Apply the owner's request with minimal edits; unchanged pictures/voice are reused from
            # build/<job>/prior (see _reuse_*), so a small fix costs cents, not a whole new video.
            d = self.build / job_id
            script = json.loads((d / "script.json").read_text())
            script.pop("_revised", None)
            fx = self._llm(P.OWNER_FIX.format(note=note, length_rule=json.dumps(self._length_rule()),
                                              script=json.dumps(script, ensure_ascii=False)),
                           job_id, "owner_fix", est=0.2, system=P.SYSTEM_WRITER,
                           model=self.cfg.pipeline["providers"]["llm"]["model_script"], max_tokens=12000).data or {}
            if not fx.get("scenes"):
                raise StageFailed("the fix could not be applied (no script returned)")
            fx["_revised"] = True
            fx["hook_scores"] = [hook_score(h) for h in fx.get("hooks", [])]
            self._validate_script(fx)
            (d / "script.json").write_text(json.dumps(fx, indent=2, ensure_ascii=False))
            arts = job["artifacts"]
            rv = dict(arts.get("review") or {})
            rv["script"] = fx                      # _restore must bring back the FIXED script
            rv.setdefault("content", {})
            self.state.finish_stage(job_id, "review", rv)
            self.state.set_job_status(job_id, "running")
            self.state.add_feedback(job_id, "fix", note)
            self.state.log(f"owner fix applied: {fx.get('change_summary', '')}", job_id=job_id)
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
