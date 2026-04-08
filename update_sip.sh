#!/bin/bash
cd /opt/krakow_sip_system

# Dodaj to, aby Git nie marudził o uprawnienia:
git config --global --add safe.directory /opt/krakow_sip_system

# Reszta bez zmian
git fetch --all
git reset --hard origin/main
