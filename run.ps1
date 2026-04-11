# AgentDir – käynnistä watcher (käyttää .venv-pythonia suoraan)
# Ollama tulee olla käynnissä. Aja agentdir-kansiosta: .\run.ps1

$ErrorActionPreference = "Stop"
Set-Location $PSScriptRoot

$py = Join-Path $PSScriptRoot ".venv\Scripts\python.exe"
if (-not (Test-Path $py)) {
    Write-Host "Puuttuva .venv. Aja ensin: .\install.ps1" -ForegroundColor Yellow
    exit 1
}

& $py watcher.py
