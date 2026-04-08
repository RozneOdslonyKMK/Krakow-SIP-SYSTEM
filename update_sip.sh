#!/bin/bash
cd /opt/krakow_sip_system
git config --global --add safe.directory /opt/krakow_sip_system
git fetch --all
git reset --hard origin/main
