import os
import sys
import random
from datetime import datetime

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
        
        self.bg = Image(source=os.path.join(BASE_DIR, 'trapeze', 'Boot.png'),
                        allow_stretch=True, keep_ratio=False)
        self.layout.add_widget(self.bg)
        self.setup_labels()
        self.add_widget(self.layout)
        self.on_enter()

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
        self.clock_lbl = Label(text="--:--:--", font_size='36sp', bold=True,
                               size_hint=(None, None), size=c_size,
                               pos=c_pos, halign='center', valign='middle')
        
        d_pos, d_size = self.pos_conv(812, 138, 178, 66)
        self.delay_lbl = Label(text="--:--", font_size='34sp', bold=True,
                               size_hint=(None, None), size=d_size,
                               pos=d_pos)

        l_pos, l_size = self.pos_conv(812, 31, 178, 66)
        self.line_brygada_lbl = Label(text="---/---", font_size='34sp',
                                      size_hint=(None, None), size=l_size,
                                      pos=l_pos)

    def on_enter(self):
        Clock.schedule_once(self.start_loading, 2)
        Clock.schedule_interval(self.update_ui_data, 1)

    def update_ui_data(self, dt):
        self.clock_lbl.text = datetime.now().strftime("%H:%M:%S")

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
        self.layout.add_widget(self.bg)
        
        if screen_type == "drive":
            self.add_btn(782, 360, 238, 116, lambda x: self.init_shutdown())
        elif screen_type == "settings":
            self.add_btn(782, 360, 100, 100, self.handle_info)
            self.add_btn(902, 360, 118, 116, lambda x: self.init_shutdown())

    def show_tryb_pracy(self):
        self.refresh_layout("Tryb_Pracy.png", "settings")
        self.add_list_logic(self.select_tryb, back_func=self.show_tryb_pracy)

    def select_tryb(self, index):
        tryby = ["Dom", "Pojazd"]
        if index < len(tryby):
            SESSION["mode"] = tryby[index]
            print(f"Wybrano tryb: {SESSION['mode']}")
            self.show_operator()

    def show_operator(self):
        self.refresh_layout("Operator.png", "settings")
        self.add_list_logic(self.select_operator, back_func=self.show_tryb_pracy)

    def select_operator(self, index):
        op_display_names = list(OPERATORS.keys())
        if index < len(op_display_names):
            selected_op = op_display_names[index]
            SESSION["operator"] = selected_op
            SESSION["operator_folder"] = FOLDER_MAP.get(selected_op, "unknown")
            self.show_wybor_pojazdu()
    
    def show_wybor_pojazdu(self):
        self.refresh_layout("Pojazd.png", "settings")
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
        bg = "Typ_kursu_01.png" if self.current_page == 1 else "Typ_kursu_02.png"
        self.refresh_layout(bg, "settings")
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
        self.refresh_layout("Linia.png", "settings")
        self.input_buffer = ""
        coords = [
            (248, 244, '1'), (381, 244, '2'), (515, 244, '3'), (649, 244, '4'),
            (248, 362, '5'), (381, 362, '6'), (515, 362, '7'), (649, 362, '8'),
            (248, 482, 'C'), (381, 482, '0'), (515, 482, '9'), (649, 482, 'OK')
        ]
        for x, y, val in coords:
            self.add_btn(x, y, 128, 112, lambda instance, v=val: self.handle_numpad(v))
        
        pos, size = self.pos_conv(254, 154, 250, 78)
        self.numpad_lbl = Label(text="", font_size='50sp', color=(1,1,1,1),
                                size_hint=(None, None), size=size,
                                pos=pos)
        self.layout.add_widget(self.numpad_lbl)

    def show_numpad_special(self, special_key):
        self.refresh_layout("Linia.png", "settings")
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
            self.layout.add_widget(Label(text="BŁĄD: BRAK LINII", pos=self.pos_conv(248, 128, 530, 112)))

    def handle_numpad(self, val):
        if val == 'C':
            self.input_buffer = self.input_buffer[:-1]
        elif val == 'OK':
            if self.input_buffer:
                self.show_kierunek()
        else:
            if len(self.input_buffer) < 4:
                self.input_buffer += val
        
        self.numpad_lbl.text = self.input_buffer

    def show_kierunek(self):
        self.refresh_layout("Kierunek.png", "settings")
        
        rel_path = os.path.join(
            "routes", 
            SESSION.get("operator_folder", ""),
            SESSION.get("type_folder", ""),
            self.input_buffer
        )
        full_path = os.path.join(BASE_DIR, rel_path)
        
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
        else:
            self.layout.add_widget(Label(text="BŁĄD: BRAK LINII", pos=self.pos_conv(248, 128, 530, 112)))

    def confirm_route(self, full_path):
        sync_data = {
            "selected_csv_path": full_path,
            "special_key": SESSION.get("special_key"),
            "line": SESSION.get("line_number")
        }
        with open("sync.json", "w") as f:
            json.dump(sync_data, f)
    
    def start_special_drive(self, special_key):
        data = SPECIAL_MODES.get(special_key)
        
        SESSION["mode_type"] = "SPECIAL"
        SESSION["special_key"] = special_key
        SESSION["label"] = data["label"]
        
        if special_key in ["TRAM_WYJAZD", "TRAM_ZJAZD"]:
            self.show_numpad_special(special_key)
            return
        
        self.refresh_layout("bg.png", "drive")

        self.line_brygada_lbl.text = f"{data['line']}/---" if data['line'] else "---/---"
        
        l_pos, l_size = self.pos_conv(112, 250, 800, 100)

        target_label = Label(
            text=data["label"], font_size='40sp', bold=True,
            size_hint=(None, None), size=l_size,
            pos=l_pos
        )
        self.layout.add_widget(target_label)
        
        app = App.get_running_app()
        if hasattr(app, 'sip_screen'):
            app.sip_screen.setup_special_display(
                target_name=data["label"], 
                show_stops=False
            )

    def start_drive(self):
        self.refresh_layout("bg_01.png", "drive")
        self.layout.add_widget(self.clock_lbl)
        self.layout.add_widget(self.delay_lbl)
        self.layout.add_widget(self.line_brygada_lbl)
        self.add_btn(782, 480, 238, 116, lambda x: print("Menu lektora"))

        app = App.get_running_app()
        csv_to_load = SESSION["selected_csv_path"]

        if os.path.exists(csv_to_load):
            app.sip_screen.setup_sip(csv_to_load)
            app.sm.current = 'sip' 
        else:
            print(f"BŁĄD: Nie znaleziono trasy {csv_to_load}")

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

    def handle_info(self, instance):
        if self.bg.source.endswith("Linia.png"):
            self.bg.source = os.path.join(BASE_DIR, 'trapeze', 'Info.png')
        elif self.bg.source.endswith("Info.png"):
            self.bg.source = os.path.join(BASE_DIR, 'trapeze', 'Linia.png')

    def init_shutdown(self, *args):
        self.layout.clear_widgets()
        shutdown_path = os.path.join(BASE_DIR, 'trapeze', 'Shutdown.png')
        self.bg.source = shutdown_path
        self.layout.add_widget(self.bg)
        
        Clock.schedule_once(lambda dt: sys.exit(), 1.5)
        return True
