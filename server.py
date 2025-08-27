import os
import socket
import threading
import logging
from http.server import HTTPServer, SimpleHTTPRequestHandler
from pathlib import Path
import signal
import sys
from contextlib import contextmanager
from PyQt5.QtCore import QThread, pyqtSignal

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class SecureHTTPRequestHandler(SimpleHTTPRequestHandler):
    """Secure handler that restricts file serving to a specific directory"""

    def __init__(self, *args, directory=None, **kwargs):
        # Use pathlib for better path handling
        self.base_directory = Path(directory).resolve() if directory else Path.cwd()
        super().__init__(*args, directory=str(self.base_directory), **kwargs)

    def translate_path(self, path):
        """Translate URL path to filesystem path with directory traversal protection"""
        try:
            translated_path = super().translate_path(path)
            full_path = Path(translated_path).resolve()

            # Prevent directory traversal by checking if path is within base directory
            if not str(full_path).startswith(str(self.base_directory)):
                logger.warning(f"Directory traversal attempt blocked: {path}")
                return str(self.base_directory)
            return str(full_path)
        except (OSError, ValueError) as e:
            logger.error(f"Path translation error for {path}: {e}")
            return str(self.base_directory)

    def log_message(self, format, *args):
        """Override to use proper logging instead of stderr"""
        logger.info(f"{self.address_string()} - {format % args}")

    def log_error(self, format, *args):
        """Override to use proper logging for errors"""
        logger.error(f"{self.address_string()} - {format % args}")


class ServerThread(threading.Thread):
    """Thread-safe HTTP server that can be cleanly started and stopped"""

    def __init__(self, directory=None, port=8000, bind_address='127.0.0.1'):
        super().__init__(name=f"HTTPServer-{port}")
        self.daemon = True
        self.directory = Path(directory).resolve() if directory else Path.cwd()
        self.port = port
        self.bind_address = bind_address
        self._stop_event = threading.Event()
        self.httpd = None
        self._server_started = threading.Event()
        self.error = None

        # Validate directory exists and is readable
        if not self.directory.exists():
            raise FileNotFoundError(f"Directory does not exist: {self.directory}")
        if not self.directory.is_dir():
            raise NotADirectoryError(f"Path is not a directory: {self.directory}")

    def run(self):
        """Start the HTTP server"""
        try:
            server_address = (self.bind_address, self.port)
            handler_class = lambda *args, **kwargs: SecureHTTPRequestHandler(
                *args, directory=str(self.directory), **kwargs
            )

            self.httpd = HTTPServer(server_address, handler_class)
            # Allow port reuse to avoid "Address already in use" errors
            self.httpd.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

            actual_port = self.httpd.server_address[1]
            logger.info(f"Server started on {self.bind_address}:{actual_port}, serving {self.directory}")
            self._server_started.set()

            # Use serve_forever with shutdown capability instead of manual loop
            self.httpd.serve_forever()

        except Exception as e:
            self.error = e
            logger.error(f"Server error: {e}")
            self._server_started.set()  # Signal that startup completed (with error)

    def stop(self, timeout=5):
        """Stop the server gracefully with timeout"""
        if not self.is_alive():
            return True

        logger.info("Shutting down server...")
        self._stop_event.set()

        if self.httpd:
            # Graceful shutdown
            self.httpd.shutdown()
            self.httpd.server_close()

        # Wait for thread to finish with timeout
        self.join(timeout=timeout)

        if self.is_alive():
            logger.warning(f"Server thread did not stop within {timeout} seconds")
            return False
        else:
            logger.info("Server stopped successfully")
            return True

    def wait_for_startup(self, timeout=10):
        """Wait for server to start up, return True if successful"""
        if self._server_started.wait(timeout=timeout):
            if self.error:
                raise self.error
            return True
        else:
            raise TimeoutError(f"Server did not start within {timeout} seconds")

    @property
    def url(self):
        """Get the server URL"""
        if self.httpd:
            host, port = self.httpd.server_address
            # Use localhost for 127.0.0.1 or 0.0.0.0
            if host in ('127.0.0.1', '0.0.0.0'):
                host = 'localhost'
            return f"http://{host}:{port}"
        return None


class ServerWorker(QThread):
    """Background thread for server operations - handles Qt integration"""
    server_started = pyqtSignal(str)  # URL
    server_stopped = pyqtSignal()
    server_error = pyqtSignal(str)

    def __init__(self):
        super().__init__()
        self.server = None
        self.operation = None
        self.directory = None
        self.port = None

    def start_server(self, directory, port):
        """Queue server start operation"""
        self.operation = "start"
        self.directory = directory
        self.port = port
        self.start()

    def stop_server(self):
        """Queue server stop operation"""
        self.operation = "stop"
        self.start()

    def run(self):
        """Execute server operation in background"""
        if self.operation == "start":
            try:
                self.server = ServerThread(self.directory, self.port)
                self.server.start()
                self.server.wait_for_startup()
                url = f"http://localhost:{self.port}"
                self.server_started.emit(url)
            except Exception as e:
                self.server_error.emit(str(e))

        elif self.operation == "stop":
            try:
                if self.server:
                    self.server.stop()
                    self.server = None
                self.server_stopped.emit()
            except Exception as e:
                self.server_error.emit(str(e))


@contextmanager
def http_server(directory=None, port=8000, bind_address='127.0.0.1'):
    """Context manager for HTTP server - ensures cleanup"""
    server = ServerThread(directory, port, bind_address)
    try:
        server.start()
        server.wait_for_startup()
        yield server
    finally:
        server.stop()


# Example usage and signal handling
if __name__ == "__main__":
    # Handle Ctrl+C gracefully
    def signal_handler(signum, frame):
        logger.info("Received interrupt signal, shutting down...")
        sys.exit(0)


    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    # Example 1: Using context manager (recommended)
    try:
        with http_server(directory="./public", port=8080) as server:
            print(f"Server running at {server.url}")
            print("Press Ctrl+C to stop")

            # Keep main thread alive
            while True:
                threading.Event().wait(1)

    except KeyboardInterrupt:
        pass
    except Exception as e:
        logger.error(f"Server failed to start: {e}")