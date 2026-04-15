@echo off
cd /d "%~dp0"
echo [UPDATE] Sprawdzanie aktualizacji w repozytorium git...
git config --global --add safe.directory "%cd:\=/%"
git fetch --all
git reset --hard origin/main
echo [UPDATE] Gotowe.
