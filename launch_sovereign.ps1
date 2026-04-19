#Requires -Version 5.1
# launch_sovereign.ps1 - Achii Sovereign Engine v4.2 Launcher
# Käynnistää kaikki järjestelmät yhdellä komennolla ja jättää REPL:n tähän terminaaliin.

$ErrorActionPreference = "Stop"
$Root = $PSScriptRoot
Set-Location -LiteralPath $Root

Write-Host "" -ForegroundColor Cyan
Write-Host "  ╔══════════════════════════════════════════════════╗" -ForegroundColor Cyan
Write-Host "  ║  ACHII SOVEREIGN ENGINE v4.2                    ║" -ForegroundColor Cyan
Write-Host "  ║  The Rusty Awakening                            ║" -ForegroundColor Cyan
Write-Host "  ╚══════════════════════════════════════════════════╝" -ForegroundColor Cyan
Write-Host ""

$py = Join-Path $Root ".venv\Scripts\python.exe"
if (-not (Test-Path $py)) {
    # Fallback: järjestelmän Python
    $py = "python"
    Write-Host "  [!] .venv ei löydy — käytetään järjestelmän Pythonia" -ForegroundColor Yellow
}

# 1. KÄYNNISTETÄÄN A2A SERVER (FastAPI portti 8080)
Write-Host "  [1/4] Käynnistetään A2A Server (portti 8080)..." -ForegroundColor Green
Start-Process -FilePath $py -ArgumentList "server.py" -WorkingDirectory $Root -WindowStyle Minimized

# 2. KÄYNNISTETÄÄN WATCHER (Inbox-valvoja)
Write-Host "  [2/4] Käynnistetään Watcher (Inbox-valvoja)..." -ForegroundColor Green
Start-Process -FilePath $py -ArgumentList "watcher.py" -WorkingDirectory $Root -WindowStyle Minimized

# 3. KÄYNNISTETÄÄN ACHII CORE (Needy Loop + WebSocket portti 8081)
Write-Host "  [3/4] Käynnistetään Achii Core (WS portti 8081)..." -ForegroundColor Green
Start-Process -FilePath $py -ArgumentList "achii_project/achii_core.py" -WorkingDirectory $Root -WindowStyle Minimized

Start-Sleep -Seconds 2

# 4. KÄYNNISTETÄÄN DESKTOP (Vite dev server portti 5173)
Write-Host "  [4/4] Käynnistetään Achii Desktop (Vite :5173)..." -ForegroundColor Green
Start-Process -FilePath "cmd.exe" -ArgumentList "/c cd desktop && npm run dev" -WorkingDirectory $Root -WindowStyle Normal

Start-Sleep -Seconds 2

# 5. AVATAR REPL — tähän terminaaliin
Write-Host ""
Write-Host "  ════════════════════════════════════════════════════" -ForegroundColor DarkGray
Write-Host "  Kaikki järjestelmät käynnissä:" -ForegroundColor Green
Write-Host "    A2A Server      → http://127.0.0.1:8080" -ForegroundColor Gray
Write-Host "    Achii Core (WS) → ws://127.0.0.1:8081/ws/achii" -ForegroundColor Gray
Write-Host "    Desktop UI      → http://127.0.0.1:5173" -ForegroundColor Gray
Write-Host "  ════════════════════════════════════════════════════" -ForegroundColor DarkGray
Write-Host ""

# Käynnistetään Sovereign REPL suoraan tähän terminaaliin
& $py cli.py
