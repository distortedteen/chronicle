#!/bin/bash
# Chronicle Bash Completion

_chroniclectrl_complete() {
    local cur prev opts
    COMPREPLY=()
    cur="${COMP_WORDS[COMP_CWORD]}"
    prev="${COMP_WORDS[COMP_CWORD-1]}"

    opts="log idea win fail show stats export q note last view edit search tags browse delete undo redo backup restore theme --help --version --quiet --json"

    case "${prev}" in
        -c|--category)
            COMPREPLY=( $(compgen -W "idea build learn fail win research general" -- ${cur}) )
            return 0
            ;;
        -t|--title|-m|--mood)
            return 0
            ;;
        --tag)
            return 0
            ;;
        -n|--limit|-d|--date|-f|--format|-o|--output)
            return 0
            ;;
        chronicle)
            COMPREPLY=( $(compgen -W "${opts}" -- ${cur}) )
            return 0
            ;;
    esac

    COMPREPLY=( $(compgen -W "${opts}" -- ${cur}) )
}

complete -F _chroniclectrl_complete chronicle