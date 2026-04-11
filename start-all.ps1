#Requires -Version 5.1
# AgentDir: asennus (tarvittaessa), verify_setup, watcher + server omissa ikkunoissa.
# Käyttö: .\start-all.ps1  [-SkipVerify] [-SkipOllamaCheck] [-WatcherOnly] [-ServerOnly] [-Force] [-NoBrowser]

[CmdletBinding()]
param(
    [switch] $SkipVerify,
    [switch] $SkipOllamaCheck,
    [switch] $WatcherOnly,
    [switch] $ServerOnly,
    [switch] $Force,
    [switch] $NoBrowser
)

$ErrorActionPreference = "Stop"
$Root = $PSScriptRoot
Set-Location -LiteralPath $Root

$py = Join-Path $Root ".venv\Scripts\python.exe"

if (-not (Test-Path $py)) {
    Write-Host "Luodaan ympäristö (install.ps1)..." -ForegroundColor Cyan
    $install = Join-Path $Root "install.ps1"
    if (-not (Test-Path $install)) {
        Write-Host "install.ps1 puuttuu." -ForegroundColor Red
        exit 1
    }
    & $install
    if (-not (Test-Path $py)) {
        Write-Host ".venv puuttuu asennuksen jälkeen." -ForegroundColor Red
        exit 1
    }
}

if (-not $SkipOllamaCheck) {
    try {
        $null = Invoke-WebRequest -Uri "http://localhost:11434/api/tags" -UseBasicParsing -TimeoutSec 3
    }
    catch {
        Write-Host "VAROITUS: Ollama ei vastaa portissa 11434 – käynnistä Ollama." -ForegroundColor Yellow
    }
}

if (-not $SkipVerify) {
    Write-Host "verify_setup.py ..." -ForegroundColor Cyan
    & $py (Join-Path $Root "verify_setup.py")
    if ($LASTEXITCODE -ne 0) {
        if ($Force) {
            Write-Host "verify_setup epäonnistui; jatketaan (-Force)." -ForegroundColor Yellow
        }
        else {
            Write-Host "verify_setup epäonnistui. Käytä -SkipVerify tai -Force" -ForegroundColor Red
            exit 1
        }
    }
}

if ($ServerOnly -and $WatcherOnly) {
    Write-Host "Älä käytä -WatcherOnly ja -ServerOnly yhdessä." -ForegroundColor Red
    exit 1
}

if (-not $ServerOnly) {
    Write-Host "Käynnistetään watcher (uusi ikkuna)..." -ForegroundColor Green
    Start-Process -FilePath $py -ArgumentList "watcher.py" -WorkingDirectory $Root -WindowStyle Normal
    Start-Sleep -Seconds 1
}

if (-not $WatcherOnly) {
    Write-Host "Käynnistetään server + Web-UI (uusi ikkuna)..." -ForegroundColor Green
    Start-Process -FilePath $py -ArgumentList "server.py" -WorkingDirectory $Root -WindowStyle Normal
}

Write-Host ""
Write-Host "Valmis." -ForegroundColor Green
if (-not $WatcherOnly) {
    Write-Host "  Web-UI:  http://127.0.0.1:8080/ui/" -ForegroundColor Cyan
    Write-Host "  OpenAPI: http://127.0.0.1:8080/docs" -ForegroundColor Cyan
    if (-not $NoBrowser) {
        Start-Sleep -Seconds 3
        Start-Process "http://127.0.0.1:8080/ui/"
        Write-Host "Selain avattu (käytä -NoBrowser estääksesi)." -ForegroundColor Gray
    }
}
Write-Host "Sulje avautuneet konsoli-ikkunat lopettaaksesi palvelut." -ForegroundColor Gray
