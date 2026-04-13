#Requires -Version 5.1
# build_release.ps1 - Automatisoi Sovereign Engine v4.0 binäärijakelun (Windows)

$ErrorActionPreference = "Stop"
$Root = $PSScriptRoot
Set-Location -LiteralPath $Root

Write-Host "===============================================" -ForegroundColor Cyan
Write-Host " Sovereign Engine v4.0 - Työpöytäsovelluksen Build" -ForegroundColor Cyan
Write-Host "===============================================" -ForegroundColor Cyan

# Varmistetaan että Tauri on saatavilla ja riippuvuudet asennettu
Set-Location -LiteralPath "$Root\desktop"
Write-Host "-> Asennetaan Node.js riippuvuudet (desktop/)..." -ForegroundColor Yellow
npm install

Write-Host "-> Rakennetaan Tauri -sovellus (voi kestää 5-10 min)..." -ForegroundColor Yellow
# Suoritetaan Tauri build. (Se pakkaa "target/release" kansioon Exet sekä nsis asennusohjelmat)
npm run tauri build

# Määritellään Output kansio agentdir-juureen
$BuildOut = "$Root\Release\SovereignEngine-v4.0.0-windows"
if (Test-Path $BuildOut) { Remove-Item -Recurse -Force $BuildOut }
New-Item -ItemType Directory -Path $BuildOut | Out-Null

Set-Location -LiteralPath $Root

Write-Host "-> Kopioidaan asennusohjelma ja backend..." -ForegroundColor Yellow

# Kopioi Tauri-asennusohjelma (NSIS) Release-kansioon
$TauriInstaller = "$Root\desktop\src-tauri\target\release\bundle\nsis\Sovereign Engine_4.0.0_x64-setup.exe"
if (Test-Path $TauriInstaller) {
    Copy-Item -Path $TauriInstaller -Destination "$BuildOut\"
    Write-Host "Tauri Installer kopioitu!" -ForegroundColor Green
} else {
    Write-Host "Varoitus: Tauri installeria ei löytynyt. Varmista ettei build kaatunut." -ForegroundColor Red
}

# Kopioi backend pika-asennusta varten 
# (Tämä vaatii että loppukäyttäjällä on asennettuna Python, kuten README:ssa lukee)
Write-Host "-> Kerätään Python backend..." -ForegroundColor Yellow
$BackendDir = "$BuildOut\backend"
New-Item -ItemType Directory -Path $BackendDir | Out-Null

$FilesToCopy = @("*.py", "config.json", "manifest.json", "requirements.txt", "launch_sovereign.ps1", "install.ps1")
$DirsToCopy = @("docs", "web", "workspace", "sandbox", "workflows", "templates", "plugins", ".prompts")

foreach ($file in $FilesToCopy) {
    Get-ChildItem -Path $Root -Filter $file | Copy-Item -Destination $BackendDir
}

foreach ($dir in $DirsToCopy) {
    if (Test-Path "$Root\$dir") {
        Copy-Item -Path "$Root\$dir" -Destination "$BackendDir\$dir" -Recurse
    }
}

# Pakkaa koko hoito ZIP:ksi (Compression Level Optimal)
Write-Host "-> Luodaan ZIP arkisto (SovereignEngine-v4.0.0-windows.zip)..." -ForegroundColor Yellow
Compress-Archive -Path "$BuildOut\*" -DestinationPath "$Root\Release\SovereignEngine-v4.0.0-windows.zip" -Force

Write-Host "===============================================" -ForegroundColor Cyan
Write-Host " BUILD VALMIS!" -ForegroundColor Green
Write-Host " Jakelupaketti: Release\SovereignEngine-v4.0.0-windows.zip"
Write-Host " Asennusohjelma löytyy paketin sisältä."
