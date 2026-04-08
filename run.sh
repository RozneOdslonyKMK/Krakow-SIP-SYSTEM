#!/bin/bash
# Czekamy 5 sekund na sieć (opcjonalne, ale zalecane w autobusie/laptopie)
sleep 5

# Przechodzimy do folderu apki
cd /opt/krakow_sip_system

# Aktualizujemy i odpalamy
./update_sip.sh && python3 system.py
