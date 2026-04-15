from system.imports import *

class StartModeScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        layout = BoxLayout(orientation='vertical', padding=100, spacing=40)
        layout.add_widget(Label(text="WYBIERZ TRYB PRACY", font_size='50sp', bold=True))
        
        btn_dom = Button(text="DOM\n(Ręczne klikanie)", halign='center', font_size='30sp', background_color=(0, 0.5, 0, 1))
        btn_poj = Button(text="POJAZD\n(Automatyczny GPS)", halign='center', font_size='30sp', background_color=(0.7, 0, 0, 1))
        
        btn_dom.bind(on_release=lambda x: self.set_mode("Dom"))
        
        if sys.platform != "win32":
            btn_poj.bind(on_release=lambda x: self.set_mode("Pojazd"))
        else:
            btn_poj.disabled = True
            btn_poj.text = "POJAZD\n(GPS niedostępny na Windows)"
            btn_poj.background_color = (0.3, 0.3, 0.3, 1)
            
        layout.add_widget(btn_dom)
        layout.add_widget(btn_poj)
        self.add_widget(layout)

    def set_mode(self, mode):
        SESSION["mode"] = mode
        self.manager.current = 'voice_select'
