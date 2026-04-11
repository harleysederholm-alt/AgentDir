#!/bin/bash
# AgentDir v1.0 – Asennusskripti
# Käyttö: curl -fsSL https://raw.githubusercontent.com/YOUR_GITHUB_USER/agentdir/main/install.sh | sh
# Tai paikallisesti: chmod +x install.sh && ./install.sh

set -e

BOLD='\033[1m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

echo ""
echo "🧬 AgentDir v1.0 – Asennus"
echo "================================="
echo ""

# ── Tarkista Python ───────────────────────────────────────────────────────────
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}❌ Python 3 ei löydy. Asenna Python 3.10+ ensin.${NC}"
    exit 1
fi

PYTHON_VERSION=$(python3 -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')")
REQUIRED_MAJOR=3
REQUIRED_MINOR=10

ACTUAL_MINOR=$(python3 -c "import sys; print(sys.version_info.minor)")
if [ "$(python3 -c "import sys; print(sys.version_info.major)")" -lt $REQUIRED_MAJOR ] || \
   [ "$ACTUAL_MINOR" -lt $REQUIRED_MINOR ]; then
    echo -e "${RED}❌ Python $PYTHON_VERSION liian vanha. Tarvitaan Python 3.10+${NC}"
    exit 1
fi
echo -e "${GREEN}✅ Python $PYTHON_VERSION${NC}"

# ── Asenna pip-riippuvuudet ───────────────────────────────────────────────────
echo ""
echo "📦 Asennetaan riippuvuudet..."

# Käytä virtual env jos mahdollista
if [ ! -d ".venv" ]; then
    python3 -m venv .venv
    echo "   Luotiin .venv/"
fi

source .venv/bin/activate 2>/dev/null || true

pip install --quiet --upgrade pip
pip install --quiet -r requirements.txt

echo -e "${GREEN}✅ Riippuvuudet asennettu${NC}"

# ── Tarkista Ollama ───────────────────────────────────────────────────────────
echo ""
if command -v ollama &> /dev/null; then
    echo -e "${GREEN}✅ Ollama löytyy${NC}"

    # Tarkista käynnissä
    if curl -s http://localhost:11434/api/tags > /dev/null 2>&1; then
        echo "   Ollama käynnissä ✓"
        echo ""
        echo "   Ladataan tarvittavat mallit (voi kestää hetken)..."

        MAIN_MODEL=$(python3 -c "import json; print(json.load(open('config.json'))['llm']['model'])" 2>/dev/null || echo "llama3.2:3b")
        EMB_MODEL=$(python3 -c "import json; print(json.load(open('config.json'))['embedding']['model'])" 2>/dev/null || echo "mxbai-embed-large")

        ollama pull $MAIN_MODEL   || echo -e "${YELLOW}⚠️  Mallin $MAIN_MODEL lataus epäonnistui${NC}"
        ollama pull $EMB_MODEL    || echo -e "${YELLOW}⚠️  Mallin $EMB_MODEL lataus epäonnistui${NC}"
    else
        echo -e "${YELLOW}   ⚠️  Ollama ei käynnissä. Käynnistä: ollama serve${NC}"
    fi
else
    echo -e "${YELLOW}⚠️  Ollama ei asennettu. Asenna: https://ollama.com${NC}"
fi

# ── Luo kansiorakenne ─────────────────────────────────────────────────────────
echo ""
echo "📁 Luodaan kansiorakenne..."
mkdir -p Inbox Outbox memory plugins swarm templates
echo -e "${GREEN}✅ Kansiot luotu${NC}"

# ── Valmis ────────────────────────────────────────────────────────────────────
echo ""
echo "================================="
echo -e "${GREEN}${BOLD}🚀 Asennus valmis!${NC}"
echo ""
echo "Käynnistä agentti:"
echo "  python3 watcher.py"
echo ""
echo "A2A-serveri (toisessa terminaalissa):"
echo "  python3 server.py"
echo ""
echo "Testaa:"
echo "  echo 'Tee tiivistelmä tästä tekstistä: Tekoäly on...' > Inbox/testi.txt"
echo ""
