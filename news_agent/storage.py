import json
import sqlite3
from datetime import datetime, timezone

from news_agent.config import DB_PATH
from news_agent.models import Digest, NewsItem


def init_db() -> None:
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS digests (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                created_at TEXT NOT NULL,
                synthesis TEXT NOT NULL,
                items_json TEXT NOT NULL
            )
            """
        )


def save_digest(synthesis: str, items: list[NewsItem]) -> Digest:
    init_db()
    created_at = datetime.now(timezone.utc)
    items_json = json.dumps([item.model_dump() for item in items])
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.execute(
            "INSERT INTO digests (created_at, synthesis, items_json) VALUES (?, ?, ?)",
            (created_at.isoformat(), synthesis, items_json),
        )
        digest_id = cursor.lastrowid
    return Digest(id=digest_id, created_at=created_at, synthesis=synthesis, items=items)


def get_latest_digest() -> Digest | None:
    init_db()
    with sqlite3.connect(DB_PATH) as conn:
        row = conn.execute(
            "SELECT id, created_at, synthesis, items_json FROM digests ORDER BY id DESC LIMIT 1"
        ).fetchone()
    if row is None:
        return None
    digest_id, created_at, synthesis, items_json = row
    items = [NewsItem(**item) for item in json.loads(items_json)]
    return Digest(
        id=digest_id,
        created_at=datetime.fromisoformat(created_at),
        synthesis=synthesis,
        items=items,
    )
