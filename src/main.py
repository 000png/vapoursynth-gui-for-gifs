#!./bin/python.exe
import sys
sys.path.append('.')

import vapoursynth as vs
from PyQt5.QtWidgets import QApplication
from lib.layout.main_layout import MainLayout


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainLayout()
    window.resize(800, 600)
    window.show()
    sys.exit(app.exec_())
