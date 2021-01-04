#!./bin/python.exe
import sys
sys.path.append('.')

from PyQt5.QtWidgets import QApplication
from lib.layouts.MainWindow import MainWindow
from version import MODULE_VERSION


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow(MODULE_VERSION)
    window.resize(1020, 740)
    window.show()
    sys.exit(app.exec_())
