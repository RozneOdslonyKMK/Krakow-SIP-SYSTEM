from system.imports import *

class RouteSelectScreen(Screen):
    def update_routes(self, line_no, files, line_path):
        self.clear_widgets()
        self.line_path = line_path
        layout = BoxLayout(orientation='vertical', padding=20, spacing=10)
        layout.add_widget(Label(text=f"LINIA {line_no} - WYBIERZ TRASĘ", font_size='30sp', size_hint_y=0.1))
        
        grid = GridLayout(cols=1, spacing=10)
        for f in files:
            name = f.replace('.csv', '').replace('_', ' ')
            btn = Button(text=name, font_size='22sp', background_color=(0, 0.4, 0.8, 1))
            btn.bind(on_release=lambda x, f_name=f: self.set_route(f_name))
            grid.add_widget(btn)
        
        layout.add_widget(grid)
        
        opt_box = BoxLayout(size_hint_y=0.2, spacing=10)
        self.change_btn = Button(text="ZMIANA TRASY: OFF")
        self.change_btn.bind(on_release=self.toggle_change)
        opt_box.add_widget(self.change_btn)
        
        back = Button(text="POWRÓT", background_color=(0.5, 0.5, 0.5, 1))
        back.bind(on_release=lambda x: setattr(self.manager, 'current', 'lines'))
        opt_box.add_widget(back)
        
        layout.add_widget(opt_box)
        self.add_widget(layout)

    def toggle_change(self, btn):
        SESSION["is_route_changed"] = not SESSION["is_route_changed"]
        btn.text = f"ZMIANA TRASY: {'ON' if SESSION['is_route_changed'] else 'OFF'}"

    def set_route(self, file_name):
        SESSION["selected_csv_path"] = os.path.join(self.line_path, file_name)
        self.manager.current = 'news_editor'
