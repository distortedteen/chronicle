# Fish shell completion for Chronicle

# Main commands
set -l commands log idea win fail show stats export q note last view edit search tags browse delete undo redo backup restore theme

# Options
set -l options --help --version --quiet --json

# Categories for completion
set -l categories idea build learn fail win research general

# Formats for export
set -l formats markdown json

# Themes
set -l themes light dark system

# Command completions
complete -c chronicle -n "not __fish_seen_subcommand_from $commands" -a "$commands" -d "Chronicle commands"

# Global options
complete -c chronicle -n "not __fish_seen_subcommand_from $commands" -l help -d "Show this message and exit"
complete -c chronicle -n "not __fish_seen_subcommand_from $commands" -l version -d "Show version number"
complete -c chronicle -n "not __fish_seen_subcommand_from $commands" -l quiet -d "Suppress all output except errors"
complete -c chronicle -n "not __fish_seen_subcommand_from $commands" -l json -d "Output results as JSON"

# log command options
complete -c chronicle -n "__fish_seen_subcommand_from log" -s c -l category -d "Category" -a "$categories"
complete -c chronicle -n "__fish_seen_subcommand_from log" -s t -l title -d "Optional title"
complete -c chronicle -n "__fish_seen_subcommand_from log" -s m -l mood -d "Your mood/energy"
complete -c chronicle -n "__fish_seen_subcommand_from log" -l tag -d "Add tags (repeat for multiple)"

# idea, win, fail commands - just content
complete -c chronicle -n "__fish_seen_subcommand_from idea" -f -a "(__fish_print_common_commands)"

# show command options
complete -c chronicle -n "__fish_seen_subcommand_from show" -s n -l limit -d "Number of entries to show"
complete -c chronicle -n "__fish_seen_subcommand_from show" -s c -l category -d "Filter by category" -a "$categories"
complete -c chronicle -n "__fish_seen_subcommand_from show" -s s -l search -d "Filter by keyword"
complete -c chronicle -n "__fish_seen_subcommand_from show" -s d -l date -d "Filter by date: YYYY-MM-DD"
complete -c chronicle -n "__fish_seen_subcommand_from show" -l full -d "Show full content, no truncation"
complete -c chronicle -n "__fish_seen_subcommand_from show" -l table -d "Compact table view"

# stats, tags, browse - no additional options

# export command options
complete -c chronicle -n "__fish_seen_subcommand_from export" -s f -l format -d "Export format" -a "$formats"
complete -c chronicle -n "__fish_seen_subcommand_from export" -s o -l output -d "Output filename"

# q command - just content

# note command options
complete -c chronicle -n "__fish_seen_subcommand_from note" -s c -l category -d "Category" -a "$categories"
complete -c chronicle -n "__fish_seen_subcommand_from note" -s t -l title -d "Title"

# last command options
complete -c chronicle -n "__fish_seen_subcommand_from last" -s n -l limit -d "Number of entries to show"

# view command - takes entry ID

# edit command - takes entry ID

# search command - takes keyword

# delete, undo, redo - takes entry ID

# backup command options
complete -c chronicle -n "__fish_seen_subcommand_from backup" -s o -l output -d "Output filename"

# restore command - takes backup file path

# theme command - takes theme name
complete -c chronicle -n "__fish_seen_subcommand_from theme" -d "Theme" -a "$themes"