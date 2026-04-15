from system.imports import *

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

    def start(self, *args):
        SESSION["news_text"] = self.ti.text
        csv_name = os.path.basename(SESSION["selected_csv_path"])
        self.manager.get_screen('sip').setup_sip(csv_name)
        self.manager.current = 'sip'
