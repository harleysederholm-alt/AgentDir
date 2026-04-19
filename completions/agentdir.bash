# agentdir — bash completion
#
# Installation:
#   mkdir -p ~/.local/share/bash-completion/completions
#   cp completions/agentdir.bash ~/.local/share/bash-completion/completions/agentdir
#   # or source inline:
#   . completions/agentdir.bash
#
# Provides completion for subcommands and --mode values. Slash-commands
# live inside the REPL and are not completed at the shell level.

_agentdir_complete() {
    local cur prev words cword
    _init_completion || return

    local cmds="run init status benchmark harness clean attach logs print"
    local global_flags="-v --verbose --json -h --help"

    case "$prev" in
        --mode)
            COMPREPLY=( $(compgen -W "openclaw hermes" -- "$cur") )
            return 0
            ;;
        --model)
            COMPREPLY=( $(compgen -W "auto gemma4:e4b gemma2:2b llama3.2:3b mistral:7b" -- "$cur") )
            return 0
            ;;
        --tail)
            COMPREPLY=( $(compgen -W "10 20 50 100" -- "$cur") )
            return 0
            ;;
        --path)
            _filedir -d
            return 0
            ;;
        attach)
            _filedir '@(yaml|yml|md)'
            return 0
            ;;
    esac

    if [[ "$cur" == -* ]]; then
        COMPREPLY=( $(compgen -W "$global_flags --mode --model --path --tail --task-id" -- "$cur") )
        return 0
    fi

    # First positional → subcommand
    local i subcmd=""
    for ((i=1; i < cword; i++)); do
        case "${words[i]}" in
            -*) continue ;;
            *) subcmd="${words[i]}"; break ;;
        esac
    done

    if [[ -z "$subcmd" ]]; then
        COMPREPLY=( $(compgen -W "$cmds" -- "$cur") )
        return 0
    fi

    case "$subcmd" in
        attach) _filedir '@(yaml|yml|md)' ;;
        *) COMPREPLY=() ;;
    esac
}

complete -F _agentdir_complete agentdir
