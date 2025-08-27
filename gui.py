from PyQt5.QtWidgets import (
    QApplication,
    QMainWindow,
    QSystemTrayIcon,
    QMenu,
    QStyle,
    QLineEdit,
    QPushButton,
    QVBoxLayout,
    QHBoxLayout,
    QWidget,
    QLabel,
    QSpinBox,
    QGroupBox,
    QFileDialog,
    QTextEdit
)
from PyQt5.QtCore import QTimer
from PyQt5.QtGui import QFont
from pixoo_handler import PixooHandler
from server import ServerWorker
import os
from pathlib import Path


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
        exit_action.triggered.connect(self.cleanup_and_exit)
        self.tray_icon.setContextMenu(self.tray_menu)
        self.tray_icon.activated.connect(self.on_tray_icon_activated)
        self.tray_icon.show()

        # Initialize components
        self.setup_ui()

        # Use singleton PixooHandler
        self.pixoo_handler = PixooHandler()

        # Server worker thread
        self.server_worker = ServerWorker()
        self.server_worker.server_started.connect(self.on_server_started)
        self.server_worker.server_stopped.connect(self.on_server_stopped)
        self.server_worker.server_error.connect(self.on_server_error)

        # Server state
        self.server_running = False

    def setup_ui(self):
        """Setup the user interface"""
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        main_layout = QVBoxLayout(main_widget)

        # Pixoo Control Group
        pixoo_group = QGroupBox("Pixoo Display Control")
        pixoo_layout = QVBoxLayout(pixoo_group)

        # Text input and controls
        text_layout = QHBoxLayout()
        self.text_input = QLineEdit(self)
        self.text_input.setPlaceholderText("Enter message to display...")
        self.update_button = QPushButton('Update Text', self)
        self.update_button.clicked.connect(self.handle_update_text)

        text_layout.addWidget(self.text_input)
        text_layout.addWidget(self.update_button)
        pixoo_layout.addLayout(text_layout)

        # GIF controls
        gif_layout = QHBoxLayout()
        self.save_button = QPushButton('Save SD GIF', self)
        self.save_button.clicked.connect(self.save_gif)
        self.play_button = QPushButton('Play SD GIF', self)
        self.play_button.clicked.connect(self.play_gif)

        gif_layout.addWidget(self.save_button)
        gif_layout.addWidget(self.play_button)
        pixoo_layout.addLayout(gif_layout)

        main_layout.addWidget(pixoo_group)

        # HTTP Server Control Group
        server_group = QGroupBox("HTTP Server Control")
        server_layout = QVBoxLayout(server_group)

        # Directory selection
        dir_layout = QHBoxLayout()
        self.directory_input = QLineEdit(self)
        self.directory_input.setText(str(Path.cwd()))
        self.browse_button = QPushButton('Browse', self)
        self.browse_button.clicked.connect(self.browse_directory)

        dir_layout.addWidget(QLabel("Directory:"))
        dir_layout.addWidget(self.directory_input)
        dir_layout.addWidget(self.browse_button)
        server_layout.addLayout(dir_layout)

        # Server settings
        settings_layout = QHBoxLayout()

        self.port_spinbox = QSpinBox(self)
        self.port_spinbox.setRange(1024, 65535)
        self.port_spinbox.setValue(8000)

        settings_layout.addWidget(QLabel("Port:"))
        settings_layout.addWidget(self.port_spinbox)
        settings_layout.addStretch()
        server_layout.addLayout(settings_layout)

        # Server control buttons
        button_layout = QHBoxLayout()
        self.start_server_button = QPushButton('Start Server', self)
        self.start_server_button.clicked.connect(self.start_server)
        self.stop_server_button = QPushButton('Stop Server', self)
        self.stop_server_button.clicked.connect(self.stop_server)
        self.stop_server_button.setEnabled(False)

        button_layout.addWidget(self.start_server_button)
        button_layout.addWidget(self.stop_server_button)
        button_layout.addStretch()
        server_layout.addLayout(button_layout)

        # Server status display
        self.server_status_label = QLabel("Server Status: Stopped")
        server_layout.addWidget(self.server_status_label)

        main_layout.addWidget(server_group)

        # Log display
        log_group = QGroupBox("Server Log")
        log_layout = QVBoxLayout(log_group)

        self.log_display = QTextEdit(self)
        self.log_display.setMaximumHeight(120)
        self.log_display.setFont(QFont("Courier", 9))
        self.log_display.setReadOnly(True)

        log_layout.addWidget(self.log_display)
        main_layout.addWidget(log_group)

    def browse_directory(self):
        """Open file dialog to select directory"""
        directory = QFileDialog.getExistingDirectory(
            self,
            "Select Directory to Serve",
            self.directory_input.text()
        )
        if directory:
            self.directory_input.setText(directory)

    def start_server(self):
        """Start the HTTP server"""
        if self.server_running:
            self.log_message("Server is already running")
            return

        directory = self.directory_input.text().strip()
        if not directory or not os.path.exists(directory):
            self.log_message("ERROR: Invalid directory")
            return

        port = self.port_spinbox.value()
        self.log_message(f"Starting server on port {port}...")
        self.start_server_button.setEnabled(False)

        # Start server in background thread
        self.server_worker.start_server(directory, port)

    def stop_server(self):
        """Stop the HTTP server"""
        if not self.server_running:
            return

        self.log_message("Stopping server...")
        self.stop_server_button.setEnabled(False)
        self.server_worker.stop_server()

    def on_server_started(self, url):
        """Called when server successfully starts"""
        self.server_running = True
        self.start_server_button.setEnabled(False)
        self.stop_server_button.setEnabled(True)
        self.server_status_label.setText(f"Server Status: Running at {url}")
        self.log_message(f"✓ Server started at {url}")

    def on_server_stopped(self):
        """Called when server successfully stops"""
        self.server_running = False
        self.start_server_button.setEnabled(True)
        self.stop_server_button.setEnabled(False)
        self.server_status_label.setText("Server Status: Stopped")
        self.log_message("✓ Server stopped")

    def on_server_error(self, error_message):
        """Called when server encounters an error"""
        self.start_server_button.setEnabled(True)
        self.stop_server_button.setEnabled(self.server_running)
        self.log_message(f"✗ Server error: {error_message}")

    def log_message(self, message):
        """Add a message to the log display"""
        from datetime import datetime
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.log_display.append(f"[{timestamp}] {message}")
        # Auto-scroll to bottom
        scrollbar = self.log_display.verticalScrollBar()
        scrollbar.setValue(scrollbar.maximum())

    def save_gif(self):
        """Save GIF to Pixoo"""
        try:
            self.pixoo_handler.save_gif_to_pixoo()
            self.log_message("GIF saved to Pixoo")
        except Exception as e:
            self.log_message(f"Error saving GIF: {e}")

    def play_gif(self):
        """Play GIF on Pixoo"""
        try:
            self.pixoo_handler.display_status_gif()
            self.log_message("Playing GIF on Pixoo")
        except Exception as e:
            self.log_message(f"Error playing GIF: {e}")

    def handle_update_text(self):
        """Handle text update button click"""
        message = self.text_input.text()
        if not message:
            message = "Hello Pixoo!"
        try:
            self.pixoo_handler.display_status(status_message=message)
            self.log_message(f"Updated Pixoo: '{message}'")
        except Exception as e:
            self.log_message(f"Error updating Pixoo: {e}")

    def cleanup_and_exit(self):
        """Clean shutdown - stop server before exiting"""
        if self.server_running:
            self.server_worker.stop_server()
        QApplication.quit()

    def closeEvent(self, event):
        """Override close event to hide to tray instead of exit"""
        event.ignore()
        self.hide()

    def on_tray_icon_activated(self, reason):
        """Handle tray icon activation"""
        if reason == QSystemTrayIcon.Trigger:
            self.showNormal()
            self.activateWindow()