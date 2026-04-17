# Krakow-SIP-SYSTEM
## O projekcie
Projekt wpadł do głowy jako pomysł przy tworzeniu aplikacji 🔗<a href="https://sklep.rokmk.pl/produkt/kod-aktywacyjny-programu-buscrafter">BusCrafter</a> i dodawaniu do niej coraz więcej opcji. W pierwotnym planie było dodać ekran podsufitowy jako obrazek lub plik PDF z obrazkiem tworzony na podstawie wpisanych danych do programu. Jednak, żeby zaoszczędzić sobie czasu i roboty, postanowiłem zrobić mały programik do uruchamiania na komputerach z systemami Linux. Początkowo miał być tylko Linux, ale po namysłach stwierdziłem, że dodam też support na systemy Windows.

W programie na początku odpala się coś w stylu sterownika typu Trapeze, który ma kierowca/motorniczy w swojej kabinie. Po ustawieniu linii i trasy można włączyć monitor podsufitowy z trasą, który zapowiada komunikaty dźwiękowe kolejnych przystanków.

# Linux
## Przed pierwszym uruchomieniem
Aby pobrać program wpisz to polecenie w terminalu:
```
sudo git clone https://github.com/RozneOdslonyKMK/Krakow-SIP-SYSTEM/ /opt/krakow_sip_system
cd /opt/krakow_sip_system/linux
chmod +x ./run.sh
```

## Uruchamianie
Wpisz w terminalu to polecenie:
```
cd /opt/krakow_sip_system/linux
chmod +x ./run.sh
./run.sh
```

## Autostart
Dodaj nowe polecenie autostartu o nazwie np. SIP. W oknie ustawień autostartu w polu polecenia wpisz:
```
bash /opt/krakow_sip_system/linux/run.sh
```

## Generator tras
Jeśli jesteś zainteresowany stworzeniem własnej trasy, której nie ma w plikach, uruchom w terminalu poniższe polecenie:
```
cd /opt/krakow_sip_system/linux
chmod +x ./run_generator.sh
./run_generator.sh
```
Pamiętaj, żeby zapisać wygenerowaną trasę jako kopię w innym folderze niż katalog programu `/opt/krakow_sip_system/`, ponieważ przy aktualizacji system nadpisze wszystkie pliki synchronizując dane z GitHubem (np. w `/home/twoja-nazwa/Desktop/trasy sip`).

# Windows
## Przed pierwszym uruchomieniem
Zainstaluj program 🔗<a href="https://git-scm.com/install/windows">Git</a> oraz 🔗<a href="https://www.python.org/downloads/windows/">Python 3.8</a>. Podczas instalacji programu Git należy zaznaczyć opcję "Git from the command line and also from 3rd-party software", aby komenda była widoczna w CMD, natomiast przy instalacji Pythona należy **koniecznie** zaznaczyć "Add Python to PATH". Po zainstalowaniu wymaganych programów uruchom w CMD to polecenie:
```
git clone https://github.com/RozneOdslonyKMK/Krakow-SIP-SYSTEM.git "C:\Users\Twoja-nazwa\krakow_sip_system"
```
Zamień "Twoja-nazwa" na rzeczywistą nazwę użytkownika Windows, która jest w plikach

## Uruchamianie
Możesz otworzyć plik run.bat dwukrotnie klikając plik w folderze, albo poprzez CMD uruchamiając poniższe polecenie:
```
cd "C:\Users\Twoja-nazwa\krakow_sip_system\windows"
.\run.bat
```
Zamień "Twoja-nazwa" na rzeczywistą nazwę użytkownika Windows, która jest w plikach

## Generator tras
Jeśli jesteś zainteresowany stworzeniem własnej trasy, której nie ma w plikach, otwórz plik run_generator.bat dwukrotnie klikając, albo poprzez CMD uruchamiając poniższe polecenie:
```
cd "C:\Users\Twoja-nazwa\krakow_sip_system\windows"
.\run_generator.bat
```
Zamień "Twoja-nazwa" na rzeczywistą nazwę użytkownika Windows, która jest w plikach oraz pamiętaj, żeby zapisać wygenerowaną trasę jako kopię w innym folderze niż katalog programu `C:\Users\Twoja-nazwa\krakow_sip_system\windows`, ponieważ przy aktualizacji system nadpisze wszystkie pliki synchronizując dane z GitHubem (np. w `C:\Users\Twoja-nazwa\Desktop\trasy sip`).

<br>
<br>
