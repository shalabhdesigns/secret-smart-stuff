"""Persistent state: topics, jobs, costs and uploads in one SQLite file.

Design goals
- Every stage writes its result here, so an interrupted run resumes from the
  last finished stage instead of starting over (and paying twice).
- Idempotency keys stop the same topic being produced or uploaded twice.
- Plain SQLite: no server, works locally and on GitHub Actions (the file is
  persisted between runs by the workflow).
"""
from __future__ import annotations

import json
import sqlite3
import time
from contextlib import contextmanager
from pathlib import Path
from typing import Any, Iterator

SCHEMA = """
CREATE TABLE IF NOT EXISTS topics (
    id            TEXT PRIMARY KEY,          -- stable slug/hash of the idea
    title         TEXT NOT NULL,
    pillar        TEXT,
    status        TEXT NOT NULL DEFAULT 'discovered',
    score         REAL,
    score_detail  TEXT,                      -- JSON rubric breakdown
    evidence      TEXT,                      -- JSON list of {url, note, seen_at, confidence}
    created_at    REAL NOT NULL,
    updated_at    REAL NOT NULL,
    notes         TEXT
);

CREATE TABLE IF NOT EXISTS jobs (
    id            TEXT PRIMARY KEY,          -- job id = topic id + version
    topic_id      TEXT NOT NULL REFERENCES topics(id),
    stage         TEXT NOT NULL,             -- last stage that FINISHED
    status        TEXT NOT NULL,             -- running | done | failed | review | approved | rejected | published
    attempts      INTEGER NOT NULL DEFAULT 0,
    artifacts     TEXT NOT NULL DEFAULT '{}',-- JSON: stage -> file paths / ids
    error         TEXT,
    created_at    REAL NOT NULL,
    updated_at    REAL NOT NULL
);

CREATE TABLE IF NOT EXISTS costs (
    id            INTEGER PRIMARY KEY AUTOINCREMENT,
    job_id        TEXT,
    provider      TEXT NOT NULL,
    item          TEXT NOT NULL,             -- e.g. tts_chars, image, video_seconds, llm_tokens
    quantity      REAL NOT NULL,
    usd           REAL NOT NULL,
    estimated     INTEGER NOT NULL DEFAULT 1,-- 1 = our estimate, 0 = provider-reported
    at            REAL NOT NULL
);

CREATE TABLE IF NOT EXISTS uploads (
    job_id        TEXT PRIMARY KEY,
    idempotency   TEXT UNIQUE NOT NULL,      -- sha256 of final mp4; blocks duplicate uploads
    video_id      TEXT,
    url           TEXT,
    privacy       TEXT,
    publish_at    TEXT,
    status        TEXT NOT NULL,             -- started | uploaded | processed | failed
    at            REAL NOT NULL
);

CREATE TABLE IF NOT EXISTS metrics (
    video_id      TEXT NOT NULL,
    fetched_at    REAL NOT NULL,
    age_hours     REAL,
    data          TEXT NOT NULL,             -- JSON of whatever the API returned
    PRIMARY KEY (video_id, fetched_at)
);

CREATE TABLE IF NOT EXISTS settings (
    key           TEXT PRIMARY KEY,          -- e.g. telegram_chat_id, telegram_review_msg:<job>
    value         TEXT NOT NULL,
    at            REAL NOT NULL
);

CREATE TABLE IF NOT EXISTS feedback (
    id            INTEGER PRIMARY KEY AUTOINCREMENT,
    at            REAL NOT NULL,
    job_id        TEXT,
    decision      TEXT NOT NULL,             -- approve | fix | drop
    note          TEXT
);

CREATE TABLE IF NOT EXISTS features (
    job_id        TEXT PRIMARY KEY,          -- what the video was made of (for learning)
    data          TEXT NOT NULL,             -- JSON: pillar, hook formula, seconds, beats, wit, slot, ...
    at            REAL NOT NULL
);

CREATE TABLE IF NOT EXISTS experiments (
    id            TEXT PRIMARY KEY,          -- e.g. exp-001-publish-time
    data          TEXT NOT NULL,             -- JSON: hypothesis, arms, metric, min_n, status, result, decision
    at            REAL NOT NULL
);

CREATE TABLE IF NOT EXISTS assignments (
    experiment_id TEXT NOT NULL,
    job_id        TEXT NOT NULL,
    arm           TEXT NOT NULL,
    at            REAL NOT NULL,
    PRIMARY KEY (experiment_id, job_id)
);

CREATE TABLE IF NOT EXISTS revenue (
    period        TEXT NOT NULL,             -- YYYY-MM (owner-entered) or YYYY-MM-DD (API)
    video_id      TEXT NOT NULL DEFAULT '',  -- '' = whole channel
    usd           REAL NOT NULL,
    source        TEXT NOT NULL,             -- owner | youtube_api
    at            REAL NOT NULL,
    PRIMARY KEY (period, video_id, source)
);

CREATE TABLE IF NOT EXISTS channel_daily (
    day           TEXT PRIMARY KEY,          -- YYYY-MM-DD (YouTube Analytics, channel totals)
    data          TEXT NOT NULL,
    at            REAL NOT NULL
);

CREATE TABLE IF NOT EXISTS video_detail (
    video_id      TEXT NOT NULL,
    kind          TEXT NOT NULL,             -- retention | traffic | demographics
    data          TEXT NOT NULL,
    at            REAL NOT NULL,
    PRIMARY KEY (video_id, kind)
);

CREATE TABLE IF NOT EXISTS events (
    id            INTEGER PRIMARY KEY AUTOINCREMENT,
    at            REAL NOT NULL,
    level         TEXT NOT NULL,
    job_id        TEXT,
    message       TEXT NOT NULL
);
"""

TOPIC_STATUSES = (
    "discovered", "shortlisted", "approved", "in_production",
    "published", "rejected", "awaiting_analysis",
)


class State:
    def __init__(self, path: str | Path):
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.db = sqlite3.connect(self.path)
        self.db.row_factory = sqlite3.Row
        self.db.executescript(SCHEMA)
        self.db.commit()

    @contextmanager
    def tx(self) -> Iterator[sqlite3.Connection]:
        try:
            yield self.db
            self.db.commit()
        except Exception:
            self.db.rollback()
            raise

    # ---------- events ----------
    def log(self, message: str, level: str = "info", job_id: str | None = None) -> None:
        with self.tx() as db:
            db.execute(
                "INSERT INTO events(at, level, job_id, message) VALUES (?,?,?,?)",
                (time.time(), level, job_id, message),
            )

    # ---------- topics ----------
    def upsert_topic(self, topic_id: str, title: str, **fields: Any) -> None:
        now = time.time()
        for k in ("score_detail", "evidence"):
            if k in fields and not isinstance(fields[k], str):
                fields[k] = json.dumps(fields[k])
        existing = self.get_topic(topic_id)
        with self.tx() as db:
            if existing is None:
                cols = ["id", "title", "created_at", "updated_at", *fields.keys()]
                vals = [topic_id, title, now, now, *fields.values()]
                db.execute(
                    f"INSERT INTO topics({','.join(cols)}) VALUES ({','.join('?' * len(cols))})",
                    vals,
                )
            elif fields:
                sets = ",".join(f"{k}=?" for k in fields) + ",updated_at=?"
                db.execute(f"UPDATE topics SET {sets} WHERE id=?", (*fields.values(), now, topic_id))

    def set_topic_status(self, topic_id: str, status: str) -> None:
        if status not in TOPIC_STATUSES:
            raise ValueError(f"unknown topic status {status!r}")
        self.upsert_topic(topic_id, "", status=status)

    def get_topic(self, topic_id: str) -> dict | None:
        row = self.db.execute("SELECT * FROM topics WHERE id=?", (topic_id,)).fetchone()
        return dict(row) if row else None

    def topics(self, status: str | None = None) -> list[dict]:
        if status:
            rows = self.db.execute(
                "SELECT * FROM topics WHERE status=? ORDER BY score DESC", (status,)
            )
        else:
            rows = self.db.execute("SELECT * FROM topics ORDER BY updated_at DESC")
        return [dict(r) for r in rows]

    # ---------- jobs ----------
    def start_job(self, job_id: str, topic_id: str) -> dict:
        """Create the job if new; otherwise return the existing one (resume)."""
        job = self.get_job(job_id)
        if job:
            return job
        now = time.time()
        with self.tx() as db:
            db.execute(
                "INSERT INTO jobs(id, topic_id, stage, status, created_at, updated_at) "
                "VALUES (?,?,?,?,?,?)",
                (job_id, topic_id, "created", "running", now, now),
            )
        return self.get_job(job_id)  # type: ignore[return-value]

    def get_job(self, job_id: str) -> dict | None:
        row = self.db.execute("SELECT * FROM jobs WHERE id=?", (job_id,)).fetchone()
        if not row:
            return None
        job = dict(row)
        job["artifacts"] = json.loads(job["artifacts"] or "{}")
        return job

    def finish_stage(self, job_id: str, stage: str, artifacts: dict | None = None) -> None:
        job = self.get_job(job_id)
        if job is None:
            raise KeyError(job_id)
        merged = job["artifacts"]
        if artifacts:
            merged[stage] = artifacts
        with self.tx() as db:
            db.execute(
                "UPDATE jobs SET stage=?, artifacts=?, error=NULL, updated_at=? WHERE id=?",
                (stage, json.dumps(merged), time.time(), job_id),
            )

    def set_job_status(self, job_id: str, status: str, error: str | None = None) -> None:
        with self.tx() as db:
            db.execute(
                "UPDATE jobs SET status=?, error=?, updated_at=? WHERE id=?",
                (status, error, time.time(), job_id),
            )

    def bump_attempt(self, job_id: str) -> int:
        with self.tx() as db:
            db.execute("UPDATE jobs SET attempts=attempts+1 WHERE id=?", (job_id,))
        return self.get_job(job_id)["attempts"]  # type: ignore[index]

    def jobs(self, status: str | None = None) -> list[dict]:
        q = "SELECT id FROM jobs" + (" WHERE status=?" if status else "") + " ORDER BY created_at"
        rows = self.db.execute(q, (status,) if status else ()).fetchall()
        return [self.get_job(r["id"]) for r in rows]  # type: ignore[misc]

    # ---------- costs ----------
    def add_cost(self, provider: str, item: str, quantity: float, usd: float,
                 job_id: str | None = None, estimated: bool = True) -> None:
        with self.tx() as db:
            db.execute(
                "INSERT INTO costs(job_id, provider, item, quantity, usd, estimated, at) "
                "VALUES (?,?,?,?,?,?,?)",
                (job_id, provider, item, quantity, usd, int(estimated), time.time()),
            )

    def spend_since(self, since_ts: float) -> float:
        row = self.db.execute("SELECT COALESCE(SUM(usd),0) s FROM costs WHERE at>=?", (since_ts,)).fetchone()
        return float(row["s"])

    def job_cost(self, job_id: str) -> float:
        row = self.db.execute("SELECT COALESCE(SUM(usd),0) s FROM costs WHERE job_id=?", (job_id,)).fetchone()
        return float(row["s"])

    # ---------- uploads ----------
    def upload_for_hash(self, digest: str) -> dict | None:
        row = self.db.execute("SELECT * FROM uploads WHERE idempotency=?", (digest,)).fetchone()
        return dict(row) if row else None

    def record_upload(self, job_id: str, digest: str, status: str, **fields: Any) -> None:
        now = time.time()
        with self.tx() as db:
            db.execute(
                "INSERT INTO uploads(job_id, idempotency, status, at) VALUES (?,?,?,?) "
                "ON CONFLICT(job_id) DO UPDATE SET status=excluded.status, at=excluded.at",
                (job_id, digest, status, now),
            )
            if fields:
                sets = ",".join(f"{k}=?" for k in fields)
                db.execute(f"UPDATE uploads SET {sets} WHERE job_id=?", (*fields.values(), job_id))

    # ---------- metrics ----------
    # ---------- settings / feedback ----------
    def get_setting(self, key: str, default: str | None = None) -> str | None:
        r = self.db.execute("SELECT value FROM settings WHERE key=?", (key,)).fetchone()
        return r["value"] if r else default

    def set_setting(self, key: str, value: str) -> None:
        with self.tx() as db:
            db.execute("INSERT INTO settings(key, value, at) VALUES (?,?,?) "
                       "ON CONFLICT(key) DO UPDATE SET value=excluded.value, at=excluded.at",
                       (key, value, time.time()))

    def add_feedback(self, job_id: str | None, decision: str, note: str = "") -> None:
        with self.tx() as db:
            db.execute("INSERT INTO feedback(at, job_id, decision, note) VALUES (?,?,?,?)",
                       (time.time(), job_id, decision, note))

    def set_features(self, job_id: str, data: dict) -> None:
        with self.tx() as db:
            db.execute("INSERT INTO features(job_id, data, at) VALUES (?,?,?) "
                       "ON CONFLICT(job_id) DO UPDATE SET data=excluded.data, at=excluded.at",
                       (job_id, json.dumps(data), time.time()))

    def add_metrics(self, video_id: str, data: dict, age_hours: float | None) -> None:
        with self.tx() as db:
            db.execute(
                "INSERT OR REPLACE INTO metrics(video_id, fetched_at, age_hours, data) VALUES (?,?,?,?)",
                (video_id, time.time(), age_hours, json.dumps(data)),
            )
