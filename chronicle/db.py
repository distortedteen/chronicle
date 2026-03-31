# chronicle/db.py
import sqlite3
import os
from pathlib import Path
from datetime import datetime

DB_DIR = Path.home() / ".chronicle"
DB_PATH = DB_DIR / "logbook.db"

def get_connection():
    DB_DIR.mkdir(exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_connection()
    conn.executescript("""
        CREATE TABLE IF NOT EXISTS entries (
            id        INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT NOT NULL,
            category  TEXT NOT NULL DEFAULT 'general',
            title     TEXT,
            content   TEXT NOT NULL,
            mood      TEXT,
            tags      TEXT
        );
        CREATE INDEX IF NOT EXISTS idx_timestamp ON entries(timestamp);
        CREATE INDEX IF NOT EXISTS idx_category  ON entries(category);
        
        CREATE TABLE IF NOT EXISTS entry_backups (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            entry_id    INTEGER NOT NULL,
            content     TEXT NOT NULL,
            category    TEXT NOT NULL,
            title       TEXT,
            mood        TEXT,
            tags        TEXT,
            created_at  TEXT NOT NULL,
            FOREIGN KEY (entry_id) REFERENCES entries(id) ON DELETE CASCADE
        );
        CREATE INDEX IF NOT EXISTS idx_backup_entry ON entry_backups(entry_id);
    """)
    conn.commit()
    conn.close()

def add_entry(content: str, category: str = "general",
              title: str = None, mood: str = None, tags: list = None):
    conn = get_connection()
    timestamp = datetime.now().isoformat(sep=" ", timespec="seconds")
    tags_str = ",".join(tags) if tags else None
    conn.execute(
        "INSERT INTO entries (timestamp, category, title, content, mood, tags) "
        "VALUES (?, ?, ?, ?, ?, ?)",
        (timestamp, category, title, content, mood, tags_str)
    )
    conn.commit()
    conn.close()

def get_entries(limit: int = 20, category: str = None,
                search: str = None, date: str = None):
    conn = get_connection()
    query = "SELECT * FROM entries WHERE 1=1"
    params = []
    if category:
        query += " AND category = ?"
        params.append(category)
    if search:
        query += " AND (content LIKE ? OR title LIKE ? OR tags LIKE ?)"
        params += [f"%{search}%", f"%{search}%", f"%{search}%"]
    if date:
        query += " AND timestamp LIKE ?"
        params.append(f"{date}%")
    query += " ORDER BY timestamp DESC LIMIT ?"
    params.append(limit)
    rows = conn.execute(query, params).fetchall()
    conn.close()
    return rows

def get_entry_by_id(entry_id: int):
    conn = get_connection()
    row = conn.execute("SELECT * FROM entries WHERE id = ?", (entry_id,)).fetchone()
    conn.close()
    return row

def update_entry(entry_id: int, content: str = None, category: str = None,
                title: str = None, mood: str = None, tags: list = None):
    conn = get_connection()
    
    existing = conn.execute("SELECT * FROM entries WHERE id = ?", (entry_id,)).fetchone()
    if not existing:
        conn.close()
        return False
    
    if any(x is not None for x in [content, category, title, mood, tags]):
        conn.execute("""
            INSERT INTO entry_backups (entry_id, content, category, title, mood, tags, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (entry_id, existing["content"], existing["category"], existing["title"],
              existing["mood"], existing["tags"], datetime.now().isoformat()))
    
    fields = []
    params = []
    
    if content is not None:
        fields.append("content = ?")
        params.append(content)
    if category is not None:
        fields.append("category = ?")
        params.append(category)
    if title is not None:
        fields.append("title = ?")
        params.append(title)
    if mood is not None:
        fields.append("mood = ?")
        params.append(mood)
    if tags is not None:
        fields.append("tags = ?")
        params.append(",".join(tags) if tags else None)
    
    if fields:
        params.append(entry_id)
        conn.execute(f"UPDATE entries SET {', '.join(fields)} WHERE id = ?", params)
        conn.commit()
    
    conn.close()
    return True

def get_stats():
    conn = get_connection()
    stats = {}
    stats["total"] = conn.execute("SELECT COUNT(*) FROM entries").fetchone()[0]
    stats["by_category"] = conn.execute(
        "SELECT category, COUNT(*) as n FROM entries GROUP BY category"
    ).fetchall()
    stats["first_entry"] = conn.execute(
        "SELECT timestamp FROM entries ORDER BY timestamp ASC LIMIT 1"
    ).fetchone()
    conn.close()
    return stats
