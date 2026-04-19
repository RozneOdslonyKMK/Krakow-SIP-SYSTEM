from system.imports import *

class MainSIPLayout(FloatLayout):
    def __init__(self, csv_file, **kwargs):
        super().__init__(**kwargs)
        
        self.base_size = (1920, 1080)
        self.content_box = FloatLayout(size_hint=(None, None), size=self.base_size)
        self.add_widget(self.content_box)
        
        Window.bind(on_resize=self._apply_scaling)
        Clock.schedule_once(self._apply_scaling, 0)
        
        self.audio_queue = []
        self.is_audio_playing = False
        self.current_sound = None
        Window.show_cursor = False

        self.ubuntu_font = os.path.join(BASE_DIR, 'fonts', 'Ubuntu-Regular.ttf')
        self.arial_font = os.path.join(BASE_DIR, 'fonts', 'Arial.ttf')
        self.arimo_font = os.path.join(BASE_DIR, 'fonts', 'Arimo.ttf')
        self.krakow_blue = (0, 0.23, 0.45, 1)
        self.screen_h = 1080

        self.special_id = SESSION.get("special_key")
        self.stops = []
        self.stops_db = {}
        self.current_idx = 0
        self.is_at_stop = True
        
        self.load_stops_db()
        self.load_route(csv_file)

        ads_dir = os.path.join(BASE_DIR, 'ads')
        self.ad_files = [os.path.join(ads_dir, f) for f in os.listdir(ads_dir) if f.endswith(('.mp4', '.mkv', '.avi'))]
        self.ad_files.sort()
        self.current_ad_idx = 0 
        self._loading_ad = False
        self.ads = None
        
        bg = 'podklad_zmiana.png' if SESSION["is_route_changed"] else 'podklad.png'
        bg_source = os.path.join(BASE_DIR, 'sip', 'top', bg)
        self.content_box.add_widget(Image(source=bg_source, allow_stretch=True, keep_ratio=False))

        if self.ad_files:
            Clock.schedule_once(self._rebuild_video_widget, 1.0)

        l_color = (1, 1, 1, 1) if SESSION["is_route_changed"] else self.krakow_blue
        line_display = ""
        if self.special_id:
            line_display = SPECIAL_MODES[self.special_id].get("line", "")
            if not line_display and SESSION.get("line_number"):
                line_display = SESSION.get("line_number")
        elif csv_file:
            path_parts = os.path.normpath(csv_file).split(os.sep)
            line_display = path_parts[-2] if len(path_parts) >= 2 else ""

        self.content_box.add_widget(Label(
            text=str(line_display), font_size='165sp', font_name=self.arimo_font,
            color=l_color, bold=True, size_hint=(None, None), size=(309, 184),
            pos=(0, 1080-184), halign='center', valign='middle', text_size=(309, 184)))

        limit_dest_width = 1316 
        dest_pos_x, dest_pos_y = 309, 1080 - 95
        
        self.dest_container = StencilView(size_hint=(None, None), size=(limit_dest_width, 100),
                                         pos=(dest_pos_x, dest_pos_y))

        direction = self._get_direction_text(csv_file)
        
        self.dest_label = Label(text=direction.upper(), font_size='80sp', font_name=self.arimo_font,
                                color=self.krakow_blue, bold=True, size_hint=(None, None),
                                size=(limit_dest_width, 100), pos=(dest_pos_x, dest_pos_y),
                                halign='left', valign='middle', text_size=(None, 100))
        
        self.dest_label.texture_update()
        self.dest_label.width = self.dest_label.texture_size[0]
        self.should_scroll_dest = self.dest_label.width > limit_dest_width
        
        self.dest_container.add_widget(self.dest_label)
        self.content_box.add_widget(self.dest_container)

        self.stencil = StencilView(size_hint=(None, None), size=(1726, 107), pos=(194, 1080-973-107))
        self.ticker = Label(text=SESSION["news_text"], font_name=self.arial_font, font_size='85sp',
                            size_hint=(None, 1), halign='left', valign='middle', height=107)
        self.ticker.x = 1920
        self.stencil.add_widget(self.ticker)
        self.content_box.add_widget(self.stencil)

        self.clock_label = Label(text="01:00", font_size='90sp', font_name=self.arimo_font,
                                 color=self.krakow_blue, bold=True,
                                 size_hint=(None, None), size=(250, 92),
                                 pos=(1670, 1080 - 92), halign='right', valign='middle',
                                 text_size=(240, 92))
        self.content_box.add_widget(self.clock_label)

        self.date_label = Label(text="poniedziałek\n1 stycznia", font_size='32sp', font_name=self.arimo_font,
                                color=self.krakow_blue, line_height=0.95,
                                size_hint=(None, None), size=(305, 92),
                                pos=(1615, 1080 - 184), halign='right', valign='middle',
                                text_size=(295, 92))
        self.content_box.add_widget(self.date_label)

        Clock.schedule_interval(self.update_ui, 1)
        Clock.schedule_interval(self.scroll_news, 0.02)
        
        if self.stops:
            self.update_stop_label(self.stops[0]['Nazwa'])

        Window.bind(on_key_down=self._on_keyboard_down)
        
        if SESSION["mode"] == "Pojazd" and GPS_AVAILABLE:
            self._init_gps()

        Clock.schedule_once(self.play_welcome_sequence, 1.5)

    def _apply_scaling(self, *args):
        win_w, win_h = Window.size
        scale = min(win_w / self.base_size[0], win_h / self.base_size[1])
        self.content_box.scale = scale
        self.content_box.pos = (
            (win_w - self.base_size[0] * scale) / 2,
            (win_h - self.base_size[1] * scale) / 2
        )
    
    def _get_direction_text(self, csv_file):
        if self.special_id == "TRAM_WYJAZD":
            return self.stops[-1]['Nazwa'].rsplit(' ', 1)[0] if self.stops else "Wyjazd na linię"

        elif self.special_id == "TRAM_ZJAZD":
            if self.stops:
                last_stop = self.stops[-1]['Nazwa'].upper()
                if "PH" in last_stop or "HUTA" in last_stop: 
                    return "Zajezdnia Nowa Huta"
                if "PT" in last_stop or "PODGÓRZE" in last_stop: 
                    return "Zajezdnia Podgórze"
            return "Zjazd do zajezdni"

        elif self.special_id:
            return SPECIAL_MODES[self.special_id]["label"]

        elif self.stops and self.stops[0].get('Kierunek'):
            return self.stops[0]['Kierunek']
            
        if csv_file:
            return os.path.basename(csv_file).replace('.csv', '').replace('_', ' ')
            
        return "Brak Trasy"
    
    def _on_keyboard_down(self, instance, keyboard, keycode, text, modifiers):
        if 'ctrl' in modifiers:
            if text == 't':
                self.show_route_panel()
                return True
            elif text == 'k':
                self.show_announcements_panel()
                return True
        return True

    def show_route_panel(self):
        view = ModalView(size_hint=(0.8, 0.8), background_color=(0, 0, 0, 0.8))
        layout = BoxLayout(orientation='vertical', padding=20, spacing=10)
        
        layout.add_widget(Label(text="WYBÓR PRZYSTANKU", font_size='30sp', size_hint_y=None, height=50))

        scroll = ScrollView()
        list_layout = BoxLayout(orientation='vertical', size_hint_y=None, spacing=5)
        list_layout.bind(minimum_height=list_layout.setter('height'))

        for i, stop in enumerate(self.stops):
            is_active = (i == self.current_idx)
            btn_color = (0, 0.5, 1, 1) if is_active else (0.2, 0.2, 0.2, 1)
            
            btn = Button(text=f"{i+1}. {stop['Nazwa']}", size_hint_y=None, height=60,
                         background_color=btn_color)
            
            btn.bind(on_release=lambda btn, idx=i: self.set_stop_manually(idx, view))
            list_layout.add_widget(btn)

        scroll.add_widget(list_layout)
        layout.add_widget(scroll)

        nav_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height=80, spacing=10)
        
        prev_btn = Button(text="[ PREV ]", background_color=(0.7, 0.4, 0, 1), bold=True)
        prev_btn.bind(on_release=lambda b: self.set_stop_manually(max(0, self.current_idx - 1), view))
        
        next_btn = Button(text="[ NEXT ]", background_color=(0, 0.6, 0.3, 1), bold=True)
        next_btn.bind(on_release=lambda b: self.set_stop_manually(min(len(self.stops)-1, self.current_idx + 1), view))
        
        nav_layout.add_widget(prev_btn)
        nav_layout.add_widget(next_btn)
        layout.add_widget(nav_layout)

        close_btn = Button(text="ZAMKNIJ", size_hint_y=None, height=50, background_color=(0.7, 0.2, 0.2, 1))
        close_btn.bind(on_release=view.dismiss)
        layout.add_widget(close_btn)
        
        view.add_widget(layout)
        view.open()

    def set_stop_manually(self, idx, view):
        self.current_idx = idx
        stop_data = self.stops[self.current_idx]

        def after_audio():
            self.update_stop_label(stop_data['Nazwa'])

        audio_name = f"{stop_data['Audio']}.mp3"
        self.play_sequence([audio_name], callback=after_audio)

        view.dismiss()

    def show_announcements_panel(self):
        view = ModalView(size_hint=(0.8, 0.8), background_color=(0,0,0,0.8))
        layout = BoxLayout(orientation='vertical', padding=20, spacing=10)
        
        scroll = ScrollView()
        list_layout = BoxLayout(orientation='vertical', size_hint_y=None, spacing=5)
        list_layout.bind(minimum_height=list_layout.setter('height'))
        
        anns_path = os.path.join(BASE_DIR, 'dictionaries', 'anns.txt')

        layout.add_widget(Label(text="WYBÓR KOMUNIKATU", font_size='30sp', size_hint_y=None, height=50))

        if not os.path.exists(anns_path):
            list_layout.add_widget(Label(text="Brak pliku anns.txt", size_hint_y=None, height=60))
        else:
            with open(anns_path, 'r', encoding='utf-8') as f:
                for line in f:
                    if '|' in line:
                        title, filename = line.strip().split('|')
                        
                        btn = Button(
                            text=title, 
                            size_hint_y=None, 
                            height=60, 
                            background_color=(0.2, 0.2, 0.2, 1)
                        )
                        
                        btn.bind(on_release=lambda b, f=filename: self.play_custom_audio(f, view))
                        
                        list_layout.add_widget(btn)

        scroll.add_widget(list_layout)
        layout.add_widget(scroll)
        
        close_btn = Button(text="ZAMKNIJ", size_hint_y=None, height=60, background_color=(0.7, 0.2, 0.2, 1))
        close_btn.bind(on_release=view.dismiss)
        layout.add_widget(close_btn)

        view.add_widget(layout)
        view.open()

    def play_custom_audio(self, filename, view):
        audio_path = os.path.join(BASE_DIR, 'audio', filename)
        if os.path.exists(audio_path):
            sound = SoundLoader.load(audio_path)
            if sound:
                sound.play()
            print(f"Odtwarzam: {audio_path}")
            view.dismiss()
        else:
            print(f"Błąd: Plik {filename} nie istnieje w folderze audio")
        
    # def update_stop_label(self, full_name):
    #     print(f"DEBUG: Próba wyświetlenia przystanku: {full_name}")
    #     clean_name = full_name.rsplit(' ', 1)[0] if ' ' in full_name else full_name.upper()
        
    #     prefix_x = 360
    #     text_start_x = 418
    #     stop_pos_y = 1080 - 184
    #     limit_width = 1187

    #     if not hasattr(self, 'lbl_prefix'):
    #         self.lbl_prefix = Label(text="> ", font_size='80sp', font_name=self.arimo_font,
    #                                color=self.krakow_blue, size_hint=(None, None),
    #                                size=(60, 92), pos=(prefix_x, stop_pos_y),
    #                                halign='left', valign='middle')
    #         self.content_box.add_widget(self.lbl_prefix)

    #     if not hasattr(self, 'stop_container'):
    #         self.stop_container = StencilView(size_hint=(None, None), 
    #                                          size=(limit_width, 92),
    #                                          pos=(text_start_x, stop_pos_y))
            
    #         self.lbl_stop = Label(text=clean_name.upper(), font_size='80sp', 
    #                              font_name=self.arimo_font,
    #                              color=self.krakow_blue, size_hint=(None, None),
    #                              size=(limit_width, 92), 
    #                              pos=(text_start_x, stop_pos_y),
    #                              halign='left', valign='middle',
    #                              text_size=(limit_width, 92))
            
    #         self.stop_container.add_widget(self.lbl_stop)
    #         self.content_box.add_widget(self.stop_container)
    #     else:
    #         self.lbl_stop.text = clean_name.upper()

    #     self.lbl_stop.texture_update()
    #     new_width = self.lbl_stop.texture_size[0]
    #     self.lbl_stop.width = max(new_width, limit_width)
    #     self.should_scroll_stop = new_width > limit_width
        
    #     self.lbl_stop.x = text_start_x

    #     # Dodaj to na samym końcu funkcji update_stop_label
    #     from kivy.uix.button import Button
    #     test_btn = Button(text="KLIKNIJ MNIE", pos=(418, 500), size_hint=(None, None), size=(200, 100))
    #     self.content_box.add_widget(test_btn)

    def update_stop_label(self, full_name):
        print(f"DEBUG: TESTOWA AKTUALIZACJA: {full_name}")
        clean_name = full_name.rsplit(' ', 1)[0] if ' ' in full_name else full_name.upper()
        
        # Usuwamy stare, jeśli istnieją, żeby nie śmiecić przy testach
        if hasattr(self, 'lbl_stop'):
            self.content_box.remove_widget(self.lbl_stop)

        self.lbl_stop = Label(
            text=clean_name.upper(),
            font_size='80sp',
            font_name=self.arimo_font,
            color=(0, 0, 0, 1), # BIAŁY
            size_hint=(None, None),
            size=(1187, 92),
            pos=(418, 1080 - 184),
            halign='left',
            valign='middle',
            text_size=(1187, 92) # KONIECZNE
        )
        
        self.content_box.add_widget(self.lbl_stop)
        print(f"DEBUG: Label dodany do {self.content_box} na pos {self.lbl_stop.pos}")
        
    def load_stops_db(self):
        db_p = os.path.join(BASE_DIR, 'dictionaries', 'stops.csv')
        if os.path.exists(db_p):
            with open(db_p, mode='r', encoding='utf-8') as f:
                reader = csv.DictReader(f, delimiter=';')
                for row in reader:
                    base_name = row['Nazwa'].rsplit(' ', 1)[0]
                    self.stops_db[base_name] = {"lat": float(row['Lat']), "lon": float(row['Lon'])}

    def load_route(self, csv_file):
        self.stops = []
        path = csv_file
        if not path or not os.path.exists(path):
            self.stops = [{'Nazwa': '', 'Audio': '', 'Kierunek': ''}]
            return

        try:
            with open(path, mode='r', encoding='utf-8') as f:
                lines = f.readlines()

            csv_content = []
            for line in lines:
                if line.startswith('#'):
                    if "Route changed:" in line:
                        is_changed = "True" in line
                        SESSION["is_route_changed"] = is_changed
                    continue
                
                csv_content.append(line)

            reader = csv.DictReader(csv_content, delimiter=';')
            for row in reader:
                clean_row = {k.strip(): v.strip() for k, v in row.items() if k is not None}
                clean_row['Extras'] = clean_row.get('Extras', '')
                self.stops.append(clean_row)
                
            if self.stops:
                print(f"Pomyślnie załadowano {len(self.stops)} przystanków.")
                first_stop = self.stops[0].get('Nazwa', '')
                self.update_stop_label(first_stop)
                self.canvas.ask_update()
            else:
                print("Lista przystanków jest pusta po wczytaniu!")
                
        except Exception as e:
            print(f"Błąd ładowania trasy: {e}")
            self.stops = [{'Nazwa': 'BŁĄD STRUKTURY', 'Audio': '', 'Kierunek': ''}]
    
    def get_audio_path(self, filename):
        folders = SEARCH_ORDER.get(SESSION["voice_path"], [SESSION["voice_path"]])
        
        for folder in folders:
            full_path = os.path.join(BASE_DIR, folder, filename)
            if os.path.exists(full_path):
                return full_path
        return None
    
    def play_welcome_sequence(self, dt):
        if not self.stops: return
        
        path_parts = os.path.normpath(SESSION["selected_csv_path"]).split(os.sep)
        line_no = path_parts[-2] if len(path_parts) >= 2 else ""
        
        last_stop_audio = self.stops[-1]['Audio']
        
        seq = [
            "Linia.mp3", 
            f"{line_no}.mp3", 
            "Kierunek.mp3", 
            f"{last_stop_audio}.mp3"
        ]
        self.play_sequence(seq)
    
    def get_stop_audio_files(self, stop_data, is_next=True):
        files = []
        
        if is_next:
            files.append("Następny Przystanek.mp3")
        else:
            voice_mode = SESSION.get("voice_path", "audio")
            if voice_mode in ["audio/new", "audio/maklowicz"]:
                files.append("Przystanek.mp3")

        stop_filename = f"{stop_data['Audio']}.mp3"
        path_to_stop = self.get_audio_path(stop_filename)
        
        if path_to_stop:
            files.append(stop_filename)

            if "(NŻ)" in stop_data['Nazwa'].upper() or "NŻ" in stop_data['Nazwa'].upper():
                files.append("Na Żądanie.mp3")
                
            extras = stop_data['Extras'].lower()
            if "przesiadka_bus" in extras:
                files.append("Możliwość przesiadki na inne linie a.mp3")
            if "przesiadka_tram" in extras:
                files.append("Możliwość przesiadki na inne linie t.mp3")
            if "przesiadka_tram_bus" in extras:
                files.append("Możliwość przesiadki na inne linie t lub a.mp3")
            if "przesiadka_train_tram_bus" in extras:
                files.append("Możliwość przesiadki na pa oraz na inne linie t i a.mp3")
            if "przesiadka_train_bus" in extras:
                files.append("Możliwość przesiadki na pa oraz na inne linie a.mp3")
            if "przesiadka_train_tram" in extras:
                files.append("Możliwość przesiadki na pa oraz na inne linie t.mp3")
            if "main_station" in extras or "dworzec_główny" in extras or "dworzec_glowny" in extras:
                files.append("Możliwość dojścia do Dworca Głównego.mp3")
            if "wrażliwy" in extras or "wrazliwy" in extras:
                files.append("Bądź wrażliwy Ustąp miejsca.mp3")
            if "1_strefa" in extras:
                voice_mode = SESSION.get("voice_path", "audio")
                if voice_mode in ["audio/new"]:
                    files.append("Uwaga Ostatni przystanek w I strefie biletowej.mp3")
            if "2_strefa" in extras:
                voice_mode = SESSION.get("voice_path", "audio")
                if voice_mode in ["audio/new"]:
                    files.append("Uwaga Ostatni przystanek w II strefie biletowej.mp3")
            if "3_strefa" in extras:
                voice_mode = SESSION.get("voice_path", "audio")
                if voice_mode in ["audio/new"]:
                    files.append("Uwaga Ostatni przystanek w III strefie biletowej.mp3")
            if "koniec_trasy" in extras:
                voice_mode = SESSION.get("voice_path", "audio")
                if voice_mode in ["audio"]:
                    files.append("Koniec trasy MPK.mp3")
                if voice_mode in ["audio/new"]:
                    files.append("Koniec trasy.mp3")
                if voice_mode in ["audio/maklowicz"]:
                    files.append("Koniec trasy KMK.mp3")
        else:
            print(f"BŁĄD: Brak pliku nazwy przystanku {stop_filename}. Pomijam resztę sekwencji.")
            if files:
                files = [files[0]]
            
        return files

    def calculate_distance(self, lat1, lon1, lat2, lon2):
        phi1, phi2 = math.radians(lat1), math.radians(lat2)
        dphi = math.radians(lat2 - lat1)
        dlambda = math.radians(lon2 - lon1)
        a = math.sin(dphi/2)**2 + math.cos(phi1)*math.cos(phi2)*math.sin(dlambda/2)**2
        return 6371 * 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))

    def scroll_news(self, dt):
        self.ticker.texture_update()
        self.ticker.width = self.ticker.texture_size[0]
        self.ticker.x -= 6
        if self.ticker.right < 0: self.ticker.x = 1726
        
        if hasattr(self, 'should_scroll_dest') and self.should_scroll_dest:
            self.dest_label.x -= 6
            if self.dest_label.right < 309:
                self.dest_label.x = 309 + 1316
        elif hasattr(self, 'dest_label'):
            self.dest_label.x = 309

        if hasattr(self, 'should_scroll_stop') and self.should_scroll_stop:
            self.lbl_stop.x -= 6
            if self.lbl_stop.right < 428:
                self.lbl_stop.x = 428 + 1197
        elif hasattr(self, 'lbl_stop'):
            self.lbl_stop.x = 418

    def next_ad(self, *args):
        if hasattr(self, '_mute_checker'):
            Clock.unschedule(self._mute_checker)

        if hasattr(self, '_loading_ad') and self._loading_ad:
            self._loading_ad = False 

        if not self.ad_files:
            return

        if self.ads:
            try:
                self.ads.unbind(eos=self.next_ad)
                self.ads.state = 'stop'
                self.ads.unload()
                if hasattr(self, 'video_container'):
                    self.remove_widget(self.video_container)
                else:
                    self.remove_widget(self.ads)
            except Exception as e:
                print(f"Błąd przy usuwaniu reklamy: {e}")
            
            self.ads = None

        self.current_ad_idx = (self.current_ad_idx + 1) % len(self.ad_files)
        
        Clock.schedule_once(self._rebuild_video_widget, 0.5)

    def _rebuild_video_widget(self, dt):
        if not self.ad_files:
            return
        
        self._loading_ad = True

        if hasattr(self, 'video_container') and self.video_container.parent:
            self.content_box.remove_widget(self.video_container)

        self.video_container = StencilView(
            size_hint=(None, None),
            size=(1402, 789),
            pos=(259, self.screen_h - 184 - 789)
        )

        self.ads = Video(
            source=self.ad_files[self.current_ad_idx],
            state='play',
            allow_stretch=True,
            keep_ratio=False,
            size_hint=(None, None),
            size=(1402, 789),
            pos=(259, self.screen_h - 184 - 789)
        )
        
        self.ads.bind(eos=self.next_ad)
        self.video_container.add_widget(self.ads)
        self.content_box.add_widget(self.video_container)

    def update_ui(self, *args):
        now = datetime.now()
        days_pl = ["poniedziałek", "wtorek", "środa", "czwartek", "piątek", "sobota", "niedziela"]
        months_pl = ["stycznia", "lutego", "marca", "kwietnia", "maja", "czerwca", "lipca", "sierpnia", "września", "października", "listopada", "grudnia"]
        self.clock_label.text = now.strftime("%H:%M")
        self.date_label.text = f"{days_pl[now.weekday()]}\n{now.day} {months_pl[now.month-1]}"

    def gps_loop(self, dt):
        if not GPS_AVAILABLE: return
        try:
            report = self.gpsd.next()
            if report['class'] == 'TPV':
                my_lat, my_lon = getattr(report, 'lat', 0.0), getattr(report, 'lon', 0.0)
                if my_lat != 0.0: self.process_gps_logic(my_lat, my_lon)
        except:
            pass

    def process_gps_logic(self, my_lat, my_lon):
        target_idx = self.current_idx if self.is_at_stop else self.current_idx + 1
        if target_idx >= len(self.stops): return

        target_stop = self.stops[target_idx]
        coords = self.stops_db.get(target_stop['Nazwa'].rsplit(' ', 1)[0])
        if not coords: return

        dist = self.calculate_distance(my_lat, my_lon, coords['lat'], coords['lon'])

        if self.is_at_stop and dist > 0.040: 
            self.is_at_stop = False
            if self.current_idx < len(self.stops) - 1:
                next_data = self.stops[self.current_idx + 1]
                self.play_sequence(["Następny Przystanek.mp3", f"{next_data['Audio']}.mp3"], 
                                callback=lambda: self.update_stop_label(next_data['Nazwa']))

        elif not self.is_at_stop and dist < 0.025:
            self.current_idx += 1
            self.is_at_stop = True
            self.play_sequence([f"{self.stops[self.current_idx]['Audio']}.mp3"])
            
    def play_sequence(self, file_list, callback=None, clear_queue=False):
        if clear_queue:
            if self.current_sound:
                self.current_sound.stop()
            self.audio_queue = []

        self.audio_queue.extend(file_list)
        if callback:
            self.audio_queue.append(callback)
            
        if not self.is_audio_playing:
            self.process_queue()
    
    def process_queue(self, *args):
        if not self.audio_queue:
            self.is_audio_playing = False
            return

        self.is_audio_playing = True
        item = self.audio_queue.pop(0)

        if callable(item):
            item()
            self.process_queue()
            return

        full_path = self.get_audio_path(item)
        
        if not full_path:
            print(f"Pominięto dźwięk (brak pliku w żadnej lokalizacji): {item}")
            self.process_queue()
            return

        sound = SoundLoader.load(full_path)
        if sound:
            self.current_sound = sound
            sound.bind(on_stop=self.process_queue)
            sound.play()
        else:
            self.process_queue()

    def on_touch_down(self, touch):
        if SESSION["mode"] == "Dom":
            if self.is_at_stop:
                if self.current_idx < len(self.stops) - 1:
                    self.is_at_stop = False
                    next_stop = self.stops[self.current_idx + 1]
                    
                    files = self.get_stop_audio_files(next_stop, is_next=True)
                    self.play_sequence(files, callback=lambda: self.update_stop_label(next_stop['Nazwa']))
            else:
                self.current_idx += 1
                self.is_at_stop = True
                curr_stop = self.stops[self.current_idx]
                
                files = self.get_stop_audio_files(curr_stop, is_next=False)
                self.play_sequence(files)
        return True
