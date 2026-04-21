#!/usr/bin/env bash
# AgentDir – käynnistä watcher. Ollama käyntiin. chmod +x run.sh && ./run.sh
set -e
cd "$(dirname "$0")"
if [ ! -x ".venv/bin/python" ]; then
  echo "Puuttuva .venv. Aja ensin: ./install.sh" >&2
  exit 1
fi
exec .venv/bin/python watcher.py
