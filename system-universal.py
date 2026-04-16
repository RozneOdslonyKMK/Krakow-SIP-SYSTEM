from system.imports import *
from system.anns_type import VoiceSelectScreen
from system.line import LineSelectScreen
from system.news_editor import NewsEditorScreen
from system.operator_type import OperatorSelectScreen
from system.route import RouteSelectScreen
from system.top_screen import MainSIPLayout
from system.vehicle_type import TypeSelectScreen
from system.work_mode import StartModeScreen

class SipScreen(Screen):
    def setup_sip(self, csv_file):
        self.clear_widgets()
        self.sip_layout = MainSIPLayout(csv_file)
        self.add_widget(self.sip_layout)

    def on_enter(self):
        if hasattr(self, 'sip_layout'):
            start_stop = self.sip_layout.stops[0]
            self.sip_layout.update_stop_label(start_stop['Nazwa'])
            Clock.schedule_once(lambda dt: self.sip_layout.play_sequence([f"{start_stop['Audio']}.mp3"]), 1.0)

class SIPApp(App):
    def build(self):
        Window.show_cursor = False
        Window.bind(on_key_down=self._on_keyboard_down)
        sm = ScreenManager(transition=FadeTransition())
        sm.add_widget(StartModeScreen(name='start_mode'))
        sm.add_widget(VoiceSelectScreen(name='voice_select'))
        sm.add_widget(OperatorSelectScreen(name='operator_select'))
        sm.add_widget(TypeSelectScreen(name='type_select'))
        sm.add_widget(LineSelectScreen(name='lines'))
        sm.add_widget(RouteSelectScreen(name='routes'))
        sm.add_widget(NewsEditorScreen(name='news_editor'))
        sm.add_widget(SipScreen(name='sip'))
        return sm
    
    def _on_keyboard_down(self, instance, key, scancode, codepoint, modifiers):
        if 'ctrl' in modifiers and (key == 113):
            Window.show_cursor = not Window.show_cursor
            return True
        
        return False
    
    def on_stop(self): 
        Window.show_cursor = True

if __name__ == '__main__':
    SIPApp().run()
