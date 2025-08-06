#	PyQt-based system tray app for status control and settings
from PyQt5 import QtWidgets, QtGui, QtCore
from config import load_config, save_config
from priority_manager import get_current_status
from pixoo_handler import update_pixoo_display

class SystemTrayApp(QtWidgets.QSystemTrayIcon):
    def __init__(self, app, icon, parent=None):
        super().__init__(icon, parent)
        self.app = app
        self.setToolTip("Pixoo64 App")
        self.config = load_config()

        # Menu
        menu = QtWidgets.QMenu(parent)
        mh = menu.addAction("Set Manual High Priority")
        mh.triggered.connect(self.set_manual_high)
        ml = menu.addAction("Set Manual Low Priority")
        ml.triggered.connect(self.set_manual_low)
        quit_action = menu.addAction("Quit")
        quit_action.triggered.connect(app.quit)
        self.setContextMenu(menu)

        # Status window
        self.status_window = QtWidgets.QWidget()
        self.status_window.setWindowTitle("Pixoo64 Status")
        layout = QtWidgets.QVBoxLayout()

        self.status_label = QtWidgets.QLabel("Current Status: None")
        layout.addWidget(self.status_label)

        self.gif_label = QtWidgets.QLabel()
        self.movie = QtGui.QMovie("status.gif")  # Replace with actual path
        self.gif_label.setMovie(self.movie)
        self.movie.start()
        layout.addWidget(self.gif_label)

        self.status_window.setLayout(layout)
        self.status_window.show()

        # Timer for updates
        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self.update_status_display)
        self.timer.start(5000)

    def set_manual_high(self):
        self.config['manual_priority'] = "highest"
        save_config(self.config)

    def set_manual_low(self):
        self.config['manual_priority'] = "lowest"
        save_config(self.config)

    def update_status_display(self):
        status = get_current_status()
        self.status_label.setText(f"Current Status: {status}")
        update_pixoo_display(status, "status.gif")
