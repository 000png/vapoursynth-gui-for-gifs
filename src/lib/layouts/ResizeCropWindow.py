#!./bin/python.exe
"""
Resize/crop window and layout; utilizes a modified version of resizer.html, which was
originall written by brandinator.
"""
import os
from PyQt5.QtCore import QDir, Qt, QUrl
from PyQt5.QtWebEngineWidgets import QWebEngineView
from PyQt5.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QAction, \
    QFileDialog, QMessageBox, QStyle

SCRIPT_DIR = os.path.abspath(os.path.dirname(os.path.realpath(__file__)))
HTML_RESIZER_SCRIPT = os.path.abspath(os.path.join(SCRIPT_DIR, '..\\..\\html\\resizer.html'))

class ResizeCropWindow(QMainWindow):
    """ Resize and cropping window """
    def __init__(self, parent=None, html=HTML_RESIZER_SCRIPT):
        """ Initializer """
        super(ResizeCropWindow, self).__init__(parent)
        self.resize(900, 700)
        self.setWindowTitle("Resize & Crop")
        self._generateLayout(html)

    def _generateLayout(self, html):
        """ Generate layout """
        web = QWebEngineView()
        web.load(QUrl.fromLocalFile(rf"{html}"))
        web.show()

        wid = QWidget(self)
        self.setCentralWidget(wid)
        layout = QVBoxLayout()

        layout.addWidget(web)
        wid.setLayout(layout)
