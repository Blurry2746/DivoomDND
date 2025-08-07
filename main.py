import sys
from PyQt5.QtWidgets import QApplication
from gui import DivoomDNDGUI  # Make sure gui.py is in the same directory or properly imported

def main():
    app = QApplication(sys.argv)
    window = DivoomDNDGUI()
    # window.show()  # Optional: show the main window if needed
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
