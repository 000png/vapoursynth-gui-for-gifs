#!./bin/python.exe
import sys
sys.path.append('.')

from PyQt5.QtWidgets import QApplication
from lib.layouts.MainLayout import MainLayout


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainLayout()
    window.resize(900, 700)
    window.show()
    sys.exit(app.exec_())
