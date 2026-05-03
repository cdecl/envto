"""SQLite3 storage for .env files (envto package)."""

import sqlite3
import os
from datetime import datetime, timezone

# Use the new package name in the storage path
DB_DIR = os.path.expanduser("~/.local/share/envto")
DB_PATH = os.path.join(DB_DIR, "envto.db")


def _ensure_db():
    os.makedirs(DB_DIR, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    # Use executescript because we have multiple statements (table + index)
    conn.executescript(
        """
        CREATE TABLE IF NOT EXISTS envs (
            id TEXT PRIMARY KEY,
            path TEXT NOT NULL,
            env TEXT NOT NULL,
            update_dt TEXT NOT NULL
        );
        -- Composite index for faster look‑ups by id + path
        CREATE INDEX IF NOT EXISTS idx_envs_id_path ON envs (id, path);
        """
    )
    conn.commit()
    return conn


def save(rel_path: str, content: str) -> str:
    """Save .env content keyed by parent directory name.

    Args:
        rel_path: Directory path (relative to cwd or absolute).
        content: Full .env file content.

    Returns:
        The generated id (parent directory name + '.env').
    """
    abs_path = os.path.abspath(rel_path)
    parent_name = os.path.basename(os.path.normpath(abs_path))
    record_id = f"{parent_name}.env"
    now = datetime.now(timezone.utc).isoformat()

    conn = _ensure_db()
    conn.execute(
        "INSERT OR REPLACE INTO envs (id, path, env, update_dt) VALUES (?, ?, ?, ?)",
        (record_id, abs_path, content, now),
    )
    conn.commit()
    conn.close()
    return record_id


def load(record_id: str) -> tuple[str, str, str] | None:
    """Load a single record by id.

    Returns:
        (id, path, env) or None if not found.
    """
    conn = _ensure_db()
    cur = conn.execute("SELECT id, path, env FROM envs WHERE id = ?", (record_id,))
    row = cur.fetchone()
    conn.close()
    return row


def all_records() -> list[tuple[str, str, str]]:
    """Return all records as (id, path, update_dt)."""
    conn = _ensure_db()
    cur = conn.execute("SELECT id, path, update_dt FROM envs ORDER BY update_dt DESC")
    rows = cur.fetchall()
    conn.close()
    return rows


def view_record(record_id: str) -> str | None:
    """Get the env content for a record id."""
    conn = _ensure_db()
    cur = conn.execute("SELECT env FROM envs WHERE id = ?", (record_id,))
    row = cur.fetchone()
    conn.close()
    return row[0] if row else None
