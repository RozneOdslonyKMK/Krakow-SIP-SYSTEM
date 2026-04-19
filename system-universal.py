import sys
from kivy.config import Config

mode = sys.argv[1] if len(sys.argv) > 1 else "driver"

if mode == "sip":
    Config.set('graphics', 'width', '1920')
    Config.set('graphics', 'height', '1080')
    Config.set('graphics', 'fullscreen', '0')
    Config.set('graphics', 'borderless', '1')
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
        self.last_synced_path = None
        Clock.schedule_interval(self.check_sync, 1.0)

    def check_sync(self, dt):
        if mode != "sip": return
        
        sync_file = "sync.json"
        if not os.path.exists(sync_file): return

        try:
            with open(sync_file, "r") as f:
                content = f.read().strip()
                if not content: return
                data = json.loads(content)
                
                path_from_json = data.get("selected_csv_path")
                    
                if path_from_json and path_from_json != self.last_synced_path:
                    self.last_synced_path = path_from_json
                    
                    full_path = path_from_json
                    if not os.path.isabs(full_path):
                        base_dir = os.path.dirname(os.path.abspath(__file__))
                        full_path = os.path.join(base_dir, full_path)
                    
                    print(f"SIP ładuje trasę: {full_path}")
                    
                    self.setup_sip(full_path)
                    
        except (json.JSONDecodeError, OSError):
            pass

    def setup_sip(self, csv_file):
        self.clear_widgets()
        self.sip_layout = MainSIPLayout(csv_file)
        self.add_widget(self.sip_layout)

    def on_enter(self):
        if hasattr(self, 'sip_layout') and self.sip_layout.stops:
            start_stop = self.sip_layout.stops[0]
            self.sip_layout.update_stop_label(start_stop['Nazwa'])
            if start_stop.get('Audio'):
                Clock.schedule_once(lambda dt: self.sip_layout.play_sequence([f"{start_stop['Audio']}.mp3"]), 1.0)

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
    
    def _on_keyboard_down(self, instance, key, scancode, codepoint, modifiers):
        if 'ctrl' in modifiers:
            if key == 113:
                Window.show_cursor = not Window.show_cursor
                return True
            if key == 109:
                self.sm.current = 'sip' if self.sm.current == 'driver' else 'driver'
                return True
        return False
    
    def on_request_close(self, *args):
        if hasattr(self, 'driver_panel'):
            self.driver_panel.init_shutdown()
        return True
    
    def on_stop(self): 
        Window.show_cursor = True

if __name__ == '__main__':
    SIPApp().run()