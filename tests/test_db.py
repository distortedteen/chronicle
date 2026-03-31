# tests/test_db.py
import os, pytest
from pathlib import Path

# Override DB path for tests
import chronicle.db as db
db.DB_PATH = Path("/tmp/test_chronicle.db")

from chronicle.db import init_db, add_entry, get_entries

def setup_function():
    if db.DB_PATH.exists():
        db.DB_PATH.unlink()
    init_db()

def test_add_and_retrieve():
    add_entry("Test entry", category="build")
    entries = get_entries(limit=1)
    assert len(entries) == 1
    assert entries[0]["content"] == "Test entry"
    assert entries[0]["category"] == "build"

def test_search():
    add_entry("Implemented OAuth", category="build", tags=["auth", "security"])
    entries = get_entries(search="OAuth")
    assert any("OAuth" in e["content"] for e in entries)

def test_update_entry():
    from chronicle.db import get_entry_by_id, update_entry
    
    add_entry("Original content", category="general")
    update_entry(1, content="Updated content", category="build")
    
    entry = get_entry_by_id(1)
    assert entry["content"] == "Updated content"
    assert entry["category"] == "build"
