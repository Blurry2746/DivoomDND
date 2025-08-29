from hax.pixoo_ng import Pixoo
from hax.pixoo_ng.config import PixooConfig
from hax.pixoo_ng.simulator import SimulatorConfig
from hax.pixoo_ng.exceptions import NoPixooDevicesFound
from gif_manager import get_gif_manager, track_uploaded_gif


class PixooHandler:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        if hasattr(self, 'initialized'):
            return
        self.simulator_mode = False
        self.pixoo = None
        self.gif_manager = get_gif_manager()  # Add GIF manager

        try:
            pixoo_config = PixooConfig()
            self.pixoo = Pixoo(pixoo_config, True, self.simulator_mode, SimulatorConfig(8))
        except NoPixooDevicesFound:
            # Fall back to simulator mode
            pixoo_config = PixooConfig(address="simulated", size=64)
            self.simulator_mode = True
            self.pixoo = Pixoo(pixoo_config, True, self.simulator_mode, SimulatorConfig(8))
        except Exception as e:
            print(f"Failed to initialize Pixoo: {e}")

        self.initialized = True

    def is_simulator(self):
        return self.simulator_mode

    def display_status(self, status=None, status_message='Test'):
        if not self.pixoo:
            print("Pixoo not initialized")
            return
        try:
            self.pixoo.clear()
            self.pixoo.draw_text(status_message)
            self.pixoo.push()
        except Exception as e:
            print(f"Failed to display status: {e}")

    def display_status_gif(self):
        if not self.pixoo:
            print("Pixoo not initialized")
            return
        try:
            self.pixoo.play_pixoo_gif(0, 'test/phone2.gif')
        except Exception as e:
            print(f"Failed to play GIF: {e}")

    def save_gif_to_pixoo(self, url="http://localhost:8000/test.gif", local_name="test/saved_gif.gif"):
        if not self.pixoo:
            print("Pixoo not initialized")
            return
        try:
            # Note: The original method signature seems incorrect
            # This is a placeholder implementation
            self.pixoo.save_gif_to_pixoo(url, local_name)
        except Exception as e:
            print(f"Failed to save GIF: {e}")