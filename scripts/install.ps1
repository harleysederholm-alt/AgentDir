# AgentDir – Windows-asennus (vastine install.sh:lle)
# Suorita agentdir-kansiossa: Set-ExecutionPolicy -Scope Process Bypass; .\install.ps1

$ErrorActionPreference = "Stop"

Write-Host ""
Write-Host "AgentDir – Asennus (Windows)"
Write-Host "=================================" -ForegroundColor Cyan
Write-Host ""

# Python 3.10+
$py = Get-Command python -ErrorAction SilentlyContinue
if (-not $py) {
    Write-Host "Python ei löydy PATH:sta. Asenna Python 3.10+." -ForegroundColor Red
    exit 1
}

$ver = python -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')"
$minor = [int](python -c "import sys; print(sys.version_info.minor)")
$major = [int](python -c "import sys; print(sys.version_info.major)")
if ($major -lt 3 -or $minor -lt 10) {
    Write-Host "Python $ver on liian vanha. Tarvitaan Python 3.10+." -ForegroundColor Red
    exit 1
}
Write-Host "Python $ver OK" -ForegroundColor Green

Write-Host ""
Write-Host "Asennetaan riippuvuudet..."

if (-not (Test-Path ".venv")) {
    python -m venv .venv
    Write-Host "   Luotiin .venv/"
}

& .\.venv\Scripts\python.exe -m pip install --quiet --upgrade pip
& .\.venv\Scripts\pip.exe install --quiet -r requirements.txt
if (Test-Path "requirements-ocr.txt") {
    Write-Host "   OCR-riippuvuudet (pdf2image, pytesseract)..."
    & .\.venv\Scripts\pip.exe install --quiet -r requirements-ocr.txt 2>$null
    if ($LASTEXITCODE -ne 0) {
        Write-Host "   Varoitus: OCR-paketit jäivät osittain asentamatta (Tesseract/Poppler erikseen)." -ForegroundColor Yellow
    }
}
if (Test-Path "pyproject.toml") {
    Write-Host "   Editable-paketti (pip install -e .)..."
    & .\.venv\Scripts\pip.exe install --quiet -e .
}

Write-Host "Riippuvuudet asennettu" -ForegroundColor Green

# Ollama
Write-Host ""
$ollama = Get-Command ollama -ErrorAction SilentlyContinue
if ($ollama) {
    Write-Host "Ollama löytyy" -ForegroundColor Green
    try {
        $null = Invoke-WebRequest -Uri "http://localhost:11434/api/tags" -UseBasicParsing -TimeoutSec 3
        Write-Host "   Ollama käynnissä"
        Write-Host ""
        Write-Host "   Ladataan mallit config.json:n mukaan (voi kestää)..."

        $cfg = Get-Content -Path "config.json" -Encoding UTF8 | ConvertFrom-Json
        $mainModel = $cfg.llm.model
        if (-not $mainModel) { $mainModel = "llama3.2:3b" }
        $embModel = $cfg.embedding.model
        if (-not $embModel) { $embModel = "mxbai-embed-large" }

        & ollama pull $mainModel
        if ($LASTEXITCODE -ne 0) { Write-Host "   Varoitus: mallin $mainModel lataus epäonnistui" -ForegroundColor Yellow }
        & ollama pull $embModel
        if ($LASTEXITCODE -ne 0) { Write-Host "   Varoitus: mallin $embModel lataus epäonnistui" -ForegroundColor Yellow }
        $embFb = $cfg.embedding.fallback
        if ($embFb -and "$embFb".Trim()) {
            Write-Host "   ollama pull $embFb ..."
            & ollama pull "$embFb"
            if ($LASTEXITCODE -ne 0) { Write-Host "   Varoitus: $embFb" -ForegroundColor Yellow }
        }
        if ($cfg.llm.fallback_models) {
            foreach ($m in $cfg.llm.fallback_models) {
                if ($m -and "$m".Trim()) {
                    Write-Host "   ollama pull $m ..."
                    & ollama pull "$m"
                    if ($LASTEXITCODE -ne 0) { Write-Host "   Varoitus: $m" -ForegroundColor Yellow }
                }
            }
        }
    }
    catch {
        Write-Host "   Ollama ei vastaa (käynnistä: ollama serve)" -ForegroundColor Yellow
    }
}
else {
    Write-Host "Ollama ei löydy. Asenna: https://ollama.com" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "Luodaan kansiot..."
$dirs = @("Inbox", "Outbox", "memory", "plugins", "swarm", "templates")
foreach ($d in $dirs) {
    if (-not (Test-Path $d)) { New-Item -ItemType Directory -Path $d | Out-Null }
}
Write-Host "Kansiot OK" -ForegroundColor Green

Write-Host ""
Write-Host "=================================" -ForegroundColor Cyan
Write-Host "Asennus valmis!" -ForegroundColor Green
Write-Host ""
Write-Host "Aktivoi venv ja käynnistä:"
Write-Host "  .\.venv\Scripts\Activate.ps1"
Write-Host "  python watcher.py"
Write-Host ""
Write-Host "A2A (valinnainen): python server.py"
Write-Host ""
