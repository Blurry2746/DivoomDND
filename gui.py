from PyQt5.QtWidgets import (
    QApplication,
    QMainWindow,
    QSystemTrayIcon,
    QMenu,
    QStyle,
    QMessageBox
)
from PyQt5.QtCore import QTimer


class DivoomDNDGUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setMinimumSize(400, 300)
        self.resize(600, 400)
        self.setWindowTitle("DivoomDND Status Manager")
        # Setup system tray icon using a default system icon
        default_icon = QApplication.style().standardIcon(QStyle.SP_ComputerIcon)
        self.tray_icon = QSystemTrayIcon(default_icon, self)
        self.tray_icon.setToolTip("DivoomDND")

        # Create tray menu
        self.tray_menu = QMenu(self)
        self.tray_icon.activated.connect(self.on_tray_icon_activated)
        exit_action = self.tray_menu.addAction("Exit")
        exit_action.triggered.connect(QApplication.quit)
        show_action = self.tray_menu.addAction("Show")
        show_action.triggered.connect(self.show)
        self.tray_icon.setContextMenu(self.tray_menu)
        self.tray_icon.show()

        # Start the periodic update timer
        self.start_timer()

    def update_status_display(self):
        """
        This method should contain the logic to update the Pixoo display
        based on current status, priority, etc.
        """
        # TODO: Add your display update logic here

    def start_timer(self):
        """
        Starts a QTimer that calls update_status_display every 5 seconds.
        """
        self.timer = QTimer(self)
        self.timer.setInterval(5000)  # 5 seconds
        self.timer.timeout.connect(self.update_status_display)
        self.timer.start()

    def closeEvent(self, event):
        """
        Override the window close event to hide the window instead of exiting the app.
        """
        event.ignore()
        self.hide()

    def on_tray_icon_activated(self, reason):
        """
        Handle tray icon activation (clicks).
        """
        if reason == QSystemTrayIcon.Trigger:  # Single click
            self.showNormal()
            self.activateWindow()
        elif reason == QSystemTrayIcon.DoubleClick:  # Optional: handle double click separately
            self.showNormal()
            self.activateWindow()