#	Handles communication with Pixoo64
from vendor.pixoo_ng import Pixoo

def update_pixoo_display(status, gif_path=None):
    device = Pixoo()

    device.clear()
    device.draw_text(status)

    if gif_path:
        device.draw_image(gif_path)