import os
import csv
import math
import sys
from datetime import datetime

os.environ['KIVY_NO_ARGS'] = '1'

if sys.platform != "win32":
    os.environ['KIVY_WINDOW'] = 'sdl2'
    os.environ['KIVY_GL_BACKEND'] = 'gl'
else:
    os.environ['KIVY_GL_BACKEND'] = 'angle_sdl2'
    os.environ['KIVY_VIDEO'] = 'ffpyplayer'
    print("INFO: Skonfigurowano backend ANGLE dla systemu Windows")

from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen, FadeTransition
from kivy.uix.stencilview import StencilView
from kivy.uix.scrollview import ScrollView
from kivy.uix.modalview import ModalView
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.video import Video
from kivy.uix.image import Image
from kivy.uix.textinput import TextInput
from kivy.core.window import Window
from kivy.core.audio import SoundLoader
from kivy.clock import Clock
from kivy.config import Config

GPS_AVAILABLE = False
try:
    from gps import *
    GPS_AVAILABLE = True
except ImportError:
    print("Biblioteka GPS nie znaleziona. Tryb automatyczny (Pojazd) będzie nieaktywny.")

Config.set('kivy', 'keyboard_mode', 'systemanddock')
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
Window.fullscreen = 'auto'
Window.show_cursor = False 

now = datetime.now()
formatted_news = f"******* Jakość powietrza: DOBRA. Godzina pomiaru: {now.strftime('%H')}:00 {now.strftime('%d-%m-%Y')}. *******"

OPERATORS = {
    "MPK Kraków": ["Tramwaj", "Autobus"],
    "Mobilis": ["Autobus"],
    "KLM": ["Tramwaj", "Autobus"]
}

SPECIAL_MODES = {
    "TRAM_WYJAZD": {"line": "", "label": "Wyjazd na linię", "stops": True},
    "TRAM_ZJAZD": {"line": "", "label": "Zajezdnia", "stops": True},
    "BUS_WYJAZD": {"line": "", "label": "Wyjazd na linię", "stops": False},
    "BUS_ZJAZD": {"line": "", "label": "Zjazd do zajezdni", "stops": False},
    "PRZEJAZD_TECH": {"line": "", "label": "Przejazd Techniczny", "stops": False},
    "NAUKA_JAZDY": {"line": "", "label": "Nauka Jazdy", "stops": False},
    "JAZDA_TEST": {"line": "TEST", "label": "Jazda Testowa", "stops": False},
    "JAZDA_PROBNA": {"line": "", "label": "Jazda Próbna", "stops": False},
    "MPK_KRAKOW": {"line": "", "label": "MPK S.A. w Krakowie", "stops": False},
    "MOBILIS": {"line": "", "label": "MOBILIS KRAKÓW", "stops": False}
}

VOICE_TYPES = {
    "Stare": "audio",
    "Nowe": "audio/new",
    "Makłowicz": "audio/maklowicz"
}

SEARCH_ORDER = {
    "audio/maklowicz": ["audio/maklowicz", "audio/new", "audio"],
    "audio/new": ["audio/new", "audio", "audio/maklowicz"],
    "audio": ["audio", "audio/new", "audio/maklowicz"]
}

SESSION = {
    "mode": "Dom",
    "operator": "",
    "type": "",
    "voice_path": "audio",
    "news_text": formatted_news,
    "is_route_changed": False,
    "selected_csv_path": "",
    "special_mode_id": None
}
