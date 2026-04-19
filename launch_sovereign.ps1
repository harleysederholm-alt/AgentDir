#Requires -Version 5.1
# launch_sovereign.ps1 - Achii Sovereign Engine v4.2 Launcher
# Käynnistää kaikki järjestelmät yhdellä komennolla ja jättää REPL:n tähän terminaaliin.

$ErrorActionPreference = "Stop"
$Root = $PSScriptRoot
Set-Location -LiteralPath $Root

Write-Host "" -ForegroundColor Cyan
Write-Host '  ╔══════════════════════════════════════════════════╗' -ForegroundColor Cyan
Write-Host '  ║  ACHII SOVEREIGN ENGINE v4.2                    ║' -ForegroundColor Cyan
Write-Host '  ║  The Rusty Awakening                            ║' -ForegroundColor Cyan
Write-Host '  ╚══════════════════════════════════════════════════╝' -ForegroundColor Cyan
Write-Host ""

$py = Join-Path $Root ".venv\Scripts\python.exe"
if (-not (Test-Path $py)) {
    $py = "python"
    Write-Host '  [!] .venv ei loydy - kaytetaan jarjestelman Pythonia' -ForegroundColor Yellow
}

# 1. KAYNNISTETAAN A2A SERVER
Write-Host '  [1/4] Kaynnistetaan A2A Server...' -ForegroundColor Green
Start-Process -FilePath $py -ArgumentList "server.py" -WorkingDirectory $Root -WindowStyle Minimized

# 2. KAYNNISTETAAN WATCHER
Write-Host '  [2/4] Kaynnistetaan Watcher...' -ForegroundColor Green
Start-Process -FilePath $py -ArgumentList "watcher.py" -WorkingDirectory $Root -WindowStyle Minimized

# 3. KAYNNISTETAAN ACHII CORE
Write-Host '  [3/4] Kaynnistetaan Achii Core...' -ForegroundColor Green
Start-Process -FilePath $py -ArgumentList "achii_project/achii_core.py" -WorkingDirectory $Root -WindowStyle Minimized

Start-Sleep -Seconds 2

# 4. KAYNNISTETAAN DESKTOP
Write-Host '  [4/4] Kaynnistetaan Achii Desktop...' -ForegroundColor Green
$desktopPath = Join-Path $Root "desktop"
Start-Process -FilePath "cmd.exe" -ArgumentList "/k npm run dev" -WorkingDirectory $desktopPath -WindowStyle Normal

Start-Sleep -Seconds 2

# 5. AVATAR REPL
Write-Host ""
Write-Host '  ════════════════════════════════════════════════════' -ForegroundColor DarkGray
Write-Host '  Kaikki jarjestelmat kaynnissa:' -ForegroundColor Green
Write-Host '    A2A Server      http://127.0.0.1:8080' -ForegroundColor Gray
Write-Host '    Achii Core      ws://127.0.0.1:8081/ws/achii' -ForegroundColor Gray
Write-Host '    Desktop UI      http://127.0.0.1:5173' -ForegroundColor Gray
Write-Host '  ════════════════════════════════════════════════════' -ForegroundColor DarkGray
Write-Host ""

# Sovereign REPL suoraan terminaaliin
& $py cli.py
