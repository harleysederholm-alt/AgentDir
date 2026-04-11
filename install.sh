#!/bin/bash
# AgentDir – Asennusskripti (Linux / macOS)
# Kaytto: chmod +x install.sh && ./install.sh

set -e

BOLD='\033[1m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

echo ""
echo "AgentDir – Asennus"
echo "================================="
echo ""

if ! command -v python3 &> /dev/null; then
    echo -e "${RED}Python 3 ei loydy. Asenna Python 3.10+ ensin.${NC}"
    exit 1
fi

PYTHON_VERSION=$(python3 -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')")
REQUIRED_MAJOR=3
REQUIRED_MINOR=10
ACTUAL_MINOR=$(python3 -c "import sys; print(sys.version_info.minor)")
if [ "$(python3 -c "import sys; print(sys.version_info.major)")" -lt $REQUIRED_MAJOR ] || \
   [ "$ACTUAL_MINOR" -lt $REQUIRED_MINOR ]; then
    echo -e "${RED}Python $PYTHON_VERSION liian vanha. Tarvitaan Python 3.10+${NC}"
    exit 1
fi
echo -e "${GREEN}Python $PYTHON_VERSION${NC}"

echo ""
echo "Asennetaan riippuvuudet..."

if [ ! -d ".venv" ]; then
    python3 -m venv .venv
    echo "   Luotiin .venv/"
fi

# shellcheck source=/dev/null
source .venv/bin/activate

pip install --quiet --upgrade pip
pip install --quiet -r requirements.txt

if [ -f "requirements-ocr.txt" ]; then
    echo "   OCR-riippuvuudet..."
    pip install --quiet -r requirements-ocr.txt || echo -e "${YELLOW}   OCR-paketit osittain epaonnistuivat (Tesseract/Poppler erikseen).${NC}"
fi

if [ -f "pyproject.toml" ]; then
    echo "   pip install -e . ..."
    pip install --quiet -e .
fi

echo -e "${GREEN}Riippuvuudet asennettu${NC}"

echo ""
if command -v ollama &> /dev/null; then
    echo -e "${GREEN}Ollama loytyy${NC}"

    if curl -s http://localhost:11434/api/tags > /dev/null 2>&1; then
        echo "   Ollama kaynnissa"
        echo ""
        echo "   Ladataan mallit config.json:n mukaan..."

        MAIN_MODEL=$(python3 -c "import json; print(json.load(open('config.json'))['llm']['model'])" 2>/dev/null || echo "llama3.2:3b")
        EMB_MODEL=$(python3 -c "import json; print(json.load(open('config.json'))['embedding']['model'])" 2>/dev/null || echo "mxbai-embed-large")

        ollama pull "$MAIN_MODEL"   || echo -e "${YELLOW}  Malli $MAIN_MODEL epaonnistui${NC}"
        ollama pull "$EMB_MODEL"    || echo -e "${YELLOW}  Malli $EMB_MODEL epaonnistui${NC}"

        EMB_FB=$(python3 -c "import json; print(json.load(open('config.json')).get('embedding',{}).get('fallback','') or '')" 2>/dev/null || true)
        if [ -n "$EMB_FB" ]; then
            echo "   ollama pull $EMB_FB ..."
            ollama pull "$EMB_FB" || echo -e "${YELLOW}  $EMB_FB epaonnistui${NC}"
        fi

        python3 << 'PY'
import json
from pathlib import Path
import subprocess
import sys
p = Path("config.json")
if not p.exists():
    sys.exit(0)
cfg = json.loads(p.read_text(encoding="utf-8"))
for m in cfg.get("llm", {}).get("fallback_models") or []:
    if not m:
        continue
    print(f"   ollama pull {m} ...")
    r = subprocess.run(["ollama", "pull", str(m)])
    if r.returncode != 0:
        print(f"   (varoitus) {m}", file=sys.stderr)
PY
    else
        echo -e "${YELLOW}   Ollama ei vastaa. Kaynnista: ollama serve${NC}"
    fi
else
    echo -e "${YELLOW}Ollama ei asennettu. https://ollama.com${NC}"
fi

echo ""
echo "Luodaan kansiorakenne..."
mkdir -p Inbox Outbox memory plugins swarm templates
echo -e "${GREEN}Kansiot OK${NC}"

echo ""
echo "================================="
echo -e "${GREEN}${BOLD}Asennus valmis!${NC}"
echo ""
echo "Kaynnista:"
echo "  source .venv/bin/activate && python3 watcher.py"
echo ""
echo "A2A (toinen terminaali):"
echo "  python3 server.py"
echo ""
