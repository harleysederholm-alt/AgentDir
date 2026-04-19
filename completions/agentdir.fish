# agentdir — fish completion
#
# Installation:
#   mkdir -p ~/.config/fish/completions
#   cp completions/agentdir.fish ~/.config/fish/completions/agentdir.fish

set -l cmds run init status benchmark harness clean attach logs print

function __agentdir_needs_cmd
    set -l tokens (commandline -opc)
    if test (count $tokens) -eq 1
        return 0
    end
    # Scan for the first non-flag token after `agentdir`.
    for t in $tokens[2..-1]
        switch $t
            case '-*'
                continue
            case '*'
                return 1
        end
    end
    return 0
end

function __agentdir_using_cmd
    set -l tokens (commandline -opc)
    for t in $tokens[2..-1]
        switch $t
            case '-*'
                continue
            case $argv[1]
                return 0
            case '*'
                return 1
        end
    end
    return 1
end

# Subcommands — only when we haven't picked one yet.
complete -c agentdir -n __agentdir_needs_cmd -a run       -d 'aja orkestroitu tehtävä'
complete -c agentdir -n __agentdir_needs_cmd -a init      -d 'alusta AgentDir-rakenne'
complete -c agentdir -n __agentdir_needs_cmd -a status    -d 'moottorin tila'
complete -c agentdir -n __agentdir_needs_cmd -a benchmark -d 'latency · tok/s testit'
complete -c agentdir -n __agentdir_needs_cmd -a harness   -d 'listaa .yaml-valjaat'
complete -c agentdir -n __agentdir_needs_cmd -a clean     -d 'tyhjennä konteksti-ikkuna'
complete -c agentdir -n __agentdir_needs_cmd -a attach    -d 'liitä .yaml / .md tiedosto'
complete -c agentdir -n __agentdir_needs_cmd -a logs      -d 'viimeisimmät lokit'
complete -c agentdir -n __agentdir_needs_cmd -a print     -d 'Agent Print -raportti'

# Global flags (available everywhere)
complete -c agentdir -s v -l verbose -d 'verbose cognitive trace'
complete -c agentdir      -l json    -d 'machine-readable output'

# Per-subcommand flags
complete -c agentdir -n '__agentdir_using_cmd run' -l mode  -a 'openclaw hermes' -d 'workflow mode'
complete -c agentdir -n '__agentdir_using_cmd run' -l model -a 'auto gemma4:e4b gemma2:2b llama3.2:3b mistral:7b' -d 'mallitunnus tai auto'
complete -c agentdir -n '__agentdir_using_cmd init' -l path -d 'kohdehakemisto' -x -a '(__fish_complete_directories)'
complete -c agentdir -n '__agentdir_using_cmd attach' -k -x -a '(__fish_complete_suffix .yaml; __fish_complete_suffix .yml; __fish_complete_suffix .md)'
complete -c agentdir -n '__agentdir_using_cmd logs' -l tail -a '10 20 50 100' -d 'rivien määrä'
complete -c agentdir -n '__agentdir_using_cmd print' -l task-id -d 'tehtävän id tai latest'
