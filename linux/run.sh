#!/bin/bash

APP_DIR="/opt/krakow_sip_system"
RUN_DIR="$APP_DIR/linux"
LOG_DIR="$APP_DIR/logs"
LATEST_LOG="$LOG_DIR/latest.log"

sleep 10
cd "$APP_DIR" || exit

mkdir -p "$LOG_DIR"

if [ -f "$LATEST_LOG" ]; then
    TIMESTAMP=$(date +"%Y-%m-%d_%H-%M-%S")
    mv "$LATEST_LOG" "$LOG_DIR/latest-$TIMESTAMP.log"
fi

exec > >(tee -a "$LATEST_LOG") 2>&1

echo "--- START SYSTEMU: $(date +"%Y-%m-%d %H:%M:%S") ---"

SYSTEM_DEPS="python3-pip python3-setuptools libsdl2-dev libsdl2-image-dev libsdl2-mixer-dev libsdl2-ttf-dev"
PYTHON_DEPS="kivy ffpyplayer"

echo "--- Sprawdzanie zależności systemowych ---"
for pkg in $SYSTEM_DEPS; do
    if ! dpkg -s "$pkg" >/dev/null 2>&1; then
        echo "[$(date +%T)] Brak pakietu: $pkg. Instalacja..."
        sudo apt-get update && sudo apt-get install -y "$pkg"
    fi
done

echo "--- Sprawdzanie bibliotek Python ---"
for lib in $PYTHON_DEPS; do
    if ! python3 -c "import $lib" >/dev/null 2>&1; then
        echo "[$(date +%T)] Brak biblioteki Python: $lib. Instalacja..."
        python3 -m pip install "$lib"
    fi
done

if ! python3 -c "import gps" >/dev/null 2>&1; then
    echo "[$(date +%T)] Instalacja biblioteki GPS..."
    sudo apt-get install -y python3-gps
fi

echo "--- Zależności sprawdzone. Uruchamianie SIP ---"

/usr/bin/chmod +x $RUN_DIR/update_sip.sh
/usr/bin/bash $RUN_DIR/update_sip.sh
/usr/bin/python3 $APP_DIR/system-universal.py sip
/usr/bin/python3 $APP_DIR/system-universal.py driver

echo "--- ZAMKNIĘCIE SYSTEMU: $(date +"%Y-%m-%d %H:%M:%S") ---"
