# `agentdir` shell completions

Clinical tab-completion for the three major POSIX shells. Nothing fancy;
it matches the subcommand list, global flags (`-v`, `--json`), and per-subcommand
flags (`--mode`, `--model`, `--tail`, `--path`, …). File suggestions for
`attach` are filtered to `.yaml` / `.yml` / `.md` — anything else the harness
rejects anyway.

## Bash

```bash
mkdir -p ~/.local/share/bash-completion/completions
cp completions/agentdir.bash ~/.local/share/bash-completion/completions/agentdir
# then: exec bash
```

## Zsh

```zsh
mkdir -p ~/.zsh/completions
cp completions/agentdir.zsh ~/.zsh/completions/_agentdir
# in ~/.zshrc:
#   fpath=(~/.zsh/completions $fpath)
#   autoload -Uz compinit && compinit
```

## Fish

```fish
mkdir -p ~/.config/fish/completions
cp completions/agentdir.fish ~/.config/fish/completions/agentdir.fish
```

The slash-command family (`/harness`, `/status`, `/clean`, `/attach`, `/logs`)
lives inside the REPL, not the shell — the built-in completion inside
`input()` handles those.
