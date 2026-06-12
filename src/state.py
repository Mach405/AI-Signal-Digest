"""A tiny SQLite seen-store so we never process the same item twice."""
import sqlite3
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DB_PATH = ROOT / "data" / "seen.sqlite"


def _conn():
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.execute(
        "CREATE TABLE IF NOT EXISTS seen ("
        "  id TEXT PRIMARY KEY,"
        "  source TEXT,"
        "  first_seen TEXT"
        ")"
    )
    return conn


def filter_new(items):
    """Return only items whose id we haven't recorded before."""
    conn = _conn()
    try:
        have = {row[0] for row in conn.execute("SELECT id FROM seen")}
        return [it for it in items if it["id"] not in have]
    finally:
        conn.close()


def mark_seen(items, now_iso):
    conn = _conn()
    try:
        conn.executemany(
            "INSERT OR IGNORE INTO seen (id, source, first_seen) VALUES (?, ?, ?)",
            [(it["id"], it.get("source_name", ""), now_iso) for it in items],
        )
        conn.commit()
    finally:
        conn.close()
