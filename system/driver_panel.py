from system.imports import *

class DriverPanel(Screen):
    def on_route_select(self, route_data):
        self.manager.get_screen('sip_main').load_new_route(route_data)
        
        if SESSION["use_led"]:
            led_controller.update_led(route_data['line'], route_data['direction'])
