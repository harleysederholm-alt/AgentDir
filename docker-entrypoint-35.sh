#!/bin/bash
# docker-entrypoint-35.sh — AgentDir 3.5 Sovereign Engine
# Käynnistää oikean moodin Docker-kontissa.

set -e

# Jos AGENTDIR_TARGET annettu, käytä sitä työhakemistona
if [ -n "$AGENTDIR_TARGET" ] && [ -d "$AGENTDIR_TARGET" ]; then
    cd "$AGENTDIR_TARGET"
fi

# Alusta rakenne jos puuttuu
if [ ! -f "!_SOVEREIGN.md" ]; then
    echo "[INIT] Alustetaan AgentDir 3.5 -rakenne..."
    python /app/cli.py init --path .
fi

# Käynnistä komento tai oletus
case "${1:-status}" in
    run)
        shift
        exec python /app/cli.py run "$@"
        ;;
    status)
        exec python /app/cli.py status
        ;;
    benchmark)
        exec python /app/cli.py benchmark
        ;;
    server)
        exec python /app/server.py
        ;;
    test)
        exec python -m pytest /app/workspace/tests/ -v
        ;;
    shell)
        exec /bin/bash
        ;;
    *)
        exec python /app/cli.py "$@"
        ;;
esac
