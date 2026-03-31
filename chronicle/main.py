import typer
import json
from datetime import datetime
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.text import Text
from typing import Optional, List
from chronicle.db import init_db, add_entry, get_entries, get_stats
from chronicle.export import export_markdown, export_json

__version__ = "0.1.0"

app = typer.Typer(
    name="chronicle",
    help="Chronicle — Your Project Logbook. Log your journey.",
    add_completion=False
)

def print_version(version: bool):
    if version:
        print(f"chronicle {__version__}")
        raise typer.Exit()

version_option = typer.Option(False, "--version", help="Show version number")

quiet_mode = typer.Option(False, "--quiet", "-q", help="Suppress all output except errors")
json_output = typer.Option(False, "--json", "-j", help="Output results as JSON")

console = Console(force_terminal=False)

OUTPUT_MODE = "normal"

def print_json(data):
    print(json.dumps(data, indent=2, ensure_ascii=False))

def set_output_mode(mode: str):
    global OUTPUT_MODE
    OUTPUT_MODE = mode
    if mode == "json":
        console.quiet = True
    elif mode == "quiet":
        console.quiet = True
    else:
        console.quiet = False

CATEGORIES = ["idea", "build", "learn", "fail", "win", "research", "general"]
MOODS = ["🔥 fire", "😤 grind", "😌 calm", "😩 stuck", "🎯 focused", "🤔 thinking"]

CATEGORY_COLORS = {
    "idea": "yellow", "build": "cyan", "learn": "blue",
    "fail": "red", "win": "green", "research": "magenta", "general": "white"
}

CAT_ICONS = {
    "idea": "💡", "build": "🔨", "learn": "📚",
    "fail": "📉", "win": "🏆", "research": "🔬", "general": "📝"
}

CATEGORY_ALIASES = {
    "b": "build",    "build": "build",
    "i": "idea",     "idea": "idea",
    "w": "win",      "win": "win",
    "f": "fail",     "fail": "fail",
    "l": "learn",    "learn": "learn",
    "r": "research", "research": "research",
    "g": "general",  "general": "general",
}

@app.callback(invoke_without_command=True)
def startup(ctx: typer.Context, 
            quiet: bool = quiet_mode, 
            json_out: bool = json_output,
            version: bool = version_option):
    if version:
        print(f"chronicle {__version__}")
        raise typer.Exit()
    
    init_db()
    
    if json_out:
        console.quiet = True
    elif quiet:
        console.quiet = True
    
    if ctx.invoked_subcommand is None:
        if json_out:
            print_json({"message": "Chronicle — Your Project Logbook", "hint": "Run chronicle --help to see all commands"})
        else:
            console.print(Panel(
                "[bold cyan]Chronicle[/bold cyan] — Your Project Logbook\n"
                "[dim]Run [bold]chronicle --help[/bold] to see all commands[/dim]",
                border_style="cyan"
            ))

@app.command("log")
def log_entry(
    content: str = typer.Argument(..., help="Your log entry"),
    category: str = typer.Option("general", "-c", "--category",
                                  help=f"Category: {', '.join(CATEGORIES)}"),
    title: Optional[str] = typer.Option(None, "-t", "--title", help="Optional title"),
    mood: Optional[str] = typer.Option(None, "-m", "--mood", help="Your mood/energy"),
    tags: Optional[List[str]] = typer.Option(None, "--tag", help="Add tags (repeat for multiple)"),
    quiet: bool = typer.Option(False, "-q", "--quiet", help="Suppress output"),
    json_out: bool = typer.Option(False, "-j", "--json", help="Output as JSON")
):
    """Log a new entry."""
    from chronicle.db import get_connection
    add_entry(content, category=category, title=title, mood=mood, tags=tags)
    conn = get_connection()
    entry_id = conn.execute("SELECT last_insert_rowid()").fetchone()[0]
    conn.close()
    if json_out:
        print_json({"status": "success", "entry_id": entry_id, "category": category})
    elif not quiet:
        console.print(f"[green]✓[/green] Entry logged under [bold]{category}[/bold]")

@app.command("idea")
def log_idea(
    content: str = typer.Argument(..., help="Your idea"),
    quiet: bool = typer.Option(False, "-q", "--quiet", help="Suppress output"),
    json_out: bool = typer.Option(False, "-j", "--json", help="Output as JSON")
):
    """Quick-log an idea."""
    add_entry(content, category="idea")
    if json_out:
        print_json({"status": "success", "message": "Idea captured", "category": "idea"})
    elif not quiet:
        console.print("[yellow]Idea captured.[/yellow]")

@app.command("win")
def log_win(
    content: str = typer.Argument(..., help="What did you achieve?"),
    quiet: bool = typer.Option(False, "-q", "--quiet", help="Suppress output"),
    json_out: bool = typer.Option(False, "-j", "--json", help="Output as JSON")
):
    """Log a win, no matter how small."""
    add_entry(content, category="win")
    if json_out:
        print_json({"status": "success", "message": "Win logged", "category": "win"})
    elif not quiet:
        console.print("[bold green]WIN logged. Keep going.[/bold green]")

@app.command("fail")
def log_fail(
    content: str = typer.Argument(..., help="What went wrong?"),
    quiet: bool = typer.Option(False, "-q", "--quiet", help="Suppress output"),
    json_out: bool = typer.Option(False, "-j", "--json", help="Output as JSON")
):
    """Log a failure or lesson learned."""
    add_entry(content, category="fail")
    if json_out:
        print_json({"status": "success", "message": "Failure logged", "category": "fail"})
    elif not quiet:
        console.print("[dim red]Failure logged. This is data, not defeat.[/dim red]")

@app.command("show")
def show_entries(
    limit:    int           = typer.Option(10,    "-n", "--limit",    help="Number of entries to show"),
    category: Optional[str] = typer.Option(None,  "-c", "--category", help="Filter by category"),
    search:   Optional[str] = typer.Option(None,  "-s", "--search",   help="Filter by keyword"),
    date:     Optional[str] = typer.Option(None,  "-d", "--date",     help="Filter by date: YYYY-MM-DD"),
    full:     bool          = typer.Option(False,        "--full",     help="Show full content, no truncation"),
    table:    bool          = typer.Option(False,        "--table",    help="Compact table view"),
):
    """Show log entries. Default is card view; use --table for compact view."""
    entries = get_entries(limit=limit, category=category, search=search, date=date)
    if not entries:
        console.print("[dim]No entries found.[/dim]")
        return

    if table:
        # ── Compact table view (good for scripting / quick scan) ──
        t = Table(show_header=True, header_style="bold cyan",
                  border_style="dim", expand=True)
        t.add_column("ID",        style="dim", width=4)
        t.add_column("Timestamp", style="dim", width=20)
        t.add_column("Category",  width=10)
        t.add_column("Title / Content")
        t.add_column("Tags",      style="dim", width=20)
        for e in entries:
            color   = CATEGORY_COLORS.get(e["category"], "white")
            display = e["title"] if e["title"] else (
                e["content"][:70] + "..." if len(e["content"]) > 70 else e["content"]
            )
            t.add_row(
                str(e["id"]),
                e["timestamp"],
                f"[{color}]{e['category']}[/{color}]",
                display,
                e["tags"] or ""
            )
        console.print(t)
        return

    # ── Card view (default) ──
    current_date = None
    for e in entries:
        day = e["timestamp"][:10]

        # Print a date separator whenever the day changes
        if day != current_date:
            current_date = day
            console.rule(f"[dim]{day}[/dim]", style="dim")

        color = CATEGORY_COLORS.get(e["category"], "white")
        icon  = CAT_ICONS.get(e["category"], "📝")
        time  = e["timestamp"][11:16]  # HH:MM only

        # Build the header line
        header = (
            f"{icon} [dim]#{e['id']}[/dim]"
            f"  [{color}]{e['category']}[/{color}]"
            f"  [dim]{time}[/dim]"
        )
        if e["title"]:
            header += f"  [bold]{e['title']}[/bold]"
        if e["tags"]:
            tag_str = "  ".join(f"[cyan]#{t.strip()}[/cyan]"
                                for t in e["tags"].split(",") if t.strip())
            header += f"  {tag_str}"
        if e["mood"]:
            header += f"  [dim]{e['mood']}[/dim]"

        # Build the body line
        if full:
            body = e["content"]
        else:
            body = e["content"][:120] + ("…" if len(e["content"]) > 120 else "")

        console.print(header)
        console.print(f"  [white]{body}[/white]")
        console.print()

@app.command("stats")
def show_stats():
    """Show journey stats: totals, category bars, streak, and 12-week heatmap."""
    from datetime import date, timedelta
    from collections import Counter
    from chronicle.db import get_connection

    conn       = get_connection()
    total      = conn.execute("SELECT COUNT(*) FROM entries").fetchone()[0]
    cats       = conn.execute(
        "SELECT category, COUNT(*) as n FROM entries "
        "GROUP BY category ORDER BY n DESC"
    ).fetchall()
    first_row  = conn.execute(
        "SELECT timestamp FROM entries ORDER BY timestamp ASC LIMIT 1"
    ).fetchone()
    all_dates  = [
        row[0][:10]
        for row in conn.execute("SELECT timestamp FROM entries").fetchall()
    ]
    conn.close()

    if total == 0:
        console.print("[dim]No entries yet. Start with: chronicle q your first thought[/dim]")
        return

    date_counts = Counter(all_dates)
    today       = date.today()
    started     = first_row[0][:10] if first_row else "N/A"

    # ── Streak calculation ─────────────────────────────────────
    current_streak = 0
    while (today - timedelta(days=current_streak)).isoformat() in date_counts:
        current_streak += 1

    best_streak = cur = 0
    for i in range(365):
        d = (today - timedelta(days=i)).isoformat()
        if d in date_counts:
            cur += 1
            best_streak = max(best_streak, cur)
        else:
            cur = 0

    days_active  = len(date_counts)
    days_elapsed = (today - date.fromisoformat(started)).days + 1 if started != "N/A" else 1
    consistency  = int((days_active / days_elapsed) * 100)

    # ── Header panel ──────────────────────────────────────────
    console.print()
    console.print(Panel(
        f"[bold]Total entries :[/bold] {total}\n"
        f"[bold]Journey started:[/bold] {started}\n"
        f"[bold]Days active    :[/bold] {days_active} / {days_elapsed} "
        f"[dim]({consistency}% consistency)[/dim]\n"
        f"[bold]Current streak :[/bold] "
        + (f"[bold yellow]🔥 {current_streak} day(s)[/bold yellow]" if current_streak else "[dim]0 days[/dim]")
        + f"   [dim]best: {best_streak} day(s)[/dim]",
        title="[bold cyan]Chronicle[/bold cyan]",
        border_style="cyan",
        padding=(0, 2)
    ))

    # ── Category bar chart ─────────────────────────────────────
    console.print("\n[bold]By category[/bold]")
    max_n = max(row[1] for row in cats) if cats else 1
    for row in cats:
        cat   = row[0]
        n     = row[1]
        icon  = CAT_ICONS.get(cat, "📝")
        color = CATEGORY_COLORS.get(cat, "white")
        bar   = "█" * int((n / max_n) * 32)
        pct   = int(n / total * 100)
        console.print(
            f"  {icon} [{color}]{cat:<12}[/{color}]"
            f"[{color}]{bar:<32}[/{color}]"
            f"  [dim]{n:>3} entries  ({pct:>2}%)[/dim]"
        )

    # ── Last 7 days bar ────────────────────────────────────────
    console.print("\n[bold]Last 7 days[/bold]")
    week_max = max(
        (date_counts.get((today - timedelta(days=i)).isoformat(), 0) for i in range(7)),
        default=1
    ) or 1
    for i in range(6, -1, -1):
        d      = today - timedelta(days=i)
        n      = date_counts.get(d.isoformat(), 0)
        bar    = "█" * int((n / week_max) * 28)
        label  = "today" if i == 0 else d.strftime("%a %d")
        color  = "cyan" if n > 0 else "dim"
        marker = " ◀ today" if i == 0 else ""
        console.print(
            f"  [dim]{label:<9}[/dim]"
            f"[{color}]{bar:<28}[/{color}]"
            f"  [dim]{n}{marker}[/dim]"
        )

    # ── 12-week heatmap ────────────────────────────────────────
    console.print("\n[bold]Activity heatmap — last 12 weeks[/bold]")

    today_weekday = today.weekday()   # 0 = Monday
    start         = today - timedelta(weeks=11, days=today_weekday)

    HEAT = ["·", "░", "▒", "▓", "█"]
    DAYS = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]

    # Print week-number header
    week_header = "      "
    for w in range(12):
        d = start + timedelta(weeks=w)
        week_header += f"[dim]{d.strftime('%d')[0]}[/dim] "
    console.print(f"  {week_header}")

    for day_i in range(7):
        cells = []
        for week_i in range(12):
            d     = start + timedelta(weeks=week_i, days=day_i)
            n     = date_counts.get(d.isoformat(), 0)
            level = (
                0 if n == 0 else
                1 if n == 1 else
                2 if n <= 3 else
                3 if n <= 6 else 4
            )
            is_today = (d == today)
            if is_today:
                cells.append(f"[bold white]{HEAT[level]}[/bold white]")
            elif n == 0:
                cells.append(f"[dim]{HEAT[level]}[/dim]")
            elif n >= 3:
                cells.append(f"[green]{HEAT[level]}[/green]")
            else:
                cells.append(f"[yellow]{HEAT[level]}[/yellow]")

        console.print(
            f"  [dim]{DAYS[day_i]}[/dim] " + "  ".join(cells)
        )

    console.print(
        "\n  [dim]· none   "
        "[/dim][yellow]░ 1   ▒ 2-3  "
        "[/yellow][green]▓ 4-6  █ 7+[/green]"
    )
    console.print()

@app.command("export")
def export_entries(
    format: str = typer.Option("markdown", "-f", "--format",
                                help="Export format: markdown | json"),
    output: str = typer.Option("chronicle_export", "-o", "--output",
                                help="Output filename (no extension)")
):
    """Export your log to Markdown or JSON."""
    entries = get_entries(limit=99999)
    if format == "markdown":
        path = export_markdown(entries, output)
    elif format == "json":
        path = export_json(entries, output)
    else:
        console.print("[red]Unknown format. Use 'markdown' or 'json'[/red]")
        return
    console.print(f"[green]✓[/green] Exported to [bold]{path}[/bold]")

@app.command("q")
def quick_log(
    words: List[str] = typer.Argument(..., help="[category?] your log text")
):
    """Ultra-fast log. First word can be a category shortcut.

    Examples:
      chronicle q b finished the auth module
      chronicle q win first user signed up
      chronicle q just had a wild idea about pricing
    """
    if not words:
        console.print("[red]Nothing to log.[/red]")
        return

    first = words[0].lower()
    if first in CATEGORY_ALIASES:
        category = CATEGORY_ALIASES[first]
        content  = " ".join(words[1:])
    else:
        category = "general"
        content  = " ".join(words)

    if not content.strip():
        console.print("[red]Content can't be empty after the category shortcut.[/red]")
        return

    add_entry(content, category=category)
    icon = CAT_ICONS.get(category, "📝")
    preview = content[:60] + ("..." if len(content) > 60 else "")
    console.print(f"{icon} [dim]{category}[/dim] → {preview}")


@app.command("note")
def log_note(
    category: str          = typer.Option("general", "-c", "--category"),
    title:    Optional[str]= typer.Option(None,      "-t", "--title")
):
    """Write a longer entry interactively. Press Enter twice when done."""
    console.print("[dim]Write your entry below. Press Enter twice to save, Ctrl+C to cancel.[/dim]\n")
    lines = []
    try:
        while True:
            line = input()
            if line == "" and lines and lines[-1] == "":
                break
            lines.append(line)
    except KeyboardInterrupt:
        console.print("\n[dim]Cancelled. Nothing logged.[/dim]")
        return

    content = "\n".join(lines).strip()
    if not content:
        console.print("[dim]Nothing to save.[/dim]")
        return

    add_entry(content, category=category, title=title)
    console.print(f"\n[green]✓[/green] Note logged under [bold]{category}[/bold] ({len(content)} chars)")


@app.command("last")
def show_last(
    n: int = typer.Argument(1, help="How many recent entries to show (default: 1)")
):
    """Show your last N entries in full detail."""
    entries = get_entries(limit=n)
    if not entries:
        console.print("[dim]No entries yet. Start with: chronicle q your first thought[/dim]")
        return
    for e in entries:
        color = CATEGORY_COLORS.get(e["category"], "white")
        icon  = CAT_ICONS.get(e["category"], "📝")
        title_part = f"  [bold]{e['title']}[/bold]" if e["title"] else ""
        tags_part  = f"  [dim]#{e['tags'].replace(',', ' #')}[/dim]" if e["tags"] else ""
        console.print(Panel(
            e["content"],
            title=f"{icon} [{color}]{e['category']}[/{color}]"
                  f"  [dim]#{e['id']}  {e['timestamp']}[/dim]"
                  f"{title_part}{tags_part}",
            border_style=color
        ))


@app.command("view")
def view_entry(
    entry_id: int = typer.Argument(..., help="ID of the entry to view")
):
    """View one entry in full detail by its ID."""
    from chronicle.db import get_connection
    conn = get_connection()
    e    = conn.execute("SELECT * FROM entries WHERE id = ?", (entry_id,)).fetchone()
    conn.close()

    if not e:
        console.print(f"[red]No entry found with ID {entry_id}.[/red]")
        console.print("[dim]Tip: run 'chronicle show' to see IDs.[/dim]")
        return

    color = CATEGORY_COLORS.get(e["category"], "white")
    icon  = CAT_ICONS.get(e["category"], "📝")

    from rich.table import Table as RichTable
    meta = RichTable.grid(padding=(0, 2))
    meta.add_column(style="dim", justify="right")
    meta.add_column()
    meta.add_row("ID",        str(e["id"]))
    meta.add_row("Timestamp", e["timestamp"])
    meta.add_row("Category",  f"{icon} [{color}]{e['category']}[/{color}]")
    if e["title"]: meta.add_row("Title", f"[bold]{e['title']}[/bold]")
    if e["mood"]:  meta.add_row("Mood",  e["mood"])
    if e["tags"]:
        tags = "  ".join(f"[cyan]#{t.strip()}[/cyan]" for t in e["tags"].split(","))
        meta.add_row("Tags", tags)

    console.print()
    console.print(meta)
    console.print()
    console.print(Panel(e["content"], border_style=color))
    console.print()


@app.command("edit")
def edit_entry(
    entry_id: int = typer.Argument(..., help="ID of the entry to edit"),
    content: Optional[str] = typer.Option(None, "-c", "--content", help="New content"),
    category: Optional[str] = typer.Option(None, "-cat", "--category", help="New category"),
    title: Optional[str] = typer.Option(None, "-t", "--title", help="New title"),
    mood: Optional[str] = typer.Option(None, "-m", "--mood", help="New mood"),
    tags: Optional[List[str]] = typer.Option(None, "--tag", help="Replace tags"),
):
    """Edit an existing entry."""
    from chronicle.db import get_entry_by_id, update_entry
    
    existing = get_entry_by_id(entry_id)
    if not existing:
        console.print(f"[red]No entry found with ID {entry_id}.[/red]")
        console.print("[dim]Tip: run 'chronicle show' to see IDs.[/dim]")
        return
    
    no_changes = all(x is None for x in [content, category, title, mood, tags])
    if no_changes:
        console.print(f"[yellow]No changes specified for entry #{entry_id}.[/yellow]")
        console.print("[dim]Use --content, --category, --title, --mood, or --tag to make changes.[/dim]")
        return
    
    update_entry(
        entry_id,
        content=content,
        category=category,
        title=title,
        mood=mood,
        tags=tags
    )
    
    icon = CAT_ICONS.get(category if category else existing["category"], "📝")
    console.print(f"[green]✓[/green] Entry #{entry_id} updated. {icon}")


@app.command("search")
def search_entries(
    query:     str           = typer.Argument(...,  help="Keyword to search for"),
    category:  Optional[str] = typer.Option(None,   "-c", "--category", help="Filter by category"),
    from_date: Optional[str] = typer.Option(None,   "--from", help="Start date: YYYY-MM-DD"),
    to_date:   Optional[str] = typer.Option(None,   "--to",   help="End date:   YYYY-MM-DD"),
    tag:       Optional[str] = typer.Option(None,   "--tag",  help="Filter by tag"),
    limit:     int           = typer.Option(20,     "-n", "--limit"),
    full:      bool          = typer.Option(False,   "--full", help="Show full content"),
):
    """Search entries by keyword, with results highlighted."""
    from chronicle.db import get_connection
    conn   = get_connection()
    sql    = "SELECT * FROM entries WHERE (content LIKE ? OR title LIKE ?)"
    params = [f"%{query}%", f"%{query}%"]

    if category:
        sql += " AND category = ?"
        params.append(category)
    if from_date:
        sql += " AND timestamp >= ?"
        params.append(from_date)
    if to_date:
        sql += " AND timestamp <= ?"
        params.append(to_date + " 23:59:59")
    if tag:
        sql += " AND tags LIKE ?"
        params.append(f"%{tag}%")

    sql += " ORDER BY timestamp DESC LIMIT ?"
    params.append(limit)

    entries = conn.execute(sql, params).fetchall()
    conn.close()

    if not entries:
        console.print(f"[dim]No results for '[bold]{query}[/bold]'.[/dim]")
        console.print("[dim]Tip: search is case-insensitive and matches partial words.[/dim]")
        return

    console.print(
        f"\n[dim]Found [bold]{len(entries)}[/bold] result(s) for "
        f"'[bold cyan]{query}[/bold cyan]'[/dim]\n"
    )

    current_date = None
    for e in entries:
        day = e["timestamp"][:10]
        if day != current_date:
            current_date = day
            console.rule(f"[dim]{day}[/dim]", style="dim")

        color = CATEGORY_COLORS.get(e["category"], "white")
        icon  = CAT_ICONS.get(e["category"], "📝")
        time  = e["timestamp"][11:16]

        # Header line
        header = (
            f"{icon} [dim]#{e['id']}[/dim]"
            f"  [{color}]{e['category']}[/{color}]"
            f"  [dim]{time}[/dim]"
        )
        if e["title"]:
            header += f"  [bold]{e['title']}[/bold]"
        if e["tags"]:
            tag_str = "  ".join(f"[cyan]#{t.strip()}[/cyan]"
                                for t in e["tags"].split(",") if t.strip())
            header += f"  {tag_str}"

        # Body with highlighted keyword
        raw  = e["content"] if full else (
            e["content"][:200] + ("…" if len(e["content"]) > 200 else "")
        )
        body = Text(raw)
        body.highlight_words([query], style="bold yellow")

        console.print(header)
        console.print("  ", body)
        console.print()


@app.command("tags")
def list_tags():
    """List all tags you've used, with entry counts."""
    from chronicle.db import get_connection
    from collections import Counter

    conn = get_connection()
    rows = conn.execute(
        "SELECT tags FROM entries WHERE tags IS NOT NULL AND tags != ''"
    ).fetchall()
    total = conn.execute("SELECT COUNT(*) FROM entries").fetchone()[0]
    conn.close()

    all_tags = []
    for row in rows:
        all_tags.extend(t.strip() for t in row[0].split(",") if t.strip())

    if not all_tags:
        console.print("[dim]No tags used yet.[/dim]")
        console.print(
            "[dim]Add tags when logging: "
            "chronicle log \"content\" --tag security --tag python[/dim]"
        )
        return

    counts  = Counter(all_tags).most_common()
    max_n   = counts[0][1]

    console.print(f"\n[bold]Tags[/bold]  [dim]({len(counts)} unique, "
                  f"{len(all_tags)} total uses)[/dim]\n")

    for tag_name, n in counts:
        bar   = "█" * int((n / max_n) * 28)
        pct   = int(n / len(all_tags) * 100)
        console.print(
            f"  [cyan]#{tag_name:<20}[/cyan]"
            f"[cyan]{bar:<28}[/cyan]"
            f"  [dim]{n} use{'s' if n != 1 else ''} ({pct}%)[/dim]"
        )
    console.print()

@app.command("browse")
def browse(
    quiet: bool = typer.Option(False, "-q", "--quiet", help="Suppress output"),
    json_out: bool = typer.Option(False, "-j", "--json", help="Output as JSON")
):
    """Open the interactive TUI browser."""
    from chronicle.tui import launch
    if json_out:
        print_json({"status": "success", "message": "Launching TUI browser"})
    elif not quiet:
        console.print("[dim]Opening interactive browser...[/dim]")
    launch()


@app.command("delete")
def delete_entry(
    entry_id: int = typer.Argument(..., help="ID of the entry to delete"),
    force: bool = typer.Option(False, "-f", "--force", help="Skip confirmation prompt"),
    quiet: bool = typer.Option(False, "-q", "--quiet", help="Suppress output"),
    json_out: bool = typer.Option(False, "-j", "--json", help="Output as JSON")
):
    """Delete an entry by ID."""
    from chronicle.db import get_entry_by_id, get_connection
    
    existing = get_entry_by_id(entry_id)
    if not existing:
        if json_out:
            print_json({"status": "error", "message": f"No entry found with ID {entry_id}"})
        else:
            console.print(f"[red]No entry found with ID {entry_id}.[/red]")
            console.print("[dim]Tip: run 'chronicle show' to see IDs.[/dim]")
        return
    
    if not force:
        if json_out:
            print_json({"status": "error", "message": "Use --force to confirm deletion"})
        else:
            console.print(f"[yellow]Delete entry #{entry_id}?[/yellow]")
            console.print(f"[dim]Category: {existing['category']} | {existing['content'][:50]}...[/dim]")
            confirm = input("Type 'yes' to confirm: ")
            if confirm.lower() != "yes":
                if not quiet:
                    console.print("[dim]Deletion cancelled.[/dim]")
                return
    
    conn = get_connection()
    conn.execute("DELETE FROM entries WHERE id = ?", (entry_id,))
    conn.commit()
    conn.close()
    
    if json_out:
        print_json({"status": "success", "message": f"Entry #{entry_id} deleted", "deleted_id": entry_id})
    elif not quiet:
        console.print(f"[green]✓[/green] Entry #{entry_id} deleted.")


@app.command("undo")
def undo_edit(
    entry_id: int = typer.Argument(..., help="ID of the entry to restore"),
    quiet: bool = typer.Option(False, "-q", "--quiet", help="Suppress output"),
    json_out: bool = typer.Option(False, "-j", "--json", help="Output as JSON")
):
    """Restore an entry to its previous state from backup."""
    from chronicle.db import get_connection
    from datetime import datetime
    
    conn = get_connection()
    
    current = conn.execute("SELECT * FROM entries WHERE id = ?", (entry_id,)).fetchone()
    if not current:
        if json_out:
            print_json({"status": "error", "message": f"No entry found with ID {entry_id}"})
        else:
            console.print(f"[red]No entry found with ID {entry_id}.[/red]")
        conn.close()
        return
    
    backup = conn.execute("SELECT * FROM entry_backups WHERE entry_id = ? ORDER BY created_at DESC LIMIT 1", (entry_id,)).fetchone()
    if not backup:
        if json_out:
            print_json({"status": "error", "message": f"No backup found for entry #{entry_id}"})
        else:
            console.print(f"[red]No backup found for entry #{entry_id}.[/red]")
            console.print("[dim]Only entries that have been edited have backups.[/dim]")
        conn.close()
        return
    
    conn.execute("""
        UPDATE entries 
        SET content = ?, category = ?, title = ?, mood = ?, tags = ?
        WHERE id = ?
    """, (backup["content"], backup["category"], backup["title"], backup["mood"], backup["tags"], entry_id))
    conn.commit()
    conn.close()
    
    if json_out:
        print_json({"status": "success", "message": f"Entry #{entry_id} restored from backup", "entry_id": entry_id})
    elif not quiet:
        console.print(f"[green]✓[/green] Entry #{entry_id} restored from backup.")


@app.command("redo")
def redo_edit(
    entry_id: int = typer.Argument(..., help="ID of the entry to redo"),
    quiet: bool = typer.Option(False, "-q", "--quiet", help="Suppress output"),
    json_out: bool = typer.Option(False, "-j", "--json", help="Output as JSON")
):
    """Re-apply the most recent edit to an entry."""
    from chronicle.db import get_connection
    
    conn = get_connection()
    
    current = conn.execute("SELECT * FROM entries WHERE id = ?", (entry_id,)).fetchone()
    if not current:
        if json_out:
            print_json({"status": "error", "message": f"No entry found with ID {entry_id}"})
        else:
            console.print(f"[red]No entry found with ID {entry_id}.[/red]")
        conn.close()
        return
    
    backup = conn.execute("SELECT * FROM entry_backups WHERE entry_id = ? ORDER BY created_at DESC LIMIT 1", (entry_id,)).fetchone()
    if not backup:
        if json_out:
            print_json({"status": "error", "message": f"No backup found for entry #{entry_id}"})
        else:
            console.print(f"[red]No backup found for entry #{entry_id}.[/red]")
        conn.close()
        return
    
    current_backup = conn.execute("SELECT * FROM entries WHERE id = ?", (entry_id,)).fetchone()
    conn.execute("""
        INSERT INTO entry_backups (entry_id, content, category, title, mood, tags, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (entry_id, current_backup["content"], current_backup["category"], current_backup["title"], 
          current_backup["mood"], current_backup["tags"], datetime.now().isoformat()))
    
    conn.execute("""
        UPDATE entries 
        SET content = ?, category = ?, title = ?, mood = ?, tags = ?
        WHERE id = ?
    """, (backup["content"], backup["category"], backup["title"], backup["mood"], backup["tags"], entry_id))
    conn.commit()
    conn.close()
    
    if json_out:
        print_json({"status": "success", "message": f"Entry #{entry_id} redo applied", "entry_id": entry_id})
    elif not quiet:
        console.print(f"[green]✓[/green] Entry #{entry_id} redo applied.")


@app.command("backup")
def create_backup(
    output: str = typer.Option("chronicle_backup", "-o", "--output", help="Output filename (no extension)"),
    quiet: bool = typer.Option(False, "-q", "--quiet", help="Suppress output"),
    json_out: bool = typer.Option(False, "-j", "--json", help="Output as JSON")
):
    """Create a full backup of your logbook."""
    import shutil
    from pathlib import Path
    from chronicle.db import DB_PATH
    
    if not DB_PATH.exists():
        if json_out:
            print_json({"status": "error", "message": "No logbook found to backup"})
        else:
            console.print("[red]No logbook found to backup.[/red]")
        return
    
    backup_path = Path(f"{output}.chronicle")
    shutil.copy2(DB_PATH, backup_path)
    
    if json_out:
        print_json({"status": "success", "message": f"Backup created", "file": str(backup_path)})
    elif not quiet:
        console.print(f"[green]✓[/green] Backup created: [bold]{backup_path}[/bold]")


@app.command("restore")
def restore_backup(
    file: str = typer.Argument(..., help="Path to the backup file (.chronicle)"),
    quiet: bool = typer.Option(False, "-q", "--quiet", help="Suppress output"),
    json_out: bool = typer.Option(False, "-j", "--json", help="Output as JSON")
):
    """Restore logbook from a backup file."""
    import shutil
    from pathlib import Path
    from chronicle.db import DB_PATH
    
    backup_path = Path(file)
    if not backup_path.exists():
        if json_out:
            print_json({"status": "error", "message": f"Backup file not found: {file}"})
        else:
            console.print(f"[red]Backup file not found: {file}[/red]")
        return
    
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(backup_path, DB_PATH)
    
    if json_out:
        print_json({"status": "success", "message": "Logbook restored from backup", "file": str(DB_PATH)})
    elif not quiet:
        console.print(f"[green]✓[/green] Logbook restored from: [bold]{file}[/bold]")


@app.command("theme")
def set_theme(
    theme: str = typer.Argument(..., help="Theme to use: light, dark, or system"),
    quiet: bool = typer.Option(False, "-q", "--quiet", help="Suppress output"),
    json_out: bool = typer.Option(False, "-j", "--json", help="Output as JSON")
):
    """Set the terminal color theme (light/dark/system)."""
    from pathlib import Path
    import os
    
    config_dir = Path.home() / ".chronicle"
    config_dir.mkdir(exist_ok=True)
    config_file = config_dir / "theme.conf"
    
    if theme.lower() not in ["light", "dark", "system"]:
        if json_out:
            print_json({"status": "error", "message": "Invalid theme. Use: light, dark, or system"})
        else:
            console.print("[red]Invalid theme. Use: light, dark, or system[/red]")
        return
    
    config_file.write_text(theme.lower())
    
    if json_out:
        print_json({"status": "success", "message": f"Theme set to {theme}", "theme": theme})
    elif not quiet:
        console.print(f"[green]✓[/green] Theme set to [bold]{theme}[/bold]")


if __name__ == "__main__":
    app()