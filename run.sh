#!/bin/bash
# Czekamy 5 sekund na sieć (opcjonalne, ale zalecane w autobusie/laptopie)
sleep 5

# Przechodzimy do folderu apki
cd /opt/krakow_sip_system

chmod +x /opt/krakow_sip_system/update_sip.sh

# Aktualizujemy i odpalamy
./update_sip.sh && python3 system.py
