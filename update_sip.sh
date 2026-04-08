#!/bin/bash
cd /opt/krakow_sip_system
# Pobierz najnowsze info z serwera
git fetch --all
# Wymuś nadpisanie lokalnych plików wersją z głównej gałęzi (zazwyczaj main lub master)
git reset --hard origin/main
