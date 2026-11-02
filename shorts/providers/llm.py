"""LLM access. Live: Anthropic Messages API over plain HTTPS. Dry-run: a fake
that returns clearly-labelled placeholder JSON so the pipeline can be tested
without spending anything."""
from __future__ import annotations

import json
import re
import time
from dataclasses import dataclass, field

import requests

API = "https://api.anthropic.com/v1/messages"


@dataclass
class LLMResult:
    text: str
    data: dict | list | None
    usd: float
    sources: list[dict] = field(default_factory=list)   # {url, title, cited_text}
    model: str = ""
    usage: dict = field(default_factory=dict)            # measured tokens + web searches (from the API response)


class LLMError(RuntimeError):
    pass


def extract_json(text: str):
    """Take the first JSON object/array from model text (models sometimes wrap it in prose)."""
    m = re.search(r"```(?:json)?\s*(\{.*\}|\[.*\])\s*```", text, re.S)
    raw = m.group(1) if m else None
    if raw is None:
        start = min([i for i in (text.find("{"), text.find("[")) if i >= 0], default=-1)
        if start < 0:
            raise LLMError("no JSON in model output")
        raw = text[start:]
        # trim trailing prose after the last closing bracket
        end = max(raw.rfind("}"), raw.rfind("]"))
        raw = raw[: end + 1]
    return json.loads(raw, strict=False)          # strict=False: tolerate raw newlines/tabs inside strings


class AnthropicLLM:
    def __init__(self, api_key: str, cfg: dict):
        self.key, self.cfg = api_key, cfg

    def _price(self, model: str, usage: dict, searches: int) -> float:
        pin, pout = self.cfg["prices"].get(model, [3.0, 15.0])
        usd = (usage.get("input_tokens", 0) / 1e6 * pin + usage.get("output_tokens", 0) / 1e6 * pout
               + usage.get("cache_creation_input_tokens", 0) / 1e6 * pin * 1.25      # prompt-cache write
               + usage.get("cache_read_input_tokens", 0) / 1e6 * pin * 0.10)         # prompt-cache read
        return usd + searches * self.cfg.get("web_search_usd_each", 0.01)

    def ask(self, prompt: str, system: str = "", model: str | None = None, json_out: bool = True,
            web_search: bool = False, max_tokens: int = 4000, images: list[bytes] | None = None,
            retries: int = 3, temperature: float | None = None, cache_system: bool = False) -> LLMResult:
        model = model or self.cfg["model_routine"]
        content: list[dict] = []
        for img in images or []:
            import base64
            content.append({"type": "image", "source": {"type": "base64", "media_type": "image/jpeg" if img[:3] == b"\xff\xd8\xff" else "image/png",
                                                          "data": base64.b64encode(img).decode()}})
        content.append({"type": "text", "text": prompt})
        body: dict = {"model": model, "max_tokens": max_tokens,
                      "messages": [{"role": "user", "content": content}]}
        if system:
            # cache_system: the same long system prompt is reused across a writers'-room run -> 90% cheaper reads
            body["system"] = ([{"type": "text", "text": system, "cache_control": {"type": "ephemeral"}}]
                              if cache_system else system)
        if temperature is not None:
            body["temperature"] = temperature
        if web_search:
            body["tools"] = [{"type": self.cfg["web_search_tool"], "name": "web_search",
                              "max_uses": self.cfg.get("max_searches_per_video", 6)}]
        headers = {"x-api-key": self.key, "anthropic-version": "2023-06-01",
                   "content-type": "application/json"}
        last = None
        blocks: list[dict] = []
        usage_total = {"input_tokens": 0, "output_tokens": 0, "cache_creation_input_tokens": 0,
                       "cache_read_input_tokens": 0}
        searches = 0
        attempt = 0
        continuations = 0
        json_fail = 0
        while attempt < retries:
            r = requests.post(API, headers=headers, json=body, timeout=300)
            if r.status_code in (429, 500, 502, 503, 529):
                last = r.text[:200]
                time.sleep(5 * (2 ** attempt))
                attempt += 1
                continue
            if r.status_code == 400 and "temperature" in r.text and "temperature" in body:
                body.pop("temperature")                     # some models fix sampling; retry without it
                continue
            if r.status_code != 200:
                raise LLMError(f"Anthropic {r.status_code}: {r.text[:300]}")
            msg = r.json()
            u = msg.get("usage", {})
            usage_total["input_tokens"] += u.get("input_tokens", 0)
            usage_total["output_tokens"] += u.get("output_tokens", 0)
            usage_total["cache_creation_input_tokens"] += u.get("cache_creation_input_tokens", 0) or 0
            usage_total["cache_read_input_tokens"] += u.get("cache_read_input_tokens", 0) or 0
            searches += (u.get("server_tool_use") or {}).get("web_search_requests", 0)
            blocks += msg.get("content", [])
            stop = msg.get("stop_reason")
            if stop == "pause_turn" and continuations < 4:
                # long server-tool turn: send the partial turn back so the model continues
                body["messages"] = body["messages"] + [{"role": "assistant", "content": msg["content"]}]
                continuations += 1
                continue
            if stop == "max_tokens":
                if body["max_tokens"] < 32000:
                    # out of room: start this request again once with double the limit
                    body["max_tokens"] = min(32000, body["max_tokens"] * 2)
                    body["messages"] = body["messages"][:1]
                    blocks, continuations = [], 0
                    continue
                raise LLMError(f"model hit max_tokens ({body['max_tokens']}) even after retry")
            text_parts, sources = [], []
            for block in blocks:
                if block.get("type") == "text":
                    text_parts.append(block["text"])
                    for c in block.get("citations") or []:
                        if c.get("url"):
                            sources.append({"url": c["url"], "title": c.get("title", ""),
                                            "cited_text": c.get("cited_text", "")})
            text = "".join(text_parts)
            try:
                data = extract_json(text) if json_out else None
            except (ValueError, LLMError) as e:
                # malformed JSON (e.g. an unescaped quote inside Hindi dialogue): ask again, a few times
                json_fail += 1
                if json_fail > 2:
                    raise LLMError(f"model returned invalid JSON 3 times: {e}")
                body["messages"] = body["messages"][:1]
                body["messages"][0]["content"][-1]["text"] = (prompt + "\n\nIMPORTANT: return strictly valid JSON. "
                                                              "Escape any double quote inside a string as \\\".")
                blocks, continuations = [], 0
                continue
            usd = self._price(model, usage_total, searches)
            return LLMResult(text=text, data=data, usd=usd, sources=sources, model=model,
                             usage={**usage_total, "web_searches": searches, "model": model})
        raise LLMError(f"Anthropic kept failing: {last}")


class FakeLLM:
    """Dry-run stand-in. Returns a fixed, obviously-fake script so the rest of
    the pipeline (voice, render, QA, packaging) can be exercised end to end."""

    def ask(self, prompt: str, **kw) -> LLMResult:
        task = re.search(r"TASK:\s*(\w+)", prompt)
        task = task.group(1) if task else "unknown"
        data = FAKE_RESPONSES.get(task, {"note": "fake"})
        return LLMResult(text=json.dumps(data), data=json.loads(json.dumps(data)), usd=0.0,
                         sources=[{"url": "https://example.com/fake-source", "title": "FAKE SOURCE",
                                   "cited_text": "dry run"}], model="fake")


FAKE_RESPONSES: dict = {
    "ideas": {"ideas": [
        {"object": "railway track stones", "pillar": "walk_past",
         "question": "Why are there stones beside railway tracks?", "angle": "the wrong guess is decoration"},
        {"object": "jeans coin pocket", "pillar": "why_detail",
         "question": "Why do jeans have a tiny pocket?", "angle": "it was never meant for coins"},
    ]},
    "score": {"scores": {"audience": 8, "novelty": 7, "hook": 8, "story": 7, "cost": 9, "policy": 10},
              "total": 82, "reason": "dry run"},
    "script": {
        "title": "[DRY RUN] Why are there stones beside railway tracks?",
        "thumb_text": "NOT DECORATION", "hook_card": "HIDDEN JOB",
        "hooks": ["Why are there sharp stones beside every railway track?",
                  "Those stones under the rails are not decoration. What are they for?",
                  "Why do trains run on a bed of broken rock?",
                  "What are the stones along railway tracks actually doing?",
                  "Why is every railway line buried in gravel?"],
        "chosen_hook": 0,
        "motions": {"img1": "slow push-in along the rails", "img2": "stones settle as a train passes"},
        "images": {"img1": "railway track on crushed stone ballast, low angle",
                   "img2": "close-up of angular grey crushed granite stones",
                   "img3": "concrete sleeper resting on stones, side view",
                   "img4": "railway track after rain, water draining between stones",
                   "img5": "old railway line with muddy, sunken track and no stones",
                   "img6": "maintenance machine tamping stones under a track"},
        "scenes": [
            {"id": "b1", "narration": "Why are there sharp stones beside every railway track?", "image": "img1", "focus": "the crushed stones beside the rail", "motion": "push", "transition": "cut", "callout": None, "pop": None, "arrow": None, "card_text": None, "sfx": None},
            {"id": "b2", "narration": "They are not decoration.", "image": "img2", "focus": "the sharp edges of the stones", "motion": "punch", "transition": "zoom_cut", "callout": "sharp edges", "pop": None, "arrow": None, "card_text": None, "sfx": "tick"},
            {"id": "b3", "narration": "Every train pushes the track sideways.", "image": "img3", "focus": "the concrete sleeper", "motion": "drift", "transition": "cut", "callout": "sleeper", "pop": None, "arrow": {"from": "the wheel", "to": "the sleeper"}, "card_text": None, "sfx": None},
            {"id": "b4", "narration": "The stones lock together and hold it.", "image": "img2", "focus": "stones wedged against each other", "motion": "punch", "transition": "whip", "callout": "interlock", "pop": "LOCK", "arrow": None, "card_text": None, "sfx": None},
            {"id": "b5", "narration": "That is why they are angular, not round.", "image": "img2", "focus": "a single angular stone", "motion": "pull", "transition": "cut", "callout": None, "pop": None, "arrow": None, "card_text": None, "sfx": None},
            {"id": "b6", "narration": "Round pebbles would roll apart.", "image": "img5", "focus": "the sunken muddy track", "motion": "push", "transition": "zoom_cut", "callout": "no support", "pop": None, "arrow": None, "card_text": None, "sfx": None},
            {"id": "b7", "narration": "The bed also drains rain away.", "image": "img4", "focus": "water draining between the stones", "motion": "drift", "transition": "cut", "callout": "drains", "pop": None, "arrow": None, "card_text": None, "sfx": None},
            {"id": "b8", "narration": "Wet ground turns to mud, and rails sink.", "image": "img5", "focus": "mud beside the rail", "motion": "punch", "transition": "whip", "callout": None, "pop": "MUD", "arrow": None, "card_text": None, "sfx": None},
            {"id": "b9", "narration": "Stones keep the sleepers dry and level.", "image": "img4", "focus": "the level rail", "motion": "pull", "transition": "cut", "callout": None, "pop": None, "arrow": None, "card_text": None, "sfx": None},
            {"id": "b10", "narration": "Machines shake them tight again every few years.", "image": "img6", "focus": "the tamping arms of the machine", "motion": "drift", "transition": "zoom_cut", "callout": "tamping", "pop": None, "arrow": None, "card_text": None, "sfx": None},
            {"id": "b11", "narration": "Locks, drains, holds.", "image": None, "focus": None, "motion": "hold", "transition": "cut", "callout": None, "pop": None, "arrow": None, "card_text": "LOCKS · DRAINS · HOLDS", "sfx": "ding"},
            {"id": "b12", "narration": "So next time you are on a platform...", "image": "img1", "focus": "the crushed stones beside the rail", "motion": "pull", "transition": "whip", "callout": None, "pop": None, "arrow": None, "card_text": None, "sfx": None},
        ],
        "facts": [{"claim": "Ballast holds sleepers in place", "sources": ["https://example.com/fake-source"], "main": True},
                  {"claim": "Ballast drains water", "sources": ["https://example.com/fake-source"]}],
        "description": "[DRY RUN] Railway ballast explained.",
        "hashtags": ["#railway", "#design"], "affiliate_product": None,
    },
    "review": {"scores": {"hook": 2, "payoff": 2, "visual_match": 2, "accuracy": 1, "originality": 1},
               "total": 8, "problems": [], "verdict": "pass"},
    "markers": {"markers": [{"label": "1", "x": 0.5, "y": 0.4, "confidence": "high"}]},
    "clipcheck": {"ok": True, "morphing": False, "text_or_logo": False, "faces": False, "shows_action": True,
                  "problems": ""},
    "match": {"matches": True, "missing": "", "better_prompt": ""},
    "postmortem": {"verdict": "above", "summary": "dry run", "what_worked": ["hook"], "what_didnt": ["b4 slow"],
                   "drop_points": [{"beat": "b4", "second": 10, "why": "repeat"}],
                   "lessons": [{"area": "pacing", "lesson": "cut repeats", "confidence": "hypothesis"}],
                   "topic_signal": "keep"},
    "realism": {"ok": True, "recognisable": True, "ai_tells": [], "wrong_parts": [], "shows_detail": True, "retry_prompt": ""},
    "critic": {"scores": {"hook_curiosity": 4, "visual_credibility": 4, "image_word_match": 4, "payoff": 4,
                          "flow_pacing": 4, "accuracy": 4, "loop": 4, "rewatch": 4, "share": 4},
               "blocking": [], "improvements": [], "retention_risks": [], "unshowable": False,
               "verdict": "send", "summary": "dry run"},
    "locate": {"found": True, "x": 0.5, "y": 0.55, "w": 0.4, "h": 0.2,
               "has_text_or_logo": False, "artifacts": False},
}
