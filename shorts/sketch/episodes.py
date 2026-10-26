"""Episode records (in the state DB) and the publishing calendar.

Status flow:  writing -> review -> (revising -> review)* -> approved -> scheduled -> published
              any -> rejected | failed
One episode per day; each is made LEAD_DAYS ahead of its publish slot so there is time for revisions.
"""
from __future__ import annotations

import datetime as dt
import json
import time
from zoneinfo import ZoneInfo

IST = ZoneInfo("Asia/Kolkata")
SLOT_IST = (19, 30)          # 7:30 PM IST default (docs/METADATA.md); change with set_slot
LEAD_DAYS = 3

SCHEMA = """
CREATE TABLE IF NOT EXISTS episodes (
  id TEXT PRIMARY KEY,
  number INTEGER,
  status TEXT,
  slot TEXT,                 -- planned publish time, ISO UTC
  title TEXT,
  premise TEXT,
  plan TEXT,                 -- JSON written plan
  meta TEXT,                 -- JSON YouTube metadata
  version INTEGER DEFAULT 0,
  video_asset TEXT,          -- release asset name of the current version
  qa TEXT,                   -- JSON QA result
  yt_video_id TEXT,
  history TEXT DEFAULT '[]', -- JSON list of {t, event, note}
  cost REAL DEFAULT 0,
  created REAL,
  updated REAL
);
"""


EXTRA_COLS = {"hold": "INTEGER DEFAULT 0"}     # columns added after the first release (migrated in place)


def init(state) -> None:
    with state.tx() as c:
        c.executescript(SCHEMA)
        have = {r[1] for r in c.execute("PRAGMA table_info(episodes)").fetchall()}
        for col, typ in EXTRA_COLS.items():
            if col not in have:
                c.execute(f"ALTER TABLE episodes ADD COLUMN {col} {typ}")


def _row(r) -> dict | None:
    if not r:
        return None
    d = dict(r)
    for k in ("plan", "meta", "qa", "history"):
        if d.get(k):
            d[k] = json.loads(d[k])
    return d


def get(state, ep_id: str) -> dict | None:
    init(state)
    return _row(state.db.execute("SELECT * FROM episodes WHERE id=?", (ep_id,)).fetchone())


def all_eps(state, statuses: tuple[str, ...] | None = None) -> list[dict]:
    init(state)
    rows = state.db.execute("SELECT * FROM episodes ORDER BY number").fetchall()
    out = [_row(r) for r in rows]
    return [e for e in out if not statuses or e["status"] in statuses]


def save(state, ep: dict) -> None:
    init(state)
    ep = dict(ep)
    ep["updated"] = time.time()
    ep.setdefault("created", ep["updated"])
    for k in ("plan", "meta", "qa", "history"):
        if k in ep and not isinstance(ep[k], str) and ep[k] is not None:
            ep[k] = json.dumps(ep[k], ensure_ascii=False)
    cols = list(ep)
    with state.tx() as c:
        c.execute(f"INSERT INTO episodes ({','.join(cols)}) VALUES ({','.join('?' * len(cols))}) "
                  f"ON CONFLICT(id) DO UPDATE SET {','.join(f'{k}=excluded.{k}' for k in cols if k != 'id')}",
                  [ep[k] for k in cols])


def log(ep: dict, event: str, note: str = "") -> None:
    h = ep.get("history") or []
    if isinstance(h, str):
        h = json.loads(h)
    h.append({"t": dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds"), "event": event, "note": note[:500]})
    ep["history"] = h


def slot_time(state) -> tuple[int, int]:
    v = state.get_setting("publish_slot_ist")
    if v and ":" in v:
        h, m = v.split(":")
        return int(h), int(m)
    return SLOT_IST


def next_free_slot(state, earliest: dt.datetime | None = None) -> dt.datetime:
    """First daily slot (IST) that is not already taken and is at least LEAD_DAYS days out (or after `earliest`)."""
    now = dt.datetime.now(IST)
    h, m = slot_time(state)
    taken = {e["slot"][:10] for e in all_eps(state) if e.get("slot") and e["status"] not in ("rejected", "failed")}
    day = (earliest.astimezone(IST) if earliest else now + dt.timedelta(days=LEAD_DAYS)).date()
    while True:
        cand = dt.datetime(day.year, day.month, day.day, h, m, tzinfo=IST)
        if cand > now + dt.timedelta(minutes=30) and cand.astimezone(dt.timezone.utc).isoformat()[:10] not in taken:
            return cand.astimezone(dt.timezone.utc)
        day += dt.timedelta(days=1)


def pipeline_days_covered(state) -> int:
    """How many of the next LEAD_DAYS+1 daily slots already have an episode (any live status)."""
    live = [e for e in all_eps(state) if e["status"] in ("writing", "review", "revising", "approved", "scheduled")]
    return len(live)


def next_number(state) -> int:
    """Dropped or failed episodes don't use up a number: their replacement takes it."""
    eps = [e for e in all_eps(state) if e["status"] not in ("rejected", "failed")]
    return max([1] + [e["number"] for e in eps]) + 1        # Ep 1 is the pilot


def new_id(state, number: int) -> str:
    base = f"ep{number:03d}"
    taken = {e["id"] for e in all_eps(state)}
    if base not in taken:
        return base
    return next(f"{base}{c}" for c in "bcdefghijklmnopqrstuvwxyz" if f"{base}{c}" not in taken)


def fmt_ist(iso_utc: str) -> str:
    t = dt.datetime.fromisoformat(iso_utc.replace("Z", "+00:00")).astimezone(IST)
    return t.strftime("%a %d %b, %I:%M %p IST").replace(" 0", " ")
