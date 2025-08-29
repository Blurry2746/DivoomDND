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
    QTextEdit,
    QListWidget,
    QListWidgetItem,
    QSplitter,
    QTabWidget,
    QComboBox
)
from PyQt5.QtCore import QTimer, Qt
from PyQt5.QtGui import QFont
from pixoo_handler import PixooHandler
from server import ServerWorker
from config import get_settings, save_settings
from gif_manager import get_gif_manager
import os
from pathlib import Path



class DivoomDNDGUI(QMainWindow):
    def __init__(self):
        super().__init__()

        # Get settings instance
        self.settings = get_settings()

        self.setWindowTitle("DivoomDND Status Manager")

        # Restore window size and position
        width = self.settings.get('gui.window_width', 600)
        height = self.settings.get('gui.window_height', 400)
        self.setMinimumSize(400, 300)
        self.resize(width, height)

        # Restore window position if saved
        if self.settings.get('gui.remember_window_position', True):
            x = self.settings.get('gui.window_x')
            y = self.settings.get('gui.window_y')
            if x is not None and y is not None:
                self.move(x, y)

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



        # Use singleton PixooHandler and GIF manager
        self.pixoo_handler = PixooHandler()
        self.gif_manager = get_gif_manager()

        # Initialize components
        self.setup_ui()

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

        # Upload GIF section
        upload_layout = QVBoxLayout()
        self.gif_url_input = QLineEdit(self)
        self.gif_url_input.setPlaceholderText("GIF URL (e.g., http://localhost:8000/mygif.gif)")
        self.gif_path_input = QLineEdit(self)
        self.gif_path_input.setPlaceholderText("Pixoo path (e.g., test/mygif.gif)")

        upload_input_layout = QHBoxLayout()
        upload_input_layout.addWidget(QLabel("URL:"))
        upload_input_layout.addWidget(self.gif_url_input)
        upload_layout.addLayout(upload_input_layout)

        path_input_layout = QHBoxLayout()
        path_input_layout.addWidget(QLabel("Path:"))
        path_input_layout.addWidget(self.gif_path_input)
        upload_layout.addLayout(path_input_layout)

        self.save_button = QPushButton('Upload GIF to Pixoo', self)
        self.save_button.clicked.connect(self.save_gif)
        upload_layout.addWidget(self.save_button)

        # Play GIF section
        play_layout = QVBoxLayout()
        self.gif_selector = QComboBox(self)
        self.gif_selector.setEditable(True)
        self.gif_selector.setPlaceholderText("Select or enter Pixoo path...")
        play_layout.addWidget(QLabel("Play GIF:"))
        play_layout.addWidget(self.gif_selector)

        self.play_button = QPushButton('Play Selected GIF', self)
        self.play_button.clicked.connect(self.play_gif)
        play_layout.addWidget(self.play_button)

        # Add both sections to main layout
        gif_layout.addLayout(upload_layout)
        gif_layout.addLayout(play_layout)
        pixoo_layout.addLayout(gif_layout)

        # GIF tracking list
        self.gif_list = QListWidget(self)
        self.gif_list.setMaximumHeight(100)
        pixoo_layout.addWidget(QLabel("Tracked GIFs:"))
        pixoo_layout.addWidget(self.gif_list)

        # Refresh GIF list initially
        self.refresh_gif_list()

        main_layout.addWidget(pixoo_group)

        # HTTP Server Control Group
        server_group = QGroupBox("HTTP Server Control")
        server_layout = QVBoxLayout(server_group)

        # Directory selection
        dir_layout = QHBoxLayout()
        self.directory_input = QLineEdit(self)
        # Load saved directory or use current working directory
        saved_directory = self.settings.get('server.directory', str(Path.cwd()))
        self.directory_input.setText(saved_directory)
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
        # Load saved port or use default
        saved_port = self.settings.get('server.port', 8000)
        self.port_spinbox.setValue(saved_port)

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
            # Save the selected directory
            self.settings.set('server.directory', directory)
            save_settings()

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

        # Save server settings
        self.settings.update_section('server', {
            'directory': directory,
            'port': port
        })
        save_settings()

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

    def refresh_gif_list(self):
        """Refresh the list of tracked GIFs"""
        self.gif_list.clear()
        self.gif_selector.clear()

        tracked_gifs = self.gif_manager.get_all_gifs()

        if not tracked_gifs:
            item = QListWidgetItem("No GIFs uploaded yet")
            item.setFlags(item.flags() & ~Qt.ItemIsSelectable)
            self.gif_list.addItem(item)
            return

        # Populate list widget
        for gif in tracked_gifs:
            status_icon = "✓" if gif.local_exists else "✗"
            display_text = f"{status_icon} {gif.local_filename} -> {gif.pixoo_path}"

            item = QListWidgetItem(display_text)
            if not gif.local_exists:
                item.setForeground(Qt.red)
            self.gif_list.addItem(item)

        # Populate combo box
        for gif in tracked_gifs:
            self.gif_selector.addItem(gif.pixoo_path)

    def save_gif(self):
        """Upload GIF to Pixoo and track it"""
        gif_url = self.gif_url_input.text().strip()
        pixoo_path = self.gif_path_input.text().strip()

        if not gif_url:
            self.log_message("ERROR: Please enter a GIF URL")
            return

        if not pixoo_path:
            # Auto-generate path from URL
            filename = os.path.basename(gif_url.split('?')[0])  # Remove query params
            if not filename.endswith('.gif'):
                filename += '.gif'
            pixoo_path = f"uploaded/{filename}"
            self.gif_path_input.setText(pixoo_path)

        try:
            success = self.pixoo_handler.save_gif_to_pixoo(gif_url, pixoo_path)
            if success:
                self.log_message(f"✓ Uploaded GIF: {gif_url} -> {pixoo_path}")
                self.refresh_gif_list()
                # Clear inputs
                self.gif_url_input.clear()
                self.gif_path_input.clear()
            else:
                self.log_message("✗ Failed to upload GIF")
        except Exception as e:
            self.log_message(f"✗ Error uploading GIF: {e}")

    def play_gif(self):
        """Play selected GIF on Pixoo"""
        pixoo_path = self.gif_selector.currentText().strip()

        if not pixoo_path:
            self.log_message("ERROR: Please select or enter a Pixoo path")
            return

        try:
            success = self.pixoo_handler.display_status_gif(pixoo_path)
            if success:
                self.log_message(f"✓ Playing GIF: {pixoo_path}")
            else:
                self.log_message("✗ Failed to play GIF")
        except Exception as e:
            self.log_message(f"✗ Error playing GIF: {e}")

    def handle_update_text(self):
        """Handle text update button click"""
        message = self.text_input.text()
        if not message:
            message = self.settings.get('pixoo.default_message', 'Hello Pixoo!')
        try:
            self.pixoo_handler.display_status(status_message=message)
            self.log_message(f"Updated Pixoo: '{message}'")
        except Exception as e:
            self.log_message(f"Error updating Pixoo: {e}")

    def save_window_state(self):
        """Save current window position and size"""
        if self.settings.get('gui.remember_window_position', True):
            self.settings.update_section('gui', {
                'window_width': self.width(),
                'window_height': self.height(),
                'window_x': self.x(),
                'window_y': self.y()
            })
            save_settings()

    def cleanup_and_exit(self):
        """Clean shutdown - stop server before exiting"""
        # Save window state
        self.save_window_state()

        if self.server_running:
            self.server_worker.stop_server()
        QApplication.quit()

    def closeEvent(self, event):
        """Override close event to hide to tray instead of exit"""
        # Save window state when hiding
        self.save_window_state()
        event.ignore()
        self.hide()

    def on_tray_icon_activated(self, reason):
        """Handle tray icon activation"""
        if reason == QSystemTrayIcon.Trigger:
            self.showNormal()
            self.activateWindow()