# Chronicle — Your Project Logbook

<p align="center">
  <img src="https://img.shields.io/pypi/v/chronicle-cli" alt="PyPI version">
  <img src="https://img.shields.io/pypi/pyversions/chronicle-cli" alt="Python versions">
  <img src="https://img.shields.io/pypi/l/chronicle-cli" alt="License">
</p>

> Log the journey. Tell the story.

Chronicle is a minimal CLI logbook built for builders, makers, and anyone tracking their project journey. Log your ideas, wins, failures, and progress — with accurate timestamps — as you build.

---

## Features

- **Quick Logging** — Multiple ways to log entries (standard, quick, interactive)
- **Categories** — Organize entries by type (idea, build, learn, fail, win, research, general)
- **Tags & Mood** — Add metadata to entries for better organization
- **Rich CLI** — Beautiful terminal output with colors and formatting
- **Interactive TUI** — Browse entries in an interactive terminal interface
- **Search & Filter** — Find entries by keyword, category, or date
- **Statistics** — Track your journey with stats, streaks, and heatmaps
- **Export** — Export your logbook to Markdown or JSON
- **Backup/Restore** — Full database backup and restore capability
- **Undo/Redo** — Revert accidental edits
- **Cross-Platform** — Works on Linux, macOS, and Windows
- **Shell Completions** — Bash, Zsh, and Fish support

---

## Installation

```bash
pip install chronicle-cli
```

Or install from source:

```bash
git clone https://github.com/distortedteen/chronicle.git
cd chronicle
pip install -e .
```

---

## Quick Start

```bash
# Log an entry
chronicle log "Had a breakthrough on the auth flow" -c build

# Quick log with category shortcut
chronicle q b finished the auth module

# Log an idea
chronicle idea "What if we added voice logging?"

# Log a win
chronicle win "First real user signed up"

# Log a failure/lesson
chronicle fail "Shipped a bug that deleted sessions. Lesson: always backup."

# View your entries
chronicle show

# View stats
chronicle stats

# Export to Markdown
chronicle export --format markdown
```

---

## Commands

### Logging Commands

| Command | Description | Example |
|---------|-------------|---------|
| `log` | Log a new entry | `chronicle log "content" -c build` |
| `idea` | Quick-log an idea | `chronicle idea "new feature idea"` |
| `win` | Log a win | `chronicle win "milestone achieved"` |
| `fail` | Log a failure/lesson | `chronicle fail "what went wrong"` |
| `q` | Ultra-fast log | `chronicle q b quick note` |
| `note` | Interactive multi-line | `chronicle note -c build` |

### Viewing Commands

| Command | Description |
|---------|-------------|
| `show` | Show log entries (card/table view) |
| `last` | Show last N entries in full detail |
| `view` | View one entry by ID |
| `search` | Search entries by keyword |
| `stats` | Show journey stats and heatmap |
| `tags` | List all tags with counts |
| `browse` | Open interactive TUI browser |

### Management Commands

| Command | Description |
|---------|-------------|
| `edit` | Edit an existing entry |
| `delete` | Delete an entry by ID |
| `undo` | Restore entry from backup |
| `redo` | Re-apply undone edit |
| `backup` | Create full database backup |
| `restore` | Restore from backup file |
| `export` | Export to Markdown or JSON |
| `theme` | Set terminal theme (light/dark/system) |

### Global Options

| Option | Short | Description |
|--------|-------|-------------|
| `--version` | | Show version number |
| `--quiet` | `-q` | Suppress output |
| `--json` | `-j` | JSON output |
| `--help` | | Show help |

---

## Categories

Chronicle supports 7 categories:

| Category | Shortcut | Description |
|----------|----------|-------------|
| `general` | `g` | General notes (default) |
| `idea` | `i` | Ideas and brainstorming |
| `build` | `b` | Building/implementation |
| `learn` | `l` | Learning and research |
| `fail` | `l` | Failures and lessons |
| `win` | `w` | Wins and achievements |
| `research` | `r` | Research and investigation |

### Category Shortcuts with `q` Command

```bash
chronicle q b built the login page       # build
chronicle q i a new feature idea          # idea
chronicle q w shipped v1.0                # win
chronicle q f fixed a bug                 # fail
chronicle q l learned about async         # learn
chronicle q r researched APIs              # research
chronicle q g random thought              # general
```

---

## TUI Browser

Launch the interactive terminal UI:

```bash
chronicle browse
```

### Keyboard Shortcuts

| Key | Action |
|-----|--------|
| `↑` / `↓` | Navigate entries |
| `/` | Focus search |
| `Esc` | Clear search |
| `s` | Toggle stats view |
| `n` | New entry |
| `e` | Edit selected entry |
| `q` | Quit |

---

## Shell Completions

### Bash

```bash
# Source the completion script
source /path/to/shell_completions/chronicle.bash

# Or copy to your completions directory
cp shell_completions/chronicle.bash /etc/bash_completion.d/
```

### Zsh

```bash
# Copy to your completions directory
cp shell_completions/chronicle.zsh ~/.zsh/completions/_chronicle

# Or add to fpath in .zshrc
fpath=(~/.zsh/completions $fpath)
```

### Fish

```bash
# Copy to your completions directory
cp shell_completions/chronicle.fish ~/.config/fish/completions/chronicle.fish
```

---

## Configuration

Chronicle stores data in:

- **Database**: `~/.chronicle/logbook.db`
- **Config**: `~/.chronicle/` (theme settings, etc.)

---

## Development

```bash
# Clone the repo
git clone https://github.com/distortedteen/chronicle.git
cd chronicle

# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # or .venv\Scripts\activate on Windows

# Install dependencies
pip install -e .

# Run tests
pytest

# Run the CLI
chronicle --help
```

---

## License

MIT License — Copyright (c) 2026 Pratyay Mukherjee

---

## Support

- Report issues: https://github.com/distortedteen/chronicle/issues
- View changelog: https://github.com/distortedteen/chronicle/releases