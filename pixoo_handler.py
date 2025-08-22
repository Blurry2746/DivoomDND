from hax.pixoo_ng import Pixoo
from hax.pixoo_ng.config import PixooConfig
from hax.pixoo_ng.simulator import SimulatorConfig
from hax.pixoo_ng.exceptions import NoPixooDevicesFound



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

        try:
            pixoo_config = PixooConfig()
        except NoPixooDevicesFound:
            pixoo_config = PixooConfig(address="simulated", size=64)
            self.simulator_mode = True

        self.pixoo = Pixoo(pixoo_config,True,self.simulator_mode,SimulatorConfig(8))
        self.initialized = True

    def is_simulator(self):
        return self.simulator_mode

    def display_status(self, status_text):
        if not self.pixoo:

            return

        try:
            self.pixoo.draw_text(status_text)
            self.pixoo.push()
        except Exception as e:
            print(f"Failed to display status: {e}")
