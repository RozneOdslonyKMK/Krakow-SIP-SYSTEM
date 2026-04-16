@echo off
setlocal enabledelayedexpansion

set "APP_DIR=%~dp0"

if "%APP_DIR:~-1%"=="\" set "APP_DIR=%APP_DIR:~0,-1%"

set "RUN_DIR=%APP_DIR%\windows"
set "LOG_DIR=%APP_DIR%\logs"
set "LATEST_LOG=%LOG_DIR%\latest.log"

cd /d "%APP_DIR%"

if not exist "%LOG_DIR%" mkdir "%LOG_DIR%"

for /f "tokens=2 delims==" %%I in ('wmic os get localdatetime /format:list') do set "datetime=%%I"
set "STAMP=%datetime:~0,4%-%datetime:~4,2%-%datetime:~6,2%_%datetime:~8,2%-%datetime:~10,2%-%datetime:~12,2%"

if exist "%LATEST_LOG%" (
    move /y "%LATEST_LOG%" "%LOG_DIR%\latest-%STAMP%.log" >nul
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

if exist "%RUN_DIR%\update_sip.bat" (
    pushd "%RUN_DIR%"
    call update_sip.bat >> "%LATEST_LOG%" 2>&1
    popd
)

python %APP_DIR%\system-universal.py >> "%LATEST_LOG%" 2>&1

echo --- ZAMKNIĘCIE SYSTEMU: %date% %time% --- >> "%LATEST_LOG%"
pause
