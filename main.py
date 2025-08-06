from PyQt5 import QtWidgets, QtGui
from gui import SystemTrayApp

def main():
    import sys
    app = QtWidgets.QApplication(sys.argv)
    icon = QtGui.QIcon()  # Add icon path if available
    tray = SystemTrayApp(app, icon)
    tray.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
