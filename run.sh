#!/bin/bash
sleep 10
cd /opt/krakow_sip_system || exit
/usr/bin/chmod +x ./update_sip.sh
/usr/bin/bash ./update_sip.sh && /usr/bin/python3 system.py
