#!/bin/bash
# Docker-entrypoint: kopioi skriptit agenttikansioon ja käynnistä

set -e

# Kopioi Python-skriptit jos puuttuvat
for f in watcher.py server.py config_manager.py rag_memory.py sandbox_executor.py \
          file_parser.py llm_client.py swarm_manager.py evolution_engine.py; do
    if [ ! -f "/agentdir/$f" ]; then
        cp "/app/$f" "/agentdir/$f"
    fi
done

# Luo kansiot
mkdir -p /agentdir/Inbox /agentdir/Outbox /agentdir/memory /agentdir/plugins /agentdir/swarm

# Kopioi default config jos puuttuu
if [ ! -f "/agentdir/config.json" ]; then
    cp /app/config.json /agentdir/config.json
    echo "ℹ️  Kopioitu oletuskonfiguraatio → /agentdir/config.json"
fi
if [ ! -f "/agentdir/manifest.json" ] && [ -f "/app/manifest.json" ]; then
    cp /app/manifest.json /agentdir/manifest.json
fi

cd /agentdir

# Valitse käynnistystapa
case "$1" in
    watcher)
        echo "🚀 Käynnistetään watcher..."
        exec python3 watcher.py
        ;;
    server)
        echo "🌐 Käynnistetään A2A-serveri..."
        exec python3 server.py
        ;;
    both)
        echo "🚀 Käynnistetään watcher + A2A-serveri..."
        python3 server.py &
        exec python3 watcher.py
        ;;
    *)
        exec "$@"
        ;;
esac
