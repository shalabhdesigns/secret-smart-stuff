"""Load YAML config + environment secrets into one object."""
from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]


@dataclass
class Config:
    channel: dict
    pipeline: dict
    root: Path = ROOT

    @property
    def live(self) -> bool:
        return self.pipeline.get("mode") == "live"

    def path(self, key: str) -> Path:
        p = self.root / self.pipeline["paths"][key]
        # Dry-run data lives in its own database, so test runs never mix with real topics/jobs.
        if key == "state_db" and not self.live:
            p = p.with_name("dryrun.db")
        return p

    def secret(self, name: str, required: bool = True) -> str | None:
        val = os.environ.get(name)
        if required and not val:
            raise RuntimeError(f"missing environment variable {name} (set it as a GitHub secret)")
        return val


def load(root: Path = ROOT, mode: str | None = None) -> Config:
    channel = yaml.safe_load((root / "config" / "channel.yaml").read_text())
    pipeline = yaml.safe_load((root / "config" / "pipeline.yaml").read_text())
    env_mode = mode or os.environ.get("SHORTS_MODE")
    if env_mode:
        pipeline["mode"] = env_mode
    return Config(channel=channel, pipeline=pipeline, root=root)
