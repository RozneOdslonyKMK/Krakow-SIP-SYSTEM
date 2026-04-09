@echo off
setlocal enabledelayedexpansion

set "APP_DIR=%~dp0"
set "LOG_DIR=%APP_DIR%logs"
set "LATEST_LOG=%LOG_DIR%\latest.log"

cd /d "%APP_DIR%"

if not exist "%LOG_DIR%" mkdir "%LOG_DIR%"

if exist "%LATEST_LOG%" (
    for /f "tokens=2-4 delims=/ " %%a in ('date /t') do (set mydate=%%c-%%a-%%b)
    for /f "tokens=1-3 delims=/: " %%a in ('time /t') do (set mytime=%%a-%%b-%%c)
    set "STAMP=%date:~0,4%-%date:~5,2%-%date:~8,2%_%time:~0,2%-%time:~3,2%-%time:~6,2%"
    set "STAMP=!STAMP: =0!"
    move "%LATEST_LOG%" "%LOG_DIR%\latest-!STAMP!.log" >nul
)

echo --- START SYSTEMU: %date% %time% --- > "%LATEST_LOG%"

echo --- Sprawdzanie bibliotek Python --- >> "%LATEST_LOG%"

set "LIBS=kivy ffpyplayer"

for %%i in (%LIBS%) do (
    python -c "import %%i" 2>nul
    if errorlevel 1 (
        echo [%time%] Brak biblioteki %%i. Instalacja... | tee -a "%LATEST_LOG%"
        python -m pip install %%i >> "%LATEST_LOG%" 2>&1
    ) else (
        echo [%time%] Biblioteka %%i jest juz zainstalowana. >> "%LATEST_LOG%"
    )
)

echo --- Uruchamianie SIP --- >> "%LATEST_LOG%"

if exist "update_sip.bat" call update_sip.bat >> "%LATEST_LOG%" 2>&1

python system-win.py >> "%LATEST_LOG%" 2>&1

echo --- ZAMKNIĘCIE SYSTEMU: %date% %time% --- >> "%LATEST_LOG%"
pause
