#!./bin/python.exe
"""
Resize/crop window and layout; utilizes a modified version of resizer.html, which was
originall written by brandinator.
"""
import os
import webbrowser
from shutil import copyfile
from PyQt5.QtCore import QDir, Qt, QUrl
from PyQt5.QtWebEngineWidgets import QWebEngineView
from PyQt5.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QAction, \
    QFileDialog, QMessageBox, QStyle

from lib.utils.GlobalConstants import WORK_DIR

SCRIPT_DIR = os.path.dirname(os.path.realpath(__file__))
HTML_RESIZER_BASE_SCRIPT = os.path.join(SCRIPT_DIR, 'resizer.html')
HTML_RESIZER_SCRIPT = os.path.join(WORK_DIR, 'resizer.html')

class ResizerWindow(QMainWindow):
    """ Resize and cropping window """
    def __init__(self, parent=None):
        """ Initializer """
        super(ResizerWindow, self).__init__(parent)
        self.resize(900, 700)
        self.setWindowTitle("Resize & Crop")
        self._generateLayout()

    def _generateLayout(self):
        """ Generate layout; always assumes webmd """
        self.setResizeVideoExtension(filename='./resizer.webm', extension='.webm')
        web = QWebEngineView()
        web.load(QUrl.fromLocalFile(rf"{HTML_RESIZER_SCRIPT}"))
        web.show()

        wid = QWidget(self)
        self.setCentralWidget(wid)
        layout = QVBoxLayout()

        layout.addWidget(web)
        wid.setLayout(layout)

    @classmethod
    def openInBrowser(cls, filename):
        """ Open HTML script in browser; need to copy video to working dir """
        extension = cls.setResizeVideoExtension(filename=filename)
        url = 'file://' + HTML_RESIZER_SCRIPT
        webbrowser.open(url)

    @classmethod
    def setResizeVideoExtension(cls, filename=None, extension=None):
        """ Set the resizer video the html script should look for """
        if not extension:
            if not filename:
                raise ValueError(f"Need video filename to set HTML resize video extension")

            _, extension = os.path.splitext(filename)

        result = f"<source src=\"{filename}\" type=\"video/{extension[1:]}\">"

        with open(HTML_RESIZER_BASE_SCRIPT, 'r') as infh:
            newHtml = infh.read().replace('[REPLACE_RESIZE_VIDEO]', result)
            with open(HTML_RESIZER_SCRIPT, 'w') as outfh:
                outfh.write(newHtml)

        return extension
