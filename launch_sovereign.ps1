#Requires -Version 5.1
# launch_sovereign.ps1 - The Ultimate Sovereign Engine Launcher
# Tämä skripti nivoo kaiken yhteen ja jättää puhtaan REPL-käyttöliittymän nykyiseen terminaaliin.

$ErrorActionPreference = "Stop"
$Root = $PSScriptRoot
Set-Location -LiteralPath $Root

Write-Host "==========================================" -ForegroundColor Cyan
Write-Host " Käynnistetään Sovereign Engine (Fullstack) " -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan

$py = Join-Path $Root ".venv\Scripts\python.exe"
if (-not (Test-Path $py)) {
    Write-Host "VIRHE: .venv puuttuu! Aja install.ps1 ensin." -ForegroundColor Red
    exit 1
}

# 1. KÄYNNISTETÄÄN BACKENDIT (Minimoituna, ei häiritse visuaalista kokemusta)
Write-Host "-> Käynnistetään A2A Server & Watcher taustalle..." -ForegroundColor Green
Start-Process -FilePath $py -ArgumentList "server.py" -WorkingDirectory $Root -WindowStyle Minimized
Start-Process -FilePath $py -ArgumentList "watcher.py" -WorkingDirectory $Root -WindowStyle Minimized
Start-Sleep -Seconds 2

# 2. KÄYNNISTETÄÄN TAURI-DESKTOP (Visuaalinen hallinta)
Write-Host "-> Käynnistetään Tauri Web-UI / Desktop ohjelma..." -ForegroundColor Green
Start-Process -FilePath "cmd.exe" -ArgumentList "/c cd desktop && npx tauri dev" -WorkingDirectory $Root -WindowStyle Normal
Start-Sleep -Seconds 2

# 3. KÄYNNISTETÄÄN AGENTDIR REPL (Tähän terminaaliin)
Write-Host "-> Tuodaan Sovereign Matrix tähän terminaaliin..." -ForegroundColor Green
Start-Sleep -Seconds 1

# Käynnistetään Sovereign REPL suoraan tähän terminaaliin
& $py cli.py
