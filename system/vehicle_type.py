from system.imports import *

class TypeSelectScreen(Screen):
    def update_types(self, op):
        self.clear_widgets()
        layout = BoxLayout(orientation='vertical', padding=50, spacing=20)
        layout.add_widget(Label(text=f"{op} - RODZAJ POJAZDU", font_size='35sp', size_hint_y=0.2))
        
        for t in OPERATORS[op]:
            btn = Button(text=t, font_size='30sp', background_color=(0, 0.23, 0.45, 1))
            btn.bind(on_release=lambda x, typ=t: self.select_type(typ))
            layout.add_widget(btn)

        back = Button(text="POWRÓT", size_hint_y=0.2, background_color=(0.5, 0.5, 0.5, 1))
        back.bind(on_release=lambda x: setattr(self.manager, 'current', 'operator_select'))
        layout.add_widget(back)
        self.add_widget(layout)

    def select_type(self, typ):
        SESSION["type"] = typ.lower()
        self.manager.get_screen('lines').load_lines()
        self.manager.current = 'lines'
