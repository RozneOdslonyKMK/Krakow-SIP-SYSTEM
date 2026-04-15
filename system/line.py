from system.imports import *

class LineSelectScreen(Screen):
    def load_lines(self):
        self.clear_widgets()
        layout = BoxLayout(orientation='vertical', padding=20, spacing=10)
        grid = GridLayout(cols=6, spacing=10, size_hint_y=None)
        grid.bind(minimum_height=grid.setter('height'))
        
        scroll = ScrollView()
        
        op_dir = SESSION["operator"].split()[0].lower()
        self.base_path = os.path.join(BASE_DIR, 'routes', op_dir, SESSION["type"])

        EXCLUDED_FOLDERS = [
            "notusednow", "not_used_now", "not used now",
            "special_tram_wyjazd", "special_tram_zjazd"
        ]
        
        lines = []
        if os.path.exists(self.base_path):
            lines = [
                d for d in os.listdir(self.base_path)
                if os.path.isdir(os.path.join(self.base_path, d))
                and d.lower() not in EXCLUDED_FOLDERS
            ]
            lines.sort(key=lambda x: (len(x), x))
        
        for line in lines:
            btn = Button(text=line, font_size='30sp', bold=True, background_color=(0, 0.23, 0.45, 1), size_hint_y=None, height=100)
            btn.bind(on_release=lambda x, l=line: self.select_line(l))
            grid.add_widget(btn)

        grid.add_widget(Label(text="TRYBY SPECJALNE", size_hint_y=None, height=50))
        for mode_id, data in SPECIAL_MODES.items():
            if mode_id == "MPK_KRAKOW" and "Mobilis" in SESSION["operator"]:
                continue
                
            if mode_id == "MOBILIS" and "MPK" in SESSION["operator"]:
                continue
            
            btn = Button(text=data["label"], font_size='18sp', background_color=(0.4, 0.4, 0.4, 1), size_hint_y=None, height=100)
            btn.bind(on_release=lambda x, m=mode_id: self.select_special(m))
            grid.add_widget(btn)

        scroll.add_widget(grid)
        layout.add_widget(Label(text="WYBIERZ NUMER LINII LUB TRYB", size_hint_y=0.1))
        layout.add_widget(scroll)
        
        back = Button(text="POWRÓT", size_hint_y=0.15, background_color=(0.5, 0.5, 0.5, 1))
        back.bind(on_release=lambda x: setattr(self.manager, 'current', 'type_select'))
        layout.add_widget(back)
        self.add_widget(layout)

    def select_line(self, line_no):
        SESSION["special_mode_id"] = None
        line_path = os.path.join(self.base_path, line_no)
        files = [f for f in os.listdir(line_path) if f.endswith('.csv')]
        self.manager.get_screen('routes').update_routes(line_no, files, line_path)
        self.manager.current = 'routes'

    def select_special(self, mode_id):
        SESSION["special_mode_id"] = mode_id
        if SPECIAL_MODES[mode_id]["stops"]:
            op_dir = SESSION["operator"].split()[0].lower()
            base_path = os.path.join(BASE_DIR, 'routes', op_dir, SESSION["type"])
            line_path = os.path.join(base_path, "SPECIAL_" + mode_id)
            if not os.path.exists(line_path): os.makedirs(line_path)
            files = [f for f in os.listdir(line_path) if f.endswith('.csv')]
            self.manager.get_screen('routes').update_routes(mode_id, files, line_path)
            self.manager.current = 'routes'
        else:
            SESSION["selected_csv_path"] = ""
            self.manager.current = 'news_editor'
