# Krakow-SIP-SYSTEM

# Linux
## Przed pierwszym uruchomieniem
```
sudo git clone https://github.com/RozneOdslonyKMK/Krakow-SIP-SYSTEM/ /opt/krakow_sip_system
```

## Uruchamianie
```
/opt/krakow_sip_system/run.sh
```

## Autostart
Dodaj nowe polecenie autostartu o nazwie np. SIP. W oknie ustawień autostartu w polu polecenia wpisz:
```
bash /opt/krakow_sip_system/run.sh
```

# Windows
## Najpierw zainstaluj niezbędne do uruchomienia programu zależności
```
pip install kivy[base] kivy_examples
pip install ffpyplayer
```
