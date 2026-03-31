# chronicle/export.py
from datetime import datetime
import json
from pathlib import Path

def export_markdown(entries, filename: str = "chronicle_export") -> str:
    """Export all entries as a Markdown document — book-ready format."""
    lines = [
        "# Chronicle — Project Logbook\n",
        f"*Exported: {datetime.now().strftime('%B %d, %Y at %H:%M')}*\n",
        "---\n"
    ]
    current_date = None
    for e in reversed(list(entries)):  # Chronological order for export
        entry_date = e["timestamp"][:10]
        if entry_date != current_date:
            current_date = entry_date
            lines.append(f"\n## {entry_date}\n")
        if e["title"]:
            lines.append(f"### {e['title']}\n")
        lines.append(f"**[{e['category'].upper()}]** — *{e['timestamp'][11:]}*\n")
        if e["mood"]:
            lines.append(f"*Mood: {e['mood']}*\n")
        lines.append(f"\n{e['content']}\n")
        if e["tags"]:
            lines.append(f"\n*Tags: {e['tags']}*\n")
        lines.append("\n---\n")

    path = Path(f"{filename}.md")
    path.write_text("\n".join(lines), encoding="utf-8")
    return str(path)

def export_json(entries, filename: str = "chronicle_export") -> str:
    """Export as structured JSON."""
    data = [dict(e) for e in entries]
    path = Path(f"{filename}.json")
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")
    return str(path)
