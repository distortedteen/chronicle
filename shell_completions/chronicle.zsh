#compdef chronicle

local -a _commands
_commands=(
  'log:Log a new entry'
  'idea:Quick-log an idea'
  'win:Log a win, no matter how small'
  'fail:Log a failure or lesson learned'
  'show:Show log entries'
  'stats:Show journey stats'
  'export:Export your log to Markdown or JSON'
  'q:Ultra-fast log'
  'note:Write a longer entry interactively'
  'last:Show your last N entries in full detail'
  'view:View one entry in full detail by its ID'
  'edit:Edit an existing entry'
  'search:Search entries by keyword'
  'tags:List all tags you have used'
  'browse:Open the interactive TUI browser'
  'delete:Delete an entry by ID'
  'undo:Restore an entry to its previous state from backup'
  'redo:Re-apply the most recent edit to an entry'
  'backup:Create a full backup of your logbook'
  'restore:Restore logbook from a backup file'
  'theme:Set the terminal color theme'
)

local -a _options
_options=(
  '--help:Show this message and exit'
  '--version:Show version number'
  '--quiet:Suppress all output except errors'
  '--json:Output results as JSON'
)

case "$words[1]" in
  log)
    _arguments -C \
      '1:: :->log' \
      '2:: :->content' && return 0
    case "$state" in
      log)
        _describe 'command' _commands
        ;;
      content)
        _message 'Your log entry'
        ;;
    esac
    ;;
  show)
    _arguments \
      '(-n --limit)'{-n,--limit}'[Number of entries to show]:number:' \
      '(-c --category)'{-c,--category}'[Filter by category]:category:(idea build learn fail win research general)' \
      '(-s --search)'{-s,--search}'[Filter by keyword]:keyword:' \
      '(-d --date)'{-d,--date}'[Filter by date]:date:' \
      '(--full)'[Show full content]' \
      '(--table)'[Compact table view]'
    ;;
  edit)
    _arguments \
      '1:entry id:_numbers'
    ;;
  delete|undo|redo)
    _arguments \
      '1:entry id:_numbers'
    ;;
  backup)
    _arguments \
      '(-o --output)'{-o,--output}'[Output filename]:filename:'
    ;;
  restore)
    _arguments \
      '1:backup file:_files'
    ;;
  theme)
    _arguments \
      '1:theme:(light dark system)'
    ;;
  export)
    _arguments \
      '(-f --format)'{-f,--format}'[Export format]:format:(markdown json)' \
      '(-o --output)'{-o,--output}'[Output filename]:filename:'
    ;;
  *)
    _describe 'command' _commands
    _describe 'option' _options
    ;;
esac