import sys
from kivy.config import Config

mode = sys.argv[1] if len(sys.argv) > 1 else "driver"

if mode == "sip":
    Config.set('graphics', 'width', '1920')
    Config.set('graphics', 'height', '1080')
    Config.set('graphics', 'fullscreen', '0')
    # Config.set('graphics', 'borderless', '1')
    Config.set('graphics', 'position', 'custom')
    Config.set('graphics', 'top', '0')
    Config.set('graphics', 'left', '1024') 
else:
    Config.set('graphics', 'width', '1024')
    Config.set('graphics', 'height', '602')

from system.imports import *
from system.top_screen import MainSIPLayout
from system.driver_panel import DriverPanel

class SipScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.current_idx = 0
        self.last_synced_path = None
        self.is_at_stop = True
        self.stops = []
        Clock.schedule_interval(self.check_sync, 1.0)

    def check_sync(self, dt):
        if mode != "sip": return
        
        sync_file = "sync.json"
        if not os.path.exists(sync_file): return

        try:
            with open(sync_file, "r", encoding="utf-8") as f:
                content = f.read().strip()
                if not content: return
                data = json.loads(content)
                
            path_from_json = data.get("selected_csv_path")
            if path_from_json and path_from_json != self.last_synced_path:
                print(f"SIP: Wykryto zmianę trasy na: {path_from_json}")
                self.last_synced_path = path_from_json
                self.setup_sip(path_from_json)
                return 

            source = data.get("last_update_source")
            new_idx = data.get("current_stop_index")

            if source == "driver" and new_idx is not None:
                if new_idx != self.current_idx:
                    print(f"SIP: Kierowca wymusił przeskok na przystanek {new_idx}")
                    
                    self.jump_to_stop(new_idx)
                    
                    self.update_sync_source_to_sip()

        except Exception as e:
            print(f"DEBUG SIP ERROR: {e}")
    
    def jump_to_stop(self, index):
        if self.stops and 0 <= index < len(self.stops):
            self.current_idx = index
            curr_stop = self.stops[index]
            
            if hasattr(self, 'sip_content'):
                self.sip_content.update_stop_label(curr_stop['Nazwa'])
                
                self.sip_content.current_idx = index
                
                self.sip_content.canvas.ask_update()
            
            files = self.sip_content.get_stop_audio_files(curr_stop, is_next=False)
            self.sip_content.play_sequence(files)
            
    def update_sync_source_to_sip(self):
        try:
            with open("sync.json", "r", encoding="utf-8") as f:
                data = json.load(f)
            
            data["last_update_source"] = "sip" 
            
            with open("sync.json", "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=4)
            print("DEBUG: Flaga źródła zresetowana na 'sip'")
        except Exception as e:
            print(f"Błąd resetu flagi: {e}")

    def setup_sip(self, csv_file):
        self.clear_widgets()
        self.sip_content = MainSIPLayout(csv_file)
        self.add_widget(self.sip_content)
        self.sip_content.load_route(csv_file)
        self.stops = self.sip_content.stops

        if SESSION.get("mode") == "sip":
            SESSION["sip_launched"] == True
            curr_stop = self.stops[0]
            files = self.get_stop_audio_files(curr_stop, is_next=False)
            self.play_sequence(files)

    def on_enter(self):
        if hasattr(self, 'sip_content') and self.sip_content.stops:
            start_stop = self.sip_content.stops[0]
            self.sip_content.update_stop_label(start_stop['Nazwa'])
            if start_stop.get('Audio'):
                Clock.schedule_once(lambda dt: self.sip_content.play_sequence([f"{start_stop['Audio']}.mp3"]), 1.0)

class SIPApp(App):
    icon = 'app-icon.png'
    
    def build(self):
        Window.show_cursor = False
        Window.bind(on_key_down=self._on_keyboard_down)
        Window.bind(on_request_close=self.on_request_close)
        
        self.sm = ScreenManager(transition=FadeTransition())
        
        self.driver_panel_screen = Screen(name='driver')
        self.driver_panel = DriverPanel()
        self.driver_panel_screen.add_widget(self.driver_panel)
        
        self.sip_screen = SipScreen(name='sip')

        self.sm.add_widget(self.driver_panel_screen)
        self.sm.add_widget(self.sip_screen)

        if mode == "sip":
            self.sm.current = 'sip'
            self.title = "Ekran podsufitowy SIP"
            self.icon = 'app-icon.png'
        else:
            self.sm.current = 'driver'
            self.title = "Panel prowadzącego"
            self.icon = 'app-icon.png'

        return self.sm
    
    def _on_keyboard_down(self, instance, keyboard, keycode, text, modifiers):
        if 'ctrl' in modifiers:
            if text == 'q':
                Window.show_cursor = not Window.show_cursor
                return True
            elif text == 'm':
                self.sm.current = 'sip' if self.sm.current == 'driver' else 'driver'
                return True
            elif text == 'p':
                self.toggle_fullscreen()
                return True
        return False
    
    def toggle_fullscreen(self):
        if Window.fullscreen in (True, 'auto'):
            Window.fullscreen = False
            Window.show_cursor = True 
        else:
            Window.fullscreen = 'auto'
            Window.show_cursor = False

    def on_request_close(self, *args):
        if hasattr(self, 'driver_panel'):
            self.driver_panel.init_shutdown()
        return True
    
    def on_stop(self): 
        Window.show_cursor = True

if __name__ == '__main__':
    SIPApp().run()
    