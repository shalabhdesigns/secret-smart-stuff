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


def _month_start(now: float) -> float:
    lt = time.gmtime(now)
    return time.mktime((lt.tm_year, lt.tm_mon, 1, 0, 0, 0, 0, 0, -1))


class Budget:
    def __init__(self, state: State, limits: Limits):
        self.state, self.limits = state, limits

    def remaining(self, job_id: str | None = None) -> dict:
        now = time.time()
        day = self.limits.daily_usd - self.state.spend_since(now - 86400)
        month = self.limits.monthly_usd - self.state.spend_since(_month_start(now))
        video = self.limits.per_video_usd - (self.state.job_cost(job_id) if job_id else 0.0)
        return {"day": day, "month": month, "video": video}

    def authorize(self, est_usd: float, what: str, job_id: str | None = None) -> None:
        """Raise BudgetExceeded if spending `est_usd` would cross any limit."""
        rem = self.remaining(job_id)
        for scope, left in rem.items():
            if est_usd > left + 1e-9:
                self.state.log(f"budget stop: {what} needs ${est_usd:.3f}, {scope} left ${left:.3f}",
                               "warn", job_id)
                raise BudgetExceeded(f"{what}: ${est_usd:.3f} exceeds {scope} remaining ${left:.3f}")
