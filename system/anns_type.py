from system.imports import *

class VoiceSelectScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        layout = BoxLayout(orientation='vertical', padding=50, spacing=20)
        layout.add_widget(Label(text="WYBIERZ TYP ZAPOWIEDZI", font_size='40sp'))
        
        for name, path in VOICE_TYPES.items():
            btn = Button(text=name, font_size='30sp', background_color=(0.1, 0.4, 0.6, 1))
            btn.bind(on_release=lambda x, p=path: self.select_voice(p))
            layout.add_widget(btn)
        self.add_widget(layout)

    def select_voice(self, path):
        SESSION["voice_path"] = path
        self.manager.current = 'operator_select'
