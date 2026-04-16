@echo off
setlocal enabledelayedexpansion

set "WIN_DIR=%~dp0"
if "%WIN_DIR:~-1%"=="\" set "WIN_DIR=%WIN_DIR:~0,-1%"

for %%I in ("%WIN_DIR%") do set "ROOT_DIR=%%~dpI"
if "%ROOT_DIR:~-1%"=="\" set "ROOT_DIR=%ROOT_DIR:~0,-1%"

set "LOG_DIR=%ROOT_DIR%\logs"
set "LATEST_LOG=%LOG_DIR%\latest.log"

cd /d "%ROOT_DIR%"

if not exist "%LOG_DIR%" mkdir "%LOG_DIR%"

for /f "tokens=*" %%i in ('powershell -NoProfile -Command "Get-Date -Format 'yyyy-MM-dd_HH-mm-ss'"') do set "STAMP=%%i"

if exist "%LATEST_LOG%" (
    move /y "%LATEST_LOG%" "%LOG_DIR%\latest-%STAMP%.log" >nul 2>&1
)

echo --- START SYSTEMU: %date% %time% --- > "%LATEST_LOG%"
echo --- Sprawdzanie bibliotek Python --- >> "%LATEST_LOG%"

set "LIBS=kivy ffpyplayer"

for %%i in (%LIBS%) do (
    python -c "import %%i" 2>nul
    if errorlevel 1 (
        echo [%time%] Brak biblioteki %%i. Instalacja...
        echo [%time%] Brak biblioteki %%i. Instalacja... >> "%LATEST_LOG%"
        python -m pip install %%i >> "%LATEST_LOG%" 2>&1
    ) else (
        echo [%time%] Biblioteka %%i jest juz zainstalowana. >> "%LATEST_LOG%"
    )
)

echo --- Uruchamianie SIP --- >> "%LATEST_LOG%"

if exist "%WIN_DIR%\update_sip.bat" (
    pushd "%WIN_DIR%"
    call "update_sip.bat" >> "%LATEST_LOG%" 2>&1
    popd
)

python "system-universal.py" >> "%LATEST_LOG%" 2>&1

echo --- ZAMKNIĘCIE SYSTEMU: %date% %time% --- >> "%LATEST_LOG%"
pause