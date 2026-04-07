import os
import csv
import math
from datetime import datetime

# Środowisko i sterowniki
os.environ['KIVY_NO_ARGS'] = '1'
os.environ['KIVY_WINDOW'] = 'sdl2'
os.environ['KIVY_GL_BACKEND'] = 'gl'

from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen, FadeTransition
from kivy.uix.stencilview import StencilView
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
from gps import *

Config.set('kivy', 'keyboard_mode', 'systemanddock')
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
Window.fullscreen = 'auto'
Window.show_cursor = False 

OPERATORS = {
    "MPK Kraków": ["Tramwaj", "Autobus"],
    "Mobilis": ["Autobus"],
    "KLM": ["Tramwaj", "Autobus"]
}

SESSION = {
    "mode": "Dom",
    "operator": "",
    "type": "",
    "news_text": "Miłej podróży!",
    "is_route_changed": False,
    "selected_csv_path": ""
}

# --- EKRANY KONFIGURACJI ---

class StartModeScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        layout = BoxLayout(orientation='vertical', padding=100, spacing=40)
        layout.add_widget(Label(text="WYBIERZ TRYB PRACY", font_size='50sp', bold=True))
        
        btn_dom = Button(text="DOM\n(Ręczne klikanie)", halign='center', font_size='30sp', background_color=(0, 0.5, 0, 1))
        btn_poj = Button(text="POJAZD\n(Automatyczny GPS)", halign='center', font_size='30sp', background_color=(0.7, 0, 0, 1))
        
        btn_dom.bind(on_release=lambda x: self.set_mode("Dom"))
        btn_poj.bind(on_release=lambda x: self.set_mode("Pojazd"))
        
        layout.add_widget(btn_dom)
        layout.add_widget(btn_poj)
        self.add_widget(layout)

    def set_mode(self, mode):
        SESSION["mode"] = mode
        self.manager.current = 'operator_select'

class OperatorSelectScreen(Screen):
    def on_enter(self):
        self.clear_widgets()
        layout = BoxLayout(orientation='vertical', padding=50, spacing=20)
        layout.add_widget(Label(text="WYBIERZ OPERATORA", font_size='40sp', size_hint_y=0.2))
        
        grid = GridLayout(cols=2, spacing=20)
        for op in OPERATORS.keys():
            btn = Button(text=op, font_size='25sp', background_color=(0, 0.23, 0.45, 1))
            btn.bind(on_release=lambda x, o=op: self.select_operator(o))
            grid.add_widget(btn)
        layout.add_widget(grid)

        back = Button(text="POWRÓT", size_hint_y=0.2, background_color=(0.5, 0.5, 0.5, 1))
        back.bind(on_release=lambda x: setattr(self.manager, 'current', 'start_mode'))
        layout.add_widget(back)
        self.add_widget(layout)

    def select_operator(self, op):
        SESSION["operator"] = op
        self.manager.get_screen('type_select').update_types(op)
        self.manager.current = 'type_select'

class TypeSelectScreen(Screen):
    def update_types(self, op):
        self.clear_widgets()
        layout = BoxLayout(orientation='vertical', padding=50, spacing=20)
        layout.add_widget(Label(text=f"{op} - RODZAJ POJAZDU", font_size='35sp', size_hint_y=0.2))
        
        for t in OPERATORS[op]:
            btn = Button(text=t, font_size='30sp', background_color=(0, 0.23, 0.45, 1))
            btn.bind(on_release=lambda x, typ=t: self.select_type(typ))
            layout.add_widget(btn)

        back = Button(text="POWRÓT", size_hint_y=0.2, background_color=(0.5, 0.5, 0.5, 1))
        back.bind(on_release=lambda x: setattr(self.manager, 'current', 'operator_select'))
        layout.add_widget(back)
        self.add_widget(layout)

    def select_type(self, typ):
        SESSION["type"] = typ.lower()
        self.manager.get_screen('lines').load_lines()
        self.manager.current = 'lines'

class LineSelectScreen(Screen):
    def load_lines(self):
        self.clear_widgets()
        layout = BoxLayout(orientation='vertical', padding=20, spacing=10)
        grid = GridLayout(cols=6, spacing=10)
        
        op_dir = SESSION["operator"].split()[0].lower()
        self.base_path = os.path.join(BASE_DIR, 'routes', op_dir, SESSION["type"])
        
        if os.path.exists(self.base_path):
            # Skanujemy FOLDERY jako linie
            lines = [d for d in os.listdir(self.base_path) if os.path.isdir(os.path.join(self.base_path, d))]
            lines.sort(key=lambda x: (len(x), x))
            for line in lines:
                btn = Button(text=line, font_size='30sp', bold=True, background_color=(0, 0.23, 0.45, 1))
                btn.bind(on_release=lambda x, l=line: self.select_line(l))
                grid.add_widget(btn)
        
        layout.add_widget(Label(text="WYBIERZ NUMER LINII", size_hint_y=0.1))
        layout.add_widget(grid)
        
        back = Button(text="POWRÓT", size_hint_y=0.15, background_color=(0.5, 0.5, 0.5, 1))
        back.bind(on_release=lambda x: setattr(self.manager, 'current', 'type_select'))
        layout.add_widget(back)
        self.add_widget(layout)

    def select_line(self, line_no):
        line_path = os.path.join(self.base_path, line_no)
        files = [f for f in os.listdir(line_path) if f.endswith('.csv')]
        self.manager.get_screen('routes').update_routes(line_no, files, line_path)
        self.manager.current = 'routes'

class RouteSelectScreen(Screen):
    def update_routes(self, line_no, files, line_path):
        self.clear_widgets()
        self.line_path = line_path
        layout = BoxLayout(orientation='vertical', padding=20, spacing=10)
        layout.add_widget(Label(text=f"LINIA {line_no} - WYBIERZ TRASĘ", font_size='30sp', size_hint_y=0.1))
        
        grid = GridLayout(cols=1, spacing=10)
        for f in files:
            name = f.replace('.csv', '').replace('_', ' ')
            btn = Button(text=name, font_size='22sp', background_color=(0, 0.4, 0.8, 1))
            btn.bind(on_release=lambda x, f_name=f: self.set_route(f_name))
            grid.add_widget(btn)
        
        layout.add_widget(grid)
        
        opt_box = BoxLayout(size_hint_y=0.2, spacing=10)
        self.change_btn = Button(text="ZMIANA TRASY: OFF")
        self.change_btn.bind(on_release=self.toggle_change)
        opt_box.add_widget(self.change_btn)
        
        back = Button(text="POWRÓT", background_color=(0.5, 0.5, 0.5, 1))
        back.bind(on_release=lambda x: setattr(self.manager, 'current', 'lines'))
        opt_box.add_widget(back)
        
        layout.add_widget(opt_box)
        self.add_widget(layout)

    def toggle_change(self, btn):
        SESSION["is_route_changed"] = not SESSION["is_route_changed"]
        btn.text = f"ZMIANA TRASY: {'ON' if SESSION['is_route_changed'] else 'OFF'}"

    def set_route(self, file_name):
        SESSION["selected_csv_path"] = os.path.join(self.line_path, file_name)
        self.manager.current = 'news_editor'

class NewsEditorScreen(Screen):
    def on_enter(self):
        self.clear_widgets()
        layout = BoxLayout(orientation='vertical', padding=50, spacing=20)
        layout.add_widget(Label(text="WPISZ TEKST NEWSÓW", font_size='30sp'))
        self.ti = TextInput(text=SESSION["news_text"], font_size='30sp', multiline=False)
        layout.add_widget(self.ti)
        
        btn_go = Button(text="URUCHOM SIP", background_color=(0, 0.6, 0, 1))
        btn_go.bind(on_release=self.start)
        layout.add_widget(btn_go)
        
        back = Button(text="POWRÓT", background_color=(0.5, 0.5, 0.5, 1))
        back.bind(on_release=lambda x: setattr(self.manager, 'current', 'routes'))
        layout.add_widget(back)
        self.add_widget(layout)

    def start(self, *args): # usunięto csv_file z argumentów
        SESSION["news_text"] = self.ti.text
        # Przekazujemy samą nazwę pliku (bez ścieżki) do setup_sip
        csv_name = os.path.basename(SESSION["selected_csv_path"])
        self.manager.get_screen('sip').setup_sip(csv_name)
        self.manager.current = 'sip'

# --- MONITOR PODSUFITOWY ---

class MainSIPLayout(FloatLayout):
    def __init__(self, csv_file, **kwargs):
        super().__init__(**kwargs)
        self.ubuntu_font = os.path.join(BASE_DIR, 'Ubuntu-Regular.ttf')
        self.arial_font = os.path.join(BASE_DIR, 'Arial.ttf')
        self.krakow_blue = (0, 0.23, 0.45, 1)
        self.screen_h = 1080
        
        self.stops = []
        self.stops_db = {}
        self.current_idx = 0
        self.is_at_stop = True # Flaga stanu
        
        self.load_stops_db()
        self.load_route()

        ads_dir = os.path.join(BASE_DIR, 'ads')
        self.ad_files = [os.path.join(ads_dir, f) for f in os.listdir(ads_dir) if f.endswith(('.mp4', '.mkv', '.avi'))]
        self.ad_files.sort()

        self.current_ad_idx = 0 
        self._loading_ad = False
        self.ads = None
        
        # Tło
        bg = 'podklad_zmiana.png' if SESSION["is_route_changed"] else 'podklad.png'
        self.add_widget(Image(source=os.path.join(BASE_DIR, bg), allow_stretch=True, keep_ratio=False))

        if self.ad_files:
            Clock.schedule_once(self._rebuild_video_widget, 1.0)

        # Numer linii
        l_color = (1, 1, 1, 1) if SESSION["is_route_changed"] else self.krakow_blue
        # Pobieramy numer linii z nazwy folderu w ścieżce
        line_no = SESSION["selected_csv_path"].split('/')[-2] 
        self.add_widget(Label(text=line_no, font_size='165sp', font_name=self.ubuntu_font,
                              color=l_color, bold=True, size_hint=(None, None), size=(309, 184),
                              pos=(0, 1080-184), halign='center', valign='middle', text_size=(309, 184)))

        # Przystanek Obecny
        self.update_stop_label(self.stops[0]['Nazwa'])
        
        # --- PRZYSTANEK DOCELOWY (KIERUNEK) ---
        limit_dest_width = 1197
        dest_pos_x = 428
        dest_pos_y = self.screen_h - 184 # Pozycja pod nazwą obecnego przystanku

        self.dest_container = StencilView(size_hint=(None, None), size=(limit_dest_width, 92),
                                          pos=(dest_pos_x, dest_pos_y))
        
        if '_' in csv_file:
            direction = csv_file.split('_', 1)[1].replace('.csv', '').replace('_', ' ')
        else:
            direction = csv_file.replace('.csv', '')

        self.dest_label = Label(text=direction, font_size='65sp', font_name=self.ubuntu_font,
                                color=self.krakow_blue, size_hint=(None, None),
                                size=(limit_dest_width, 92), pos=(dest_pos_x, dest_pos_y),
                                halign='left', valign='middle', text_size=(None, 92))
        
        self.dest_label.texture_update()
        self.dest_label.width = self.dest_label.texture_size[0]
        self.should_scroll_dest = self.dest_label.width > limit_dest_width
        
        self.dest_container.add_widget(self.dest_label)
        self.add_widget(self.dest_container)

        # Newsy (Ticker)
        self.stencil = StencilView(size_hint=(None, None), size=(1726, 107), pos=(194, 1080-973-107))
        self.ticker = Label(text=SESSION["news_text"], font_name=self.arial_font, font_size='85sp',
                            size_hint=(None, 1), halign='left', valign='middle', height=107)
        self.ticker.x = 1920
        self.stencil.add_widget(self.ticker)
        self.add_widget(self.stencil)

        # Czas i data
        self.clock_label = Label(text="00:00", font_size='90sp', font_name=self.ubuntu_font,
                                 color=self.krakow_blue, bold=True,
                                 size_hint=(None, None), size=(250, 92),
                                 pos=(1670, self.screen_h - 92), halign='right', valign='middle',
                                 text_size=(240, 92))
        self.add_widget(self.clock_label)

        self.date_label = Label(text="poniedziałek\n1 stycznia", font_size='32sp', font_name=self.ubuntu_font,
                                color=self.krakow_blue, line_height=0.95,
                                size_hint=(None, None), size=(305, 92),
                                pos=(1615, self.screen_h - 92 - 92), halign='right', valign='middle',
                                text_size=(295, 92))
        self.add_widget(self.date_label)
        Clock.schedule_interval(self.update_ui, 1)
        Clock.schedule_interval(self.scroll_news, 0.02)
        
        if SESSION["mode"] == "Pojazd":
            try:
                self.gpsd = gps(mode=WATCH_ENABLE|WATCH_NEWSTYLE)
                Clock.schedule_interval(self.gps_loop, 1)
            except:
                print("Błąd GPSD")

    def update_stop_label(self, full_name):
        clean_name = full_name.rsplit(' ', 1)[0] if ' ' in full_name else full_name
        limit_width = 1316

        if not hasattr(self, 'stop_container'):
            # 1. Kontener na górze (pośrodku niebieskiego paska)
            self.stop_container = StencilView(size_hint=(None, None), size=(limit_width, 100),
                                            pos=(309, self.screen_h - 95))
            
            # 2. Label - WAŻNE: pos musi być taki sam jak kontenera, żeby trafił w "okno"
            self.lbl_stop = Label(text=clean_name, font_size='75sp', font_name=self.ubuntu_font,
                                  color=self.krakow_blue, bold=True, size_hint=(None, None),
                                  size=(limit_width, 100), pos=(309, self.screen_h - 95),
                                  halign='left', valign='middle', text_size=(None, 100))
            
            self.stop_container.add_widget(self.lbl_stop)
            self.add_widget(self.stop_container)
        else:
            self.lbl_stop.text = clean_name

        # Aktualizacja szerokości do przewijania
        self.lbl_stop.texture_update()
        self.lbl_stop.width = self.lbl_stop.texture_size[0]
        self.should_scroll_stop = self.lbl_stop.width > limit_width
        
        # Reset pozycji na start pola
        self.lbl_stop.x = 309
            
    def load_stops_db(self):
        db_p = os.path.join(BASE_DIR, 'stops.csv')
        if os.path.exists(db_p):
            with open(db_p, mode='r', encoding='utf-8') as f:
                reader = csv.DictReader(f, delimiter=';')
                for row in reader:
                    # Dopasowanie: "Wizjonerów 01" -> klucz "Wizjonerów"
                    base_name = row['Nazwa'].rsplit(' ', 1)[0]
                    self.stops_db[base_name] = {"lat": float(row['Lat']), "lon": float(row['Lon'])}

    def load_route(self):
        with open(SESSION["selected_csv_path"], mode='r', encoding='utf-8') as f:
            reader = csv.DictReader(f, delimiter=';')
            for row in reader: self.stops.append(row)

    def calculate_distance(self, lat1, lon1, lat2, lon2):
        phi1, phi2 = math.radians(lat1), math.radians(lat2)
        dphi = math.radians(lat2 - lat1)
        dlambda = math.radians(lon2 - lon1)
        a = math.sin(dphi/2)**2 + math.cos(phi1)*math.cos(phi2)*math.sin(dlambda/2)**2
        return 6371 * 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))

    def scroll_news(self, dt):
        # 1. NEWSY
        self.ticker.texture_update()
        self.ticker.width = self.ticker.texture_size[0]
        self.ticker.x -= 4
        if self.ticker.right < 0: self.ticker.x = 1726
        
        # 2. OBECNY PRZYSTANEK
        if hasattr(self, 'should_scroll_stop') and self.should_scroll_stop:
            self.lbl_stop.x -= 2
            if self.lbl_stop.right < 309: # 309 to lewa krawędź pola
                self.lbl_stop.x = 309 + 1316 # Wróć na prawą krawędź pola
        elif hasattr(self, 'lbl_stop'):
            self.lbl_stop.x = 309

        # 3. KIERUNEK
        if hasattr(self, 'should_scroll_dest') and self.should_scroll_dest:
            self.dest_label.x -= 2
            if self.dest_label.right < 428: # 428 to lewa krawędź pola
                self.dest_label.x = 428 + 1197
        elif hasattr(self, 'dest_label'):
            self.dest_label.x = 428

    def next_ad(self, *args):
        # Usuwamy blokadę ładowania, jeśli została z poprzedniej próby
        if hasattr(self, '_loading_ad') and self._loading_ad:
            # Jeśli minęło za dużo czasu, a nadal wisi blokada, zdejmij ją
            self._loading_ad = False 

        if not self.ad_files:
            return

        # 1. Całkowite niszczenie starego obiektu (kluczowe przy zapętleniu)
        if self.ads:
            try:
                self.ads.unbind(eos=self.next_ad)
                self.ads.state = 'stop'
                self.ads.unload()
                # Usuwamy z kontenera, jeśli go używamy
                if hasattr(self, 'video_container'):
                    self.remove_widget(self.video_container)
                else:
                    self.remove_widget(self.ads)
            except Exception as e:
                print(f"Błąd przy usuwaniu reklamy: {e}")
            
            self.ads = None

        # 2. Przeliczenie indeksu (powrót z ostatniej na pierwszą)
        self.current_ad_idx = (self.current_ad_idx + 1) % len(self.ad_files)
        
        # 3. Krótka przerwa, żeby podkład.png "oddetchnął"
        Clock.schedule_once(self._rebuild_video_widget, 0.5)

    def _rebuild_video_widget(self, dt):
        if not self.ad_files:
            return
        
        self._loading_ad = True # Blokujemy podwójne wywołania podczas ładowania

        # Tworzymy kontener (nożyczki)
        self.video_container = StencilView(
            size_hint=(None, None),
            size=(1402, 789),
            pos=(259, self.screen_h - 184 - 789)
        )

        # Tworzymy NOWY obiekt wideo
        self.ads = Video(
            source=self.ad_files[self.current_ad_idx],
            state='play',
            volume=0,
            allow_stretch=True,
            keep_ratio=False,
            size_hint=(None, None),
            size=(1402, 789),
            pos=(259, self.screen_h - 184 - 789)
        )
        
        # Ponowne bindowanie zdarzenia końca
        self.ads.bind(eos=self.next_ad)
        
        self.video_container.add_widget(self.ads)
        self.add_widget(self.video_container)
        
        # Na wszelki wypadek wymuszamy start za 0.2s
        Clock.schedule_once(self._force_play, 0.2)

    def _force_play(self, dt):
        if self.ads:
            self.ads.state = 'play'
        self._loading_ad = False

    def update_ui(self, *args):
        now = datetime.now()
        days_pl = ["poniedziałek", "wtorek", "środa", "czwartek", "piątek", "sobota", "niedziela"]
        months_pl = ["stycznia", "lutego", "marca", "kwietnia", "maja", "czerwca", "lipca", "sierpnia", "września", "października", "listopada", "grudnia"]
        self.clock_label.text = now.strftime("%H:%M")
        self.date_label.text = f"{days_pl[now.weekday()]}\n{now.day} {months_pl[now.month-1]}"
        
    def on_touch_down(self, touch):
        if SESSION["mode"] == "Dom":
            if self.is_at_stop:
                # --- AKCJA: ODJAZD Z PRZYSTANKU ---
                if self.current_idx < len(self.stops) - 1:
                    self.is_at_stop = False
                    next_stop_data = self.stops[self.current_idx + 1]
                    
                    # Co zrobić, gdy skończy mówić "Następny przystanek: Nazwa"?
                    def po_skonczeniu_audio():
                        self.update_stop_label(next_stop_data['Nazwa'])
                    
                    # Budujemy listę plików do odtworzenia
                    sekwencja = ["Następny Przystanek.mp3", f"{next_stop_data['Audio']}.mp3"]
                    self.play_sequence(sekwencja, callback=po_skonczeniu_audio)
            else:
                # --- AKCJA: WJAZD NA NASTĘPNY PRZYSTANEK ---
                self.current_idx += 1
                self.is_at_stop = True
                current_stop = self.stops[self.current_idx]
                
                # Tylko zapowiedź nazwy (napis zmienił się już przy odjeździe)
                self.play_sequence([f"{current_stop['Audio']}.mp3"])
        return True

    def gps_loop(self, dt):
        report = self.gpsd.next()
        if report['class'] == 'TPV':
            my_lat = getattr(report, 'lat', 0.0)
            my_lon = getattr(report, 'lon', 0.0)
            if my_lat != 0.0:
                self.process_gps_logic(my_lat, my_lon)

    def process_gps_logic(self, my_lat, my_lon):
        target_idx = self.current_idx if self.is_at_stop else self.current_idx + 1
        if target_idx >= len(self.stops): return

        target_stop = self.stops[target_idx]
        coords = self.stops_db.get(target_stop['Nazwa'].rsplit(' ', 1)[0]) # Dopasowanie bazy
        if not coords: return

        dist = self.calculate_distance(my_lat, my_lon, coords['lat'], coords['lon'])

        # Logika odjazdu (GPS)
        if self.is_at_stop and dist > 0.040: 
            self.is_at_stop = False
            if self.current_idx < len(self.stops) - 1:
                next_data = self.stops[self.current_idx + 1]
                # Napis zmieni się dopiero jak lektor skończy mówić
                self.play_sequence(["Następny Przystanek.mp3", f"{next_data['Audio']}.mp3"], 
                                callback=lambda: self.update_stop_label(next_data['Nazwa']))

        elif not self.is_at_stop and dist < 0.025:
            self.current_idx += 1
            self.is_at_stop = True
            self.play_sequence([f"{self.stops[self.current_idx]['Audio']}.mp3"])
            
    def play_sequence(self, file_list, callback=None):
        # Jeśli dostaniemy jeden napis zamiast listy, robimy z niego listę
        if isinstance(file_list, str):
            file_list = [file_list]
            
        # Jeśli lista pusta, odpalamy callback (np. zmianę napisu)
        if not file_list:
            if callback: 
                Clock.schedule_once(lambda dt: callback(), 0.1)
            return

        current_file = file_list.pop(0)
        full_path = os.path.join(BASE_DIR, 'audio', current_file)

        if not os.path.exists(full_path):
            print(f"Błąd: Brak pliku {current_file}")
            self.play_sequence(file_list, callback) # Przeskocz do następnego
            return

        sound = SoundLoader.load(full_path)
        if sound:
            def on_stop_handler(inst):
                inst.unload() # Ważne na Linuxie: zwolnij kartę dźwiękową
                Clock.schedule_once(lambda dt: self.play_sequence(file_list, callback), 0.1)
            
            sound.bind(on_stop=on_stop_handler)
            sound.play()
        else:
            # Jeśli SoundLoader zawiedzie, leć dalej
            self.play_sequence(file_list, callback)

class SipScreen(Screen):
    def setup_sip(self, csv_file):
        self.clear_widgets()
        self.sip_layout = MainSIPLayout(csv_file)
        self.add_widget(self.sip_layout)

    def on_enter(self):
        # Dopiero gdy ekran faktycznie się pojawi, puszczamy JEDNĄ zapowiedź
        if hasattr(self, 'sip_layout'):
            start_stop = self.sip_layout.stops[0]
            self.sip_layout.update_stop_label(start_stop['Nazwa'])
            # Opóźnienie 1s, żeby dźwięk nie "strzelił" przed pokazaniem obrazu
            Clock.schedule_once(lambda dt: self.sip_layout.play_sequence([f"{start_stop['Audio']}.mp3"]), 1.0)

class SIPApp(App):
    def build(self):
        sm = ScreenManager(transition=FadeTransition())
        sm.add_widget(StartModeScreen(name='start_mode'))
        sm.add_widget(OperatorSelectScreen(name='operator_select'))
        sm.add_widget(TypeSelectScreen(name='type_select'))
        sm.add_widget(LineSelectScreen(name='lines'))
        sm.add_widget(RouteSelectScreen(name='routes'))
        sm.add_widget(NewsEditorScreen(name='news_editor'))
        sm.add_widget(SipScreen(name='sip'))
        return sm
    def on_stop(self): Window.show_cursor = True

if __name__ == '__main__':
    SIPApp().run()