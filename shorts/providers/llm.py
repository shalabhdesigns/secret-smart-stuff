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
    return json.loads(raw)


class AnthropicLLM:
    def __init__(self, api_key: str, cfg: dict):
        self.key, self.cfg = api_key, cfg

    def _price(self, model: str, usage: dict, searches: int) -> float:
        pin, pout = self.cfg["prices"].get(model, [3.0, 15.0])
        usd = usage.get("input_tokens", 0) / 1e6 * pin + usage.get("output_tokens", 0) / 1e6 * pout
        return usd + searches * self.cfg.get("web_search_usd_each", 0.01)

    def ask(self, prompt: str, system: str = "", model: str | None = None, json_out: bool = True,
            web_search: bool = False, max_tokens: int = 4000, images: list[bytes] | None = None,
            retries: int = 3) -> LLMResult:
        model = model or self.cfg["model_routine"]
        content: list[dict] = []
        for img in images or []:
            import base64
            content.append({"type": "image", "source": {"type": "base64", "media_type": "image/png",
                                                          "data": base64.b64encode(img).decode()}})
        content.append({"type": "text", "text": prompt})
        body: dict = {"model": model, "max_tokens": max_tokens,
                      "messages": [{"role": "user", "content": content}]}
        if system:
            body["system"] = system
        if web_search:
            body["tools"] = [{"type": self.cfg["web_search_tool"], "name": "web_search",
                              "max_uses": self.cfg.get("max_searches_per_video", 6)}]
        headers = {"x-api-key": self.key, "anthropic-version": "2023-06-01",
                   "content-type": "application/json"}
        last = None
        blocks: list[dict] = []
        usage_total = {"input_tokens": 0, "output_tokens": 0}
        searches = 0
        attempt = 0
        continuations = 0
        while attempt < retries:
            r = requests.post(API, headers=headers, json=body, timeout=300)
            if r.status_code in (429, 500, 502, 503, 529):
                last = r.text[:200]
                time.sleep(5 * (2 ** attempt))
                attempt += 1
                continue
            if r.status_code != 200:
                raise LLMError(f"Anthropic {r.status_code}: {r.text[:300]}")
            msg = r.json()
            u = msg.get("usage", {})
            usage_total["input_tokens"] += u.get("input_tokens", 0)
            usage_total["output_tokens"] += u.get("output_tokens", 0)
            searches += (u.get("server_tool_use") or {}).get("web_search_requests", 0)
            blocks += msg.get("content", [])
            stop = msg.get("stop_reason")
            if stop == "pause_turn" and continuations < 4:
                # long server-tool turn: send the partial turn back so the model continues
                body["messages"] = body["messages"] + [{"role": "assistant", "content": msg["content"]}]
                continuations += 1
                continue
            if stop == "max_tokens":
                raise LLMError(f"model hit max_tokens ({max_tokens}); raise the limit for this step")
            text_parts, sources = [], []
            for block in blocks:
                if block.get("type") == "text":
                    text_parts.append(block["text"])
                    for c in block.get("citations") or []:
                        if c.get("url"):
                            sources.append({"url": c["url"], "title": c.get("title", ""),
                                            "cited_text": c.get("cited_text", "")})
            text = "".join(text_parts)
            data = extract_json(text) if json_out else None
            usd = self._price(model, usage_total, searches)
            return LLMResult(text=text, data=data, usd=usd, sources=sources, model=model)
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
        "hooks": ["Those stones next to every railway track are not decoration.",
                  "You've seen these stones a thousand times. Here's their job."],
        "chosen_hook": 0,
        "scenes": [
            {"id": "s1", "type": "hero", "narration": "Those stones next to every railway track are not decoration.",
             "on_screen_text": "NOT DECORATION", "image_prompt": "railway track with crushed stone ballast",
             "callouts": [{"target": "the crushed stones", "label": "crushed stone"}]},
            {"id": "s2", "type": "detail", "narration": "Every time a train passes, the sleepers try to shift.",
             "image_prompt": "close-up of a concrete railway sleeper on stones", "callouts": []},
            {"id": "s3", "type": "detail", "narration": "These sharp, jagged stones lock together and hold them in place.",
             "image_prompt": "macro of angular crushed granite stones", "callouts": [
                 {"target": "the sharp stone edges", "label": "edges interlock"}]},
            {"id": "s4", "type": "context", "narration": "They also let rainwater drain away, so the track never sits in mud.",
             "image_prompt": "railway track after rain, water draining through stones", "callouts": []},
            {"id": "s5", "type": "blueprint_card", "narration": "So next time you're on a platform, look down. That gravel is doing a lot of work.",
             "card_text": "LOCKS · DRAINS · HOLDS", "callouts": []},
        ],
        "facts": [{"claim": "Ballast holds sleepers in place", "sources": ["https://example.com/fake-source"]},
                  {"claim": "Ballast drains water", "sources": ["https://example.com/fake-source"]}],
        "description": "[DRY RUN] Railway ballast explained.",
        "hashtags": ["#railway", "#design"],
    },
    "review": {"scores": {"hook": 2, "payoff": 2, "visual_match": 2, "accuracy": 1, "originality": 1},
               "total": 8, "problems": [], "verdict": "pass"},
    "locate": {"found": True, "x": 0.5, "y": 0.55, "w": 0.4, "h": 0.2,
               "has_text_or_logo": False, "artifacts": False},
}
