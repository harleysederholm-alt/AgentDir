#compdef agentdir
# agentdir — zsh completion
#
# Installation:
#   mkdir -p ~/.zsh/completions
#   cp completions/agentdir.zsh ~/.zsh/completions/_agentdir
#   echo 'fpath=(~/.zsh/completions $fpath); autoload -Uz compinit; compinit' >> ~/.zshrc

_agentdir() {
    local -a subcmds global_flags modes models

    subcmds=(
        'run:aja orkestroitu tehtävä (openclaw | hermes)'
        'init:alusta AgentDir-rakenne kansioon'
        'status:tulosta moottorin tila'
        'benchmark:suorituskykytestit (latency · tok/s)'
        'harness:listaa aktiiviset .yaml-valjaat'
        'clean:tyhjennä konteksti-ikkuna'
        'attach:liitä .yaml / .md cognitive scaffoldiin'
        'logs:näytä viimeisimmät lokimerkinnät'
        'print:tulosta Agent Print -raportti'
    )

    global_flags=(
        '-v[verbose cognitive trace]'
        '--verbose[verbose cognitive trace]'
        '--json[emit machine-readable output]'
        '-h[show help]'
        '--help[show help]'
    )

    modes=(openclaw hermes)
    models=(auto gemma4:e4b gemma2:2b llama3.2:3b mistral:7b)

    _arguments -C \
        "${global_flags[@]}" \
        '1: :->cmd' \
        '*:: :->args'

    case $state in
        cmd)
            _describe 'command' subcmds
            ;;
        args)
            case $words[1] in
                run)
                    _arguments \
                        '--mode[workflow mode]:mode:(openclaw hermes)' \
                        '--model[model id or auto]:model:($models)' \
                        '1:task: '
                    ;;
                init)
                    _arguments '--path[target directory]:path:_files -/'
                    ;;
                attach)
                    _arguments '1:file:_files -g "*.(yaml|yml|md)"'
                    ;;
                logs)
                    _arguments '--tail[number of lines]:lines:(10 20 50 100)'
                    ;;
                print)
                    _arguments '--task-id[task id or latest]:task-id:'
                    ;;
            esac
            ;;
    esac
}

_agentdir "$@"
