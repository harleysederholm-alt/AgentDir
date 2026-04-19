@echo off
color 0E
title Achii Sovereign Engine v4.2 - The Rusty Awakening

echo ========================================================
echo   ACHII SOVEREIGN ENGINE v4.2 - ONE-CLICK BOOTSTRAP
echo   "Zero-Cloud Egress - Maximum Local Compute"
echo ========================================================
echo.

:: Vaihda skriptin suorituskansioon (varmistetaan polku)
cd /d "%~dp0"

echo [SYSTEM] Tarkistetaan riippuvuuksia...

:: Tarkista Python
python --version >nul 2>&1
IF %ERRORLEVEL% NEQ 0 (
    echo [VIRHE] Python ei ole asennettu tai sita ei loydy PATH-muuttujasta! 
    echo Lataa Python osoitteesta https://www.python.org/downloads/
    pause
    exit /b
)

:: Tarkista Node.js
npm -v >nul 2>&1
IF %ERRORLEVEL% NEQ 0 (
    echo [VIRHE] Node.js ei ole asennettu tai sita ei loydy PATH-muuttujasta! 
    echo Lataa Node osoitteesta https://nodejs.org/
    pause
    exit /b
)

:: Tarkistetaan .venv
IF NOT EXIST ".venv" (
    echo [SYSTEM] Luodaan eristetty Python Virtual Environment (.venv)...
    python -m venv .venv
    echo [SYSTEM] Asennetaan Python-riippuvuudet...
    call .venv\Scripts\activate.bat
    pip install -r requirements.txt
) ELSE (
    echo [SYSTEM] Python .venv loytyy jo.
)

:: Tarkistetaan Desktop-riippuvuudet
IF NOT EXIST "desktop\node_modules" (
    echo [SYSTEM] Asennetaan Desktop UI -riippuvuudet (Node.js)...
    cd desktop
    call npm install
    cd ..
) ELSE (
    echo [SYSTEM] Desktop node_modules loytyy jo.
)

echo.
echo [SYSTEM] Kaikki komponentit asennettu. Sytytetaan Achii OmniNode Swarm...
echo [SYSTEM] Ala sulje tata ikkunaa. Se hallinnoi taustaprosesseja.
echo.

:: Kaynnistetaan powershell-skripti
powershell -ExecutionPolicy Bypass -File launch_sovereign.ps1
