#	Handles communication with Pixoo64
from vendor.pixoo_ng import Pixoo


class PixooHandler:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(PixooHandler, cls).__new__(cls)
        return cls._instance

    def __init__(self, *args, **kwargs):
        if getattr(self, '_initialized', False):
            return  # Prevent reinitialization

        # Instantiate Pixoo only once
        self.pixoo = Pixoo(*args, **kwargs)

        # Optional: initialize other state variables
        self._initialized = True

    def display_status(self, status_text):
        """
        Display a status message on the Pixoo device.
        """
        self.pixoo.draw_text(status_text)
        self.pixoo.push()

    def display_gif(self, gif_path):
        """
        Display a GIF on the Pixoo device.
        """
        self.pixoo.draw_gif(gif_path)
        self.pixoo.push()

    def clear_display(self):
        """
        Clear the Pixoo display.
        """
        self.pixoo.clear()
        self.pixoo.push()
