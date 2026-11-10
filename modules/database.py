"""DB layer: Neon (pg8000) + SQLite fallback."""
import logging
from config import Config

logger = logging.getLogger(__name__)
_fallback_warned = False


def get_db():
    global _fallback_warned
    if Config.DATABASE_URL:
        try:
            import pg8000.native
            from urllib.parse import urlparse
            p = urlparse(Config.DATABASE_URL)
            return pg8000.native.Connection(
                user=p.username, password=p.password,
                host=p.hostname, port=p.port or 5432,
                database=p.path.lstrip("/"),
            )
        except Exception as e:
            if not _fallback_warned:
                logger.warning(f"Neon gagal ({str(e)[:80]}), fallback SQLite")
                _fallback_warned = True
    import sqlite3
    conn = sqlite3.connect("search.db")
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_db()
    try:
        if Config.DATABASE_URL:
            try:
                conn.run(
                    "CREATE TABLE IF NOT EXISTS discoveries ("
                    "id SERIAL PRIMARY KEY, query TEXT, name TEXT, url TEXT UNIQUE, "
                    "category TEXT, auth_type TEXT, free_tier TEXT, "
                    "created_at TIMESTAMP DEFAULT NOW())"
                )
                return
            except Exception:
                pass
        conn.execute(
            "CREATE TABLE IF NOT EXISTS discoveries ("
            "id INTEGER PRIMARY KEY, query TEXT, name TEXT, "
            "url TEXT UNIQUE, category TEXT, auth_type TEXT, "
            "free_tier TEXT, created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)"
        )
        conn.commit()
    finally:
        conn.close()


def save(query, item):
    conn = get_db()
    try:
        if Config.DATABASE_URL:
            try:
                conn.run(
                    "INSERT INTO discoveries (query, name, url, category, auth_type, free_tier) "
                    "VALUES (:q, :n, :u, :c, :a, :f) ON CONFLICT (url) DO NOTHING",
                    q=query, n=item.get("name", ""), u=item.get("url", ""),
                    c=item.get("category", ""), a=item.get("auth_type", ""),
                    f=item.get("free_tier", ""),
                )
                return
            except Exception:
                pass
        conn.execute(
            "INSERT OR IGNORE INTO discoveries "
            "(query, name, url, category, auth_type, free_tier) VALUES (?, ?, ?, ?, ?, ?)",
            (query, item.get("name", ""), item.get("url", ""),
             item.get("category", ""), item.get("auth_type", ""),
             item.get("free_tier", "")),
        )
        conn.commit()
    finally:
        conn.close()
