# Changelog

All notable changes to Chronicle will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [0.1.0] - 2024-04-01

### Added

- **Core Logging**
  - `log` command - Log a new entry with category, title, mood, and tags
  - `idea` command - Quick-log an idea
  - `win` command - Log a win/achievement
  - `fail` command - Log a failure or lesson learned
  - `q` command - Ultra-fast logging with category shortcuts
  - `note` command - Interactive multi-line note entry

- **Viewing & Search**
  - `show` command - Display entries in card or table view
  - `last` command - Show last N entries in full detail
  - `view` command - View one entry by ID
  - `search` command - Full-text search with highlighting
  - `tags` command - List all tags with usage counts
  - `stats` command - Journey stats with streak and heatmap
  - `browse` command - Interactive TUI browser

- **Management**
  - `edit` command - Edit existing entries
  - `delete` command - Delete entries by ID
  - `undo` / `redo` commands - Restore/redo edits with automatic backups
  - `backup` / `restore` commands - Full database backup and restore
  - `export` command - Export to Markdown or JSON
  - `theme` command - Set terminal theme (light/dark/system)

- **Global Options**
  - `--version` - Show version number
  - `--quiet` / `-q` - Suppress output
  - `--json` / `-j` - JSON output for scripting

- **Categories**
  - 7 categories: idea, build, learn, fail, win, research, general
  - Category shortcuts: b, i, w, f, l, r, g
  - Color-coded display with icons

- **TUI Features**
  - Interactive entry browser
  - Search and category filtering
  - Stats panel with heatmap
  - Entry creation and editing via modal dialogs

- **Shell Completions**
  - Bash completion script
  - Zsh completion script
  - Fish completion script

- **Cross-Platform**
  - Linux, macOS, and Windows support

### Dependencies

- typer >= 0.9
- rich >= 13
- textual >= 8.0
- Python >= 3.9

---

## [0.0.1] - 2024-03-14

### Added

- Initial pre-release version
- Basic logging commands
- SQLite database storage
- Terminal output formatting

---

[0.1.0]: https://github.com/distortedteen/chronicle/releases/tag/v0.1.0
[0.0.1]: https://github.com/distortedteen/chronicle/releases/tag/v0.0.1