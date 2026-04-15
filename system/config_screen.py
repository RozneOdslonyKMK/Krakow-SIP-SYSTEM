from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.checkbox import CheckBox
from kivy.uix.spinner import Spinner

class ConfigScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        layout = BoxLayout(orientation='vertical', padding=50, spacing=20)

        layout.add_widget(Label(text="KONFIGURACJA SYSTEMU SIP", font_size='40sp', bold=True))

        monitor_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height=50)
        monitor_layout.add_widget(Label(text="Liczba monitorów:"))
        self.monitor_spinner = Spinner(
            text='1',
            values=('1', '2', '3'),
            size_hint=(None, None),
            size=(100, 50)
        )
        monitor_layout.add_widget(self.monitor_spinner)
        layout.add_widget(monitor_layout)

        led_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height=50)
        led_layout.add_widget(Label(text="Obsługa wyświetlacza LED:"))
        self.led_checkbox = CheckBox(active=False, size_hint_x=None, width=100)
        led_layout.add_widget(self.led_checkbox)
        layout.add_widget(led_layout)

        start_btn = Button(
            text="URUCHOM SYSTEM",
            size_hint_y=None,
            height=80,
            background_color=(0, 0.6, 0.3, 1),
            font_size='25sp'
        )
        start_btn.bind(on_release=self.save_and_start)
        layout.add_widget(start_btn)

        self.add_widget(layout)

    def save_and_start(self, instance):
        SESSION["num_monitors"] = int(self.monitor_spinner.text)
        SESSION["use_led"] = self.led_checkbox.active
        
        self.manager.current = 'route_selection'
