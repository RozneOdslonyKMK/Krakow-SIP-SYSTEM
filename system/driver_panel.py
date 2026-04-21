import os
import sys
import random
import subprocess
from datetime import datetime, timedelta

from kivy.config import Config
Config.set('graphics', 'width', '1024')
Config.set('graphics', 'height', '602')
Config.set('graphics', 'resizable', False)

from system.imports import *

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

FOLDER_MAP = {
    "MPK Kraków": "mpk",
    "Mobilis": "mobilis",
    "KLM": "klm",
    "Tramwaj": "tramwaj",
    "Autobus": "autobus"
}

class DriverPanel(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.screen_width = 1024
        self.screen_height = 602
        self.layout = FloatLayout(size=(self.screen_width, self.screen_height))
        self.input_buffer = ""
        self.current_page = 1
        self.color_white = (1, 1, 1, 1)
        self.color_black = (0, 0, 0, 1)
        self.color_blue = (0, 0.23, 0.65, 1)
        
        self.bg = Image(source=os.path.join(BASE_DIR, 'trapeze', 'Boot.png'),
                        allow_stretch=True, keep_ratio=False)
        self.layout.add_widget(self.bg)
        self.setup_labels()
        self.add_widget(self.layout)
        self.on_enter()

        Clock.schedule_interval(self.update_delay_display, 10)
        
    def pos_conv(self, x, y, w, h):
        win_w, win_h = Window.size
        scale_x = win_w / 1024
        scale_y = win_h / 602
        
        final_w = w * scale_x
        final_h = h * scale_y
        final_x = x * scale_x
        final_y = win_h - (y * scale_y) - final_h
        
        return (final_x, final_y), (final_w, final_h)

    def setup_labels(self):
        c_pos, c_size = self.pos_conv(4, 4, 240, 60)
        self.clock_lbl = Label(text="--:--:--", font_size='60sp', bold=True,
                               size_hint=(None, None), size=c_size,
                               pos=c_pos, halign='center', valign='middle')
        
        d_pos, d_size = self.pos_conv(812, 138, 178, 66)
        self.delay_lbl = Label(text="--:--", font_size='60sp', bold=True,
                               size_hint=(None, None), size=d_size,
                               pos=d_pos)

        l_pos, l_size = self.pos_conv(812, 31, 178, 66)
        self.line_brygada_lbl = Label(text="---/---", font_size='60sp',
                                      size_hint=(None, None), size=l_size,
                                      pos=l_pos)

    def on_enter(self):
        SESSION["is_running"] = False
        SESSION["current_view"] = "settings"
        Clock.schedule_once(self.start_loading, 2)
        Clock.schedule_interval(self.update_ui_data, 1)

    def update_ui_data(self, dt):
        self.clock_lbl.text = datetime.now().strftime("%H:%M:%S")

        try:
            if os.path.exists("sync.json"):
                with open("sync.json", "r", encoding="utf-8") as f:
                    data = json.load(f)
                    new_idx = data.get("current_stop_index", 0)
                    
                    if not hasattr(self, 'last_sync_idx'): self.last_sync_idx = new_idx
                    
                    if new_idx != self.last_sync_idx:
                        self.last_sync_idx = new_idx
                        SESSION["current_stop_index"] = new_idx
                        self.show_list_elements(mode="stops")
        except Exception as e:
            print(f"Błąd odczytu sync.json: {e}")

    def add_btn(self, x, y, w, h, callback, disabled=False):
        pos, size = self.pos_conv(x, y, w, h)
        btn = Button(
            size_hint=(None, None),
            size=size,
            pos=pos,
            background_color=(0, 0, 0, 0) if not disabled else (0.2, 0.2, 0.2, 0.5)
        )
        if not disabled:
            btn.bind(on_release=callback)
        self.layout.add_widget(btn)

    def start_loading(self, dt):
        self.loading_idx = 1
        self.fake_loading_step()

    def fake_loading_step(self, *args):
        if self.loading_idx <= 10:
            self.bg.source = os.path.join(BASE_DIR, 'trapeze', f'Boot_{self.loading_idx:02d}.png')
            self.loading_idx += 1
            Clock.schedule_once(self.fake_loading_step, random.uniform(0, 1))
        else:
            self.show_tryb_pracy()

    def refresh_layout(self, bg_name, screen_type):
        self.layout.clear_widgets()
        self.bg.source = os.path.join(BASE_DIR, 'trapeze', bg_name)
        self.current_bg_name = bg_name
        self.layout.add_widget(self.bg)
        
        if screen_type == "drive":
            self.add_btn(782, 360, 238, 116, lambda x: self.show_tryb_pracy())
            SESSION["current_view"] = "drive"
        elif screen_type == "settings":
            self.add_btn(782, 360, 100, 100, self.handle_info)
            self.add_btn(902, 360, 118, 116, lambda x: self.show_tryb_pracy())
            SESSION["is_running"] = False
            SESSION["current_route_data"] = []
            SESSION["current_view"] = "settings"

    def show_tryb_pracy(self):
        SESSION["settings_back_func"] = self.show_tryb_pracy
        SESSION["is_running"] = False
        SESSION["current_view"] = "settings"
        self.refresh_layout("Tryb_Pracy.png", "settings")
        
        c_pos, c_size = self.pos_conv(4, 4, 240, 60)
        self.clock_lbl.pos = c_pos
        self.clock_lbl.size = c_size
        
        self.layout.add_widget(self.clock_lbl)
        self.add_btn(782, 480, 238, 116, self.handle_speaker_btn)

        self.add_list_logic(self.select_tryb, back_func=self.show_tryb_pracy)

    def select_tryb(self, index):
        tryby = ["Dom", "Pojazd"]
        if index < len(tryby):
            SESSION["mode"] = tryby[index]
            print(f"Wybrano tryb: {SESSION['mode']}")
            self.show_operator()

    def show_operator(self):
        SESSION["settings_back_func"] = self.show_operator
        SESSION["current_view"] = "settings"
        self.refresh_layout("Operator.png", "settings")
        
        c_pos, c_size = self.pos_conv(4, 4, 240, 60)
        self.clock_lbl.pos = c_pos
        self.clock_lbl.size = c_size
        
        self.layout.add_widget(self.clock_lbl)
        self.add_btn(782, 480, 238, 116, self.handle_speaker_btn)

        self.add_list_logic(self.select_operator, back_func=self.show_tryb_pracy)

    def select_operator(self, index):
        op_display_names = list(OPERATORS.keys())
        if index < len(op_display_names):
            selected_op = op_display_names[index]
            SESSION["operator"] = selected_op
            SESSION["operator_folder"] = FOLDER_MAP.get(selected_op, "unknown")
            self.show_wybor_pojazdu()
    
    def show_wybor_pojazdu(self):
        SESSION["settings_back_func"] = self.show_wybor_pojazdu
        SESSION["current_view"] = "settings"
        self.refresh_layout("Pojazd.png", "settings")
        
        c_pos, c_size = self.pos_conv(4, 4, 240, 60)
        self.clock_lbl.pos = c_pos
        self.clock_lbl.size = c_size
        
        self.layout.add_widget(self.clock_lbl)
        self.add_btn(782, 480, 238, 116, self.handle_speaker_btn)

        self.add_list_logic(self.select_pojazd, back_func=self.show_operator, is_vehicle_screen=True)

    def select_pojazd(self, index):
        pojazdy = ["Tramwaj", "Autobus"]
        
        if index < len(pojazdy):
            selected = pojazdy[index]
            dostepne = OPERATORS.get(SESSION.get("operator"), [])
            
            if selected in dostepne:
                SESSION["type"] = selected
                SESSION["type_folder"] = FOLDER_MAP.get(selected, selected.lower())
                self.show_typ_kursu()
            else:
                print(f"Ten operator nie obsługuje: {selected}")

    def show_typ_kursu(self):
        SESSION["settings_back_func"] = self.show_typ_kursu
        SESSION["current_view"] = "settings"
        bg = "Typ_kursu_01.png" if self.current_page == 1 else "Typ_kursu_02.png"
        self.refresh_layout(bg, "settings")
        
        c_pos, c_size = self.pos_conv(4, 4, 240, 60)
        self.clock_lbl.pos = c_pos
        self.clock_lbl.size = c_size
        
        self.layout.add_widget(self.clock_lbl)
        self.add_btn(782, 480, 238, 116, self.handle_speaker_btn)

        self.add_list_logic(self.select_typ_kursu, back_func=self.show_wybor_pojazdu, has_paging=True)

    def select_typ_kursu(self, index):
        if index == "paging":
            self.current_page = 2 if self.current_page == 1 else 1
            self.show_typ_kursu()
            return

        page1_keys = ["LINIA", "WYJAZD", "ZJAZD", "PRZEJAZD_TECH"]
        page2_keys = ["NAUKA_JAZDY", "JAZDA_TEST", "JAZDA_PROBNA", "LOGO"]
        
        current_keys = page1_keys if self.current_page == 1 else page2_keys
        selected_key = current_keys[index]

        if selected_key == "LINIA":
            SESSION["mode_type"] = "LINE"
            self.show_numpad_linia()
        
        elif selected_key == "LOGO":
            self.handle_logo_selection()
            
        else:
            final_key = selected_key
            if selected_key in ["WYJAZD", "ZJAZD"]:
                prefix = "TRAM_" if SESSION.get("type") == "Tramwaj" else "BUS_"
                final_key = prefix + selected_key
            
            self.start_special_drive(final_key)

    def handle_logo_selection(self):
        operator = SESSION.get("operator")
        
        if operator == "Mobilis":
            special_key = "MOBILIS"
        else:
            special_key = "MPK_KRAKOW"
            
        self.start_special_drive(special_key)

    def show_numpad_linia(self):
        SESSION["settings_back_func"] = self.show_numpad_linia
        SESSION["current_view"] = "settings"
        self.refresh_layout("Linia.png", "settings")
        
        c_pos, c_size = self.pos_conv(4, 4, 240, 60)
        self.clock_lbl.pos = c_pos
        self.clock_lbl.size = c_size
        
        self.layout.add_widget(self.clock_lbl)
        self.add_btn(782, 480, 238, 116, self.handle_speaker_btn)

        self.input_buffer = ""
        coords = [
            (248, 244, '1'), (381, 244, '2'), (515, 244, '3'), (649, 244, '4'),
            (248, 362, '5'), (381, 362, '6'), (515, 362, '7'), (649, 362, '8'),
            (248, 482, 'C'), (381, 482, '0'), (515, 482, '9'), (649, 482, 'OK')
        ]
        for x, y, val in coords:
            self.add_btn(x, y, 128, 112, lambda instance, v=val: self.handle_numpad(v, back_func=self.show_typ_kursu))
        
        pos, size = self.pos_conv(254, 154, 250, 78)
        self.numpad_lbl = Label(text="", font_size='50sp', color=(1,1,1,1),
                                size_hint=(None, None), size=size,
                                pos=pos)
        self.layout.add_widget(self.numpad_lbl)

    def show_numpad_special(self, special_key):
        self.refresh_layout("Linia.png", "settings")
        
        c_pos, c_size = self.pos_conv(4, 4, 240, 60)
        self.clock_lbl.pos = c_pos
        self.clock_lbl.size = c_size
        
        self.layout.add_widget(self.clock_lbl)

        self.input_buffer = ""
        self.show_numpad_linia(callback=lambda: self.show_kierunek_special(special_key))

    def show_kierunek_special(self, special_key):
        sub_folder = "wyjazdy" if "WYJAZD" in special_key else "zjazdy"
        rel_path = os.path.join(
            "routes", 
            SESSION.get("operator_folder", ""),
            SESSION.get("typ_pojazdu_folder", ""),
            sub_folder
        )
        full_path = os.path.join(BASE_DIR, rel_path)
        
        if os.path.exists(full_path):
            pliki = [f for f in os.listdir(full_path) if f.endswith(".csv")]
            for i, plik in enumerate(pliki[:4]):
                y = [128, 244, 362, 482][i]
                nazwa = plik.replace(".csv", "")
                
                btn_lbl = Label(text=nazwa, pos=self.pos_conv(248, y, 530, 112),
                                size_hint=(None, None), size=(530, 112), 
                                font_size='24sp', color=(1,1,1,1))
                self.layout.add_widget(btn_lbl)
                
                csv_full_path = os.path.join(full_path, plik)
                self.add_btn(248, y, 530, 112, lambda inst, p=csv_full_path: self.confirm_route(p))
        else:
            p_pos, p_size = self.pos_conv(248, 128, 530, 112)
            self.layout.add_widget(Label(text="BŁĄD: BRAK LINII", pos=p_pos, size=p_size, size_hint=(None, None)))

    def handle_numpad(self, val, back_func):
        self.add_btn(260, 6, 55, 84, lambda x: back_func())
        if val == 'C':
            self.input_buffer = self.input_buffer[:-1]
        elif val == 'OK':
            if len(self.input_buffer) == 7:
                raw_line = self.input_buffer[:3]
                raw_brygada = self.input_buffer[-3:]

                line_to_check = raw_line.lstrip("0")
                if not line_to_check: line_to_check = "0"

                routes_path = os.path.join(
                    BASE_DIR, "routes", 
                    SESSION.get("operator_folder", ""),
                    SESSION.get("type_folder", ""),
                )
                
                matched_folder = None
                if os.path.exists(routes_path):
                    items = os.listdir(routes_path)
                    for f in items:
                        full_p = os.path.join(routes_path, f)
                        if os.path.isdir(full_p):
                            if f == line_to_check:
                                matched_folder = f
                                break

                if matched_folder:
                    SESSION["line_folder"] = matched_folder
                    SESSION["line_number"] = line_to_check
                    SESSION["brygada_number"] = raw_brygada
                    SESSION["full_input"] = self.input_buffer
                    self.show_kierunek()
                    return
                else:
                    self.input_buffer = ""
                    return
            else:
                self.input_buffer = ""
                return            
        else:
            if len(self.input_buffer) < 7:
                self.input_buffer += val
        
        self.numpad_lbl.text = self.input_buffer

    def show_kierunek(self):
        SESSION["settings_back_func"] = self.show_kierunek
        SESSION["current_view"] = "settings"
        self.refresh_layout("Kierunek.png", "settings")
        
        c_pos, c_size = self.pos_conv(4, 4, 240, 60)
        self.clock_lbl.pos = c_pos
        self.clock_lbl.size = c_size
        
        self.layout.add_widget(self.clock_lbl)
        self.add_btn(782, 480, 238, 116, self.handle_speaker_btn)

        line_folder = SESSION.get("line_folder")
        
        full_path = os.path.join(
            BASE_DIR, "routes", 
            SESSION.get("operator_folder", ""),
            SESSION.get("type_folder", ""),
            line_folder
        )

        if os.path.exists(full_path):
            pliki = [f for f in os.listdir(full_path) if f.endswith(".csv")]
            for i, plik in enumerate(pliki[:4]):
                y = [128, 244, 362, 482][i]
                nazwa = plik.replace(".csv", "")
                
                pos, size = self.pos_conv(248, y, 530, 112)
                btn_lbl = Label(text=nazwa, pos=pos,
                                size_hint=(None, None), size=size, 
                                font_size='24sp', color=(1,1,1,1))
                self.layout.add_widget(btn_lbl)
                
                csv_full_path = os.path.join(full_path, plik)
                self.add_btn(248, y, 530, 112, lambda inst, p=csv_full_path: self.confirm_route(p))

    def show_lektor_menu(self, *args):
        SESSION["current_view"] = "lektor_menu"
        self.refresh_layout("Lektor.png", "settings")
        
        c_pos, c_size = self.pos_conv(4, 4, 240, 60)
        self.clock_lbl.pos = c_pos
        self.clock_lbl.size = c_size
        
        self.layout.add_widget(self.clock_lbl)
        self.add_btn(782, 480, 238, 116, self.handle_speaker_btn)

        voice_options = list(VOICE_TYPES.keys())

        back_to = SESSION.get("settings_back_func", self.show_operator)

        def select_voice(index):
            if index < len(voice_options):
                choice = voice_options[index]
                SESSION["voice_path"] = VOICE_TYPES[choice]
                print(f"DRIVER: Wybrano lektora: {choice}")
                
                if SESSION.get("is_running"):
                    self.show_list_elements(mode="stops")
                else:
                    back_to()

        self.add_list_logic(select_voice, back_func=back_to)

    def confirm_route(self, full_path):
        self.load_route_data_from_csv(full_path)

        raw_line = self.input_buffer
        prefix = raw_line[:3]
        try:
            formatted_line = str(int(prefix))
            if not formatted_line: formatted_line = "0"
        except ValueError:
            formatted_line = prefix

        SESSION["selected_csv_path"] = full_path
        SESSION["line_number"] = formatted_line
        SESSION["current_stop_index"] = 0
        
        sync_data = {
            "selected_csv_path": full_path,
            "line_number": formatted_line,
            "line": raw_line,
            "current_stop_index": 0,
            "last_update_source": "driver",
            "full_route_data": self.stops,
            "voice_types": VOICE_TYPES,
            "search_order": SEARCH_ORDER,
            "voice_path": SESSION.get("voice_path", ""),
            "special_key": SESSION.get("special_key")
        }
        try:
            with open("sync.json", "w", encoding="utf-8") as f:
                json.dump(sync_data, f, ensure_ascii=False, indent=4)
                f.flush()
                os.fsync(f.fileno())
        except Exception as e:
            print(f"Błąd zapisu startowego: {e}")
            
        self.start_drive()
    
    def start_special_drive(self, special_key):
        data = SPECIAL_MODES.get(special_key)
        
        SESSION["mode_type"] = "SPECIAL"
        SESSION["special_key"] = special_key
        SESSION["label"] = data["label"]
        SESSION["is_running"] = True
        SESSION["current_view"] = "drive"
        
        if special_key in ["TRAM_WYJAZD", "TRAM_ZJAZD"]:
            self.show_numpad_special(special_key)
            return
        
        self.refresh_layout("bg.png", "drive")

        c_pos, c_size = self.pos_conv(4, 4, 240, 60)
        self.clock_lbl.pos = c_pos
        self.clock_lbl.size = c_size
        
        d_pos, d_size = self.pos_conv(812, 138, 178, 66)
        self.delay_lbl.pos = d_pos
        self.delay_lbl.size = d_size
        
        l_pos, l_size = self.pos_conv(812, 31, 178, 66)
        self.line_brygada_lbl.pos = l_pos
        self.line_brygada_lbl.size = l_size

        line_val = SESSION.get("full_input", "---")[:3]
        brygada_val = SESSION.get("brygada_number", "---")
        self.line_brygada_lbl.text = f"{line_val}/{brygada_val}"

        self.layout.add_widget(self.clock_lbl)
        self.layout.add_widget(self.delay_lbl)
        self.layout.add_widget(self.line_brygada_lbl)

        self.add_btn(782, 480, 238, 116, self.handle_speaker_btn)
        self.add_btn(4, 244, 118, 112, self.toggle_map_view)

        target_label = Label(
            text=data["label"], font_size='40sp', bold=True,
            size_hint=(None, None), size=l_size,
            pos=l_pos
        )
        self.layout.add_widget(target_label)
        
        if not SESSION.get("sip_launched", False):
            subprocess.Popen([sys.executable, "system-universal.py", "sip"])
            SESSION["sip_launched"] = True

    def start_drive(self):
        SESSION["is_running"] = True
        SESSION["current_view"] = "drive"
        self.refresh_layout("bg_01.png", "drive")

        c_pos, c_size = self.pos_conv(4, 4, 240, 60)
        self.clock_lbl.pos = c_pos
        self.clock_lbl.size = c_size
        
        d_pos, d_size = self.pos_conv(812, 138, 178, 66)
        self.delay_lbl.pos = d_pos
        self.delay_lbl.size = d_size
        
        l_pos, l_size = self.pos_conv(812, 31, 178, 66)
        self.line_brygada_lbl.pos = l_pos
        self.line_brygada_lbl.size = l_size

        line_val = SESSION.get("full_input", "---")[:3]
        brygada_val = SESSION.get("brygada_number", "---")
        self.line_brygada_lbl.text = f"{line_val}/{brygada_val}"

        self.layout.add_widget(self.clock_lbl)
        self.layout.add_widget(self.delay_lbl)
        self.layout.add_widget(self.line_brygada_lbl)

        Clock.unschedule(self.update_delay_display) 
        Clock.schedule_interval(self.update_delay_display, 10)
        self.update_delay_display(0)

        self.add_btn(782, 480, 238, 116, self.handle_speaker_btn)
        self.add_btn(4, 244, 118, 112, self.toggle_map_view)

        csv_to_load = SESSION["selected_csv_path"]

        if csv_to_load and os.path.exists(csv_to_load):
            self.load_route_data_from_csv(csv_to_load)
            Clock.schedule_once(lambda dt: self.show_list_elements(mode="stops"), 0.1)
            if not SESSION.get("sip_launched", False):
                subprocess.Popen([sys.executable, "system-universal.py", "sip"])
                SESSION["sip_launched"] = True
        else:
            print(f"BŁĄD: Nie znaleziono trasy {csv_to_load}")

    def get_delay_bg(self, delay_seconds):
        abs_sec = abs(delay_seconds)
        minutes = abs_sec // 60

        if abs_sec == 0:
            return "bg_01.png"

        if delay_seconds < 0:
            if minutes == 0: return "bg_+.png"
            if minutes == 1: return "bg_+_01.png"
            if minutes == 2: return "bg_+_02.png"
            if minutes == 3: return "bg_+_03.png"
            if minutes == 4: return "bg_+_04.png"
            return "bg_+_05.png"

        else:
            if minutes == 0: return "bg_-.png"
            if minutes == 1: return "bg_-_01.png"
            if minutes == 2: return "bg_-_02.png"
            if minutes == 3: return "bg_-_03.png"
            if minutes == 4: return "bg_-_04.png"
            return "bg_-_05.png"

    def update_delay_display(self, dt):
        if SESSION.get("is_running"):
            delay_str, diff_seconds = self.calculate_delay_full() 
            
            if hasattr(self, 'delay_lbl'):
                self.delay_lbl.text = delay_str
                
            new_bg = self.get_delay_bg(diff_seconds)
            if hasattr(self, 'bg') and self.bg.source != new_bg:
                self.bg.source = os.path.join(BASE_DIR, 'trapeze', new_bg)
                self.current_bg_name = new_bg

    def load_route_data_from_csv(self, csv_path):
        self.stops = []
        now = datetime.now()
        if now.second < 30:
            start_time = (now + timedelta(minutes=1)).replace(second=0, microsecond=0)
        else:
            start_time = (now + timedelta(minutes=2)).replace(second=0, microsecond=0)
        SESSION["route_start_datetime"] = start_time.isoformat()

        try:
            with open(csv_path, mode='r', encoding='utf-8-sig') as f:
                filtered_lines = [line for line in f if line.strip() and not line.startswith('#')]
                
                if not filtered_lines:
                    return
                    
                reader = csv.DictReader(filtered_lines, delimiter=';')
                
                SESSION["direction"] = "KIERUNEK"

                for i, row in enumerate(reader):
                    clean_row = {k.strip(): v.strip() for k, v in row.items() if k}
                    
                    if i == 0:
                        kierunek = clean_row.get('Kierunek')
                        if kierunek:
                            SESSION["direction"] = kierunek
                            print(f"DRIVER: Ustawiono kierunek z CSV: {kierunek}")

                    try:
                        relative_minutes = int(clean_row.get('Czas', 0))
                    except ValueError:
                        relative_minutes = 0
                    scheduled_time = start_time + timedelta(minutes=relative_minutes)

                    self.stops.append({
                        'name': clean_row.get('Nazwa', '---'),
                        'time': scheduled_time.strftime("%H:%M"),
                        'Timestamp_Planowy': scheduled_time.timestamp()
                    })

            SESSION["current_route_data"] = self.stops
            
        except Exception as e:
            print(f"BŁĄD CSV: {e}")

    def calculate_delay_full(self):
        trasa = SESSION.get("current_route_data", self.stops)
        curr_idx = SESSION.get("current_stop_index", 0)
        
        if not trasa or curr_idx >= len(trasa):
            return "+00:00", 0

        planned_ts = trasa[curr_idx].get('Timestamp_Planowy')
        if planned_ts is None:
            return "--:--", 0

        now_ts = datetime.now().timestamp()
        diff = planned_ts - now_ts
        
        abs_diff = abs(int(diff))
        rounded_diff = (abs_diff // 10) * 10
        
        minutes = rounded_diff // 60
        seconds = rounded_diff % 60
        
        if rounded_diff == 0:
            sign = "+"
        else:
            sign = "+" if diff > 0 else "-"
            
        formatted = f"{sign}{minutes:02d}:{seconds:02d}"
        
        real_diff_for_bg = rounded_diff if diff > 0 else -rounded_diff
        
        return formatted, real_diff_for_bg

    def update_top_bar(self, name_fallback):
        p_pos, p_size = self.pos_conv(248, 4, 530, 81)
        
        trasa = SESSION.get("current_route_data", [])
        idx = SESSION.get("current_stop_index", 0)
        
        if trasa and 0 <= idx < len(trasa):
            stop_name = str(trasa[idx].get("name", "BŁĄD DANYCH"))
        else:
            stop_name = str(name_fallback)

        if hasattr(self, 'current_stop_lbl'):
            self.layout.remove_widget(self.current_stop_lbl)
        if hasattr(self, 'top_time_lbl'):
            self.layout.remove_widget(self.top_time_lbl)

        self.current_stop_lbl = Label(
            text=stop_name.upper(), 
            font_size='24sp', 
            color=self.color_white,
            size_hint=(None, None), 
            size=(p_size[0]*0.7, p_size[1]),
            pos=p_pos, 
            halign='left', 
            valign='middle', 
            text_size=(p_size[0]*0.7, p_size[1])
        )
        
        self.top_time_lbl = Label(
            text=datetime.now().strftime("%H:%M"), 
            font_size='24sp',
            size_hint=(None, None), 
            size=(p_size[0]*0.3, p_size[1]),
            pos=(p_pos[0] + p_size[0]*0.7, p_pos[1]), 
            color=self.color_blue,
            halign='right', 
            valign='middle', 
            text_size=(p_size[0]*0.3, p_size[1])
        )
        
        self.layout.add_widget(self.current_stop_lbl)
        self.layout.add_widget(self.top_time_lbl)

    def add_list_logic(self, callback, back_func, has_paging=False, is_vehicle_screen=False):
        self.add_btn(260, 6, 55, 84, lambda x: back_func())
        
        y_coords = [91, 159, 230, 300]
        operator = SESSION.get("operator")
        dostepne_pojazdy = OPERATORS.get(operator, []) if is_vehicle_screen else None

        for i, y in enumerate(y_coords):
            is_disabled = False

            if is_vehicle_screen:
                if i == 0 and "Tramwaj" not in dostepne_pojazdy:
                    is_disabled = True
                elif i == 1 and "Autobus" not in dostepne_pojazdy:
                    is_disabled = True

            self.add_btn(260, y, 508, 66, lambda inst, idx=i: callback(idx), disabled=is_disabled)

        if has_paging:
            self.add_btn(260, 399, 508, 66, lambda x: callback("paging"))

    def handle_speaker_btn(self, instance):
        print(f"DEBUG: view={SESSION.get('current_view')}, running={SESSION.get('is_running')}")
        bg = getattr(self, 'current_bg_name', "")
        curr_view = SESSION.get("current_view")

        if bg.startswith("bg"):
            if curr_view == "anns":
                self.show_list_elements(mode="stops")
            else:
                self.show_list_elements(mode="anns")

        else:
            if bg == "Lektor.png" or curr_view == "lektor_menu":
                back_func = SESSION.get("settings_back_func")
                if back_func:
                    back_func()
                else:
                    self.show_operator_selection()
                SESSION["current_view"] = "settings"
            else:
                self.show_lektor_menu()

    def handle_info(self, instance):
        if self.bg.source.endswith("Linia.png"):
            self.bg.source = os.path.join(BASE_DIR, 'trapeze', 'Info.png')
        elif self.bg.source.endswith("Info.png"):
            self.bg.source = os.path.join(BASE_DIR, 'trapeze', 'Linia.png')

    def load_announcements(self):
        ann_path = os.path.join(BASE_DIR, "dictionaries", "anns.txt")
        anns = []
        if os.path.exists(ann_path):
            with open(ann_path, "r", encoding="utf-8") as f:
                for line in f:
                    if "|" in line:
                        text, audio = line.strip().split("|")
                        anns.append({"text": text, "audio": audio})
        return anns
    
    def show_list_elements(self, mode="stops"):
        if mode == "anns":
            SESSION["current_view"] = "anns"
        else:
            SESSION["current_view"] = "drive"
        
        if not self.stops:
            self.force_sync_from_file()
        
        list_coords = [
            (248, 480, 530, 116),
            (248, 360, 530, 116),
            (248, 244, 530, 112),
            (248, 128, 530, 112),
            (248, 4, 530, 120)
        ]
        
        for child in [c for c in self.layout.children if isinstance(c, FloatLayout)]:
             self.layout.remove_widget(child)

        if mode == "anns":
            anns = self.load_announcements()
            for i in range(5):
                coord_idx = 4 - i
                if i < len(anns):
                    x, y, w, h = list_coords[coord_idx]
                    self.draw_list_item(anns[i]["text"], "", x, y, w, h)
        
        elif mode == "stops":
            trasa = SESSION.get("current_route_data", [])
            curr_idx = SESSION.get("current_stop_index", 0)
            
            offsets = [2, 1, 0, -1, -2]
            
            for i, offset in enumerate(offsets):
                coord_idx = 4 - i
                x, y, w, h = list_coords[coord_idx]
                
                target_idx = curr_idx + offset
                if 0 <= target_idx < len(trasa):
                    stop_item = trasa[target_idx]
                    name = stop_item.get('name', '---')
                    planned_time = stop_item.get('time', '--:--')
                    
                    self.draw_list_item(
                        name, planned_time,
                        x, y, w, h, 
                        is_first=(coord_idx == 4),
                        target_idx=target_idx
                    )
    
    def draw_list_item(self, name, time, x, y, w, h, is_first=False, target_idx=None):
        pos, size = self.pos_conv(x, y, w, h)
        
        item_box = FloatLayout(size_hint=(None, None), size=size, pos=pos)
        
        name_lbl = Label(
            text=name.upper(), font_size='60sp', bold=True, color=self.color_white,
            size_hint=(0.85, 0.5), pos_hint={'x': 0.02, 'top': 0.95},
            halign='left', valign='top', text_size=(size[0]*0.85, size[1]*0.5)
        )
        
        time_lbl = Label(
            text=time, font_size='60sp', color=self.color_blue,
            size_hint=(0.2, 0.5), pos_hint={'right': 0.98, 'top': 0.95},
            halign='right', valign='top', text_size=(size[0]*0.2, size[1]*0.5)
        )

        btn = Button(background_color=(0,0,0,0), size_hint=(1, 1), pos_hint={'x': 0, 'y': 0})
        if target_idx is not None:
            btn.bind(on_release=lambda instance: self.change_stop_manually(target_idx))

        item_box.add_widget(btn)

        item_box.add_widget(name_lbl)
        item_box.add_widget(time_lbl)

        if is_first:
            target = SESSION.get("direction", "KIERUNEK")
            target_lbl = Label(
                text=target.upper(), font_size='55sp', color=self.color_blue,
                size_hint=(0.85, 0.3), pos_hint={'x': 0.02, 'y': 0.05},
                halign='left', valign='bottom', text_size=(size[0]*0.85, size[1]*0.3)
            )
            item_box.add_widget(target_lbl)

        self.layout.add_widget(item_box)

    def change_stop_manually(self, new_idx):
        trasa = SESSION.get("current_route_data", [])
        if not trasa or not (0 <= new_idx < len(trasa)):
            return

        print(f"Kierowca wybiera przystanek: {new_idx} ({trasa[new_idx]['name']})")
        
        SESSION["current_stop_index"] = new_idx
        
        try:
            data = {}
            if os.path.exists("sync.json"):
                with open("sync.json", "r", encoding="utf-8") as f:
                    data = json.load(f)
            
            data["current_stop_index"] = new_idx
            data["last_update_source"] = "driver"
            
            if "full_route_data" not in data:
                data["full_route_data"] = trasa

            with open("sync.json", "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=4)
        except Exception as e:
            print(f"Błąd zapisu rozkazu: {e}")
            
        self.show_list_elements(mode="stops")
        self.update_delay_display(0)
        # self.update_top_bar("")
        
    def toggle_map_view(self, instance):
        print("DEBUG: Przełączanie widoku mapy (OSM Placeholder)")
        
        self.update_top_bar(self.name)

        # m_pos, m_size = self.pos_conv(248, 91, 530, 505)
        # with self.layout.canvas.after:
        #     from kivy.graphics import Color, Rectangle
        #     Color(self.color_black)
        #     self.map_rect = Rectangle(pos=m_pos, size=m_size)

    def init_shutdown(self, *args):
        self.layout.clear_widgets()
        shutdown_path = os.path.join(BASE_DIR, 'trapeze', 'Shutdown.png')
        self.bg.source = shutdown_path
        self.layout.add_widget(self.bg)
        
        Clock.schedule_once(lambda dt: sys.exit(), 1.5)
        return True

    def check_sync(self, dt):
        sync_file = "sync.json"
        if not os.path.exists(sync_file):
            return
        
        try:
            with open(sync_file, "r", encoding="utf-8") as f:
                content = f.read().strip()
                if not content: 
                    return
                data = json.loads(content)

            full_data = data.get("full_route_data", [])
            
            if full_data:
                current_local_data = SESSION.get("current_route_data", [])
                
                if not current_local_data or len(current_local_data) != len(full_data):
                    print(f"DEBUG: Ładowanie {len(full_data)} przystanków z sync.json do SESSION")
                    SESSION["current_route_data"] = full_data
                    self.show_list_elements(mode="stops")

            new_idx = data.get("current_stop_index", 0)
            if not hasattr(self, 'local_idx'): self.local_idx = -1
            
            if new_idx != self.local_idx:
                print(f"DEBUG: Zmiana indeksu na {new_idx}")
                self.local_idx = new_idx
                SESSION["current_stop_index"] = new_idx
                self.show_list_elements(mode="stops")
                # self.update_top_bar("")

        except (json.JSONDecodeError, OSError) as e:
            pass
    
    def force_sync_from_file(self):
        try:
            if os.path.exists("sync.json"):
                with open("sync.json", "r", encoding="utf-8") as f:
                    data = json.load(f)
                    if "full_route_data" in data:
                        global SESSION
                        SESSION["current_route_data"] = data["full_route_data"]
                        SESSION["current_stop_index"] = data.get("current_stop_index", 0)
        except:
            pass
        