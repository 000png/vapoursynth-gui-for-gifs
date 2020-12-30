#!./bin/python.exe
import sys
sys.path.append('.')

from PyQt5.QtWidgets import QApplication
from lib.layouts.MainWindow import MainWindow


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.resize(1020, 740)
    window.show()
    sys.exit(app.exec_())
