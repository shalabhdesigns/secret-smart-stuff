"""Spending guard. Every paid call asks the guard first; production pauses
before a configured limit would be crossed, never after."""
from __future__ import annotations

import time
from dataclasses import dataclass

from .state import State


class BudgetExceeded(RuntimeError):
    pass


@dataclass
class Limits:
    daily_usd: float
    monthly_usd: float
    per_video_usd: float
    per_video_override: dict | None = None     # {job_id: usd}: owner-approved exceptions for one video


def _month_start(now: float) -> float:
    lt = time.gmtime(now)
    return time.mktime((lt.tm_year, lt.tm_mon, 1, 0, 0, 0, 0, 0, -1))


def _ist_day_start(now: float) -> float:
    """Midnight IST today. The daily limit is per IST day: a rolling 24 h counted yesterday's late run against
    today's video and stopped its fix (30 Oct 2026)."""
    ist = 5.5 * 3600
    return (now + ist) // 86400 * 86400 - ist


class Budget:
    def __init__(self, state: State, limits: Limits):
        self.state, self.limits = state, limits

    def remaining(self, job_id: str | None = None) -> dict:
        now = time.time()
        ist_day = time.strftime("%Y-%m-%d", time.gmtime(now + 5.5 * 3600))
        month_key = time.strftime("%Y-%m", time.gmtime(now))
        extra = lambda k: float(self.state.get_setting(k) or 0)   # noqa: E731 - owner raised it in Telegram
        day = self.limits.daily_usd + extra(f"day_extra:{ist_day}") - self.state.spend_since(_ist_day_start(now))
        month = self.limits.monthly_usd + extra(f"month_extra:{month_key}") - self.state.spend_since(_month_start(now))
        cap = float((self.limits.per_video_override or {}).get(job_id or "", self.limits.per_video_usd))
        cap += extra(f"video_extra:{job_id}") if job_id else 0.0
        video = cap - (self.state.job_cost(job_id) if job_id else 0.0)
        return {"day": day, "month": month, "video": video}

    def authorize(self, est_usd: float, what: str, job_id: str | None = None) -> None:
        """Raise BudgetExceeded if spending `est_usd` would cross any limit."""
        rem = self.remaining(job_id)
        for scope, left in rem.items():
            if est_usd > left + 1e-9:
                self.state.log(f"budget stop: {what} needs ${est_usd:.3f}, {scope} left ${left:.3f}",
                               "warn", job_id)
                raise BudgetExceeded(f"{what}: ${est_usd:.3f} exceeds {scope} remaining ${left:.3f}")
