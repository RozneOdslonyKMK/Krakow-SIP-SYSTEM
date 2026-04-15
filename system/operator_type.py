from system.imports import *

class OperatorSelectScreen(Screen):
    def on_enter(self):
        self.clear_widgets()
        layout = BoxLayout(orientation='vertical', padding=50, spacing=20)
        layout.add_widget(Label(text="WYBIERZ OPERATORA", font_size='40sp', size_hint_y=0.2))
        
        grid = GridLayout(cols=2, spacing=20)
        for op in OPERATORS.keys():
            btn = Button(text=op, font_size='25sp', background_color=(0, 0.23, 0.45, 1))
            btn.bind(on_release=lambda x, o=op: self.select_operator(o))
            grid.add_widget(btn)
        layout.add_widget(grid)

        back = Button(text="POWRÓT", size_hint_y=0.2, background_color=(0.5, 0.5, 0.5, 1))
        back.bind(on_release=lambda x: setattr(self.manager, 'current', 'start_mode'))
        layout.add_widget(back)
        self.add_widget(layout)

    def select_operator(self, op):
        SESSION["operator"] = op
        self.manager.get_screen('type_select').update_types(op)
        self.manager.current = 'type_select'
