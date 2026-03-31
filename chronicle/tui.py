# chronicle/tui.py

from textual.app import App, ComposeResult
from textual.widgets import (
    Header, Footer, Input, ListView, ListItem,
    Label, Static, Select, ContentSwitcher, Button, TextArea
)
from textual.containers import Horizontal, VerticalScroll, Container
from textual.binding import Binding
from textual.screen import ModalScreen, Screen
from textual import on

from chronicle.db import get_entries, get_connection, add_entry, get_entry_by_id, update_entry

CATEGORY_COLORS = {
    "idea": "yellow", "build": "cyan", "learn": "blue",
    "fail": "red", "win": "green", "research": "magenta", "general": "white"
}

CAT_ICONS = {
    "idea": "💡", "build": "🔨", "learn": "📚",
    "fail": "📉", "win":  "🏆", "research": "🔬", "general": "📝"
}

CATEGORY_OPTIONS = [
    ("All categories", "all"),
    ("Idea",        "idea"),
    ("Build",       "build"),
    ("Win",         "win"),
    ("Fail",        "fail"),
    ("Learn",       "learn"),
    ("Research",    "research"),
    ("General",     "general"),
]

CATEGORY_CHOICES = [
    ("General", "general"),
    ("Idea", "idea"),
    ("Build", "build"),
    ("Win", "win"),
    ("Fail", "fail"),
    ("Learn", "learn"),
    ("Research", "research"),
]


class EntryItem(ListItem):
    def __init__(self, entry) -> None:
        self.entry = entry
        icon  = CAT_ICONS.get(entry["category"], "📝")
        color = CATEGORY_COLORS.get(entry["category"], "white")
        time  = entry["timestamp"][5:16]
        title = entry["title"] or entry["content"]
        if len(title) > 44:
            title = title[:44] + "…"
        super().__init__(
            Label(f"{icon} [{color}]▎[/{color}] [dim]{time}[/dim]  {title}")
        )


class DetailPane(Static):
    def on_mount(self) -> None:
        self.update(self._render_empty())

    def _render_empty(self) -> str:
        return (
            "\n\n\n"
            "  [dim]No entry selected.[/dim]\n\n"
            "  [dim]Use ↑ ↓ or click to select an entry.[/dim]"
        )

    def _render_entry(self, e) -> str:
        icon  = CAT_ICONS.get(e["category"], "📝")
        color = CATEGORY_COLORS.get(e["category"], "white")

        header_title = e["title"] if e["title"] else ""
        lines = [
            f"[bold {color}]  {icon}  {e['category'].upper()}[/bold {color}]"
            + (f"  [white]{header_title}[/white]" if header_title else ""),
            f"  [{color}]{'━' * 42}[/{color}]",
            "",
        ]

        lines.append(f"  [dim]#{e['id']}   {e['timestamp']}[/dim]")
        lines.append(f"  [{color}]{e['category'].upper()}[/{color}]")

        if e["mood"]:
            lines.append(f"  [dim]mood › {e['mood']}[/dim]")

        if e["tags"]:
            tags = "  ".join(
                f"[{color}]#{t.strip()}[/{color}]"
                for t in e["tags"].split(",") if t.strip()
            )
            lines.append(f"  {tags}")

        lines += ["", f"  [dim]{'─' * 40}[/dim]", ""]

        words = e["content"].split()
        cur   = "  "
        for word in words:
            if len(cur) + len(word) + 1 > 56:
                lines.append(cur)
                cur = "  " + word + " "
            else:
                cur += word + " "
        if cur.strip():
            lines.append(cur)

        lines.append("")
        return "\n".join(lines)

    def show_entry(self, e) -> None:
        if e is None:
            self.update(self._render_empty())
        else:
            self.update(self._render_entry(e))


class StatsPane(Static):
    def render(self) -> str:
        from datetime import date, timedelta
        from collections import Counter

        conn    = get_connection()
        total   = conn.execute("SELECT COUNT(*) FROM entries").fetchone()[0]
        cats    = conn.execute(
            "SELECT category, COUNT(*) as n FROM entries "
            "GROUP BY category ORDER BY n DESC"
        ).fetchall()
        all_dates = [
            row[0][:10]
            for row in conn.execute("SELECT timestamp FROM entries").fetchall()
        ]
        conn.close()

        if total == 0:
            return "\n\n  [dim]No entries yet.[/dim]"

        date_counts = Counter(all_dates)
        today       = date.today()

        streak = 0
        while (today - timedelta(days=streak)).isoformat() in date_counts:
            streak += 1

        lines = [
            "",
            "  [bold]Overview[/bold]",
            f"  Total entries : [bold]{total}[/bold]",
            f"  Current streak: [bold]{'🔥 ' if streak else ''}{streak}[/bold] day(s)",
            "",
            "  [bold]By category[/bold]",
        ]

        max_n = max(row[1] for row in cats) if cats else 1
        for row in cats:
            cat, n = row[0], row[1]
            icon   = CAT_ICONS.get(cat, "📝")
            color  = CATEGORY_COLORS.get(cat, "white")
            bar    = "█" * int((n / max_n) * 18)
            pct    = int(n / total * 100)
            lines.append(
                f"  {icon} [{color}]{cat:<10}[/{color}]"
                f" [{color}]{bar:<18}[/{color}]"
                f" [dim]{n} ({pct}%)[/dim]"
            )

        lines += ["", "  [bold]Last 12 weeks[/bold]", ""]
        today_weekday = today.weekday()
        start = today - timedelta(weeks=11, days=today_weekday)

        HEAT   = ["·", "░", "▒", "▓", "█"]
        DAYS   = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]

        for day_i in range(7):
            cells = []
            for week_i in range(12):
                d = start + timedelta(weeks=week_i, days=day_i)
                n = date_counts.get(d.isoformat(), 0)
                level = (
                    0 if n == 0 else
                    1 if n == 1 else
                    2 if n <= 3 else
                    3 if n <= 6 else 4
                )
                color = "dim" if n == 0 else ("green" if n >= 3 else "yellow")
                cells.append(f"[{color}]{HEAT[level]}[/{color}]")
            lines.append(f"  [dim]{DAYS[day_i]}[/dim] " + "  ".join(cells))

        lines += [
            "",
            "  [dim]·none  ░1  ▒2-3  ▓4-6  █7+[/dim]",
            "",
        ]
        return "\n".join(lines)


class NewEntryScreen(ModalScreen):
    def __init__(self, callback) -> None:
        super().__init__()
        self.callback = callback

    def compose(self) -> ComposeResult:
        yield Container(
            Static("New Entry", id="modal-title"),
            Horizontal(Static("Category:"), Select(options=CATEGORY_CHOICES, value="general", id="entry-category"), id="modal-cat"),
            Horizontal(Static("Title:"), Input(placeholder="Optional title", id="entry-title"), id="modal-title-field"),
            Horizontal(Static("Mood:"), Input(placeholder="e.g., focused, stuck, fire", id="entry-mood"), id="modal-mood"),
            Horizontal(Static("Tags:"), Input(placeholder="comma, separated, tags", id="entry-tags"), id="modal-tags"),
            Static("Content:"),
            TextArea(id="entry-content"),
            Horizontal(Button("Save", variant="primary", id="btn-save"), Button("Cancel", variant="default", id="btn-cancel"), id="modal-buttons"),
            id="new-entry-dialog"
        )

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "btn-save":
            category = str(self.query_one("#entry-category", Select).value)
            title = self.query_one("#entry-title", Input).value or None
            mood = self.query_one("#entry-mood", Input).value or None
            tags = self.query_one("#entry-tags", Input).value
            tags_list = [t.strip() for t in tags.split(",") if t.strip()] if tags else None
            content = self.query_one("#entry-content", TextArea).value
            
            if content.strip():
                add_entry(content, category=category, title=title, mood=mood, tags=tags_list)
                self.callback()
        self.app.pop_screen()


class EditEntryScreen(ModalScreen):
    def __init__(self, entry, callback) -> None:
        super().__init__()
        self.entry = entry
        self.callback = callback

    def compose(self) -> ComposeResult:
        yield Container(
            Static(f"Edit Entry #{self.entry['id']}", id="modal-title"),
            Horizontal(Static("Category:"), Select(options=CATEGORY_CHOICES, value=self.entry["category"], id="entry-category"), id="modal-cat"),
            Horizontal(Static("Title:"), Input(value=self.entry["title"] or "", placeholder="Optional title", id="entry-title"), id="modal-title-field"),
            Horizontal(Static("Mood:"), Input(value=self.entry["mood"] or "", placeholder="e.g., focused, stuck, fire", id="entry-mood"), id="modal-mood"),
            Horizontal(Static("Tags:"), Input(value=self.entry["tags"] or "", placeholder="comma, separated, tags", id="entry-tags"), id="modal-tags"),
            Static("Content:"),
            TextArea(self.entry["content"], id="entry-content"),
            Horizontal(Button("Save", variant="primary", id="btn-save"), Button("Cancel", variant="default", id="btn-cancel"), id="modal-buttons"),
            id="edit-entry-dialog"
        )

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "btn-save":
            category = str(self.query_one("#entry-category", Select).value)
            title = self.query_one("#entry-title", Input).value or None
            mood = self.query_one("#entry-mood", Input).value or None
            tags = self.query_one("#entry-tags", Input).value
            tags_list = [t.strip() for t in tags.split(",") if t.strip()] if tags else None
            content = self.query_one("#entry-content", TextArea).value
            
            if content.strip():
                update_entry(self.entry["id"], content=content, category=category, 
                           title=title, mood=mood, tags=tags_list)
                self.callback()
        self.app.pop_screen()


class ChronicleApp(App):
    TITLE                  = "Chronicle"
    SUB_TITLE              = "Your Project Logbook"
    ENABLE_COMMAND_PALETTE = False

    CSS = """
    Screen {
        layout: vertical;
        background: $background;
    }

    Header {
        background: $surface;
        color: $text;
        text-style: bold;
    }

    #toolbar {
        height: 5;
        layout: horizontal;
        padding: 1 2;
        background: $surface;
        border-bottom: tall $primary 30%;
    }

    #search-input {
        width: 1fr;
        margin-right: 2;
        border: tall $primary 40%;
    }

    #search-input:focus {
        border: tall $accent;
    }

    #cat-select {
        width: 28;
        border: tall $primary 40%;
    }

    #main-area {
        layout: horizontal;
        height: 1fr;
    }

    #list-scroll {
        width: 50%;
        border-right: tall $primary 25%;
    }

    #right-panel {
        width: 50%;
        background: $surface;
    }

    #switcher {
        height: 1fr;
        width: 1fr;
    }

    #detail-pane {
        height: 1fr;
        overflow-y: auto;
        padding: 1 2;
    }

    #stats-pane {
        height: 1fr;
        overflow-y: auto;
        padding: 1 2;
    }

    ListView {
        background: $background;
        padding: 0 1;
    }

    EntryItem {
        padding: 0 1;
        border-left: thick transparent;
    }

    EntryItem:hover {
        background: $boost;
        border-left: thick $accent 60%;
    }

    EntryItem.--highlight {
        background: $accent 15%;
        border-left: thick $accent;
        color: $text;
        text-style: bold;
    }

    ListView:focus > EntryItem.--highlight {
        background: $accent 25%;
        border-left: thick $accent;
    }

    #empty-msg {
        padding: 2 2;
        color: $text-muted;
    }

    Footer {
        background: $surface;
        color: $text-muted;
    }

    #new-entry-dialog, #edit-entry-dialog {
        width: 60;
        height: auto;
        background: $surface;
        border: thick $primary;
        padding: 2 4;
        align: center middle;
    }

    #modal-title {
        text-align: center;
        text-style: bold;
        margin-bottom: 1;
    }

    #modal-cat, #modal-title-field, #modal-mood, #modal-tags {
        layout: horizontal;
        height: auto;
        margin-bottom: 1;
    }

    #modal-cat > Static, #modal-title-field > Static, 
    #modal-mood > Static, #modal-tags > Static {
        width: 12;
    }

    #modal-cat > Select, #modal-title-field > Input,
    #modal-mood > Input, #modal-tags > Input {
        width: 1fr;
    }

    #new-entry-dialog > TextArea, #edit-entry-dialog > TextArea {
        height: 10;
        margin-bottom: 1;
    }

    #modal-buttons {
        layout: horizontal;
        align: right middle;
        height: auto;
    }

    #modal-buttons > Button {
        margin-left: 1;
    }
    """

    BINDINGS = [
        Binding("q",      "quit",         "Quit"),
        Binding("s",      "toggle_stats", "Stats"),
        Binding("slash",  "focus_search", "Search"),
        Binding("escape", "clear_search", "Clear"),
        Binding("j",      "move_down",    "Down",  show=False),
        Binding("k",      "move_up",      "Up",    show=False),
        Binding("n",      "new_entry",    "New",   show=False),
        Binding("e",      "edit_entry",   "Edit",  show=False),
    ]

    _all_entries: list = []
    _showing_stats: bool = False

    def compose(self) -> ComposeResult:
        yield Header()

        with Horizontal(id="toolbar"):
            yield Input(
                placeholder="Press / to search...",
                id="search-input"
            )
            yield Select(
                options=CATEGORY_OPTIONS,
                value="all",
                allow_blank=False,
                compact=True,
                id="cat-select"
            )

        with Horizontal(id="main-area"):
            with VerticalScroll(id="list-scroll"):
                yield ListView(id="entry-list")
            with VerticalScroll(id="right-panel"):
                yield ContentSwitcher(
                    DetailPane(id="detail-pane"),
                    StatsPane(id="stats-pane"),
                    initial="detail-pane",
                    id="switcher"
                )

        yield Footer()

    def on_mount(self) -> None:
        self._load_entries()

    def _load_entries(
        self,
        search:   str = "",
        category: str = "all"
    ) -> None:
        self._all_entries = list(get_entries(
            limit    = 500,
            search   = search   or None,
            category = category if category != "all" else None,
        ))

        lv = self.query_one("#entry-list", ListView)
        lv.clear()

        if not self._all_entries:
            lv.append(ListItem(Label("[dim]  No entries found.[/dim]"), id="empty-msg"))
            self.query_one(DetailPane).show_entry(None)
            return

        for entry in self._all_entries:
            lv.append(EntryItem(entry))

        lv.index = 0
        self.query_one(DetailPane).show_entry(self._all_entries[0])

    @on(Input.Changed, "#search-input")
    def handle_search(self, event: Input.Changed) -> None:
        cat = str(self.query_one("#cat-select", Select).value)
        self._load_entries(search=event.value, category=cat)

    @on(Select.Changed, "#cat-select")
    def handle_category(self, event: Select.Changed) -> None:
        search = self.query_one("#search-input", Input).value
        self._load_entries(search=search, category=str(event.value))

    @on(ListView.Highlighted, "#entry-list")
    def handle_highlight(self, event: ListView.Highlighted) -> None:
        if event.item is None:
            return
        if not isinstance(event.item, EntryItem):
            return
        self.query_one(DetailPane).show_entry(event.item.entry)

    def action_toggle_stats(self) -> None:
        switcher = self.query_one("#switcher", ContentSwitcher)
        if self._showing_stats:
            switcher.current    = "detail-pane"
            self._showing_stats = False
        else:
            self.query_one(StatsPane).refresh()
            switcher.current    = "stats-pane"
            self._showing_stats = True

    def action_focus_search(self) -> None:
        self.query_one("#search-input", Input).focus()

    def action_clear_search(self) -> None:
        inp = self.query_one("#search-input", Input)
        if inp.value:
            inp.value = ""
        else:
            self.query_one("#entry-list", ListView).focus()

    def action_move_down(self) -> None:
        lv = self.query_one("#entry-list", ListView)
        lv.action_cursor_down()

    def action_move_up(self) -> None:
        lv = self.query_one("#entry-list", ListView)
        lv.action_cursor_up()

    def action_new_entry(self) -> None:
        def on_save():
            self._load_entries()
        self.push_screen(NewEntryScreen(on_save))

    def action_edit_entry(self) -> None:
        lv = self.query_one("#entry-list", ListView)
        if not lv.index or lv.index >= len(self._all_entries):
            return
        entry = self._all_entries[lv.index]
        
        def on_save():
            self._load_entries()
        self.push_screen(EditEntryScreen(dict(entry), on_save))


def launch() -> None:
    ChronicleApp().run()