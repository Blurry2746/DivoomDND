from PyQt5.QtWidgets import (
    QApplication,
    QMainWindow,
    QSystemTrayIcon,
    QMenu,
    QStyle,
    QLineEdit,
    QPushButton,
    QVBoxLayout,
    QWidget
)
from PyQt5.QtCore import QTimer
from pixoo_handler import PixooHandler  # Singleton PixooHandler

class DivoomDNDGUI(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("DivoomDND Status Manager")
        self.setMinimumSize(400, 300)
        self.resize(600, 400)

        # Setup system tray icon
        default_icon = QApplication.style().standardIcon(QStyle.SP_ComputerIcon)
        self.tray_icon = QSystemTrayIcon(default_icon, self)
        self.tray_icon.setToolTip("DivoomDND")

        self.tray_menu = QMenu(self)
        show_action = self.tray_menu.addAction("Show")
        show_action.triggered.connect(self.show)
        exit_action = self.tray_menu.addAction("Exit")
        exit_action.triggered.connect(QApplication.quit)
        self.tray_icon.setContextMenu(self.tray_menu)
        self.tray_icon.activated.connect(self.on_tray_icon_activated)
        self.tray_icon.show()

        # Add text input and button
        self.text_input = QLineEdit(self)
        self.update_button = QPushButton('Update Text', self)
        self.update_button.clicked.connect(self.handle_update_text)

        # Add to layout
        layout = QVBoxLayout()
        layout.addWidget(self.text_input)
        layout.addWidget(self.update_button)

        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

        # Use singleton PixooHandler
        self.pixoo_handler = PixooHandler()

        # Start periodic updates
        self.start_timer()

    def update_status_display(self):
        self.pixoo_handler.display_status("TEST message")

    def handle_update_text(self):
        message = self.text_input.text()
        self.pixoo_handler.display_status(message)

    def start_timer(self):
        self.timer = QTimer(self)
        self.timer.setInterval(1000)
        self.timer.timeout.connect(self.update_status_display)
        self.timer.start()

    def closeEvent(self, event):
        event.ignore()
        self.hide()

    def on_tray_icon_activated(self, reason):
        if reason == QSystemTrayIcon.Trigger:
            self.showNormal()
            self.activateWindow()
